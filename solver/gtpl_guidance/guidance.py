"""Planner wrappers used by the closed loop (1 Hz receding replans) and time-of-flight searches."""
import time
import numpy as np

from .aacg import AACG
from .certify import certify_B, certify_3dof
from .lcvx3dof import tf_search_A, solve_candidate_C, solve_3dof_relaxation
from .rotations import quat_to_R
from .sim6dof import Reference


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
                 tf_cap=20.0, replan_iters=4):
        self.B = AACG(veh, cfg)
        self.extensions, self.tol, self.tf_cap, self.replan_iters = extensions, tol, tf_cap, replan_iters
        self.veh, self.cfg, self.target, self.tf_abs = veh, cfg, np.asarray(target, float), tf_abs
        self.certify, self.replay = certify, replay
        self.last, self.last_t0 = None, None

    def __call__(self, t, x, prev_ref):
        tf = self.tf_abs - t
        R0, w0 = quat_to_R(x[6:10]), x[10:13]
        ai = None
        if self.last is not None:
            ai = _shift_alpha(self.last, self.last_t0, t, np.linspace(0, tf, self.cfg.N + 1))
        t0 = time.perf_counter()
        # anytime: warm-started replans get a small iteration budget (every accepted iterate is already flyable)
        p = self.B.plan(x[0:3], x[3:6], x[13], R0, w0, self.target, tf, alpha_init=ai, tol=self.tol,
                        max_iter=self.replan_iters if ai is not None else 15)
        solve_time, ext = p.solve_time, 0.0
        # fallback: the shrinking-horizon problem can become infeasible after tracking errors (min-fuel plans ride
        # the throttle limit while braking) -> extend the final time, as the flight code's tf search would
        for dt_ext in self.extensions:
            if p.status == 'certified-inner' or tf + dt_ext > self.tf_cap:
                break
            p2 = self.B.plan(x[0:3], x[3:6], x[13], R0, w0, self.target, tf + dt_ext, tol=self.tol)  # fresh warm start
            solve_time += p2.solve_time
            if p2.status == 'certified-inner' or p2.merit < p.merit:
                p, ext = p2, dt_ext
        p.solve_time = solve_time
        wall = time.perf_counter() - t0
        info = dict(t=t, method='B', status=p.status, solve_time=p.solve_time, wall=wall, iters=p.iters, tf_ext=ext,
                    n_solves=p.info.get('n_solves'), fuel_plan=p.fuel)
        if p.T_body is None:
            info['cert'] = False
            return None, info
        if self.certify:
            c = certify_B(p, self.veh, self.cfg, x[0:3], x[3:6], x[13], R0, w0, self.target, replay=self.replay)
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

    def __call__(self, t, x, prev_ref):
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

    def __call__(self, t, x, prev_ref):
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
