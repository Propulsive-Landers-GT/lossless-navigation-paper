"""[adversary-6dof] Sanity check of Thm D: decoupled transverse torque (|tau_perp|<=tau), cone gimbal, free terminal attitude.
Expect Vmin == V* = int a1 cos(delta + Phi), Phi = abar s^2/2, and |lat| = int a1 sin(delta+Phi)."""
import numpy as np
from m3tvc import *
P=gtpl(); tf=1.0; N=80; tau=61.0
R=Reach6(P,tf,N,gimbal="cone",decoupled=True,tau_dec=tau)
rng=np.random.default_rng(0); best=None
for i in range(4):
    R.init(rng,None if i>1 else (lambda s,r:1.0)); r=R.solve()
    if r["ok"] and (best is None or r["vN"][2]<best["vN"][2]): best=r
s=np.linspace(0,tf,20001); ab=tau/P["Jt"]; Phi=ab*s**2/2; a1=P["rho1"]/(P["m0"]-P["alpha"]*P["rho1"]*s)
Vs=np.trapezoid(a1*np.cos(P["delta"]+Phi),s); Ls=np.trapezoid(a1*np.sin(P["delta"]+Phi),s)
print(f"decoupled: NLP Vmin={best['vN'][2]:.6f} lat={np.hypot(*best['vN'][:2]):.6f} | theory V*={Vs:.6f} lat*={Ls:.6f}")
r=R.solve(lat=[0,0]); print(f"decoupled lat=0: V0={r['vN'][2]:.6f} gap={r['vN'][2]-best['vN'][2]:.4e}")
