import Mathlib

/-!
# Positive side, Tier 5: gimbal-torque-coupled TVC (M3b) — Lemma 8.1 and Theorem C-6 (pointwise)

Source: `math/04` §8; blueprint P23, P24.

* `torque_balance_iff` (**Lemma 8.1**, P23), in `Fin 3 → ℝ` with `⨯₃` and `⬝ᵥ`: for a unit axis
  `b` and `k ≠ 0`, Euler's equation `b × b̈ = k⁻¹ (T × b)` is equivalent to
  `Π_b T = -k Π_b b̈`.
* `throttle_interval` (**C-6 core**, P24), general inner-product space: if `T = T_a b + F` with
  `F ⊥ b`, `‖F‖ = κ`, the exact (nonconvex) constraints
  `ρ₁ ≤ ‖T‖ ≤ ρ₂`, `‖T‖ cos δ ≤ ⟪b,T⟫` are equivalent to the interval
  `κ cos δ ≤ T_a sin δ`, `√(ρ₁²-κ²) ≤ T_a ≤ √(ρ₂²-κ²)`.
* `convex_tvcSet` (**C-6, pointwise**): for a given attitude (hence given `F = -k Π_b b̈`) the
  exact thrust set `{T | ρ₁ ≤ ‖T‖ ≤ ρ₂, ‖T‖ cos δ ≤ ⟪b,T⟫, Π_b T = F}` is convex — no relaxation.
* `tvcSet_upright` (**Cor. 8.2**): with `F = 0` (body held at constant attitude) every admissible
  thrust is parallel to `b` (`δ_eff = 0`).
-/

open scoped RealInnerProductSpace
open Matrix

namespace LcvxPositive

/-! ## Lemma 8.1 in coordinates -/

section Torque

