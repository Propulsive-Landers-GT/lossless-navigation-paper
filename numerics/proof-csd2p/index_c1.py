import os, sys, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "../verifier-sdp")); sys.path.insert(0, os.path.join(here, "..")); sys.path.insert(0, os.path.join(here, "../redteam-lift"))
from vgim import Gim
from c1_csd2_check import make_cases
import picone
from picone import criterion, stress, jacobi_m, unpack, primer
picone.stress.full = True
cases, a1 = make_cases(); rng = np.random.default_rng(2)
for ci, c in enumerate(cases):
    if c["N"] > 24 or ci in (14, 17): continue
    wv, wr = np.array(c["wv_m"]), np.array(c["wr_m"])
    G = Gim(c["N"], c["tf"], c["om"], np.deg2rad(15), a=a1, cvx=True)
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 12, Zv=s["Z"])
    Q, C, res = stress(G, x, wv, wr); sc = np.abs(Q).max(); tol = 1e-7 * sc
    negQ = int(np.sum(np.linalg.eigvalsh(Q) < -tol)); negZ = int(np.sum(np.linalg.eigvalsh(Q - C) < -tol))
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    Cyw = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2]); ec = np.linalg.eigvalsh(0.5 * (Cyw + Cyw.T))
    p0 = int(np.sum(ec >= -1e-9 * np.abs(ec).max())); h, k = jacobi_m(G, x, wv, wr)
    cls = "k<=p0 (proved)" if k <= p0 else ("k-1>p0 (obstructed)" if k - 1 > p0 else "k=p0+1 (open)")
    print(f"case {ci} set {c['set']}: SDP={s['val']:.6g} gen={b:.6g} k={k} negZ={negZ} p0={p0} negQ={negQ} Cyw eig={np.round(ec/np.abs(ec).max(),3)} -> {cls}", flush=True)
