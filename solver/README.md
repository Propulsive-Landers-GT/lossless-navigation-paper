# solver/: landing guidance for the GTPL lander

> **Recommended algorithm (November 2026): the landing algorithm, planner F.** It is one convex program per plan with no
> iteration. Start at [`../LANDING-ALGORITHM.md`](../LANDING-ALGORITHM.md); proof in
> [`../math/10-landing-proof.md`](../math/10-landing-proof.md); benchmarks against planners B and S in
> [RESULTS-FLAT.md](RESULTS-FLAT.md); worked example `scripts/example_landing.py`.
>
> The rest of this file documents planner B (attitude-aware convex guidance), the earlier recommendation. It still
> runs and is one of the two baselines.

This folder holds the practical end product of the lcvx-5dof-research project: a landing-guidance algorithm whose
every plan can actually be flown by our pure-TVC vehicle, plus the code that compares it with the current flight
guidance. Numbers and plots are in [RESULTS.md](RESULTS.md), the Rust/flight-software plan is in
[PORTING.md](PORTING.md), and the maths each step relies on is listed in [CLAIMS.md](CLAIMS.md).

## Short version

**Recommendation: planner B, "attitude-aware convex guidance" (AACG).** It runs a short loop of small convex
problems, the same kind of SOCP Clarabel already solves in `rust_lossless`:

1. **Warm start.** Solve the usual 3DOF problem, then fit a smooth body-attitude profile whose nose follows the 3DOF
   thrust direction.
2. **Exact inner solve.** Hold the attitude profile fixed and solve for the throttle. With the attitude fixed, this
   problem is *exactly* convex: no relaxation and no "lossless" trick. Its output is a trajectory the vehicle can fly.
3. **Attitude step.** Linearise the effect of a small attitude change, then solve one convex problem limited to
   small changes (a "trust region") to get a better attitude profile.
4. **Accept or shrink.** Re-run the exact inner solve at the new attitude. Keep the new profile only if
   fuel + penalty went down; otherwise shrink the trust region. Repeat until the improvement is tiny.
5. **Certificate.** Check the final plan against the real limits on a fine time grid and replay it through a full
   6DOF quaternion simulation, open loop. Fly it only if it passes.

What it achieved here (details in RESULTS.md):

- Every plan B flew passed the certificate.
- B is within **0.012 %** of the best nonconvex 6DOF optimum IPOPT found (multistart), and within 0.03–0.85 % of a
  rigorous 3DOF lower bound.
- In the closed-loop Monte Carlo, B landed in 40/40 in-air descents (median touchdown 0.20 m/s, 3 cm) and 29/30 pad
  hops.
- The current flight LCvx (baseline A) asks for thrust below the 400 N minimum and for direction changes the gimbal
  cannot produce. In closed loop it succeeds in 28 % of in-air descents and in no pad hop.

**Compared with standard 6DOF successive convexification (SCvx)** ([RESULTS-SCVX.md](RESULTS-SCVX.md)): B does *not*
outperform it. Both are within 0.03 % of the IPOPT optimum and 100 % certified open loop. In closed loop the standard
SCvx baseline (`gtpl_guidance/scvx6dof.py`) landed 40/40 in-air and 30/30 hops versus B's 40/40 and 29/30, with
slightly lower touchdown speeds in-air, but took about twice B's solver time per replan (0.62 vs 0.33 s mean).
Either is a sound choice; B's edge is speed and anytime feasibility.

## Why we need this: what is wrong with the current guidance

The flight code (`guidance/LosslessConvexification`) solves a **3DOF** problem: a point mass whose thrust vector can
point anywhere inside a 15° cone around vertical. On our vehicle that is not true:

- **The gimbal angle is the steering torque.** The thrust can only point where the body points, give or take the
  gimbal angle. To turn the body you have to deflect the gimbal, and that deflection also pushes the vehicle
  sideways. The direction of thrust therefore cannot jump. With J_t ≈ 64 kg m² and L ≈ 0.59 m, the vehicle manages
  roughly 1–2.4 rad/s² of pitch/yaw acceleration.
- The 3DOF plans contain direction jumps that would need 10³× more angular acceleration than that
  (`context/vehicle.md` §5.5). The flight MPC copes only because it throws the planned direction away.
