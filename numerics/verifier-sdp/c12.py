"""[verifier-sdp] Independent reproduction of [numerics] CSD2 'case 12' and a hard search for a 3-D
trajectory beating it.

Model (matches numerics/models.py ReachM1 'inner', alpha=0): N=16, tf=4, omega=30 deg/s, delta=15 deg,
a=11 const.  Nodes b_0..b_N, b_0=b_N=e_z, <b_k,b_k+1> >= cos(omega h).  Thrust d_k on [t_k,t_k+1),
k=0..N-1, <d_k,b_k> >= cos delta and <d_k,b_k+1> >= cos delta.  dv = sum a h d_k,
dr = sum a h (tf-(k+.5)h) d_k.  cost |dv-wv|^2 + |dr-wr|^2.

Usage: python c12.py [nstart]
"""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import cvxpy as cp
import casadi as ca

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
N, TF, OM, DEL, A = 16, 4.0, np.deg2rad(30.0), np.deg2rad(15.0), 11.0
WV = np.array([5.0939, 21.9914, 32.1819])
WR = np.array([8.2825, 44.1701, 64.908])
H = TF / N
CR = np.cos(OM * H)
CD = np.cos(DEL)
GV = A * H * np.ones(N)
GR = A * H * (TF - (np.arange(N) + 0.5) * H)


def model_args(both=True, delta=DEL):
    return dict(both=both, cd=np.cos(delta))


# ------------------------------------------------------------------ Gram SDP
def gram_sdp(wv=WV, wr=WR, both=True, delta=DEL, solver="CLARABEL", tol=1e-9):
    nb = N - 1                         # b_1..b_{N-1}
    n = nb + N                         # + d_0..d_{N-1}
    Z = cp.Variable((n + 3, n + 3), symmetric=True)
    ib = lambda k: k - 1
    idd = lambda k: nb + k
    ez = n + 2
    cd = np.cos(delta)
    cons = [Z >> 0, Z[n:, n:] == np.eye(3), cp.diag(Z[:n, :n]) == 1]

    def bvec_dot_d(k, j):              # <b_k, d_j>
        if 1 <= k <= nb:
            return Z[ib(k), idd(j)]
        return Z[idd(j), ez]           # b_0 = b_N = e_z

    for k in range(N):
        if k == 0:
            cons.append(Z[ib(1), ez] >= CR)
        elif k == N - 1:
            cons.append(Z[ib(N - 1), ez] >= CR)
        else:
            cons.append(Z[ib(k), ib(k + 1)] >= CR)
    for k in range(N):
        cons.append(bvec_dot_d(k, k) >= cd)
        if both:
            cons.append(bvec_dot_d(k + 1, k) >= cd)
    D = slice(nb, n)
    G = Z[D, D]; X = Z[D, n:]
    obj = (GV @ G @ GV - 2 * GV @ X @ wv + wv @ wv) + (GR @ G @ GR - 2 * GR @ X @ wr + wr @ wr)
    pr = cp.Problem(cp.Minimize(obj), cons)
    if solver == "CLARABEL":
        pr.solve(solver="CLARABEL", tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500)
    else:
        pr.solve(solver="SCS", eps_abs=tol, eps_rel=tol, max_iters=400000)
    Zv = Z.value
    ev = np.linalg.eigvalsh(Zv)[::-1]
    return dict(val=float(pr.value), status=pr.status, Z=Zv, ev=ev, n=n, nb=nb)


def factor_aligned(Zv, n):
    """vectors (columns) in R^r with e_1,e_2,e_3 mapped to the first three standard axes."""
    w, V = np.linalg.eigh(Zv)
    keep = w > 1e-7 * w.max()
    F = (V[:, keep] * np.sqrt(w[keep])).T          # r x (n+3)
    E = F[:, n:]                                   # r x 3, orthonormal columns
    Qf, _ = np.linalg.qr(np.hstack([E, np.random.default_rng(0).normal(size=(F.shape[0], F.shape[0]))]))
    Qf[:, :3] = E                                  # make the first three exactly E
    Qf, _ = np.linalg.qr(Qf)
    Qf[:, :3] *= np.sign(np.sum(Qf[:, :3] * E, 0))
    C = Qf.T @ F                                   # coordinates
    return C                                       # r x (n+3), e's -> standard axes


