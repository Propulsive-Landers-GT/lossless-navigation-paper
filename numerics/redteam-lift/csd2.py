"""redteam-lift: direct test of candidate C-SD2 (per-instance Dirac-lifted Shor / Hilbert-sphere SDP).
Fixed thrust a1, alpha=0, tent attitude, velocity-only.  For target w=(z, rho, 0) (index 0 vertical):
  SDP value  q(w) = min E||Sigma - w||^2  over the Gram G of {e_0,e_1,e_2, b_0..b_N, d_0..d_{N-1}} (PSD, consts orthonormal)
  vs the uniform Shor (first-moment only)  q1(w) = min ||P_R3 Sigma - w||^2.
C-SD2 is lossless iff q(w)=0 <=> w in R (the true reachable set). Compare with NLP dist^2(w,R) from dimlift.py."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import casadi as ca

def sdp(w, N=16, tf=4.0, om=np.deg2rad(30), dl=np.deg2rad(15), a1=5.0, uniform=False):
    h = tf / N; nb = N + 1; nd = N; n = 3 + nb + nd
    G = cp.Variable((n, n), PSD=True)
    E = lambda i: i; Bk = lambda k: 3 + k; Dk = lambda k: 3 + nb + k
    cons = [G[i, j] == (1.0 if i == j else 0.0) for i in range(3) for j in range(3)]
    cons += [G[Bk(k), Bk(k)] == 1 for k in range(nb)] + [G[Dk(k), Dk(k)] == 1 for k in range(nd)]
    cons += [G[Bk(0), 0] == 1, G[Bk(N), 0] == 1]
    for k in range(N):
        cons += [G[Bk(k), Bk(k + 1)] >= np.cos(om * h), G[Dk(k), Bk(k)] >= np.cos(dl), G[Dk(k), Bk(k + 1)] >= np.cos(dl)]
    c = h * a1
    di = [Dk(k) for k in range(nd)]
    mean = [c * cp.sum(cp.hstack([G[Dk(k), i] for k in range(nd)])) for i in range(3)]   # <Sigma, e_i>
    if uniform:
        obj = cp.sum_squares(cp.hstack(mean) - w)
    else:
        SS = c * c * cp.sum(G[np.ix_(di, di)])                                          # ||Sigma||^2
        obj = SS - 2 * sum(w[i] * mean[i] for i in range(3)) + float(w @ w)
    pr = cp.Problem(cp.Minimize(obj), cons)
    pr.solve(solver=cp.CLARABEL)
    return pr.value

def nlp_dist2(w, N=16, tf=4.0, om=np.deg2rad(30), dl=np.deg2rad(15), a1=5.0, starts=10, seed=1):
    from dimlift import build
    x, dv, g, lb, ub, lbx, ubx = build(3, N, tf, om, dl, a1, a1, False)
    S = ca.nlpsol("s", "ipopt", {"x": x, "f": ca.sumsqr(dv - w), "g": ca.vertcat(*g)},
                  {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-10, "ipopt.sb": "yes"})
    rng = np.random.default_rng(seed); h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); best = None
    for t in range(starts):
        sc = rng.uniform(0.2, 1.0); ang = rng.uniform(0, 2*np.pi) + rng.uniform(-3, 3) * s / tf
        B0 = np.vstack([np.cos(sc * phi), np.sin(sc * phi) * np.cos(ang), np.sin(sc * phi) * np.sin(ang)])
        D0 = 0.5 * (B0[:, :-1] + B0[:, 1:]); D0 /= np.linalg.norm(D0, axis=0)
        r = S(x0=np.r_[B0.T.ravel(), D0.T.ravel(), a1 * np.ones(N)], lbg=lb, ubg=ub, lbx=lbx, ubx=ubx)
        if S.stats()["return_status"] in ("Solve_Succeeded", "Solved_To_Acceptable_Level"):
            fv = float(r["f"]); best = fv if best is None or fv < best else best
    return best

if __name__ == "__main__":
    N = 16; tf = 4.0; a1 = 5.0; h = tf / N
    s = np.arange(N + 1) * h; phi = np.deg2rad(30) * np.minimum(s, tf - s)
    psi = np.deg2rad(15) + np.minimum(phi[:-1], phi[1:])
    Mz = np.sum(h * a1 * np.cos(psi)); c = np.sum(h * a1 * np.sin(psi))
    tests = [("theta_M", Mz, 0.0), ("P_u", Mz, c)]
    for z, rin in [(15.8950, 4.94553), (16.6579, 2.87769)]:
        for f in [0.0, 0.5, 0.9, 0.98, 1.02, 1.2]:
            tests.append((f"z={z} rho={f:.2f}*rho_in", z, f * rin))
    print("label | SDP C-SD2 q(w) | uniform Shor q1(w) | NLP dist^2(w,R)")
    for lab, z, rho in tests:
        w = np.array([z, rho, 0.0])
        print(f"{lab:28s} | {sdp(w):.3e} | {sdp(w, uniform=True):.3e} | {nlp_dist2(w):.3e}", flush=True)
