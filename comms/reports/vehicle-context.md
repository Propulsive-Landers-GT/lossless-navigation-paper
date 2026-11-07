# Vehicle-context report (summary of context/vehicle.md)

Vehicle is an N2O/paraffin HYBRID (repos say "monoprop"). No single parameter set exists; ranges below. Full citations in `context/vehicle.md`.

| Parameter | Central | Range / alternatives | Source |
|---|---|---|---|
| m_wet | 80 kg | 78 (mock), 79.88 (sim plant) | fsm/mod.rs:60; rocket_dynamics.rs:609 |
| m_dry | 50 kg (benchmarks) | 55.88 (plant), 58, 61 | state.rs:109; rocket_dynamics.rs:613; algorithms.rs:350 |
| propellant (main) | 19 kg physical | 30 kg in LCvx benchmarks | rocket_dynamics.rs:282,285 |
| rho1 (min thrust) | 400 N | 300 N (flight) | lossless.py:135; guidance.rs:25 |
| rho2 (max thrust) | 1000 N | 900, 1200 | guidance.rs:26; algorithms.rs:353 |
| rho1/rho2 | 0.40 | 0.30 to 0.444 | |
| alpha = 1/(Isp g0) | 5.66e-4 kg/(N s) (180 s) | 4.7e-4 (sim, 216 s); 6.4e-4 (mock 160 s) | lossless.py:134; fluid_dynamics.rs:101 |
| delta_gimbal | 15 deg per axis (box) | corner 21.2 deg | algorithms.rs:91; control.rs:161 |
| J_xx = J_yy (pitch/yaw) | 63.6 kg m^2 wet | 40.2 dry; MPC model uses 6.65 | derived from rocket_dynamics.rs:276-312, 618-663 |
| J_zz (roll) | 3.7 kg m^2 | 2.3 in MPC | same |
| lever arm L | 0.589 m wet | 0.543 dry; MPC uses 0.286 | rocket_dynamics.rs:286,419; mpc_crate.rs:209 |
| gimbal rate limit | 100 deg/s (2 deg per 20 ms clamp) | actuator model 86 deg/s unused; no accel limit | actuator.rs:34 |
| throttle slew | 2000 N/s | | actuator.rs:35 |
| max angular accel T sin(d) L / J | 0.96 rad/s^2 (wet, 400 N) | 2.40 (wet, 1000 N); 3.5 (dry, 1000 N); MPC believes 4.5 to 11 | derived |
| usable rate envelope | 0.3 to 0.5 rad/s | peak 0.5 to 1.0 rad/s bang-bang for 15 deg | derived |
| roll RCS | 3 N m, 0.8 rad/s^2 | placeholders | device_sim.rs:664-666 |
| typical tf | 7 s (50 m drop) | 11 to 12 s with 5 m/s cap | stored ZOH CSVs |
| profile | hover 50 m, 10 s, land at z=1.5 m, replan 1 Hz, MPC 50 Hz | | state.rs:48; autopilot.rs:287 |

Key findings for the proof effort:
- No attitude-rate limit exists in any guidance or MPC code. MPC discards the LCvx thrust direction (identity attitude reference).
- LCvx pointing cone is about inertial vertical, 15 deg, conflating gimbal and tilt.
- Stored ZOH solutions have thrust-direction jumps (14.8 deg to 0 deg in 24 ms; 180 deg azimuth flip), needing ~1e3 rad/s^2 vs plant 1 to 3.5.
- Stored solutions are not relaxation-tight in the min-thrust arc: m||u|| = 296 N while m sigma = 400 N.
- Inconsistencies: MPC inertia/lever arm are ~4.6x too agile vs the plant; python vs rust z0 sign; glide slope 0.05 deg is inactive; test data are LFS stubs.
