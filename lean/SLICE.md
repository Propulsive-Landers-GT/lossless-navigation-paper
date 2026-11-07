# Lean ↔ mathematics: the slice files (`LcvxObstruction/Slice/`), owner [lean-s]

Files: `Slice/AOpt.lean`, `Slice/Affine.lean`, `Slice/Wirtinger.lean`, `Slice/Master.lean`,
`Slice/LemmaS.lean`, `Slice/Axioms.lean`. Namespace `LcvxObstruction.Slice`
(the Theorem-D generalisation sits in `LcvxObstruction`).
They import `Model.lean`, `DiveBrake.lean` and `TheoremD.lean` and reuse their definitions:
`E3`, `ez`, `ex`, `AttitudeAdmissible`, `AccBox`, `position`, `velocity`, `landingSet`,
`StateLinearRelaxation`, `minError_lossy`, `position_eq_tail`. So every theorem below talks
about the same model M1 as the rest of the project (see `lean/MODEL.md` §1–§3 for conventions).
None of the files contains `sorry` or `axiom`. `#print axioms` output: see §7.

---

## 1. Theorem A-opt, Prop T, Theorem D with penalty (`AOpt.lean`; math/redteam-lift.md §5, §7)

| Lean | Formal content | Mathematics |
|---|---|---|
| `CostRelaxation θ Φ c` | convex `C ⊆ Θ × Y`, cost `J` convex on `C`, every genuine trajectory `τ` represented: `(θ τ, Φ τ) ∈ C`, `J (θ τ, Φ τ) = c τ` | uniform convex relaxation with a convex cost (redteam-lift §7 with `J` allowed to depend on the datum too) |
| `mixing`, `mixing_finset` | convex mixtures of genuine points lie in `C` with relaxed cost `≤` the mixed true cost | Lemma ML |
| `ValueLossless` | `∀ (x,y) ∈ C, x ∈ F → ∃ τ, θ τ = x ∧ c τ ≤ J (x,y)` | value-lossless on `F`, infimum-free form (implied by `V_rel = V` on `F` + attainment, and by the standard LCvx guarantee) |
| `aOpt`, `aOpt_finset` | under `ValueLossless`, a feasible convex mixture of data carries a genuine trajectory of cost `≤` the mixed cost | **Theorem A-opt** |
| `value`, `value_le_convexCombination` | `V x := sInf {c τ \| θ τ = x}`; `V (∑ wᵢ xᵢ) ≤ ∑ wᵢ V xᵢ` when all `xᵢ` and the mixture are in `F` | **"V = V\*\* on F"** (convex-envelope form; the lsc closure step is not needed for the obstruction) |
| `no_valueLossless_of_strict` | equal-cost `τ₊, τ₋`, midpoint datum feasible but only with cost `> Λ` ⇒ `¬ ValueLossless` for every `CostRelaxation` | **Corollary T-abstract** (skeleton of Prop T) |
| `StateLinearRelaxation.lossy_of_gap` | for any readout cost `f` and `x ∈ conv Reach` with `f x + ε ≤ f z` for all genuine `z`: the relaxed cost `f∘ρ + P` attains `f x`, genuine cost `≥ f x + ε` | Theorem D with the class (d) cost "f(readout) + convex penalty vanishing on genuine points" (TheoremD.lean already has the `‖ρ y - q‖ + P y` case, `minError_lossy`) |

Not formalized: the M1 facts F1–F5 that discharge the hypotheses of `no_valueLossless_of_strict`
for the cost `∫ b·e_z` (rigidity, Aumann/unique maximiser, admissibility of the mixed datum).
So Prop T is formalized as the abstract implication only.

## 2. Affine projection in L² (`Affine.lean`; blueprint SW1)

| Lean | Content |
|---|---|
| `BM T f` | `f` a.e.-strongly measurable and bounded on `[0,T]` (standing class; all M1 integrands are in it) |
| `mom0 T f`, `mom1 T f` | `∫₀ᵀ f`, `∫₀ᵀ s f(s)` (Lebesgue, over `Icc 0 T`) |
| `fit T f` | the affine function with the same two moments; `= P f` (orthogonal projection onto affine functions) |
| `L2 T f` | `∫₀ᵀ ‖f‖²` |
| `L2_sub_affLine`, `L2_sub_fit_le`, `L2_sub_fit_le_L2`, `L2_eq_add_fit` | Pythagoras; `‖P^⊥f‖ ≤ ‖f − A‖` for every affine `A`; `‖P^⊥ f‖ ≤ ‖f‖`; `‖f‖² = ‖P^⊥f‖² + ‖Pf‖²` |
| `L2_fit_of_mom0_eq_zero` | `‖π_{(0,q)}‖² = 12‖q‖²/T³` |
| `fit_add`, `fit_sub`, `fit_smul` | linearity of `P` |
| `L2_add_le` | Minkowski (squared form) |

## 3. Lemma W (`Wirtinger.lean`; math/07 §2, blueprint SW2–SW3)

