"""Theorem P0-X witness (early-kink face, face2.py): tie sigma_c, both maximisers, and the largest g/a2 for which
both landing trajectories stay above ground (g_crit).  F^X nonconvex for every g <= a2*min(g_crit)."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, json
from face2 import V
def tie(T, dl):
    def AB(sig):
        A = V(sig, sig, T, dl)[0]; bs = np.linspace(-sig, sig, 3001); v = V(bs, sig, T, dl)
        sel = bs < sig*(1 - 0.05); return A, v[sel].max(), bs[sel][np.argmax(v[sel])]
    lo, hi = 0.05*T, 0.9*T
    assert AB(lo)[0] > AB(lo)[1] and AB(hi)[0] < AB(hi)[1]
    for _ in range(40):
        m = 0.5*(lo+hi); A, B, _ = AB(m)
        if A > B: lo = m
        else: hi = m
    sig = 0.5*(lo+hi); A, B, b2 = AB(sig); return sig, b2, A, B
def witness_u(bs, sig, T, dl, n=20001):
    s = np.linspace(0, T, n)
    be = np.where(s <= sig, np.maximum(-s, bs - (sig - s)), bs + (s - sig))
    early = s < sig
    ang = np.where(early, be - dl, np.minimum(be + dl, np.pi/2 - dl))
    con = np.where(early, np.sin(-be), np.sin(np.minimum(2*dl + be, np.pi/2)))
    a = (con > 1e-12).astype(float)
    return s, a*np.sin(ang), a*np.cos(ang)
def gcrit(s, uz):
    T = s[-1]; best = np.inf
    for k in range(0, len(s)-1, 20):
        t = s[k]; L = np.trapezoid((s[k:] - t)*uz[k:], s[k:]); best = min(best, L/((T-t)**2/2))
    return best
for T, dd in [(0.1, 15), (0.3, 15), (0.5, 15), (0.8, 15), (1.2, 15), (0.3, 5), (0.3, 30), (0.6, 30)]:
    dl = np.deg2rad(dd)
    try: sig, b2, A, B = tie(T, dl)
    except AssertionError: print(T, dd, "no bracket"); continue
    g = []
    for bs in (sig, b2):
        s, ux, uz = witness_u(bs, sig, T, dl); g.append(gcrit(s, uz))
    print(json.dumps(dict(T=T, delta_deg=dd, sigma_over_tf=sig/T, beta2_over_sigma=b2/sig, gcrit=g,
          min_TW_needed=1/min(g), in_thm_regime=bool(T < min(2*dl, np.pi/2 - 2*dl)))))
