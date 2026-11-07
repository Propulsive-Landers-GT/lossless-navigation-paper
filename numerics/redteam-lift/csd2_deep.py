"""redteam-lift: deep check of C-SD2 at selected targets: SDP value vs (a) NLP with many multistarts,
(b) NLP warm-started from the SDP solution projected onto the constants' span (extraction)."""
import sys, numpy as np, cvxpy as cp, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dimlift import build

def targets(cfg_index_wanted, a1=5.0):
    cfgs = [(16, 4.0, 30, 15), (16, 3.0, 30, 40), (20, 5.0, 30, 15), (16, 6.0, 30, 15)]
    rng = np.random.default_rng(7); out = []
    for ci, (N, tf, omd, dld) in enumerate(cfgs):
        om, dl = np.deg2rad(omd), np.deg2rad(dld); h = tf / N
        s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
        cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
        Mv = np.array([np.sum(h * a1 * np.cos(psi)), 0, 0]); Mr = np.array([np.sum(cr * np.cos(psi)), 0, 0])
        Pv = Mv + np.array([0, np.sum(h * a1 * np.sin(psi)), 0]); Pr = Mr + np.array([0, np.sum(cr * np.sin(psi)), 0])
        for j in range(5):
            lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi)
            R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
            up = rng.uniform(0, 1.5)
            if ci == cfg_index_wanted:
                out.append((f"rand{j}", (N, tf, om, dl), lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]),
                            lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])))
    return out

def sdp_rv(wv, wr, N, tf, om, dl, a1=5.0):
    h = tf / N; nb = N + 1; nd = N; n = 3 + nb + nd
    G = cp.Variable((n, n), PSD=True); B = lambda k: 3 + k; D = lambda k: 3 + nb + k
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(3)]
    cons += [G[B(k), B(k)] == 1 for k in range(nb)] + [G[D(k), D(k)] == 1 for k in range(nd)]
    cons += [G[B(0), 0] == 1, G[B(N), 0] == 1]
    for k in range(N):
        cons += [G[B(k), B(k + 1)] >= np.cos(om * h), G[D(k), B(k)] >= np.cos(dl), G[D(k), B(k + 1)] >= np.cos(dl)]
    di = [D(k) for k in range(nd)]
    cv = h * a1 * np.ones(nd); cr = h * a1 * (tf - (np.arange(nd) + 0.5) * h)
    def sq(c, w):
        m = [cp.sum(cp.multiply(c, cp.hstack([G[D(k), i] for k in range(nd)]))) for i in range(3)]
        return cp.sum(cp.multiply(np.outer(c, c), G[np.ix_(di, di)])) - 2 * sum(w[i] * m[i] for i in range(3)) + float(w @ w)
    pr = cp.Problem(cp.Minimize(sq(cv, wv) + sq(cr, wr)), cons); pr.solve(solver=cp.CLARABEL)
    Gv = G.value
    Bx = np.array([Gv[B(k), :3] for k in range(nb)]); Dx = np.array([Gv[D(k), :3] for k in range(nd)])
    return pr.value, Bx, Dx, np.sort(np.linalg.eigvalsh(Gv))[::-1]

def nlp(wv, wr, N, tf, om, dl, a1=5.0, starts=0, warm=None, seed=11):
    x, dv, g, lb, ub, lbx, ubx = build(3, N, tf, om, dl, a1, a1, False); h = tf / N
    Dm = ca.reshape(x[3 * (N + 1):3 * (N + 1) + 3 * N], 3, N)
    dr = ca.mtimes(Dm, ca.DM(h * a1 * (tf - (np.arange(N) + 0.5) * h)))
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": ca.sumsqr(dv - wv) + ca.sumsqr(dr - wr), "g": ca.vertcat(*g)},
                  {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 5000, "ipopt.tol": 1e-12, "ipopt.sb": "yes"})
    inits = []
    if warm is not None:
        Bx, Dx = warm
        Bn = Bx / np.linalg.norm(Bx, axis=1, keepdims=True); Dn = Dx / np.linalg.norm(Dx, axis=1, keepdims=True)
        inits.append(np.r_[Bn.ravel(), Dn.ravel(), a1 * np.ones(N)])
    rng = np.random.default_rng(seed); s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s)
    for t in range(starts):
        sc = rng.uniform(0.0, 1.0); ang = rng.uniform(0, 2 * np.pi) + rng.uniform(-6, 6) * s / tf + rng.normal(0, 0.5, N + 1).cumsum() * 0.2
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * np.cos(ang), np.sin(sc * phi) * np.sin(ang)])
        D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
        inits.append(np.r_[B0.T.ravel(), D0.T.ravel(), a1 * np.ones(N)])
    best = None
    for x0 in inits:
        r = S(x0=x0, lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
        if S.stats()["return_status"] in ("Solve_Succeeded", "Solved_To_Acceptable_Level"):
            fv = float(r["f"]); best = fv if best is None or fv < best else best
    return best

if __name__ == "__main__":
    ci = int(sys.argv[1]); which = sys.argv[2].split(",")
    for lab, (N, tf, om, dl), wv, wr in targets(ci):
        if lab not in which: continue
        v, Bx, Dx, ev = sdp_rv(wv, wr, N, tf, om, dl)
        w = nlp(wv, wr, N, tf, om, dl, warm=(Bx, Dx))
        m = nlp(wv, wr, N, tf, om, dl, starts=80)
        print(f"cfg{ci} {lab}: SDP={v:.6e}  NLP(warm from SDP)={w}  NLP(80 starts)={m}  eig[:6]={np.round(ev[:6],4)}", flush=True)
