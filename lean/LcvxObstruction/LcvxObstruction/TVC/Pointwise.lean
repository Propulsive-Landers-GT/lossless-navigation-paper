import Mathlib

/-!
# Pure TVC: elementary pointwise inequalities of the TVC-1 proof (math/06 §4.2–4.3; blueprint
TVC-P1, P2, P3, Q4)

Scalar forms (all quantities real): `b_z` vertical component of the unit body axis, `H = ‖h‖²`
the squared horizontal tilt (`H = 1 - b_z²`), `p = ⟪u, b⟫`, `q = ‖Π_b u‖`, `a₂` maximal thrust
acceleration, `f = p - ε v²`.

* `early_tilt_identity` (P1): `1 - b_z = H / (1 + b_z)`.
* `speed_sq_le` (P1): if `b_z ḃ_z = -⟪h, ḣ⟫` with `|⟪h,ḣ⟫| ≤ ‖h‖‖ḣ‖`, then
  `v² b_z² ≤ ‖ḣ‖²` where `v² = ‖ḣ‖² + ḃ_z²`.
* `late_majorant` (P2): `p² + q² ≤ a₂²`, `b_z² + H = 1`, `a₂ > 0` ⇒
  `a₂ - p b_z ≥ (q² b_z² + a₂² H)/(2 a₂)`.
* `late_pi_ge` (P3 / §5.6): `f ≤ a₂`, `a₂ ≥ 0`, `b_z ≤ 1` ⇒ `a₂ - f b_z ≥ b_z |a₂ - f|` (either sign of
  `f`), and `a₂ - f b_z ≥ |a₂ - f|` if `f ≥ 0`.
* `sq_add_le_split`, `sq_sub_pos_ge_split` (Q4 / §4.3): `(x+y)² ≤ (1+κ)x² + (1+1/κ)y²` and
  `(x - y)² ≥ (1-ϑ)x² - (1/ϑ - 1)y²`.
* `relaxed_contains_ordinary` (PT6, "⊆"): an ordinary control `u = a d` with `a ∈ [a₁, a₂]`,
  unit `d` within angle `δ` of the unit axis `b` lies in
  `𝒞(b) = {⟪u,b⟫ ≥ a₁ cos δ, ‖u‖ ≤ a₂, ‖u - ⟪u,b⟫ b‖ ≤ ⟪u,b⟫ tan δ}` (needs `δ < π/2`).
-/

open Real
open scoped RealInnerProductSpace

namespace LcvxObstruction.TVC

theorem early_tilt_identity {bz H : ℝ} (hH : H = 1 - bz ^ 2) (hbz : 1 + bz ≠ 0) :
    1 - bz = H / (1 + bz) := by
  rw [hH, eq_div_iff hbz]; ring

theorem speed_sq_le {bz bzd hn hdn ip : ℝ} (hbz2 : bz ^ 2 + hn ^ 2 = 1) (hrel : bz * bzd = -ip) (hcs : |ip| ≤ hn * hdn) :
    (hdn ^ 2 + bzd ^ 2) * bz ^ 2 ≤ hdn ^ 2 := by
  have h1 : (bz * bzd) ^ 2 ≤ (hn * hdn) ^ 2 := by
    rw [hrel, neg_sq]; exact sq_le_sq' (by linarith [neg_abs_le ip]) (le_trans (le_abs_self _) hcs)
  nlinarith [h1]

theorem late_majorant {p q a2 bz H : ℝ} (ha2 : 0 < a2)
    (hpq : p ^ 2 + q ^ 2 ≤ a2 ^ 2) (hbzH : bz ^ 2 + H = 1) :
    (q ^ 2 * bz ^ 2 + a2 ^ 2 * H) / (2 * a2) ≤ a2 - p * bz := by
  rw [div_le_iff₀ (by positivity)]
  have h1 : p ^ 2 * bz ^ 2 ≤ (a2 ^ 2 - q ^ 2) * bz ^ 2 :=
    mul_le_mul_of_nonneg_right (by linarith) (sq_nonneg bz)
  nlinarith [sq_nonneg (a2 - p * bz)]

theorem late_pi_ge {f a2 bz : ℝ} (hf : f ≤ a2) (ha2 : 0 ≤ a2) (hbz1 : bz ≤ 1) :
    bz * |a2 - f| ≤ a2 - f * bz := by
  rw [abs_of_nonneg (by linarith)]
  nlinarith [mul_nonneg ha2 (by linarith : 0 ≤ 1 - bz)]

theorem late_pi_ge_of_nonneg {f a2 bz : ℝ} (hf : f ≤ a2) (hf0 : 0 ≤ f) (hbz1 : bz ≤ 1) :
    |a2 - f| ≤ a2 - f * bz := by
  rw [abs_of_nonneg (by linarith)]; nlinarith [mul_nonneg hf0 (by linarith : 0 ≤ 1 - bz)]

theorem sq_add_le_split (x y : ℝ) {κ : ℝ} (hκ : 0 < κ) :
    (x + y) ^ 2 ≤ (1 + κ) * x ^ 2 + (1 + 1 / κ) * y ^ 2 := by
  have : 0 ≤ (κ * x - y) ^ 2 / κ := by positivity
  have e : (1 + κ) * x ^ 2 + (1 + 1 / κ) * y ^ 2 - (x + y) ^ 2 = (κ * x - y) ^ 2 / κ := by
    field_simp; ring
  linarith

