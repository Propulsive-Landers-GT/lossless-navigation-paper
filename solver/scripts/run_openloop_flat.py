"""Open-loop comparison: planner F (one SOCP) vs planner B vs standard 6DOF SCvx (S) on the 8 in-air scenarios.

For each scenario, at B's minimum certified final time + 0.5 s (the closed-loop operating point) and at each
planner's own minimum final time:
  fuel, number of SOCPs, conic-solver time, the planner's certificate, and the landing error of an OPEN-LOOP replay of
  the plan through the full rigid body under three plant models ('cop' = centre of percussion fixed in the body,
  'frozen' = J_t and L frozen at their initial values, 'table' = the sim-plant mass-property table).

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/run_openloop_flat.py  -> results/openloop_flat.json
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
from gtpl_guidance.lcvx3dof import solve_3dof_relaxation
from gtpl_guidance.aacg import AACG
from gtpl_guidance.scvx6dof import SCvx6DOF
from gtpl_guidance.fcg import FCG
from gtpl_guidance.certify import certify_B
from gtpl_guidance.flatcert import certify_F
from gtpl_guidance.guidance import min_tf_F
from gtpl_guidance.dynamics import deriv
from gtpl_guidance.rotations import R_to_quat, quat_to_R, tilt_of_R

TARGET = np.array([0, 0, 1.5])
M0 = 80.0
R0, W0 = np.eye(3), np.zeros(3)


def replay_planB(plan, veh, r0, v0, m0, model, sub=8):
    """Open-loop replay of a B / S plan (FOH body thrust on the fine grid) under a chosen mass-property model."""
    g = plan.grid
    J0, L0 = veh.inertia_lever(m0)
    eps0 = J0 / (m0 * L0)

    def props(m):
        if model == 'frozen':
            return J0, L0
        if model == 'cop':
            return eps0 * m * L0, L0
        return veh.inertia_lever(m)
    x = np.concatenate([r0, v0, R_to_quat(R0), W0, [m0]])
    Tb = plan.T_body
    dt = g.hs / sub
    for s in range(g.S):
        for j in range(sub):
            l0, lm, l1 = j / sub, (j + 0.5) / sub, (j + 1) / sub
            Tl = lambda l: (1 - l) * Tb[s] + l * Tb[s + 1]
            f = lambda xx, T: deriv(xx, T, 0.0, *props(xx[13])[:1], veh.J_z, props(xx[13])[1], veh.alpha)
            k1 = f(x, Tl(l0)); k2 = f(x + 0.5 * dt * k1, Tl(lm)); k3 = f(x + 0.5 * dt * k2, Tl(lm)); k4 = f(x + dt * k3, Tl(l1))
            x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            x[6:10] /= np.linalg.norm(x[6:10])
    return dict(dr=float(np.linalg.norm(x[0:3] - TARGET)), dv=float(np.linalg.norm(x[3:6])),
                tilt_deg=float(np.degrees(tilt_of_R(quat_to_R(x[6:10])))))


def main():
    veh, cfg = default_vehicle(), default_config()
    stored = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'results', 'openloop.json')))
    F = FCG(veh, cfg, S=16)
    out = []
    for row in stored:
        r0, v0 = np.array(row['r0'], float), np.array(row['v0'], float)
        tfB = row['tfB']['tf']
        rec = dict(name=row['name'], r0=row['r0'], v0=row['v0'], tfB=tfB, tf3=row['tf']['min_3dof'])
        t0 = time.time()
        rec['tfF'] = min_tf_F(r0, v0, M0, R0, W0, TARGET, veh, cfg, lo=tfB - 0.05, tol=0.01)
        rec['tfF_search_wall'] = time.time() - t0
        for label, tf in (('tfB+0.5', tfB + 0.5), ('own_min', None)):
            e = {}
            tfb = tf if tf is not None else tfB
            tff = tf if tf is not None else rec['tfF']
            lb = solve_3dof_relaxation(r0, v0, M0, TARGET, tfb, veh, cfg)
            e['LB'] = dict(tf=tfb, fuel=lb.fuel)
            pB = AACG(veh, cfg).plan(r0, v0, M0, R0, W0, TARGET, tfb)
            cB = certify_B(pB, veh, cfg, r0, v0, M0, R0, W0, TARGET)
            e['B'] = dict(tf=tfb, fuel=pB.fuel, n_solves=pB.info.get('n_solves'), solve_time=pB.solve_time, cert=cB['passed'],
                          **{f'replay_{m}': replay_planB(pB, veh, r0, v0, M0, m) for m in ('frozen', 'cop', 'table')})
            pS = SCvx6DOF(veh, cfg).plan(r0, v0, M0, R0, W0, TARGET, tfb, init='3dof', max_iter=100)
            cS = certify_B(pS, veh, cfg, r0, v0, M0, R0, W0, TARGET)
            e['S'] = dict(tf=tfb, fuel=pS.fuel, n_solves=pS.info.get('n_solves'), solve_time=pS.solve_time, cert=cS['passed'],
                          status=pS.status,
                          **{f'replay_{m}': replay_planB(pS, veh, r0, v0, M0, m) for m in ('frozen', 'cop', 'table')})
            for name, refine in (('F1', 0), ('F', 2)):
                p = F.plan(r0, v0, M0, R0, W0, TARGET, tff, refine=refine)
                if p.traj is None:
                    e[name] = dict(tf=tff, fuel=None, status=p.status)
                    continue
                c = certify_F(p, veh, cfg, r0, v0, M0, R0, W0, TARGET, models=('cop', 'frozen', 'table'))
                e[name] = dict(tf=tff, fuel=p.fuel, fuel_bound=p.fuel_bound, n_solves=p.n_solves, solve_time=p.solve_time,
                               cert=c['passed'], checks={k: bool(v) for k, v in c['checks'].items()},
                               **{k: c[k] for k in c if k not in ('checks', 'passed')})
            rec[label] = e
        out.append(rec)
        a = rec['tfB+0.5']
        print(f"{rec['name'][:3]} tfB {tfB:.2f} tfF {rec['tfF']:.2f} | @tfB+0.5 fuel LB {a['LB']['fuel']:.4f} B {a['B']['fuel']:.4f} S {a['S']['fuel']:.4f} "
              f"F1 {a['F1']['fuel']:.4f} F {a['F']['fuel']:.4f} | SOCPs B {a['B']['n_solves']} S {a['S']['n_solves']} F1 1 | "
              f"time B {a['B']['solve_time']:.2f} S {a['S']['solve_time']:.2f} F1 {a['F1']['solve_time']:.3f} | "
              f"replay own-model dr: B {a['B']['replay_frozen']['dr']:.1e} S {a['S']['replay_frozen']['dr']:.1e} F {a['F1']['replay_cop_dr']:.1e} | "
              f"table dr: B {a['B']['replay_table']['dr']:.2f} S {a['S']['replay_table']['dr']:.2f} F {a['F1']['replay_table_dr']:.2f}", flush=True)
        with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'openloop_flat.json'), 'w') as f:
            json.dump(out, f, indent=0, default=float)


if __name__ == '__main__':
    main()