- The 3DOF plans are **not tight on the minimum-throttle arc**. On the 50 m drop the plan delivers 296 N while
  claiming 400 N. This is the "lossy" behaviour the theory predicts (claim C-E). Our faithful re-implementation
  (`solve_baseline_A`) reproduces it exactly: t_f = 7.0 s, minimum delivered thrust 296 N.

The research project proved, and machine-checked in Lean, that **no single convex program can be exactly lossless
for 5DOF/6DOF landing**. A clever reformulation of LCvx will never remove this. The proofs also show where the
nonconvexity lives: entirely in the **choice of attitude profile**. Once the attitude is fixed, everything else is
exactly convex (claim C-6). AACG is built on that split: a small outer loop over attitude, around an exact convex
inner problem.

(Lossless means exact: feasible exactly when a flyable plan exists. That does not rule out a single convex program
that is merely *sound*. Planner F is one; see the note at the top.)

## How the algorithm works, in more detail

### The model the planner uses

- The CG translates under gravity and the thrust vector. The thrust is applied at the gimbal, L below the CG.
- The body rolls only via RCS, which holds the roll rate at zero. Pitch/yaw torque comes **only** from the gimbal:
  `J_t * angular_accel = L * (lateral thrust)`.
- The planner's attitude variable is the **body angular acceleration** α(t) (two components, pitch and yaw). It is
  piecewise linear in time, so the gimbal angle never jumps. Fixing α(t) fixes:
  - the body rate ω(t) (exactly linear in α, because the roll rate is zero),
  - the attitude R(t) (integrate ω),
  - the gimbal's lateral thrust `T_x = -(J_t/L) α_y`, `T_y = +(J_t/L) α_x` (torque balance, Lemma 8.1).
- The one remaining free control is the **axial thrust T_a(t)**, the component along the body axis.

### Step 2, the exact inner problem (`AACG.solve_inner`)

The decision variables are T_a at the N+1 nodes, plus slacks. With the attitude fixed, the CG acceleration
`(R(t) [T_x, T_y, T_a] )/m(t) - g` is **linear in T_a**. Position and velocity at the nodes are therefore linear in
T_a. We integrate them exactly with 8 quadrature substeps per interval. The constraints are:

| constraint | form |
|---|---|
| throttle 440–920 N (planning margin inside 400–1000) | interval on T_a: `sqrt(440² − κ²) ≤ T_a ≤ sqrt(920² − κ²)`, κ = lateral thrust |
| gimbal (planning limit 10° inside the 15° box) | `\|T_x\|, \|T_y\| ≤ tan(10°) T_a` |
| gimbal slew 100°/s, throttle slew 2000 N/s | linear sufficient conditions on node-to-node changes |
| glide slope (10°) and altitude | second-order cones on node positions (soft with a large penalty, so replans from slightly outside still solve) |
| land at the target at rest | linear in T_a (L1 penalty, which is exact when feasible) |
| fuel | Σ ‖thrust‖ · dt (a second-order cone) |

Every solution of this problem is a trajectory of the true dynamics for that attitude. Nothing is relaxed, so there
is no lossiness to check.

### Step 3, the attitude step (`AACG.solve_step`)

The variables are α and T_a together. A small attitude change δφ moves the thrust direction by δφ × T. We compute
how δφ depends on δα (`attitude_sensitivity`) and linearise only that term. Every other constraint stays exact and
convex. The minimum-thrust bound ‖T‖ ≥ 440 is the only nonconvex constraint; we replace it by its tangent plane at
the current solution, which is a safe inner approximation (claim 9). The trust region limits the attitude change at
every node to Δ radians (starting at 0.05 rad).

### Step 4, accept or reject

The merit is fuel [kg] + 10·(position defect [m] + velocity defect [m/s]) + 20·(touchdown tilt [rad]) +
100·(glide-slope violation [m]). A step is accepted if the exact inner merit decreased by at least 10 % of the
predicted decrease. Δ doubles after a very good step and halves after a rejected one. **Every accepted iterate is an
exact, flyable solution**, so the loop can be stopped at any time: that is what the 1 Hz replans do.

### Step 5, certificate (`certify.certify_B`)

The certificate checks the *returned plan*, not the optimiser:

- throttle within 400–1000 N,
- exact gimbal angles (flight convention) within ±15°,
- gimbal rate ≤ 100°/s and throttle rate ≤ 2000 N/s,
- tilt and glide slope,
- touchdown defect ≤ 1 cm and 1 cm/s, tilt ≤ 0.5°, zero rate,
- an **open-loop replay** of the planned body-frame thrust through the full quaternion rigid-body model, which must
  land within 5 cm. In practice it lands within about 1 mm.

