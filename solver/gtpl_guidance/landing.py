"""The GTPL landing algorithm: the one entry point.

    guide = LandingGuidance(target=[0, 0, 1.5])
    guide.update(t, x)            # x = [r(3), v(3), quaternion(4), body rate(3), mass]; call at up to 10 Hz
    ref = guide.reference(t)      # position, velocity, body axis, throttle, gimbal: what to track right now

What it does (LANDING-ALGORITHM.md; proof in math/10-landing-proof.md):
  1. first call: pick the time of flight, the smallest one for which the convex program is feasible plus a margin;
  2. every call: solve ONE convex program for the path of the centre of percussion from the current state to the pad;
  3. between calls: evaluate the closed-form flat map of that path to get the reference at any instant.
Every plan it accepts is a trajectory of the vehicle model within the planning limits at every instant (Theorem F).
If a solve is infeasible or fails the limit check, the previous plan stays in force.
"""
import numpy as np

from .params import default_vehicle, default_config
from .guidance import PlannerF, bisect_min_tf
from .fcg import FCG
from .rotations import quat_to_R


class LandingGuidance:
    def __init__(self, target, vehicle=None, config=None, margin=0.25, spans=16):
        self.target = np.asarray(target, float)
        self.veh = vehicle or default_vehicle()
        self.cfg = config or default_config()
        self.margin, self.spans = margin, spans
        self.planner = None
        self.tf_abs = None
        self.plan, self.plan_t0 = None, None

    # ------------------------------------------------------------------ step 1: time of flight
    def time_of_flight(self, x):
        """Smallest feasible time of flight from state x, plus the margin. None if no landing is found."""
        r, v, m = x[0:3], x[3:6], x[13]
        R, w = quat_to_R(x[6:10]), x[10:13]
        F = FCG(self.veh, self.cfg, S=self.spans)
        self.n_tf_solves = 0

        def feasible(tf):
            self.n_tf_solves += 1
            return F.solve(r, v, m, R, w, self.target, tf)[0] is not None
        tf = bisect_min_tf(feasible, 1.0, 3.0, tol=0.05, hi_max=40.0)   # doubles outward, then bisects
        return None if tf is None else tf + self.margin

    # ------------------------------------------------------------------ step 2: one convex program
    def update(self, t, x, actuators=(0.0, 0.0, None)):
        """Plan from state x at time t. actuators = (gimbal theta, gimbal phi, thrust) as currently deflected, so the
        plan starts from where the gimbal is. Returns True if a new plan was accepted."""
        ref, _ = self(t, x, None, actuators)
        return ref is not None

    def __call__(self, t, x, prev_ref, act=(0.0, 0.0, None)):
        """Same call signature as the other planners in guidance.py, for sim6dof.simulate."""
        if self.planner is None:
            tf = self.time_of_flight(x)
            if tf is None:
                return None, dict(t=t, method='F', status='no feasible time of flight', cert=False)
            self.tf_abs = t + tf
            self.planner = PlannerF(self.veh, self.cfg, self.target, self.tf_abs, S=self.spans)
        ref, info = self.planner(t, x, prev_ref, act)
        if ref is not None:
            self.plan, self.plan_t0, self.tf_abs = self.planner.last, self.planner.last_t0, self.planner.tf_abs
        return ref, info

    # ------------------------------------------------------------------ step 3: closed-form reference
    def reference(self, t):
        """What the vehicle should be doing at absolute time t according to the current plan."""
        if self.plan is None:
            raise RuntimeError('no plan yet: call update() first')
        e = self.plan.traj.eval(np.array([min(max(t - self.plan_t0, 0.0), self.plan.traj.tf)]))
        return dict(position=e['r'][0], velocity=e['v'][0], body_axis=e['b'][0], body_axis_rate=e['bd'][0],
                    throttle=float(e['T'][0]), gimbal_angle=float(np.arctan(e['gim_tan'][0])),
                    thrust_world=e['Ta'][0] * e['b'][0] + e['Tlat_w'][0], mass=float(e['m'][0]),
                    time_to_go=float(self.tf_abs - t))
