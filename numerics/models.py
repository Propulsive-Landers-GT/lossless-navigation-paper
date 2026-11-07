"""
Discretized 5DOF reachable-set NLPs (casadi SX + ipopt) for the LCvx-obstruction study.

Models
------
M1  kinematic rate-limited body axis b (angle(b(s),b(s')) <= omega|s-s'|), thrust direction d
    measurable within gimbal cone angle(d,b) <= delta, thrust T in [rho1, rho2], mass depletion
    mdot = -alpha T.  Discretization is an INNER approximation: b piecewise geodesic between nodes
    with node-to-node angle <= omega h; d_k piecewise constant and within delta of both b_k and
    b_{k+1}.  Spherical caps of radius delta < pi/2 are geodesically convex, so d_k is within delta
    of b(s) for all s in the interval: every discrete solution is an admissible continuous-time
    trajectory.  The per-interval velocity gain (1/alpha) ln(m_k/m_{k+1}) is exact.
M1A acceleration-limited kinematic axis (planar): theta'' in [-eps, eps], |theta'| <= omega,
    d free within delta of b.  (Brief's "torque-limited" variant with gimbal decoupled.)
M3  torque-coupled rigid body (TVC): the gimbal deflection IS the torque input.
    b' = w x b,  w' = -(L T / J) (b x g),  d = sqrt(1-|g|^2) b + g,  g perp b, |g| <= sin(delta),
    body-frame gimbal rate |g' - w x g| <= gdot_max, optional |w| <= omega_max.
    Planar version: th'' = -(L T/J) sin(gam), d angle = th + gam.  Multiple shooting, RK4.

Velocity increments Dv = int_0^tf a d ds (gravity excluded: affine shift), position increments
Dr = int_0^tf (tf - s) a d ds.  Landing feasibility: (r0, v0) in F_tf  <=>
    v0 = g_up*tf*e_z - Dv,   r0 = -v0 tf + g_up tf^2/2 e_z - Dr    (g_up = |g|).
"""
import numpy as np
import casadi as ca

G0 = 9.80665


# --------------------------------------------------------------------------------------
# Parameter sets
# --------------------------------------------------------------------------------------
def gtpl(**kw):
    """GTPL lander, from context/vehicle.md (central values): wet 80 kg, 400-1000 N,
    alpha = 1/(180 g0), gimbal 15 deg, J_xx 63.6 kg m^2 (wet), lever arm 0.589 m,
    gimbal slew 100 deg/s, usable body rate 0.3-0.5 rad/s."""
    P = dict(name="GTPL", m0=80.0, rho1=400.0, rho2=1000.0, delta=np.deg2rad(15.0),
             Isp=180.0, g=9.80665, L=0.589, J=63.6, gdot=np.deg2rad(100.0),
             omega=np.deg2rad(30.0), eps=1.0)
    P.update(kw)
    if "alpha" not in kw:
        P["alpha"] = 1.0 / (P["Isp"] * G0) if P["Isp"] else 0.0
    return P


def mars(**kw):
    """Mars-lander-like set after Acikmese & Ploen 2007 (m_wet 1905 kg, Isp 225 s, 6 x 3100 N
    thrusters canted 27 deg, throttle 0.3-0.8).  Attitude numbers (L, J, gdot, omega) are
    illustrative assumptions, not from the paper."""
    Tbar = 6 * 3100.0 * np.cos(np.deg2rad(27.0))
    P = dict(name="Mars", m0=1905.0, rho1=0.3 * Tbar, rho2=0.8 * Tbar, delta=np.deg2rad(15.0),
             Isp=225.0, g=3.7114, L=1.0, J=2000.0, gdot=np.deg2rad(20.0),
             omega=np.deg2rad(10.0), eps=0.2)
    P.update(kw)
    if "alpha" not in kw:
        P["alpha"] = 1.0 / (P["Isp"] * G0) if P["Isp"] else 0.0
    return P


IPOPT = {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 1500, "ipopt.tol": 1e-10,
         "ipopt.acceptable_tol": 1e-7, "ipopt.acceptable_iter": 10, "ipopt.sb": "yes"}


# --------------------------------------------------------------------------------------
# Extreme arcs for M1 (Theorem B)
# --------------------------------------------------------------------------------------
def min_throttle_coeffs(P, tf, N):
    h = tf / N
    s = np.arange(N + 1) * h
    m = P["m0"] - P["alpha"] * P["rho1"] * s
    if P["alpha"] > 0:
        c = np.log(m[:-1] / m[1:]) / P["alpha"]
    else:
        c = P["rho1"] / P["m0"] * h * np.ones(N)
    return s, c


