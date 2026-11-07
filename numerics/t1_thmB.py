"""Task 1: numerical check of Theorem B (model M1) -- reachable velocity-increment set R,
unreachability of the midpoint M, gap quantification.

Usage: .venv/bin/python t1_thmB.py [quick]
Outputs: results/t1_*.png, results/t1_*.json
"""
import sys, json, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import models
from runner import run_many, run_batch

QUICK = len(sys.argv) > 1 and sys.argv[1] == "quick"
OUT = "results/"
D2R = np.pi / 180


def spec(P, **kw):
    return ("M1", P, kw)


def mc_cloud_planar(P, tf, N, n, rng):
    """Monte-Carlo samples of the planar (inner-discretized) M1 set."""
    h = tf / N; om, de = P["omega"], P["delta"]
    s, c1 = models.min_throttle_coeffs(P, tf, N)
    pts = []
    for i in range(n):
        typ = i % 4
        if typ == 0:
            steps = om * h * np.clip(rng.normal(rng.uniform(-1, 1), 0.6, N), -1, 1)
        elif typ == 1:
            ks = rng.integers(0, N + 1); sg = rng.choice([-1, 1])
            steps = om * h * sg * np.where(np.arange(N) < ks, 1, -1) * rng.uniform(0.6, 1)
        elif typ == 2:
            k1, k2 = np.sort(rng.integers(0, N + 1, 2)); sg = rng.choice([-1, 1])
            steps = om * h * sg * np.where(np.arange(N) < k1, 1, np.where(np.arange(N) < k2, -1, 0))
        else:
            steps = om * h * rng.choice([-1, 1]) * np.ones(N) * rng.uniform(0, 1)
        th = np.concatenate([[0], np.cumsum(steps)])
        lo = np.maximum(th[:-1], th[1:]) - de; hi = np.minimum(th[:-1], th[1:]) + de
        u = rng.random()
        ps = np.where(rng.random(N) < 0.5, lo, hi) if u < 0.3 else (
            hi if u < 0.5 else (lo if u < 0.7 else lo + rng.random(N) * (hi - lo)))
        r = rng.random()
        T = P["rho1"] * np.ones(N) if r < 0.4 else (rng.uniform(P["rho1"], P["rho2"], N) if r < 0.7 else
                                                     np.full(N, rng.uniform(P["rho1"], P["rho2"])))
        m = P["m0"] - P["alpha"] * np.concatenate([[0], np.cumsum(T * h)])
        c = np.log(m[:-1] / m[1:]) / P["alpha"] if P["alpha"] > 0 else T / P["m0"] * h
        pts.append([np.sum(c * np.sin(ps)), np.sum(c * np.cos(ps))])
    return np.array(pts)


def midpoint_gap(P, tf, N, planar, nstart, tent=False, target=None):
    ex = models.extreme_arcs_M1_cont(P, tf, tent=tent)
    M = np.array([0, 0, ex["Mz"]]) if target is None else target
    r = run_many(spec(P, tf=tf, N=N, planar=planar, tent=tent), dict(mode="dist", target=M), nstart)
    # how many local optima within 1e-6 of best
    fs = np.sqrt(np.array(r["fs"]))
    return dict(dist=float(np.sqrt(r["f"])), z=r["z"].tolist(), Px=ex["Px"], Mz=ex["Mz"],
                n_ok=r["nok"], frac_at_best=float(np.mean(fs < fs[0] + 1e-6)), fs_q=np.quantile(fs, [0, .1, .5, .9]).tolist())


def planar_to_3d(xp, N):
    T = xp[:N]; th = xp[N:2 * N + 1]; ps = xp[2 * N + 1:]
    b = np.stack([np.sin(th), 0 * th, np.cos(th)], 1).ravel()
    d = np.stack([np.sin(ps), 0 * ps, np.cos(ps)], 1).ravel()
    return np.concatenate([T, b, d])


def zmin_curve(P, tf, N, planar, xs, nstart, sign=+1, warm=None):
    """min (sign=+1) or max (sign=-1) of Dv_z subject to Dv_x = x (and Dv_y = 0 in 3D).
    warm: optional list of planar solution vectors used as extra 3D initial guesses."""
    eq = (0,) if planar else (0, 1)
    jobs = []
    for x in xs:
        jobs.append((spec(P, tf=tf, N=N, planar=planar, eq_idx=eq),
                     dict(mode="lin", c=[0, 0, sign], eq_val=[x] if planar else [x, 0.0])))
    res = run_batch(jobs, nstart)
    out = np.array([sign * r["f"] if np.isfinite(r["f"]) else np.nan for r in res])
    if warm is not None and not planar:
        R3 = models.ReachM1(P, tf, N, planar=False, eq_idx=eq)
        for i, (x, xp) in enumerate(zip(xs, warm)):
            if xp is None:
                continue
            r = R3.solve(planar_to_3d(xp, N), mode="lin", c=[0, 0, sign], eq_val=[x, 0.0])
            if r["viol"] < 1e-7 and (not np.isfinite(out[i]) or r["f"] < sign * out[i]):
                out[i] = sign * r["f"]
    return out, res