theorem sq_sub_pos_ge_split (x y : ℝ) {ϑ : ℝ} (hϑ : 0 < ϑ) :
    (1 - ϑ) * x ^ 2 - (1 / ϑ - 1) * y ^ 2 ≤ (x - y) ^ 2 := by
  have : 0 ≤ (ϑ * x - y) ^ 2 / ϑ := by positivity
  have e : (x - y) ^ 2 - ((1 - ϑ) * x ^ 2 - (1 / ϑ - 1) * y ^ 2) = (ϑ * x - y) ^ 2 / ϑ := by
    field_simp; ring
  linarith

/-- **PT6 "⊆"**: ordinary thrust accelerations lie in the convex relaxed set `𝒞(b)`. -/
theorem relaxed_contains_ordinary {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
    {b d : V} {a a1 a2 δ : ℝ} (hb : ‖b‖ = 1) (hd : ‖d‖ = 1)
    (hang : InnerProductGeometry.angle d b ≤ δ) (hδ : δ < π / 2)
    (ha1 : a1 ≤ a) (ha2 : a ≤ a2) (ha10 : 0 ≤ a1) :
    a1 * cos δ ≤ ⟪a • d, b⟫ ∧ ‖a • d‖ ≤ a2 ∧
      ‖a • d - ⟪a • d, b⟫ • b‖ ≤ ⟪a • d, b⟫ * tan δ := by
  have ha0 : 0 ≤ a := le_trans ha10 ha1
  set c := ⟪d, b⟫ with hc
  have hcos : cos (InnerProductGeometry.angle d b) = c := by
    rw [InnerProductGeometry.cos_angle, hd, hb]; simp [hc]
  have hang0 := InnerProductGeometry.angle_nonneg d b
  have hcδ : cos δ ≤ c := by
    rw [← hcos]
    exact Real.cos_le_cos_of_nonneg_of_le_pi hang0 (by linarith [Real.pi_pos]) hang
  have hcosδ : 0 < cos δ := Real.cos_pos_of_mem_Ioo ⟨by linarith, hδ⟩
  have hc0 : 0 < c := lt_of_lt_of_le hcosδ hcδ
  have hinner : ⟪a • d, b⟫ = a * c := by rw [real_inner_smul_left]
  -- lateral part of `d`: `‖d - c b‖² = 1 - c²`
  have hlat : ‖d - c • b‖ ^ 2 = 1 - c ^ 2 := by
    rw [@norm_sub_sq_real, norm_smul, real_inner_smul_right, hd, hb, Real.norm_eq_abs,
      ← hc]
    rw [mul_one, sq_abs]; ring
  -- `sin(angle) = √(1-c²)` and `sin(angle) ≤ tan δ · cos(angle)`
  have hsin : sin (InnerProductGeometry.angle d b) = ‖d - c • b‖ := by
    have h1 : sin (InnerProductGeometry.angle d b) ^ 2 = ‖d - c • b‖ ^ 2 := by
      rw [hlat, Real.sin_sq, hcos]
    have h2 : 0 ≤ sin (InnerProductGeometry.angle d b) :=
      Real.sin_nonneg_of_nonneg_of_le_pi hang0 (InnerProductGeometry.angle_le_pi d b)
    exact (pow_left_inj₀ h2 (norm_nonneg _) two_ne_zero).mp h1
  have htan : ‖d - c • b‖ ≤ c * tan δ := by
    rw [← hsin, ← hcos, Real.tan_eq_sin_div_cos]
    have hθ : InnerProductGeometry.angle d b < π / 2 := lt_of_le_of_lt hang hδ
    have hcθ : 0 < cos (InnerProductGeometry.angle d b) :=
      Real.cos_pos_of_mem_Ioo ⟨by linarith, hθ⟩
    -- tan is monotone on [0, π/2): tan θ ≤ tan δ
    have hmono : Real.tan (InnerProductGeometry.angle d b) ≤ Real.tan δ := by
      rcases eq_or_lt_of_le hang with h | h
      · rw [h]
      · exact le_of_lt (Real.tan_lt_tan_of_lt_of_lt_pi_div_two (by linarith) hδ h)
    rw [Real.tan_eq_sin_div_cos, Real.tan_eq_sin_div_cos] at hmono
    rw [div_le_div_iff₀ hcθ hcosδ] at hmono
    rw [mul_div_assoc', le_div_iff₀ hcosδ]
    linarith [hmono]
  refine ⟨?_, ?_, ?_⟩
  · rw [hinner]; exact mul_le_mul ha1 hcδ hcosδ.le ha0
  · rw [norm_smul, hd, mul_one, Real.norm_eq_abs, abs_of_nonneg ha0]; exact ha2
  · rw [hinner, mul_smul, ← smul_sub, norm_smul, Real.norm_eq_abs, abs_of_nonneg ha0, mul_assoc]
    exact mul_le_mul_of_nonneg_left htan ha0

end LcvxObstruction.TVC
