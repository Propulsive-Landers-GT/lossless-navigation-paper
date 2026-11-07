"""[verify-tvc] Numerical test of the discretization lemma 4.6' (continuous validity from the N=120 SDP).
The certificate claims inequality (C) for EVERY n in L^2 (with the coarse-cell multipliers lambda_k, Mlate_k and the
coefficients frozen on the coarse sub-cells).  Here the same continuous form -- WITHOUT the tau/tau'/tau_rho split
factors and without any remainder -- is restricted to a much finer piecewise-linear space (refine x N of the coarse
grid) and its top generalized eigenvalue (form vs int n^2) is computed.  The lemma predicts <= 0 for every refinement.
usage: disc_check.py N gim roll rho0 rhow refine"""
import sys
import numpy as np
N, gim, roll = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]); rho0, rhow = float(sys.argv[4]), float(sys.argv[5])
ref = int(sys.argv[6]) if len(sys.argv) > 6 else 2
assert roll == 0
th = np.load(f"theirs_{gim}_{N}_roll{roll}.npz")
pc, vc, dsf = th['phicells'], th['vcells'], float(th['ds'])
m, rho1, rho2, Jt, L = 79.88, 400., 1000., 63.6, 0.589
de = np.pi/12 if gim == 'cone' else np.arccos(np.cos(np.pi/12)**2)
a1, a2, eps = rho1/m, rho2/m, Jt/(m*L); tf, ss = 1.0, 0.25
zeta, kap, lam_max, rhoc, r_theta, nsub = 0.1, 0.01, 3e-3, 0.1, 0.2, 3
h = tf/N; kss = int(round(ss/h))
def cellmax(cells, lo, hi):
    i0 = max(int(np.floor(lo/dsf))-1, 0); i1 = min(int(np.ceil(hi/dsf))+1, len(cells)); return float(np.max(cells[i0:i1]))
def theta_of(vb):
    er = 2*eps**2*vb**4/a2**2; return 1e-3 if er <= 0 else float(np.clip(1/(1+r_theta/er), 1e-3, 0.9))
# coarse sub-cell coefficients
coef = []
for k in range(N):
    for j in range(nsub):
        lo = k*h + j*h/nsub; hi = lo + h/nsub
        ph, vb = cellmax(pc, lo, hi), cellmax(vc, lo, hi)
        early = hi <= ss + 1e-15
        if early: cA, cB, c2 = a1*np.cos(de)/(1+np.cos(ph)), eps/np.cos(ph)**2, 0.0
        else:
            t_ = theta_of(vb)
            cA = -(1-zeta)*(a2/2 - (1/t_-1)*eps**2*2*vb**4/(2*a2)); cB = -(1-zeta)*eps*np.cos(ph)
            c2 = (1-zeta)*(1-t_)*eps**2*np.cos(ph)**2/(2*a2)
        coef.append((lo, hi, early, cA, cB, 2*(1+1/kap)*vb**4, c2))
Nf = N*nsub*ref; hf = tf/Nf
xg, wg = np.polynomial.legendre.leggauss(6)
S, Wq, cA_, cB_, cL_, c2_ = [], [], [], [], [], []
for (lo, hi, early, cA, cB, cL, c2) in coef:
    for r in range(ref):
        a = lo + r*(hi-lo)/ref; b = a + (hi-lo)/ref
        s = (a+b)/2 + (b-a)/2*xg; S += list(s); Wq += list(wg*(b-a)/2)
        w = np.abs(s-ss)
        cA_ += list(w*cA); cB_ += list(w*cB); cL_ += [cL]*6; c2_ += list(w*c2)
S, Wq, cA_, cB_, cL_, c2_ = map(np.array, (S, Wq, cA_, cB_, cL_, c2_))
tk = np.arange(Nf+1)*hf
Sm = S[:, None]; T0 = tk[:-1][None, :]; T1 = tk[1:][None, :]
sig = np.clip(Sm-T0, 0, hf); inside = (Sm > T0) & (Sm <= T1); after = Sm > T1
X0 = np.where(Sm <= T0, 0, np.where(inside, sig**2/2, hf*(Sm-(T0+T1)/2))); Xd0 = sig
X1 = np.where(inside, sig**3/6 - hf*sig**2/4, np.where(after, -hf**3/12, 0.0)); Xd1 = np.where(inside, sig**2/2 - hf*sig/2, 0.0)
X = np.hstack([X0, X1]); Xd = np.hstack([Xd0, Xd1])
form = lambda cx, cv: (X.T*(Wq*cx))@X + (Xd.T*(Wq*cv))@Xd
K = form(cA_, cB_) + lam_max*form(cL_, 0*cL_)
f0 = np.where(S <= ss, a1*np.cos(de), a2)
G0 = (Wq*f0)@X; Gw = (Wq*(S-ss)*f0)@X
ck = (tk[:-1]+tk[1:])/2
Cm = np.vstack([np.r_[hf*np.ones(Nf), np.zeros(Nf)], np.r_[hf*(tf-ck), -np.full(Nf, hf**3/12)]])
# int (lambda + Mlate(=coarse-cell min of c2 multiplier)) n^2 : lambda_k, Mlate_k are coarse-cell constants
lam = th['lam']; Ml = th['Mlate']
cellc = np.minimum((ck/h).astype(int), N-1)
mult = lam[cellc] + Ml[cellc]
Wd = np.r_[np.full(Nf, hf), np.full(Nf, hf**3/12)]
Mf = K - rho0*np.outer(G0, G0) - rhow*np.outer(Gw, Gw) - rhoc*Cm.T@Cm - np.diag(Wd*np.r_[mult, mult])
Sc = 1/np.sqrt(Wd); Ms = (Mf+Mf.T)/2*Sc[:, None]*Sc[None, :]
ev = np.linalg.eigvalsh(Ms)
print(f"[{gim} N={N}] refined space: {2*Nf} dof (x{nsub*ref} of the coarse grid); top generalized eigenvalue of the continuous "
      f"form (no split factors, no remainders) = {ev.max():.4e}   (Lemma 4.6' predicts <= 0)")
