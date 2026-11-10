"""Certificate for planner F: checks the returned plan (not the optimiser) and replays it open loop.

* `check_limits`: evaluates the exact flat map on a dense time grid and compares throttle, gimbal angles (flight
  convention), gimbal rate, throttle rate, tilt, altitude / glide slope and the boundary conditions with the PHYSICAL
  limits (and reports the margins to the planning limits).
* `replay`: integrates the full quaternion rigid body (dynamics.deriv), open loop, with the plan's throttle and gimbal
  commands as the only inputs. Three plant models:
      'cop'    centre of percussion fixed in the body, J_t(m) = eps m L  (the planning model; the replay error is then
               pure integration error)
      'frozen' J_t and L frozen at their initial values (the model planners B / S and their certificate use)
      'table'  J_t(m), L(m) from the sim-plant table (what the closed-loop simulator uses)
"""
import numpy as np
from scipy.integrate import solve_ivp

from .dynamics import deriv
from .rotations import quat_to_R, R_to_quat, gimbal_angles, tilt_of_R


def plan_frame(traj, R0, rtol=1e-12, atol=1e-13):
    """Body frame R(t) of the plan: the frame transported along b(t) with zero roll rate. Dense quaternion solution."""
    def f(t, q):
        e = traj.eval(np.array([t]), mass=False)
        w = np.cross(e['b'][0], e['bd'][0])                       # world angular velocity (perpendicular to b)
        qw, qv = q[0], q[1:]
        return 0.5 * np.concatenate([[-qv @ w], qw * w - np.cross(qv, w)])   # qdot = 0.5 * (0,w_world) * q
    sol = solve_ivp(f, (0.0, traj.tf), R_to_quat(R0), method='DOP853', rtol=rtol, atol=atol, dense_output=True)
    return sol.sol


def body_thrust(traj, frame, t):
    """Planned body-frame thrust vector [N] at scalar time t."""
    e = traj.eval(np.array([t]))
    q = frame(t)
    R = quat_to_R(q / np.linalg.norm(q))
    Tw = e['Ta'][0] * e['b'][0] + e['Tlat_w'][0]
    return R.T @ Tw


def replay(traj, veh, r0, v0, m0, R0, w0, model='cop', L=None, rtol=1e-12, atol=1e-13, frame=None):
    """Open-loop 6DOF replay. Returns the final 14-state."""
    frame = frame or plan_frame(traj, R0)
    J0, L0 = veh.inertia_lever(m0)
    L = L if L is not None else veh.L

    def props(m):
        if model == 'cop':
            return traj.eps * m * L, L
        if model == 'frozen':
            return J0, L0
        return veh.inertia_lever(m)

    def f(t, x):
        J, Lm = props(x[13])
        return deriv(x, body_thrust(traj, frame, t), 0.0, J, veh.J_z, Lm, veh.alpha)
    x0 = np.concatenate([r0, v0, R_to_quat(R0), [w0[0], w0[1], 0.0], [m0]])
    sol = solve_ivp(f, (0.0, traj.tf), x0, method='DOP853', rtol=rtol, atol=atol)
    return sol.y[:, -1]


