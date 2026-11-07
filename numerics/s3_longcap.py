"""Long-horizon test requested by [adversary]: exact 3D pure dive (min Dv_z), 30 deg tilt cap,
tf = 12 and 20 s (coning plateau fits >= 1 revolution for tf >~ 9.2 s), Pv vs Pvr, GTPL, r_z >= 0, w = 0.4.
Coning share of 3D initial guesses raised to 0.6.  2 workers.  Output results/s3_longcap.json"""
import json, time, sys
import numpy as np
import models
from runner import run_stream
models.ReachM1.p_coning = 0.6
D2R = np.pi / 180


def main():
    P = models.gtpl(omega=0.4)
    jobs, keys = [], []
    for tf, N in [(12.0, 48), (20.0, 64)]:
        for ctrl in ["3d", "planar"]:
            for cons in ["Pv", "Pvr", "U"]:
                planar = ctrl == "planar"
                eq = ({"U": (), "Pv": (0,), "Pvr": (0, 3)} if planar else {"U": (), "Pv": (0, 1), "Pvr": (0, 1, 3, 4)})[cons]
                spec = ("M1", P, dict(tf=tf, N=N, planar=planar, use_r=True, alt=True, eq_idx=eq, tilt_max=30 * D2R))
                jobs.append((spec, dict(mode="lin", c=[0, 0, 1, 0, 0, 0], eq_val=[0.0] * len(eq))))
                keys.append(dict(tf=tf, N=N, ctrl=ctrl, cons=cons))
    ns = [32 if k["ctrl"] == "3d" else 16 for k in keys]
    t0 = time.time(); rows = []
    for j, r in run_stream(jobs, ns):
        k = dict(keys[j]); z = r["z"]
        diag = {}
        if r["x"] is not None and k["ctrl"] == "3d":
            R = models.ReachM1(P, k["tf"], k["N"], planar=False, use_r=True, tilt_max=30 * D2R)
            u = R.unpack(r["x"]); b = u["b"]
            tilt = np.degrees(np.arccos(np.clip(b[2], -1, 1)))
            az = np.unwrap(np.arctan2(b[1], b[0]))
            on = tilt > 29.0
            diag = dict(tilt_max=float(tilt.max()), frac_on_cap=float(on.mean()),
                        az_sweep_on_cap_deg=float(np.degrees(az[on].max() - az[on].min())) if on.sum() > 1 else 0.0,
                        az_total_var_deg=float(np.degrees(np.sum(np.abs(np.diff(az[tilt > 1.0]))))) if (tilt > 1.0).sum() > 1 else 0.0,
                        T_mean=float(np.mean(u["T"])))
        k.update(diag=diag, x=None if r["x"] is None else r["x"].tolist())
        k.update(val=float(r["f"]), nok=r["nok"], z=None if z is None else z.tolist(),
                 lat_v=float(np.hypot(z[0], z[1])) if z is not None else None,
                 lat_r=float(np.hypot(z[3], z[4])) if z is not None else None,
                 n_at_best=int(np.sum(np.array(r["fs"]) < r["fs"][0] + 1e-6 * max(1, abs(r["fs"][0])))) if r["fs"] else 0)
        rows.append(k)
        print(f"[{time.time() - t0:6.0f}s] tf={k['tf']} {k['ctrl']:6s} {k['cons']:3s} val={k['val']:.4f} lat_v={k['lat_v']} lat_r={k['lat_r']} nok={k['nok']} n@best={k['n_at_best']} diag={k['diag']}", flush=True)
        json.dump(rows, open("results/s3_longcap.json", "w"), indent=1)


if __name__ == "__main__":
    main()
