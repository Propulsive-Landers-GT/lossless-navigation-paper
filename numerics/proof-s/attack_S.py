"""Adversarial check of the master inequality: maximize  gain - Cm |pi_m|^2  over 3D trajectories
(min throttle, alpha=0; b driven by tangential angular velocity |w|<=om; d anywhere in cap(b,delta)).
The theorem says the sup is <= Bnd.  Also reports best value with exact Pvr constraints (m=0) vs Pv (only int F=0)."""
import numpy as np, sys
from scipy.optimize import minimize
from verify_S import consts, witness
rng=np.random.default_rng(1)
def build(T,om,delta,a1,N):
    h=T/N; s=(np.arange(N)+.5)*h
    G=np.array([[T,T**2/2],[T**2/2,T**3/3]]); Gi=np.linalg.inv(G)
    def traj(x):
        W=x[:2*N].reshape(N,2); Dg=x[2*N:].reshape(N,2)
        b=np.array([0,0,1.0]); ds=[]
        for k in range(N):
            e1=np.array([1.0,0,0])-b[0]*b; e1/=np.linalg.norm(e1); e2=np.cross(b,e1)
            wv=W[k,0]*e1+W[k,1]*e2; nw=np.linalg.norm(wv)
            sc=om*np.tanh(nw)/nw if nw>1e-12 else om
            wv=wv*sc; ang=np.linalg.norm(wv)*h
            if ang>1e-15:
                t=wv/np.linalg.norm(wv); bm=np.cos(ang/2)*b+np.sin(ang/2)*t; bn=np.cos(ang)*b+np.sin(ang)*t
            else: bm=b; bn=b
            # gimbal at midpoint attitude (cone radius reduced by om*h/2 to stay admissible in-cell)
            r=Dg[k]; nr=np.linalg.norm(r); gam=max(delta-om*h/2,0)*np.tanh(nr)
            u=(r[0]*e1+r[1]*e2)/nr if nr>1e-12 else e1
            u=u-np.dot(u,bm)*bm; u/=np.linalg.norm(u)
            ds.append(np.cos(gam)*bm+np.sin(gam)*u); b=bn/np.linalg.norm(bn)
        return np.array(ds)
    def stats(x):
        D=traj(x); gain=a1*np.sum(1-D[:,2])*h; F=a1*D[:,:2]
        m=np.array([F.sum(0)*h,(s[:,None]*F).sum(0)*h]); pim=sum(m[:,j]@Gi@m[:,j] for j in range(2))
        return gain,pim,m
    return stats
def run(T,om,delta,m0,rho1,rho2,N=24,starts=12):
    a1=rho1/m0; C=consts(T,om,delta,m0,rho1,rho2,0.0); stats=build(T,om,delta,a1,N)
    best=-np.inf; bestPvr=-np.inf
    for k in range(starts):
        x0=rng.normal(size=4*N)*rng.uniform(0.3,3)
        f=lambda x: -(stats(x)[0]-C['Cm']*stats(x)[1])
        r=minimize(f,x0,method='L-BFGS-B',options=dict(maxiter=300))
        best=max(best,-r.fun)
        # exact Pvr (m=0) via penalty continuation
        x=r.x
        for mu in [1e2,1e4,1e6]:
            g=lambda x: -(stats(x)[0]-mu*np.sum(stats(x)[2]**2))
            x=minimize(g,x,method='L-BFGS-B',options=dict(maxiter=300)).x
        gg,pp,mm=stats(x)
        if np.abs(mm).max()<1e-4: bestPvr=max(bestPvr,gg)
    W=witness(T,om,delta,m0,rho1,0.0)
    print(f"T={T} om={om} delta={np.rad2deg(delta):.0f}: sup[gain-Cm|pi|^2] found={best:.5f} <= Bnd={C['Bnd']:.5f}? {best<=C['Bnd']+1e-9};  best Pvr gain found={bestPvr:.5f};  Pv witness gain={W['gain']:.5f}",flush=True)
if __name__=="__main__":
    run(2.0,0.2,0.0,100,1200,2500)
    run(2.0,0.15,np.deg2rad(5),100,1200,2500)
    run(2.0,0.1,np.deg2rad(10),100,1200,2500)
