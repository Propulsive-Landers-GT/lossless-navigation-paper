import Mathlib

/-!
# Theorem A: the abstract obstruction to lossless uniform convex relaxation

Let `Θ` (boundary data, e.g. initial position/velocity) and `Y` (any space of lifted /
relaxed decision variables) be real vector spaces.

A *uniform convex relaxation* is a single convex set `C ⊆ Θ × Y`; the relaxed problem for the
datum `θ` is posed over the slice `C_θ = {y | (θ, y) ∈ C}` (with any cost whatsoever).
The relaxation is *lossless* (feasibility form) for the feasible-data set `F ⊆ Θ` if
`C_θ ≠ ∅ ↔ θ ∈ F` for every `θ`.

Theorem A: if a lossless uniform convex relaxation exists then `F` is convex
(it is the linear image `Prod.fst '' C`), and so is every linear/affine image of `F`.
Contrapositive: if some linear/affine image of `F` is not convex, no lossless uniform convex
relaxation exists.

We also give the optimisation ("LCvx") form of losslessness and show it implies the
feasibility form, so the obstruction is cost-independent.
-/

namespace LcvxObstruction

variable {Θ Y Θ' : Type*}
variable [AddCommGroup Θ] [Module ℝ Θ] [AddCommGroup Y] [Module ℝ Y]
variable [AddCommGroup Θ'] [Module ℝ Θ']

/-- A **uniform convex relaxation** with boundary-data space `Θ` and lifted-variable space `Y`:
a single convex set `C ⊆ Θ × Y`. The boundary data `θ` enter *jointly convexly* together with
the decision variables `y` (this covers lifted variables, slacks, any discretisation, ...).
The relaxed problem for the datum `θ` is posed over the slice `C_θ = {y | (θ,y) ∈ C}`. -/
structure UniformConvexRelaxation (Θ Y : Type*) [AddCommGroup Θ] [Module ℝ Θ]
    [AddCommGroup Y] [Module ℝ Y] where
  /-- The joint constraint set in (data, decision) space. -/
  C : Set (Θ × Y)
  /-- Joint convexity. -/
  convex : Convex ℝ C

namespace UniformConvexRelaxation

/-- The feasible set of the relaxed problem for the boundary datum `θ`. -/
def slice (R : UniformConvexRelaxation Θ Y) (θ : Θ) : Set Y := {y | (θ, y) ∈ R.C}

/-- **Lossless (feasibility form)** with respect to the set `F` of data for which the
original (nonconvex) problem is feasible: for every datum `θ`, the relaxed problem is feasible
iff the original problem is. -/
def IsLossless (R : UniformConvexRelaxation Θ Y) (F : Set Θ) : Prop :=
  ∀ θ, (R.slice θ).Nonempty ↔ θ ∈ F

/-- **Lossless (optimisation / LCvx form)** for the cost `J` (arbitrary, not necessarily
convex): (1) the relaxation contains the original problem — whenever the original problem is
feasible, so is the relaxed one; (2) whenever the relaxed problem is feasible it attains its
optimum at some `y`, and that relaxed optimum corresponds to a feasible solution of the original
problem (formally: `θ ∈ F`). This is the standard meaning of "lossless convexification". -/
def IsLosslessFor (R : UniformConvexRelaxation Θ Y) (J : Θ → Y → ℝ) (F : Set Θ) : Prop :=
  (∀ θ ∈ F, (R.slice θ).Nonempty) ∧
    ∀ θ, (R.slice θ).Nonempty → ∃ y ∈ R.slice θ, IsMinOn (J θ) (R.slice θ) y ∧ θ ∈ F

/-- The LCvx (optimisation) form of losslessness implies the feasibility form,
for every cost `J`. -/
theorem IsLosslessFor.isLossless {R : UniformConvexRelaxation Θ Y} {J : Θ → Y → ℝ}
    {F : Set Θ} (h : R.IsLosslessFor J F) : R.IsLossless F := by
  intro θ
  constructor
  · intro hne
    obtain ⟨_, _, _, hθ⟩ := h.2 θ hne
    exact hθ
  · exact h.1 θ

/-- Under losslessness, `F` is exactly the projection of `C` onto the data space. -/
theorem IsLossless.eq_image_fst {R : UniformConvexRelaxation Θ Y} {F : Set Θ}
    (h : R.IsLossless F) : F = Prod.fst '' R.C := by
  ext θ
  rw [← h θ]
  constructor
  · rintro ⟨y, hy⟩
    exact ⟨(θ, y), hy, rfl⟩
  · rintro ⟨⟨θ', y⟩, hy, rfl⟩
    exact ⟨y, hy⟩

end UniformConvexRelaxation

open UniformConvexRelaxation

/-- **Theorem A** (abstract obstruction). If `C ⊆ Θ × Y` is convex and `F ⊆ Θ` satisfies
`∀ θ, (∃ y, (θ, y) ∈ C) ↔ θ ∈ F`, then `F` is convex. -/
theorem theoremA {C : Set (Θ × Y)} (hC : Convex ℝ C) {F : Set Θ}
    (hF : ∀ θ, (∃ y, (θ, y) ∈ C) ↔ θ ∈ F) : Convex ℝ F := by
  have : F = Prod.fst '' C := by
    ext θ
    rw [← hF θ]
    constructor
    · rintro ⟨y, hy⟩
      exact ⟨(θ, y), hy, rfl⟩
    · rintro ⟨⟨θ', y⟩, hy, rfl⟩
      exact ⟨y, hy⟩
  rw [this]
  exact hC.linear_image (LinearMap.fst ℝ Θ Y)

/-- Theorem A, stated for a `UniformConvexRelaxation`. -/
theorem UniformConvexRelaxation.IsLossless.convex {R : UniformConvexRelaxation Θ Y} {F : Set Θ}
    (h : R.IsLossless F) : Convex ℝ F :=
  theoremA R.convex fun θ => h θ

/-- Theorem A pushed through a linear map (e.g. the projection `(r₀, v₀) ↦ v₀`). -/
theorem UniformConvexRelaxation.IsLossless.convex_linear_image {R : UniformConvexRelaxation Θ Y} {F : Set Θ}
    (h : R.IsLossless F) (L : Θ →ₗ[ℝ] Θ') : Convex ℝ (L '' F) :=
  h.convex.linear_image L

/-- Theorem A pushed through an affine map. -/
theorem UniformConvexRelaxation.IsLossless.convex_affine_image {R : UniformConvexRelaxation Θ Y} {F : Set Θ}
    (h : R.IsLossless F) (L : Θ →ᵃ[ℝ] Θ') : Convex ℝ (L '' F) :=
  h.convex.affine_image L

/-- **Corollary of Theorem A.** If `F` is not convex, then *no* uniform convex relaxation
(with any lifted-variable space `Y`) is lossless for `F`. -/
theorem not_isLossless_of_not_convex {F : Set Θ} (hF : ¬ Convex ℝ F)
    (R : UniformConvexRelaxation Θ Y) : ¬ R.IsLossless F :=
  fun h => hF h.convex

/-- **Corollary of Theorem A** (linear-image form). If some linear image of `F` is not convex,
then no uniform convex relaxation is lossless for `F`. -/
theorem not_isLossless_of_not_convex_linear_image {F : Set Θ} (L : Θ →ₗ[ℝ] Θ')
    (hF : ¬ Convex ℝ (L '' F)) (R : UniformConvexRelaxation Θ Y) : ¬ R.IsLossless F :=
  fun h => hF (h.convex_linear_image L)

/-- Optimisation-form corollary: for any cost `J`, no uniform convex relaxation is lossless
in the LCvx sense when `F` is not convex. -/
theorem not_isLosslessFor_of_not_convex {F : Set Θ} (hF : ¬ Convex ℝ F)
    (R : UniformConvexRelaxation Θ Y) (J : Θ → Y → ℝ) : ¬ R.IsLosslessFor J F :=
  fun h => hF h.isLossless.convex

end LcvxObstruction
