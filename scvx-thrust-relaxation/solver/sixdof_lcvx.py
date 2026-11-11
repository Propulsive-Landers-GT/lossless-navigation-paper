"""6-DOF powered descent guidance with a lossless thrust relaxation, solved by successive
convexification (penalized trust region, PTR).

Model, units and parameters follow the baseline case of Szmuk, Reynolds & Acikmese, "Successive
Convexification for Real-Time 6-DoF Powered Descent Guidance with State-Triggered Constraints"
(arXiv:1811.10803): non-dimensional units, inertial x axis up, body x axis along the engine.

The one change from that paper is the thrust magnitude constraint. They linearize the nonconvex
lower bound T_min <= ||T_B|| around the previous iterate and deplete mass at alpha*||T_B||. Here
the bound is replaced by the LCvx relaxation

    ||T_B|| <= Gamma,   T_min <= Gamma <= T_max,   mass rate = -alpha * Gamma,

which is convex. lean/LCvx/Basic.lean proves when an optimum of this relaxation has
||T_B|| = Gamma at every node, so that it also solves the original problem.

State x = [m, r_I(3), v_I(3), q_B->I(4, scalar first), w_B(3)], control u = T_B (body frame),
slack Gamma, and the time of flight s. Controls are held constant over each interval (ZOH), and
each interval is integrated with RK4 substeps. The linearization used by the solver is the exact
Jacobian of that discrete map, which is also the derivative the Lean theorem talks about.
"""
from dataclasses import dataclass, field

import cvxpy as cp
import numpy as np
import sympy as sp

NX, NU = 14, 3
IM, IR, IV, IQ, IW = 0, slice(1, 4), slice(4, 7), slice(7, 11), slice(11, 14)


@dataclass
class Params:
    # Szmuk, Reynolds & Acikmese 2018, Table 2 (baseline, no aerodynamics).
    g: np.ndarray = field(default_factory=lambda: np.array([-1.0, 0.0, 0.0]))
    J: np.ndarray = field(default_factory=lambda: 0.168 * np.array([2e-2, 1.0, 1.0]))
    rT: np.ndarray = field(default_factory=lambda: np.array([-0.25, 0.0, 0.0]))
    alpha: float = 1.0 / 30.0  # 1 / (Isp g0), Isp = 30, g0 = 1
    m_wet: float = 2.0
    m_dry: float = 1.0
    T_min: float = 1.5
    T_max: float = 6.5
    delta_max: float = np.radians(20.0)  # gimbal
    theta_max: float = np.radians(90.0)  # tilt
    omega_max: float = np.radians(28.6)
    # Minimum elevation of the vehicle as seen from the pad. The paper lists 75 deg, but its own
    # initial positions violate tan(75 deg)*||r_yz|| <= r_x, so a 20 deg cone is used here.
    gamma_gs: float = np.radians(20.0)
    r0: np.ndarray = field(default_factory=lambda: np.array([4.0, 3.0, 2.0]))
    v0: np.ndarray = field(default_factory=lambda: np.array([-1.0, -2.0, 1.0]))
    vf: np.ndarray = field(default_factory=lambda: np.array([-0.1, 0.0, 0.0]))
    N: int = 25  # intervals
    substeps: int = 8
    s_guess: float = 4.0
    s_bounds: tuple = (0.5, 15.0)
    fixed_s: float | None = None  # set to fix the time of flight
    # PTR weights and tolerances (paper: w_nu = 1e4, W_tr = 0.5). The fuel term is scaled up so
    # that one unit of Gamma is worth O(1) against the trust-region penalty; this changes the
    # iterates, not the optimum. Gamma is left out of the trust region by default (tr_gamma = 0):
    # it only drives the mass equation, and penalizing it makes Gamma trail behind ||U||.
    w_fuel: float = 100.0
    w_vc: float = 1e4
    w_tr: float = 0.05
    tr_gamma: float = 0.0
    tol_step: float = 1e-6
    tol_vc: float = 1e-8
    max_iter: int = 300


def quat_to_dcm(q):
    """Body-to-inertial DCM for a scalar-first Hamilton quaternion (works on sympy or numpy)."""
    q0, q1, q2, q3 = q
    return [
        [1 - 2 * (q2**2 + q3**2), 2 * (q1 * q2 - q0 * q3), 2 * (q1 * q3 + q0 * q2)],
        [2 * (q1 * q2 + q0 * q3), 1 - 2 * (q1**2 + q3**2), 2 * (q2 * q3 - q0 * q1)],
        [2 * (q1 * q3 - q0 * q2), 2 * (q2 * q3 + q0 * q1), 1 - 2 * (q1**2 + q2**2)],
    ]


