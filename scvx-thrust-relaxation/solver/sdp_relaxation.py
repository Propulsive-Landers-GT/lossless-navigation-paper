"""One convex solve for a small 6-DOF lander: a Shor SDP relaxation, checked against IPOPT.

Same vehicle as sixdof_lcvx.py (Szmuk et al. baseline) at a fixed time of flight, discretized so
that every constraint is at most quadratic in the unknowns:

  attitude      R_{k+1} = R_k F_k,  (I - h/2 [w_k]x) F_k = I + h/2 [w_k]x   (Cayley step)
  translation   m_k a_k = R_k T_k + m_k g,  v_{k+1} = v_k + h a_k,  r_{k+1} = r_k + h v_k + h^2/2 a_k
  rotation rate w_{k+1} = w_k + h J^-1 (r_T x T_k)
  mass          m_{k+1} = m_k - h alpha Gamma_k,  ||T_k|| <= Gamma_k   (the LCvx relaxation)

The rate equation leaves out w x Jw. That is exact for this vehicle: J_y = J_z and the engine
makes no roll torque, so the roll rate stays 0 and w x Jw = 0.

Shor's relaxation replaces each product x_i x_j by an entry of a PSD matrix whose first row is
(1, x). The problem is a chain, so there is one PSD matrix per pair of consecutive nodes, and
neighbouring matrices must agree where they overlap. Redundant quadratic constraints (rotation
matrix identities, squared bounds, linear equalities multiplied by every unknown) hold at any true
solution and only tighten the relaxation. If every matrix comes out rank one, its first row is a
feasible point that attains the relaxation's bound, which proves it is the global optimum.

Usage: python sdp_relaxation.py [N] [t_f]
"""
import sys
import time

import casadi as ca
import cvxpy as cp
import numpy as np
import scipy.sparse as sps

from sixdof_lcvx import Params


class Poly(dict):
    """Polynomial of degree <= 2 in the unknowns: {(): c, (i,): c, (i, j): c} with i <= j."""
    __array_ufunc__ = None  # numpy scalars defer to Poly's operators

    def __add__(a, b):
        r = Poly(a)
        for k, c in poly(b).items():
            r[k] = r.get(k, 0.0) + c
        return r

    def __mul__(a, b):
        r = Poly()
        for k1, c1 in a.items():
            for k2, c2 in poly(b).items():
                k = tuple(sorted(k1 + k2))
                assert len(k) <= 2
                r[k] = r.get(k, 0.0) + c1 * c2
        return r

    __radd__, __rmul__ = __add__, __mul__

    def __sub__(a, b):
        return a + poly(b) * -1.0

    def __rsub__(a, b):
        return poly(b) - a

    def __neg__(a):
        return a * -1.0

    def degree(a):
        return max((len(k) for k in a), default=0)

    def unknowns(a):
        return {i for k in a for i in k}


def poly(b):
    return b if isinstance(b, Poly) else Poly({(): float(b)})


def evaluate(P, x):
    return sum((c * (x[k[0]] * x[k[1]] if len(k) == 2 else x[k[0]] if k else 1.0)
                for k, c in P.items()), 0.0)


def dot(u, v):
    return sum((a * b for a, b in zip(u, v)), Poly())


def minus(u, v):
    return [a - b for a, b in zip(u, v)]


def cross(u, v):
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


def matmul(A, B):
    """Product of two 3x3 matrices stored row-major as length-9 lists."""
    return [dot(A[3 * i:3 * i + 3], B[l::3]) for i in range(3) for l in range(3)]


def so3(M):
    """Quadratic identities of a rotation matrix: orthonormal, right-handed rows and columns."""
    cols = [M[j::3] for j in range(3)]
    rows = [M[3 * i:3 * i + 3] for i in range(3)]
    out = []
    for vs in (cols, rows):
        out += [dot(vs[a], vs[b]) - float(a == b) for a in range(3) for b in range(a, 3)]
        for a in range(3):
            out += minus(vs[a], cross(vs[(a + 1) % 3], vs[(a + 2) % 3]))
    return out