# ------------------------------------------------------------------ NLP in R^dim (dim=3 genuine; dim=4 with penalty)
class NLP:
    def __init__(self, dim=3, both=True, delta=DEL, wv=WV, wr=WR):
        self.dim = dim
        nb = N - 1
        x = ca.SX.sym("x", dim * (nb + N))
        lam = ca.SX.sym("lam")
        Bf = ca.reshape(x[:dim * nb], dim, nb)
        Dm = ca.reshape(x[dim * nb:], dim, N)
        ez = ca.DM([0, 0, 1] + [0] * (dim - 3))
        B = ca.horzcat(ez, Bf, ez)                 # dim x (N+1)
        dv = ca.mtimes(Dm, ca.DM(GV)); dr = ca.mtimes(Dm, ca.DM(GR))
        tv = ca.DM(list(wv) + [0] * (dim - 3)); tr = ca.DM(list(wr) + [0] * (dim - 3))
        f = ca.sumsqr(dv - tv) + ca.sumsqr(dr - tr)
        if dim > 3:
            f = f + lam * (ca.sumsqr(Bf[3:, :]) + ca.sumsqr(Dm[3:, :]))
        g, lb, ub = [], [], []
        cd = np.cos(delta)
        for k in range(1, N):
            g.append(ca.sumsqr(B[:, k])); lb.append(1); ub.append(1)
        for k in range(N):
            g.append(ca.sumsqr(Dm[:, k])); lb.append(1); ub.append(1)
            g.append(ca.dot(B[:, k], B[:, k + 1])); lb.append(CR); ub.append(ca.inf)
            g.append(ca.dot(Dm[:, k], B[:, k])); lb.append(cd); ub.append(ca.inf)
            if both:
                g.append(ca.dot(Dm[:, k], B[:, k + 1])); lb.append(cd); ub.append(ca.inf)
        self.lb, self.ub = lb, ub
        opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.tol": 1e-12, "ipopt.sb": "yes",
                "ipopt.constr_viol_tol": 1e-11, "ipopt.max_iter": 3000}
        self.S = ca.nlpsol("S", "ipopt", {"x": x, "p": lam, "f": f, "g": ca.vertcat(*g)}, opts)
        self.gf = ca.Function("g", [x], [ca.vertcat(*g)])
        f3 = ca.sumsqr(dv[:3] - tv[:3]) + ca.sumsqr(dr[:3] - tr[:3])
        self.f3 = ca.Function("f3", [x], [f3])
        self.ff = ca.Function("f", [x], [ca.sumsqr(dv - tv) + ca.sumsqr(dr - tr)])

    def solve(self, x0, lam=0.0):
        r = self.S(x0=x0, p=lam, lbg=self.lb, ubg=self.ub)
        x = np.array(r["x"]).ravel()
        gv = np.array(self.gf(x)).ravel()
        viol = max(0.0, np.max(np.array(self.lb) - gv), np.max(gv - np.array(self.ub, float)))
        return x, float(self.ff(x)), viol, self.S.stats()["return_status"]


def pack(Bfree, Dm):        # Bfree: (N-1, dim), Dm: (N, dim)
    return np.r_[Bfree.ravel(), Dm.ravel()]


def unpack(x, dim):
    nb = N - 1
    return x[:dim * nb].reshape(nb, dim), x[dim * nb:].reshape(N, dim)


def to3(x, dim):
    Bf, Dm = unpack(x, dim)
    Bf = Bf[:, :3] / np.linalg.norm(Bf[:, :3], axis=1, keepdims=True)
    Dm = Dm[:, :3] / np.linalg.norm(Dm[:, :3], axis=1, keepdims=True)
    return pack(Bf, Dm)


def random_start(rng):
    kk = np.arange(N + 1)
    s = rng.uniform(0.1, 1.0)
    phi = s * np.minimum(kk, N - kk) * OM * H
    mode = rng.integers(4)
    psi0 = rng.uniform(0, 2 * np.pi)
    if mode == 0:
        psi = psi0 * np.ones(N + 1)
    elif mode == 1:
        psi = psi0 + rng.uniform(-np.pi, np.pi) * np.linspace(0, 1, N + 1)
    elif mode == 2:
        psi = psi0 + np.cumsum(rng.normal(0, 0.4, N + 1))
    else:
        phi = s * np.minimum(kk, N - kk) * OM * H * rng.uniform(0, 1, N + 1)
        psi = psi0 + rng.uniform(-3, 3) * np.linspace(0, 1, N + 1) ** 2
    B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
    D = B[:N] + rng.uniform(0, 1) * np.sin(DEL) * rng.normal(size=(N, 3))
    # lean toward the target direction sometimes
    if rng.uniform() < 0.5:
        tgt = WV / np.linalg.norm(WV)
        D = D + rng.uniform(0, 0.4) * tgt
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    return pack(B[1:N], D)