class Model:
    """Vector field f(x, u, Gamma) and the RK4 discrete map with its exact Jacobian."""

    def __init__(self, p: Params):
        self.p = p
        x = sp.Matrix(sp.symbols("x0:14"))
        u = sp.Matrix(sp.symbols("u0:3"))
        G = sp.Symbol("G")
        m, v, q, w = x[0], x[4:7, 0], x[7:11, 0], x[11:14, 0]
        C = sp.Matrix(quat_to_dcm(list(q)))
        Om = sp.Matrix([
            [0, -w[0], -w[1], -w[2]],
            [w[0], 0, w[2], -w[1]],
            [w[1], -w[2], 0, w[0]],
            [w[2], w[1], -w[0], 0],
        ])
        Jm = sp.diag(*[sp.Float(j) for j in p.J])
        rT = sp.Matrix([sp.Float(c) for c in p.rT])
        f = sp.Matrix.vstack(
            sp.Matrix([-p.alpha * G]),
            v,
            C * u / m + sp.Matrix([sp.Float(c) for c in p.g]),
            Om * q / 2,
            Jm.inv() * (rT.cross(u) - w.cross(Jm * w)),
        )
        args = (list(x), list(u), G)
        self._f = sp.lambdify(args, f, "numpy", cse=True)
        self._fx = sp.lambdify(args, f.jacobian(x), "numpy", cse=True)
        self._fu = sp.lambdify(args, f.jacobian(u), "numpy", cse=True)
        self._fG = sp.lambdify(args, f.diff(G), "numpy", cse=True)

    def f(self, x, u, G):
        return np.asarray(self._f(x, u, G), dtype=float).ravel()

    def step(self, x, u, G, s, jac=True):
        """One interval: x_next = Phi(x, u, G, s). With jac, also D = dPhi/d(x, u, G, s), 14x19."""
        p = self.p
        M = p.substeps
        dh_ds = 1.0 / (p.N * M)
        h = s * dh_ds
        nz = NX + NU + 2
        D = np.zeros((NX, nz))
        D[:, :NX] = np.eye(NX)
        du = np.zeros((NU, nz))
        du[:, NX:NX + NU] = np.eye(NU)
        dG = np.zeros(nz)
        dG[NX + NU] = 1.0
        dh = np.zeros(nz)
        dh[NX + NU + 1] = dh_ds

        def stage(y, Dy):
            k = self.f(y, u, G)
            if not jac:
                return k, None
            dk = (np.asarray(self._fx(y, u, G), float) @ Dy
                  + np.asarray(self._fu(y, u, G), float) @ du
                  + np.outer(np.asarray(self._fG(y, u, G), float).ravel(), dG))
            return k, dk

        for _ in range(M):
            k1, d1 = stage(x, D)
            k2, d2 = stage(x + h / 2 * k1, None if not jac else D + h / 2 * d1 + np.outer(k1 / 2, dh))
            k3, d3 = stage(x + h / 2 * k2, None if not jac else D + h / 2 * d2 + np.outer(k2 / 2, dh))
            k4, d4 = stage(x + h * k3, None if not jac else D + h * d3 + np.outer(k3, dh))
            ksum = k1 + 2 * k2 + 2 * k3 + k4
            if jac:
                D = D + h / 6 * (d1 + 2 * d2 + 2 * d3 + d4) + np.outer(ksum / 6, dh)
            x = x + h / 6 * ksum
        return x, D

    def propagate(self, x0, U, G, s):
        """Single shooting through the discrete map from x0."""
        X = [np.asarray(x0, float)]
        for k in range(self.p.N):
            X.append(self.step(X[-1], U[k], G[k], s, jac=False)[0])
        return np.array(X)


def initial_state(p: Params):
    return np.concatenate([[p.m_wet], p.r0, p.v0, [1.0, 0, 0, 0], np.zeros(3)])


def initial_guess(p: Params):
    """Straight-line guess as in the paper: interpolate states, thrust cancels gravity."""
    x0 = initial_state(p)
    xf = np.concatenate([[p.m_dry], np.zeros(3), p.vf, [1.0, 0, 0, 0], np.zeros(3)])
    lam = np.linspace(0, 1, p.N + 1)[:, None]
    X = (1 - lam) * x0 + lam * xf
    U = -X[:-1, IM:IM + 1] * p.g[None, :]
    G = np.maximum(np.linalg.norm(U, axis=1), p.T_min)
    s = p.fixed_s if p.fixed_s is not None else p.s_guess
    return X, U, G, s


def terminal_rows(X):
    """Terminal equality constraints, as a function of the final state (10 rows).

    Position, velocity, upright attitude (q2 = q3 = 0) and no pitch/yaw rate. Roll is left free:
    the vehicle is axisymmetric about the thrust axis, so roll rate stays exactly zero and roll
    angle does not matter for landing.
    """
    return X[IR], X[IV], X[IQ][2:4], X[IW][1:3]


