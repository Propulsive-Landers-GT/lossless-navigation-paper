"""Shor SDP relaxation of the roll-free (5-DOF) lander, checked against IPOPT.

The vehicle of sixdof_lcvx.py is axisymmetric (J_y = J_z) and its engine makes no roll torque, so
the roll rate stays 0 and roll never enters the translation. The attitude then reduces to the
thrust axis b = R e_1 and the inertial rate W = R w (with W . b = 0), and T is the inertial thrust:

  b' = W x b,   J_y W' = r_T,x (b x T),   m v' = T + m g,   gimbal b . T >= cos(delta) ||T||

Discretized so that every constraint is at most quadratic. This is the discrete problem of
sdp_relaxation.py written in these variables, so the two have the same optimum:

  attitude      (I - h/2 [W_k]x) b_{k+1} = (I + h/2 [W_k]x) b_k                  (Cayley step)
  rotation rate (I - h/2 [W_k]x) (W_{k+1} - W_k) = c (I + h/2 [W_k]x) tau_k,   c = h r_T,x / J_y
  thrust split  s_k = b_k . T_k,  tau_k = b_k x T_k
  translation   m_k a_k = T_k + m_k g,  v_{k+1} = v_k + h a_k,  r_{k+1} = r_k + h v_k + h^2/2 a_k
  mass          m_{k+1} = m_k - h alpha Gamma_k,  ||T_k|| <= Gamma_k

Usage: python sdp_relaxation_5dof.py [N] [t_f]
"""
import sys
import time

import numpy as np

from sdp_relaxation import (Lander, cross, dot, evaluate, minus, poly, solve_nlp, solve_sdp,
                            thrust_gap)
from sixdof_lcvx import Params


