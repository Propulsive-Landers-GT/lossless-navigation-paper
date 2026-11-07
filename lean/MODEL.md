# Lean ↔ mathematics: faithfulness map

Project: `lean/LcvxObstruction` (Lean 4 `v4.36.0-rc2`, Mathlib pinned in `lake-manifest.json`).
Namespace `LcvxObstruction`. Build: `source ~/.elan/env && cd lean/LcvxObstruction && lake build`.
No `sorry` and no `axiom` anywhere in the project. `#print axioms` for every headline theorem
gives only `[propext, Classical.choice, Quot.sound]` (see §8).

Use this document to check that the formal statements say what the paper claims. Each row gives the
Lean object, its exact formal content, and the mathematical object it stands for.

---

## 1. Conventions

| Lean | Meaning |
|---|---|
| `E3 := EuclideanSpace ℝ (Fin 3)` | ℝ³ with the Euclidean inner product `⟪x,y⟫` and norm. |
| `ez := EuclideanSpace.single 2 1` | vertical unit vector e_z ("up"). `ex := single 0 1` is a horizontal unit vector. |
| `InnerProductGeometry.angle x y` | `arccos(⟪x,y⟫/(‖x‖‖y‖))` ∈ [0,π], the great-circle distance between unit vectors (Mathlib). |
| `Icc 0 tf` | the closed time interval [0, t_f]. |
| `∫ s in Icc 0 t, f s` | Lebesgue (Bochner) integral over [0,t]. Vector-valued integrands are Bochner integrals in ℝ³. |
| `IntegrableOn f (Icc 0 tf)` | f is Lebesgue integrable on [0,t_f] (this includes a.e.-strong measurability). |

Pointwise constraints are imposed for **every** `s ∈ [0,tf]`, not just a.e. Every quantity in the
theorems is an integral, so this changes nothing: an a.e.-admissible control can be modified on a
null set without changing any integral.

---

## 2. Relaxations (`Abstract.lean`, `TheoremD.lean`)

| Lean | Formal content | Mathematics |
|---|---|---|
| `UniformConvexRelaxation Θ Y` | structure: `C : Set (Θ × Y)`, `convex : Convex ℝ C`; `Θ, Y` arbitrary real vector spaces | a uniform convex relaxation: one convex set in (data, lifted decision) space; the data θ enter jointly convexly. Covers lifted variables, slacks, and any discretisation (Y is arbitrary). |
| `R.slice θ` | `{y \| (θ,y) ∈ R.C}` | feasible set of the relaxed problem at datum θ |
| `R.IsLossless F` | `∀ θ, (R.slice θ).Nonempty ↔ θ ∈ F` | lossless, feasibility form: the relaxed problem is feasible iff the original one is |
| `R.IsLosslessFor J F` | `(∀ θ ∈ F, slice θ ≠ ∅) ∧ ∀ θ, slice θ ≠ ∅ → ∃ y ∈ slice θ, IsMinOn (J θ) (slice θ) y ∧ θ ∈ F` | standard LCvx losslessness for an arbitrary cost `J`: the relaxation contains the original problem, and the relaxed optimum is attained and is original-feasible |
| `IsLosslessFor.isLossless` | LCvx form ⇒ feasibility form | the obstruction is cost-independent |
| `theoremA` | `Convex C → (∀θ, (∃y,(θ,y)∈C) ↔ θ∈F) → Convex F` | **Theorem A** |
| `IsLossless.convex_linear_image`, `…_affine_image` | lossless ⇒ `L '' F` convex for linear / affine `L` | Theorem A pushed through the projection (r₀,v₀) ↦ v₀ |
| `not_isLossless_of_not_convex`, `not_isLosslessFor_of_not_convex` | `¬Convex F → ¬ R.IsLossless F` (resp. `IsLosslessFor J F`) for every `R` | corollary of Theorem A |
| `StateLinearRelaxation Y E` | `C` convex ⊆ Y, `ρ : Y →ᵃ[ℝ] E` affine readout, `P : Y → ℝ` convex and ≥ 0 on `C` | state-linear relaxation of one instance (math/02 Def. 11.1) |
| `S.Contains Reach` | `∀ x ∈ Reach, ∃ y ∈ C, ρ y = x ∧ P y = 0` | embedding (E): every genuine readout is represented with zero penalty |
| `StateLinearRelaxation.convexHull_subset` | `Contains Reach → ∀ x ∈ convexHull Reach, ∃ y ∈ C, ρ y = x ∧ P y = 0` | **Theorem D (abstract)** |
| `minError_lossy` | for `q ∈ convexHull Reach \ closure Reach`: the relaxed min-error value is 0, every genuine point has error ≥ `infDist q Reach > 0`, and every relaxed optimum reads out a non-genuine state | Corollary D.1, abstract form |
| `convex_superset_gap` | convex `K ⊇ L`, `L` closed, `q ∈ conv L \ L` ⇒ `q ∈ K ∧ 0 < infDist q L` | orchestrator's form of D |

