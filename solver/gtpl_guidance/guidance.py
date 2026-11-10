"""Planner wrappers used by the closed loop (1 Hz receding replans) and time-of-flight searches."""
import time
from dataclasses import replace
import numpy as np

from .aacg import AACG
from .scvx6dof import SCvx6DOF
from .certify import certify_B, certify_3dof
from .lcvx3dof import tf_search_A, solve_candidate_C, solve_3dof_relaxation
from .rotations import quat_to_R, gimbal_dir
from .sim6dof import Reference
from .fcg import FCG
from .flatcert import check_limits


def bisect_min_tf(feasible, lo, hi, tol=0.1, hi_max=25.0):
    """Smallest tf in [lo, hi] with feasible(tf) True (assumes monotone feasibility)."""
    while not feasible(hi):
        lo, hi = hi, hi + 2.0
        if hi > hi_max:
            return None
    if feasible(lo):
        return lo
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if feasible(mid):
            hi = mid
        else:
            lo = mid
    return hi


def min_tf_3dof(r0, v0, m0, target, veh, cfg):
    f = lambda tf: solve_3dof_relaxation(r0, v0, m0, target, tf, veh, cfg).u is not None
    return bisect_min_tf(f, 1.0, 8.0, tol=0.05)


def min_tf_B(r0, v0, m0, R0, w0, target, veh, cfg, lo=None):
    B = AACG(veh, cfg)
    lo = lo or min_tf_3dof(r0, v0, m0, target, veh, cfg)
    cache = {}

    def f(tf):
        p = B.plan(r0, v0, m0, R0, w0, target, tf)
        cache[tf] = p
        return p.status == 'certified-inner'
    tf = bisect_min_tf(f, lo, lo + 2.0)
    return tf, cache.get(tf)


def min_tf_C(r0, v0, m0, target, veh, cfg, lo=None, **kw):
    lo = lo or min_tf_3dof(r0, v0, m0, target, veh, cfg)
    f = lambda tf: solve_candidate_C(r0, v0, m0, target, tf, veh, cfg, **kw).u is not None
    return bisect_min_tf(f, lo, lo + 2.0)


def _shift_alpha(prev_plan, prev_t0, t, grid_t_new):
    ta = prev_t0 + prev_plan.grid.t
    tn = t + grid_t_new
    a = np.column_stack([np.interp(tn, ta, prev_plan.alpha[:, i], right=0.0) for i in range(2)])
    return a


