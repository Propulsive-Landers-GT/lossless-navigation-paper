"""Certify the steering hypothesis with interval arithmetic.

check_lossless.py tests, in floating point, that every set of `s` thrust nodes can steer the
terminal conditions (plus any held path constraints) for a converged solution. This script
proves it for the solution the solver reported:

1. Re-run the 6-DOF RK4 shooting map at the reported controls in interval arithmetic with
   outward rounding, carrying derivatives forward. The vector field is written the way
   lean/LCvx/SixDOF.lean writes `field` (division by m and by J). The result encloses the exact
   derivative of that exact map at that exact (floating-point) point.
2. For each node set, take an approximate inverse X of the midpoint matrix and bound
   ||M X - I||_inf over the whole enclosure, with every floating-point error accounted for.
   If the bound is below 1, every matrix in the enclosure, including the true one, has full row
   rank.

It does not address whether the reported point is an exact optimum; that is the solver's
convergence tolerance.

Usage: python certify_rank.py <case> <m> <s> [held...]   e.g.  python certify_rank.py loose_rate 0 4
"""
import itertools
import math
import sys
from pathlib import Path

import numpy as np
from mpmath import iv
from mpmath.libmp import round_ceiling, round_floor, to_float

from check_lossless import CASES, TERM_IDX, TOL_ACTIVE, active_constraints
from sixdof_lcvx import Params, initial_state

U_RND = 2.0 ** -53

# Interval arithmetic at 50 significant digits with outward rounding (mpmath). Double-precision
# intervals blow up through 200 RK4 substeps of rotational dynamics; at this precision the
# enclosures stay far below the rank margins.
iv.dps = 50


def Iv(x):
    """Exact interval around a number (floats are exact binary rationals)."""
    return iv.mpf(x)


def lo_hi(e):
    """Float bounds of an interval, rounded outward."""
    a, b = e._mpi_
    return to_float(a, rnd=round_floor), to_float(b, rnd=round_ceiling)


class Du:
    """Interval value with an interval gradient (forward-mode derivative)."""
    __slots__ = ("v", "g")

    def __init__(self, v, g):
        self.v, self.g = v, g

    @staticmethod
    def const(c, n):
        return Du(iv.mpf(c), [Iv(0)] * n)

    def _o(self, o):
        return o if isinstance(o, Du) else Du.const(o, len(self.g))

    def __add__(self, o):
        o = self._o(o)
        return Du(self.v + o.v, [a + b for a, b in zip(self.g, o.g)])

    __radd__ = __add__

    def __neg__(self):
        return Du(-self.v, [-a for a in self.g])

    def __sub__(self, o):
        return self + (-self._o(o))

    def __rsub__(self, o):
        return self._o(o) + (-self)

    def __mul__(self, o):
        o = self._o(o)
        return Du(self.v * o.v, [a * o.v + self.v * b for a, b in zip(self.g, o.g)])

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = self._o(o)
        q = self.v / o.v
        return Du(q, [(a - q * b) / o.v for a, b in zip(self.g, o.g)])


def field(p, x, u, G):
    """Same formulas as `field` in SixDOF.lean: x = (m, r, v, q, w)."""
    m, v, q, w = x[0], x[4:7], x[7:11], x[11:14]
    q0, q1, q2, q3 = q
    T = u
    rot = [
        (1 - 2 * (q2 * q2 + q3 * q3)) * T[0] + 2 * (q1 * q2 - q0 * q3) * T[1]
        + 2 * (q1 * q3 + q0 * q2) * T[2],
        2 * (q1 * q2 + q0 * q3) * T[0] + (1 - 2 * (q1 * q1 + q3 * q3)) * T[1]
        + 2 * (q2 * q3 - q0 * q1) * T[2],
        2 * (q1 * q3 - q0 * q2) * T[0] + 2 * (q2 * q3 + q0 * q1) * T[1]
        + (1 - 2 * (q1 * q1 + q2 * q2)) * T[2],
    ]
    qd = [-(q1 * w[0] + q2 * w[1] + q3 * w[2]) / 2, (q0 * w[0] + q2 * w[2] - q3 * w[1]) / 2,
          (q0 * w[1] - q1 * w[2] + q3 * w[0]) / 2, (q0 * w[2] + q1 * w[1] - q2 * w[0]) / 2]
    rT, J, g = p.rT, p.J, p.g
    cr = lambda a, b: [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
                       a[0] * b[1] - a[1] * b[0]]
    Jw = [J[0] * w[0], J[1] * w[1], J[2] * w[2]]
    c1, c2 = cr([float(c) for c in rT], T), cr(w, Jw)
    return ([-(p.alpha * G)] + list(v) + [rot[i] / m + g[i] for i in range(3)] + qd
            + [(c1[i] - c2[i]) / J[i] for i in range(3)])


def interval_step(p, x, u, G, s):
    """One interval (M RK4 substeps) in Du arithmetic. Seeds: x (14), u (3), G, s."""
    n = 19
    seed = lambda val, k: Du(val, [Iv(1.0 if i == k else 0.0) for i in range(n)])
    X = [seed(x[i], i) for i in range(14)]
    Uu = [seed(Iv(float(u[i])), 14 + i) for i in range(3)]
    Gd = seed(Iv(float(G)), 17)
    h = seed(Iv(float(s)), 18) / float(p.N * p.substeps)
    for _ in range(p.substeps):
        k1 = field(p, X, Uu, Gd)
        k2 = field(p, [a + h / 2 * b for a, b in zip(X, k1)], Uu, Gd)
        k3 = field(p, [a + h / 2 * b for a, b in zip(X, k2)], Uu, Gd)
        k4 = field(p, [a + h * b for a, b in zip(X, k3)], Uu, Gd)
        X = [a + h / 6 * (b1 + 2 * b2 + 2 * b3 + b4) for a, b1, b2, b3, b4 in zip(X, k1, k2, k3, k4)]
    return [d.v for d in X], [d.g for d in X]