if __name__ == "__main__":
    nstart = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    out = {}
    t0 = time.time()
    # --- SDP, both solvers, and model variants
    s = gram_sdp(); s2 = gram_sdp(solver="SCS", tol=1e-8)
    print(f"SDP Gram (inner, both): Clarabel {s['val']:.9f} [{s['status']}]  SCS {s2['val']:.9f} [{s2['status']}]")
    print("  eig:", np.round(s["ev"][:7], 5))
    out["sdp"] = dict(clarabel=s["val"], st=s["status"], scs=s2["val"], st_scs=s2["status"], ev=s["ev"][:8].tolist())
    # cross-check with full (non-isotropic) Shor via vqcqp
    from vext import fixed_thrust
    F = fixed_thrust(N, TF, OM, np.array([WR, WV]), readout="rv", delta=DEL, accel=np.full(N + 1, A), both=True)
    sf = F.sdp()
    print(f"SDP full Shor (vqcqp): {sf['val']:.9f} [{sf['status']}] rank {sf['rank']}")
    out["sdp_fullshor"] = sf["val"]
    for both in (False,):
        sv = gram_sdp(both=both)
        print(f"variant both={both}: SDP {sv['val']:.9f}")

    # --- genuine 3-D search
    rng = np.random.default_rng(12)
    nlp3 = NLP(3)
    best = (np.inf, None)
    fs = []
    # (i) SDP-derived: aligned factor projected to R^3, and random projections of the 4th+ coords
    C = factor_aligned(s["Z"], s["n"])
    r = C.shape[0]
    nb = N - 1
    Bc = C[:, :nb].T; Dc = C[:, nb:nb + N].T          # (., r)
    sdp_starts = []
    for j in range(60):
        if j == 0:
            R = np.zeros((3, r)); R[:, :3] = np.eye(3)
        else:
            # random orthogonal map R^r -> R^3 (any 3-frame; cost not invariant, so polishing decides)
            Mx = rng.normal(size=(r, r)); Qm, _ = np.linalg.qr(Mx)
            R = Qm[:3] if j % 2 else np.hstack([np.eye(3), rng.normal(0, 1, (3, r - 3))])
        Bs = Bc @ R.T; Ds = Dc @ R.T
        Bs /= np.linalg.norm(Bs, axis=1, keepdims=True); Ds /= np.linalg.norm(Ds, axis=1, keepdims=True)
        sdp_starts.append(pack(Bs, Ds))
    for x0 in sdp_starts:
        x, f, v, st = nlp3.solve(x0)
        if v < 1e-8:
            fs.append(f)
            if f < best[0]:
                best = (f, x)
    print(f"[sdp-projection starts] best 3D = {best[0]:.9f}  ({len(fs)} feasible)", flush=True)
    out["sdp_proj_best"] = best[0]

    # (ii) homotopy from the exact 4-D (rank-r) SDP configuration: penalty on coords >= 4
    nlpr = NLP(r) if r > 3 else None
    hom = []
    if nlpr is not None:
        x4 = pack(Bc, Dc)
        f4 = nlpr.solve(x4, 0.0)
        print(f"[R^{r}] NLP at lam=0 from SDP config: f={f4[1]:.9f} viol={f4[2]:.1e} (should equal SDP)")
        for path in range(12):
            x = x4.copy()
            if path > 0:     # perturb + random rotation inside the extra coordinates
                x = x + 0.02 * path * rng.normal(size=x.shape)
            for lam in np.r_[0.0, np.geomspace(1e-3, 1e4, 22)]:
                x, f, v, st = nlpr.solve(x, lam)
            x3 = to3(x, r)
            x3, f3, v3, st3 = nlp3.solve(x3)
            hom.append(f3)
            if v3 < 1e-8 and f3 < best[0]:
                best = (f3, x3)
        print(f"[homotopy] 3D values: {np.round(sorted(hom), 7)}", flush=True)
    out["homotopy"] = sorted(hom)

    # (iii) random multistart
    for j in range(nstart):
        x, f, v, st = nlp3.solve(random_start(rng))
        if v < 1e-8:
            fs.append(f)
            if f < best[0]:
                best = (f, x)
        if (j + 1) % 100 == 0:
            print(f"[multistart {j + 1}] best 3D = {best[0]:.9f}", flush=True)
    fs = np.array(fs)
    out["genuine_best"] = best[0]
    out["n_feasible"] = int(len(fs))
    out["n_within_1e-7"] = int(np.sum(fs < best[0] + 1e-7))
    out["quantiles"] = np.quantile(fs, [0, .05, .25, .5]).tolist()
    out["below_sdp_plus_1e-6"] = int(np.sum(fs < s["val"] + 1e-6))
    Bf, Dm = unpack(best[1], 3)
    out["best_B"] = Bf.tolist(); out["best_D"] = Dm.tolist()
    print(f"FINAL: SDP {s['val']:.9f}  best genuine 3D {best[0]:.9f}  gap {best[0] - s['val']:.3e} "
          f"(rel {(best[0] - s['val']) / best[0]:.2%})  n_feas={len(fs)} n_hit_best={out['n_within_1e-7']}  "
          f"secs={time.time() - t0:.0f}")
    json.dump(out, open(os.path.join(OUT, "c12.json"), "w"), indent=1)