class PlannerB:
    """Closed-loop wrapper of planner B (fixed absolute final time, shrinking horizon, warm start from last plan)."""

    def __init__(self, veh, cfg, target, tf_abs, certify=True, replay=True, extensions=(0.5, 1.0), tol=1e-3,
                 tf_cap=20.0, replan_iters=4, replan_margin_use=(20.0, 40.0)):
        self.B0 = AACG(veh, cfg)
        # replans may use part of the throttle margin kept by the first plan: a min-fuel plan brakes at T_max_plan, so
        # after any tracking lag the shrinking-horizon problem at the same limits is infeasible
        dlo, dhi = replan_margin_use
        self.cfg_replan = replace(cfg, T_min_plan=cfg.T_min_plan - dlo, T_max_plan=cfg.T_max_plan + dhi)
        self.B = AACG(veh, self.cfg_replan)
        self.extensions, self.tol, self.tf_cap, self.replan_iters = extensions, tol, tf_cap, replan_iters
        self.veh, self.cfg, self.target, self.tf_abs = veh, cfg, np.asarray(target, float), tf_abs
        self.certify, self.replay = certify, replay
        self.last, self.last_t0 = None, None

    def __call__(self, t, x, prev_ref, act=(0.0, 0.0, None)):
        tf = self.tf_abs - t
        R0, w0 = quat_to_R(x[6:10]), x[10:13]
        J, L = self.veh.inertia_lever(x[13])
        if act[2] is None:
            a0 = np.zeros(2)
        else:   # angular acceleration the current gimbal deflection produces (plan must start there)
            Tb = act[2] * gimbal_dir(act[0], act[1])
            lim = 0.95 * np.tan(self.cfg.gimbal_plan) * Tb[2]
            Tb[:2] = np.clip(Tb[:2], -lim, lim)          # the plan's gimbal limit is tighter than the tracker's
            a0 = np.array([Tb[1], -Tb[0]]) * L / J
        ai = None
        if self.last is not None:
            ai = _shift_alpha(self.last, self.last_t0, t, np.linspace(0, tf, self.cfg.N + 1))
        t0 = time.perf_counter()
        # anytime: warm-started replans get a small iteration budget (every accepted iterate is already flyable)
        planner = self.B if self.last is not None else self.B0
        p = planner.plan(x[0:3], x[3:6], x[13], R0, w0, self.target, tf, alpha_init=ai, alpha0=a0, tol=self.tol,
                         max_iter=self.replan_iters if ai is not None else 15)
        solve_time, ext, continued = p.solve_time, 0.0, False
        if p.status != 'certified-inner' and ai is not None and p.alpha is not None:
            # budget ran out before the terminal defect closed: keep iterating at the same t_f first
            p2 = planner.plan(x[0:3], x[3:6], x[13], R0, w0, self.target, tf, alpha_init=p.alpha, alpha0=a0, tol=self.tol,
                              max_iter=15)
            solve_time += p2.solve_time
            p2.iters += p.iters
            continued = True
            p = p2 if p2.merit <= p.merit else p
        # fallback: the shrinking-horizon problem can become infeasible after tracking errors (min-fuel plans ride
        # the throttle limit while braking) -> extend the final time, as the flight code's tf search would
        for dt_ext in self.extensions:
            if p.status == 'certified-inner' or tf + dt_ext > self.tf_cap:
                break
            p2 = planner.plan(x[0:3], x[3:6], x[13], R0, w0, self.target, tf + dt_ext, alpha0=a0, tol=self.tol)  # fresh warm start
            solve_time += p2.solve_time
            if p2.status == 'certified-inner' or p2.merit < p.merit:
                p, ext = p2, dt_ext
        p.solve_time = solve_time
        wall = time.perf_counter() - t0
        info = dict(t=t, method='B', status=p.status, solve_time=p.solve_time, wall=wall, iters=p.iters, tf_ext=ext, continued=continued,
                    n_solves=p.info.get('n_solves'), fuel_plan=p.fuel)
        if p.T_body is None:
            info['cert'] = False
            return None, info
        if self.certify:
            c = certify_B(p, self.veh, planner.cfg, x[0:3], x[3:6], x[13], R0, w0, self.target, replay=self.replay)
            info['cert'] = c['passed']
            info['cert_detail'] = {k: bool(v) for k, v in c['checks'].items()}
        else:
            info['cert'] = p.status == 'certified-inner'
        if p.status != 'certified-inner':
            return None, info      # keep flying the previous (certified) plan
        self.last, self.last_t0 = p, t
        self.tf_abs = t + p.tf
        return Reference.from_planB(p, t), info


class PlannerA:
    """Faithful flight-code guidance: shortest-feasible tf search from scratch at every replan."""

    def __init__(self, veh, target, v_max=15.0):
        self.veh, self.target, self.v_max = veh, np.asarray(target, float), v_max

    def __call__(self, t, x, prev_ref, act=None):
        t0 = time.perf_counter()
        p = tf_search_A(x[0:3], x[3:6], x[13], self.target, self.veh, v_max=self.v_max)
        wall = time.perf_counter() - t0
        if p is None:
            return None, dict(t=t, method='A', status='infeasible', wall=wall, cert=False)
        c = certify_3dof(p, self.veh)
        info = dict(t=t, method='A', status=p.status, solve_time=p.info['total_solve_time'], wall=wall, tf=p.tf,
                    cert=c['passed'], tight_min=c['tight_min'], T_del_min=c['T_delivered_min'],
                    dir_acc_max=c['dir_acc_max'], fuel_plan=p.fuel, n_solves=p.info['n_solves'])
        return Reference.from_plan3(p, t), info


