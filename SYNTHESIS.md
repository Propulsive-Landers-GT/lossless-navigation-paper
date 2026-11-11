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
**Also machine-checked with explicit mass depletion** (thrust T ∈ [ρ1,ρ2], ṁ = −αT, m ≥ m_dry; `…_constrained_5dof_mass`
and upright/6DOF variants), on **free-final-time windows**, quantitatively, and **instantiated at GTPL's wet constants**
(400–1000 N, 79.88/55.88 kg, Isp 180 s, 15° cone, any tf ≤ 42 s or any window ⊆ (0,42]): `LcvxObstruction.gtpl_no_lossless_upright_6dof_mass`,
`gtpl_no_lossless_freeTime_mass` (kinematic rate-limited 6DOF/5DOF model; orchestrator-verified build + axioms).

**Real GTPL actuation (pure TVC, gimbal = torque):** computer-assisted proofs, each independently re-certified in exact
arithmetic, that the landing set is nonconvex (GTPL constants, upright at rest, constant mass, unlimited gimbal rate,
roll held, 15° cone): tf = 1 s (altitude + glide slope; also Cardan box and roll-free), **tf = 2 s with no tilt cap**
(altitude + glide slope), and **tf = 3 s and 5 s for the tilt-capped class** (cap 80° or 30°; altitude r_z ≥ 0). ⇒ no uniform
lossless convexification for those problem classes either. tf = 7 s, the 100°/s gimbal limit and mass depletion: numerical only.

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
   - **Sound single convex program (added 2026-11-10):** lossless means sound and complete. Dropping completeness, one SOCP in
     centre-of-percussion coordinates returns only flyable plans for the pure-TVC vehicle (Theorem F, row F-SOUND below). This is
     the recommended landing algorithm (`LANDING-ALGORITHM.md`).
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
| B* | Dive-then-brake exposed face ⇒ F nonconvex with altitude/glide slope, any tf, upright landing, bounded free-tf window | M1; kinematic 6DOF (proper rotations, free roll); independent-torque 6DOF | **LEAN** for M1 + kinematic 6DOF, constant acceleration bounds (constant mass), any tf>0, any constraint set ⊇ glide-slope cone, upright or free terminal attitude: `no_lossless_relaxation_constrained_5dof`, `…_upright_5dof`, `…_constrained_6dof`, `…_upright_6dof` (+ optimisation form for every cost). Orchestrator-verified: full build, standard axioms only. Also LEAN (lean-tvc): B* with mass depletion α>0 for every tf, free-tf windows, quantitative Step-7 bound, GTPL instance. Not in Lean: torque-limited (pure-TVC) 6DOF analysis | lean/…/DiveBrake.lean, Upright.lean, SixDOF.lean, Main.lean |
| RR-LS | Line search over tf cannot rescue LCvx (needs B*'s braking condition / time window) | M1 | abstract lemma **LEAN** (FreeTime.lean); concrete instance on paper | math/redteam-reform.md §4 |
| A-opt, T | Value-lossless on F ⇒ V equals its finite-mixture convex envelope on F; cost ∫b·e_z violates it (upright variant) | abstract / M1 | PROVED (referee); A-opt + abstract Prop T **LEAN** (`Slice.CostRelaxation.aOpt`, `no_valueLossless_of_strict`) | math/redteam-lift.md §7, lean/SLICE.md |
| D | Per-instance min-landing-error: state-linear relaxations (affine readout + convex penalty) lossy | M1 | abstract theorem **LEAN** (TheoremD.lean); hard-v(tf)=0 instance via Lemma S (proved on paper) | math/02, threads/theorem-D.md |
| S | Straight-below landing infeasible, offset feasible (vertical instance) ⇒ Theorem D with hard v(tf)=0 lossy | M1; δ+ωtf<π/2; min-throttle T/W > 1/cos(δ+ωtf) (cannot hover at min throttle) | PROVED (referee-confirmed; Ω-range lower ends fixed) + **LEAN** on an explicit instance (a≡12 m/s² fixed thrust, ω=0.1 rad/s, no gimbal, r_z≥0, any 3D path incl. coning): every landing offset ≥ 1 m, L nonconvex, every state-linear relaxation reports error 0 vs true ≥ 1 m (`Slice.lemmaS`, `Slice.theoremD_hard_landing`; Wirtinger `Slice.periodic_wirtinger`, master inequality). Orchestrator-verified | math/07, lean/SLICE.md |
| S-GTPL | Lemma S at GTPL constants (hovering possible at min throttle) | M1 | NUMERICAL (gap ≈1 cm in ℓ; optimizers land 1.5–2.4 m off-axis) | math/07, numerics s1 |
| FLAT | Centre-of-percussion identity: pure TVC ≡ zero-gimbal, torque-limited point thrust along b (+ roll-rate term) | pure TVC, ε const | **LEAN** (`TVC.cop_identity_E3`, `cop_identity_roll`, `convex_tvcSet_iff`); TVC-1 logical skeleton LEAN (`TVC.tvc1_main`) with the certificate and analytic reduction as explicit hypotheses | lean/TVC.md |
| B6-TVC | Pure-TVC F nonconvex (Thm E₀) | terminal r=v=0, ω⊥(tf)=0, tilt free; constant mass, ω3≡0 | PROVED, refereed (verify-pos6 NEEDS FIX: constant mass + closure step, applied in paper/math/06) | math/adversary-6dof-report.md, math/06 |
| B6-TVC-up | Pure-TVC F nonconvex, upright at rest + r_z ≥ 0 + glide slope (**the real GTPL actuation**) | pure TVC, GTPL wet constants, constant mass, unlimited gimbal rate, cone 15° or Cardan box ±15°, roll held or free, tf = 1 s | **COMPUTER-ASSISTED PROOF, CERTIFIED IN EXACT ARITHMETIC** (verify-tvc: exact rational/Arb rebuild, exact integer-determinant PD check; margins 13.7% cone / 5.4% box / 4.0% free roll; certified dist(θ_m,F) ≥ 9.6e-6 m). Repairs: witness replaced by explicit fast bang-bang gimbal (needs unlimited gimbal rate); free-roll gyro weight made rigorous. NUMERICAL at tf=5/7 s (≈3 cm). **Fully realistic model (100°/s box gimbal from centred, mass depletion, roll free, r_z ≥ 0, upright at rest): NUMERICALLY NONCONVEX at every horizon tried** (dive-then-brake face; gaps 1.26e-2 m tf=3, 4.8e-3 m tf=5, 2.8e-2 / 3.3e-2 m tf=5/7) — 'nonconvex but unproved'. Open (rigor): tf ≥ 2 s certificate (structural loss ~300× on this face; route: penalty localized to G_w + state-space Riccati certificate), rate-limited certificate (jerk multiplier), mass depletion, free tf, tumbling lemma | math/06, math/verify-tvc-report.md |
| TVC-2/3/5 | Pure-TVC F nonconvex at realistic horizons via a backward Riccati/DP certificate (O(N), up to 1500 cells) | pure TVC, GTPL wet, constant mass, roll held, cone 15°, unlimited gimbal rate, upright at rest; tf=2 s uncapped (r_z≥0 + glide slope); tf=3,5 s tilt-capped class (80° or 30°, r_z≥0) | **COMPUTER-ASSISTED, CERTIFIED IN EXACT ARITHMETIC** (verify-tvc independent Arb recursion; adversary-6dof: TVC-2 survives). Margins: tf=2 8.06% (dist ≥ 9.2e-5 m); tf=3 4.16% (≥ 4.8e-5 m); tf=5 0.20% (thin but rigorous; ≥ 2.3e-6 m). Not certified: tf=7 (fails by 4.8%), uncapped tf>2.3 s (tumbling lemma), box/roll-free beyond tf=1, mass depletion, gimbal-rate limit, free tf | math/06 §5.7–5.9, math/verify-tvc-report.md §9–11 |
| C | LCvx exact given attitude profile b(t); strong form under PMP + checkable non-degeneracy | M1 | PROVED; **LEAN**: C-3 pointwise lemma (`LcvxPositive.C3_headline`), C-S/C-D2 (const. mass), discrete purification C-K, C-F (`convex_origFeas`, with Aumann as explicit hypothesis), C-6 TVC convexity — 35 theorems, standard axioms only; PMP & Aumann only as explicit named hypotheses | math/04, lean/POSITIVE.md |
| C-Y | 3DOF LCvx optimum exactly 6DOF-flyable for GTPL essentially never (initial-rate window ≈3.5e-6 rad/s at ρ1=400 N) | pure TVC | PROVED, refereed CONFIRMED | math/04 |
| X5 | Pointing cone ≤ gimbal ⇒ 5DOF = 3DOF, LCvx exact (needs ωtf ≥ ∠(b0,b_f) if terminal attitude prescribed) | M1 only (pure TVC: effective gimbal 0) | PROVED, refereed (hypothesis added) | math/redteam-reform.md |
| P0-R | ρ1 = 0: velocity set R convex iff δ+ωtf ≤ π/2 | M1 | PROVED | math/possibility-rho0.md |
| P0-F | ρ1 = 0 still gives nonconvex F_tf (coast-while-rotating; thrust on/off kink) ⇒ no 'possible iff ρ1=0' dichotomy | M1, α=0, δ<π/4, ωtf<π/2−2δ | PROVED | math/possibility-rho0.md |
| P0-X | ρ1 = 0 with r_z ≥ 0: nonconvex for T/W ≳ 2.1 (numerics ≳1.7); GTPL T/W 1.27 open | M1 | PROVED (regime) | math/possibility-rho0.md |
| CSD2 | Degree-2 SDP lift exact for min-landing-error | M1 | **Unit-d gimbal discretization: LOSSY** (Lasserre-2 certified up to solver accuracy at N=3; case 12 2.5%, explicit R⁴ chain). **CSD2′ (δ=0 or convexified lens): UNBROKEN** (~4,500 solves, N≤48; stress PSD at every exact optimum, indefinite at every unit-d gap). **Variable throttle: LOSSY and gap grows with N** (12→68%, tends to the no-rate-limit value: genuine, not an artifact). Separate-axis lift CSD3: LOSSY. Altitude r_z≥0: exact; **glide slope can break it** (1.19% in 1/8 scenarios) | math/verifier-sdp-report.md, math/08, math/09 |
| CSD2′-T | Partial proof of CSD2′: T1 (terminal-state reduction), T2 (lift exact for every linear objective of the terminal (r,v) readout, all models ⇒ SDP computes the support function / convex hull of the reachable terminal set exactly), T3/T4 (stress / hemisphere certificates; continuous versions assume normal KKT), T5 index theorem (terminal-attitude case confirmed; FREE terminal attitude: sharper — exact iff crossings k ≤ p₀, residual class vanishes, under T5's nondegeneracy hypotheses, which hold at only 188/898 ≈ 21% of optima — the rest are certified by the direct stress test). 898 fresh optima: no gap | M1, fixed thrust, convexified lens | **CONFIRMED** (verify-sdp2: 0 BROKEN; minor fixes: κ sign, hypotheses D≻0, certification counts overstated, 'bang-bang' wording) | math/09, math/verify-sdp2-report.md |
| SDP-4.1 | For coplanar data (velocity-only, position-only, vertical-plane targets), every planar LICQ local min is a certified global optimum (no state constraints, or altitude-type constraints; glide-slope clause removed as unproved) | M1, fixed thrust | PROVED, refereed (verify-pos6: NEEDS FIX applied) | math/08 Thm 4.1 |
| SDP-2.4 | SDP exact ⇔ genuine optimum is a local min in ℝ⁴ ⇔ PSD stress matrix ⇒ a-posteriori certificate | M1, fixed thrust | PROVED, refereed CONFIRMED (verify-pos6) | math/08 Thm 2.1/2.4 |
| HOP | Largest physically admissible nonconvexity (r_z ≥ 0): pad-launched hop (r0z=0, v0z 7.73–7.92 m/s, tf=4): reachable landing spots form a RING — hole radius 0.55→4.99 m around the pad; torque-coupled TVC: 1.74 m hole at v0z=8.0. Realistic in-air descent (50 m, −5 m/s, 4 m/s crossrange, tf=7): no dent > 0.016 m | M1, M3 (TVC) | NUMERICAL (proof-s: reduction + offset witnesses rigorous; hole not certifiable by quadratic/S-procedure bounds — needs 2D rigidity or validated branch-and-bound) | numerics/README.md, numerics/results/s5_annulus.png |

| F-SOUND | **Theorem F.** Every feasible point of the landing algorithm's SOCP (path of the centre of percussion, quintic spline, limits imposed as convex restrictions on Bezier control tuples) is a trajectory of the pure-TVC model that starts from the given position, velocity, attitude, rate and gimbal deflection, lands at rest upright, and keeps throttle, gimbal and tilt within limits at every instant | pure TVC, roll rate zero, mass depletion, centre of percussion fixed in the body (ε = J_t/(mL) constant) | PROVED on paper (6 lemmas); Lemma 1 = FLAT is **LEAN**; every lemma tested (`solver/tests/test_flat.py`); 458 feasible random plans with no violation; open-loop replay within 23 nm. Not in Lean. Slew limits and sampled state constraints are outside the theorem | math/10-landing-proof.md |
| F-INC | The landing algorithm is incomplete (rejects some flyable landings), as Theorem A requires of any sound convex program with affine data entry | same | PROVED (one line from A); size NUMERICAL: +0.10 % fuel at the operating final time, +0.04 to +0.22 s minimum final time in-air, up to +0.41 s on 4 s hops, 4 of 9 flyable cells kept on the hop map | math/10 §9, solver/RESULTS-FLAT.md |
| RING-TVC | On the solver's planning model (pure TVC, throttle 440 to 920 N, gimbal 10°, tilt 20°, roll rate zero), launch at 6.3 m/s, t_f = 4 s: landings 1, 2, 3 m away exist, a landing straight back down does not | pure TVC planning model | NUMERICAL (IPOPT, symmetric and 9 asymmetric starts; not a proof of infeasibility) | AUDIT-2026-11.md §2, solver/scripts/audit_hop_ring*.py |
| SCVX-SLACK | **The LCvx thrust slack survives inside 6-DOF successive convexification.** At a local minimum (or converged iterate) of the relaxed discrete problem, lossy nodes cannot steer the terminal conditions; so at most 3 nodes are lossy when every 4-node set steers | full rigid body, RK4, 25 nodes; free or fixed final time; path constraints via tail/fold versions | LEAN (separate project, not rebuilt here) | `scvx-thrust-relaxation/README.md`, `scvx-thrust-relaxation/lean` |
| SCVX-NUM | No lossy node in four solved cases on Szmuk's vehicle; steering certified by interval arithmetic | same | NUMERICAL (one case re-run) | `scvx-thrust-relaxation/solver/results` |
| SDP-6DOF | One semidefinite program for the rigid-body problem is far from tight (bound 1.557 vs optimum 1.316) | rigid body, N = 10, fixed t_f | NUMERICAL | `scvx-thrust-relaxation/solver/sdp_relaxation.py` |

## What breaks LCvx, in one paragraph
LCvx works for 3DOF because the thrust direction is a free control. The relaxed (filled-in) thrust set is achievable
on average by rapid switching (Lyapunov/Aumann), so the reachable set is already convex. In 5DOF the thrust direction
is tied to a body axis that rotates at a finite rate (or with finite angular acceleration on the real TVC vehicle),
so it cannot switch. With a minimum throttle, "wasting" vertical impulse requires tilting, and maximal tilt forces a
single tilt direction. The average of a left-tilting and a right-tilting maneuver is therefore not flyable, yet any
convex program that contains both must contain their average.

## Practical implications for GTPL: update, November 2026
- **Recommended: the landing algorithm (planner F)**, [`LANDING-ALGORITHM.md`](LANDING-ALGORITHM.md). One SOCP per plan in
  centre-of-percussion coordinates, no iteration, sound by Theorem F.
- **vs standard 6DOF SCvx (S) and planner B**, same plant, tracker, cases and seeds, each plan applied after its solver
  time, each planner at its sustainable replan rate (solver/RESULTS-FLAT.md §4): NUMERICAL.
  In-air (40): success S 40, B 36, F 40; lateral error median / max S 5.9 / 18.3 cm, F 0.2 / 1.1 cm; touchdown speed
  median / max S 0.23 / 0.58, F 0.19 / 0.29 m/s. Hops (30): success S 30, B 28, F 30; lateral S 3.9 / 8.2 cm, F
  0.4 / 2.0 cm; speed S 0.54 / 0.88, F 0.14 / 0.23 m/s; fuel F +5 %. Solver time per replan S 1.05 s, B 0.70 s, F 0.031 s (in-air means).
- With zero computation time and 1 Hz replans for all (the earlier protocol), lateral accuracy is a tie (3.1 cm in-air).
- **Correction:** the earlier statement that every practical method must iterate on the attitude was wrong
  (AUDIT-2026-11.md §4). The earlier notes below are kept as written.

## Practical implications for GTPL (solver-v2; superseded by the update above)
- **Recommended planner B (attitude-aware convex guidance):** 3DOF warm start → SCvx steps on the body angular-
  acceleration profile, each followed by the EXACT convex inner SOCP given attitude (C-6). Every accepted iterate is
  flyable; certificate = fine-grid physical limits + open-loop 6DOF replay. Open loop: within 0.012% of the best
  nonconvex 6DOF optimum (IPOPT multistart), ≤0.85% above the 3DOF lower bound, 8/8 certified.
- **Closed loop** (6DOF, same tracker for all, 1 Hz replans, wind/noise/Isp error; success = |v|≤1 m/s, ≤1 m, ≤5°):
  in-air (40 runs): current flight LCvx (A) 28%, 3DOF + rate limits (C) 95%, **B 100%** (median 0.20 m/s, 3 cm; worst 0.38 m/s, 9 cm);
  pad hop (30 runs): A 0%, C 100% (+23% fuel), **B 97%**. Open loop: B within 0.012% of IPOPT 6DOF, ≤0.85% above the 3DOF lower bound.
- **vs standard 6DOF SCvx** (baseline S, `solver/gtpl_guidance/scvx6dof.py`, same model/constraints/certificate; solver/RESULTS-SCVX.md): NUMERICAL. Open loop (16 problems): tie, B +0.006 % / S +0.004 % vs IPOPT, all certified. Hop map: both 20/20 agree with IPOPT. Closed loop: in-air B 100 % / S 100 % (median touchdown 0.20 / 0.13 m/s), hops B 97 % / S 100 %; S ≈ 2× B's solver time per replan (0.62 vs 0.33 s mean in-air). **B does not outperform standard SCvx**; its advantages are speed and anytime feasibility.
- **Compute:** mean 0.37 s / max 1.33 s per replan (loaded Mac); flight port needs a hard time budget + fallback to last certified plan (solver/PORTING.md).
- **Also fix regardless of guidance:** the flight MPC overstates angular authority ~4.6× (inertia/lever arm mismatch).
- 15 pytest tests pass (orchestrator-verified; 27 as of 2026-11-10, with planner F's). Solver's elementary claims N1–N7 **LEAN** (28 theorems, standard axioms; orchestrator-verified). Formalization caught one error: the documented standalone φ-axis gimbal-rate condition is FALSE (`LcvxSolver.phi_rate_heuristic_false`), but the constraint pair the planner actually imposes is proved sufficient (`gimbal_rate_pair`), so no code change was needed.
- **Pad hops:** the 3DOF relaxation reports 'optimal' at all 20 targets of a 4 s hop map, but neither B nor IPOPT finds
  any flyable plan at 11 of them (all 8 with v0z ≥ 6.5 m/s + 3 at 6 m offset): the nonconvexity showing up in practice
  ("no plan found" is numerical evidence, not a proof of infeasibility). Documented failure mode of B: one stall where IPOPT finds a plan.
- Details: solver/README.md, solver/RESULTS.md.

### Earlier notes
- The current 3DOF guidance asks for thrust-direction changes ~10³× faster than the vehicle can rotate, and is not
  relaxation-tight on min-thrust arcs (context/vehicle.md).
- The theory points to: an attitude-profile outer loop + an exactly convex inner problem (C-6/C-U), with SDP-lift
  certificates to certify global optimality or infeasibility where they apply (fixed thrust; see CSD2 rows).