def extreme_arcs_M1(P, tf, N, tent=False, omega=None):
    """Discrete min-throttle maximal-tilt arc of the inner discretization (planar, +x)."""
    om = P["omega"] if omega is None else omega
    s, c = min_throttle_coeffs(P, tf, N)
    h = tf / N
    phi = om * s if not tent else om * np.minimum(s, tf - s)
    psi = P["delta"] + np.minimum(phi[:-1], phi[1:])
    smid = s[:-1] + h / 2
    return dict(Px=np.sum(c * np.sin(psi)), Mz=np.sum(c * np.cos(psi)),
                Rx=np.sum((tf - smid) * c * np.sin(psi)), Rz=np.sum((tf - smid) * c * np.cos(psi)),
                psi=psi, phi=phi)


def extreme_arcs_M1_cont(P, tf, tent=False, n=20001, omega=None):
    om = P["omega"] if omega is None else omega
    s = np.linspace(0, tf, n)
    phi = om * s if not tent else om * np.minimum(s, tf - s)
    a1 = P["rho1"] / (P["m0"] - P["alpha"] * P["rho1"] * s)
    return dict(Px=np.trapezoid(a1 * np.sin(P["delta"] + phi), s),
                Mz=np.trapezoid(a1 * np.cos(P["delta"] + phi), s))


# --------------------------------------------------------------------------------------
# Generic NLP wrapper
# --------------------------------------------------------------------------------------
class NLP:
    """min  mode*|W(z-target)|^2 + (1-mode) c.z   s.t. model constraints, z[eq_idx] == eq_val.
    z = (Dv) or (Dv, Dr); optional tf free (decision variable)."""

    def _finish(self, x, g, lbg, ubg, lbx, ubx, z, use_r, eq_idx, extra_obj=None):
        nz = 6 if use_r else 3
        self.nz = nz
        p = ca.SX.sym("p", 1 + 3 * nz + len(eq_idx))
        mode = p[0]; target = p[1:1 + nz]; W = p[1 + nz:1 + 2 * nz]; c = p[1 + 2 * nz:1 + 3 * nz]
        eqv = p[1 + 3 * nz:]
        e = z - target
        f = mode * ca.sum1(W * e * e) + (1 - mode) * ca.dot(c, z)
        if extra_obj is not None:
            f = f + extra_obj
        for i, j in enumerate(eq_idx):
            g.append(z[j] - eqv[i]); lbg.append(0.0); ubg.append(0.0)
        G = ca.vertcat(*g)
        self.solver = ca.nlpsol("s", "ipopt", {"x": x, "p": p, "f": f, "g": G}, IPOPT)
        self.lbg, self.ubg = np.array(lbg, float), np.array(ubg, float)
        self.lbx, self.ubx = np.array(lbx, float), np.array(ubx, float)
        self.zf = ca.Function("zf", [x], [z])
        self.eq_idx = eq_idx
        self.Gf = ca.Function("Gf", [x], [G[:G.shape[0] - len(eq_idx)]])

    def solve(self, x0, mode="dist", target=None, W=None, c=None, eq_val=()):
        nz = self.nz
        pv = np.concatenate([[1.0 if mode == "dist" else 0.0],
                             np.zeros(nz) if target is None else np.asarray(target, float),
                             np.ones(nz) if W is None else np.asarray(W, float),
                             np.zeros(nz) if c is None else np.asarray(c, float),
                             np.asarray(eq_val, float)])
        x0 = np.clip(x0, self.lbx, self.ubx)
        r = self.solver(x0=x0, p=pv, lbg=self.lbg, ubg=self.ubg, lbx=self.lbx, ubx=self.ubx)
        x = np.array(r["x"]).ravel()
        st = self.solver.stats()
        gv = np.array(self.Gf(x)).ravel()
        n = gv.size
        viol = float(np.max(np.abs(gv - np.clip(gv, self.lbg[:n], self.ubg[:n])))) if n else 0.0
        return dict(x=x, z=np.array(self.zf(x)).ravel(), f=float(r["f"]),
                    ok=st["success"] or st["return_status"] in ("Solve_Succeeded", "Solved_To_Acceptable_Level"),
                    status=st["return_status"], viol=viol)

    def multistart(self, n, rng, accept_viol=1e-7, **kw):
        best, allr = None, []
        for _ in range(n):
            r = self.solve(self.random_x0(rng), **kw)
            if r["viol"] < accept_viol:
                allr.append(r)
                if best is None or r["f"] < best["f"]:
                    best = r
        return best, allr


