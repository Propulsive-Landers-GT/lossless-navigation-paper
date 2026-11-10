# Planner B vs standard 6DOF successive convexification (SCvx)

Generated 2026-11-07. Question: does planner B (attitude-aware convex guidance) perform better than standard
successive convexification? **Short answer: no, not measurably. They tie on optimality, both always produce
flyable plans, and in closed loop the standard SCvx baseline was as good or slightly better, at about twice the
solver time per replan.** Planner B's distinctive property (every accepted iterate is exactly flyable) did not
translate into a measurable advantage on these tests.

## The baseline (S)

`gtpl_guidance/scvx6dof.py`: textbook SCvx (Mao, Szmuk & Açıkmeşe 2016; Szmuk & Açıkmeşe 2018; Malyuta et al. 2022).

- **Model:** the full 14-state quaternion rigid body, identical to the IPOPT reference D: same vehicle, same
  first-order-hold body thrust on N = 35 intervals, roll torque 0, J_t and L at their m₀ values, RK4 with 4 substeps.
- **Constraints:** identical to B and D: throttle 440–920 N (upper bound as a cone, lower bound linearized at the
  current thrust, a safe inner approximation), |T_x|, |T_y| ≤ tan 10° T_z, the same linear gimbal-rate and
  throttle-slew conditions, tilt ≤ 20° (convex in the quaternion), altitude floor and 10° glide slope (soft, same
  exact penalty as B), upright at rest at the pad, gimbal starting at its current deflection.
- **Algorithm:** linearize the whole discrete dynamics about the current trajectory (multiple shooting, CasADi
  Jacobians), add virtual control with an exact L1 penalty (weight 1000), ∞-norm trust region on scaled
  variables, standard ratio test (ρ₀ = 0, ρ₁ = 0.25, ρ₂ = 0.7). Stop when the virtual control is below 1e-6 and the
  predicted decrease is below 1e-5 · (1 + merit), the same relative tolerance B uses.
- **Initial guesses:** the 3DOF solution (the same warm start B uses) or a straight-line guess (Szmuk & Açıkmeşe 2018).
- **Judged by the same certificate as B** (`certify_B`): physical limits on an 8× finer grid and an open-loop replay
  of the planned thrust through the full rigid body. The returned plan is the forward integration of S's thrust
  from the initial state, so the certificate checks what would actually be flown.
- **Tuning:** default parameters chosen once; no per-scenario tuning of either method.

Reproduce: `scripts/run_openloop_scvx.py`, `scripts/run_hop_scvx.py`,
`scripts/run_montecarlo.py --methods B,S --tag _scvx --scenario {inair,hop}`, then `scripts/report_scvx.py` prints
every table below. Raw data: `results/*_scvx.json`. B was re-run alongside S in every experiment so both are timed
under the same machine load (load average about 3–4). Solver times are Clarabel's internal times.

## 1. Open loop: 8 in-air scenarios × 2 final times (16 problems)

Final times as in RESULTS.md §1: B's minimum certified t_f and t_f + 0.5 s. D = best IPOPT multistart optimum.

| | certified | fuel vs IPOPT: mean / max | SOCPs per plan: median / max | solver time per plan [s]: median / max | to first flyable plan: SOCPs / solver time [s], median |
|---|---|---|---|---|---|
| **B** | 16/16 | +0.0060 % / +0.0205 % | 43 / 63 | 0.62 / 0.95 | 18 / 0.24 |
| **S, 3DOF start** | 16/16 | +0.0044 % / +0.0268 % | 33 / 46 | 0.70 / 1.02 | 13 / 0.29 |
| **S, straight-line start** | 16/16 | +0.0021 % / +0.0086 % | 36 / 44 | 0.79 / 0.95 | 16 / 0.38 |

- **Optimality: a tie.** All three are within 0.03 % of IPOPT on every problem. Differences of a few thousandths of
  a percent are below what the discretization resolves.
- **Feasibility: a tie.** Every plan from every method passed the certificate.
- **Cost: about equal.** B solves more but much smaller SOCPs (36–108 variables vs about 650 for S), so total solver
  time is similar. "First flyable plan" uses the same criterion for both (lands within 1 cm, 1 cm/s and 0.5° when
  flown open loop): B gets there in a median 0.24 s, S in 0.29 s from the same warm start.
- S does not need a good initial guess here: from a straight line it converged on all 16 problems.

Per-problem numbers: `scripts/report_scvx.py`.

## 2. Pad-hop map (20 cells, t_f = 4 s)

| | agrees with IPOPT on which landings are possible | certified where possible (9 cells) | SOCPs, possible cells: median / max | SOCPs, impossible cells: median / max | total solver time [s] |
|---|---|---|---|---|---|
| **B** | 20/20 | 9/9 | 23 / 39 | 65 / 85 | 6.9 |
| **S, 3DOF start** | 20/20 | 9/9 | 33 / 71 | 101 / 101 | 33.0 |
| **S, straight-line start** | 20/20 | 9/9 | 35 / 47 | 100 / 100 | 33.3 |

- Both find every landing IPOPT finds, at the same fuel (within 0.006 %), and neither claims a landing IPOPT can't find.
- On the 11 impossible cells, S runs its whole 100-iteration budget before giving up; B's trust region collapses
  sooner. That is most of S's 5× higher total time here. It reflects the stopping rule, not solution quality: a flight
  implementation of S would cap iterations anyway.

