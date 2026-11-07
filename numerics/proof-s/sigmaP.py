import numpy as np, scipy.linalg as sl
for N in [400,800,1600]:
    h=1/N; s=(np.arange(N)+.5)*h
    V=np.tril(np.ones((N,N)))*h-np.eye(N)*h/2
    Bs=np.vstack([np.ones(N),s]).T; Qb,_=np.linalg.qr(Bs)
    Pp=np.eye(N)-Qb@Qb.T
    sv=np.linalg.svd(Pp@V,compute_uv=False)
    print(N, "sigma_P^2 =", sv[0]**2, " sigma_P=",sv[0], " (lambda* constrained 0.017728, 1/48=",1/48,")")