class PlannerC:
    """3DOF LCvx + thrust rate / second-difference limits; fixed absolute final time."""

    def __init__(self, veh, cfg, target, tf_abs, **kw):
        self.veh, self.cfg, self.target, self.tf_abs, self.kw = veh, cfg, np.asarray(target, float), tf_abs, kw

    def __call__(self, t, x, prev_ref, act=None):
        tf = self.tf_abs - t
        t0 = time.perf_counter()
        N = max(8, int(round(self.cfg.N * tf / max(self.tf_abs, 1e-6))))
        p = solve_candidate_C(x[0:3], x[3:6], x[13], self.target, tf, self.veh, self.cfg, N=N, **self.kw)
        wall = time.perf_counter() - t0
        if p.u is None:
            return None, dict(t=t, method='C', status=p.status, wall=wall, cert=False)
        c = certify_3dof(p, self.veh)
        info = dict(t=t, method='C', status=p.status, solve_time=p.solve_time, wall=wall, cert=c['passed'],
                    tight_min=c['tight_min'], dir_acc_max=c['dir_acc_max'], fuel_plan=p.fuel)
        return Reference.from_plan3(p, t), info


def _shift_guess(prev_plan, prev_t0, t, tf, N):
    """Warm start for a shrinking-horizon SCvx replan: interpolate the previous node trajectory onto the new grid."""
    ta = prev_t0 + prev_plan.grid.t
    tn = t + np.linspace(0.0, tf, N + 1)
    X0, T0 = prev_plan.info['X'], prev_plan.info['T']
    X = np.column_stack([np.interp(tn, ta, X0[:, i]) for i in range(14)])
    X[:, 6:10] /= np.linalg.norm(X[:, 6:10], axis=1, keepdims=True)
    T = np.column_stack([np.interp(tn, ta, T0[:, i]) for i in range(3)])
    return X, T