# --------------------------------------------------------------------------------------
# M1
# --------------------------------------------------------------------------------------
class ReachM1(NLP):
    def __init__(self, P, tf, N, planar=False, tent=False, use_r=False, eq_idx=(),
                 free_tf=False, tf_lo=None, tf_hi=None, omega=None, discretization="inner", tilt_max=None, alt=False, lin_ineq=None):
        """alt=True: path constraint r_z(t_k) >= 0 at all nodes (landing-site altitude), using the
        boundary data implied by (Dv, Dr) for landing at r(tf)=0, v(tf)=0 under gravity P['g'].
        lin_ineq: list of (a (len nz), b) meaning a.z >= b."""
        """discretization='inner' (admissible) or 'outer' (relaxed: d_k within delta+omega*h of b_k
        only; contains the true continuous-time set up to O(h) mass effects)."""
        self.P, self.N, self.planar, self.tent, self.tf, self.free_tf = P, N, planar, tent, tf, free_tf
        om = P["omega"] if omega is None else omega
        self.om = om
        self.tilt_max = tilt_max
        de, al = P["delta"], P["alpha"]
        xs, lbx, ubx, g, lbg, ubg = [], [], [], [], [], []

        def var(n, lo, hi, name):
            v = ca.SX.sym(name, n); xs.append(v); lbx.extend(np.broadcast_to(lo, n)); ubx.extend(np.broadcast_to(hi, n)); return v

        if free_tf:
            tfv = var(1, tf_lo, tf_hi, "tf")[0]
        else:
            tfv = tf
        h = tfv / N
        T = var(N, P["rho1"], P["rho2"], "T")
        self.iT = (1 if free_tf else 0, (1 if free_tf else 0) + N)
        if planar:
            th = var(N + 1, -np.inf, np.inf, "th"); ps = var(N, -np.inf, np.inf, "ps")
            g.append(th[0]); lbg.append(0); ubg.append(0)
            if tent:
                g.append(th[N]); lbg.append(0); ubg.append(0)
            if tilt_max is not None:
                for k in range(N + 1):
                    g.append(th[k]); lbg.append(-tilt_max); ubg.append(tilt_max)
            for k in range(N):
                g.append((th[k + 1] - th[k]) / h); lbg.append(-om); ubg.append(om)
                if discretization == "inner":
                    g.append(ps[k] - th[k]); lbg.append(-de); ubg.append(de)
                    g.append(ps[k] - th[k + 1]); lbg.append(-de); ubg.append(de)
                else:
                    g.append(ps[k] - th[k] - (om * h) * 0); lbg.append(-de - om * tf / N); ubg.append(de + om * tf / N)
            D = ca.horzcat(ca.sin(ps), ca.SX.zeros(N, 1), ca.cos(ps)).T
        else:
            b = var(3 * (N + 1), -1.0, 1.0, "b"); d = var(3 * N, -1.0, 1.0, "d")
            B = ca.reshape(b, 3, N + 1); D = ca.reshape(d, 3, N)
            for i in range(3):
                g.append(B[i, 0]); lbg.append(0.0 if i < 2 else 1.0); ubg.append(0.0 if i < 2 else 1.0)
                if tent:
                    g.append(B[i, N]); lbg.append(0.0 if i < 2 else 1.0); ubg.append(0.0 if i < 2 else 1.0)
            for k in range(N + 1):
                g.append(ca.sumsqr(B[:, k])); lbg.append(1); ubg.append(1)
                if tilt_max is not None:
                    g.append(B[2, k]); lbg.append(np.cos(tilt_max)); ubg.append(1)
            for k in range(N):
                g.append(ca.sumsqr(D[:, k])); lbg.append(1); ubg.append(1)
                g.append(ca.dot(B[:, k], B[:, k + 1]) - ca.cos(om * h)); lbg.append(0); ubg.append(np.inf)
                if discretization == "inner":
                    g.append(ca.dot(D[:, k], B[:, k])); lbg.append(np.cos(de)); ubg.append(1)
                    g.append(ca.dot(D[:, k], B[:, k + 1])); lbg.append(np.cos(de)); ubg.append(1)
                else:
                    g.append(ca.dot(D[:, k], B[:, k])); lbg.append(np.cos(de + om * tf / N)); ubg.append(1)
        m = P["m0"]; cs = []
        for k in range(N):
            mn = m - al * T[k] * h
            cs.append(ca.log(m / mn) / al if al > 0 else T[k] / P["m0"] * h)
            m = mn
        cvec = ca.vertcat(*cs)
        dv = ca.mtimes(D, cvec)
        smid = (ca.DM(np.arange(N)) + 0.5) * h
        dr = ca.mtimes(D, cvec * (tfv - smid))
        if alt:
            gg = P["g"]
            r0z = dv[2] * tfv - dr[2] - gg * tfv ** 2 / 2
            v0z = gg * tfv - dv[2]
            Dz = D[2, :].T * cvec
            for j in range(1, N):
                tj = j * h
                rz = r0z + v0z * tj - gg * tj ** 2 / 2 + ca.sum1((tj - smid[:j]) * Dz[:j])
                g.append(rz); lbg.append(0.0); ubg.append(np.inf)
            g.append(r0z); lbg.append(0.0); ubg.append(np.inf)
        z = ca.vertcat(dv, dr) if use_r else dv
        if lin_ineq is not None:
            for a_, b_ in lin_ineq:
                g.append(ca.dot(ca.DM(a_), z)); lbg.append(b_); ubg.append(np.inf)
        x = ca.vertcat(*xs)
        self.nx = x.shape[0]
        self._finish(x, g, lbg, ubg, lbx, ubx, z, use_r, list(eq_idx))

    def random_x0(self, rng):
        P, N = self.P, self.N
        tf = self.tf if not self.free_tf else rng.uniform(self.lbx[0], self.ubx[0])
        h = tf / N; om, de = self.om, P["delta"]
        parts = [[tf]] if self.free_tf else []
        r = rng.random()
        T = P["rho1"] * np.ones(N) if r < 0.4 else (rng.uniform(P["rho1"], P["rho2"], N) if r < 0.8
                                                     else np.full(N, rng.uniform(P["rho1"], P["rho2"])))
        parts.append(T)
        sk = np.arange(N + 1) * h
        cap = om * (np.minimum(sk, tf - sk) if self.tent else sk)
        if self.tilt_max is not None:
            cap = np.minimum(cap, self.tilt_max)
        if self.planar:
            mode = rng.integers(3)
            if mode == 0:   # random walk
                steps = om * h * np.clip(rng.normal(rng.uniform(-1, 1), 0.8, N), -1, 1)
            elif mode == 1:  # one switch (tilt one way then the other)
                ks = rng.integers(1, N); sg = rng.choice([-1, 1])
                steps = om * h * np.where(np.arange(N) < ks, sg, -sg) * rng.uniform(0.5, 1)
            else:  # two switches
                k1, k2 = np.sort(rng.integers(1, N, 2)); sg = rng.choice([-1, 1])
                steps = om * h * sg * np.where(np.arange(N) < k1, 1, np.where(np.arange(N) < k2, -1, 1))
            th = np.concatenate([[0], np.cumsum(steps)])
            th = np.clip(th, -cap, cap)
            lo = np.maximum(th[:-1], th[1:]) - de; hi = np.minimum(th[:-1], th[1:]) + de
            ps = lo + rng.uniform(0, 1, N) * (hi - lo) if rng.random() < 0.5 else \
                np.where(rng.random(N) < 0.5, lo, hi)
            parts += [th, ps]
        else:
            b = np.zeros((3, N + 1)); b[:, 0] = [0, 0, 1]
            az = rng.uniform(0, 2 * np.pi); turn = rng.normal(0, 3.0) / max(tf, 1e-3)
            heading = np.array([np.cos(az), np.sin(az), 0.0])
            for k in range(N):
                heading = heading + h * turn * np.cross(b[:, k], heading) + 0.2 * rng.normal(size=3)
                t = heading - heading.dot(b[:, k]) * b[:, k]; t /= np.linalg.norm(t) + 1e-12
                ang = om * h * rng.uniform(0.2, 1.0)
                if self.tent and k >= N // 2:
                    # head back toward vertical
                    ez = np.array([0, 0, 1.0]); t = ez - ez.dot(b[:, k]) * b[:, k]
                    nt = np.linalg.norm(t)
                    if nt < 1e-9:
                        t = heading - heading.dot(b[:, k]) * b[:, k]; nt = np.linalg.norm(t)
                    t /= nt
                    ang = min(om * h, np.arccos(np.clip(b[2, k], -1, 1)) / max(N - k, 1) * 1.0 + 0) \
                        if k > N // 2 else ang
                b[:, k + 1] = np.cos(ang) * b[:, k] + np.sin(ang) * t
                b[:, k + 1] /= np.linalg.norm(b[:, k + 1])
                if self.tilt_max is not None and b[2, k + 1] < np.cos(self.tilt_max):
                    # slide along the tilt circle instead
                    hor = b[:2, k + 1] / (np.linalg.norm(b[:2, k + 1]) + 1e-12)
                    b[:, k + 1] = [np.sin(self.tilt_max) * hor[0], np.sin(self.tilt_max) * hor[1], np.cos(self.tilt_max)]
                    if b[:, k].dot(b[:, k + 1]) < np.cos(om * h):
                        b[:, k + 1] = b[:, k]
            if self.tent:
                b[:, N] = [0, 0, 1]
            if (not self.tent) and rng.random() < self.p_coning:
                b = self.coning_b(rng, tf)
            d = np.zeros((3, N))
            for k in range(N):
                bm = b[:, k] + b[:, k + 1]; bm /= np.linalg.norm(bm)
                rr = rng.normal(size=3); rr -= rr.dot(bm) * bm; rr /= np.linalg.norm(rr)
                ang = rng.uniform(0, 1) * max(de - om * h, 0)
                d[:, k] = np.cos(ang) * bm + np.sin(ang) * rr
            parts += [b.T.ravel(), d.T.ravel()]
        return np.concatenate(parts)

    p_coning = 0.35

    def coning_b(self, rng, tf):
        """Coning guess: tilt to rho at rate omega, then precess the azimuth at psi_dot = f*omega/sin(rho)
        (f in [0.6, 1], sign random), i.e. the body axis moves along the tilt circle at (nearly) max rate."""
        N, om = self.N, self.om; h = tf / N
        rho_max = om * tf * 0.8
        if self.tilt_max is not None:
            rho_max = min(rho_max, self.tilt_max)
        rho = rng.uniform(0.15, 1.0) * min(rho_max, 80 * np.pi / 180)
        if rng.random() < 0.3 and self.tilt_max is not None:
            rho = self.tilt_max * 0.999
        f = rng.uniform(0.6, 0.995) * rng.choice([-1, 1]); az0 = rng.uniform(0, 2 * np.pi)
        b = np.zeros((3, N + 1)); Phi = 0.0; az = az0
        for k in range(N + 1):
            b[:, k] = [np.sin(Phi) * np.cos(az), np.sin(Phi) * np.sin(az), np.cos(Phi)]
            if Phi < rho - 1e-12:
                Phi = min(rho, Phi + 0.995 * om * h)
            else:
                az += f * om * h / max(np.sin(rho), 1e-3)
        return b

    def unpack(self, x):
        N = self.N; o = 1 if self.free_tf else 0
        out = dict(tf=x[0] if self.free_tf else self.tf, T=x[o:o + N])
        o += N
        if self.planar:
            out["th"] = x[o:o + N + 1]; out["ps"] = x[o + N + 1:o + 2 * N + 1]
        else:
            out["b"] = x[o:o + 3 * (N + 1)].reshape(N + 1, 3).T
            out["d"] = x[o + 3 * (N + 1):].reshape(N, 3).T
        return out


