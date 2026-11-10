# GTPL lander: vehicle and guidance-stack context for 5DOF/6DOF LCvx research

Scope: everything relevant to powered-descent guidance, read from the sibling GTPL repos (read-only).
Paths are relative to `/Users/aneesh/Documents/GitHub/GTPL/`. Citations are `path:line`.
Derived numbers (not in source) are marked **[derived]** with assumptions stated.
Coordinates: body +Z is the thrust axis (up through the nose), engine/gimbal at the bottom (-Z). World +Z is up.

## 0. Headline findings (read first)

1. **The vehicle is a hybrid (N2O / paraffin), not a monoprop.** Repos are named "monoprop" but the sim engine, fuel grain, wiki and club mission statement are hybrid (`wiki/README.md:25` "hybrid rocket"; `simulations/RocketSimulation/rust_rocket_sim/src/fluid_dynamics.rs:95-101` fuel grain + Isp(O/F) polynomial; `.../rocket_dynamics.rs:284-285` fuel grain 3 kg). Only the ground-system mock calls it monoprop (Isp 160 s, `ground-system/crates/gs-bridge/src/bin/gs-mock/physics.rs:15-16`).
2. **There is no single parameter set.** Dry mass is 50 / 55.88 / 58 / 61 kg, min thrust 300 / 400 N, max thrust 900 / 1000 / 1200 N, depending on file (Section 7).
3. **Min-throttle ratio** is ρ1/ρ2 = 0.30 (flight guidance), 0.40 (benchmarks, python), 0.444 (sim `algorithms.rs`). The vehicle can never hover at min thrust: hover needs T = m g = 548 to 784 N, and min thrust (300 or 400 N) only equals weight when m <= 30.6 or 40.8 kg **[derived]**.
4. **Guidance's 3DOF thrust direction is discarded by the tracker.** `generate_mpc_reference` keeps only |T| from the LCvx trajectory and sets the attitude reference to the identity quaternion with zero rate (`monoprop-flight-software/Lander/src/fsm/autopilot.rs:234-246`). The 15 deg "pointing cone" in LCvx is the only coupling to attitude, and it is about the inertial vertical, not about the body.
5. **Nothing in the stack limits attitude rate.** No explicit angular-rate or tilt-rate constraint in guidance or MPC; the only limits are the gimbal box (+-15 deg/axis), a gimbal step clamp (2 deg per 20 ms) and a thrust step clamp (40 N per 20 ms).
6. **LCvx trajectories contain thrust-direction jumps the vehicle cannot follow** (Section 5.5): tilt 14.8 deg -> 0 deg in 24 ms, and an azimuth flip of 180 deg, in the ZOH solutions in `guidance/LosslessConvexification/lossless_compare/output/`.
7. **The relaxation is not tight in the stored solutions:** delivered thrust m*||u|| is 296 N in the min-thrust arc although sigma*m = 400 N (Section 5.4).
8. **MPC plant/model mismatch:** controller uses I = diag(6.65, 6.65, 2.3), lever arm 0.286 m; the simulator plant has I_xx of 40 to 64 kg m^2 and lever arm 0.54 to 0.59 m. The controller thinks it has ~4.6x more angular acceleration than the plant (Section 4).
9. **The centre of percussion barely moves.** ε = I_xx/(m L) is 1.32 to 1.37 m across the whole mass table (Section 1). The recommended landing algorithm (`LANDING-ALGORITHM.md`, added 2026-11-10) relies on this.

## 1. Mass properties

Source of truth for the physical vehicle model: `simulations/RocketSimulation/rust_rocket_sim/src/rocket_dynamics.rs` (call it **sim/rocket_dynamics.rs**).

| Item | Value | Citation |
|---|---|---|
| Frame mass | 15.66 kg | sim/rocket_dynamics.rs:276 |
| N2 storage tank empty / N2 charge | 15.6 kg / 5.0 kg | :277-278 |
| N2O tank empty | 15.86 kg | :280 |
| N2O (liquid) | 16.0 kg | :282 |
| Pressurizing N2 in run tank (initial) | 0.0 kg | :281 |
| TVC module empty / paraffin grain | 8.76 kg / 3.0 kg | :284-285 |
| Dry mass (frame + 2 tanks + TVC module) | 55.88 kg | get_dry_mass, :613-614 **[derived sum]** |
| Wet mass | 79.88 kg | get_mass, :609-610 **[derived sum]** |
| Main-engine propellant (N2O + paraffin) | 19.0 kg | **[derived]** (the 5 kg N2 is RCS/pressurant) |
| Sim hands the FSM mass = 79.88, dry = 55.88 | | simulation.rs:92-93 |
| Flight FSM nominal wet / dry | 80 kg / 50 kg | monoprop-flight-software/Lander/src/fsm/mod.rs:60, Lander/src/state.rs:108-109 |
| Lossless config in sim `algorithms.rs` | dry 61 kg (~ 55.88 + 5 kg N2) | simulations/.../algorithms.rs:350 |
| Benchmarks / python / README | dry 50, fuel 30 (wet 80) | guidance/LosslessConvexification/lossless.py:131-133; lossless_compare/src/main.rs:34-35 |

