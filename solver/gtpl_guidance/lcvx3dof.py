"""3DOF lossless-convexification planners.

* Baseline A  (`solve_baseline_A`, `tf_search_A`): faithful re-implementation of the GTPL flight guidance
  (guidance/LosslessConvexification/rust_lossless/src/lossless.rs): forward-Euler dynamics, log-mass with first-order
  Taylor thrust bounds about the full-throttle mass profile, 15 deg pointing cone about the INERTIAL vertical,
  speed limit, min sum(sigma) dt, shortest-feasible time-of-flight search (coarse 0.5 s, fine 0.2 s).
* Candidate C  (`solve_candidate_C`): the same SOCP plus thrust-vector rate limits ||u_{k+1}-u_k|| <= D1 and
  second-difference limits ||u_{k+1}-2u_k+u_{k-1}|| <= D2, sized by `size_rate_limits` (chord bound, claims N4/N5).
* `solve_3dof_relaxation`: a 3DOF relaxation of the 6DOF problem (no attitude, no rate limits, ZOH-exact
  dynamics, relaxed mass bounds). Its optimal fuel is a lower bound for any 6DOF plan with the same throttle range and
  state constraints (claims N7); also used to warm-start B and to pick the time of flight.
* `purify` : C-K2 purification (fix sigma*, maximise a random linear functional) to remove lossy nodes.
"""
from dataclasses import dataclass, field
import time
import numpy as np
import cvxpy as cp

from .params import G0

GVEC = np.array([0.0, 0.0, -G0])


@dataclass
class Plan3:
    """A 3DOF plan. Nodes k = 0..N; thrust acceleration u_k is held on [t_k, t_{k+1})."""
    tf: float
    t: np.ndarray          # (N+1,)
    r: np.ndarray          # (N+1, 3)
    v: np.ndarray          # (N+1, 3)
    m: np.ndarray          # (N+1,)
    u: np.ndarray          # (N, 3) thrust / mass
    sigma: np.ndarray      # (N,)  slack (thrust-magnitude bound / mass)
    fuel: float
    dyn: str               # 'euler' or 'zoh'
    status: str
    solve_time: float
    info: dict = field(default_factory=dict)

    @property
    def N(self):
        return len(self.t) - 1

    @property
    def T(self):
        """Delivered thrust vectors (N,3) in newtons."""
        return self.u * self.m[:-1, None]

    def tightness(self):
        """||u_k|| / sigma_k (1 = lossless)."""
        return np.linalg.norm(self.u, axis=1) / np.maximum(self.sigma, 1e-12)


def _mass_taylor_rust(m0, alpha, rho2, dt, N):
    return np.log(np.maximum(m0 - alpha * rho2 * dt * np.arange(N), 1e-3))


def _solve(prob):
    t0 = time.perf_counter()
    try:
        prob.solve(solver=cp.CLARABEL)
    except cp.error.SolverError:
        try:
            prob.solve(solver=cp.ECOS)
        except cp.error.SolverError:
            return 'solver_error', time.perf_counter() - t0
    st = prob.solver_stats.solve_time if prob.solver_stats and prob.solver_stats.solve_time else time.perf_counter() - t0
    return prob.status, st