# --------------------------------------------------------------------------------------
# M1A: planar acceleration-limited kinematic axis, gimbal decoupled
# --------------------------------------------------------------------------------------
class ReachM1A(NLP):
    def __init__(self, P, tf, N, eps=None, omega=None, use_r=False, eq_idx=(), tent=False):
        self.P, self.N, self.tf = P, N, tf
        eps = P["eps"] if eps is None else eps; om = P["omega"] if omega is None else omega
        self.eps, self.om = eps, om
        de, al = P["delta"], P["alpha"]; h = tf / N
        T = ca.SX.sym("T", N); th = ca.SX.sym("th", N + 1); w = ca.SX.sym("w", N + 1)
        acc = ca.SX.sym("acc", N); ps = ca.SX.sym("ps", N)
        x = ca.vertcat(T, th, w, acc, ps)
        lbx = [P["rho1"]] * N + [-np.inf] * (N + 1) + [-om] * (N + 1) + [-eps] * N + [-np.inf] * N
        ubx = [P["rho2"]] * N + [np.inf] * (N + 1) + [om] * (N + 1) + [eps] * N + [np.inf] * N
        g, lbg, ubg = [th[0], w[0]], [0, 0], [0, 0]
        if tent:
            g += [th[N], w[N]]; lbg += [0, 0]; ubg += [0, 0]
        for k in range(N):
            g.append(w[k + 1] - w[k] - h * acc[k]); lbg.append(0); ubg.append(0)
            g.append(th[k + 1] - th[k] - h * w[k] - 0.5 * h * h * acc[k]); lbg.append(0); ubg.append(0)
            # inner: d_k within delta of theta at both ends AND at the interior extremum (theta is
            # quadratic on the interval; conservative: also mid-point)
            for thv in (th[k], th[k + 1], th[k] + 0.5 * h * w[k] + 0.125 * h * h * acc[k]):
                g.append(ps[k] - thv); lbg.append(-de); ubg.append(de)
        m = P["m0"]; cs = []
        for k in range(N):
            mn = m - al * T[k] * h
            cs.append(ca.log(m / mn) / al if al > 0 else T[k] / P["m0"] * h); m = mn
        cvec = ca.vertcat(*cs)
        D = ca.horzcat(ca.sin(ps), ca.SX.zeros(N, 1), ca.cos(ps)).T
        dv = ca.mtimes(D, cvec); smid = (ca.DM(np.arange(N)) + 0.5) * h
        dr = ca.mtimes(D, cvec * (tf - smid))
        self._finish(x, g, lbg, ubg, lbx, ubx, ca.vertcat(dv, dr) if use_r else dv, use_r, list(eq_idx))

    def random_x0(self, rng):
        P, N, h = self.P, self.N, self.tf / self.N
        T = P["rho1"] * np.ones(N) if rng.random() < 0.5 else rng.uniform(P["rho1"], P["rho2"], N)
        k1, k2 = np.sort(rng.integers(0, N, 2))
        acc = self.eps * rng.choice([-1, 1]) * np.where(np.arange(N) < k1, 1, np.where(np.arange(N) < k2, -1, 1)) * rng.uniform(0.3, 1)
        th = [0.0]; w = [0.0]
        for k in range(N):
            a = acc[k]
            if abs(w[-1] + h * a) > self.om:
                a = 0.0; acc[k] = 0.0
            th.append(th[-1] + h * w[-1] + 0.5 * h * h * a); w.append(w[-1] + h * a)
        th = np.array(th); ps = 0.5 * (th[:-1] + th[1:]) + rng.uniform(-0.5, 0.5, N) * P["delta"]
        return np.concatenate([T, th, w, acc, ps])


