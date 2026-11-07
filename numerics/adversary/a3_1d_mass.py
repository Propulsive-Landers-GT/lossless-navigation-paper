"""A3: exact 3DOF/1D rocket with mass depletion and thrust fixed along e_z (pointing angle 0):
is the reachable set {(S,W)} = {(int sigma, int (tf-s) sigma)}, sigma=T/m, T in [rho1,rho2], convex?
Boundary curves: W_max(S) = burn-early (rho2 then rho1), W_min(S) = burn-late (rho1 then rho2).
(Reachable set is exactly {(S,W): S in [Smin,Smax], W_min(S)<=W<=W_max(S)} by comparison/continuity.)"""
import numpy as np
def curves(m0, rho1, rho2, alpha, tf, n=4001):
    s = np.linspace(0, tf, n); h = s[1]-s[0]
    out = {}
    for name, early, late in (('max', rho2, rho1), ('min', rho1, rho2)):
        S, W = [], []
        for t1 in np.linspace(0, tf, 801):
            T = np.where(s < t1, early, late)
            m = m0 - alpha*np.concatenate([[0], np.cumsum(T[:-1])*h])
            sig = T/m
            S.append(np.trapezoid(sig, s)); W.append(np.trapezoid((tf-s)*sig, s))
        out[name] = (np.array(S), np.array(W))
    return out
def convexity_defect(S, W, upper):
    o = np.argsort(S); S, W = S[o], W[o]
    # second differences of W as function of S (uniform-ish grid -> use slopes)
    sl = np.diff(W)/np.maximum(np.diff(S), 1e-15)
    ds = np.diff(sl)
    return (ds.max() if upper else -ds.min())   # >0 => concavity (upper) / convexity (lower) violated
for (lab, m0, a) in (('GTPL alpha', 80, 5.66e-4), ('alpha x20 (mass ratio ~0.5)', 80, 5.66e-4*20)):
    c = curves(m0, 400., 1000., a, 8.0)
    up = convexity_defect(*c['max'], upper=True); lo = convexity_defect(*c['min'], upper=False)
    # explicit midpoint test on upper curve endpoints vs interior
    S, W = c['max']; i, j = 50, 750; Sm, Wm = (S[i]+S[j])/2, (W[i]+W[j])/2
    Wcap = np.interp(Sm, *[arr[np.argsort(S)] for arr in (S, W)])
    print(f"{lab}: upper-curve concavity violation={up:.3e}, lower-curve convexity violation={lo:.3e}; "
          f"midpoint test W_mid={Wm:.5f} vs W_max(S_mid)={Wcap:.5f} -> {'OUTSIDE (nonconvex)' if Wm>Wcap+1e-9 else 'inside'}")
