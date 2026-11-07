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
| `position_eq_integral_velocity` (`Trajectory.lean`) | `position g r₀ v₀ a d t = r₀ + ∫₀ᵗ velocity g v₀ a d` for `t ≥ 0`, `a•d` integrable (via Fubini, `integral_primitive`) | the closed form really is the double integral of the acceleration |
| `AccMass ρ₁ ρ₂ α m₀ m_dry tf` (`MassModel.lean`) | `{a \| a integrable ∧ ∃ T integrable, ρ₁ ≤ T ≤ ρ₂, m_dry ≤ m(t) := m₀ − α∫₀ᵗT, a = T/m on [0,tf]}` | explicit mass-depletion model ṁ = −αT, a = T/m, dry-mass limit |
| `accMass_spec`, `aMinMass_mem`, `aMinMass_props` | every `a ∈ AccMass` has `a ≥ a₁ := ρ₁/(m₀ − αρ₁ s)`; `a₁ ∈ AccMass` (T ≡ ρ₁) if `m_dry ≤ m₀ − αρ₁ tf`; `a₁` continuous, > 0 | math/02 Lemma 4.3 |
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
| `no_lossless_relaxation_5dof_mass` (`MassModel.lean`) | the same for `Acc = AccMass ρ₁ ρ₂ α m₀ m_dry tf` (hyp.: `0 < ρ₁ ≤ ρ₂`, `α ≥ 0`, `0 < m_dry ≤ m₀ − αρ₁ tf`) | **Main theorem, unconstrained, explicit mass depletion** |

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

## 5a. Free final time / line search (`FreeTime.lean`, Lemma RR-LS)

| Lean | Formal content | Mathematics (math/redteam-reform.md §4) |
|---|---|---|
| `not_lineSearch_lossless` | horizons `W ⊆ ι`, true sets `F t`, one uniform convex relaxation `C t` per horizon (lifted space `Y t` may depend on t) with `F t ⊆ proj C t`. If `x̄ ∈ convexHull (F t₀)`, `t₀ ∈ W`, and `x̄ ∉ F t` for all `t ∈ W`, then "∃ t ∈ W, slice nonempty ↔ ∃ t ∈ W, x ∈ F t" fails | RR-LS (i): line search over t_f accepts an infeasible datum |
| `symmetric_supply` | linear involution `R` preserving each `F t`; `ℓ` linear with `ℓ ∘ R = ℓ`; `x₀ ∈ F t₀` maximises ℓ over the graph; every maximiser `x` has `x − R x ≠ 0`. Then `½(x₀ + R x₀) ∈ convexHull (F t₀)` and lies in no `F t` | RR-LS (ii), hypotheses (H1)–(H3) |
| `not_lineSearch_lossless_of_symmetry` | (i) + (ii) | RR-LS combined |

These are abstract (any real vector space X). (H2)/(H3) for the concrete 5DOF problem (existence of a
graph maximiser on a compact window, and the structure lemma) are **not** formalized. The concrete
free-final-time theorem is therefore not machine-checked; only the abstract kill is.

## 5b. 6DOF, kinematic (`SixDOF.lean`)

