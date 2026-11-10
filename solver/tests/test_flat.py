"""Tests for planner F (flat convex guidance). Run: cd solver && OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q"""
import os
import sys
import warnings

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config, G0
from gtpl_guidance.flat import SplineBasis, FlatTrajectory, flat_map, _bernstein, DEG
from gtpl_guidance.fcg import FCG
from gtpl_guidance.flatcert import certify_F, check_limits, replay, plan_frame
from gtpl_guidance.dynamics import deriv
from gtpl_guidance.rotations import expm_so3, R_to_quat, quat_to_R

VEH, CFG = default_vehicle(), default_config()
TGT = np.array([0, 0, 1.5])
EPS = VEH.J_t / (VEH.m_wet * VEH.L)


def _rand_point(rng):
    """A random flat-output jet (u, u', u'', u''') with a tilted thrust direction."""
    b = np.array([rng.normal(0, 0.15), rng.normal(0, 0.15), 1.0])
    u = rng.uniform(5, 13) * b / np.linalg.norm(b)
    return u, rng.normal(0, 4, 3), rng.normal(0, 8, 3), rng.normal(0, 20, 3)


# ---------------------------------------------------------------- spline machinery
def test_bezier_control_polygons_reproduce_every_derivative():
    S = 7
    bs = SplineBasis(S)
    rng = np.random.default_rng(0)
    c = rng.normal(size=(bs.n, 3))
    for s in range(S):
        xl = rng.uniform(0, 1, 5)
        x = (s + xl) / S
        B3 = _bernstein(3, xl)
        for d in range(DEG + 1):
            direct = bs.design(x, d) @ c
            assert np.allclose(_bernstein(DEG - d, xl) @ (bs.bez[d][s] @ c), direct, atol=1e-6 * S**d)
            if d >= 2:      # degree-elevated cubic control tuples share the same Bernstein weights
                assert np.allclose(B3 @ (bs.ctrl[d][4 * s:4 * s + 4] @ c), direct, atol=1e-6 * S**d)


# ---------------------------------------------------------------- the flat map is the true dynamics
def test_flat_map_matches_finite_differences_of_the_body_axis():
    rng = np.random.default_rng(1)
    bs = SplineBasis(6)
    c = rng.normal(size=(bs.n, 3)) * 0.5
    c[:, 2] += np.linspace(0, 3, bs.n)**2            # keeps u_z = y_z'' + g well away from zero
    tr = FlatTrajectory(c, 4.0, EPS, 80.0, VEH.alpha)
    t, h = np.array([1.3]), 1e-4
    e = tr.eval(t, mass=False)
    bm, b0, bp = (tr.eval(t + k * h, mass=False)['b'][0] for k in (-1, 0, 1))
    assert np.allclose((bp - bm) / (2 * h), e['bd'][0], atol=1e-6)
    assert np.allclose((bp - 2 * b0 + bm) / h**2, e['bdd'][0], atol=1e-4)
    bdm, bdp = (tr.eval(t + k * h, mass=False)['bdd'][0] for k in (-1, 1))
    assert np.allclose((bdp - bdm) / (2 * h), e['bddd'][0], atol=1e-4)


def test_centre_of_percussion_identity_with_flat_controls():
    """Rigid-body derivative with the flat map's thrust equals the planned acceleration, rate and mass flow."""
    rng = np.random.default_rng(2)
    for _ in range(50):
        u, u1, u2, u3 = _rand_point(rng)
        m, L = rng.uniform(60, 80), rng.uniform(0.5, 0.6)
        fm = flat_map(u[None], u1[None], u2[None], u3[None], EPS)
        b, bd, bdd = fm['b'][0], fm['bd'][0], fm['bdd'][0]
        # any body frame whose z axis is b
        x_ax = np.cross(b, [0.3, 0.9, 0.1]); x_ax /= np.linalg.norm(x_ax)
        R = np.column_stack([x_ax, np.cross(b, x_ax), b])
        w_body = R.T @ np.cross(b, bd)
        Tw = m * (fm['a'][0] * b + fm['lvec'][0])
        x = np.concatenate([rng.normal(size=3), rng.normal(size=3), R_to_quat(R), w_body, [m]])
        dx = deriv(x, R.T @ Tw, 0.0, EPS * m * L, VEH.J_z, L, VEH.alpha)
        acc_cg = u - G0 * np.array([0, 0, 1.0]) - EPS * bdd                # r'' = y'' - eps b''
        assert np.allclose(dx[3:6], acc_cg, atol=1e-9)
        wdot_w = R @ dx[10:13]
        assert np.allclose(np.cross(wdot_w, b) + np.cross(np.cross(b, bd), bd), bdd, atol=1e-9)
        assert np.isclose(dx[13], -VEH.alpha * m * fm['tau'][0])


