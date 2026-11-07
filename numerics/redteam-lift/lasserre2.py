"""redteam-lift: order-2 Lasserre (degree-4 moments) lower bound for the N=4 fixed-thrust problem,
to CERTIFY that the order-1 Shor/C-SD2 value is strictly below the true minimum (order-2 bound <= true min).
Variables x = (b_1,b_2,b_3, d_0..d_3) in R^21; b_0 = b_4 = e_z. Vertical = coordinate 0."""
import sys, itertools, numpy as np, scipy.sparse as sp, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from csd2_deep import sdp_rv, nlp

N = int(sys.argv[2]) if len(sys.argv) > 2 else 4
tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h = tf / N; nv = 3 * (N - 1) + 3 * N
def bidx(k): return None if k in (0, N) else [3 * (k - 1) + i for i in range(3)]
def didx(k): return [3 * (N - 1) + 3 * k + i for i in range(3)]
EZ = {(): 0.0}
def padd(p, q, s=1.0):
    r = dict(p)
    for m, c in q.items(): r[m] = r.get(m, 0.0) + s * c
    return r
def pmul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(sorted(m1 + m2)); r[m] = r.get(m, 0.0) + c1 * c2
    return r
def var(i): return {(i,): 1.0}
def const(c): return {(): float(c)}
def vec(k, kind):
    if kind == "b" and bidx(k) is None: return [const(1.0), const(0.0), const(0.0)]
    ids = bidx(k) if kind == "b" else didx(k)
    return [var(i) for i in ids]
def dot(u, v):
    r = {}
    for a, b in zip(u, v): r = padd(r, pmul(a, b))
    return r

mons = lambda d: [()] + [tuple(c) for k in range(1, d + 1) for c in itertools.combinations_with_replacement(range(nv), k)]
B1, B2, B4 = mons(1), mons(2), mons(4)
yid = {m: i for i, m in enumerate(B4)}; ny = len(B4)
y = cp.Variable(ny)
def lin(p):  # linear functional L_y(p)
    rows = [yid[m] for m in p]; vals = [p[m] for m in p]
    return sp.csr_matrix((vals, ([0] * len(rows), rows)), shape=(1, ny)) @ y
def momat(basis, g):
    n = len(basis); R, C, V = [], [], []
    for i, mi in enumerate(basis):
        for j, mj in enumerate(basis):
            for m, c in pmul(pmul({mi: 1.0}, {mj: 1.0}), g).items():
                R.append(i * n + j); C.append(yid[m]); V.append(c)
    A = sp.csr_matrix((V, (R, C)), shape=(n * n, ny))
    return cp.reshape(A @ y, (n, n), order="C")

eqs = [padd(dot(vec(k, "b"), vec(k, "b")), const(-1)) for k in range(1, N)] + [padd(dot(vec(k, "d"), vec(k, "d")), const(-1)) for k in range(N)]
ineqs = [padd(dot(vec(k, "b"), vec(k + 1, "b")), const(-np.cos(om * h))) for k in range(N)]
ineqs += [padd(dot(vec(k, "d"), vec(k, "b")), const(-np.cos(dl))) for k in range(N)] + [padd(dot(vec(k, "d"), vec(k + 1, "b")), const(-np.cos(dl))) for k in range(N)]

def objective(wv, wr):
    cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h); p = {}
    for c, w in ((cv, wv), (cr, wr)):
        for i in range(3):
            e = const(-w[i])
            for k in range(N): e = padd(e, {(didx(k)[i],): c[k]})
            p = padd(p, pmul(e, e))
    return p

def bound(wv, wr):
    cons = [y[yid[()]] == 1, momat(B2, const(1.0)) >> 0]
    for g in eqs:
        for m in B2:
            pm = pmul({m: 1.0}, g)
            if max(len(t) for t in pm) <= 4: cons.append(lin(pm) == 0)
    cons += [momat(B1, g) >> 0 for g in ineqs]
    pr = cp.Problem(cp.Minimize(lin(objective(wv, wr))), cons)
    if len(sys.argv) > 3 and sys.argv[3] == "scs":
        pr.solve(solver=cp.SCS, eps_abs=1e-8, eps_rel=1e-8, max_iters=200000, acceleration_lookback=10)
    else:
        pr.solve(solver=cp.CLARABEL)
    return pr.value, pr.status

if __name__ == "__main__":
    s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
    cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
    rng = np.random.default_rng(0); want = [int(t) for t in sys.argv[1].split(",")]
    for j in range(max(want) + 1):
        lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
        R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
        wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
        if j not in want: continue
        v1 = sdp_rv(wv, wr, N, tf, om, dl)[0]
        v2, st = bound(wv, wr)
        m = float('nan')
        print(f"N={N} j={j}: order-1 Shor={v1:.6e}  order-2 Lasserre={v2:.6e} ({st})  NLP={m:.6e}", flush=True)
