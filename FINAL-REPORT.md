# Final report: lossless convexification for 5DOF / 6DOF powered descent

## Update, November 2026

1. **The impossibility result was audited and stands** ([`AUDIT-2026-11.md`](AUDIT-2026-11.md)). The obstruction was
   reproduced independently on the planner's own model: launched upward at 6.3 m/s on a 4 s hop, the vehicle can land
   1, 2 or 3 m away but not straight back down. The Lean build was not re-run in that audit.
2. **One conclusion below was wrong.** "Every practical method must iterate on the attitude" does not follow from the
   theorem. Lossless means sound and complete; a single convex program can still be sound.
3. **There is now a recommended landing algorithm** ([`LANDING-ALGORITHM.md`](LANDING-ALGORITHM.md)). It plans the path
   of the vehicle's centre of percussion, where the gimbal's sideways push cancels exactly, as one SOCP. Every plan is
   flyable at every instant (Theorem F, [`math/10-landing-proof.md`](math/10-landing-proof.md)); it costs 0.10 % of
   fuel on average at the operating point.
4. **Against standard successive convexification**, same simulator and cases, with each planner's solver time counted
   ([`solver/RESULTS-FLAT.md`](solver/RESULTS-FLAT.md)):

   | | SCvx | landing algorithm |
   |---|---|---|
   | in-air landings within limits | 40/40 | 40/40 |
   | lateral error, median / worst | 5.9 / 18.3 cm | 0.2 / 1.1 cm |
   | touchdown speed, median / worst | 0.23 / 0.58 m/s | 0.19 / 0.29 m/s |
   | solver time per replan, mean / worst | 1.05 / 4.9 s | 0.031 / 0.39 s |
   | pad-hop fuel | 1.46 kg | 1.54 kg |

   It is worse on pad-hop fuel (+5 %) and on the shortest possible flight time (up to 0.4 s longer on hops). With
   zero computation time and equal replan rates, lateral accuracy is a tie.

5. **The paper is updated** (revision 7, 48 pages): Section 4.5 states the program and Theorem F, Appendix E proves it,
   Section 6.3 reports the benchmarks. Theorem F is tagged as proved but not refereed and not machine-checked.

The sections below are the original report. "The practical algorithm" describes planner B, which the landing
algorithm supersedes as the recommendation.

Written by the orchestrator for the user's return. Details live in `SYNTHESIS.md` (results table with the status of
every claim), `paper/main.pdf` (40-page paper draft), and `comms/LOG.md` (decision log).

## The answer

**Lossless convexification is impossible for 5DOF and 6DOF powered descent, in the sense LCvx means it.** This is a proof,
not a failure to find a method. Strongest form, machine-checked in Lean 4 / Mathlib:

> For the 5DOF model (3D translation + thrust-axis pitch/yaw with an attitude-rate limit and a gimbal cone) and the
> kinematic 6DOF model (full rotations, free roll, body-rate limit), with throttle bounds, thrust-to-weight > 1 at full
> throttle, **altitude and glide-slope constraints, upright or free touchdown attitude, and any final time**,
> no convex program whose boundary data (initial position/velocity) enter jointly convexly — with any lifted or slack
> variables, for any cost — is lossless. (Constant acceleration bounds, i.e. constant mass, in the formal statement.)
>
> `LcvxObstruction.no_lossless_relaxation_constrained_{5dof, upright_5dof, 6dof, upright_6dof}` — sorry-free,
> axioms = [propext, Classical.choice, Quot.sound]. I rebuilt the project and checked the axioms myself.
>
> Also machine-checked **with real mass depletion, on free-final-time windows, and instantiated at our rocket's numbers**
> (400–1000 N, 79.88 kg wet / 55.88 kg dry, Isp 180 s, 15° gimbal, any burn ≤ 42 s):
> `LcvxObstruction.gtpl_no_lossless_upright_6dof_mass`, `gtpl_no_lossless_freeTime_mass`.

**Why:** 3DOF LCvx works because the thrust direction can switch instantly, so the convex "filled-in" thrust set is
achievable on average (Lyapunov/Aumann). On a real lander the thrust direction is tied to a body that rotates at a
finite rate. The vehicle can't average a left tilt and a right tilt, so the set of initial conditions from which a
landing is possible has a dent. Any convex program containing two landable states also contains their average, which
is not landable.

