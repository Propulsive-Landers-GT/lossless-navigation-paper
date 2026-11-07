import numpy as np, cvxpy as cp
g0=1.0; rho1=0.5; rho2=2.0; delta=np.deg2rad(30); tf=10.0; N=100; h=tf/N
D=lambda s: 0.5*(g0-s)*tf*(rho2-g0)/(rho2-s)*tf
H=0.5*(D(rho1)+D(rho1*np.cos(delta))); print("D(rho1)",D(rho1),"D(rho1 cos)",D(rho1*np.cos(delta)),"h",H)
def solve(sig_fix=None, obj=None):
    T=cp.Variable((N,3)); G=cp.Variable(N)
    r=cp.Variable((N+1,3)); v=cp.Variable((N+1,3))
    c=[r[0]==np.array([0,0,H]), v[0]==0, r[N]==0, v[N]==0]
    gv=np.array([0,0,-g0])
    for j in range(N):
        c+=[v[j+1]==v[j]+h*(T[j]+gv), r[j+1]==r[j]+h*v[j]+h*h/2*(T[j]+gv),
            cp.norm(T[j])<=G[j], T[j,2]>=G[j]*np.cos(delta), G[j]>=rho1, G[j]<=rho2]
    if sig_fix is not None: c+=[G==sig_fix]
    p=cp.Problem(cp.Minimize(cp.sum(G)*h if obj is None else obj(T)),c); p.solve(solver=cp.CLARABEL)
    return T.value,G.value,p
T,G,p=solve(); nT=np.linalg.norm(T,axis=1)
lossy=np.where(G-nT>1e-5)[0]
print("cost",p.value,"max lateral",np.abs(T[:,:2]).max(),"#lossy",len(lossy),"Gamma at lossy (min)",G[lossy].min() if len(lossy) else None, G[lossy].max() if len(lossy) else None)
rng=np.random.default_rng(0); C=rng.standard_normal((N,3))
T2,G2,p2=solve(sig_fix=G,obj=lambda TT: -cp.sum(cp.multiply(C,TT)))
n2=np.linalg.norm(T2,axis=1); print("purified #lossy",np.sum(G-n2>1e-5), "max gap", (G-n2).max())
