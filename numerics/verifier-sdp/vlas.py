"""[verifier-sdp] Order-2 Lasserre (moment) relaxation of a QCQP from vqcqp (own implementation).
Moment matrix M_2(y) over monomials of degree <= 2 (PSD), localizing matrices M_1(g y) for each
inequality (PSD) and g*x^beta = 0 (|beta| <= 2) for each equality.  Objective degree 2.
Value >= Shor value; if > Shor + tol it certifies that the Shor relaxation is not exact
(as Lasserre-2 is itself a valid lower bound for the genuine problem)."""
import itertools
import numpy as np
import scipy.sparse as sp
import cvxpy as cp


def monos(m, d):
    out = [()]
    for k in range(1, d + 1):
        out += list(itertools.combinations_with_replacement(range(m), k))
    return out


def lasserre2(P, solver="CLARABEL", tol=1e-8, verbose=False):
    m = P.m
    B2 = monos(m, 2)
    B1 = monos(m, 1)
    all4 = monos(m, 4)
    idx = {a: i for i, a in enumerate(all4)}
    ny = len(all4)
    y = cp.Variable(ny)

    def key(*parts):
        return tuple(sorted(sum(parts, ())))

    def mat_from(basis, entry_fn):
        """entry_fn(a,b) -> list of (coef, mono); returns cvxpy expression for symmetric matrix."""
        n = len(basis)
        rows, cols, vals = [], [], []
        for i, a in enumerate(basis):
            for j, b in enumerate(basis):
                for c, mo in entry_fn(a, b):
                    rows.append(i * n + j); cols.append(idx[mo]); vals.append(c)
        A = sp.csr_matrix((vals, (rows, cols)), shape=(n * n, ny))
        return cp.reshape(A @ y, (n, n), order="C")

    def poly_terms(f):
        Q, q, c = f
        terms = []
        if c != 0:
            terms.append((c, ()))
        for i in range(m):
            if q[i] != 0:
                terms.append((2 * q[i], (i,)))
        nz = np.argwhere(Q != 0)
        for i, j in nz:
            terms.append((Q[i, j], key((i,), (j,))))
        return terms

    cons = [y[idx[()]] == 1]
    Mm = mat_from(B2, lambda a, b: [(1.0, key(a, b))])
    cons.append((Mm + Mm.T) / 2 >> 0)
    for (Q, q, c, kind) in P.cons:
        t = poly_terms((Q, q, c))
        if kind == ">=":
            L = mat_from(B1, lambda a, b: [(cf, key(mo, a, b)) for cf, mo in t])
            cons.append((L + L.T) / 2 >> 0)
        else:
            for beta in B2:
                cons.append(sum(cf * y[idx[key(mo, beta)]] for cf, mo in t) == 0)
    obj = sum(cf * y[idx[mo]] for cf, mo in poly_terms(P.obj))
    pr = cp.Problem(cp.Minimize(obj), cons)
    if solver == "CLARABEL":
        pr.solve(solver="CLARABEL", tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500, verbose=verbose)
    else:
        pr.solve(solver="SCS", eps_abs=tol, eps_rel=tol, max_iters=200000, verbose=verbose)
    return dict(val=float(pr.value) if pr.value is not None else np.nan, status=pr.status, ny=ny,
                size=len(B2))
