"""Exact-admissible discretisation of model M1 (5-DOF, rate-limited thrust axis b,
gimbal cone delta, throttle box, constant mass). Written from the paper alone,
without looking at models.py.

Per cell k (width h_k):
  rho_k in [-omega, omega]  signed turn rate of the body axis along a geodesic
  chi_k                     heading of that geodesic in the transported frame
  mu_k  in [0, delta]       gimbal deflection (constant in the body frame)
  nu_k                      gimbal azimuth in the transported frame
  a_k   in [amin, amax]     thrust acceleration

b is piecewise geodesic with speed <= omega, d stays exactly mu_k <= delta from
b, so EVERY parameter vector is an admissible continuous-time M1 control.
All constraints are boxes.
"""
import numpy as np

GLX, GLW = np.polynomial.legendre.leggauss(8)
GLX = 0.5 * (GLX + 1.0)
GLW = 0.5 * GLW


class M1:
    def __init__(self, edges, omega, delta, amin, amax, g0=9.81):
        self.edges = np.asarray(edges, float)
        self.h = np.diff(self.edges)
        self.N = len(self.h)
        self.tf = self.edges[-1]
        self.omega, self.delta, self.amin, self.amax, self.g0 = omega, delta, amin, amax, g0

    # ---- parameter packing -------------------------------------------------
    def unpack(self, X):
        N = self.N
        X = np.atleast_2d(X)
        return X[:, :N], X[:, N:2*N], X[:, 2*N:3*N], X[:, 3*N:4*N], X[:, 4*N:5*N]

    def bounds(self):
        N = self.N
        lo = np.r_[-self.omega*np.ones(N), -np.inf*np.ones(N), np.zeros(N),
                   -np.inf*np.ones(N), self.amin*np.ones(N)]
        hi = np.r_[self.omega*np.ones(N), np.inf*np.ones(N), self.delta*np.ones(N),
                   np.inf*np.ones(N), self.amax*np.ones(N)]
        return list(zip(lo, hi))

    # ---- moments: I = int a d, J = int (tf-s) a d, batched over rows of X ---
    def moments(self, X):
        rho, chi, mu, nu, a = self.unpack(X)
        B = rho.shape[0]
        b = np.tile([0.0, 0.0, 1.0], (B, 1))
        e1 = np.tile([1.0, 0.0, 0.0], (B, 1))
        e2 = np.tile([0.0, 1.0, 0.0], (B, 1))
        I = np.zeros((B, 3))
        J = np.zeros((B, 3))
        for k in range(self.N):
            h, s0 = self.h[k], self.edges[k]
            c, s = np.cos(chi[:, k])[:, None], np.sin(chi[:, k])[:, None]
            w = c*e1 + s*e2                # geodesic direction (unit tangent)
            n = c*e2 - s*e1                # b x w, fixed along the geodesic
            tau = h*GLX                    # (Q,)
            ang = rho[:, k][:, None]*tau[None, :]            # (B,Q)
            ca, sa = np.cos(ang)[:, :, None], np.sin(ang)[:, :, None]
            bq = ca*b[:, None, :] + sa*w[:, None, :]         # (B,Q,3)
            wq = -sa*b[:, None, :] + ca*w[:, None, :]
            cm, sm = np.cos(mu[:, k])[:, None, None], np.sin(mu[:, k])[:, None, None]
            dn = (nu[:, k] - chi[:, k])
            cn, sn = np.cos(dn)[:, None, None], np.sin(dn)[:, None, None]
            dq = cm*bq + sm*(cn*wq + sn*n[:, None, :])       # unit thrust dir
            wt = (h*GLW)[None, :, None]
            ak = a[:, k][:, None]
            I += ak*np.sum(wt*dq, axis=1)
            J += ak*np.sum(wt*(self.tf - (s0 + tau))[None, :, None]*dq, axis=1)
            ce, se = np.cos(rho[:, k]*h)[:, None], np.sin(rho[:, k]*h)[:, None]
            b, w = ce*b + se*w, -se*b + ce*w
            e1, e2 = c*w - s*n, s*w + c*n
        return I, J

    # ---- data theta=(r0,v0) from which this control lands at rest at origin -
    def theta(self, X):
        I, J = self.moments(X)
        ez = np.array([0.0, 0.0, 1.0])
        v0 = self.g0*self.tf*ez - I
        r0 = -v0*self.tf + 0.5*self.g0*self.tf**2*ez - J
        return np.hstack([r0, v0])

    # ---- planar helper: build X from signed rate, signed gimbal, throttle ---
    def planar(self, rate, gimbal, a):
        N = self.N
        rate, gimbal, a = (np.broadcast_to(np.asarray(v, float), (N,)) for v in (rate, gimbal, a))
        return np.r_[rate, np.zeros(N), np.abs(gimbal), np.where(gimbal >= 0, 0.0, np.pi), a]
