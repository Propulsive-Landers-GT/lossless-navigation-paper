"""redteam-lift: rank-3 extraction -> strictly feasible contraction -> IPOPT polish from inside -> genuine upper bound."""
import sys, numpy as np, cvxpy as cp, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rankred import build as sdpbuild
from dimlift import build as nlpbuild
from csd2_deep import targets
from certify2 import contract, check

def run(wv, wr, N, tf, om, dl, a1=5.0):
    G, cons, obj = sdpbuild(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value; Gv = G.value
    for it in range(8):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + 1e-8 * max(abs(v), 1e-3)]); q.solve(solver=cp.CLARABEL); Gv = G.value
        if np.sort(np.linalg.eigvalsh(Gv))[::-1][3] < 1e-9: break
    nb = N + 1; h = tf / N
    Bn = np.array([Gv[3 + k, :3] for k in range(nb)]); Dn = np.array([Gv[3 + nb + k, :3] for k in range(N)])
    Bn /= np.linalg.norm(Bn, axis=1, keepdims=True); Dn /= np.linalg.norm(Dn, axis=1, keepdims=True); Bn[0] = Bn[N] = [1, 0, 0]
    x, dv, g, lb, ub, lbx, ubx = nlpbuild(3, N, tf, om, dl, a1, a1, False)
    Dm = ca.reshape(x[3 * nb:3 * nb + 3 * N], 3, N); dr = ca.mtimes(Dm, ca.DM(h * a1 * (tf - (np.arange(N) + 0.5) * h)))
    f = ca.sumsqr(dv - wv) + ca.sumsqr(dr - wr); gg = ca.vertcat(*g); Gf = ca.Function("G", [x], [gg])
    best = np.inf
    for eps in [1e-3, 3e-3, 1e-2]:
        B2, D2 = contract(Bn, eps), contract(Dn, eps)
        if check(B2, D2, N, tf, om, dl) > 0: continue
        for mu in (1e-1, 1e-4, 1e-8):
            S = ca.nlpsol("s", "ipopt", {"x": x, "f": f, "g": gg}, {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-12, "ipopt.sb": "yes", "ipopt.mu_init": mu})
            r = S(x0=np.r_[B2.ravel(), D2.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
            xv = np.array(r["x"]).ravel(); gv = np.array(Gf(xv)).ravel()
            viol = float(np.max(np.maximum(np.array(lb) - gv, 0) + np.maximum(gv - np.array(ub), 0)))
            if viol < 1e-9: best = min(best, float(r["f"]))
    return v, best

if __name__ == "__main__":
    jobs = [(0, "rand0"), (0, "rand2"), (1, "rand0"), (1, "rand1"), (1, "rand2")]
    for ci, lab in jobs:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab:
                v, up = run(wv, wr, N, tf, om, dl)
                print(f"CERT3 cfg{ci} {lab} N={N}: SDP lower={v:.8e}  genuine upper={up:.8e}  relgap={(up - v) / up:.1e}", flush=True)
