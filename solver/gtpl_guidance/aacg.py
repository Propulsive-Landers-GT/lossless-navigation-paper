"""Candidate B: attitude-aware convex guidance (AACG).

Idea in one paragraph (see README.md): the only nonconvex part of pure-TVC landing is the choice of the attitude
profile (C-U). For a FIXED body angular-acceleration profile alpha(t), the gimbal's lateral thrust is fixed
(T_perp = k * alpha x e3, C-6 / Lemma 8.1), the body axis b(t) is fixed, and the remaining problem in the scalar
axial thrust T_a(t) and the translational state is an exact SOCP (no relaxation). We therefore:

  1. warm-start alpha from the 3DOF solution (fit the body axis to the 3DOF thrust direction),
  2. INNER: solve the exact SOCP at the current alpha  -> a plan that is flyable by construction,
  3. STEP:  solve one convex subproblem where the attitude is linearised around the current profile inside a trust
            region (|alpha - alpha_bar| <= Delta), all thrust/gimbal/rate constraints are exact convex restrictions,
  4. re-run INNER at the candidate alpha; accept if the merit (fuel + penalty on terminal defects) decreased,
     otherwise shrink the trust region. Every accepted iterate is an exactly-feasible plan of the inner problem.

Merit = fuel [kg] + W * (|r_N - r_target|_1 + |v_N|_1) + W_b * |b_N,xy|_1.  A plan is CERTIFIED when the inner
solve reports zero terminal defect and the a-posteriori checks in `certify.py` pass.
"""
from dataclasses import dataclass, field
import time
import numpy as np
import cvxpy as cp

from .params import G0
from .attitude import Grid, propagate_attitude, attitude_sensitivity, integrate_translation, integrate_mass, HAT_E3
from .lcvx3dof import solve_3dof_relaxation
from .rotations import hat

GV = np.array([0.0, 0.0, -G0])
W_POS, W_VEL, W_ATT, W_STATE = 10.0, 10.0, 20.0, 100.0


@dataclass
class PlanB:
    tf: float
    grid: Grid
    alpha: np.ndarray        # (N+1, 2) body angular acceleration nodes
    Ta: np.ndarray           # (N+1,) axial thrust nodes [N]
    kk: float                # J_t / L used by the planner
    att: dict                # attitude propagation (R, w, b on substeps)
    r: np.ndarray            # (S+1, 3) CG position on substeps
    v: np.ndarray
    a: np.ndarray            # (S+1, 3) CG acceleration
    m: np.ndarray            # (S+1,) mass
    T_body: np.ndarray       # (S+1, 3) body-frame thrust vector
    fuel: float
    merit: float
    defect: dict
    status: str
    iters: int
    solve_time: float        # sum of conic solver times
    wall_time: float
    history: list = field(default_factory=list)
    info: dict = field(default_factory=dict)

    @property
    def t(self):
        return self.grid.ts


def _tbody_nodes(alpha, Ta, kk):
    return np.column_stack([-kk * alpha[:, 1], kk * alpha[:, 0], Ta])


def _solve(prob):
    try:
        prob.solve(solver=cp.CLARABEL)
    except cp.error.SolverError:
        try:
            prob.solve(solver=cp.ECOS)
        except cp.error.SolverError:
            return 'solver_error', 0.0
    st = prob.solver_stats.solve_time if prob.solver_stats and prob.solver_stats.solve_time else 0.0
    return prob.status, st