**Our actual vehicle (pure TVC: the gimbal is the pitch/yaw torque).** Computer-assisted proofs, each independently
re-certified in exact arithmetic, show the same nonconvexity at realistic horizons. The common setting is GTPL constants,
landing upright at rest, constant mass, unlimited gimbal rate, roll held.
- tf = 1 s: altitude + glide slope; cone, Cardan box, and roll-free.
- **tf = 2 s with no tilt cap:** altitude + glide slope.
- **tf = 3 s and 5 s with a tilt cap** (80° or 30°, like the flight code's 30° abort): altitude.

The fully realistic model (100°/s gimbal limit, mass depletion, 7 s burns) is nonconvex **numerically** at every horizon
tried, but not yet proved.

## What *is* possible (also proved)
- **Given an attitude profile, the problem is exactly convex** (for pure TVC, no relaxation is needed at all). All the
  nonconvexity is in choosing the attitude. Lean-checked for constant mass, with PMP and Aumann as explicitly named
  hypotheses.
- An SDP (moment) lift is exact for linear objectives. It is conjecturally exact (unbroken in ~4,500 tests, partially
  proved) for fixed-thrust min-landing-error. It is **not** exact with variable throttle or glide slope, so for us it is
  a certificate tool, not a solution.
- Infinite-dimensional occupation-measure LPs are exact, but that is generic and impractical.

## How big is the effect for GTPL?
- **In-air descents (e.g. from 50 m):** the nonconvex dent is thin, cm-level or less. Convex methods can get very close
  to optimal, but not exactly, and the current 3DOF output is not flyable as-is.
- **Pad-launched hops:** the reachable landing spots form a ring with a hole up to ~5 m (1.7 m in the TVC model). The 3DOF
  relaxation reports "optimal" for 11/20 hop targets where no flyable plan was found.

## The practical algorithm (built after the proof, as you asked)
`solver/`, planner B ("attitude-aware convex guidance"):
- **How it works:** warm-start from 3DOF, iterate a smooth flyable attitude profile, and solve the exactly-convex
  throttle problem at each step. Every accepted plan is flyable for the planning model and is certified by a 6DOF replay.
- **Open loop:** within 0.012% of the best nonconvex 6DOF optimum, and ≤0.85% above a provable lower bound.
- **Closed-loop 6DOF Monte Carlo** (wind, noise, Isp error): in-air success 100% (current flight guidance 28%); pad hops
  97% (current 0%).
- **Tests and Lean:** 15 pytest tests pass (27 as of 2026-11-10, with planner F's). The algorithm's 7 elementary math claims are Lean-checked. Formalizing them
  caught one wrong documented condition; the code was already correct.
- **Compared with standard 6DOF successive convexification** (`solver/RESULTS-SCVX.md`): planner B does **not** beat
  it. They tie on fuel (both within 0.03 % of IPOPT) and every plan from both is certified flyable. In closed loop
  standard SCvx landed 100 % in-air and 100 % of hops (B: 100 % / 97 %), at about 2× B's solver time per replan.
  Either works for the lander; B is faster, SCvx is the better-known method.
- **Also worth fixing:** the flight MPC's inertia and lever arm overstate angular authority by ~4.6×
  (`context/vehicle.md`).

## How we know it's right
- **Adversaries:** 7 adversary and red-team agents tried to break the proof or make LCvx work.
  - Breaks they found and we fixed: the first witness started underground; the 6DOF transfer was wrong for gimbal-torque
    coupling; a definitional loophole needed the "affine data entry" condition; a solver artifact faked an SDP
    counterexample.
  - Every "make it work" route failed with a proof: slacks, rate constraints, quaternion and SO(3) lifts, SDP lifts with
    throttle, and zero minimum throttle.
- **Referees:** 4 independent referees checked every proof line by line. Result: 0 broken, about 20 minor repairs, all
  applied.
- **Exact-arithmetic audit** of the computer-assisted TVC proof. It found and fixed a real bug: the witness assumed
  gimbal chattering.
- **Final audit:** the paper was audited against the registry and Lean. All 101 cited Lean theorems exist and depend
  only on standard axioms.

## Open (honestly)
- Pure-TVC rigor at tf = 7 s, uncapped beyond 2.3 s (needs a no-tumbling lemma), with the 100°/s gimbal limit, and with
  mass depletion.
- Lemma S / hop-ring rigor at GTPL constants (proved for higher thrust-to-weight vehicles; numerical for ours).
- The SDP conjecture CSD2′ residual class.
- Planner B's convergence (empirical only); the flight port needs a hard time budget.

## Where things are
| What | Where |
|---|---|
| One-page status of every claim | `SYNTHESIS.md` |
| **The landing algorithm, its proof, its benchmarks** | `LANDING-ALGORITHM.md`, `math/10-landing-proof.md`, `solver/RESULTS-FLAT.md` |
| November 2026 audit | `AUDIT-2026-11.md` |
| Paper draft (LaTeX + PDF) | `paper/main.pdf`, `paper/CLAIMS-MAP.md`, `paper/AUDIT.md` |
| **Shareable paper + proof archive** | `paper/main-share.pdf`; `share/make_bundle.sh` builds `share/dist/lcvx-impossibility-supplement.zip` (paper, Lean project with `Verify.lean`, TVC certificates) |
| Lean formalization | `lean/LcvxObstruction/` (`lean/MODEL.md`, `POSITIVE.md`, `SLICE.md`, `SOLVER.md`) |
| Proofs | `math/00`–`math/09`, referee reports `math/verify-*.md` |
| Practical guidance code | `solver/` (README, RESULTS, PORTING, CLAIMS) |
| Agent communication | `comms/` (BOARD, CLAIMS registry, threads, briefs, reports, LOG) |
| Full session transcript (conversation + every subagent) | `session-transcript/session-export.zip` |
| Complete map of the repository | `README.md` |

(Written 2026-11-07, before the repository was published. It has since been pushed to GitHub as `aneesh-iyer29/lossless-work`.)
At the time of writing nothing was pushed anywhere and everything was committed in the local git repo `GTPL/lcvx-5dof-research`. No sibling GTPL
repo was modified.
