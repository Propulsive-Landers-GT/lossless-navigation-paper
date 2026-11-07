# Porting planner B to `rust_lossless` and the flight software

This is a plan only. Sibling repositories were read, never modified. Changes to the existing GTPL repos must go on
feature branches and land through PRs that the team reviews.

## 1. What has to change, and where

| Today (`context/vehicle.md` §5) | With planner B |
|---|---|
| `rust_lossless::LosslessSolver::solve_at_current_time` builds one SOCP: 3DOF, forward Euler, 15° pointing cone about vertical | Keep it **unchanged** as the warm start and t_f bracket. Add a module `aacg.rs` holding B's two SOCP builders and the loop. |
| `LosslessSolver::solve` scans t_f for the *shortest feasible* 3DOF time, which is physically infeasible because of the lossy min-thrust arc | Pick t_f once, during the 10 s hover: bisection on B's certified status starting from the 3DOF minimum, plus a 0.5 s margin. Then fly a fixed absolute touchdown time and shrink the horizon at each 1 Hz replan. |
| `autopilot.rs::generate_mpc_reference` keeps only \|T\| and sets the attitude reference to identity, with ω_ref = 0 | Pass B's full reference: r, v, quaternion, ω, and the feed-forward (axial thrust and gimbal angles). The MPC then tracks a dynamically consistent trajectory. |
| MPC internal model: I = 6.65 kg m², lever arm d = 0.286 m (`control.rs`, `mpc_crate.rs:209`) | **Fix first, whatever guidance is used.** The plant has J_t = 40–64 kg m² and L = 0.54–0.59 m. Use `get_moi_mpc` / the mass table, as B does. The current model overestimates angular authority by about 4.6×. |
| No attitude-rate, gimbal-rate or throttle-rate constraints in guidance | B enforces gimbal ≤ 10° (planning), gimbal slew, throttle slew and tilt ≤ 20°. The certificate re-checks the physical limits. |

## 2. Rust module layout (`rust_lossless/src/aacg.rs`, suggested)

```
struct AacgConfig { t_min_plan, t_max_plan, gimbal_plan, gimbal_rate_plan, thrust_rate_plan, tilt_max,
                    glide_slope: Option<f64>, n: usize, substeps: usize, delta0, max_iter, tol }
struct Plan { alpha: Vec<[f64;2]>, ta: Vec<f64>, r, v, a: Vec<Vector3>, q: Vec<UnitQuaternion>, w: Vec<Vector3>,
              t_body: Vec<Vector3>, m: Vec<f64>, status, defect, iters }

fn propagate_attitude(grid, q0, w0, alpha) -> Attitude         // ~40 lines; nalgebra exp map
fn attitude_sensitivity(grid, &Attitude) -> Vec<Matrix3xX>     // ~20 lines
fn integrate_translation(grid, A: &[Matrix3xX], c: &[Vector3]) // ~30 lines; cumulative sums
fn build_inner_socp(...) -> (P, q, A, b, cones)                // like solve_at_current_time; variables = T_a + slacks
fn build_step_socp(...)  -> (P, q, A, b, cones)                // variables = alpha_x, alpha_y, T_a + slacks
fn plan(state, target, tf, warm: Option<&Plan>, budget: Duration) -> Plan   // loop of README §"How it works"
fn certify(plan, vehicle) -> Certificate                       // fine-grid checks + RK4 replay (~80 lines)
```

The Python reference is the specification:

| Python | Rust (to write) |
|---|---|
| `aacg.py` | about 300 lines |
| `attitude.py` | about 100 lines |
| `certify.py` | about 120 lines |

Every SOCP keeps the cone types `rust_lossless` already uses: zero, nonnegative and second-order. Port the cvxpy
expressions row by row, the same way `solve_at_current_time` assembles triplets. Absolute values become pairs of
linear inequalities, and L1 penalties become slack variables.

Problem sizes at N = 35:

| problem | variables | rows (approx.) | SOC blocks |
|---|---|---|---|
| inner | about 80 | 400 | 72 |
| step | about 150 | 600 | 108 |

These are the same size class as today's LCvx SOCP, which has about 300 variables at N = 35.

