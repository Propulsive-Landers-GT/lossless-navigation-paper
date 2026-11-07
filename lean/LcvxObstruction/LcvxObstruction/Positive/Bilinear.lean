import Mathlib

/-!
# Positive side, Tier 4: bilinear restriction for CCP (P22)

Source: `math/04` §11 "Deferred" (CCP on `⟪w,u⟫ ≥ σ cos δ`), blueprint P22.

* `bilinear_restriction` : `⟪w,u⟫ ≥ ¼(‖w₀+u₀‖² + 2⟪w₀+u₀,(w+u)-(w₀+u₀)⟫) - ¼‖w-u‖²`.
* `bilinear_restriction_eq` : equality at `(w,u) = (w₀,u₀)`.
* `convex_ccpSet` : the restricted constraint `σ k ≤ RHS(w,u)` defines a convex set of
  `(w,u,σ)`.
* `ccpSet_subset` : every point of it satisfies the original bilinear constraint
  `σ k ≤ ⟪w,u⟫`, so CCP iterates stay feasible.
-/

open scoped RealInnerProductSpace

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- The convex (concave-majorant-free) lower model of `⟪w,u⟫` linearised at `(w₀,u₀)`. -/
noncomputable def ccpModel (w₀ u₀ w u : V) : ℝ :=
  1/4 * (‖w₀ + u₀‖ ^ 2 + 2 * ⟪w₀ + u₀, (w + u) - (w₀ + u₀)⟫) - 1/4 * ‖w - u‖ ^ 2

/-- **P22.** The CCP model is a global lower bound of the bilinear form. -/
theorem bilinear_restriction (w₀ u₀ w u : V) : ccpModel w₀ u₀ w u ≤ ⟪w, u⟫ := by
  unfold ccpModel
  have hpol : ⟪w, u⟫ = 1/4 * ‖w + u‖ ^ 2 - 1/4 * ‖w - u‖ ^ 2 := by
    rw [norm_add_sq_real, norm_sub_sq_real]; ring
  have htan : ‖w₀ + u₀‖ ^ 2 + 2 * ⟪w₀ + u₀, (w + u) - (w₀ + u₀)⟫ ≤ ‖w + u‖ ^ 2 := by
    have h := norm_sub_sq_real (w + u) (w₀ + u₀)
    rw [inner_sub_right, real_inner_self_eq_norm_sq, real_inner_comm]
    nlinarith [sq_nonneg ‖(w + u) - (w₀ + u₀)‖]
  rw [hpol]
  linarith

/-- Equality of the CCP model at the linearisation point. -/
theorem bilinear_restriction_eq (w₀ u₀ : V) : ccpModel w₀ u₀ w₀ u₀ = ⟪w₀, u₀⟫ := by
  unfold ccpModel
  rw [sub_self, inner_zero_right, mul_zero, add_zero, norm_add_sq_real, norm_sub_sq_real]
  ring

theorem norm_sq_comb_le (x y : V) {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (hab : a + b = 1) :
    ‖a • x + b • y‖ ^ 2 ≤ a * ‖x‖ ^ 2 + b * ‖y‖ ^ 2 := by
  have h1 : ‖a • x + b • y‖ ^ 2 = a ^ 2 * ‖x‖ ^ 2 + 2 * (a * b) * ⟪x, y⟫ + b ^ 2 * ‖y‖ ^ 2 := by
    rw [norm_add_sq_real, norm_smul, norm_smul, real_inner_smul_left, real_inner_smul_right,
      Real.norm_of_nonneg ha, Real.norm_of_nonneg hb]; ring
  have h2 := norm_sub_sq_real x y
  have hb' : b = 1 - a := by linarith
  subst hb'
  nlinarith [mul_nonneg (mul_nonneg ha hb) (sq_nonneg ‖x - y‖)]

/-- The CCP-restricted constraint set `{(w,u,σ) | σ k ≤ ccpModel w₀ u₀ w u}`. -/
def ccpSet (w₀ u₀ : V) (k : ℝ) : Set (V × V × ℝ) :=
  {p | p.2.2 * k ≤ ccpModel w₀ u₀ p.1 p.2.1}

/-- The CCP-restricted constraint is convex (the model is concave in `(w,u)`). -/
theorem convex_ccpSet (w₀ u₀ : V) (k : ℝ) : Convex ℝ (ccpSet w₀ u₀ k) := by
  intro p hp q hq a b ha hb hab
  simp only [ccpSet, Set.mem_ofPred_eq, ccpModel] at *
  simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd, smul_eq_mul]
  have hdiff : a • p.1 + b • q.1 - (a • p.2.1 + b • q.2.1) =
      a • (p.1 - p.2.1) + b • (q.1 - q.2.1) := by module
  have hlin : a • p.1 + b • q.1 + (a • p.2.1 + b • q.2.1) - (w₀ + u₀) =
      a • (p.1 + p.2.1 - (w₀ + u₀)) + b • (q.1 + q.2.1 - (w₀ + u₀)) := by
    have : w₀ + u₀ = a • (w₀ + u₀) + b • (w₀ + u₀) := by rw [← add_smul, hab, one_smul]
    conv_lhs => rw [this]
    module
  rw [hdiff, hlin, inner_add_right, real_inner_smul_right, real_inner_smul_right]
  have hq2 := norm_sq_comb_le (p.1 - p.2.1) (q.1 - q.2.1) ha hb hab
  have hc : ‖w₀ + u₀‖ ^ 2 = a * ‖w₀ + u₀‖ ^ 2 + b * ‖w₀ + u₀‖ ^ 2 := by
    rw [← add_mul, hab, one_mul]
  nlinarith [mul_le_mul_of_nonneg_left hp ha, mul_le_mul_of_nonneg_left hq hb]

/-- CCP iterates are feasible for the original bilinear constraint. -/
theorem ccpSet_subset (w₀ u₀ : V) (k : ℝ) {p : V × V × ℝ} (hp : p ∈ ccpSet w₀ u₀ k) :
    p.2.2 * k ≤ ⟪p.1, p.2.1⟫ :=
  le_trans hp (bilinear_restriction w₀ u₀ p.1 p.2.1)

/-- The linearisation point itself is CCP-feasible whenever it is feasible (monotone CCP). -/
theorem mem_ccpSet_self (w₀ u₀ : V) {σ k : ℝ} (h : σ * k ≤ ⟪w₀, u₀⟫) :
    (w₀, u₀, σ) ∈ ccpSet w₀ u₀ k := by
  show σ * k ≤ ccpModel w₀ u₀ w₀ u₀
  rw [bilinear_restriction_eq]; exact h

end LcvxPositive
