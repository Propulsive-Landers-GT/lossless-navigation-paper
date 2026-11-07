# CLAIMS map: paper statement → registry row → status → proof file → Lean name

Maintained by [paper-writer]. Revision 4, 2026-11-07 (revision 3 added TVC-1, CSD2′ partial theorems and the practical section; revision 4 fills the last placeholders and updates the pure-TVC status). Sources:
- comms/CLAIMS.md;
- the referee reports math/verify-imp-report.md and math/verify-pos6-report.md (no claim BROKEN);
- lean/MODEL.md, lean/POSITIVE.md, lean/SLICE.md and comms/reports/lean.md, with the orchestrator-verified full build (all axioms = [propext, Classical.choice, Quot.sound]).

Paper tags:
- `[Lean-checked]`: FORMALIZED.
- `[proved; independently refereed]`: CONFIRMED by a referee.
- `[proved; refereed, statement as repaired]`: the referee said NEEDS FIX, and the paper prints the repaired statement.
- `[proved in project notes; registry status CLAIMED]`: not refereed. Only TRIV (Prop 2.7) and P-3 (Rem 3.22) remain in this state.
- `[numerical evidence only]`.

| Paper label | Statement | CLAIMS row(s) | Status (registry / referee) | Repair applied in paper | Proof file | Lean name(s) |
|---|---|---|---|---|---|---|
| **Main Theorem** (§1) | no lossless uniform convex relaxation, altitude + glide slope, every tf, free/upright terminal attitude, 5DOF + kinematic 6DOF | A + B*, P-B* | CONFIRMED + FORMALIZED | — | math/02 §2, §10 | `no_lossless_relaxation_constrained_5dof`, `no_losslessFor_relaxation_constrained_5dof`, `no_lossless_relaxation_constrained_upright_5dof`, `no_lossless_relaxation_constrained_6dof`, `no_lossless_relaxation_constrained_upright_6dof` |
| Lem 2.1 (lem:cop) | centre-of-percussion identity | P-K3, FLAT | CONFIRMED (verify-pos6) | — | math/02 Lemma 6.4 | — |
| Def 2.2–2.4, 2.6 | feasible sets, uniform relaxation, lossless forms, state-linear | A, D (defs) | — | — | math/02 §1.4, §11.1 | `UniformConvexRelaxation`, `IsLossless`, `IsLosslessFor`, `StateLinearRelaxation` |
| Prop 2.5 (prop:opt-feas) | LCvx form ⇒ feasibility form | A | FORMALIZED | — | math/02 Prop 1.5 | `IsLosslessFor.isLossless` |
| Prop 2.7 (prop:triv) | trivial convex-hull reformulation | TRIV | CLAIMED (not refereed) | — | math/02 Prop 11.3 | — |
| Thm 3.1 (thm:A) | Theorem A | A | CONFIRMED / FORMALIZED | — | math/02 §2 | `theoremA`, `not_isLossless_of_not_convex`, `not_isLosslessFor_of_not_convex` |
| Cor 3.2 (cor:A) | affine pushforward; ε-lossless | A, P-ε | FORMALIZED (i) / CONFIRMED (ii) | — | math/02 Cor 5.2 | `IsLossless.convex_affine_image` |
| Lem 3.3 (lem:reduction) | reduction to velocity increments | P-B | FORMALIZED | — | math/02 Lemma 3.1 | `snd_image_landingSet`, `convex_reachSet_of_convex_landingSet` |
| Thm 3.4 (thm:B) | Theorem B, variants F and T | B, P-B | F: FORMALIZED (incl. mass model); T: CONFIRMED | — | math/02 §4; App. A | `not_convex_reachSet`, `not_convex_landingSet`, `no_lossless_relaxation_5dof`, `no_losslessFor_relaxation_5dof`, `no_lossless_relaxation_5dof_mass` |
| Thm 3.5 (thm:Q) | ball bound Γ_F | P-Q, P-ε | CONFIRMED | Q_T: valid only under δ+ωtf/2 ≤ π/2; only the in-hypothesis value 3.24 m/s is quoted (rows 3–4 of the math/02 table dropped) | math/02 §5; App. A | — |
| Prop 3.6 (prop:L) | all horizons | P-L, P-L0 | CONFIRMED | — | math/02 §7–8 | — |
| Thm 3.7 (thm:Bstar) | Theorem B*: all variants + quantitative | B*, P-B*, P-B*env | CONFIRMED; qualitative FORMALIZED (constant accel. bounds, free + upright, 5DOF + kinematic 6DOF) | — | math/02 §10; App. B | `not_convex_constrainedLandingSet`, `exists_switchTime`, `not_convex_constrainedLandingSetUp`, `not_convex_constrainedLandingSet6(Up)`, headline names above |
| Rem 3.9 (rem:thin) | gap ≈1.3e-5 m rigorous | P-B* | CONFIRMED | — | math/02 Rem 10.2 | — |
| Lem 3.10 (lem:LS) | RR-LS (i)–(ii) | RR-LS, LS | CONFIRMED + FORMALIZED | — | math/redteam-reform §4 | `not_lineSearch_lossless`, `symmetric_supply`, `not_lineSearch_lossless_of_symmetry` |
| Cor 3.11 (cor:LS) | free-tf line search fails on windows | RR-LS (iii), P-tf | NEEDS FIX → repaired | window W=[t_a,t_b], s*<t_a, (S1)–(S3) at t_a with a_max at t_b, m0−αρ2 t_b ≥ m_dry; ρ1-fuel window explicitly rejected | math/02 Cor 10.4; App. B | abstract part only |
| Thm 3.12 (thm:D) | Theorem D (abstract) | D, P-D | CONFIRMED + FORMALIZED | Cor D.1 text: δ ≤ π/4; extra vertical constraints must be satisfied by the witness | math/02 §11 | `StateLinearRelaxation.convexHull_subset`, `minError_lossy`, `convex_superset_gap`, `lossy_of_gap` |
| Lem 3.13 (lem:W) | Wirtinger modulo affine | S-W | CONFIRMED + FORMALIZED | — | math/07 §2; App. C | `Slice.periodic_wirtinger`, `wirtinger_scalar`, `wirtinger_lipschitz` |
| Thm 3.14 (thm:S) | Theorem S (Lemma S in regime) + hard-landing D | S, S-M, S-T | CONFIRMED; Ω-ranges NEEDS FIX → repaired; explicit instance FORMALIZED | certified Ω: (0,0.55] δ=0; [0.004,0.46] δ=5°; [0.038,0.34] δ=10° (T=2 s); positive lower end explained | math/07; App. C | `Slice.master_inequality`, `Slice.dent`, `Slice.lemmaS`, `Slice.instL_norm_ge`, `Slice.theoremD_hard_landing` (a≡12, δ=0, ω=0.1, ωtf≈0.35, dent ≥ 1 m) |
| Thm 3.15 (thm:Aopt) | Theorem A-opt | L-Aopt | CONFIRMED (wording fix) + FORMALIZED | conclusion = conv V over finite mixtures, not V** | math/redteam-lift §5 | `Slice.CostRelaxation.aOpt`, `aOpt_finset`, `value_le_convexCombination` |
| Prop 3.16 (prop:T) | Prop T | L-Aopt | NEEDS FIX → repaired; abstract part FORMALIZED | variant T (b(0)=b(tf)=e_z); variant F with ωtf in place of ωtf/2 | math/redteam-lift §5.3 | `no_valueLossless_of_strict` (abstract; model facts F1–F5 not formalized) |
| Prop 3.17 (prop:P0R) | ρ1=0 velocity set | P0-R, RR-R0 | F: CONFIRMED; tent NEEDS FIX → repaired | tent: convex if ≤ π/2, nonconvex if π/2 < · ≤ π, open beyond | math/possibility-rho0 §1 | — |
| Thm 3.18 (thm:P0F) | ρ1=0 landing set nonconvex | P0-F | CONFIRMED | — | math/possibility-rho0 §2; App. D | — |
| (text after 3.18) | P0-X | P0-X | CONFIRMED (clarifications) | threshold ≈2.1 only as ωtf→0; 2.16/2.38/2.78 at ωtf=0.1/0.3/0.5 (δ=15°) | math/possibility-rho0 §2.3 | — |
| Thm 3.19 (thm:6kin) | kinematic 6DOF | B6 (Thm K) | CONFIRMED + FORMALIZED | Cardan corner 21.09° (§2); B* box variant needs ωs* ≤ δ_in | math/02 Thm 6.2; adversary-6dof Thm K | `Attitude6Admissible.toM1`, `lift_admissible`, `not_convex_landingSet6`, `not_convex_constrainedLandingSet6(Up)`, `no_lossless_relaxation_constrained(_upright)_6dof` |
| Thm 3.20 (thm:6dyn) | independent torque (D, D*) | P-E, B6-D, B6-D* | CONFIRMED (D* unconstrained core) | state-constraint clause flagged as inherited, not re-derived; no "TVC torque may be added" remark in paper | adversary-6dof §2 | — |
| Thm 3.21 (thm:E0) | pure TVC, ω⊥(tf)=0, tilt free | B6-TVC, B6-E0 | NEEDS FIX → repaired | constant mass explicit; roll-rate zero as model restriction; regime (H-f) strict + (H-π); closure (duty-cycle) step in App. D | adversary-6dof §3.5, §6; App. D | — |
| Thm 3.22 (thm:TVC1) | pure TVC upright at rest, r_z ≥ 0 + glide slope, GTPL wet, tf=1 s, s*=0.25 s; margins G_w−U = 9.96e-6 m (cone, 13.7 %) / 7.57e-6 m (Cardan box, 5.4 %) / 2.90e-6 m (free roll, 4.0 %); d* = 9.63e-6 / 7.34e-6 / 2.81e-6 m | TVC-1, TVC-1q, TVC-B, TVC-1R, TVC-L | CONFIRMED (verify-tvc, exact arithmetic, after repairs W1–W3); d* float-evaluated | W1 explicit fast ±δ bang-bang witness; W2 rigorous gyro weight; W3 sup-based remainder constants. Scope: constant mass, unlimited gimbal rate, tf = 1 s. TVC-R / TVC-α / TVC-L∞: nonconvex NUMERICALLY in the fully realistic model (rate-limited box, mass depletion, roll free) at tf = 3/5/5/7 s (1.26e-2 / 4.8e-3 / 2.8e-2 / 3.3e-2 m), unproved. Open: tf ≥ 2 s certificate (throttle-near-s* obstacle, ~300×; route: G_w-relative penalty + Riccati certificate), jerk-multiplier rate-limited certificate, mass depletion, free tf, tumbling lemma for tf > 2.3 s | math/06; math/verify-tvc-report.md | — |
| Rem 3.22 (rem:3dof) | exact 3DOF F convex | P-3 | CLAIMED (not refereed) | — | math/02 Prop 8.2 | — |
| Thm 4.1 (thm:CW) | C-W (+ C-F) | C, C-W, C-F | CONFIRMED; C-F FORMALIZED, C-W partly | Slater caveat: uniform Slater impossible for constraints active at touchdown (glide-slope apex, r_z(tf)=0) | math/04 §3; App. D | `relaxed_subset_original`, `origFeas_eq_relFeas`, `convex_origFeas` (Aumann hyp.) |
| Thm 4.2 (thm:CS) | C-S / C-D | C-S/C-D | NEEDS FIX (minor) → repaired; partly FORMALIZED | meagre set in admissible class (proof route stated); velocity constraints ⇒ λ_v BV, structure only on constraint-free intervals | math/04 §5 | `PMPConclusion.lossless_ae_off_degenerate`, `lossy_subset_degenerate_minThrottle`, `lossless_ae_of_ND` |
| (text) | C-X, C-K | C-X, C-K | C-X CLAIMED; C-K FORMALIZED | — | math/04 §6–7 | `purification_three` |
| Thm 4.3 (thm:CU) | C-U | C-U | CONFIRMED | stated without path constraints | math/04 §9 | — |
| Thm 4.4 (thm:C6) | pure TVC exactly convex given b | C-6 | CONFIRMED + FORMALIZED (constant mass) | — | math/04 §8; App. D | `torque_balance_iff`, `convex_tvcSet`, `convex_feasData_M3b` |
| Prop 4.5 (prop:X5) | X5 / RR-P (M1 only) | X5, RR-P | NEEDS FIX → repaired | added ωtf ≥ ∠(b0,b_f) when b_f prescribed | math/redteam-reform §3.1 | — |
| (text after 4.5) | C-Y thinness | C-Y | CONFIRMED | 3.5e-6 rad/s at ρ1=400 N; 1.8e-5 at 300 N; b0 in plane, in-plane rate | math/04 §10 | — |
| Lem 4.6 (lem:shor) | Shor = Hilbert sphere | L-SD2 (lemma) | not disputed | — | math/08 Lemma 1.1 | — |
| Thm 4.7 (thm:stress) | stress certificate, local⇒global | SDP-T1, SDP-T4 | CONFIRMED | — | math/08 §2 | — |
| Thm 4.8 (thm:coplanar) | coplanar certified subclass | SDP-P | NEEDS FIX → repaired | glide-slope clause removed; only Gram-linear constraints (altitude); glide slope a posteriori | math/08 Thm 4.1 | — |
| (text after 4.8) | rank ≤ 4 | SDP-R4 | NEEDS FIX → repaired | added E_w ⊆ W step; rank ≤ 4 when data span 3D, ≤ 5 coplanar | math/08 Prop 5.1 | — |
| (bullet) | unit-d lift lossy (case 12) + Prop 6.1 mechanism | L-SD2, SDP-L | numerical / CONFIRMED (Prop 6.1) | consequence toned down: cancellation not automatic; continuous-time vanishing = CSD2′ | math/08 §6 | — |
| (bullet) | variable-throttle lift lossy | V-THR | certified at N=3 (order-2 Lasserre) | — | math/08 §7.1 | — |
| Conj 4.9 (conj:csd2p) | CSD2′ | CSD2′, CSD2″ | OPEN (unbroken, ~4,500 solves; 0 gaps on 509 former unit-d gap instances) | stated as a conjecture; CSD2″ stated as an open problem (residual k = p₀+1 with fixed terminal attitude; continuous-time normality); no active prover | math/09 §0 | — |
| (list after 4.9) | T1 alignment; T2 every linear objective of the terminal readout exact (closes SDP-F) | CSD2′-T1, T2 | CONFIRMED (verify-sdp2) | T2 scope: readout objectives only, not attitude costs | math/09 §2 | — |
| (list after 4.9) | T3/T4 stress certificate, hemisphere/Picone; T5 index identity; P6, P7 | CSD2′-T3, T4, T5, P6, P7 | CONFIRMED / NEEDS FIX → repaired | T3/T4 continuous given normal KKT (automatic only with free terminal attitude); discrete T4 rigorous; T5 free-attitude: exact ⇔ k ≤ p₀; hypotheses hold at only 188/898 (9/17 c1) optima, direct stress test certifies all 17; Aumann selection = full-thrust direction selection in the cap, not a ±δ law | math/09 §3–7 | — |
| (bullets §4.5) | unit-d lossy (Lasserre-2 certified at small N); throttle lift gap 12→68 % with N; CSD3 lossy; glide slope 1.19 % lossy; altitude exact | L-SD2, V-THR | numerical / certified to solver accuracy | — | math/verifier-sdp-report.md | — |
| §6 (sec:practice) | planner B; open loop within 0.012 % of IPOPT, ≤ 0.85 % above 3DOF LB, 8/8 certified; closed loop in-air A 28 % / C 95 % / B 100 %, hop A 0 % / C 100 % (+23 % fuel) / B 97 %; 3DOF relaxation accepts 11/20 hop targets where neither B nor IPOPT finds a plan | solver/CLAIMS.md 1–17 (C-U, C-6, Lemma 8.1, N1–N7, P22) | NUMERICAL (results); N1–N7 FORMALIZED (28 theorems, lean/SOLVER.md): N1 tighter (|θ|,|φ| ≤ δ); N2 standalone φ heuristic refuted, imposed pair proved incl. FOH; N5 continuous time only; N7 V3 ≤ V5 ≤ V6 incl. free tf (grid not covered); C-6/torque balance/P22 FORMALIZED | SCvx convergence not claimed | solver/README.md, RESULTS.md, lean/SOLVER.md | `LcvxSolver.gimbal_box_angles`, `gimbal_rate_pair`, `phi_rate_heuristic_false`, `foh_gimbal_rate`, `throttle_slew_foh`, `chord_bound`, `dir_accel_bound_calculus`, `euler_axisymmetric`, `value3_le_value6`, `value3_le_value6_freeTime` |
| Lem A.1, A.3 | triangle inequality; rigidity | P-B | FORMALIZED | — | math/02 §4.1 | `inner_triangle`, `inner_triangle_eq_lateral`, `lateral_eq_of_inner_ge` |
| Lem A.4 | support bound | P-Q | CONFIRMED | — | math/02 Lemma 5.1 | — |
| Prop C.1 (prop:master) | master inequality | S-M | CONFIRMED + FORMALIZED (constant mass) | — | math/07 Prop M | `Slice.master_inequality` |
| §5 (all) | numerics | HOP, S-HOP, S-GTPL, S-LH, B6-E | NUMERICAL | — | numerics/README.md | — |

## Remaining placeholders
None. CSD2′ and CSD2″ are stated as an open conjecture and an open problem, not as placeholders.

## Kept out of theorem statements
- S-GTPL and the hole at hop data (S-HOP): numerical only.
- OM exactness: cited as context.
- P0-TVC, P0-T: text mentions only.
- Min-fuel value-losslessness: open.
