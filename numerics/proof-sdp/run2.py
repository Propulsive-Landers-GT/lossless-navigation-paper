import numpy as np, sys
from dimtest import *
tf, dl = 4.0, np.deg2rad(15)
for omd in (2.0, 30.0):
    om = np.deg2rad(omd)
    for N in (3, 4, 5):
        h, cv, cr = weights(N, tf)
        for mu in (0.975, 0.99):
            wv = np.array([mu * cv.sum(), 0, 0]); wr = np.array([mu * cr.sum(), 0, 0])
            v, st, ev, _ = sdp(wv, wr, N, tf, om, dl)
            n3, _ = nlp(wv, wr, N, tf, om, dl, 3, 40); n4, _ = nlp(wv, wr, N, tf, om, dl, 4, 40); n6, _ = nlp(wv, wr, N, tf, om, dl, 6, 30)
            print(f"om={omd} N={N} mu={mu} SDP={v:.3e}[{st}] NLP3={n3:.3e} NLP4={n4:.3e} NLP6={n6:.3e} rank-ev={np.round(ev[:6]/ev[0],4)}", flush=True)
