import os, sys, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
from vgim import Gim
from picone import criterion, stress, unpack, primer
wv = np.array([5.0939, 21.9914, 32.1819]); wr = np.array([8.2825, 44.1701, 64.908])
rng = np.random.default_rng(1)
G = Gim(16, 4.0, np.deg2rad(30), np.deg2rad(15), a=11.0, cvx=True)
s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 40, Zv=s["Z"])
B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
np.set_printoptions(precision=3, suppress=True)
print("yv", yv, "yr", yr)
for k in range(17):
    pk = P[min(k,15)]/np.linalg.norm(P[min(k,15)])
    print(k, B[k], D[min(k,15)], np.linalg.norm(D[min(k,15)]), pk, "ang(b,P)=%.1f"%np.degrees(np.arccos(np.clip(B[k]@pk,-1,1))))