def check_limits(plan, veh, cfg, r0, v0, m0, R0, w0, target, n=2001, frame=None):
    traj = plan.traj
    t = np.linspace(0.0, traj.tf, n)
    e = traj.eval(t)
    frame = frame or plan_frame(traj, R0)
    Tb = np.array([body_thrust(traj, frame, ti) for ti in t[::10]])
    ang = np.array([gimbal_angles(tb) for tb in Tb])
    tilt = np.arccos(np.clip(e['b'][:, 2], -1, 1))
    rz = e['r'][:, 2] - target[2]
    lat = np.linalg.norm(e['r'][:, :2] - target[None, :2], axis=1)
    gs = 0.0 if cfg.glide_slope is None else float(np.max(lat[1:] * np.tan(cfg.glide_slope) - rz[1:]))
    out = dict(T_min=float(e['T'].min()), T_max=float(e['T'].max()),
               gimbal_max_deg=float(np.degrees(np.abs(ang).max())),
               gimbal_cone_max_deg=float(np.degrees(np.arctan(e['gim_tan'].max()))),
               gimbal_rate_max_dps=float(np.degrees(e['gim_rate'].max())),
               thrust_rate_max=float(np.abs(e['T_dot']).max()),
               tilt_max_deg=float(np.degrees(tilt.max())),
               body_rate_max=float(np.sqrt(e['w2'].max())),
               ang_acc_max=float(np.linalg.norm(e['Pbdd'], axis=1).max()),
               glide_violation=max(gs, float(-rz.min())),
               bc_r0=float(np.linalg.norm(e['r'][0] - r0)), bc_v0=float(np.linalg.norm(e['v'][0] - v0)),
               bc_b0=float(np.linalg.norm(e['b'][0] - R0[:, 2])),
               bc_w0=float(np.linalg.norm(e['bd'][0] - R0 @ np.array([w0[1], -w0[0], 0.0]))),
               defect_r=float(np.linalg.norm(e['r'][-1] - target)), defect_v=float(np.linalg.norm(e['v'][-1])),
               terminal_tilt_deg=float(np.degrees(tilt[-1])), terminal_rate=float(np.sqrt(e['w2'][-1])),
               m_final=float(e['m'][-1]))
    out['checks'] = dict(
        throttle=veh.T_min - 1e-6 <= out['T_min'] and out['T_max'] <= veh.T_max + 1e-6,
        throttle_plan=cfg.T_min_plan - 1e-6 <= out['T_min'] and out['T_max'] <= cfg.T_max_plan + 1e-6,
        gimbal=out['gimbal_max_deg'] <= np.degrees(veh.gimbal_max) + 1e-6,
        gimbal_plan=out['gimbal_cone_max_deg'] <= np.degrees(cfg.gimbal_plan) + 1e-6,
        gimbal_rate=out['gimbal_rate_max_dps'] <= np.degrees(veh.gimbal_rate) + 1e-6,
        thrust_rate=out['thrust_rate_max'] <= veh.thrust_rate + 1e-6,
        tilt=out['tilt_max_deg'] <= np.degrees(cfg.tilt_max) + 1e-6,
        state=out['glide_violation'] <= 0.02,
        boundary=max(out['bc_r0'], out['bc_v0'], out['bc_b0'], out['bc_w0']) <= 1e-6,
        terminal=out['defect_r'] <= 1e-6 and out['defect_v'] <= 1e-6 and out['terminal_tilt_deg'] <= 1e-4
        and out['terminal_rate'] <= 1e-6)
    return out


def certify_F(plan, veh, cfg, r0, v0, m0, R0, w0, target, models=('cop',), tol_r=0.05, tol_v=0.05):
    if plan.traj is None:
        return dict(passed=False, reason='no plan')
    r0, v0, target = (np.asarray(z, float) for z in (r0, v0, target))
    frame = plan_frame(plan.traj, R0)
    out = check_limits(plan, veh, cfg, r0, v0, m0, R0, w0, target, frame=frame)
    for mdl in models:
        xf = replay(plan.traj, veh, r0, v0, m0, R0, w0, model=mdl, frame=frame)
        out[f'replay_{mdl}_dr'] = float(np.linalg.norm(xf[0:3] - target))
        out[f'replay_{mdl}_dv'] = float(np.linalg.norm(xf[3:6]))
        out[f'replay_{mdl}_tilt_deg'] = float(np.degrees(tilt_of_R(quat_to_R(xf[6:10]))))
        out[f'replay_{mdl}_dm'] = float(abs(xf[13] - out['m_final']))
    m = models[0]
    out['checks']['replay'] = out[f'replay_{m}_dr'] <= tol_r and out[f'replay_{m}_dv'] <= tol_v
    out['passed'] = bool(all(v for k, v in out['checks'].items() if not k.endswith('_plan')))
    return out
