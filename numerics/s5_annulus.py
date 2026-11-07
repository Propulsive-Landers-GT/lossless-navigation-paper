"""Dent of the lateral landing set L in METERS at hop data (r0z = 0, v0_lat = 0, v0z in the sliver between
the Pvr- and Pv-optimal values from s1: 7.727 < v0z <= 7.917 at tf=4, N=28).  L is rotation-invariant, so
L = annulus {r_in <= |r0_lat| <= r_out};  r_in > 0  <=> 0 not in L  <=> nonconvex, dent = r_in.
3D M1, GTPL, w=0.4, r_z >= 0, coning guesses, seeds from an equality-free phase.  2 workers.
"""
import json, time
import numpy as np
import models
from runner import run_batch

if __name__ == "__main__":
    P = models.gtpl(omega=0.4); g = P["g"]; tf = 4.0; N = 28
    rows = []
    for v0z in [7.65, 7.75, 7.80, 7.85, 7.90]:
        dvz = g * tf - v0z; drz = dvz * tf - g * tf ** 2 / 2 - 0.0
        eqv = [0.0, 0.0, dvz, drz]
        spec0 = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True))
        seeds = run_batch([(spec0, dict(mode="dist", target=[0, 0, dvz, 0, 0, drz], W=[1, 1, 1, 0, 0, 1 / tf ** 2]))] * 4, 8)
        x0s = [s["x"] for s in seeds if s["x"] is not None and s["f"] < 1e-8]
        spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True, eq_idx=(0, 1, 2, 5)))
        rin, rout = run_batch([(spec, dict(mode="dist", target=[0] * 6, W=[0, 0, 0, 1, 1, 0], eq_val=eqv, x0s=x0s[:4])),
                               (spec, dict(mode="lin", c=[0, 0, 0, -1, 0, 0], eq_val=eqv, x0s=x0s[:4]))], 32, chunk=16)
        row = dict(v0z=v0z, n_seeds=len(x0s), r_in=float(np.sqrt(rin["f"])) if np.isfinite(rin["f"]) else None,
                   r_out=float(-rout["f"]) if np.isfinite(rout["f"]) else None)
        rows.append(row); print(row, flush=True)
    json.dump(rows, open("results/s5_annulus.json", "w"), indent=1)