def main():
    t0 = time.time()
    results = {}
    P = models.gtpl()
    tf = 2.0
    ns3 = 60 if QUICK else 200
    ns2 = 40 if QUICK else 100
    # ---------------- 1. base case + N convergence ----------------
    conv = {"planar": [], "3d": []}
    for N in ([10, 20, 40] if QUICK else [10, 20, 40, 80]):
        g = midpoint_gap(P, tf, N, True, ns2); g["N"] = N; conv["planar"].append(g)
        print("planar N", N, g["dist"], g["frac_at_best"], flush=True)
    for N in ([10, 20, 30] if QUICK else [10, 20, 40, 60]):
        g = midpoint_gap(P, tf, N, False, ns3); g["N"] = N; conv["3d"].append(g)
        print("3d N", N, g["dist"], g["frac_at_best"], g["z"], flush=True)
    results["gtpl_base"] = dict(tf=tf, omega_deg=30, delta_deg=15, conv=conv)
    # Mars-like
    Pm = models.mars()
    gm = {}
    for tfm in [2.0, 5.0, 7.5]:
        gm[tfm] = midpoint_gap(Pm, tfm, 40, False, ns3)
        print("mars tf", tfm, gm[tfm]["dist"], gm[tfm]["Px"], flush=True)
    results["mars"] = gm
    json.dump(results, open(OUT + "t1_base.json", "w"), indent=1)
    print("base done", time.time() - t0, flush=True)

    # ---------------- 2. section plot of R (planar controls and 3D y=0 section) ----------------
    N2 = N3 = 40
    ex = models.extreme_arcs_M1(P, tf, N2)
    xs = np.linspace(-1.0, 1.0, 21 if QUICK else 41) * ex["Px"] * 1.0
    zlo2, r2 = zmin_curve(P, tf, N2, True, xs, 20)
    zhi2, _ = zmin_curve(P, tf, N2, True, xs, 10, sign=-1)
    zlo3, _ = zmin_curve(P, tf, N3, False, xs, 20 if QUICK else 60, warm=[r["x"] for r in r2])
    rng = np.random.default_rng(1)
    cloud = mc_cloud_planar(P, tf, N2, 20000, rng)
    near = np.array(conv["3d"][-1]["z"])
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].plot(cloud[:, 0], cloud[:, 1], ".", ms=1, color="0.7", label="random admissible controls (planar)")
    ax[0].plot(xs, zlo2, "b-", lw=2, label="lower boundary, planar controls")
    ax[0].plot(xs, zhi2, "b--", lw=1, label="upper boundary, planar controls")
    ax[0].plot(xs, zlo3, "r-", lw=2, label="lower boundary, 3D controls, section y=0")
    ax[0].plot([-ex["Px"], ex["Px"]], [ex["Mz"], ex["Mz"]], "k:", lw=1.5, label="chord P- P+ (in conv R)")
    ax[0].plot([-ex["Px"], ex["Px"]], [ex["Mz"], ex["Mz"]], "ko")
    ax[0].plot(0, ex["Mz"], "k*", ms=14, label="midpoint M")
    ax[0].plot(np.hypot(near[0], near[1]) * np.sign(near[0]), near[2], "gs", label="nearest point of R to M (3D NLP, |lateral| shown)")
    ax[0].set_xlabel("Dv_x [m/s]"); ax[0].set_ylabel("Dv_z [m/s]")
    ax[0].set_title(f"M1 set R (GTPL, tf={tf}s, w=30deg/s, delta=15deg, rho1/rho2=0.4, N={N2})", fontsize=9)
    ax[0].legend(fontsize=7, loc="upper right"); ax[0].set_aspect("equal")
    m = (np.abs(xs) <= ex["Px"])
    ax[1].plot(xs, zlo2 - ex["Mz"], "b-", label="planar")
    ax[1].plot(xs, zlo3 - ex["Mz"], "r-", label="3D (y=0)")
    ax[1].axhline(0, color="k", ls=":")
    ax[1].set_xlabel("Dv_x [m/s]"); ax[1].set_ylabel("z_min(x) - M_z [m/s]")
    ax[1].set_title("Dent: lower boundary above the chord => conv R != R")
    ax[1].legend()
    plt.tight_layout(); plt.savefig(OUT + "t1_R_section.png", dpi=130); plt.close()
    results["section"] = dict(xs=xs.tolist(), zlo_planar=zlo2.tolist(), zhi_planar=zhi2.tolist(), zlo_3d=zlo3.tolist())
    json.dump(results, open(OUT + "t1_base.json", "w"), indent=1)
    print("section done", time.time() - t0, flush=True)

    # ---------------- 3. gap sweeps (3D, within the proven regime delta + omega tf <= pi/2) ----------------
    Nsw = 30; nsw = 40 if QUICK else 80
    sweeps = {}

    def gap_job(Pp, tfp):
        exx = models.extreme_arcs_M1_cont(Pp, tfp)
        return (spec(Pp, tf=tfp, N=Nsw, planar=False), dict(mode="dist", target=[0, 0, exx["Mz"]])), exx

    def run_sweep(name, configs):
        jobs, exs = [], []
        for Pp, tfp in configs:
            j, e = gap_job(Pp, tfp); jobs.append(j); exs.append(e)
        res = run_batch(jobs, nsw, chunk=nsw // 4)
        out = []
        for (Pp, tfp), r, e in zip(configs, res, exs):
            out.append(dict(tf=tfp, omega_deg=Pp["omega"] / D2R, delta_deg=Pp["delta"] / D2R,
                            ratio=Pp["rho1"] / Pp["rho2"], alpha=Pp["alpha"], dist=float(np.sqrt(r["f"])), Px=e["Px"], Mz=e["Mz"],
                            regime=bool(Pp["delta"] + Pp["omega"] * tfp <= np.pi / 2 + 1e-9)))
        sweeps[name] = out
        print(name, [(round(o["dist"], 4), round(o["dist"] / o["Px"], 4)) for o in out], flush=True)

    # (a) omega in {10,30,60,120} deg/s, tf such that omega*tf in {15,30,45,60,75} deg (all in regime)
    cfg = []
    for om in [10, 30, 60, 120]:
        for ang in [15, 30, 45, 60, 75]:
            cfg.append((models.gtpl(omega=om * D2R), ang / om))
    run_sweep("omega_tf", cfg)
    # (b) delta sweep at tf=2, omega=30
    run_sweep("delta", [(models.gtpl(delta=d * D2R), 2.0) for d in [2, 5, 10, 15, 20, 25, 30]])
    # (c) rho1/rho2 sweep at tf=2, omega=30
    run_sweep("ratio", [(models.gtpl(rho1=r * 1000.0), 2.0) for r in [0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]])
    # (d) mass depletion on/off
    run_sweep("alpha", [(models.gtpl(alpha=a), 2.0) for a in [0.0, 5.66e-4, 2e-3, 5e-3]])
    results["sweeps"] = sweeps
    json.dump(results, open(OUT + "t1_base.json", "w"), indent=1)

    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    for om in [10, 30, 60, 120]:
        o = [r for r in sweeps["omega_tf"] if abs(r["omega_deg"] - om) < 1e-6]
        ax[0, 0].plot([r["omega_deg"] * r["tf"] for r in o], [r["dist"] for r in o], "o-", label=f"w={om} deg/s")
    ax[0, 0].set_xlabel("omega*tf [deg]"); ax[0, 0].set_ylabel("dist(M, R) [m/s]"); ax[0, 0].legend(); ax[0, 0].set_title("gap vs omega tf (delta=15)")
    o = sweeps["delta"]; ax[0, 1].plot([r["delta_deg"] for r in o], [r["dist"] for r in o], "o-", label="dist")
    ax[0, 1].plot([r["delta_deg"] for r in o], [r["dist"] / r["Px"] for r in o], "s--", label="dist / |P_x|")
    ax[0, 1].set_xlabel("gimbal delta [deg]"); ax[0, 1].legend(); ax[0, 1].set_title("tf=2, w=30 deg/s")
    o = sweeps["ratio"]; ax[1, 0].plot([r["ratio"] for r in o], [r["dist"] for r in o], "o-", label="dist")
    ax[1, 0].plot([r["ratio"] for r in o], [r["dist"] / r["Px"] for r in o], "s--", label="dist / |P_x|")
    ax[1, 0].set_xlabel("rho1/rho2"); ax[1, 0].legend(); ax[1, 0].set_title("tf=2, w=30, delta=15")
    o = sweeps["alpha"]; ax[1, 1].plot([r["alpha"] if "alpha" in r else i for i, r in enumerate(o)], [r["dist"] for r in o], "o-")
    ax[1, 1].set_xticks(range(len(o))); ax[1, 1].set_xticklabels(["0", "5.66e-4", "2e-3", "5e-3"])
    ax[1, 1].set_xlabel("alpha [s/m]"); ax[1, 1].set_ylabel("dist(M,R)"); ax[1, 1].set_title("mass depletion")
    plt.tight_layout(); plt.savefig(OUT + "t1_gap_sweeps.png", dpi=130); plt.close()

    # N convergence plot
    fig, ax = plt.subplots(figsize=(5, 4))
    for k, lab in [("planar", "planar"), ("3d", "3D")]:
        ax.plot([g["N"] for g in conv[k]], [g["dist"] for g in conv[k]], "o-", label=lab)
    ax.set_xlabel("N (intervals)"); ax.set_ylabel("dist(M_cont, R_N) [m/s]"); ax.set_title("discretization convergence (GTPL tf=2)")
    ax.legend(); plt.tight_layout(); plt.savefig(OUT + "t1_N_convergence.png", dpi=130); plt.close()
    print("all done", time.time() - t0)


if __name__ == "__main__":
    main()
