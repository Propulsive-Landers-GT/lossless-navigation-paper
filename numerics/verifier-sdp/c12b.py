"""[verifier-sdp] Case 12, harder 3-D search + target homotopy.
 (1) basin hopping around the best 3-D solution (perturbation scales 0.02..0.8 rad), 300 runs;
 (2) target homotopy: q(s) = (1-s) q_reach + s q12, where q_reach is the readout of the best 3-D
     trajectory (cost 0 at s=0).  Track the SDP value / 4th eigenvalue and the warm-started 3-D NLP
     (plus 20 fresh restarts per step) -> where does the SDP leave R^3?"""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
from c12 import *

if __name__ == "__main__":
    res = json.load(open(os.path.join(OUT, "c12.json")))
    rng = np.random.default_rng(1212)
    nlp3 = NLP(3)
    xb = pack(np.array(res["best_B"]), np.array(res["best_D"]))
    fb = res["genuine_best"]
    hop = []
    for j in range(300):
        sc = [0.02, 0.05, 0.1, 0.2, 0.4, 0.8][j % 6]
        Bf, Dm = unpack(xb, 3)
        Bf = Bf + sc * rng.normal(size=Bf.shape); Dm = Dm + sc * rng.normal(size=Dm.shape)
        Bf /= np.linalg.norm(Bf, axis=1, keepdims=True); Dm /= np.linalg.norm(Dm, axis=1, keepdims=True)
        x, f, v, st = nlp3.solve(pack(Bf, Dm))
        if v < 1e-8:
            hop.append(f)
            if f < fb - 1e-10:
                fb, xb = f, x
                print(f"  basin hop improved: {f:.9f}", flush=True)
    hop = np.array(hop)
    print(f"[basin hopping] {len(hop)} feasible, best {hop.min():.9f}, quantiles {np.round(np.quantile(hop, [0, .1, .5]), 7)}", flush=True)
    out = dict(hop_best=float(hop.min()), hop_n=int(len(hop)))

    # target homotopy from a reachable point
    Bf, Dm = unpack(xb, 3)
    qv = GV @ Dm; qr = GR @ Dm
    # start from a *different* reachable point: planar tent arc with gimbal leaning, azimuth of the target
    psi = np.arctan2(WV[1], WV[0])
    kk = np.arange(N + 1); phi = np.minimum(kk, N - kk) * OM * H
    B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
    q0v = GV @ B[:N]; q0r = GR @ B[:N]
    x3 = pack(B[1:N], B[:N].copy())
    rows = []
    for s in np.linspace(0, 1, 26):
        wv = (1 - s) * q0v + s * WV; wr = (1 - s) * q0r + s * WR
        sd = gram_sdp(wv=wv, wr=wr)
        nl = NLP(3, wv=wv, wr=wr)
        x3, f3, v3, _ = nl.solve(x3)
        fbest = f3 if v3 < 1e-8 else np.inf
        for j in range(20):
            x, f, v, _ = nl.solve(random_start(rng))
            if v < 1e-8 and f < fbest - 1e-12:
                fbest = f; x3 = x
        ev = sd["ev"]
        rows.append(dict(s=float(s), sdp=sd["val"], st=sd["status"], e4=float(ev[3] / ev[0]), genuine=float(fbest)))
        print(f"s={s:.2f}: SDP {sd['val']:.9f} [{sd['status'][:4]}] e4/e1={ev[3] / ev[0]:.2e}  3D {fbest:.9f}  "
              f"gap {fbest - sd['val']:.2e}", flush=True)
    out["homotopy"] = rows
    json.dump(out, open(os.path.join(OUT, "c12b.json"), "w"), indent=1)
