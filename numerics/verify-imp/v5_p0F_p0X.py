"""verify-imp: independent check of the 1D face reduction behind P0-F and P0-X (math/possibility-rho0.md §2).
Units omega=1, a2=1. V(beta*) = E(beta*) + L_t(beta*) from the envelopes; find the tie sigma_c, check that the
two maximizer groups are separated by <p,I>. Also brute-force check of P[beta] <= max V over random Lipschitz paths.
Single process."""
import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad

def mk(dl, T, face):
    if face == 'F':   # p-hat delta below horizontal: early sin^+(2d - L), late sin^+(beta)
        ce = lambda L: np.maximum(np.sin(np.minimum(2 * dl - L, np.pi / 2)), 0) * (2 * dl - L > 0)
        cl = lambda b: np.maximum(np.sin(np.minimum(b, np.pi / 2)), 0) * (b > 0)
    else:             # P0-X: p-hat delta above horizontal: early sin^+(-L), late sin(2d + beta)
        ce = lambda L: np.maximum(np.sin(-L), 0) * (L < 0)
        cl = lambda b: np.sin(2 * dl + b)
    return ce, cl

def Vfun(bs, sig, T, ce, cl, n=4001):
    s = np.linspace(0, sig, n); tau = T - sig; t = np.linspace(0, tau, n)
    L = np.maximum(-s, bs - (sig - s))
    E = np.trapezoid((sig - s) * ce(L), s)
    Lt = np.trapezoid(t * cl(bs + t), t)
    pI_e = -np.trapezoid(ce(L), s); pI_l = np.trapezoid(cl(bs + t), t)
    return E + Lt, pI_e + pI_l

def tie(dl, T, face, lo, hi, split):
    ce, cl = mk(dl, T, face)
    def AmB(sig):
        bsg = np.linspace(-sig, sig, 801)
        V = np.array([Vfun(b, sig, T, ce, cl, 801)[0] for b in bsg])
        thr = split(sig)
        left = V[bsg <= thr].max(); right = V[bsg > thr].max()
        return left - right
    a, b = AmB(lo), AmB(hi)
    sc = brentq(AmB, lo, hi, xtol=1e-7)
    bsg = np.linspace(-sc, sc, 2001)
    VV = [Vfun(x, sc, T, ce, cl) for x in bsg]
    V = np.array([v[0] for v in VV]); pI = np.array([v[1] for v in VV])
    thr = split(sc)
    iL = np.argmax(np.where(bsg <= thr, V, -np.inf)); iR = np.argmax(np.where(bsg > thr, V, -np.inf))
    return sc, a, b, bsg[iL], bsg[iR], V[iL], V[iR], pI[iL], pI[iR]

print("=== P0-F (delta<pi/4, T<pi/2-2delta), sigma in [T/2,T], split at -tau ===")
for dd, T in [(0, 0.6), (5, 0.6), (15, 0.6), (15, 0.9), (30, 0.4), (40, 0.1)]:
    dl = np.radians(dd)
    assert T < np.pi / 2 - 2 * dl
    sc, a, b, bL, bR, VL, VR, pL, pR = tie(dl, T, 'F', T / 2, T * (1 - 1e-6), lambda sig: -(T - sig))
    print(f"d={dd} T={T}: (A-B)(T/2)={a:+.2e} (A-B)(T)={b:+.2e} sigma_c/T={sc/T:.4f} "
          f"betaL={bL:+.4f} betaR={bR:+.4f} V={VL:.6e}/{VR:.6e} <p,I> L={pL:.5f} R={pR:.5f} separated={pL < pR}")
h = np.linspace(1e-4, np.pi / 4, 2000)
f = np.sin(2 * h) - h * np.cos(2 * h) + np.sin(h) - 2 * h
print("min f(h)/h^3 on (0, pi/4] =", (f / h ** 3).min())

print("\n=== P0-X (0<delta<pi/4, T<min(2delta, pi/2-2delta)) ===")
for dd, T in [(15, 0.1), (15, 0.3), (15, 0.5), (30, 0.3)]:
    dl = np.radians(dd)
    assert T < min(2 * dl, np.pi / 2 - 2 * dl)
    def beta0(sig):
        tau = T - sig
        return sig - min(sig, tau ** 2 * np.cos(2 * dl + T) / (2 * sig))
    # x*: smallest x with sigma - sin sigma > (T-sigma)^2 sin sigma
    xs = np.linspace(0.01, 0.999, 2000)
    ok = [x for x in xs if x * T - np.sin(x * T) > (T - x * T) ** 2 * np.sin(x * T)]
    xstar = ok[0]
    sc, a, b, bL, bR, VL, VR, pL, pR = tie(dl, T, 'X', 0.02 * T, xstar * T, beta0)
    k0 = np.cos(dl + T)
    print(f"d={dd} T={T}: x*={xstar:.4f} sigma_c/T={sc/T:.4f} betaL={bL:+.4f} betaR={bR:+.4f} "
          f"<p,I> L={pL:.5f} R={pR:.5f} sep={pL < pR}  TW_proof={1/(k0*(1-xstar**2)):.3f}  TW_at_sigma_c={1/(k0*(1-(sc/T)**2)):.3f}")
