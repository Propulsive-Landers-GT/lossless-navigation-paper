"""A-posteriori certificates.

certify_B(plan): every planner-B output is checked on the fine quadrature grid against the PHYSICAL limits (throttle,
15 deg gimbal box in the flight-code convention, 100 deg/s gimbal slew, 2000 N/s throttle slew), the planner's state
constraints, the terminal conditions, and by an open-loop replay of the plan's body-frame thrust through the full
6DOF quaternion rigid-body model (no feedback). PASS means: the plan is a trajectory the torque-limited body can fly.

certify_3dof(plan): the checks that apply to a 3DOF plan (tightness ||u|| = sigma, delivered thrust >= T_min, and the
thrust-direction rate/acceleration it demands versus the TVC angular-acceleration envelope).
"""
import numpy as np

from .dynamics import deriv
from .rotations import R_to_quat, quat_to_R, gimbal_angles, tilt_of_R
from .lcvx3dof import direction_rates


def replay_open_loop(plan, veh, r0, v0, m0, R0, w0, sub=4):
    """Integrate the 6DOF rigid body with the plan's body thrust as a feed-forward input."""
    g = plan.grid
    J, L = veh.inertia_lever(m0)
    x = np.concatenate([r0, v0, R_to_quat(R0), [w0[0], w0[1], 0.0], [m0]])
    Tb = plan.T_body
    dt = g.hs / sub
    for s in range(g.S):
        for j in range(sub):
            lam0, lam1 = j / sub, (j + 1) / sub
            # FOH thrust within the substep; RK4 stages at 0, 1/2, 1
            Ta, Tb1 = Tb[s], Tb[s + 1]
            def Tb_of(lam):
                return (1 - lam) * Ta + lam * Tb1
            k1 = deriv(x, Tb_of(lam0), 0.0, J, veh.J_z, L, veh.alpha)
            lm = 0.5 * (lam0 + lam1)
            k2 = deriv(x + 0.5 * dt * k1, Tb_of(lm), 0.0, J, veh.J_z, L, veh.alpha)
            k3 = deriv(x + 0.5 * dt * k2, Tb_of(lm), 0.0, J, veh.J_z, L, veh.alpha)
            k4 = deriv(x + dt * k3, Tb_of(lam1), 0.0, J, veh.J_z, L, veh.alpha)
            x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            x[6:10] /= np.linalg.norm(x[6:10])
    return x


def certify_B(plan, veh, cfg, r0, v0, m0, R0, w0, target, replay=True, tol_r=0.05, tol_v=0.05):
    out = {}
    if plan.T_body is None:
        return dict(passed=False, reason='no plan')
    Tb = plan.T_body
    Tn = np.linalg.norm(Tb, axis=1)
    hs = plan.grid.hs
    out['T_min'] = float(Tn.min())
    out['T_max'] = float(Tn.max())
    ang = np.array([gimbal_angles(t) for t in Tb])
    out['gimbal_max_deg'] = float(np.degrees(np.abs(ang).max()))
    out['gimbal_rate_max_dps'] = float(np.degrees(np.abs(np.diff(ang, axis=0)).max() / hs))
    out['thrust_rate_max'] = float(np.abs(np.diff(Tn)).max() / hs)
    tilt = np.arccos(np.clip(plan.att['b'][:, 2], -1, 1))
    out['tilt_max_deg'] = float(np.degrees(tilt.max()))
    out['ang_acc_max'] = float(np.linalg.norm(plan.att['alpha'], axis=1).max())
    # TVC angular acceleration envelope actually available at the planned thrust: L T sin(mu)/J_t with mu = 15 deg
    J, L = veh.inertia_lever(m0)
    out['ang_acc_ratio'] = float((np.linalg.norm(plan.att['alpha'], axis=1) / (L * Tn * np.sin(veh.gimbal_max) / J)).max())
    rz = plan.r[:, 2] - target[2]
    lat = np.linalg.norm(plan.r[:, :2] - target[None, :2], axis=1)
    gs = 0.0 if cfg.glide_slope is None else float(np.max(lat[1:] * np.tan(cfg.glide_slope) - rz[1:]))
    out['glide_violation'] = max(gs, float(-rz.min()))
    out['defect_r'], out['defect_v'] = plan.defect['r'], plan.defect['v']
    out['terminal_tilt_deg'] = float(np.degrees(tilt[-1]))
    out['terminal_rate'] = float(np.linalg.norm(plan.att['w'][-1]))
    checks = dict(
        throttle=veh.T_min - 1e-6 <= out['T_min'] and out['T_max'] <= veh.T_max + 1e-6,
        gimbal=out['gimbal_max_deg'] <= np.degrees(veh.gimbal_max) + 1e-6,
        gimbal_rate=out['gimbal_rate_max_dps'] <= np.degrees(veh.gimbal_rate) + 1e-6,
        thrust_rate=out['thrust_rate_max'] <= veh.thrust_rate + 1e-6,
        tilt=out['tilt_max_deg'] <= np.degrees(cfg.tilt_max) + 0.5,
        state=out['glide_violation'] <= 0.02,
        terminal=out['defect_r'] <= 0.01 and out['defect_v'] <= 0.01
        and out['terminal_tilt_deg'] <= np.degrees(cfg.terminal_tilt_tol) and out['terminal_rate'] <= 1e-3,
    )
    if replay:
        xf = replay_open_loop(plan, veh, np.asarray(r0, float), np.asarray(v0, float), m0, R0, w0)
        out['replay_dr'] = float(np.linalg.norm(xf[0:3] - target))
        out['replay_dv'] = float(np.linalg.norm(xf[3:6]))
        out['replay_tilt_deg'] = float(np.degrees(tilt_of_R(quat_to_R(xf[6:10]))))
        out['replay_dm'] = float(abs(xf[13] - plan.m[-1]))
        checks['replay'] = out['replay_dr'] <= tol_r and out['replay_dv'] <= tol_v and out['replay_tilt_deg'] <= 1.0
    out['checks'] = checks
    out['passed'] = bool(all(checks.values()))
    return out


def certify_3dof(plan, veh, tol=1e-3):
    """Checks that a 3DOF plan can satisfy: tightness and delivered thrust, plus the TVC envelope test."""
    if plan.u is None:
        return dict(passed=False, reason='infeasible')
    tight = plan.tightness()
    Tdel = np.linalg.norm(plan.T, axis=1)
    rate, acc, acc2 = direction_rates(plan)
    J, L = veh.J_t, veh.L
    amax = L * veh.T_min * np.sin(veh.gimbal_max) / J      # worst-case available angular acceleration
    out = dict(tight_min=float(tight.min()), n_lossy=int(np.sum(tight < 1 - tol)),
               T_delivered_min=float(Tdel.min()), dir_rate_max=float(rate.max(initial=0)),
               dir_acc_max=float(acc2.max(initial=0)), alpha_available=float(amax))
    out['checks'] = dict(tight=out['n_lossy'] == 0, throttle=out['T_delivered_min'] >= veh.T_min - 1e-6,
                         ang_acc=out['dir_acc_max'] <= amax)
    out['passed'] = bool(all(out['checks'].values()))
    return out
