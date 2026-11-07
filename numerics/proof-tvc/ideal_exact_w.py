"""[proof-tvc] DIAGNOSTIC: ideal S-procedure bound with EXACT moment + clamp constraints (null space), piecewise-linear
basis (deg=1) or piecewise-constant (deg=0), no rigorous remainders. Tells whether the route can work at all."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf=float(sys.argv[1]); ss=float(sys.argv[2]); N=int(sys.argv[3]); deg=int(sys.argv[4])
vf,pf,info,_=localize(P,tf,ss)
par=dict(C2.PAR); par.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf))
A=D['Kp']+D['Km']; Wd=D['Wdiag']; h=D['h']
cons=np.vstack([D['G'],D['C']])
idx=np.arange(2*N) if deg==1 else np.arange(N)
A=A[np.ix_(idx,idx)]; cons=cons[:,idx]; Wd=Wd[idx]; Ml=np.concatenate([D['Mlate'],D['Mlate']])[idx]
Gw=(D['G'][1]-ss*D['G'][0])[idx][None,:]
for name,cmat in [("weighted moment only (Lambda_h=0)",np.vstack([Gw,D['C'][:,idx]])),("zero lateral",cons)]:
    u,s,vt=np.linalg.svd(cmat); Z=vt[np.sum(s>1e-12*s[0]):].T
    lam=cp.Variable(N); l2=lam if deg==0 else cp.hstack([lam,lam])
    Sc=1/np.sqrt(Wd); As=A*Sc[:,None]*Sc[None,:]; Zs=(Z.T/Sc).T   # x = Sc*y ; constraint on n: cmat n=0 -> n = Z c
    # LMI in n-space scaled: n = Sc*y, Z basis for n: y = Z c / Sc
    Zy=Z/Sc[:,None]
    Mx=Zy.T@(As)@Zy - Zy.T@cp.diag(l2+Ml)@Zy
    prob=cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam,D['Nb2']))),[lam>=0,(Mx+Mx.T)/2<<0])
    prob.solve(solver='CLARABEL')
    print(f"tf={tf} s*={ss} N={N} deg={deg} {name}: ideal bound {prob.value:.5e}",flush=True)
