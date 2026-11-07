"""Vehicle and planner parameters for the GTPL lander.

Sources: context/vehicle.md (sim plant rocket_dynamics.rs, flight code). Units: SI, angles in radians.
World frame: +z up. Body frame: +z is the thrust axis (through the nose), engine gimbal below the CG.
"""
from dataclasses import dataclass, field, replace
import numpy as np

G0 = 9.80665


@dataclass
class Vehicle:
    """Physical vehicle (the 'plant')."""
    m_wet: float = 80.0
    m_dry: float = 55.88            # frame + tanks + TVC module (sim plant)
    isp: float = 180.0              # guidance value; the sim plant realises ~216 s
    T_min: float = 400.0            # N  (rho1)
    T_max: float = 1000.0           # N  (rho2)
    gimbal_max: float = np.radians(15.0)       # per-axis box limit
    gimbal_rate: float = np.radians(100.0)     # per-axis slew limit (flight clamp 2 deg / 20 ms)
    thrust_rate: float = 2000.0                # N/s (flight clamp 40 N / 20 ms)
    J_t: float = 63.6               # transverse inertia, wet (kg m^2)
    J_z: float = 3.74               # roll inertia
    L: float = 0.589                # gimbal pivot to CG (m), wet
    rcs_torque: float = 3.0         # N m roll torque (one valve pair)
    land_height: float = 1.5        # CG height when standing on the pad (flight target z)
    # mass-property table (mass, J_t, L) from context/vehicle.md §1, used by the simulator only
    mass_table: tuple = ((55.88, 40.2, 0.543), (60.88, 48.6, 0.581), (70.37, 51.7, 0.556), (79.88, 63.6, 0.589))

    @property
    def alpha(self):
        """Mass flow per newton of thrust, kg/(N s)."""
        return 1.0 / (self.isp * G0)

    def inertia_lever(self, m):
        """(J_t, L) at mass m, linear interpolation of the sim-plant table (simulator only)."""
        tab = np.array(self.mass_table)
        return float(np.interp(m, tab[:, 0], tab[:, 1])), float(np.interp(m, tab[:, 0], tab[:, 2]))


@dataclass
class PlannerConfig:
    """Constraint set used by every planner (A, B, C, D) plus planning margins.

    The planner deliberately keeps margins inside the physical limits so the tracking controller has authority left:
    throttle [T_min_plan, T_max_plan] inside [400, 1000] N, gimbal tan-angle tan(gimbal_plan) inside the 15 deg box,
    gimbal rate and throttle rate below the actuator slew limits.
    """
    T_min_plan: float = 440.0
    T_max_plan: float = 920.0
    gimbal_plan: float = np.radians(10.0)       # |T_x|, |T_y| <= tan(gimbal_plan) * T_axial
    gimbal_rate_plan: float = np.radians(60.0)  # used in the linear sufficient condition (claims N2)
    thrust_rate_plan: float = 1500.0            # N/s, sufficient condition on |dT| (claims N3)
    tilt_max: float = np.radians(20.0)          # body tilt from vertical along the path
    glide_slope: float = np.radians(10.0)       # min elevation angle seen from the target; None = off
    terminal_tilt_tol: float = np.radians(0.5)  # certificate tolerance on touchdown tilt
    v_max: float = 15.0                         # flight descent speed limit (3DOF baseline)
    N: int = 35                                 # nodes - 1
    substeps: int = 8                           # quadrature substeps per interval (B, certificate)


def default_vehicle():
    return Vehicle()


def default_config(**kw):
    return replace(PlannerConfig(), **kw)
