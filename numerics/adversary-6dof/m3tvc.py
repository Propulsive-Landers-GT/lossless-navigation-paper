"""
[adversary-6dof] Full rigid-body (6DOF attitude) torque-coupled TVC model for the Claim-B6 attack.

State  x = (v[3], m, q[4], w_body[3], [gimbal angles 2 if rate-limited])
Controls u = (T, gimbal[2] or gimbal-rate[2], tau_roll)
Gimbal  'cone': gimbal = (gx, gy), gx^2+gy^2 <= sin(delta)^2, d_b = (gx, gy, sqrt(1-|g|^2))
        'box' : gimbal = (alpha, beta) in [-delta, delta]^2,     d_b = (cos b sin a, sin b, cos a cos b)
Engine at r = (0,0,-L) in body frame  =>  tau_b = L T (d_y, -d_x, 0)   (gimbal outward => body rotates inward)
Euler:  J w' = tau_b + tau_roll e_z - w x J w,   J = diag(Jt, Jt, Ja)
        q' = 0.5 q (x) (0, w)        v' = (T/m) R(q) d_b    m' = -alpha T
Velocity increment excludes gravity (affine shift).
decoupled=True replaces the TVC torque by an independent transverse torque input (|tau_xy| <= tau_max), used for model M3a.
"""
import numpy as np
import casadi as ca

G0 = 9.80665


def gtpl(**kw):
    P = dict(m0=79.88, rho1=400.0, rho2=1000.0, alpha=5.663e-4, L=0.589, Jt=63.6, Ja=3.74,
             delta=np.deg2rad(15.0), gdot=np.deg2rad(100.0), tau_roll=3.0)
    P.update(kw)
    return P


def qmul(p, q):
    pw, px, py, pz = p[0], p[1], p[2], p[3]
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    return ca.vertcat(pw*qw - px*qx - py*qy - pz*qz,
                      pw*qx + px*qw + py*qz - pz*qy,
                      pw*qy - px*qz + py*qw + pz*qx,
                      pw*qz + px*qy - py*qx + pz*qw)


def qrot(q, v):
    # rotate body vector v to world
    qv = ca.vertcat(0, v)
    qc = ca.vertcat(q[0], -q[1], -q[2], -q[3])
    r = qmul(qmul(q, qv), qc)
    return r[1:4]


