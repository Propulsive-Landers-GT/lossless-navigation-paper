"""Independent reproduction of the obstruction behind the impossibility theorem, on the planner's own model.

Theorem A: a convex program that is both sound and complete exists only if the set of initial data from which a
landing is possible is convex. Here: launch from the pad straight up with speed v0z, land d metres away after exactly
4 s (pure-TVC vehicle, planning limits of params.py, no glide slope). If, for some v0z, a landing straight back down
(d = 0) is impossible while landings at +d and -d are possible, the feasible set is not convex (its midpoint is
missing): the landing spots form a ring.

Feasibility is decided by the nonconvex reference D (CasADi/IPOPT on the full rigid body, several starts), which does
not use planner F. "No plan found" is numerical evidence, not a proof. Planner F is run on the same cells: it must
refuse the cells where no plan exists.

Usage: .venv/bin/python scripts/audit_hop_ring.py   -> results/audit_hop_ring.json
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
from gtpl_guidance.aacg import AACG
from gtpl_guidance.fcg import FCG
from gtpl_guidance.reference_nlp import solve_reference, guess_from_planB, guess_from_3dof

TF = 4.0


def main():
    veh, cfg = default_vehicle(), default_config(glide_slope=None)
    B, F = AACG(veh, cfg), FCG(veh, cfg, S=16)
    out = []
    for v0z in [6.0, 6.1, 6.2, 6.3, 6.4]:
        for d in [0.0, 1.0, 2.0, 3.0]:
            r0, v0, tgt = np.array([0, 0, 1.5]), np.array([0, 0, v0z]), np.array([d, 0, 1.5])
            p3 = solve_3dof_relaxation(r0, v0, 80.0, tgt, TF, veh, cfg)
            pB = B.plan(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, max_iter=40)
            gs = []
            if pB.T_body is not None:
                gs.append(('B',) + guess_from_planB(pB, cfg.N))
            if p3.u is not None:
                gs.append(('3dof',) + guess_from_3dof(p3, cfg.N, 80.0))
            D = solve_reference(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, veh, cfg, gs, max_iter=800)
            pF = F.plan(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, TF, refine=0)
            rec = dict(v0z=v0z, d=d, relax3=p3.status, B=pB.status, D_feasible=D['best'] is not None,
                       D_fuel=None if D['best'] is None else D['best']['fuel'], F_feasible=pF.traj is not None)
            print(json.dumps(rec, default=float), flush=True)
            out.append(rec)
            with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'audit_hop_ring.json'), 'w') as f:
                json.dump(out, f, indent=1, default=float)
    for v0z in sorted({r['v0z'] for r in out}):
        row = [r for r in out if r['v0z'] == v0z]
        print(f"v0z = {v0z}: " + ', '.join(f"d={r['d']:.0f}: {'flyable' if r['D_feasible'] else 'none'}" for r in row)
              + ('   <-- ring (d = 0 impossible, d > 0 possible)' if (not row[0]['D_feasible'] and any(r['D_feasible'] for r in row[1:])) else ''))
    print('F feasible where D found nothing:', sum(r['F_feasible'] and not r['D_feasible'] for r in out))


if __name__ == '__main__':
    main()