class Lander:
    def __init__(self, p: Params, N: int, tf: float):
        self.n, self.N, self.node, self.node_of, self.plain = 0, N, [], {}, set()
        self.eq, self.ge, self.soc = [], [], []  # the problem
        self.eq_r, self.ge_r = [], []  # redundant: only used to tighten the relaxation
        h = tf / N
        self.r = r = [self.new(3) for _ in range(N + 1)]
        self.v = v = [self.new(3) for _ in range(N + 1)]
        self.X = X = []
        for k in range(N + 1):
            x = dict(m=self.new(1, k)[0], R=self.new(9, k), w=self.new(3, k))
            if k < N:
                x.update(a=self.new(3, k), F=self.new(9, k), T=self.new(3, k), G=self.new(1, k)[0])
            X.append(x)

        I = np.eye(3).ravel()
        self.eq += ([X[0]["m"] - p.m_wet] + minus(X[0]["R"], I) + minus(X[0]["w"], np.zeros(3))
                    + minus(r[0], p.r0) + minus(v[0], p.v0))
        self.eq += (minus(r[N], np.zeros(3)) + minus(v[N], p.vf)
                    + [X[N]["R"][3], X[N]["R"][6], X[N]["w"][1], X[N]["w"][2]])
        for k in range(N):
            x, y = X[k], X[k + 1]
            m, a, R, F, w, T, G = (x[s] for s in ("m", "a", "R", "F", "w", "T", "G"))
            RT = [dot(R[3 * i:3 * i + 3], T) for i in range(3)]
            self.eq += [m * a[i] - RT[i] - p.g[i] * m for i in range(3)]
            self.eq += minus(y["R"], matmul(R, F))
            z = Poly()
            W = [z, -w[2], w[1], w[2], z, -w[0], -w[1], w[0], z]
            self.eq += [F[q] - h / 2 * WF - I[q] - h / 2 * W[q] for q, WF in enumerate(matmul(W, F))]
            tau = cross(p.rT, T)
            self.eq += [y["w"][i] - w[i] - h / p.J[i] * tau[i] for i in range(3)]
            self.eq += [y["m"] - m + h * p.alpha * G]
            self.eq += [v[k + 1][i] - v[k][i] - h * a[i] for i in range(3)]
            self.eq += [r[k + 1][i] - r[k][i] - h * v[k][i] - h * h / 2 * a[i] for i in range(3)]
            self.soc += [(G, T), (T[0] * (1 / np.cos(p.delta_max)), T),
                         (r[k][0] * (1 / np.tan(p.gamma_gs)), r[k][1:])]
            self.ge += [G - p.T_min, p.T_max - G]
            a_max = p.T_max / p.m_dry
            self.ge_r += [G * G - dot(T, T), T[0] * T[0] - np.cos(p.delta_max) ** 2 * dot(T, T),
                          (G - p.T_min) * (p.T_max - G),
                          a_max ** 2 - dot(minus(a, p.g), minus(a, p.g))]
            self.eq_r += so3(F)
        for x in X:
            self.soc += [(poly(p.omega_max), x["w"])]
            self.ge += [x["m"] - p.m_dry, x["R"][0] - np.cos(p.theta_max)]
            self.ge_r += [(x["m"] - p.m_dry) * (p.m_wet - x["m"]),
                          p.omega_max ** 2 - dot(x["w"], x["w"])]
            self.eq_r += so3(x["R"])
        self.objective = X[N]["m"]  # maximize final mass

    def new(self, d, node=None):
        idx = range(self.n, self.n + d)
        self.n += d
        if node is None:
            self.plain.update(idx)
        else:
            if node == len(self.node):
                self.node.append([])
            self.node[node] += idx
            self.node_of.update({i: node for i in idx})
        return [Poly({(i,): 1.0}) for i in idx]

    def violation(self, x):
        eq = max(abs(evaluate(P, x)) for P in self.eq)
        ge = max(-evaluate(P, x) for P in self.ge)
        soc = max(np.linalg.norm([evaluate(q, x) for q in vs]) - evaluate(t, x) for t, vs in self.soc)
        return eq, max(ge, soc, 0.0)

    def straight_line(self, p: Params):
        x = np.zeros(self.n)
        ix = lambda P: next(iter(P))[0]
        for k, X in enumerate(self.X):
            lam = k / self.N
            m = p.m_wet - lam * 0.5
            vals = dict(m=[m], R=np.eye(3).ravel(), w=np.zeros(3), a=np.zeros(3),
                        F=np.eye(3).ravel(), T=[m, 0, 0], G=[max(m, p.T_min)])
            for s, P in X.items():
                x[[ix(q) for q in (P if isinstance(P, list) else [P])]] = vals[s]
            x[[ix(q) for q in self.r[k]]] = (1 - lam) * p.r0
            x[[ix(q) for q in self.v[k]]] = (1 - lam) * p.v0 + lam * p.vf
        return x


