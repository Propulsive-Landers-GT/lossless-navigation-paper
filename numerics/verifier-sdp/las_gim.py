"""[verifier-sdp] Rigorous-certificate attempt for the gimbal gaps at small N:
order-2 Lasserre (own implementation, vlas.py) vs degree-2 Shor vs genuine multistart.
Lasserre-2 is a valid lower bound on the genuine optimum, so Lasserre-2 > Shor + tol certifies the
Shor/Gram lift is NOT exact on that instance (no reliance on NLP global optimality).
Picks the largest-gap N=3 (and a few N=4) instances from results/gim.jsonl."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vgim import Gim
from vext import fixed_thrust
from vlas import lasserre2

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

if __name__ == "__main__":
    R = [json.loads(l) for l in open(os.path.join(OUT, "gim.jsonl"))]
    R = [r for r in R if r.get("part") == "screen" and r["deg"] is not None and r["rel"] > 1e-3 and r["absn"] > 1e-7]
    picks = []
    for N, k in ((3, 6), (4, 2)):
        for deg in (15.0, 40.0):
            c = sorted([r for r in R if r["N"] == N and r["deg"] == deg], key=lambda r: -r["rel"] * (r["L"] > 1e-6))
            picks += c[:k // 2 if N == 4 else k // 2]
    rng = np.random.default_rng(99)
    rows = []
    for r in picks:
        N, deg, wtf = r["N"], r["deg"], r["wtf"]
        tf = 4.0; om = wtf / tf; delta = np.deg2rad(deg)
        wv, wr = np.array(r["wv"]), np.array(r["wr"])
        for both in (True, False):
            G = Gim(N, tf, om, delta, a=11.0, both=both)
            s = G.sdp(wv, wr)
            b, x, fs = G.best3(wv, wr, rng, 300, Zv=s["Z"])
            SC = 11.0 * tf               # rescale readout by 1/SC (cost by 1/SC^2) for conditioning
            F = fixed_thrust(N, tf, om, np.array([wr, wv]) / SC, readout="rv", delta=delta,
                             accel=np.full(N + 1, 11.0 / SC), both=both)
            sf = F.sdp(); sf["val"] *= SC ** 2
            t0 = time.time()

            def L2(solver, tol):
                try:
                    o = lasserre2(F, solver=solver, tol=tol); o["val"] *= SC ** 2; return o
                except Exception as e:
                    return dict(val=np.nan, status="fail")
            l2 = L2("CLARABEL", 1e-8)
            l2s = L2("SCS", 1e-7) if N == 3 else dict(val=np.nan, status="skip")
            row = dict(N=N, deg=deg, wtf=wtf, both=both, wv=wv.tolist(), wr=wr.tolist(), gram=s["val"], gram_st=s["status"],
                       shor=sf["val"], shor_st=sf["status"], las2=l2["val"], las2_st=l2["status"], las2_scs=l2s["val"],
                       las2_scs_st=l2s["status"], genuine=b, nhit=int(np.sum(fs < b + 1e-7 * max(1, b))), nfeas=int(len(fs)),
                       secs=time.time() - t0)
            rows.append(row)
            print(f"N={N} deg={deg} wtf={wtf:.3f} both={both}: Gram {s['val']:.7g} [{s['status'][:4]}]  Shor {sf['val']:.7g}  "
                  f"Las2 {l2['val']:.7g} [{l2['status'][:6]}] (SCS {l2s['val']:.7g})  genuine {b:.7g} "
                  f"(hits {row['nhit']}/{row['nfeas']})  {row['secs']:.0f}s", flush=True)
            json.dump(rows, open(os.path.join(OUT, "las_gim.json"), "w"), indent=1)
