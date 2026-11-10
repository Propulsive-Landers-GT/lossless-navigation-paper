"""Closed-loop 6DOF simulation: plant (500 Hz), tracking controller (50 Hz), guidance replanning (1 Hz).

Plant: rigid body with pure-TVC torque coupling, 15 deg per-axis gimbal box with 100 deg/s slew, throttle 400-1000 N
with 2000 N/s slew, mass depletion with mass-dependent J_t and lever arm (sim-plant table), RCS roll (3 N m bang-bang),
optional wind drag, thrust-magnitude noise, gimbal misalignment and Isp error.

Controller ("CoP-LQR"): tracks the plan in centre-of-percussion coordinates y = r + eps b (eps = J_t/(m L)), where the
gimbal's lateral force cancels exactly (FLAT): y'' = f b - g. Per horizontal axis an LQR on [y, y', b, b'] commands
b'' (i.e. body angular acceleration = gimbal lateral thrust), the vertical channel commands the axial thrust.
Feed-forward is taken from the plan (b, b', b'', axial thrust). 3DOF plans provide only r, v, thrust vector.
"""
from dataclasses import dataclass, field
import time
import numpy as np
from scipy.linalg import solve_continuous_are

from .params import G0
from .rotations import quat_to_R, R_to_quat, gimbal_angles, gimbal_dir, tilt_of_R, hat
from .dynamics import deriv

E3 = np.array([0.0, 0.0, 1.0])


# ---------------------------------------------------------------- references
class Reference:
    """Time-indexed reference built from a plan; t is absolute sim time."""

    def __init__(self, t0, ts, r, v, a, b, bd, bdd, Ta, m, kind, tf_abs):
        self.t0, self.ts, self.r, self.v, self.a = t0, ts, r, v, a
        self.b, self.bd, self.bdd, self.Ta, self.m, self.kind = b, bd, bdd, Ta, m, kind
        self.tf_abs = tf_abs

    @staticmethod
    def from_planB(plan, t0):
        R, w, al = plan.att['R'], plan.att['w'], plan.att['alpha']
        b = R[:, :, 2]
        bd = np.einsum('sij,sj->si', R, np.cross(w, E3))
        bdd = np.einsum('sij,sj->si', R, np.cross(al, E3) + np.cross(w, np.cross(w, E3)))
        return Reference(t0, plan.grid.ts.copy(), plan.r, plan.v, plan.a, b, bd, bdd, plan.T_body[:, 2], plan.m,
                         'B', t0 + plan.tf)

    @staticmethod
    def from_planF(plan, t0, dt=0.02):
        """Reference from a flat plan: every quantity is the exact flat map of the spline, sampled every `dt`."""
        tr = plan.traj
        ts = np.linspace(0.0, tr.tf, max(int(np.ceil(tr.tf / dt)), 2) + 1)
        e = tr.eval(ts)
        return Reference(t0, ts, e['r'], e['v'], e['acc'], e['b'], e['bd'], e['bdd'], e['Ta'], e['m'], 'F', t0 + tr.tf)

    @staticmethod
    def from_plan3(plan, t0):
        # piecewise-linear r, v at nodes (as the flight autopilot interpolates); thrust direction held per interval
        N = plan.N
        ts = np.repeat(plan.t, 2)[1:-1]                 # duplicate interior nodes -> ZOH thrust representable
        idx = np.repeat(np.arange(N + 1), 2)[1:-1]
        k_int = np.repeat(np.arange(N), 2)
        Tw = plan.T[k_int]
        Tn = np.linalg.norm(Tw, axis=1)
        b = Tw / Tn[:, None]
        a = Tw / plan.m[idx][:, None] + np.array([0, 0, -G0])
        z = np.zeros_like(b)
        return Reference(t0, ts, plan.r[idx], plan.v[idx], a, b, z, z, Tn, plan.m[idx], '3dof', t0 + plan.tf)

    def at(self, t):
        tau = t - self.t0
        if tau >= self.ts[-1]:   # after the plan: hold the end point, sink slowly onto the pad
            dt = tau - self.ts[-1]
            r = self.r[-1] + np.array([0, 0, -0.3 * dt])
            return dict(r=r, v=np.array([0, 0, -0.3]), a=np.zeros(3), b=E3, bd=np.zeros(3), bdd=np.zeros(3),
                        Ta=None, after=True)
        i = int(np.clip(np.searchsorted(self.ts, tau, side='right') - 1, 0, len(self.ts) - 2))
        t0, t1 = self.ts[i], self.ts[i + 1]
        lam = 0.0 if t1 <= t0 else (tau - t0) / (t1 - t0)
        L = lambda arr: (1 - lam) * arr[i] + lam * arr[i + 1]
        b = L(self.b)
        return dict(r=L(self.r), v=L(self.v), a=L(self.a), b=b / np.linalg.norm(b), bd=L(self.bd), bdd=L(self.bdd),
                    Ta=L(self.Ta), after=False)


