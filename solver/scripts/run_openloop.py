"""Open-loop comparison of planners A, B, C against the reference D and the 3DOF lower bound.

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/run_openloop.py  -> results/openloop.json
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
from gtpl_guidance.lcvx3dof import tf_search_A, solve_candidate_C, solve_3dof_relaxation, optimal_tf_3dof
from gtpl_guidance.aacg import AACG
from gtpl_guidance.certify import certify_B, certify_3dof
from gtpl_guidance.guidance import min_tf_B, min_tf_C, min_tf_3dof
from gtpl_guidance.reference_nlp import solve_reference, guess_from_planB, guess_from_3dof, perturb

SCENARIOS = [
    ('S1 vertical 50 m', [0, 0, 50], [0, 0, 0]),
    ('S2 offset (10,20,50)', [10, 20, 50], [0, 0, 0]),
    ('S3 (-8,5,45) moving', [-8, 5, 45], [2, -1, -4]),
    ('S4 (5,0,55) moving', [5, 0, 55], [-3, 2, -2]),
    ('S5 numerics in-air', [0, 0, 50], [4, 0, -5]),
    ('S6 (15,-10,60) sinking', [15, -10, 60], [0, 0, -6]),
    ('S7 (-5,-12,40)', [-5, -12, 40], [1, 3, -3]),
    ('S8 (20,0,50) drifting', [20, 0, 50], [-2, 0, -2]),
]
TARGET = np.array([0, 0, 1.5])
M0 = 80.0


def run_D(r0, v0, tf, veh, cfg, pB, p3, seed=0):
    rng = np.random.default_rng(seed)
    gs = []
    if pB is not None and pB.T_body is not None:
        Xb, Tb = guess_from_planB(pB, cfg.N)
        gs += [('B', Xb, Tb), ('B+pert1',) + perturb(Xb, Tb, rng), ('B+pert2',) + perturb(Xb, Tb, rng, 0.1, 60.0)]
    if p3 is not None and p3.u is not None:
        gs.append(('3dof',) + guess_from_3dof(p3, cfg.N, M0))
    res = solve_reference(r0, v0, M0, np.eye(3), np.zeros(3), TARGET, tf, veh, cfg, gs)
    return dict(best=None if res['best'] is None else res['best']['fuel'],
                best_start=None if res['best'] is None else res['best']['name'],
                runs=[dict(name=r['name'], ok=r['ok'], fuel=r['fuel'], wall=r['wall'], status=r['status']) for r in res['runs']])


def main():
    veh, cfg = default_vehicle(), default_config()
    out = []
    for name, r0, v0 in SCENARIOS:
        r0, v0 = np.array(r0, float), np.array(v0, float)
        row = dict(name=name, r0=r0.tolist(), v0=v0.tolist())
        t0 = time.time()
        # A: faithful flight code
        pA = tf_search_A(r0, v0, M0, TARGET, veh)
        cA = certify_3dof(pA, veh)
        row['A'] = dict(tf=pA.tf, fuel=pA.fuel, **{k: v for k, v in cA.items() if k != 'checks'}, checks=cA['checks'],
                        solve_time=pA.info['total_solve_time'])
        # lower bounds and times of flight
        tf3 = min_tf_3dof(r0, v0, M0, TARGET, veh, cfg)
        tf3opt, V3opt = optimal_tf_3dof(r0, v0, M0, TARGET, veh, cfg, lo=max(tf3, 2.0))
        tfB, pB = min_tf_B(r0, v0, M0, np.eye(3), np.zeros(3), TARGET, veh, cfg, lo=tf3)
        row['tf'] = dict(min_3dof=tf3, opt_3dof=tf3opt, min_B=tfB)
        row['LB_global'] = V3opt
        B = AACG(veh, cfg)
        for tag, tf in [('tfB', tfB), ('tfB+0.5', tfB + 0.5)]:
            p3 = solve_3dof_relaxation(r0, v0, M0, TARGET, tf, veh, cfg)
            pB = B.plan(r0, v0, M0, np.eye(3), np.zeros(3), TARGET, tf, tol=1e-5, max_iter=30)
            cB = certify_B(pB, veh, cfg, r0, v0, M0, np.eye(3), np.zeros(3), TARGET)
            # B0: warm start + one exact inner solve, no attitude iterations
            pB0 = B.plan(r0, v0, M0, np.eye(3), np.zeros(3), TARGET, tf, max_iter=0)
            pC = solve_candidate_C(r0, v0, M0, TARGET, tf, veh, cfg)
            cC = certify_3dof(pC, veh)
            D = run_D(r0, v0, tf, veh, cfg, pB, p3)
            row[tag] = dict(tf=tf, LB=p3.fuel,
                            B=dict(fuel=pB.fuel, status=pB.status, iters=pB.iters, solve_time=pB.solve_time,
                                   wall=pB.wall_time, n_solves=pB.info['n_solves'], cert=cB['passed'],
                                   cert_detail={k: bool(v) for k, v in cB['checks'].items()},
                                   gimbal_max_deg=cB['gimbal_max_deg'], gimbal_rate_max_dps=cB['gimbal_rate_max_dps'],
                                   tilt_max_deg=cB['tilt_max_deg'], ang_acc_ratio=cB['ang_acc_ratio'],
                                   replay_dr=cB.get('replay_dr'), replay_dv=cB.get('replay_dv')),
                            B0=dict(fuel=pB0.fuel, status=pB0.status, defect=pB0.defect),
                            C=dict(fuel=pC.fuel, status=pC.status, **({} if pC.u is None else
                                   {k: v for k, v in cC.items() if k != 'checks'})),
                            D=D)
        tfC = min_tf_C(r0, v0, M0, TARGET, veh, cfg, lo=tf3)
        pC = solve_candidate_C(r0, v0, M0, TARGET, tfC, veh, cfg) if tfC else None
        row['C_own'] = dict(tf=tfC, fuel=None if pC is None else pC.fuel)
        row['wall'] = time.time() - t0
        print(json.dumps(dict(name=name, A=(round(pA.tf, 2), round(pA.fuel, 3)), tfB=tfB,
                              B=row['tfB']['B']['fuel'], D=row['tfB']['D']['best'], LB=row['tfB']['LB'],
                              C=row['tfB']['C']['fuel'], C_own=row['C_own'], wall=round(row['wall'], 1))), flush=True)
        out.append(row)
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'results'), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'openloop.json'), 'w') as f:
            json.dump(out, f, indent=1, default=float)


if __name__ == '__main__':
    main()
