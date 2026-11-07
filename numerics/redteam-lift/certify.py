"""redteam-lift: certificate pipeline for C-SD2: SDP -> rank reduction on optimal face -> rank-3 extraction ->
exact-feasibility NLP polish (ipopt) -> report [lower bound SDP, upper bound genuine cost]."""
import sys, numpy as np, cvxpy as cp, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rankred import build as sdpbuild
from dimlift import build as nlpbuild
from csd2_deep import targets

def certify(wv, wr, N, tf, om, dl, a1=5.0):
    G, cons, obj = sdpbuild(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value; Gv = G.value
    for it in range(6):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + 1e-7 * max(abs(v), 1e-3)]); q.solve(solver=cp.CLARABEL); Gv = G.value
        if np.sort(np.linalg.eigvalsh(Gv))[::-1][3] < 1e-8: break
    e4 = np.sort(np.linalg.eigvalsh(Gv))[::-1][3]
    nb = N + 1; h = tf / N
    Bx = np.array([Gv[3 + k, :3] for k in range(nb)]); Dx = np.array([Gv[3 + nb + k, :3] for k in range(N)])
    Bn = Bx / np.linalg.norm(Bx, axis=1, keepdims=True); Dn = Dx / np.linalg.norm(Dx, axis=1, keepdims=True)
    Bn[0] = Bn[N] = [1, 0, 0]
    x, dv, g, lb, ub, lbx, ubx = nlpbuild(3, N, tf, om, dl, a1, a1, False)
    Dm = ca.reshape(x[3 * nb:3 * nb + 3 * N], 3, N); dr = ca.mtimes(Dm, ca.DM(h * a1 * (tf - (np.arange(N) + 0.5) * h)))
    f = ca.sumsqr(dv - wv) + ca.sumsqr(dr - wr); gg = ca.vertcat(*g)
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": f, "g": gg}, {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-12, "ipopt.sb": "yes"})
    r = S(x0=np.r_[Bn.ravel(), Dn.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
    gv = np.array(ca.Function("G", [x], [gg])(r["x"])).ravel()
    viol = float(np.max(np.maximum(np.array(lb) - gv, 0) + np.maximum(gv - np.array(ub), 0)))
    return v, e4, float(r["f"]), viol, S.stats()["return_status"]

if __name__ == "__main__":
    for ci, lab in [(0, "rand0"), (1, "rand1"), (1, "rand2")]:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab:
                v, e4, up, viol, st = certify(wv, wr, N, tf, om, dl)
                print(f"CERT cfg{ci} {lab} N={N}: SDP(lower)={v:.8e}  rank-red eig4={e4:.1e}  genuine polished(upper)={up:.8e} viol={viol:.1e} [{st}]  relgap={(up-v)/up:.1e}", flush=True)
