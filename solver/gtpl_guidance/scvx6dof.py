"""Baseline S: standard 6DOF successive convexification (SCvx) on the full rigid body.

This is the textbook method planner B is compared against (Mao, Szmuk & Acikmese 2016; Szmuk & Acikmese 2018;
Malyuta et al. 2022): linearize the ENTIRE nonlinear dynamics about the current trajectory, add virtual control so
every subproblem is feasible, solve one convex SOCP inside a trust region, and accept or reject the step with the
usual actual-vs-predicted ratio test on a penalized (exact-penalty) merit.

Model and constraints are exactly those of the IPOPT reference D (`reference_nlp.py`) and planner B:
  state x = [r(3), v(3), q(4) body->world, w(3), m] (14), control = body-frame thrust T (FOH on N+1 nodes),
  roll torque 0, J_t and L frozen at their m0 values, RK4 with `ns` substeps per interval (the discrete map whose
  Jacobians are used for the linearization, i.e. multiple shooting).
  Throttle [T_min_plan, T_max_plan] (upper bound SOC; lower bound linearized at the current thrust, a safe inner
  approximation by convexity), |T_x|, |T_y| <= tan(gimbal_plan) T_z, the same linear gimbal-rate and throttle-slew
  conditions, tilt (convex in q: q_x^2 + q_y^2 <= (1 - cos tilt_max)/2), altitude floor and glide-slope cone
  (soft with the same exact L1 penalty as planner B), upright at rest at the target at t_f, gimbal starts at the
  current deflection.

Differences from planner B, which is what the comparison measures:
  * S linearizes translation, attitude and mass together; B linearizes only the attitude and solves the throttle
    problem exactly (C-6).
  * S's iterates satisfy the dynamics only at convergence (virtual control -> 0); every accepted B iterate is an exact
    trajectory of the planning model.

The returned plan is the single-shooting forward integration of the planned thrust from the initial state on the
certificate's fine grid, so `certify.certify_B` checks what would actually be flown.
"""
from dataclasses import dataclass, field
import time

import numpy as np
import cvxpy as cp
import casadi as ca

from .params import G0
from .attitude import Grid
from .rotations import R_to_quat, quat_to_R
from .reference_nlp import _dyn_sx, guess_from_3dof
from .lcvx3dof import solve_3dof_relaxation
from .aacg import PlanB, _solve, W_STATE

GV = np.array([0.0, 0.0, -G0])
# scaling of states and controls inside the subproblem (x = SX * xhat + CX)
SX = np.array([10, 10, 10, 5, 5, 5, 1, 1, 1, 1, 0.2, 0.2, 0.2, 10.0])
ST = 1000.0


def _interval_fn_notorque(f, h, ns):
    x = ca.SX.sym('x', 14)
    T0, T1 = ca.SX.sym('T0', 3), ca.SX.sym('T1', 3)
    dt = h / ns
    xx = x
    for j in range(ns):
        l0, lm, l1 = j / ns, (j + 0.5) / ns, (j + 1) / ns
        Tl = lambda l: (1 - l) * T0 + l * T1
        k1 = f(xx, Tl(l0), 0)
        k2 = f(xx + 0.5 * dt * k1, Tl(lm), 0)
        k3 = f(xx + 0.5 * dt * k2, Tl(lm), 0)
        k4 = f(xx + dt * k3, Tl(l1), 0)
        xx = xx + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ca.Function('F', [x, T0, T1], [xx])


@dataclass
class SCvxStats:
    iters: int = 0
    n_solves: int = 0
    solve_time: float = 0.0
    history: list = field(default_factory=list)