def solve_3dof(r0, v0, m0, target, tf, N, veh, *, dyn='euler', T_bounds=None, pointing=np.radians(15.0),
               v_max=None, glide=None, rate=None, mass_bounds='taylor_rust', objective='fuel', fixed_sigma=None,
               lin_obj=None, dir0=None, dirN=None):
    """Generic 3DOF LCvx SOCP in the flight-code variables (x, v, w = ln m, u = T/m, sigma).

    rate: None or (D1, D2) bounds on ||u_{k+1}-u_k|| and ||u_{k+1}-2u_k+u_{k-1}|| (acceleration units).
    mass_bounds: 'taylor_rust' (flight code) or 'relax' (rigorous relaxation: tangent lower bound, secant upper bound).
    fixed_sigma / lin_obj: used by `purify`.
    dir0 / dirN: optional unit vectors; the first / last thrust vector must be parallel to them ("thrust direction is
    the attitude": start attitude and upright landing as linear constraints on the thrust vector).
    """
    r0, v0, target = map(np.asarray, (r0, v0, target))
    rho1, rho2 = T_bounds if T_bounds is not None else (veh.T_min, veh.T_max)
    alpha = veh.alpha
    dt = tf / N
    x = cp.Variable((N + 1, 3))
    v = cp.Variable((N + 1, 3))
    w = cp.Variable(N + 1)
    u = cp.Variable((N, 3))
    sg = cp.Variable(N) if fixed_sigma is None else fixed_sigma
    c = [x[0] == r0, v[0] == v0, w[0] == np.log(m0), x[N] == target, v[N] == 0, w[N] >= np.log(veh.m_dry)]
    if dyn == 'euler':
        c += [x[1:] == x[:-1] + dt * v[:-1],
              v[1:] == v[:-1] + dt * (u + GVEC[None, :])]
    else:  # exact for piecewise-constant u
        c += [x[1:] == x[:-1] + dt * v[:-1] + 0.5 * dt**2 * (u + GVEC[None, :]),
              v[1:] == v[:-1] + dt * (u + GVEC[None, :])]
    c += [w[1:] == w[:-1] - dt * alpha * sg]
    if mass_bounds == 'taylor_rust':
        z0 = _mass_taylor_rust(m0, alpha, rho2, dt, N)
        e = np.exp(-z0)
        c += [sg >= rho1 * cp.multiply(e, 1 - (w[:-1] - z0)),
              sg <= rho2 * cp.multiply(e, 1 - (w[:-1] - z0))]
    else:  # relaxation of rho1 e^-z <= sigma <= rho2 e^-z on the reachable z-range
        tk = dt * np.arange(N)
        zlo = np.log(np.maximum(m0 - alpha * rho2 * tk, 1e-3))
        zhi = np.log(m0 - alpha * rho1 * tk)
        z0 = 0.5 * (zlo + zhi)
        e0 = np.exp(-z0)
        c += [sg >= rho1 * cp.multiply(e0, 1 - (w[:-1] - z0))]          # tangent below convex => relaxation
        slope = np.where(zhi - zlo > 1e-12, (np.exp(-zhi) - np.exp(-zlo)) / np.maximum(zhi - zlo, 1e-12), -np.exp(-zlo))
        c += [sg <= rho2 * (np.exp(-zlo) + cp.multiply(slope, w[:-1] - zlo)),  # secant above convex => relaxation
              w[:-1] >= zlo - 1e-9, w[:-1] <= zhi + 1e-9]
    c += [cp.norm(u, axis=1) <= sg]
    if pointing is not None:
        d = np.array([0.0, 0.0, 1.0])
        c += [cp.norm(u - cp.reshape(sg, (N, 1), order='C') @ d[None, :], axis=1) <= np.sin(pointing) * sg]
    if v_max is not None:
        c += [cp.norm(v[:N], axis=1) <= v_max]
    if glide is not None:
        c += [cp.norm(x[1:, :2] - target[None, :2], axis=1) <= (x[1:, 2] - target[2]) / np.tan(glide)]
    for k_, d_ in ((0, dir0), (N - 1, dirN)):
        if d_ is not None:
            d_ = np.asarray(d_, float) / np.linalg.norm(d_)
            c += [u[k_] == (u[k_] @ d_) * d_, u[k_] @ d_ >= 0]
    if rate is not None:
        D1, D2 = rate
        c += [cp.norm(u[1:] - u[:-1], axis=1) <= D1]
        if D2 is not None:
            c += [cp.norm(u[2:] - 2 * u[1:-1] + u[:-2], axis=1) <= D2]
    if lin_obj is not None:
        obj = cp.Maximize(cp.sum(cp.multiply(lin_obj, u)))
    else:
        obj = cp.Minimize(cp.sum(sg) * dt)
    prob = cp.Problem(obj, c)
    status, st = _solve(prob)
    t = np.linspace(0, tf, N + 1)
    if status not in ('optimal', 'optimal_inaccurate') or x.value is None:
        return Plan3(tf, t, None, None, None, None, None, np.inf, dyn, status, st)
    sgv = sg.value if fixed_sigma is None else fixed_sigma
    m = np.exp(w.value)
    return Plan3(tf, t, x.value, v.value, m, u.value, np.asarray(sgv), float(m0 - m[-1]), dyn, status, st)


