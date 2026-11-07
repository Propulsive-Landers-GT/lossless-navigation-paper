"""[proof-tvc] Gimbal-rate-limited planar witness (GTPL: 100 deg/s per axis, gimbal centred at t=0).
Planar meridian: psi'' = a sin(mu)/eps, f = a cos(mu) - eps psi'^2, throttle a in [a1,a2] free, |mu|<=delta, |mu'|<=gdot.
Gain G = int (s-s*) f cos(psi) - J0, with the SAME J0 as the unconstrained competitor bound, so G_rl > U_total
(the zero-lateral bound over the larger, rate-unlimited class) would extend Theorem TVC-1 to the rate-limited class."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, casadi as ca
from witness_nl import gtpl, J0
def solve(P,tf,ss,gdot_deg=100.,N=100,starts=6,seed=0,nw=None):
    a1,a2,de,eps=P['a1'],P['a2'],P['de'],P['eps']; gd=np.deg2rad(gdot_deg); h=tf/N
    rng=np.random.default_rng(seed); best=None
    for st in range(starts):
        o=ca.Opti(); X=o.variable(3,N+1); U=o.variable(2,N)   # X=(psi,om,mu), U=(a, mudot)
        o.subject_to(X[:,0]==0); o.subject_to(X[0,N]==0); o.subject_to(X[1,N]==0)
        W=0
        def fdyn(x,u): return ca.vertcat(x[1], u[0]*ca.sin(x[2])/eps, u[1])
        for k in range(N):
            xk=X[:,k]; uk=U[:,k]
            k1=fdyn(xk,uk); k2=fdyn(xk+h/2*k1,uk); k3=fdyn(xk+h/2*k2,uk); k4=fdyn(xk+h*k3,uk)
            o.subject_to(X[:,k+1]==xk+h/6*(k1+2*k2+2*k3+k4))
            for (c,wt) in [(0,1/6),(0.5,4/6),(1,1/6)]:
                xm=xk+c*h*k1 if c<1 else X[:,k+1]
                if c==0.5: xm=(xk+X[:,k+1])/2
                s=(k+c)*h
                W+=h*wt*(s-ss)*(uk[0]*ca.cos(xm[2])-eps*xm[1]**2)*ca.cos(xm[0])
        o.subject_to(o.bounded(a1,U[0,:],a2)); o.subject_to(o.bounded(-gd,U[1,:],gd)); o.subject_to(o.bounded(-de,X[2,:],de))
        o.minimize(-W)
        aa=np.where((np.arange(N)+.5)*h<ss,a1,a2); o.set_initial(U[0,:],aa)
        if nw is not None and st==0:
            mu=np.arcsin(np.clip(eps*nw/aa,-np.sin(de),np.sin(de))); mu=np.clip(mu,-de,de)
            # rate-limited tracking of mu from 0
            mut=np.zeros(N+1); 
            for k in range(N): mut[k+1]=mut[k]+np.clip(mu[k]-mut[k],-gd*h,gd*h)
            o.set_initial(X[2,:],mut); o.set_initial(U[1,:],np.diff(mut)/h)
        else: o.set_initial(U[1,:],rng.uniform(-1,1,N)*gd*0.3)
        o.solver('ipopt',{'ipopt.print_level':0,'print_time':0,'ipopt.sb':'yes','ipopt.max_iter':3000})
        try: sol=o.solve()
        except RuntimeError: continue
        v=float(sol.value(W))
        if best is None or v>best: best=v
    return best-J0(P,tf,ss)
if __name__=="__main__":
    P=gtpl()
    nw=np.load('witness_cone_1.0_0.25.npy')
    for gd in [1e5,1000.,100.]:
        print(f"tf=1.0 s*=0.25 gimbal rate {gd:g} deg/s: G_rl={solve(P,1.0,0.25,gd,nw=nw):.4e}",flush=True)
