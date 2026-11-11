"""Attack on the headline result (Theorem B*, the 'dive-then-brake' face).

1. Build the two mirror-image witness manoeuvres and confirm, by integrating the
   real equations of motion, that each lands at rest at the origin without
   violating altitude / glide slope / gimbal / turn-rate limits.
2. Take the midpoint of their initial conditions (theta_m) and search as hard as
   we can for ANY admissible control that lands from it. The theorem says none
   exists. Finding one would disprove the paper.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from m1 import M1

rng = np.random.default_rng(0)


def run(name, delta, omega, sstar, amin, amax, tf, gamma, Nd, Nb, nstarts=40, g0=9.81):
    print(f"\n=== {name}: delta={np.degrees(delta):.1f} deg, omega={omega}, s*={sstar:.4f}, "
          f"a in [{amin},{amax}], tf={tf}, glide={np.degrees(gamma):.0f} deg, cells={Nd}+{Nb}")
    Ab, D = amax - g0, tf - sstar
    print("  hypotheses: S1 w s*<=delta:", omega*sstar <= delta + 1e-12,
          "| delta+w s*<=90deg:", delta + omega*sstar <= np.pi/2 + 1e-12,
          "| S2:", g0*sstar < Ab*D, "| S3:", np.tan(gamma)*amax*sstar**2 <= Ab*D**2)
    edges = np.r_[np.linspace(0, sstar, Nd + 1), np.linspace(sstar, tf, Nb + 1)[1:]]
    m = M1(edges, omega, delta, amin, amax, g0)
    dive = np.arange(m.N) < Nd
    Xw = m.planar(np.where(dive, omega, 0.0), np.where(dive, delta, -omega*sstar),
                  np.where(dive, amin, amax))
    th_w = m.theta(Xw)[0]
    th_mirror = th_w*np.array([-1, -1, 1, -1, -1, 1])
    th_m = 0.5*(th_w + th_mirror)
    print("  witness  theta* = r0", np.round(th_w[:3], 4), "v0", np.round(th_w[3:], 4))
    print("  midpoint theta_m = r0", np.round(th_m[:3], 4), "v0", np.round(th_m[3:], 4))

    # --- 1. independent forward simulation of the witness -------------------
    def ctrl(t):
        if t < sstar:
            phi, psi, a = omega*t, delta + omega*t, amin
        else:
            phi, psi, a = omega*sstar, 0.0, amax
        return phi, psi, a

    def rhs(t, y):
        _, psi, a = ctrl(t)
        return [y[3], y[4], y[5], a*np.sin(psi), 0.0, a*np.cos(psi) - g0]

    y = th_w.copy()
    ts, ys = [0.0], [y.copy()]
    for (t0, t1) in [(0, sstar), (sstar, tf)]:
        sol = solve_ivp(rhs, (t0, t1), y, rtol=1e-12, atol=1e-13, max_step=(t1 - t0)/400,
                        dense_output=False)
        y = sol.y[:, -1]
        ts += list(sol.t[1:]); ys += list(sol.y.T[1:])
    ys = np.array(ys)
    rz, rh = ys[:, 2], np.hypot(ys[:, 0], ys[:, 1])
    print(f"  ODE landing miss of witness: |r(tf)|={np.linalg.norm(y[:3]):.2e}, |v(tf)|={np.linalg.norm(y[3:]):.2e}")
    print(f"  min altitude along path: {rz.min():.3e}   min (r_z - tan(gamma)|r_h|): {(rz - np.tan(gamma)*rh).min():.3e}")
    print(f"  max gimbal angle used: {np.degrees(max(delta, omega*sstar)):.2f} deg (limit {np.degrees(delta):.2f})")

    # --- face value check ----------------------------------------------------
    sq = np.linspace(0, sstar, 200001)
    Vstar = -amin*np.trapezoid((sstar - sq)*np.cos(delta + omega*sq), sq) + amax*D**2/2
    kappa = g0*tf*(sstar - tf/2)
    ell = lambda th: th[2] + sstar*th[5]
    print(f"  l(theta*) = {ell(th_w):.8f}   V*+kappa = {Vstar + kappa:.8f}   (paper: these are equal, and it is the max over F)")

    # --- 2. the attack -------------------------------------------------------
    def make_obj(target):
        def batch(X):
            return np.sum((m.theta(X) - target)**2, axis=1)

        def fg(x):
            n = len(x)
            eps = 1e-6
            Xp = np.tile(x, (2*n + 1, 1))
            Xp[np.arange(n), np.arange(n)] += eps
            Xp[n + np.arange(n), np.arange(n)] -= eps
            f = batch(Xp)
            return f[-1], (f[:n] - f[n:2*n])/(2*eps)
        return fg

    bnds = m.bounds()
    lo = np.array([b[0] for b in bnds]); hi = np.array([b[1] for b in bnds])

    def clip(x):
        return np.minimum(np.maximum(x, np.where(np.isfinite(lo), lo, -1e9)), np.where(np.isfinite(hi), hi, 1e9))

    def rand_start(kind):
        N = m.N
        if kind == 0:      # witness + noise
            x = Xw + rng.normal(0, 0.15, Xw.shape)*np.r_[omega*np.ones(N), np.ones(N), delta*np.ones(N), np.ones(N), (amax - amin)*np.ones(N)]
        elif kind == 1:    # fully random
            x = np.r_[rng.uniform(-omega, omega, N), rng.uniform(0, 2*np.pi, N), rng.uniform(0, delta, N),
                      rng.uniform(0, 2*np.pi, N), rng.uniform(amin, amax, N)]
        elif kind == 2:    # coning: constant rate, heading drifting -> spiral
            x = np.r_[omega*rng.uniform(0.3, 1)*np.ones(N), np.cumsum(rng.uniform(-0.5, 0.5)*np.ones(N)),
                      delta*rng.uniform(0, 1, N), rng.uniform(0, 2*np.pi)*np.ones(N),
                      np.where(dive, amin, amax)]
        elif kind == 3:    # upright body, gimbal chatter (what a 3-DOF solver would ask for)
            x = np.r_[np.zeros(N), np.zeros(N), delta*np.ones(N), np.pi*(np.arange(N) % 2),
                      np.where(dive, amin, amax)]
        else:              # S-turn: out and back
            x = m.planar(np.where(np.arange(N) < N//3, omega, np.where(np.arange(N) < 2*N//3, -omega, 0.0)),
                         rng.uniform(-delta, delta, N), np.where(dive, amin, amax))
        return clip(x)

    def attack(target, label, starts):
        fg = make_obj(target)
        best = (np.inf, None)
        vals = []
        for x0 in starts:
            res = minimize(fg, x0, jac=True, method="L-BFGS-B", bounds=bnds,
                           options=dict(maxiter=4000, maxfun=8000, ftol=1e-16, gtol=1e-11, maxcor=30))
            vals.append(np.sqrt(res.fun))
            if res.fun < best[0]:
                best = (res.fun, res.x)
        vals = np.array(vals)
        print(f"  [{label}] closest approach over {len(starts)} starts: best {vals.min():.3e}, median {np.median(vals):.3e}, worst {vals.max():.3e}")
        return np.sqrt(best[0]), best[1]

    starts = [Xw, m.planar(np.where(dive, -omega, 0.0), np.where(dive, -delta, omega*sstar), np.where(dive, amin, amax))]
    starts += [rand_start(k % 5) for k in range(nstarts)]

    # sanity: the solver must be able to find landings that DO exist
    d_w, _ = attack(th_w, "sanity: land from witness data theta*   ", [rand_start(k % 5) for k in range(8)])
    Xr = rand_start(1)
    d_r, _ = attack(m.theta(Xr)[0], "sanity: land from a random feasible datum", [rand_start(k % 5) for k in range(8)])
    d_m, xb = attack(th_m, "ATTACK: land from midpoint theta_m       ", starts)

    # paper's proved lower bound on dist(theta_m, F) (valid for delta <= 45 deg)
    if delta <= np.pi/4 + 1e-12:
        gX = (5/32)*amin*np.sin(delta)*sstar**2
        c1 = 4*amax/(omega*amin*np.sin(delta)*sstar)
        Wb = 0.5*amax*D**2
        A_, B_, C_ = 1 + c1, np.sqrt(2*Wb), -gX
        xr = (-B_ + np.sqrt(B_**2 - 4*A_*C_))/(2*A_)
        bound = xr**2/np.sqrt(1 + sstar**2)
        print(f"  paper's proved lower bound on dist(theta_m, F): {bound:.3e}   -> search found {d_m:.3e}  "
              f"({'CONSISTENT' if d_m >= bound else '*** VIOLATES THE BOUND ***'})")
    thb = m.theta(xb)[0]
    print(f"  best competitor: l deficit V*+kappa-l = {Vstar + kappa - ell(thb):.3e}, its data offset from theta_m = {np.round(thb - th_m, 5)}")
    return d_m


if __name__ == "__main__":
    d2r = np.pi/180
    run("A big-gap demo", 40*d2r, 1.0, 0.5, 6.0, 20.0, 1.5, 30*d2r, Nd=10, Nb=14)
    run("A refined grid", 40*d2r, 1.0, 0.5, 6.0, 20.0, 1.5, 30*d2r, Nd=20, Nb=28, nstarts=20)
    run("B vehicle-like (const mass)", 15*d2r, 0.4, 15*d2r/0.4, 5.0, 12.5, 4.0, 30*d2r, Nd=10, Nb=20, nstarts=30)