# ---------------------------------------------------------------- controller
@dataclass
class CoPLQR:
    veh: object
    sig_y: float = 0.5      # m
    sig_v: float = 0.8      # m/s
    sig_b: float = 0.06     # rad
    sig_bd: float = 0.25    # rad/s
    sig_u: float = 0.35     # rad/s^2
    kp_z: float = 1.2
    kd_z: float = 1.6
    rcs_deadband: float = 0.02

    def __post_init__(self):
        F = G0
        A = np.array([[0, 1, 0, 0], [0, 0, F, 0], [0, 0, 0, 1], [0, 0, 0, 0.0]])
        B = np.array([[0], [0], [0], [1.0]])
        Q = np.diag([1 / self.sig_y**2, 1 / self.sig_v**2, 1 / self.sig_b**2, 1 / self.sig_bd**2])
        Rm = np.array([[1 / self.sig_u**2]])
        P = solve_continuous_are(A, B, Q, Rm)
        self.K = (np.linalg.solve(Rm, B.T @ P)).ravel()

    def __call__(self, x, ref, J_t, L):
        veh = self.veh
        r, v, q, w, m = x[0:3], x[3:6], x[6:10], x[10:13], x[13]
        R = quat_to_R(q)
        b = R[:, 2]
        ww = R @ np.array([w[0], w[1], 0.0])
        bd = np.cross(ww, b)
        eps = J_t / (m * L)
        y, yd = r + eps * b, v + eps * bd
        yr, ydr = ref['r'] + eps * ref['b'], ref['v'] + eps * ref['bd']
        ydd_r = ref['a'] + eps * ref['bdd']
        bdd_cmd = ref['bdd'].copy()
        for i in (0, 1):
            e = np.array([y[i] - yr[i], yd[i] - ydr[i], b[i] - ref['b'][i], bd[i] - ref['bd'][i]])
            bdd_cmd[i] = ref['bdd'][i] - self.K @ e
        # vertical channel on the CoP (y'' = f b - g)
        yzdd = ydd_r[2] - self.kp_z * (y[2] - yr[2]) - self.kd_z * (yd[2] - ydr[2])
        f_cmd = (yzdd + G0) / max(b[2], 0.5)
        Ta = m * (f_cmd + eps * (ww @ ww))
        # body angular acceleration from b'' (component perpendicular to b), then gimbal lateral thrust
        qv = bdd_cmd - np.cross(ww, np.cross(ww, b))
        wdot_w = np.cross(b, qv)
        al = R.T @ wdot_w
        k = J_t / L
        Tb = np.array([-k * al[1], k * al[0], Ta])
        th, ph = gimbal_angles(Tb) if Ta > 1 else (0.0, 0.0)
        Tmag = np.linalg.norm(Tb)
        tau_z = 0.0 if abs(w[2]) < self.rcs_deadband else -np.sign(w[2]) * veh.rcs_torque
        return th, ph, Tmag, tau_z


