"""Random search for non-singleton faces of K (planar M1, rho1=0, alpha=0) and altitude feasibility of the witnesses.
Physical GTPL-like units: a2 = 12.5 m/s^2, g = 9.80665, omega = 0.4 rad/s, delta = 15 deg, tf = argv[1].
For each tie: both maximiser trajectories landing at r=v=0 at tf; report min altitude (r_z) along each."""
import numpy as np, sys, json
from dp import solve
tf = float(sys.argv[1]); seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
om, dl, a2, g = 0.4, np.deg2rad(15), 12.5, 9.80665
N, m = 200, 3
rng = np.random.default_rng(seed)

def traj_min_alt(beta, a, dang):
    h = tf/N
    acc_z = a*np.cos(dang) - g; acc_x = a*np.sin(dang)
    # backward from rest at origin, piecewise-constant acc
    vz = np.zeros(N+1); rz = np.zeros(N+1); vx = np.zeros(N+1); rx = np.zeros(N+1)
    for k in range(N-1, -1, -1):
        vz[k] = vz[k+1] - acc_z[k]*h; rz[k] = rz[k+1] - vz[k+1]*h + 0.5*acc_z[k]*h*h
        vx[k] = vx[k+1] - acc_x[k]*h; rx[k] = rx[k+1] - vx[k+1]*h + 0.5*acc_x[k]*h*h
    return rz.min(), (rx[0], rz[0], vx[0], vz[0])

def X_of(A, B):
    val, beta, X, a, dang = solve(A, B, tf, om, dl, N=N, m=m, a2=a2)
    return X, beta, a, dang

res = []; ntie = 0
for trial in range(int(sys.argv[3]) if len(sys.argv) > 3 else 60):
    A0, B0 = rng.normal(size=2), rng.normal(size=2)/tf
    A1, B1 = rng.normal(size=2), rng.normal(size=2)/tf
    ts = np.linspace(0, 1, 41); Xs = [X_of((1-t)*A0+t*A1, (1-t)*B0+t*B1)[0] for t in ts]
    dX = np.linalg.norm(np.diff(Xs, axis=0), axis=1); med = np.median(dX) + 1e-9
    for k in np.where(dX > 15*med)[0]:
        lo, hi = ts[k], ts[k+1]; Xlo = Xs[k]
        for _ in range(30):
            mid = 0.5*(lo+hi); Xm = X_of((1-mid)*A0+mid*A1, (1-mid)*B0+mid*B1)[0]
            if np.linalg.norm(Xm - Xlo) < np.linalg.norm(Xm - Xs[k+1]): lo = mid
            else: hi = mid
        w = []
        for t in (lo, hi):
            X, beta, a, dang = X_of((1-t)*A0+t*A1, (1-t)*B0+t*B1); w.append((X, traj_min_alt(beta, a, dang)))
        sep = float(np.linalg.norm(w[0][0]-w[1][0]))
        if sep < 0.05*np.linalg.norm(w[0][0]) + 1e-6: continue
        ntie += 1
        r = dict(trial=trial, t=lo, sep=sep, minalt=[float(w[0][1][0]), float(w[1][1][0])],
                 theta0=[list(map(float, w[0][1][1])), list(map(float, w[1][1][1]))])
        res.append(r); print(json.dumps(r), flush=True)
feas = [r for r in res if min(r["minalt"]) >= -1e-6]
print(f"tf={tf}: ties found {ntie}; with both witnesses above ground: {len(feas)}")
