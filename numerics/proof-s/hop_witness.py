"""Planar Pv witness at hop data (r0=0, v0=(0,0,v0z)), M1, GTPL constants, tf=4.
Maximize v0z s.t. I_h=0 (v0_lat=0), landing r(tf)=(p,0), v(tf)=0, r_z(t)>=0.
Inner discretization: N ZOH cells, thrust T_k, thrust tilt chi_k (planar, signed), body tilt phi at nodes with
|phi_{k+1}-phi_k| <= om h, |chi_k - phi(s)| <= delta for all s in the cell (enforced as |chi_k-phi_k|,|chi_k-phi_{k+1}| <= delta,
valid since phi is linear in the cell). Exact mass (log formula), exact integrals of piecewise-constant thrust.
Returns an admissible continuous trajectory (rigorous witness up to float)."""
import numpy as np, json, sys
from scipy.optimize import minimize
m0,r1,r2,g,T=80.,400.,1000.,9.80665,4.0
delta=np.deg2rad(15); om=0.4
def setup(N,al):
    h=T/N
    def incr(x):
        Tq=x[:N]; chi=x[N:2*N]
        # exact: within cell k, m(t)=m_k - al*T_k*(t-t_k); a = T_k/m
        mk=m0-al*h*np.concatenate([[0],np.cumsum(Tq)[:-1]])
        tk=np.arange(N)*h
        if al>0:
            # int_cell a dt = -(1/al) ln(m_{k+1}/m_k); int_cell t a dt = t_k*A0 + int_0^h tau*T/(m_k-al T tau) dtau
            A0=-np.log((mk-al*Tq*h)/mk)/al
            c=al*Tq; A1=(-h/al) - (mk/(al*c))*np.log((mk-c*h)/mk)   # int_0^h tau*Tq/(mk-c tau) dtau
            A1=Tq*( -h/c - mk/c**2*np.log((mk-c*h)/mk) )
        else:
            A0=Tq/m0*h; A1=Tq/m0*h*h/2
        S1=tk*A0+A1
        Ix=np.sum(np.sin(chi)*A0); Iz=np.sum(np.cos(chi)*A0)
        Mx=np.sum(np.sin(chi)*S1); Mz=np.sum(np.cos(chi)*S1)
        return Ix,Iz,Mx,Mz,A0,S1
    def alt(x):
        # r_z at nodes from data: v0z = gT - Iz ; r_z(t)= v0z t - g t^2/2 + int_0^t (t-s) a cos chi
        Tq=x[:N]; chi=x[N:2*N]; Ix,Iz,Mx,Mz,A0,S1=incr(x); v0z=g*T-Iz
        tn=np.arange(1,N+1)*h
        # int_0^{t_j}(t_j - s) f = t_j*cum(A0 f) - cum(S1 f)
        f0=np.cos(chi)*A0; f1=np.cos(chi)*S1
        rz=v0z*tn-g*tn**2/2+tn*np.cumsum(f0)-np.cumsum(f1)
        return rz[:-1]
    return h,incr,alt
def solve(N=40,al=5.665090072099601e-4,seed=0,starts=20):
    h,incr,alt=setup(N,al); rng=np.random.default_rng(seed)
    # x=[T(N), chi(N), phi(N+1)]
    def obj(x): return incr(x)[1]            # minimize Iz <=> maximize v0z
    cons=[dict(type='eq',fun=lambda x: incr(x)[3]-0.5*g*T**2),
          dict(type='eq',fun=lambda x: incr(x)[0]),
          dict(type='eq',fun=lambda x: x[2*N]),                         # phi(0)=0
          dict(type='ineq',fun=lambda x: om*h-np.abs(np.diff(x[2*N:]))+0*x[0]),
          dict(type='ineq',fun=lambda x: delta-np.abs(x[N:2*N]-x[2*N:3*N])),
          dict(type='ineq',fun=lambda x: delta-np.abs(x[N:2*N]-x[2*N+1:3*N+1])),
          dict(type='ineq',fun=lambda x: alt(x))]
    bnds=[(r1,r2)]*N+[(-1.4,1.4)]*N+[(-1.4,1.4)]*(N+1)
    best=None
    for k in range(starts):
        t1=rng.uniform(0.6,2.4); s=np.arange(N+1)*h
        ph=np.where(s<t1,om*s,om*(2*t1-s))*rng.uniform(0.5,1)
        ph=np.clip(ph,-1.2,1.2); chi=(ph[:-1]+ph[1:])/2+delta*np.sign(ph[:-1]+ph[1:]+1e-9)*0.9
        Tq=np.where(s[:-1]<2.4,r1,r2)
        x0=np.concatenate([Tq,chi,ph])
        r=minimize(obj,x0,method='SLSQP',bounds=bnds,constraints=cons,options=dict(maxiter=600,ftol=1e-12))
        if r.success or True:
            viol=max(abs(incr(r.x)[3]-0.5*g*T**2),abs(incr(r.x)[0]),np.max(np.abs(np.diff(r.x[2*N:])))-om*h,
                     np.max(np.abs(r.x[N:2*N]-r.x[2*N:3*N]))-delta,-np.min(alt(r.x)),abs(r.x[2*N]))
            if viol<1e-7 and (best is None or r.fun<best[0]): best=(r.fun,r.x)
    Iz=best[0]; x=best[1]; Ix,Iz,Mx,Mz,A0,S1=incr(x)
    return dict(N=N,alpha=al,v0z=g*T-Iz,p=-Mx,x=x.tolist(),minrz=float(np.min(alt(x))))
if __name__=="__main__":
    for al in [0.0,5.665090072099601e-4]:
        R=solve(al=al); print(f"alpha={al}: Pv-witness v0z={R['v0z']:.5f}  landing offset p={R['p']:.4f} m  min r_z={R['minrz']:.3e}",flush=True)
        json.dump(R,open(f"hop_witness_alpha{al:g}.json","w"))
