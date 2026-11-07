# CLAIMS map: paper statement → registry row → status → proof file → Lean name

Maintained by [paper-writer]. Snapshot taken 2026-11-07 ~00:40–01:15 (system clock; updated after orchestrator commit b0dd184), from comms/CLAIMS.md, SYNTHESIS.md and lean/MODEL.md, plus [lean]'s DM confirming the build at eb2f850.

Two status columns are given because the claims registry often lags the orchestrator's synthesis:
- **Registry**: the status in comms/CLAIMS.md.
- **Synthesis**: the status in SYNTHESIS.md.

The paper tags each theorem as follows:
- `[Lean-checked]`: FORMALIZED.
- `[proved; survived attack]`: CONFIRMED, or survived an adversary attack.
- `[proved in project notes; registry status CLAIMED]`: written proof; the synthesis says PROVED, but the registry row is still CLAIMED.
- `[numerical evidence only]`.

**Action for orchestrator:** every row marked ⚠ is stated as a theorem in the paper on the strength of SYNTHESIS = PROVED, while its registry row still says CLAIMED. Either move the registry row to CONFIRMED, or tell me to demote the statement to a proposition-with-caveat or a conjecture.

| Paper label | Paper statement | CLAIMS row(s) | Registry | Synthesis | Proof file | Lean name(s) |
|---|---|---|---|---|---|---|
| Lem 2.1 (lem:cop) | Centre-of-percussion identity | P-K3, FLAT | CLAIMED / identity CONFIRMED (ε const, ω3=0) | numerical identity check | math/02 Lemma 6.4; math/checks/flat_output_tvc.py | — |
| Def 2.2–2.4, 2.6 | feasible sets, uniform relaxation, lossless (feasibility/LCvx/value), state-linear | A, D (defs) | — | — | math/02 §1.4, §11.1 | `UniformConvexRelaxation`, `IsLossless`, `IsLosslessFor`, `StateLinearRelaxation` |
| Prop 2.5 (prop:opt-feas) | LCvx form ⇒ feasibility form | A (scope) | FORMALIZED | LEAN | math/02 Prop 1.5 | `IsLosslessFor.isLossless` |
| Prop 2.7 (prop:triv) ⚠ | trivial convex-hull reformulation | TRIV | CLAIMED | — | math/02 Prop 11.3 | — |
| **Thm 3.1 (thm:A)** | Theorem A | A | CONFIRMED / FORMALIZED | LEAN | math/00 §3, math/02 §2 | `theoremA`, `not_isLossless_of_not_convex`, `not_isLosslessFor_of_not_convex` (Abstract.lean) |
| Cor 3.2 (cor:A) | affine pushforward; ε-lossless bound | A, P-ε | FORMALIZED (i) / CLAIMED (ii) | — | math/02 Cor A.2, Cor 5.2 | `IsLossless.convex_affine_image` |
| Lem 3.3 (lem:reduction) | reduction to velocity increments | P-B (part) | FORMALIZED | LEAN | math/02 Lemma 3.1 | `snd_image_landingSet`, `convex_reachSet_of_convex_landingSet` |
| **Thm 3.4 (thm:B)** | Theorem B, variants F and T | B, P-B | F: FORMALIZED; T: CLAIMED ⚠ | LEAN (F) | math/02 §4; paper App. A | `not_convex_reachSet`, `not_convex_landingSet`, `no_lossless_relaxation_5dof`, `no_losslessFor_relaxation_5dof`, `landingSet_nonempty` |
| Thm 3.5 (thm:Q) ⚠ | ball bound Γ_F, no ε-lossless | Q, P-Q, P-ε | CLAIMED | PROVED | math/02 §5; App. A | — |
| Prop 3.6 (prop:L) ⚠ | all horizons (free terminal), ρ1=0 long horizon | P-L, P-L0 | CLAIMED | — | math/02 §7.1, §8.4 | — |
| **Thm 3.7 (thm:Bstar)** | Theorem B*: altitude+glide slope, every tf, T′, free-tf window, quantitative | B*, P-B* | qualitative α=0: FORMALIZED; Steps 1–7 + Cor 10.4: survived adversary | PROVED (Lean pending for variants) | math/02 §10; App. B | `VStar_not_mem_WSet`, `witness_mem_glideSlope`, `not_convex_constrainedLandingSet`, `exists_switchTime`, `no_lossless_relaxation_constrained_5dof`, `no_losslessFor_relaxation_constrained_5dof`, `constrainedLandingSet_nonempty` |
| Rem 3.9 (rem:thin) | B* gap ≈1.3e-5 m (GTPL); B*-env | P-B*, P-B*env | survived adversary | — | math/02 Rem 10.2, §10.6 | — |
| Lem 3.10 (lem:LS) | RR-LS line-search lemma (abstract) | RR-LS, LS | CLAIMED (registry not updated) | PROVED (Lean pending) | math/redteam-reform §4 | `not_lineSearch_lossless`, `symmetric_supply`, `not_lineSearch_lossless_of_symmetry` (FreeTime.lean, commit 517f1bb; sorry-free; axiom audit after next full build, per [lean]) |
| Cor 3.11 (cor:LS) ⚠ | free-tf line search fails on compact windows | RR-LS + P-B* | CLAIMED | PROVED | math/redteam-reform §4(iii), math/02 Cor 10.4 | abstract part only |
| **Thm 3.12 (thm:D)** | Theorem D (abstract) | D, P-D | abstract FORMALIZED | PROVED | math/02 §11.2 | `StateLinearRelaxation.convexHull_subset`, `minError_lossy`, `convex_superset_gap` |
| Lem 3.13 (lem:W) | Wirtinger modulo affine | S-W | CLAIMED (used in S-T, survived attack) | PROVED | math/07 §2; App. C | `periodic_wirtinger`, `wirtinger_scalar`, `wirtinger_lipschitz` (Slice/Wirtinger.lean; **uncommitted, pending**) |
| **Thm 3.14 (thm:S)** | Theorem S (Lemma S in regime) + Theorem D hard landing | S, S-M, S-T | PROVED IN REGIME / SURVIVED adversary | PROVED | math/07 §2–4; App. C | `master_inequality`, `dent` (Slice/Master.lean; **pending**). Lemma S itself not formalized |
| Thm 3.15 (thm:Aopt) ⚠ | Theorem A-opt | L-Aopt | CLAIMED | PROVED | math/redteam-lift §5 | `mixing`, `aOpt`, `value_le_convexCombination` (Slice/AOpt.lean; **pending**) |
| Prop 3.16 (prop:T) ⚠ | Prop T (∫b·e_z cost) | L-Aopt | CLAIMED | PROVED | math/redteam-lift §5.3 | skeleton `no_valueLossless_of_strict` (**pending**) |
| Prop 3.17 (prop:P0R) ⚠ | ρ1=0: R convex iff δ+ωtf≤π/2 | P0-R (= RR-R0) | CLAIMED | PROVED | math/possibility-rho0 §1 | — |
| Thm 3.18 (thm:P0F) ⚠ | ρ1=0: F_tf nonconvex | P0-F | CLAIMED | PROVED | math/possibility-rho0 §2.2; App. D | — |
| (text) | P0-X (altitude, T/W≳2.1) | P0-X | CLAIMED | PROVED (regime) | math/possibility-rho0 §2.3 | — |
| (text) | separable monotone data maps; chord-rate SOCP | L-P1, T | CLAIMED | — | math/redteam-lift §4.2; redteam-reform §6 | — |
| Thm 3.19 (thm:6kin) ⚠ | kinematic 6DOF transfer | B6 (Thm K), B6-D | FIXED / CLAIMED | PROVED | math/02 Thm 6.2; adversary-6dof Thm K | `not_convex_landingSet6`, `not_convex_constrainedLandingSet6` (SixDOF.lean; **PENDING per [lean]**) |
| Thm 3.20 (thm:6dyn) ⚠ | independent-torque 6DOF (D, D*) | P-E, B6-D, B6-D* | CLAIMED (P-E survived adversary-6dof) | PROVED | math/02 §6.1–6.3; adversary-6dof §2 | — |
| Thm 3.21 (thm:E0) ⚠ | pure TVC, ω⊥(tf)=0, tilt free | B6-TVC, B6-E0 | CLAIMED (B6-TVC "PROVED (adversary-6dof)" in SYNTHESIS) | PROVED | adversary-6dof §3.5, §6 | — |
| **TODO box** | TVC-1 pure TVC upright at rest, r_z≥0 | B6-TVC-up | **OPEN** | OPEN (proof-tvc) | math/06 (CERT_TABLE placeholder) | — |
| Rem 3.22 (rem:3dof) ⚠ | exact 3DOF F convex | P-3 | CLAIMED | — | math/02 Prop 8.2 | — |
| Thm 4.1 (thm:CW) ⚠ | C-W (+C-F) | C, C-W, C-F | C-W: CLAIMED, PARTIALLY FORMALIZED; C-F: FORMALIZED (Aumann hyp.) | PROVED; LEAN (parts) | math/04 §3; App. D | `relaxed_subset_original`, `original_subset_relaxed`, `origFeas_eq_relFeas`, `convex_origFeas` (Positive/Convexity.lean, commit 455a288; Aumann as explicit hypothesis; axioms clean per lean/POSITIVE.md) |
| Thm 4.2 (thm:CS) ⚠ | C-S, C-D | C-S, C-D | CLAIMED; PARTIALLY FORMALIZED (PMP hyp.) | PROVED (under PMP); LEAN (parts) | math/04 §5 | `PMPConclusion.lossless_ae_off_degenerate`, `lossy_subset_degenerate_minThrottle`, `lossless_ae_of_ND` (Positive/PMP.lean) |
| (text) | C-X sharpness, C-K purification | C-X, C-K | C-X CLAIMED; C-K FORMALIZED | — | math/04 §6–7 | `purification_three` (Positive/Discrete.lean) |
| Thm 4.3 (thm:CU) ⚠ | C-U | C-U | CLAIMED | PROVED | math/04 §9 | — |
| Thm 4.4 (thm:C6) | C-6 pure TVC exactly convex given b | C-6 | FORMALIZED (constant mass) | PROVED; LEAN | math/04 §8; App. D | `torque_balance_iff`, `convex_tvcSet`, `convex_feasData_M3b`, `tvcSet_upright` (Positive/TVC.lean, Convexity.lean; not joined) |
| Prop 4.5 (prop:X5) ⚠ | X5 / RR-P (M1 only) | X5, RR-P | CLAIMED | PROVED | math/redteam-reform §3.1 | — |
| (text) | C-Y thinness 3.5 µrad/s; C-3D | C-Y, C-3D | CLAIMED | PROVED (C-Y) | math/04 §10 | — |
| Lem 4.6 (lem:shor) ⚠ | Shor = Hilbert sphere | L-SD2 (lemma) | (row BROKEN for exactness conjecture; lemma itself not disputed) | — | math/08 Lemma 1.1 | — |
| Thm 4.7 (thm:stress) ⚠ | stress certificate, local⇒global | SDP-T1, SDP-T4 | CLAIMED (proved) | PROVED | math/08 §2 | — |
| Thm 4.8 (thm:coplanar) ⚠ | coplanar certified subclass | SDP-P (= SDP-4.1) | CLAIMED (proved; not yet attacked) | PROVED (not yet attacked) | math/08 Thm 4.1 | — |
| (bullets, numerical) | unit-d lift lossy (case 12, 2.5%) | L-SD2, CSD2 | BROKEN (numerical) | numerical | math/08 §6, numerics c1–c4 | — |
| (bullet, certified numerically) | variable-throttle lift lossy, Lasserre-2 at N=3 | V-THR | CLAIMED (certified numerically) | CERTIFIED LOSSY | math/08 §7.1 | — |
| **TODO box** | CSD2′ | CSD2′ | OPEN | OPEN | math/08 §6.3 | — |
| Lem A.1, A.3 (lem:tri, lem:rigid) | spherical triangle inequality with equality case; rigidity | P-B (lemmas) | FORMALIZED | LEAN | math/02 §4.1 | `inner_triangle`, `inner_triangle_eq_lateral`, `lateral_eq_of_inner_ge` (Sphere.lean) |
| Lem A.4 (lem:support) | support bound | P-Q | CLAIMED | PROVED | math/02 Lemma 5.1 | — |
| Prop C.1 (prop:master) | master inequality | S-M | CLAIMED / SURVIVED adversary | PROVED | math/07 Prop M | `master_inequality`, `dent` (pending) |
| §5 (all) | gap law, beyond regime, B* face gap, slice S, hop ring, MT convex, in-air no dent, pure-TVC 2.8–3.3 cm | HOP, S-HOP, S-GTPL, S-LH, B6-E numerics | NUMERICAL | NUMERICAL | numerics/README.md; adversary-6dof §4 | — |
| §5.4 | 3DOF LCvx jumps ~1e3 rad/s², 296 vs 400 N | — | context | — | context/vehicle.md §0, §5 | — |

## Claims I could not support as theorems (kept out, or kept only as numerics, open problems or TODO boxes)
- B6-TVC-up / TVC-1 (pure TVC upright at rest with r_z ≥ 0): TODO box only.
- S-GTPL, S-HOP (hole at hop data), S-LH: numerical only.
- CSD2′: open, TODO box. Occupation-measure exactness (OM): mentioned as context with citations, not stated as a theorem (registry: "superposition principle cited, not proved").
- P0-TVC (asymptotic), P0-T (numerics only): mentioned in text only.
- Prop 5.3 of math/02 (false feasibility on a set of positive measure): a sketch, not used.
- Min-fuel value-losslessness: open problem.
