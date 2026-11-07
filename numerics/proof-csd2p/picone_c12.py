import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
from picone import criterion, stress
wv = np.array([5.0939, 21.9914, 32.1819]); wr = np.array([8.2825, 44.1701, 64.908])
rng = np.random.default_rng(1)
for cvx in (False, True):
    G = Gim(16, 4.0, np.deg2rad(30), np.deg2rad(15), a=11.0, cvx=cvx)
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 40, Zv=s["Z"])
    t, c = criterion(G, x, wv, wr); ev, res = stress(G, x, wv, wr)
    print(f"case12 cvx={cvx}: SDP={s['val']:.8f} best3={b:.8f} crit t*={t:.3e} c={c} stress min ev={ev[0]:.3e} res={res:.1e}")
