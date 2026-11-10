"""Open-loop replay of planner F plans: throttle and gimbal commands only, through the full nonlinear rigid body.

For the 8 in-air scenarios, from an upright start and from a tilted, rotating start, one SOCP is solved and its
commands are integrated through `dynamics.deriv` (quaternion attitude, depleting mass, centre of percussion fixed in
the body). No feedback. The landing error is then pure integration error. Writes results/replay_flat.json.

Usage: .venv/bin/python scripts/replay_flat.py
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
from gtpl_guidance.flatcert import replay
from gtpl_guidance.rotations import expm_so3, quat_to_R, tilt_of_R


def main():
    veh, cfg = default_vehicle(), default_config()
    here = os.path.dirname(__file__)
    F = FCG(veh, cfg, S=16)
    target = np.array([0, 0, 1.5])
    stored = json.load(open(os.path.join(here, '..', 'results', 'openloop.json')))
    R1, w1 = expm_so3(np.radians(3) * np.array([0.6, 0.8, 0])), np.array([0.03, -0.02, 0])
    out = []
    for row in stored:
        r0, v0 = np.array(row['r0'], float), np.array(row['v0'], float)
        tf = row['tfB']['tf'] + 0.5
        for R0, w0, tag in ((np.eye(3), np.zeros(3), 'upright, at rest'), (R1, w1, 'tilted 3 deg, rotating')):
            p = F.plan(r0, v0, 80.0, R0, w0, target, tf, refine=0)
            xf = replay(p.traj, veh, r0, v0, 80.0, R0, w0, model='cop')
            rec = dict(name=row['name'], start=tag, tf=tf, dr=float(np.linalg.norm(xf[:3] - target)),
                       dv=float(np.linalg.norm(xf[3:6])), tilt_deg=float(np.degrees(tilt_of_R(quat_to_R(xf[6:10])))))
            out.append(rec)
            print(f"{row['name'][:2]} {tag:24s} position {rec['dr'] * 1e9:7.2f} nm   velocity {rec['dv'] * 1e9:7.2f} nm/s", flush=True)
    with open(os.path.join(here, '..', 'results', 'replay_flat.json'), 'w') as f:
        json.dump(out, f, indent=1)
    print(f"max position error {max(r['dr'] for r in out) * 1e9:.1f} nm, max velocity error {max(r['dv'] for r in out) * 1e9:.1f} nm/s "
          f"over {len(out)} replays")


if __name__ == '__main__':
    main()
