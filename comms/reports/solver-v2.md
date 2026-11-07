# [solver] solver-v2 report: practical guidance for the GTPL pure-TVC lander

**Recommendation: planner B, attitude-aware convex guidance (AACG).** Code is in `solver/`; the plain-language
description is in `solver/README.md`.

## How planner B works

B uses an outer loop over the body angular-acceleration profile α(t). Each pass has two convex solves:

- **Step.** One SCvx step with a trust region on the attitude change. Only the attitude-to-thrust-direction map is
  linearised; every other constraint stays exact and convex.
- **Inner solve.** The exact inner SOCP at the new attitude. It is C-6: with the attitude fixed, the axial thrust is
  the only control and the problem is exactly convex, with no relaxation.

The pieces around that loop:

- **Acceptance.** A step is accepted only if the exact merit decreases, so every accepted iterate is flyable.
- **Warm start.** A 3DOF solution, smoothed into a flyable attitude profile.
- **Certificate.** Each plan is checked against the physical limits on an 8× finer grid. It is then replayed open
  loop through the full quaternion rigid body.

## Key numbers

All numbers are in `solver/RESULTS.md`.

**Open loop, 8 in-air scenarios**

| measure | result |
|---|---|
| B vs best IPOPT 6DOF multistart (D) | within 0.012 % (mean 0.005 %) |
| B above the rigorous 3DOF-relaxation lower bound | 0.03–0.85 % |
| plans certified | 8/8 |
| open-loop replay landing error | ≤ 0.7 mm |
| solver work for the first plan | 37–63 SOCPs, 0.6–1.2 s Clarabel time on a loaded Mac |

**Candidates A and C**

- **A** (faithful flight LCvx) reproduces t_f 7.0 s and the 296 N lossy "min-thrust" arc (C-E). Three of 8 plans
  are lossy, and plans jump the thrust direction by 15° at t = 0 (5–14× the available angular acceleration at
  h = 0.2 s). Plans touch down with the thrust tilted up to 12°.
- **C** (3DOF + chord-bound-sized rate and second-difference limits) is infeasible at B's t_f in 8/8 scenarios. The
  second-difference bound also forbids the bang-bang throttle. At its own minimum t_f it costs +3.9 to +12.6 % fuel.
  It is tight when feasible, but never exactly flyable (C-Y).

**Closed loop**

Setup: 6DOF plant with mass-dependent J/L, gimbal/throttle slew limits, wind, noise and Isp error; a CoP-LQR tracker;
replans at 1 Hz.

| | success, 40 in-air descents | success, 30 pad hops |
|---|---|---|
| A | 28 % | 0 % |
| B | **100 %** (median 0.20 m/s, 3 cm) | **97 %** |
| C | 95 % (median 0.48 m/s, 18 cm) | 100 % (+23 % fuel) |

- B's one hop failure: the plan skimmed the altitude floor and touched down early, tilted 5.2°. Fix: add a clearance
  or glide-slope corridor for hops.

**Pad hop map (t_f = 4 s)**

- The 3DOF relaxation and A accept all 20 targets.
- For v0z ≥ 6.5 m/s, and at d = 6 m, neither B nor IPOPT finds any flyable plan.
- B and IPOPT agree on feasibility in 20/20 cells.

## Costs and caveats

- **Compute.** Mean solver time per replan was 0.37 s (max 1.33 s) on the Mac. About half of the in-air replans
  needed more than the 4-iteration budget or a t_f extension. For flight this means a hard anytime time budget:
  every accepted iterate is flyable, so stop at the budget, and fall back to the last certified plan if needed.
  Guidance should run in its own thread at 1 Hz. The first plan should be computed during the 10 s hover. See
  `solver/PORTING.md`.
- **No new deep claims.**
  - B rests on the formalized C-6 / Lemma 8.1 and on P22.
  - It also uses elementary new claims N1–N7, flagged in `solver/CLAIMS.md`. The φ-axis gimbal-rate condition is
    heuristic, and the certificate re-checks it.
  - Not claimed: SCvx convergence, the mass fixed point, closed-loop robustness.
- **Fix the MPC model regardless of guidance.** The flight MPC's inertia and lever arm are wrong by about 4.6× in
  angular authority (`context/vehicle.md` §4).

## Deliverables

- `solver/gtpl_guidance/` (package)
- `solver/tests/` (15 pytest tests, about 10 s)
- `solver/scripts/`
- `solver/results/` (JSON and PNG)
- `solver/README.md`, `RESULTS.md`, `PORTING.md`, `CLAIMS.md`
