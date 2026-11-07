"""[verify-tvc] Independent bound of the moment term of Lemma 4.7 (math/06), on the 20000 localization step cells.
  T(Pen) = kgf*rho0*(M0 + mu0(Pen))^2 + rhow*(Mw + cw*Pen)^2 - Pen,   0 <= Pen <= Penmax
mu0 = value of the knapsack LP  max sum g_i z_i, 0<=z_i<=1, sum c_i z_i <= Pen  (bathtub).
(1) exact float evaluation: mu0 is concave piecewise linear and T is a convex quadratic on each piece, so the max is
    attained at a breakpoint -> no grid needed.
(2) rigorous Arb bound via LP duality: mu0(Pen) <= y*Pen + sum_i max(0, g_i - y c_i) for every y >= 0; the resulting
    bound is a convex quadratic in Pen, so its max over [0, Penmax] is at an endpoint.
usage: moment_check.py N gim roll rho0 rhow [kapg]"""
import sys
from fractions import Fraction as Fr
import numpy as np
from flint import arb, ctx
ctx.prec = 128
# TVC-2 variant: tf=2, s*=0.5, zeta=xi=0.15, late omega_D = zeta*cos(phibar) ((A2) dropped), rho=(0.1,45)
N, gim, roll = 600, 'cone', 0
rho0, rhow, kapg = 0.1, 45.0, 10.0
import os
TF = float(os.environ.get("TF", "2")); CAP = os.environ.get("CAP", "none")
th = np.load(f"theirs_riccati_{TF}_{CAP}.npz")
pc, vc, ds = th['phicells'], th['vcells'], float(th['ds'])
m, rho1, rho2, Jt, L = 79.88, 400., 1000., 63.6, 0.589
de = np.pi/12 if gim == 'cone' else np.arccos(np.cos(np.pi/12)**2)
a1, a2, eps = rho1/m, rho2/m, Jt/(m*L); tf, ss, zeta, xi = TF, 0.5, 0.15, 0.15
K2 = a2*np.sin(de)/eps
n = len(pc); lo = np.arange(n)*ds; hi = lo + ds
E = hi <= ss + 1e-15
wmax = np.maximum(np.abs(lo-ss), np.abs(hi-ss)); wmin = np.where((lo < ss) & (hi > ss), 0, np.minimum(np.abs(lo-ss), np.abs(hi-ss)))
sph = np.sin(pc)
M0 = np.sum(np.where(E, sph*eps*vc**2, 0))*ds
Mw = np.sum(np.where(E, wmax*sph*eps*vc**2, 0))*ds
Dmax = a2 - a1*np.cos(de) + eps*vc.max()**2
om = np.where(E, xi, zeta)*np.cos(pc)
cw = np.max(sph/om)
g = sph*Dmax*ds; c = om*wmin*Dmax*ds
kgf = 1 + kapg if roll else 1.0
# Penmax from Lemma 4.0 (max of my closed-form E0 and theirs, i.e. the more conservative)
E0t, cabs, latf = th['info']
cE = np.cos(min(K2*ss**2/2, np.deg2rad(float(CAP)) if CAP != 'none' else np.pi))
Penmax = (xi/(cE*(1-cabs)) + zeta*latf)*E0t
# (1) exact float max over breakpoints
free = c <= 0
G0free = g[free].sum()
idx = np.where(~free)[0]; order = idx[np.argsort(-(g[idx]/c[idx]))]
cumP = np.concatenate([[0], np.cumsum(c[order])]); cumG = G0free + np.concatenate([[0], np.cumsum(g[order])])
bp = cumP[cumP <= Penmax]; Gb = cumG[:len(bp)]
def mu0(P):
    j = np.searchsorted(cumP, P, side='right') - 1
    if j >= len(order): return cumG[-1]
    return cumG[j] + (P - cumP[j]) * g[order[j]]/c[order[j]]