| Lean | Formal content | Mathematics (math/02 §6, Thm 6.2 kinematic) |
|---|---|---|
| `Attitude6Admissible Att tf ω δ d A` | `A : ℝ → (E3 →ₗᵢ[ℝ] E3)` (body→inertial, any roll), fields: `A ∈ Att`; `A 0 ez = ez`; `s ↦ A s x` continuous; **`∀ x ≠ 0, angle (A s x) (A s' x) ≤ ω|s−s'|`** (every body-fixed direction turns at rate ≤ ω, ⇔ ‖Ω‖ ≤ ω); `d` measurable, unit; `angle (d s) (A s ez) ≤ δ` | rate-limited 6DOF attitude kinematics, thrust axis = body z |
| `properAttitudes` | `{A \| ∀ s, det (A s) = 1}` | SO(3)-valued attitude paths |
| `landingSet6`, `constrainedLandingSet6` | as in §3/§5 with `Attitude6Admissible` in place of `AttitudeAdmissible` | F^{6DOF}_{t_f}, F^{6DOF,𝒳}_{t_f} |
| `Attitude6Admissible.toM1`, `landingSet6_subset`, `constrainedLandingSet6_subset` | the body z-axis of a 6DOF attitude is M1-admissible; 6DOF sets ⊆ 5DOF unconstrained set | projection |
| `rotY φ` | explicit linear isometry, rotation about `e_y` by φ; `rotY_ez`: `e_z ↦ sin φ e_x + cos φ e_z`; `angle_rotY_le` | the zero-roll planar lift |
| `lift_admissible` | rotations `rotY(±ω φ(s))` with φ 1-Lipschitz are 6DOF-admissible | lift of the planar witnesses |
| `not_convex_landingSet6` | Theorem B for 6DOF, any attitude class `Att` containing the two rotation paths | **Theorem B, 6DOF** |
| `not_convex_constrainedLandingSet6` | Theorem B* for 6DOF | **Theorem B*, 6DOF** |

| `det_rotY`, `rotY_path_mem_proper` | `det (rotY φ) = 1`, so the witness attitudes are proper rotations | witnesses lie in SO(3) |
| `no_lossless_relaxation_constrained_6dof` (`Upright.lean`) | headline: no lossless uniform convex relaxation of the 6DOF (proper rotations) altitude/glide-slope-constrained landing set, every `tf > 0` | **Main theorem, 6DOF, constrained** |

## 5c. Upright landing `b(t_f) = e_z` (`Upright.lean`, variant T')

| Lean | Formal content | Mathematics |
|---|---|---|
| `constrainedLandingSetUp`, `constrainedLandingSet6Up` | as `constrainedLandingSet(6)` plus `b tf = ez` (resp. `A tf ez = ez`) | upright terminal attitude |
| `phiUp`, `bWU`, `witness_admissible_upright` | tilt `ω·max(0, min(s, 2s*−s))`: up until s*, back down along the same meridian, upright after 2s* | the T' witness (math/02 §10 Step 2) |
| `not_convex_constrainedLandingSetUp`, `not_convex_constrainedLandingSet6Up` | Theorem B* with upright landing, needs `2 s* ≤ tf` | **Theorem B*, variant T'** |
| `no_lossless_relaxation_constrained_upright_5dof`, `…_upright_6dof` | headlines for every `tf > 0` (`exists_switchTime` also gives `2 s* ≤ tf`) | **Main theorem, upright landing** |

Scope: this is *kinematic* 6DOF (angular velocity bounded, no torque/inertia dynamics). The
torque-limited (M3a/M4-dyn) and gimbal-torque-coupled pure-TVC (M3b) models are not formalized.

---

## 6. What is NOT formalized (honest gaps)

* **Mass depletion in B*** (α > 0). B* is proved for constant acceleration bounds. That is exact for
  constant mass, and also for any model whose acceleration class is a box with constant bounds
  containing the min-then-max profile. With α > 0 the min-then-max witness has a history-dependent
  acceleration, and math/02 Step 3 needs a separate comparison argument that is not formalized.
  Theorem B (unconstrained) does cover α > 0, including the derivation of a ≥ a₁ from the mass
  model (`MassModel.lean`).
* **Terminal attitude**: b(t_f) = e_z is formalized for B* (variant T', §5c). It is not formalized for the
  unconstrained tent variant T of Theorem B.
* **Free final time** (Cor. 10.4) and the **quantitative gaps** (ball bound Thm Q, ε-lossless
  Cor. 5.2) are not formalized.
* **6DOF**: only the kinematic rate-limited model (§5b). The M3a/M4 torque envelopes, the TVC flat
  output and the center-of-percussion identity are not formalized.
* (Resolved) `position` is defined by Cauchy's closed form; `position_eq_integral_velocity` proves it
  equals `r₀ + ∫ v`.
