"""Time grid, attitude propagation and translational quadrature shared by planner B and the certificates.

Attitude model (pure TVC, roll rate held at zero by the RCS, axisymmetric body):
    body angular acceleration  alpha_body = (alpha_x, alpha_y, 0)   [exactly linear Euler equations, claims N6]
    gimbal lateral thrust      T_x = -k alpha_y,  T_y = +k alpha_x,  k = J_t / L          [torque balance, C-6 / Lemma 8.1]
    alpha_body is piecewise linear in time (first-order hold on the nodes), so the body rate is piecewise quadratic and
    the gimbal angle is continuous (the gimbal cannot jump).
"""
import numpy as np

from .rotations import expm_so3, hat

E3 = np.array([0.0, 0.0, 1.0])
HAT_E3 = hat(E3)


class Grid:
    """N intervals of length h, each split into `ns` quadrature substeps of length hs."""

    def __init__(self, tf, N, ns):
        self.tf, self.N, self.ns = float(tf), int(N), int(ns)
        self.h = self.tf / N
        self.hs = self.h / ns
        S = N * ns
        self.S = S
        self.ts = np.linspace(0.0, self.tf, S + 1)
        s = np.arange(S + 1)
        k = np.minimum(s // ns, N - 1)
        lam = (s - k * ns) / ns
        W = np.zeros((S + 1, N + 1))
        W[s, k] = 1 - lam
        W[s, k + 1] += lam
        self.W = W                                   # FOH interpolation, nodes -> substep points
        self.node = np.arange(N + 1) * ns            # substep index of each node
        # cumulative trapezoid of a FOH signal (exact): int_0^{t_s} x(t) dt = Cint[s] @ x_nodes
        self.Cint = np.vstack([np.zeros(N + 1), self.hs * np.cumsum(0.5 * (W[:-1] + W[1:]), axis=0)])
        self.t = np.linspace(0.0, self.tf, N + 1)


def propagate_attitude(grid, R0, w0, alpha_nodes):
    """Exact-in-the-limit attitude propagation of the body for a FOH body angular-acceleration profile.

    alpha_nodes: (N+1, 2) body-frame angular acceleration (x, y). w0: body rate (roll component ignored).
    Returns dict with R (S+1,3,3), w (S+1,3), alpha (S+1,3), theta (S,3) rotation increments, b (S+1,3).
    """
    a = np.zeros((grid.S + 1, 3))
    a[:, :2] = grid.W @ alpha_nodes
    w = np.zeros((grid.S + 1, 3))
    w[:, 0] = w0[0] + grid.Cint @ alpha_nodes[:, 0]
    w[:, 1] = w0[1] + grid.Cint @ alpha_nodes[:, 1]
    # body rate is quadratic on each substep; Simpson-like increment with the commutator-free midpoint rate
    wmid = np.zeros((grid.S, 3))
    wmid[:, :2] = w0[:2] + (grid.Cint[:-1] + 0.5 * grid.hs * (0.75 * grid.W[:-1] + 0.25 * grid.W[1:])) @ alpha_nodes
    theta = grid.hs * (w[:-1] + 4 * wmid + w[1:]) / 6.0
    R = np.empty((grid.S + 1, 3, 3))
    R[0] = R0
    E = np.empty((grid.S, 3, 3))
    for s in range(grid.S):
        E[s] = expm_so3(theta[s])
        R[s + 1] = R[s] @ E[s]
    return dict(R=R, w=w, alpha=a, theta=theta, E=E, b=R[:, :, 2].copy())


def attitude_sensitivity(grid, att):
    """Phi[s] (3 x 2(N+1)): first-order body-frame rotation perturbation dphi_s (R = Rbar Exp(dphi)) caused by a
    perturbation of the angular-acceleration nodes, ordered [dalpha_x nodes, dalpha_y nodes]."""
    N1 = grid.N + 1
    Dw = np.zeros((grid.S + 1, 3, 2 * N1))
    Dw[:, 0, :N1] = grid.Cint
    Dw[:, 1, N1:] = grid.Cint
    Phi = np.zeros((grid.S + 1, 3, 2 * N1))
    for s in range(grid.S):
        Phi[s + 1] = att['E'][s].T @ Phi[s] + 0.5 * grid.hs * (Dw[s] + Dw[s + 1])
    return Phi


def integrate_translation(grid, A, c, r0, v0):
    """Exact integration of r'' = a for a piecewise-linear-in-time acceleration sampled at the substep points.

    a_s = A[s] @ x + c[s]  with A (S+1, 3, nx), c (S+1, 3). Returns affine maps for all substep points:
    r_s = Ar[s] @ x + cr[s], v_s = Av[s] @ x + cv[s].
    """
    hs = grid.hs
    dv_A = 0.5 * hs * (A[:-1] + A[1:])
    dv_c = 0.5 * hs * (c[:-1] + c[1:])
    Av = np.concatenate([np.zeros_like(A[:1]), np.cumsum(dv_A, axis=0)])
    cv = np.concatenate([v0[None, :], v0[None, :] + np.cumsum(dv_c, axis=0)])
    dr_A = hs * Av[:-1] + hs**2 * (A[:-1] / 3 + A[1:] / 6)
    dr_c = hs * cv[:-1] + hs**2 * (c[:-1] / 3 + c[1:] / 6)
    Ar = np.concatenate([np.zeros_like(A[:1]), np.cumsum(dr_A, axis=0)])
    cr = np.concatenate([r0[None, :], r0[None, :] + np.cumsum(dr_c, axis=0)])
    return Ar, cr, Av, cv


def integrate_mass(grid, Tnorm_s, m0, alpha):
    """m(t) for mdot = -alpha ||T||, trapezoid on the substeps."""
    dm = alpha * 0.5 * grid.hs * (Tnorm_s[:-1] + Tnorm_s[1:])
    return np.concatenate([[m0], m0 - np.cumsum(dm)])