# --------------------------------------------------------------------------------------
# M3 torque-coupled TVC rigid body
# --------------------------------------------------------------------------------------
class ReachM3(NLP):
    def __init__(self, P, tf, N, planar=False, omega_max=None, tent=False, use_r=False, eq_idx=(),
                 nsub=2, free_tf=False, tf_lo=None, tf_hi=None, rest_final=False, alt=False):
        self.P, self.N, self.planar, self.tf, self.free_tf, self.omega_max = P, N, planar, tf, free_tf, omega_max
        de, al, kk, gd = P["delta"], P["alpha"], P["L"] / P["J"], P["gdot"]
        if planar:
            nx, nu = 8, 2
            xs = ca.SX.sym("x", nx); us = ca.SX.sym("u", nu)
            vx, vz, rx, rz, m, th, w, gm = [xs[i] for i in range(nx)]
            T, gr = us[0], us[1]; ps = th + gm
            xdot = ca.vertcat(T / m * ca.sin(ps), T / m * ca.cos(ps), vx, vz, -al * T, w, -kk * T * ca.sin(gm), gr)
            x0 = [0, 0, 0, 0, P["m0"], 0, 0, 0]
        else:
            nx, nu = 16, 4
            xs = ca.SX.sym("x", nx); us = ca.SX.sym("u", nu)
            v = xs[0:3]; m = xs[6]; b = xs[7:10]; w = xs[10:13]; gg = xs[13:16]
            T = us[0]; eta = us[1:4]
            d = ca.sqrt(1 - ca.sumsqr(gg)) * b + gg
            xdot = ca.vertcat(T / m * d, v, -al * T, ca.cross(w, b), -kk * T * ca.cross(b, gg), ca.cross(w, gg) + eta)
            x0 = [0] * 6 + [P["m0"], 0, 0, 1] + [0] * 6
        f = ca.Function("f", [xs, us], [xdot])
        hs = ca.SX.sym("h"); xk = xs
        for _ in range(nsub):
            hh = hs / nsub
            k1 = f(xk, us); k2 = f(xk + hh / 2 * k1, us); k3 = f(xk + hh / 2 * k2, us); k4 = f(xk + hh * k3, us)
            xk = xk + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        self.F = ca.Function("F", [xs, us, hs], [xk])
        self.nxs, self.nus = nx, nu
        X = ca.SX.sym("X", nx * (N + 1)); U = ca.SX.sym("U", nu * N)
        Xm = ca.reshape(X, nx, N + 1); Um = ca.reshape(U, nu, N)
        allx = [X, U]; lbx = [-np.inf] * (nx * (N + 1)); ubx = [np.inf] * (nx * (N + 1))
        # control bounds
        lu = [P["rho1"]] + ([-gd] if planar else [-gd] * 3); uu = [P["rho2"]] + ([gd] if planar else [gd] * 3)
        lbx += lu * N; ubx += uu * N
        if free_tf:
            tfs = ca.SX.sym("tf"); allx = [tfs] + allx; lbx = [tf_lo] + lbx; ubx = [tf_hi] + ubx; tfv = tfs
        else:
            tfv = tf
        h = tfv / N
        g, lbg, ubg = [], [], []
        g.append(Xm[:, 0] - ca.DM(x0)); lbg += [0] * nx; ubg += [0] * nx
        for j in range(N):
            g.append(Xm[:, j + 1] - self.F(Xm[:, j], Um[:, j], h)); lbg += [0] * nx; ubg += [0] * nx
        for j in range(N + 1):
            if planar:
                g.append(Xm[7, j]); lbg.append(-de); ubg.append(de)
                if omega_max is not None:
                    g.append(Xm[6, j]); lbg.append(-omega_max); ubg.append(omega_max)
            else:
                g.append(ca.sumsqr(Xm[13:16, j])); lbg.append(0); ubg.append(np.sin(de) ** 2)
                if omega_max is not None:
                    g.append(ca.sumsqr(Xm[10:13, j])); lbg.append(0); ubg.append(omega_max ** 2)
        if not planar:
            for j in range(N):
                g.append(ca.sumsqr(Um[1:4, j])); lbg.append(0); ubg.append(gd ** 2)
                g.append(ca.dot(Um[1:4, j], Xm[7:10, j])); lbg.append(0); ubg.append(0)
        if tent:
            if planar:
                g.append(Xm[5, N]); lbg.append(0); ubg.append(0)
            else:
                g.append(Xm[7:9, N]); lbg += [0, 0]; ubg += [0, 0]
        if rest_final:
            if planar:
                g.append(Xm[6, N]); lbg.append(0); ubg.append(0)
            else:
                g.append(Xm[10:13, N]); lbg += [0] * 3; ubg += [0] * 3
        if planar:
            dv = ca.vertcat(Xm[0, N], 0, Xm[1, N]); dr = ca.vertcat(Xm[2, N], 0, Xm[3, N])
        else:
            dv = Xm[0:3, N]; dr = Xm[3:6, N]
        if alt:
            gg = P["g"]; iz = 3 if planar else 5
            r0z = dv[2] * tfv - dr[2] - gg * tfv ** 2 / 2; v0z = gg * tfv - dv[2]
            for j in range(0, N):
                tj = j * h
                g.append(r0z + v0z * tj - gg * tj ** 2 / 2 + Xm[iz, j]); lbg.append(0.0); ubg.append(np.inf)
        x = ca.vertcat(*allx)
        self.x0state = np.array(x0, float)
        self._finish(x, g, lbg, ubg, lbx, ubx, ca.vertcat(dv, dr) if use_r else dv, use_r, list(eq_idx))

    def rollout(self, Ufun, tf):
        """simulate with a control policy Ufun(j, X_j) -> u (projected)."""
        N = self.N; h = tf / N
        X = np.zeros((self.nxs, N + 1)); U = np.zeros((self.nus, N)); X[:, 0] = self.x0state
        for j in range(N):
            U[:, j] = Ufun(j, X[:, j], h)
            X[:, j + 1] = np.array(self.F(X[:, j], U[:, j], h)).ravel()
            if not self.planar:
                X[7:10, j + 1] /= np.linalg.norm(X[7:10, j + 1])
        return X, U

    def random_x0(self, rng):
        P, N = self.P, self.N
        tf = self.tf if not self.free_tf else rng.uniform(self.lbx[0], self.ubx[0])
        de, gd = P["delta"], P["gdot"]
        r = rng.random()
        T = P["rho1"] * np.ones(N) if r < 0.4 else (rng.uniform(P["rho1"], P["rho2"], N) if r < 0.8
                                                     else np.full(N, rng.uniform(P["rho1"], P["rho2"])))
        nk = rng.integers(2, 8)
        if self.planar:
            knots = rng.uniform(-de, de, nk) * rng.uniform(0.3, 1)
            gt = np.interp(np.linspace(0, 1, N + 1), np.linspace(0, 1, nk), knots)

            def pol(j, X, h):
                gr = np.clip((gt[j + 1] - X[7]) / h, -gd, gd)
                if self.omega_max is not None:  # crude rate protection
                    if abs(X[6]) > 0.9 * self.omega_max:
                        gr = np.clip((np.sign(X[6]) * de * 0.5 - X[7]) / h, -gd, gd)
                return np.array([T[j], gr])
        else:
            knots = rng.uniform(-1, 1, (3, nk)) * np.sin(de) * 0.9
            gt = np.array([np.interp(np.linspace(0, 1, N + 1), np.linspace(0, 1, nk), q) for q in knots])

            def pol(j, X, h):
                b = X[7:10]; gg = X[13:16]; w = X[10:13]
                gtar = gt[:, j + 1] - gt[:, j + 1].dot(b) * b
                if self.omega_max is not None and np.linalg.norm(w) > 0.8 * self.omega_max:
                    gtar = 0.5 * np.sin(de) * np.cross(w, b) / (np.linalg.norm(w) + 1e-12)  # brake: b x g ~ w
                ng = np.linalg.norm(gtar)
                if ng > np.sin(de) * 0.95:
                    gtar *= np.sin(de) * 0.95 / ng
                eta = (gtar - gg) / h - np.cross(w, gg); eta -= eta.dot(b) * b
                ne = np.linalg.norm(eta)
                if ne > gd * 0.99:
                    eta *= gd * 0.99 / ne
                return np.concatenate([[T[j]], eta])
        X, U = self.rollout(pol, tf)
        parts = [[tf]] if self.free_tf else []
        return np.concatenate(parts + [X.T.ravel(), U.T.ravel()])

    def unpack(self, x):
        o = 1 if self.free_tf else 0
        N = self.N
        X = x[o:o + self.nxs * (N + 1)].reshape(N + 1, self.nxs).T
        U = x[o + self.nxs * (N + 1):].reshape(N, self.nus).T
        return dict(tf=x[0] if self.free_tf else self.tf, X=X, U=U)