# ---------------------------------------------------------------- the inequalities behind the restriction (math/10, Lemma 4)
def test_pointwise_bounds_used_by_the_restriction():
    rng = np.random.default_rng(3)
    for _ in range(4000):
        u, u1, u2, u3 = _rand_point(rng)
        rho, kap, k = rng.normal(0, 1.5), rng.normal(0, 3), rng.normal(0, 10)
        fm = flat_map(u[None], u1[None], u2[None], u3[None], EPS)
        f, b, p = fm['f'][0], fm['b'][0], u[2]
        s = np.hypot(b[0], b[1]) * rng.uniform(1.0, 1.5)                   # any bound on sin(tilt)
        Lb = p * rng.uniform(0.5, 1.0)
        e1 = np.linalg.norm(u1 - rho * u)
        q = e1**2 / p
        G = np.linalg.norm(u2 - 2 * rho * u1 - kap * u - k * np.array([0, 0, 1.0])) + s * abs(k) + q
        assert f * np.sqrt(fm['w2'][0]) <= e1 + 1e-9                       # B1: f |b'| <= e1
        assert f * fm['w2'][0] <= q + 1e-9                                 # B2: f |b'|^2 <= q
        assert f * np.linalg.norm(fm['Pbdd'][0]) <= G + 1e-9               # B3: f |P b''| <= G
        sig = np.hypot(f + EPS * q / Lb, EPS * G / Lb)
        assert p <= fm['tau'][0] + 1e-12 and fm['tau'][0] <= sig + 1e-9    # B4: p <= T/m <= sigma
        phi = rng.uniform(4, 14)
        assert 2 * phi * p - phi**2 <= f**2 + 1e-9                         # B5: tangent of p^2


# ---------------------------------------------------------------- the planner
def _problems():
    R1 = expm_so3(np.radians(3) * np.array([0.6, 0.8, 0]))
    return [([10, 20, 50], [0, 0, 0], np.eye(3), np.zeros(3), 8.89),
            ([0, 0, 50], [4, 0, -5], R1, np.array([0.03, -0.02, 0]), 8.02),
            ([-8, 5, 45], [2, -1, -4], np.eye(3), np.zeros(3), 7.72)]


def test_single_solve_is_flyable_at_every_instant():
    """One SOCP, no refinement: the plan meets the PLANNING limits on a dense grid (they were imposed on Bezier
    control tuples, so they must hold between nodes too) and matches the initial attitude, rate and gimbal."""
    F = FCG(VEH, CFG, S=16)
    for r0, v0, R0, w0, tf in _problems():
        p = F.plan(r0, v0, 80.0, R0, w0, TGT, tf, refine=0)
        assert p.traj is not None and p.n_solves == 1
        c = check_limits(p, VEH, CFG, np.array(r0, float), np.array(v0, float), 80.0, R0, w0, TGT, frame=False)
        for k in ('throttle_plan', 'gimbal_plan', 'tilt', 'state', 'boundary', 'terminal', 'gimbal_rate', 'thrust_rate'):
            assert c['checks'][k], (k, c)
        assert p.fuel <= p.fuel_bound + 1e-9                                # the SOCP objective bounds the true fuel


def test_open_loop_replay_lands_within_a_micrometre():
    """Throttle and gimbal commands only, through the full quaternion rigid body with depleting mass."""
    F = FCG(VEH, CFG, S=16)
    r0, v0, R0, w0, tf = _problems()[1]
    p = F.plan(r0, v0, 80.0, R0, w0, TGT, tf, refine=0)
    xf = replay(p.traj, VEH, np.array(r0, float), np.array(v0, float), 80.0, R0, w0, model='cop')
    assert np.linalg.norm(xf[0:3] - TGT) < 1e-6 and np.linalg.norm(xf[3:6]) < 1e-6
    assert np.degrees(np.arccos(min(1.0, quat_to_R(xf[6:10])[2, 2]))) < 1e-3


