"""S-procedure (Shor) upper bound on v0z for which landing AT THE PAD is possible from hop data (Pvr), M1, alpha=0,
GTPL constants (m0=80, rho 400/1000, delta 15deg, om 0.4), tf=4. Quadratic majorant (math/07 'Hop instance'):
  l = M_z - s* I_z = int (s-s*) a d_z <= V0 + Q,
  Q = int_0^{s*} |w| (a1 cbar |u|^2 - kap0 |K|^2) - int_{s*}^T w (a2|u|^2/2 + |Kb|^2/(2(a2-a1))),
  u = d_h = beta + e,  F = a1 u + K (dive), F = a2 u - Kb (brake; Kb=(a2-a)u, cost w|Kb|^2/(2(a2-a1)));  int F = 0, int s F = 0 (Pvr) [or only int F=0 (Pv)].
Per component, rotation-invariant => valid for coning.  Discretized (NOT a rigorous continuous-time certificate)."""
import numpy as np, scipy.linalg as sl, cvxpy as cp, sys
m0,r1,r2,g,T=80.,400.,1000.,9.80665,4.0
delta=np.deg2rad(15); om=0.4; a1=r1/m0; a2=r2/m0; dp=2*np.sin(delta/2)
def bound(sstar,N=40,mode="Pvr"):
    h=T/N; s=(np.arange(N)+.5)*h; dive=s<sstar; w=s-sstar
    tau=np.minimum(delta+om*s,np.pi/2-1e-3); cbar=1/(1+np.cos(tau))
    kap0=(np.cos(tau)/np.sin(tau))/((a2-a1)*np.sin(tau))
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2; I=np.eye(N); Z=np.zeros((N,N))
    # x=[udot(N), e(N), K(N)]; K plays K on dive cells and Fb on brake cells
    B=np.hstack([V,Z,Z]); E=np.hstack([Z,I,Z]); Kk=np.hstack([Z,Z,I]); U=np.hstack([I,Z,Z]); Uu=B+E
    cu=np.where(dive,np.abs(w)*a1*cbar,-w*a2/2)
    cK=np.where(dive,-np.abs(w)*kap0,-w/(2*(a2-a1)))
    Q=h*(Uu.T@np.diag(cu)@Uu+Kk.T@np.diag(cK)@Kk)
    Fm=np.where(dive[:,None],a1*Uu+Kk,a2*Uu-Kk)
    rows=[h*np.ones(N)@Fm]+([h*s@Fm] if mode=="Pvr" else [])
    Zs=sl.null_space(np.array(rows)); Mq=Zs.T@Q@Zs; Mq=(Mq+Mq.T)/2; n=Mq.shape[0]
    UZ=U@Zs; EZ=E@Zs
    Wr=np.stack([h*np.outer(UZ[k],UZ[k]).ravel() for k in range(N)],1)
    We=np.stack([h*np.outer(EZ[k],EZ[k]).ravel() for k in range(N)],1)
    rho=cp.Variable(N,nonneg=True); sig=cp.Variable(N,nonneg=True)
    M=cp.reshape(Wr@rho+We@sig,(n,n),order='C')-Mq
    pr=cp.Problem(cp.Minimize(om**2*h*cp.sum(rho)+dp**2*h*cp.sum(sig)),[M>>0]); pr.solve(solver=cp.CLARABEL)
    Qmax=pr.value
    V0=-a1*sstar**2/2+a2*(T-sstar)**2/2
    lmax=V0+Qmax
    v0z=g*T-(0.5*g*T**2-lmax)/sstar
    return Qmax,V0,v0z
if __name__=="__main__":
    N=int(sys.argv[1]) if len(sys.argv)>1 else 30
    for ss in [2.2,2.4,2.5]:
        for mode in ["Pvr","Pv"]:
            Qm,V0,v=bound(ss,N,mode)
            print(f"N={N} s*={ss} {mode}: Qmax={Qm:.4f} V0={V0:.4f} => v0z <= {v:.4f}",flush=True)
