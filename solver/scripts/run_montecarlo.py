"""Closed-loop Monte Carlo of guidance options A (flight code), B (recommended), C (3DOF + rate limits),
S (standard 6DOF SCvx baseline; e.g. --methods B,S --tag _scvx).

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/run_montecarlo.py --scenario inair --n 40 --workers 2
Writes results/mc_<scenario>.json (one record per run and method).
"""
import argparse
import json
import os
import sys
import time
import warnings
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.guidance import PlannerA, PlannerB, PlannerC, PlannerS, min_tf_B, min_tf_C, min_tf_3dof
from gtpl_guidance.sim6dof import simulate, SimOptions
from gtpl_guidance.rotations import R_to_quat, expm_so3

TARGET = np.array([0, 0, 1.5])
TF_MARGIN = 0.5


def draw_case(scenario, i):
    rng = np.random.default_rng(1000 + i)
    if scenario == 'inair':
        r0 = np.array([rng.uniform(-15, 15), rng.uniform(-15, 15), rng.uniform(40, 60)])
        v0 = np.array([rng.normal(0, 1.5), rng.normal(0, 1.5), rng.uniform(-6, -1)])
        tilt = np.radians(rng.uniform(0, 3))
        w0 = np.array([rng.normal(0, 0.03), rng.normal(0, 0.03), 0.0])
        m0 = rng.uniform(77, 80)
        target = TARGET.copy()
    else:  # pad hop: launched from the pad with upward speed, land at an offset spot
        r0 = np.array([0.0, 0.0, 1.5])
        v0 = np.array([rng.normal(0, 0.2), rng.normal(0, 0.2), rng.uniform(5.0, 6.0)])
        tilt = np.radians(rng.uniform(0, 1.5))
        w0 = np.array([rng.normal(0, 0.02), rng.normal(0, 0.02), 0.0])
        m0 = rng.uniform(78, 80)
        az = rng.uniform(0, 2 * np.pi)
        d = rng.uniform(0, 4)
        target = np.array([d * np.cos(az), d * np.sin(az), 1.5])
    az = rng.uniform(0, 2 * np.pi)
    R0 = expm_so3(tilt * np.array([np.cos(az), np.sin(az), 0.0]))
    wind_dir = rng.uniform(0, 2 * np.pi)
    wind = rng.uniform(0, 3)
    opts = SimOptions(wind=(wind * np.cos(wind_dir), wind * np.sin(wind_dir), 0.0), gust_sigma=0.5,
                      thrust_noise=0.02, isp_error=rng.normal(0, 0.05),
                      gimbal_bias=tuple(np.radians(rng.normal(0, 0.2, size=2))), seed=i)
    return r0, v0, R0, w0, m0, target, opts


def run_case(args):
    scenario, i, methods = args
    veh = default_vehicle()
    cfg = default_config(glide_slope=None) if scenario == 'hop' else default_config()
    r0, v0, R0, w0, m0, target, opts = draw_case(scenario, i)
    x0 = np.concatenate([r0, v0, R_to_quat(R0), w0, [m0]])
    recs = []
    t0 = time.time()
    tf3 = min_tf_3dof(r0, v0, m0, target, veh, cfg)
    tfB = tfC = None
    if 'B' in methods or 'S' in methods:
        tfB, _ = min_tf_B(r0, v0, m0, R0, w0, target, veh, cfg, lo=tf3)
    if 'C' in methods:
        tfC = min_tf_C(r0, v0, m0, target, veh, cfg, lo=tf3)
    for meth in methods:
        tm = time.time()
        if meth == 'A':
            pl = PlannerA(veh, target)
        elif meth == 'B':
            if tfB is None:
                recs.append(dict(case=i, method='B', failed='no feasible tf'))
                continue
            pl = PlannerB(veh, cfg, target, tfB + TF_MARGIN)
        elif meth == 'S':   # same problem and the same final time as B
            if tfB is None:
                recs.append(dict(case=i, method='S', failed='no feasible tf'))
                continue
            pl = PlannerS(veh, cfg, target, tfB + TF_MARGIN)
        else:
            if tfC is None:
                recs.append(dict(case=i, method='C', failed='no feasible tf'))
                continue
            pl = PlannerC(veh, cfg, target, tfC + TF_MARGIN)
        out = simulate(x0, target, pl, veh, opts)
        infos = out.pop('infos')
        if 'failed' in out:
            recs.append(dict(case=i, method=meth, failed=out['failed']))
            continue
        st = [inf.get('solve_time', np.nan) for inf in infos if inf.get('solve_time') is not None]
        wl = [inf.get('wall', np.nan) for inf in infos]
        rec = dict(case=i, method=meth, tf3=tf3, tfB=tfB, tfC=tfC, **out,
                   n_replans=len(infos), cert_rate=float(np.mean([bool(inf.get('cert')) for inf in infos])),
                   cert_first=bool(infos[0].get('cert')),
                   solve_mean=float(np.nanmean(st)) if st else None, solve_max=float(np.nanmax(st)) if st else None,
                   wall_mean=float(np.nanmean(wl)), wall_max=float(np.nanmax(wl)), sim_wall=time.time() - tm,
                   tf_ext=float(sum(inf.get('tf_ext', 0) or 0 for inf in infos)),
                   n_fallback=int(sum(bool(inf.get('continued')) or (inf.get('tf_ext') or 0) > 0 for inf in infos[1:])),
                   tight_min=float(min([inf.get('tight_min', 1.0) for inf in infos])),
                   plan_fuel0=infos[0].get('fuel_plan'))
        recs.append(rec)
    print(f'case {i} done in {time.time() - t0:.1f}s: ' + ', '.join(
        f"{r['method']}:{'OK' if r.get('success') else 'x'} v={r.get('speed', np.nan):.2f} e={r.get('pos_err', np.nan):.2f}"
        for r in recs), flush=True)
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scenario', default='inair')
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--methods', default='A,B,C')
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    methods = a.methods.split(',')
    jobs = [(a.scenario, i, methods) for i in range(a.start, a.start + a.n)]
    path = os.path.join(os.path.dirname(__file__), '..', 'results', f'mc_{a.scenario}{a.tag}.json')
    allrecs = []
    with Pool(min(a.workers, 2)) as pool:
        for recs in pool.imap_unordered(run_case, jobs):
            allrecs += recs
            with open(path, 'w') as f:
                json.dump(allrecs, f, indent=0, default=float)


if __name__ == '__main__':
    main()
