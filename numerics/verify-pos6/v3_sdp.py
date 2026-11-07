"""[verify-pos6] Spot checks of math/08 (Thm 4.1 and Prop 5.1) on the unit-d discretization D^unit.

D^unit: b_0=b_N=e_z, unknown unit b_1..b_{N-1}, unit d_0..d_{N-1};
<d_k,b_k> >= cos(delta), <d_k,b_{k+1}> >= cos(delta), <b_k,b_{k+1}> >= cos(omega h).
cost |sum cv_k d_k - wv|^2 + |sum cr_k d_k - wr|^2.

Test A (Thm 4.1, coplanar data): best planar config (planar multistart) -> is it a 3D local min
  (3D SLSQP from planar + out-of-plane kicks)? If yes, Thm 4.1 predicts SDP == planar value.
Test B (Prop 5.1, non-coplanar data): SDP (IPM -> max-rank point of the optimal face); if all rate duals > 0,
  Prop 5.1 predicts rank(G) <= 4 (G includes the E basis; needs E_w subset W, see report).
"""
import numpy as np, cvxpy as cp, sys
from scipy.optimize import minimize
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
import os
N, tf, a = int(os.environ.get('VN', 4)), 1.0, 1.0
delta = np.radians(15); omega = 1.0/tf
h = tf/N
cv = h*a*np.ones(N); cr = h*a*(tf - (np.arange(N)+0.5)*h)
cd, cw = np.cos(delta), np.cos(omega*h)
nb, nd = N-1, N
m = nb + nd
ez = np.array([0, 0, 1.])
# index helpers: z = [b_1..b_{N-1}, d_0..d_{N-1}]
def bidx(k):  # k = 0..N ; returns None for fixed e_z
    return None if k in (0, N) else k-1
def didx(k): return nb + k

def cost_z(Z, wv, wr):
    D = Z[nb:]
    return np.sum((cv @ D - wv)**2) + np.sum((cr @ D - wr)**2)

def get_b(Z, k):
    i = bidx(k); return ez if i is None else Z[i]

def cons_list(Z):
    out = []
    for k in range(N):
        out += [Z[didx(k)] @ get_b(Z, k) - cd, Z[didx(k)] @ get_b(Z, k+1) - cd, get_b(Z, k) @ get_b(Z, k+1) - cw]
    return np.array(out)

def solve3d(wv, wr, Z0):
    x0 = Z0.ravel()
    f = lambda x: cost_z(x.reshape(m, 3), wv, wr)
    eq = {'type': 'eq', 'fun': lambda x: np.sum(x.reshape(m, 3)**2, axis=1) - 1}
    ineq = {'type': 'ineq', 'fun': lambda x: cons_list(x.reshape(m, 3))}
    r = minimize(f, x0, constraints=[eq, ineq], method='SLSQP', options=dict(maxiter=1000, ftol=1e-14))
    Z = r.x.reshape(m, 3)
    feas = np.abs(np.sum(Z**2, 1)-1).max() < 1e-7 and cons_list(Z).min() > -1e-7
    return (r.fun if feas else np.inf), Z

def solve_planar(wv, wr, th0):
    def Z_of(th): return np.stack([np.sin(th), 0*th, np.cos(th)], 1)
    f = lambda th: cost_z(Z_of(th), wv, wr)
    ineq = {'type': 'ineq', 'fun': lambda th: cons_list(Z_of(th))}
    r = minimize(f, th0, constraints=[ineq], method='SLSQP', options=dict(maxiter=1000, ftol=1e-15))
    Z = Z_of(r.x)
    return (r.fun if cons_list(Z).min() > -1e-8 else np.inf), Z

def sdp(wv, wr):
    n = 3 + m
    G = cp.Variable((n, n), symmetric=True)
    zi = lambda i: 3 + i
    def ip(u, v):  # u, v: ('z', i) or ('e', vec)
        if u[0] == 'e' and v[0] == 'e': return float(u[1] @ v[1])
        if u[0] == 'e': u, v = v, u
        if v[0] == 'e': return sum(v[1][j]*G[zi(u[1]), j] for j in range(3) if v[1][j] != 0)
        return G[zi(u[1]), zi(v[1])]
    def bref(k):
        i = bidx(k); return ('e', ez) if i is None else ('z', i)
    cons = [G >> 0, G[:3, :3] == np.eye(3)] + [G[zi(i), zi(i)] == 1 for i in range(m)]
    rate = []
    for k in range(N):
        cons += [ip(('z', didx(k)), bref(k)) >= cd, ip(('z', didx(k)), bref(k+1)) >= cd]
        c = ip(bref(k), bref(k+1)) >= cw
        if not (bidx(k) is None and bidx(k+1) is None):
            rate.append(c)
        cons.append(c)
    C = np.outer(cv, cv) + np.outer(cr, cr)
    Gdd = G[3+nb:, 3+nb:]
    lin = sum(G[3+didx(k), j]*(cv[k]*wv[j] + cr[k]*wr[j]) for k in range(N) for j in range(3))
    obj = cp.trace(C @ Gdd) - 2*lin + wv @ wv + wr @ wr
    p = cp.Problem(cp.Minimize(obj), cons)
    p.solve(solver=cp.CLARABEL, tol_gap_abs=1e-10, tol_gap_rel=1e-10, tol_feas=1e-10)
    ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]
    return p.value, ev, [float(c.dual_value) for c in rate]

