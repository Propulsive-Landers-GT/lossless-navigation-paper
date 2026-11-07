"""pytest suite for the solver package. Run: cd solver && OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q"""
import os
import sys
import warnings

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config, G0
from gtpl_guidance.lcvx3dof import (tf_search_A, solve_baseline_A, solve_candidate_C, solve_3dof_relaxation,
                                    size_rate_limits, purify, direction_rates)
from gtpl_guidance.attitude import Grid, propagate_attitude, attitude_sensitivity, integrate_translation
from gtpl_guidance.aacg import AACG
from gtpl_guidance.certify import certify_B, certify_3dof
from gtpl_guidance.dynamics import deriv
from gtpl_guidance.rotations import quat_to_R, R_to_quat, expm_so3, gimbal_angles, gimbal_dir

VEH, CFG = default_vehicle(), default_config()
TGT = np.array([0, 0, 1.5])


# ---------------------------------------------------------------- baseline A (faithful flight code)
def test_baseline_A_reproduces_flight_code_behaviour():
    p = tf_search_A([0, 0, 50], [0, 0, 0], 80.0, TGT, VEH)
    assert abs(p.tf - 7.0) < 0.21                      # stored flight-code solutions: tf = 7.01 s
    c = certify_3dof(p, VEH)
    assert c['T_delivered_min'] < VEH.T_min - 50       # relaxation not tight on the min-thrust arc (296 N in repo CSVs)
    assert not c['passed']


def test_purification_does_not_increase_lossy_nodes():
    p = solve_baseline_A([0, 0, 50], [0, 0, 0], 80.0, TGT, 7.4, VEH)
    q = purify(p, [0, 0, 50], [0, 0, 0], 80.0, TGT, VEH, pointing=np.radians(15), v_max=15.0)
    assert q.u is not None
    assert np.sum(q.tightness() < 0.999) <= np.sum(p.tightness() < 0.999)
    assert abs(q.fuel - p.fuel) < 1e-9


# ---------------------------------------------------------------- claims used by C
def test_chord_bound():
    rng = np.random.default_rng(0)
    rho = 1.3
    for _ in range(2000):
        a, b = rng.normal(size=3), rng.normal(size=3)
        a *= rho * (1 + rng.exponential()) / np.linalg.norm(a)
        b *= rho * (1 + rng.exponential()) / np.linalg.norm(b)
        th = np.arccos(np.clip(a @ b / np.linalg.norm(a) / np.linalg.norm(b), -1, 1))
        assert np.linalg.norm(a - b) >= 2 * rho * np.sin(th / 2) - 1e-12


def test_rate_limit_sizing_guarantees_direction_rate_when_tight():
    rho, h, w = 5.5, 0.2, 0.3
    D1, D2 = size_rate_limits(rho, h, w, 0.4)
    # worst case: two tight vectors at the chord limit
    th = 2 * np.arcsin(D1 / (2 * rho))
    assert th / h <= w + 1e-12


def test_candidate_C_infeasible_at_fuel_optimal_time_but_tight_when_feasible():
    r0, v0 = [10, 20, 50], [0, 0, 0]
    assert solve_candidate_C(r0, v0, 80.0, TGT, 7.7, VEH, CFG).u is None
    p = solve_candidate_C(r0, v0, 80.0, TGT, 9.0, VEH, CFG)
    assert p.u is not None and p.tightness().min() > 0.999


# ---------------------------------------------------------------- B building blocks
def test_attitude_sensitivity_matches_finite_differences():
    g = Grid(6.0, 20, 6)
    rng = np.random.default_rng(1)
    a0 = 0.2 * rng.normal(size=(21, 2))
    w0 = np.array([0.03, -0.02, 0.0])
    att = propagate_attitude(g, np.eye(3), w0, a0)
    Phi = attitude_sensitivity(g, att)
    da = 1e-5 * rng.normal(size=(21, 2))
    att2 = propagate_attitude(g, np.eye(3), w0, a0 + da)
    x = np.concatenate([da[:, 0], da[:, 1]])
    for s in (5, 60, g.S):
        Rrel = att['R'][s].T @ att2['R'][s]
        dphi = 0.5 * np.array([Rrel[2, 1] - Rrel[1, 2], Rrel[0, 2] - Rrel[2, 0], Rrel[1, 0] - Rrel[0, 1]])
        assert np.linalg.norm(dphi - Phi[s] @ x) <= 0.03 * np.linalg.norm(dphi)


def test_translation_quadrature_exact_for_linear_acceleration():
    g = Grid(3.0, 6, 4)
    a = np.column_stack([g.ts, 2 - g.ts, np.ones_like(g.ts)])
    Ar, cr, Av, cv = integrate_translation(g, np.zeros((g.S + 1, 3, 1)), a, np.zeros(3), np.zeros(3))
    T = g.ts[-1]
    exact_v = np.array([T**2 / 2, 2 * T - T**2 / 2, T])
    exact_r = np.array([T**3 / 6, T**2 - T**3 / 6, T**2 / 2])
    assert np.allclose(cv[-1], exact_v) and np.allclose(cr[-1], exact_r)


