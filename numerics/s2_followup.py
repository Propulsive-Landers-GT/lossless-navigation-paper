"""Follow-up to s1_slice: (a) dent size of the lateral landing set L in METERS at the Pv-optimal vertical data
(L is rotation-invariant there, conv L contains 0, so dent = inner radius r_in = min |r0_lat| over L);
(b) discretization check (N) of the B* gap and of r_in.  Reads results/s1_slice.json.  2 workers.
"""
import json, time
import numpy as np
import models
from runner import run_stream

D2R = np.pi / 180


def main():
    S = json.load(open("results/s1_slice.json"))
    P = models.gtpl(omega=0.4)
    caps = {"none": None, "30deg": 30 * D2R}
    jobs, keys = [], []
    for o in S["rows"]:
        if o["ctrl"] == "3d" and o["cons"] == "Pv":
            for N in sorted({o["N"], 40}):
                z = np.array(o["z"]); tf = o["tf"]
                spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True, eq_idx=(0, 1, 2, 5), tilt_max=caps[o["cap"]]))
                jobs.append((spec, dict(mode="dist", target=[0] * 6, W=[0, 0, 0, 1, 1, 0], eq_val=[0, 0, z[2], z[5]])))
                keys.append(dict(kind="r_in", obj=o["obj"], cap=o["cap"], tf=tf, N=N, lat_r_Pv=o["lat_r"]))
    for b in S["bstar"]:
        if b["cap"] == "none":
            tf = b["tf"]; z = np.array(b["zface"])
            for N in [20, 40]:
                spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True))
                # recompute the face at this N, then the midpoint distance (two-stage job done sequentially below)
                jobs.append((spec, dict(mode="lin", c=[0, 0, -(tf - S["sstar"]), 0, 0, 1])))
                keys.append(dict(kind="face", tf=tf, N=N))
    t0 = time.time()
    out = []
    faces = {}
    for j, r in run_stream(jobs, 24):
        k = dict(keys[j])
        if k["kind"] == "r_in":
            k["r_in"] = float(np.sqrt(r["f"])) if np.isfinite(r["f"]) else None
            print(f"[{time.time() - t0:5.0f}s] r_in {k['obj']:9s} cap={k['cap']:5s} tf={k['tf']} N={k['N']}: r_in={k['r_in']} m "
                  f"(Pv optimizer |r0_lat|={k['lat_r_Pv']:.2f} m)", flush=True)
        else:
            k["z"] = r["z"].tolist(); faces[(k["tf"], k["N"])] = r["z"]
            print(f"[{time.time() - t0:5.0f}s] face tf={k['tf']} N={k['N']}: val={r['f']:.4f} lat_v={np.hypot(*r['z'][:2]):.3f}", flush=True)
        out.append(k)
    mj, mk = [], []
    for (tf, N), z in faces.items():
        spec = ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True))
        W = [1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2]
        mj.append((spec, dict(mode="dist", target=[0, 0, z[2], 0, 0, z[5]], W=W))); mk.append(dict(kind="bstar", tf=tf, N=N))
    for j, r in run_stream(mj, 24):
        k = dict(mk[j]); k["dist_w"] = float(np.sqrt(r["f"])); out.append(k)
        print(f"B* gap tf={k['tf']} N={k['N']}: {k['dist_w']:.4f}", flush=True)
    json.dump(out, open("results/s2_followup.json", "w"), indent=1)


if __name__ == "__main__":
    main()