## 3. Closed-loop 6DOF Monte Carlo

Same plant, disturbances, tracker, cases and seeds as RESULTS.md §3. B and S fly the same problem with the same final
time (B's minimum certified t_f + 0.5 s), the same replan margins and the same fallback rules: warm start from the
previous plan, small iteration budget (B: 4 iterations ≈ 9 SOCPs; S: 8 SOCPs), continuation if no flyable plan yet,
then t_f extension, and keep flying the previous plan if a replan fails.

**In-air descents (40 runs)**

| method | success | touchdown speed [m/s] median / p95 / max | lateral error [m] median / p95 / max | fuel at t_f [kg] mean | replans certified | replans needing continuation or t_f extension | solver time per replan [s] mean / max |
|---|---|---|---|---|---|---|---|
| **B** | 100 % (40/40) | 0.20 / 0.37 / 0.38 | 0.03 / 0.08 / 0.09 | 3.821 | 97 % | 123/251 (49 %) | 0.33 / 1.21 |
| **S** | 100 % (40/40) | 0.13 / 0.33 / 0.37 | 0.03 / 0.07 / 0.10 | 3.807 | 100 % | 146/260 (56 %) | 0.62 / 1.65 |

Paired by case: S used 0.31 % less fuel on average (range −7.7 % to +8.7 %) and touched down slower in 31 of 40 cases.

**Pad hops (30 runs)**

| method | success | touchdown speed [m/s] median / p95 / max | lateral error [m] median / p95 / max | fuel at t_f [kg] mean | replans certified | replans needing continuation or t_f extension | solver time per replan [s] mean / max |
|---|---|---|---|---|---|---|---|
| **B** | 97 % (29/30) | 0.41 / 0.61 / 0.66 | 0.03 / 0.06 / 0.06 | 1.603 | 100 % | 20/73 (27 %) | 0.18 / 0.71 |
| **S** | 100 % (30/30) | 0.50 / 0.57 / 0.58 | 0.02 / 0.05 / 0.05 | 1.471 | 100 % | 1/61 (2 %) | 0.36 / 1.50 |

Paired by case: S used 6.4 % less fuel on average (range −29 % to +15 %).

**Why the closed-loop numbers differ when the first plans don't.** The first plans of B and S agree within 0.13 %
in fuel in every case. The differences come from replanning after disturbances:

- In hops, B's shrinking-horizon replans failed to close the landing defect within budget and fell back to a 0.5 s
  final-time extension in 17/30 runs; S needed one in 1/30. Each extension costs roughly 20–30 % more fuel on a 4 s
  hop. S's warm start carries the whole previous state trajectory, and that recovered better from tracking errors here.
- In-air, S extended more often (35 vs 24 runs) but the fuel effect averaged out.
- B's one hop failure (case 12, which skims the altitude floor) is landed by S.

This is a property of the two replanning implementations as built, not a theorem about either method. Tuning B's
replan budget or warm start might close the gap.

## 4. Verdict

| | B (attitude-aware convex guidance) | S (standard 6DOF SCvx) |
|---|---|---|
| fuel vs IPOPT, open loop | within 0.02 % | within 0.03 % |
| plans certified flyable | 100 % | 100 % |
| closed-loop success, in-air / hop | 100 % / 97 % | **100 % / 100 %** |
| median touchdown speed, in-air / hop | 0.20 / 0.41 m/s | **0.13** / 0.50 m/s |
| solver time per replan, mean / max | **0.33 / 1.21 s** in-air, **0.18 / 0.71 s** hop | 0.62 / 1.65 s in-air, 0.36 / 1.50 s hop |
| anytime feasibility | every accepted iterate is exactly flyable | flyable only once virtual control vanishes |
| needs a good initial guess | uses the 3DOF warm start | no (straight line works) |
| subproblem size | many small SOCPs (36–108 variables) | fewer, larger SOCPs (~650 variables) |
| theory behind it | exact convexity given attitude (Lean-checked) | standard SCvx convergence theory (Mao et al.) |

**What the numbers support:**

- Planner B does **not** outperform standard SCvx on landing quality, fuel or reliability in these tests. S was as
  good or slightly better in closed loop.
- B is about **2× faster per replan** (mean and worst case), which matters for the flight computer's time budget
  (`PORTING.md`).
- Both are large improvements over the current flight guidance (28 % / 0 % success) and over 3DOF + rate limits.

**Practical recommendation:** either is a sound choice for the lander. Standard SCvx is the better-known method,
with published convergence theory and flight heritage in the literature, and here it was at least as robust. B's
advantages are speed and the "stop any time and fly the last accepted plan" property. If the flight computer can
afford about 0.6 s average and 1.7 s worst-case per replan, standard SCvx is the conservative pick. If not, B.

**Correction (November 2026).** This section used to end: "the research result, that exact lossless convexification
is impossible and every practical method must iterate on the attitude, applies to both." The first half is right.
The second half does not follow from the theorem and is false: planner F ([FLAT.md](FLAT.md)) is a single convex
program whose plans are all flyable, with no iteration on the attitude. It was compared with B and S on the same
cases in [RESULTS-FLAT.md](RESULTS-FLAT.md), which also adds computation time to the closed loop. The numbers above
give every planner zero computation time; see `../AUDIT-2026-11.md` §4.

**Not tested:** other SCvx variants (PTR, free final time inside the solver), tuning either method's parameters,
timing on the flight hardware, or running either planner in the club's Rust simulator.
