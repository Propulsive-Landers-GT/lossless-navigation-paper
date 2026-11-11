"""Solve 6-DOF cases and check them against the Lean theorems.

For each case this prints and saves:
  * Gamma - ||T|| at every node, and the lossy nodes (where it is > tol),
  * the terminal error after re-integrating the converged controls with scipy's adaptive RK45,
  * which path constraints are active,
  * a fixed-point check: re-solving the convex subproblem at the converged trajectory, with no
    trust-region penalty and a hard box around it, should not find anything cheaper,
  * for the lossy nodes, the rank of d(terminal conditions)/d(lossy thrusts). This is the
    surjectivity hypothesis of LCvx.Problem.slack_eq_lower_of_surjective: full rank (10) means
    the lossy thrusts can steer the terminal state in every direction,
  * the hypotheses of the tail theorems (sixDOF_tail, sixDOF_ptr_tail): the last node m with an
    active path constraint, and whether every 4 thrust nodes from m on can steer the terminal
    state.

Usage:  python check_lossless.py            (all cases)
        python check_lossless.py baseline   (one case)
"""
import itertools
import json
import math
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

from sixdof_lcvx import (IM, IQ, IW, NX, Params, initial_state, linearize, solve,
                         solve_subproblem)

OUT = Path(__file__).parent / "results"
TOL_LOSSY = 1e-6
TOL_ACTIVE = 1e-6
TERM_IDX = [1, 2, 3, 4, 5, 6, 9, 10, 12, 13]  # r, v, q2, q3, w_y, w_z: the 10 terminal rows

CASES = {
    # Szmuk et al. baseline with an out-of-plane start, free time of flight. The angular rate
    # limit ends up active at 16 nodes, so the "path constraints inactive" hypothesis fails here.
    "baseline": dict(),
    # Same, with the angular rate limit raised from 28.6 to 90 deg/UT. No path constraint is
    # active at the solution, so every hypothesis of sixDOF_ptr_free_time can be checked.
    "loose_rate": dict(omega_max=np.radians(90.0)),
    # Time of flight fixed a little above the free optimum (6.87). Needs a stiffer trust region.
    "fixed_short": dict(fixed_s=7.5, w_tr=0.2, max_iter=500),
    # Time of flight fixed far above the optimum (12 vs 6.87). PTR 2-cycles with w_tr <= 0.1 and
    # converges slowly (about 2100 iterations, 8 minutes) with w_tr = 0.5.
    "fixed_long": dict(fixed_s=12.0, w_tr=0.5, max_iter=3000),
}


def resimulate(model, sol):
    """Integrate the true ODE with ZOH controls using adaptive RK45 at tight tolerance."""
    p = model.p
    x = initial_state(p)
    dt = sol["s"] / p.N
    for k in range(p.N):
        u, G = sol["U"][k], sol["G"][k]
        r = solve_ivp(lambda t, y: model.f(y, u, G), (0, dt), x, rtol=1e-11, atol=1e-12)
        x = r.y[:, -1]
    return x


def active_constraints(p, X, U, G, s):
    act = []
    tg = np.tan(p.gamma_gs)
    for k in range(p.N):
        if tg * np.linalg.norm(X[k, 2:4]) - X[k, 1] > -TOL_ACTIVE:
            act.append(("glide_slope", k))
    for k in range(p.N + 1):
        if np.linalg.norm(X[k, 9:11]) - np.sqrt((1 - np.cos(p.theta_max)) / 2) > -TOL_ACTIVE:
            act.append(("tilt", k))
        if np.linalg.norm(X[k, IW]) - p.omega_max > -TOL_ACTIVE:
            act.append(("omega", k))
        if p.m_dry - X[k, IM] > -TOL_ACTIVE:
            act.append(("dry_mass", k))
    if p.fixed_s is None and min(s - p.s_bounds[0], p.s_bounds[1] - s) < TOL_ACTIVE:
        act.append(("tof_bound", None))
    gimbal = [k for k in range(p.N)
              if np.cos(p.delta_max) * np.linalg.norm(U[k]) - U[k, 0] > -TOL_ACTIVE]
    at_min = [k for k in range(p.N) if G[k] - p.T_min < TOL_ACTIVE]
    at_max = [k for k in range(p.N) if p.T_max - G[k] < TOL_ACTIVE]
    return act, gimbal, at_min, at_max


