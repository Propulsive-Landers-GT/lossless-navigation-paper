"""Planner F: flat convex guidance (single convex program in centre-of-percussion coordinates).

The decision variable is the trajectory y(t) of the centre of percussion, a quintic B-spline. In y the pure-TVC
vehicle is exactly a point whose acceleration is along the body axis (flat.py), so

  * the dynamics are LINEAR (y'' = u - g e3) and are satisfied identically: no linearisation, no virtual control,
    no trust region, no defect to close;
  * the initial attitude, body rate and gimbal deflection, and the upright / zero-rate / centred-gimbal touchdown are
    LINEAR equalities in the spline coefficients;
  * every actuator limit (throttle range, gimbal angle, tilt) is imposed as a convex RESTRICTION (an inner
    approximation, never a relaxation) on the Bezier control tuples of (u, u', u''), which by the convex-hull
    property makes it hold at every instant of the flight, not only at nodes.

Hence every feasible point of the SOCP is a trajectory the planning model can fly exactly: soundness is by
construction and needs no losslessness theorem. What is given up is completeness (the restriction can reject or
over-charge some flyable plans); Theorem A/B* (math/02) shows that some loss of this kind is unavoidable for any
convex program. The restriction uses per-span scalar references (thrust level phi, throttle log-rate rho, and kappa);
they affect only how tight it is, never whether the result is flyable. A previous plan (or one refinement pass)
supplies them.

Restriction, per control tuple (U, U1, U2) = (u, u', u'') with p = e3.U  (derivation and proofs: solver/FLAT.md):
    tilt          ||U_xy|| <= tan(tilt_max) p                                              (exact)
    min throttle  p >= T_min e^{-z_lo}                 [ T/m >= f >= p ]
    rate term     e1 >= ||U1 - rho U||,  q >= e1^2 / p [ f |b'| <= e1,  f |b'|^2 <= q ]
    torque term   G  = ||U2 - 2 rho U1 - kappa U|| + 2 q            [ f |P b''| <= G ]
    gimbal        eps G <= tan(gimbal) (2 phi p - phi^2)            [ eps |P b''| <= tan(gimbal) f ]
    max throttle  sigma >= ||( ||U|| + eps q / Lb ,  eps G / Lb )||,  sigma <= T_max e^{-z_up}   [ T/m <= sigma ]
with p >= Lb enforced, z_lo <= ln m <= z_up affine in the variables, and fuel <= alpha * integral(sigma).
"""
from dataclasses import dataclass, field
import time

import numpy as np
import cvxpy as cp

from .params import G0
from .flat import SplineBasis, FlatTrajectory, DEG, GE3, E3
from .attitude import Grid
from .rotations import quat_to_R, R_to_quat, expm_so3

W_STATE = 100.0


@dataclass
class FlatRef:
    """Per-span scalar references (length S). Any values give a sound plan; good values give a tight one."""
    rho: np.ndarray      # throttle log-rate f'/f  [1/s]
    kap: np.ndarray      # (f'' - 2 rho f')/f - |b'|^2  [1/s^2]
    phi: np.ndarray      # tangent point for f^2 >= 2 phi p - phi^2  [m/s^2]
    Lb: np.ndarray       # enforced lower bound on p = u_z on the span [m/s^2]


@dataclass
class PlanF:
    tf: float
    traj: FlatTrajectory
    status: str
    fuel: float            # true fuel of the plan [kg] (from the flat map)
    fuel_bound: float      # the SOCP's upper bound on it
    solve_time: float      # conic solver time [s]
    n_solves: int
    wall_time: float
    ref: FlatRef = None
    info: dict = field(default_factory=dict)