class Lander5(Lander):
    def __init__(self, p: Params, N: int, tf: float):
        self.n, self.N, self.node, self.node_of, self.plain = 0, N, [], {}, set()
        self.eq, self.ge, self.soc = [], [], []
        self.eq_r, self.ge_r = [], []
        h = tf / N
        c = h * p.rT[0] / p.J[1]
        cd, td = np.cos(p.delta_max), np.tan(p.delta_max)
        self.r = r = [self.new(3) for _ in range(N + 1)]
        self.v = v = [self.new(3) for _ in range(N + 1)]
        self.X = X = []
        for k in range(N + 1):
            x = dict(m=self.new(1, k)[0], b=self.new(3, k), W=self.new(3, k))
            if k < N:
                x.update(a=self.new(3, k), T=self.new(3, k), G=self.new(1, k)[0],
                         s=self.new(1, k)[0], tau=self.new(3, k))
            X.append(x)

        e1, z3 = np.eye(3)[0], np.zeros(3)
        self.eq += ([X[0]["m"] - p.m_wet] + minus(X[0]["b"], e1) + minus(X[0]["W"], z3)
                    + minus(r[0], p.r0) + minus(v[0], p.v0))
        # b_N,x = 1 and W_N,x = 0 follow from the dynamics; as rows they would break IPOPT's LICQ.
        self.eq += minus(r[N], z3) + minus(v[N], p.vf) + X[N]["b"][1:] + X[N]["W"][1:]
        self.eq_r += [X[N]["b"][0] - 1, X[N]["W"][0]]
        for k in range(N):
            x, y = X[k], X[k + 1]
            m, a, b, W, T, G, s, tau = (x[q] for q in ("m", "a", "b", "W", "T", "G", "s", "tau"))
            self.eq += [m * a[i] - T[i] - p.g[i] * m for i in range(3)]
            self.eq += [s - dot(b, T)] + minus(tau, cross(b, T))
            Wb = cross(W, [y["b"][i] + b[i] for i in range(3)])
            self.eq += [y["b"][i] - b[i] - h / 2 * Wb[i] for i in range(3)]
            WW, Wt = cross(W, y["W"]), cross(W, tau)
            self.eq += [y["W"][i] - W[i] - h / 2 * WW[i] - c * tau[i] - c * h / 2 * Wt[i]
                        for i in range(3)]
            self.eq += [y["m"] - m + h * p.alpha * G]
            self.eq += [v[k + 1][i] - v[k][i] - h * a[i] for i in range(3)]
            self.eq += [r[k + 1][i] - r[k][i] - h * v[k][i] - h * h / 2 * a[i] for i in range(3)]
            self.soc += [(G, T), (s * (1 / cd), T), (s * td, tau),
                         (r[k][0] * (1 / np.tan(p.gamma_gs)), r[k][1:])]
            self.ge += [G - p.T_min, p.T_max - G]
            a_max = p.T_max / p.m_dry
            self.ge_r += [G * G - dot(T, T), s * s - cd ** 2 * dot(T, T),
                          td ** 2 * s * s - dot(tau, tau), G - s,
                          (G - p.T_min) * (p.T_max - G),
                          a_max ** 2 - dot(minus(a, p.g), minus(a, p.g))]
            # Valid because |b| = 1 and the Cayley step rotates about W_k.
            dW = minus(y["W"], W)
            self.eq_r += [s * s + dot(tau, tau) - dot(T, T), dot(b, tau), dot(T, tau),
                          dot(y["b"], W), dot(dW, dW) - c * c * dot(tau, tau)]
            self.eq_r += [T[i] - s * b[i] + bt for i, bt in enumerate(cross(b, tau))]
        for x in X:
            self.soc += [(poly(p.omega_max), x["W"])]
            self.ge += [x["m"] - p.m_dry, x["b"][0] - np.cos(p.theta_max)]
            self.ge_r += [(x["m"] - p.m_dry) * (p.m_wet - x["m"]),
                          p.omega_max ** 2 - dot(x["W"], x["W"]),
                          (x["b"][0] - np.cos(p.theta_max)) * (1 - x["b"][0])]
            self.eq_r += [dot(x["b"], x["b"]) - 1, dot(x["b"], x["W"])]
        self.objective = X[N]["m"]  # maximize final mass

    def straight_line(self, p: Params):
        x = np.zeros(self.n)
        ix = lambda P: next(iter(P))[0]
        for k, X in enumerate(self.X):
            lam = k / self.N
            m = p.m_wet - lam * 0.5
            vals = dict(m=[m], b=[1, 0, 0], W=np.zeros(3), a=np.zeros(3), T=[m, 0, 0],
                        G=[max(m, p.T_min)], s=[m], tau=np.zeros(3))
            for s, P in X.items():
                x[[ix(q) for q in (P if isinstance(P, list) else [P])]] = vals[s]
            x[[ix(q) for q in self.r[k]]] = (1 - lam) * p.r0
            x[[ix(q) for q in self.v[k]]] = (1 - lam) * p.v0 + lam * p.vf
        return x


if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    tf = float(sys.argv[2]) if len(sys.argv) > 2 else 7.5
    solver = sys.argv[3] if len(sys.argv) > 3 else "CLARABEL"
    p = Params()
    L = Lander5(p, N, tf)
    print(f"N = {N}, t_f = {tf}: {L.n} unknowns, {len(L.eq)} equalities")

    t0 = time.time()
    status, bound, xhat, eig, nrlt = solve_sdp(L, solver=solver)
    print(f"\nSDP {solver} ({status}, {time.time() - t0:.1f} s, {nrlt} RLT rows): m_N <= {bound:.6f}")
    print("  lambda_2 / lambda_1 per PSD block:",
          " ".join(f"{e[1] / e[0]:.1e}" for e in eig))
    eqv, gev = L.violation(xhat)
    print(f"  first row as a trajectory: m_N = {evaluate(L.objective, xhat):.6f}, "
          f"max equality error {eqv:.1e}, max inequality violation {gev:.1e}, "
          f"max Gamma - ||T|| {thrust_gap(L, xhat):.1e}")

    for name, guess in [("from SDP first row", xhat), ("from straight line", L.straight_line(p))]:
        t0 = time.time()
        xs, mN, st = solve_nlp(L, guess)
        eqv, gev = L.violation(xs)
        print(f"\nIPOPT {name} ({st}, {time.time() - t0:.1f} s): m_N = {mN:.6f}, "
              f"max equality error {eqv:.1e}, max inequality violation {gev:.1e}, "
              f"max Gamma - ||T|| {thrust_gap(L, xs):.1e}")
        print(f"  gap to SDP bound: {bound - mN:.2e}")
