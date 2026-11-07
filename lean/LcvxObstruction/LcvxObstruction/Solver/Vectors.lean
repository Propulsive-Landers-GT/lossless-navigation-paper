import Mathlib

/-!
# Solver claims N3, N4, N5: throttle slew, chord bound, direction-acceleration bound

Source: `solver/CLAIMS.md` rows 7 (N3), 15 (N4), 16 (N5). General real inner-product space `E`
unless stated otherwise; `ℝ³` is `EuclideanSpace ℝ (Fin 3)`.

* `hasDerivAt_norm_of_ne`, `throttle_rate_le` (**N3**): for differentiable `T` with `T ≠ 0`,
  `d‖T‖/dt = ⟪T, Ṫ⟫/‖T‖` and `|d‖T‖/dt| ≤ ‖Ṫ‖`; `norm_le_sum_abs` : `‖v‖ ≤ |v₀|+|v₁|+|v₂|` in ℝ³;
  `throttle_slew_foh` : the first-order-hold form `|d‖T‖/dt| ≤ (|ΔT_x|+|ΔT_y|+|ΔT_z|)/h`;
  `throttle_slew_increment` : the difference form `|‖T₁‖ − ‖T₀‖| ≤ ‖ΔT‖ ≤ Σ|ΔT_i|`.
* `chord_bound` (**N4**): `‖a‖, ‖b‖ ≥ ρ ≥ 0` ⇒ `‖a − b‖ ≥ 2ρ sin(∠(a,b)/2)`.
* `dir_accel_bound` (**N5**, pointwise algebraic form) and `dir_accel_bound_calculus`
  (**N5**, derivative form): `T = Γ e`, `Γ ≥ ρ > 0`, `‖e‖ = 1`, `‖Ṫ‖ ≤ D₁`, `‖T̈‖ ≤ D₂`,
  `‖ė‖ ≤ ω` ⇒ `‖Π_e ë‖ ≤ (D₂ + 2 D₁ ω)/ρ`, `Π_e x = x − ⟪e,x⟫ e`.
-/

open Real InnerProductGeometry
open scoped RealInnerProductSpace

namespace LcvxSolver

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-! ## N3: throttle slew -/

