"""proof-sdp: stress-matrix certificate (math/08 Thm 2.1). Given a genuine configuration (b_1..b_{N-1}, d_0..d_{N-1}),
recover KKT multipliers (lambda>=0 on active constraints, mu free on norms) by bounded least squares, build
Q = C_ext + diag(mu) - 1/2 sum lambda_e (E_ij+E_ji) and return its eigenvalues.
Q >= 0 (and small stationarity residual) certifies global optimality for the lifted (SDP) AND genuine problem."""
import numpy as np
from scipy.optimize import lsq_linear
from dimtest import weights

def stress(Bs, Ds, wv, wr, N, tf, om, dl, a1=5.0, act_tol=1e-6):
    h, cv, cr = weights(N, tf, a1); n = Bs.shape[1]; e0 = np.zeros(n); e0[0] = 1
    W = np.zeros((2, n)); W[0, :3] = wv; W[1, :3] = wr
    nbi = N - 1; m = nbi + N
    Z = np.vstack([Bs[1:N], Ds])                     # variables: b_1..b_{N-1}, d_0..d_{N-1}
    bi = lambda k: None if k in (0, N) else k - 1     # index of b_k among variables (None = constant e0)
    di = lambda k: nbi + k
    V = cv @ Ds - W[0]; R = cr @ Ds - W[1]
    grad = np.zeros((m, n))
    for k in range(N): grad[di(k)] = 2 * (cv[k] * V + cr[k] * R)
    cons = []   # (i, j or None, c): <z_i, z_j or e0> >= c
    for k in range(N):
        cons.append((bi(k), bi(k + 1), np.cos(om * h))); cons.append((di(k), bi(k), np.cos(dl))); cons.append((di(k), bi(k + 1), np.cos(dl)))
    vec = lambda i: e0 if i is None else Z[i]
    act = []
    for (i, j, c) in cons:
        if i is None and j is None: continue
        if i is None: i, j = j, None
        if vec(i) @ vec(j) - c < act_tol: act.append((i, j, c))
    # unknowns: lambda (len act) >= 0, mu (m) free. Stationarity: grad - sum lam dh + 2 mu z = 0
    cols = []
    for (i, j, c) in act:
        g = np.zeros((m, n)); g[i] -= vec(j)
        if j is not None: g[j] -= vec(i)
        cols.append(g.ravel())
    for i in range(m):
        g = np.zeros((m, n)); g[i] = 2 * Z[i]; cols.append(g.ravel())
    A = np.array(cols).T; lb = np.r_[np.zeros(len(act)), -np.inf * np.ones(m)]
    sol = lsq_linear(A, -grad.ravel(), bounds=(lb, np.inf * np.ones(len(lb))), lsmr_tol='auto', tol=1e-14)
    lam, mu = sol.x[:len(act)], sol.x[len(act):]
    res = np.linalg.norm(A @ sol.x + grad.ravel()) / max(np.linalg.norm(grad), 1e-12)
    C = np.zeros((m, m)); C[nbi:, nbi:] = np.outer(cv, cv) + np.outer(cr, cr)
    Q = C + np.diag(mu)
    for (i, j, c), l in zip(act, lam):
        if j is not None: Q[i, j] -= l / 2; Q[j, i] -= l / 2
    ev, U = np.linalg.eigh(Q)
    return ev, U, res, lam, mu, act
