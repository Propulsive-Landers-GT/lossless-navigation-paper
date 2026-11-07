import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np
import certificate as C
from witness_nl import gtpl
P=gtpl(); tf,ss,N=1.0,0.25,int(sys.argv[1]) if len(sys.argv)>1 else 80
for over in [dict(taup=0.05,tau=0.05,zeta=0.05), dict(taup=0.02,tau=0.02,zeta=0.02,xi=0.3)]:
    par=dict(C.PAR); par.update(over)
    D=C.setup(P,tf,ss,N,par)
    for rho in [3e-3,3e-2,3e-1]:
        c=C.solve_cert(D,rho,1e-1)
        if c is None: print(over,rho,"none",flush=True); continue
        lb=D['h']*np.sum(c['lam_lb']*D['Nb2'])
        print(over, f"rho={rho:g}: SDP={c['val']:.4e}  (lam_lb part {lb:.3e})  moment={C.moment_term(D,rho):.3e}",flush=True)
