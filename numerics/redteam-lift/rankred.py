"""redteam-lift: search the C-SD2 optimal face for a rank-3 (genuine) point via reweighted trace minimization.
If found (rank 3, objective = SDP value), the SDP is exact at that target and the NLP 'gap' was an NLP failure."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from csd2_deep import targets

def build(wv, wr, N, tf, om, dl, a1=5.0):
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
    return G, cons, sq(cv, wv) + sq(cr, wr)

def run(wv, wr, N, tf, om, dl, slack_rel=1e-6, iters=8):
    G, cons, obj = build(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value
    Gv = G.value; out = [f"SDP={v:.8e} eig4={np.sort(np.linalg.eigvalsh(Gv))[::-1][3]:.2e}"]
    for it in range(iters):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T     # complement of top-3 eigenspace
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + slack_rel * max(abs(v), 1e-3)])
        q.solve(solver=cp.CLARABEL); Gv = G.value
        e = np.sort(np.linalg.eigvalsh(Gv))[::-1]
        out.append(f"it{it}: eig4={e[3]:.2e} obj={obj.value:.8e}")
        if e[3] < 1e-7: break
    return out

if __name__ == "__main__" and len(sys.argv) == 1:
    for ci, lab in [(0, "rand0"), (1, "rand1")]:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab: print(f"cfg{ci} {lab} N={N}:", " | ".join(run(wv, wr, N, tf, om, dl)), flush=True)

def extract_and_check(wv, wr, N, tf, om, dl, a1=5.0, iters=6):
    G, cons, obj = build(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value; Gv = G.value
    for it in range(iters):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + 1e-7 * max(abs(v), 1e-3)]); q.solve(solver=cp.CLARABEL); Gv = G.value
        if np.sort(np.linalg.eigvalsh(Gv))[::-1][3] < 1e-8: break
    h = tf / N; nb = N + 1
    Bx = np.array([Gv[3 + k, :3] for k in range(nb)]); Dx = np.array([Gv[3 + nb + k, :3] for k in range(N)])
    Bn = Bx / np.linalg.norm(Bx, axis=1, keepdims=True); Dn = Dx / np.linalg.norm(Dx, axis=1, keepdims=True)
    cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    cost = np.sum((cv @ Dn - wv) ** 2) + np.sum((cr @ Dn - wr) ** 2)
    vb = min(Bn[k] @ Bn[k + 1] for k in range(N)) - np.cos(om * h)
    vd = min(min(Dn[k] @ Bn[k], Dn[k] @ Bn[k + 1]) for k in range(N)) - np.cos(dl)
    return v, cost, vb, vd, np.max(np.abs(np.linalg.norm(Bx, axis=1) - 1)), np.abs(Bn[0] - [1, 0, 0]).max(), np.abs(Bn[N] - [1, 0, 0]).max()

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "extract":
    for ci, lab in [(0, "rand0"), (1, "rand1")]:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab:
                v, c, vb, vd, nb_, e0, eN = extract_and_check(wv, wr, N, tf, om, dl)
                print(f"EXTRACT cfg{ci} {lab}: SDP={v:.8e} genuine-3D cost={c:.8e} min slack rate={vb:.1e} gimbal={vd:.1e} |proj b|-1 max={nb_:.1e} b0err={e0:.1e} bNerr={eN:.1e}", flush=True)
