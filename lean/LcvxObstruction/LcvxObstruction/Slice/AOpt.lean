import LcvxObstruction.TheoremD

/-!
# Theorem A-opt, the mixing lemma and Proposition T (abstract form)

Source: math/redteam-lift.md §5 and §7 ("Lean-ready statements"), claim `L-Aopt`.

Setting. `𝒯` is any type (the admissible trajectories of the original problem). `Θ` (boundary
data) and `Y` (lifted / relaxed decision variables) are real vector spaces.
* `θ : 𝒯 → Θ` reads off the boundary datum of a trajectory,
* `Φ : 𝒯 → Y` embeds a trajectory into the relaxed variables,
* `c : 𝒯 → ℝ` is the (true) cost of a trajectory.

A **uniform convex relaxation with cost** is a convex set `C ⊆ Θ × Y` with a cost
`J : Θ × Y → ℝ` that is convex on `C`, such that every genuine trajectory is represented:
`(θ τ, Φ τ) ∈ C` and `J (θ τ, Φ τ) = c τ`. (`J` may depend on the datum as well; the
redteam-lift statement has `J : Y → ℝ`, which is the special case `J ∘ Prod.snd`.)

* `mixing`, `mixing_finset`: every convex mixture of genuine trajectories is a relaxed point
  whose relaxed cost is at most the mixture of the true costs (Lemma ML).
* `ValueLossless`: "every relaxed point over a feasible datum is dominated by a genuine
  trajectory at the same datum" (the infimum-free form of `V_rel = V` on `F` with attainment).
* `aOpt`, `aOpt_finset`: **Theorem A-opt**. Under value-losslessness, any convex mixture of
  genuine data that is itself feasible carries a genuine trajectory of cost at most the mixed cost.
* `value_le_convexCombination`: the infimum form, `V (∑ λᵢ xᵢ) ≤ ∑ λᵢ V xᵢ` whenever the `xᵢ` and
  `∑ λᵢ xᵢ` lie in `F` (i.e. `V` agrees with its convex envelope on `F`).
* `no_valueLossless_of_strict` (**Corollary T-abstract / Prop T skeleton**): two genuine
  trajectories with equal cost `Λ` whose midpoint datum is feasible but only by trajectories of
  cost `> Λ` rule out every value-lossless uniform convex relaxation.
* `stateLinear_lossy_of_gap`: Theorem D with a general cost `f ∘ ρ + P` (`P` the convex penalty
  vanishing on genuine points, as in `TheoremD.lean`).

The M1-specific inputs of Prop T (F1–F5 of math/redteam-lift.md §7: angle bound, rigidity,
Aumann/unique maximizer, admissibility of the mixed datum, strictness) are NOT formalized here.
-/

open Set

namespace LcvxObstruction

namespace Slice

variable {𝒯 Θ Y : Type*} [AddCommGroup Θ] [Module ℝ Θ] [AddCommGroup Y] [Module ℝ Y]

/-- A uniform convex relaxation with a convex cost, representing the original problem
`(θ, Φ, c)` on the trajectory type `𝒯`. -/
structure CostRelaxation (θ : 𝒯 → Θ) (Φ : 𝒯 → Y) (c : 𝒯 → ℝ) where
  /-- joint (data, lifted variable) constraint set -/
  C : Set (Θ × Y)
  convex : Convex ℝ C
  /-- relaxed cost -/
  J : Θ × Y → ℝ
  J_convex : ConvexOn ℝ C J
  /-- every genuine trajectory is a relaxed point -/
  mem : ∀ τ, (θ τ, Φ τ) ∈ C
  /-- with the same cost -/
  cost : ∀ τ, J (θ τ, Φ τ) = c τ

namespace CostRelaxation

variable {θ : 𝒯 → Θ} {Φ : 𝒯 → Y} {c : 𝒯 → ℝ}