class Reach6:
    def __init__(self, P, tf, N, gimbal="cone", rate_limited=False, terminal_att=False,
                 roll=True, nsub=2, decoupled=False, tau_dec=None, omega_max=None,
                 lat_eq=False, lat_dir_free=True, with_r=False):
        self.P, self.N, self.tf = P, N, tf
        self.gimbal, self.rate_limited = gimbal, rate_limited
        de, al = P["delta"], P["alpha"]
        Jt, Ja, L = P["Jt"], P["Ja"], P["L"]
        h = tf / N
        nx = 11 + (2 if rate_limited else 0) + (3 if with_r else 0)
        self.ir = 11 + (2 if rate_limited else 0)
        nu = 4 + (2 if decoupled else 0)
        x = ca.MX.sym("x", nx); u = ca.MX.sym("u", nu)
        v, m, q, w = x[0:3], x[3], x[4:8], x[8:11]
        T = u[0]
        gim = x[11:13] if rate_limited else u[1:3]
        if gimbal == "cone":
            db = ca.vertcat(gim[0], gim[1], ca.sqrt(1 - gim[0]**2 - gim[1]**2))
        else:
            a_, b_ = gim[0], gim[1]
            db = ca.vertcat(ca.cos(b_) * ca.sin(a_), ca.sin(b_), ca.cos(a_) * ca.cos(b_))
        if decoupled:
            tau = ca.vertcat(u[4], u[5], 0)
        else:
            tau = L * T * ca.vertcat(db[1], -db[0], 0)
        tau = tau + ca.vertcat(0, 0, u[3] if roll else 0)
        Jw = ca.vertcat(Jt * w[0], Jt * w[1], Ja * w[2])
        wdot = (tau - ca.cross(w, Jw)) / ca.vertcat(Jt, Jt, Ja)
        qdot = 0.5 * qmul(q, ca.vertcat(0, w))
        vdot = T / m * qrot(q, db)
        xdot = [vdot, -al * T, qdot, wdot]
        if rate_limited:
            xdot.append(u[1:3])
        if with_r:
            xdot.append(v)
        xdot = ca.vertcat(*xdot)
        f = ca.Function("f", [x, u], [xdot])
        xk = x
        for _ in range(nsub):
            hh = h / nsub
            k1 = f(xk, u); k2 = f(xk + hh/2*k1, u); k3 = f(xk + hh/2*k2, u); k4 = f(xk + hh*k3, u)
            xk = xk + hh/6*(k1 + 2*k2 + 2*k3 + k4)
        F = ca.Function("F", [x, u], [xk])
        self.F, self.f, self.nx, self.nu = F, f, nx, nu
        opti = ca.Opti(); self.opti = opti
        X = opti.variable(nx, N + 1); U = opti.variable(nu, N)
        self.X, self.U = X, U
        x0 = np.zeros(nx); x0[3] = P["m0"]; x0[4] = 1.0
        opti.subject_to(X[:, 0] == x0)
        for k in range(N):
            opti.subject_to(X[:, k + 1] == F(X[:, k], U[:, k]))
        opti.subject_to(opti.bounded(P["rho1"], U[0, :], P["rho2"]))
        opti.subject_to(opti.bounded(-P["tau_roll"], U[3, :], P["tau_roll"]))
        if not roll:
            opti.subject_to(U[3, :] == 0)
        G = X[11:13, :] if rate_limited else U[1:3, :]
        if gimbal == "cone":
            opti.subject_to(G[0, :]**2 + G[1, :]**2 <= np.sin(de)**2)
        else:
            opti.subject_to(opti.bounded(-de, G, de))
        if rate_limited:
            gd = P["gdot"]
            if gimbal == "cone":  # rate of gimbal vector (approx, in sin units)
                opti.subject_to(opti.bounded(-gd, U[1:3, :], gd))
            else:
                opti.subject_to(opti.bounded(-gd, U[1:3, :], gd))
        if decoupled:
            tm = tau_dec
            opti.subject_to(U[4, :]**2 + U[5, :]**2 <= tm**2)
        if omega_max is not None:
            opti.subject_to(X[8, :]**2 + X[9, :]**2 <= omega_max**2)
        if terminal_att == "rate":
            opti.subject_to(X[8, N] == 0); opti.subject_to(X[9, N] == 0)
        elif terminal_att:
            qN = X[4:8, N]
            # body z-axis = world z  <=>  qx = qy = 0 ; transverse rate zero
            opti.subject_to(qN[1] == 0); opti.subject_to(qN[2] == 0)
            opti.subject_to(X[8, N] == 0); opti.subject_to(X[9, N] == 0)
        # tilt stays below 90 deg - delta  (keeps us in the theorem regime): b_z = 1 - 2(qx^2+qy^2)
        bz = 1 - 2 * (X[5, :]**2 + X[6, :]**2)
        opti.subject_to(bz >= np.sin(de + np.deg2rad(6.5)))
        self.vN = X[0:3, N]
        self.lat_par = opti.parameter(2)
        self.lat_on = opti.parameter()
        opti.subject_to(self.lat_on * (X[0:2, N] - self.lat_par) == 0)
        opti.minimize(X[2, N])
        opti.solver("ipopt", {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 4000,
                              "ipopt.tol": 1e-10, "ipopt.sb": "yes"})

    def init(self, rng, pattern=None, amp=1.0, axis=None):
        """Simulate a guessed control schedule to produce a consistent initial guess."""
        P, N, h = self.P, self.N, self.tf / self.N
        de = P["delta"]
        X = np.zeros((self.nx, N + 1)); X[3, 0] = P["m0"]; X[4, 0] = 1.0
        U = np.zeros((self.nu, N))
        if axis is None:
            th = rng.uniform(0, 2*np.pi); axis = np.array([np.cos(th), np.sin(th)])
        lim = np.sin(de) if self.gimbal == "cone" else de
        for k in range(N):
            s = (k + 0.5) / N
            if pattern is None:
                gk = rng.uniform(-1, 1, 2) * lim * 0.9
            else:
                gk = pattern(s, rng) * axis * lim * amp
                if self.gimbal == "cone" and np.linalg.norm(gk) > lim * 0.999:
                    gk *= lim * 0.999 / np.linalg.norm(gk)
            U[0, k] = P["rho1"] * (1 + 0.01 * rng.random())
            if self.rate_limited:
                cur = X[11:13, k]
                U[1:3, k] = np.clip((gk - cur) / h, -P["gdot"], P["gdot"])
            else:
                U[1:3, k] = gk
            U[3, k] = 0.0
            X[:, k + 1] = np.array(self.F(X[:, k], U[:, k])).ravel()
            X[4:8, k + 1] /= np.linalg.norm(X[4:8, k + 1])
        self.opti.set_initial(self.X, X); self.opti.set_initial(self.U, U)

    def solve(self, lat=None):
        o = self.opti
        if lat is None:
            o.set_value(self.lat_on, 0); o.set_value(self.lat_par, [0, 0])
        else:
            o.set_value(self.lat_on, 1); o.set_value(self.lat_par, lat)
        try:
            sol = o.solve(); ok = True
        except RuntimeError:
            sol = o.debug; ok = False
        X = np.array(sol.value(self.X)); U = np.array(sol.value(self.U))
        return dict(ok=ok, vN=X[0:3, -1], X=X, U=U)


def tilt(X):
    bz = 1 - 2 * (X[5, :]**2 + X[6, :]**2)
    return np.degrees(np.arccos(np.clip(bz, -1, 1)))
