"""Open-loop head-to-head: planner B vs standard 6DOF SCvx (baseline S) on the 8 in-air scenarios.

Same t_f as RESULTS.md section 1 (B's minimum certified t_f, read from results/openloop.json) and t_f + 0.5 s.
S is run from two standard initial guesses: the 3DOF solution (the same warm start B uses) and a straight-line
guess (Szmuk & Acikmese 2018). Every plan is checked by the same certificate (certify_B: physical limits on the fine
grid + open-loop replay through the full quaternion rigid body). D (IPOPT multistart) and LB are taken from
results/openloop.json.

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/run_openloop_scvx.py  -> results/openloop_scvx.json
"""
import json
import os
import sys
import time
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.aacg import AACG
from gtpl_guidance.scvx6dof import SCvx6DOF
from gtpl_guidance.certify import certify_B

HERE = os.path.dirname(__file__)
TARGET = np.array([0, 0, 1.5])
M0 = 80.0
I3, Z3 = np.eye(3), np.zeros(3)


def _ok(d, tol_tilt):
    return d['r'] < 0.01 and d['v'] < 0.01 and d['tilt'] < tol_tilt


def first_feasible_B(hist, tol_tilt):
    """SOCPs solved (incl. warm start) when B first holds a plan landing within 1 cm / 1 cm/s / tilt tol."""
    for h in hist:
        if _ok(h, tol_tilt):
            return h['n_solves'], h['solve_time']
    return None


def first_feasible_S(hist, tol_tilt):
    """Same criterion for S, applied to the open-loop (single-shooting) landing error of its current thrust plan."""
    for h in hist:
        if _ok(h['shoot'], tol_tilt):
            return h['n_solves'], h['solve_time']
    return None


def summarize(p, c, kind, cfg):
    d = dict(fuel=p.fuel, status=p.status, iters=p.iters, n_solves=p.info.get('n_solves'), solve_time=p.solve_time,
             wall=p.wall_time, cert=c['passed'], failed_checks=[k for k, v in c['checks'].items() if not v],
             replay_dr=c.get('replay_dr'), replay_dv=c.get('replay_dv'), defect=p.defect)
    if kind == 'B':
        d['first_feasible_iter'] = first_feasible_B(p.history, cfg.terminal_tilt_tol)
    else:
        d['first_feasible_iter'] = first_feasible_S(p.history, cfg.terminal_tilt_tol)
        d['converged'] = p.info.get('converged')
    return d


def main():
    veh, cfg = default_vehicle(), default_config()
    ref = json.load(open(os.path.join(HERE, '..', 'results', 'openloop.json')))
    B, S = AACG(veh, cfg), SCvx6DOF(veh, cfg)
    out = []
    for row0 in ref:
        r0, v0 = np.array(row0['r0'], float), np.array(row0['v0'], float)
        row = dict(name=row0['name'], r0=row0['r0'], v0=row0['v0'])
        for tag in ('tfB', 'tfB+0.5'):
            tf = row0[tag]['tf']
            res = dict(tf=tf, LB=row0[tag]['LB'], D=row0[tag]['D']['best'])
            pB = B.plan(r0, v0, M0, I3, Z3, TARGET, tf, tol=1e-5, max_iter=30)
            res['B'] = summarize(pB, certify_B(pB, veh, cfg, r0, v0, M0, I3, Z3, TARGET), 'B', cfg)
            for init in ('3dof', 'linear'):
                pS = S.plan(r0, v0, M0, I3, Z3, TARGET, tf, init=init, tol=1e-5, max_iter=100, track_feasible=True)
                res[f'S_{init}'] = summarize(pS, certify_B(pS, veh, cfg, r0, v0, M0, I3, Z3, TARGET), 'S', cfg)
            row[tag] = res
            print(json.dumps(dict(name=row['name'], tag=tag, D=res['D'],
                                  **{k: (round(res[k]['fuel'], 4), res[k]['cert'], res[k]['iters'], round(res[k]['solve_time'], 2))
                                     for k in ('B', 'S_3dof', 'S_linear')})), flush=True)
        out.append(row)
        with open(os.path.join(HERE, '..', 'results', 'openloop_scvx.json'), 'w') as f:
            json.dump(out, f, indent=1, default=float)


if __name__ == '__main__':
    main()