Validation: run the Python and Rust versions on `scripts/run_openloop.py`'s eight scenarios and compare fuel
(1e-6 kg), the iteration history and the certificate fields. Port `tests/test_solver.py` into `cargo test`.

## 3. Compute budget at 1 Hz on the flight computer (Jetson)

Python's `clarabel` package wraps the same Rust solver `rust_lossless` uses. The reported `solve_time` is therefore
the Rust solver's own time. Measured on the development Mac, under a load average of about 15–25 from other jobs:

| quantity | measured (Mac, loaded) | Jetson estimate (×2–4, single core) |
|---|---|---|
| one inner or step SOCP (N = 35) | 10–25 ms | 30–100 ms |
| first plan (warm start + ~15–30 iterations, 40–90 SOCPs) | 0.5–1.3 s | 2–5 s, **done during the 10 s hover** |
| warm-started replan, 4 iterations (≈ 9 SOCPs) | 0.1–0.25 s | 0.3–0.9 s |
| replan that needs continuation or a t_f extension (≈ 30–60 SOCPs; 49 % of in-air replans) | 0.5–1.5 s | 2–5 s, **over budget** |
| certificate (fine grid + RK4 replay, 1120 steps) | 0.15 s in Python | < 5 ms in Rust |
| attitude propagation + sensitivities + quadrature matrices | ~0.1 s in Python | < 5 ms in Rust |

How to stay inside 1 Hz:

1. **Hard time budget (anytime).** Every accepted iterate is flyable, so stop the loop at the budget (for example
   600 ms) and return the best certified iterate. If none is certified, keep flying the previous plan. It stays
   flyable and only loses the latest state correction, which the 50 Hz tracker handles.
2. **Run guidance in its own thread.** The flight code already runs guidance at 1 Hz and the MPC at 50 Hz. Hand the
   plan to the tracker when it is ready, timestamped with the state it was computed from.
3. **Reduce N for late replans.** As time-to-go shrinks, keep the step size h ≈ 0.2 s (N = t_go/0.2) instead of a
   fixed N = 35. Solve time is roughly linear in N.
4. **Clarabel settings.** Warm starts do not help interior-point methods much. Use `tol_gap_abs = tol_gap_rel = 1e-6`
   and `max_iter = 50`; the defaults are tighter than needed.
5. **Stop replanning at t_go < 1.5 s** (implemented). The final second is pure tracking.

On the measurements above, a warm-started replan with a 4-iteration budget fits 1 Hz on a Jetson-class CPU with
margin. Fallback replans are not rare: 49 % of in-air replans and 27 % of hop replans needed iterations beyond the 4-iteration budget or a t_f extension. They need the time budget in point 1. The measured mean solver time per replan was 0.37 s (in-air) and 0.19 s (hop), with a maximum of 1.33 s.

## 4. Tracking controller

The simulator's tracker (`sim6dof.CoPLQR`) is a deliberately simple stand-in for the club's MPC:

- an LQR per horizontal axis on [y, ẏ, b, ḃ] in centre-of-percussion coordinates y = r + (J_t/(mL)) b,
- a PD loop on vertical CoP motion,
- feed-forward of b, ḃ, b̈ and the axial thrust from the plan.

Either keep the existing NMPC and give it B's full reference with the corrected inertia and lever arm, or port the
CoP-LQR. The CoP-LQR is about 40 lines, has no solver, and has gains computed offline. The CoP form removes TVC's
"push sideways before turning" (non-minimum-phase) effect from the position loop.

## 5. Things to verify on hardware or in `rust_rocket_sim` before flight

- **Gimbal convention and sign of the torque.** B assumes d = (sin θ cos φ, sin φ, cos θ cos φ) and torque
  τ = (−L e₃) × T. Check both against `device_sim.rs` and the real actuator wiring.
- **RCS roll hold.** B assumes zero roll rate. Check that the RCS deadband keeps |ω_z| small, or include roll in the
  attitude propagation.
- **Isp and throttle map.** The sim plant realises about 216 s; guidance uses 180 s. Mass mismatch is absorbed by
  replans, but fuel numbers shift by about 20 %.
- **Planning margins.** Choose 440/920 N, 10° gimbal and t_f + 0.5 s against measured tracking performance in
  `rust_rocket_sim` with the real MPC.