**Centre of mass.** Offsets are measured from the frame CoM, +Z toward the nose. Gimbal pivot is at (-0.02, -0.01, -0.24) m from the frame CoM (sim/rocket_dynamics.rs:286); TVC module CoM is 0.25 m below the pivot (:287); N2 tank at z = +0.76 m (:279), N2O tank at z = +0.592 m (:283).
I re-implemented `get_com_offset`/`get_moi` (:618-663) in `/private/tmp/claude-501/-Users-aneesh--claude-spares-spare-Wsq0nM/62624014-ca2b-46e1-ab20-060a17497411/scratchpad/moi.py`; it reproduces the logged t=0 value (simulation.csv: com_z = 0.349 m, I_xx = 63.58). **[derived]**

| State | mass (kg) | CoM above frame CoM (m) | I_xx = I_yy (kg m^2) | I_zz (kg m^2) | gimbal lever arm L (m) |
|---|---|---|---|---|---|
| Wet (5 N2, 16 N2O, 3 paraffin) | 79.88 | 0.349 | 63.6 | 3.74 | 0.589 |
| After ~24 s (N2O 8.67, N2 2.8) | 70.37 | 0.316 | 51.7 | 3.72 | 0.556 |
| Propellant gone, N2 kept | 60.88 | 0.341 | 48.6 | 3.69 | 0.581 |
| Fully dry | 55.88 | 0.303 | 40.2 | 3.68 | 0.543 |

L = |gimbal_z - com_z| = 0.24 + com_z (sim/rocket_dynamics.rs:419 passes `frame_com_to_gimbal - com_offset` as the lever arm). The wet I_xx and CoM are confirmed by the logged run: `simulations/RocketSimulation/rust_rocket_sim/simulation.csv` (t=0: i_xx 63.58, com_z 0.349; t=24.37: i_xx 51.80, com_z 0.303).

**Inertia vs fuel.** Components: frame 6.65/6.65/2.3 (+ products 0.35, -0.02) (:289-291); N2 tank wet 1.0075 / dry 0.9275 about its own CoM (:292-297), interpolated by N2 fraction; N2O tank (dry) 1.31/1.31/0.21 (:299-302) plus the liquid; TVC module 0.84 wet / 0.64 dry (:304-309), interpolated by paraffin fraction. Total I_xx falls ~37% from wet to dry (63.6 -> 40.2) **[derived]**. The code does not add the liquid-N2O and pressurant cylinder inertias to the sum (computed at :644-646 but unused in `moi`, :657-661) and does not parallel-axis-shift the frame inertia to the combined CoM; both are small, but the wet I_xx is therefore approximate.
Slosh model exists (`sloshing_sim.rs`, `SloshModel::default()`), not needed for guidance.

**Centre of percussion (added 2026-11-10).** The landing algorithm (`LANDING-ALGORITHM.md`) plans the point a distance
ε = I_xx/(m L) above the CoM on the body axis, and assumes ε stays constant as propellant burns. From the table above **[derived]**:

| State | mass (kg) | ε = I_xx/(m L) (m) |
|---|---|---|
| Wet | 79.88 | 1.352 |
| After ~24 s | 70.37 | 1.321 |
| Propellant gone, N2 kept | 60.88 | 1.374 |
| Fully dry | 55.88 | 1.325 |

Over a descent (about 80 to 75 kg) ε moves by about 1 %; over the whole table by ±2 %. These come from the simulator's mass model,
which the paragraph above says is approximate. Measured mass properties of the real vehicle are needed before flight.

**Legacy, not the lander:** `monoprop-firmware/firmware/src/Loop/loopFirmware.cpp:44` (inertia 0.0094 kg m^2, m = 0.05 kg) and `simulations/DynamicsModel/FHL-DM/fhl-dyn-model.py:70-84` are small test-article models with TODO placeholders.

## 2. Propulsion

