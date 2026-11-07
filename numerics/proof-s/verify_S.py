"""Lemma S (pure-waste face) -- constants of Theorem S and an independent random-trajectory check of the
master inequality (valid for EVERY admissible M1 trajectory, any 3D/coning attitude path):
  gain(c) := int a1(s) - I_z(c)  <=  Bnd + Cm * |pi_m|^2,
  Bnd = a10 c0 T (Om/(2pi) + de)^2 + E4,   c0 = 1/(1+cos delta),  de = 2 sin(delta/2) + eps_m sin(tb),
  E4  = a10 (1+eps_m)^2 int_0^T (cbar(s)-c0) sin^2(tau(s)) ds,  tau(s)=delta+om s, cbar=1/(1+cos tau), tb=delta+Om,
  |pi_m|^2 = m^T G^{-1} m,  m = (int F, int s F) (lateral, F = a d_h),  G = [[T,T^2/2],[T^2/2,T^3/3]],
  Cm = A' k0/(k0-A'),  A' = c0/a10,  k0 = cot(tb)/((a2max-a10) sin tb)   (Cm = A' if rho1=rho2).
For landing data with v0_lat = r0_lat = 0 and offset p: m = (0,-p), |pi_m|^2 = 12|p|^2/T^3.
Usage: python verify_S.py            (table + random check)"""
import numpy as np
from scipy.optimize import brentq
rng=np.random.default_rng(0)
def consts(T,om,delta,m0,rho1,rho2,alpha):
    Om=om*T; tb=delta+Om; assert tb<np.pi/2
    a10=rho1/m0; a2max=rho2/(m0-alpha*rho2*T); eps=(rho1/(m0-alpha*rho1*T))/a10-1
    c0=1/(1+np.cos(delta)); de=2*np.sin(delta/2)+eps*np.sin(tb)
    s=np.linspace(0,T,40001); tau=delta+om*s
    E4=a10*(1+eps)**2*np.trapezoid((1/(1+np.cos(tau))-c0)*np.sin(tau)**2,s)
    Bnd=a10*c0*T*(Om/(2*np.pi)+de)**2+E4
    Ap=c0/a10
    if rho2>rho1:
        k0=(np.cos(tb)/np.sin(tb))/((a2max-a10)*np.sin(tb))
        Cm=Ap*k0/(k0-Ap) if k0>Ap else np.inf
    else: Cm=Ap
    return dict(Bnd=Bnd,Cm=Cm,E4=E4,a10=a10)
def witness(T,om,delta,m0,rho1,alpha,n=400001):
    s=np.linspace(0,T,n); a=rho1/(m0-alpha*rho1*s)
    def chi(t1):
        phi=np.where(s<=t1,om*s,om*(2*t1-s)); return phi+delta*np.sign(phi)
    t1=brentq(lambda t1: np.trapezoid(a*np.sin(chi(t1)),s),1e-9,T,xtol=1e-14)
    c=chi(t1); F=a*np.sin(c)
    return dict(t1=t1,gain=np.trapezoid(a*(1-np.cos(c)),s),p=-np.trapezoid(s*F,s),chimax=np.abs(c).max(),Ih=np.trapezoid(F,s))
def theorem_row(T,om,delta,m0,rho1,rho2,alpha,g0=9.81,gs=None):
    C=consts(T,om,delta,m0,rho1,rho2,alpha); W=witness(T,om,delta,m0,rho1,alpha)
    marg=W['gain']-C['Bnd']; a10=rho1/m0
    alt=a10*np.cos(W['chimax'])>g0
    dent=np.sqrt(marg*T**3/(12*C['Cm'])) if marg>0 else 0.0
    return dict(margin=marg,dent=dent,alt=alt,p=abs(W['p']),gain=W['gain'],Bnd=C['Bnd'],t1=W['t1'],chimax=W['chimax'])
