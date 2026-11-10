"""Audit of the 'single convex program for 6-DoF' construction on the GTPL vehicle.

The construction (as described): treat the thrust direction as the attitude; impose the start attitude, the upright
landing, a turn-rate limit and a torque limit as convex constraints on the thrust vector (sized for the minimum
thrust, hence stricter than the true limits); keep the lossless thrust relaxation ||T|| <= Gamma. In this repo that
is candidate C (`lcvx3dof.solve_candidate_C`, sound sizing) plus the two boundary directions.

Questions answered on the 40 in-air and 30 pad-hop Monte Carlo cases, at the same final time the other planners fly:
  1. Is the relaxation tight (||T|| = Gamma at every node)? If not, the plan asks for less thrust than the engine's
     minimum and is not a trajectory of the vehicle at all.
  2. For a GIMBALLED vehicle following the planned thrust direction with its body: which gimbal angle does that need,
     and how far does the CG depart from the plan (centre-of-percussion identity: the planned path is followed by the
     centre of percussion, so the CG is off by eps * (b0 - b(t)) plus the effect of the initial body rate)?

Usage: .venv/bin/python scripts/audit_single_convex.py   -> results/audit_single_convex.json
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.lcvx3dof import solve_candidate_C
from gtpl_guidance.fcg import FCG
from gtpl_guidance.guidance import bisect_min_tf
from run_montecarlo import draw_case


def main():
    veh = default_vehicle()
    here = os.path.dirname(__file__)
    out = []
    for scen in ('inair', 'hop'):
        cfg = default_config(glide_slope=None) if scen == 'hop' else default_config()
        mc = json.load(open(os.path.join(here, '..', 'results', f'mc_{scen}_flat.json')))
        tfs = {r['case']: r['tfB'] + 0.5 for r in mc if r.get('tfB')}
        F = FCG(veh, cfg, S=16)
        for i in sorted(tfs):
            r0, v0, R0, w0, m0, target, _ = draw_case(scen, i)
            tf = tfs[i]
            p = solve_candidate_C(r0, v0, m0, target, tf, veh, cfg, dir0=R0[:, 2], dirN=[0, 0, 1.0])
            rec = dict(scenario=scen, case=i, tf=tf, status=p.status)
            if p.u is not None:
                tight = p.tightness()
                Tdel = np.linalg.norm(p.T, axis=1)
                h = tf / p.N
                b = p.u / np.linalg.norm(p.u, axis=1, keepdims=True)
                f = np.linalg.norm(p.u, axis=1)
                bdd = (b[2:] - 2 * b[1:-1] + b[:-2]) / h**2
                Pbdd = bdd - np.sum(bdd * b[1:-1], axis=1)[:, None] * b[1:-1]
                J, L = veh.inertia_lever(m0)
                eps = J / (m0 * L)
                gim = np.degrees(np.arctan(eps * np.linalg.norm(Pbdd, axis=1) / f[1:-1]))
                bd0 = R0 @ np.array([w0[1], -w0[0], 0.0])
                rec.update(fuel=p.fuel, tight_min=float(tight.min()), n_lossy=int(np.sum(tight < 0.999)),
                           T_delivered_min=float(Tdel.min()), gimbal_needed_max_deg=float(gim.max()),
                           cg_offset_midflight_max=float(eps * np.linalg.norm(b - R0[:, 2], axis=1).max()),
                           cg_drift_from_initial_rate=float(eps * np.linalg.norm(bd0) * tf),
                           tilt_start_deg=float(np.degrees(np.arccos(np.clip(b[0] @ R0[:, 2], -1, 1)))))
            else:   # how much later a final time does this program need?
                feas = lambda t: solve_candidate_C(r0, v0, m0, target, t, veh, cfg, dir0=R0[:, 2], dirN=[0, 0, 1.0]).u is not None
                rec['min_tf'] = bisect_min_tf(feas, tf, tf + 1.0, tol=0.05, hi_max=tf + 6.0)
                rec['feasible_without_attitude_bc'] = solve_candidate_C(r0, v0, m0, target, tf, veh, cfg).u is not None
            pf = F.plan(r0, v0, m0, R0, w0, target, tf, refine=0)
            rec.update(F_status=pf.status, F_fuel=None if pf.traj is None else pf.fuel)
            out.append(rec)
            print(json.dumps(rec, default=float), flush=True)
    with open(os.path.join(here, '..', 'results', 'audit_single_convex.json'), 'w') as fh:
        json.dump(out, fh, indent=0, default=float)
    for scen in ('inair', 'hop'):
        rr = [r for r in out if r['scenario'] == scen]
        ok = [r for r in rr if 'fuel' in r]
        bad = [r for r in rr if 'fuel' not in r]
        print(f"{scen}: {len(rr)} cases | program feasible {len(ok)} | relaxation not tight {sum(r['n_lossy'] > 0 for r in ok)} | "
              f"infeasible cases need {np.median([r['min_tf'] - r['tf'] for r in bad if r.get('min_tf')] or [np.nan]):.2f} s more (median) | "
              f"F feasible {sum(r['F_status'] != 'infeasible' for r in rr)}")


if __name__ == '__main__':
    main()
