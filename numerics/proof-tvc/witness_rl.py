"""[proof-tvc] Rate-limited planar witness (gimbal angle mu is a state, |mu'| <= gdot, mu(0)=0; throttle free).
Planar meridian: psi'' = a sin(mu)/eps (sign convention), f = a cos(mu) - eps psi'^2,  W = int (s-s*) f cos(psi).
Baseline for the rate-limited class:  J0_rl = -int_0^{s*} (s*-s) a1 cos(delta(s)) ds + a2 (tf-s*)^2/2,
delta(s) = min(gdot s, delta)   (math/06 §5.3).  Gain G_rl = W - J0_rl, evaluated with fine RK4 (error ~1e-10)."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np, casadi as ca
from witness_nl import gtpl

def J0_rl(P, tf, ss, gd):
    s = np.linspace(0, ss, 200001); de = P['de']
    return -np.trapezoid((ss-s)*P['a1']*np.cos(np.minimum(gd*s, de)), s) + P['a2']*(tf-ss)**2/2

def evaluate_rl(P, tf, ss, aU, mdU, sub=400):
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    N = len(aU); h = tf/N; dt = h/sub
    x = np.zeros(3); W = 0.0; rz_ok = True
    f = lambda x, a, md: np.array([x[1], a*np.sin(x[2])/eps, md])
    integ = lambda t, x, a: (t-ss)*(a*np.cos(x[2]) - eps*x[1]**2)*np.cos(x[0])
    t = 0.0; maxtilt = 0.0; mumax = 0.0
    for k in range(N):
        a, md = aU[k], mdU[k]
        for j in range(sub):
            k1 = f(x, a, md); k2 = f(x+dt/2*k1, a, md); k3 = f(x+dt/2*k2, a, md); k4 = f(x+dt*k3, a, md)
            xm = x+dt/2*k1  # Simpson for the integrand
            xn = x+dt/6*(k1+2*k2+2*k3+k4)
            W += dt/6*(integ(t, x, a) + 4*integ(t+dt/2, (x+xn)/2, a) + integ(t+dt, xn, a))
            x = xn; t += dt; maxtilt = max(maxtilt, abs(x[0])); mumax = max(mumax, abs(x[2]))
    return W, x, maxtilt, mumax

def solve(P, tf, ss, gd, N=100, starts=6, seed=0):
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']; h = tf/N
    rng = np.random.default_rng(seed); best = None
    for st in range(starts):
        o = ca.Opti(); X = o.variable(3, N+1); U = o.variable(2, N)
        o.subject_to(X[:, 0] == 0); o.subject_to(X[0, N] == 0); o.subject_to(X[1, N] == 0)
        fd = lambda x, u: ca.vertcat(x[1], u[0]*ca.sin(x[2])/eps, u[1])
        W = 0
        for k in range(N):
            xk = X[:, k]; uk = U[:, k]
            k1 = fd(xk, uk); k2 = fd(xk+h/2*k1, uk); k3 = fd(xk+h/2*k2, uk); k4 = fd(xk+h*k3, uk)
            o.subject_to(X[:, k+1] == xk+h/6*(k1+2*k2+2*k3+k4))
            g = lambda t, x: (t-ss)*(uk[0]*ca.cos(x[2])-eps*x[1]**2)*ca.cos(x[0])
            W += h/6*(g(k*h, xk) + 4*g((k+.5)*h, (xk+X[:, k+1])/2) + g((k+1)*h, X[:, k+1]))
        o.subject_to(o.bounded(a1, U[0, :], a2)); o.subject_to(o.bounded(-gd, U[1, :], gd)); o.subject_to(o.bounded(-de, X[2, :], de))
        o.minimize(-W)
        tc = (np.arange(N)+.5)*h
        o.set_initial(U[0, :], np.where(tc < ss, a1, a2))
        sgn = 1 if st % 2 == 0 else -1
        # initial guess: ramp up during dive, reverse at s*, random afterwards
        md0 = np.where(tc < ss, gd, -gd*(rng.random(N) < 0.5)) * sgn if st > 0 else np.where(tc < ss, gd, 0)
        o.set_initial(U[1, :], md0)
        o.solver('ipopt', {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.sb': 'yes', 'ipopt.max_iter': 3000})
        try: sol = o.solve()
        except RuntimeError: continue
        v = float(sol.value(W))
        if best is None or v > best[0]: best = (v, np.array(sol.value(U[0, :])).ravel(), np.array(sol.value(U[1, :])).ravel())
    return best

if __name__ == "__main__":
    P = gtpl(); gd = np.deg2rad(float(sys.argv[1]))
    for x in sys.argv[2:]:
        tf, ss = [float(y) for y in x.split(":")]
        b = solve(P, tf, ss, gd, N=int(round(tf*40)))
        W, xe, mt, mm = evaluate_rl(P, tf, ss, b[1], b[2])
        J = J0_rl(P, tf, ss, gd)
        np.savez(f"witness_rl_{sys.argv[1]}_{tf}_{ss}.npz", a=b[1], md=b[2])
        print(f"gdot={sys.argv[1]}deg/s tf={tf} s*={ss}: G_rl={W-J:.4e} (opt {b[0]-J:.4e}) end state {xe} maxtilt={np.degrees(mt):.2f}deg max|mu|={np.degrees(mm):.2f}", flush=True)