class SCvx6DOF:
    """Standard SCvx. Construct once per vehicle/config, call `plan(...)`."""

    def __init__(self, veh, cfg, ns=4, w_nu=1e3, rho0=0.0, rho1=0.25, rho2=0.7, r_init=0.5, r_min=1e-5, r_max=10.0):
        self.veh, self.cfg, self.ns = veh, cfg, ns
        self.w_nu, self.rho0, self.rho1, self.rho2 = w_nu, rho0, rho1, rho2
        self.r_init, self.r_min, self.r_max = r_init, r_min, r_max
        self._fn_cache = {}

    # ------------------------------------------------------------------ discrete dynamics and Jacobians
    def _functions(self, tf, m0):
        J, L = self.veh.inertia_lever(m0)
        key = (round(tf, 9), round(J, 9), round(L, 9))
        if key not in self._fn_cache:
            N = self.cfg.N
            f = _dyn_sx(J, self.veh.J_z, L, self.veh.alpha)
            F = _interval_fn_notorque(f, tf / N, self.ns)
            x, T0, T1 = ca.SX.sym('x', 14), ca.SX.sym('T0', 3), ca.SX.sym('T1', 3)
            y = F(x, T0, T1)
            JF = ca.Function('JF', [x, T0, T1], [y, ca.jacobian(y, x), ca.jacobian(y, T0), ca.jacobian(y, T1)])
            self._fn_cache[key] = (F.map(N), JF.map(N), f, J, L, F)
        return self._fn_cache[key]

    def _shoot_defect(self, F1, T, target):
        """Single-shooting landing error of the thrust plan alone (what flying it open loop would give): the same
        1 cm / 1 cm/s / terminal-tilt criterion planner B's iterates are judged by."""
        x = self._x0.copy()
        for k in range(len(T) - 1):
            x = np.array(F1(x, T[k], T[k + 1])).ravel()
        b = quat_to_R(x[6:10] / np.linalg.norm(x[6:10]))[:, 2]
        return dict(r=float(np.linalg.norm(x[0:3] - target)), v=float(np.linalg.norm(x[3:6])),
                    tilt=float(np.arcsin(min(1.0, np.hypot(b[0], b[1])))))

    def _defects(self, Fm, X, T):
        Y = np.array(Fm(X[:-1].T, T[:-1].T, T[1:].T)).T
        return X[1:] - Y

    # ------------------------------------------------------------------ merit (exact penalty)
    def _merit(self, Fm, X, T, target):
        d = self._defects(Fm, X, T) / SX[None, :]
        c = self.cfg
        rz = X[1:, 2] - target[2]
        viol = np.maximum(0.0, -rz)
        if c.glide_slope is not None:
            lat = np.linalg.norm(X[1:, :2] - target[None, :2], axis=1)
            viol = np.maximum(viol, np.tan(c.glide_slope) * lat - rz)
        # fuel (m0 - m_N, same scale as planner B's merit) + exact penalties
        return self._m0 - X[-1, 13] + self.w_nu * np.abs(d).sum() + W_STATE * viol.sum(), float(np.abs(d).max())

    # ------------------------------------------------------------------ convex subproblem
    def _subproblem(self, JFm, Xb, Tb, x0, target, r, T_lat0):
        c, N = self.cfg, self.cfg.N
        N1 = N + 1
        Y, Ax, Bm, Bp = (np.array(o) for o in JFm(Xb[:-1].T, Tb[:-1].T, Tb[1:].T))
        Y = Y.T
        # mapped Jacobians are horizontally concatenated blocks: column 14k + j belongs to interval k
        Ax = Ax.reshape(14, N, 14).transpose(1, 0, 2)
        Bm = Bm.reshape(14, N, 3).transpose(1, 0, 2)
        Bp = Bp.reshape(14, N, 3).transpose(1, 0, 2)
        Xh = cp.Variable((N1, 14))
        Th = cp.Variable((N1, 3))
        nu = cp.Variable((N, 14))
        X = cp.multiply(Xh, np.tile(SX, (N1, 1)))
        T = ST * Th
        cons = [X[0] == x0]
        for k in range(N):
            cons.append(X[k + 1] == Y[k] + Ax[k] @ (X[k] - Xb[k]) + Bm[k] @ (T[k] - Tb[k]) + Bp[k] @ (T[k + 1] - Tb[k + 1])
                        + cp.multiply(SX, nu[k]))
        tg = np.tan(c.gimbal_plan)
        nb = Tb / np.linalg.norm(Tb, axis=1, keepdims=True)
        cons += [cp.norm(T, axis=1) <= c.T_max_plan,
                 cp.sum(cp.multiply(nb, T), axis=1) >= c.T_min_plan,      # tangent of ||T|| >= T_min (inner approx.)
                 cp.abs(T[:, 0]) <= tg * T[:, 2], cp.abs(T[:, 1]) <= tg * T[:, 2]]
        if T_lat0 is not None:
            cons += [T[0, 0] == T_lat0[0], T[0, 1] == T_lat0[1]]
        h = self._tf / N
        ta_floor = c.T_min_plan * np.cos(np.arctan(np.sqrt(2) * tg))
        gbud = c.gimbal_rate_plan * ta_floor * h
        dT = T[1:] - T[:-1]
        cons += [cp.abs(dT[:, 0]) + tg * cp.abs(dT[:, 2]) <= gbud,
                 cp.abs(dT[:, 1]) + tg * cp.abs(dT[:, 2]) <= gbud,
                 cp.abs(dT[:, 0]) + cp.abs(dT[:, 1]) + cp.abs(dT[:, 2]) <= c.thrust_rate_plan * h]
        # tilt: 1 - 2(qx^2 + qy^2) >= cos(tilt_max)  <=>  ||(qx, qy)|| <= sqrt((1 - cos)/2)   (convex)
        cons += [cp.norm(X[1:, 7:9], axis=1) <= np.sqrt((1 - np.cos(c.tilt_max)) / 2)]
        s = cp.Variable(N, nonneg=True)
        rz = X[1:, 2] - target[2]
        cons += [rz + s >= 0]
        if c.glide_slope is not None:
            cons += [np.tan(c.glide_slope) * cp.norm(X[1:, :2] - target[None, :2], axis=1) <= rz + s]
        # terminal: at the target, at rest, upright, zero body rate
        cons += [X[N, 0:3] == target, X[N, 3:6] == 0, X[N, 7] == 0, X[N, 8] == 0, X[N, 10:13] == 0]
        # trust region on the scaled deviation (infinity norm, per variable)
        cons += [cp.abs(Xh - Xb / SX[None, :]) <= r, cp.abs(Th - Tb / ST) <= r]
        lin_pen = self.w_nu * cp.sum(cp.abs(nu)) + W_STATE * cp.sum(s)
        obj = self._m0 - X[N, 13] + lin_pen
        prob = cp.Problem(cp.Minimize(obj), cons)
        st, stime = _solve(prob)
        self.stats.solve_time += stime
        self.stats.n_solves += 1
        if st not in ('optimal', 'optimal_inaccurate') or Xh.value is None:
            return None
        return Xh.value * SX[None, :], Th.value * ST, float(prob.value)

    # ------------------------------------------------------------------ initial guesses
    def initial_guess(self, kind, r0, v0, m0, R0, w0, target, tf, p3=None):
        N = self.cfg.N
        if kind == '3dof':
            p3 = p3 if p3 is not None else solve_3dof_relaxation(r0, v0, m0, target, tf, self.veh, self.cfg, N=N)
            if p3.u is not None:
                X, T = guess_from_3dof(p3, N, m0)
                X[0] = self._x0
                return X, T, p3
            kind = 'linear'
        # 'linear': straight-line position, linear velocity blend, upright attitude, hover-ish thrust (Szmuk 2018)
        lam = np.linspace(0, 1, N + 1)[:, None]
        X = np.zeros((N + 1, 14))
        X[:, 0:3] = (1 - lam) * r0 + lam * target
        X[:, 3:6] = (1 - lam) * v0
        X[:, 6] = 1.0
        X[:, 13] = m0 - lam[:, 0] * self.veh.alpha * m0 * G0 * tf
        X[0] = self._x0
        T = np.zeros((N + 1, 3))
        T[:, 2] = np.clip(m0 * G0, self.cfg.T_min_plan, self.cfg.T_max_plan)
        return X, T, p3

    # ------------------------------------------------------------------ main loop
    def plan(self, r0, v0, m0, R0, w0, target, tf, init='3dof', guess=None, T_lat0=(0.0, 0.0), max_iter=30,
             tol=1e-5, defect_tol=1e-6, verbose=False, track_feasible=False):
        t_wall = time.perf_counter()
        r0, v0, target = map(lambda z: np.asarray(z, float), (r0, v0, target))
        self._tf, self._m0 = tf, m0
        self.stats = SCvxStats()
        self._x0 = np.concatenate([r0, v0, R_to_quat(R0), [w0[0], w0[1], 0.0], [m0]])
        Fm, JFm, f, J, L, F1 = self._functions(tf, m0)
        p3 = None
        if guess is not None:
            Xb, Tb = (np.array(z, float) for z in guess)
            Xb[0] = self._x0
        else:
            Xb, Tb, p3 = self.initial_guess(init, r0, v0, m0, R0, w0, target, tf)
            if p3 is not None:
                self.stats.solve_time += p3.solve_time
                self.stats.n_solves += 1
        if T_lat0 is not None:
            Tb[0, :2] = T_lat0
        phi, dmax = self._merit(Fm, Xb, Tb, target)
        r = self.r_init
        hist = [dict(it=0, merit=phi, defect=dmax, r=r, n_solves=self.stats.n_solves, solve_time=self.stats.solve_time,
                     **({'shoot': self._shoot_defect(F1, Tb, target)} if track_feasible else {}))]
        it = 0
        converged = False
        for it in range(1, max_iter + 1):
            sub = self._subproblem(JFm, Xb, Tb, self._x0, target, r, T_lat0)
            if sub is None:
                r *= 0.5
                if r < self.r_min:
                    break
                continue
            Xn, Tn, L_new = sub
            phi_n, dmax_n = self._merit(Fm, Xn, Tn, target)
            pred = phi - L_new
            act = phi - phi_n
            rho = act / pred if abs(pred) > 1e-12 else 1.0
            if verbose:
                print(f'it {it}: merit {phi:.6f} pred {pred:.2e} act {act:.2e} rho {rho:.2f} r {r:.3g} defect {dmax_n:.1e}')
            if rho > self.rho0:
                Xb, Tb, phi, dmax = Xn, Tn, phi_n, dmax_n
                if rho < self.rho1:
                    r = max(r / 2, self.r_min)
                elif rho >= self.rho2:
                    r = min(2 * r, self.r_max)
            else:
                r /= 2
            hist.append(dict(it=it, merit=phi, defect=dmax, r=r, rho=rho, pred=pred, n_solves=self.stats.n_solves, solve_time=self.stats.solve_time,
                             **({'shoot': self._shoot_defect(F1, Tb, target)} if track_feasible else {})))
            if dmax < defect_tol and abs(pred) < tol * (1 + abs(phi)):
                converged = True
                break
            if r < self.r_min:
                break
        self.stats.iters, self.stats.history = it, hist
        return self._result(Xb, Tb, m0, R0, w0, r0, v0, target, tf, J, L, converged, t_wall, p3)

    # ------------------------------------------------------------------ plan object on the certificate grid
    def _result(self, X, T, m0, R0, w0, r0, v0, target, tf, J, L, converged, t_wall, p3):
        c, veh = self.cfg, self.veh
        g = Grid(tf, c.N, c.substeps)
        Ts = g.W @ T                                        # FOH thrust on the fine grid (what would be flown)
        f = lambda x, Tb: _deriv_np(x, Tb, J, veh.J_z, L, veh.alpha)
        sub = 4
        x = self._x0.copy()
        xs = np.empty((g.S + 1, 14))
        xs[0] = x
        dt = g.hs / sub
        for s in range(g.S):
            for j in range(sub):
                l0, lm, l1 = j / sub, (j + 0.5) / sub, (j + 1) / sub
                Tl = lambda l: (1 - l) * Ts[s] + l * Ts[s + 1]
                k1 = f(x, Tl(l0))
                k2 = f(x + 0.5 * dt * k1, Tl(lm))
                k3 = f(x + 0.5 * dt * k2, Tl(lm))
                k4 = f(x + dt * k3, Tl(l1))
                x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
                x[6:10] /= np.linalg.norm(x[6:10])
            xs[s + 1] = x
        R = np.array([quat_to_R(q) for q in xs[:, 6:10]])
        w = xs[:, 10:13]
        alpha = np.column_stack([L * Ts[:, 1] / J, -L * Ts[:, 0] / J, np.zeros(g.S + 1)])
        a = np.einsum('sij,sj->si', R, Ts) / xs[:, 13:14] + GV[None, :]
        bN = R[-1][:, 2]
        defect = dict(r=float(np.linalg.norm(xs[-1, 0:3] - target)), v=float(np.linalg.norm(xs[-1, 3:6])),
                      tilt=float(np.arcsin(min(1.0, np.hypot(bN[0], bN[1])))), state=0.0,
                      w=float(np.linalg.norm(w[-1])))
        feasible = defect['r'] < 0.01 and defect['v'] < 0.01 and defect['tilt'] < c.terminal_tilt_tol
        status = 'converged' if (converged and feasible) else ('feasible' if feasible else 'infeasible-best-effort')
        att = dict(R=R, w=w, alpha=alpha, b=R[:, :, 2].copy())
        p = PlanB(tf, g, None, T[:, 2].copy(), J / L, att, xs[:, 0:3], xs[:, 3:6], a, xs[:, 13], Ts,
                  float(m0 - xs[-1, 13]), float(self.stats.history[-1]['merit']), defect, status, self.stats.iters,
                  self.stats.solve_time, time.perf_counter() - t_wall, self.stats.history,
                  info=dict(n_solves=self.stats.n_solves, solve_time=self.stats.solve_time, converged=converged, X=X, T=T,
                            node_fuel=float(m0 - X[-1, 13]), max_node_defect=float(self.stats.history[-1]['defect'])))
        return p


def _deriv_np(x, T_body, J_t, J_z, L, alpha):
    q = x[6:10] / np.linalg.norm(x[6:10])
    R = quat_to_R(q)
    a = R @ T_body / x[13] + GV
    w = x[10:13]
    tau = np.array([L * T_body[1], -L * T_body[0], 0.0])
    J = np.array([J_t, J_t, J_z])
    wdot = (tau - np.cross(w, J * w)) / J
    qw, qv = q[0], q[1:]
    qdot = 0.5 * np.concatenate([[-qv @ w], qw * w + np.cross(qv, w)])
    return np.concatenate([x[3:6], a, qdot, wdot, [-alpha * np.linalg.norm(T_body)]])
