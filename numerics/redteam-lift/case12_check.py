"""redteam-lift: independent check of [numerics] case 12 (CSD2 counterexample candidate).
(1) well-posed SDP value/eigs; (2) factor Gram -> explicit 4D trajectory, verify feasibility + cost = SDP;
(3) SLSQP polish in R^3 and R^4 from many random starts."""
import sys, numpy as np, cvxpy as cp
from scipy.optimize import minimize
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sdp_clean import build
N, tf, om, dl, a1 = 16, 4.0, np.deg2rad(30), np.deg2rad(15), 11.0
wv = np.array([32.1819, 5.0939, 21.9914]); wr = np.array([64.908, 8.2825, 44.1701])
h = tf / N; cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
G, cons, obj = build(wv, wr, N, tf, om, dl, a1=a1); p = cp.Problem(cp.Minimize(obj), cons)
p.solve(solver=cp.CLARABEL, tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11); Gv = G.value
ev, V = np.linalg.eigh(Gv); print("SDP", p.value, p.status, "eig", np.round(ev[::-1][:6], 5))
# factor with constants mapped to e_0..e_2
r = int(np.sum(ev > 1e-6)); X = V[:, -r:] * np.sqrt(ev[-r:])
Q, _ = np.linalg.qr(X[:3].T, mode="complete"); Y = X @ Q          # first 3 coords span the constants
Y[:, :3] = Y[:, :3] @ np.linalg.inv(Y[:3, :3])                     # constants -> exact identity
nbi = N - 1; B = np.vstack([Y[0], Y[3:3 + nbi], Y[0]]); D = Y[3 + nbi:]
n = Y.shape[1]; Wv = np.r_[wv, np.zeros(n - 3)]; Wr = np.r_[wr, np.zeros(n - 3)]
ang = lambda a, b: np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))
print(f"factored dim={n}; cost={np.sum((cv @ D - Wv)**2)+np.sum((cr @ D - Wr)**2):.7f}; max rate excess={max(ang(B[k],B[k+1])-om*h for k in range(N)):.1e}; "
      f"max gimbal excess={max(max(ang(D[k],B[k]),ang(D[k],B[k+1]))-dl for k in range(N)):.1e}; norms {np.abs(np.linalg.norm(B,axis=1)-1).max():.1e},{np.abs(np.linalg.norm(D,axis=1)-1).max():.1e}")
def polish(n, z0):
    def unpack(z):
        Bi = z[:n * nbi].reshape(nbi, n); e = np.zeros(n); e[0] = 1
        return np.vstack([e, Bi, e]), z[n * nbi:].reshape(N, n)
    W1 = np.r_[wv, np.zeros(n - 3)]; W2 = np.r_[wr, np.zeros(n - 3)]
    f = lambda z: (lambda B, D: np.sum((cv @ D - W1)**2) + np.sum((cr @ D - W2)**2))(*unpack(z))
    def g(z):
        B, D = unpack(z); gD = 2 * (np.outer(cv, cv @ D - W1) + np.outer(cr, cr @ D - W2)); return np.r_[np.zeros(n * nbi), gD.ravel()]
    eq = lambda z: (lambda B, D: np.r_[np.sum(B[1:-1]**2, 1) - 1, np.sum(D**2, 1) - 1])(*unpack(z))
    iq = lambda z: (lambda B, D: np.r_[np.sum(B[:-1]*B[1:], 1) - np.cos(om*h), np.sum(D*B[:-1], 1) - np.cos(dl), np.sum(D*B[1:], 1) - np.cos(dl)])(*unpack(z))
    r = minimize(f, z0, jac=g, method="SLSQP", constraints=[{"type": "eq", "fun": eq}, {"type": "ineq", "fun": iq}], options={"maxiter": 3000, "ftol": 1e-15})
    ok = np.abs(eq(r.x)).max() < 1e-9 and iq(r.x).min() > -1e-9
    return r.fun if ok else np.inf
# 4D polish from the factored solution (pad/truncate to 4 dims)
if n >= 4:
    z0 = np.r_[B[1:-1, :4].ravel(), D[:, :4].ravel()]; print("4D polish from SDP factor:", polish(4, z0))
rng = np.random.default_rng(1); s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s)
for n in (3, 4):
    best = np.inf
    for t in range(int(sys.argv[1]) if len(sys.argv) > 1 else 60):
        sc = rng.uniform(0, 1); lat = rng.normal(size=(n - 1, 1)) + rng.normal(size=(n - 1, 1)) * s / tf + rng.normal(size=(n - 1, 1)) * (s / tf)**2
        lat /= np.linalg.norm(lat, axis=0, keepdims=True)
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * lat]).T; D0 = 0.5 * (B0[:-1] + B0[1:]); D0 /= np.linalg.norm(D0, axis=1, keepdims=True)
        best = min(best, polish(n, np.r_[B0[1:-1].ravel(), D0.ravel()]))
    print(f"SLSQP multistart best in R^{n}: {best:.7f}", flush=True)