def solve_baseline_A(r0, v0, m0, target, tf, veh, dt=0.2, glide=None, v_max=15.0, T_bounds=None):
    """Faithful flight-code LCvx at a fixed time of flight (rounded to the grid)."""
    N = max(int(round(tf / dt)), 2)
    return solve_3dof(r0, v0, m0, target, N * dt, N, veh, dyn='euler', T_bounds=T_bounds,
                      pointing=np.radians(15.0), v_max=v_max, glide=glide, mass_bounds='taylor_rust')


def tf_search_A(r0, v0, m0, target, veh, coarse_dt=0.5, fine_dt=0.2, v_max=15.0, glide=None, T_bounds=None):
    """Time-of-flight search exactly as LosslessSolver::solve (shortest feasible on the coarse grid, then one fine solve)."""
    rho1, rho2 = T_bounds if T_bounds is not None else (veh.T_min, veh.T_max)
    fuel = m0 - veh.m_dry
    t_min = veh.m_dry * np.linalg.norm(v0) / rho2
    t_max = fuel / (veh.alpha * rho1)
    plan, n_solves, total = None, 0, 0.0
    for k in range(max(int(np.ceil(t_min / coarse_dt)), 2), int(t_max / coarse_dt) + 1):
        p = solve_3dof(r0, v0, m0, target, k * coarse_dt, k, veh, dyn='euler', T_bounds=T_bounds,
                       pointing=np.radians(15.0), v_max=v_max, glide=glide)
        n_solves += 1
        total += p.solve_time
        if p.r is not None:
            plan = p
            break
        if k * coarse_dt > 30:
            break
    if plan is None:
        return None
    kf = int(np.ceil(plan.tf / fine_dt))
    p = solve_3dof(r0, v0, m0, target, kf * fine_dt, kf, veh, dyn='euler', T_bounds=T_bounds,
                   pointing=np.radians(15.0), v_max=v_max, glide=glide)
    n_solves += 1
    total += p.solve_time
    if p.r is not None:
        plan = p
    plan.info.update(n_solves=n_solves, total_solve_time=total)
    return plan


def size_rate_limits(rho, h, omega_allow, alpha_allow):
    """Thrust-vector difference bounds (in the units of rho) that, IF the relaxation is tight with ||T_k|| >= rho,
    keep the thrust-direction angular rate <= omega_allow (chord bound, claim N4) and the angular acceleration
    <= alpha_allow (continuous-time bound a <= (D2 + 2 D1 w)/rho, claim N5)."""
    D1 = 2 * rho * np.sin(omega_allow * h / 2)
    d1 = D1 / h
    d2 = rho * alpha_allow - 2 * d1 * omega_allow
    if d2 <= 0:
        raise ValueError('alpha_allow must exceed 2 omega_allow^2')
    return D1, d2 * h**2


def solve_candidate_C(r0, v0, m0, target, tf, veh, cfg, N=None, omega_allow=0.3, alpha_allow=None, sizing='sound',
                      glide='cfg', dir0=None, dirN=None):
    """3DOF LCvx (ZOH-exact dynamics, planner throttle margins, 15 deg tilt cone) + thrust-vector rate limits.

    sizing='sound': D1, D2 from the chord bound for (omega_allow, alpha_allow) (guarantee if tight);
    sizing='throttle': D1 from the throttle slew only, D2 from alpha_allow (no rate guarantee from D1).
    """
    N = N or cfg.N
    h = tf / N
    if alpha_allow is None:  # half the TVC angular acceleration at minimum planned thrust and planned gimbal
        alpha_allow = 0.5 * veh.L * cfg.T_min_plan * np.sin(cfg.gimbal_plan) / veh.J_t
    rho_u = cfg.T_min_plan / m0
    if sizing == 'sound':
        D1, D2 = size_rate_limits(rho_u, h, omega_allow, alpha_allow)
    else:
        D1 = cfg.thrust_rate_plan * h / m0
        D2 = rho_u * alpha_allow * h**2
    g = cfg.glide_slope if glide == 'cfg' else glide
    p = solve_3dof(r0, v0, m0, target, tf, N, veh, dyn='zoh', T_bounds=(cfg.T_min_plan, cfg.T_max_plan),
                   pointing=cfg.tilt_max, v_max=None, glide=g, rate=(D1, D2), mass_bounds='taylor_rust',
                   dir0=dir0, dirN=dirN)
    p.info.update(D1=D1, D2=D2, omega_allow=omega_allow, alpha_allow=alpha_allow, sizing=sizing)
    return p


