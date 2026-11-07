"""Independent forward simulation of the Theorem S witness: compute vertical data zeta_w from the witness
increments, integrate forward from zeta_w (RK45, exact mass), check v(T)=0, r_z(T)=0, r_z>=0, offset p_w,
and admissibility (|b'|=om, gimbal=delta). Also loads GTPL parameters from numerics/models.py to show (S1) fails."""
import sys, numpy as np
from scipy.integrate import solve_ivp
from verify_S import witness
sys.path.insert(0,'..'); import models
def sim(T,om,delta,m0,rho1,alpha,g0=9.81):
    W=witness(T,om,delta,m0,rho1,alpha); t1=W['t1']
    chi=lambda s: (lambda ph: ph+delta*np.sign(ph))(om*s if s<=t1 else om*(2*t1-s))
    def f(s,y):
        r,v,m=y[:3],y[3:6],y[6]; a=rho1/m; c=chi(s)
        return np.r_[v, a*np.sin(c), 0, a*np.cos(c)-g0, -alpha*rho1]
    # backward from landing state to get zeta (any lateral r0 is then a translate): integrate T->0
    yb=solve_ivp(f,[T,0],np.r_[0,0,0,0,0,0,m0-alpha*rho1*T],rtol=1e-11,atol=1e-12,max_step=T/2000,dense_output=True)
    y0=yb.y[:,-1]; zeta=(y0[2],y0[5]); lat0=y0[[0,1,3,4]]
    # forward from VERTICAL data (r0_lat=v0_lat=0): landing offset = -lateral r0 of backward run
    y0v=y0.copy(); y0v[[0,1,3,4]]=0
    yf=solve_ivp(f,[0,T],y0v,rtol=1e-11,atol=1e-12,max_step=T/2000,dense_output=True)
    ts=np.linspace(0,T,4001); Y=yf.sol(ts)
    return dict(zeta=zeta, v0lat_backward=lat0[2:], vT=yf.y[3:6,-1], rT=yf.y[:3,-1], min_rz=Y[2].min(), pw=W['p'])
if __name__=="__main__":
    R=sim(2.0,0.2,0.0,100,1200,0.0); print("demo delta=0:",{k:np.round(v,6) for k,v in R.items()})
    R=sim(2.0,0.1,np.deg2rad(10),100,1200,0.0); print("demo delta=10:",{k:np.round(v,6) for k,v in R.items()})
    P=models.gtpl(omega=0.4); print("GTPL params from models.gtpl:",{k:P[k] for k in P if k in('m0','rho1','rho2','alpha','delta','g')})
    m0,rho1=P['m0'],P['rho1']; print("GTPL rho1/m0 =",rho1/m0," vs g0 -> (S1) fails:",rho1/m0<9.81)
