"""Search R_pi-invariant faces of F^X (GTPL, altitude path constraint r_z >= 0) for the largest nonconvexity gap.

Every rotation-invariant linear functional of the boundary data is l = cos(phi) * v0z + sin(phi) * r0z / tf (scaled).
In terms of z = (Dv, Dr):  v0z = g tf - Dv_z,  r0z = Dv_z tf - Dr_z - g tf^2/2, so l is linear in (Dv_z, Dr_z).
For each phi: maximize l over F^X (3D M1, multistart with coning), take the optimizer z*, its rotation midpoint
zbar = (0,0,z*_3, 0,0,z*_6) (in conv F^X), and compute the weighted distance dist_W(zbar, Q^X),
W = (1,1,1,1/tf^2,1/tf^2,1/tf^2).  dist_W > 0 with lat != 0 => F^X nonconvex at that face, gap = dist_W.
Also reports the Pv-optimizer midpoint for pure dive (phi = 0).  2 workers.  Output results/s4_faces.json
"""
import json, time, sys
import numpy as np
import models
from runner import run_stream

D2R = np.pi / 180


def main():
    P = models.gtpl(omega=0.4); g = P["g"]
    tfs = [4.0, 8.0]
    phis = np.deg2rad([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330])
    jobs, keys = [], []
    for tf in tfs:
        N = 28 if tf < 6 else 32
        spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True))
        for ph in phis:
            # maximize cos*v0z + sin*r0z/tf  <=> minimize -(cos*(-Dv_z) + sin*(Dv_z tf - Dr_z)/tf) + const
            cz = np.cos(ph) * 1.0 - np.sin(ph) * 1.0          # coefficient of Dv_z in -l
            cr = np.sin(ph) / tf                                 # coefficient of Dr_z in -l
            jobs.append((spec, dict(mode="lin", c=[0, 0, cz, 0, 0, cr])))
            keys.append(dict(tf=tf, N=N, phi_deg=float(np.degrees(ph))))
    t0 = time.time(); faces = []
    for j, r in run_stream(jobs, 24):
        k = dict(keys[j])
        if r["z"] is None:
            k.update(ok=False); faces.append(k); continue
        z = r["z"]
        k.update(ok=True, z=z.tolist(), lat_v=float(np.hypot(z[0], z[1])), lat_r=float(np.hypot(z[3], z[4])),
                 v0z=float(g * k["tf"] - z[2]), r0z=float(z[2] * k["tf"] - z[5] - g * k["tf"] ** 2 / 2))
        faces.append(k)
        print(f"[{time.time() - t0:5.0f}s] face tf={k['tf']} phi={k['phi_deg']:5.0f}: lat_v={k['lat_v']:.3f} lat_r={k['lat_r']:.3f} "
              f"v0z={k['v0z']:.2f} r0z={k['r0z']:.2f}", flush=True)
    mj, mk = [], []
    for k in faces:
        if k.get("ok") and (k["lat_v"] > 1e-3 or k["lat_r"] > 1e-3):
            tf = k["tf"]; z = k["z"]
            spec = ("M1", P, dict(tf=tf, N=k["N"], planar=False, use_r=True, alt=True))
            mj.append((spec, dict(mode="dist", target=[0, 0, z[2], 0, 0, z[5]], W=[1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2])))
            mk.append(k)
    S1 = json.load(open("results/s1_slice.json"))
    for o in S1["rows"]:
        if o["obj"] == "dive" and o["ctrl"] == "3d" and o["cons"] == "Pv" and o["cap"] == "none":
            tf = o["tf"]; z = o["z"]
            spec = ("M1", P, dict(tf=tf, N=o["N"], planar=False, use_r=True, alt=True))
            mj.append((spec, dict(mode="dist", target=[0, 0, z[2], 0, 0, z[5]], W=[1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2])))
            k = dict(tf=tf, N=o["N"], phi_deg=-1.0, kind="dive-Pv-midpoint", z=z, lat_v=o["lat_v"], lat_r=o["lat_r"],
                     v0z=float(g * tf - z[2]), r0z=float(z[2] * tf - z[5] - g * tf ** 2 / 2), ok=True)
            mk.append(k); faces.append(k)
    for j, r in run_stream(mj, 24):
        k = mk[j]; k["gap_w"] = float(np.sqrt(r["f"])); k["znear"] = None if r["z"] is None else r["z"].tolist()
        print(f"gap tf={k['tf']} phi={k['phi_deg']:5.0f}: weighted dist of rotation midpoint = {k['gap_w']:.4f} "
              f"(lat_v {k['lat_v']:.2f}, lat_r {k['lat_r']:.2f}, v0z {k['v0z']:.2f}, r0z {k['r0z']:.2f})", flush=True)
    json.dump(faces, open("results/s4_faces.json", "w"), indent=1)


if __name__ == "__main__":
    main()