class AACG:
    """Planner B. Construct once per vehicle/config, call `plan(...)`."""

    def __init__(self, veh, cfg):
        self.veh, self.cfg = veh, cfg

    # ------------------------------------------------------------------ helpers
    def _ta_floor(self):
        c = self.cfg
        return c.T_min_plan * np.cos(np.arctan(np.sqrt(2) * np.tan(c.gimbal_plan)))

    def _state_constraints(self, rN, target):
        """Glide-slope cone + altitude floor at nodes 1..N, softened by a slack s >= 0 with an exact L1 penalty
        (s = 0 whenever the hard constraints are satisfiable; replans from slightly outside the cone stay solvable)."""
        c = self.cfg
        s = cp.Variable(self.grid.N, nonneg=True)
        cons = [rN[1:, 2] - target[2] + s >= 0]
        if c.glide_slope is not None:
            cons += [np.tan(c.glide_slope) * cp.norm(rN[1:, :2] - target[None, :2], axis=1) <= rN[1:, 2] - target[2] + s]
        return cons, W_STATE * cp.sum(s), s

    def _rate_constraints(self, Tb):
        """Linear sufficient conditions for the gimbal-rate and throttle-slew limits (claims N2, N3).
        Tb: (N+1,3) cvxpy expression or array of body thrust nodes (FOH)."""
        c = self.cfg
        h = self.grid.h
        dT = Tb[1:] - Tb[:-1]
        tg = np.tan(c.gimbal_plan)
        gbud = c.gimbal_rate_plan * self._ta_floor() * h
        return [cp.abs(dT[:, 0]) + tg * cp.abs(dT[:, 2]) <= gbud,
                cp.abs(dT[:, 1]) + tg * cp.abs(dT[:, 2]) <= gbud,
                cp.abs(dT[:, 0]) + cp.abs(dT[:, 1]) + cp.abs(dT[:, 2]) <= c.thrust_rate_plan * h]

    # ------------------------------------------------------------------ inner exact SOCP (C-6)
    def solve_inner(self, att, alpha, m_s, r0, v0, target):
        """Exact convex problem at a fixed attitude profile: variables = axial thrust nodes T_a (and terminal slacks)."""
        g, c, kk = self.grid, self.cfg, self.kk
        N1 = g.N + 1
        Tx, Ty = -kk * alpha[:, 1], kk * alpha[:, 0]
        kap = np.hypot(Tx, Ty)
        tg = np.tan(c.gimbal_plan)
        if np.any(kap >= c.T_max_plan) or np.any(np.maximum(np.abs(Tx), np.abs(Ty)) / tg > np.sqrt(np.maximum(c.T_max_plan**2 - kap**2, 0))):
            return None
        lo = np.maximum.reduce([np.sqrt(np.maximum(c.T_min_plan**2 - kap**2, 0.0)), np.abs(Tx) / tg, np.abs(Ty) / tg])
        up = np.sqrt(c.T_max_plan**2 - kap**2)
        # acceleration a_s = (b_s / m_s) * Ta_s + R_s Tperp_s / m_s + g
        R = att['R']
        a_s = att['alpha']
        Tperp_s = np.column_stack([-kk * a_s[:, 1], kk * a_s[:, 0], np.zeros(g.S + 1)])
        A = (R[:, :, 2] / m_s[:, None])[:, :, None] * g.W[:, None, :]
        cc = np.einsum('sij,sj->si', R, Tperp_s) / m_s[:, None] + GV[None, :]
        Ar, cr, Av, cv = integrate_translation(g, A, cc, r0, v0)
        nd = g.node
        Ta = cp.Variable(N1)
        rN = cp.hstack([Ar[nd, i, :] @ Ta + cr[nd, i] for i in range(3)])
        rN = cp.reshape(rN, (3, N1), order='C').T
        r_end = Ar[-1] @ Ta + cr[-1] - target
        v_end = Av[-1] @ Ta + cv[-1]
        Tb = cp.hstack([cp.reshape(cp.Constant(Tx), (N1, 1), order='C'), cp.reshape(cp.Constant(Ty), (N1, 1), order='C'),
                        cp.reshape(Ta, (N1, 1), order='C')])
        scons, spen, slack = self._state_constraints(rN, target)
        cons = [Ta >= lo, Ta <= up] + scons + self._rate_constraints(Tb)
        wts = np.full(N1, g.h)
        wts[[0, -1]] *= 0.5
        fuel = self.veh.alpha * cp.sum(cp.multiply(wts, cp.norm(cp.vstack([Ta, kap]), axis=0)))
        bN = att['b'][-1]
        pen_b = W_ATT * (abs(bN[0]) + abs(bN[1]))
        obj = fuel + W_POS * cp.norm1(r_end) + W_VEL * cp.norm1(v_end) + pen_b + spen
        prob = cp.Problem(cp.Minimize(obj), cons)
        st, stime = _solve(prob)
        self.solve_time += stime
        self.n_solves += 1
        if st not in ('optimal', 'optimal_inaccurate') or Ta.value is None:
            return None
        Tav = Ta.value
        Tb_s = np.column_stack([Tperp_s[:, 0], Tperp_s[:, 1], g.W @ Tav])
        r_s = np.einsum('sij,j->si', Ar, Tav) + cr
        v_s = np.einsum('sij,j->si', Av, Tav) + cv
        acc = np.einsum('sij,j->si', A, Tav) + cc
        defect = dict(r=float(np.linalg.norm(r_s[-1] - target)), v=float(np.linalg.norm(v_s[-1])),
                      tilt=float(np.arcsin(min(1.0, np.hypot(bN[0], bN[1])))), state=float(slack.value.max()))
        return dict(Ta=Tav, merit=float(prob.value), fuel=float(fuel.value), r=r_s, v=v_s, a=acc, T_body=Tb_s,
                    defect=defect, duals=dict(terminal=None), status=st)

    # ------------------------------------------------------------------ convex step with linearised attitude
    def solve_step(self, att, alpha_bar, Ta_bar, m_s, r0, v0, w0, target, Delta):
        g, c, kk = self.grid, self.cfg, self.kk
        N1 = g.N + 1
        Phi = attitude_sensitivity(g, att)                      # (S+1, 3, 2N1)
        R = att['R']
        Tbar_nodes = _tbody_nodes(alpha_bar, Ta_bar, kk)
        Tbar_s = g.W @ Tbar_nodes                               # (S+1, 3)
        # decision x = [alpha_x (N1), alpha_y (N1), Ta (N1)]
        nx = 3 * N1
        Tb_lin = np.zeros((g.S + 1, 3, nx))                     # T_body,s = Tb_lin[s] @ x
        Tb_lin[:, 0, N1:2 * N1] = -kk * g.W
        Tb_lin[:, 1, :N1] = kk * g.W
        Tb_lin[:, 2, 2 * N1:] = g.W
        PhiX = np.zeros((g.S + 1, 3, nx))
        PhiX[:, :, :2 * N1] = Phi
        That = np.stack([hat(t) for t in Tbar_s])               # (S+1,3,3)
        M = Tb_lin - np.einsum('sij,sjk->sik', That, PhiX)
        A = np.einsum('sij,sjk->sik', R, M) / m_s[:, None, None]
        xbar_a = np.concatenate([alpha_bar[:, 0], alpha_bar[:, 1]])
        cc = np.einsum('sij,sj->si', R, np.einsum('sij,sj->si', That, Phi @ xbar_a)) / m_s[:, None] + GV[None, :]
        Ar, cr, Av, cv = integrate_translation(g, A, cc, r0, v0)
        nd = g.node
        ax, ay, Ta = cp.Variable(N1), cp.Variable(N1), cp.Variable(N1)
        x = cp.hstack([ax, ay, Ta])
        rN = cp.reshape(cp.hstack([Ar[nd, i, :] @ x + cr[nd, i] for i in range(3)]), (3, N1), order='C').T
        r_end = Ar[-1] @ x + cr[-1] - target
        v_end = Av[-1] @ x + cv[-1]
        Tx, Ty = -kk * ay, kk * ax
        Tb = cp.hstack([cp.reshape(Tx, (N1, 1), order='C'), cp.reshape(Ty, (N1, 1), order='C'), cp.reshape(Ta, (N1, 1), order='C')])
        tg = np.tan(c.gimbal_plan)
        nbar = Tbar_nodes / np.linalg.norm(Tbar_nodes, axis=1, keepdims=True)
        cons = [cp.norm(Tb, axis=1) <= c.T_max_plan,
                cp.sum(cp.multiply(nbar, Tb), axis=1) >= c.T_min_plan,     # CCP restriction of ||T|| >= rho1 (P22)
                cp.abs(Tx) <= tg * Ta, cp.abs(Ty) <= tg * Ta]
        scons, spen, _ = self._state_constraints(rN, target)
        cons += scons + self._rate_constraints(Tb)
        # terminal body rate = 0 (exact, linear) and linearised tilt
        cons += [w0[0] + g.Cint[-1] @ ax == 0, w0[1] + g.Cint[-1] @ ay == 0]
        if self.alpha0 is not None:   # the gimbal cannot jump: start from the actuator's current lateral thrust
            cons += [ax[0] == self.alpha0[0], ay[0] == self.alpha0[1]]
        dalpha = cp.hstack([ax - alpha_bar[:, 0], ay - alpha_bar[:, 1]])
        Bn = -R[-1] @ HAT_E3 @ Phi[-1]                          # d b_N / d alpha
        bN = att['b'][-1] + Bn @ dalpha
        # path tilt (linearised) at nodes
        Bz = np.stack([-(R[s] @ HAT_E3 @ Phi[s])[2] for s in nd])
        cons += [att['b'][nd, 2] + Bz @ dalpha >= np.cos(c.tilt_max)]
        # trust region on the attitude perturbation at the nodes (radians): this is what limits linearisation error
        Pn = Phi[nd][:, :2, :].reshape(-1, 2 * N1)
        cons += [cp.abs(Pn @ dalpha) <= Delta]
        wts = np.full(N1, g.h)
        wts[[0, -1]] *= 0.5
        fuel = self.veh.alpha * cp.sum(cp.multiply(wts, cp.norm(Tb, axis=1)))
        obj = fuel + W_POS * cp.norm1(r_end) + W_VEL * cp.norm1(v_end) + W_ATT * cp.norm1(bN[:2]) + spen
        prob = cp.Problem(cp.Minimize(obj), cons)
        st, stime = _solve(prob)
        self.solve_time += stime
        self.n_solves += 1
        if st not in ('optimal', 'optimal_inaccurate') or ax.value is None:
            return None
        return dict(alpha=np.column_stack([ax.value, ay.value]), Ta=Ta.value, obj=float(prob.value))

    # ------------------------------------------------------------------ warm start
    def warm_start(self, R0, w0, p3, iters=2, lam=1e-3):
        """Fit a flyable alpha profile so that the body axis follows the 3DOF thrust direction (Gauss-Newton on
        the linearised attitude map), with zero terminal rate and the gimbal-implied angular-acceleration bound."""
        g, c, kk = self.grid, self.cfg, self.kk
        N1 = g.N + 1
        # desired direction at nodes from the 3DOF thrust (ZOH per interval) interpolated in time
        tc = 0.5 * (p3.t[:-1] + p3.t[1:])
        T3 = p3.u
        D = np.column_stack([np.interp(g.t, tc, T3[:, i]) for i in range(3)])
        D /= np.linalg.norm(D, axis=1, keepdims=True)
        D[-1] = [0, 0, 1.0]
        amax = np.tan(c.gimbal_plan) * self._ta_floor() / kk
        alpha = np.zeros((N1, 2))
        for _ in range(iters):
            att = propagate_attitude(g, R0, w0, alpha)
            Phi = attitude_sensitivity(g, att)
            ax, ay = cp.Variable(N1), cp.Variable(N1)
            da = cp.hstack([ax - alpha[:, 0], ay - alpha[:, 1]])
            res = []
            for k, s in enumerate(g.node):
                Bk = -att['R'][s] @ HAT_E3 @ Phi[s]
                res.append(att['b'][s, :2] + Bk[:2] @ da - D[k, :2])
            obj = cp.sum_squares(cp.hstack(res)) + lam * (cp.sum_squares(cp.diff(ax)) + cp.sum_squares(cp.diff(ay)))
            cons = [cp.abs(ax) <= amax, cp.abs(ay) <= amax,
                    w0[0] + g.Cint[-1] @ ax == 0, w0[1] + g.Cint[-1] @ ay == 0,
                    ax[0] == (0 if self.alpha0 is None else self.alpha0[0]),
                    ay[0] == (0 if self.alpha0 is None else self.alpha0[1]),
                    cp.abs(cp.diff(ax)) <= 0.5 * amax, cp.abs(cp.diff(ay)) <= 0.5 * amax]
            prob = cp.Problem(cp.Minimize(obj), cons)
            st, stime = _solve(prob)
            self.solve_time += stime
            self.n_solves += 1
            if ax.value is None:
                break
            alpha = np.column_stack([ax.value, ay.value])
        return alpha

    # ------------------------------------------------------------------ main loop
    def plan(self, r0, v0, m0, R0, w0, target, tf, alpha_init=None, alpha0=(0.0, 0.0), max_iter=15, Delta0=0.05,
             tol=1e-4,
             mass_iters=2, verbose=False):
        t_wall = time.perf_counter()
        veh, c = self.veh, self.cfg
        r0, v0, target = map(lambda z: np.asarray(z, float), (r0, v0, target))
        w0 = np.array([w0[0], w0[1], 0.0])
        self.grid = g = Grid(tf, c.N, c.substeps)
        J, L = veh.inertia_lever(m0)
        self.kk = J / L
        self.solve_time, self.n_solves = 0.0, 0
        # alpha0: angular acceleration produced by the CURRENT gimbal deflection (None = unconstrained)
        self.alpha0 = None if alpha0 is None else np.asarray(alpha0, float)
        p3 = None
        if alpha_init is None:
            p3 = solve_3dof_relaxation(r0, v0, m0, target, tf, veh, c, N=c.N)
            self.solve_time += p3.solve_time
            self.n_solves += 1
            if p3.u is None:   # 3DOF relaxation infeasible => 6DOF infeasible too (claims N7); still try vertical
                alpha = np.zeros((g.N + 1, 2))
            else:
                alpha = self.warm_start(R0, w0, p3)
        else:
            alpha = np.array(alpha_init, float)
            if self.alpha0 is not None:
                alpha[0] = self.alpha0
        m_s = m0 - veh.alpha * 0.5 * (c.T_min_plan + c.T_max_plan) * g.ts
        att = propagate_attitude(g, R0, w0, alpha)
        inner = None
        for _ in range(mass_iters + 1):
            inner = self.solve_inner(att, alpha, m_s, r0, v0, target)
            if inner is None:
                break
            m_s = integrate_mass(g, np.linalg.norm(inner['T_body'], axis=1), m0, veh.alpha)
        if inner is None:   # warm start not inner-feasible: retreat to zero acceleration (vertical attitude hold)
            alpha = np.zeros_like(alpha)
            if self.alpha0 is not None:
                alpha[0] = self.alpha0
            att = propagate_attitude(g, R0, w0, alpha)
            inner = self.solve_inner(att, alpha, m_s, r0, v0, target)
            if inner is None:
                return self._result(None, None, None, None, m0, tf, 'infeasible', 0, t_wall, [])
        hist = [dict(it=0, merit=inner['merit'], fuel=inner['fuel'], **inner['defect'], Delta=Delta0)]
        Delta = Delta0
        it = 0
        for it in range(1, max_iter + 1):
            step = self.solve_step(att, alpha, inner['Ta'], m_s, r0, v0, w0, target, Delta)
            if step is None:
                Delta *= 0.5
                if Delta < 1e-4:
                    break
                continue
            pred = inner['merit'] - step['obj']
            att_c = propagate_attitude(g, R0, w0, step['alpha'])
            inner_c = self.solve_inner(att_c, step['alpha'], m_s, r0, v0, target)
            actual = inner['merit'] - inner_c['merit'] if inner_c is not None else -np.inf
            rho = actual / pred if pred > 1e-12 else (1.0 if actual > 0 else 0.0)
            if verbose:
                print(f'it {it}: merit {inner["merit"]:.5f} pred {pred:.2e} act {actual:.2e} rho {rho:.2f} Delta {Delta:.3f}')
            if actual > 0 and rho > 0.1:
                alpha, att = step['alpha'], att_c
                inner = inner_c
                # mass fixed point: next iterations use the mass profile of the accepted plan
                m_s = integrate_mass(g, np.linalg.norm(inner_c['T_body'], axis=1), m0, veh.alpha)
                if rho > 0.75:
                    Delta = min(2 * Delta, 0.5)
                hist.append(dict(it=it, merit=inner['merit'], fuel=inner['fuel'], **inner['defect'], Delta=Delta))
                if actual < tol * (1 + abs(inner['merit'])) and self._feasible(inner):
                    break
            else:
                Delta *= 0.5
                if Delta < 1e-4 or (pred < tol * (1 + abs(inner['merit'])) and self._feasible(inner)):
                    break
        # final exact inner solve with the mass profile of the returned plan (mass fixed point)
        m_s = integrate_mass(g, np.linalg.norm(inner['T_body'], axis=1), m0, veh.alpha)
        inner_f = self.solve_inner(att, alpha, m_s, r0, v0, target)
        if inner_f is not None and (self._feasible(inner_f) or not self._feasible(inner)):
            inner = inner_f
        status = 'certified-inner' if self._feasible(inner) else 'infeasible-best-effort'
        return self._result(inner, alpha, att, m_s, m0, tf, status, it, t_wall, hist, p3)

    def _feasible(self, inner):
        d = inner['defect']
        return d['r'] < 0.01 and d['v'] < 0.01 and d['tilt'] < self.cfg.terminal_tilt_tol

    def _result(self, inner, alpha, att, m_s, m0, tf, status, it, t_wall, hist, p3=None):
        wall = time.perf_counter() - t_wall
        if inner is None:
            return PlanB(tf, self.grid, None, None, self.kk, None, None, None, None, None, None, np.inf, np.inf, {},
                         status, it, self.solve_time, wall, hist)
        m_true = integrate_mass(self.grid, np.linalg.norm(inner['T_body'], axis=1), m0, self.veh.alpha)
        return PlanB(tf, self.grid, alpha, inner['Ta'], self.kk, att, inner['r'], inner['v'], inner['a'], m_true,
                     inner['T_body'], float(m0 - m_true[-1]), inner['merit'], inner['defect'], status, it,
                     self.solve_time, wall, hist, info=dict(n_solves=self.n_solves,
                                                             fuel_3dof_relax=None if p3 is None else p3.fuel))
