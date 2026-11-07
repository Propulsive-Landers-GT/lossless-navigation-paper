"""[verifier-sdp] Heavy re-check of glide-slope instances with an apparent gap (results/glide.jsonl):
300 random starts + 200 Gaussian samples from the Shor moment matrix (normalized), then ipopt."""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vcore import EZ
from vext import fixed_thrust, starts_fixed
from run_ext import altitude_path

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
R = [json.loads(l) for l in open(os.path.join(OUT, "glide.jsonl"))]
R = [r for r in R if r["variant"] == "G2" and r["relgap"] > 1e-4]
rng = np.random.default_rng(8)
out = []
for r in R:
    N, tf, om, deg = r["N"], r["tf"], r["omega"], r["deg"]
    tang = np.tan(np.radians(deg)); r0 = np.array(r["r0"]); v0 = np.array(r["v0"]); a = 1.5; g = 1.0
    Q = np.array([-(r0 + v0 * tf - 0.5 * g * tf ** 2 * EZ), -(v0 - g * tf * EZ)])
    F = fixed_thrust(N, tf, om, Q, readout="rv", accel=np.full(N + 1, a), path=altitude_path(r0, v0, g, a, "G2", tang=tang))
    s = F.sdp()
    z = s["z"]; Y = s["M"][1:, 1:]; C = Y - np.outer(z, z)
    w, V = np.linalg.eigh((C + C.T) / 2); Cs = V * np.sqrt(np.clip(w, 0, None))
    starts = starts_fixed(F, N, rng, 300, omega=om)
    for j in range(200):
        x = z + Cs @ rng.normal(size=len(z))
        B = x.reshape(-1, 3); B /= np.linalg.norm(B, axis=1, keepdims=True)
        starts.append(B.ravel())
    b = F.best_of(starts)
    fs = np.array(b["fs"])
    rec = dict(N=N, tf=tf, omega=om, deg=deg, sdp=s["val"], rank=s["rank"], U_before=r["U"], U_heavy=b["f"],
               rel=(b["f"] - s["val"]) / b["f"], nhit=int(np.sum(fs < b["f"] + 1e-7)), nfeas=int(len(fs)))
    out.append(rec)
    print(rec, flush=True)
json.dump(out, open(os.path.join(OUT, "glide_check.json"), "w"), indent=1)
