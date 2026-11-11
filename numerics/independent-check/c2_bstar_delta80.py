"""Theorem B* as printed assumes (S1) w s* <= delta, (S2), (S3) with
0 < delta < 90 deg. Its proof (Step 4 'T* = rho1 then rho2', Step 5 'on the dive
v_z' >= -g0') also needs delta + w s* <= 90 deg, which (S1) only gives for
delta <= 45 deg. The Lean statement has that hypothesis; the printed one did not.
This is a case with delta = 80 deg where the printed S1-S3 all hold."""
import numpy as np
from scipy.integrate import solve_ivp

g0 = 9.81
delta, omega = np.radians(80), 1.0
sstar = delta/omega
amin, amax = 1.0, 30.0
D = 0.68
tf = sstar + D
Ab = amax - g0
print("S1:", omega*sstar <= delta + 1e-15, " S2:", g0*sstar < Ab*D, f"({g0*sstar:.3f} < {Ab*D:.3f})",
      " S3 (altitude only, gamma=0): True", f"  delta + w s* = {np.degrees(delta+omega*sstar):.0f} deg")
sc = (np.pi/2 - delta)/omega   # thrust passes below the horizon here


def face_value(a_dive):
    s = np.linspace(0, sstar, 400001)
    return -np.trapezoid((sstar - s)*a_dive(s)*np.cos(delta + omega*s), s) + amax*D**2/2


thr_opt = lambda s: np.where(delta + omega*s > np.pi/2, amax, amin)   # true maximiser of the face functional
thr_paper = lambda s: amin*np.ones_like(s)                           # 'rho1 then rho2' as written in Step 4
print(f"face value with paper's 'rho1 then rho2' throttle: {face_value(thr_paper):.4f}")
print(f"face value with the actual maximising throttle  : {face_value(thr_opt):.4f}   <- V*; the written witness does not attain it")

for label, thr in (("actual face maximiser", thr_opt), ("paper's rho1-then-rho2", thr_paper)):
    def rhs(t, y):
        if t < sstar:
            a, psi = float(thr(np.array(t))), delta + omega*t
        else:
            a, psi = amax, 0.0
        return [y[2], y[3], a*np.sin(psi), a*np.cos(psi) - g0]
    # integrate backward from touchdown (x, z, vx, vz) = 0
    y = np.zeros(4); T, Y = [], []
    for (t0, t1) in ((tf, sstar), (sstar, sc), (sc, 0.0)):
        sol = solve_ivp(rhs, (t0, t1), y, rtol=1e-11, atol=1e-12, max_step=abs(t1 - t0)/300)
        y = sol.y[:, -1]; T += list(sol.t); Y += list(sol.y.T)
    Y = np.array(Y); T = np.array(T)
    i = np.argmin(Y[:, 1])
    print(f"{label}: min altitude {Y[i,1]:+.3f} m at t={T[i]:.3f} s ; start state z0={y[1]:+.3f} m, vz0={y[3]:+.3f} m/s")
