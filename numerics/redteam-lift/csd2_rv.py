"""redteam-lift: C-SD2 with position+velocity targets (full (r0,v0) landing data, fixed thrust a1, alpha=0),
rank/flatness check, and extraction.  Min-landing-error cost  ||Sv - wv||^2 + ||Sr - wr||^2  (lifted, linear in G).
Sv = sum h a1 d_k,  Sr = sum h a1 (tf - s_mid_k) d_k  (velocity/position increments, gravity removed).
Compare with multistart NLP (casadi/ipopt) on the true 3D problem. SDP <= true min <= NLP; equality certifies both."""
import sys, numpy as np, cvxpy as cp, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dimlift import build

def sdp_rv(wv, wr, N, tf, om, dl, a1, bfree=False):
    h = tf / N; nb = N + 1; nd = N; n = 3 + nb + nd
    G = cp.Variable((n, n), PSD=True)
    B = lambda k: 3 + k; D = lambda k: 3 + nb + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(3)]
    cons += [G[B(k), B(k)] == 1 for k in range(nb)] + [G[D(k), D(k)] == 1 for k in range(nd)]
    cons += [G[B(0), 0] == 1] + ([] if bfree else [G[B(N), 0] == 1])
    for k in range(N):
        cons += [G[B(k), B(k + 1)] >= np.cos(om * h), G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    di = [D(k) for k in range(nd)]
    cv = h * a1 * np.ones(nd); cr = h * a1 * (tf - (np.arange(nd) + 0.5) * h)
    def sq(c, w):   # ||sum c_k d_k - w||^2, linear in G
        Gd = G[np.ix_(di, di)]
        m = [cp.sum(cp.multiply(c, cp.hstack([G[D(k), i] for k in range(nd)]))) for i in range(3)]
        return cp.sum(cp.multiply(np.outer(c, c), Gd)) - 2 * sum(w[i] * m[i] for i in range(3)) + float(w @ w)
    pr = cp.Problem(cp.Minimize(sq(cv, wv) + sq(cr, wr)), cons)
    pr.solve(solver=cp.CLARABEL)
    ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]
    return pr.value, ev

def nlp_rv(wv, wr, N, tf, om, dl, a1, starts=12, seed=3, bfree=False):
    x, dv, g, lb, ub, lbx, ubx = build(3, N, tf, om, dl, a1, a1, False)
    if bfree:  # drop the last 3 equality rows (b_N = e_z): they are the final 3 of the 6 boundary rows, interleaved -> rebuild
        pass
    h = tf / N
    Dm = ca.reshape(x[3 * (N + 1):3 * (N + 1) + 3 * N], 3, N)
    cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    dr = ca.mtimes(Dm, ca.DM(cr))
    f = ca.sumsqr(dv - wv) + ca.sumsqr(dr - wr)
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": f, "g": ca.vertcat(*g)},
                  {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-11, "ipopt.sb": "yes"})
    rng = np.random.default_rng(seed); s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); best = None
    for t in range(starts):
        sc = rng.uniform(0.1, 1.0); ang = rng.uniform(0, 2 * np.pi) + rng.uniform(-4, 4) * s / tf
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * np.cos(ang), np.sin(sc * phi) * np.sin(ang)])
        D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
        r = S(x0=np.r_[B0.T.ravel(), D0.T.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
        if S.stats()["return_status"] in ("Solve_Succeeded", "Solved_To_Acceptable_Level"):
            fv = float(r["f"]); best = fv if best is None or fv < best else best
    return best

if __name__ == "__main__":
    a1 = 5.0
    cfgs = [(16, 4.0, 30, 15), (16, 3.0, 30, 40), (20, 5.0, 30, 15), (16, 6.0, 30, 15)]
    rng = np.random.default_rng(7)
    print("cfg(N,tf,om,dl) | target | SDP | NLP | eig4/eig1 (rank>3 indicator)")
    for N, tf, omd, dld in cfgs:
        om, dl = np.deg2rad(omd), np.deg2rad(dld); h = tf / N
        s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
        cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
        # midpoint-type targets: P_u and P_-u averaged (theta_M analog in (v,r)), plus random targets near/inside conv
        Mv = np.array([np.sum(h * a1 * np.cos(psi)), 0, 0]); Mr = np.array([np.sum(cr * np.cos(psi)), 0, 0])
        Pv = Mv + np.array([0, np.sum(h * a1 * np.sin(psi)), 0]); Pr = Mr + np.array([0, np.sum(cr * np.sin(psi)), 0])
        targets = [("theta_M", Mv, Mr), ("P_u", Pv, Pr)]
        for j in range(5):
            lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi)
            R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
            up = rng.uniform(0, 1.5)
            targets.append((f"rand{j}", lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]),
                            lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])))
        for lab, wv, wr in targets:
            v, ev = sdp_rv(wv, wr, N, tf, om, dl, a1)
            nl = nlp_rv(wv, wr, N, tf, om, dl, a1)
            print(f"({N},{tf},{omd},{dld}) | {lab:7s} | {v:.4e} | {nl:.4e} | {ev[3]/ev[0]:.1e}", flush=True)
