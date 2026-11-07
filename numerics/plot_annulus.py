"""Plot the hop-data landing annulus (s5_annulus.json) and the M3 landing-set map (d1_M3w_S5_quick.json)."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
A = json.load(open("results/s5_annulus.json"))
D = json.load(open("results/d1_M3w_S5_quick.json"))
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
v = [a["v0z"] for a in A]; ri = [a["r_in"] for a in A]; ro = [a["r_out"] for a in A]
ax[0].fill_between(v, ri, ro, color="tab:blue", alpha=0.3, label="L = {r_in <= |landing offset| <= r_out}")
ax[0].plot(v, ri, "b-o", label="r_in (dent of L) [m]"); ax[0].plot(v, ro, "b--o", label="r_out [m]")
ax[0].axvline(7.727, color="g", ls=":", label="max v0z with straight-below landing (Pvr)")
ax[0].axvline(7.917, color="r", ls=":", label="max v0z with v0_lat=0 (Pv)")
ax[0].set_xlabel("v0z [m/s]  (r0 = 0 on the pad, v0_lat = 0, tf = 4 s)"); ax[0].set_ylabel("landing offset radius [m]")
ax[0].set_title("M1 (w=0.4 rad/s), GTPL, r_z>=0: lateral landing set L", fontsize=9); ax[0].legend(fontsize=7)
for k, a in zip([1, 2], [A[1], A[-1]]):
    t = np.linspace(0, 2 * np.pi, 200)
    ax[k].fill(a["r_out"] * np.cos(t), a["r_out"] * np.sin(t), color="tab:blue", alpha=0.35, label="L (annulus)")
    ax[k].fill(a["r_in"] * np.cos(t), a["r_in"] * np.sin(t), color="white")
    ax[k].plot(a["r_out"] * np.cos(t), a["r_out"] * np.sin(t), "r--", lw=1, label="boundary of conv L")
    ax[k].plot(0, 0, "k*", ms=10, label="pad (in conv L, not in L)")
    ax[k].set_aspect("equal"); ax[k].legend(fontsize=7, loc="upper right")
    ax[k].set_title(f"M1: v0z = {a['v0z']} m/s: dent r_in = {a['r_in']:.2f} m", fontsize=9)
    ax[k].set_xlabel("landing x [m]"); ax[k].set_ylabel("landing y [m]")
plt.tight_layout(); plt.savefig("results/s5_annulus.png", dpi=130)
