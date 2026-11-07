"""[verify-sdp2] Independent implementation (no imports from proof-csd2p / verifier-sdp / proof-sdp) of the
fixed-thrust 5DOF min-landing-error discretizations of math/08 §1.1, their Gram (Shor) SDP, a 3D multistart NLP,
KKT multiplier recovery, the stress Q (math/08 Thm 2.1), and the math/09 objects (primer, m, h_m, C_yw, Z, S).

Models:  'unit'  ||d_k|| = 1,  <d_k,b_k> >= cos d, <d_k,b_{k+1}> >= cos d      (D^unit)
         'cvx'   ||d_k|| <= 1, same gimbal half-spaces                         (D^cvx)
         'd0'    d_k = b_k                                                     (D^0)
Case T: b_0 = b_N = e_z.  Case F: b_0 = e_z, b_N free (gimbal models), in d0 the free b_N is irrelevant and dropped.
Weights cv_k = h a_k, cr_k = h a_k (tf-(k+1/2)h); a_k an arbitrary positive profile.
Vectors are stored as (x, y, z) with z vertical.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import cvxpy as cp
from scipy.optimize import minimize, lsq_linear, linprog

EZ = np.array([0.0, 0.0, 1.0])
E = None  # marker for the fixed vector e_z


class Model:
    def __init__(self, N, tf, omega, delta_deg, kind, terminal=True, a=None):
        self.N, self.tf, self.kind, self.terminal = N, tf, kind, terminal
        self.h = tf / N
        a = np.full(N, 1.0) if a is None else np.asarray(a, float)
        self.a = a
        self.cv = self.h * a
        self.cr = self.h * a * (tf - (np.arange(N) + 0.5) * self.h)
        self.crate = np.cos(min(omega * self.h, np.pi))
        self.cd = np.cos(np.deg2rad(delta_deg)) if kind != 'd0' else None
        # variable layout
        if kind == 'd0':
            self.nb = N - 1                         # b_1..b_{N-1}
            self.bslot = lambda k: E if (k == 0 or (k == N and terminal)) else (k - 1 if k <= N - 1 else 'drop')
            self.thr = [E] + list(range(N - 1))     # thrust slot of segment k: d_k = b_k
            self.n = self.nb
        else:
            self.nb = N - 1 if terminal else N
            nb = self.nb
            self.bslot = lambda k: E if (k == 0 or (k == N and terminal)) else k - 1
            self.thr = [nb + k for k in range(N)]
            self.n = nb + N
        n = self.n
        # constraints: cables (i, j, c): <z_i, z_j> >= c (j may be E); norms
        cab = []
        for k in range(N):
            i, j = self.bslot(k), self.bslot(k + 1)
            if j == 'drop':
                continue
            if i is E and j is E:
                continue
            if i is E:
                i, j = j, E
            cab.append((i, j, self.crate, 'rate'))
        if kind != 'd0':
            for k in range(N):
                for kk in (k, k + 1):
                    j = self.bslot(kk)
                    cab.append((self.thr[k], j, self.cd, 'gim'))
        self.cab = cab
        self.norm_eq = list(range(self.nb)) + ([] if kind in ('d0', 'cvx') else [self.nb + k for k in range(N)])
        self.norm_le = [self.nb + k for k in range(N)] if kind == 'cvx' else []
        # cost: sum_kl C_kl <z_k,z_l> - 2 sum <z_i, l_i> + const; Gamma (n x 2)
        Gam = np.zeros((n, 2))
        self.const_thr = np.zeros(2)  # coefficients (cv,cr) multiplying the fixed e_z thrust slots
        for k in range(N):
            s = self.thr[k]
            if s is E:
                self.const_thr += [self.cv[k], self.cr[k]]
            else:
                Gam[s] += [self.cv[k], self.cr[k]]
        self.Gam = Gam
        self.C = Gam @ Gam.T

    # ---- readout and cost in any dimension (z: n x dim, first 3 coords = E)
    def readout(self, z):
        dim = z.shape[1]
        ez = np.zeros(dim); ez[2] = 1
        V = self.Gam[:, 0] @ z + self.const_thr[0] * ez
        R = self.Gam[:, 1] @ z + self.const_thr[1] * ez
        return V, R

    def cost(self, z, wv, wr):
        V, R = self.readout(z)
        dim = z.shape[1]
        W = np.zeros(dim); W[:3] = wv; Wr = np.zeros(dim); Wr[:3] = wr
        return float(np.sum((V - W) ** 2) + np.sum((R - Wr) ** 2))

    def violation(self, z):
        dim = z.shape[1]
        ez = np.zeros(dim); ez[2] = 1
        vec = lambda i: ez if i is E else z[i]
        v = 0.0
        for (i, j, c, _) in self.cab:
            v = max(v, c - vec(i) @ vec(j))
        for i in self.norm_eq:
            v = max(v, abs(z[i] @ z[i] - 1))
        for i in self.norm_le:
            v = max(v, z[i] @ z[i] - 1)
        return v

    # ---- Gram SDP. obj='quad' (min cost) or ('lin', yv, yr): max <yv,V>+<yr,R>
    def sdp(self, wv=None, wr=None, obj='quad', tol=1e-10):
        n = self.n
        G = cp.Variable((n + 3, n + 3), symmetric=True)
        cons = [G >> 0, G[n:, n:] == np.eye(3)]
        ez = n + 2
        ent = lambda i, j: G[i, ez] if j is E else G[i, j]
        for (i, j, c, _) in self.cab:
            cons.append(ent(i, j) >= c)
        for i in self.norm_eq:
            cons.append(G[i, i] == 1)
        for i in self.norm_le:
            cons.append(G[i, i] <= 1)
        M = G[:n, n:]
        if obj == 'quad':
            cfix = np.r_[0, 0, 1.0]
            lv = np.outer(self.Gam[:, 0], wv - self.const_thr[0] * cfix) + np.outer(self.Gam[:, 1], wr - self.const_thr[1] * cfix)
            const = np.sum((wv - self.const_thr[0] * cfix) ** 2) + np.sum((wr - self.const_thr[1] * cfix) ** 2)
            f = cp.trace(self.C @ G[:n, :n]) - 2 * cp.sum(cp.multiply(lv, M)) + const
            prob = cp.Problem(cp.Minimize(f), cons)
        else:
            _, yv, yr = obj
            lv = np.outer(self.Gam[:, 0], yv) + np.outer(self.Gam[:, 1], yr)
            f = cp.sum(cp.multiply(lv, M)) + self.const_thr[0] * yv[2] + self.const_thr[1] * yr[2]
            prob = cp.Problem(cp.Maximize(f), cons)
        prob.solve(solver='CLARABEL', tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=400)
        Gv = G.value
        ev = np.linalg.eigvalsh(Gv)[::-1]
        return dict(val=prob.value, G=Gv, status=prob.status, ev=ev)

    def factor(self, Gv, dim=None):
        """rows z_i in R^{3+r}: first 3 coords = E (G[n:,n:] = I)."""
        n = self.n
        M = Gv[:n, n:]
        Rm = Gv[:n, :n] - M @ M.T
        w, U = np.linalg.eigh(Rm)
        w = np.clip(w, 0, None)
        idx = np.argsort(w)[::-1]
        if dim is not None:
            idx = idx[:dim - 3]
        Zp = U[:, idx] * np.sqrt(w[idx])
        return np.hstack([M, Zp])

    # ---- NLP in R^dim
    def _pack(self, z):
        return z.ravel()

    def solve_nlp(self, z0, wv=None, wr=None, obj='quad', maxiter=600):
        n = self.n
        dim = z0.shape[1]
        ez = np.zeros(dim); ez[2] = 1
        W = np.zeros(dim); Wr = np.zeros(dim)
        if obj == 'quad':
            W[:3] = wv; Wr[:3] = wr
        else:
            _, yv, yr = obj
            Yv = np.zeros(dim); Yv[:3] = yv; Yr = np.zeros(dim); Yr[:3] = yr
        Gam = self.Gam
        cfix = self.const_thr

        def f(x):
            z = x.reshape(n, dim)
            V = Gam[:, 0] @ z + cfix[0] * ez; R = Gam[:, 1] @ z + cfix[1] * ez
            if obj == 'quad':
                yv_, yr_ = V - W, R - Wr
                val = yv_ @ yv_ + yr_ @ yr_
                g = 2 * (np.outer(Gam[:, 0], yv_) + np.outer(Gam[:, 1], yr_))
            else:
                val = -(Yv @ V + Yr @ R)
                g = -(np.outer(Gam[:, 0], Yv) + np.outer(Gam[:, 1], Yr))
            return val, g.ravel()

        cons = []
        cab = self.cab

        def cin(x):
            z = x.reshape(n, dim)
            out = [(z[i] @ (ez if j is E else z[j])) - c for (i, j, c, _) in cab]
            out += [1 - z[i] @ z[i] for i in self.norm_le]
            return np.array(out)

        def cin_jac(x):
            z = x.reshape(n, dim)
            rows = []
            for (i, j, c, _) in cab:
                g = np.zeros((n, dim))
                if j is E:
                    g[i] += ez
                else:
                    g[i] += z[j]; g[j] += z[i]
                rows.append(g.ravel())
            for i in self.norm_le:
                g = np.zeros((n, dim)); g[i] = -2 * z[i]; rows.append(g.ravel())
            return np.array(rows)

        def ceq(x):
            z = x.reshape(n, dim)
            return np.array([z[i] @ z[i] - 1 for i in self.norm_eq])

        def ceq_jac(x):
            z = x.reshape(n, dim)
            rows = []
            for i in self.norm_eq:
                g = np.zeros((n, dim)); g[i] = 2 * z[i]; rows.append(g.ravel())
            return np.array(rows)

        cons = [dict(type='ineq', fun=cin, jac=cin_jac)]
        if self.norm_eq:
            cons.append(dict(type='eq', fun=ceq, jac=ceq_jac))
        r = minimize(f, z0.ravel(), jac=True, constraints=cons, method='SLSQP',
                     options=dict(maxiter=maxiter, ftol=1e-15))
        z = r.x.reshape(n, dim)
        val = self.cost(z, wv, wr) if obj == 'quad' else -f(r.x)[0]
        return z, val, self.violation(z)

    def random_start(self, rng, dim=3, spread=0.6):
        z = np.zeros((self.n, dim)); z[:, 2] = 1
        z[:, :3] += spread * rng.normal(size=(self.n, 3))
        if dim > 3:
            z[:, 3:] += 0.05 * rng.normal(size=(self.n, dim - 3))
        z /= np.linalg.norm(z, axis=1, keepdims=True)
        if self.kind == 'cvx':
            z[self.nb:] *= 0.98
        return z

    def best(self, wv=None, wr=None, obj='quad', rng=None, nstart=8, extra=(), dim=3, feas=1e-7):
        cand = []
        starts = list(extra) + [self.random_start(rng, dim) for _ in range(nstart)]
        for z0 in starts:
            z0 = z0[:, :dim] if z0.shape[1] >= dim else np.hstack([z0, np.zeros((self.n, dim - z0.shape[1]))])
            nr = np.linalg.norm(z0, axis=1, keepdims=True); nr[nr < 1e-9] = 1
            z0 = z0 / nr
            try:
                z, v, vi = self.solve_nlp(z0, wv, wr, obj)
            except Exception:
                continue
            if vi < feas:
                cand.append((v, z))
        if not cand:
            return None, None, []
        cand.sort(key=lambda t: t[0] if obj == 'quad' else -t[0])
        return cand[0][0], cand[0][1], cand

    # ---- KKT multipliers at a 3D point and stress Q
    def kkt(self, z, wv, wr, act_tol=1e-6):
        n = self.n
        V, R = self.readout(z)
        yv, yr = V - wv, R - wr
        grad = 2 * (np.outer(self.Gam[:, 0], yv) + np.outer(self.Gam[:, 1], yr))   # n x 3
        vec = lambda i: EZ if i is E else z[i]
        act = [(i, j, c, t) for (i, j, c, t) in self.cab if vec(i) @ vec(j) - c < act_tol]
        nle = [i for i in self.norm_le if z[i] @ z[i] > 1 - 1e-6]
        cols = []
        for (i, j, c, t) in act:
            g = np.zeros((n, 3)); g[i] -= vec(j)
            if j is not E:
                g[j] -= z[i]
            cols.append(g.ravel())
        for i in self.norm_eq + nle:
            g = np.zeros((n, 3)); g[i] = 2 * z[i]; cols.append(g.ravel())
        A = np.array(cols).T if cols else np.zeros((3 * n, 0))
        na = len(act)
        lb = np.r_[np.zeros(na), -np.inf * np.ones(len(self.norm_eq)), np.zeros(len(nle))]
        ub = np.inf * np.ones(len(lb))
        sol = lsq_linear(A, -grad.ravel(), bounds=(lb, ub), tol=1e-15, max_iter=5000)
        res = np.linalg.norm(A @ sol.x + grad.ravel()) / max(np.linalg.norm(grad), 1e-12)
        lam = sol.x[:na]
        mu = np.zeros(n)
        for i, v in zip(self.norm_eq + nle, sol.x[na:]):
            mu[i] = v
        Zm = np.diag(mu)
        lamf = np.zeros(n)   # sum of fixed-vector multipliers per slot
        for (i, j, c, t), l in zip(act, lam):
            if j is E:
                lamf[i] += l
            else:
                Zm[i, j] -= l / 2; Zm[j, i] -= l / 2
        # LICQ check (rank of active gradients)
        licq = (np.linalg.matrix_rank(A, tol=1e-8 * max(1, np.abs(A).max())) == A.shape[1]) if A.shape[1] else True
        Q = self.C + Zm
        return dict(Q=Q, Z=Zm, mu=mu, lam=lam, act=act, lamf=lamf, res=res, yv=yv, yr=yr, licq=licq, nle=nle)

    def primer(self, yv, yr):
        """P for each variable thrust slot (n x 3, zero rows for non-thrust slots)."""
        P = -(np.outer(self.Gam[:, 0], yv) + np.outer(self.Gam[:, 1], yr))
        return P

    def nodes(self, z):
        """b_0..b_N (case F gimbal: b_N variable; d0 case F: b_N dropped)."""
        B = [EZ]
        for k in range(1, self.N + 1):
            s = self.bslot(k)
            if s is E:
                B.append(EZ)
            elif s == 'drop':
                pass
            else:
                B.append(z[s])
        return np.array(B)

    def criterion(self, z, yv, yr):
        """LP of math/09 Thm 4.4: max t s.t. <b_k,c> >= t (variable b-slots), <P_k,c> >= 0, <e_z,c> >= 0, |c|_inf<=1."""
        P = self.primer(yv, yr)
        sc = np.linalg.norm(P, axis=1).max() + 1e-300
        rows, rhs = [], []
        for i in range(self.nb):
            rows.append(np.r_[-z[i], 1.0]); rhs.append(0.0)
        for i in range(self.n):
            if np.linalg.norm(P[i]) > 0:
                rows.append(np.r_[-P[i] / sc, 0.0]); rhs.append(0.0)
        rows.append(np.r_[-EZ, 0.0]); rhs.append(0.0)
        r = linprog(np.r_[0, 0, 0, -1.0], A_ub=np.array(rows), b_ub=np.array(rhs),
                    bounds=[(-1, 1)] * 3 + [(None, 1)], method='highs')
        return (float(-r.fun) if r.status == 0 else -1.0), (r.x[:3] if r.status == 0 else None)
