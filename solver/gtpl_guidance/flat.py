"""Flat-output (centre-of-percussion) machinery for the pure-TVC lander.

Model (planning model of planner F): rigid axisymmetric body, thrust applied at the gimbal pivot L below the CG, roll
rate held at zero, mass m(t) with mdot = -alpha ||T||, and the centre of percussion fixed in the body:

    eps = J_t(m) / (m L(m)) = const.                                                       (CoP assumption)

Then y = r + eps b (b = body axis) satisfies, exactly,

    y'' = f b - g e3,          f = T_a / m - eps |b'|^2,                                    (FLAT)

where T_a is the axial thrust. The gimbal's lateral thrust (the steering torque) drops out of y''. So the whole
state and both controls are algebraic functions of y and its derivatives up to order four:

    u := y'' + g e3,  f = |u|,  b = u / f,
    b'  = P u' / f,                                    P = I - b b^T
    P b'' = P (u'' - 2 (f'/f) u') / f,                 f' = b . u'
    axial specific thrust     a   = f + eps |b'|^2                      (T_a = m a)
    lateral specific thrust   l   = -eps P b''   (world frame, perpendicular to b; |l| = eps |P b''|)
    thrust / mass             tau = sqrt(a^2 + |l|^2),   ln m(t) = ln m0 - alpha int_0^t tau
    gimbal tangent            |l| / a
    CG                        r = y - eps b,  v = y' - eps b'.

This file provides: the quintic B-spline parametrisation of y with exact Bezier control polygons of every derivative
(used for constraints that hold at EVERY instant, not only at nodes), and the flat map itself.
"""
import numpy as np
from scipy.interpolate import BSpline

from .params import G0

E3 = np.array([0.0, 0.0, 1.0])
GE3 = G0 * E3
DEG = 5          # quintic: y in C^4, so the gimbal angle and the throttle are continuous and slew-limited


def _bernstein(q, x):
    """Bernstein basis of degree q at points x in [0,1]: (len(x), q+1)."""
    from math import comb
    x = np.asarray(x, float)[:, None]
    j = np.arange(q + 1)[None, :]
    c = np.array([comb(q, k) for k in range(q + 1)], float)[None, :]
    return c * x**j * (1 - x)**(q - j)


def _elevate(q, to):
    """Degree-elevation matrix for Bezier control points: degree q -> degree `to` ((to+1) x (q+1))."""
    M = np.eye(q + 1)
    for d in range(q, to):
        E = np.zeros((d + 2, d + 1))
        for i in range(d + 2):
            if i > 0:
                E[i, i - 1] = i / (d + 1)
            if i < d + 1:
                E[i, i] = 1 - i / (d + 1)
        M = E @ M
    return M


class SplineBasis:
    """Clamped uniform quintic B-spline on the unit interval with S spans (n = S + 5 coefficients).

    bez[d]  : (S, 6-d, n)  Bezier control points of the d-th derivative (w.r.t. normalised time x = t/tf) on each span
    ctrl[d] : (S*4, n) for d = 2..5, the same control polygons degree-elevated to cubic, stacked span by span.
              For every x in span s: D^d y(x) = sum_j B_j^3(xloc) ctrl[d][4 s + j] @ c   (same weights for all d),
              so any constraint that is jointly convex in (y'', y''', y'''', y''''') and imposed on the 4 control
              tuples of a span holds at every instant of that span.
    """
    _cache = {}

    def __new__(cls, S):
        if S not in cls._cache:
            cls._cache[S] = super().__new__(cls)
            cls._cache[S]._init(S)
        return cls._cache[S]

    def _init(self, S):
        self.S = S
        self.n = n = S + DEG
        self.knots = np.concatenate([np.zeros(DEG), np.linspace(0, 1, S + 1), np.ones(DEG)])
        I = np.eye(n)
        self._spl = [BSpline(self.knots, I, DEG)]
        for d in range(1, DEG + 1):
            self._spl.append(self._spl[0].derivative(d))
        h = 1.0 / S
        self.bez = []
        for d in range(DEG + 1):
            q = DEG - d
            xl = (np.arange(q + 1) + 0.5) / (q + 1)
            Vb = _bernstein(q, xl)
            B = np.empty((S, q + 1, n))
            for s in range(S):
                E = self._spl[d](s * h + xl * h)
                B[s] = np.linalg.solve(Vb, E)
            self.bez.append(B)
        self.ctrl = {}
        for d in range(2, DEG + 1):
            El = _elevate(DEG - d, 3)
            self.ctrl[d] = np.einsum('ij,sjn->sin', El, self.bez[d]).reshape(S * 4, n)

    def design(self, x, d=0):
        """(len(x), n) matrix of the d-th derivative (normalised time) at points x in [0,1]."""
        x = np.clip(np.asarray(x, float), 0.0, 1.0)
        return self._spl[d](x)


