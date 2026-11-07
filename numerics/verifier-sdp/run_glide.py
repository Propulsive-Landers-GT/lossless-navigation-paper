"""[verifier-sdp] Glide-slope (+altitude) constraints with fixed thrust, scenarios started inside the cone.
Variants: G  = altitude + glide-slope SOC on first moments (state-linear);  G2 = G + lifted quadratic
tan^2 r_z^2 - |r_xy|^2 >= 0.  Genuine = exact quadratic cone + altitude (NLP).  Writes results/glide.jsonl."""
import os, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vcore import EZ
from vext import fixed_thrust, starts_fixed
from run_ext import altitude_path, gapstr

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
if __name__ == "__main__":
    rng = np.random.default_rng(41)
    fout = open(os.path.join(OUT, "glide.jsonl"), "w")
    g, a = 1.0, 1.5
    found = tries = 0
    while found < 12 and tries < 400:
        tries += 1
        N = int(rng.choice([8, 12])); tf = float(rng.choice([2.0, 3.0, 4.0])); omega = float(rng.choice([0.3, 0.8]))
        deg = float(rng.choice([45.0, 60.0, 75.0])); tang = np.tan(np.radians(deg))
        h0 = rng.uniform(0.5, 3.0)
        lat = rng.uniform(0, 0.8) * tang * h0; psi = rng.uniform(0, 2 * np.pi)
        r0 = np.array([lat * np.cos(psi), lat * np.sin(psi), h0])
        v0 = np.array([rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-2.0, 0.0)])
        accel = np.full(N + 1, a)
        Q = np.array([-(r0 + v0 * tf - 0.5 * g * tf ** 2 * EZ), -(v0 - g * tf * EZ)])
        F2 = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel, path=altitude_path(r0, v0, g, a, "G2", tang=tang))
        b = F2.best_of(starts_fixed(F2, N, rng, 30, omega=omega))
        if b["z"] is None:
            continue
        F0 = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel)
        b0 = F0.best_of(starts_fixed(F0, N, rng, 12, omega=omega))
        if b["f"] < b0["f"] * (1 + 1e-4):
            continue      # constraints inactive: not informative
        found += 1
        for var in ("G", "G2"):
            Fv = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel, path=altitude_path(r0, v0, g, a, var, tang=tang))
            s = Fv.sdp()
            dg, rg = gapstr(s["val"], b["f"])
            rec = dict(N=N, tf=tf, omega=omega, deg=deg, r0=r0.tolist(), v0=v0.tolist(), variant=var, uncon=b0["f"],
                       L=s["val"], st=s["status"], rank=s["rank"], U=b["f"], relgap=rg)
            fout.write(json.dumps(rec) + "\n"); fout.flush()
            print(f"glide #{found} N={N} tf={tf} w={omega} cone={deg}: uncon {b0['f']:.6g} | {var}: L={s['val']:.8g} "
                  f"[{str(s['status'])[:4]}] U={b['f']:.8g} rel={rg:.2e} rank={s['rank']}", flush=True)
