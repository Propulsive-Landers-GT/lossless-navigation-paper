"""S-procedure (Shor) upper bound for the pure-waste face, exact-model quadratic majorant, alpha=0.
Per lateral component (bound is rotation-invariant => valid for all 3D / coning maneuvers).
  gain <= Q = int a1 cbar(s) (beta+e)^2 - kappa(s) K^2 ,  F = a1(beta+e)+K,  int F = 0, int s F = 0
  budgets |beta'|<=om, |e|<=dp (=2 sin(delta/2)).
Certificate: rho,sigma>=0 with Q <= int rho beta'^2 + int sigma e^2 on subspace => gain <= om^2 int rho + dp^2 int sigma.
Compare with exact planar antisymmetric triangle witness gain."""
import numpy as np, scipy.linalg as sl, cvxpy as cp, sys
def setup(T, om, delta, a1, a2, N):
    h=T/N; s=(np.arange(N)+.5)*h
    tau=np.minimum(delta+om*s, np.pi/2-1e-3)
    cbar=1/(1+np.cos(tau)); dp=2*np.sin(delta/2)
    Kmax=(a2-a1)*np.sin(tau); kap=np.cos(tau)/np.sin(tau)/np.maximum(Kmax,1e-12)
    # variables x = [u (beta' per cell, N), e (N), K (N)]; beta at midpoints = V u
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2
    I=np.eye(N); Z=np.zeros((N,N))
    B=np.hstack([V,I*0,Z]); E=np.hstack([Z,I,Z]); Kk=np.hstack([Z,Z,I]); U=np.hstack([I,Z,Z])
    BE=B+E
    Q=h*(BE.T@np.diag(a1*cbar)@BE - Kk.T@np.diag(kap)@Kk)
    Fm=a1*BE+Kk
    C=np.vstack([h*np.ones(N)@Fm, h*s@Fm])
    return dict(h=h,s=s,Q=Q,U=U,E=E,C=C,dp=dp,N=N)
def bound(T, om, delta, a1, a2, N=60, constant=False):
    d=setup(T,om,delta,a1,a2,N); h=d['h']
    Zs=sl.null_space(d['C'])
    rho=cp.Variable(N, nonneg=True); sig=cp.Variable(N, nonneg=True)
    if constant: cons_extra=[rho==rho[0], sig==sig[0]]
    else: cons_extra=[]
    Mq=Zs.T@d['Q']@Zs
    UZ=d['U']@Zs; EZ=d['E']@Zs
    n=Mq.shape[0]
    Wr=np.stack([h*np.outer(UZ[k],UZ[k]).ravel() for k in range(N)],1)
    We=np.stack([h*np.outer(EZ[k],EZ[k]).ravel() for k in range(N)],1)
    M=cp.reshape(Wr@rho+We@sig,(n,n),order='C')-(Mq+Mq.T)/2
    prob=cp.Problem(cp.Minimize(om**2*h*cp.sum(rho)+d['dp']**2*h*cp.sum(sig)),[M>>0]+cons_extra)
    prob.solve(solver=cp.CLARABEL)
    return prob.value, rho.value, sig.value
def witness(T, om, delta, a1, n=20000):
    s=(np.arange(n)+.5)*T/n
    phi=om*np.minimum(s, np.abs(T/2-s))  # |tilt| of b, tent on each half
    chi=phi+delta
    return a1*np.sum(1-np.cos(chi))*T/n, a1*T*(1-np.cos(delta))
if __name__=="__main__":
    from regime import witness as wit1
    a1,a2=12.0,25.0
    for (T,Om,deg) in [(2,0.4,0),(2,0.3,10),(2,0.3,15),(2,0.5,15),(2,0.3,20)]:
        delta=np.deg2rad(deg); om=Om/T
        w=wit1(T,om,delta,a1)['gain']
        for N in [30,50]:
            b,_,_=bound(T,om,delta,a1,a2,N=N)
            print(f"T={T} Om={Om} delta={deg}deg N={N}: single-crossing witness gain={w:.6f}  Shor/S-procedure bound={b:.6f}  margin={w-b:.3e}",flush=True)
