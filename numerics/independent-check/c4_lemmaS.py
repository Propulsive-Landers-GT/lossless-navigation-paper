"""Lean-checked instance of Lemma S (Slice.lemmaS: a=12, delta=0, omega=0.1 rad/s,
tf~3.50 s). Claim: every soft landing from the straight-down data zeta_w touches
down at least 1 m off the point directly below. Search for the smallest offset.
Solver: bounded Gauss-Newton (scipy least_squares) on [offset, w * constraint
violations] with the weight w raised in stages, so the four landing equalities
end up satisfied to ~1e-8."""
import time
import numpy as np
from scipy.optimize import least_squares
from m1 import M1

rng = np.random.default_rng(5)
a, g0, omega = 12.0, 9.81, 0.1
hold = (1 - np.cos(0.1))/(0.1*np.sin(0.1))
tf = 3.0 + hold


def build(n1, n2, n3):
    edges = np.r_[np.linspace(0, 1, n1 + 1), np.linspace(1, 3, n2 + 1)[1:], np.linspace(3, tf, n3 + 1)[1:]]
    m = M1(edges, omega, 0.0, a, a, g0)
    rate = np.r_[omega*np.ones(n1), -omega*np.ones(n2), np.zeros(n3)]
    return m, m.planar(rate, 0.0, a)


for (n1, n2, n3), nstarts in (((6, 12, 3), 14),):
    t0 = time.time()
    m, Xw = build(n1, n2, n3)
    N = m.N
    thw = m.theta(Xw)[0]
    v0z, r0z = thw[5], thw[2]
    free = np.r_[np.arange(N), N + np.arange(N)]
    lb = np.r_[-omega*np.ones(N), -np.inf*np.ones(N)]
    ub = np.r_[omega*np.ones(N), np.inf*np.ones(N)]

    def parts(Z):
        Z = np.atleast_2d(Z)
        X = np.tile(Xw, (Z.shape[0], 1))
        X[:, free] = Z
        th = m.theta(X)
        return th[:, :2], np.c_[th[:, 3], th[:, 4], th[:, 5] - v0z, th[:, 2] - r0z]

    def solve(z0):
        z = np.clip(z0, lb, ub)
        for w in (1e1, 1e2, 1e3, 1e4, 1e5):
            def res(zz):
                p, c = parts(zz)
                return np.r_[p[0], w*c[0]]

            def jac(zz):
                n = len(zz); eps = 1e-6
                Zp = np.tile(zz, (2*n, 1))
                Zp[np.arange(n), np.arange(n)] += eps
                Zp[n + np.arange(n), np.arange(n)] -= eps
                p, c = parts(Zp)
                R = np.c_[p, w*c]
                return ((R[:n] - R[n:])/(2*eps)).T
            z = least_squares(res, z, jac=jac, bounds=(lb, ub), method="trf",
                              xtol=1e-14, ftol=1e-14, gtol=1e-12, max_nfev=300).x
        p, c = parts(z)
        return float(np.hypot(*p[0])), float(np.abs(c[0]).max()), z

    zw = Xw[free]
    out = []
    for k in range(nstarts):
        if k == 0:
            z0, kind = zw.copy(), "witness"
        elif k % 3 == 1:
            z0, kind = zw + np.r_[rng.normal(0, 0.03, N), rng.normal(0, 0.8, N)], "witness+noise"
        elif k % 3 == 2:
            z0, kind = np.r_[rng.uniform(-omega, omega, N), rng.uniform(0, 6.28, N)], "random"
        else:
            z0, kind = np.r_[omega*np.ones(N), rng.uniform(0, 6.28) + np.cumsum(rng.uniform(-1.2, 1.2)*np.ones(N))], "coning"
        off, viol, z = solve(z0)
        out.append((off, viol, kind))
        print(f"  cells={N} start {k:2d} ({kind:13s}): offset {off:.4f} m, landing-constraint violation {viol:.1e}", flush=True)
    ok = [o for o in out if o[1] < 1e-6]
    if not ok:
        print(f"cells={N}: no start reached a valid landing"); continue
    best = min(ok)
    print(f"cells={N}: witness offset {np.hypot(thw[0], thw[1]):.4f} m; smallest offset over {len(ok)} valid landings: "
          f"{best[0]:.4f} m (from a '{best[2]}' start); Lean bound >= 1 m, paper's r_S ~ 1.38 m -> "
          f"{'consistent' if best[0] >= 1.0 else '*** BELOW 1 m ***'}   [{time.time()-t0:.0f} s]", flush=True)
