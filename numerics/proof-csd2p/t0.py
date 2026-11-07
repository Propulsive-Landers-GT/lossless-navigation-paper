import sys, time, os
sys.path.insert(0, "../verifier-sdp")
import numpy as np
from vgim import Gim
rng = np.random.default_rng(0)
for (N, wtf, dl) in [(24, np.pi, 15), (24, 2*np.pi, 15)]:
    G = Gim(N, 4.0, wtf/4.0, np.deg2rad(dl), a=11.0, cvx=True)
    Pv, Pr = G.extreme_readouts()
    v = 0.5*Pv + 0.5*np.array([[0,-1,0],[1,0,0],[0,0,1]])@Pv; r = 0.5*Pr + 0.5*np.array([[0,-1,0],[1,0,0],[0,0,1]])@Pr
    t=time.time(); s = G.sdp(v, r); t1=time.time()-t
    t=time.time(); b, x, fs = G.best3(v, r, rng, 8, Zv=s["Z"]); t2=time.time()-t
    print(N, wtf, s["val"], s["status"], s["e4"], b, t1, t2, flush=True)
