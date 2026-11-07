"""Evaluate the hemisphere (Picone) certificate and the discrete stress at genuine optima over instance banks."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
from picone import criterion, stress, unpack, primer
src, out = sys.argv[1], sys.argv[2]
maxn = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
rng = np.random.default_rng(7)
recs = [json.loads(l) for l in open(src)]
rng.shuffle(recs)
f = open(out, "w"); cnt = 0
for r in recs[:maxn]:
    model = r["model"]; delta = None if model == "d=b" else np.deg2rad(int(model[3:]))
    term = r.get("term", True)
    G = Gim(r["N"], 4.0, r["wtf"] / 4.0, delta, a=11.0, cvx=(delta is not None), terminal=term)
    wv, wr = np.array(r["wv"]), np.array(r["wr"])
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 10, Zv=s["Z"])
    if x is None: continue
    t, c = criterion(G, x, wv, wr); ev, res = stress(G, x, wv, wr)
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    Pz_min = float(np.min(P[:, 2]) / (np.abs(P).max() + 1e-300)); bz_min = float(B[:, 2].min())
    rel = (b - s["val"]) / max(abs(b), 1e-12)
    rec = dict(N=r["N"], model=model, term=term, wtf=r["wtf"], kind=r["kind"], L=s["val"], U=b, rel=rel, e4=s["e4"], crit=t,
               evmin=float(ev[0] / max(abs(ev[-1]), 1e-300)), res=res, Pz_min=Pz_min, bz_min=bz_min, cost=b)
    f.write(json.dumps(rec) + "\n"); f.flush(); cnt += 1
    print(f"{r['N']} {model} wtf={r['wtf']:.2f} k={r['kind']} cost={b:.3e} rel={rel:+.1e} crit={t:+.2e} evmin/evmax={rec['evmin']:+.1e} res={res:.0e} Pzmin={Pz_min:+.2f} bzmin={bz_min:.2f}", flush=True)
