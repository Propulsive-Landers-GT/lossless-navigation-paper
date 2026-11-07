"""redteam-lift: is the Shor gap explained by genuinely higher-dimensional trajectories?
NLP in R^n (n=3,4,5) for the same (wv,wr) target embedded in R^3 x {0}."""
import sys, numpy as np, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dimlift import build
from csd2_deep import targets, sdp_rv

def nlp_n(n, wv, wr, N, tf, om, dl, a1=5.0, starts=60, seed=5):
    x, dv, g, lb, ub, lbx, ubx = build(n, N, tf, om, dl, a1, a1, False); h = tf / N
    Dm = ca.reshape(x[n * (N + 1):n * (N + 1) + n * N], n, N)
    dr = ca.mtimes(Dm, ca.DM(h * a1 * (tf - (np.arange(N) + 0.5) * h)))
    Wv = np.r_[wv, np.zeros(n - 3)]; Wr = np.r_[wr, np.zeros(n - 3)]
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": ca.sumsqr(dv - Wv) + ca.sumsqr(dr - Wr), "g": ca.vertcat(*g)},
                  {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 5000, "ipopt.tol": 1e-12, "ipopt.sb": "yes"})
    rng = np.random.default_rng(seed); s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); best = None
    for t in range(starts):
        sc = rng.uniform(0.0, 1.0)
        lat = rng.normal(size=(n - 1, 1)) + rng.normal(size=(n - 1, 1)) * (s / tf) + rng.normal(size=(n - 1, 1)) * (s / tf) ** 2
        lat /= np.linalg.norm(lat, axis=0, keepdims=True)
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * lat])
        D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
        r = S(x0=np.r_[B0.T.ravel(), D0.T.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
        if S.stats()["return_status"] in ("Solve_Succeeded", "Solved_To_Acceptable_Level"):
            fv = float(r["f"]); best = fv if best is None or fv < best else best
    return best

if __name__ == "__main__":
    for ci, lab in [(0, "rand0"), (1, "rand1")]:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l != lab: continue
            v = sdp_rv(wv, wr, N, tf, om, dl)[0]
            res = {n: nlp_n(n, wv, wr, N, tf, om, dl) for n in (3, 4, 5)}
            print(f"cfg{ci} {lab}: SDP={v:.6e}  NLP n=3:{res[3]:.6e} n=4:{res[4]:.6e} n=5:{res[5]:.6e}", flush=True)
