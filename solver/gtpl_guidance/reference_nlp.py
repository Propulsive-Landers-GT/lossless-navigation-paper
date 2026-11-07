"""Reference D: nonconvex 6DOF optimal control (CasADi + IPOPT, multiple shooting, multiple starts).

Same vehicle model, same function class (first-order-hold body thrust) and the same constraint set as planner B
(planned throttle range, tan-gimbal limits, linear rate conditions, tilt limit, glide slope, upright at rest at t_f),
but with the attitude as a free decision (full quaternion rigid body, roll torque allowed). Its best local optimum
over several starts measures B's optimality gap. Multistart NLP cannot certify global optimality.
"""
import time
import numpy as np
import casadi as ca

from .params import G0
from .rotations import R_to_quat, quat_to_R


def _dyn_sx(J_t, J_z, L, alpha):
    x = ca.SX.sym('x', 14)
    T = ca.SX.sym('T', 3)
    tz = ca.SX.sym('tz')
    r, v, q, w, m = x[0:3], x[3:6], x[6:10], x[10:13], x[13]
    qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    R = ca.vertcat(
        ca.horzcat(1 - 2 * (qy**2 + qz**2), 2 * (qx * qy - qw * qz), 2 * (qx * qz + qw * qy)),
        ca.horzcat(2 * (qx * qy + qw * qz), 1 - 2 * (qx**2 + qz**2), 2 * (qy * qz - qw * qx)),
        ca.horzcat(2 * (qx * qz - qw * qy), 2 * (qy * qz + qw * qx), 1 - 2 * (qx**2 + qy**2)))
    a = R @ T / m - ca.vertcat(0, 0, G0)
    tau = ca.vertcat(L * T[1], -L * T[0], tz)
    Jv = ca.vertcat(J_t, J_t, J_z)
    wdot = (tau - ca.cross(w, Jv * w)) / Jv
    qv = q[1:4]
    qdot = 0.5 * ca.vertcat(-ca.dot(qv, w), qw * w + ca.cross(qv, w))
    mdot = -alpha * ca.sqrt(ca.sumsqr(T) + 1e-9)
    return ca.Function('f', [x, T, tz], [ca.vertcat(v, a, qdot, wdot, mdot)])


def _interval_fn(f, h, ns):
    x = ca.SX.sym('x', 14)
    T0, T1 = ca.SX.sym('T0', 3), ca.SX.sym('T1', 3)
    z0, z1 = ca.SX.sym('z0'), ca.SX.sym('z1')
    dt = h / ns
    xx = x
    for j in range(ns):
        l0, lm, l1 = j / ns, (j + 0.5) / ns, (j + 1) / ns
        Tl = lambda l: (1 - l) * T0 + l * T1
        zl = lambda l: (1 - l) * z0 + l * z1
        k1 = f(xx, Tl(l0), zl(l0))
        k2 = f(xx + 0.5 * dt * k1, Tl(lm), zl(lm))
        k3 = f(xx + 0.5 * dt * k2, Tl(lm), zl(lm))
        k4 = f(xx + dt * k3, Tl(l1), zl(l1))
        xx = xx + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ca.Function('F', [x, T0, T1, z0, z1], [xx])