class FCG:
    """Flat convex guidance. Construct once per vehicle/config; call `plan`."""

    def __init__(self, veh, cfg, S=16, eps=None, samples_per_span=3, reg=1e-6, centre_gimbal_at_td=True,
                 phi0=7.5, slew=False, soft_td=0):
        self.veh, self.cfg, self.S = veh, cfg, S
        self.eps = eps if eps is not None else veh.J_t / (veh.m_wet * veh.L)
        self.sps, self.reg, self.centre = samples_per_span, reg, centre_gimbal_at_td
        self.phi0, self.slew, self.soft_td = phi0, slew, soft_td
        self.s_tilt = np.sin(cfg.tilt_max)
        self.basis = SplineBasis(S)

    # ------------------------------------------------------------------ references
    def default_ref(self, m0, S=None):
        S = S or self.S
        Lb = np.full(S, self.cfg.T_min_plan / m0)
        return FlatRef(np.zeros(S), np.zeros(S), np.full(S, self.phi0), Lb)

    def ref_from_traj(self, traj, t0=0.0, tf_new=None, S=None, m0=None, chi=0.8):
        """References taken from an existing flat trajectory (previous plan), on the grid of the new problem that
        starts at time t0 of `traj` and lasts tf_new. Span-wise values at 4 Gauss points, averaged."""
        S = S or self.S
        tf_new = tf_new if tf_new is not None else traj.tf - t0
        m0 = m0 if m0 is not None else traj.m0
        gx = np.array([0.0694318442, 0.3300094782, 0.6699905218, 0.9305681558])
        h = tf_new / S
        tq = (t0 + (np.arange(S)[:, None] + gx[None, :]) * h).ravel()
        e = traj.eval(np.minimum(tq, traj.tf), mass=False)
        f, fd, fdd, w2 = (e[k].reshape(S, 4) for k in ('f', 'fd', 'fdd', 'w2'))
        p = e['u'][:, 2].reshape(S, 4)
        rho = np.mean(fd / f, axis=1)
        kap = np.mean((fdd - 2 * rho[:, None] * fd) / f - w2, axis=1)
        phi = np.mean(p, axis=1)
        Lb = np.maximum(self.cfg.T_min_plan / m0, chi * p.min(axis=1))
        return FlatRef(rho, kap, phi, Lb)

    # ------------------------------------------------------------------ the convex program
    def solve(self, r0, v0, m0, R0, w0, target, tf, ref=None, T_lat0=(0.0, 0.0), soft_terminal=False, eps=None):
        """One SOCP. Returns (c, info) with c the (n,3) spline coefficients or None."""
        veh, cfg, S = self.veh, self.cfg, self.S
        eps = self.eps if eps is None else eps
        bs = self.basis
        n = bs.n
        ref = ref or self.default_ref(m0)
        h = tf / S
        alpha = veh.alpha
        r0, v0, target = (np.asarray(z, float) for z in (r0, v0, target))
        b0 = R0[:, 2]
        bd0 = R0 @ np.array([w0[1], -w0[0], 0.0])
        rep = lambda z: np.repeat(z, 4)

        c = cp.Variable((n, 3))
        M2, M3, M4, M5 = (bs.ctrl[d] / tf**d for d in (2, 3, 4, 5))
        gz = np.zeros((4 * S, 3))
        gz[:, 2] = G0
        U = M2 @ c + gz
        U1 = M3 @ c
        U2 = M4 @ c
        p = U[:, 2]
        rho, kap, phi, Lb = rep(ref.rho), rep(ref.kap), rep(ref.phi), rep(ref.Lb)

        e1 = cp.Variable(4 * S)
        q = cp.Variable(4 * S)
        g2 = cp.Variable(4 * S)
        sf = cp.Variable(4 * S)
        sig = cp.Variable(4 * S)
        cons = []
        # tilt (exact) and enforced lower bound on p
        cons += [cp.norm(U[:, :2], axis=1) <= np.tan(cfg.tilt_max) * p, p >= Lb]
        # rate term
        cons += [cp.norm(U1 - cp.multiply(rho[:, None], U), axis=1) <= e1]
        cons += [cp.norm(cp.vstack([2 * e1, q - p]), axis=0) <= q + p]                 # q >= e1^2 / p
        # torque term
        kz = cp.Variable(4 * S)
        W = U2 - cp.multiply(2 * rho[:, None], U1) - cp.multiply(kap[:, None], U)
        Wz = cp.hstack([W[:, :2], cp.reshape(W[:, 2] - kz, (4 * S, 1), order='C')])
        cons += [cp.norm(Wz, axis=1) + self.s_tilt * cp.abs(kz) <= g2]
        G = g2 + q
        tg = np.tan(cfg.gimbal_plan)
        cons += [eps * G <= tg * (cp.multiply(2 * phi, p) - phi**2)]
        # thrust / mass upper bound sigma
        cons += [cp.norm(U, axis=1) <= sf]
        cons += [cp.norm(cp.vstack([sf + cp.multiply(eps / Lb, q), cp.multiply(eps / Lb, G)]), axis=0) <= sig]
        if self.slew:
            # slew surrogates (dominant terms only, NOT part of the guarantee; the certificate checks the true rates):
            #   gimbal rate ~ eps |P u'''| / (f a) <= eps |u'''| / (2 phi p - phi^2),   throttle rate ~ m |f'| <= m0 |u'|
            U3 = M5 @ c
            cons += [eps * cp.norm(U3, axis=1) <= cfg.gimbal_rate_plan * (cp.multiply(2 * phi, p) - phi**2),
                     cp.norm(U1, axis=1) <= cfg.thrust_rate_plan / m0]

        # ---- mass bounds: z_lo <= ln m <= z_up
        z0 = np.log(m0)
        V0 = bs.design(np.linspace(0, 1, S + 1), 1) / tf          # y' at span boundaries
        vz = V0 @ c[:, 2]
        ts = np.linspace(0, tf, S + 1)
        z_up = z0 - alpha * (vz[:-1] - vz[0] + G0 * ts[:-1])       # at span starts (length S)
        Csum = np.kron(np.tril(np.ones((S, S))), np.ones((1, 4))) * (h / 4)
        z_lo = z0 - alpha * (Csum @ sig)                           # at span ends (length S)
        zmin = np.log(np.maximum(m0 - alpha * cfg.T_max_plan * 1.02 * ts[1:], 0.5 * veh.m_dry))
        zmax = np.log(m0 - alpha * cfg.T_min_plan * 0.98 * ts[1:])
        cons += [z_lo >= zmin, z_lo <= zmax, z_lo[-1] >= np.log(veh.m_dry)]
        slope = (np.exp(-zmax) - np.exp(-zmin)) / (zmax - zmin)
        chord = np.exp(-zmin) + cp.multiply(slope, z_lo - zmin)   # >= e^{-z_lo} on [zmin, zmax]
        zhat = np.log(m0 - alpha * m0 * G0 * ts[:-1])
        tang = cp.multiply(np.exp(-zhat), 1 - (z_up - zhat))      # <= e^{-z_up}
        Rep = np.kron(np.eye(S), np.ones((4, 1)))
        cons += [p >= cfg.T_min_plan * (Rep @ chord), sig <= cfg.T_max_plan * (Rep @ tang)]

        # ---- boundary conditions (all linear)
        D = [bs.design(np.array([0.0, 1.0]), d) / tf**d for d in range(5)]
        y0, y1 = D[0][0] @ c, D[0][1] @ c
        yd0, yd1 = D[1][0] @ c, D[1][1] @ c
        u0, u1_0, u2_0 = D[2][0] @ c + GE3, D[3][0] @ c, D[4][0] @ c
        uT, u1_T, u2_T = D[2][1] @ c + GE3, D[3][1] @ c, D[4][1] @ c
        f0, fd0 = b0 @ u0, b0 @ u1_0
        beta0 = -(R0 @ np.array([T_lat0[0], T_lat0[1], 0.0])) / (m0 * eps)
        cons += [y0 == r0 + eps * b0, yd0 == v0 + eps * bd0,
                 u0 == f0 * b0,
                 u1_0 - fd0 * b0 == f0 * bd0,
                 u2_0 - (b0 @ u2_0) * b0 == f0 * beta0 + 2 * fd0 * bd0]
        pen = 0
        if soft_terminal:
            dr = cp.Variable(3)
            cons += [y1 == target + eps * E3 + dr]
            pen = 1e3 * cp.norm(dr)
        else:
            cons += [y1 == target + eps * E3]
        cons += [yd1 == 0, uT[:2] == 0, u1_T[:2] == 0]
        if self.centre:
            cons += [u2_T[:2] == 0]
        if self.soft_td >= 1:        # arrive in hover: zero vertical acceleration at touchdown (thrust = weight)
            cons += [uT[2] == G0]
        if self.soft_td >= 2:        # ... and zero vertical jerk
            cons += [u1_T[2] == 0]

        # ---- state constraints on the CG, sampled, soft (as planners B / S)
        xs = (np.arange(S * self.sps) + 1) / (S * self.sps)
        Ys = bs.design(xs, 0) @ c
        Us = bs.design(xs, 2) / tf**2 @ c
        sl = cp.Variable(len(xs), nonneg=True)
        rz_lo = Ys[:, 2] - eps - target[2]                        # <= r_z - target_z (b_z <= 1)
        cons += [rz_lo + sl >= 0]
        if cfg.glide_slope is not None:
            Lb_s = np.repeat(ref.Lb, self.sps)
            lat = cp.norm(Ys[:, :2] - target[None, :2], axis=1) + cp.multiply(eps / Lb_s, cp.norm(Us[:, :2], axis=1))
            cons += [np.tan(cfg.glide_slope) * lat <= rz_lo + sl]

        obj = (h / 4) * cp.sum(sig) + W_STATE * cp.sum(sl) + pen
        if self.reg > 0:
            obj = obj + self.reg * (h / 4) * cp.sum(g2)
        prob = cp.Problem(cp.Minimize(obj), cons)
        t0 = time.perf_counter()
        try:
            prob.solve(solver=cp.CLARABEL)
            st = prob.status
        except cp.error.SolverError:
            st = 'solver_error'
        wall = time.perf_counter() - t0
        stime = prob.solver_stats.solve_time if (prob.solver_stats and prob.solver_stats.solve_time) else wall
        info = dict(status=st, solve_time=stime, wall=wall)
        if st not in ('optimal', 'optimal_inaccurate') or c.value is None:
            return None, info
        info.update(fuel_bound=float(m0 * (1 - np.exp(-alpha * (h / 4) * np.sum(sig.value)))),
                    slack=float(sl.value.max()), obj=float(prob.value))
        return c.value, info

    # ------------------------------------------------------------------ plan = solve (+ optional refinement passes)
    def plan(self, r0, v0, m0, R0, w0, target, tf, ref=None, T_lat0=(0.0, 0.0), refine=2, tol=2e-4, eps=None):
        """Solve, then `refine` passes that re-solve with the references taken from the best plan so far. Every pass
        returns a flyable plan; the best (lowest fuel) one is kept."""
        t_wall = time.perf_counter()
        eps = self.eps if eps is None else eps
        best, best_info, total, n = None, None, 0.0, 0
        hist = []
        for k in range(refine + 1):
            c, info = self.solve(r0, v0, m0, R0, w0, target, tf, ref=ref, T_lat0=T_lat0, eps=eps)
            total += info['solve_time']
            n += 1
            if c is None:
                hist.append(dict(status=info['status']))
                if best is None and k == 0 and ref is not None:
                    ref = None          # a stale reference made the restriction infeasible: fall back to the default
                    continue
                break
            traj = FlatTrajectory(c, tf, eps, m0, self.veh.alpha)
            fuel = float(m0 - traj.eval(np.array([tf]))['m'][0])
            hist.append(dict(status=info['status'], fuel=fuel, bound=info['fuel_bound'], slack=info['slack']))
            if best is None or fuel < best.fuel - 1e-9:
                improved = best is None or (best.fuel - fuel) > tol * best.fuel
                best = PlanF(tf, traj, 'flyable' if info['slack'] < 1e-6 else 'flyable-soft-state', fuel,
                             info['fuel_bound'], total, n, 0.0, ref, dict(slack=info['slack']))
                if not improved:
                    break
            else:
                break
            ref = self.ref_from_traj(traj, m0=m0)
        if best is None:
            return PlanF(tf, None, 'infeasible', np.inf, np.inf, total, n, time.perf_counter() - t_wall, None,
                         dict(history=hist))
        best.solve_time, best.n_solves, best.wall_time = total, n, time.perf_counter() - t_wall
        best.info['history'] = hist
        return best
