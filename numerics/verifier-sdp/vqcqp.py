"""[verifier-sdp] Generic real QCQP -> (full, non-isotropic) Shor SDP + genuine ipopt NLP.
Used for the extensions (gimbal, variable throttle, altitude/glide slope, min-fuel) and as a
cross-check of the Gram-form SDP in vcore.py.

A quadratic function is a triple (Q, q, c):  f(z) = z^T Q z + 2 q^T z + c   (Q symmetric).
Constraints: (Q, q, c, kind) with kind in {">=", "=="}  meaning f(z) kind 0.
Shor:  M = [[1, z^T], [z, Y]] >= 0,  f lifted = <Q, Y> + 2 q^T z + c.
Extra purely convex constraints on the first moments z (e.g. SOC) can be added via `convex_z`.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import cvxpy as cp
import casadi as ca


def qf(m, Q=None, q=None, c=0.0):
    return (np.zeros((m, m)) if Q is None else np.asarray(Q, float),
            np.zeros(m) if q is None else np.asarray(q, float), float(c))


def qadd(*fs, w=None):
    w = [1.0] * len(fs) if w is None else w
    Q = sum(wi * f[0] for wi, f in zip(w, fs)); q = sum(wi * f[1] for wi, f in zip(w, fs))
    c = sum(wi * f[2] for wi, f in zip(w, fs))
    return (Q, q, c)


def lin(m, a, c=0.0):
    """affine function a^T z + c as a quadratic triple."""
    return (np.zeros((m, m)), 0.5 * np.asarray(a, float), float(c))


def prod(f1, f2):
    """product of two AFFINE functions (Q must be zero) -> quadratic triple."""
    a1, c1 = 2 * f1[1], f1[2]
    a2, c2 = 2 * f2[1], f2[2]
    Q = 0.5 * (np.outer(a1, a2) + np.outer(a2, a1))
    q = 0.5 * (c1 * a2 + c2 * a1)
    return (Q, q, c1 * c2)


class QCQP:
    def __init__(self, m, obj, cons, convex_z=None, casadi_extra=None):
        self.m, self.obj, self.cons = m, obj, cons
        self.convex_z = convex_z          # callable(z_cvx) -> list of cvxpy constraints
        self.casadi_extra = casadi_extra  # callable(z_sx) -> (g list, lb, ub) extra exact constraints

    # --------------------------------------------------------------- SDP
    def sdp(self, solver="CLARABEL", tol=1e-9, extra_lifted=()):
        m = self.m
        M = cp.Variable((m + 1, m + 1), symmetric=True)
        z = M[0, 1:]
        Y = M[1:, 1:]

        def L(f):
            Q, q, c = f
            e = 2 * (q @ z) + c
            if np.any(Q):
                e = e + cp.trace(Q @ Y)
            return e
        cons = [M >> 0, M[0, 0] == 1]
        for (Q, q, c, kind) in list(self.cons) + list(extra_lifted):
            e = L((Q, q, c))
            cons.append(e >= 0 if kind == ">=" else e == 0)
        if self.convex_z is not None:
            cons += self.convex_z(z)
        pr = cp.Problem(cp.Minimize(L(self.obj)), cons)
        st = None
        for t in (tol, 10 * tol):
            try:
                if solver == "CLARABEL":
                    pr.solve(solver="CLARABEL", tol_gap_abs=t, tol_gap_rel=t, tol_feas=t, max_iter=500)
                else:
                    pr.solve(solver="SCS", eps_abs=t, eps_rel=t, max_iters=300000)
            except cp.error.SolverError:
                st = "error"; continue
            st = pr.status
            if st == "optimal":
                break
        Mv = M.value
        ev = np.linalg.eigvalsh(Mv)[::-1] if Mv is not None else np.array([np.nan])
        return dict(status=st, val=float(pr.value) if pr.value is not None else np.nan,
                    z=None if Mv is None else Mv[0, 1:].copy(), M=Mv, ev=ev,
                    rank=int(np.sum(ev > 1e-6 * ev[0])) if Mv is not None else -1)

    # --------------------------------------------------------------- NLP
    def nlp(self):
        m = self.m
        z = ca.SX.sym("z", m)

        def F(f):
            Q, q, c = f
            return ca.mtimes([z.T, ca.DM(Q), z]) + 2 * ca.dot(ca.DM(q), z) + c
        g, lb, ub = [], [], []
        for (Q, q, c, kind) in self.cons:
            g.append(F((Q, q, c))); lb.append(0.0); ub.append(0.0 if kind == "==" else ca.inf)
        if self.casadi_extra is not None:
            gg, l2, u2 = self.casadi_extra(z)
            g += gg; lb += l2; ub += u2
        nlp = {"x": z, "f": F(self.obj), "g": ca.vertcat(*g)}
        opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.tol": 1e-11, "ipopt.sb": "yes",
                "ipopt.constr_viol_tol": 1e-10, "ipopt.max_iter": 3000}
        S = ca.nlpsol("S", "ipopt", nlp, opts)
        self._S, self._lb, self._ub = S, lb, ub
        self._gfun = ca.Function("g", [z], [ca.vertcat(*g)])
        self._ffun = ca.Function("f", [z], [F(self.obj)])
        return S

    def viol(self, zv):
        gv = np.array(self._gfun(zv)).ravel()
        lb, ub = np.array(self._lb, float), np.array(self._ub, float)
        return float(max(0.0, np.max(lb - gv), np.max(gv - ub)))

    def solve_nlp(self, z0):
        if not hasattr(self, "_S"):
            self.nlp()
        r = self._S(x0=z0, lbg=self._lb, ubg=self._ub)
        zv = np.array(r["x"]).ravel()
        return dict(f=float(self._ffun(zv)), z=zv, viol=self.viol(zv))

    def best_of(self, starts, feas_tol=1e-7):
        best = None
        fs = []
        for s in starts:
            r = self.solve_nlp(s)
            if r["viol"] < feas_tol:
                fs.append(r["f"])
                if best is None or r["f"] < best["f"]:
                    best = r
        if best is None:
            return dict(f=np.inf, z=None, fs=[])
        best["fs"] = sorted(fs)
        return best

    def eval_lifted(self, f, M):
        Q, q, c = f
        return float(np.sum(Q * M[1:, 1:]) + 2 * q @ M[0, 1:] + c)
