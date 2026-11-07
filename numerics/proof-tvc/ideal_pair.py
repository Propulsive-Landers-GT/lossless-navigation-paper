"""DIAGNOSTIC: ideal bound with Finsler (rho0 on m0, rhow on weighted m_w), exact clamps, deg=1, no remainders;
plus the rigorous moment term for realistic zeta."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf,ss,N=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3])
vf,pf,info,_=localize(P,tf,ss)
par=dict(C2.PAR); par.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf)); h=D['h']; Wd=D['Wdiag']; Ml=np.concatenate([D['Mlate']]*2)
u,s,vt=np.linalg.svd(D['C']); Z=vt[np.sum(s>1e-12*s[0]):].T; Sc=1/np.sqrt(Wd); Zy=Z/Sc[:,None]
parR=dict(C2.PAR); parR.update(zeta=0.1, xi=0.1); DR=C2.setup(P,tf,ss,20,parR,loc=(vf,pf))
cE=np.cos(DR['K2']*ss**2/2); DR['Penmax']=(0.1/(cE*(1-info['c_abs']))+0.1)*info['E0']
for x in sys.argv[4:]:
    r0,rw=[float(y) for y in x.split(":")]
    A=D['Kp']+D['Km']-D['G'].T@np.diag([r0,rw])@D['G']; As=A*Sc[:,None]*Sc[None,:]
    lam=cp.Variable(N); Mx=Zy.T@As@Zy - Zy.T@cp.diag(cp.hstack([lam,lam])+Ml)@Zy
    prob=cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam,D['Nb2']))),[lam>=0,(Mx+Mx.T)/2<<0]); prob.solve(solver='CLARABEL')
    print(f"tf={tf} s*={ss} rho=({r0:g},{rw:g}): ideal {prob.value:.5e}   moment term (zeta=0.1) {C2.moment_term(DR,(r0,rw)):.3e}",flush=True)
