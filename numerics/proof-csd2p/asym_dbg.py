import os, sys, json, numpy as np
sys.path.insert(0, "../verifier-sdp")
from vgim import Gim
from picone import unpack, primer
R = [json.loads(l) for l in open("../verifier-sdp/results/idx_full.jsonl")]
R = [r for r in R if r['k'] == 2 and r['p0'] == 1 and r['negZ'] == 2][:3]
rng = np.random.default_rng(0)
for r in R:
    G = Gim(r["N"], 4.0, r["wtf"] / 4.0, None, a=11.0, terminal=r.get("term", True))
    wv, wr = np.array(r["wv"]), np.array(r["wr"])
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 10, Zv=s["Z"])
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    Yv, Yr = G.gv @ D, G.gr @ D
    rot = np.cross(Yv, yv)[2] + np.cross(Yr, yr)[2]
    C = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2])
    # finite-difference rotation derivative of cost
    def J(th):
        Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
        return np.sum((Rz @ Yv - wv) ** 2) + np.sum((Rz @ Yr - wr) ** 2)
    print(r["N"], r["wtf"], "cost", b, "dJ/dth", (J(1e-6) - J(-1e-6)) / 2e-6, "rot", rot, "C", C.round(6), "|y|", np.linalg.norm(yv), np.linalg.norm(yr), "wv", wv.round(3))
