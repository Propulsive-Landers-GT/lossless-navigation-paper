"""redteam-lift: well-posed C-SD2 (b_0=b_N=e_z eliminated, so Slater holds) and solver cross-check."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])

def build(wv, wr, N, tf, om, dl, a1=5.0):
    h = tf / N; nbi = N - 1; n = 3 + nbi + N
    G = cp.Variable((n, n), PSD=True)
    def B(k): return 0 if k in (0, N) else 3 + (k - 1)        # b_0=b_N=e_0 (vertical constant)
    D = lambda k: 3 + nbi + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(i, 3)]
    cons += [G[3 + i, 3 + i] == 1 for i in range(nbi)] + [G[D(k), D(k)] == 1 for k in range(N)]
    for k in range(N):
        if not (k == 0 and N == 1):
            cons += [G[B(k), B(k + 1)] >= np.cos(om * h)]
        cons += [G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    di = [D(k) for k in range(N)]
    cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    def sq(c, w):
        m = [cp.sum(cp.multiply(c, cp.hstack([G[D(k), i] for k in range(N)]))) for i in range(3)]
        return cp.sum(cp.multiply(np.outer(c, c), G[np.ix_(di, di)])) - 2 * sum(w[i] * m[i] for i in range(3)) + float(w @ w)
    return G, cons, sq(cv, wv) + sq(cr, wr)

def solve(wv, wr, N, tf, om, dl):
    G, cons, obj = build(wv, wr, N, tf, om, dl); p = cp.Problem(cp.Minimize(obj), cons)
    p.solve(solver=cp.CLARABEL); a = (p.value, p.status)
    p.solve(solver=cp.SCS, eps_abs=1e-9, eps_rel=1e-9, max_iters=300000); b = (p.value, p.status)
    return a, b

if __name__ == "__main__":
    from csd2_deep import targets
    tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
    for N in (3, 4):
        h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
        cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
        Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
        rng = np.random.default_rng(0); want = {3: (5, 9), 4: (3, 5)}[N]
        for j in range(10):
            lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
            R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
            wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
            if j in want: print(f"CLEAN N={N} j={j}:", solve(wv, wr, N, tf, om, dl), flush=True)
    for ci, lab in [(0, "rand0"), (1, "rand1")]:
        for l, (N, tf_, om_, dl_), wv, wr in targets(ci):
            if l == lab: print(f"CLEAN cfg{ci} {lab} N={N}:", solve(wv, wr, N, tf_, om_, dl_), flush=True)