def solve_reference(r0, v0, m0, R0, w0, target, tf, veh, cfg, guesses, N=None, ns=4, max_iter=1500, verbose=False):
    """guesses: list of (name, X_guess (N+1,14), T_guess (N+1,3)). Returns dict(best, runs)."""
    N = N or cfg.N
    h = tf / N
    J, L = veh.inertia_lever(m0)
    f = _dyn_sx(J, veh.J_z, L, veh.alpha)
    F = _interval_fn(f, h, ns)
    tg = np.tan(cfg.gimbal_plan)
    ta_floor = cfg.T_min_plan * np.cos(np.arctan(np.sqrt(2) * tg))
    gbud = cfg.gimbal_rate_plan * ta_floor * h
    tbud = cfg.thrust_rate_plan * h
    target = np.asarray(target, float)
    x0 = np.concatenate([r0, v0, R_to_quat(R0), [w0[0], w0[1], 0.0], [m0]])

    opti = ca.Opti()
    X = opti.variable(14, N + 1)
    T = opti.variable(3, N + 1)
    Z = opti.variable(1, N + 1)
    D = opti.variable(3, N)          # |dT| slacks
    opti.subject_to(X[:, 0] == x0)
    for k in range(N):
        opti.subject_to(X[:, k + 1] == F(X[:, k], T[:, k], T[:, k + 1], Z[k], Z[k + 1]))
    Tn2 = ca.sum1(T**2)
    opti.subject_to(opti.bounded(cfg.T_min_plan**2, Tn2, cfg.T_max_plan**2))
    opti.subject_to(opti.bounded(-tg * T[2, :], T[0, :], tg * T[2, :]))
    opti.subject_to(opti.bounded(-tg * T[2, :], T[1, :], tg * T[2, :]))
    opti.subject_to(opti.bounded(-veh.rcs_torque, Z, veh.rcs_torque))
    dT = T[:, 1:] - T[:, :-1]
    opti.subject_to(ca.vec(D - dT) >= 0)
    opti.subject_to(ca.vec(D + dT) >= 0)
    opti.subject_to(D[0, :] + tg * D[2, :] <= gbud)
    opti.subject_to(D[1, :] + tg * D[2, :] <= gbud)
    opti.subject_to(D[0, :] + D[1, :] + D[2, :] <= tbud)
    qx, qy = X[7, :], X[8, :]
    opti.subject_to(1 - 2 * (qx[1:]**2 + qy[1:]**2) >= np.cos(cfg.tilt_max))
    rz = X[2, 1:] - target[2]
    opti.subject_to(rz >= 0)
    if cfg.glide_slope is not None:
        lat2 = (X[0, 1:] - target[0])**2 + (X[1, 1:] - target[1])**2
        opti.subject_to(np.tan(cfg.glide_slope) * ca.sqrt(lat2 + 1e-6) <= rz + 1e-3 * np.tan(cfg.glide_slope))
    opti.subject_to(X[0:3, N] == target)
    opti.subject_to(X[3:6, N] == 0)
    opti.subject_to(X[10:13, N] == 0)
    opti.subject_to(X[7, N] == 0)
    opti.subject_to(X[8, N] == 0)
    opti.minimize(-X[13, N] + 1e-6 * ca.sumsqr(Z))
    opts = {'ipopt.print_level': 5 if verbose else 0, 'print_time': 0, 'ipopt.max_iter': max_iter,
            'ipopt.tol': 1e-8, 'ipopt.acceptable_tol': 1e-6, 'ipopt.constr_viol_tol': 1e-7}
    opti.solver('ipopt', opts)
    runs = []
    for name, Xg, Tg in guesses:
        opti.set_initial(X, Xg.T)
        opti.set_initial(T, Tg.T)
        opti.set_initial(Z, 0)
        dTg = np.abs(np.diff(Tg, axis=0)).T
        opti.set_initial(D, dTg + 1e-3)
        t0 = time.perf_counter()
        try:
            sol = opti.solve()
            ok = True
            Xs, Ts = sol.value(X).T, sol.value(T).T
            stat = sol.stats()['return_status']
        except RuntimeError:
            ok = False
            stat = opti.stats()['return_status']
            Xs, Ts = opti.debug.value(X).T, opti.debug.value(T).T
        wall = time.perf_counter() - t0
        fuel = float(m0 - Xs[-1, 13])
        runs.append(dict(name=name, ok=ok and stat in ('Solve_Succeeded', 'Solved_To_Acceptable_Level'), status=stat,
                         fuel=fuel, X=Xs, T=Ts, wall=wall, iters=opti.stats().get('iter_count')))
    good = [r for r in runs if r['ok']]
    best = min(good, key=lambda r: r['fuel']) if good else None
    return dict(best=best, runs=runs, N=N, h=h)


def guess_from_planB(planB, N):
    """Node states/controls of a planner-B solution (same node grid when N matches)."""
    g = planB.grid
    idx = g.node if g.N == N else np.round(np.linspace(0, g.S, N + 1)).astype(int)
    X = np.zeros((N + 1, 14))
    X[:, 0:3] = planB.r[idx]
    X[:, 3:6] = planB.v[idx]
    X[:, 6:10] = np.array([R_to_quat(planB.att['R'][s]) for s in idx])
    X[:, 10:13] = planB.att['w'][idx]
    X[:, 13] = planB.m[idx]
    return X, planB.T_body[idx].copy()


def guess_from_3dof(p3, N, m0):
    t = np.linspace(0, p3.tf, N + 1)
    X = np.zeros((N + 1, 14))
    for i in range(3):
        X[:, i] = np.interp(t, p3.t, p3.r[:, i])
        X[:, 3 + i] = np.interp(t, p3.t, p3.v[:, i])
    tc = 0.5 * (p3.t[:-1] + p3.t[1:])
    Tw = np.column_stack([np.interp(t, tc, p3.T[:, i]) for i in range(3)])
    Tw[-1] = [0, 0, np.linalg.norm(Tw[-1])]
    Tg = np.zeros((N + 1, 3))
    for k in range(N + 1):
        b = Tw[k] / np.linalg.norm(Tw[k])
        ax = np.cross([0, 0, 1.0], b)
        s = np.linalg.norm(ax)
        if s < 1e-9:
            Rk = np.eye(3)
        else:
            ang = np.arcsin(min(s, 1.0))
            from .rotations import expm_so3
            Rk = expm_so3(ax / s * ang)
        X[k, 6:10] = R_to_quat(Rk)
        Tg[k] = [0, 0, np.linalg.norm(Tw[k])]
    X[:, 13] = np.interp(t, p3.t, p3.m)
    return X, Tg


def perturb(Xg, Tg, rng, att_sigma=0.05, T_sigma=30.0):
    X = Xg.copy()
    T = Tg.copy()
    for k in range(1, len(X) - 1):
        dq = np.concatenate([[1.0], 0.5 * rng.normal(scale=att_sigma, size=3) * np.array([1, 1, 0])])
        from .rotations import quat_mul
        q = quat_mul(X[k, 6:10], dq)
        X[k, 6:10] = q / np.linalg.norm(q)
    T[:, 2] += rng.normal(scale=T_sigma, size=len(T))
    T[:, :2] += rng.normal(scale=T_sigma / 4, size=(len(T), 2))
    return X, T
