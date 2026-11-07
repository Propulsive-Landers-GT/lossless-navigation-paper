"""Pad-hop feasibility map: where the 3DOF relaxations (A, LCvx) claim a landing is possible but no flyable
pure-TVC plan exists. Vehicle launched from the pad (CG at 1.5 m) with upward speed v0z, land after tf = 4 s at a spot
d metres away. Writes results/hop_map.json.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.lcvx3dof import solve_baseline_A, solve_3dof_relaxation
from gtpl_guidance.aacg import AACG
from gtpl_guidance.certify import certify_3dof
from gtpl_guidance.reference_nlp import solve_reference, guess_from_planB, guess_from_3dof

TF = 4.0


def main():
    veh, cfg = default_vehicle(), default_config(glide_slope=None)
    B = AACG(veh, cfg)
    out = []
    for v0z in [5.0, 5.5, 6.0, 6.5, 7.0]:
        for d in [0.0, 2.0, 4.0, 6.0]:
            r0, v0, tgt = np.array([0, 0, 1.5]), np.array([0, 0, v0z]), np.array([d, 0, 1.5])
            pA = solve_baseline_A(r0, v0, 80.0, tgt, TF, veh, dt=0.2)
            cA = certify_3dof(pA, veh) if pA.u is not None else None
            p3 = solve_3dof_relaxation(r0, v0, 80.0, tgt, TF, veh, cfg)
            pB = B.plan(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, max_iter=40)
            gs = []
            if pB.T_body is not None:
                gs.append(('B',) + guess_from_planB(pB, cfg.N))
            if p3.u is not None:
                gs.append(('3dof',) + guess_from_3dof(p3, cfg.N, 80.0))
            D = solve_reference(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, veh, cfg, gs, max_iter=800)
            rec = dict(v0z=v0z, d=d, A_status=pA.status, A_Tdel_min=None if cA is None else cA['T_delivered_min'],
                       A_lossy=None if cA is None else cA['n_lossy'], relax3=p3.status, relax3_fuel=p3.fuel,
                       B=pB.status, B_defect=pB.defect, B_fuel=pB.fuel,
                       D_feasible=D['best'] is not None, D_fuel=None if D['best'] is None else D['best']['fuel'])
            print(json.dumps(rec, default=float), flush=True)
            out.append(rec)
            with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'hop_map.json'), 'w') as f:
                json.dump(out, f, indent=1, default=float)


if __name__ == '__main__':
    main()
