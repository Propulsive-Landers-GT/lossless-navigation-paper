"""[verifier-sdp] Parametrized gimbal ('inner' discretization) problem: Gram SDP + R^dim NLP.
Nodes b_0..b_N (b_0=b_N=e_z if terminal), thrust d_0..d_{N-1}; <b_k,b_k+1> >= cos(omega h);
<d_k,b_k> >= cos delta and (both) <d_k,b_k+1> >= cos delta.  delta=0 -> d_k = b_k (pure fixed thrust,
both=False there, handled by delta=None).  Cost |dv-wv|^2 + |dr-wr|^2 (or one of them)."""
import os, warnings
warnings.filterwarnings("ignore")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import cvxpy as cp
import casadi as ca


class Gim:
    def __init__(self, N, tf, omega, delta, a=1.0, both=True, terminal=True, readout="rv"):
        self.N, self.tf, self.om, self.delta, self.a = N, tf, omega, delta, a
        self.h = tf / N
        self.cr = np.cos(min(omega * self.h, np.pi))
        self.cd = None if delta is None else np.cos(delta)
        self.both, self.terminal, self.readout = both, terminal, readout
        self.gv = a * self.h * np.ones(N)
        self.gr = a * self.h * (tf - (np.arange(N) + 0.5) * self.h)
        self.nb = N - 1 if terminal else N
        self.gim = delta is not None
        self.n = self.nb + (N if self.gim else 0)
        self.mu = {"rv": (1.0, 1.0), "r": (0.0, 1.0), "v": (1.0, 0.0)}[readout]
        self._sdp = None

    # ---------------------------------------------------------------- SDP
    def build(self):
        N, nb, n = self.N, self.nb, self.n
        Z = cp.Variable((n + 3, n + 3), symmetric=True)
        wv = cp.Parameter(3); wr = cp.Parameter(3)
        ez = n + 2
        cons = [Z >> 0, Z[n:, n:] == np.eye(3), cp.diag(Z[:n, :n]) == 1]
        bidx = lambda k: (k - 1) if 1 <= k <= nb else None       # None -> e_z

        def dot_idx(i, j):
            if i is None and j is None:
                return 1.0
            if i is None:
                return Z[j, ez]
            if j is None:
                return Z[i, ez]
            return Z[i, j]
        for k in range(N):
            e = dot_idx(bidx(k), bidx(k + 1))
            if not isinstance(e, float):
                cons.append(e >= self.cr)
        if self.gim:
            didx = lambda k: nb + k
            for k in range(N):
                cons.append(dot_idx(bidx(k), didx(k)) >= self.cd)
                if self.both:
                    cons.append(dot_idx(bidx(k + 1), didx(k)) >= self.cd)
            thr = [didx(k) for k in range(N)]
        else:
            thr = [bidx(k) for k in range(N)]
        # readout: sum_k g_k t_k, t_k = thrust vector (e_z if fixed)
        free = [i for i in thr if i is not None]
        fixed_k = [k for k, i in enumerate(thr) if i is None]
        obj = 0
        for (g, w, mu) in ((self.gv, wv, self.mu[0]), (self.gr, wr, self.mu[1])):
            if mu == 0:
                continue
            gf = np.array([g[k] for k, i in enumerate(thr) if i is not None])
            yfix = sum(g[k] for k in fixed_k) * np.array([0, 0, 1.0])
            S = np.zeros((n + 3, n + 3))
            for a_, ia in zip(gf, free):
                for b_, ib in zip(gf, free):
                    S[ia, ib] += a_ * b_
            lin = np.zeros((n, 3))
            for a_, ia in zip(gf, free):
                lin[ia] = a_
            # |sum g t - w|^2 = <S,Z> + 2 <sum g x, yfix - w> + |yfix - w|^2
            X = Z[:n, n:]
            obj = obj + mu * (cp.trace(S @ Z)
                              + 2 * (cp.sum(cp.multiply(lin, X), axis=0) @ (yfix - w))
                              + cp.sum_squares(yfix - w))
        self._sdp = (cp.Problem(cp.Minimize(obj), cons), Z, wv, wr)
        return self._sdp

    def sdp(self, wv, wr, solver="CLARABEL", tol=1e-9):
        if self._sdp is None:
            self.build()
        pr, Z, pv, pw = self._sdp
        pv.value = np.asarray(wv, float); pw.value = np.asarray(wr, float)
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
        Zv = Z.value
        ev = np.linalg.eigvalsh(Zv)[::-1]
        X = Zv[:self.n, self.n:]
        perp = float(np.sum(1 - np.sum(X ** 2, 1)))
        return dict(val=float(pr.value), status=st, Z=Zv, ev=ev, e4=float(ev[3] / ev[0]), perp=perp)

    # ---------------------------------------------------------------- NLP in R^dim
    def nlp(self, dim=3):
        key = ("nlp", dim)
        if hasattr(self, "_nlps") and key in self._nlps:
            return self._nlps[key]
        N, nb = self.N, self.nb
        nv = nb + (N if self.gim else 0)
        x = ca.SX.sym("x", dim * nv)
        p = ca.SX.sym("p", 7)          # wv(3), wr(3), lam
        ez = ca.DM([0, 0, 1] + [0] * (dim - 3))
        Bf = ca.reshape(x[:dim * nb], dim, nb)
        cols = [ez] + [Bf[:, i] for i in range(nb)] + ([ez] if self.terminal else [])
        B = ca.horzcat(*cols)
        T = ca.reshape(x[dim * nb:], dim, N) if self.gim else B[:, :N]
        pad = [0] * (dim - 3)
        tv = ca.vertcat(p[0:3], ca.DM(pad)) if dim > 3 else p[0:3]
        tr = ca.vertcat(p[3:6], ca.DM(pad)) if dim > 3 else p[3:6]
        dv = ca.mtimes(T, ca.DM(self.gv)); dr = ca.mtimes(T, ca.DM(self.gr))
        f = self.mu[0] * ca.sumsqr(dv - tv) + self.mu[1] * ca.sumsqr(dr - tr)
        if dim > 3:
            Xr = ca.reshape(x, dim, nv)
            f = f + p[6] * ca.sumsqr(Xr[3:, :])
        g, lb, ub = [], [], []
        for i in range(nb):
            g.append(ca.sumsqr(Bf[:, i])); lb.append(1); ub.append(1)
        for k in range(N):
            if (1 <= k <= nb) or (1 <= k + 1 <= nb):
                g.append(ca.dot(B[:, k], B[:, k + 1])); lb.append(self.cr); ub.append(ca.inf)
        if self.gim:
            for k in range(N):
                g.append(ca.sumsqr(T[:, k])); lb.append(1); ub.append(1)
                g.append(ca.dot(T[:, k], B[:, k])); lb.append(self.cd); ub.append(ca.inf)
                if self.both and k + 1 < B.shape[1]:
                    g.append(ca.dot(T[:, k], B[:, k + 1])); lb.append(self.cd); ub.append(ca.inf)
        opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.tol": 1e-12, "ipopt.sb": "yes",
                "ipopt.constr_viol_tol": 1e-11, "ipopt.max_iter": 3000}
        S = ca.nlpsol("S", "ipopt", {"x": x, "p": p, "f": f, "g": ca.vertcat(*g)}, opts)
        gf = ca.Function("g", [x], [ca.vertcat(*g)])
        ff = ca.Function("f", [x, p], [self.mu[0] * ca.sumsqr(dv - tv) + self.mu[1] * ca.sumsqr(dr - tr)])
        if not hasattr(self, "_nlps"):
            self._nlps = {}
        self._nlps[key] = (S, gf, ff, np.array(lb, float), np.array(ub, float), nv)
        return self._nlps[key]

    def solve(self, x0, wv, wr, dim=3, lam=0.0):
        S, gf, ff, lb, ub, nv = self.nlp(dim)
        p = np.r_[wv, wr, lam]
        r = S(x0=x0, p=p, lbg=lb, ubg=ub)
        x = np.array(r["x"]).ravel()
        gv = np.array(gf(x)).ravel()
        viol = float(max(0.0, np.max(lb - gv), np.max(gv - ub)))
        return x, float(ff(x, p)), viol

    def random_start(self, rng, wv=None):
        N = self.N
        kk = np.arange(N + 1)
        s = rng.uniform(0.1, 1.0)
        base = np.minimum(kk, N - kk) if self.terminal else kk
        phi = np.minimum(s * base * self.om * self.h, np.pi)
        mode = rng.integers(4)
        psi0 = rng.uniform(0, 2 * np.pi)
        if mode == 0:
            psi = psi0 * np.ones(N + 1)
        elif mode == 1:
            psi = psi0 + rng.uniform(-np.pi, np.pi) * np.linspace(0, 1, N + 1)
        elif mode == 2:
            psi = psi0 + np.cumsum(rng.normal(0, 0.4, N + 1))
        else:
            phi = phi * rng.uniform(0, 1, N + 1)
            psi = psi0 + rng.uniform(-3, 3) * np.linspace(0, 1, N + 1) ** 2
        B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
        x = list(B[1:1 + self.nb].ravel())
        if self.gim:
            D = B[:N] + rng.uniform(0, 1) * np.sin(self.delta) * rng.normal(size=(N, 3))
            if wv is not None and rng.uniform() < 0.5:
                D = D + rng.uniform(0, 0.4) * np.asarray(wv) / np.linalg.norm(wv)
            D /= np.linalg.norm(D, axis=1, keepdims=True)
            x += list(D.ravel())
        return np.array(x)

    def sdp_starts(self, Zv, rng, k=20):
        n = self.n
        w, V = np.linalg.eigh(Zv)
        keep = w > 1e-7 * w.max()
        F = (V[:, keep] * np.sqrt(w[keep])).T
        E = F[:, n:]
        r = F.shape[0]
        Qf, _ = np.linalg.qr(np.hstack([E, rng.normal(size=(r, r))]))
        Qf[:, :3] *= np.sign(np.sum(Qf[:, :3] * E, 0))
        C = Qf.T @ F
        out = []
        vecs = C[:, :n].T
        for j in range(k):
            if j == 0:
                R = np.zeros((3, r)); R[:, :3] = np.eye(3)
            elif j % 2:
                R = np.linalg.qr(rng.normal(size=(r, r)))[0][:3]
            else:
                R = np.hstack([np.eye(3), rng.normal(0, 1, (3, r - 3))])
            Vv = vecs @ R.T
            Vv /= np.maximum(np.linalg.norm(Vv, axis=1, keepdims=True), 1e-12)
            out.append(Vv.ravel())
        return out, C

    def best3(self, wv, wr, rng, nstart, Zv=None):
        best, xb, fs = np.inf, None, []
        starts = []
        if Zv is not None:
            starts += self.sdp_starts(Zv, rng)[0]
        starts += [self.random_start(rng, wv) for _ in range(nstart)]
        for x0 in starts:
            x, f, v = self.solve(x0, wv, wr)
            if v < 1e-8:
                fs.append(f)
                if f < best:
                    best, xb = f, x
        return best, xb, np.array(fs)

    def extreme_readouts(self):
        """tent extreme arc (with thrust leaning by delta in the same plane, inner-consistent) readouts."""
        N = self.N
        kk = np.arange(N + 1)
        phi = np.minimum(np.minimum(kk, N - kk) * self.om * self.h, np.pi)
        # thrust on [k,k+1] can lean min(phi_k, phi_k+1)+delta... use the largest tilt allowed by both cones
        if self.gim:
            th = np.minimum(np.minimum(phi[:N], phi[1:]) + self.delta, np.maximum(phi[:N], phi[1:]) - 0 + self.delta)
            if self.both:
                th = np.minimum(phi[:N], phi[1:]) + self.delta
                th = np.minimum(th, np.maximum(phi[:N], phi[1:]) + self.delta)
        else:
            th = phi[:N]
        Pv = np.array([self.gv @ np.sin(th), 0, self.gv @ np.cos(th)])
        Pr = np.array([self.gr @ np.sin(th), 0, self.gr @ np.cos(th)])
        return Pv, Pr
