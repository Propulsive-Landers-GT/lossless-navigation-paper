# c1 = int_0^1 || P_perp 1_[s,1] ||_{L1} ds  (P = L2 projection onto affine functions on [0,1])
import numpy as np
for n in [2000,4000,8000]:
    t=(np.arange(n)+.5)/n
    # orthonormal basis of affine: q0=1, q1=sqrt(12)(t-1/2)
    tot=0.0
    S=(np.arange(n)+.5)/n
    for s in S[::max(1,n//2000)]:
        f=(t>=s).astype(float)
        c0=1-s; c1=np.sqrt(12)*((1-s**2)/2-(1-s)/2)
        r=f-c0-c1*np.sqrt(12)*(t-.5)
        tot+=np.mean(np.abs(r))
    print(n, tot/len(S[::max(1,n//2000)]))