def solve_sdp(L: Lander, **solver_opts):
    N = L.N
    cliques = [L.node[k] + L.node[k + 1] for k in range(N)]
    size = [len(c) + 1 for c in cliques]
    Z = [cp.Variable((s, s), PSD=True) for s in size]
    xp = cp.Variable(len(L.plain))
    y = cp.hstack([cp.vec(z, order="F") for z in Z] + [xp])
    off = np.cumsum([0] + [s * s for s in size])
    plain = {i: off[-1] + j for j, i in enumerate(sorted(L.plain))}
    pos = {(c, i): j + 1 for c, idx in enumerate(cliques) for j, i in enumerate(idx)}

    def col(i, j=None):
        """Position in y of the moment x_i (j is None) or x_i x_j."""
        if j is None and i in plain:
            return plain[i]
        ks = {L.node_of[i], L.node_of[i if j is None else j]}
        c = min(min(ks), N - 1)
        assert max(ks) - c <= 1
        return off[c] + (0 if j is None else pos[c, j]) * size[c] + pos[c, i]

    def affine(Ps):
        ri, ci, vals, b = [], [], [], np.zeros(len(Ps))
        for r, P in enumerate(Ps):
            for k, c in P.items():
                if k:
                    ri.append(r), ci.append(col(*k)), vals.append(c)
                else:
                    b[r] += c
        return sps.csr_matrix((vals, (ri, ci)), shape=(len(Ps), y.size)) @ y + b

    # Linear equalities times every unknown that shares a PSD matrix with them.
    rlt = []
    for P in L.eq:
        u = P.unknowns()
        if P.degree() == 1 and not u & L.plain:
            ks = {L.node_of[i] for i in u}
            near = {i for c in range(N) if ks <= {c, c + 1} for i in cliques[c]}
            rlt += [P * Poly({(i,): 1.0}) for i in sorted(near)]

    cons = [z[0, 0] == 1 for z in Z]
    for c in range(N - 1):
        nb, na = len(L.node[c + 1]), len(L.node[c])
        s1 = [0] + list(range(na + 1, na + 1 + nb))
        cons.append(Z[c][s1, :][:, s1] == Z[c + 1][:nb + 1, :nb + 1])
    cons += [affine(L.eq + L.eq_r + rlt) == 0, affine(L.ge + L.ge_r) >= 0]
    cons += [cp.SOC(affine([t])[0], affine(vs)) for t, vs in L.soc]
    prob = cp.Problem(cp.Maximize(affine([L.objective])[0]), cons)
    # Default regularization stalls with NumericalError at N = 10.
    prob.solve(**({"solver": "CLARABEL", "static_regularization_constant": 1e-6} | solver_opts))

    yv = np.concatenate([z.value.ravel(order="F") for z in Z] + [xp.value])
    xhat = np.array([yv[col(i)] for i in range(L.n)])
    eig = [np.linalg.eigvalsh(z.value)[::-1] for z in Z]
    return prob.status, prob.value, xhat, eig, len(rlt)


def solve_nlp(L: Lander, guess):
    x = ca.SX.sym("x", L.n)
    g = [evaluate(P, x) for P in L.eq]
    lbg, ubg = [0.0] * len(g), [0.0] * len(g)
    ineq = L.ge + [t for t, _ in L.soc] + [t * t - dot(vs, vs) for t, vs in L.soc]
    g += [evaluate(P, x) for P in ineq]
    lbg += [0.0] * len(ineq)
    ubg += [np.inf] * len(ineq)
    nlp = {"x": x, "f": -evaluate(L.objective, x), "g": ca.vertcat(*g)}
    opts = {"ipopt.print_level": 0, "print_time": False, "ipopt.max_iter": 5000, "ipopt.tol": 1e-10}
    S = ca.nlpsol("S", "ipopt", nlp, opts)
    sol = S(x0=guess, lbg=lbg, ubg=ubg)
    xs = np.array(sol["x"]).ravel()
    return xs, -float(sol["f"]), S.stats()["return_status"]


def thrust_gap(L, x):
    """Largest Gamma_k - ||T_k|| over the nodes (0 means the thrust relaxation is lossless)."""
    return max(evaluate(X["G"], x) - np.linalg.norm([evaluate(q, x) for q in X["T"]])
               for X in L.X[:-1])


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    tf = float(sys.argv[2]) if len(sys.argv) > 2 else 7.5
    p = Params()
    L = Lander(p, N, tf)
    print(f"N = {N}, t_f = {tf}: {L.n} unknowns, {len(L.eq)} equalities")

    t0 = time.time()
    status, bound, xhat, eig, nrlt = solve_sdp(L)
    print(f"\nSDP ({status}, {time.time() - t0:.1f} s, {nrlt} RLT rows): m_N <= {bound:.6f}")
    print("  lambda_2 / lambda_1 per PSD block:",
          " ".join(f"{e[1] / e[0]:.1e}" for e in eig))
    eqv, gev = L.violation(xhat)
    print(f"  first row as a trajectory: m_N = {evaluate(L.objective, xhat):.6f}, "
          f"max equality error {eqv:.1e}, max inequality violation {gev:.1e}, "
          f"max Gamma - ||T|| {thrust_gap(L, xhat):.1e}")

    for name, guess in [("from SDP first row", xhat), ("from straight line", L.straight_line(p))]:
        t0 = time.time()
        xs, mN, st = solve_nlp(L, guess)
        eqv, gev = L.violation(xs)
        print(f"\nIPOPT {name} ({st}, {time.time() - t0:.1f} s): m_N = {mN:.6f}, "
              f"max equality error {eqv:.1e}, max inequality violation {gev:.1e}, "
              f"max Gamma - ||T|| {thrust_gap(L, xs):.1e}")
        print(f"  gap to SDP bound: {bound - mN:.2e}")