| Item | Value | Citation |
|---|---|---|
| Propellants | N2O (liquid, run-tank pressurized by GN2) / paraffin grain; hybrid | wiki/README.md:25; wiki/wiki/nasa-cea-web.md:48,70 ("1000N N2O(L)/Paraffin engine", O/F 7.1); sim/fluid_dynamics.rs:95-101 |
| Max thrust (design) | 1000 N | wiki/wiki/nasa-cea-web.md:48; guidance rust/python configs; sim `MPC::default` algorithms.rs:90 |
| Min thrust | 300 N (flight, sim log) or 400 N (python/benchmarks/sim algorithms.rs) | Lander/src/algorithms/guidance.rs:25; Lander/src/algorithms/control.rs:162; lossless.py:135; sim/algorithms.rs:89,352 |
| Observed thrust range in sim run | 299.9 to 998.96 N | `simulation.csv` thrust_x/y/z columns **[derived]** |
| rho1 / rho2 | 0.30 (300/1000) flight; 0.40 benchmarks; 0.444 (400/900) sim algorithms.rs | see above |
| alpha used by guidance | 1/(9.81*180) = 5.663e-4 kg/(N s) (Isp = 180 s) | lossless.py:134; Lander/.../guidance.rs:24; algorithms.rs:351; lossless_compare/src/main.rs:36 |
| Isp in the physical sim | polynomial in O/F: 1040.6 + 595.11x - 250.95x^2 + 60.909x^3 - 7.3421x^4 + 0.4167x^5 - 0.009x^6 [m/s] | sim/fluid_dynamics.rs:101; thrust = isp * mdot (:224) |
| Realized sim Isp | 2115 to 2142 m/s (216 to 218 s) at O/F 6.8 to 7.6 (T = 730 to 1000 N); 1948 m/s (198.6 s) at O/F 5.16 (T = 300 N) | `simulation.csv` isp, of_ratio, t = 20 s **[derived]** |
| alpha implied by sim | 4.7e-4 kg/(N s) (216 s) vs 5.66e-4 in guidance: guidance over-predicts mass flow by ~20% | **[derived]** |
| FSM mass-depletion model | mdot = T / (180 g) | Lander/src/fsm/mod.rs:374 |
| Throttle actuator (MTV valve) | angle 0 to 90 deg, unloaded 60 deg/s, stall torque 70, load 30 -> speed limit 60*(1-30/70) = 34.3 deg/s | sim/device_sim.rs:456-462, :517-522 (update: MTV at ~:480-515) |
| Valve angle vs thrust | 3.4 deg at 300 N, 15.4 deg at 999 N (from log) | `simulation.csv` valve_angle **[derived]** |
| Throttle slew implied by MTV | 700 N / (12 deg / 34.3 deg/s = 0.35 s) ~ 2000 N/s **[derived]** | |
| Throttle slew imposed in flight code | 40 N per MPC tick at 50 Hz = 2000 N/s | Lander/src/fsm/actuator.rs:35; Lander/src/fsm/mod.rs:28 (Scheduler 50 Hz) |
| Chamber pressure / feed | tank set pressure 6.5 MPa; throat 14.56 mm; fuel grain 155.9 mm long, OD 177 mm, rho 856 kg/m^3 | sim/fluid_dynamics.rs:95-108 |
| Propulsion design script (reference) | O/F up to 16 allowed, eta_c* = eta_Cf = 0.90, Pc = 40 bar, mdot_o = 0.45 kg/s | Propulsion/scripts/Engine Design Code Fixed Configuration.py:12,23,62-63 |
| Measured hot-fire data | Not usable: `Testing/**/*.tdms` are git-lfs pointer stubs (130-byte files) and `Propulsion/1000N/*` are empty placeholders | Testing/04102026/Scaled_RunData_2026-04-10_19-35-05.tdms ("version https://git-lfs..."); `wc -c Propulsion/1000N/*` = 1 byte |

Consequences for LCvx: because O/F changes with throttle and fuel regression, mdot is **not** exactly proportional to T (alpha varies roughly 4.7e-4 to 5.1e-4 over the throttle range in the sim, **[derived]**); the guidance model alpha*T is an approximation (5.66e-4). Hover thrust (548 to 784 N) is within [ρ1 T_max, T_max] at every mass.

## 3. TVC, actuators, RCS