def lossy_sensitivity_rank(model, sol, lossy):
    """Rank of d(terminal rows)/d(u_j), j in lossy, through the exact discrete Jacobians."""
    if not lossy:
        return 0
    S = node_sensitivities(model, sol)
    return rank([S[j] for j in lossy])[0]


def node_sensitivities(model, sol):
    """d(terminal rows)/d(u_j) for every node j: A_{N-1} ... A_{j+1} B_j, restricted to rows."""
    lin = linearize(model, sol["X"], sol["U"], sol["G"], sol["s"])
    S, Phi = [None] * model.p.N, np.eye(NX)
    for j in reversed(range(model.p.N)):
        S[j] = (Phi @ lin[j][2])[TERM_IDX]
        Phi = Phi @ lin[j][1]
    return S


def rank(cols):
    sv = np.linalg.svd(np.hstack(cols), compute_uv=False)
    return int((sv > 1e-9 * sv[0]).sum()), float(sv[-1] / sv[0])


def constraint_grad(p, kind, x):
    """State gradient of an active path constraint g(x) <= 0, as the solver writes it."""
    gv = np.zeros(NX)
    if kind == "omega":
        gv[IW] = x[IW] / np.linalg.norm(x[IW])
    elif kind == "tilt":
        gv[9:11] = x[9:11] / np.linalg.norm(x[9:11])
    elif kind == "glide_slope":
        gv[2:4] = np.tan(p.gamma_gs) * x[2:4] / np.linalg.norm(x[2:4])
        gv[1] = -1.0
    elif kind == "dry_mass":
        gv[IM] = -1.0
    return gv


