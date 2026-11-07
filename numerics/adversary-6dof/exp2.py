"""[adversary-6dof] Adversarial search for a zero-lateral trajectory at the bottom face (try to REACH the centre).
Starts: (a) the free minimizer itself (continuation), (b) its time-split variants, (c) rotating/coning gimbal patterns,
(d) two-lobe patterns (direction flips by pi at mid-time), (e) random.  Reports min V0 found and the gap to Vmin."""
import numpy as np, sys
from m3tvc import *
P = gtpl()
tf=float(sys.argv[1]); N=int(sys.argv[2]); term=sys.argv[3]=="1"; gim=sys.argv[4]; rate=sys.argv[5]=="1"
R = Reach6(P, tf, N, gimbal=gim, rate_limited=rate, terminal_att=term)
rng=np.random.default_rng(7)
diag = np.array([1.0,1.0]) if gim=="box" else np.array([1.0,0.0])
# free minimizer
best=None
for p in [lambda s,r:1.0 if s<0.55 else -1.0, lambda s,r:-1.0 if (s<0.25 or s>0.75) else 1.0, None, None]:
    R.init(rng,p,axis=diag if p is not None else None); r=R.solve()
    if r["ok"] and (best is None or r["vN"][2]<best["vN"][2]): best=r
Vm=best["vN"][2]; print(f"Vmin={Vm:.6f} lat={np.hypot(*best['vN'][:2]):.5f}", flush=True)
res=[]
def rot(th): return np.array([[np.cos(th),-np.sin(th)],[np.sin(th),np.cos(th)]])
pats=[]
for k in [0.5,1,2,3,5]:
    pats.append(("cone%.1f"%k, lambda s,r,k=k: rot(2*np.pi*k*s)))
pats.append(("lobe2", lambda s,r: np.eye(2) if s<0.5 else -np.eye(2)))
pats.append(("lobe2q", lambda s,r: (np.eye(2) if (s%0.5)<0.25 else -np.eye(2)) * (1 if s<0.5 else -1)))
pats.append(("perp", lambda s,r: np.eye(2) if s<0.5 else rot(np.pi/2)))
for name,M in pats:
    for trial in range(2):
        R.init(rng, (lambda s,r,M=M: (M(s,r)@diag)[0]), axis=np.array([1.0,0.0]))  # placeholder, overwritten below
        # custom init with matrix pattern
        Pp=R.P; h=tf/N; X=np.zeros((R.nx,N+1)); X[3,0]=Pp["m0"]; X[4,0]=1; U=np.zeros((R.nu,N))
        lim=np.sin(Pp["delta"]) if gim=="cone" else Pp["delta"]
        ax0=rot(rng.uniform(0,2*np.pi)) if gim=="cone" else np.eye(2)
        for k in range(N):
            gk=(M((k+.5)/N,rng)@ax0@diag)*lim*(0.97 if trial==0 else rng.uniform(0.6,1))
            if gim=="box": gk=np.clip(gk,-lim,lim)
            elif np.linalg.norm(gk)>lim*0.999: gk*=lim*0.999/np.linalg.norm(gk)
            U[0,k]=Pp["rho1"]
            U[1:3,k]=np.clip((gk-X[11:13,k])/h,-Pp["gdot"],Pp["gdot"]) if rate else gk
            X[:,k+1]=np.array(R.F(X[:,k],U[:,k])).ravel(); X[4:8,k+1]/=np.linalg.norm(X[4:8,k+1])
        R.opti.set_initial(R.X,X); R.opti.set_initial(R.U,U)
        r=R.solve(lat=[0,0]); res.append((name,r["ok"],r["vN"][2])); print(name, r["ok"], round(r["vN"][2],6), flush=True)
# continuation from minimizer
R.opti.set_initial(R.X,best["X"]); R.opti.set_initial(R.U,best["U"]); r=R.solve(lat=[0,0]); res.append(("from_min",r["ok"],r["vN"][2])); print("from_min",r["ok"],r["vN"][2])
for i in range(6):
    R.init(rng,None); r=R.solve(lat=[0,0]); res.append(("rand",r["ok"],r["vN"][2])); print("rand",r["ok"],r["vN"][2], flush=True)
ok=[x[2] for x in res if x[1]]
print(f"RESULT tf={tf} N={N} term={term} gim={gim} rate={rate}: Vmin={Vm:.6f}  best V0(lat=0)={min(ok):.6f}  gap={min(ok)-Vm:.4e}  n_ok={len(ok)}/{len(res)}")