Out of scope, and stated in the file docstring: relaxations whose costs or terminal constraints are
not functions of the affine readout (moment/Shor lifts, occupation-measure LPs).

---

## 3. Model M1 (`Model.lean`)

| Lean | Formal content | Mathematics (math/00 §1, math/02 §1.2) |
|---|---|---|
| `AttitudeAdmissible tf ω δ d b` | structure with fields: | admissible attitude/thrust-direction pair on [0,t_f] |
| `.b_init` | `b 0 = ez` | b(0) = e_z (upright start). **b(t_f) is free.** |
| `.b_unit` | `∀ s ∈ [0,tf], ‖b s‖ = 1` | b ∈ S² |
| `.b_cont` | `ContinuousOn b [0,tf]` | continuity (redundant: it follows from `b_rate`) |
| `.b_rate` | `∀ s s' ∈ [0,tf], angle (b s) (b s') ≤ ω * |s - s'|` | slew-rate limit: b is ω-Lipschitz in the great-circle metric, ⇔ ‖ω_⊥‖ ≤ ω for an a.c. axis |
| `.d_meas` | `AEStronglyMeasurable d (volume.restrict [0,tf])` | thrust direction measurable |
| `.d_unit` | `∀ s, ‖d s‖ = 1` | d ∈ S² |
| `.gimbal` | `∀ s, angle (d s) (b s) ≤ δ` | gimbal cone of half-angle δ around b |
| `Acc : Set (ℝ → ℝ)` | a parameter of every theorem | class of admissible thrust-acceleration magnitudes a = T/m. Theorems assume only: members are integrable with `a ≥ a₁` (Thm B), or `a_min ≤ a ≤ a_max` (Thm B*), and that the extreme profile is a member. |
| `AccLower tf a₁` | `{a \| IntegrableOn a [0,tf] ∧ ∀ s, a₁ s ≤ a s}` | abstract a ≥ a₁ class (math/00: a₁(s) = ρ₁/(m₀ − αρ₁s) covers mass depletion) |
| `AccBox tf a₁ a₂` | `{a \| IntegrableOn a ∧ ∀ s, a₁ s ≤ a s ≤ a₂ s}` | throttle box. With constants `a₁ = ρ₁/m₀`, `a₂ = ρ₂/m₀` this is the constant-mass (α = 0) model exactly. |
| `reachSet Acc tf ω δ` | `{∫₀^tf a • d \| a ∈ Acc, AttitudeAdmissible tf ω δ d b}` | velocity-increment set R |
| `velocity g v₀ a d t` | `v₀ + t•g + ∫₀ᵗ a•d` | the solution of v̇ = a d + g, v(0) = v₀ |
| `position g r₀ v₀ a d t` | `r₀ + t•v₀ + (t²/2)•g + ∫₀ᵗ (t−s)•(a•d)` | the solution of r̈ = a d + g (Cauchy's formula for the double integral, i.e. Carathéodory solution) |
| `landingSet Acc tf ω δ g` | `{(r₀,v₀) \| ∃ admissible (a,d,b), position … tf = 0 ∧ velocity … tf = 0}` | F_{t_f}: initial data from which a soft landing (r = v = 0) at time t_f is possible. Initial position and velocity are free, there are no state constraints, and the final attitude is free. |
| `snd_image_landingSet` | `Prod.snd '' F = {−w − tf•g \| w ∈ R}` | proj_{v₀} F_{t_f} = −g t_f − R (math/02 Lemma 3.1) |
| `convex_reachSet_of_convex_landingSet` | `Convex F → Convex R` | |

---

## 4. Theorem B, unconstrained (`Nonconvex.lean`, `Main.lean`)

| Lean | Formal content | Mathematics |
|---|---|---|
| `arcB ω u s`, `arcD ω δ u s` | `sin(ωs)•u + cos(ωs)•ez`, `sin(δ+ωs)•u + cos(δ+ωs)•ez` | extreme tilt arcs |
| `arc_admissible` | for unit `u ⊥ ez`, `0≤ω`, `0≤δ≤π`, `ω tf ≤ π`: `AttitudeAdmissible tf ω δ (arcD ω δ u) (arcB ω u)` | the extreme arcs are admissible, so the hypotheses are not vacuous |
| `midpointM tf ω δ a₁` | `(∫₀^tf a₁ s * cos(δ+ωs)) • ez` | M = midpoint of P_u and P_{−u} (`midpoint_arcEndpoint`) |
| `midpointM_not_mem_reachSet` | `M ∉ R` | key step |
| `not_convex_reachSet`, `not_convex_landingSet` | `¬ Convex R`, `¬ Convex F_tf` (any gravity `g`) | **Theorem B** |
| `no_lossless_relaxation_5dof` (+ `_lower`, `_box`, `no_losslessFor_…`) | `¬ R.IsLossless (landingSet …)` for every `Y` and every uniform convex relaxation `R` | **Main theorem, unconstrained** |

Hypotheses: `0 < tf`, `0 < ω`, `0 ≤ δ`, `δ + ω tf ≤ π/2`, `a₁` continuous with `a₁ > 0` on [0,t_f]
(neither constancy nor monotonicity of a₁ is needed), every `a ∈ Acc` integrable with `a ≥ a₁`, and
`a₁ ∈ Acc`. Joint satisfiability: `main_hypotheses_satisfiable`, `landingSet_nonempty`.

**Physical scope caveat** ([adversary] BREAK 23:50): no altitude constraint. For GTPL
(ρ₁ < m₀g) the witness trajectories start underground, so this theorem alone says nothing about the
altitude-constrained problem. That problem is covered by §5.

---

## 5. Theorem B*, altitude / glide-slope constrained (`DiveBrake.lean`, `Main.lean`)

| Lean | Formal content | Mathematics (math/02 §10) |
|---|---|---|
| `glideSlopeSet tanγ` | `{(r,v) \| 0 ≤ ⟪r,ez⟫ ∧ tanγ * ‖r − ⟪r,ez⟫•ez‖ ≤ ⟪r,ez⟫}` | the set 𝒳: r_z ≥ 0 and glide slope tanγ ‖r_h‖ ≤ r_z (`tanγ = 0` gives altitude only) |
| `constrainedLandingSet Acc tf ω δ g X` | `landingSet` plus `∀ t ∈ [0,tf], (position … t, velocity … t) ∈ X` | F^𝒳_{t_f}: the state constraint holds along the whole trajectory |
| `lambda_identity` | landing ⇒ `r₀ + s*•v₀ = ∫ (s−s*)•(a•d) + (tf²/2 − s* tf)•g` | Lemma 10.1 |
| `position_eq_tail` | landing ⇒ `r(t) = ∫_t^tf (s−t)•(a•d) + ((tf−t)²/2)•g` | backward (Taylor) form of the trajectory |
| `hStar`, `VStar` | `h*(s) = min(s−s*,0)·a_min·cos(δ+ωs) + max(s−s*,0)·a_max`, `V* = ∫₀^tf h*` | pointwise maximiser and maximum of ⟪W, e_z⟫ |
| `WSet` | `{∫ (s−s*)•(a•d) \| admissible}` | the set of weighted impulses W(c) |
| `VStar_not_mem_WSet` | `V*•ez ∉ WSet` | Step 6 (equality case and rigidity on the dive, d = e_z on the brake) |
| `aW`, `dW`, `bW` | min/max throttle; `arcD` on [0,s*] then `ez`; `arcB(min s s*)` | the dive-then-brake witnesses c_{±u} |
| `witness_admissible`, `aW_mem_accBox` | the witnesses are admissible | Step 2 |
| `witness_W_midpoint` | `½W(c_u) + ½W(c_{−u}) = V*•ez` | |
| `witness_mem_glideSlope` | the witness trajectory stays in `glideSlopeSet tanγ` for all t ∈ [0,t_f] | Step 5 (with the simpler sufficient condition below) |
| `not_convex_constrainedLandingSet` | `¬ Convex (constrainedLandingSet Acc tf ω δ (−g₀•ez) X)` for every `X ⊇ glideSlopeSet tanγ` | **Theorem B*** |
| `exists_switchTime` | for every `tf > 0` there is `s*` meeting all switch-time conditions | "for every t_f" |
| `no_lossless_relaxation_constrained_5dof` (+ `no_losslessFor_…`) | `¬ R.IsLossless (constrainedLandingSet (AccBox tf a_min a_max) tf ω δ (−g₀•ez) X)` | **Main theorem, state-constrained** |
| `constrainedLandingSet_nonempty` | the constrained set is nonempty | non-vacuity |

Hypotheses of `not_convex_constrainedLandingSet`: `0 < s* < tf`, `ω > 0`, `ω s* ≤ δ`,
`δ + ω s* ≤ π/2`, `0 < a_min ≤ a_max`, `g₀ ≤ a_max`, `tanγ ≥ 0`,
`(a_max + 2 tanγ a_min) s*² ≤ (a_max − g₀)(tf − s*)²`. The last condition replaces (S2)/(S3) of math/02;
it is a cruder but simpler sufficient condition. Members of `Acc` are integrable with
`a_min ≤ a ≤ a_max`, and the witness throttle `aW` ∈ `Acc`.
Headline hypotheses (`no_lossless_relaxation_constrained_5dof`): `tf > 0`, `ω > 0`, `0 < δ < π/2`,
`0 < a_min ≤ a_max`, `g₀ < a_max` (thrust-to-weight > 1 at full throttle), `tanγ ≥ 0`.
GTPL (ρ₁ = 400 N, ρ₂ = 1000 N, m₀ ≈ 80 kg, δ = 15°) satisfies these with constant mass.

---

## 6. What is NOT formalized (honest gaps)

* **Mass depletion in B*** (α > 0). B* is proved for constant acceleration bounds. That is exact for
  constant mass, and also for any model whose acceleration class is a box with constant bounds
  containing the min-then-max profile. With α > 0 the min-then-max witness has a history-dependent
  acceleration, and math/02 Step 3 needs a separate comparison argument that is not formalized.
  Theorem B (unconstrained) does cover α > 0 through `AccLower` with a₁(s) = ρ₁/(m₀ − αρ₁s) (the
  derivation a ≥ a₁ from the mass ODE is also not formalized).
* **Terminal attitude** b(t_f) = e_z (variant T / T') is not formalized. b(t_f) is free in all theorems.
* **Free final time** (Cor. 10.4) and the **quantitative gaps** (ball bound Thm Q, ε-lossless
  Cor. 5.2) are not formalized.
* **6DOF** corollaries (kinematic 6DOF, M3a/M4 envelopes, TVC flat output, center-of-percussion
  identity) are not formalized.
* `position` is defined by Cauchy's closed form, not as `r₀ + ∫ v`. The equivalence (Fubini) is standard
  and not proved here.
