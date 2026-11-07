"""Early-kink sign-change face (altitude-friendly): axis p_hat = (cos d, 0, sin d) (delta ABOVE horizontal, +x),
functional <p_hat, int (s - sigma) a d ds>; early primer -p_hat points delta BELOW horizontal (-x).
omega=1, a2=1.  early payoff (sigma-s) sin^+(-beta); late payoff (s-sigma) sin(min(2 delta + beta, pi/2))^+."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
def V(bs, sig, T, dl, n=3000):
    bs = np.atleast_1d(np.asarray(bs, float))
    s1 = np.linspace(0, sig, n)[None, :]
    L = np.maximum(-s1, bs[:, None] - (sig - s1))
    E = np.trapezoid((sig - s1)*np.maximum(0, np.sin(-L)), s1, axis=1)
    t = np.linspace(0, T - sig, n)[None, :]
    Lt = np.trapezoid(t*np.maximum(0, np.sin(np.minimum(2*dl + bs[:, None] + t, np.pi/2))), t, axis=1)
    return E + Lt
if __name__ == "__main__":
    for T, dd in [(0.3, 15), (0.6, 15), (1.0, 15), (0.2, 40)]:
        dl = np.deg2rad(dd); print(f"T={T} delta={dd}")
        prev = None
        for sig in np.linspace(0.02, 0.98, 49)*T:
            bs = np.linspace(-sig, sig, 2001); v = V(bs, sig, T, dl)
            loc = [round(bs[j]/sig, 3) for j in range(len(v)) if (j == 0 or v[j] >= v[j-1]) and (j == len(v)-1 or v[j] > v[j+1])]
            arg = bs[np.argmax(v)]/sig
            if prev is not None and abs(arg - prev) > 0.1: print(f"  JUMP between sigma/T={prevs:.3f} and {sig/T:.3f}: {prev:+.3f} -> {arg:+.3f}; local maxima {loc}")
            prev, prevs = arg, sig/T
