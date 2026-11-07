# [lean] final report: machine-checked impossibility of uniform lossless convexification (5DOF / kinematic 6DOF)

Project: `lean/LcvxObstruction` (Lean 4 v4.36.0-rc2 + Mathlib). Build: `source ~/.elan/env && cd lean/LcvxObstruction && lake build`.
Faithfulness map (each Lean definition beside the mathematics, plus scope): `lean/MODEL.md`.

## What is proven (sorry-free, no new axioms)

| File | Headline theorems | Mathematical content |
|---|---|---|
| `Abstract.lean` | `theoremA`, `IsLossless.convex(_linear_image/_affine_image)`, `not_isLossless_of_not_convex`, `IsLosslessFor.isLossless`, `not_isLosslessFor_of_not_convex` | Theorem A. Lossless uniform convex relaxation ⇒ F convex. The LCvx (optimisation, any cost) form ⇒ the feasibility form. |
| `Sphere.lean` | `inner_triangle`, `inner_triangle_eq`, `inner_triangle_eq_lateral`, `lateral_eq_of_inner_ge` | Spherical triangle inequality (inner-product form), its equality case, and rigidity. Stated in a general real inner product space; the triangle inequality reuses Mathlib's `angle_le_angle_add_angle`. |
| `Model.lean` | `AttitudeAdmissible`, `AccLower`, `AccBox`, `reachSet`, `velocity`, `position`, `landingSet`, `snd_image_landingSet` | Model M1 (b(0)=e_z, slew-rate limit in the great-circle metric, gimbal cone, measurable thrust direction, abstract throttle class); closed-form trajectories; proj_{v0}F = −g t_f − R. |
| `Nonconvex.lean` | `arc_admissible`, `midpointM_not_mem_reachSet`, `not_convex_reachSet`, `not_convex_landingSet` | Theorem B, rigidity route, variant F: 0<t_f, 0<ω, 0≤δ, δ+ωt_f ≤ π/2, any continuous a₁>0 (mass depletion included through a ≥ a₁). |
| `DiveBrake.lean` | `lambda_identity`, `position_eq_tail`, `VStar_not_mem_WSet`, `witness_admissible`, `witness_mem_glideSlope`, `witness_midpoint_not_mem_landingSet`, `not_convex_constrainedLandingSet`, `exists_switchTime` | Theorem B*, qualitative (math/02 §10 Step 6), with altitude + glide-slope state constraints (any X ⊇ glide cone), for every t_f > 0. Constant acceleration bounds a_min ≤ a ≤ a_max (α=0), g₀ < a_max. |
| `TheoremD.lean` | `StateLinearRelaxation`, `convexHull_subset`, `minError_lossy`, `convex_superset_gap` | Theorem D (abstract): state-linear relaxations with convex penalty are lossy for min-landing-error at targets in conv(Reach) \ cl(Reach). |
| `FreeTime.lean` | `not_lineSearch_lossless`, `symmetric_supply`, `not_lineSearch_lossless_of_symmetry` | Lemma RR-LS: a line search over t_f with per-horizon convex relaxations cannot be lossless (abstract form, hypotheses (H1)–(H3)). |
| `SixDOF.lean` | `Attitude6Admissible.toM1`, `rotY`, `angle_rotY_le`, `lift_admissible`, `not_convex_landingSet6`, `not_convex_constrainedLandingSet6` | Kinematic 6DOF: the attitude is a linear isometry with every body direction rate-limited by ω and arbitrary roll. Projection to M1, plus the zero-roll lift of the witnesses, so Theorems B and B* carry over. |
| `Trajectory.lean` | `integral_primitive`, `position_eq_integral_velocity` | Fubini: the closed-form position equals r₀ + ∫v, so it is faithful to r̈ = a d + g. |
| `MassModel.lean` | `AccMass`, `accMass_spec`, `aMinMass_mem`, `no_lossless_relaxation_5dof_mass` | Explicit mass depletion (ṁ = −αT, a = T/m, dry-mass limit). Lemma 4.3 gives a ≥ a₁ = ρ₁/(m₀−αρ₁s), so the unconstrained main theorem holds for this model. |
| `Upright.lean` | `witness_admissible_upright`, `not_convex_constrainedLandingSetUp`, `not_convex_constrainedLandingSet6Up`, `no_lossless_relaxation_constrained_upright_5dof`, `no_lossless_relaxation_constrained_upright_6dof`, `no_lossless_relaxation_constrained_6dof` | B* with upright landing b(t_f)=e_z (variant T'), 5DOF and 6DOF (proper rotations), every t_f. |
| `Main.lean` | `no_lossless_relaxation_5dof` (+`_lower`, `_box`), `no_losslessFor_relaxation_5dof`, `no_lossless_relaxation_constrained_5dof`, `no_losslessFor_relaxation_constrained_5dof`, `landingSet_nonempty`, `constrainedLandingSet_nonempty`, `main_hypotheses_satisfiable` | Final statements: no uniform convex relaxation (any lifted space Y, any cost J) is lossless, unconstrained or altitude/glide-slope-constrained. The hypotheses are shown non-vacuous. |

## `#print axioms` (all headline theorems)
Every theorem listed above gives `depends on axioms: [propext, Classical.choice, Quot.sound]`.
Verbatim output is in §Axioms below.

## Remaining gaps (not formalized)
- B* with mass depletion (α > 0). B* uses constant acceleration bounds, which are exact for constant mass. The unconstrained Theorem B *is* formalized with explicit mass depletion (`MassModel.lean`).
- Upright terminal attitude for the *unconstrained* tent variant T of Theorem B (B* with b(t_f)=e_z IS formalized).
- Quantitative gaps (ball bound Thm Q, η₀ bound, ε-lossless Cor. 5.2) and the concrete free-final-time theorem (Cor. 10.4; only abstract RR-LS is formalized).
- Concrete Corollary D.1 (dist(x°, Reach(θ_m)) > 0); only abstract Theorem D is formalized.
- 6DOF with torque/inertia dynamics (M3a/M4-dyn), pure TVC (M3b, flat output), and the center-of-percussion identity.

## Notes for [proof] / [orchestrator]
- B* smallness condition used: (a_max + 2 tanγ·a_min)·s*² ≤ (a_max − g₀)(t_f − s*)², with ωs* ≤ δ and δ + ωs* ≤ π/2. This is a simpler sufficient replacement for (S2)/(S3), and `exists_switchTime` shows it is satisfiable for every t_f. δ ≤ π/4 is not needed; δ + ωs* ≤ π/2 suffices.
- Theorem B needs no constancy or monotonicity of a₁: rigidity is applied on pairs of a.e.-good times, so no a.e.→everywhere step is needed.

## Axioms
`lake build` (full, at commit 19ffe1a) → `Build completed successfully (18218 jobs).` Then `#print axioms`:
```
'LcvxObstruction.theoremA' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_isLossless_of_not_convex' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_isLosslessFor_of_not_convex' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.inner_triangle' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.inner_triangle_eq_lateral' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.lateral_eq_of_inner_ge' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_reachSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_landingSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_5dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_losslessFor_relaxation_5dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.landingSet_nonempty' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.VStar_not_mem_WSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.witness_mem_glideSlope' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_constrainedLandingSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.exists_switchTime' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_constrained_5dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_losslessFor_relaxation_constrained_5dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.constrainedLandingSet_nonempty' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.StateLinearRelaxation.convexHull_subset' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.minError_lossy' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.convex_superset_gap' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_lineSearch_lossless' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.symmetric_supply' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_lineSearch_lossless_of_symmetry' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.Attitude6Admissible.toM1' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.det_rotY' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_landingSet6' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_constrainedLandingSet6' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.witness_midpoint_not_mem_landingSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.position_eq_integral_velocity' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.accMass_spec' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_5dof_mass' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_constrainedLandingSetUp' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.not_convex_constrainedLandingSet6Up' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_constrained_upright_5dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_constrained_upright_6dof' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxObstruction.no_lossless_relaxation_constrained_6dof' depends on axioms: [propext, Classical.choice, Quot.sound]
```
`grep -rn "sorry\|^axiom" LcvxObstruction/*.lean` → no matches.
