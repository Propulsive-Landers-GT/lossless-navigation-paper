"""Soundness stress test of planner F: many random problems, one SOCP each, every plan checked on a dense grid.

Draws initial states wider than the Monte Carlo (in-air and pad-hop), solves once with default references and once
with deliberately bad random references, and evaluates the exact flat map at 1201 instants. A sound restriction must
give zero violations of the planning limits (throttle range, gimbal cone, tilt) and of the boundary conditions,
whatever the references. Slew rates are not part of the guarantee and are only reported.

Usage: .venv/bin/python scripts/stress_flat.py [n]   -> results/stress_flat.json
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.fcg import FCG, PlanF
from gtpl_guidance.flat import FlatTrajectory
from gtpl_guidance.flatcert import check_limits
from gtpl_guidance.rotations import expm_so3

KEYS = ('throttle_plan', 'gimbal_plan', 'tilt', 'boundary', 'terminal')


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    veh = default_vehicle()
    rng = np.random.default_rng(2026)
    recs = []
    for i in range(n):
        hop = i % 3 == 2
        cfg = default_config(glide_slope=None) if hop else default_config()
        if hop:
            r0 = np.array([0.0, 0.0, 1.5])
            v0 = np.array([rng.normal(0, 0.5), rng.normal(0, 0.5), rng.uniform(3.0, 6.0)])
            d, az = rng.uniform(0, 5), rng.uniform(0, 2 * np.pi)
            target = np.array([d * np.cos(az), d * np.sin(az), 1.5])
            tf = rng.uniform(4.2, 6.0)
        else:
            r0 = np.array([rng.uniform(-25, 25), rng.uniform(-25, 25), rng.uniform(30, 70)])
            v0 = np.array([rng.normal(0, 3), rng.normal(0, 3), rng.uniform(-8, 0)])
            target = np.array([0.0, 0.0, 1.5])
            tf = rng.uniform(7.0, 11.0)
        az = rng.uniform(0, 2 * np.pi)
        R0 = expm_so3(np.radians(rng.uniform(0, 8)) * np.array([np.cos(az), np.sin(az), 0.0]))
        w0 = np.array([rng.normal(0, 0.08), rng.normal(0, 0.08), 0.0])
        m0 = rng.uniform(62, 80)
        S = int(rng.choice([8, 12, 16]))
        F = FCG(veh, cfg, S=S, soft_td=int(rng.integers(0, 2)))
        Tlat = rng.normal(0, 15, 2)
        for kind in ('default', 'random'):
            ref = None
            if kind == 'random':
                ref = F.default_ref(m0)
                ref.rho[:] = rng.normal(0, 0.3, S)
                ref.kap[:] = rng.normal(0, 0.3, S)
                ref.phi[:] = rng.uniform(5.5, 11.0, S)
            c, info = F.solve(r0, v0, m0, R0, w0, target, tf, ref=ref, T_lat0=Tlat)
            rec = dict(i=i, hop=hop, kind=kind, S=S, status=info['status'])
            if c is not None:
                p = PlanF(tf, FlatTrajectory(c, tf, F.eps, m0, veh.alpha), 'flyable', 0, 0, 0, 1, 0)
                ck = check_limits(p, veh, cfg, r0, v0, m0, R0, w0, target, n=1201, frame=False)
                rec.update(ok=bool(all(ck['checks'][k] for k in KEYS)), failed=[k for k in KEYS if not ck['checks'][k]],
                           T_min=ck['T_min'], T_max=ck['T_max'], gimbal=ck['gimbal_cone_max_deg'], tilt=ck['tilt_max_deg'],
                           gimbal_rate=ck['gimbal_rate_max_dps'], thrust_rate=ck['thrust_rate_max'],
                           slew_ok=bool(ck['checks']['gimbal_rate'] and ck['checks']['thrust_rate']))
            recs.append(rec)
    with open(os.path.join(os.path.dirname(__file__), '..', 'results', 'stress_flat.json'), 'w') as f:
        json.dump(recs, f, indent=0, default=float)
    for kind in ('default', 'random'):
        rr = [r for r in recs if r['kind'] == kind]
        ok = [r for r in rr if 'ok' in r]
        print(f"{kind} references: {len(rr)} problems, {len(ok)} feasible, {sum(not r['ok'] for r in ok)} with a planning-limit or "
              f"boundary violation; throttle in [{min(r['T_min'] for r in ok):.1f}, {max(r['T_max'] for r in ok):.1f}] N, "
              f"gimbal cone max {max(r['gimbal'] for r in ok):.2f} deg, tilt max {max(r['tilt'] for r in ok):.2f} deg; "
              f"slew check failed in {sum(not r['slew_ok'] for r in ok)} (gimbal rate max {max(r['gimbal_rate'] for r in ok):.0f} deg/s, "
              f"throttle rate max {max(r['thrust_rate'] for r in ok):.0f} N/s)")
        print('   violations:', [(r['i'], r['failed']) for r in ok if not r['ok']][:10])


if __name__ == '__main__':
    main()
