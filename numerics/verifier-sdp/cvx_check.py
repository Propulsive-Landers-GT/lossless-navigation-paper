"""[verifier-sdp] Convexified-lens gimbal model (||d_k|| <= 1, <d_k,b_k>,<d_k,b_k+1> >= cos delta;
= discrete relaxed controls, alpha = 0): is ITS Gram lift exact?  Re-tests case 12 and every
unit-d gap instance found by run_gim.py.  Writes results/cvx_check.jsonl."""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vgim import Gim

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

if __name__ == "__main__":
    rng = np.random.default_rng(77)
    fout = open(os.path.join(OUT, "cvx_check.jsonl"), "w")
    cases = [dict(N=16, deg=15.0, wtf=4.0 * np.deg2rad(30), wv=[5.0939, 21.9914, 32.1819],
                  wr=[8.2825, 44.1701, 64.908], label="case12", L_unit=0.0275290, U_unit=0.0282327)]
    R = [json.loads(l) for l in open(os.path.join(OUT, "gim.jsonl"))]
    for r in R:
        if r.get("part") == "screen" and r["deg"] is not None and r["rel"] > 1e-4 and r["absn"] > 1e-9:
            cases.append(dict(N=r["N"], deg=r["deg"], wtf=r["wtf"], wv=r["wv"], wr=r["wr"], label="unit-gap",
                              L_unit=r["L"], U_unit=r["U"]))
    print(f"{len(cases)} instances", flush=True)
    worst = 0.0
    Gs = {}
    for c in cases:
        key = (c["N"], c["deg"], c["wtf"])
        if key not in Gs:
            Gs[key] = Gim(c["N"], 4.0, c["wtf"] / 4.0, np.deg2rad(c["deg"]), a=11.0, cvx=True)
        G = Gs[key]
        wv, wr = np.array(c["wv"]), np.array(c["wr"])
        s = G.sdp(wv, wr)
        b, x, fs = G.best3(wv, wr, rng, 60 if c["N"] <= 6 else 80, Zv=s["Z"])
        S2 = (11.0 * 4.0) ** 2 * (1 + 4.0 ** 2 / 4)
        absn = (b - s["val"]) / S2
        rel = (b - s["val"]) / max(b, 1e-12)
        if absn > 1e-9:
            worst = max(worst, rel)
        rec = dict(c, L_cvx=s["val"], st=s["status"], e4=s["e4"], U_cvx=b, rel=rel, absn=absn,
                   nhit=int(np.sum(fs < b + 1e-7 * max(1, b))), nfeas=int(len(fs)))
        fout.write(json.dumps(rec) + "\n"); fout.flush()
        print(f"{c['label']:8s} N={c['N']} deg={c['deg']} wtf={c['wtf']:.3f}: unit L={c['L_unit']:.6g} U={c['U_unit']:.6g} | "
              f"cvx L={s['val']:.8g} [{s['status'][:4]}] U={b:.8g} rel={rel:.1e} absn={absn:.1e} e4/e1={s['e4']:.1e}", flush=True)
    print(f"worst cvx rel gap (absn>1e-9): {worst:.2e}")
