"""Pad-hop feasibility map for baseline S (standard 6DOF SCvx), on the same 20 cells as results/hop_map.json.

Planner B is re-run here (same settings as run_hop.py) so both are timed under the same machine load; the IPOPT
reference D's feasibility verdict is read from results/hop_map.json. Writes results/hop_map_scvx.json.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.aacg import AACG
from gtpl_guidance.scvx6dof import SCvx6DOF
from gtpl_guidance.certify import certify_B

HERE = os.path.dirname(__file__)
TF = 4.0
I3, Z3 = np.eye(3), np.zeros(3)


def main():
    veh, cfg = default_vehicle(), default_config(glide_slope=None)
    B, S = AACG(veh, cfg), SCvx6DOF(veh, cfg)
    ref = {(r['v0z'], r['d']): r for r in json.load(open(os.path.join(HERE, '..', 'results', 'hop_map.json')))}
    out = []
    for (v0z, d), r in sorted(ref.items()):
        r0, v0, tgt = np.array([0, 0, 1.5]), np.array([0, 0, v0z]), np.array([d, 0, 1.5])
        rec = dict(v0z=v0z, d=d, D_feasible=r['D_feasible'], D_fuel=r['D_fuel'], relax3=r['relax3'])
        pB = B.plan(r0, v0, 80.0, I3, Z3, tgt, TF, max_iter=40)
        cB = certify_B(pB, veh, cfg, r0, v0, 80.0, I3, Z3, tgt)
        rec['B'] = dict(status=pB.status, cert=cB['passed'], fuel=pB.fuel, defect=pB.defect, iters=pB.iters,
                        n_solves=pB.info.get('n_solves'), solve_time=pB.solve_time, wall=pB.wall_time)
        for init in ('3dof', 'linear'):
            pS = S.plan(r0, v0, 80.0, I3, Z3, tgt, TF, init=init, max_iter=100)
            cS = certify_B(pS, veh, cfg, r0, v0, 80.0, I3, Z3, tgt)
            rec[f'S_{init}'] = dict(status=pS.status, cert=cS['passed'], fuel=pS.fuel, defect=pS.defect,
                                    iters=pS.iters, n_solves=pS.info.get('n_solves'), solve_time=pS.solve_time,
                                    wall=pS.wall_time, converged=pS.info.get('converged'),
                                    max_node_defect=pS.info.get('max_node_defect'))
        print(json.dumps(dict(v0z=v0z, d=d, D=r['D_feasible'],
                              **{k: (rec[k]['status'], rec[k]['cert'], round(rec[k]['fuel'], 3), rec[k]['iters'])
                                 for k in ('B', 'S_3dof', 'S_linear')}), default=float), flush=True)
        out.append(rec)
        with open(os.path.join(HERE, '..', 'results', 'hop_map_scvx.json'), 'w') as f:
            json.dump(out, f, indent=1, default=float)


if __name__ == '__main__':
    main()
