"""The landing algorithm on one descent: plan, print the plan, fly it closed loop with disturbances.

Usage: OMP_NUM_THREADS=1 .venv/bin/python scripts/example_landing.py
"""
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
warnings.filterwarnings('ignore')

from gtpl_guidance.landing import LandingGuidance
from gtpl_guidance.sim6dof import simulate, SimOptions

target = np.array([0.0, 0.0, 1.5])                       # CG height when standing on the pad
# state: position [m], velocity [m/s], quaternion (upright), body rate [rad/s], mass [kg]
x0 = np.array([10.0, 20.0, 50.0, 0.0, 0.0, -3.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 79.0])

guide = LandingGuidance(target)
guide.update(0.0, x0)
p = guide.plan
print(f'time of flight {p.tf:.2f} s, planned fuel {p.fuel:.3f} kg, {p.n_solves} convex program, '
      f'{1e3 * p.solve_time:.0f} ms in the solver\n')
print('  t [s]   CG position [m]            tilt [deg]  throttle [N]  gimbal [deg]')
for t in np.linspace(0.0, p.tf, 9):
    r = guide.reference(t)
    tilt = np.degrees(np.arccos(r['body_axis'][2]))
    print(f"  {t:5.2f}   ({r['position'][0]:6.2f}, {r['position'][1]:6.2f}, {r['position'][2]:6.2f})   {tilt:6.2f}      "
          f"{r['throttle']:6.1f}       {np.degrees(r['gimbal_angle']):5.2f}")

# closed loop: wind, gusts, thrust noise, 5 % Isp error, gimbal misalignment; replans every 0.1 s, each plan applied
# only after its solver time has elapsed
opts = SimOptions(wind=(2.0, -1.0, 0.0), gust_sigma=0.5, thrust_noise=0.02, isp_error=0.05,
                  gimbal_bias=(0.003, -0.002), seed=3, replan_dt=0.1, t_lock=0.6, latency=True)
out = simulate(x0, target, LandingGuidance(target), guide.veh, opts)
print(f"\nclosed loop: touchdown {100 * out['pos_err']:.1f} cm from the target at {out['speed']:.2f} m/s, tilted "
      f"{out['tilt_deg']:.2f} deg, fuel {out['fuel']:.2f} kg, {len(out['infos'])} plans")
