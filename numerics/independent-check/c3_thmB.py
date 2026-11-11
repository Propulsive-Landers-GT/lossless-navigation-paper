"""Theorem B and the ball bound (no state constraints): the midpoint M of the two
mirror-image extreme arcs is claimed to be at least Gamma_F away from the
reachable velocity-increment set R. Sec. 5.1 reports dist(M, R) = 2.18-2.23 m/s
for tf=2 s, omega=30 deg/s, delta=15 deg. Search for the admissible control
whose velocity increment gets closest to M (constant mass, a in [5, 12.5])."""
import numpy as np
from scipy.optimize import minimize
from m1 import M1

rng = np.random.default_rng(1)
d2r = np.pi/180
delta, omega, tf, a1, a2 = 15*d2r, 30*d2r, 2.0, 5.0, 12.5

Mz = a1/omega*(np.sin(delta + omega*tf) - np.sin(delta))
Px = a1/omega*(np.cos(delta) - np.cos(delta + omega*tf))
GammaF = 4*a1/omega*np.sin(delta + omega*tf/2)*np.sin(omega*tf/4)**2
print(f"extreme arcs: P = (+-{Px:.4f}, {Mz:.4f}) m/s ; midpoint M = (0, {Mz:.4f})")
print(f"paper's proved lower bound Gamma_F = {GammaF:.4f} m/s ; paper's numerical distance 2.18-2.23 m/s")

for N in (16, 32):
    m = M1(np.linspace(0, tf, N + 1), omega, delta, a1, a2)
    # check the extreme arc reproduces P
    Xe = m.planar(omega, delta, a1)
    I, _ = m.moments(Xe)
    target = np.array([0.0, 0.0, Mz])

    def fg(x):
        n = len(x); eps = 1e-6
        Xp = np.tile(x, (2*n + 1, 1))
        Xp[np.arange(n), np.arange(n)] += eps
        Xp[n + np.arange(n), np.arange(n)] -= eps
        f = np.sum((m.moments(Xp)[0] - target)**2, axis=1)
        return f[-1], (f[:n] - f[n:2*n])/(2*eps)

    bnds = m.bounds()
    vals = []
    for k in range(30):
        if k % 3 == 0:
            x0 = Xe + rng.normal(0, 0.2, Xe.shape)
        elif k % 3 == 1:
            x0 = np.r_[rng.uniform(-omega, omega, N), rng.uniform(0, 6.28, N), rng.uniform(0, delta, N),
                       rng.uniform(0, 6.28, N), rng.uniform(a1, a2, N)]
        else:  # spiral / coning seed
            x0 = np.r_[omega*np.ones(N), np.cumsum(rng.uniform(-0.6, 0.6)*np.ones(N)), delta*np.ones(N),
                       rng.uniform(0, 6.28)*np.ones(N), a1*np.ones(N)]
        lo = np.array([b[0] for b in bnds]); hi = np.array([b[1] for b in bnds])
        x0 = np.clip(x0, np.where(np.isfinite(lo), lo, -1e9), np.where(np.isfinite(hi), hi, 1e9))
        res = minimize(fg, x0, jac=True, method="L-BFGS-B", bounds=bnds,
                       options=dict(maxiter=3000, ftol=1e-15, gtol=1e-10, maxcor=30))
        vals.append(np.sqrt(res.fun))
    vals = np.array(vals)
    print(f"N={N}: extreme arc gives I=({I[0,0]:.4f},{I[0,2]:.4f}); closest approach to M over 30 starts: "
          f"best {vals.min():.4f}, median {np.median(vals):.4f}  -> "
          f"{'consistent with bound' if vals.min() >= GammaF else '*** BELOW THE PROVED BOUND ***'}")
