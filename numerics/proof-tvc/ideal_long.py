"""DIAGNOSTIC (not rigorous): ideal zero-lateral bound, exact moment+clamp constraints, piecewise-constant basis,
no remainders, localized coefficients, optional tilt cap.  usage: ideal_long.py cap_deg tf ss N"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, cvxpy as cp, certificate2 as C2
from witness_nl import gtpl, evaluate
from localize import localize
cap=np.deg2rad(float(sys.argv[1])); tf,ss,N=float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4])
P=gtpl(); vf,pf,info,_=localize(P,tf,ss,cap=cap)
par=dict(C2.PAR); par.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0, cap=cap)
D=C2.setup(P,tf,ss,N,par,loc=(vf,pf)); h=D['h']
idx=np.arange(N); A=(D['Kp']+D['Km'])[np.ix_(idx,idx)]
cons=np.vstack([D['G'],D['C']])[:,idx]
u,s,vt=np.linalg.svd(cons); Z=vt[np.sum(s>1e-12*s[0]):].T
Sc=1/np.sqrt(np.full(N,h)); Zy=Z/Sc[:,None]; As=A*Sc[:,None]*Sc[None,:]
lam=cp.Variable(N); Mx=Zy.T@As@Zy - Zy.T@cp.diag(lam+D['Mlate'])@Zy
prob=cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam,D['Nb2']))),[lam>=0,(Mx+Mx.T)/2<<0]); prob.solve(solver='SCS',eps=1e-8,max_iters=100000)
nv=np.load(f"witness_cone_{tf}_{ss}_cap{sys.argv[1]}.npy"); G=evaluate(P,tf,ss,nv)['G']
print(f"cap={sys.argv[1]} tf={tf} s*={ss} N={N}: ideal zero-lateral bound {prob.value:.4e} vs G_w {G:.4e}  ratio {prob.value/G:.3f}",flush=True)