# ---------------------------------------------------------------- simulation
@dataclass
class SimOptions:
    dt: float = 0.002          # plant step (500 Hz)
    ctrl_dt: float = 0.02      # controller (50 Hz)
    replan_dt: float = 1.0     # guidance (1 Hz)
    t_lock: float = 1.5        # stop replanning when less than this remains
    t_extra: float = 4.0       # max time after the plan ends
    wind: tuple = (0.0, 0.0, 0.0)
    gust_sigma: float = 0.0
    drag_CdA: float = 0.2      # m^2
    thrust_noise: float = 0.0  # relative 1-sigma, per control tick
    gimbal_bias: tuple = (0.0, 0.0)   # rad
    isp_error: float = 0.0     # relative error of the true Isp vs guidance
    seed: int = 0
    log: bool = False
    latency: bool = False      # if True, a replan computed from the state at time t is applied at t + its solver time
    latency_key: str = 'solve_time'
    latency_scale: float = 1.0


def simulate(x0, target, planner, veh, opts=SimOptions(), controller=None):
    """planner(t, x, prev_ref) -> (Reference or None, info dict). Returns metrics dict (and log if requested)."""
    rng = np.random.default_rng(opts.seed)
    ctrl = controller or CoPLQR(veh)
    x = np.array(x0, float)
    target = np.asarray(target, float)
    alpha_true = veh.alpha / (1 + opts.isp_error)
    th_a, ph_a = 0.0, 0.0
    J0, L0 = veh.inertia_lever(x[13])
    T_a = x[13] * G0
    t = 0.0
    ref, infos = None, []
    ref, info = planner(0.0, x.copy(), None, (0.0, 0.0, T_a))
    infos.append(info)
    if ref is None:
        return dict(failed='initial plan failed', infos=infos)
    next_replan = opts.replan_dt
    pending = None
    cmd = (0.0, 0.0, T_a, 0.0)
    noise = 1.0
    gust = np.zeros(3)
    log = []
    max_tilt = 0.0
    sat_g = sat_T = 0
    n_ctrl = 0
    gim_travel = thr_travel = gim_sq = 0.0      # actuator effort: total gimbal travel [rad], throttle travel [N]
    min_glide_margin = np.inf
    t_end = ref.tf_abs + opts.t_extra
    touchdown = None
    fuel_tf = None
    n_steps_ctrl = int(round(opts.ctrl_dt / opts.dt))
    step = 0
    while t < t_end:
        if pending is not None and t >= pending[0] - 1e-9:
            ref = pending[1]
            t_end = ref.tf_abs + opts.t_extra
            pending = None
        if t >= next_replan - 1e-9 and ref.tf_abs - t > opts.t_lock and pending is None:
            new, info = planner(t, x.copy(), ref, (th_a, ph_a, T_a))
            infos.append(info)
            if new is not None:
                if opts.latency:
                    pending = (t + opts.latency_scale * (info.get(opts.latency_key) or 0.0), new)
                else:
                    ref = new
                    t_end = ref.tf_abs + opts.t_extra
            next_replan = max(next_replan + opts.replan_dt, t + 1e-9) if not opts.latency else \
                max(next_replan + opts.replan_dt, (pending[0] if pending is not None else t) + 1e-9)
        J, L = veh.inertia_lever(x[13])
        if step % n_steps_ctrl == 0:
            rf = ref.at(t)
            cmd = ctrl(x, rf, J, L)
            n_ctrl += 1
            noise = 1.0 + opts.thrust_noise * rng.normal()
            if opts.gust_sigma > 0:
                gust = 0.95 * gust + np.sqrt(1 - 0.95**2) * opts.gust_sigma * rng.normal(size=3)
            th_c, ph_c, T_c, tz = cmd
            if abs(th_c) > veh.gimbal_max or abs(ph_c) > veh.gimbal_max:
                sat_g += 1
            if T_c > veh.T_max or T_c < veh.T_min:
                sat_T += 1
        th_c, ph_c, T_c, tz = cmd
        th_c = np.clip(th_c, -veh.gimbal_max, veh.gimbal_max)
        ph_c = np.clip(ph_c, -veh.gimbal_max, veh.gimbal_max)
        T_c = np.clip(T_c, veh.T_min, veh.T_max)
        dg = veh.gimbal_rate * opts.dt
        d_th, d_ph = np.clip(th_c - th_a, -dg, dg), np.clip(ph_c - ph_a, -dg, dg)
        d_T = np.clip(T_c - T_a, -veh.thrust_rate * opts.dt, veh.thrust_rate * opts.dt)
        th_a += d_th
        ph_a += d_ph
        T_a += d_T
        gim_travel += abs(d_th) + abs(d_ph)
        thr_travel += abs(d_T)
        gim_sq += (th_a**2 + ph_a**2) * opts.dt
        Tb = T_a * noise * gimbal_dir(th_a + opts.gimbal_bias[0], ph_a + opts.gimbal_bias[1])
        vrel = x[3:6] - (np.array(opts.wind) + gust)
        F_drag = -0.5 * 1.225 * opts.drag_CdA * np.linalg.norm(vrel) * vrel
        f = lambda xx: deriv(xx, Tb, tz, J, veh.J_z, L, alpha_true, F_ext=F_drag)
        k1 = f(x); k2 = f(x + 0.5 * opts.dt * k1); k3 = f(x + 0.5 * opts.dt * k2); k4 = f(x + opts.dt * k3)
        x = x + opts.dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        x[6:10] /= np.linalg.norm(x[6:10])
        t += opts.dt
        step += 1
        R = quat_to_R(x[6:10])
        tilt = tilt_of_R(R)
        max_tilt = max(max_tilt, tilt)
        rz = x[2] - target[2]
        lat = np.linalg.norm(x[:2] - target[:2])
        min_glide_margin = min(min_glide_margin, rz)
        if fuel_tf is None and t >= ref.tf_abs:
            fuel_tf = float(x0[13] - x[13])
        if opts.log and step % 10 == 0:
            log.append(np.concatenate([[t], x, [th_a, ph_a, T_a, tilt]]))
        if x[2] <= target[2] + 0.01 and t > 0.5:
            touchdown = t
            break
        if x[13] <= veh.m_dry:
            break
    R = quat_to_R(x[6:10])
    out = dict(t_td=touchdown if touchdown is not None else t, touched=touchdown is not None,
               pos_err=float(np.linalg.norm(x[:2] - target[:2])), vz=float(x[5]), vlat=float(np.linalg.norm(x[3:5])),
               speed=float(np.linalg.norm(x[3:6])), tilt_deg=float(np.degrees(tilt_of_R(R))),
               rate=float(np.linalg.norm(x[10:12])), fuel=float(x0[13] - x[13]),
               fuel_tf=fuel_tf if fuel_tf is not None else float(x0[13] - x[13]), tf_final=float(ref.tf_abs), max_tilt_deg=float(np.degrees(max_tilt)),
               gimbal_sat_frac=sat_g / max(n_ctrl, 1), thrust_sat_frac=sat_T / max(n_ctrl, 1),
               min_alt_margin=float(min_glide_margin), infos=infos,
               gimbal_travel_deg=float(np.degrees(gim_travel)), thrust_travel=float(thr_travel),
               gimbal_rms_deg=float(np.degrees(np.sqrt(gim_sq / max(t, 1e-9)))))
    out['success'] = bool(out['touched'] and out['speed'] <= 1.0 and out['pos_err'] <= 1.0 and out['tilt_deg'] <= 5.0)
    if opts.log:
        out['log'] = np.array(log)
    return out
