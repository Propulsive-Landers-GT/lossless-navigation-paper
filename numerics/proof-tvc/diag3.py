import os; os.environ["OMP_NUM_THREADS"]="1"; os.environ["FASTL"]="1"
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf,ss,Nc=3.0,0.5,60; cap=np.deg2rad(30); rho=(0.1,45.0)
par=dict(C2.PAR); par.update(tau=0.03,zeta=0.15,xi=0.15,lam_max=0.01,kap=0.03,cap=cap)
vf,pf,info,_=localize(P,tf,ss,cap=cap)
D=C2.setup(P,tf,ss,Nc,par,loc=(vf,pf)); hc=D['h']; idx=np.arange(Nc)
A=(1+0.03)*D['Kp']+(1-0.01)*D['Km']-0.8*D['G'].T@np.diag(rho)@D['G']-(0.99)*0.1*D['C'].T@D['C']+(1.03)*par['lam_max']*sum(D['Lk'])
A=A[np.ix_(idx,idx)]; A=(A+A.T)/2/hc
print("A diag range", A.diagonal().min(), A.diagonal().max(), "top eig A", np.linalg.eigvalsh(A).max(), "Mlate max", D['Mlate'].max(), "lam_ub min/max", D['lam_ub'].min(), D['lam_ub'].max())
for caps in [True, False]:
    lamv=cp.Variable(Nc); cons=[lamv>=0,(A-cp.diag(lamv+D['Mlate']))<<0]
    if caps: cons.append(lamv<=D['lam_ub'])
    pr=cp.Problem(cp.Minimize(hc*cp.sum(cp.multiply(lamv,D['Nb2']))),cons)
    try: pr.solve(solver='CLARABEL'); print("caps",caps,"clarabel",pr.status,pr.value, None if lamv.value is None else np.round(lamv.value[:12],5), None if lamv.value is None else lamv.value.max())
    except Exception as e: print("caps",caps,"clarabel error",e); pr.solve(solver='SCS',eps=1e-8,max_iters=50000); print("  scs",pr.status,pr.value, None if lamv.value is None else lamv.value.max())