class PlannerS:
    """Closed-loop wrapper of baseline S (standard 6DOF SCvx), built to mirror PlannerB exactly: same fixed absolute
    final time, same replan margins, same initial-gimbal condition, warm start from the previous plan, a small
    iteration budget with continuation, t_f extensions as a last resort, and 'keep flying the last accepted plan' when
    a replan does not produce a flyable plan. Budgets are in SOCPs comparable to B's (B solves ~2 SOCPs per iteration).
    """

    def __init__(self, veh, cfg, target, tf_abs, certify=True, replay=True, extensions=(0.5, 1.0), tf_cap=20.0,
                 first_iters=30, replan_iters=8, continue_iters=30, replan_margin_use=(20.0, 40.0), hover_td=False):
        self.S0 = SCvx6DOF(veh, cfg, hover_td=hover_td)
        dlo, dhi = replan_margin_use
        self.cfg_replan = replace(cfg, T_min_plan=cfg.T_min_plan - dlo, T_max_plan=cfg.T_max_plan + dhi)
        self.S = SCvx6DOF(veh, self.cfg_replan, hover_td=hover_td)
        self.extensions, self.tf_cap = extensions, tf_cap
        self.first_iters, self.replan_iters, self.continue_iters = first_iters, replan_iters, continue_iters
        self.veh, self.cfg, self.target, self.tf_abs = veh, cfg, np.asarray(target, float), tf_abs
        self.certify, self.replay = certify, replay
        self.last, self.last_t0 = None, None

    @staticmethod
    def _ok(p):
        return p.status in ('converged', 'feasible')

    def __call__(self, t, x, prev_ref, act=(0.0, 0.0, None)):
        tf = self.tf_abs - t
        R0, w0 = quat_to_R(x[6:10]), x[10:13]
        if act[2] is None:
            Tlat = np.zeros(2)
        else:
            Tb = act[2] * gimbal_dir(act[0], act[1])
            lim = 0.95 * np.tan(self.cfg.gimbal_plan) * Tb[2]
            Tlat = np.clip(Tb[:2], -lim, lim)
        planner = self.S if self.last is not None else self.S0
        t0 = time.perf_counter()
        args = (x[0:3], x[3:6], x[13], R0, w0, self.target)
        if self.last is None:
            p = planner.plan(*args, tf, init='3dof', T_lat0=Tlat, max_iter=self.first_iters)
        else:
            g = _shift_guess(self.last, self.last_t0, t, tf, self.cfg.N)
            p = planner.plan(*args, tf, guess=g, T_lat0=Tlat, max_iter=self.replan_iters)
        solve_time, ext, continued = p.solve_time, 0.0, False
        if not self._ok(p):
            p2 = planner.plan(*args, tf, guess=(p.info['X'], p.info['T']), T_lat0=Tlat, max_iter=self.continue_iters)
            solve_time += p2.solve_time
            p2.iters += p.iters
            continued = True
            p = p2 if (self._ok(p2) or p2.merit <= p.merit) else p
        for dt_ext in self.extensions:
            if self._ok(p) or tf + dt_ext > self.tf_cap:
                break
            p2 = planner.plan(*args, tf + dt_ext, init='3dof', T_lat0=Tlat, max_iter=self.first_iters)
            solve_time += p2.solve_time
            if self._ok(p2) or p2.merit < p.merit:
                p, ext = p2, dt_ext
        p.solve_time = solve_time
        wall = time.perf_counter() - t0
        info = dict(t=t, method='S', status=p.status, solve_time=p.solve_time, wall=wall, iters=p.iters, tf_ext=ext,
                    continued=continued, n_solves=p.info.get('n_solves'), fuel_plan=p.fuel)
        if self.certify:
            c = certify_B(p, self.veh, planner.cfg, x[0:3], x[3:6], x[13], R0, w0, self.target, replay=self.replay)
            info['cert'] = c['passed']
            info['cert_detail'] = {k: bool(v) for k, v in c['checks'].items()}
        else:
            info['cert'] = self._ok(p)
        if not self._ok(p):
            return None, info      # keep flying the previous plan
        self.last, self.last_t0 = p, t
        self.tf_abs = t + p.tf
        return Reference.from_planB(p, t), info


def min_tf_F(r0, v0, m0, R0, w0, target, veh, cfg, lo=None, S=16, tol=0.05):
    """Smallest final time at which planner F's single convex program is feasible (bisection, one SOCP per probe)."""
    F = FCG(veh, cfg, S=S)
    lo = lo or min_tf_3dof(r0, v0, m0, target, veh, cfg)
    f = lambda tf: F.solve(r0, v0, m0, R0, w0, target, tf)[0] is not None
    return bisect_min_tf(f, lo, lo + 2.0, tol=tol)


