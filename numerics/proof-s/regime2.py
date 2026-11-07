"""Improved bound: gain <= a10 c0 T (Om/2pi + dp)^2 + E4,  c0=1/(1+cos delta),
E4 = int_0^T a1(s) (cbar(s)-c0) sin^2(delta+om s) ds  (pointwise |u|<=sin tau(s)),  cbar(s)=1/(1+cos(delta+om s)).
K-penalty kap0=cos tb/((a2-a1) sin^2 tb), tb=delta+Om; need kap0 a10^2 >= a10 c0 for p=0; dent constant uses A=a10 c0."""
import numpy as np, sys
from regime import witness
def bound2(T, om, delta, a10, a20, arm=0.0):
    Om=om*T; tb=delta+Om
    eps=1/(1-arm*T)-1
    dp=2*np.sin(delta/2)+eps*np.sin(tb)
    c0=1/(1+np.cos(delta)); A=a10*c0
    s=np.linspace(0,T,20001); a1=a10/(1-arm*s)
    E4=np.trapezoid(a1*(1/(1+np.cos(delta+om*s))-c0)*np.sin(delta+om*s)**2,s)
    B=A*T*(Om/(2*np.pi)+dp)**2+E4
    if a20>a10:
        kap0=np.cos(tb)/((a20-a10)*np.sin(tb)**2); Ap=A/a10**2
        ok=kap0>=Ap; cd=12*Ap*kap0/((kap0-Ap)*T**3) if kap0>Ap else np.inf
    else: ok=True; cd=12*(A/a10**2)/T**3
    return B, ok, cd, E4
def scan(a10,a20,deg,T,g0=9.81,arm=0.0,verbose=False):
    delta=np.deg2rad(deg); rows=[]
    for Om in np.arange(0.05,1.51,0.05):
        if delta+Om>=np.pi/2-1e-9: break
        om=Om/T; w=witness(T,om,delta,a10,arm); B,ok,cd,E4=bound2(T,om,delta,a10,a20,arm)
        alt=a10*np.cos(w['chimax'])>g0
        dent=np.sqrt((w['gain']-B)/cd) if (w['gain']>B and ok) else 0.0
        rows.append((Om,w['gain'],B,E4,dent,abs(w['p']),alt,ok))
    return rows
if __name__=="__main__":
    for (a10,a20) in [(12.0,25.0)]:
      for deg in [0,5,10,15,20]:
        for T in [2.0,4.0]:
            rows=scan(a10,a20,deg,T)
            good=[r for r in rows if r[4]>0 and r[6]]
            if not good: print(f"a1={a10} a2={a20} delta={deg} T={T}: no certified Om"); continue
            Oms=[r[0] for r in good]; best=max(good,key=lambda r:r[4])
            print(f"a1={a10} a2={a20} delta={deg:2d} T={T}: certified Om in [{min(Oms):.2f},{max(Oms):.2f}]; best Om={best[0]:.2f}: gain_w={best[1]:.4f} bound={best[2]:.4f} (E4={best[3]:.1e}) dent>={best[4]:.3f} m, witness |p|={best[5]:.2f} m")
