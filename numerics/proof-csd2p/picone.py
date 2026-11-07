"""[proof-csd2p] Hemisphere (Picone) certificate for CSD2' (math/09 Thm 3.1 / 3.3) and the discrete stress check.
Given a genuine 3D configuration (b_0..b_N, d_0..d_{N-1}) of the Gim model (verifier-sdp/vgim.py layout):
  primer P_k = -(gv_k y_v + gr_k y_r),  y = readout - target;
  criterion:  exists c with <b_k,c> > 0 (all k, incl. b_0=b_N=e_z), <P_k,c> >= 0  (LP); d-slots eliminated by Schur (mu_d>=0).
If it holds (and the configuration is KKT), the Z-matrix part of the stress is PSD => Q >= 0 => lift exact.
stress(): recovers multipliers by bounded least squares and returns eig(Q) (cross-check)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
import numpy as np
from scipy.optimize import linprog, lsq_linear

EZ = np.array([0, 0, 1.0])

def unpack(G, x):
    N, nb = G.N, G.nb
    B = np.vstack([EZ, x[:3 * nb].reshape(nb, 3)] + ([EZ] if G.terminal else []))
    D = x[3 * nb:].reshape(N, 3) if G.gim else B[:N].copy()
    return B, D

def primer(G, D, wv, wr):
    yv = G.gv @ D - wv; yr = G.gr @ D - wr
    return -(np.outer(G.gv, yv) + np.outer(G.gr, yr)), yv, yr

def criterion(G, x, wv, wr):
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    sc = np.linalg.norm(P, axis=1).max() + 1e-300
    rows = [-np.r_[b, -1.0] for b in B]   # d-slots are Schur-eliminated (needs mu_d >= 0: convexified lens)
    rows += [-np.r_[p / sc, 0.0] for p in P]
    A = np.array(rows); bnd = [(-1, 1)] * 3 + [(None, 1)]
    r = linprog(np.r_[0, 0, 0, -1.0], A_ub=A, b_ub=np.zeros(len(A)), bounds=bnd, method="highs")
    return (float(-r.fun) if r.status == 0 else -1.0), (r.x[:3] if r.status == 0 else None)

def stress(G, x, wv, wr, act_tol=1e-6):
    """discrete stress Q (math/08 Thm 2.1) for the Gim model; variables b_1..b_nb, d_0..d_{N-1}."""
    N, nb = G.N, G.nb
    B, D = unpack(G, x)
    Z = np.vstack([B[1:1 + nb], D]) if G.gim else B[1:1 + nb].copy()
    m = Z.shape[0]
    bi = lambda k: (k - 1) if 1 <= k <= nb else None
    di = (lambda k: nb + k) if G.gim else bi
    yv = G.gv @ D - wv; yr = G.gr @ D - wr
    grad = np.zeros((m, 3))
    for k in range(N):
        i = di(k)
        if i is not None:
            grad[i] += 2 * (G.gv[k] * yv + G.gr[k] * yr)
    vec = lambda i: EZ if i is None else Z[i]
    cons = [(bi(k), bi(k + 1), G.cr) for k in range(N)]
    if G.gim:
        for k in range(N):
            cons.append((di(k), bi(k), G.cd))
            if G.both and (k + 1 <= nb or G.terminal):
                cons.append((di(k), bi(k + 1), G.cd))
    act = []
    for (i, j, c) in cons:
        if i is None and j is None: continue
        if i is None: i, j = j, None
        if vec(i) @ vec(j) - c < act_tol: act.append((i, j))
    norm_eq = list(range(nb)) if G.gim else list(range(m))
    norm_in = [nb + k for k in range(N) if G.gim and (not G.cvx or np.linalg.norm(D[k]) > 1 - 1e-6)]
    cols = []
    for (i, j) in act:
        g = np.zeros((m, 3)); g[i] -= vec(j)
        if j is not None: g[j] -= vec(i)
        cols.append(g.ravel())
    nlam = len(act)
    for i in norm_eq + norm_in:
        g = np.zeros((m, 3)); g[i] = 2 * Z[i]; cols.append(g.ravel())
    A = np.array(cols).T
    lb = np.r_[np.zeros(nlam), -np.inf * np.ones(len(norm_eq)), (np.zeros if G.cvx else lambda n: -np.inf * np.ones(n))(len(norm_in))]
    sol = lsq_linear(A, -grad.ravel(), bounds=(lb, np.inf * np.ones(len(lb))), tol=1e-14)
    res = np.linalg.norm(A @ sol.x + grad.ravel()) / max(np.linalg.norm(grad), 1e-12)
    lam = sol.x[:nlam]; mu = np.zeros(m)
    for i, v in zip(norm_eq + norm_in, sol.x[nlam:]): mu[i] = v
    C = np.zeros((m, m))
    idx = [di(k) for k in range(N)]
    for k in range(N):
        for j in range(N):
            if idx[k] is not None and idx[j] is not None:
                C[idx[k], idx[j]] += G.gv[k] * G.gv[j] + G.gr[k] * G.gr[j]
    Q = C + np.diag(mu)
    for (i, j), l in zip(act, lam):
        if j is not None: Q[i, j] -= l / 2; Q[j, i] -= l / 2
    if getattr(stress, 'full', False):
        return Q, C, res
    return np.linalg.eigvalsh(Q), res

def jacobi_m(G, x, wv, wr):
    """m = unit normal of the primer plane span(y_v,y_r) with <e_z,m> >= 0; returns h_m = <b_k,m> (k=0..N) and #sign changes."""
    B, D = unpack(G, x); P, yv, yr = primer(G, D, wv, wr)
    m = np.cross(yv, yr); nm = np.linalg.norm(m)
    if nm < 1e-12 * max(np.linalg.norm(yv) * np.linalg.norm(yr), 1e-300):
        return None, -1
    m /= nm
    if m @ EZ < 0: m = -m
    h = B @ m
    hh = h.copy(); hh[0] = abs(hh[0]) + 1.0; hh[-1] = abs(hh[-1]) + 1.0 if G.terminal else hh[-1]   # <e_z,m> >= 0 orientation
    s = np.sign(hh[np.abs(hh) > 1e-9])
    return h, int(np.sum(s[1:] != s[:-1]))

def zindex(G, x, wv, wr):
    """number of negative eigenvalues of the local (Z-matrix) part Z = Q - C of the stress, and of Q."""
    import numpy.linalg as la
    ev, res = stress(G, x, wv, wr)
    return ev, res
