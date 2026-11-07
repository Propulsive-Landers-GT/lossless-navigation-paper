"""[proof-csd2p] Verify the index identity (math/09 Thm 5.2):  neg(Q) = neg(Z) - p0(C_yw),
Z = Q - C (local cable part of the stress), C_yw = sum_c y_{c,h} w_{c,h}^T (lateral residual/target cross-covariance),
p0 = number of nonnegative eigenvalues; plus neg(Z) >= k-1 with k = #crossings of the primer plane (Jacobi field h_m)."""
import os, sys, json, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
import picone
from picone import stress, unpack, primer, jacobi_m, criterion
picone.stress.full = True
srcs, out, maxn = sys.argv[1].split(","), sys.argv[2], int(sys.argv[3])
rng = np.random.default_rng(5)
recs = []
for s in srcs: recs += [json.loads(l) for l in open(s)]
for r in recs:
    if "L_cvx" in r: r["model"] = "cvx%d" % int(r["deg"]); r["L"] = r["L_cvx"]; r["kind"] = r["label"]
recs = [r for r in recs if r["L"] > 1e-8]
rng.shuffle(recs)
f = open(out, "w")
for r in recs[:maxn]:
    model = r["model"]; delta = None if model == "d=b" else np.deg2rad(int(model[3:]))
    G = Gim(r["N"], 4.0, r["wtf"] / 4.0, delta, a=11.0, cvx=(delta is not None), terminal=r.get("term", True))
    wv, wr = np.array(r["wv"]), np.array(r["wr"])
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 10, Zv=s["Z"])
    if x is None: continue
    Q, C, res = stress(G, x, wv, wr); Zm = Q - C
    sc = np.abs(Q).max(); tol = 1e-7 * sc
    eq, ez = np.linalg.eigvalsh(Q), np.linalg.eigvalsh(Zm)
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    Cyw = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2])
    asym = abs(Cyw[0, 1] - Cyw[1, 0]) / (np.abs(Cyw).max() + 1e-300)
    ec = np.linalg.eigvalsh(0.5 * (Cyw + Cyw.T))
    p0 = int(np.sum(ec >= -1e-9 * np.abs(ec).max()))
    h, k = jacobi_m(G, x, wv, wr); t, _ = criterion(G, x, wv, wr)
    rec = dict(N=r["N"], model=model, wtf=r["wtf"], rel=(b - s["val"]) / max(b, 1e-12), cost=b, res=res, k=k, crit=t,
               negQ=int(np.sum(eq < -tol)), negZ=int(np.sum(ez < -tol)), zeroZ=int(np.sum(np.abs(ez) <= tol)), p0=p0,
               ecyw=list(map(float, ec / (np.abs(ec).max() + 1e-300))), asym=asym, minZ=float(ez[0] / sc), minQ=float(eq[0] / sc),
               wv=list(wv), wr=list(wr), term=r.get('term', True), hint=(list(map(float, h)) if h is not None else None),
               mud_min=float(np.min(np.diag(Zm)[G.nb:]) / sc) if G.gim else 0.0)
    ok = rec["negQ"] == rec["negZ"] - p0
    f.write(json.dumps(rec) + "\n"); f.flush()
    print(f"N={r['N']} {model} wtf={r['wtf']:.2f} k={k} crit={t:+.1e} negZ={rec['negZ']} (zero {rec['zeroZ']}) p0={p0} negQ={rec['negQ']} "
          f"identity={'OK' if ok else 'FAIL'} Cyw eig={np.round(rec['ecyw'],3)} asym={asym:.0e} res={res:.0e} rel={rec['rel']:+.0e}", flush=True)