| Item | Value | Citation |
|---|---|---|
| Gimbal limit | +-15 deg on each axis (box, not cone) | sim/algorithms.rs:91; Lander/src/algorithms/control.rs:161-166; Lander/src/state.rs:85; control/MPC/src/mpc_crate.rs:685-688; monoprop-prototype-software/teensy41-firmware/src/config.rs:45 |
| Max thrust-vector angle with both axes at limit | 21.2 deg (corner of box) **[derived]** | |
| LCvx pointing half-angle | 15 deg, same constant, against the **inertial** vertical | Lander/.../guidance.rs:27; lossless.rs:318 |
| Gimbal slew limit in flight code | 2 deg per 20 ms = 100 deg/s per axis | Lander/src/fsm/actuator.rs:34 (applies per MPC tick, Lander/src/fsm/mod.rs:407-414) |
| Gimbal actuator model in sim | Linear actuator: stroke 0.08 m, unloaded 0.14986 m/s, stall 102.06 N, lever arm 0.1 m -> unloaded 1.5 rad/s (86 deg/s) **[derived]** | sim/device_sim.rs:372-377, 563 |
| ...but it is not wired in | `get_target_position` returns 0 and the gimbal angles command[0], command[1] are applied directly to the thrust vector; no actuator dynamics, no angular acceleration limit | sim/device_sim.rs:583-605, :615-620 |
| Gimbal angular acceleration limit | none anywhere (legacy MATLAB has `gimbal_acceleration = 2 % TODO`) | simulations/DynamicsModel/monocopter_dynamics_model.m:75-77 |
| Experimental gimbal-rate MPC | control/MPC2: u = gimbal rates, bound 50 deg/s; lever arm d = 1.0 (placeholder) | control/MPC2/src/mpc_crate.rs:45-46,86,526 |
| Engine lever arm used by MPC model | d = 0.286 m ("TODO: make customizable") | control/MPC/src/mpc_crate.rs:209 |
| Lever arm of the sim plant | 0.543 to 0.589 m (Section 1) | sim/rocket_dynamics.rs:419 |
| Torque on the plant | tau = (r_gimbal - r_com) x F_thrust (+ reaction term from engine inertia, `engine_inertia` 8 to 3 kg m^2 are placeholders "TODO fix these values") | sim/device_sim.rs:557-566, 574-606 |
| RCS (roll only) | N2 cold gas, 10 N per thruster, arm 0.15 m, torque per valve pair = 2*10*0.15 = 3 N m, N2 use 0.1 kg/s per valve; placeholders "TODO update" | sim/device_sim.rs:664-666, 704; |
| Roll acceleration | 3 / 3.74 = 0.80 rad/s^2 (wet) **[derived]** | |
| Roll controller | bang-bang with dead band, 10 Hz, kp 15.35, kd 9.69, fire threshold 1.5 | Lander/src/algorithms/rcs.rs:17-25 |
| Flight tilt termination | max_tilt 30 deg (but checked on first Euler angle, not true tilt, see code note) | Lander/src/state.rs:50; Lander/src/fsm/mod.rs:497-505 |
| Sim "exceeded angle" flag | tilt > 15 deg (cos < 0.9659) | simulations/.../simulation.rs:167-172 |
| MPC tuner targets | max tilt 10 deg soft penalty (hard stop 25 deg), descent rate < 8 m/s, touchdown |vz| < 3 m/s | simulations/.../mpc_tuning.rs:245,307-314,299-303 |

Roll does not alter thrust direction (the vehicle is axisymmetric about the thrust axis in all models), which supports the 5DOF reduction.

## 4. Achievable angular acceleration and rate envelope (pitch/yaw) **[derived]**

Model: rigid body, small gimbal angle delta, lateral thrust component T sin(delta) acting at lever arm L below the CoM:

    alpha_max(T) = T sin(delta_max) L / I_xx,  delta_max = 15 deg, sin = 0.2588.

Assumptions: thrust magnitude = full T, gimbal at its mechanical limit on one axis (the other axis at 0), thrust axis aligned with the body axis, no gyroscopic coupling (I_zz small, omega_z ~ 0), no slosh, no actuator lag, no aerodynamic or ground effect, CoM and I at the states of Section 1, and the engine reaction torque (engine inertia times gimbal acceleration) ignored.

| Case | T (N) | L (m) | I_xx (kg m^2) | tau_max (N m) | alpha_max (rad/s^2) |
|---|---|---|---|---|---|
| Plant, wet, rho1 = 0.4 | 400 | 0.589 | 63.6 | 61.0 | **0.96** |
| Plant, wet, flight min | 300 | 0.589 | 63.6 | 45.7 | 0.72 |
| Plant, wet, max | 1000 | 0.589 | 63.6 | 152.4 | **2.40** |
| Plant, mid-burn, 700 N | 700 | 0.556 | 51.7 | 100.7 | 1.95 |
| Plant, dry, 400 N | 400 | 0.543 | 40.2 | 56.2 | 1.40 |
| Plant, dry, max | 1000 | 0.543 | 40.2 | 140.5 | **3.50** |
| MPC internal model, 300 N | 300 | 0.286 | 6.65 | 22.2 | 3.34 |
| MPC internal model, 400 N | 400 | 0.286 | 6.65 | 29.6 | 4.45 |
| MPC internal model, 1000 N | 1000 | 0.286 | 6.65 | 74.0 | **11.1** |

So the true envelope is alpha_max ~ 0.7 to 3.5 rad/s^2 (0.96 wet/ρ1 .. 2.4 wet/max is the pessimistic range); the MPC model overestimates by ~4.6x. Note torque and lateral force are the same gimbal action: at 1000 N the lateral acceleration is T sin(delta)/m = 3.2 to 4.3 m/s^2 for 80 to 60 kg.

Rest-to-rest rotation by Delta (bang-bang, gimbal alternately at +-limit): t = 2 sqrt(Delta/alpha), omega_peak = sqrt(alpha Delta).

| alpha (rad/s^2) | time for 15 deg | peak omega |
|---|---|---|
| 1.0 (wet, ρ1) | 1.02 s | 0.51 rad/s = 29 deg/s |
| 2.4 (wet, max T) | 0.66 s | 0.79 rad/s = 45 deg/s |
| 3.5 (dry, max T) | 0.55 s | 0.96 rad/s = 55 deg/s |

