"""verify-imp: independent recomputation of Thm Q table, Thm Q_T table, Thm B* constants (math/02 §5, §10).
Single process, numpy/scipy only."""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

def a1f(rho1, m0, al):
    return lambda s: rho1 / (m0 - al * rho1 * s)

print("=== Thm Q table (rho1=400, m0=80, alpha=5.66e-4, delta=15deg) ===")
rho1, m0, al, dl = 400., 80., 5.66e-4, np.radians(15)
for w, tf in [(0.3, 5), (0.5, 5), (0.3, 8.5)]:
    a1 = a1f(rho1, m0, al)
    reg = dl + w * tf / 2 <= np.pi / 2
    G = quad(lambda s: a1(s) * np.cos(dl + w * abs(s - tf / 2)), 0, tf, points=[tf / 2])[0]
    Mz = quad(lambda s: a1(s) * np.cos(dl + w * s), 0, tf)[0]
    GF = 4 * a1(tf / 4) / w * np.sin(dl + w * tf / 2) * np.sin(w * tf / 4) ** 2
    print(f"w={w} tf={tf} regime={reg} G={G:.2f} Mz={Mz:.2f} gap={G-Mz:.2f} GammaF={GF:.2f}")

print("\n=== Thm Q_T gamma_T (rho1=400, m0=80) ===")
def gammaT(tf, w, dl, al, nb=121, nl=121, ns=4001):
    a1 = a1f(rho1, m0, al)
    s = np.linspace(0, tf, ns)
    A1 = a1(s)
    phi = w * np.minimum(s, tf - s)
    wt = np.full(ns, tf / (ns - 1)); wt[0] = wt[-1] = wt[0] / 2
    Mz = np.sum(wt * A1 * np.cos(dl + phi))
    best = np.inf
    for b in np.linspace(0, w * tf / 2, nb):
        q = -np.inf
        for lam in np.linspace(0, b, nl):
            A = np.minimum(phi + lam, w * np.abs(s - tf / 2) + b - lam)
            H = np.sum(wt * A1 * np.cos(dl + A))
            q = max(q, H - Mz * np.cos(lam))
        best = min(best, q)
    # analytic alpha=0 bound (i)
    a10 = rho1 / m0
    kap = 8 * a10 / w * np.sin(dl + w * tf / 4) * np.sin(w * tf / 8) ** 2
    lb = min(kap / 2, Mz * (1 - np.cos(kap / (2 * a10 * tf))))
    return best, Mz, lb
for tf, w, dd, al in [(6, 0.3, 15, 0), (6, 0.3, 15, 5.66e-4), (6, 0.3, 15, 0.03), (10, 0.3, 15, 5.66e-4)]:
    dl = np.radians(dd)
    g, Mz, lb = gammaT(tf, w, dl, al)
    print(f"tf={tf} w={w} d={dd} al={al}: regime(d+w tf/2<=pi/2)={dl + w*tf/2 <= np.pi/2} "
          f"gammaT={g:.3f} Mz={Mz:.2f}  (alpha=0 analytic lb={lb:.4f})  m0-al*rho1*tf={m0-al*rho1*tf:.1f} m0-al*1000*tf={m0-al*1000*tf:.1f}")

print("\n=== Thm B* constants (GTPL, math/02 Rem 10.2) ===")
def bstar(rho1=400, rho2=1000, m0=80, al=5.66e-4, g0=9.81, dl=np.radians(15), w=0.4, tf=7.0, gs=np.radians(30), s=None):
    amax = rho2 / (m0 - al * rho2 * tf); a10 = rho1 / m0; Ab = rho2 / m0 - g0
    if s is None:
        s = dl / w
    S1 = w * s <= dl + 1e-12
    S2 = g0 * s < Ab * (tf - s)
    S3 = np.tan(gs) * amax * s ** 2 <= Ab * (tf - s) ** 2
    th = a10 * np.sin(dl) / (4 * amax)
    gX = 5 / 32 * a10 * np.sin(dl) * s ** 2
    Wb = amax * (tf - s) ** 2 / 2
    c1 = 1 / (w * th * s)
    c1b = 4 * amax / (w * a10 * np.sin(dl) * s)
    f = lambda e: (1 + c1) * e + np.sqrt(2 * Wb * e) - gX
    eta0 = brentq(f, 0, gX)
    return dict(s=s, S1=S1, S2=S2, S3=S3, theta=th, gX=gX, c1=c1, c1_alt=c1b, Wb=Wb, eta0=eta0,
                dist=eta0 / np.sqrt(1 + s * s))
for tf in [5, 7, 12]:
    print(tf, {k: (round(v, 8) if isinstance(v, float) else v) for k, v in bstar(tf=tf).items()})
# what if c1 had been written without s* (dimensionally inconsistent)?
r = bstar(tf=7)
c1_wrong = 4 * (1000 / (80 - 5.66e-4 * 1000 * 7)) / (0.4 * 5 * np.sin(np.radians(15)))
print("c1 without s* would be", c1_wrong, " vs correct", r['c1'])
