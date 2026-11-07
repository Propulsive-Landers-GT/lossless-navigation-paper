"""redteam-lift: (E1) dimension-invariance test for the Dirac-lifted Shor relaxation C-SD2,
(E3) min-fuel convex-envelope test (does extra throttle reach axis points below the min-throttle axis point?).
Velocity-only, alpha=0, tent attitude b0=bN=e_z, inner discretization (d_k within delta of b_k and b_{k+1}).
Coordinate 0 = vertical; coordinates 1..n-1 lateral.  n=3 is the real problem; n>3 = Shor/Hilbert-sphere lift."""
import sys, numpy as np, casadi as ca

def build(n, N, tf, om, dl, a1, a2, throttle):
    h = tf / N
    B = ca.SX.sym("B", n, N + 1); D = ca.SX.sym("D", n, N); A = ca.SX.sym("A", N)
    g, lb, ub = [], [], []
    def add(e, l, u): g.append(e); lb.append(l); ub.append(u)
    for k in range(N + 1):
        add(ca.dot(B[:, k], B[:, k]), 1, 1)
    for k in range(N):
        add(ca.dot(D[:, k], D[:, k]), 1, 1)
        add(ca.dot(B[:, k], B[:, k + 1]), np.cos(om * h), 2)
        add(ca.dot(D[:, k], B[:, k]), np.cos(dl), 2)
        add(ca.dot(D[:, k], B[:, k + 1]), np.cos(dl), 2)
    ez = np.zeros(n); ez[0] = 1
    for i in range(n):
        add(B[i, 0], ez[i], ez[i]); add(B[i, N], ez[i], ez[i])
    a = A if throttle else a1 * ca.DM.ones(N)
    dv = h * ca.mtimes(D, a)
    x = ca.vertcat(ca.vec(B), ca.vec(D), A)
    lbx = np.r_[-np.ones(n * (N + 1) + n * N) * 1.5, a1 * np.ones(N)]
    ubx = np.r_[np.ones(n * (N + 1) + n * N) * 1.5, (a2 if throttle else a1) * np.ones(N)]
    return x, dv, g, lb, ub, lbx, ubx

def solve_axis(n, N, tf, om, dl, a1, a2, throttle, starts, seed=0, zfix=None):
    """zfix None: min dv_z s.t. dv_lat=0.  zfix=z: min |dv_lat|^2 s.t. dv_z=z."""
    x, dv, g, lb, ub, lbx, ubx = build(n, N, tf, om, dl, a1, a2, throttle)
    g = list(g); lb = list(lb); ub = list(ub)
    if zfix is None:
        for i in range(1, n): g.append(dv[i]); lb.append(0); ub.append(0)
        f = dv[0]
    else:
        g.append(dv[0]); lb.append(zfix); ub.append(zfix)
        f = ca.sumsqr(dv[1:])
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": f, "g": ca.vertcat(*g)},
                  {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-10, "ipopt.sb": "yes"})
    rng = np.random.default_rng(seed); best = None
    h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s)
    for t in range(starts):
        # initial guess: tilt profile scaled, lateral direction curve = random smooth curve on S^{n-2}
        sc = rng.uniform(0.3, 1.0)
        w = rng.normal(size=(n - 1, 4))
        lat = np.array([w[:, 0] * np.cos(2 * np.pi * rng.uniform() * si / tf * rng.integers(0, 3)) + w[:, 1] * np.sin(np.pi * si / tf * rng.integers(0, 3)) + 0.3 * w[:, 2] for si in s]).T
        lat /= np.linalg.norm(lat, axis=0, keepdims=True) + 1e-12
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * lat])
        D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
        A0 = a1 * np.ones(N) if not throttle else rng.uniform(a1, a2, N)
        x0 = np.r_[B0.T.ravel(), D0.T.ravel(), A0]
        r = S(x0=x0, lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
        st = S.stats()["return_status"]
        if st not in ("Solve_Succeeded", "Solved_To_Acceptable_Level"): continue
        fv = float(r["f"])
        if best is None or fv < best: best = fv
    return best

if __name__ == "__main__":
    a1, a2 = 400 / 80, 1000 / 80
    dl = np.deg2rad(float(sys.argv[3]) if len(sys.argv) > 3 else 15); om = np.deg2rad(30); tf = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0; N = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    starts = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s)
    psi = dl + np.minimum(phi[:-1], phi[1:])
    zmin = np.sum(h * a1 * np.cos(psi)); c = np.sum(h * a1 * np.sin(psi))
    print(f"N={N} zmin(M_z)={zmin:.5f} c(P lateral)={c:.5f} a1*tf={a1*tf:.4f}")
    res = {}
    for (n, thr) in [(3, False), (4, False), (5, False), (3, True)]:
        res[(n, thr)] = solve_axis(n, N, tf, om, dl, a1, a2, thr, starts)
        print(f"E axis-lowest  n={n} throttle={thr}:  z_c = {res[(n,thr)]}", flush=True)
    z3 = res[(3, False)]
    for frac in [0.25, 0.5, 0.75]:
        z = zmin + frac * (z3 - zmin)
        r3 = solve_axis(3, N, tf, om, dl, a1, a2, False, starts, zfix=z)
        r4 = solve_axis(4, N, tf, om, dl, a1, a2, False, starts, zfix=z)
        r3t = solve_axis(3, N, tf, om, dl, a1, a2, True, starts, zfix=z)
        print(f"E inner-radius at z={z:.4f}: n=3 rho_in={np.sqrt(r3):.5f}  n=4 rho_in={np.sqrt(r4):.5f}  n=3+throttle rho_in={np.sqrt(r3t):.5f}", flush=True)
