"""[proof-csd2p] Discretization mechanism in stress language: at genuine UNIT-d optima the norm multipliers mu_d
on ||d_k||^2=1 can be negative; Q restricted to {E-perp tilts of d only, zeta with sum cv*zeta = sum cr*zeta = 0}
is diag(mu_d) + (cv cv^T + cr cr^T) -> indefinite once enough mu_d<0.  In D^cvx mu_d >= 0 (KKT sign)."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
import picone
picone.stress.full = True
from picone import stress
rng = np.random.default_rng(3)
cases = [dict(N=16, deg=15.0, wtf=4*np.deg2rad(30), wv=[5.0939, 21.9914, 32.1819], wr=[8.2825, 44.1701, 64.908], label="case12")]
R = [json.loads(l) for l in open("../verifier-sdp/results/cvx_check.jsonl")][1:]
rng.shuffle(R); cases += R[:12]
for c in cases:
    wv, wr = np.array(c["wv"]), np.array(c["wr"])
    out = []
    for cvx in (False, True):
        G = Gim(c["N"], 4.0, c["wtf"] / 4.0, np.deg2rad(c["deg"]), a=11.0, cvx=cvx)
        s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 30, Zv=s["Z"])
        Q, C, res = stress(G, x, wv, wr); nb = G.nb
        mu = np.diag(Q - C)[nb:]
        Qdd = Q[nb:, nb:]; Gm = np.vstack([G.gv, G.gr]).T
        Uo = np.linalg.svd(Gm, full_matrices=True)[0][:, 2:]   # zeta orthogonal to cv, cr
        ev = np.linalg.eigvalsh(Uo.T @ Qdd @ Uo)
        out.append(f"{'cvx ' if cvx else 'unit'}: SDP={s['val']:.6g} gen={b:.6g} #mu_d<0={int(np.sum(mu < -1e-9*np.abs(mu).max()))} "
                   f"min eig Q|zeta-perp={ev[0]/np.abs(Q).max():+.1e} min eig Q={np.linalg.eigvalsh(Q)[0]/np.abs(Q).max():+.1e}")
    print(f"{c['label']} N={c['N']} deg={c['deg']} wtf={c['wtf']:.2f} | " + " | ".join(out), flush=True)
