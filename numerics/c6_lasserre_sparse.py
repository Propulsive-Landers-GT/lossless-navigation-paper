"""Certify the CSD2 (Gram/Hilbert-sphere SDP) gap on a small instance with a VALID lower bound on the true 3D
minimum that is stronger than the Gram SDP:
  (L1c) coordinate order-1 Lasserre (full moment matrix in the 3D coordinates of all b_k, d_k; scalar
        localizing constraints) -- dominates the Gram SDP;
  (L2s) correlatively-sparse order-2 Lasserre: full order-1 moment matrix + order-2 moment matrices on the
        cliques C_k = {b_k, b_{k+1}, d_k} (k = 0..N-1) and C_D = {all d}, localizing order-1 matrices of the
        rate/gimbal inequalities on their cliques, and equality constraints multiplied by clique monomials
        of degree <= 2.  Every such relaxation is a valid lower bound on the 3D minimum.
If L > SDP_Gram, the Gram relaxation is certified strictly lossy: SDP_Gram < L <= min_3D.
Model = redteam-lift/sdp_clean.py (fixed thrust a1, tent b_0 = b_N = e_vert, inner discretization); coordinates
(vert, x, y).  Usage: .venv/bin/python c6_lasserre_sparse.py <json of candidates> <index> [order]
"""
import sys, json, itertools, time
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
sys.path.insert(0, "redteam-lift")
from sdp_clean import build

fn = sys.argv[1]; idx = int(sys.argv[2]); ORDER = int(sys.argv[3]) if len(sys.argv) > 3 else 2
DCLIQUE = not (len(sys.argv) > 4 and sys.argv[4] == "nod")   # 'nod': omit the order-2 block on {all d}
C = json.load(open(fn))[idx]
wv, wr = np.array(C["wv"]), np.array(C["wr"])
N = int(fn.split("_N")[1].split("_")[0]); a1 = float(fn.split("_a")[1].split(".json")[0])
tf, om, dl = 4.0, np.deg2rad(30), np.deg2rad(15); h = tf / N
nb = N - 1; nv = 3 * nb + 3 * N
bidx = lambda k: None if k in (0, N) else [3 * (k - 1) + i for i in range(3)]
didx = lambda k: [3 * nb + 3 * k + i for i in range(3)]


def padd(p, q, s=1.0):
    r = dict(p)
    for m, c in q.items():
        r[m] = r.get(m, 0.0) + s * c
    return r


def pmul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(sorted(m1 + m2)); r[m] = r.get(m, 0.0) + c1 * c2
    return r


const = lambda c: {(): float(c)}
var = lambda i: {(i,): 1.0}


def vec(k, kind):
    if kind == "b" and bidx(k) is None:
        return [const(1.0), const(0.0), const(0.0)]
    return [var(i) for i in (bidx(k) if kind == "b" else didx(k))]


def dot(u, v):
    r = {}
    for a, b in zip(u, v):
        r = padd(r, pmul(a, b))
    return r


def vars_of(p):
    return sorted({i for m in p for i in m})


eqs = [padd(dot(vec(k, "b"), vec(k, "b")), const(-1)) for k in range(1, N)] + \
      [padd(dot(vec(k, "d"), vec(k, "d")), const(-1)) for k in range(N)]
ineqs = [padd(dot(vec(k, "b"), vec(k + 1, "b")), const(-np.cos(om * h))) for k in range(N)] + \
        [padd(dot(vec(k, "d"), vec(k, "b")), const(-np.cos(dl))) for k in range(N)] + \
        [padd(dot(vec(k, "d"), vec(k + 1, "b")), const(-np.cos(dl))) for k in range(N)]
cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
obj = {}
for c, w in ((cv, wv), (cr, wr)):
    for i in range(3):
        e = const(-w[i])
        for k in range(N):
            e = padd(e, {(didx(k)[i],): c[k]})
        obj = padd(obj, pmul(e, e))

cliques = []
for k in range(N):
    cl = []
    for kk in (k, k + 1):
        if bidx(kk) is not None:
            cl += bidx(kk)
    cliques.append(sorted(cl + didx(k)))
if DCLIQUE:
    cliques.append(sorted(sum([didx(k) for k in range(N)], [])))


def mons(vs, d):
    return [()] + [tuple(c) for k in range(1, d + 1) for c in itertools.combinations_with_replacement(vs, k)]


# collect all monomials needed
allv = list(range(nv))
B1 = mons(allv, 1)
need = set(tuple(sorted(a + b)) for a in B1 for b in B1)
Bc2 = [mons(cl, 2) for cl in cliques] if ORDER >= 2 else []
Bc1 = [mons(cl, 1) for cl in cliques]
for B in Bc2:
    need |= set(tuple(sorted(a + b)) for a in B for b in B)
need |= set(obj.keys())
yid = {m: i for i, m in enumerate(sorted(need, key=lambda m: (len(m), m)))}
ny = len(yid)
y = cp.Variable(ny)
print(f"N={N} a1={a1} nv={nv} order={ORDER}: #moments={ny}", flush=True)


def linrow(p):
    r = np.zeros(ny)
    for m, c in p.items():
        if m not in yid:
            return None
        r[yid[m]] += c
    return r


def lin(p):
    rows, vals = [], []
    for m, c in p.items():
        if m not in yid:
            return None
        rows.append(yid[m]); vals.append(c)
    return sp.csr_matrix((vals, ([0] * len(rows), rows)), shape=(1, ny)) @ y


