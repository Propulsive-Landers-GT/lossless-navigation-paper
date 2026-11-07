"""[verifier-sdp] Builders for the extension QCQPs (full Shor via vqcqp)."""
import numpy as np
from vqcqp import QCQP, qf, qadd, lin, prod

EZ = np.array([0.0, 0.0, 1.0])


class Vec:
    """affine 3-vector v = A z + a0."""
    def __init__(self, A, a0):
        self.A, self.a0 = np.asarray(A, float), np.asarray(a0, float)

    def __add__(self, o): return Vec(self.A + o.A, self.a0 + o.a0)
    def __mul__(self, s): return Vec(self.A * s, self.a0 * s)
    __rmul__ = __mul__
    def comp(self, i): return lin(self.A.shape[1], self.A[i], self.a0[i])


def vdot(v, w):
    Q = 0.5 * (v.A.T @ w.A + w.A.T @ v.A)
    q = 0.5 * (v.A.T @ w.a0 + w.A.T @ v.a0)
    return (Q, q, float(v.a0 @ w.a0))


def vconst(m, a):
    return Vec(np.zeros((3, m)), a)


def vvar(m, i0):
    A = np.zeros((3, m)); A[:, i0:i0 + 3] = np.eye(3)
    return Vec(A, np.zeros(3))


def sq_err(vs_by_l, Q, mu):
    """sum_l mu_l ||v_l - Q_l||^2 ; vs_by_l is a list of Vec."""
    fs = []
    for l, v in enumerate(vs_by_l):
        d = v + vconst(v.A.shape[1], -np.asarray(Q[l]))
        fs.append(vdot(d, d))
    return qadd(*fs, w=list(mu))


def weights(N, tf, accel=None):
    dt = tf / N
    a = np.ones(N) if accel is None else np.asarray(accel, float)[:N]
    t = np.arange(N) * dt
    gw = a * dt
    gr = a * dt * (tf - t - dt / 2)
    return gr, gw, dt


# ------------------------------------------------------------------ fixed thrust (+ gimbal)
def fixed_thrust(N, tf, omega, Q, readout="rv", terminal=True, delta=None, accel=None, mu=(1.0, 1.0),
                 path=None, both=False):
    """ZOH: b_k on [t_k,t_k+1), k=0..N-1; b_0 = e_z; terminal => b_N = e_z (only via rate).
    delta=None: thrust along b.  delta>0: thrust direction d_k with <d_k,b_k> >= cos(delta).
    path: callable(m, thrust_vecs, b_vecs) -> list of extra (Q,q,c,kind) constraints + convex_z fn."""
    gr, gw, dt = weights(N, tf, accel)
    c = np.cos(min(omega * dt, np.pi))
    nb = N - 1 if terminal else N            # free b's: 1..N-1 (or 1..N)
    nd = N if delta is not None else 0
    m = 3 * nb + 3 * nd
    b = [vconst(m, EZ)] + [vvar(m, 3 * i) for i in range(nb)]
    if terminal:
        b.append(vconst(m, EZ))
    cons = []
    for i in range(1, nb + 1):
        Qn, qn, cn = vdot(b[i], b[i]); cons.append((Qn, qn, cn - 1.0, "=="))
    for k in range(N):
        if (1 <= k <= nb) or (1 <= k + 1 <= nb):
            Qr, qr, cr = vdot(b[k], b[k + 1]); cons.append((Qr, qr, cr - c, ">="))
    if delta is not None:
        d = [vvar(m, 3 * nb + 3 * k) for k in range(N)]
        cd = np.cos(delta)
        for k in range(N):
            Qn, qn, cn = vdot(d[k], d[k]); cons.append((Qn, qn, cn - 1.0, "=="))
            Qg, qg, cg = vdot(d[k], b[k]); cons.append((Qg, qg, cg - cd, ">="))
            if both and k + 1 < len(b):   # 'inner' discretization: d_k within delta of b_k AND b_{k+1}
                Qg, qg, cg = vdot(d[k], b[k + 1]); cons.append((Qg, qg, cg - cd, ">="))
        th = d
    else:
        th = b[:N]
    R = sum((th[k] * gr[k] for k in range(1, N)), th[0] * gr[0])
    V = sum((th[k] * gw[k] for k in range(1, N)), th[0] * gw[0])
    vs = {"r": [R], "v": [V], "rv": [R, V]}[readout]
    obj = sq_err(vs, Q, mu[:len(vs)])
    convex_z = None
    if path is not None:
        extra, convex_z = path(m, th, b, dt)
        cons += extra
    P = QCQP(m, obj, cons, convex_z=convex_z)
    P.info = dict(m=m, nb=nb, nd=nd, gr=gr, gw=gw, c=c, dt=dt, readout=readout, terminal=terminal)
    return P


