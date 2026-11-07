"""Independent test of [redteam-lift] Conjecture CSD2 (degree-2 Shor / Hilbert-sphere lift EXACT for fixed-thrust
5DOF min-landing-error, tent attitude, inner discretization).

SDP: numerics/redteam-lift/sdp_clean.py::build (their code, unchanged; coordinate 0 = vertical).
Genuine optimum (upper bound): my ReachM1 NLP (tent=True, fixed thrust rho1=rho2=a*m0, alpha=0) with the SAME
discretization, objective |Dv - wv|^2 + |Dr - wr|^2, multistart (incl. coning guesses).
Exactness on an instance  <=>  NLP_min - SDP = 0 (to solver tolerance).  A positive gap with a well-converged
multistart is evidence against CSD2 (or a missed NLP optimum; we warm-start from the SDP rank-3 projection too).

Targets: (A) GTPL-realistic above-ground boundary data (r0z 10-50 m, v0z -8..0, lateral offsets) converted to
(wv, wr); (B) asymmetric random targets near the dent; (C) larger N and omega.
Output: results/c1_csd2.json
"""
import sys, json, time
import numpy as np
import cvxpy as cp
sys.path.insert(0, "redteam-lift")
from sdp_clean import build
import models
from runner import run_batch

G0 = 9.80665


def sdp(wv, wr, N, tf, om, dl, a):
    G, cons, obj = build(wv, wr, N, tf, om, dl, a1=a)
    p = cp.Problem(cp.Minimize(obj), cons)
    p.solve(solver=cp.CLARABEL)
    ev = np.linalg.eigvalsh(G.value) if G.value is not None else np.array([np.nan])
    rank = int(np.sum(ev > 1e-6 * max(ev.max(), 1)))
    return p.value, p.status, rank, G.value


def to_mine(w):   # theirs: (vert, x, y)  -> mine: (x, y, vert)
    return np.array([w[1], w[2], w[0]])


def make_cases():
    rng = np.random.default_rng(5)
    a = 11.0
    cases = []
    # (A) GTPL-realistic above-ground data
    for i in range(10):
        tf = rng.uniform(4, 6); om = 0.4; N = 16 if i < 5 else 24
        r0 = np.array([rng.uniform(-10, 10), rng.uniform(-10, 10), rng.uniform(10, 50)])
        v0 = np.array([rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-8, 0)])
        dv = G0 * tf * np.array([0, 0, 1.0]) - v0
        dr = dv * tf - 0.5 * G0 * tf ** 2 * np.array([0, 0, 1.0]) - r0
        cases.append(dict(set="A", N=N, tf=tf, om=om, wv_m=dv, wr_m=dr))
    # (B) asymmetric targets near the extreme-arc chord (dent region), tent
    for i in range(8):
        tf = 4.0; om = np.deg2rad(30); N = 16
        P = models.gtpl(rho1=a, rho2=a, m0=1.0, alpha=0.0, omega=om)
        ex = models.extreme_arcs_M1(P, tf, N, tent=True)
        lam = rng.uniform(0.2, 0.8); rot = rng.uniform(0.5, np.pi)
        Pv = np.array([ex["Px"], 0, ex["Mz"]]); Pr = np.array([ex["Rx"], 0, ex["Rz"]])
        Rz = np.array([[np.cos(rot), -np.sin(rot), 0], [np.sin(rot), np.cos(rot), 0], [0, 0, 1]])
        up = rng.uniform(0, 1.5)
        dv = lam * Pv + (1 - lam) * Rz @ Pv + np.array([0, 0, up]) + rng.normal(0, 0.3, 3)
        dr = lam * Pr + (1 - lam) * Rz @ Pr + np.array([0, 0, up * tf / 2]) + rng.normal(0, 0.6, 3)
        cases.append(dict(set="B", N=N, tf=tf, om=om, wv_m=dv, wr_m=dr))
    # (C) larger N / omega, asymmetric
    for i, (N, omd) in enumerate([(32, 30), (32, 60), (40, 60), (24, 90)]):
        tf = 3.0; om = np.deg2rad(omd)
        P = models.gtpl(rho1=a, rho2=a, m0=1.0, alpha=0.0, omega=om)
        ex = models.extreme_arcs_M1(P, tf, N, tent=True)
        Pv = np.array([ex["Px"], 0, ex["Mz"]]); Pr = np.array([ex["Rx"], 0, ex["Rz"]])
        rot = rng.uniform(1.0, 2.5); lam = rng.uniform(0.3, 0.7)
        Rz = np.array([[np.cos(rot), -np.sin(rot), 0], [np.sin(rot), np.cos(rot), 0], [0, 0, 1]])
        dv = lam * Pv + (1 - lam) * Rz @ Pv + rng.normal(0, 0.3, 3); dr = lam * Pr + (1 - lam) * Rz @ Pr + rng.normal(0, 0.5, 3)
        cases.append(dict(set="C", N=N, tf=tf, om=om, wv_m=dv, wr_m=dr))
    return cases, a


def main():
    cases, a = make_cases(); dl = np.deg2rad(15)
    # NLP jobs
    jobs = []
    for c in cases:
        P = models.gtpl(rho1=a, rho2=a, m0=1.0, alpha=0.0, omega=c["om"])
        spec = ("M1", P, dict(tf=c["tf"], N=c["N"], planar=False, use_r=True, tent=True))
        jobs.append((spec, dict(mode="dist", target=np.concatenate([c["wv_m"], c["wr_m"]]))))
    t0 = time.time()
    nl = run_batch(jobs, 32, chunk=16)
    print("NLP done", round(time.time() - t0), "s", flush=True)
    out = []
    for c, r in zip(cases, nl):
        wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
        val, st, rank, Gv = sdp(wv, wr, c["N"], c["tf"], c["om"], dl, a)
        gap = r["f"] - val
        row = dict(set=c["set"], N=c["N"], tf=c["tf"], om_deg=float(np.degrees(c["om"])), nlp=float(r["f"]), sdp=float(val),
                   status=st, rank=rank, gap=float(gap), rel=float(gap / max(abs(r["f"]), 1e-9)), nok=r["nok"],
                   n_at_best=int(np.sum(np.array(r["fs"]) < r["fs"][0] + 1e-7 * max(1, r["fs"][0]))) if r["fs"] else 0)
        out.append(row)
        print(f"{row['set']} N={row['N']:2d} tf={row['tf']:.2f} w={row['om_deg']:5.1f}: NLP={row['nlp']:.6f} SDP={row['sdp']:.6f} "
              f"gap={row['gap']:.2e} rel={row['rel']:.1e} rank={rank} {st} n@best={row['n_at_best']}/{row['nok']}", flush=True)
    json.dump(out, open("results/c1_csd2.json", "w"), indent=1)


if __name__ == "__main__":
    main()
