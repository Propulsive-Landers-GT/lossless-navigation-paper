"""Slice lemma S test (CLAIMS row S) + B* gap size, GTPL, with altitude path constraint r_z(t) >= 0.

Fix v0_lat = 0 (<=> Dv_lat = 0 since v(tf) = 0).  Optimize a rotation-invariant vertical functional under
   (U)   no lateral constraint (B* face; shows the lateral offset of the optimizers),
   (Pv)  v0_lat = 0                     (Dv_x = Dv_y = 0),
   (Pvr) v0_lat = 0 and r0_lat = 0      (also Dr_x = Dr_y = 0: landing straight below; r0_lat = Dv_lat tf - Dr_lat).
A strict gap opt(Pvr) > opt(Pv) (minimization) => at the Pv-optimal vertical data the lateral landing set
L is nonempty but 0 not in L => that r0_lat-slice of F is nonconvex (slice lemma S).

Objectives (MINIMIZE c.z, z = (Dv, Dr)):
  dive      : Dv_z = int a d_z                                     (max vertical waste)
  divebrake : -int (s - s*) a d_z = -( (tf - s*) Dv_z - Dr_z ),  s* = 1 s   ([adversary] B*)
Planar vs full 3D controls; the 3D multistart includes coning guesses (tilt to rho, precess at
psi_dot ~ omega/sin rho; models.ReachM1.coning_b).  Tilt cap none / 30 deg.
B* gap: for the 3D U optimum z* of divebrake, the rotation midpoint (0,0,z*_3,0,0,z*_6) is tested for
membership in Q (with r_z >= 0) by a weighted min-distance NLP.

Results stream to results/s1_slice.jsonl (one line per job) and are summarized in results/s1_slice.json/.png.
Compute budget: 2 workers (runner.py).
"""
import sys, json, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import models
from runner import run_stream

D2R = np.pi / 180
SSTAR = 1.0


def build_jobs(P, tfs, caps):
    jobs, keys, ns = [], [], []
    order = [("3d", "Pv"), ("3d", "Pvr"), ("3d", "U"), ("planar", "Pv"), ("planar", "Pvr"), ("planar", "U")]
    for obj in ["divebrake", "dive"]:
        for ctrl, cons in order:
            for capn, cap in caps:
                for tf in tfs:
                    N = 32 if tf > 5 else 28
                    planar = ctrl == "planar"
                    eq = ({"U": (), "Pv": (0,), "Pvr": (0, 3)} if planar else {"U": (), "Pv": (0, 1), "Pvr": (0, 1, 3, 4)})[cons]
                    spec = ("M1", P, dict(tf=tf, N=N, planar=planar, use_r=True, alt=True, eq_idx=eq, tilt_max=cap))
                    c = [0, 0, 1, 0, 0, 0] if obj == "dive" else [0, 0, -(tf - SSTAR), 0, 0, 1]
                    jobs.append((spec, dict(mode="lin", c=c, eq_val=[0.0] * len(eq))))
                    keys.append(dict(cap=capn, tf=tf, ctrl=ctrl, cons=cons, obj=obj, N=N))
                    ns.append(16 if planar else 24)
    return jobs, keys, ns


def summarize(rows, P, tfs, caps):
    def get(**k):
        for o in rows:
            if all(o[a] == b for a, b in k.items()):
                return o
    lines = [f"{'obj':9s} {'cap':6s} {'tf':>4s} {'w*tf':>5s} {'ctrl':6s} {'U':>9s} {'latU_v':>7s} {'latU_r':>7s} {'Pv':>9s} {'Pvr':>9s} {'Pvr-Pv':>8s}  Pvr n_ok/n@best"]
    for obj in ["divebrake", "dive"]:
        for capn, _ in caps:
            for tf in tfs:
                for ctrl in ["3d", "planar"]:
                    U = get(obj=obj, cap=capn, tf=tf, ctrl=ctrl, cons="U"); a = get(obj=obj, cap=capn, tf=tf, ctrl=ctrl, cons="Pv")
                    b = get(obj=obj, cap=capn, tf=tf, ctrl=ctrl, cons="Pvr")
                    if not (U and a and b):
                        continue
                    lines.append(f"{obj:9s} {capn:6s} {tf:4.0f} {P['omega'] * tf:5.2f} {ctrl:6s} {U['val']:9.3f} {U['lat_v']:7.3f} {U['lat_r']:7.3f} "
                                 f"{a['val']:9.3f} {b['val']:9.3f} {b['val'] - a['val']:8.4f}  {b['nok']}/{b['n_at_best']}")
    return "\n".join(lines)


