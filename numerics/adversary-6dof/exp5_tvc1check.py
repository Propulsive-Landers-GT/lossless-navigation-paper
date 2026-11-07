"""[adversary-6dof] Independent falsification test of [proof-tvc] TVC-1 (math/06): constant mass (alpha=0), cone 15 deg,
unlimited gimbal rate, upright at rest, NO state constraint (competitor class = F).  Maximize gain = W_z - J0 where
l = r0z + s* v0z = W_z + kappa, (i) free, (ii) with r0_lat = v0_lat = 0.  Certificate claims: zero-lateral gain <= U
(R0: 6.274e-5, R1: 6.980e-5); witness gain G_w = 7.269e-5.  Any zero-lateral NLP point (inner discretization => truly
admissible) with gain > U refutes the certificate."""
import os, sys, numpy as np
os.environ.setdefault("OMP_NUM_THREADS","1")
from m3tvc import *
roll = sys.argv[1]=="1"; N=int(sys.argv[2]) if len(sys.argv)>2 else 80
P=gtpl(alpha=0.0); g=9.80665; tf=1.0; ss=0.25
R=Reach6(P,tf,N,gimbal="cone",rate_limited=False,terminal_att=True,with_r=True,roll=roll)
o=R.opti; X=R.X; ir=R.ir
dv=X[0:3,N]; dr=X[ir:ir+3,N]
r0z=-g*tf**2/2+tf*dv[2]-dr[2]; v0z=g*tf-dv[2]
kappa=g*tf*(ss-tf/2); a1=P["rho1"]/P["m0"]; a2=P["rho2"]/P["m0"]
J0=-a1*np.cos(P["delta"])*ss**2/2+a2*(tf-ss)**2/2
latpar=o.parameter(); o.subject_to(latpar*(tf*dv[0:2]-dr[0:2])==0)
# remove the tilt guard? it is inactive (tilt << 1 deg); keep.
o.minimize(-(r0z+ss*v0z))
o.solver("ipopt",{"ipopt.print_level":0,"print_time":0,"ipopt.max_iter":5000,"ipopt.tol":1e-12,"ipopt.sb":"yes"})
rng=np.random.default_rng(11)
def gain(r):
    d=r["X"][0:3,-1]; q=r["X"][ir:ir+3,-1]
    return (-g*tf**2/2+tf*d[2]-q[2])+ss*(g*tf-d[2])-kappa-J0, np.hypot(*d[:2]), np.hypot(*(tf*d[:2]-q[:2]))
def dive(s,r): return 1.0 if s<0.125 else (-1.0 if s<0.25 else (0.3 if s<0.45 else (-0.3 if s<0.8 else 0.3)))
res={}
for lat in (False,True):
    o.set_value(latpar,1 if lat else 0); best=None
    for k,(p,ax) in enumerate([(dive,np.array([1.,0.])),(dive,np.array([0.,1.])),(None,None),(None,None)]):
        R.init(rng,p,axis=ax); r=R.solve(lat=[0,0] if lat else None)
        G,vl,rl=gain(r); print(("lat " if lat else "free"),k,r["ok"],f"gain={G:.4e} |v0lat|={vl:.2e} |r0lat|={rl:.2e}",flush=True)
        if r["ok"] and (best is None or G>best[0]): best=(G,r)
    if lat and res.get(False):
        R.opti.set_initial(R.X,res[False][1]["X"]); R.opti.set_initial(R.U,res[False][1]["U"]); r=R.solve(lat=[0,0])
        G,vl,rl=gain(r); print("lat cont",r["ok"],f"gain={G:.4e}",flush=True)
        if r["ok"] and G>best[0]: best=(G,r)
    res[lat]=best
print(f"RESULT roll={roll} N={N}: max gain free={res[False][0]:.5e} (G_w=7.269e-5)  max gain zero-lateral={res[True][0]:.5e}  (certified U: R0 6.274e-5, R1 6.980e-5)")