Realistic pitch/yaw rate envelope: **|omega| of about 0.3 to 0.5 rad/s sustained (17 to 29 deg/s) and |omega_dot| <= 1 (conservative) to 2.4 rad/s^2**, since a 50% derating is needed for a real controller that also has to stop the rotation. The realized rates in the logged MPC-in-the-loop sim are far lower: max |gyro| 0.045, 0.143, 0.019 rad/s (x, y, z) and max tilt 7.0 deg over a 24 s ascent-phase run (`simulations/.../flight_data.csv`, **[derived]**); angular rate peaks are tracked by the MPC cost, not constrained.

Explicit attitude-rate or acceleration limits in controller code: **none**. Closest: MPC cost weights on omega (diag 100 or 500 on wx, wy; `Lander/src/algorithms/control.rs:79,89`, descent tuning 11491 on wx,wy :272), quaternion weights on (qx,qy) (6000 to 742900), the gimbal box, and the FSM 2 deg/tick clamp.

## 5. Existing guidance stack

### 5.1 Problem solved by `guidance/LosslessConvexification`

Python (`lossless.py`, identical to `python_imp/lossless.py`) and Rust (`rust_lossless/src/lossless.rs`) solve the same family: fixed-time (time searched outside the solve), min-fuel soft landing, 3DOF point mass in a flat-earth frame (g = 9.80665 at lossless.py:26; 9.81 at lossless.rs:5).

* **Variables** (per node k = 0..N): position x, velocity v, log mass w = ln m, per step: acceleration-like thrust u (thrust/mass) and slack sigma (lossless.py:51-55; lossless.rs:171-181).
* **Dynamics** (explicit Euler, called "ZOH"): x_{k+1} = x_k + dt v_k, v_{k+1} = v_k + dt (u_k + g), w_{k+1} = w_k - dt alpha sigma_k (lossless.py:76-80; lossless.rs:235-289). Note there is no 0.5 dt^2 term in position, so "ZOH" is a misnomer; it is forward Euler.
* **Boundary**: x_0, v_0 given, w_0 = ln(m_dry + fuel); x_N = landing point, v_N = 0, w_N >= ln m_dry (lossless.py:60-71; lossless.rs:194-312, 526-531). There is no attitude or rate state, no terminal attitude, no terminal tilt constraint.
* **Thrust magnitude** ||u_k|| <= sigma_k (lossless.py:85; lossless.rs:357-375).
* **Thrust bounds (the min throttle)**: rho1 e^{-w} <= sigma <= rho2 e^{-w}, with e^{-w} linearized about z0 = ln(m0 - alpha rho2 dt k) (reference mass trajectory = full-throttle burn) (lossless.rs:327-355). Only the first-order Taylor is used for the lower bound; the comment at lossless.rs:326 says so. The reference mass trajectory is therefore an extreme (max-burn) trajectory, accurate for the sigma_max constraint and loose for rho1 away from that trajectory.
* **Pointing constraint**: YES. ||u_k - sigma_k d|| <= sigma_k sin(theta), d = `pointing_direction` = (0,0,1) **in the inertial frame**, theta = `tvc_range_rad` = 15 deg (lossless.py:91-94; lossless.rs:377-399). This is a convex cone constraint (ball around sigma d), a 15 deg bound on the angle between the thrust vector and inertial vertical. The code uses the TVC range as the limit on the whole thrust-direction tilt, conflating gimbal range and vehicle tilt.
* **Speed limit**: ||v_k|| <= v_max (lossless.py:96-98; lossless.rs:445-458). v_max = 5 m/s (benchmarks, python), 50 m/s (flight ascent) or 15 m/s (flight descent) (Lander/src/fsm/autopilot.rs:264,290).
* **Glide slope**: Rust only, two-sided corridor, ||(x_k - a_xy)|| <= |z_k - a_z|/tan(gamma) from both endpoints (lossless.rs:462-524, README "Glide Slope Constraint"). The Python one-sided cone is commented out (lossless.py:100-104). gamma = 5 deg README, 10 deg `lossless_compare/src/main.rs:67`, **0.05 deg in flight and sim** (Lander/.../guidance.rs:32; sim/algorithms.rs:359) which, with tan floored at 1e-6, is an almost horizontal cone and therefore effectively **inactive**. `rust_lossless/src/main.rs:35` uses 1e-7 deg for the same effect.
* **Cost**: min sum sigma_k dt, i.e. min fuel (lossless.py:107; lossless.rs:537-545).
* **Solvers**: Python cvxpy + ECOS (lossless.py:110); Rust Clarabel `DefaultSolver` (lossless.rs:561). SOCP.
* **Time of flight**: not optimized inside the SOCP. `solve()` (lossless.rs:745-860) sets t_min = m_dry |v0| / rho2 and t_max = fuel / (alpha rho1) (:756-757), scans N upward on a coarse dt (0.5 s flight, 0.05 s benchmark) until the first feasible solve, then re-solves with a fine dt (0.2 s flight / 0.025 s), searching N downward from the coarse N (lossless.rs:807-838). Result: approximately the shortest feasible tf, not the minimum-fuel tf. Default timeout 3 s (:144).
* **Chebyshev variant**: `chebyshev_lossless.rs` is incomplete (README: "mostly a copy ... with TODO comments"); not used in flight.