/-- Derivative of the norm along a curve that avoids the origin. -/
theorem hasDerivAt_norm_of_ne {T : ℝ → E} {T' : E} {s : ℝ} (h : HasDerivAt T T' s)
    (h0 : T s ≠ 0) : HasDerivAt (fun u => ‖T u‖) (⟪T s, T'⟫ / ‖T s‖) s := by
  have hi := h.inner ℝ h
  have hpos : 0 < ⟪T s, T s⟫ := real_inner_self_pos.mpr h0
  have hs := hi.sqrt hpos.ne'
  have hfun : (fun u => ‖T u‖) = fun u => √⟪T u, T u⟫ := by
    funext u; rw [real_inner_self_eq_norm_sq, sqrt_sq (norm_nonneg _)]
  rw [hfun]
  refine hs.congr_deriv ?_
  rw [real_inner_comm T' (T s), real_inner_self_eq_norm_sq, sqrt_sq (norm_nonneg _)]
  have : 0 < ‖T s‖ := norm_pos_iff.mpr h0
  field_simp
  ring

/-- **N3 (continuous time).** For differentiable `T` with `T(s) ≠ 0`, `‖T‖` is differentiable at
`s` and `|d‖T‖/dt| ≤ ‖Ṫ‖`. -/
theorem throttle_rate_le {T : ℝ → E} {T' : E} {s : ℝ} (h : HasDerivAt T T' s) (h0 : T s ≠ 0) :
    ∃ r, HasDerivAt (fun u => ‖T u‖) r s ∧ |r| ≤ ‖T'‖ := by
  refine ⟨_, hasDerivAt_norm_of_ne h h0, ?_⟩
  have hn : 0 < ‖T s‖ := norm_pos_iff.mpr h0
  rw [abs_div, abs_of_pos hn, div_le_iff₀ hn, mul_comm]
  exact abs_real_inner_le_norm _ _

/-- `‖v‖ ≤ |v₀| + |v₁| + |v₂|` in `ℝ³`. -/
theorem norm_le_sum_abs (v : EuclideanSpace ℝ (Fin 3)) : ‖v‖ ≤ |v 0| + |v 1| + |v 2| := by
  have h2 : ‖v‖ ^ 2 = v 0 ^ 2 + v 1 ^ 2 + v 2 ^ 2 := by
    rw [EuclideanSpace.norm_sq_eq]; simp [Fin.sum_univ_three]
  have hs : 0 ≤ |v 0| + |v 1| + |v 2| := by positivity
  apply (pow_le_pow_iff_left₀ (norm_nonneg v) hs two_ne_zero).mp
  rw [h2]
  have := abs_nonneg (v 0); have := abs_nonneg (v 1); have := abs_nonneg (v 2)
  nlinarith [sq_abs (v 0), sq_abs (v 1), sq_abs (v 2), mul_nonneg (abs_nonneg (v 0)) (abs_nonneg (v 1)),
    mul_nonneg (abs_nonneg (v 0)) (abs_nonneg (v 2)), mul_nonneg (abs_nonneg (v 1)) (abs_nonneg (v 2))]

/-- **N3 (first-order hold).** On an interval of length `h > 0` with body thrust
`T(u) = T₀ + ((u − s₀)/h) ΔT`, at every `u` with `T(u) ≠ 0`:
`|d‖T‖/dt| ≤ ‖ΔT‖/h ≤ (|ΔT_x| + |ΔT_y| + |ΔT_z|)/h`. -/
theorem throttle_slew_foh (T₀ ΔT : EuclideanSpace ℝ (Fin 3)) {s₀ h u : ℝ} (hh : 0 < h)
    (h0 : T₀ + ((u - s₀) / h) • ΔT ≠ 0) :
    ∃ r, HasDerivAt (fun u => ‖T₀ + ((u - s₀) / h) • ΔT‖) r u ∧
      |r| ≤ ‖ΔT‖ / h ∧ ‖ΔT‖ / h ≤ (|ΔT 0| + |ΔT 1| + |ΔT 2|) / h := by
  have hd : HasDerivAt (fun u => T₀ + ((u - s₀) / h) • ΔT) ((1 / h) • ΔT) u := by
    have := (((hasDerivAt_id u).sub_const s₀).div_const h).smul_const ΔT
    exact (this.const_add T₀).congr_deriv (by simp)
  obtain ⟨r, hr, hb⟩ := throttle_rate_le hd h0
  refine ⟨r, hr, ?_, ?_⟩
  · rw [norm_smul, Real.norm_eq_abs, abs_of_pos (by positivity : (0:ℝ) < 1 / h)] at hb
    rwa [one_div_mul_eq_div] at hb
  · exact div_le_div_of_nonneg_right (norm_le_sum_abs ΔT) hh.le

/-- **N3 (difference form).** `|‖T₁‖ − ‖T₀‖| ≤ ‖T₁ − T₀‖ ≤ Σ |ΔT_i|`. -/
theorem throttle_slew_increment (T₀ T₁ : EuclideanSpace ℝ (Fin 3)) :
    |‖T₁‖ - ‖T₀‖| ≤ ‖T₁ - T₀‖ ∧
      ‖T₁ - T₀‖ ≤ |T₁ 0 - T₀ 0| + |T₁ 1 - T₀ 1| + |T₁ 2 - T₀ 2| := by
  refine ⟨abs_norm_sub_norm_le _ _, ?_⟩
  simpa using norm_le_sum_abs (T₁ - T₀)

/-! ## N4: chord bound -/

/-- **N4 (chord bound).** If `‖a‖ ≥ ρ`, `‖b‖ ≥ ρ`, `ρ ≥ 0`, then
`‖a − b‖ ≥ 2 ρ sin (∠(a,b)/2)`. -/
theorem chord_bound {a b : E} {ρ : ℝ} (hρ : 0 ≤ ρ) (ha : ρ ≤ ‖a‖) (hb : ρ ≤ ‖b‖) :
    2 * ρ * sin (angle a b / 2) ≤ ‖a - b‖ := by
  set θ := angle a b
  have hc : ⟪a, b⟫ = ‖a‖ * ‖b‖ * cos θ := by rw [← cos_angle_mul_norm_mul_norm]; ring
  have hsq : ‖a - b‖ ^ 2 = ‖a‖ ^ 2 + ‖b‖ ^ 2 - 2 * (‖a‖ * ‖b‖ * cos θ) := by
    rw [norm_sub_sq_real, hc]; ring
  have hcos : cos θ = 1 - 2 * sin (θ / 2) ^ 2 := by
    have h1 := cos_two_mul (θ / 2)
    rw [show 2 * (θ / 2) = θ by ring] at h1
    have h2 := sin_sq_add_cos_sq (θ / 2)
    linarith
  have hs0 : 0 ≤ sin (θ / 2) :=
    sin_nonneg_of_nonneg_of_le_pi (by linarith [angle_nonneg a b])
      (by linarith [angle_le_pi a b, pi_pos])
  have hAB : ρ * ρ ≤ ‖a‖ * ‖b‖ := mul_le_mul ha hb hρ (norm_nonneg a)
  have key : (2 * ρ * sin (θ / 2)) ^ 2 ≤ ‖a - b‖ ^ 2 := by
    rw [hsq, hcos]
    have : ‖a‖ ^ 2 + ‖b‖ ^ 2 - 2 * (‖a‖ * ‖b‖ * (1 - 2 * sin (θ / 2) ^ 2)) =
        (‖a‖ - ‖b‖) ^ 2 + 4 * (‖a‖ * ‖b‖) * sin (θ / 2) ^ 2 := by ring
    rw [this]
    nlinarith [sq_nonneg (‖a‖ - ‖b‖), sq_nonneg (sin (θ / 2))]
  exact (pow_le_pow_iff_left₀ (by positivity) (norm_nonneg _) two_ne_zero).mp key

/-! ## N5: direction-acceleration bound -/

/-- The projection `Π_e x = x − ⟪e,x⟫ e` onto `e^⊥` does not increase the norm (`‖e‖ = 1`). -/
theorem norm_proj_le {e : E} (he : ‖e‖ = 1) (x : E) : ‖x - ⟪e, x⟫ • e‖ ≤ ‖x‖ := by
  have h : ‖x - ⟪e, x⟫ • e‖ ^ 2 = ‖x‖ ^ 2 - ⟪e, x⟫ ^ 2 := by
    rw [norm_sub_sq_real, inner_smul_right, norm_smul, he, Real.norm_eq_abs, real_inner_comm]
    rw [mul_one, sq_abs]; ring
  have : ‖x - ⟪e, x⟫ • e‖ ^ 2 ≤ ‖x‖ ^ 2 := by rw [h]; nlinarith [sq_nonneg ⟪e, x⟫]
  exact (pow_le_pow_iff_left₀ (norm_nonneg _) (norm_nonneg _) two_ne_zero).mp this

/-- **N5 (pointwise algebraic form).** Let `‖e‖ = 1`, `⟪e, ė⟫ = 0`, and let
`T₁ = Γ̇ e + Γ ė`, `T₂ = Γ̈ e + 2Γ̇ ė + Γ ë` (the first two derivatives of `T = Γ e`).
If `Γ ≥ ρ > 0`, `‖T₁‖ ≤ D₁`, `‖T₂‖ ≤ D₂`, `‖ė‖ ≤ ω`, then
`‖Π_e ë‖ ≤ (D₂ + 2 D₁ ω)/ρ`. -/
theorem dir_accel_bound {e de dde T₁ T₂ : E} {Γ dΓ ddΓ ρ D₁ D₂ ω : ℝ} (hρ : 0 < ρ)
    (hΓ : ρ ≤ Γ) (he : ‖e‖ = 1) (hede : ⟪e, de⟫ = 0)
    (hT₁ : T₁ = dΓ • e + Γ • de) (hT₂ : T₂ = ddΓ • e + (2 * dΓ) • de + Γ • dde)
    (hD₁ : ‖T₁‖ ≤ D₁) (hD₂ : ‖T₂‖ ≤ D₂) (hω : ‖de‖ ≤ ω) :
    ‖dde - ⟪e, dde⟫ • e‖ ≤ (D₂ + 2 * D₁ * ω) / ρ := by
  have hee : ⟪e, e⟫ = 1 := by rw [real_inner_self_eq_norm_sq, he]; norm_num
  have hΓpos : 0 < Γ := lt_of_lt_of_le hρ hΓ
  -- Γ̇ = ⟪e, T₁⟫, so |Γ̇| ≤ D₁
  have hdΓ : dΓ = ⟪e, T₁⟫ := by
    rw [hT₁, inner_add_right, inner_smul_right, inner_smul_right, hee, hede]; ring
  have hdΓb : |dΓ| ≤ D₁ := by
    rw [hdΓ]
    calc |⟪e, T₁⟫| ≤ ‖e‖ * ‖T₁‖ := abs_real_inner_le_norm _ _
      _ = ‖T₁‖ := by rw [he, one_mul]
      _ ≤ D₁ := hD₁
  -- Π_e T₂ = 2Γ̇ ė + Γ Π_e ë
  have hproj : T₂ - ⟪e, T₂⟫ • e = (2 * dΓ) • de + Γ • (dde - ⟪e, dde⟫ • e) := by
    have hi : ⟪e, T₂⟫ = ddΓ + Γ * ⟪e, dde⟫ := by
      rw [hT₂, inner_add_right, inner_add_right, inner_smul_right, inner_smul_right,
        inner_smul_right, hee, hede]; ring
    rw [hi, hT₂, smul_sub, add_smul, smul_smul]
    module
  have hmain : Γ * ‖dde - ⟪e, dde⟫ • e‖ ≤ D₂ + 2 * D₁ * ω := by
    have h1 : Γ • (dde - ⟪e, dde⟫ • e) = (T₂ - ⟪e, T₂⟫ • e) - (2 * dΓ) • de := by
      rw [hproj]; abel
    have h2 := congrArg norm h1
    rw [norm_smul, Real.norm_eq_abs, abs_of_pos hΓpos] at h2
    rw [h2]
    calc ‖(T₂ - ⟪e, T₂⟫ • e) - (2 * dΓ) • de‖ ≤ ‖T₂ - ⟪e, T₂⟫ • e‖ + ‖(2 * dΓ) • de‖ :=
          norm_sub_le _ _
      _ ≤ ‖T₂‖ + 2 * |dΓ| * ‖de‖ := by
          gcongr
          · exact norm_proj_le he T₂
          · rw [norm_smul, Real.norm_eq_abs, abs_mul, abs_two]
      _ ≤ D₂ + 2 * D₁ * ω := by
          have := norm_nonneg de
          have : |dΓ| * ‖de‖ ≤ D₁ * ω :=
            mul_le_mul hdΓb hω this (le_trans (abs_nonneg _) hdΓb)
          linarith
  have hnum : 0 ≤ D₂ + 2 * D₁ * ω := le_trans (by positivity) hmain
  rw [le_div_iff₀ hρ]
  calc ‖dde - ⟪e, dde⟫ • e‖ * ρ ≤ ‖dde - ⟪e, dde⟫ • e‖ * Γ := by gcongr
    _ = Γ * ‖dde - ⟪e, dde⟫ • e‖ := by ring
    _ ≤ D₂ + 2 * D₁ * ω := hmain

/-- A unit-norm curve is orthogonal to its velocity. -/
theorem inner_deriv_eq_zero_of_unit {e : ℝ → E} {de : E} {s : ℝ} (hunit : ∀ u, ‖e u‖ = 1)
    (he : HasDerivAt e de s) : ⟪e s, de⟫ = 0 := by
  have h1 := he.inner ℝ he
  have hconst : (fun u => ⟪e u, e u⟫) = fun _ => (1 : ℝ) := by
    funext u; rw [real_inner_self_eq_norm_sq, hunit u]; norm_num
  rw [hconst] at h1
  have h2 := h1.unique (hasDerivAt_const s (1 : ℝ))
  have h3 : ⟪de, e s⟫ = ⟪e s, de⟫ := real_inner_comm _ _
  linarith

/-- **N5 (derivative form).** `T = Γ e` with `Γ, e` twice differentiable, `‖e(u)‖ = 1` for all
`u`, `T₁` the derivative of `T` everywhere and `T₂` the derivative of `T₁` at `s`. If
`Γ(s) ≥ ρ > 0`, `‖T₁(s)‖ ≤ D₁`, `‖T₂‖ ≤ D₂`, `‖ė(s)‖ ≤ ω`, then
`‖Π_{e(s)} ë(s)‖ ≤ (D₂ + 2 D₁ ω)/ρ`. -/
theorem dir_accel_bound_calculus {Γ dΓ : ℝ → ℝ} {e de T₁ : ℝ → E} {ddΓ : ℝ} {dde T₂ : E}
    {s ρ D₁ D₂ ω : ℝ} (hunit : ∀ u, ‖e u‖ = 1)
    (hΓ₁ : ∀ u, HasDerivAt Γ (dΓ u) u) (he₁ : ∀ u, HasDerivAt e (de u) u)
    (hΓ₂ : HasDerivAt dΓ ddΓ s) (he₂ : HasDerivAt de dde s)
    (hT₁ : ∀ u, HasDerivAt (fun v => Γ v • e v) (T₁ u) u) (hT₂ : HasDerivAt T₁ T₂ s)
    (hρ : 0 < ρ) (hΓρ : ρ ≤ Γ s) (hD₁ : ‖T₁ s‖ ≤ D₁) (hD₂ : ‖T₂‖ ≤ D₂) (hω : ‖de s‖ ≤ ω) :
    ‖dde - ⟪e s, dde⟫ • e s‖ ≤ (D₂ + 2 * D₁ * ω) / ρ := by
  have hT₁eq : ∀ u, T₁ u = dΓ u • e u + Γ u • de u := by
    intro u
    have := (hΓ₁ u).smul (he₁ u)
    exact (hT₁ u).unique (this.congr_deriv (by abel))
  have hT₁fun : T₁ = fun u => dΓ u • e u + Γ u • de u := funext hT₁eq
  have hT₂eq : T₂ = ddΓ • e s + (2 * dΓ s) • de s + Γ s • dde := by
    have h := (hΓ₂.smul (he₁ s)).add ((hΓ₁ s).smul he₂)
    rw [hT₁fun] at hT₂
    rw [hT₂.unique h, two_mul, add_smul]
    abel
  exact dir_accel_bound hρ hΓρ (hunit s) (inner_deriv_eq_zero_of_unit hunit (he₁ s))
    (hT₁eq s) hT₂eq hD₁ hD₂ hω

end LcvxSolver
