"""A5: coning vs planar S-turn in the slice lemma S (v0_lat = 0 imposed).
Small-angle lateral model (qualitative): tilt vectors in R^2. b-tilt beta (|beta'|<=om, beta(0)=0, |beta|<=cap),
thrust tilt theta with |theta-beta|<=delta.  Vertical waste ~ |theta|^2/2 (a const, alpha=0).
Maximize  J = sum c_k |theta_k|^2/2 h   where c_k = -w(s_k) on the waste window (w<0), and late (w>0) costs w*|theta|^2/2:
   J = sum (-w_k) |theta_k|^2/2 h       (w = s - s*;  s*=tf -> pure dive)
 Pv : int theta = 0 ;  Pvr : int theta = 0 and int s theta = 0  (landing straight below).
Multistart with planar (S-turn), coning and random initial guesses; analytic gradients; SLSQP."""
import numpy as np, sys, json
from scipy.optimize import minimize
delta, om = 0.26, 0.4
def setup(tf, sstar, cap, N):
    h = tf/N; s = (np.arange(N)+0.5)*h; w = s - sstar
    return h, s, w
def solve(tf, sstar, cap, N, mode, init, seed):
    h, s, w = setup(tf, sstar, cap, N); rng = np.random.default_rng(seed)
    def unpack(x): return x[:2*N].reshape(N, 2), x[2*N:].reshape(N, 2)    # beta at s_k (beta_0 implied 0), theta
    def f(x):
        B, Th = unpack(x); return np.sum(w*np.sum(Th**2, 1))*h/2         # minimize -J = sum w|th|^2/2
    def fg(x):
        B, Th = unpack(x); return np.concatenate([np.zeros(2*N), (w[:, None]*Th).ravel()*h])
    def ineq(x):
        B, Th = unpack(x); Bp = np.vstack([np.zeros(2), B])
        dB = np.diff(Bp, axis=0)
        c = [(om*h)**2 - np.sum(dB**2, 1), delta**2 - np.sum((Th-B)**2, 1)]
        if cap: c.append(cap**2 - np.sum(B**2, 1))
        return np.concatenate(c)
    def eq(x):
        B, Th = unpack(x); e = [Th.sum(0)*h]
        if mode == 'Pvr': e.append((s[:, None]*Th).sum(0)*h)
        return np.concatenate(e)
    # initial guesses
    if init == 'planar':
        k = rng.integers(1, 4); tri = om*tf/(2*np.pi*k)*np.sin(np.pi*k*s/tf*rng.uniform(0.8, 1.2))
        B = np.stack([tri, 0*tri], 1)
    elif init == 'coning':
        rho = min(cap or 9, om*tf/(2*np.pi)*rng.uniform(0.5, 3)); ramp = np.minimum(om*s, rho)
        psi = np.cumsum(np.where(om*s >= rho, om/max(rho, 1e-3), 0))*h + rng.uniform(0, 6.3)
        B = np.stack([ramp*np.cos(psi), ramp*np.sin(psi)], 1)
    else:
        B = np.cumsum(rng.normal(size=(N, 2))*om*h*0.7, 0)
    if cap: B *= np.minimum(1, cap/np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-9))
    Th = B + delta*0.9*B/np.maximum(np.linalg.norm(B, axis=1, keepdims=True), 1e-6)
    x0 = np.concatenate([B.ravel(), Th.ravel()])
    r = minimize(f, x0, jac=fg, method='SLSQP', constraints=[{'type': 'ineq', 'fun': ineq}, {'type': 'eq', 'fun': eq}],
                 options={'maxiter': 1500, 'ftol': 1e-12})
    ok = ineq(r.x).min() > -1e-8 and np.abs(eq(r.x)).max() < 1e-8
    B, Th = unpack(r.x)
    planarity = np.linalg.svd(B, compute_uv=False); planarity = planarity[1]/max(planarity[0], 1e-12)
    off = (s[:, None]*Th).sum(0)*h
    return (-r.fun if ok else -np.inf), planarity, np.linalg.norm(off)
if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rows = []
    for (tf, sstar) in [(3, 3), (8, 8), (20, 20), (8, 0.5), (8, 1.5), (20, 2.0)]:
        for cap in (0, 0.6):
            res = {}
            for mode in ('Pv', 'Pvr'):
                best = (-np.inf, None, None, None)
                for init in ('planar', 'coning', 'random'):
                    for sd in range(3):
                        v, pl, off = solve(tf, sstar, cap, N, mode, init, sd)
                        if v > best[0]: best = (v, init, pl, off)
                res[mode] = best
            gap = res['Pv'][0] - res['Pvr'][0]
            line = (f"tf={tf:>4} s*={sstar:>4} cap={cap}: Pv={res['Pv'][0]:.6f} [{res['Pv'][1]}, planarity {res['Pv'][2]:.2f}, |offset| {res['Pv'][3]:.4f}] "
                    f"Pvr={res['Pvr'][0]:.6f} [{res['Pvr'][1]}, planarity {res['Pvr'][2]:.2f}]  gap={gap:.2e} rel={gap/max(res['Pv'][0],1e-12):.2e}")
            print(line, flush=True); rows.append(line)
