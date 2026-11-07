"""redteam-lift: factor the C-SD2 Gram into an explicit n-dim pseudo-trajectory (constants -> e_0..e_2),
verify it is feasible for the n-dim problem and reproduces the SDP value (Hilbert-sphere lemma check)."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from csd2_deep import targets

def solve_G(wv, wr, N, tf, om, dl, a1=5.0):
    h = tf / N; nb = N + 1; nd = N; n = 3 + nb + nd
    G = cp.Variable((n, n), PSD=True); B = lambda k: 3 + k; D = lambda k: 3 + nb + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(3)]
    cons += [G[B(k), B(k)] == 1 for k in range(nb)] + [G[D(k), D(k)] == 1 for k in range(nd)]
    cons += [G[B(0), 0] == 1, G[B(N), 0] == 1]
    for k in range(N):
        cons += [G[B(k), B(k + 1)] >= np.cos(om * h), G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    di = [D(k) for k in range(nd)]
    cv = h * a1 * np.ones(nd); cr = h * a1 * (tf - (np.arange(nd) + 0.5) * h)
    def sq(c, w):
        m = [cp.sum(cp.multiply(c, cp.hstack([G[D(k), i] for k in range(nd)]))) for i in range(3)]
        return cp.sum(cp.multiply(np.outer(c, c), G[np.ix_(di, di)])) - 2 * sum(w[i] * m[i] for i in range(3)) + float(w @ w)
    pr = cp.Problem(cp.Minimize(sq(cv, wv) + sq(cr, wr)), cons); pr.solve(solver=cp.CLARABEL)
    return pr.value, G.value, cv, cr

if __name__ == "__main__":
  for ci, lab in [(0, "rand0")]:
      for l, (N, tf, om, dl), wv, wr in targets(ci):
          if l != lab: continue
          val, Gv, cv, cr = solve_G(wv, wr, N, tf, om, dl)
          ev, V = np.linalg.eigh(Gv); idx = ev > 1e-7; X = V[:, idx] * np.sqrt(ev[idx])   # rows = vectors
          print("eigenvalues (desc):", np.round(np.sort(ev)[::-1][:14], 5))
          Q, _ = np.linalg.qr(np.c_[X[:3].T, np.random.default_rng(0).normal(size=(X.shape[1], X.shape[1] - 3))])
          Y = X @ Q; Y[:, :3] = X @ np.linalg.pinv(X[:3]) if False else Y[:, :3]
          # rows 0..2 should be orthonormal constants; express everything in basis where they are e_0..e_2
          C = Y[:3]; T = np.linalg.solve(C[:, :3], np.eye(3)) if False else None
          nb = N + 1; Bm = Y[3:3 + nb]; Dm = Y[3 + nb:]
          Sv = cv @ Dm; Sr = cr @ Dm
          Wv = np.zeros(Y.shape[1]); Wr = np.zeros(Y.shape[1])
          Wv[:] = (wv @ np.linalg.pinv(C).T) if False else 0
          # target in the same coordinates: w = sum_i w_i * C_i
          Wv = wv @ C; Wr = wr @ C
          cost = np.sum((Sv - Wv) ** 2) + np.sum((Sr - Wr) ** 2)
          lat = lambda v: np.linalg.norm(v - (v @ C.T) @ C)
          print(f"cfg{ci} {lab}: SDP={val:.6e} factored cost={cost:.6e} dim={Y.shape[1]}  |Sv off-R3|={lat(Sv):.2e} |Sr off-R3|={lat(Sr):.2e}")
          bz = Bm @ C[0]; print("min |b|-1:", np.max(np.abs(np.linalg.norm(Bm, axis=1) - 1)), " b·e_z profile:", np.round(bz, 3))
          offdim = [np.linalg.norm(Dm[k] - (Dm[k] @ C.T) @ C) for k in range(N)]
          print("d_k component outside R^3:", np.round(offdim, 3))
