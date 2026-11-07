"""Sign-change face with arbitrary axis p_hat (angle phi0 from e_z), M1, rho1=0, alpha=0, omega=1, a2=1.
Functional  <p_hat, int (s - sigma) a d>.  Exact 1D reduction: theta(s)=angle(p_hat,b(s)), beta = phi0 - theta.
early (s<sigma): weight (sigma-s) * c(pi - phi0 + beta);  late: (s-sigma) * c(|phi0 - beta|)
c(x) = 1 (x<=delta), cos(x-delta) (delta<=x<=delta+pi/2), 0 beyond."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
def c(x, dl):
    return np.where(x <= dl, 1.0, np.maximum(0.0, np.cos(np.minimum(x - dl, np.pi))))
def V(bs, sig, tf, dl, phi0, n=1500):
    s1 = np.linspace(0, sig, n)[None, :]
    L = np.maximum(-s1, bs[:, None] - (sig - s1))
    E = np.trapezoid((sig - s1) * c(np.pi - phi0 + L, dl), s1, axis=1)
    s2 = np.linspace(sig, tf, n)[None, :]
    U = bs[:, None] + (s2 - sig)
    Lt = np.trapezoid((s2 - sig) * c(np.abs(phi0 - U), dl), s2, axis=1)
    return E + Lt
def maxjump(tf, dl, phi0, ns=160, nb=601):
    prev = None; best = 0.0; where = None
    for sig in np.linspace(0.01, 0.99, ns) * tf:
        bs = np.linspace(-sig, sig, nb); arg = bs[np.argmax(V(bs, sig, tf, dl, phi0))] / sig
        if prev is not None and abs(arg - prev) > best: best, where = abs(arg - prev), sig
        prev = arg
    return best, where
if __name__ == "__main__":
    import sys
    for wtf, dd in [(0.05, 15), (0.1, 15), (0.2, 15), (0.2, 40), (0.6, 40)]:
        dl = np.deg2rad(dd); out = []
        for phi0 in np.deg2rad(np.arange(0, 181, 7.5)):
            j, w = maxjump(wtf, dl, phi0); out.append(f"{np.rad2deg(phi0):.0f}:{j:.2f}")
        print(f"wtf={wtf} delta={dd}:", " ".join(out), flush=True)
