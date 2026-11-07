"""Small-N analog of the CSD2 counterexample, plus an order-2 Lasserre certificate.
(1) Search N=3,4 (fixed thrust a1=5, tent, tf=4, w=30 deg/s, delta=15 deg, same as redteam-lift/lasserre2.py)
    over targets near rotated tent-arc mixtures. Keep instances whose well-posed SDP (sdp_clean.build) has rank >= 4.
(2) Genuine 3D minimum by my ReachM1 NLP multistart (identical discretization).
(3) For the best instance (largest NLP - SDP), run the order-2 Lasserre bound (redteam-lift/lasserre2.py::bound).
    If L2 > SDP (order 1), the order-1 relaxation is certified lossy: L2 <= true 3D minimum.
Usage: .venv/bin/python c5_smallN.py <N> [ntargets]
"""
import sys, json, time
import numpy as np
import cvxpy as cp
sys.path.insert(0, "redteam-lift")
from sdp_clean import build
import models
from runner import run_batch

N = int(sys.argv[1]); NT = int(sys.argv[2]) if len(sys.argv) > 2 else 200
A1 = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), A1


def sdp(wv, wr):
    G, cons, obj = build(wv, wr, N, tf, om, dl, a1=a1)
    p = cp.Problem(cp.Minimize(obj), cons)
    p.solve(solver=cp.CLARABEL, tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11)
    ev = np.linalg.eigvalsh(G.value)[::-1]
    return float(p.value), ev


def main():
    h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
    cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
    rng = np.random.default_rng(N)
    cands = []
    t0 = time.time()
    for j in range(NT):
        lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(-0.5, 1.5)
        R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
        wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]) + rng.normal(0, 0.2, 3) * rng.choice([0, 1])
        wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0]) + rng.normal(0, 0.4, 3) * rng.choice([0, 1])
        v, ev = sdp(wv, wr)
        if ev[3] > 1e-4 and v > 1e-6:
            cands.append(dict(j=j, wv=wv.tolist(), wr=wr.tolist(), sdp=v, eig=ev[:6].tolist()))
    print(f"N={N}: {len(cands)}/{NT} targets with SDP rank >= 4  ({time.time() - t0:.0f}s)", flush=True)
    P = models.gtpl(rho1=a1, rho2=a1, m0=1.0, alpha=0.0, omega=om)
    spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, tent=True))
    jobs = []
    for c in cands:
        wv, wr = np.array(c["wv"]), np.array(c["wr"])
        tgt = np.concatenate([[wv[1], wv[2], wv[0]], [wr[1], wr[2], wr[0]]])   # theirs (vert,x,y) -> mine (x,y,vert)
        jobs.append((spec, dict(mode="dist", target=tgt)))
    res = run_batch(jobs, 64, chunk=32)
    for c, r in zip(cands, res):
        c["nlp"] = float(r["f"]); c["gap"] = c["nlp"] - c["sdp"]; c["rel"] = c["gap"] / max(c["nlp"], 1e-12)
    cands.sort(key=lambda c: -c["gap"])
    for c in cands[:8]:
        print(f"  j={c['j']}: SDP={c['sdp']:.6e} NLP={c['nlp']:.6e} gap={c['gap']:.3e} rel={c['rel']:.2e} eig4={c['eig'][3]:.3e}", flush=True)
    json.dump(cands, open(f"results/c5_smallN_N{N}_a{a1:g}.json", "w"), indent=1)
    if not cands or cands[0]["gap"] <= 1e-6 or N > 5:
        print("no gap candidate"); return
    best = cands[0]
    # order-2 Lasserre bound (their implementation; module reads N from argv[2])
    sys.argv = ["lasserre2.py", "0", str(N)]
    import lasserre2
    lasserre2.a1 = a1   # objective() reads the module global at call time
    assert lasserre2.N == N
    t1 = time.time()
    v2, st = lasserre2.bound(np.array(best["wv"]), np.array(best["wr"]))
    best["lasserre2"] = float(v2); best["lasserre2_status"] = st
    print(f"BEST j={best['j']}: order-1 SDP={best['sdp']:.8e}  order-2 Lasserre={v2:.8e} ({st}, {time.time() - t1:.0f}s)  "
          f"3D NLP={best['nlp']:.8e}  => certified gap >= {v2 - best['sdp']:.3e}" , flush=True)
    json.dump(cands, open(f"results/c5_smallN_N{N}_a{a1:g}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
