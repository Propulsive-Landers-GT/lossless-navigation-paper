"""[adversary-6dof] B*-type (dive-then-brake) face for PURE TVC with altitude constraint r_z>=0 and terminal upright-at-rest.
maximize l = r0z + s* v0z over F (soft landing r(tf)=0, v(tf)=0), with and without zero-lateral data (r0_lat = v0_lat = 0).
If max with lateral=0 < unconstrained max  => F (with altitude constraint) nonconvex (rotation-midpoint lemma)."""
import numpy as np, sys, casadi as ca
from m3tvc import *
P=gtpl(); g=9.81
tf=float(sys.argv[1]); N=int(sys.argv[2]); sstar=float(sys.argv[3]); gim=sys.argv[4]; rate=sys.argv[5]=="1"
R=Reach6(P,tf,N,gimbal=gim,rate_limited=rate,terminal_att=True,with_r=True)
o=R.opti; X=R.X; ir=R.ir; h=tf/N
dv=X[0:3,N]; dr=X[ir:ir+3,N]
r0z=-g*tf**2/2+tf*dv[2]-dr[2]; v0z=g*tf-dv[2]
for k in range(N+1):
    t=k*h
    o.subject_to(r0z+v0z*t-g*t**2/2+X[ir+2,k]>=0)
latpar=o.parameter(); o.subject_to(latpar*(tf*dv[0:2]-dr[0:2])==0)   # r0_lat
o.minimize(-(r0z+sstar*v0z))
rng=np.random.default_rng(3)
diag=np.array([1.0,1.0]) if gim=="box" else np.array([1.0,0.0])
def pat_dive(s,r,f=sstar/tf):  # gimbal inward first then outward during dive, then recover
    return -1.0 if s<0.5*f else (1.0 if s<f else (-0.5 if s<2*f else 0.3*np.sin(8*s)))
def run(lat):
    o.set_value(latpar,1 if lat else 0)
    out=[]
    inits=[(pat_dive,diag),(None,None)]
    for p,ax in inits:
        R.init(rng,p,axis=ax)
        r=R.solve(lat=[0,0] if lat else None)
        if r["ok"]:
            Xv=r["X"]; val=-float(o.debug.value(o.f)) if False else None
            d=Xv[0:3,-1]; q=Xv[ir:ir+3,-1]
            l=(-g*tf**2/2+tf*d[2]-q[2])+sstar*(g*tf-d[2])
            out.append((l,np.hypot(*d[:2]),np.hypot(*(tf*d[:2]-q[:2])),tilt(Xv).max(),r))
            print("lat" if lat else "free", round(l,5), "vlat",round(out[-1][1],4),"rlat",round(out[-1][2],4),"maxtilt",round(out[-1][3],2),flush=True)
    return max(out,key=lambda x:x[0]) if out else None
bf=run(False)
o.set_value(latpar,1)
R.opti.set_initial(R.X,bf[4]["X"]); R.opti.set_initial(R.U,bf[4]["U"])
rc=R.solve(lat=[0,0])
bl=run(True)
if rc["ok"]:
    d=rc["X"][0:3,-1]; q=rc["X"][ir:ir+3,-1]; lc=(-g*tf**2/2+tf*d[2]-q[2])+sstar*(g*tf-d[2])
    print("lat(continuation)", round(lc,5), flush=True)
    if lc>bl[0]: bl=(lc,)+bl[1:]
print(f"RESULT tf={tf} N={N} s*={sstar} gim={gim} rate={rate}: max l free={bf[0]:.5f} (|v0lat|={bf[1]:.4f}, |r0lat|={bf[2]:.4f}, r0z={(-g*tf**2/2+tf*bf[4]['X'][2,-1]-bf[4]['X'][ir+2,-1]):.2f})  max l lat=0: {bl[0]:.5f}  gap={bf[0]-bl[0]:.4e}")
