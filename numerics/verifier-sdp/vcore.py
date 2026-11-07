"""[verifier-sdp] Independent implementation of the degree-2 Gram/Shor SDP for fixed-thrust 5DOF
min-landing-error, plus a genuine-trajectory upper bound (multistart ipopt + rank-3 rounding + polish).

Problem (discrete, fixed thrust, delta = 0 unless a gimbal variant is used):
    b_0 = e_z (fixed), b_N = e_z (fixed, optional), b_k in S^2,
    <b_k, b_{k+1}> >= c := cos(omega*dt)  for k = 0..N-1,
    readout  Y_l = sum_k gamma[k, l] b_k  (l = 0: position, l = 1: velocity; thrust part only;
             r0, v0 and gravity are absorbed into the target Q),
    cost     J = sum_l mu_l || Y_l - Q_l ||^2.
Everything is isotropic (C_k = gamma_k (x) I_3), so the cost is affine in the Gram matrix of
(b_free..., e_x, e_y, e_z).  The SDP variable is that Gram matrix Z (size n+3), with Z[e,e] = I_3,
Z_kk = 1, rate constraints on the superdiagonal, b_0 and b_N substituted as the constant e_z.
A Gram matrix of rank exactly 3 means every b_k lies in span(e) -> genuine 3-D trajectory.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import cvxpy as cp
import casadi as ca

EZ = np.array([0.0, 0.0, 1.0])


# ----------------------------------------------------------------------------------------------
# Problem data
# ----------------------------------------------------------------------------------------------
class Prob:
    """Weights gamma[k, l] for k = 0..N (row N unused under ZOH)."""

    def __init__(self, N, tf, omega, accel=None, scheme="zoh", terminal=True, readout="r", mu_v=1.0):
        self.N, self.tf, self.omega = N, tf, omega
        self.dt = tf / N
        self.c = np.cos(min(omega * self.dt, np.pi))
        a = np.ones(N + 1) if accel is None else np.asarray(accel, float)
        self.a = a
        t = np.arange(N + 1) * self.dt
        gw = np.zeros(N + 1)
        gr = np.zeros(N + 1)
        if scheme == "zoh":            # b_k held on [t_k, t_k+1), k < N
            gw[:N] = a[:N] * self.dt
            gr[:N] = a[:N] * self.dt * (tf - t[:N] - self.dt / 2)
        elif scheme == "trap":         # trapezoidal quadrature of the acceleration (b_N enters)
            w = np.full(N + 1, self.dt); w[0] = w[-1] = self.dt / 2
            gw = a * w
            gr = a * w * (tf - t)
        else:
            raise ValueError(scheme)
        self.scheme, self.terminal, self.readout = scheme, terminal, readout
        if readout == "r":
            self.gamma = gr[:, None]; self.mu = np.array([1.0])
        elif readout == "v":
            self.gamma = gw[:, None]; self.mu = np.array([1.0])
        elif readout == "rv":
            self.gamma = np.stack([gr, gw], 1); self.mu = np.array([1.0, mu_v])
        else:
            raise ValueError(readout)
        self.p = self.gamma.shape[1]
        # free indices
        self.free = list(range(1, N)) if terminal else list(range(1, N + 1))
        self.fixed = [0, N] if terminal else [0]
        self.n = len(self.free)
        self.scale2 = float(np.sum(self.mu * np.sum(np.abs(self.gamma), 0) ** 2))

    # readout of a full 3-D chain B (N+1, 3)
    def readout_of(self, B):
        return self.gamma.T @ B           # (p, 3)

    def cost_of(self, B, Q):
        Y = self.readout_of(B)
        return float(np.sum(self.mu[:, None] * (Y - Q) ** 2))

    def full_chain(self, Bfree):
        B = np.zeros((self.N + 1, 3))
        for k in self.fixed:
            B[k] = EZ
        B[self.free] = Bfree
        return B

    def feas_viol(self, B):
        nrm = np.abs(np.linalg.norm(B, axis=1) - 1).max()
        dots = np.sum(B[:-1] * B[1:], 1)
        rate = max(0.0, (self.c - dots).max())
        bc = max(np.linalg.norm(B[k] - EZ) for k in self.fixed)
        return max(nrm, rate, bc)

    # Theorem-B extreme arc (tent) in horizontal direction u, tilt phi_k
    def tent_phi(self):
        k = np.arange(self.N + 1)
        if self.terminal:
            return np.minimum(k, self.N - k) * self.omega * self.dt
        return k * self.omega * self.dt

    def extreme_arc(self, psi):
        phi = np.minimum(self.tent_phi(), np.pi)
        u = np.array([np.cos(psi), np.sin(psi), 0.0])
        return np.sin(phi)[:, None] * u[None, :] + np.cos(phi)[:, None] * EZ[None, :]

    def midpoint_M(self):
        return 0.5 * (self.readout_of(self.extreme_arc(0.0)) + self.readout_of(self.extreme_arc(np.pi)))


# ----------------------------------------------------------------------------------------------
# SDP (Gram form)
# ----------------------------------------------------------------------------------------------
def build_sdp(P, extra=None):
    """Returns (problem, Z, Qparam).  Q is a cvxpy Parameter of shape (p, 3)."""
    n = P.n
    Z = cp.Variable((n + 3, n + 3), symmetric=True)
    Qp = cp.Parameter((P.p, 3))
    G = Z[:n, :n]
    X = Z[:n, n:]                      # first moments x_k = <b_k, e_j>
    cons = [Z >> 0, Z[n:, n:] == np.eye(3), cp.diag(G) == 1]
    # rate constraints along the chain 0..N
    idx = {k: i for i, k in enumerate(P.free)}

    def inner(j, k):                  # <b_j, b_k> as affine expression
        jf, kf = j in idx, k in idx
        if jf and kf:
            return Z[idx[j], idx[k]]
        if jf:
            return X[idx[j], 2]
        if kf:
            return X[idx[k], 2]
        return 1.0
    for k in range(P.N):
        e = inner(k, k + 1)
        if not isinstance(e, float):
            cons.append(e >= P.c)
    # cost
    gF = P.gamma[P.free]               # (n, p)
    yfix = sum(np.outer(P.gamma[k], EZ) for k in P.fixed)   # (p, 3)
    obj = 0
    for l in range(P.p):
        g = gF[:, l]
        d = yfix[l] - Qp[l]           # affine in parameter
        obj = obj + P.mu[l] * (g @ G @ g + 2 * g @ X @ d + cp.sum_squares(d))
    if extra is not None:
        cons += extra(P, Z, X, G, inner)
    prob = cp.Problem(cp.Minimize(obj), cons)
    return prob, Z, Qp


def solve_sdp(P, Q, solver="CLARABEL", tight=True, built=None, extra=None):
    """Clarabel: tol 1e-9 (1e-10 is below its attainable accuracy here -> 'inaccurate'); falls back
    to 1e-8 if needed.  Status is returned verbatim; callers only accept 'optimal'."""
    prob, Z, Qp = built if built is not None else build_sdp(P, extra)
    Qp.value = np.asarray(Q, float).reshape(P.p, 3)
    ladder = [1e-9, 1e-8] if tight else [1e-7, 1e-6]
    st, val = None, np.nan
    for tol in ladder:
        if solver == "CLARABEL":
            kw = dict(tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500)
        elif solver == "SCS":
            kw = dict(eps_abs=tol, eps_rel=tol, max_iters=300000)
        else:
            kw = {}
        try:
            prob.solve(solver=solver, **kw)
        except cp.error.SolverError as e:
            st = "error"; continue
        st = prob.status
        if st == "optimal":
            break
    val = float(prob.value) if prob.value is not None else np.nan
    return dict(status=st, val=val, Z=Z.value, built=(prob, Z, Qp), tol=tol)


def sdp_diag(P, Zv, tol=1e-6):
    """eigenvalues, numerical rank, min eig, and 3-D-ness of the free vectors."""
    ev = np.linalg.eigvalsh((Zv + Zv.T) / 2)[::-1]
    rank = int(np.sum(ev > tol * max(ev[0], 1.0)))
    n = P.n
    X = Zv[:n, n:]
    G = Zv[:n, :n]
    perp = np.diag(G) - np.sum(X ** 2, 1)     # ||b_k - proj_e b_k||^2
    return dict(ev=ev, rank=rank, mineig=float(ev[-1]), perp_max=float(perp.max()),
                perp_sum=float(perp.sum()), X=X)


def slater_margin(P):
    """max t s.t. Z - t I >= 0 (on the free block), rate slack >= t.  t > 0 => Slater."""
    n = P.n
    Z = cp.Variable((n + 3, n + 3), symmetric=True)
    t = cp.Variable()
    X = Z[:n, n:]
    idx = {k: i for i, k in enumerate(P.free)}
    cons = [Z[n:, n:] == np.eye(3), cp.diag(Z[:n, :n]) == 1, t <= 1]
    M = np.zeros((n + 3, n + 3)); M[:n, :n] = np.eye(n)
    cons.append(Z - t * np.eye(n + 3) + t * np.diag([0] * n + [1, 1, 1]) >> 0)
    for k in range(P.N):
        j, kk = k, k + 1
        if j in idx and kk in idx:
            e = Z[idx[j], idx[kk]]
        elif j in idx:
            e = X[idx[j], 2]
        elif kk in idx:
            e = X[idx[kk], 2]
        else:
            continue
        cons.append(e - P.c >= t)
    pr = cp.Problem(cp.Maximize(t), cons)
    pr.solve(solver="CLARABEL")
    return float(t.value), pr.status


# ----------------------------------------------------------------------------------------------
# Genuine upper bound: ipopt NLP
# ----------------------------------------------------------------------------------------------
class GenuineNLP:
    def __init__(self, P, path_cons=None):
        self.P = P
        n = P.n
        x = ca.SX.sym("x", 3 * n)
        q = ca.SX.sym("q", 3 * P.p)
        Bf = ca.reshape(x, 3, n).T            # (n,3)
        rows = []
        fi = {k: i for i, k in enumerate(P.free)}
        for k in range(P.N + 1):
            rows.append(Bf[fi[k], :] if k in fi else ca.DM(EZ).T)
        B = ca.vertcat(*rows)                 # (N+1, 3)
        Y = ca.DM(P.gamma.T) @ B              # (p,3)
        Q = ca.reshape(q, 3, P.p).T
        f = 0
        for l in range(P.p):
            f += P.mu[l] * ca.sumsqr(Y[l, :] - Q[l, :])
        g, lbg, ubg = [], [], []
        for i in range(n):
            g.append(ca.sumsqr(Bf[i, :])); lbg.append(1.0); ubg.append(1.0)
        for k in range(P.N):
            if k in fi or (k + 1) in fi:
                g.append(ca.dot(B[k, :], B[k + 1, :])); lbg.append(P.c); ubg.append(ca.inf)
        if path_cons is not None:
            gg, lb, ub = path_cons(P, B)
            g += gg; lbg += lb; ubg += ub
        self.lbg, self.ubg = lbg, ubg
        nlp = {"x": x, "p": q, "f": f, "g": ca.vertcat(*g)}
        opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.tol": 1e-12,
                "ipopt.constr_viol_tol": 1e-11, "ipopt.max_iter": 3000, "ipopt.sb": "yes",
                "ipopt.acceptable_tol": 1e-9, "ipopt.mu_strategy": "adaptive"}
        self.S = ca.nlpsol("S", "ipopt", nlp, opts)

    def solve(self, Bfree0, Q):
        P = self.P
        r = self.S(x0=np.asarray(Bfree0).reshape(-1), p=np.asarray(Q).reshape(-1),
                   lbg=self.lbg, ubg=self.ubg)
        Bf = np.array(r["x"]).reshape(P.n, 3)
        B = P.full_chain(Bf)
        # project to exact unit norm and re-evaluate (no cheating with norm slack)
        Bn = B / np.linalg.norm(B, axis=1, keepdims=True)
        viol = P.feas_viol(Bn)
        ok = self.S.stats()["success"] or viol < 1e-8
        return dict(f=P.cost_of(Bn, Q), B=Bn, viol=viol, ok=ok,
                    status=self.S.stats()["return_status"])


def random_starts(P, rng, m):
    """Mixed initial guesses: tilted tents with random azimuth/amplitude, smooth random curves, noise."""
    out = []
    phi0 = P.tent_phi()
    for j in range(m):
        kind = j % 4
        if kind == 0:
            s = rng.uniform(0.2, 1.0)
            psi = rng.uniform(0, 2 * np.pi)
            phi = s * phi0
            u = np.array([np.cos(psi), np.sin(psi), 0])
            B = np.sin(phi)[:, None] * u + np.cos(phi)[:, None] * EZ
        elif kind == 1:   # azimuth sweeping (coning) curve
            s = rng.uniform(0.2, 1.0)
            psi = rng.uniform(0, 2 * np.pi) + rng.uniform(-3, 3) * np.linspace(0, 1, P.N + 1) * np.pi
            phi = s * phi0
            B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
        elif kind == 2:   # smooth random
            K = 4
            t = np.linspace(0, 1, P.N + 1)
            B = np.zeros((P.N + 1, 3)); B[:, 2] = 1
            for d in range(2):
                coef = rng.normal(size=K) * 0.6
                B[:, d] = sum(coef[i] * np.sin((i + 1) * np.pi * t) for i in range(K))
            B[:, 2] = np.abs(B[:, 2]) * rng.uniform(-0.3, 1)
        else:
            B = rng.normal(size=(P.N + 1, 3)) * 0.5 + EZ
        B = B / np.linalg.norm(B, axis=1, keepdims=True)
        out.append(B[P.free])
    return out


def round_from_Z(P, Zv, rng, nrand=4):
    """Rank-3 projections of the SDP solution."""
    n = P.n
    ev, V = np.linalg.eigh((Zv + Zv.T) / 2)
    ev = np.clip(ev, 0, None)
    F = (V * np.sqrt(ev)).T          # columns are vectors in R^{n+3}
    Bv, E = F[:, :n], F[:, n:]       # E has orthonormal columns
    starts = []
    X = E.T @ Bv                     # 3 x n (first moments)
    starts.append(X.T.copy())
    # top-3 PCA of the b-vectors, Procrustes-aligned to X
    G = Zv[:n, :n]
    w, U = np.linalg.eigh(G)
    kk = min(3, n)
    B3 = U[:, -kk:] * np.sqrt(np.clip(w[-kk:], 0, None))
    Uu, _, Vt = np.linalg.svd(B3.T @ X.T, full_matrices=False)
    starts.append(B3 @ (Uu @ Vt))
    # random projections of the perpendicular part into span(e)
    Pperp = Bv - E @ X
    for _ in range(nrand):
        R = rng.normal(size=(3, Bv.shape[0])) / np.sqrt(max(1, Bv.shape[0] - 3))
        starts.append((X + R @ Pperp).T)
    out = []
    for S in starts:
        nr = np.linalg.norm(S, axis=1, keepdims=True)
        S = np.where(nr > 1e-9, S / np.maximum(nr, 1e-12), EZ)
        out.append(S)
    return out


def genuine_best(P, nlp, Q, rng, nstart=16, Zv=None, extra_starts=()):
    best = None
    starts = list(extra_starts)
    if Zv is not None:
        starts += round_from_Z(P, Zv, rng)
    starts += random_starts(P, rng, nstart)
    fs = []
    for s in starts:
        r = nlp.solve(s, Q)
        if r["viol"] < 1e-7:
            fs.append(r["f"])
            if best is None or r["f"] < best["f"]:
                best = r
    if best is None:
        return dict(f=np.inf, B=None, nfeas=0, fs=[])
    best["nfeas"] = len(fs)
    best["fs"] = sorted(fs)
    return best
