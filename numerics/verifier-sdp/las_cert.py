"""[verifier-sdp] Order-2 Lasserre certificate for unit-d gimbal gaps at N=3 (two instances), with two solvers.
Las2 is a valid lower bound on the genuine optimum; Las2 >> Shor (beyond solver accuracy) certifies a Shor gap."""
import os, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vext import fixed_thrust
from vlas import lasserre2
from vgim import Gim
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
R = [json.loads(l) for l in open(os.path.join(OUT, "gim.jsonl"))]
picks = []
for deg in (15.0, 40.0):
    c = sorted([r for r in R if r.get("part") == "screen" and r["N"] == 3 and r["deg"] == deg and r["L"] > 1e-3],
               key=lambda r: -r["rel"])
    picks.append(c[0])
rows = []
rng = np.random.default_rng(5)
for r in picks:
    SC = 44.0
    delta = np.deg2rad(r["deg"])
    F = fixed_thrust(3, 4.0, r["wtf"] / 4, np.array([r["wr"], r["wv"]]) / SC, readout="rv", delta=delta,
                     accel=np.full(4, 11 / SC), both=True)
    s = F.sdp()
    G = Gim(3, 4.0, r["wtf"] / 4, delta, a=11.0, both=True)
    b, x, fs = G.best3(np.array(r["wv"]), np.array(r["wr"]), rng, 1000)
    row = dict(deg=r["deg"], wtf=r["wtf"], wv=r["wv"], wr=r["wr"], shor=s["val"] * SC ** 2, shor_st=s["status"],
               genuine=b, nhit=int(np.sum(fs < b + 1e-7)), nfeas=int(len(fs)))
    for solver, tol in (("CLARABEL", 1e-7), ("SCS", 1e-6)):
        t0 = time.time()
        try:
            l = lasserre2(F, solver=solver, tol=tol)
            row[f"las2_{solver}"] = l["val"] * SC ** 2; row[f"las2_{solver}_st"] = l["status"]
        except Exception as e:
            row[f"las2_{solver}"] = None; row[f"las2_{solver}_st"] = "fail:" + str(e)[:40]
        row[f"secs_{solver}"] = time.time() - t0
        print(row, flush=True)
    rows.append(row)
    json.dump(rows, open(os.path.join(OUT, "las_cert.json"), "w"), indent=1)