def random_traj(T,om,delta,m0,rho1,rho2,alpha,N=2000,mode=0):
    h=T/N; s=(np.arange(N)+.5)*h
    b=np.array([0,0,1.0]); B=[]
    # attitude: random rate-limited 3D path; modes: 0 random walk, 1 coning (precession), 2 S-turn-ish
    phase=rng.uniform(0,2*np.pi); prec=rng.uniform(-1,1)
    for k in range(N):
        if mode==0: w=rng.normal(size=3)
        elif mode==1:
            tilt=np.arccos(np.clip(b[2],-1,1)); 
            az=np.array([-b[1],b[0],0.0]) if tilt>1e-6 else np.array([np.cos(phase),np.sin(phase),0])
            rad=np.cross(az,b) if tilt>1e-6 else np.zeros(3)
            w=(rng.uniform(0.2,1)*az*np.sign(prec)+rng.uniform(-0.6,0.6)*rad) if tilt>0.4*om*T*abs(prec) else np.cross(b,[np.cos(phase),np.sin(phase),0])
        else:
            w=np.cross(b,[np.cos(phase),np.sin(phase),0])*(1 if s[k]<T*abs(prec)*0.5 else -1)
        w=w-np.dot(w,b)*b; nw=np.linalg.norm(w)
        if nw>0: w=w/nw*om*rng.uniform(0.5,1.0)
        # rotate b by angle |w| h about axis b x w_dir (geodesic step)
        ang=np.linalg.norm(w)*h
        if ang>0:
            t=w/np.linalg.norm(w); bmid=np.cos(ang/2)*b+np.sin(ang/2)*t
            B.append(bmid/np.linalg.norm(bmid)); b=np.cos(ang)*b+np.sin(ang)*t; b/=np.linalg.norm(b)
        else: B.append(b.copy())
    B=np.array(B)
    # gimbal: random direction within cone (slightly inside to absorb in-cell motion)
    D=[]
    for k in range(N):
        bk=B[k]; e1=np.cross(bk,[1,0,0]); 
        if np.linalg.norm(e1)<1e-3: e1=np.cross(bk,[0,1,0])
        e1/=np.linalg.norm(e1); e2=np.cross(bk,e1)
        g=rng.uniform(0,max(delta-om*h,0)) if rng.uniform()<0.5 else max(delta-om*h,0)
        ps=rng.uniform(0,2*np.pi) if rng.uniform()<0.5 else np.arctan2(*([np.dot(bk,e2),np.dot(bk,e1)]))
        D.append(np.cos(g)*bk+np.sin(g)*(np.cos(ps)*e1+np.sin(ps)*e2))
    D=np.array(D)
    Tq=np.where(rng.uniform(size=N)<0.7,rho1,rng.uniform(rho1,rho2,N))
    m=m0-alpha*h*np.concatenate([[0],np.cumsum(Tq)[:-1]])-alpha*h*Tq/2
    a=Tq/m; a1=rho1/(m0-alpha*rho1*s)
    gain=np.sum(a1-a*D[:,2])*h
    F=a[:,None]*D[:,:2]
    mvec=np.array([F.sum(0)*h,(s[:,None]*F).sum(0)*h])   # 2x2: rows moments, cols components
    G=np.array([[T,T**2/2],[T**2/2,T**3/3]]); Gi=np.linalg.inv(G)
    pim=sum(mvec[:,j]@Gi@mvec[:,j] for j in range(2))
    return gain,pim
if __name__=="__main__":
    print("== Theorem S table (pure-waste face), g0=9.81 ==")
    cases=[("high-T/W demo, delta=0",2.0,0.20,0.0,100,1200,2500,0.0),
           ("high-T/W demo, delta=0, T=4",4.0,0.10,0.0,100,1200,2500,0.0),
           ("high-T/W demo, delta=5deg",2.0,0.15,np.deg2rad(5),100,1200,2500,0.0),
           ("high-T/W demo, delta=5deg, alpha",2.0,0.15,np.deg2rad(5),100,1200,2500,5.66e-4),
           ("high-T/W demo, delta=10deg",2.0,0.10,np.deg2rad(10),100,1200,2500,0.0),
           ("high-T/W demo, delta=10deg, T=4",4.0,0.05,np.deg2rad(10),100,1200,2500,0.0),
           ("GTPL-like masses (rho1/m0=5): altitude fails",2.0,0.2,0.0,80,400,1000,5.66e-4)]
    for name,T,om,dl,m0,r1,r2,al in cases:
        R=theorem_row(T,om,dl,m0,r1,r2,al)
        print(f"{name:45s} T={T} om={om} Om={om*T:.2f}: gain_w={R['gain']:.5f} bound={R['Bnd']:.5f} margin={R['margin']:.2e} "
              f"dent>={R['dent']:.3f} m (witness |p|={R['p']:.2f} m, t1={R['t1']:.3f}, chimax={np.rad2deg(R['chimax']):.1f}deg) altitude_ok={R['alt']}")
    print("== random-trajectory check of master inequality (3D incl. coning) ==")
    for (T,om,dl,m0,r1,r2,al) in [(2.0,0.2,0.0,100,1200,2500,0.0),(2.0,0.15,np.deg2rad(5),100,1200,2500,5.66e-4),(3.0,0.2,np.deg2rad(10),80,400,1000,5.66e-4)]:
        C=consts(T,om,dl,m0,r1,r2,al); worst=-np.inf
        for it in range(300):
            g,pim=random_traj(T,om,dl,m0,r1,r2,al,N=600,mode=it%3)
            worst=max(worst,g-C['Bnd']-C['Cm']*pim)
        print(f"T={T} om={om} delta={np.rad2deg(dl):.0f}: max over 300 random 3D trajectories of [gain - Bnd - Cm|pi_m|^2] = {worst:.3e}  (must be <= 0)")
