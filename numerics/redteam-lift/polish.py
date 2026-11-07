"""redteam-lift: robust 3D polish of the C-SD2 solution (warm-start ipopt with small mu/bound_push, report all statuses)
and many diverse multistarts.  Decides whether an apparent SDP<NLP gap is real or an NLP failure."""
import sys, numpy as np, casadi as ca
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from dimlift import build
import factor
N = int(sys.argv[1]); J = int(sys.argv[2]); NS = int(sys.argv[3]) if len(sys.argv) > 3 else 150
tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
rng = np.random.default_rng(0)
for j in range(J + 1):
    lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
    R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
    wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
val, G, cv, crr = factor.solve_G(wv, wr, N, tf, om, dl)
nb = N + 1; Bx = np.array([G[3 + k, :3] for k in range(nb)]); Dx = np.array([G[3 + nb + k, :3] for k in range(N)])
x, dv, g, lb, ub, lbx, ubx = build(3, N, tf, om, dl, a1, a1, False)
Dm = ca.reshape(x[3 * nb:3 * nb + 3 * N], 3, N); dr = ca.mtimes(Dm, ca.DM(cr))
f = ca.sumsqr(dv - wv) + ca.sumsqr(dr - wr)
opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 5000, "ipopt.tol": 1e-12, "ipopt.sb": "yes"}
S = ca.nlpsol("s", "ipopt", {"x": x, "f": f, "g": ca.vertcat(*g)}, opts)
Sw = ca.nlpsol("w", "ipopt", {"x": x, "f": f, "g": ca.vertcat(*g)}, dict(opts, **{"ipopt.warm_start_init_point": "yes", "ipopt.bound_push": 1e-10, "ipopt.bound_frac": 1e-10, "ipopt.mu_init": 1e-10}))
Gf = ca.Function("G", [x], [ca.vertcat(*g)]); Ff = ca.Function("F", [x], [f])
def viol(xv):
    gv = np.array(Gf(xv)).ravel(); return float(np.max(np.maximum(np.array(lb) - gv, 0) + np.maximum(gv - np.array(ub), 0)))
Bn = Bx / np.linalg.norm(Bx, axis=1, keepdims=True); Dn = Dx / np.linalg.norm(Dx, axis=1, keepdims=True)
x0 = np.r_[Bn.ravel(), Dn.ravel(), a1 * np.ones(N)]
print(f"N={N} j={J}: SDP={val:.8e}; projected traj: cost={float(Ff(x0)):.8e} viol={viol(x0):.1e}")
for name, solver in (("plain", S), ("warm", Sw)):
    r = solver(x0=x0, lbg=lb, ubg=ub, lbx=lbx, ubx=ubx); xv = np.array(r["x"]).ravel()
    print(f"  polish[{name}]: status={solver.stats()['return_status']} cost={float(r['f']):.8e} viol={viol(xv):.1e}")
best = (np.inf, None); r2 = np.random.default_rng(42)
for t in range(NS):
    sc = r2.uniform(0, 1); ang = r2.uniform(0, 2 * np.pi) + r2.uniform(-6, 6) * s / tf + np.cumsum(r2.normal(0, 0.4, N + 1))
    B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * np.cos(ang), np.sin(sc * phi) * np.sin(ang)])
    D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
    r = S(x0=np.r_[B0.T.ravel(), D0.T.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
    xv = np.array(r["x"]).ravel()
    if viol(xv) < 1e-8 and float(r["f"]) < best[0]: best = (float(r["f"]), S.stats()["return_status"])
print(f"  best feasible multistart ({NS}): {best[0]:.8e} [{best[1]}]")