### Inputs and outputs

`AACG(vehicle, config).plan(r0, v0, m0, R0, w0, target, tf, alpha_init=None)`

- **inputs:** CG position and velocity (world, z up), mass, body-to-world rotation matrix, body rate, target CG
  position (pad: z = 1.5 m), time to go, and optionally the previous plan's α for a warm start;
- **outputs (`PlanB`):** at 8 samples per node,
  - CG position, velocity and acceleration,
  - attitude R(t), body rate and angular acceleration,
  - body-frame thrust vector (hence gimbal angles and throttle),
  - mass and fuel,
  - `status` (`certified-inner` or `infeasible-best-effort`), defects, iteration count and solver time.

The closed-loop wrapper `guidance.PlannerB` adds:

- the 1 Hz shrinking-horizon replans, warm-started from the previous plan,
- an iteration budget (4 SCvx iterations, more only if the plan is not yet feasible),
- t_f extension as a last resort,
- "keep flying the last certified plan" if a replan fails.

## Parameters and tuning (`params.PlannerConfig`)

| parameter | default | what it does / how to tune |
|---|---|---|
| `T_min_plan`, `T_max_plan` | 440, 920 N | Throttle margin left for the tracking controller. Smaller margins save fuel and time but make the tracker saturate. Replans may use 20/40 N of this margin (`replan_margin_use`). |
| `gimbal_plan` | 10° | Gimbal angle the plan may use, out of the 15° box. The other 5° is the tracker's steering authority. |
| `gimbal_rate_plan` | 60°/s | Feeds the linear gimbal-slew condition. The certificate checks against the true 100°/s. |
| `thrust_rate_plan` | 1500 N/s | Feeds the throttle-slew condition (true limit 2000 N/s). |
| `tilt_max` | 20° | Body-tilt limit along the path. |
| `glide_slope` | 10° | Minimum elevation of the vehicle as seen from the target. Set `None` for pad hops. |
| `N`, `substeps` | 35, 8 | Nodes and quadrature substeps. Solve time grows roughly linearly with N. N = 25 is fine for replans. |
| t_f margin | +0.5 s over the minimum feasible t_f | Fuel-optimal plans brake at full planned thrust, so some spare time makes replans robust. |
| `Delta0`, `max_iter`, `tol` | 0.05 rad, 15, 1e-4 | Trust region and stopping rule. Replans use 4 iterations. |

**Choosing t_f.** Fuel always increases with t_f, so the fuel-optimal time is the shortest feasible one.
`guidance.min_tf_B` finds it by bisection, starting from the 3DOF lower bound, in about 6–8 B solves. In flight,
do this during the 10 s hover, then fly a fixed absolute touchdown time with shrinking-horizon replans.

## Failure modes, and what the code does about them

| failure | symptom | handling |
|---|---|---|
| No flyable plan exists (e.g. pad hops with too much upward speed; the 3DOF relaxation wrongly claims feasibility, see the hop map) | `status = infeasible-best-effort`, certificate fails | Do not fly it. The returned plan minimises the landing defect (a "least-bad" plan) and can serve as an abort/divert reference. |
| SCvx stalls near the feasibility edge (seen once in an early run without the initial-gimbal condition; not seen in the final runs) | not certified after `max_iter` | Retry from the 3DOF warm start, extend t_f, or keep the previous certified plan. |
| A replan becomes infeasible after tracking errors | the shrinking-horizon problem at the remaining t_f is not certified | Continue iterating, then extend t_f by 0.5 s / 1.0 s. If that still fails, keep the last certified plan, which is still flyable. |
| Plant differs from the model (mass properties, Isp, wind) | tracking errors | Handled by the tracking controller plus replans. The plan certificate covers only the planning model. |
| Hop plans skimming the altitude floor (no glide slope for hops; 1/30 hops touched down early, tilted 5.2°) | early touchdown | Add a clearance or glide-slope corridor near the target for hops. |
| Symmetric problems (pure vertical drop at too short a t_f) | B stays vertical; a tilted dive would waste vertical impulse | Choose t_f with `min_tf_B` (bisection on certified status). |

## How it relates to the theory (one paragraph per result)

