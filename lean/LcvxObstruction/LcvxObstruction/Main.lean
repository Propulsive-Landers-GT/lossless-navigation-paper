import LcvxObstruction.Abstract
import LcvxObstruction.Nonconvex
import LcvxObstruction.DiveBrake
import LcvxObstruction.TheoremD

/-!
# Main theorem: no lossless uniform convex relaxation of 5DOF (model M1, no state constraints)

Combines Theorem A (`Abstract.lean`) with Theorem B (`Nonconvex.lean`).
Also: concrete acceleration classes (`AccLower`, `AccBox`) and non-vacuity lemmas.

Scope: model M1 with `b(0) = e_z`, `b(tf)` free, free initial position/velocity, no
altitude / glide-slope state constraints, fixed final time `tf` in the regime
`δ + ω tf ≤ π/2`.
-/

open MeasureTheory Set Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

open UniformConvexRelaxation

/-- **Main theorem (general acceleration class).** -/
theorem no_lossless_relaxation_5dof {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s)
    (ha₁ : a₁ ∈ Acc) (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (landingSet Acc tf ω δ g) :=
  not_isLossless_of_not_convex
    (not_convex_landingSet g htf hω hδ hreg ha₁c ha₁p hAcc ha₁) R

/-- **Main theorem, LCvx (optimisation) form**: for every cost `J`. -/
theorem no_losslessFor_relaxation_5dof {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s)
    (ha₁ : a₁ ∈ Acc) (R : UniformConvexRelaxation (E3 × E3) Y) (J : E3 × E3 → Y → ℝ) :
    ¬ R.IsLosslessFor J (landingSet Acc tf ω δ g) :=
  not_isLosslessFor_of_not_convex
    (not_convex_landingSet g htf hω hδ hreg ha₁c ha₁p hAcc ha₁) R J

/-! ### Concrete acceleration classes -/

theorem accLower_spec {tf : ℝ} {a₁ : ℝ → ℝ} :
    ∀ a ∈ AccLower tf a₁, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s :=
  fun _ ha => ha

theorem mem_accLower {tf : ℝ} {a₁ : ℝ → ℝ} (ha₁c : ContinuousOn a₁ (Icc 0 tf)) :
    a₁ ∈ AccLower tf a₁ :=
  ⟨ha₁c.integrableOn_Icc, fun _ _ => le_rfl⟩

theorem accBox_spec {tf : ℝ} {a₁ a₂ : ℝ → ℝ} :
    ∀ a ∈ AccBox tf a₁ a₂, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s :=
  fun _ ha => ⟨ha.1, fun s hs => (ha.2 s hs).1⟩

theorem mem_accBox {tf : ℝ} {a₁ a₂ : ℝ → ℝ} (ha₁c : ContinuousOn a₁ (Icc 0 tf))
    (h12 : ∀ s ∈ Icc 0 tf, a₁ s ≤ a₂ s) : a₁ ∈ AccBox tf a₁ a₂ :=
  ⟨ha₁c.integrableOn_Icc, fun s hs => ⟨le_rfl, h12 s hs⟩⟩

/-- **Main theorem, abstract class** `a ≥ a₁` (math/00 §4). -/
theorem no_lossless_relaxation_5dof_lower {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (landingSet (AccLower tf a₁) tf ω δ g) :=
  no_lossless_relaxation_5dof g htf hω hδ hreg ha₁c ha₁p accLower_spec (mem_accLower ha₁c) R

/-- **Main theorem, box class** `a₁ ≤ a ≤ a₂` (throttle bounds `ρ₁ ≤ T ≤ ρ₂`). -/
theorem no_lossless_relaxation_5dof_box {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {tf ω δ : ℝ} {a₁ a₂ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (h12 : ∀ s ∈ Icc 0 tf, a₁ s ≤ a₂ s) (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (landingSet (AccBox tf a₁ a₂) tf ω δ g) :=
  no_lossless_relaxation_5dof g htf hω hδ hreg ha₁c ha₁p accBox_spec (mem_accBox ha₁c h12) R

/-! ### Non-vacuity of the model -/

/-- An admissible control exists (the extreme arc), so the hypotheses are consistent. -/
theorem exists_admissible {tf ω δ : ℝ} {Acc : Set (ℝ → ℝ)} {a₁ : ℝ → ℝ} (ha₁ : a₁ ∈ Acc)
    (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hδπ : δ ≤ π) (hωtf : ω * tf ≤ π) :
    ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b :=
  ⟨a₁, arcD ω δ ex, arcB ω ex, ha₁, arc_admissible norm_ex inner_ex_ez hω hδ hδπ hωtf⟩

/-- The landing set is nonempty (so "`F_tf` is not convex" is not a statement about `∅`;
indeed `∅` is convex). -/
theorem landingSet_nonempty {tf ω δ : ℝ} {Acc : Set (ℝ → ℝ)} {a₁ : ℝ → ℝ} (g : E3)
    (ha₁ : a₁ ∈ Acc) (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hδπ : δ ≤ π) (hωtf : ω * tf ≤ π) :
    (landingSet Acc tf ω δ g).Nonempty := by
  obtain ⟨a, d, b, ha, hatt⟩ := exists_admissible ha₁ hω hδ hδπ hωtf
  have : -(∫ s in Icc 0 tf, a s • d s) - tf • g ∈ Prod.snd '' landingSet Acc tf ω δ g := by
    rw [snd_image_landingSet g]
    exact ⟨_, ⟨a, d, b, ha, hatt, rfl⟩, rfl⟩
  obtain ⟨θ, hθ, -⟩ := this
  exact ⟨θ, hθ⟩

/-- Sanity check of the hypotheses of the main theorem: they are jointly satisfiable
(e.g. `tf = 1`, `ω = 1`, `δ = 0`, `a₁ ≡ 1`). -/
theorem main_hypotheses_satisfiable :
    ∃ tf ω δ : ℝ, ∃ a₁ : ℝ → ℝ, 0 < tf ∧ 0 < ω ∧ 0 ≤ δ ∧ δ + ω * tf ≤ π / 2 ∧
      ContinuousOn a₁ (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, 0 < a₁ s :=
  ⟨1, 1, 0, fun _ => 1, one_pos, one_pos, le_rfl, by linarith [Real.pi_gt_three],
    continuousOn_const, fun _ _ => one_pos⟩

/-! ### Main theorem with altitude / glide-slope state constraints (Theorem B*) -/

/-- **Main theorem (state-constrained, every horizon).** Model M1 with constant acceleration
bounds `0 < a_min ≤ a_max` (constant mass: `a = T/m₀`, `T ∈ [ρ₁, ρ₂]`), gravity `-g₀ e_z` with
`g₀ < a_max` (full-throttle thrust-to-weight `> 1`), gimbal `0 < δ < π/2`, slew rate `ω > 0`,
any horizon `tf > 0`, and any state-constraint set `X` containing the glide-slope cone
`{r_z ≥ 0, tan γ ‖r_h‖ ≤ r_z}` (`tanγ = 0`: altitude only). Then no uniform convex relaxation is
lossless for the constrained landing set. -/
theorem no_lossless_relaxation_constrained_5dof {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ2 : δ < π / 2)
    (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ < amax) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless
      (constrainedLandingSet (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsStf, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet hsS hsStf hω hωs hreg hamin h hg.le htan hS
      (fun _ ha => ha) (aW_mem_accBox h) hX) R

/-- LCvx (optimisation) form of the state-constrained main theorem, for every cost `J`. -/
theorem no_losslessFor_relaxation_constrained_5dof {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ2 : δ < π / 2)
    (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ < amax) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) (J : E3 × E3 → Y → ℝ) :
    ¬ R.IsLosslessFor J
      (constrainedLandingSet (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ (-(g₀ • ez)) X) :=
  fun hL => no_lossless_relaxation_constrained_5dof htf hω hδ hδ2 hamin h hg htan hX R
    hL.isLossless

/-- Non-vacuity of the constrained main theorem: the constrained landing set is nonempty
(it contains the dive-then-brake witnesses). -/
theorem constrainedLandingSet_nonempty {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf)
    (hω : 0 < ω) (hδ : 0 < δ) (hδ2 : δ < π / 2) (hamin : 0 < amin) (h : amin ≤ amax)
    (hg : g₀ < amax) (htan : 0 ≤ tanγ) :
    (constrainedLandingSet (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ (-(g₀ • ez))
      (glideSlopeSet tanγ)).Nonempty := by
  obtain ⟨sS, hsS, hsStf, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) htf hω hδ hδ2 hg
  have hδπ : δ ≤ π := by linarith [Real.pi_pos]
  exact ⟨_, _, _, _, aW_mem_accBox h,
    witness_admissible norm_ex inner_ex_ez hsS hω.le hδ.le hδπ hωs,
    (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
    fun t ht => witness_mem_glideSlope norm_ex inner_ex_ez hsS hsStf hω.le hδ.le hreg hamin h
      hg.le htan hS ht⟩

end LcvxObstruction