def fold_check(model, sol, act, max_sets=300_000):
    """Hypotheses of sixDOF_fold / sixDOF_ptr_fold. For each split node m, hold the active path
    constraints after m as equalities and find the smallest s such that every s thrust nodes
    from m on can steer the terminal rows plus those held constraints. Then at most s - 1 of
    those nodes can be lossy (when some of them has Gamma > T_min)."""
    p, X = model.p, sol["X"]
    lin = linearize(model, X, sol["U"], sol["G"], sol["s"])
    sens = {}  # sens[k, j] = d x_k / d u_j for j < k
    for j in range(p.N):
        M = lin[j][2]
        sens[j + 1, j] = M
        for k in range(j + 1, p.N):
            M = lin[k][1] @ M
            sens[k + 1, j] = M
    states = [(kind, k) for kind, k in act if k is not None]
    out = []
    for m in range(p.N):
        folded = [(kind, k) for kind, k in states if k > m]
        tail = list(range(m, p.N))
        cols = {}
        for j in tail:
            rows = [sens[p.N, j][TERM_IDX]]
            rows += [(constraint_grad(p, kind, X[k]) @ sens[k, j])[None, :] if k > j
                     else np.zeros((1, 3)) for kind, k in folded]
            cols[j] = np.vstack(rows)
        nrows = len(TERM_IDX) + len(folded)
        best = None
        for s in range(-(-nrows // 3), len(tail) + 1):
            if math.comb(len(tail), s) > max_sets:
                break
            if all(rank([cols[j] for j in c])[0] == nrows
                   for c in itertools.combinations(tail, s)):
                best = s - 1
                break
        above = any(sol["G"][i] - p.T_min > TOL_ACTIVE for i in tail)
        out.append((m, len(folded), best if above else None))
    return out


def tail_check(model, sol, act, size=4):
    """Hypotheses of sixDOF_tail / sixDOF_ptr_tail. Path constraints may be active up to state
    node m and must be slack after it, so the theorem covers thrust nodes m..N-1 (a thrust at
    node j only moves states after j). If every `size` of those nodes can steer the terminal
    rows and some of them has Gamma > T_min, then fewer than `size` of them can be lossy
    (gimbal-inactive)."""
    p = model.p
    m = max([k for _, k in act if k is not None], default=0)
    tail = list(range(m, p.N))
    S = node_sensitivities(model, sol)
    bad, worst, total = 0, 1.0, 0
    for c in itertools.combinations(tail, size):
        r, ratio = rank([S[j] for j in c])
        total += 1
        bad += r < len(TERM_IDX)
        worst = min(worst, ratio)
    above = [i for i in tail if sol["G"][i] - p.T_min > TOL_ACTIVE]
    holds = total > 0 and bad == 0 and bool(above)
    return dict(m=m, tail_nodes=len(tail), sets=total, rank_deficient=bad,
                worst_sv_ratio=worst if total else None, tail_nodes_above_Tmin=above,
                at_most_3_lossy_in_tail=holds)


def cost_model_check(model, sol, trials=5, scale=0.1, seed=0):
    """The solver's subproblem cost is -m_N of the linearized recursion. Compare it with the
    cost Lean uses for the subproblem (Data.linProblem.cost):
        -m_0 + kappa(s_ref) * sum(Gamma) + kappa(s - s_ref) * sum(Gamma_ref),
    with kappa(s) = s * alpha / N, on random perturbations of the converged point."""
    p = model.p
    Xb, Ub, Gb, sb = sol["X"], sol["U"], sol["G"], sol["s"]
    lin = linearize(model, Xb, Ub, Gb, sb)
    kappa = lambda s: s * p.alpha / p.N
    rng = np.random.default_rng(seed)
    worst = 0.0
    for _ in range(trials):
        U = Ub + scale * rng.standard_normal(Ub.shape)
        G = Gb + scale * rng.standard_normal(Gb.shape)
        s = sb + scale * rng.standard_normal()
        x = initial_state(p)
        for k in range(p.N):
            xn, A, B, E, S = lin[k]
            x = xn + A @ (x - Xb[k]) + B @ (U[k] - Ub[k]) + E * (G[k] - Gb[k]) + S * (s - sb)
        lean = -p.m_wet + kappa(sb) * G.sum() + kappa(s - sb) * Gb.sum()
        worst = max(worst, abs(-x[IM] - lean))
    return worst


def fixed_point_check(model, sol, box=0.05):
    lin = linearize(model, sol["X"], sol["U"], sol["G"], sol["s"])
    X, U, G, s, _, prob = solve_subproblem(model, sol["X"], sol["U"], sol["G"], sol["s"], lin,
                                           hard_tr=box)
    p = model.p
    dmf = X[-1, IM] - sol["X"][-1, IM]  # positive would mean the linearization finds better
    step = max(np.abs(X - sol["X"]).max(), np.abs(U - sol["U"]).max(),
               np.abs(G - sol["G"]).max(), abs(s - sol["s"]))
    return dict(box=box, mf_gain=float(dmf), max_move=float(step))


def plot(name, p, sol):
    X, U, G, s = sol["X"], sol["U"], sol["G"], sol["s"]
    t_nodes = np.linspace(0, s, p.N + 1)
    T = np.linalg.norm(U, axis=1)
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    ax[0].step(t_nodes[:-1], G, where="post", label="slack Γ", lw=2.5, alpha=0.5)
    ax[0].step(t_nodes[:-1], T, where="post", label="‖T_B‖", lw=1.2, color="k")
    ax[0].axhline(p.T_min, ls="--", c="gray", lw=0.8)
    ax[0].axhline(p.T_max, ls="--", c="gray", lw=0.8)
    ax[0].set(xlabel="time [UT]", ylabel="thrust [UM UL/UT²]", title="Thrust magnitude vs slack")
    ax[0].legend()
    tilt = np.degrees(np.arccos(np.clip(1 - 2 * (X[:, 9]**2 + X[:, 10]**2), -1, 1)))
    gim = np.degrees(np.arccos(np.clip(U[:, 0] / np.maximum(T, 1e-12), -1, 1)))
    ax[1].plot(t_nodes, tilt, label="tilt from vertical")
    ax[1].step(t_nodes[:-1], gim, where="post", label="gimbal angle")
    ax[1].axhline(np.degrees(p.delta_max), ls="--", c="gray", lw=0.8)
    ax[1].set(xlabel="time [UT]", ylabel="deg", title="Attitude and gimbal")
    ax[1].legend()
    a3 = fig.add_subplot(1, 3, 3, projection="3d")
    ax[2].remove()
    a3.plot(X[:, 2], X[:, 3], X[:, 1], "o-", ms=2)
    for k in range(0, p.N, 2):  # thrust direction in inertial frame, scaled
        q0, q1, q2, q3 = X[k, IQ]
        C = np.array([[1 - 2 * (q2**2 + q3**2), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
                      [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1**2 + q3**2), 2 * (q2 * q3 - q0 * q1)],
                      [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1**2 + q2**2)]])
        TI = -C @ U[k] * 0.12  # plume points opposite the thrust
        a3.plot([X[k, 2], X[k, 2] + TI[1]], [X[k, 3], X[k, 3] + TI[2]],
                [X[k, 1], X[k, 1] + TI[0]], c="r", lw=1)
    a3.set(xlabel="y", ylabel="z", zlabel="x (up)", title="Trajectory (red: plume)")
    fig.tight_layout()
    fig.savefig(OUT / f"{name}.png", dpi=110)
    plt.close(fig)


def run(name):
    p = Params(**CASES[name])
    t0 = time.time()
    model, sol = solve(p, verbose=False)
    wall = time.time() - t0
    X, U, G, s = sol["X"], sol["U"], sol["G"], sol["s"]
    T = np.linalg.norm(U, axis=1)
    gap = G - T
    lossy = [int(k) for k in np.where(gap > TOL_LOSSY)[0]]
    xf = resimulate(model, sol)
    term_target = np.concatenate([np.zeros(3), p.vf, np.zeros(2), np.zeros(2)])
    term_err = float(np.abs(xf[TERM_IDX] - term_target).max())
    act, gimbal, at_min, at_max = active_constraints(p, X, U, G, s)
    lossy_rank = lossy_sensitivity_rank(model, sol, lossy)
    conv = sol["converged"]
    fpc = fixed_point_check(model, sol) if conv else "skipped: not converged"
    steer = tail_check(model, sol, act) if conv else "skipped: not converged"
    folds = fold_check(model, sol, act) if conv else []
    fold_summary = [f"m={m}: {nf} held, at most {b} lossy" for m, nf, b in folds
                    if b is not None]
    cost_err = cost_model_check(model, sol)
    res = dict(
        case=name, converged=sol["converged"], iterations=len(sol["history"]),
        wall_s=round(wall, 1), t_f=s, m_f=float(X[-1, IM]), fuel=float(p.m_wet - X[-1, IM]),
        max_gap=float(gap.max()), lossy_nodes=lossy,
        lossy_gimbal_inactive=[k for k in lossy if k not in gimbal],
        lossy_sensitivity_rank=lossy_rank, terminal_rows=len(TERM_IDX),
        all_slacks_at_Tmin=bool(np.all(G - p.T_min < TOL_ACTIVE)),
        nodes_at_Tmin=at_min, nodes_at_Tmax=at_max, gimbal_active=gimbal,
        active_path_constraints=act, resim_terminal_error=term_err, fixed_point=fpc,
        tail_check=steer, fold_check=fold_summary, cost_vs_lean_formula=cost_err, Gamma=G.tolist(), T_norm=T.tolist(),
    )
    print(f"\n=== {name} ===")
    for k in ["converged", "iterations", "wall_s", "t_f", "m_f", "max_gap", "lossy_nodes",
              "lossy_gimbal_inactive", "lossy_sensitivity_rank", "all_slacks_at_Tmin",
              "nodes_at_Tmin", "nodes_at_Tmax", "gimbal_active", "active_path_constraints",
              "resim_terminal_error", "fixed_point", "tail_check", "fold_check", "cost_vs_lean_formula"]:
        print(f"  {k:24s} {res[k]}")
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=1))
    np.savez(OUT / f"{name}.npz", X=X, U=U, G=G, s=s)
    plot(name, p, sol)
    return res


if __name__ == "__main__":
    for name in (sys.argv[1:] or CASES):
        run(name)
