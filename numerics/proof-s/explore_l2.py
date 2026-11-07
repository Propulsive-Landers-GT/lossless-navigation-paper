# Small-angle pure-waste model, delta=0: max int |beta|^2, |beta'|<=1, beta(0)=0
# Pv: int beta = 0 ; Pvr: also int s beta = 0.
import numpy as np, scipy.linalg as sl
N=400; h=1/N; s=(np.arange(N)+0.5)*h
V=np.tril(np.ones((N,N)))*h - np.eye(N)*h/2   # beta at midpoints = V u
def l2bound(cons):
    C=np.array([np.ones(N)*h] + ([s*h] if cons==2 else []))  # C beta = 0
    A=C@V
    Z=sl.null_space(A)       # u = Z y
    M=(V@Z).T@(V@Z)*h        # ||beta||^2
    Gm=Z.T@Z*h               # int u^2
    ev=sl.eigh(M,Gm,eigvals_only=True)
    return ev[-1]
print("L2 rho=1 bound: Pv", l2bound(1), " Pvr", l2bound(2), " 1/48=",1/48)