/-- **Lemma ML (mixing, finite form).** -/
theorem mixing_finset (R : CostRelaxation θ Φ c) {ι : Type*} (s : Finset ι) (τ : ι → 𝒯)
    (w : ι → ℝ) (hw₀ : ∀ i ∈ s, 0 ≤ w i) (hw₁ : ∑ i ∈ s, w i = 1) :
    (∑ i ∈ s, w i • θ (τ i), ∑ i ∈ s, w i • Φ (τ i)) ∈ R.C ∧
      R.J (∑ i ∈ s, w i • θ (τ i), ∑ i ∈ s, w i • Φ (τ i)) ≤ ∑ i ∈ s, w i * c (τ i) := by
  have hpair : (∑ i ∈ s, w i • θ (τ i), ∑ i ∈ s, w i • Φ (τ i)) =
      ∑ i ∈ s, w i • (θ (τ i), Φ (τ i)) := by
    simp [Prod.ext_iff, Prod.fst_sum, Prod.snd_sum]
  rw [hpair]
  refine ⟨R.convex.sum_mem hw₀ hw₁ fun i _ => R.mem _, ?_⟩
  have := R.J_convex.map_sum_le hw₀ hw₁ fun i _ => R.mem (τ i)
  simpa [smul_eq_mul, R.cost] using this

/-- **Lemma ML (mixing, two-point form).** -/
theorem mixing (R : CostRelaxation θ Φ c) (τ₁ τ₂ : 𝒯) {l : ℝ} (hl₀ : 0 ≤ l) (hl₁ : l ≤ 1) :
    (l • θ τ₁ + (1 - l) • θ τ₂, l • Φ τ₁ + (1 - l) • Φ τ₂) ∈ R.C ∧
      R.J (l • θ τ₁ + (1 - l) • θ τ₂, l • Φ τ₁ + (1 - l) • Φ τ₂) ≤
        l * c τ₁ + (1 - l) * c τ₂ := by
  have hm : (l • θ τ₁ + (1 - l) • θ τ₂, l • Φ τ₁ + (1 - l) • Φ τ₂) =
      l • (θ τ₁, Φ τ₁) + (1 - l) • (θ τ₂, Φ τ₂) := by simp
  rw [hm]
  refine ⟨R.convex (R.mem τ₁) (R.mem τ₂) hl₀ (by linarith) (by ring), ?_⟩
  have := R.J_convex.2 (R.mem τ₁) (R.mem τ₂) hl₀ (by linarith : 0 ≤ 1 - l) (by ring)
  simpa [smul_eq_mul, R.cost] using this

/-- **Value-lossless on `F = range θ`** (infimum-free form): every relaxed point over a feasible
datum is dominated by a genuine trajectory with the same datum. This follows from
`V_rel = V` on `F` together with attainment of `V`; it is implied by the standard LCvx
guarantee (relaxed optimum attained and genuine). -/
def ValueLossless (R : CostRelaxation θ Φ c) : Prop :=
  ∀ x y, (x, y) ∈ R.C → x ∈ range θ → ∃ τ, θ τ = x ∧ c τ ≤ R.J (x, y)

/-- **Theorem A-opt (finite form).** -/
theorem aOpt_finset (R : CostRelaxation θ Φ c) (hVL : R.ValueLossless) {ι : Type*}
    (s : Finset ι) (τ : ι → 𝒯) (w : ι → ℝ) (hw₀ : ∀ i ∈ s, 0 ≤ w i) (hw₁ : ∑ i ∈ s, w i = 1)
    (hF : ∑ i ∈ s, w i • θ (τ i) ∈ range θ) :
    ∃ τ', θ τ' = ∑ i ∈ s, w i • θ (τ i) ∧ c τ' ≤ ∑ i ∈ s, w i * c (τ i) := by
  obtain ⟨hC, hJ⟩ := R.mixing_finset s τ w hw₀ hw₁
  obtain ⟨τ', h1, h2⟩ := hVL _ _ hC hF
  exact ⟨τ', h1, h2.trans hJ⟩

/-- **Theorem A-opt (two-point form, math/redteam-lift.md §7).** -/
theorem aOpt (R : CostRelaxation θ Φ c) (hVL : R.ValueLossless) (τ₁ τ₂ : 𝒯) {l : ℝ}
    (hl₀ : 0 ≤ l) (hl₁ : l ≤ 1) (hF : l • θ τ₁ + (1 - l) • θ τ₂ ∈ range θ) :
    ∃ τ, θ τ = l • θ τ₁ + (1 - l) • θ τ₂ ∧ c τ ≤ l * c τ₁ + (1 - l) * c τ₂ := by
  obtain ⟨hC, hJ⟩ := R.mixing τ₁ τ₂ hl₀ hl₁
  obtain ⟨τ, h1, h2⟩ := hVL _ _ hC hF
  exact ⟨τ, h1, h2.trans hJ⟩

