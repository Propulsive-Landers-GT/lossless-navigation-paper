import os; os.environ["OMP_NUM_THREADS"]="1"; os.environ["FASTL"]="1"; os.environ["NOFLOOR"]="1"
import numpy as np, certificate2 as C2, riccati_cert as R
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf,ss,N=1.0,0.25,20; rho=(1.0,15.0)
par=dict(C2.PAR); par.update(tau=0.03,zeta=0.1,xi=0.1,lam_max=3e-3)
vf,pf,info,_=localize(P,tf,ss)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf))
c=C2.solve_cert(D,rho,0.1); lam=c['lam']
par['eta1_time']=par['eta1_cells']*tf/N
FD=R.fine_data(P,tf,ss,N,par,(vf,pf),rho,0.1)
# dense matrix for comparison
tau,taup=par['tau'],par['taup']; h=D['h']; Wd=D['Wdiag']
A=(1+tau)*D['Kp']+(1-taup)*D['Km']-(1-0.2)*D['G'].T@np.diag(rho)@D['G']-(1-taup)*0.1*D['C'].T@D['C']+(1+tau)*par['lam_max']*sum(D['Lk'])
for f in [1.0,1.02,0.9,0.7]:
    l=lam*f
    Mv=A-np.diag(Wd*np.concatenate([l+D['Mlate']]*2)); Sc=1/np.sqrt(Wd); top=np.linalg.eigvalsh((Mv+Mv.T)/2*np.outer(Sc,Sc)).max()
    ok,w,k=R.riccati_check(FD,l)
    print(f"scale {f}: dense top eig {top:.3e} (neg={top<0})  riccati ok={ok} worst={w:.3e}")
print("Mlate diff", np.abs(FD['Mlate']-D['Mlate']).max(), "Nb2 diff", np.abs(FD['Nb2']-D['Nb2']).max())
