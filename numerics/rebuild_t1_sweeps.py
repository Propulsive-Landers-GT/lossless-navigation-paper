"""Rebuild results/t1_sweeps.json from results/t1_quick.log (the sweep section of t1_thmB.py quick run:
3D, N=30, 40 restarts per config; t1_base.json was later overwritten by the full run, which was stopped
under the compute budget before re-running the sweeps)."""
import re, json, ast
import numpy as np
import models
D2R = np.pi / 180
log = open("results/t1_quick.log").read()
cfg = {"omega_tf": [(om, ang / om, 15, 0.4, 5.66e-4) for om in [10, 30, 60, 120] for ang in [15, 30, 45, 60, 75]],
       "delta": [(30, 2.0, d, 0.4, 5.66e-4) for d in [2, 5, 10, 15, 20, 25, 30]],
       "ratio": [(30, 2.0, 15, r, 5.66e-4) for r in [0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0]],
       "alpha": [(30, 2.0, 15, 0.4, a) for a in [0.0, 5.66e-4, 2e-3, 5e-3]]}
out = {}
for name, cl in cfg.items():
    line = [l for l in log.splitlines() if l.startswith(name + " [")][0]
    nums = [float(x) for x in re.findall(r"[-+]?\d*\.\d+(?:e[-+]?\d+)?", line[len(name) + 1:])]; vals = list(zip(nums[0::2], nums[1::2]))
    rows = []
    for (om, tf, de, ra, al), (d, rel) in zip(cl, vals):
        P = models.gtpl(omega=om * D2R, delta=de * D2R, rho1=ra * 1000.0, alpha=al)
        ex = models.extreme_arcs_M1_cont(P, tf)
        rows.append(dict(tf=tf, omega_deg=om, delta_deg=de, ratio=ra, alpha=al, dist=d, Px=ex["Px"], Mz=ex["Mz"]))
    out[name] = rows
json.dump(dict(sweeps=out, source="t1_quick.log (3D, N=30, 40 restarts)"), open("results/t1_sweeps.json", "w"), indent=1)
print({k: len(v) for k, v in out.items()})
