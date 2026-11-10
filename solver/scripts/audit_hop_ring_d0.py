"""Follow-up to audit_hop_ring.py: is 'no plan straight back down' at v0z = 6.3 m/s an artefact of symmetric starts?

For d = 0 the 3DOF and planner-B guesses have no lateral motion, and a symmetric start can leave IPOPT at a symmetric
infeasible point. This script retries the d = 0 cell from ASYMMETRIC starts: the flyable solutions found for d = 1, 2
and 3 m (with their lateral position scaled to return to the pad) and random perturbations of them.
Writes results/audit_hop_ring_d0.json.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.lcvx3dof import solve_3dof_relaxation
from gtpl_guidance.reference_nlp import solve_reference, guess_from_3dof, perturb

TF = 4.0


def main():
    veh, cfg = default_vehicle(), default_config(glide_slope=None)
    rng = np.random.default_rng(0)
    out = []
    for v0z in (6.3, 6.25):
        r0, v0 = np.array([0, 0, 1.5]), np.array([0, 0, v0z])
        starts = []
        for d in (1.0, 2.0, 3.0):
            tgt = np.array([d, 0, 1.5])
            p3 = solve_3dof_relaxation(r0, v0, 80.0, tgt, TF, veh, cfg)
            D = solve_reference(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, veh, cfg,
                                [('3dof',) + guess_from_3dof(p3, cfg.N, 80.0)], max_iter=800)
            if D['best'] is None:
                continue
            X, T = D['best']['X'].copy(), D['best']['T'].copy()
            lam = np.linspace(0, 1, len(X))
            Xb = X.copy()
            Xb[:, 0] = X[:, 0] * (1 - lam)                      # same attitude history, path bent back to the pad
            starts += [(f'from d={d:.0f}', Xb, T), (f'from d={d:.0f} perturbed',) + perturb(Xb, T, rng),
                       (f'from d={d:.0f} raw', X, T)]
        res = solve_reference(r0, v0, 80.0, np.eye(3), np.zeros(3), np.array([0, 0, 1.5]), TF, veh, cfg, starts,
                              max_iter=1500)
        rec = dict(v0z=v0z, n_starts=len(starts), feasible=res['best'] is not None,
                   runs=[dict(name=r['name'], ok=r['ok'], status=r['status']) for r in res['runs']])
        print(json.dumps(rec), flush=True)
        out.append(rec)
    with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'audit_hop_ring_d0.json'), 'w') as f:
        json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