- **Impossibility (Thm A, B\*, Lean).** No uniform convex relaxation is lossless for 5DOF/6DOF, so the single-SOCP
  *relaxations* A and C are either infeasible for the vehicle or loose somewhere. B is not a single convex
  program: its constraint set depends on the instance through the attitude profile, which is allowed (C-U).
  (An earlier version said "any single-SOCP method". That was too strong: a single-SOCP *restriction* can be sound,
  and planner F is.)
- **C-6 (Lean, constant mass).** With the attitude fixed, the pure-TVC problem is exactly convex in the axial
  thrust. That is B's inner problem. We use a prescribed mass history (fixed point), and the replay certificate
  checks the residual.
- **C-U.** The 6DOF feasible set is a union of convex sets, one per attitude profile. B searches over that union
  locally.
- **C-Y.** A 3DOF thrust history is exactly TVC-realisable only for a measure-zero set of initial body rates. That is
  why A and C plans can be tracked approximately but never certified.
- **FLAT (centre of percussion).** The point y = r + (J_t/(mL)) b accelerates exactly along the body axis. The
  tracking controller works in y, which removes the "push sideways before turning" (non-minimum-phase) effect of TVC.
  Planner F plans in y as well, which is what removes B's outer loop.
- **Hop ring (numerics).** On pad hops the nonconvexity is metre-scale. There the 3DOF relaxation accepts landings
  that do not exist, while B correctly refuses to certify them.

## Files

| file | content |
|---|---|
| `gtpl_guidance/landing.py` | **entry point of the landing algorithm** (`LandingGuidance`) |
| `gtpl_guidance/fcg.py`, `flat.py`, `flatcert.py` | planner F: the convex program, the centre-of-percussion formulas and spline, the limit check and open-loop replay |
| `gtpl_guidance/params.py` | vehicle (plant) and planner parameters |
| `gtpl_guidance/lcvx3dof.py` | A (faithful flight LCvx + t_f search), C (rate-limited 3DOF), 3DOF relaxation lower bound, purification |
| `gtpl_guidance/attitude.py` | grid, attitude propagation from α, sensitivities, exact translational quadrature |
| `gtpl_guidance/aacg.py` | **planner B** |
| `gtpl_guidance/certify.py` | certificates for B (fine grid + 6DOF replay) and for 3DOF plans |
| `gtpl_guidance/reference_nlp.py` | D: CasADi/IPOPT 6DOF multistart reference |
| `gtpl_guidance/dynamics.py`, `sim6dof.py` | rigid-body plant, CoP-LQR tracking controller, closed loop with 1 Hz replans |
| `gtpl_guidance/guidance.py` | closed-loop planner wrappers, t_f searches |
| `gtpl_guidance/scvx6dof.py` | S: standard 6DOF successive convexification baseline |
| `scripts/` | `run_openloop.py`, `run_hop.py`, `run_montecarlo.py`, `make_report.py`; for planner F: `example_landing.py`, `run_openloop_flat.py`, `replay_flat.py`, `run_hop_flat.py`, `run_mc_flat.py`, `stress_flat.py`, `report_flat.py`, `plot_flat.py`; for the audit: `audit_hop_ring.py`, `audit_hop_ring_d0.py`, `audit_single_convex.py` |
| `tests/test_solver.py`, `tests/test_flat.py` | pytest (16 + 11 tests, about 35 s) |

## Running

```sh
cd solver
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python numpy scipy cvxpy clarabel ecos casadi matplotlib pytest
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
.venv/bin/python -m pytest -q                       # tests
.venv/bin/python scripts/example_landing.py         # the landing algorithm on one descent
.venv/bin/python scripts/run_openloop.py            # A/B/C/D/LB comparison  -> results/openloop.json
.venv/bin/python scripts/run_montecarlo.py --scenario inair --n 40 --workers 2
.venv/bin/python scripts/make_report.py --example   # tables + plots
```

Minimal use:

```python
import numpy as np
from gtpl_guidance.params import default_vehicle, default_config
from gtpl_guidance.aacg import AACG
from gtpl_guidance.certify import certify_B
veh, cfg = default_vehicle(), default_config()
plan = AACG(veh, cfg).plan(r0=[10, 20, 50], v0=[0, 0, 0], m0=80, R0=np.eye(3), w0=[0, 0, 0],
                           target=[0, 0, 1.5], tf=8.6)
print(plan.status, plan.fuel, certify_B(plan, veh, cfg, [10, 20, 50], [0, 0, 0], 80, np.eye(3), [0, 0, 0],
                                        np.array([0, 0, 1.5]))['passed'])
```
