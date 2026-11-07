"""A8: adversarial check of Lemma W / Prop M core, small-angle limit, delta=0, uniform weight.
Maximize mean-square tilt (1/T) int |beta|^2 over 2D rate-limited paths beta(0)=0, |beta'|<=om, with
 Pv: int beta = 0 ;  Pvr: int beta = int s beta = 0.   Claims: Pv >= 0.0404 Om^2, Pvr <= 1/(4pi^2)=0.0253 Om^2."""
import numpy as np
from scipy.optimize import minimize
T, om, N = 1.0, 1.0, 80
h = T/N; s = (np.arange(1, N+1))*h          # beta at nodes 1..N (beta_0 = 0)
def run(mode, init, seed):
    rng = np.random.default_rng(seed)
    if init == 'planar':
        t1 = rng.uniform(0.2, 0.4); ph = np.where(s <= t1, s, 2*t1 - s); B = np.stack([ph, 0*ph], 1)
    elif init == 'coning':
        rho = rng.uniform(0.05, 0.3); ramp = np.minimum(s, rho); psi = np.cumsum(np.where(s >= rho, 1/rho, 0))*h
        B = np.stack([ramp*np.cos(psi), ramp*np.sin(psi)], 1)
    else:
        B = np.cumsum(rng.normal(size=(N, 2))*h*0.7, 0)
    f = lambda x: -np.sum(x.reshape(N, 2)**2)*h/T
    fg = lambda x: -2*x*h/T
    def ineq(x):
        Bp = np.vstack([np.zeros(2), x.reshape(N, 2)]); return (om*h)**2 - np.sum(np.diff(Bp, axis=0)**2, 1)
    def eq(x):
        Bx = x.reshape(N, 2); e = [Bx.sum(0)*h]
        if mode == 'Pvr': e.append((s[:, None]*Bx).sum(0)*h)
        return np.concatenate(e)
    r = minimize(f, B.ravel(), jac=fg, method='SLSQP', constraints=[{'type': 'ineq', 'fun': ineq}, {'type': 'eq', 'fun': eq}],
                 options={'maxiter': 2000, 'ftol': 1e-13})
    ok = ineq(r.x).min() > -1e-9 and np.abs(eq(r.x)).max() < 1e-9
    return -r.fun if ok else -np.inf
for mode in ('Pv', 'Pvr'):
    best = max(run(mode, i, sd) for i in ('planar', 'coning', 'random') for sd in range(8))
    print(f"{mode}: max mean-square tilt / Omega^2 = {best:.5f}", flush=True)
print("claims: Pv >= 0.04044 (S-turn), Pvr <= 0.02533 (Wirtinger)")
