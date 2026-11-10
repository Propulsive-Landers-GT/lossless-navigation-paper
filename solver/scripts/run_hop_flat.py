"""Pad-hop map for planner F: soundness and completeness against the IPOPT reference D (results/hop_map.json).

Same 20 cells as run_hop.py (launch from the pad with upward speed v0z, land d metres away after exactly 4 s).
Soundness: F must be infeasible wherever no flyable plan exists. Completeness: how many flyable cells F keeps, and how
much later a final time it needs where it rejects one. Writes results/hop_map_flat.json.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.fcg import FCG
from gtpl_guidance.flatcert import certify_F
from gtpl_guidance.guidance import bisect_min_tf

TF = 4.0


def main():
    veh, cfg = default_vehicle(), default_config(glide_slope=None)
    here = os.path.dirname(__file__)
    stored = json.load(open(os.path.join(here, '..', 'results', 'hop_map.json')))
    F = FCG(veh, cfg, S=16)
    out = []
    for row in stored:
        v0z, d = row['v0z'], row['d']
        r0, v0, tgt = np.array([0, 0, 1.5]), np.array([0, 0, v0z]), np.array([d, 0, 1.5])
        args = (r0, v0, 80.0, np.eye(3), np.zeros(3), tgt)
        p = F.plan(*args, TF, refine=2)
        rec = dict(v0z=v0z, d=d, D_feasible=row['D_feasible'], D_fuel=row['D_fuel'], B=row['B'], relax3=row['relax3'],
                   F_feasible=p.traj is not None, F_fuel=None if p.traj is None else p.fuel, F_solves=p.n_solves,
                   F_solve_time=p.solve_time)
        if p.traj is not None:
            c = certify_F(p, veh, cfg, *args)
            rec.update(F_cert=c['passed'], F_replay_dr=c['replay_cop_dr'])
        else:   # the smallest final time F accepts for this cell (None if it accepts none up to 8 s)
            f = lambda tf: F.solve(*args, tf)[0] is not None
            rec['F_min_tf'] = bisect_min_tf(f, TF, TF + 1.0, tol=0.05, hi_max=8.0)
        print(json.dumps(rec, default=float), flush=True)
        out.append(rec)
        with open(os.path.join(here, '..', 'results', 'hop_map_flat.json'), 'w') as fh:
            json.dump(out, fh, indent=1, default=float)
    n_sound = sum(1 for r in out if r['F_feasible'] and not r['D_feasible'])
    n_kept = sum(1 for r in out if r['F_feasible'] and r['D_feasible'])
    print(f"F feasible where no flyable plan was found: {n_sound}; flyable cells kept: {n_kept}/{sum(r['D_feasible'] for r in out)}")


if __name__ == '__main__':
    main()
