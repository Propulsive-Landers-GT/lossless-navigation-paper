"""Polish the CSD2 instances where NLP > SDP: factor the SDP Gram (components G[i,0:3] give each vector in the
fixed frame), normalize, use as initial guess for the genuine NLP, and also report the SDP rank and the genuine
value of the rank-3 projection.  Decides 'NLP missed the optimum' vs 'genuine SDP gap'."""
import json, sys
import numpy as np
import cvxpy as cp
sys.path.insert(0, "redteam-lift")
from sdp_clean import build
import models
from c1_csd2_check import make_cases

cases, a = make_cases(); dl = np.deg2rad(15)
res = json.load(open("results/c1_csd2.json"))
out = []
for i, (c, r) in enumerate(zip(cases, res)):
    if r["gap"] < 1e-4 * max(1, abs(r["nlp"])) and r["gap"] < 1e-5:
        continue
    N, tf, om = c["N"], c["tf"], c["om"]
    wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
    G, cons, obj = build(wv, wr, N, tf, om, dl, a1=a)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL)
    Gv = G.value; ev = np.linalg.eigvalsh(Gv)[::-1]
    nbi = N - 1
    def vec(idx):
        v = Gv[idx, 0:3]; v = np.array([v[1], v[2], v[0]]); return v / np.linalg.norm(v)
    b = np.zeros((3, N + 1)); b[:, 0] = b[:, N] = [0, 0, 1]
    for k in range(1, N):
        b[:, k] = vec(3 + k - 1)
    d = np.stack([vec(3 + nbi + k) for k in range(N)], 1)
    P = models.gtpl(rho1=a, rho2=a, m0=1.0, alpha=0.0, omega=om)
    R = models.ReachM1(P, tf, N, planar=False, use_r=True, tent=True)
    x0 = np.concatenate([a * np.ones(N), b.T.ravel(), d.T.ravel()])
    tgt = np.concatenate([c["wv_m"], c["wr_m"]])
    z0 = np.array(R.zf(x0)).ravel(); val0 = float(np.sum((z0 - tgt) ** 2))
    g0 = np.array(R.Gf(x0)).ravel(); viol0 = float(np.max(np.abs(g0 - np.clip(g0, R.lbg[:g0.size], R.ubg[:g0.size]))))
    rr = R.solve(x0, mode="dist", target=tgt)
    row = dict(i=i, set=c["set"], N=N, sdp=float(p.value), nlp_multistart=r["nlp"], eig_top6=ev[:6].tolist(),
               proj_value=val0, proj_viol=viol0, polished=rr["f"], polished_viol=rr["viol"])
    out.append(row)
    print(f"case {i} {c['set']}: SDP={p.value:.6f} NLPms={r['nlp']:.6f} eig={np.round(ev[:6], 5)} | rank-3 projection: value={val0:.6f} viol={viol0:.1e} "
          f"| polished NLP={rr['f']:.6f} viol={rr['viol']:.1e}", flush=True)
json.dump(out, open("results/c2_polish.json", "w"), indent=1)