def starts_fixed(P, N, rng, k, delta=None, omega=1.0, extra=()):
    """random genuine-ish starting points in z-space."""
    info = P.info
    out = list(extra)
    dt = info["dt"]
    for j in range(k):
        s = rng.uniform(0.1, 1.0); psi0 = rng.uniform(0, 2 * np.pi)
        sweep = rng.uniform(-3, 3) * (j % 2)
        kk = np.arange(N + 1)
        phi = s * (np.minimum(kk, N - kk) if info["terminal"] else kk) * omega * dt
        phi = np.minimum(phi, np.pi)
        psi = psi0 + sweep * np.linspace(0, np.pi, N + 1)
        B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
        B += 0.05 * rng.normal(size=B.shape)
        B /= np.linalg.norm(B, axis=1, keepdims=True)
        z = list(B[1:1 + info["nb"]].ravel())
        if info["nd"]:
            D = B[:N] + 0.3 * np.sin(delta) * rng.normal(size=(N, 3))
            D /= np.linalg.norm(D, axis=1, keepdims=True)
            z += list(D.ravel())
        out.append(np.array(z))
    return out


# ------------------------------------------------------------------ variable throttle
def throttle(N, tf, omega, Q, a1, a2, readout="rv", terminal=True, mu=(1.0, 1.0), rlt=True,
             objective="error", eps=None, landing="lifted"):
    """z = (a_0..a_{N-1}, U_1..U_{N-1});  U_0 = a_0 e_z.  U_k = a_k b_k, ||U_k||^2 = a_k^2.
    objective='error': min ||readout - Q||^2.  objective='fuel': min sum a_k dt subject to landing:
      landing='linear'  -> readout(first moments) == Q (6 or 3 linear equalities)
      landing='lifted'  -> lifted ||readout - Q||^2 <= eps.
    """
    dt = tf / N
    t = np.arange(N) * dt
    gr = dt * (tf - t - dt / 2); gw = dt * np.ones(N)
    c = np.cos(min(omega * dt, np.pi))
    m = N + 3 * (N - 1)
    A = [lin(m, np.eye(m)[k]) for k in range(N)]
    U = []
    for k in range(N):
        if k == 0:
            Am = np.zeros((3, m)); Am[2, 0] = 1.0; U.append(Vec(Am, np.zeros(3)))
        else:
            U.append(vvar(m, N + 3 * (k - 1)))
    cons = []
    for k in range(N):
        lo = qadd(A[k], lin(m, np.zeros(m), -a1)); hi = qadd(lin(m, np.zeros(m), a2), A[k], w=[1, -1])
        cons += [(*lo, ">="), (*hi, ">="), (*prod(lo, hi), ">=")]
        if k >= 1:
            Qn, qn, cn = qadd(vdot(U[k], U[k]), prod(A[k], A[k]), w=[1, -1]); cons.append((Qn, qn, cn, "=="))
    for k in range(N - 1):
        f = qadd(vdot(U[k], U[k + 1]), prod(A[k], A[k + 1]), w=[1, -c]); cons.append((*f, ">="))
    if terminal:      # b_N = e_z:  U_{N-1}.e_z >= c a_{N-1}
        f = qadd(U[N - 1].comp(2), A[N - 1], w=[1, -c]); cons.append((*f, ">="))
    if rlt:
        for j in range(N):
            for k in range(j + 1, N):
                lj = qadd(A[j], lin(m, np.zeros(m), -a1)); hj = qadd(lin(m, np.zeros(m), a2), A[j], w=[1, -1])
                lk = qadd(A[k], lin(m, np.zeros(m), -a1)); hk = qadd(lin(m, np.zeros(m), a2), A[k], w=[1, -1])
                for f in (prod(lj, lk), prod(hj, hk), prod(lj, hk), prod(hj, lk)):
                    cons.append((*f, ">="))
    R = sum((U[k] * gr[k] for k in range(1, N)), U[0] * gr[0])
    V = sum((U[k] * gw[k] for k in range(1, N)), U[0] * gw[0])
    vs = {"r": [R], "v": [V], "rv": [R, V]}[readout]
    err = sq_err(vs, Q, mu[:len(vs)])

    import cvxpy as cp

    def convex_z(z):            # ||U_k|| <= a_k on first moments (valid)
        out = []
        for k in range(1, N):
            out.append(cp.norm(z[N + 3 * (k - 1): N + 3 * k]) <= z[k])
        return out
    if objective == "error":
        obj = err
    else:
        obj = lin(m, np.r_[np.full(N, dt), np.zeros(3 * (N - 1))])
        if landing == "linear":
            for l, v in enumerate(vs):
                for i in range(3):
                    f = qadd(v.comp(i), lin(m, np.zeros(m), -Q[l][i])); cons.append((*f, "=="))
        else:
            f = qadd(lin(m, np.zeros(m), eps), err, w=[1, -1]); cons.append((*f, ">="))
    P = QCQP(m, obj, cons, convex_z=convex_z)
    P.info = dict(m=m, N=N, c=c, dt=dt, gr=gr, gw=gw, a1=a1, a2=a2, terminal=terminal, err=err)
    return P


