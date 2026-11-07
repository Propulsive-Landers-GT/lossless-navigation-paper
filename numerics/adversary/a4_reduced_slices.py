"""A4: symmetry-reduction loophole. F is invariant under rotations about e_z. A relaxation posed in a frame
rotated so that v0_lat points along +x only needs F ∩ H convex, H={v0y=0, v0x>=0}. Thm B's witness pair
(P_u, P_-u) is not inside H. Tests (M1, alpha=0, relaxed gimbal d in conv(cap), b0=e_z, tf small):
 (a) velocity cross-section: z_min(rho) = min int a d_z  s.t. int a d_lat = (rho,0). Is z_min convex on [0,c]?
 (b) slice G = F ∩ {v0_lat=0}: min int a d_z with v0_lat=0, with vs without r0_lat=0.
     G rotation-invariant; strict gap => G nonconvex => F∩H nonconvex (G = (F∩H)∩{v0x=0})."""
import numpy as np, sys
from scipy.optimize import minimize
m0, rho1, rho2, g = 80.0, 400.0, 1000.0, 9.81
delta, om = np.deg2rad(15), 0.4
tf, N = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0, 30
h = tf/N; s = np.arange(N)*h + h/2
a1, a2 = rho1/m0, rho2/m0
def unpack(x): return x[:N], x[N:N+3*(N+1)].reshape(N+1, 3), x[N+3*(N+1):].reshape(N, 3)
def nrm(V): return V/np.linalg.norm(V, axis=1, keepdims=True)
def mom(x):
    a, B, V = unpack(x); u = a[:, None]*V
    return u.sum(0)*h, ((tf - s)[:, None]*u).sum(0)*h      # Delta v, int (tf-s) u
def ineq(x):
    a, B, V = unpack(x); b = nrm(B)
    # outer approx of continuous-time constraint: cone widened by om*h/2
    return np.concatenate([np.sum(b[:-1]*b[1:], 1) - np.cos(om*h), 1 - np.sum(V*V, 1),
                           np.sum(b[:-1]*V, 1) - np.cos(delta + om*h/2), np.linalg.norm(B, axis=1) - 0.5])
def solve(eqf, seeds=10, throttle=True):
    best = (np.inf, None)
    for sd in range(seeds):
        rng = np.random.default_rng(sd); u = rng.normal(size=2); u /= np.linalg.norm(u)
        ph = om*np.arange(N+1)*h*rng.uniform(0, 1)
        B = np.stack([np.sin(ph)*u[0], np.sin(ph)*u[1], np.cos(ph)], 1) + 0.02*rng.normal(size=(N+1, 3)); B[0] = [0, 0, 1]
        V = 0.9*nrm(B[:-1] + 0.1*rng.normal(size=(N, 3)))
        x0 = np.concatenate([np.full(N, a1), B.ravel(), V.ravel()])
        bnds = [(a1, a2 if throttle else a1)]*N + [(-2, 2)]*(3*(N+1)) + [(-1, 1)]*(3*N)
        cons = [{'type': 'ineq', 'fun': ineq}, {'type': 'eq', 'fun': lambda x: np.concatenate([nrm(unpack(x)[1][:1])[0, :2], eqf(x)])}]
        r = minimize(lambda x: mom(x)[0][2], x0, method='SLSQP', bounds=bnds, constraints=cons, options={'maxiter': 500, 'ftol': 1e-11})
        ok = ineq(r.x).min() > -1e-7 and np.abs(cons[1]['fun'](r.x)).max() < 1e-7
        if ok and r.fun < best[0]: best = (r.fun, r.x)
    return best
if __name__ == '__main__':
    zstar, xs = solve(lambda x: np.zeros(0))
    c = np.linalg.norm(mom(xs)[0][:2]); print(f"tf={tf}: global min dv_z = {zstar:.5f} at |dv_lat|={c:.4f} (Thm B face)")
    rhos = np.linspace(0, c, 7); zs = []
    for rho in rhos:
        z, _ = solve(lambda x, rho=rho: mom(x)[0][:2] - np.array([rho, 0])); zs.append(z)
        print(f"  (a) rho={rho:.4f}  z_min={z:.5f}")
    zs = np.array(zs); sec = zs[:-2] - 2*zs[1:-1] + zs[2:]
    print(f"  (a) second differences of z_min(rho): {np.round(sec, 5)}  (all >=0 => convex cross-section lower boundary)")
    z1, x1 = solve(lambda x: mom(x)[0][:2])
    z2, _ = solve(lambda x: np.concatenate([mom(x)[0][:2], mom(x)[1][:2]]))
    print(f"  (b) min dv_z with v0_lat=0: {z1:.5f} (r0_lat-moment there = {np.round(mom(x1)[1][:2],4)}); "
          f"with v0_lat=r0_lat=0: {z2:.5f}; gap={z2 - z1:.5f}")
