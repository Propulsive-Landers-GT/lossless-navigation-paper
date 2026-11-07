"""DIAGNOSTIC: ideal bound with Finsler moment penalty rho (exact clamps), deg=1, no rigorous remainders."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf,ss,N=1.0,0.25,int(sys.argv[1])
vf,pf,info,_=localize(P,tf,ss)
par=dict(C2.PAR); par.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf)); h=D['h']; Wd=D['Wdiag']; Ml=np.concatenate([D['Mlate']]*2)
u,s,vt=np.linalg.svd(D['C']); Z=vt[np.sum(s>1e-12*s[0]):].T
Sc=1/np.sqrt(Wd); Zy=Z/Sc[:,None]
for rho in [float(x) for x in sys.argv[2:]]:
    A=D['Kp']+D['Km']-rho*D['G'].T@D['G']; As=A*Sc[:,None]*Sc[None,:]
    lam=cp.Variable(N); Mx=Zy.T@As@Zy - Zy.T@cp.diag(cp.hstack([lam,lam])+Ml)@Zy
    prob=cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam,D['Nb2']))),[lam>=0,(Mx+Mx.T)/2<<0]); prob.solve(solver='CLARABEL')
    print(f"rho={rho:g}: ideal Finsler bound {prob.value:.5e}   moment term {C2.moment_term(D,rho):.3e}",flush=True)
