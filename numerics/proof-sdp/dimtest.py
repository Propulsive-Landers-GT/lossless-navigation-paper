"""proof-sdp: compare the C-SD2 SDP value with genuine multistart NLP optima on S^{n-1}, n=3,4,5.
Discrete model as in redteam-lift sdp_clean.py: vertical = coordinate 0, b_0=b_N=e_0, d_k within delta of b_k,b_{k+1},
<b_k,b_{k+1}> >= cos(omega h); cost ||sum cv_k d_k - wv||^2 + ||sum cr_k d_k - wr||^2 (gravity absorbed in w)."""
import numpy as np, cvxpy as cp
from scipy.optimize import minimize

def weights(N, tf, a1=5.0):
    h = tf / N
    return h, h * a1 * np.ones(N), h * a1 * (tf - (np.arange(N) + 0.5) * h)

def sdp(wv, wr, N, tf, om, dl, a1=5.0):
    h, cv, cr = weights(N, tf, a1); nbi = N - 1; n = 3 + nbi + N
    G = cp.Variable((n, n), PSD=True)
    B = lambda k: 0 if k in (0, N) else 3 + (k - 1)
    D = lambda k: 3 + nbi + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(i, 3)]
    cons += [G[3 + i, 3 + i] == 1 for i in range(nbi + N)]
    for k in range(N):
        if N > 1: cons += [G[B(k), B(k + 1)] >= np.cos(om * h)]
        cons += [G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    di = [D(k) for k in range(N)]
    def sq(c, w):
        m = [cp.sum(cp.multiply(c, cp.hstack([G[D(k), i] for k in range(N)]))) for i in range(3)]
        return cp.sum(cp.multiply(np.outer(c, c), G[np.ix_(di, di)])) - 2 * sum(w[i] * m[i] for i in range(3)) + float(w @ w)
    p = cp.Problem(cp.Minimize(sq(cv, wv) + sq(cr, wr)), cons); p.solve(solver=cp.CLARABEL)
    ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]
    return p.value, p.status, ev, G.value

def nlp(wv, wr, N, tf, om, dl, n=3, starts=40, seed=0, a1=5.0, x0s=None):
    h, cv, cr = weights(N, tf, a1); nbi = N - 1; nv = nbi + N
    e0 = np.zeros(n); e0[0] = 1
    W = np.zeros((2, n)); W[0, :3] = wv; W[1, :3] = wr
    def unpack(x):
        Z = x.reshape(nv, n); Z = Z / np.linalg.norm(Z, axis=1, keepdims=True)
        Bs = np.vstack([e0, Z[:nbi], e0]); Ds = Z[nbi:]; return Bs, Ds
    def f(x):
        Bs, Ds = unpack(x); V = cv @ Ds - W[0]; R = cr @ Ds - W[1]; return V @ V + R @ R
    def g(x):
        Bs, Ds = unpack(x); out = []
        for k in range(N):
            out += [Bs[k] @ Bs[k + 1] - np.cos(om * h), Ds[k] @ Bs[k] - np.cos(dl), Ds[k] @ Bs[k + 1] - np.cos(dl)]
        return np.array(out)
    rng = np.random.default_rng(seed); best = (np.inf, None)
    inits = list(x0s or [])
    for s in range(starts):
        # random near-vertical start
        Z = np.tile(e0, (nv, 1)) + rng.normal(scale=rng.uniform(0.05, 0.6), size=(nv, n)); inits.append(Z.ravel())
    for x0 in inits:
        r = minimize(f, x0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': g}], options={'maxiter': 2000, 'ftol': 1e-14})
        if r.success or True:
            if np.min(g(r.x)) > -1e-8 and r.fun < best[0]: best = (r.fun, r.x)
    return best[0], (unpack(best[1]) if best[1] is not None else None)
