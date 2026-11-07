# delta=0, alpha=0, with throttle-excess K: maximize [int a1 cbar beta^2 - kappa K^2] / (a1 int beta'^2)
# s.t. int (a1 beta + K) = int s (a1 beta + K) = 0.  Time normalized T=1, om s -> Om s.
import numpy as np, scipy.linalg as sl
def mu(Om, ratio, N=500):   # ratio=(a2-a1)/a1 ; work with a1=1 and time T=1, om=Om
    h=1.0/N; s=(np.arange(N)+.5)*h
    tau=np.maximum(Om*s,1e-9); c=1/(1+np.cos(tau))
    kap=np.cos(tau)/(ratio*np.sin(tau)**2)       # a1=1 ; units: T=1, a1=1 (K in units of a1)
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2; I=np.eye(N); Zr=np.zeros((N,N))
    B=np.hstack([V,Zr]); K=np.hstack([Zr,I]); U=np.hstack([I,Zr])
    F=B+K; C=np.vstack([h*np.ones(N)@F, h*s@F]); Z=sl.null_space(C)
    Q=h*(B.T@np.diag(c)@B - K.T@np.diag(kap)@K); R=h*U.T@U
    Mq=Z.T@Q@Z; Mr=Z.T@R@Z+1e-12*np.eye(Z.shape[1])
    # generalized: max x'Qx / x'Rx with R singular in K-directions -> eliminate K (Q negative def there)
    nB=N
    # Schur: maximize over K first
    return None
def mu2(Om, ratio, N=500):
    h=1.0/N; s=(np.arange(N)+.5)*h
    tau=np.maximum(Om*s,1e-9); c=1/(1+np.cos(tau)); kap=np.cos(tau)/(ratio*np.sin(tau)**2)
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2
    # variables u (beta'), K. Constraint: P(Vu)+P K=0 where P=[1;s] h. Parametrize K = K0(u) + K_perp
    P=np.vstack([np.ones(N),s])*h
    # min_K int kap K^2 s.t. P K = -P V u  -> K = -W P^T (P W P^T)^{-1} P V u, W=diag(1/(kap h))
    W=np.diag(1/(kap*h)); S=P@W@P.T
    Kop=-W@P.T@np.linalg.solve(S,P@V)
    Q=V.T@np.diag(c*h)@V - Kop.T@np.diag(kap*h)@Kop
    G=np.eye(N)*h
    return sl.eigh(Q,G,eigvals_only=True)[-1]
for ratio in [1.5, 1.0, 0.5]:
  for Om in [0.5,0.8,1.0]:
    A=Om/4; wit=1-np.sin(A)/A
    m=mu2(Om,ratio)
    print(f"(a2-a1)/a1={ratio} Om={Om}: bound/wit={m*Om**2/wit:.4f}")