# --------------------------------------------------------------------------------------
# MT: tilt-angle-rate-only variant (polar angle of b is omega-Lipschitz, azimuth free)
# --------------------------------------------------------------------------------------
class ReachTilt(NLP):
    """Polar angle Phi of b: |Phi_{k+1}-Phi_k| <= omega h, Phi_0 = 0, Phi >= 0; azimuth of b free (can be set to
    the azimuth of d on every interval), so the gimbal constraint reduces to |Theta_k - Phi| <= delta at both
    interval ends, Theta_k = polar angle of d_k, azimuth psi_k of d_k free."""

    def __init__(self, P, tf, N, use_r=False, eq_idx=(), omega=None, tent=False, alt=False, tilt_max=None):
        self.P, self.N, self.tf, self.free_tf, self.tent = P, N, tf, False, tent
        om = P["omega"] if omega is None else omega; self.om = om
        de, al = P["delta"], P["alpha"]; h = tf / N
        T = ca.SX.sym("T", N); Ph = ca.SX.sym("Ph", N + 1); Th = ca.SX.sym("Th", N); ps = ca.SX.sym("ps", N)
        x = ca.vertcat(T, Ph, Th, ps)
        pm = np.pi if tilt_max is None else tilt_max
        lbx = [P["rho1"]] * N + [0.0] * (N + 1) + [0.0] * N + [-np.inf] * N
        ubx = [P["rho2"]] * N + [pm] * (N + 1) + [np.pi] * N + [np.inf] * N
        g, lbg, ubg = [Ph[0]], [0], [0]
        if tent:
            g.append(Ph[N]); lbg.append(0); ubg.append(0)
        for k in range(N):
            g.append(Ph[k + 1] - Ph[k]); lbg.append(-om * h); ubg.append(om * h)
            g.append(Th[k] - Ph[k]); lbg.append(-de); ubg.append(de)
            g.append(Th[k] - Ph[k + 1]); lbg.append(-de); ubg.append(de)
        m = P["m0"]; cs = []
        for k in range(N):
            mn = m - al * T[k] * h
            cs.append(ca.log(m / mn) / al if al > 0 else T[k] / P["m0"] * h); m = mn
        cvec = ca.vertcat(*cs)
        D = ca.horzcat(ca.sin(Th) * ca.cos(ps), ca.sin(Th) * ca.sin(ps), ca.cos(Th)).T
        dv = ca.mtimes(D, cvec); smid = (ca.DM(np.arange(N)) + 0.5) * h
        dr = ca.mtimes(D, cvec * (tf - smid))
        if alt:
            gg = P["g"]
            r0z = dv[2] * tf - dr[2] - gg * tf ** 2 / 2; v0z = gg * tf - dv[2]
            Dz = D[2, :].T * cvec
            for j in range(1, N):
                tj = j * h
                g.append(r0z + v0z * tj - gg * tj ** 2 / 2 + ca.sum1((tj - smid[:j]) * Dz[:j])); lbg.append(0.0); ubg.append(np.inf)
            g.append(r0z); lbg.append(0.0); ubg.append(np.inf)
        self._finish(x, g, lbg, ubg, lbx, ubx, ca.vertcat(dv, dr) if use_r else dv, use_r, list(eq_idx))

    def random_x0(self, rng):
        P, N, h, om, de = self.P, self.N, self.tf / self.N, self.om, self.P["delta"]
        T = P["rho1"] * np.ones(N) if rng.random() < 0.3 else rng.uniform(P["rho1"], P["rho2"], N)
        steps = om * h * np.clip(rng.normal(rng.uniform(-0.5, 1), 0.7, N), -1, 1)
        Ph = np.maximum(np.concatenate([[0], np.cumsum(steps)]), 0)
        for k in range(N):  # re-enforce rate after clipping
            Ph[k + 1] = np.clip(Ph[k + 1], Ph[k] - om * h, Ph[k] + om * h)
        if self.tent:
            sk = np.arange(N + 1) * h; Ph = np.minimum(Ph, om * (self.tf - sk))
        lo = np.maximum(np.maximum(Ph[:-1], Ph[1:]) - de, 0); hi = np.minimum(Ph[:-1], Ph[1:]) + de
        Th = lo + rng.random(N) * (hi - lo)
        a0 = rng.uniform(0, 2 * np.pi)
        ps = a0 + np.cumsum(rng.normal(0, rng.choice([0.05, 0.5, 2.0]), N))
        return np.concatenate([T, Ph, Th, ps])