/-- For `v ⊥ b`, `b` unit: `b × (v × b) = v`. -/
theorem cross_cross_perp {b v : Fin 3 → ℝ} (hb : b ⬝ᵥ b = 1) (hv : b ⬝ᵥ v = 0) :
    b ⨯₃ (v ⨯₃ b) = v := by
  rw [cross_cross_eq_smul_sub_smul', hb, dotProduct_comm, hv, one_smul, zero_smul, sub_zero]

theorem cross_proj_left (T b : Fin 3 → ℝ) :
    (T - (b ⬝ᵥ T) • b) ⨯₃ b = T ⨯₃ b := by
  simp [map_sub, map_smul, LinearMap.sub_apply, LinearMap.smul_apply, cross_self]

theorem cross_proj_right (b B : Fin 3 → ℝ) :
    b ⨯₃ (B - (b ⬝ᵥ B) • b) = b ⨯₃ B := by
  simp [map_sub, map_smul, cross_self]

theorem dot_proj (b T : Fin 3 → ℝ) (hb : b ⬝ᵥ b = 1) : b ⬝ᵥ (T - (b ⬝ᵥ T) • b) = 0 := by
  simp [dotProduct_sub, dotProduct_smul, hb]

/-- **Lemma 8.1 (P23), torque balance.** With `k = J⊥/ℓ ≠ 0` and `b` a unit vector, Euler's
equation `b × B = k⁻¹ • (T × b)` (where `B = b̈`) holds iff `Π_b T = -k Π_b B`. -/
theorem torque_balance_iff {b T B : Fin 3 → ℝ} {k : ℝ} (hb : b ⬝ᵥ b = 1) (hk : k ≠ 0) :
    b ⨯₃ B = k⁻¹ • (T ⨯₃ b) ↔ T - (b ⬝ᵥ T) • b = -k • (B - (b ⬝ᵥ B) • b) := by
  set PT := T - (b ⬝ᵥ T) • b
  set PB := B - (b ⬝ᵥ B) • b
  have hTb : T ⨯₃ b = PT ⨯₃ b := (cross_proj_left T b).symm
  have hbB : b ⨯₃ B = b ⨯₃ PB := (cross_proj_right b B).symm
  constructor
  · intro h
    set X := PT + k • PB
    have hX : b ⬝ᵥ X = 0 := by
      have e1 : b ⬝ᵥ PT = 0 := dot_proj b T hb
      have e2 : b ⬝ᵥ PB = 0 := dot_proj b B hb
      simp only [X, dotProduct_add, dotProduct_smul, smul_eq_mul]
      rw [e1, e2]; ring
    have hXb : X ⨯₃ b = 0 := by
      have e1 : PB ⨯₃ b = -(b ⨯₃ PB) := (cross_anticomm b PB).symm
      simp only [X, map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply]
      rw [← hTb, e1, ← hbB, h, smul_neg, smul_smul, mul_inv_cancel₀ hk, one_smul, add_neg_cancel]
    have := cross_cross_perp hb hX
    rw [hXb, map_zero] at this
    have hX0 : X = 0 := this.symm
    have : PT = -(k • PB) := eq_neg_of_add_eq_zero_left hX0
    rw [this, neg_smul]
  · intro h
    rw [hTb, hbB, h, map_smul, LinearMap.smul_apply, ← cross_anticomm, smul_smul, mul_neg,
      inv_mul_cancel₀ hk, neg_one_smul]

end Torque

/-! ## Theorem C-6, pointwise -/

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

theorem norm_sq_axial_add_perp {b F : V} (Ta : ℝ) (hb : ‖b‖ = 1) (hbF : ⟪b, F⟫ = 0) :
    ‖Ta • b + F‖ ^ 2 = Ta ^ 2 + ‖F‖ ^ 2 := by
  rw [norm_add_sq_real, norm_smul, real_inner_smul_left, hbF, Real.norm_eq_abs, hb]
  rw [mul_one, sq_abs]; ring

theorem inner_axial_add_perp {b F : V} (Ta : ℝ) (hb : ‖b‖ = 1) (hbF : ⟪b, F⟫ = 0) :
    ⟪b, Ta • b + F⟫ = Ta := by
  rw [inner_add_right, real_inner_smul_right, real_inner_self_eq_norm_sq, hb, hbF]; ring

/-- **P24 (C-6 core): the throttle interval.** -/
theorem throttle_interval {b F : V} {Ta ρ₁ ρ₂ δ : ℝ} (hb : ‖b‖ = 1) (hbF : ⟪b, F⟫ = 0)
    (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂) (hδ0 : 0 < δ) (hδ1 : δ < Real.pi / 2) :
    (ρ₁ ≤ ‖Ta • b + F‖ ∧ ‖Ta • b + F‖ ≤ ρ₂ ∧ ‖Ta • b + F‖ * Real.cos δ ≤ ⟪b, Ta • b + F⟫) ↔
    (‖F‖ * Real.cos δ ≤ Ta * Real.sin δ ∧ Real.sqrt (ρ₁ ^ 2 - ‖F‖ ^ 2) ≤ Ta ∧
      Ta ≤ Real.sqrt (ρ₂ ^ 2 - ‖F‖ ^ 2)) := by
  have hc : 0 < Real.cos δ := Real.cos_pos_of_mem_Ioo ⟨by linarith, hδ1⟩
  have hs : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ0 (by linarith [Real.pi_pos])
  have hcs := Real.sin_sq_add_cos_sq δ
  set c := Real.cos δ
  set s := Real.sin δ
  set κ := ‖F‖ with hκ
  have hκ0 : 0 ≤ κ := norm_nonneg F
  set N := ‖Ta • b + F‖ with hN
  have hN0 : 0 ≤ N := norm_nonneg _
  have hN2 : N ^ 2 = Ta ^ 2 + κ ^ 2 := norm_sq_axial_add_perp Ta hb hbF
  rw [inner_axial_add_perp Ta hb hbF]
  constructor
  · rintro ⟨h1, h2, h3⟩
    have hTa : 0 ≤ Ta := le_trans (mul_nonneg hN0 hc.le) h3
    have hsq : (N * c) ^ 2 ≤ Ta ^ 2 := pow_le_pow_left₀ (mul_nonneg hN0 hc.le) h3 2
    refine ⟨?_, ?_, ?_⟩
    · have : (κ * c) ^ 2 ≤ (Ta * s) ^ 2 := by nlinarith
      nlinarith [mul_nonneg hκ0 hc.le, mul_nonneg hTa hs.le]
    · rw [Real.sqrt_le_iff]
      exact ⟨hTa, by nlinarith⟩
    · rw [Real.le_sqrt hTa (by nlinarith)]
      nlinarith
  · rintro ⟨h1, h2, h3⟩
    have hTa : 0 ≤ Ta := by nlinarith [mul_nonneg hκ0 hc.le]
    have h2' : ρ₁ ^ 2 - κ ^ 2 ≤ Ta ^ 2 := (Real.sqrt_le_iff.mp h2).2
    have h3' : Ta ^ 2 ≤ ρ₂ ^ 2 - κ ^ 2 := by
      by_cases hpos : 0 ≤ ρ₂ ^ 2 - κ ^ 2
      · exact (Real.le_sqrt hTa hpos).mp h3
      · exfalso
        push Not at hpos
        rw [Real.sqrt_eq_zero'.mpr hpos.le] at h3
        have hTa0 : Ta = 0 := le_antisymm h3 hTa
        rw [hTa0, zero_mul] at h1
        have : κ = 0 := by nlinarith [mul_nonneg hκ0 hc.le]
        rw [this] at hpos
        nlinarith
    refine ⟨?_, ?_, ?_⟩
    · nlinarith
    · nlinarith
    · have hsq : (κ * c) ^ 2 ≤ (Ta * s) ^ 2 := pow_le_pow_left₀ (mul_nonneg hκ0 hc.le) h1 2
      have : (N * c) ^ 2 ≤ Ta ^ 2 := by nlinarith
      nlinarith [mul_nonneg hN0 hc.le]

/-- The blueprint form of the gimbal bound: `κ cos δ ≤ T_a sin δ ↔ κ cot δ ≤ T_a`. -/
theorem gimbal_bound_iff_cot {κ Ta δ : ℝ} (hδ0 : 0 < δ) (hδ1 : δ < Real.pi / 2) :
    κ * Real.cos δ ≤ Ta * Real.sin δ ↔ κ * Real.cot δ ≤ Ta := by
  have hs : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ0 (by linarith [Real.pi_pos])
  rw [Real.cot_eq_cos_div_sin, ← mul_div_assoc, div_le_iff₀ hs]

/-- The exact M3b thrust set at one instant, for a given attitude: throttle band, gimbal cone,
and torque balance `Π_b T = F` (with `F = -k Π_b b̈` from Lemma 8.1). -/
def tvcSet (b F : V) (ρ₁ ρ₂ δ : ℝ) : Set V :=
  {T | ρ₁ ≤ ‖T‖ ∧ ‖T‖ ≤ ρ₂ ∧ ‖T‖ * Real.cos δ ≤ ⟪b, T⟫ ∧ T - ⟪b, T⟫ • b = F}

theorem eq_axial_add_of_proj {b F T : V} (h : T - ⟪b, T⟫ • b = F) : T = ⟪b, T⟫ • b + F := by
  rw [← h]; abel

/-- **Theorem C-6 (pointwise).** For a fixed attitude `b` (unit) and the induced lateral thrust
`F ⊥ b`, the exact M3b thrust set is convex: it is a segment `{T_a b + F | T_a ∈ I}`. -/
theorem convex_tvcSet {b F : V} {ρ₁ ρ₂ δ : ℝ} (hb : ‖b‖ = 1) (hbF : ⟪b, F⟫ = 0)
    (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂) (hδ0 : 0 < δ) (hδ1 : δ < Real.pi / 2) :
    Convex ℝ (tvcSet b F ρ₁ ρ₂ δ) := by
  have key : ∀ T, T ∈ tvcSet b F ρ₁ ρ₂ δ ↔ T - ⟪b, T⟫ • b = F ∧
      (‖F‖ * Real.cos δ ≤ ⟪b, T⟫ * Real.sin δ ∧ Real.sqrt (ρ₁ ^ 2 - ‖F‖ ^ 2) ≤ ⟪b, T⟫ ∧
        ⟪b, T⟫ ≤ Real.sqrt (ρ₂ ^ 2 - ‖F‖ ^ 2)) := by
    intro T
    constructor
    · rintro ⟨h1, h2, h3, h4⟩
      refine ⟨h4, ?_⟩
      have hT := eq_axial_add_of_proj h4
      rw [hT] at h1 h2 h3
      have := (throttle_interval (Ta := ⟪b, T⟫) hb hbF hρ hρ12 hδ0 hδ1).mp ⟨h1, h2, h3⟩
      exact this
    · rintro ⟨h4, hI⟩
      have := (throttle_interval (Ta := ⟪b, T⟫) hb hbF hρ hρ12 hδ0 hδ1).mpr hI
      rw [← eq_axial_add_of_proj h4] at this
      exact ⟨this.1, this.2.1, this.2.2, h4⟩
  intro x hx y hy a a' ha ha' haa
  rw [key] at hx hy ⊢
  have hinner : ⟪b, a • x + a' • y⟫ = a * ⟪b, x⟫ + a' * ⟪b, y⟫ := by
    rw [inner_add_right, real_inner_smul_right, real_inner_smul_right]
  rw [hinner]
  refine ⟨?_, ?_, ?_, ?_⟩
  · have : a • x + a' • y - (a * ⟪b, x⟫ + a' * ⟪b, y⟫) • b =
        a • (x - ⟪b, x⟫ • b) + a' • (y - ⟪b, y⟫ • b) := by module
    rw [this, hx.1, hy.1, ← add_smul, haa, one_smul]
  · have e : ‖F‖ * Real.cos δ = a * (‖F‖ * Real.cos δ) + a' * (‖F‖ * Real.cos δ) := by
      rw [← add_mul, haa, one_mul]
    nlinarith [mul_le_mul_of_nonneg_left hx.2.1 ha, mul_le_mul_of_nonneg_left hy.2.1 ha']
  · have e : Real.sqrt (ρ₁ ^ 2 - ‖F‖ ^ 2) = a * Real.sqrt (ρ₁ ^ 2 - ‖F‖ ^ 2) +
        a' * Real.sqrt (ρ₁ ^ 2 - ‖F‖ ^ 2) := by rw [← add_mul, haa, one_mul]
    nlinarith [mul_le_mul_of_nonneg_left hx.2.2.1 ha, mul_le_mul_of_nonneg_left hy.2.2.1 ha']
  · have e : Real.sqrt (ρ₂ ^ 2 - ‖F‖ ^ 2) = a * Real.sqrt (ρ₂ ^ 2 - ‖F‖ ^ 2) +
        a' * Real.sqrt (ρ₂ ^ 2 - ‖F‖ ^ 2) := by rw [← add_mul, haa, one_mul]
    nlinarith [mul_le_mul_of_nonneg_left hx.2.2.2 ha, mul_le_mul_of_nonneg_left hy.2.2.2 ha']

/-- **Corollary 8.2.** With `F = 0` (attitude held constant, `b̈ = 0`) every admissible thrust is
parallel to `b`: the effective gimbal cone is `δ_eff = 0`. -/
theorem tvcSet_upright {b T : V} {ρ₁ ρ₂ δ : ℝ} (hT : T ∈ tvcSet b 0 ρ₁ ρ₂ δ) :
    T = ⟪b, T⟫ • b := by
  have := eq_axial_add_of_proj hT.2.2.2
  rwa [add_zero] at this

end LcvxPositive
