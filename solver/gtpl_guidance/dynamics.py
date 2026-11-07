"""6DOF rigid-body dynamics of the pure-TVC lander (used by the open-loop certificate and the closed-loop simulator).

State x = [r(3), v(3), q(4) scalar-first body->world, w(3) body rate, m].
Inputs: body-frame thrust vector T_body (applied at the gimbal pivot, -L e3 from the CG), roll torque tau_z (RCS),
external force F_ext (world, e.g. drag) and torque disturbance.
"""
import numpy as np

from .params import G0
from .rotations import quat_to_R


def deriv(x, T_body, tau_z, J_t, J_z, L, alpha, F_ext=None, tau_ext=None):
    r, v, q, w, m = x[0:3], x[3:6], x[6:10], x[10:13], x[13]
    R = quat_to_R(q / np.linalg.norm(q))
    F = R @ T_body
    if F_ext is not None:
        F = F + F_ext
    a = F / m + np.array([0.0, 0.0, -G0])
    tau = np.array([L * T_body[1], -L * T_body[0], tau_z])     # (-L e3) x T_body + RCS
    if tau_ext is not None:
        tau = tau + tau_ext
    J = np.array([J_t, J_t, J_z])
    wdot = (tau - np.cross(w, J * w)) / J
    qw, qv = q[0], q[1:]
    qdot = 0.5 * np.concatenate([[-qv @ w], qw * w + np.cross(qv, w)])
    mdot = -alpha * np.linalg.norm(T_body)
    return np.concatenate([v, a, qdot, wdot, [mdot]])


def rk4(x, dt, f):
    k1 = f(x)
    k2 = f(x + 0.5 * dt * k1)
    k3 = f(x + 0.5 * dt * k2)
    k4 = f(x + dt * k3)
    xn = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    xn[6:10] /= np.linalg.norm(xn[6:10])
    return xn