def solve_subproblem(model, Xb, Ub, Gb, sb, lin, hard_tr=None):
    """Convex PTR subproblem around the reference (Xb, Ub, Gb, sb).

    lin holds per-interval (x_next_ref, A, B, E, S). With hard_tr set, the soft trust-region
    penalty and virtual control are dropped and |delta| <= hard_tr is imposed instead; this is
    used once at convergence to check that the converged trajectory solves its own linearization.
    """
    p = model.p
    N = p.N
    X = cp.Variable((N + 1, NX))
    U = cp.Variable((N, NU))
    G = cp.Variable(N)
    s = cp.Variable()
    V = cp.Variable((N, NX))
    cons = [X[0] == initial_state(p)]
    for k in range(N):
        xn, A, B, E, S = lin[k]
        cons.append(X[k + 1] == xn + A @ (X[k] - Xb[k]) + B @ (U[k] - Ub[k])
                    + E * (G[k] - Gb[k]) + S * (s - sb) + (0 if hard_tr is not None else V[k]))
    r, v, qtilt, wpy = terminal_rows(X[N])
    cons += [r == 0, v == p.vf, qtilt == 0, wpy == 0]
    cons += [X[:, IM] >= p.m_dry]
    for k in range(N):
        cons += [np.tan(p.gamma_gs) * cp.norm(X[k, 2:4]) <= X[k, 1]]  # glide slope, k < N
    for k in range(N + 1):
        cons += [cp.norm(X[k, 9:11]) <= np.sqrt((1 - np.cos(p.theta_max)) / 2)]  # tilt
        cons += [cp.norm(X[k, IW]) <= p.omega_max]
    for k in range(N):
        cons += [cp.norm(U[k]) <= G[k], G[k] >= p.T_min, G[k] <= p.T_max]  # LCvx relaxation
        cons += [np.cos(p.delta_max) * cp.norm(U[k]) <= U[k, 0]]  # gimbal
    if p.fixed_s is not None:
        cons += [s == p.fixed_s]
    else:
        cons += [s >= p.s_bounds[0], s <= p.s_bounds[1]]

    fuel = -p.w_fuel * X[N, IM]  # maximize final mass
    if hard_tr is None:
        tr = (cp.sum_squares(X - Xb) + cp.sum_squares(U - Ub) + p.tr_gamma * cp.sum_squares(G - Gb)
              + cp.square(s - sb))
        obj = fuel + p.w_vc * cp.sum(cp.abs(V)) + p.w_tr * tr
    else:
        cons += [cp.abs(X - Xb) <= hard_tr, cp.abs(U - Ub) <= hard_tr,
                 cp.abs(G - Gb) <= hard_tr, cp.abs(s - sb) <= hard_tr]
        obj = fuel
    prob = cp.Problem(cp.Minimize(obj), cons)
    prob.solve(solver=cp.CLARABEL)
    if prob.status not in ("optimal", "optimal_inaccurate"):
        raise RuntimeError(f"subproblem status {prob.status}")
    return X.value, U.value, G.value, float(s.value), (V.value if hard_tr is None else None), prob


def linearize(model, X, U, G, s):
    out = []
    for k in range(model.p.N):
        xn, D = model.step(X[k], U[k], G[k], s)
        out.append((xn, D[:, :NX], D[:, NX:NX + NU], D[:, NX + NU], D[:, NX + NU + 1]))
    return out


def solve(p: Params, verbose=True, init=None):
    """init: optional (X, U, G, s) to start from instead of the straight-line guess."""
    model = Model(p)
    Xb, Ub, Gb, sb = initial_guess(p) if init is None else init
    history, converged = [], False
    for it in range(p.max_iter):
        lin = linearize(model, Xb, Ub, Gb, sb)
        X, U, G, s, V, _ = solve_subproblem(model, Xb, Ub, Gb, sb, lin)
        step = max(np.abs(X - Xb).max(), np.abs(U - Ub).max(), np.abs(G - Gb).max(), abs(s - sb))
        vc = np.abs(V).sum()
        history.append(dict(it=it, mf=X[-1, IM], s=s, step=step, vc=vc))
        if verbose:
            print(f"iter {it:3d}  m_f={X[-1, IM]:.6f}  t_f={s:.4f}  step={step:.2e}  vc={vc:.2e}")
        Xb, Ub, Gb, sb = X, U, G, s
        if step < p.tol_step and vc < p.tol_vc:
            converged = True
            break
    if not converged:
        print("warning: PTR hit max_iter without converging")
    return model, dict(X=Xb, U=Ub, G=Gb, s=sb, history=history, converged=converged)