def random_genuine():
    # random feasible chain (tilting within the rate limit), then random d in lens
    th = np.cumsum(rng.uniform(-1, 1, N+1)*omega*h*0.95); th -= th[0]
    th[-1] = 0
    for _ in range(100):
        ok = all(abs(th[k+1]-th[k]) <= omega*h*0.999 for k in range(N))
        if ok: break
        th = 0.7*th
    az = rng.uniform(0, 2*np.pi, N+1)
    B = [ez] + [np.array([np.sin(t)*np.cos(p), np.sin(t)*np.sin(p), np.cos(t)]) for t, p in zip(th[1:-1], az[1:-1])] + [ez]
    return B

def multistart3d(wv, wr, n=25, extra=()):
    best, Zb = np.inf, None
    starts = list(extra)
    for _ in range(n):
        Z0 = rng.normal(size=(m, 3))*0.3 + ez; Z0 /= np.linalg.norm(Z0, axis=1)[:, None]; starts.append(Z0)
    for Z0 in starts:
        v, Z = solve3d(wv, wr, Z0)
        if v < best: best, Zb = v, Z
    return best, Zb

mode = sys.argv[2] if len(sys.argv) > 2 else "A"
ntrial = int(sys.argv[3]) if len(sys.argv) > 3 else 10
for t in range(ntrial):
    if mode == "A":   # coplanar data in the x-z plane
        wv = np.array([rng.uniform(-.3, .3), 0, rng.uniform(.5, 1.2)])
        wr = np.array([rng.uniform(-.2, .2), 0, rng.uniform(.2, .6)])
    elif mode == "D":   # far, aligned lateral targets (tent-shaped tilt wanted)
        az = rng.uniform(0, 2*np.pi); u = np.array([np.cos(az), np.sin(az), 0])
        wv = rng.uniform(2, 4)*u + np.array([0, 0, rng.uniform(.0, .6)]) + 0.2*rng.normal(size=3)*np.array([1, 1, 0])
        wr = rng.uniform(1, 2)*u + np.array([0, 0, rng.uniform(.0, .3)]) + 0.1*rng.normal(size=3)*np.array([1, 1, 0])
    elif mode == "C":   # far lateral targets: force rate saturation
        wv = np.array([rng.uniform(-1.5, 1.5), rng.uniform(-1.5, 1.5), rng.uniform(.3, 1.0)])
        wr = np.array([rng.uniform(-.8, .8), rng.uniform(-.8, .8), rng.uniform(.1, .5)])
    else:
        wv = np.array([rng.uniform(-.3, .3), rng.uniform(-.3, .3), rng.uniform(.5, 1.2)])
        wr = np.array([rng.uniform(-.2, .2), rng.uniform(-.2, .2), rng.uniform(.2, .6)])
    s_val, ev, rd = sdp(wv, wr)
    if mode == "A":
        pbest, Zp = np.inf, None
        for _ in range(30):
            v, Z = solve_planar(wv, wr, rng.uniform(-.4, .4, m))
            if v < pbest: pbest, Zp = v, Z
        # is the planar optimum a 3D local min?  kick out of plane and re-solve
        drop = 0.0
        for s in range(8):
            Z0 = Zp + 1e-2*rng.normal(size=(m, 3))*np.array([0, 1, 0]); Z0 /= np.linalg.norm(Z0, axis=1)[:, None]
            v, _ = solve3d(wv, wr, Z0)
            drop = max(drop, pbest - v)
        g3, _ = multistart3d(wv, wr, n=15, extra=[Zp])
        loc = drop < 1e-9*max(1, pbest)
        verdict = ""
        if loc and abs(s_val - pbest) > 1e-6*max(1e-3, pbest): verdict = "  <-- Thm 4.1 VIOLATION?"
        print(f"[A{t}] SDP {s_val:.8f} planar {pbest:.8f} best3D {g3:.8f} planar-is-3D-local-min={loc} "
              f"(max drop {drop:.2e}) rank(G)={np.sum(ev > 1e-6*ev[0])}{verdict}", flush=True)
    else:
        g3, _ = multistart3d(wv, wr, n=25)
        r = int(np.sum(ev > 1e-6*ev[0]))
        sat = min(rd[1:N-1]) > 1e-7  # Prop 5.1 needs nu_k>0 for 1<=k<=N-2
        verdict = "  <-- Prop 5.1 VIOLATION?" if (sat and r > 4) else ""
        print(f"[B{t}] SDP {s_val:.8f} best3D {g3:.8f} gap {(g3-s_val)/max(g3,1e-12):+.2e} rank(G)={r} "
              f"ev4..6={ev[3]:.1e},{ev[4]:.1e},{ev[5]:.1e} rate duals {np.array2string(np.array(rd), precision=1)} rate-saturated={sat}{verdict}", flush=True)