def starts_throttle(P, rng, k, omega, extra=()):
    info = P.info; N = info["N"]; dt = info["dt"]
    out = list(extra)
    for j in range(k):
        s = rng.uniform(0.1, 1.0); psi0 = rng.uniform(0, 2 * np.pi); sweep = rng.uniform(-3, 3) * (j % 2)
        kk = np.arange(N + 1)
        phi = s * (np.minimum(kk, N - kk) if info["terminal"] else kk) * omega * dt
        phi = np.minimum(phi, np.pi)
        psi = psi0 + sweep * np.linspace(0, np.pi, N + 1)
        B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)[:N]
        a = rng.uniform(info["a1"], info["a2"], N) if j % 3 else np.full(N, rng.choice([info["a1"], info["a2"]]))
        Uv = (a[:, None] * B)[1:]
        out.append(np.r_[a, Uv.ravel()])
    return out


# ------------------------------------------------------------------ throttle, Hilbert (U,b) lift
def throttle_ub_sdp(N, tf, omega, Q, a1, a2, readout="rv", terminal=True, mu=(1.0, 1.0), solver="CLARABEL"):
    """Gram of (U_0..U_{N-1}, b_1..b_{N-1}[..b_N], e1,e2,e3).  Constraints (all linear in the Gram):
    ||b_k||=1, <b_k,b_{k+1}> >= c, s_k := <U_k,b_k> in [a1,a2], ||U_k||^2 <= (a1+a2) s_k - a1 a2.
    Genuine U_k = a_k b_k satisfies them with equality in the last one."""
    import cvxpy as cp
    dt = tf / N; t = np.arange(N) * dt
    gr = dt * (tf - t - dt / 2); gw = dt * np.ones(N)
    c = np.cos(min(omega * dt, np.pi))
    nb = N - 1 if terminal else N
    n = N + nb
    Z = cp.Variable((n + 3, n + 3), symmetric=True)
    iU = lambda k: k
    ib = lambda k: N + k - 1            # b_k, k=1..nb
    ie = lambda j: n + j
    cons = [Z >> 0, Z[n:, n:] == np.eye(3)]

    def bb(j, k):   # <b_j,b_k>, b_0 = e_z, b_N = e_z if terminal
        fj = 1 <= j <= nb; fk = 1 <= k <= nb
        if fj and fk: return Z[ib(j), ib(k)]
        if fj: return Z[ib(j), ie(2)]
        if fk: return Z[ib(k), ie(2)]
        return 1.0

    def ub(k):      # <U_k, b_k>
        return Z[iU(k), ib(k)] if 1 <= k <= nb else Z[iU(k), ie(2)]
    for k in range(1, nb + 1):
        cons.append(Z[ib(k), ib(k)] == 1)
    for k in range(N):
        e = bb(k, k + 1)
        if not isinstance(e, float):
            cons.append(e >= c)
    for k in range(N):
        s = ub(k)
        cons += [s >= a1, s <= a2, Z[iU(k), iU(k)] <= (a1 + a2) * s - a1 * a2]
    G = Z[:N, :N]; X = Z[:N, n:]
    gl = {"r": [gr], "v": [gw], "rv": [gr, gw]}[readout]
    obj = 0
    for l, g in enumerate(gl):
        obj = obj + mu[l] * (g @ G @ g - 2 * g @ X @ np.asarray(Q[l]) + float(np.sum(np.asarray(Q[l]) ** 2)))
    pr = cp.Problem(cp.Minimize(obj), cons)
    pr.solve(solver=solver, tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9) if solver == "CLARABEL" else pr.solve(solver=solver, eps_abs=1e-8, eps_rel=1e-8, max_iters=200000)
    Zv = Z.value
    ev = np.linalg.eigvalsh(Zv)[::-1]
    return dict(val=float(pr.value), status=pr.status, rank=int(np.sum(ev > 1e-6 * ev[0])), ev=ev, Z=Zv)