end CostRelaxation

/-- The true value function `V x = inf {c τ | θ τ = x}` (junk value `0` off `F` or if unbounded
below; all statements below assume the fibres are nonempty and bounded below). -/
noncomputable def value (θ : 𝒯 → Θ) (c : 𝒯 → ℝ) (x : Θ) : ℝ := sInf (c '' (θ ⁻¹' {x}))

omit [AddCommGroup Θ] [Module ℝ Θ] in
theorem value_le {θ : 𝒯 → Θ} {c : 𝒯 → ℝ} {x : Θ} (hb : BddBelow (c '' (θ ⁻¹' {x}))) {τ : 𝒯}
    (hτ : θ τ = x) : value θ c x ≤ c τ :=
  csInf_le hb ⟨τ, hτ, rfl⟩

/-- **Theorem A-opt, infimum form ("V = V** on F").** Under value-losslessness, for data
`xᵢ ∈ F` whose convex combination `x = ∑ wᵢ xᵢ` is in `F` (with `V x` well defined, i.e. its
fibre bounded below), `V x ≤ ∑ wᵢ V xᵢ`. -/
theorem value_le_convexCombination {θ : 𝒯 → Θ} {Φ : 𝒯 → Y} {c : 𝒯 → ℝ}
    (R : CostRelaxation θ Φ c) (hVL : R.ValueLossless) {ι : Type*} (s : Finset ι) (x : ι → Θ)
    (w : ι → ℝ) (hw₀ : ∀ i ∈ s, 0 ≤ w i) (hw₁ : ∑ i ∈ s, w i = 1)
    (hxF : ∀ i ∈ s, x i ∈ range θ)
    (hF : ∑ i ∈ s, w i • x i ∈ range θ) (hb : BddBelow (c '' (θ ⁻¹' {∑ i ∈ s, w i • x i}))) :
    value θ c (∑ i ∈ s, w i • x i) ≤ ∑ i ∈ s, w i * value θ c (x i) := by
  classical
  -- approximate each `V xᵢ` from above by genuine trajectories
  refine le_of_forall_pos_le_add fun ε hε => ?_
  have : Nonempty 𝒯 := ⟨hF.choose⟩
  have happrox : ∀ i ∈ s, ∃ τ, θ τ = x i ∧ c τ < value θ c (x i) + ε := by
    intro i hi
    obtain ⟨τ₀, hτ₀⟩ := hxF i hi
    have hne : (c '' (θ ⁻¹' {x i})).Nonempty := ⟨c τ₀, τ₀, hτ₀, rfl⟩
    obtain ⟨_, ⟨τ, hτ, rfl⟩, hlt⟩ := exists_lt_of_csInf_lt hne (lt_add_of_pos_right _ hε)
    exact ⟨τ, hτ, hlt⟩
  choose! τ hτx hτc using happrox
  have hsum : ∑ i ∈ s, w i • θ (τ i) = ∑ i ∈ s, w i • x i :=
    Finset.sum_congr rfl fun i hi => by rw [hτx i hi]
  obtain ⟨τ', h1, h2⟩ := R.aOpt_finset hVL s τ w hw₀ hw₁ (hsum ▸ hF)
  calc value θ c (∑ i ∈ s, w i • x i) ≤ c τ' := value_le hb (h1.trans hsum)
    _ ≤ ∑ i ∈ s, w i * c (τ i) := h2
    _ ≤ ∑ i ∈ s, w i * (value θ c (x i) + ε) :=
        Finset.sum_le_sum fun i hi => mul_le_mul_of_nonneg_left (hτc i hi).le (hw₀ i hi)
    _ = ∑ i ∈ s, w i * value θ c (x i) + ε := by
        simp [mul_add, Finset.sum_add_distrib, ← Finset.sum_mul, hw₁]

/-- **Corollary T-abstract (Prop T skeleton, math/redteam-lift.md §7).** Suppose two genuine
trajectories `τ₊, τ₋` have the same cost `Λ`, the midpoint `x'` of their data is feasible, but
every genuine trajectory at `x'` costs strictly more than `Λ`. Then no uniform convex relaxation
with convex cost representing the problem is value-lossless. -/
theorem no_valueLossless_of_strict {θ : 𝒯 → Θ} {Φ : 𝒯 → Y} {c : 𝒯 → ℝ} {τp τm : 𝒯} {Λ : ℝ}
    (h1p : c τp = Λ) (h1m : c τm = Λ)
    (h2 : (1 / 2 : ℝ) • θ τp + (1 / 2 : ℝ) • θ τm ∈ range θ)
    (h3 : ∀ τ, θ τ = (1 / 2 : ℝ) • θ τp + (1 / 2 : ℝ) • θ τm → Λ < c τ)
    (R : CostRelaxation θ Φ c) : ¬ R.ValueLossless := by
  intro hVL
  have h2' : (1 / 2 : ℝ) • θ τp + (1 - 1 / 2 : ℝ) • θ τm ∈ range θ := by norm_num at h2 ⊢; exact h2
  obtain ⟨τ, hτ, hc⟩ := R.aOpt hVL τp τm (by norm_num) (by norm_num) h2'
  have := h3 τ (by rw [hτ]; norm_num)
  rw [h1p, h1m] at hc
  linarith

/-- The feasibility skeleton (Claim A) in the same language: if the midpoint of two feasible
data is infeasible, no uniform convex relaxation (any cost) that is lossless in feasibility
exists. Stated directly: the mixed point is a relaxed point over an infeasible datum. -/
theorem mixed_point_of_infeasible_midpoint {θ : 𝒯 → Θ} {Φ : 𝒯 → Y} {c : 𝒯 → ℝ}
    (R : CostRelaxation θ Φ c) (τ₁ τ₂ : 𝒯)
    (h : (1 / 2 : ℝ) • θ τ₁ + (1 / 2 : ℝ) • θ τ₂ ∉ range θ) :
    ∃ y, ((1 / 2 : ℝ) • θ τ₁ + (1 / 2 : ℝ) • θ τ₂, y) ∈ R.C ∧
      (1 / 2 : ℝ) • θ τ₁ + (1 / 2 : ℝ) • θ τ₂ ∉ range θ := by
  obtain ⟨hC, -⟩ := R.mixing τ₁ τ₂ (l := 1 / 2) (by norm_num) (by norm_num)
  have e : (1 : ℝ) - 1 / 2 = 1 / 2 := by norm_num
  rw [e] at hC
  exact ⟨_, hC, h⟩

end Slice

/-! ### Theorem D with a general readout cost (the penalty class of math/02 Def 11.1) -/

section DGeneral

variable {Y E : Type*} [AddCommGroup Y] [Module ℝ Y] [AddCommGroup E] [Module ℝ E]

/-- **Theorem D, general cost `f ∘ ρ + P`.** Let `S` be a state-linear relaxation (convex `C`,
affine readout `ρ`, convex penalty `P ≥ 0` on `C`) containing the genuine readouts `Reach` with
zero penalty. For any readout cost `f : E → ℝ` (convexity of `f` is not even needed) and any
`x ∈ convexHull Reach` that beats every genuine readout by a margin `ε > 0`, the relaxed problem
`min_{y ∈ C} f (ρ y) + P y` has a point of value `f x`, while every genuine readout costs at
least `f x + ε`: the relaxation is lossy by at least `ε`. -/
theorem StateLinearRelaxation.lossy_of_gap (S : StateLinearRelaxation Y E) {Reach : Set E}
    (h : S.Contains Reach) (f : E → ℝ) {x : E} (hx : x ∈ convexHull ℝ Reach) {ε : ℝ}
    (hgap : ∀ z ∈ Reach, f x + ε ≤ f z) :
    (∃ y ∈ S.C, S.ρ y = x ∧ f (S.ρ y) + S.P y = f x) ∧
      ∀ z ∈ Reach, f x + ε ≤ f z + 0 := by
  obtain ⟨y, hy, hρ, hP⟩ := S.convexHull_subset h x hx
  exact ⟨⟨y, hy, hρ, by rw [hρ, hP, add_zero]⟩, fun z hz => by simpa using hgap z hz⟩

end DGeneral

end LcvxObstruction
