# Is 5DOF / 6DOF lossless convexification possible? — living synthesis

Orchestrator-maintained. Every item links to the file with the proof. Status keys:
**LEAN** = machine-checked (sorry-free, standard axioms only) · **PROVED** = rigorous proof that survived adversarial attack ·
**NUMERICAL** = strong numerical evidence only · **OPEN**.

## Short answer (current)

**Headline (machine-checked):** for the kinematic 5DOF model and the kinematic 6DOF model (proper rotations, free roll,
attitude-rate limit ω), with throttle bounds 0 < a_min ≤ a ≤ a_max, full-throttle thrust-to-weight > 1, gimbal
0 < δ < π/2, altitude and glide-slope constraints, upright or free touchdown attitude, and ANY final time tf > 0:
no uniform convex relaxation (boundary data entering jointly convexly, any lifted variables) is lossless, for any
cost. Lean 4/Mathlib, sorry-free, axioms = [propext, Classical.choice, Quot.sound]
(`LcvxObstruction.no_lossless_relaxation_constrained_{5dof,upright_5dof,6dof,upright_6dof}`).

**Real GTPL actuation (pure TVC, gimbal = torque):** computer-assisted proof, certified in exact arithmetic, that the
landing set is nonconvex (upright at rest, altitude + glide slope, cone or Cardan box, tf = 1 s, constant mass, unlimited
gimbal rate) ⇒ no uniform lossless convexification for that problem class either. Realistic 5–8 s horizons: numerical.

1. **Impossible in the LCvx sense.** Classical LCvx keeps the physical state (r, v, m) as decision variables, enters
   boundary data affinely, and relaxes the control constraints. No relaxation of that kind can be lossless for 5DOF
   with a finite attitude rate — with a minimum throttle ρ1 > 0 (B, B*), and even with ρ1 = 0 (P0-F: the vehicle can coast while it rotates, which creates a different nonconvex kink). The obstruction: the set of feasible boundary conditions is
   nonconvex, because the vehicle cannot "chatter" its thrust direction (math/00, math/02).
2. **The obstruction is genuine; its size depends on the flight phase.** For pad-launched hops the landing set is a ring with a metre-scale hole (up to ~5 m; 1.7 m in the torque-coupled TVC model). For in-air descents it is thin: with r_z ≥ 0 the proven dent is ≈1e-5 m (rigorous) to ≈1 cm (heuristic) for the kinematic model. Large (m/s-level) gaps exist only for
   trajectories that would start underground (math/01, math/02 §10).
3. **Possible in other senses:**
   - **Fixed attitude profile:** given b(t), the convex relaxation is exact (Thm C, math/04). On the real TVC vehicle,
     given b(t), the problem is exactly convex with no relaxation needed (C-6).
   - **Per instance:** the nonconvexity is entirely the choice of attitude profile (C-U).
   - **Infinite-dimensional lifts:** occupation-measure LPs with point-mass data entry are exact (generic; not practical).
   - **Tractable SDP lift (narrow 'possible'):** a degree-2 SDP lift is exact for every LINEAR objective (T2), and
     conjecturally (CSD2′: unbroken in ~4,500 solves, proved for an a-priori class and by an index theorem except a thin
     residual class) exact for fixed-thrust min-landing-error with a chattering gimbal. It is NOT exact with variable
     throttle (gap grows to 68%) or with glide slope in general. So for GTPL it is a certificate tool, not a solution.

## Results table

