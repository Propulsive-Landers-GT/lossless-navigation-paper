"""[verifier-sdp] PSD stress check (Thm 2.4 of math/08): lambda_min(Hess_x L) at the best genuine optimum,
with ipopt multipliers.  For these isotropic QCQPs Hess L = Q_lambda (x) I_3, so lambda_min(Hess L) >= 0
<=> stress matrix PSD <=> (under LICQ) the genuine optimum is SDP-exact."""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vgim import Gim
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
rng = np.random.default_rng(3)
rows = []
wv12 = np.array([5.0939, 21.9914, 32.1819]); wr12 = np.array([8.2825, 44.1701, 64.908])
cases = [("case12 unit", 16, 15.0, 2.0944, False, wv12, wr12), ("case12 cvx", 16, 15.0, 2.0944, True, wv12, wr12)]
R = [json.loads(l) for l in open(os.path.join(OUT, "cvx_check.jsonl"))][1:]
rng.shuffle(R)
for r in R[:16]:
    cases.append((f"gap-inst unit", r["N"], r["deg"], r["wtf"], False, np.array(r["wv"]), np.array(r["wr"])))
    cases.append((f"gap-inst cvx", r["N"], r["deg"], r["wtf"], True, np.array(r["wv"]), np.array(r["wr"])))
C = sum(([json.loads(l) for l in open(os.path.join(OUT, f))] for f in os.listdir(OUT) if f.startswith("csd2p_") and f.endswith(".jsonl")), [])
C = [c for c in C if c["model"] == "d=b" and c["e4"] > 1e-7 and c["U"] > 1e-6][:8]
for c in C:
    cases.append(("d=b rank>3", c["N"], None, c["wtf"], False, np.array(c["wv"]), np.array(c["wr"])))
for lab, N, deg, wtf, cvx, wv, wr in cases:
    G = Gim(N, 4.0, wtf / 4.0, None if deg is None else np.deg2rad(deg), a=11.0, cvx=cvx)
    s = G.sdp(wv, wr)
    b, x, fs = G.best3(wv, wr, rng, 40 if N <= 8 else 30, Zv=s["Z"])
    lmin, lmax, f, v = G.stress_min(x, wv, wr)
    row = dict(label=lab, N=N, deg=deg, wtf=wtf, cvx=cvx, sdp=s["val"], genuine=b, gap_rel=(b - s["val"]) / max(b, 1e-12),
               lam_min=lmin, lam_max=lmax, lam_min_rel=lmin / max(abs(lmax), 1e-12), viol=v)
    rows.append(row)
    print(f"{lab:14s} N={N} deg={deg} wtf={wtf:.2f}: SDP {s['val']:.7g} genuine {b:.7g} rel {row['gap_rel']:.1e} | "
          f"lam_min(HessL) {lmin:.3e} (rel {row['lam_min_rel']:.1e})", flush=True)
json.dump(rows, open(os.path.join(OUT, "stress.json"), "w"), indent=1)