def test_references_change_tightness_not_feasibility():
    """Arbitrary (even bad) references still give a flyable plan; they only cost fuel or make the SOCP infeasible."""
    F = FCG(VEH, CFG, S=12)
    r0, v0, R0, w0, tf = _problems()[0]
    rng = np.random.default_rng(5)
    ref = F.default_ref(80.0)
    ref.rho[:] = rng.normal(0, 0.05, F.S)
    ref.kap[:] = rng.normal(0, 0.05, F.S)
    ref.phi[:] = rng.uniform(6.5, 9.0, F.S)
    c, info = F.solve(r0, v0, 80.0, R0, w0, TGT, tf + 0.4, ref=ref)
    assert c is not None
    from gtpl_guidance.fcg import PlanF
    p = PlanF(tf + 0.4, FlatTrajectory(c, tf + 0.4, F.eps, 80.0, VEH.alpha), 'flyable', 0, 0, 0, 1, 0)
    ck = check_limits(p, VEH, CFG, np.array(r0, float), np.array(v0, float), 80.0, R0, w0, TGT, frame=False)
    assert all(ck['checks'][k] for k in ('throttle_plan', 'gimbal_plan', 'tilt', 'boundary', 'terminal'))


def test_refinement_does_not_increase_fuel():
    F = FCG(VEH, CFG, S=16)
    r0, v0, R0, w0, tf = _problems()[0]
    p0 = F.plan(r0, v0, 80.0, R0, w0, TGT, tf, refine=0)
    p2 = F.plan(r0, v0, 80.0, R0, w0, TGT, tf, refine=2)
    assert p2.fuel <= p0.fuel + 1e-9


def test_infeasible_request_is_refused_not_faked():
    """Too short a flight: the program is infeasible and says so (no best-effort plan that cannot be flown)."""
    F = FCG(VEH, CFG, S=16)
    p = F.plan([10, 20, 50], [0, 0, 0], 80.0, np.eye(3), np.zeros(3), TGT, 6.0, refine=0)
    assert p.traj is None and p.status == 'infeasible'


def test_landing_guidance_entry_point():
    """The one-call interface: picks its own time of flight, plans with one SOCP, returns a closed-form reference."""
    from gtpl_guidance.landing import LandingGuidance
    r0, v0, R0, w0, _ = _problems()[1]
    x0 = np.concatenate([r0, v0, R_to_quat(R0), w0, [79.0]])
    guide = LandingGuidance(TGT)
    assert guide.update(0.0, x0)
    assert guide.plan.n_solves == 1 and guide.n_tf_solves <= 16
    a, z = guide.reference(0.0), guide.reference(guide.tf_abs)
    assert np.allclose(a['position'], r0, atol=1e-8) and np.allclose(a['body_axis'], R0[:, 2], atol=1e-8)
    assert np.allclose(z['position'], TGT, atol=1e-8) and np.allclose(z['velocity'], 0, atol=1e-8)
    assert np.allclose(z['body_axis'], [0, 0, 1], atol=1e-9) and abs(z['gimbal_angle']) < 1e-9
    assert abs(z['throttle'] - z['mass'] * G0) < 1e-6          # arrives in hover: thrust equals weight


@pytest.mark.slow
def test_closed_loop_lands():
    """Wind, gusts, thrust noise, Isp error, gimbal bias; 10 Hz replans, each applied after its solver time."""
    from gtpl_guidance.landing import LandingGuidance
    from gtpl_guidance.sim6dof import simulate, SimOptions
    r0, v0, R0, w0, _ = _problems()[1]
    x0 = np.concatenate([r0, v0, R_to_quat(R0), w0, [79.0]])
    opts = SimOptions(wind=(2.0, 1.0, 0.0), gust_sigma=0.5, thrust_noise=0.02, isp_error=0.05,
                      gimbal_bias=(0.003, -0.002), seed=1, replan_dt=0.1, t_lock=0.6, latency=True)
    out = simulate(x0, TGT, LandingGuidance(TGT), VEH, opts)
    assert out['success'] and out['pos_err'] < 0.05 and out['speed'] < 0.5