| ID | Statement | Model / scope | Status | Where |
|---|---|---|---|---|
| A | Lossless uniform convex relaxation (affine data entry) ⇒ feasible boundary-data set convex | abstract | **LEAN** | lean/…/Abstract.lean |
| B | Midpoint of extreme min-throttle arcs unreachable ⇒ F_tf nonconvex | M1 kinematic 5DOF, no altitude constraint, δ+ωtf ≤ π/2 | **LEAN** (`no_lossless_relaxation_5dof`) | lean/…/Main.lean |
| Q | Quantitative gap Γ (ball bound) ⇒ no ε-lossless relaxation for ε<Γ | M1, no altitude constraint | PROVED | math/02 |
| B* | Dive-then-brake exposed face ⇒ F nonconvex with altitude/glide slope, any tf, upright landing, bounded free-tf window | M1; kinematic 6DOF (proper rotations, free roll); independent-torque 6DOF | **LEAN** for M1 + kinematic 6DOF, constant acceleration bounds (constant mass), any tf>0, any constraint set ⊇ glide-slope cone, upright or free terminal attitude: `no_lossless_relaxation_constrained_5dof`, `…_upright_5dof`, `…_constrained_6dof`, `…_upright_6dof` (+ optimisation form for every cost). Orchestrator-verified: full build, standard axioms only. Not in Lean: α>0 for B*, quantitative bounds, torque-limited 6DOF | lean/…/DiveBrake.lean, Upright.lean, SixDOF.lean, Main.lean |
| RR-LS | Line search over tf cannot rescue LCvx (needs B*'s braking condition / time window) | M1 | abstract lemma **LEAN** (FreeTime.lean); concrete instance on paper | math/redteam-reform.md §4 |
| A-opt, T | Value-lossless on F ⇒ V equals its finite-mixture convex envelope on F; cost ∫b·e_z violates it (upright variant) | abstract / M1 | PROVED (referee); A-opt + abstract Prop T **LEAN** (`Slice.CostRelaxation.aOpt`, `no_valueLossless_of_strict`) | math/redteam-lift.md §7, lean/SLICE.md |
| D | Per-instance min-landing-error: state-linear relaxations (affine readout + convex penalty) lossy | M1 | abstract theorem **LEAN** (TheoremD.lean); hard-v(tf)=0 instance via Lemma S (proved on paper) | math/02, threads/theorem-D.md |
| S | Straight-below landing infeasible, offset feasible (vertical instance) ⇒ Theorem D with hard v(tf)=0 lossy | M1; δ+ωtf<π/2; min-throttle T/W > 1/cos(δ+ωtf) (cannot hover at min throttle) | PROVED (referee-confirmed; Ω-range lower ends fixed) + **LEAN** on an explicit instance (a≡12 m/s² fixed thrust, ω=0.1 rad/s, no gimbal, r_z≥0, any 3D path incl. coning): every landing offset ≥ 1 m, L nonconvex, every state-linear relaxation reports error 0 vs true ≥ 1 m (`Slice.lemmaS`, `Slice.theoremD_hard_landing`; Wirtinger `Slice.periodic_wirtinger`, master inequality). Orchestrator-verified | math/07, lean/SLICE.md |
| S-GTPL | Lemma S at GTPL constants (hovering possible at min throttle) | M1 | NUMERICAL (gap ≈1 cm in ℓ; optimizers land 1.5–2.4 m off-axis) | math/07, numerics s1 |
| FLAT | Centre-of-percussion identity: pure TVC ≡ zero-gimbal, torque-limited point thrust along b | pure TVC, ω3 ≡ 0, ε const | identity verified numerically (5e-15) | math/checks/flat_output_tvc.py |
| B6-TVC | Pure-TVC F nonconvex | terminal r=v=0, ω⊥(tf)=0, tilt free | PROVED (adversary-6dof) | math/adversary-6dof-report.md |
| B6-TVC-up | Pure-TVC F nonconvex, upright at rest + r_z ≥ 0 + glide slope (**the real GTPL actuation**) | pure TVC, GTPL wet constants, constant mass, unlimited gimbal rate, cone 15° or Cardan box ±15°, roll held or free, tf = 1 s | **COMPUTER-ASSISTED PROOF, CERTIFIED IN EXACT ARITHMETIC** (verify-tvc: exact rational/Arb rebuild, exact integer-determinant PD check; margins 13.7% cone / 5.4% box / 4.0% free roll; certified dist(θ_m,F) ≥ 9.6e-6 m). Repairs: witness replaced by explicit fast bang-bang gimbal (needs unlimited gimbal rate); free-roll gyro weight made rigorous. NUMERICAL at tf=5/7 s (≈3 cm). **Fully realistic model (100°/s box gimbal from centred, mass depletion, roll free, r_z ≥ 0, upright at rest): NUMERICALLY NONCONVEX at every horizon tried** (dive-then-brake face; gaps 1.26e-2 m tf=3, 4.8e-3 m tf=5, 2.8e-2 / 3.3e-2 m tf=5/7) — 'nonconvex but unproved'. Open (rigor): tf ≥ 2 s certificate (structural loss ~300× on this face; route: penalty localized to G_w + state-space Riccati certificate), rate-limited certificate (jerk multiplier), mass depletion, free tf, tumbling lemma | math/06, math/verify-tvc-report.md |
| C | LCvx exact given attitude profile b(t); strong form under PMP + checkable non-degeneracy | M1 | PROVED; **LEAN**: C-3 pointwise lemma (`LcvxPositive.C3_headline`), C-S/C-D2 (const. mass), discrete purification C-K, C-F (`convex_origFeas`, with Aumann as explicit hypothesis), C-6 TVC convexity — 35 theorems, standard axioms only; PMP & Aumann only as explicit named hypotheses | math/04, lean/POSITIVE.md |
| C-Y | 3DOF LCvx optimum exactly 6DOF-flyable for GTPL essentially never | pure TVC | PROVED | math/04 |
| X5 | Pointing cone ≤ gimbal ⇒ 5DOF = 3DOF, LCvx exact | M1 only (pure TVC: effective gimbal 0) | PROVED | math/redteam-reform.md |
| P0-R | ρ1 = 0: velocity set R convex iff δ+ωtf ≤ π/2 | M1 | PROVED | math/possibility-rho0.md |
| P0-F | ρ1 = 0 still gives nonconvex F_tf (coast-while-rotating; thrust on/off kink) ⇒ no 'possible iff ρ1=0' dichotomy | M1, α=0, δ<π/4, ωtf<π/2−2δ | PROVED | math/possibility-rho0.md |
| P0-X | ρ1 = 0 with r_z ≥ 0: nonconvex for T/W ≳ 2.1 (numerics ≳1.7); GTPL T/W 1.27 open | M1 | PROVED (regime) | math/possibility-rho0.md |
| CSD2 | Degree-2 SDP lift exact for min-landing-error | M1 | **Unit-d gimbal discretization: LOSSY** (Lasserre-2 certified up to solver accuracy at N=3; case 12 2.5%, explicit R⁴ chain). **CSD2′ (δ=0 or convexified lens): UNBROKEN** (~4,500 solves, N≤48; stress PSD at every exact optimum, indefinite at every unit-d gap). **Variable throttle: LOSSY and gap grows with N** (12→68%, tends to the no-rate-limit value: genuine, not an artifact). Separate-axis lift CSD3: LOSSY. Altitude r_z≥0: exact; **glide slope can break it** (1.19% in 1/8 scenarios) | math/verifier-sdp-report.md, math/08, math/09 |
| CSD2′-T | Partial proof of CSD2′: T1 (terminal-state reduction), T2 (lift exact for every linear objective of the terminal (r,v) readout, all models ⇒ SDP computes the support function / convex hull of the reachable terminal set exactly), T3/T4 (stress / hemisphere certificates; continuous versions assume normal KKT), T5 index theorem (terminal-attitude case confirmed; FREE terminal attitude: sharper — exact iff crossings k ≤ p₀, residual class vanishes, under T5's nondegeneracy hypotheses, which hold at only 188/898 ≈ 21% of optima — the rest are certified by the direct stress test). 898 fresh optima: no gap | M1, fixed thrust, convexified lens | **CONFIRMED** (verify-sdp2: 0 BROKEN; minor fixes: κ sign, hypotheses D≻0, certification counts overstated, 'bang-bang' wording) | math/09, math/verify-sdp2-report.md |
| SDP-4.1 | For coplanar data (velocity-only, position-only, vertical-plane targets), every planar LICQ local min is a certified global optimum (incl. glide slope/altitude) | M1, fixed thrust | PROVED (proof-sdp; not yet attacked) | math/08 Thm 4.1 |
| SDP-2.4 | SDP exact ⇔ genuine optimum is a local min in ℝ⁴ ⇔ PSD stress matrix ⇒ a-posteriori certificate | M1, fixed thrust | PROVED (proof-sdp) | math/08 Thm 2.1/2.4 |
| HOP | Largest physically admissible nonconvexity (r_z ≥ 0): pad-launched hop (r0z=0, v0z 7.73–7.92 m/s, tf=4): reachable landing spots form a RING — hole radius 0.55→4.99 m around the pad; torque-coupled TVC: 1.74 m hole at v0z=8.0. Realistic in-air descent (50 m, −5 m/s, 4 m/s crossrange, tf=7): no dent > 0.016 m | M1, M3 (TVC) | NUMERICAL (proof-s: reduction + offset witnesses rigorous; hole not certifiable by quadratic/S-procedure bounds — needs 2D rigidity or validated branch-and-bound) | numerics/README.md, numerics/results/s5_annulus.png |

## What breaks LCvx, in one paragraph
LCvx works for 3DOF because the thrust direction is a free control. The relaxed (filled-in) thrust set is achievable
on average by rapid switching (Lyapunov/Aumann), so the reachable set is already convex. In 5DOF the thrust direction
is tied to a body axis that rotates at a finite rate (or with finite angular acceleration on the real TVC vehicle),
so it cannot switch. With a minimum throttle, "wasting" vertical impulse requires tilting, and maximal tilt forces a
single tilt direction. The average of a left-tilting and a right-tilting maneuver is therefore not flyable, yet any
convex program that contains both must contain their average.

## Practical implications for GTPL (solver-v2; final)
- **Recommended planner B (attitude-aware convex guidance):** 3DOF warm start → SCvx steps on the body angular-
  acceleration profile, each followed by the EXACT convex inner SOCP given attitude (C-6). Every accepted iterate is
  flyable; certificate = fine-grid physical limits + open-loop 6DOF replay. Open loop: within 0.04% of the best
  nonconvex 6DOF optimum (IPOPT multistart), 8/8 certified.
- **Closed loop** (6DOF, same tracker for all, 1 Hz replans, wind/noise/Isp error; success = |v|≤1 m/s, ≤1 m, ≤5°):
  in-air (40 runs): current flight LCvx (A) 28%, 3DOF + rate limits (C) 95%, **B 100%** (median 0.20 m/s, 3 cm; worst 0.38 m/s, 9 cm);
  pad hop (30 runs): A 0%, C 100% (+23% fuel), **B 97%**. Open loop: B within 0.012% of IPOPT 6DOF, ≤0.85% above the 3DOF lower bound.
- **Compute:** mean 0.37 s / max 1.33 s per replan (loaded Mac); flight port needs a hard time budget + fallback to last certified plan (solver/PORTING.md).
- **Also fix regardless of guidance:** the flight MPC overstates angular authority ~4.6× (inertia/lever arm mismatch).
- 15 pytest tests pass (orchestrator-verified). Solver's elementary claims N1–N7 **LEAN** (28 theorems, standard axioms; orchestrator-verified). Formalization caught one error: the documented standalone φ-axis gimbal-rate condition is FALSE (`LcvxSolver.phi_rate_heuristic_false`), but the constraint pair the planner actually imposes is proved sufficient (`gimbal_rate_pair`), so no code change was needed.
- **Pad hops:** the 3DOF relaxation reports 'optimal' at all 20 targets of a 4 s hop map, but neither B nor IPOPT finds
  any flyable plan at 11 of them (all 8 with v0z ≥ 6.5 m/s + 3 at 6 m offset): the nonconvexity showing up in practice
  ("no plan found" is numerical evidence, not a proof of infeasibility). Documented failure mode of B: one stall where IPOPT finds a plan.
- Details: solver/README.md, solver/RESULTS.md.

### Earlier notes
- The current 3DOF guidance asks for thrust-direction changes ~10³× faster than the vehicle can rotate, and is not
  relaxation-tight on min-thrust arcs (context/vehicle.md).
- The theory points to: an attitude-profile outer loop + an exactly convex inner problem (C-6/C-U), with SDP-lift
  certificates (if CSD2 holds) to certify global optimality or infeasibility.