Python/Rust discrepancies (the README calls the Python "known to be correct", but): z0 uses `m0 + alpha rho2 dt k` in Python (lossless.py:83) versus `m0 - alpha rho2 dt k` in Rust (lossless.rs:327); the Python lower bound has a typo `(w - z0**2)/2` (:86) instead of (w-z0)^2/2 and is not even convex as written; Python includes a quadratic term the Rust version deliberately dropped.

### 5.2 How the flight code uses it (`monoprop-flight-software/Lander/src/`)

* `algorithms/guidance.rs:20-78` wraps `rust_lossless::LosslessSolver`: dry 61, alpha 1/(9.81*180), rho1 300, rho2 1000, v_max 50, tvc 15 deg, coarse/fine dt 0.5/0.2, glide 0.05 deg (both cones). `Autopilot::new` overrides dry_mass = 50, rho2 = 1000, v_max 15 (`fsm/autopilot.rs:21-23`), then each solve calls `configure(50 or 15, 300, vehicle_state.dry_mass)` (autopilot.rs:264,290), so the effective values are rho1 = 300, rho2 = 1000, dry mass = whatever the navigator reports (50 by default, `state.rs:109`, `navigator.rs:107`; 55.88 in the sim, `simulation.rs:93`).
* Guidance runs at 1 Hz (`Scheduler::new(500.0, 1.0, 50.0)`, fsm/mod.rs:28; call at :400-403), re-solving from the current estimated state every second (receding replan), so trajectories are repeatedly re-anchored.
* Phases: Ascent to goal (0, 0, hover_altitude = 50 m) (`fsm/mod.rs:30`, `state.rs:48`), Hover 10 s (`state.rs:49`; no guidance), Descent to landing point (0, 0, 1.5 m) (`autopilot.rs:287`; "0.5 m up to theoretical rocket center", git log 2026-08-06). Touchdown detection: z <= 0.1 and speed < 0.2 (fsm/mod.rs:316).
* Mass bookkeeping: m_dot = T/(180 g), floor at 50 kg (fsm/mod.rs:372-376).

### 5.3 How the 6DOF MPC tracks it

* Controller: nonlinear MPC, 13-state [pos, quat(x,y,z,w), vel, omega], 3 controls [gimbal_theta, gimbal_phi, thrust], horizon 10 steps of 0.2 s = 2.0 s, update 50 Hz, OpEn/PANOC solver (Lander/src/algorithms/control.rs:70-93, 109-114; Lander/.../fsm/mod.rs:28). The `MPC` crate is `control/MPC` (git dependency; `control/MPC/src/mpc_crate.rs`). `simulations/.../algorithms.rs` contains an older copy of the MPC/Lossless/RCS wrappers (400-1000 N, 0.2 s, 10 steps) which `simulation.rs` does not appear to drive (it uses `self.fsm`).
* Internal model: rigid body, thrust vector tx = sin(th) cos(ph), ty = sin(ph), tz = cos(th) cos(ph) times T; torque = r x F with r = (0,0,-d), d = 0.286 m; **fixed inertia (6.65, 6.65, 2.3)** (control.rs:156-159 passed to `dynamics`; mpc_crate.rs:147-232). Gimbal angles are instantaneous controls, no gimbal dynamics. Position uses 0.5 dt^2 integration, attitude via quaternion integration (mpc_crate.rs:236-270).
* Constraints: gimbal box +-15 deg per axis and thrust [300, max] (control.rs:161-166; mpc_crate.rs:680-714). Max thrust 1200 (control.rs:102) or 1000 (autopilot.rs:25). No state constraints, no rate limits.
* Reference built from the LCvx trajectory by linear interpolation of position and velocity only; **attitude reference = identity quaternion, omega reference = 0, uref = [0, 0, ||u|| m]** (autopilot.rs:176-257, esp. 234-246). The lateral thrust components in the LCvx solution are thrown away; the MPC decides how to tilt to follow x, y, vx, vy. After the trajectory ends it holds the endpoint with hover thrust (autopilot.rs:191-200).
* Output conditioning: gimbal step clamp 2 deg and thrust step clamp 40 N per 20 ms (actuator.rs:34-44); roll by separate RCS bang-bang (rcs.rs).
* Tuning commentary: descent weights are genetic-algorithm-tuned (`control.rs:267-281`, `mpc_tuning.rs`), with an explicit preference for upright attitude ("PRIORITIZE UPRIGHT", mpc_tuning.rs:38) and soft tilt penalty beyond 10 deg (mpc_tuning.rs:307-310).

### 5.4 Observed relaxation behaviour (potentially important for the research)

