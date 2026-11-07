"""Re-plot t1 section from results/t1_base.json (no new solves).  The 3D lower boundary is taken as
min(3D multistart, planar), which is legitimate because planar controls are admissible 3D controls;
spikes in the raw 3D curve are multistart failures near the ends of the chord."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import models
r = json.load(open("results/t1_base.json"))
s = r["section"]; xs = np.array(s["xs"]); zl2 = np.array(s["zlo_planar"]); zl3 = np.minimum(np.array(s["zlo_3d"]), zl2)
zh2 = np.array(s["zhi_planar"])
P = models.gtpl(); ex = models.extreme_arcs_M1(P, 2.0, 40)
near = np.array(r["gtpl_base"]["conv"]["3d"][-1]["z"]); dist = r["gtpl_base"]["conv"]["3d"][-1]["dist"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
ax[0].fill_between(xs, zl2, np.where(np.isfinite(zh2), zh2, np.nan), color="0.85", label="R (planar controls)")
ax[0].plot(xs, zl2, "b-", lw=2, label="lower boundary, planar controls")
ax[0].plot(xs, zl3, "r--", lw=1.5, label="lower boundary, 3D controls (section y=0)")
ax[0].plot([-ex["Px"], ex["Px"]], [ex["Mz"], ex["Mz"]], "k:o", label="chord P- P+ (subset of conv R)")
ax[0].plot(0, ex["Mz"], "k*", ms=14, label="midpoint M")
ax[0].plot(0, near[2], "gs", label=f"nearest point of R to M (dist {dist:.2f} m/s)")
ax[0].set_xlabel("Dv_x [m/s]"); ax[0].set_ylabel("Dv_z [m/s]"); ax[0].legend(fontsize=7, loc="upper right")
ax[0].set_title("M1 velocity-increment set R: GTPL, tf=2 s, w=30 deg/s, delta=15 deg, rho1/rho2=0.4", fontsize=9)
ax[1].plot(xs, zl2 - ex["Mz"], "b-", label="planar"); ax[1].plot(xs, zl3 - ex["Mz"], "r--", label="3D (y=0)")
ax[1].axhline(0, color="k", ls=":"); ax[1].set_xlabel("Dv_x [m/s]"); ax[1].set_ylabel("z_min(x) - M_z [m/s]")
ax[1].set_title("Lower boundary lies above the chord, so conv R != R", fontsize=9); ax[1].legend()
plt.tight_layout(); plt.savefig("results/t1_R_section.png", dpi=130)