def momat(basis, g):
    n = len(basis); R, Cc, V = [], [], []
    for i, mi in enumerate(basis):
        for j, mj in enumerate(basis):
            for m, c in pmul(pmul({mi: 1.0}, {mj: 1.0}), g).items():
                if m not in yid:
                    return None
                R.append(i * n + j); Cc.append(yid[m]); V.append(c)
    A = sp.csr_matrix((V, (R, Cc)), shape=(n * n, ny))
    M = cp.reshape(A @ y, (n, n), order="C")
    PSDOPS.append((A, n))
    return 0.5 * (M + M.T)


PSDOPS = []


PSDCONS = []
_M = momat(B1, const(1.0)); PSDCONS.append((_M >> 0, len(PSDOPS) - 1)); cons = [PSDCONS[-1][0]]
EQ = [linrow(const(1.0))]; EQb = [1.0]
for g in eqs:
    EQ.append(linrow(g)); EQb.append(0.0)
    if ORDER >= 2:
        gv = set(vars_of(g))
        for cl, B in zip(cliques, Bc2):
            if gv <= set(cl):
                for m in B:
                    e = linrow(pmul({m: 1.0}, g))
                    if e is not None:
                        EQ.append(e); EQb.append(0.0)
for g in ineqs:
    cons.append(lin(g) >= 0)
    if ORDER >= 2:
        gv = set(vars_of(g))
        for cl, B in zip(cliques, Bc1):
            if gv <= set(cl):
                M = momat(B, g)
                if M is not None:
                    PSDCONS.append((M >> 0, len(PSDOPS) - 1)); cons.append(PSDCONS[-1][0])
                break
for B in Bc2:
    _M = momat(B, const(1.0)); PSDCONS.append((_M >> 0, len(PSDOPS) - 1)); cons.append(PSDCONS[-1][0])
# remove linearly dependent equality rows (rank-revealing QR), which otherwise make the KKT system singular
import scipy.linalg as sla
A = np.array(EQ); bvec = np.array(EQb)
Q, Rq, piv = sla.qr(A.T, mode="economic", pivoting=True)
rk = int(np.sum(np.abs(np.diag(Rq)) > 1e-9 * abs(Rq[0, 0])))
keep = np.sort(piv[:rk])
print(f"equalities: {len(EQ)} rows, rank {rk}", flush=True)
EQCON = sp.csr_matrix(A[keep]) @ y == bvec[keep]; cons.append(EQCON); Aeq = A[keep]; beq = bvec[keep]
cons += [y >= -1, y <= 1]   # valid for genuine measures: every coordinate of a unit vector is in [-1, 1]
pr = cp.Problem(cp.Minimize(lin(obj)), cons)
t0 = time.time()
try:
    pr.solve(solver=cp.CLARABEL, max_iter=400)
except cp.error.SolverError:
    print("Clarabel failed; trying SCS", flush=True)
    pr.solve(solver=cp.SCS, eps_abs=1e-9, eps_rel=1e-9, max_iters=1000000)
# ---- safe (rigorous) lower bound from the approximate dual:  for any lambda, PSD Z_j:
#   c.y = b.lambda + sum_j <Z_j, M_j(y)> + r.y,  r = c - Aeq^T lambda - sum_j M_j^*(Z_j);  with |y| <= 1 and M_j(y) PSD:
#   c.y >= b.lambda - |r|_1   (valid for every feasible y, hence a lower bound on the relaxation and on min_3D)
cvec = np.zeros(ny)
for m, cc in obj.items():
    cvec[yid[m]] += cc
lam = np.asarray(EQCON.dual_value).ravel()
best_safe = -np.inf
for sgn in (1.0, -1.0):
    r = cvec - sgn * Aeq.T @ lam
    for con, k in PSDCONS:
        Z = np.asarray(con.dual_value); Z = 0.5 * (Z + Z.T)
        w, U = np.linalg.eigh(Z); Z = (U * np.maximum(w, 0)) @ U.T     # project onto PSD cone
        Aop, n = PSDOPS[k]
        r = r - Aop.T @ Z.reshape(-1)        # M(y) = reshape(A y) (row-major); <Z, M(y)> = (A^T vec(Z)).y
    safe = sgn * beq @ lam - np.sum(np.abs(r))
    print(f"safe dual bound (sign {sgn:+.0f}): {safe:.8e}   (|r|_1 = {np.sum(np.abs(r)):.2e})", flush=True)
    best_safe = max(best_safe, safe)
G, gc, gobj = build(wv, wr, N, tf, om, dl, a1=a1)
pg = cp.Problem(cp.Minimize(gobj), gc); pg.solve(solver=cp.CLARABEL, tol_gap_abs=1e-11, tol_gap_rel=1e-11, tol_feas=1e-11)
print(f"Gram SDP (CSD2) = {pg.value:.8e}; Lasserre lower bound = {pr.value:.8e} ({pr.status}, {time.time() - t0:.0f}s); "
      f"3D NLP = {C['nlp']:.8e}", flush=True)
print(f"RIGOROUS safe bound = {best_safe:.8e}  vs Gram SDP {pg.value:.8e}  => " +
      (f"CERTIFIED CSD2 gap >= {best_safe - pg.value:.4e}" if best_safe > pg.value else "not certified by the safe bound"), flush=True)
json.dump(dict(instance=C, N=N, a1=a1, order=ORDER, gram=float(pg.value), lasserre=float(pr.value), status=pr.status, safe_bound=float(best_safe)),
          open(f"results/c6_lasserre_N{N}_i{idx}_o{ORDER}{'' if DCLIQUE else '_nod'}.json", "w"), indent=1)