In the stored "truth" ZOH solutions (`guidance/LosslessConvexification/lossless_compare/output/direct_descent/long/zoh/trajectory_zoh_direct_descent_long_1.csv`; 50 m straight drop, dry 50, fuel 30, rho = 400/1000, columns `mass,ux,uy,uz,sigma,thrust_force`):

* Rows 0 to ~141 (first ~1.75 s of tf = 7.01 s): sigma*m = 400.0 N (lower bound active) but ||u||*m = **296.5 N**, i.e. ||u|| < sigma. The delivered thrust is 26% below the claimed min thrust; relaxation is **not tight** there.
* Rows 200 onward: sigma*m = ||u||*m = 999.9 N (max thrust, tight).
* Same in the offset cases (min delivered 319 N / 312 N).
* The flight reference path uses ||u|| m (autopilot.rs:234), i.e. 296 N which the MPC then clips to its 300 N floor; the pad-bound solution is therefore not the one that would respect rho1 in the original nonconvex problem.

Caveat: I did not rerun the solver; this is read from stored CSVs produced by an unknown solver revision, but the pattern is the same across all stored runs (`Tmin` 296 to 319 N).

### 5.5 Where the 3DOF trajectory demands faster thrust rotation than the vehicle can do

Evidence computed from stored ZOH trajectories (`lossless_compare/output/*/long/zoh/*.csv`, tf and dt from `max_thrust_rate_change.csv`; direction = (ux,uy,uz)/||u||) **[derived]**:

| Case | tf (s) | Behaviour of thrust direction | Required rate/accel |
|---|---|---|---|
| Direct descent (x0 = 0,0,50) | 7.01 | purely vertical, tilt 0 | none |
| Offset descent (x0 = 10,20,50) | 7.23 | tilt 10 -> 15 deg (t ~ 2.5 s, saturated at the cone for ~1 s) -> 0.8 deg (t ~ 4 s) -> 13 deg at touchdown | peak direction rate 26 to 31 deg/s (0.46 to 0.55 rad/s) over 0.25 s; needs ~1 rad/s^2 for 1 s swings: borderline at wet/ρ1 (alpha 0.96) |
| Offset limited-speed (v_max = 5), 11.975 s | 11.98 | tilt 14.8 -> 11.5 -> **0 deg within 24 ms at t = 1.33 s**; 1.2 -> 14.3 deg in 24 ms at t = 10.45 s; 14.9 -> 3.2 deg in 36 ms at t = 10.9 s; **azimuth flip -117 -> +63 deg at t = 10.93 s** | instantaneous direction rate up to 922 deg/s (0.0125 s samples); 119 deg/s averaged over 0.25 s; a 15 deg step in 0.25 s needs alpha = 4 Delta/t^2 ~ 17 rad/s^2, in 24 ms ~ 1800 rad/s^2, versus a plant limit of 1 to 3.5 |

Throttle: stored solutions are bang-bang (400 -> 1000 N steps). `max_thrust_rate_change.csv` (rust_lossless/ and lossless_compare/output/) reports peak |dT/dt| from 1.3e3 N/s (dt = 0.5 s) up to 1.6e5 N/s (dt = 0.0125 s); the flight clamp is 2000 N/s (actuator.rs:35) and the MTV implies ~2000 N/s, so step throttle changes take ~0.3 s in reality **[derived]**. A script `compute_max_thrust_rate_change.py` and git message "thrust rate plot" (guidance repo, 2026-02-27) show the team looked at thrust-rate, but there is **no analogous check on thrust-direction rate**, and no comment or issue about attitude rate versus the pointing cone. Relevant git-log notes: "infeasibilities exist when end constraints are applied" (guidance, 2025-11-24); "Tuning to reduce velocity error and tilts" (flight software, 2026-08-06).

Plain statements: (a) flight tracking is saved only because the MPC ignores the lateral thrust profile (Section 5.3) and the flight-software solves a flat glide slope (inactive) so trajectories seldom use the full cone; (b) a vertical-descent benchmark never uses the pointing constraint at all, so existing benchmarks mostly do not exercise the 5DOF issue.

## 6. Typical mission profile numbers

