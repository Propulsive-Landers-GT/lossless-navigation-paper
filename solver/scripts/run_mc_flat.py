"""Closed-loop Monte Carlo: planner F (flat convex guidance) against planner B and standard 6DOF SCvx (S).

Same plant, disturbances, tracker, cases and seeds as run_montecarlo.py. Variants (comma-separated --methods):

  repo protocol (1 Hz replans, replans stop 1.5 s before touchdown, plans applied instantly; all at t_f = tfB + 0.5):
      B, S, F          the three planners under identical conditions
  realistic compute (a plan computed from the state at time t is applied at t + its conic-solver time; each planner
  replans as fast as it can sustain):
      Blat, Slat       B / S, at most every 0.5 s, t_lock 1.5 s
      F10              F every 0.1 s, t_lock 0.6 s, t_f = tfB + 0.5
      F10own           the same with F's own time of flight (min_tf_F + 0.5 s): no dependence on B at all

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/run_mc_flat.py --scenario inair --n 40 --workers 3
Writes results/mc_<scenario>_flat.json.
"""
import argparse
import json
import os
import sys
import time
import warnings
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.guidance import PlannerB, PlannerS, PlannerF, min_tf_B, min_tf_3dof, min_tf_F
from gtpl_guidance.sim6dof import simulate
from gtpl_guidance.rotations import R_to_quat
from run_montecarlo import draw_case, TF_MARGIN

SIM = {
    'B': {}, 'S': {}, 'F': {},
    'Blat': dict(latency=True, replan_dt=0.5), 'Slat': dict(latency=True, replan_dt=0.5),
    'F10': dict(latency=True, replan_dt=0.1, t_lock=0.6), 'F10own': dict(latency=True, replan_dt=0.1, t_lock=0.6),
    'F10nolat': dict(replan_dt=0.1, t_lock=0.6),
}


def run_case(args):
    scenario, i, methods = args
    veh = default_vehicle()
    cfg = default_config(glide_slope=None) if scenario == 'hop' else default_config()
    r0, v0, R0, w0, m0, target, opts = draw_case(scenario, i)
    x0 = np.concatenate([r0, v0, R_to_quat(R0), w0, [m0]])
    recs = []
    t0 = time.time()
    tf3 = min_tf_3dof(r0, v0, m0, target, veh, cfg)
    tt = time.time()
    tfB, _ = min_tf_B(r0, v0, m0, R0, w0, target, veh, cfg, lo=tf3)
    t_tfB = time.time() - tt
    tt = time.time()
    tfF = min_tf_F(r0, v0, m0, R0, w0, target, veh, cfg, lo=tf3)
    t_tfF = time.time() - tt
    for meth in methods:
        tm = time.time()
        if tfB is None or (meth == 'F10own' and tfF is None):
            recs.append(dict(case=i, method=meth, failed='no feasible tf'))
            continue
        if meth.startswith('B'):
            pl = PlannerB(veh, cfg, target, tfB + TF_MARGIN)
        elif meth.startswith('S'):
            pl = PlannerS(veh, cfg, target, tfB + TF_MARGIN)
        elif meth == 'F10own':
            pl = PlannerF(veh, cfg, target, tfF + TF_MARGIN)
        else:
            pl = PlannerF(veh, cfg, target, tfB + TF_MARGIN)
        out = simulate(x0, target, pl, veh, replace(opts, **SIM[meth]))
        infos = out.pop('infos')
        if 'failed' in out:
            recs.append(dict(case=i, method=meth, failed=out['failed']))
            continue
        st = [inf.get('solve_time', np.nan) for inf in infos if inf.get('solve_time') is not None]
        wl = [inf.get('wall', np.nan) for inf in infos]
        peaks = [inf['peaks'] for inf in infos if inf.get('peaks')]
        rec = dict(case=i, method=meth, tf3=tf3, tfB=tfB, tfF=tfF, t_tfB=t_tfB, t_tfF=t_tfF, **out,
                   n_replans=len(infos), cert_rate=float(np.mean([bool(inf.get('cert')) for inf in infos])),
                   cert_first=bool(infos[0].get('cert')),
                   solve_mean=float(np.nanmean(st)), solve_max=float(np.nanmax(st)), solve_first=float(st[0]),
                   solve_replan_mean=float(np.nanmean(st[1:])) if len(st) > 1 else None,
                   solve_replan_max=float(np.nanmax(st[1:])) if len(st) > 1 else None,
                   wall_mean=float(np.nanmean(wl)), wall_max=float(np.nanmax(wl)), sim_wall=time.time() - tm,
                   n_socp=int(sum(inf.get('n_solves') or 0 for inf in infos)),
                   n_socp_replan_max=int(max([inf.get('n_solves') or 0 for inf in infos[1:]] or [0])),
                   tf_ext=float(sum(inf.get('tf_ext', 0) or 0 for inf in infos)),
                   n_fallback=int(sum(bool(inf.get('continued')) or (inf.get('tf_ext') or 0) > 0 for inf in infos[1:])),
                   n_kept_previous=int(sum(not bool(inf.get('cert')) for inf in infos[1:])),
                   plan_fuel0=infos[0].get('fuel_plan'))
        if peaks:
            rec['plan_peaks'] = {k: float(max(p[k] for p in peaks)) if k != 'T_min' else float(min(p[k] for p in peaks))
                                 for k in peaks[0]}
        recs.append(rec)
    print(f'case {i} done in {time.time() - t0:.1f}s: ' + ', '.join(
        f"{r['method']}:{'OK' if r.get('success') else 'x'} v={r.get('speed', np.nan):.2f} e={r.get('pos_err', np.nan):.3f}"
        for r in recs), flush=True)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenario', default='inair')
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--methods', default='B,S,F,Blat,Slat,F10,F10own')
    ap.add_argument('--tag', default='_flat')
    a = ap.parse_args()
    methods = a.methods.split(',')
    jobs = [(a.scenario, i, methods) for i in range(a.start, a.start + a.n)]
    path = os.path.join(os.path.dirname(__file__), '..', 'results', f'mc_{a.scenario}{a.tag}.json')
    allrecs = []
    with Pool(a.workers) as pool:
        for recs in pool.imap_unordered(run_case, jobs):
            allrecs += recs
            with open(path, 'w') as f:
                json.dump(allrecs, f, indent=0, default=float)


if __name__ == '__main__':
    main()