class PlannerF:
    """Closed-loop wrapper of planner F (flat convex guidance): fixed absolute final time, shrinking horizon.

    Each replan solves the SAME convex program with new numbers (state, time to go). Nothing is carried over from the
    previous plan by default, so there is no iteration, no warm start, no trust region and nothing that can diverge.
    Fallbacks, in order: drop the arrive-in-hover condition; extend the final time; keep flying the previous plan.

    Options: use_refs=True takes the tightness references (FlatRef) from the previous plan instead of the fixed
    defaults, and refine_first=k re-solves the first plan k times with its own references. Both only tighten the
    restriction (math/10-landing-proof.md); neither is needed.
    """

    def __init__(self, veh, cfg, target, tf_abs, S=16, span_min=0.3, S_min=6, refine_first=0, refine=0,
                 extensions=(0.25, 0.5, 1.0), tf_cap=20.0, replan_margin_use=(20.0, 40.0), check=True, soft_td=1,
                 use_refs=False):
        self.veh, self.cfg, self.target, self.tf_abs = veh, cfg, np.asarray(target, float), tf_abs
        dlo, dhi = replan_margin_use
        self.cfg_replan = replace(cfg, T_min_plan=cfg.T_min_plan - dlo, T_max_plan=cfg.T_max_plan + dhi)
        self.S, self.span_min, self.S_min = S, span_min, S_min
        self.refine_first, self.refine = refine_first, refine
        self.extensions, self.tf_cap, self.check, self.soft_td = extensions, tf_cap, check, soft_td
        self.use_refs = use_refs     # False: every solve uses the fixed default references (the simplest form)
        self.last, self.last_t0 = None, None
        self._planners = {}

    def _planner(self, S, first, soft):
        key = (S, first, soft)
        if key not in self._planners:
            self._planners[key] = FCG(self.veh, self.cfg if first else self.cfg_replan, S=S, soft_td=soft)
        return self._planners[key]

    def __call__(self, t, x, prev_ref, act=(0.0, 0.0, None)):
        tf = self.tf_abs - t
        R0, w0 = quat_to_R(x[6:10]), x[10:13]
        first = self.last is None
        if act[2] is None:
            Tlat = np.zeros(2)
        else:
            Tb = act[2] * gimbal_dir(act[0], act[1])
            lim = 0.95 * np.tan(self.cfg.gimbal_plan) * Tb[2]
            Tlat = np.clip(Tb[:2], -lim, lim)
        if first:
            self.tf_first = tf
            S = self.S
        else:   # keep the span length roughly constant as the horizon shrinks
            S = int(round(self.S * tf / self.tf_first))
            S = max(self.S_min, min(S, self.S, max(int(tf / self.span_min), 1)))
        t0 = time.perf_counter()
        solve_time, n_solves, ext = 0.0, 0, 0.0
        args = (x[0:3], x[3:6], x[13], R0, w0, self.target)
        J, L = self.veh.inertia_lever(x[13])
        eps = J / (x[13] * L)          # centre-of-percussion offset at the current mass
        p = None
        soft_used = 0
        for dt_ext in (0.0,) + tuple(self.extensions):
            if tf + dt_ext > self.tf_cap:
                break
            # the arrive-in-hover terminal condition is used when it is feasible and dropped before t_f is extended
            for soft in ((self.soft_td, 0) if self.soft_td else (0,)):
                F = self._planner(S, first, soft)
                ref = None
                if self.last is not None and self.use_refs:
                    ref = F.ref_from_traj(self.last.traj, t0=t - self.last_t0, tf_new=tf + dt_ext, S=S, m0=x[13])
                p = F.plan(*args, tf + dt_ext, ref=ref, T_lat0=Tlat,
                           refine=self.refine_first if first else self.refine, eps=eps)
                solve_time += p.solve_time
                n_solves += p.n_solves
                if p.traj is not None:
                    break
            if p.traj is not None:
                ext, soft_used = dt_ext, soft
                break
        wall = time.perf_counter() - t0
        ok = p is not None and p.traj is not None
        info = dict(t=t, method='F', status=p.status if p is not None else 'infeasible', solve_time=solve_time,
                    wall=wall, iters=n_solves, n_solves=n_solves, tf_ext=ext, continued=False,
                    fuel_plan=p.fuel if ok else None, cert=ok, S=S, soft_td=soft_used)
        if not ok:
            return None, info      # keep flying the previous plan
        if self.check:
            c = check_limits(p, self.veh, self.cfg_replan, x[0:3], x[3:6], x[13], R0, w0, self.target, n=401,
                             frame=False)
            info['peaks'] = {k: c[k] for k in ('T_min', 'T_max', 'gimbal_cone_max_deg', 'gimbal_rate_max_dps',
                                               'thrust_rate_max', 'tilt_max_deg')}
            info['cert'] = bool(all(v for k, v in c['checks'].items() if not k.endswith('_plan')))
            info['cert_detail'] = {k: bool(v) for k, v in c['checks'].items()}
            if not info['cert'] and self.last is not None:
                return None, info  # a replan that fails the limit check is not flown; the previous plan stays active
        self.last, self.last_t0 = p, t
        self.tf_abs = t + p.tf
        return Reference.from_planF(p, t), info