| Lean | Formal content | Mathematics |
|---|---|---|
| `periodic_wirtinger` | `h` absolutely continuous on `[0,T]` (`AbsolutelyContinuousOnInterval`), `h 0 = h T`, `∫ h = 0`, `(deriv h)²` integrable ⇒ `∫ h² ≤ (T/2π)² ∫ (deriv h)²` | SW2. Proof: Parseval on `AddCircle T` (`hasSum_sq_fourierCoeffOn`) + integration by parts for AC functions |
| `wirtinger_scalar` | `g` AC on `[0,T]`, `(deriv g)²` integrable ⇒ `‖g − Pg‖² ≤ (T/2π)² ∫ (deriv g)²` | **Lemma W**, scalar (the sharper `− \|g(T)−g(0)\|²/T` term is proved inside and then dropped) |
| `wirtinger_lipschitz` | `β : ℝ → EuclideanSpace ℝ ι` (`ι` any finite type), `‖β x − β y‖ ≤ ω\|x−y\|` on `[0,T]` ⇒ `‖β − Pβ‖² ≤ (T/2π)² ω² T` | **Corollary W**. Componentwise, so it is valid for planar paths, coning and ℝ^N-lifted paths alike |

Regularity: AC with an L² a.e. derivative (scalar), Lipschitz (vector). This is exactly what the
slew-rate limit `AttitudeAdmissible.b_rate` provides (`hor_b_lipschitz`).

## 4. Proposition M, the master inequality (`Master.lean`; math/07 §2)

Scope: model M1 of `Model.lean` with **constant mass (α = 0)** and throttle box
`AccBox T (fun _ => a₁) (fun _ => a₂)`, `0 < a₁ ≤ a₂`, any gimbal `δ ≥ 0`, any 3D attitude path,
`δ + ωT < π/2`. No state constraint is used.

| Lean | Formal content | Mathematics |
|---|---|---|
| `hor`, `horL` | `v ↦ v − ⟪e_z,v⟫ e_z` | horizontal part |
| `pointwise_majorant` | `a₁ − a d_z ≤ (a₁/(1+cos τ̄))‖d_h‖² − κ‖(a−a₁) d_h‖²` under `d_z ≥ cos τ̄ > 0`, `a₁ ≤ a ≤ a₂`, `κ(a₂−a₁)sin²τ̄ ≤ cos τ̄` | Lemma P1 + throttle split (SP1, SP3), with the constant `c̄ = c̄(T)` of math/07 Remark (c) |
| `concave_quad` | `A'‖x‖² − κ‖π−x‖² ≤ (A'κ/(κ−A'))‖π‖²` | K-elimination (step 3) |
| `cbar τ`, `slackB T ω δ a₁` | `1/(1+cos τ)`; `B = a₁ c̄ T (ωT/2π + √(2−2cos δ))²` | `B` of Prop M, variant (c): `E₄ = 0`, `ε_m = 0`, `δ_e = 2 sin(δ/2) = √(2−2cos δ)` |
| `latForce a d` | `F(s) = hor (a(s) d(s))` | lateral thrust acceleration |
| `master_inequality` | every admissible `(a,d,b)`: `a₁T − ⟪∫ a d, e_z⟫ ≤ B + (A'κ/(κ−A')) ‖P F‖²`, with `A' = c̄/a₁`, any `κ > A'` with `κ(a₂−a₁)sin²τ̄ ≤ cos τ̄` | **Prop. M** (`C_m = A'κ/(κ−A')`) |
| `master_inequality_fixed` | fixed thrust `a ≡ a₁`: `gain ≤ B + A'‖PF‖²` | Prop M, Remark (b) |
| `landingOffsets Acc T ω δ g₀ ζ X` | `{p \| p_z = 0 ∧ ∃ admissible (a,d,b), r(T) = p, v(T) = 0, (r(t),v(t)) ∈ X ∀t}` with gravity `−g₀e_z` | `L(ζ)` of math/07 with the state constraint `X` |
| `mem_landingOffsets_univ_iff` | `p ∈ L(ζ) ↔ p_z = 0 ∧ (r₀ − p, v₀) ∈ landingSet` | `L(ζ)` is a horizontal slice of `F_T` (`Model.lean`) |
| `landing_moments` | vertical `ζ` and landing at `p` ⇒ `∫F = 0`, `∫ sF = −p`, `∫ a d_z = g₀T − v₀z` | math/07 §1 ("every trajectory from ζ has the same gain") |
| `dent_fixed`, `dent` | every `p ∈ L(ζ)`: `a₁T − (g₀T − v₀z) ≤ B + C·12‖p‖²/T³` | step 2 of the proof of Theorem S |

Differences from math/07 Prop M: α = 0 only (no mass depletion; `E₄`/`ε_m` terms absent), and the
constant `c̄(T)` is used everywhere (Remark (c)) instead of `c₀ + E₄`. Both are allowed variants
in math/07; with α = 0 and δ = 0 they coincide with the table's fixed-thrust row up to `E₄`.

## 5. Lemma S and Theorem D with hard v(t_f) = 0 (`LemmaS.lean`; math/07 §3)

