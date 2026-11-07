"""proof-sdp: LINEAR objective max sum_k <d_k, l_k> (far-target limit). H-optimum = R^{dim E +1} optimum by folding.
Compare NLP in R^3 vs R^4 and SDP."""
import numpy as np, cvxpy as cp, sys
from scipy.optimize import minimize

def sdp_lin(L, N, h, om, dl):
    nbi = N - 1; n = 3 + nbi + N; G = cp.Variable((n, n), PSD=True)
    B = lambda k: 0 if k in (0, N) else 3 + (k - 1); D = lambda k: 3 + nbi + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(i, 3)] + [G[3 + i, 3 + i] == 1 for i in range(nbi + N)]
    for k in range(N):
        cons += [G[B(k), B(k + 1)] >= np.cos(om * h), G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    obj = sum(L[k, i] * G[D(k), i] for k in range(N) for i in range(3))
    p = cp.Problem(cp.Maximize(obj), cons); p.solve(solver=cp.CLARABEL)
    ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]; return p.value, p.status, ev

def nlp_lin(L, N, h, om, dl, n, starts, seed=0):
    nbi = N - 1; nv = nbi + N; e0 = np.zeros(n); e0[0] = 1; Ln = np.zeros((N, n)); Ln[:, :3] = L
    def unpack(x):
        Z = x.reshape(nv, n); Z = Z / np.linalg.norm(Z, axis=1, keepdims=True); return np.vstack([e0, Z[:nbi], e0]), Z[nbi:]
    f = lambda x: -np.sum(unpack(x)[1] * Ln)
    def g(x):
        Bs, Ds = unpack(x)
        return np.concatenate([np.einsum('ij,ij->i', Bs[:-1], Bs[1:]) - np.cos(om * h), np.einsum('ij,ij->i', Ds, Bs[:-1]) - np.cos(dl), np.einsum('ij,ij->i', Ds, Bs[1:]) - np.cos(dl)])
    rng = np.random.default_rng(seed); best = -np.inf; bx = None
    for s in range(starts):
        Z = np.tile(e0, (nv, 1)) + rng.normal(scale=rng.uniform(0.05, 1.0), size=(nv, n))
        r = minimize(f, Z.ravel(), method='SLSQP', constraints=[{'type': 'ineq', 'fun': g}], options={'maxiter': 3000, 'ftol': 1e-15})
        if np.min(g(r.x)) > -1e-8 and -r.fun > best: best = -r.fun; bx = r.x
    return best, unpack(bx)

if __name__ == "__main__":
    N = int(sys.argv[1]); tf = float(sys.argv[2]); om = np.deg2rad(float(sys.argv[3])); dl = np.deg2rad(float(sys.argv[4])); K = int(sys.argv[5])
    h = tf / N; s = (np.arange(N) + 0.5) * h; rng = np.random.default_rng(int(sys.argv[6]) if len(sys.argv) > 6 else 0)
    for j in range(K):
        if j == 0:   # flip -x -> +x through a tilted direction y
            wv = np.array([0, 1, 0.]); y = np.array([0.6, 0, 0.8]); wr = (-2 * wv + 0.8 * y) / tf
        else:
            wv = rng.normal(size=3); wr = rng.normal(size=3) / tf * rng.uniform(0.5, 3)
        L = h * (np.outer(np.ones(N), wv) + np.outer(tf - s, wr))
        v, st, ev = sdp_lin(L, N, h, om, dl)
        n3, (B3, D3) = nlp_lin(L, N, h, om, dl, 3, 40); n4, (B4, D4) = nlp_lin(L, N, h, om, dl, 4, 40)
        e4 = np.max(np.abs(np.vstack([B4, D4])[:, 3]))
        print(f"N={N} j={j} SDP={v:.8f}[{st}] NLP3={n3:.8f} NLP4={n4:.8f} max|x4|={e4:.2e} (SDP-NLP3)/|NLP3|={(v-n3)/abs(n3):+.2e} ev={np.round(ev[:5]/ev[0],5)}", flush=True)