def flat_map(u, u1, u2, u3, eps):
    """Vectorised flat map. u, u1, u2, u3: (K,3) = y''+g e3 and its first three time derivatives.

    Returns dict with f, b, bd, bdd (full second derivative), Pbdd, bddd, a (axial specific thrust), lvec (lateral
    specific thrust, world), tau (thrust/mass), a_dot, lvec_dot_perp (for slew rates).
    """
    f = np.linalg.norm(u, axis=1)
    b = u / f[:, None]
    fd = np.sum(b * u1, axis=1)
    bd = (u1 - fd[:, None] * b) / f[:, None]
    w2 = np.sum(bd * bd, axis=1)
    fdd = np.sum(b * u2, axis=1) + f * w2
    bdd = (u2 - fdd[:, None] * b - 2 * fd[:, None] * bd) / f[:, None]
    Pbdd = bdd + w2[:, None] * b
    bd_bdd = np.sum(bd * bdd, axis=1)
    fddd = np.sum(b * u3, axis=1) + 3 * fd * w2 + 3 * f * bd_bdd
    bddd = (u3 - fddd[:, None] * b - 3 * fdd[:, None] * bd - 3 * fd[:, None] * bdd) / f[:, None]
    a = f + eps * w2
    a_dot = fd + 2 * eps * bd_bdd
    lvec = -eps * Pbdd
    # d/dt of lvec projected on the plane perpendicular to b (= rate of change of its body-frame components, since
    # the roll rate is zero): P d/dt(P b'') = P b''' + |b'|^2 b' ... derived in solver/FLAT.md
    Pbddd = bddd - np.sum(b * bddd, axis=1)[:, None] * b
    lvec_dot_perp = -eps * (Pbddd + w2[:, None] * bd)
    tau = np.sqrt(a * a + np.sum(lvec * lvec, axis=1))
    return dict(f=f, b=b, bd=bd, bdd=bdd, Pbdd=Pbdd, bddd=bddd, a=a, a_dot=a_dot, lvec=lvec,
                lvec_dot_perp=lvec_dot_perp, tau=tau, fd=fd, fdd=fdd, w2=w2)


class FlatTrajectory:
    """A flat-output trajectory y(t) = spline(c) on [0, tf] and everything that follows from it."""

    def __init__(self, c, tf, eps, m0, alpha):
        self.c = np.asarray(c, float)
        self.tf, self.eps, self.m0, self.alpha = float(tf), float(eps), float(m0), float(alpha)
        self.S = self.c.shape[0] - DEG
        self.basis = SplineBasis(self.S)
        self._zq = None

    def derivs(self, t, upto=5):
        x = np.clip(np.atleast_1d(np.asarray(t, float)) / self.tf, 0.0, 1.0)
        return [self.basis.design(x, d) @ self.c / self.tf**d for d in range(upto + 1)]

    def _logmass_table(self, per_span=16):
        """ln m on a fine grid by composite Gauss-Legendre quadrature of tau (4 points per sub-cell)."""
        if self._zq is None:
            K = self.S * per_span
            edges = np.linspace(0.0, self.tf, K + 1)
            gx, gw = np.polynomial.legendre.leggauss(4)
            hc = edges[1] - edges[0]
            tq = (edges[:-1, None] + 0.5 * hc * (gx[None, :] + 1)).ravel()
            tau = self.eval(tq, mass=False)['tau'].reshape(K, 4)
            inc = 0.5 * hc * (tau @ gw)
            self._zq = (edges, np.concatenate([[0.0], np.cumsum(inc)]), per_span)
        return self._zq

    def eval(self, t, mass=True):
        """Full state / control reference at times t (array). World frame; thrust in N if mass=True."""
        t = np.atleast_1d(np.asarray(t, float))
        y, yd, ydd, y3, y4, y5 = self.derivs(t)
        u = ydd + GE3[None, :]
        fm = flat_map(u, y3, y4, y5, self.eps)
        out = dict(t=t, y=y, yd=yd, u=u, **fm)
        out['r'] = y - self.eps * fm['b']
        out['v'] = yd - self.eps * fm['bd']
        out['acc'] = ydd - self.eps * fm['bdd']
        if mass:
            edges, cum, _ = self._logmass_table()
            # refine: integrate from the nearest table edge with 4-point Gauss
            k = np.clip(np.searchsorted(edges, t, side='right') - 1, 0, len(edges) - 2)
            gx, gw = np.polynomial.legendre.leggauss(4)
            dt = t - edges[k]
            tq = edges[k][:, None] + 0.5 * dt[:, None] * (gx[None, :] + 1)
            tauq = self.eval(tq.ravel(), mass=False)['tau'].reshape(len(t), 4)
            I = cum[k] + 0.5 * dt * (tauq @ gw)
            out['m'] = self.m0 * np.exp(-self.alpha * I)
            out['T'] = out['m'] * fm['tau']                 # thrust magnitude [N]
            out['Ta'] = out['m'] * fm['a']                  # axial thrust [N]
            out['Tlat_w'] = out['m'][:, None] * fm['lvec']  # lateral thrust, world frame [N]
            out['T_dot'] = out['m'] * (-self.alpha * fm['tau']**2 + (fm['a'] * fm['a_dot'] + np.sum(
                fm['lvec'] * fm['lvec_dot_perp'], axis=1)) / fm['tau'])
        out['gim_tan'] = np.linalg.norm(fm['lvec'], axis=1) / fm['a']
        # body-frame gimbal-tangent rate magnitude: |d/dt (l_body / a)| <= ...; exact value:
        g_w = fm['lvec'] / fm['a'][:, None]
        out['gim_rate'] = np.linalg.norm(fm['lvec_dot_perp'] / fm['a'][:, None] - g_w * (fm['a_dot'] / fm['a'])[:, None],
                                         axis=1)
        return out