def main():
    P = models.gtpl(omega=0.4)
    tfs = [4.0, 8.0]
    caps = [("none", None), ("30deg", 30 * D2R)]
    jobs, keys, ns = build_jobs(P, tfs, caps)
    t0 = time.time()
    rows = []
    fo = open("results/s1_slice.jsonl", "w")
    for j, r in run_stream(jobs, ns):
        z = r["z"]; k = dict(keys[j])
        k.update(val=float(r["f"]), nok=r["nok"],
                 lat_v=float(np.hypot(z[0], z[1])) if z is not None else np.nan,
                 lat_r=float(np.hypot(z[3], z[4])) if z is not None else np.nan,
                 z=None if z is None else z.tolist(),
                 n_at_best=int(np.sum(np.array(r["fs"]) < r["fs"][0] + 1e-6 * max(1, abs(r["fs"][0])))) if r["fs"] else 0)
        rows.append(k); fo.write(json.dumps(k) + "\n"); fo.flush()
        print(f"[{time.time() - t0:6.0f}s] {k['obj']:9s} {k['cap']:6s} tf={k['tf']:.0f} {k['ctrl']:6s} {k['cons']:3s} val={k['val']:.4f} "
              f"lat_v={k['lat_v']:.3f} lat_r={k['lat_r']:.3f} nok={k['nok']} n@best={k['n_at_best']}", flush=True)
    # B* gap: rotation midpoint of the 3D U face point (divebrake), membership test with r_z >= 0
    bjobs, bkeys = [], []
    for o in rows:
        if o["obj"] == "divebrake" and o["ctrl"] == "3d" and o["cons"] == "U" and o["z"] is not None:
            tf = o["tf"]; z = np.array(o["z"])
            cap = dict(caps)[o["cap"]]
            spec = ("M1", P, dict(tf=tf, N=o["N"], planar=False, use_r=True, alt=True, tilt_max=cap))
            W = np.array([1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2])
            bjobs.append((spec, dict(mode="dist", target=[0, 0, z[2], 0, 0, z[5]], W=W)))
            bkeys.append(dict(cap=o["cap"], tf=tf, zface=o["z"]))
    bstar = []
    for j, r in run_stream(bjobs, 24):
        k = dict(bkeys[j]); k.update(dist_w=float(np.sqrt(r["f"])), znear=None if r["z"] is None else r["z"].tolist())
        bstar.append(k)
        print(f"B* gap cap={k['cap']} tf={k['tf']}: weighted dist of rotation midpoint = {k['dist_w']:.4f} "
              f"(face lat_v={np.hypot(*k['zface'][:2]):.3f}, lat_r={np.hypot(*k['zface'][3:5]):.3f})", flush=True)
    summ = summarize(rows, P, tfs, caps)
    print(summ, flush=True)
    json.dump(dict(omega=P["omega"], sstar=SSTAR, rows=rows, bstar=bstar, summary=summ), open("results/s1_slice.json", "w"), indent=1)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, obj in zip(axs, ["divebrake", "dive"]):
        for capn, _ in caps:
            for ctrl, mk in [("3d", "s-"), ("planar", "o--")]:
                g = []
                for tf in tfs:
                    a = [o for o in rows if (o["obj"], o["cap"], o["tf"], o["ctrl"], o["cons"]) == (obj, capn, tf, ctrl, "Pv")]
                    b = [o for o in rows if (o["obj"], o["cap"], o["tf"], o["ctrl"], o["cons"]) == (obj, capn, tf, ctrl, "Pvr")]
                    g.append(b[0]["val"] - a[0]["val"] if a and b else np.nan)
                ax.plot([P["omega"] * t for t in tfs], g, mk, label=f"{ctrl}, cap {capn}")
        ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("omega * tf [rad]"); ax.set_ylabel("opt(Pvr) - opt(Pv)")
        ax.set_title(f"{obj}: slice-lemma gap (GTPL, r_z>=0)", fontsize=9); ax.legend(fontsize=7)
    plt.tight_layout(); plt.savefig("results/s1_slice.png", dpi=130); plt.close()
    print("done", round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
