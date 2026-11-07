"""[verify-tvc] Independent re-implementation of the BOOTSTRAP localization (math/06 §5.6/5.7, Lemma 4.0 iterated),
variant R0, no tilt cap, general (tf, s*).  Each pass is Lemma 4.0 with the a-priori tilt bound min(K2 min(s,tf-s)^2/2,
cap) where cap = the padded tilt bound proved by the previous pass for ALL competitors with gain >= 0.
Compares proof-tvc's final step functions (localize.py) with mine: theirs >= mine on every cell validates them.
usage: loc_check2.py tf ss"""
import sys
import numpy as np
sys.path.insert(0, "../proof-tvc")
from localize import localize
tf, ss = float(sys.argv[1]), float(sys.argv[2])
cap0 = np.deg2rad(float(sys.argv[3])) if len(sys.argv) > 3 else np.pi   # class tilt cap (A1)
m, rho1, rho2, Jt, L = 79.88, 400., 1000., 63.6, 0.589
de = np.pi/12; a1, a2, eps = rho1/m, rho2/m, Jt/(m*L)
K1, K2 = a1*np.sin(de)/eps, a2*np.sin(de)/eps
beta, dpm = np.tan(de)/eps, a2 - a1*np.cos(de)

def one_pass(cap):
    phib0 = lambda s: min(K2*min(s, tf-s)**2/2, cap)
    assert phib0(tf/2) < np.pi/2
    c0, cE = np.cos(phib0(tf/2)), np.cos(phib0(ss))
    A1, B1 = a1*np.cos(de)/(1+cE), eps/cE**2
    base = beta**2*dpm*ss**2/2*(B1 + A1*ss**2)/cE
    k = 0.1
    if (1+1/k)*base > 0.5: k = 1/(0.5/base - 1)
    c_abs = (1+1/k)*base; assert c_abs < 1
    E0 = A1*(1+k)*K1**2/4*ss**6/30 + B1*(1+k)*K1**2*ss**4/12
    PenE = E0/(1-c_abs)
    LhW, LvW, LqW = 2*E0/a2, E0/(eps*c0), 2*a2*E0/c0**2
    def Ybar(x):
        eta = max(np.sqrt(PenE/(cE*dpm)) - (ss-x), 0.0)
        return min(dpm*x, dpm*eta + PenE/(cE*(ss-x+eta)))
    xs = np.linspace(0, ss, 100001); vx = np.array([min(K2*x, K1*x + beta*Ybar(x)) for x in xs])
    phiE = np.concatenate([[0], np.cumsum(np.maximum(vx[:-1], vx[1:])*(xs[1]-xs[0]))])
    phiE = np.minimum(phiE, [phib0(x) for x in xs])
    vss, phiss = vx[-1], phiE[-1]
    sl = np.linspace(ss, tf, 300001)
    def vL(s0):
        sig, ln = s0-ss, tf-s0; b = [K2*min(s0, tf-s0), vss + K2*sig]
        if sig > 0 and ln > 0:
            Iv, Ivd = LvW/sig, LqW/(eps**2*sig); b.append(np.sqrt(Iv/ln + 2*np.sqrt(Iv*Ivd)))
        return min(b)
    vl = np.array([vL(s) for s in sl])
    vint = np.concatenate([[0], np.cumsum(np.maximum(vl[:-1], vl[1:])*(sl[1]-sl[0]))])
    hl = []
    for i, s0 in enumerate(sl):
        sig, ln = s0-ss, tf-s0; b = [np.sin(min(phib0(s0), np.pi/2)), np.sin(phiss) + vint[i], 1.0]
        if sig > 0 and ln > 0:
            Ih, Ihd = LhW/sig, LvW/sig; b.append(np.sqrt(Ih/ln + 2*np.sqrt(Ih*Ihd)))
        hl.append(min(b))
    phl = np.arcsin(np.array(hl))
    vmax = max(vx.max(), vl.max())
    def Bv(s):
        if s <= ss: return vx[min(np.searchsorted(xs, s), len(xs)-1)]          # vE increasing
        i = np.searchsorted(sl, s); return max(vl[max(i-1, 0)], vl[min(i, len(sl)-1)])
    def Bp(s):
        if s <= ss: return phiE[min(np.searchsorted(xs, s), len(xs)-1)]
        i = np.searchsorted(sl, s); return max(phl[max(i-1, 0)], phl[min(i, len(sl)-1)])
    phimax = max(phiE.max(), phl.max()) + vmax*(sl[1]-sl[0])*2
    return dict(Bv=Bv, Bp=Bp, vmax=vmax, phimax=phimax, E0=E0, c_abs=c_abs, k=k)

cap = cap0; r = None
for it in range(8):
    r = one_pass(cap)
    print(f"  pass {it}: cap in={cap:.5f}  E0={r['E0']:.4e} c_abs={r['c_abs']:.4f} kap={r['k']:.4f}  vmax={r['vmax']:.4f}  phimax={r['phimax']:.5f}")
    if r['phimax'] > cap - 1e-6: break
    cap = r['phimax']
P = dict(m=m, a1=a1, a2=a2, de=de, eps=eps, g0=9.80665)
vf, pf, info, _ = localize(P, tf, ss, cap=(None if cap0 == np.pi else cap0))
print(f"theirs: E0={info['E0']:.4e} c_abs={info['c_abs']:.4f} vmax={info['vmax']:.4f} phimax={info['phimax']:.5f}")
ds = vf.ds; bad = 0; wv = wp = np.inf
for i in range(len(vf.cells)):
    a, b = i*ds, (i+1)*ds
    mv = min(r['Bv'](a), r['Bv'](b)) + K2*ds; mp = min(r['Bp'](a), r['Bp'](b)) + r['vmax']*ds
    wv, wp = min(wv, vf.cells[i]-mv), min(wp, pf.cells[i]-mp)
    bad += (vf.cells[i] < mv - 1e-12) or (pf.cells[i] < mp - 1e-12)
print(f"[tf={tf} s*={ss}] theirs - mine: min over cells v: {wv:.3e}, phi: {wp:.3e}; cells where theirs < mine: {bad}/{len(vf.cells)}")