def imatmul(A, B):
    """Interval matrix product (lists of lists of Iv)."""
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), Iv(0.0))
             for j in range(len(B[0]))] for i in range(len(A))]


def mid_rad(M):
    lo = np.array([[lo_hi(e)[0] for e in r] for r in M])
    hi = np.array([[lo_hi(e)[1] for e in r] for r in M])
    mid = (lo + hi) / 2
    rad = np.nextafter(np.maximum(hi - mid, mid - lo), np.inf)
    return mid, rad


def certify_full_row_rank(Mm, Mr):
    """True only if every matrix within Mr of Mm has full row rank (proof: ||M X - I|| < 1)."""
    r, n = Mm.shape
    X = np.linalg.pinv(Mm)
    gam = lambda k: k * U_RND / (1 - k * U_RND)
    C = Mm @ X
    T = np.abs(C - np.eye(r)) + (gam(n + 2) * np.abs(Mm) + Mr) @ np.abs(X)
    bound = T.sum(axis=1).max() * (1 + 2 * gam(n + r + 20))
    return bound < 1, bound


def main(case, m, s, held_kinds=("omega", "tilt", "glide_slope", "dry_mass")):
    p = Params(**CASES[case])
    d = np.load(Path(__file__).parent / "results" / f"{case}.npz")
    U, G, sv = d["U"], d["G"], float(d["s"])
    # Interval trajectory and per-interval Jacobians of the exact RK4 map.
    x = [Iv(float(c)) for c in initial_state(p)]
    xs, A, B = [x], [], []
    for k in range(p.N):
        x, Jk = interval_step(p, x, U[k], G[k], sv)
        xs.append(x)
        A.append([row[:14] for row in Jk])
        B.append([row[14:17] for row in Jk])
    mids = np.array([[0.5 * sum(lo_hi(e)) for e in xk] for xk in xs])
    print(f"state enclosure width (max): {max(lo_hi(e)[1] - lo_hi(e)[0] for xk in xs for e in xk):.1e}")
    # Active path constraints, as check_lossless finds them on the interval midpoints.
    act, *_ = active_constraints(p, mids, U, G, sv)
    held = [(kind, k) for kind, k in act if k is not None and k > m and kind in held_kinds]
    # d x_k / d u_j for j < k, in interval arithmetic.
    sens = {}
    for j in range(p.N):
        Mj = B[j]
        sens[j + 1, j] = Mj
        for k in range(j + 1, p.N):
            Mj = imatmul(A[k], Mj)
            sens[k + 1, j] = Mj

    def grad(kind, k):
        xk = xs[k]
        gv = [Iv(0.0)] * 14
        if kind == "omega":
            nrm = iv.sqrt(xk[11] * xk[11] + xk[12] * xk[12] + xk[13] * xk[13])
            for i in (11, 12, 13):
                gv[i] = xk[i] / nrm
        elif kind == "tilt":
            nrm = iv.sqrt(xk[9] * xk[9] + xk[10] * xk[10])
            gv[9], gv[10] = xk[9] / nrm, xk[10] / nrm
        elif kind == "glide_slope":
            nrm = iv.sqrt(xk[2] * xk[2] + xk[3] * xk[3])
            tg = math.tan(p.gamma_gs)
            gv[2], gv[3], gv[1] = tg * xk[2] / nrm, tg * xk[3] / nrm, Iv(-1.0)
        elif kind == "dry_mass":
            gv[0] = Iv(-1.0)
        return gv

    tail = list(range(m, p.N))
    cols = {}
    for j in tail:
        rows = [sens[p.N, j][i] for i in TERM_IDX]
        for kind, k in held:
            if k > j:
                gk = grad(kind, k)
                rows.append([sum((gk[a] * sens[k, j][a][c] for a in range(14)), Iv(0.0))
                             for c in range(3)])
            else:
                rows.append([Iv(0.0)] * 3)
        cols[j] = mid_rad(rows)
    nrows = len(TERM_IDX) + len(held)
    total = ok = 0
    worst = 0.0
    for c in itertools.combinations(tail, s):
        Mm = np.hstack([cols[j][0] for j in c])
        Mr = np.hstack([cols[j][1] for j in c])
        good, bound = certify_full_row_rank(Mm, Mr)
        total += 1
        ok += good
        worst = max(worst, bound)
    above = [i for i in tail if G[i] - p.T_min > TOL_ACTIVE]
    print(f"{case}: m={m}, {len(held)} held, {nrows} rows, sets of {s} from nodes {m}..{p.N - 1}: "
          f"{ok}/{total} certified full rank (worst ||MX-I|| bound {worst:.2e}); "
          f"tail nodes with Gamma > T_min: {above}")
    return ok == total


if __name__ == "__main__":
    case, m, s = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    sys.exit(0 if main(case, m, s) else 1)