def test_centre_of_percussion_identity():
    """FLAT: with zero roll rate, y = r + (J_t/(m L)) b has acceleration along b (gimbal lateral force cancels)."""
    rng = np.random.default_rng(2)
    J, L, m = 60.0, 0.58, 79.0
    for _ in range(20):
        q = R_to_quat(expm_so3(0.3 * rng.normal(size=3)))
        w = np.array([*rng.normal(scale=0.5, size=2), 0.0])
        th, ph = rng.uniform(-0.25, 0.25, size=2)
        Tb = rng.uniform(400, 1000) * gimbal_dir(th, ph)
        x = np.concatenate([np.zeros(3), np.zeros(3), q, w, [m]])
        dx = deriv(x, Tb, 0.0, J, 3.7, L, 0.0)
        R = quat_to_R(q)
        b = R[:, 2]
        wd = dx[10:13]
        ww, wdw = R @ w, R @ wd
        bdd = np.cross(wdw, b) + np.cross(ww, np.cross(ww, b))
        ydd = dx[3:6] + J / (m * L) * bdd + np.array([0, 0, G0])
        assert np.linalg.norm(ydd - (ydd @ b) * b) < 1e-9


def test_gimbal_convention_roundtrip():
    for th, ph in [(0.1, -0.2), (-0.26, 0.26), (0.0, 0.0)]:
        t2, p2 = gimbal_angles(700 * gimbal_dir(th, ph))
        assert abs(t2 - th) < 1e-12 and abs(p2 - ph) < 1e-12


# ---------------------------------------------------------------- planner B end-to-end
@pytest.fixture(scope='module')
def plan_S3():
    r0, v0 = np.array([-8.0, 5, 45]), np.array([2.0, -1, -4])
    B = AACG(VEH, CFG)
    p = B.plan(r0, v0, 80.0, np.eye(3), np.zeros(3), TGT, 7.6)
    return r0, v0, p


def test_B_certified_and_flyable(plan_S3):
    r0, v0, p = plan_S3
    assert p.status == 'certified-inner'
    c = certify_B(p, VEH, CFG, r0, v0, 80.0, np.eye(3), np.zeros(3), TGT)
    assert c['passed'], c['checks']
    assert c['replay_dr'] < 0.05 and c['replay_dv'] < 0.05      # open-loop 6DOF quaternion replay lands


def test_B_above_3dof_lower_bound(plan_S3):
    r0, v0, p = plan_S3
    lb = solve_3dof_relaxation(r0, v0, 80.0, TGT, 7.6, VEH, CFG).fuel
    assert lb <= p.fuel + 1e-6
    assert (p.fuel - lb) / lb < 0.03


def test_B_vertical_matches_lower_bound():
    B = AACG(VEH, CFG)
    p = B.plan([0, 0, 50], [0, 0, 0], 80.0, np.eye(3), np.zeros(3), TGT, 8.6)
    lb = solve_3dof_relaxation(np.array([0, 0, 50.]), np.zeros(3), 80.0, TGT, 8.6, VEH, CFG).fuel
    assert p.status == 'certified-inner'
    assert abs(p.fuel - lb) / lb < 1e-3


def test_B_detects_infeasible_hop():
    """Pad hop that the 3DOF relaxation calls feasible but no flyable plan exists for (B reports best effort)."""
    cfg = default_config(glide_slope=None)
    r0, v0 = np.array([0, 0, 1.5]), np.array([0, 0, 7.0])
    assert solve_3dof_relaxation(r0, v0, 80.0, TGT, 4.0, VEH, cfg).u is not None
    p = AACG(VEH, cfg).plan(r0, v0, 80.0, np.eye(3), np.zeros(3), TGT, 4.0)
    assert p.status != 'certified-inner'


@pytest.mark.slow
def test_reference_D_agrees_with_B(plan_S3):
    from gtpl_guidance.reference_nlp import solve_reference, guess_from_planB
    r0, v0, p = plan_S3
    Xb, Tb = guess_from_planB(p, CFG.N)
    res = solve_reference(r0, v0, 80.0, np.eye(3), np.zeros(3), TGT, 7.6, VEH, CFG, [('B', Xb, Tb)])
    assert res['best'] is not None
    assert abs(res['best']['fuel'] - p.fuel) / p.fuel < 0.01


@pytest.mark.slow
def test_closed_loop_B_lands():
    from gtpl_guidance.guidance import PlannerB
    from gtpl_guidance.sim6dof import simulate, SimOptions
    r0, v0 = np.array([-8.0, 5, 45]), np.array([2.0, -1, -4])
    x0 = np.concatenate([r0, v0, R_to_quat(np.eye(3)), np.zeros(3), [80.0]])
    out = simulate(x0, TGT, PlannerB(VEH, CFG, TGT, 7.8), VEH, SimOptions(wind=(1.5, 0, 0), thrust_noise=0.02))
    assert out['success'], {k: v for k, v in out.items() if k != 'infos'}
