# Brief: VEHICLE-CONTEXT agent

You are the VEHICLE-CONTEXT agent in a multi-agent research project. Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research (read README.md and comms/BOARD.md first). Save this brief verbatim to comms/briefs/vehicle-context.md first.

The GTPL club repos are cloned (and up to date) as sibling folders in /Users/aneesh/Documents/GitHub/GTPL (simulations, control, guidance, monoprop-flight-software, monoprop-prototype-software, Propulsion, Testing, wiki, monoprop-firmware, etc.). Read-only: do NOT modify any of those repos.

Task: produce context/vehicle.md documenting everything relevant to powered-descent guidance for the monoprop lander, with file:line citations for every number:
1. Mass properties: wet/dry mass, propellant mass, moments of inertia (and how they vary with fuel), CG location, engine/gimbal lever arm.
2. Propulsion: min/max thrust (the min-throttle ratio matters a lot), Isp or mass-flow constant α = 1/(Isp g0), throttle response/rate limits, propellant type.
3. TVC: gimbal limits (15° found in simulations/RocketSimulation/rust_rocket_sim/src/algorithms.rs), gimbal actuator rate/acceleration limits, actuator lever arms; RCS (roll) capability.
4. Derive the achievable body angular acceleration and a realistic angular-rate envelope for pitch/yaw: max torque = thrust × sin(gimbal) × lever arm, divided by inertia, at min and max thrust; also any explicit attitude-rate limits in the MPC/controller. State assumptions.
5. The existing guidance stack: what problem guidance/LosslessConvexification (python_imp, rust_lossless, lossless.py) actually solves (constraints, cost, glide slope, pointing constraint?, discretization, solver), how monoprop-flight-software/Lander/src/algorithms/guidance.rs uses it, and how the 6DOF MPC in simulations/control tracks it. Note any places where the 3DOF trajectory demands thrust-direction changes faster than the vehicle can rotate, or any comments/issues about that.
6. Typical mission profile numbers: descent altitude, velocities, burn times (from sims, Testing data, wiki).
Also write comms/reports/vehicle-context.md (≤1 page summary with a parameter table: m_wet, m_dry, ρ1, ρ2, α, δ_gimbal, J, lever arm, max angular accel, typical tf). Flag inconsistencies between repos. Return the parameter table in your final message.