def throttle_full(N, tf, omega, Q, a1, a2, readout="rv", terminal=True, mu=(1.0, 1.0)):
    """Tightest natural degree-2 Shor: z = (a_k, U_k (k>=1), b_k (k=1..nb)).
    U_k - a_k b_k = 0 (3 quadratic equalities), ||b||=1, rate on b, ||U||^2 = a^2, U.U' >= c a a',
    a bounds + all pairwise RLT, ||U_k|| <= a_k (SOC), terminal via b."""
    dt = tf / N; t = np.arange(N) * dt
    gr = dt * (tf - t - dt / 2); gw = dt * np.ones(N)
    c = np.cos(min(omega * dt, np.pi))
    nb = N - 1 if terminal else N
    m = N + 3 * (N - 1) + 3 * nb
    A = [lin(m, np.eye(m)[k]) for k in range(N)]
    U = []
    for k in range(N):
        if k == 0:
            Am = np.zeros((3, m)); Am[2, 0] = 1.0; U.append(Vec(Am, np.zeros(3)))
        else:
            U.append(vvar(m, N + 3 * (k - 1)))
    o = N + 3 * (N - 1)
    b = [vconst(m, EZ)] + [vvar(m, o + 3 * (k - 1)) for k in range(1, nb + 1)]
    if terminal:
        b.append(vconst(m, EZ))
    cons = []
    one = lambda v: lin(m, np.zeros(m), v)
    for k in range(N):
        lo = qadd(A[k], one(-a1)); hi = qadd(one(a2), A[k], w=[1, -1])
        cons += [(*lo, ">="), (*hi, ">="), (*prod(lo, hi), ">=")]
        if k >= 1:
            cons.append((*qadd(vdot(U[k], U[k]), prod(A[k], A[k]), w=[1, -1]), "=="))
            for i in range(3):   # U_k,i - a_k b_k,i = 0
                cons.append((*qadd(U[k].comp(i), prod(A[k], b[k].comp(i)), w=[1, -1]), "=="))
    for k in range(1, nb + 1):
        cons.append((*qadd(vdot(b[k], b[k]), one(-1.0)), "=="))
    for k in range(N):
        if (1 <= k <= nb) or (1 <= k + 1 <= nb):
            cons.append((*qadd(vdot(b[k], b[k + 1]), one(-c)), ">="))
    for k in range(N - 1):
        cons.append((*qadd(vdot(U[k], U[k + 1]), prod(A[k], A[k + 1]), w=[1, -c]), ">="))
    for j in range(N):
        for k in range(j + 1, N):
            lj = qadd(A[j], one(-a1)); hj = qadd(one(a2), A[j], w=[1, -1])
            lk = qadd(A[k], one(-a1)); hk = qadd(one(a2), A[k], w=[1, -1])
            for f in (prod(lj, lk), prod(hj, hk), prod(lj, hk), prod(hj, lk)):
                cons.append((*f, ">="))
    R = sum((U[k] * gr[k] for k in range(1, N)), U[0] * gr[0])
    V = sum((U[k] * gw[k] for k in range(1, N)), U[0] * gw[0])
    vs = {"r": [R], "v": [V], "rv": [R, V]}[readout]
    import cvxpy as cp

    def convex_z(z):
        return [cp.norm(z[N + 3 * (k - 1): N + 3 * k]) <= z[k] for k in range(1, N)]
    P = QCQP(m, sq_err(vs, Q, mu[:len(vs)]), cons, convex_z=convex_z)
    P.info = dict(m=m, N=N, nb=nb, a1=a1, a2=a2, terminal=terminal, dt=dt)
    return P
