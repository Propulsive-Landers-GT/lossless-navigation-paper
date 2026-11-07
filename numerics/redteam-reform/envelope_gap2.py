"""[redteam-reform] Tilt-only: weight line through the origin, e(s) = (c(s-s0), -(s-s0)): folded tilt chi jumps
from atan(c) to pi-atan(c) at s0.  Exact tilt-only DP (generalized weight) vs envelope cone support."""
import numpy as np
def dp(eh, ez, P):
    a1,a2,om,de,tf,N = P["a1"],P["a2"],P["omega"],P["delta"],P["tf"],P["N"]; h=tf/N
    J=int(np.floor(np.pi/(om*h))); phi=np.arange(J+1)*om*h
    nrm=np.hypot(eh,ez); chi=np.arctan2(np.abs(eh),ez)
    tau=np.clip(chi[:,None],np.clip(phi[None,:]-de,0,np.pi),np.clip(phi[None,:]+de,0,np.pi))
    c=np.cos(tau-chi[:,None]); r=h*nrm[:,None]*np.where(c>0,a2,a1)*c
    V=np.full(J+1,-1e18); V[0]=0
    for k in range(N):
        b=V.copy(); b[1:]=np.maximum(b[1:],V[:-1]); b[:-1]=np.maximum(b[:-1],V[1:]); V=b+r[k]
    return V.max()
P=dict(a1=5.0,a2=12.5,omega=0.4,delta=np.deg2rad(15.0),tf=7.0,N=1400)
h=P["tf"]/P["N"]; s=(np.arange(P["N"])+0.5)*h
for s0 in [3.0,4.0,5.0]:
  for c in [0.3,1.0,3.0]:
    eh=c*(s-s0); ez=-(s-s0)
    nrm=np.hypot(eh,ez); chi=np.arctan2(np.abs(eh),ez)
    tau=np.minimum(chi,P["delta"]+P["omega"]*s); cc=np.cos(tau-chi)
    Venv=(h*nrm*np.where(cc>0,P["a2"],P["a1"])*cc).sum(); Vdp=dp(eh,ez,P)
    print(f"s0={s0} c={c}: chi jump {np.rad2deg(np.pi-2*np.arctan(c)):.0f} deg; envelope {Venv:.3f} exact {Vdp:.3f} rel gap {(Venv-Vdp)/abs(Venv):.2%}")
