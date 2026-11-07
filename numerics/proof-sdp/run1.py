import numpy as np, sys
from dimtest import *
tf, om, dl = 4.0, np.deg2rad(30), np.deg2rad(15)
rng = np.random.default_rng(1)
for N in (2, 3):
    h, cv, cr = weights(N, tf)
    Pz = cv.sum(); Rz = cr.sum()
    for j in range(6):
        sv, sr = rng.uniform(0.2, 0.9, 2)
        wv = np.array([sv * Pz, rng.uniform(-.5, .5) * Pz, 0]); wr = np.array([sr * Rz, 0, rng.uniform(-.5, .5) * Rz])
        v, st, ev, _ = sdp(wv, wr, N, tf, om, dl)
        n3, _ = nlp(wv, wr, N, tf, om, dl, 3, 30); n4, _ = nlp(wv, wr, N, tf, om, dl, 4, 30); n5, _ = nlp(wv, wr, N, tf, om, dl, 5, 20)
        print(f"N={N} j={j} SDP={v:.7f}[{st}] NLP3={n3:.7f} NLP4={n4:.7f} NLP5={n5:.7f} ev4/ev1={ev[3]/ev[0]:.1e} gap3-sdp={(n3-v)/max(n3,1e-9):+.1e}", flush=True)