def solve_3dof_relaxation(r0, v0, m0, target, tf, veh, cfg, N=None, glide='cfg', pointing=None):
    """3DOF relaxation of the 6DOF planning problem: same throttle range and state constraints, no attitude."""
    N = N or cfg.N
    g = cfg.glide_slope if glide == 'cfg' else glide
    return solve_3dof(r0, v0, m0, target, tf, N, veh, dyn='zoh', T_bounds=(cfg.T_min_plan, cfg.T_max_plan),
                      pointing=pointing, v_max=None, glide=g, mass_bounds='relax')


def optimal_tf_3dof(r0, v0, m0, target, veh, cfg, lo=None, hi=None, N=40, tol=0.05, glide='cfg', pointing=None):
    """Golden-section search for the fuel-optimal time of flight of the 3DOF relaxation."""
    def f(tf):
        p = solve_3dof_relaxation(r0, v0, m0, target, tf, veh, cfg, N=N, glide=glide, pointing=pointing)
        return p.fuel
    # bracket: smallest feasible tf by scanning
    lo = lo or 2.0
    hi = hi or 20.0
    grid = np.arange(lo, hi + 1e-9, 0.5)
    vals = [f(t) for t in grid]
    finite = [i for i, val in enumerate(vals) if np.isfinite(val)]
    if not finite:
        return None, np.inf
    i = min(finite, key=lambda i: vals[i])
    a, b = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    if not np.isfinite(vals[max(i - 1, 0)]):
        a = grid[i]
    gr = (np.sqrt(5) - 1) / 2
    c1, c2 = b - gr * (b - a), a + gr * (b - a)
    f1, f2 = f(c1), f(c2)
    while b - a > tol:
        if f1 < f2:
            b, c2, f2 = c2, c1, f1
            c1 = b - gr * (b - a)
            f1 = f(c1)
        else:
            a, c1, f1 = c1, c2, f2
            c2 = a + gr * (b - a)
            f2 = f(c2)
    tf = 0.5 * (a + b)
    return tf, f(tf)


def purify(plan, r0, v0, m0, target, veh, seed=0, **kw):
    """C-K2 purification: keep sigma*, maximise a random linear functional of u over the same constraints.
    The result has the same fuel and (generically) at most (1/2) sum c_i lossy nodes."""
    rng = np.random.default_rng(seed)
    lin = rng.normal(size=plan.u.shape)
    p = solve_3dof(r0, v0, m0, target, plan.tf, plan.N, veh, fixed_sigma=plan.sigma, lin_obj=lin, dyn=plan.dyn, **kw)
    if p.r is not None:
        p.fuel = plan.fuel
    return p


def direction_rates(plan):
    """Thrust-direction angular rate and acceleration demanded by a 3DOF plan (per node), rad/s and rad/s^2."""
    T = plan.u
    d = T / np.maximum(np.linalg.norm(T, axis=1, keepdims=True), 1e-12)
    h = plan.tf / plan.N
    ang = np.arccos(np.clip(np.sum(d[1:] * d[:-1], axis=1), -1, 1))
    rate = ang / h
    acc = np.abs(np.diff(rate)) / h if len(rate) > 1 else np.zeros(0)
    # second-difference based acceleration of the unit vector (captures turning, not only speed changes)
    acc2 = np.linalg.norm(d[2:] - 2 * d[1:-1] + d[:-2], axis=1) / h**2
    return rate, np.maximum(acc, 0), acc2
