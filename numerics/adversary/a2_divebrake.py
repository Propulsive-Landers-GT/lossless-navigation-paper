"""A2: 'dive-then-brake' face test for 5DOF model M1 with EXACT mass depletion, min throttle,
altitude constraint r_z>=0 (+ optional glide slope), long tf.
Maximize the rotation-invariant linear functional  l(r0,v0) = int (s - s*) a d_z ds  (+const)
 (i) with lateral boundary data free, (ii) with lateral boundary data forced to 0.
If max(ii) < max(i) strictly, the axial projection of the (i)-optimizer is infeasible while it is the
midpoint of the (i)-optimizer and its 180deg rotation  =>  F_tf (with altitude constraint) is nonconvex.
Discretization: N ZOH intervals, b at nodes with b_k.b_{k+1} >= cos(omega h), d_k in cone(b_k,delta)."""
import numpy as np, sys
from scipy.optimize import minimize
m0, rho1, rho2, alpha, g = 80.0, 400.0, 1000.0, 5.66e-4, 9.81
delta, om = np.deg2rad(15), 0.4
tf, sstar, N = float(sys.argv[1]) if len(sys.argv)>1 else 8.0, float(sys.argv[2]) if len(sys.argv)>2 else 1.0, 30
gs = np.deg2rad(float(sys.argv[3])) if len(sys.argv)>3 else 0.0   # glide-slope angle (0 => altitude only)
h = tf/N; s = np.arange(N)*h; smid = s + h/2
w = smid - sstar
gv = np.array([0, 0, -g])
J = np.arange(N+1)[:, None]; K = np.arange(N)[None, :]
Wm = np.where(K < J, h*h*(J - K - 0.5), 0.0)
def unpack(x):
    T = x[:N]; B = x[N:N+3*(N+1)].reshape(N+1, 3); D = x[N+3*(N+1):].reshape(N, 3)
    return T, B, D
def nrm(V): return V/np.linalg.norm(V, axis=1, keepdims=True)
def traj(x):
    T, B, D = unpack(x); d = nrm(D)
    m = m0 - alpha*h*np.concatenate([[0], np.cumsum(T)[:-1]]); a = T/m
    f = a[:, None]*d + gv
    v0 = -f.sum(0)*h
    r0 = -v0*tf - (h*h*(N - np.arange(N) - 0.5))[:, None].__mul__(f).sum(0)
    v = v0 + np.vstack([np.zeros(3), np.cumsum(f, 0)*h])
    r = r0 + np.outer(np.arange(N+1)*h, v0) + (Wm @ f)
    return a, d, r, v
def obj(x):
    a, d, r, v = traj(x); return -np.sum(w*a*d[:, 2])*h
def cons(x, lat0):
    T, B, D = unpack(x); b = nrm(B); d = nrm(D)
    c = [np.sum(b[:-1]*b[1:], 1) - np.cos(om*h),          # rate limit
         np.sum(b[:-1]*d, 1) - np.cos(delta)]             # gimbal cone (node b_k)
    a, d, r, v = traj(x)
    c.append(r[:-1, 2] - np.tan(gs)*np.linalg.norm(r[:-1, :2], axis=1))  # altitude / glide slope
    c.append(np.linalg.norm(B, axis=1) - 0.5)            # keep away from 0
    return np.concatenate(c)
def eqs(x, lat0):
    T, B, D = unpack(x); b0 = B[0]/np.linalg.norm(B[0])
    e = [b0[:2]]
    if lat0 >= 1:
        a, d, r, v = traj(x); e += [v[0, :2]]
        if lat0 == 2: e += [r[0, :2]]
    return np.concatenate(e)
bounds = [(rho1, rho2)]*N + [(-2, 2)]*(3*(N+1)) + [(-2, 2)]*(3*N)
def run(lat0, seed):
    rng = np.random.default_rng(seed)
    u = rng.normal(size=2); u /= np.linalg.norm(u); amp = rng.uniform(0, 0.4)
    phi = np.clip(np.minimum(om*s, om*max(sstar, 0.1)) * amp * 2.5, 0, 0.6)
    phin = np.concatenate([phi, [phi[-1]]])
    B = np.stack([np.sin(phin)*u[0], np.sin(phin)*u[1], np.cos(phin)], 1) + 0.01*rng.normal(size=(N+1, 3))
    B[0] = [0, 0, 1]
    D = B[:-1] + 0.05*rng.normal(size=(N, 3))
    T = rng.uniform(rho1, rho2, N)
    x0 = np.concatenate([T, B.ravel(), D.ravel()])
    res = minimize(obj, x0, method='SLSQP', bounds=bounds,
                   constraints=[{'type': 'ineq', 'fun': cons, 'args': (lat0,)},
                                {'type': 'eq', 'fun': eqs, 'args': (lat0,)}],
                   options={'maxiter': 600, 'ftol': 1e-10})
    feas = cons(res.x, lat0).min() > -1e-6 and np.abs(eqs(res.x, lat0)).max() < 1e-6
    return -res.fun, feas, res.x
if __name__ == '__main__':
    out = {}
    modes = [int(sys.argv[4])] if len(sys.argv) > 4 else [0, 1, 2]
    for lat0 in modes:
        best = (-np.inf, None)
        for seed in range(8):
            val, feas, x = run(lat0, seed)
            if feas and val > best[0]: best = (val, x)
        out[lat0] = best
        a, d, r, v = traj(best[1]); T, B, D = unpack(best[1]); b = nrm(B)
        tilt = np.degrees(np.arccos(np.clip(b[:, 2], -1, 1)))
        print(f"lat0={lat0}: max l = {best[0]:.5f}  v0_lat={np.round(v[0,:2],3)} r0_lat={np.round(r[0,:2],3)} "
              f"r0z={r[0,2]:.2f} v0z={v[0,2]:.2f} min r_z(interior)={r[1:-1,2].min():.3f} max tilt={tilt.max():.1f}deg "
              f"T early/late={T[:3].round(0)}/{T[-3:].round(0)}", flush=True)
    print(f"tf={tf} s*={sstar} glide={np.degrees(gs)}deg  modes={modes} maxima={[round(out[k][0],5) for k in modes]}", flush=True)
