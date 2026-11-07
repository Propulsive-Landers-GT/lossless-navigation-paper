"""Theorem S (pure-waste face) regime and constants. alpha=0 unless given.
Witness: planar single-crossing S-turn phi=om*s (s<=t1), om*(2t1-s) after; outward gimbal chi=phi+delta*sgn(phi);
t1 chosen so that int a1 sin chi = 0 (I_h=0).  gain_w = int a1 (1-cos chi).
Bound (all 3D maneuvers): gain <= A T (Om/(2pi) + dp)^2,  A=a10/(1+cos(delta+Om)), dp=2sin(delta/2)+eps_m sin(delta+Om).
Dent: |p|^2 >= (gain_w - bound) * T^3 (kap0 - A')/(12 A' kap0),  A'=A/a10^2, kap0=cos tb/((a2-a1)sin^2 tb)."""
import numpy as np
from scipy.optimize import brentq
def witness(T, om, delta, a10, alpha_rho1_over_m0=0.0, n=200001):
    s=np.linspace(0,T,n)
    a=a10/(1-alpha_rho1_over_m0*s)
    def prof(t1):
        phi=np.where(s<=t1, om*s, om*(2*t1-s))
        chi=phi+delta*np.sign(phi)
        return phi,chi
    def Ih(t1):
        _,chi=prof(t1); return np.trapezoid(a*np.sin(chi),s)
    t1=brentq(Ih,1e-9,T)
    phi,chi=prof(t1)
    gain=np.trapezoid(a*(1-np.cos(chi)),s)
    F=a*np.sin(chi)
    p=-np.trapezoid(s*F,s)          # landing offset r_h(tf) = -int s F (I_h=0)
    return dict(t1=t1, gain=gain, p=p, chimax=np.max(np.abs(chi)))
def bound(T, om, delta, a10, a20, alpha_rho1_over_m0=0.0):
    Om=om*T; tb=delta+Om
    eps=1/(1-alpha_rho1_over_m0*T)-1
    dp=2*np.sin(delta/2)+eps*np.sin(tb)
    A=a10/(1+np.cos(tb))
    B=A*T*(Om/(2*np.pi)+dp)**2
    if a20>a10:
        kap0=np.cos(tb)/((a20-a10)*np.sin(tb)**2); Ap=A/a10**2
        ok=kap0*a10**2>=A
        cdent=12*Ap*kap0/((kap0-Ap)*T**3) if kap0>Ap else np.inf
    else:
        ok=True; cdent=12*(A/a10**2)/T**3  # K absent: penalty infinite -> use moment via u only? (conservative: same formula with kap0=inf)
    return B, ok, cdent
if __name__=="__main__":
    g0=9.81
    print("small-angle check, delta=0: witness gain/(a1 T Om^2/2) ->",
          witness(1,1e-3,0,1)['gain']/(0.5*1e-6), " (0.0404..)")
    for (a10,a20,deg) in [(12,25,0),(12,25,5),(12,25,10),(12,25,15),(15,25,15)]:
        delta=np.deg2rad(deg)
        best=None
        for T in [1,2,3,4]:
          for Om in np.arange(0.1,1.41,0.05):
            om=Om/T
            if delta+Om>=np.pi/2: continue
            w=witness(T,om,delta,a10); B,ok,cd=bound(T,om,delta,a10,a20)
            alt = a10*np.cos(w['chimax'])>g0
            if w['gain']>B and ok and alt:
                dent=np.sqrt((w['gain']-B)/cd)
                best=(T,Om,w['gain'],B,dent,abs(w['p']))
          if best and best[0]==T:
            print(f"a1={a10} a2={a20} delta={deg}: T={T} max Om={best[1]:.2f} rad: gain_w={best[2]:.4f} bound={best[3]:.4f} dent>={best[4]:.3f} m (witness offset {best[5]:.3f} m)")
