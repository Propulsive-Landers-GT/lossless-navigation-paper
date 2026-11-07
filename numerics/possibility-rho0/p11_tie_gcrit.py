"""Random search for non-singleton faces of K (planar M1, rho1=0, alpha=0; omega=1, a2=1 units, tf=T) and,
for each tie, the largest gravity (as a fraction of full-throttle accel, g/a2 = 1/(T/W)) for which BOTH witness
trajectories (landing at r=v=0) keep r_z >= 0:   g_crit = min_t  int_t^tf (s-t) a d_z ds / ((tf-t)^2/2).
Witnesses are then in F^X (altitude-constrained) for every g <= min(g_crit1, g_crit2)."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, sys, json
from dp import solve
T = float(sys.argv[1]); dd = float(sys.argv[2]); seed = int(sys.argv[3]); ntr = int(sys.argv[4])
dl = np.deg2rad(dd); N, m = 200, 3; h = T/N
rng = np.random.default_rng(seed)
sm = (np.arange(N)+0.5)*h
def gcrit(a, dang):
    uz = a*np.cos(dang)
    best = np.inf
    for k in range(N):
        t = k*h; L = np.sum((sm[k:] - t)*uz[k:])*h
        best = min(best, L/((T - t)**2/2))
    return best
def X_of(A, B):
    val, beta, X, a, dang = solve(A, B, T, 1.0, dl, N=N, m=m)
    return X, a, dang
out = []
for trial in range(ntr):
    A0, B0, A1, B1 = rng.normal(size=2), rng.normal(size=2)/T, rng.normal(size=2), rng.normal(size=2)/T
    ts = np.linspace(0, 1, 41); Xs = [X_of((1-t)*A0+t*A1, (1-t)*B0+t*B1)[0] for t in ts]
    dX = np.linalg.norm(np.diff(Xs, axis=0), axis=1); med = np.median(dX) + 1e-12
    for k in np.where(dX > 15*med)[0]:
        lo, hi = ts[k], ts[k+1]; Xlo, Xhi = Xs[k], Xs[k+1]
        for _ in range(28):
            mid = 0.5*(lo+hi); Xm = X_of((1-mid)*A0+mid*A1, (1-mid)*B0+mid*B1)[0]
            if np.linalg.norm(Xm - Xlo) < np.linalg.norm(Xm - Xhi): lo = mid
            else: hi = mid
        W = [X_of((1-t)*A0+t*A1, (1-t)*B0+t*B1) for t in (lo, hi)]
        sep = float(np.linalg.norm(W[0][0] - W[1][0]))
        if sep < 0.02*max(np.linalg.norm(W[0][0]), 1e-9): continue
        gc = [float(gcrit(w[1], w[2])) for w in W]
        r = dict(trial=trial, t=lo, sep=sep, sep_rel=sep/np.linalg.norm(W[0][0]), gcrit=gc,
                 A=((1-lo)*A0+lo*A1).tolist(), B=((1-lo)*B0+lo*B1).tolist(), end_thrust=[int(w[1][-1] > 0) for w in W])
        out.append(r); print(json.dumps(r), flush=True)
good = sorted([min(r["gcrit"]) for r in out], reverse=True)
print(f"T={T} delta={dd}: ties {len(out)}; best min(gcrit) = {good[:5]}")