T = lambda P: kgf*rho0*(M0 + mu0(P))**2 + rhow*(Mw + cw*P)**2 - P
cands = list(bp) + [Penmax]
Tf = max(T(P) for P in cands)
Pbest = max(cands, key=T)
print(f"[{gim} N={N} roll={roll}] M0={M0:.4e} Mw={Mw:.4e} cw={cw:.4f} Dmax={Dmax:.4f} free gain={G0free:.3e} Penmax={Penmax:.4e}")
print(f"  exact (float) max moment term = {Tf:.6e} at Pen={Pbest:.3e}   (proof-tvc grid value {float(th['moment']):.6e})")
# (2) rigorous Arb bound: on each sub-interval [Pa,Pb] of a grid of [0,Penmax], LP duality with one y >= 0:
#     mu0(P) <= y P + R(y),  R(y) = sum_i max(0, g_i - y c_i);  the bound on T is convex in P => endpoints.
A = lambda x: arb(float(x))
dsA = A(ds)
pcA = [A(x) for x in pc]; vcA = [A(x) for x in vc]
epsA = arb(63.6)/(arb(79.88)*arb(0.589))
sphA = [x.sin() for x in pcA]
M0A = sum((sphA[i]*epsA*vcA[i]**2 for i in range(n) if E[i]), arb(0))*dsA
MwA = sum((A(wmax[i])*sphA[i]*epsA*vcA[i]**2 for i in range(n) if E[i]), arb(0))*dsA
DmaxA = A(a2) - A(a1)*A(np.cos(de)) + epsA*max(vcA, key=lambda x: float(x.mid()))**2 + arb('1e-12')
omA = [(A(xi) if E[i] else A(zeta))*pcA[i].cos() for i in range(n)]
cwA = max((sphA[i]/omA[i] for i in range(n)), key=lambda x: float(x.mid())) + arb('1e-12')
gA = [sphA[i]*DmaxA*dsA for i in range(n)]; cA_ = [omA[i]*A(wmin[i])*DmaxA*dsA for i in range(n)]
def RA(y):
    yA = A(y); R = arb(0)
    for gi, ci in zip(gA, cA_):
        t = gi - yA*ci
        up = float(t.mid()) + float(t.rad())
        if up > 0: R += arb(up) if float(t.mid()) - float(t.rad()) <= 0 else t
    return R
grid = np.concatenate([[0.0], np.geomspace(1e-10, Penmax, 60)])
Tup = -np.inf
for Pa, Pb in zip(grid[:-1], grid[1:]):
    # y = marginal ratio of the greedy order at Pb (tight dual there)
    j = min(np.searchsorted(cumP, Pb, side='right') - 1, len(order) - 1)
    y = g[order[j]]/c[order[j]]
    R = RA(y)
    for P in (Pa, Pb):
        PA = A(P)
        TA = A(kgf)*A(rho0)*(M0A + R + A(y)*PA)**2 + A(rhow)*(MwA + cwA*PA)**2 - PA
        Tup = max(Tup, float(TA.mid()) + float(TA.rad()))
print(f"  rigorous (Arb, piecewise LP-dual, 60 intervals) upper bound on the moment term = {Tup:.6e}")
np.save(f"moment_{gim}_{N}_roll{roll}.npy", np.array([Tf, Tup]))
# ---- final comparison and quantitative distance (float for d*, rigorous for the margin) ----
import os
ef = f"riccati_exact_{TF}_{CAP}.npy"; wf = f"witness_ordinary_cone_M1_tf{TF}.npz"
if os.path.exists(ef) and os.path.exists(wf):
    ex = np.load(ef); wz = np.load(wf)
    Vup, Glo = ex[0], float(wz['Glo'])
    Uup = Vup + Tup
    print(f"  FINAL: Arb-Riccati={bool(ex[1])} floors={bool(ex[2])} multiplier-bounds={bool(ex[3])}  "
          f"U_tot <= {Uup:.6e}  G_w(ordinary) >= {Glo:.6e}  certified margin = {Glo-Uup:.4e} ({(Glo-Uup)/Glo*100:.2f}%)")
    def Td(d):
        TT = lambda P: kgf*rho0*(d + M0 + mu0(P))**2 + rhow*(d*(1+ss) + Mw + cw*P)**2 - P
        return max(TT(P) for P in cands)
    lo_, hi_ = 0.0, 1e-3
    for _ in range(60):
        dm = (lo_+hi_)/2
        if Glo - dm*np.sqrt(1+ss**2) > Vup + Td(dm)*(1+1e-6): lo_ = dm
        else: hi_ = dm
    print(f"  dist(theta_m, F_relaxed) >= {lo_:.4e} m (float evaluation of the d-dependent moment term)")