| Lean | Formal content | Mathematics |
|---|---|---|
| `phi A ω`, `wB A ω u` | tilt `φ(s) = max(min(ωs, 2A−ωs), −A)`; `b = d = sin φ u + cos φ e_z` | "hold" S-turn witness: up to `A`, back through 0 to `−A`, hold. NOT the IVT S-turn of math/07; its zero-lateral-impulse condition is explicit: hold length `h = (1−cos A)/(ω sin A)` |
| `witness_admissible` | `AttitudeAdmissible T ω 0 (wB) (wB)` | slew rate ω, no gimbal |
| `integral_sin_phi_horizon`, `integral_cos_phi` | `∫₀ᵀ sin φ = 0`, `∫₀ᵀ cos φ = 3 sin A/ω + h cos A` | |
| `zetaW`, `pW` | vertical data `ζ_w = (r0z e_z, v0z e_z)`; offset `p_w(u) = a₁(∫(T−s) sin φ) u` | |
| `witness_lands`, `witness_altitude`, `pW_mem` | the witness lands at `p_w(u)` with `v(T) = 0` and `r_z(t) ≥ 0` for all `t` (if `a₁ cos A ≥ g₀`) | Thm S item 1 |
| `instT`, `instAcc`, `instZeta`, `instL X` | instance: `a ≡ 12 m/s²` (ρ₁=ρ₂), `g₀ = 9.81`, `δ = 0`, `ω = 0.1 rad/s`, `A = 0.1 rad`, `T = 3 + 10(1−cos 0.1)/sin 0.1 ≈ 3.50 s` (`Ω ≈ 0.35 rad`) | high-T/W demo vehicle of math/07 §4, fixed thrust |
| `numeric_core` | the rational-arithmetic margin, with `sin 0.1`, `cos 0.1`, `cos Ω`, `π` replaced by variables obeying the Mathlib Taylor bounds (`Real.sin_bound`, `Real.cos_bound`, `one_sub_sq_div_two_le_cos`, `pi_gt_d2`) | the numerical check `gain_w > B` (math/07 §4) |
| `instL_norm_ge` | every `p ∈ L(ζ_w)` (any constraint `X`, any admissible 3D path, coning included) has `‖p‖ ≥ 1` m | the dent `r_S` (numerically `r_S ≈ 1.38 m`; Lean proves the rational bound 1 m) |
| `lemmaS` | `ζ_w` vertical; `ωT < π/2`; `a₁ cos(ωT) > g₀`; `p_w(u) ∈ L(ζ_w)` with altitude constraint for every horizontal unit `u`; `‖p‖ ≥ 1` on `L(ζ_w)`; for every `X ⊇ {r_z ≥ 0}`: `0 ∈ conv L`, `0 ∉ cl L`, `L` not convex | **Lemma S** (Theorem S items 1–2) for one explicit instance |
| `theoremD_hard_landing` | for every `X ⊇ {r_z ≥ 0}` and every `StateLinearRelaxation` containing `L(ζ_w)`: relaxed min error 0 at target 0, every genuine landing has error ≥ 1 m, `infDist 0 L ≥ 1`, every relaxed optimum is non-genuine | **Theorem D, hard soft landing, is lossy** (Theorem S item 4) |

**Physical scope.** The instance has minimum-throttle T/W = 12/9.81 ≈ 1.22 > 1/cos A, i.e. a
vehicle that cannot hover at minimum throttle (math/07 regime (S1)). GTPL (ρ₁/m₀ = 5–7.2 m/s² < g₀)
is NOT covered; the GTPL dive-then-brake case remains numerical only (math/07 §6, CLAIMS S-GTPL).

## 6. Not formalized (honest gaps)

* Mass depletion (α > 0) in Prop M (`E₄`, `ε_m` terms); the time-varying `c̄(s)` majorant.
* The throttle (ρ₁ < ρ₂) instance and the math/07 §4 table rows (only the master inequality and
  dent are formalized for throttle; the explicit instance is fixed-thrust).
* The IVT S-turn witness of math/07 §3 (replaced by the hold S-turn; same mechanism).
* Glide-slope constraint for the witness (only `r_z ≥ 0`); dry-mass condition (S4) (irrelevant for α = 0).
* The M1 facts F1–F5 behind Prop T; only the abstract Corollary T is formalized.
* The `L` set is defined by Model.lean's closed-form `position`/`velocity` (Cauchy formula), as in
  the rest of the project.

## 7. Axiom audit (`Slice/Axioms.lean`, run `lake env lean LcvxObstruction/Slice/Axioms.lean`)

Every one of `CostRelaxation.aOpt`, `aOpt_finset`, `value_le_convexCombination`,
`no_valueLossless_of_strict`, `StateLinearRelaxation.lossy_of_gap`, `periodic_wirtinger`,
`wirtinger_scalar`, `wirtinger_lipschitz`, `master_inequality`, `master_inequality_fixed`, `dent`,
`dent_fixed`, `instL_norm_ge`, `lemmaS`, `theoremD_hard_landing` depends on axioms:
`[propext, Classical.choice, Quot.sound]`. Full `lake build` (root imports `Slice.AOpt`,
`Slice.LemmaS`): green, 2026-11-07.
