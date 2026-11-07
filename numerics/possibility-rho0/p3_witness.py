"""Tie witness on the lateral face of K (M1, rho1=0, alpha=0) and its moments.
Units: omega=1 unless rescaled; a2 = 1.  Usage: p3_witness.py tf delta_deg
Finds sigma_c where V(.;sigma) has two separated global maximisers, builds the two maximiser
trajectories, their moments X=(I,J) in R^6, and the midpoint.  Saves npz for p4 (NLP check)."""
import numpy as np, sys, json

def Vgrid(bs, sig, tf, dl, n=4000):
    s1 = np.linspace(0, sig, n)[None, :]
    L = np.maximum(-s1, bs[:, None] - (sig - s1))
    E = np.trapezoid((sig - s1) * np.maximum(0, np.sin(dl - L)), s1, axis=1)
    s2 = np.linspace(sig, tf, n)[None, :]
    Lt = np.trapezoid((s2 - sig) * np.maximum(0, np.sin(np.minimum(dl + bs[:, None] + (s2 - sig), np.pi/2))), s2, axis=1)
    return E + Lt

def beta_path(bs, sig, s):
    return np.where(s <= sig, np.maximum(-s, bs - (sig - s)), bs + (s - sig))

def moments(bs, sig, tf, dl, n=200001):
    s = np.linspace(0, tf, n)
    be = beta_path(bs, sig, s)
    early = s < sig
    ang = np.where(early, be - dl, np.minimum(be + dl, np.pi/2))      # signed tilt of d in x-z plane
    contrib = np.where(early, (sig - s) * np.sin(dl - be), (s - sig) * np.sin(np.minimum(be + dl, np.pi/2)))
    a = (contrib > 0).astype(float)
    u = np.stack([a*np.sin(ang), 0*s, a*np.cos(ang)], 1)
    I = np.trapezoid(u, s, axis=0); J = np.trapezoid((tf - s)[:, None]*u, s, axis=0)
    return np.concatenate([I, J]), s, be, a, ang

def find_tie(tf, dl, nb=2001):
    sg = np.linspace(0.02, 0.98, 500) * tf
    args = []
    for sig in sg:
        bs = np.linspace(-sig, sig, nb); v = Vgrid(bs, sig, tf, dl); args.append(bs[np.argmax(v)]/sig)
    args = np.array(args); k = np.argmax(np.abs(np.diff(args)))
    lo, hi = sg[k], sg[k+1]; jump = abs(args[k+1]-args[k])
    # bisection on which branch wins, split at midpoint of the two normalized argmaxes
    split = 0.5*(args[k]+args[k+1])
    def f(sig):
        bs = np.linspace(-sig, sig, nb); v = Vgrid(bs, sig, tf, dl)
        m1 = v[bs/sig <= split].max(); m2 = v[bs/sig > split].max()
        return m1 - m2, bs[bs/sig <= split][np.argmax(v[bs/sig <= split])], bs[bs/sig > split][np.argmax(v[bs/sig > split])], v
    flo = f(lo)[0]
    for _ in range(50):
        mid = 0.5*(lo+hi); fm = f(mid)[0]
        if np.sign(fm) == np.sign(flo): lo, flo = mid, fm
        else: hi = mid
    d, b1, b2, v = f(0.5*(lo+hi))
    bs = np.linspace(-hi, hi, nb)
    # depth of the valley between the two maximisers (relative)
    sel = (bs > min(b1,b2)) & (bs < max(b1,b2))
    valley = v.max() - v[sel].min() if sel.any() else 0.0
    return 0.5*(lo+hi), b1, b2, jump, d, v.max(), valley

if __name__ == "__main__":
    tf = float(sys.argv[1]); dl = np.deg2rad(float(sys.argv[2]))
    sig, b1, b2, jump, d, vmax, valley = find_tie(tf, dl)
    X1 = moments(b1, sig, tf, dl)[0]; X2 = moments(b2, sig, tf, dl)[0]
    n = np.array([tf - sig, 0, 0, -1, 0, 0])   # support direction (psi, chi)
    print(json.dumps(dict(tf=tf, delta=dl, sigma_c=sig, beta1=b1, beta2=b2, jump=jump, tie_residual=d,
                          hmax=vmax, valley=valley, nX1=float(n@X1), nX2=float(n@X2),
                          X1=X1.tolist(), X2=X2.tolist(), Xm=(0.5*(X1+X2)).tolist(), sep=float(np.linalg.norm(X1-X2))), indent=1))
    np.savez(f"witness_tf{tf}_d{sys.argv[2]}.npz", tf=tf, dl=dl, sig=sig, b1=b1, b2=b2, X1=X1, X2=X2, n=n)
