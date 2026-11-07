"""verify-imp: independent recomputation of the certified table of Theorem S (math/07 §2-4).
Re-derives B, C_m, the S-turn witness (t1 by root finding), gain_w, p_w, M, r_S, and the certified Omega ranges.
Single process."""
import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq

g0 = 9.81
def case(dd, T, w, al=0.0, m0=100., rho1=1200., rho2=2500., verbose=True):
    dl = np.radians(dd); Om = w * T; tb = dl + Om
    a10 = rho1 / m0
    a1 = lambda s: rho1 / (m0 - al * rho1 * s)
    a2 = rho2 / (m0 - al * rho2 * T)
    em = a1(T) / a10 - 1
    tau = lambda s: dl + w * s
    c0 = 1 / (1 + np.cos(dl))
    de = 2 * np.sin(dl / 2) + em * np.sin(tb)
    E4 = a10 * (1 + em) ** 2 * quad(lambda s: (1 / (1 + np.cos(tau(s))) - c0) * np.sin(tau(s)) ** 2, 0, T)[0]
    B = a10 * c0 * T * (Om / (2 * np.pi) + de) ** 2 + E4
    Ap = c0 / a10
    k0 = np.inf if rho1 == rho2 else np.cos(tb) / ((a2 - a10) * np.sin(tb) ** 2)
    Cm = Ap if rho1 == rho2 else Ap * k0 / (k0 - Ap)
    # witness
    def chi(s, t1):
        ph = w * s if s <= t1 else w * (2 * t1 - s)
        return ph + dl * np.sign(ph)
    def Ih(t1):
        return quad(lambda s: a1(s) * np.sin(chi(s, t1)), 0, T, points=[t1, 2 * t1], limit=200)[0]
    t1 = brentq(Ih, 1e-9, T / 2 + 1e-9, xtol=1e-14)
    gain = quad(lambda s: a1(s) * (1 - np.cos(chi(s, t1))), 0, T, points=[t1, 2 * t1], limit=200)[0]
    pw = -quad(lambda s: s * a1(s) * np.sin(chi(s, t1)), 0, T, points=[t1, 2 * t1], limit=200)[0]
    chimax = max(w * t1 + dl, abs(w * (2 * t1 - T)) + dl)
    S0 = tb < np.pi / 2
    S1 = a10 * np.cos(chimax) > g0
    S2 = k0 > Ap
    M = gain - B
    rS = np.sqrt(M * T ** 3 / (12 * Cm)) if (M > 0 and S0 and S1 and S2) else np.nan
    if verbose:
        print(f"d={dd:>4} T={T} w={w} al={al}: t1/T={t1/T:.5f} gain_w={gain:.5f} B={B:.5f} (E4={E4:.5f}) "
              f"M={M:.3e} Cm={Cm:.5f} r_S={rS:.3f} |p_w|={abs(pw):.3f} S0={S0} S1={S1} S2={S2}")
    return M, S0 and S1 and S2

print("--- table rows (demo vehicle m0=100, rho=1200/2500) ---")
for args in [(0, 2, 0.20), (0, 4, 0.10), (5, 2, 0.15), (10, 2, 0.10), (10, 4, 0.05), (5, 2, 0.15, 5.66e-4)]:
    case(*args)
print("--- fixed thrust rho1=rho2=1200, delta=0 ---")
case(0, 2, 0.2, rho2=1200.); case(0, 4, 0.1, rho2=1200.)
print("--- certified Omega ranges at T=2 ---")
for dd in [0, 5, 10, 15, 20]:
    ok = []
    for Om in np.arange(0.01, 1.2, 0.01):
        M, reg = case(dd, 2, Om / 2, verbose=False)
        if M > 0 and reg:
            ok.append(Om)
    # report maximal contiguous range from small Omega
    mx = 0
    for Om in np.arange(0.01, 1.2, 0.01):
        if any(abs(Om - o) < 1e-9 for o in ok):
            mx = Om
        else:
            break
    print(f"delta={dd}: certified Omega in (0, {mx:.2f}]  (any certified: {len(ok)} grid points)")
