"""Closed-form reduced value of the lateral sign-change face of K (M1, rho1=0, alpha=0, omega=1, a2=1).
Functional:  <e_x, int_0^tf (s - sigma) a d ds>.  beta = signed lateral tilt = pi/2 - angle(e_x, b).
V(b*) = sup over admissible controls with beta(sigma) = b*  (proof: math/possibility-rho0.md, Lemma 3)."""
import numpy as np

def _F(A, c, k, s):          # antiderivative of (A - s) sin(c + k s)
    return -(A - s) * np.cos(c + k*s) / k - np.sin(c + k*s) / k**2

def _seg(A, c, k, x0, x1):   # int_{x0}^{x1} (A-s) sin^+(c+ks) ds  for linear arg, restricted to arg>0
    # arg(s) = c + k s ; positive set is s > -c/k (k>0) or s < -c/k (k<0)
    z = -c / k
    if k > 0: lo, hi = np.maximum(x0, z), x1
    else:     lo, hi = x0, np.minimum(x1, z)
    hi = np.maximum(hi, lo)
    return _F(A, c, k, hi) - _F(A, c, k, lo)

def V(bs, sig, tf, dl):
    bs = np.asarray(bs, float)
    s1 = (sig - bs) / 2
    E = _seg(sig, dl, 1.0, 0.0, s1) + _seg(sig, dl - bs + sig, -1.0, s1, sig)
    # late: int_0^tau t sin^+(dl + bs + t) dt  = int (A - t) sin(...) with A=0, sign flipped
    tau = tf - sig
    Lt = -_seg(0.0, dl + bs, 1.0, 0.0, tau)
    return E + Lt

def beta_path(bs, sig, s):
    return np.where(s <= sig, np.maximum(-s, bs - (sig - s)), bs + (s - sig))

def moments(bs, sig, tf, dl, n=400001):
    s = np.linspace(0, tf, n); be = beta_path(bs, sig, s); early = s < sig
    ang = np.where(early, be - dl, be + dl)
    contrib = np.where(early, (sig - s)*np.sin(dl - be), (s - sig)*np.sin(be + dl))
    a = (contrib > 0).astype(float)
    u = np.stack([a*np.sin(ang), 0*s, a*np.cos(ang)], 1)
    I = np.trapezoid(u, s, axis=0); J = np.trapezoid((tf - s)[:, None]*u, s, axis=0)
    return np.concatenate([I, J]), dict(s=s, beta=be, a=a, ang=ang)

def branches(sig, tf, dl, nb=4001):
    bs = np.linspace(-sig, sig, nb); v = V(bs, sig, tf, dl)
    loc = [j for j in range(nb) if (j == 0 or v[j] >= v[j-1]) and (j == nb-1 or v[j] > v[j+1])]
    return bs, v, loc
