"""DIAGNOSTIC (not rigorous): ideal zero-lateral bounds at long horizon with different moment treatments.
usage: ideal_moments.py tf ss N cap_deg|none"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl, segments_bangbang, evaluate_segments
from localize import localize
tf,ss,N=float(sys.argv[1]),float(sys.argv[2]),int(sys.argv[3]); cap=None if sys.argv[4]=='none' else np.deg2rad(float(sys.argv[4]))
P=gtpl(); vf,pf,info,_=localize(P,tf,ss,cap=cap)
par=dict(C2.PAR); par.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0, cap=cap)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf)); h=D['h']
idx=np.arange(N); A=(D['Kp']+D['Km'])[np.ix_(idx,idx)]
G0=D['G'][0][idx]; Gw=D['G'][1][idx]; C=D['C'][:,idx]
G=evaluate_segments(P,tf,ss,segments_bangbang(P,tf,ss,np.load(f"witness_cone_{tf}_{ss}.npy")))['G']
def bound(cons, rho0=0.0):
    u,s,vt=np.linalg.svd(cons); Z=vt[np.sum(s>1e-12*s[0]):].T
    Sc=1/np.sqrt(np.full(N,h)); Zy=Z/Sc[:,None]; As=(A-rho0*np.outer(G0,G0))*Sc[:,None]*Sc[None,:]
    lam=cp.Variable(N); Mx=Zy.T@As@Zy - Zy.T@cp.diag(lam+D['Mlate'])@Zy
    prob=cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam,D['Nb2']))),[lam>=0,(Mx+Mx.T)/2<<0]); prob.solve(solver='CLARABEL')
    return prob.value
print(f"tf={tf} s*={ss} cap={sys.argv[4]} G_w={G:.4e}  loc={ {k:round(float(v),4) for k,v in info.items()} }",flush=True)
for name,cons,r0 in [("both exact",np.vstack([G0,Gw,C]),0),("weighted only",np.vstack([Gw,C]),0),("weighted exact + rho0=0.05",np.vstack([Gw,C]),0.05),("weighted exact + rho0=0.2",np.vstack([Gw,C]),0.2)]:
    b=bound(cons,r0); print(f"  {name:28s}: ideal bound {b:.4e}  ratio {b/G:.3f}",flush=True)
