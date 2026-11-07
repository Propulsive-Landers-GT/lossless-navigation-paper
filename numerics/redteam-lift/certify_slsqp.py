"""redteam-lift: SLSQP (active-set SQP, robust to degenerate active sets) polish of the rank-3 extraction.
Reports a genuine feasible (to 1e-10) trajectory cost = upper bound, vs SDP lower bound."""
import sys, numpy as np, cvxpy as cp
from scipy.optimize import minimize
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rankred import build as sdpbuild
from csd2_deep import targets

def extract(wv, wr, N, tf, om, dl):
    G, cons, obj = sdpbuild(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value; Gv = G.value
    for it in range(8):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + 1e-8 * max(abs(v), 1e-3)]); q.solve(solver=cp.CLARABEL); Gv = G.value
        if np.sort(np.linalg.eigvalsh(Gv))[::-1][3] < 1e-9: break
    nb = N + 1
    Bn = np.array([Gv[3 + k, :3] for k in range(nb)]); Dn = np.array([Gv[3 + nb + k, :3] for k in range(N)])
    return v, Bn / np.linalg.norm(Bn, axis=1, keepdims=True), Dn / np.linalg.norm(Dn, axis=1, keepdims=True)

def polish(Bn, Dn, wv, wr, N, tf, om, dl, a1=5.0):
    h = tf / N; cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    nbi = N - 1   # interior b's
    def unpack(z):
        B = np.vstack([[1, 0, 0], z[:3 * nbi].reshape(nbi, 3), [1, 0, 0]]); D = z[3 * nbi:].reshape(N, 3); return B, D
    def f(z):
        B, D = unpack(z); return np.sum((cv @ D - wv) ** 2) + np.sum((cr @ D - wr) ** 2)
    def fgrad(z):
        B, D = unpack(z); ev = cv @ D - wv; er = cr @ D - wr
        gD = 2 * (np.outer(cv, ev) + np.outer(cr, er)); return np.r_[np.zeros(3 * nbi), gD.ravel()]
    def eq(z):
        B, D = unpack(z); return np.r_[np.sum(B[1:-1] ** 2, 1) - 1, np.sum(D ** 2, 1) - 1]
    def ineq(z):
        B, D = unpack(z)
        return np.r_[np.sum(B[:-1] * B[1:], 1) - np.cos(om * h), np.sum(D * B[:-1], 1) - np.cos(dl), np.sum(D * B[1:], 1) - np.cos(dl)]
    z0 = np.r_[Bn[1:-1].ravel(), Dn.ravel()]
    r = minimize(f, z0, jac=fgrad, method="SLSQP", constraints=[{"type": "eq", "fun": eq}, {"type": "ineq", "fun": ineq}],
                 options={"maxiter": 2000, "ftol": 1e-15})
    viol = max(np.abs(eq(r.x)).max(), max(0, -ineq(r.x).min()))
    return r.fun, viol, r.message

if __name__ == "__main__":
    jobs = [(0, "rand0"), (0, "rand2"), (0, "rand3"), (1, "rand0"), (1, "rand1"), (1, "rand2")]
    for ci, lab in jobs:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab:
                v, Bn, Dn = extract(wv, wr, N, tf, om, dl)
                up, viol, msg = polish(Bn, Dn, wv, wr, N, tf, om, dl)
                print(f"SLSQP cfg{ci} {lab} N={N}: SDP lower={v:.8e}  genuine upper={up:.8e} viol={viol:.1e}  relgap={(up - v) / up:.1e}  [{msg}]", flush=True)
