"""Hemisphere criterion + index data on [numerics] c1 cases (set A = GTPL-realistic above-ground), convexified lens 15 deg."""
import os, sys, numpy as np
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "../verifier-sdp")); sys.path.insert(0, os.path.join(here, "..")); sys.path.insert(0, os.path.join(here, "../redteam-lift"))
from vgim import Gim
from c1_csd2_check import make_cases
import picone
from picone import criterion, stress, jacobi_m
cases, a1 = make_cases()
rng = np.random.default_rng(2)
for ci, c in enumerate(cases):
    if c["N"] > 24: continue
    wv, wr = np.array(c["wv_m"]), np.array(c["wr_m"])
    G = Gim(c["N"], c["tf"], c["om"], np.deg2rad(15), a=a1, cvx=True)
    s = G.sdp(wv, wr); b, x, fs = G.best3(wv, wr, rng, 12, Zv=s["Z"])
    if x is None: print(ci, "no feasible"); continue
    t, cc = criterion(G, x, wv, wr); ev, res = stress(G, x, wv, wr); h, k = jacobi_m(G, x, wv, wr)
    print(f"case {ci} set {c['set']} N={c['N']}: SDP={s['val']:.6g} gen={b:.6g} crit={t:+.2e} c={np.round(cc,2) if cc is not None else None} crossings={k} stress_min={ev[0]/abs(ev[-1]):+.1e}", flush=True)
