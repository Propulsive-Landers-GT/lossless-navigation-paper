import LcvxObstruction.Abstract
import LcvxObstruction.Nonconvex

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

end LcvxObstruction