| Quantity | Value | Source |
|---|---|---|
| Hover altitude (ascent target) | 50 m (1 to 200 m allowed) | Lander/src/fsm/mod.rs:30; state.rs:48,65 |
| Hover duration | 10 s (0 to 120) | state.rs:49,66 |
| Descent landing target | (0, 0, 1.5 m) (CoM height at touchdown) | autopilot.rs:287 |
| Max speed in guidance | ascent 50 m/s (configure) ; descent 15 m/s ; benchmarks 5 m/s | autopilot.rs:264,290; lossless_compare/src/main.rs:28 |
| 50 m descent from rest, v_max inactive | tf = 7.01 s; peak |vz| 10.7 m/s; propellant 3.17 kg (79.99 -> 76.83 kg); ~1.75 s at min thrust, then ~5.3 s at 1000 N | direct_descent CSV, [derived] |
| 50 m descent, v_max = 5 m/s | tf = 11.1 s, 5.8 kg (80 -> 74.19) | direct_limited_descent, [derived] |
| 10 m, 20 m lateral offset added | tf = 7.23 s (unlimited), 11.975 s (v_max = 5) | `max_thrust_rate_change.csv` |
| Sim ascent log | 24.4 s, thrust 300 to 999 N, N2O 16 -> 8.67 kg, tilt <= 7 deg | simulation.csv, flight_data.csv |
| Hover thrust | T = m g = 548 to 784 N | **[derived]** |
| MPC tuner scenario | descent from hover start; success needs z <= 1.5 m, |vz| <= 3 m/s at touchdown, descent rate < 8 m/s | mpc_tuning.rs:239,299-314 |
| Guidance replan | 1 Hz | fsm/mod.rs:28,400-403 |
| MPC | 50 Hz, 10 x 0.2 s | control.rs:70-73; fsm/mod.rs:28 |
| Operator/hover tilt abort | 30 deg (FSM), 15 deg (sim flag) | state.rs:50; simulation.rs:170 |

Measured hot-fire/test data (Testing/) could not be used (git-lfs pointers); the 1000 N engine design inputs are in `Propulsion/scripts/` and the wiki.

## 7. Inconsistencies between repos

| # | Item | Values and where |
|---|---|---|
| 1 | Propellant type | "monoprop" in repo names and ground-system mock (Isp ~160 s, physics.rs:15-16) versus N2O/paraffin hybrid in wiki and sim |
| 2 | Dry mass | 50 (python, benchmarks, FSM `state.rs:109`, `Autopilot::new`), 55.88 (sim plant, rocket_dynamics.rs:613), 58 (mock, physics.rs:11), 61 (sim algorithms.rs:350; Lossless::new guidance.rs:23) |
| 3 | Wet mass | 80 (FSM/MPC), 79.88 (sim plant), 78 (mock) |
| 4 | Main propellant | 30 kg in all LCvx benchmarks versus 19 kg physical (N2O 16 + paraffin 3); 24 kg if N2 is counted (sim hands dry 55.88) |
| 5 | Thrust bounds | 400/1000 (python, benchmarks, README), 400/900 (sim algorithms.rs:352-353), 300/1000 (flight guidance), MPC 300/1200 (control.rs:101-102) overridden to 300/1000 (autopilot.rs:25); mock max 1200 (physics.rs:12); sim plant log 300 to 999 N |
| 6 | rho1/rho2 | 0.30, 0.40, 0.444 |
| 7 | alpha / Isp | 180 s (guidance, FSM) versus 216 to 218 s (sim plant, O/F ~7; 198.6 s at 300 N) versus 160 s (mock) |
| 8 | MPC inertia and lever arm | MPC model I = 6.65/6.65/2.3, d = 0.286 m (control.rs:156-159, mpc_crate.rs:209) versus plant I_xx 40 to 64, L = 0.54 to 0.59 m (Section 1); MPC2 uses d = 1.0; `get_moi_mpc` (full plant inertia) exists but is only called in `old_main.rs:162` |
| 9 | Gimbal dynamics | 100 deg/s clamp in FSM, actuator model (86 deg/s) unused, MATLAB legacy "gimbal_speed = 5 TODO", MPC2 50 deg/s |
| 10 | Glide slope | 0.05 deg (flight, sim) i.e. inactive; 5 deg README; 10 deg compare; 1e-7 deg rust main |
| 11 | v_max | 5 m/s (benchmarks), 15 and 50 (flight), 5.0 (sim algorithms.rs:348) |
| 12 | Python vs Rust LCvx | sign of mass-reference z0, quadratic lower-bound typo (Section 5.1); g = 9.80665 versus 9.81 |
| 13 | Tilt check | FSM termination uses first Euler angle, not true tilt (fsm/mod.rs:497-505, acknowledged in comment) |
| 14 | RCS | all values labelled TODO placeholders (device_sim.rs:661-663) |
| 15 | Test data | LFS stubs only; `Propulsion/1000N` files are 1 byte |
| 16 | Legacy/small-scale models | `monoprop-firmware`, `DynamicsModel/FHL-DM`, `monoprop-prototype-software` (quad/ESC drone) describe 0.05 to few-kg test articles, not the lander |

## 8. Parameters recommended for research (with ranges)

See `comms/reports/vehicle-context.md` for the table. Central values: m_wet = 80, m_dry = 50 (benchmark) or 55.88 (physical), rho1 = 400 N, rho2 = 1000 N (rho1/rho2 = 0.4; 0.3 to 0.444 range), alpha = 5.66e-4 kg/(N s) (Isp 180 s; sim 216 s gives 4.7e-4), delta = 15 deg, J = 40 to 64 kg m^2 (pitch/yaw), L = 0.54 to 0.59 m, alpha_max = 0.96 to 3.5 rad/s^2, tf = 7 s (unconstrained 50 m drop) to 12 s (5 m/s cap).
