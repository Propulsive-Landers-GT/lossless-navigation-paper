"""[proof-tvc] Ablation of certificate2 relaxations at tf=1, s*=0.25, N given (diagnostic only, not a proof)."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1"); os.environ["FASTL"]="1"
import numpy as np, certificate2 as C2
from witness_nl import gtpl
from localize import localize
P=gtpl(); tf,ss=1.0,0.25; N=int(sys.argv[1]) if len(sys.argv)>1 else 60
vf,pf,info,_=localize(P,tf,ss)
base=dict(C2.PAR); base.update(lam_max=3e-3, tau=0.03)
cases=[("ideal: no remainders, zeta=xi=0, tau=0, kap->0, no curvature remainder, no caps", dict(lam_max=1.0, zeta=1e-9, xi=1e-9, tau=1e-9, taup=1e-9, kap=1e-9, noL=1, ideal_theta=1, eta1_cells=0, IDEAL=1)),
       ("+ tau=0.03 taup=0.01 (remainder floors)", dict(zeta=1e-9, xi=1e-9, kap=1e-9, noL=1, ideal_theta=1, eta1_cells=0)),
       ("+ eta1=2, xi=0.05 (Delta p caps)", dict(zeta=1e-9, kap=1e-9, noL=1, ideal_theta=1)),
       ("+ zeta=0.05", dict(kap=1e-9, noL=1, ideal_theta=1)),
       ("+ r_theta=0.2 (late torque split)", dict(kap=1e-9, noL=1)),
       ("full (kap=0.01)", dict())]
for name,ov in cases:
    par=dict(base); ov=dict(ov); ideal=ov.pop('IDEAL',0); noL=ov.pop('noL',0); par.update(ov)
    D=C2.setup(P,tf,ss,N,par,loc=(vf,pf))
    if ov.get('ideal_theta') is None and False: pass
    if ideal: D['lam_ub'][:] = 1.0
    if ideal or noL:
        D['Lk']=[0*L for L in D['Lk']]
    for rho in [3e-3,3e-2]:
        if ideal:
            # turn off remainder floors by monkeypatching
            rc=C2.remainder_constants; C2.remainder_constants=lambda D,rho:(np.zeros(D['N']),0.0)
        c=C2.solve_cert(D,rho,1e-1)
        if ideal: C2.remainder_constants=rc
        print(f"{name:60s} rho={rho:g}: {'none' if c is None else '%.4e'%c['val']}", flush=True)
