"""A7: independent check of math/07 Theorem S table row (delta=0, T=2, omega=0.2, a1=12, alpha=0) and witness constant."""
import numpy as np
from scipy.optimize import brentq
a1, T, om, g0 = 12.0, 2.0, 0.2, 9.81
s = np.linspace(0, T, 400001)
def chi(t1): return np.where(s <= t1, om*s, om*(2*t1 - s))      # delta = 0
t1 = brentq(lambda t: np.trapezoid(np.sin(chi(t)), s), 1e-6, T - 1e-6)
c = chi(t1)
gain = np.trapezoid(a1*(1 - np.cos(c)), s)
p = -np.trapezoid(s*a1*np.sin(c), s)
Om = om*T
c0 = 0.5; tau = om*s
E4 = a1*np.trapezoid((1/(1+np.cos(tau)) - c0)*np.sin(tau)**2, s)
B = a1*c0*T*(Om/(2*np.pi))**2 + E4
M = gain - B; Cm = c0/a1
rS = np.sqrt(M*T**3/(12*Cm))
print(f"t1/T={t1/T:.5f} (claim 1-1/sqrt2={1-1/np.sqrt(2):.5f})  gain_w={gain:.5f} (claim 0.07758)  B={B:.5f} (claim 0.06370)  "
      f"M={M:.3e}  r_S={rS:.3f} (claim 0.45)  |p_w|={abs(p):.3f} (claim 0.94)")
print("small-angle mean-square const:", np.trapezoid(c**2, s)/(T*Om**2), "claim", (3*np.sqrt(2)-4)/6, " vs 1/(4pi^2)=", 1/(4*np.pi**2))
print("S1 check a1 cos(chi_max) > g0:", a1*np.cos(np.abs(c).max()) > g0)
