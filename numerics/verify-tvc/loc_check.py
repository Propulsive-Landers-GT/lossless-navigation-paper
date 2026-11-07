"""[verify-tvc] Independent re-implementation of the localization Lemma 4.0 (math/06 §4.0), variant R0.
Written from the statement, not from localize.py: closed-form E0 and absorption constant, closed-form minimisation in
Ybar, closed-form Agmon.  Then checks that proof-tvc's step functions (localize.py) dominate my rigorous cell bounds
(true v is K2-Lipschitz, true phi is vmax-Lipschitz, so  sup_cell v <= min(B(s_i),B(s_i+1)) + K2 ds).
Larger a-priori bounds are always safe in the certificate (every coefficient is monotone in phibar, vbar), so
'theirs >= mine' on every cell validates their localization.
usage: loc_check.py [cone|box]"""
import sys
import numpy as np
sys.path.insert(0, "../proof-tvc")
from localize import localize          # THEIR implementation (only for comparison)

gim = sys.argv[1] if len(sys.argv) > 1 else 'cone'
m, rho1, rho2, Jt, L = 79.88, 400., 1000., 63.6, 0.589
de = np.pi/12 if gim == 'cone' else np.arccos(np.cos(np.pi/12)**2)
a1, a2, eps = rho1/m, rho2/m, Jt/(m*L)
tf, ss = 1.0, 0.25
K1, K2 = a1*np.sin(de)/eps, a2*np.sin(de)/eps
beta, dpm = np.tan(de)/eps, a2 - a1*np.cos(de)
k = 0.1
cE = np.cos(K2*ss**2/2); c0 = np.cos(K2*(tf/2)**2/2)
A1, B1 = a1*np.cos(de)/(1+cE), eps/cE**2
# E0 = int_0^s* (s*-s)[A1(1+k) K1^2 s^4/4 + B1(1+k) K1^2 s^2] ds  (closed form)
E0 = A1*(1+k)*K1**2/4 * ss**6/30 + B1*(1+k)*K1**2 * ss**4/12
# absorption: int (s*-s) Y^2 <= dpm * s*^2/2 * int|w| dp ; tilt carries an extra s^2 <= s*^2
c_abs = (1+1/k)*beta**2*dpm*ss**2/2*(B1 + A1*ss**2)/cE
assert c_abs < 1
PenE = E0/(1-c_abs)                    # bound on cE * int_E |w| dp
LhW, LvW, LqW = 2*E0/a2, E0/(eps*c0), 2*a2*E0/c0**2
def Ybar(x):                           # min_eta [dpm*eta + PenE/(cE (s*-x+eta))], eta >= 0 ; also <= dpm*x
    eta = max(np.sqrt(PenE/(cE*dpm)) - (ss-x), 0.0)
    return min(dpm*x, dpm*eta + PenE/(cE*(ss-x+eta)) if ss-x+eta > 0 else np.inf)
def vE(x): return min(K2*x, K1*x + beta*Ybar(x))
# early tilt: phi(x) <= int_0^x vE  (vE is increasing; exact integral via fine trapezoid + upper Riemann)
xs = np.linspace(0, ss, 200001); vx = np.array([vE(x) for x in xs])
phiE = np.concatenate([[0], np.cumsum(np.maximum(vx[:-1], vx[1:])*(xs[1]-xs[0]))])
phiE = np.minimum(phiE, K2*xs**2/2)
vss, phiss = vx[-1], phiE[-1]
def vL(s0):
    sig = s0 - ss; ln = tf - s0
    b = [K2*min(s0, tf-s0), vss + K2*sig]
    if sig > 0 and ln > 0:
        Iv, Ivd = LvW/sig, LqW/(eps**2*sig); b.append(np.sqrt(Iv/ln + 2*np.sqrt(Iv*Ivd)))
    return min(b)
sl = np.linspace(ss, tf, 150001); vl = np.array([vL(s) for s in sl])
vint = np.concatenate([[0], np.cumsum(np.maximum(vl[:-1], vl[1:])*(sl[1]-sl[0]))])
def hL(i):
    s0 = sl[i]; sig = s0-ss; ln = tf-s0
    b = [np.sin(K2*min(s0, tf-s0)**2/2), np.sin(phiss) + vint[i]]
    if sig > 0 and ln > 0:
        Ih, Ihd = LhW/sig, LvW/sig; b.append(np.sqrt(Ih/ln + 2*np.sqrt(Ih*Ihd)))
    return min(min(b), 1.0)
phl = np.arcsin(np.array([hL(i) for i in range(len(sl))]))
def B_v(s): return np.interp(s, xs, vx) if s <= ss else np.interp(s, sl, vl)
def B_p(s): return np.interp(s, xs, phiE) if s <= ss else np.interp(s, sl, phl)
# NB: np.interp between grid points of an increasing/decreasing bound is not itself a bound; we only evaluate at the
# fine-grid points of THEIR step function and add the Lipschitz pad, and our grids are 8-10x finer than theirs,
# so we evaluate the bound exactly at a grid point nearest from the safe side:
def Bv_at(s):
    if s <= ss: i = np.searchsorted(xs, s); return vx[min(i, len(xs)-1)] if i < len(xs) else vx[-1]
    i = np.searchsorted(sl, s); return max(vl[max(i-1, 0)], vl[min(i, len(sl)-1)])
def Bp_at(s):
    if s <= ss: i = np.searchsorted(xs, s); return phiE[min(i, len(xs)-1)]
    i = np.searchsorted(sl, s); return max(phl[max(i-1, 0)], phl[min(i, len(sl)-1)])

P = dict(m=m, a1=a1, a2=a2, de=de, eps=eps, g0=9.80665)
vf, pf, info, _ = localize(P, tf, ss)
print(f"[{gim}] mine: E0={E0:.6e} c_abs={c_abs:.6f} PenE={PenE:.6e} | theirs: E0={info['E0']:.6e} c_abs={info['c_abs']:.6f} PenE={info['PenE']:.6e}")
ds = vf.ds; ncell = len(vf.cells)
vmax_mine = max(vx.max(), vl.max())
worst_v = worst_p = np.inf; bad = 0
for i in range(0, ncell):
    s_a, s_b = i*ds, (i+1)*ds
    mv = min(Bv_at(s_a), Bv_at(s_b)) + K2*ds
    mp = min(Bp_at(s_a), Bp_at(s_b)) + vmax_mine*ds
    worst_v = min(worst_v, vf.cells[i] - mv); worst_p = min(worst_p, pf.cells[i] - mp)
    if vf.cells[i] < mv - 1e-12 or pf.cells[i] < mp - 1e-12: bad += 1
print(f"  their vbar - my rigorous bound: min over cells = {worst_v:.3e};  phibar: {worst_p:.3e};  cells where theirs < mine: {bad}/{ncell}")
print(f"  my max v_loc = {vmax_mine:.4f} rad/s (theirs {info['vmax']:.4f}); my max phi_loc = {max(phiE.max(), phl.max()):.4f} rad (theirs {info['phimax']:.4f})")
