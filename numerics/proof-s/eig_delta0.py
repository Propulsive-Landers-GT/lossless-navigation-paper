# delta=0, alpha=0, min-throttle: gain <= a1 int cbar(s)|beta|^2, cbar=1/(1+cos(om s)); constant rho:
# gain <= a1 * mu * om^2 T,  mu = max int cbar beta^2 / int beta'^2 on {beta(0)=0, int beta = int s beta = 0}
import numpy as np, scipy.linalg as sl
def mu(Om, N=600, weight=True, cons=2):
    T=1.0; h=T/N; s=(np.arange(N)+.5)*h
    c=1/(1+np.cos(Om*s)) if weight else 0.5*np.ones(N)
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2
    C=np.array([np.ones(N)*h]+([s*h] if cons==2 else []))@V
    Z=sl.null_space(C); M=(V@Z).T@np.diag(c*h)@(V@Z); G=Z.T@Z*h
    return sl.eigh(M,G,eigvals_only=True)[-1]
for Om in [0.25,0.5,1.0,1.2,1.4]:
    A=Om/4; wit=1-np.sin(A)/A           # per (a1 T)
    m=mu(Om); print(f"Om={Om}: witness/(a1T)={wit:.6e}  bound/(a1T)={m*Om**2:.6e} ratio={m*Om**2/wit:.4f}   (const 1/2: {mu(Om,weight=False)*Om**2/wit:.4f})")
