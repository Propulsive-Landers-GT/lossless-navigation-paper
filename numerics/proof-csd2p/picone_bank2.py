import os, sys, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
from picone import criterion, stress, unpack, primer, jacobi_m
srcs, out, maxn = sys.argv[1].split(","), sys.argv[2], int(sys.argv[3])
rng = np.random.default_rng(11)
recs = []
for s in srcs: recs += [json.loads(l) for l in open(s)]
for r in recs:
    if "L_cvx" in r:
        r["model"] = "cvx%d" % int(r["deg"]); r["L"] = r["L_cvx"]; r["U"] = r["U_cvx"]; r["kind"] = r["label"]
recs = [r for r in recs if r["L"] > 1e-6 * (r.get("U", 1) + 1e-9) and r["L"] > 1e-8]
rng.shuffle(recs)
f = open(out, "w")
for r in recs[:maxn]:
    model = r["model"]; delta = None if model == "d=b" else np.deg2rad(int(model[3:]))
    G = Gim(r["N"], 4.0, r["wtf"] / 4.0, delta, a=11.0, cvx=(delta is not None), terminal=r.get("term", True))
    wv, wr = np.array(r["wv"]), np.array(r["wr"])
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 10, Zv=s["Z"])
    if x is None: continue
    t, c = criterion(G, x, wv, wr); ev, res = stress(G, x, wv, wr); h, k = jacobi_m(G, x, wv, wr)
    rel = (b - s["val"]) / max(abs(b), 1e-12)
    rec = dict(N=r["N"], model=model, term=r.get("term", True), wtf=r["wtf"], kind=r["kind"], L=s["val"], U=b, rel=rel, e4=s["e4"],
               crit=t, evmin=float(ev[0] / max(abs(ev[-1]), 1e-300)), nneg=int(np.sum(ev < -1e-7 * abs(ev[-1]))), res=res, kcross=k,
               hmin=(float(h.min()) if h is not None else None))
    f.write(json.dumps(rec) + "\n"); f.flush()
    print(f"{r['N']} {model} wtf={r['wtf']:.2f} cost={b:.3e} rel={rel:+.1e} crit={t:+.2e} evmin={rec['evmin']:+.1e} nneg={rec['nneg']} crossings={k} res={res:.0e}", flush=True)
