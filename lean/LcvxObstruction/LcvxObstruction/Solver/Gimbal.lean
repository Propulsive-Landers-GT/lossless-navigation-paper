import Mathlib

/-!
# Solver claims N1 and N2: gimbal box and gimbal-rate sufficient conditions

Source: `solver/CLAIMS.md` rows 6 (N1) and 8 (N2). Body-frame thrust `T = (T_x, T_y, T_z)`,
flight-code gimbal convention

  `d = (sin θ cos φ, sin φ, cos θ cos φ)`,  `T = ‖T‖ d`,

so `θ = atan2(T_x, T_z) = arctan(T_x/T_z)` (for `T_z > 0`) and `φ = arcsin(T_y/‖T‖)`.
The planner imposes the conservative linear box `|T_x| ≤ tan δ T_z`, `|T_y| ≤ tan δ T_z` and the
linear rate conditions `|ΔT_x| + tan δ |ΔT_z| ≤ ω T_floor h`, `|ΔT_y| + tan δ |ΔT_z| ≤ ω T_floor h`.

* `gimbal_box_angles` (**N1**): the box implies `|θ| ≤ δ` and `|φ| ≤ δ` (sharper than the claimed
  `|φ| ≤ arcsin(tan δ)`, which is also proved).
* `axial_floor` : `‖T‖ ≥ T_min` and the box imply `T_z ≥ T_min cos(arctan(√2 tan δ))`; this is
  the planner's `T_floor` (`aacg._ta_floor`).
* `hasDerivAt_theta`, `theta_rate_bound` (**N2, θ axis**): the exact rate formula and
  `|θ̇| ≤ (|Ṫ_x| + tan δ |Ṫ_z|)/T_floor`.
* `hasDerivAt_phi` : the exact `φ` rate
  `φ̇ = (Ṫ_y (T_x²+T_z²) − T_y (T_x Ṫ_x + T_z Ṫ_z)) / (‖T‖² √(T_x²+T_z²))`.
* `phi_rate_heuristic_false` : the solver's **heuristic** φ-axis condition
  `|φ̇| ≤ (|Ṫ_y| + tan δ |Ṫ_z|)/T_floor` is **false** (explicit counterexample).
* `phi_rate_bound_standalone` (corrected φ condition):
  `|φ̇| ≤ (|Ṫ_y| + tan δ |Ṫ_z| + tan² δ |Ṫ_x|)/T_z`.
* `phi_rate_bound_pair`, `gimbal_rate_pair` : the planner's **pair** of linear conditions (θ row
  and φ row together) does imply `|θ̇| ≤ ω` and `|φ̇| ≤ ω`. So the solver's constraint set is a
  valid sufficient condition for both axes, although the φ row alone is not.
* `foh_gimbal_rate` : the same for first-order-hold thrust on one interval, as increments
  `|θ(s₁) − θ(s₀)| ≤ ω (s₁ − s₀)`, `|φ(s₁) − φ(s₀)| ≤ ω (s₁ − s₀)` (the box and floor are imposed
  at the two nodes only).
-/

open Real

namespace LcvxSolver

/-! ## Elementary trigonometric helpers -/

theorem abs_tan_le_of_abs_sin_le {x t : ℝ} (hc : 0 < cos x) (h : |sin x| ≤ t * cos x) :
    |tan x| ≤ t := by
  rw [tan_eq_sin_div_cos, abs_div, abs_of_pos hc, div_le_iff₀ hc]
  exact h

theorem abs_le_of_abs_tan_le {x δ : ℝ} (hx : |x| < π / 2) (hδ0 : 0 ≤ δ) (hδ : δ < π / 2)
    (h : |tan x| ≤ tan δ) : |x| ≤ δ := by
  have hx' := abs_lt.mp hx
  rw [abs_le]
  constructor
  · by_contra hc
    push Not at hc
    have h1 : tan (-x) > tan δ :=
      tan_lt_tan_of_lt_of_lt_pi_div_two (by linarith) (by linarith) (by linarith)
    rw [tan_neg] at h1
    have := neg_abs_le (tan x)
    linarith
  · by_contra hc
    push Not at hc
    have h1 : tan x > tan δ :=
      tan_lt_tan_of_lt_of_lt_pi_div_two (by linarith) (by linarith) hc
    have := le_abs_self (tan x)
    linarith

theorem abs_lt_pi_div_two_of_cos_pos {x : ℝ} (hx : |x| ≤ π) (hc : 0 < cos x) : |x| < π / 2 := by
  by_contra h
  push Not at h
  have : cos |x| ≤ 0 := cos_nonpos_of_pi_div_two_le_of_le h (by linarith [pi_pos])
  rw [cos_abs] at this
  linarith

theorem sin_le_tan_of_nonneg {δ : ℝ} (hδ0 : 0 ≤ δ) (hδ : δ < π / 2) : sin δ ≤ tan δ := by
  have hc : 0 < cos δ := cos_pos_of_mem_Ioo ⟨by linarith [pi_pos], hδ⟩
  have hs : 0 ≤ sin δ := sin_nonneg_of_nonneg_of_le_pi hδ0 (by linarith [pi_pos])
  rw [tan_eq_sin_div_cos, le_div_iff₀ hc]
  nlinarith [cos_le_one δ]

/-! ## N1: the conservative gimbal box -/

/-- **N1 (conservative gimbal box).** Flight convention `T = s (sin θ cos φ, sin φ, cos θ cos φ)`
with `s = ‖T‖ ≥ 0`, `θ ∈ [-π, π]` (atan2 range), `φ ∈ [-π/2, π/2]` (arcsin range). If `T_z > 0`
and `|T_x|, |T_y| ≤ tan δ · T_z` with `0 ≤ δ < π/2`, then `|θ| ≤ δ`, `|φ| ≤ δ`, and in particular
`|φ| ≤ arcsin (tan δ)` (the form stated in `solver/CLAIMS.md`). -/
theorem gimbal_box_angles {δ θ φ s Tx Ty Tz : ℝ} (hδ0 : 0 ≤ δ) (hδ : δ < π / 2)
    (hθ : |θ| ≤ π) (hφ : |φ| ≤ π / 2) (hs : 0 ≤ s)
    (hx : Tx = s * (sin θ * cos φ)) (hy : Ty = s * sin φ) (hz : Tz = s * (cos θ * cos φ))
    (hTz : 0 < Tz) (hbx : |Tx| ≤ tan δ * Tz) (hby : |Ty| ≤ tan δ * Tz) :
    |θ| ≤ δ ∧ |φ| ≤ δ ∧ |φ| ≤ arcsin (tan δ) := by
  have hφ' := abs_le.mp hφ
  have hcφ0 : 0 ≤ cos φ := cos_nonneg_of_neg_pi_div_two_le_of_le hφ'.1 hφ'.2
  have hspos : 0 < s := by
    rcases hs.lt_or_eq with h | h
    · exact h
    · rw [← h] at hz; simp at hz; linarith
  have hprod : 0 < cos θ * cos φ := by
    rw [hz] at hTz; exact pos_of_mul_pos_right hTz hs
  have hcφ : 0 < cos φ := lt_of_le_of_ne hcφ0 (by intro h; rw [← h] at hprod; simp at hprod)
  have hcθ : 0 < cos θ := pos_of_mul_pos_left hprod hcφ0
  have hθ2 := abs_lt_pi_div_two_of_cos_pos hθ hcθ
  have hφ2 := abs_lt_pi_div_two_of_cos_pos (by linarith [pi_pos]) hcφ
  have ht0 : 0 ≤ tan δ := by
    have : sin δ ≤ tan δ := sin_le_tan_of_nonneg hδ0 hδ
    linarith [sin_nonneg_of_nonneg_of_le_pi hδ0 (by linarith [pi_pos] : δ ≤ π)]
  -- θ axis
  have hsθ : |sin θ| ≤ tan δ * cos θ := by
    rw [hx, hz, abs_mul, abs_mul, abs_of_pos hspos, abs_of_pos hcφ] at hbx
    have : s * cos φ * |sin θ| ≤ s * cos φ * (tan δ * cos θ) := by nlinarith
    exact le_of_mul_le_mul_left this (mul_pos hspos hcφ)
  have hθδ : |θ| ≤ δ := abs_le_of_abs_tan_le hθ2 hδ0 hδ (abs_tan_le_of_abs_sin_le hcθ hsθ)
  -- φ axis: |sin φ| ≤ tan δ cos θ cos φ ≤ tan δ cos φ
  have hsφ : |sin φ| ≤ tan δ * cos φ := by
    rw [hy, hz, abs_mul, abs_of_pos hspos] at hby
    have h1 : |sin φ| ≤ tan δ * (cos θ * cos φ) := le_of_mul_le_mul_left (by nlinarith) hspos
    have h2 : tan δ * (cos θ * cos φ) ≤ tan δ * cos φ := by
      have := cos_le_one θ
      have : cos θ * cos φ ≤ cos φ := by nlinarith
      exact mul_le_mul_of_nonneg_left this ht0
    linarith
  have hφδ : |φ| ≤ δ := abs_le_of_abs_tan_le hφ2 hδ0 hδ (abs_tan_le_of_abs_sin_le hcφ hsφ)
  refine ⟨hθδ, hφδ, ?_⟩
  -- |φ| ≤ δ ≤ arcsin (sin δ) ≤ arcsin (tan δ)
  have h1 : δ = arcsin (sin δ) := (arcsin_sin (by linarith [pi_pos]) hδ.le).symm
  calc |φ| ≤ δ := hφδ
    _ = arcsin (sin δ) := h1
    _ ≤ arcsin (tan δ) := arcsin_le_arcsin (sin_le_tan_of_nonneg hδ0 hδ)

/-- The planner's axial floor: `‖T‖ ≥ T_min` and the box give
`T_z ≥ T_min · cos (arctan (√2 tan δ))` (`aacg._ta_floor`). Stated for `t = tan δ ≥ 0`. -/
theorem axial_floor {Tx Ty Tz t Tmin : ℝ} (ht : 0 ≤ t) (hz : 0 < Tz) (hx : |Tx| ≤ t * Tz)
    (hy : |Ty| ≤ t * Tz) (hmin : Tmin ≤ √(Tx ^ 2 + Ty ^ 2 + Tz ^ 2)) :
    Tmin * cos (arctan (√2 * t)) ≤ Tz := by
  have h2 : (√2 * t) ^ 2 = 2 * t ^ 2 := by rw [mul_pow, sq_sqrt (by norm_num)]
  rw [cos_arctan, h2]
  have hq : 0 < √(1 + 2 * t ^ 2) := sqrt_pos.mpr (by positivity)
  have hb : √(Tx ^ 2 + Ty ^ 2 + Tz ^ 2) ≤ Tz * √(1 + 2 * t ^ 2) := by
    rw [show Tz * √(1 + 2 * t ^ 2) = √(Tz ^ 2 * (1 + 2 * t ^ 2)) by
      rw [sqrt_mul (sq_nonneg _), sqrt_sq hz.le]]
    apply sqrt_le_sqrt
    have hx2 : Tx ^ 2 ≤ (t * Tz) ^ 2 := by
      rw [← sq_abs Tx]; exact pow_le_pow_left₀ (abs_nonneg _) hx 2
    have hy2 : Ty ^ 2 ≤ (t * Tz) ^ 2 := by
      rw [← sq_abs Ty]; exact pow_le_pow_left₀ (abs_nonneg _) hy 2
    nlinarith
  rw [mul_one_div, div_le_iff₀ hq]
  linarith

/-! ## N2, θ axis -/

/-- Exact θ rate: for `T_z > 0`, `θ = arctan (T_x/T_z)` has derivative
`(Ṫ_x T_z − T_x Ṫ_z)/(T_x² + T_z²)`. -/
theorem hasDerivAt_theta {Tx Tz : ℝ → ℝ} {dTx dTz s : ℝ} (hx : HasDerivAt Tx dTx s)
    (hz : HasDerivAt Tz dTz s) (hpos : 0 < Tz s) :
    HasDerivAt (fun u => arctan (Tx u / Tz u))
      ((dTx * Tz s - Tx s * dTz) / (Tx s ^ 2 + Tz s ^ 2)) s := by
  have h := (hx.div hz hpos.ne').arctan
  refine h.congr_deriv ?_
  have hz2 : 0 < Tz s ^ 2 := by positivity
  have hd : 0 < Tx s ^ 2 + Tz s ^ 2 := by positivity
  simp only [Pi.div_apply]
  field_simp
  ring

/-- **N2, θ axis (pointwise).** With `T_z ≥ T_floor > 0` and `|T_x| ≤ t T_z` (`t = tan δ ≥ 0`):
`|θ̇| ≤ (|Ṫ_x| + t |Ṫ_z|)/T_floor`. -/
theorem theta_rate_bound {Tx Tz dTx dTz t F : ℝ} (hF : 0 < F) (hz : F ≤ Tz) (ht : 0 ≤ t)
    (hx : |Tx| ≤ t * Tz) :
    |(dTx * Tz - Tx * dTz) / (Tx ^ 2 + Tz ^ 2)| ≤ (|dTx| + t * |dTz|) / F := by
  have hTz : 0 < Tz := lt_of_lt_of_le hF hz
  have hD : 0 < Tx ^ 2 + Tz ^ 2 := by positivity
  rw [abs_div, abs_of_pos hD, div_le_div_iff₀ hD hF]
  have hnum : |dTx * Tz - Tx * dTz| ≤ (|dTx| + t * |dTz|) * Tz := by
    calc |dTx * Tz - Tx * dTz| ≤ |dTx * Tz| + |Tx * dTz| := abs_sub _ _
      _ = |dTx| * Tz + |Tx| * |dTz| := by rw [abs_mul, abs_mul, abs_of_pos hTz]
      _ ≤ |dTx| * Tz + (t * Tz) * |dTz| := by
          gcongr
      _ = (|dTx| + t * |dTz|) * Tz := by ring
  have hK : 0 ≤ |dTx| + t * |dTz| := by positivity
  calc |dTx * Tz - Tx * dTz| * F ≤ (|dTx| + t * |dTz|) * Tz * F := by gcongr
    _ ≤ (|dTx| + t * |dTz|) * Tz * Tz := by gcongr
    _ ≤ (|dTx| + t * |dTz|) * (Tx ^ 2 + Tz ^ 2) := by
        rw [mul_assoc]; gcongr; nlinarith [sq_nonneg Tx]

/-! ## N2, φ axis -/

/-- The exact φ rate `φ̇` for `φ = arcsin (T_y/‖T‖)`, as a function of `T` and `Ṫ`. -/
noncomputable def phiRate (x y z dx dy dz : ℝ) : ℝ :=
  (dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)) / ((x ^ 2 + y ^ 2 + z ^ 2) * √(x ^ 2 + z ^ 2))

/-- Exact φ rate: if `T_x² + T_z² > 0`, `φ = arcsin (T_y/‖T‖)` has derivative `phiRate`. -/
theorem hasDerivAt_phi {Tx Ty Tz : ℝ → ℝ} {dTx dTy dTz s : ℝ} (hx : HasDerivAt Tx dTx s)
    (hy : HasDerivAt Ty dTy s) (hz : HasDerivAt Tz dTz s) (hpos : 0 < Tx s ^ 2 + Tz s ^ 2) :
    HasDerivAt (fun u => arcsin (Ty u / √(Tx u ^ 2 + Ty u ^ 2 + Tz u ^ 2)))
      (phiRate (Tx s) (Ty s) (Tz s) dTx dTy dTz) s := by
  set x := Tx s
  set y := Ty s
  set z := Tz s
  set Q := x ^ 2 + y ^ 2 + z ^ 2 with hQdef
  have hQ : 0 < Q := by rw [hQdef]; nlinarith [sq_nonneg y]
  have hQd : HasDerivAt (fun u => Tx u ^ 2 + Ty u ^ 2 + Tz u ^ 2)
      (2 * x * dTx + 2 * y * dTy + 2 * z * dTz) s := by
    have := ((hx.pow 2).add (hy.pow 2)).add (hz.pow 2)
    refine this.congr_deriv ?_
    simp only [Nat.cast_ofNat]; ring
  have hn := hQd.sqrt hQ.ne'
  have hu := hy.div hn (sqrt_pos.mpr hQ).ne'
  set n := √Q with hndef
  have hnpos : 0 < n := sqrt_pos.mpr hQ
  have hn2 : n ^ 2 = Q := sq_sqrt hQ.le
  set ρ := √(x ^ 2 + z ^ 2) with hρdef
  have hρpos : 0 < ρ := sqrt_pos.mpr hpos
  have hρ2 : ρ ^ 2 = x ^ 2 + z ^ 2 := sq_sqrt hpos.le
  have hy2 : y ^ 2 < n ^ 2 := by rw [hn2]; linarith
  have hu1 : y / n ≠ 1 := by
    intro h; rw [div_eq_one_iff_eq hnpos.ne'] at h; rw [h] at hy2; linarith
  have hum1 : y / n ≠ -1 := by
    intro h; rw [div_eq_iff hnpos.ne'] at h; rw [h] at hy2; nlinarith
  have harc := (hasDerivAt_arcsin hum1 hu1).comp s hu
  refine harc.congr_deriv ?_
  have hsq : √(1 - (y / n) ^ 2) = ρ / n := by
    rw [show 1 - (y / n) ^ 2 = (ρ / n) ^ 2 by
      field_simp; rw [hn2, hρ2]; ring]
    exact sqrt_sq (div_nonneg hρpos.le hnpos.le)
  rw [hsq]
  unfold phiRate
  rw [← hQdef, ← hρdef]
  field_simp
  rw [show Ty s = y from rfl]
  linear_combination (dTy * y ^ 2 + y * x * dTx + y * z * dTz) * (hn2 + hQdef)

/-- The solver's heuristic φ-axis condition is **false**: there are `T`, `Ṫ` satisfying the box
`|T_x|, |T_y| ≤ t T_z`, `T_z ≥ F`, and `|Ṫ_y| + t|Ṫ_z| = 0` (so the heuristic bound is `0`), while
`φ̇ ≠ 0`. Witness: `t = F = 1`, `T = (1, 1, 1)`, `Ṫ = (1, 0, 0)`, `φ̇ = −1/(3√2)`. (Any `t > 0`
works; for GTPL, `δ = 10°`, `T = (tF, tF, F)`, `Ṫ = (ωF, 0, 0)` gives `φ̇ ≈ −1.73°/s` at
`ω = 60°/s`.) -/
theorem phi_rate_heuristic_false :
    ∃ x y z dx dy dz t F : ℝ, 0 < F ∧ F ≤ z ∧ 0 ≤ t ∧ |x| ≤ t * z ∧ |y| ≤ t * z ∧
      ¬ (|phiRate x y z dx dy dz| ≤ (|dy| + t * |dz|) / F) := by
  refine ⟨1, 1, 1, 1, 0, 0, 1, 1, by norm_num, le_rfl, by norm_num, by norm_num, by norm_num, ?_⟩
  unfold phiRate
  have h2 : (0 : ℝ) < √2 := by positivity
  norm_num

/-- **Corrected φ condition (standalone).** With `T_z > 0`, `|T_x|, |T_y| ≤ t T_z`:
`|φ̇| ≤ (|Ṫ_y| + t |Ṫ_z| + t² |Ṫ_x|)/T_z`. The `t² |Ṫ_x|` cross term is what the heuristic
omits. -/
theorem phi_rate_bound_standalone {x y z dx dy dz t : ℝ} (hz : 0 < z) (ht : 0 ≤ t)
    (hx : |x| ≤ t * z) (hy : |y| ≤ t * z) :
    |phiRate x y z dx dy dz| ≤ (|dy| + t * |dz| + t ^ 2 * |dx|) / z := by
  have hp : 0 < x ^ 2 + z ^ 2 := by positivity
  set ρ := √(x ^ 2 + z ^ 2) with hρdef
  have hρpos : 0 < ρ := sqrt_pos.mpr hp
  have hρ2 : ρ ^ 2 = x ^ 2 + z ^ 2 := sq_sqrt hp.le
  have hρz : z ≤ ρ := by nlinarith [sq_nonneg x]
  set Q := x ^ 2 + y ^ 2 + z ^ 2 with hQdef
  have hQ : 0 < Q := by rw [hQdef]; positivity
  have hQρ : ρ ^ 2 ≤ Q := by rw [hρ2]; nlinarith [sq_nonneg y]
  unfold phiRate
  rw [← hQdef, ← hρdef, abs_div, abs_of_pos (mul_pos hQ hρpos),
    div_le_div_iff₀ (mul_pos hQ hρpos) hz]
  set X := |x|
  set Y := |y|
  have hX : 0 ≤ X := abs_nonneg x
  have hY : 0 ≤ Y := abs_nonneg y
  have hnum : |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)| ≤
      |dy| * ρ ^ 2 + Y * X * |dx| + Y * z * |dz| := by
    calc |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)|
        ≤ |dy * (x ^ 2 + z ^ 2)| + |y * (x * dx + z * dz)| := abs_sub _ _
      _ ≤ |dy| * ρ ^ 2 + Y * (X * |dx| + z * |dz|) := by
          rw [abs_mul, abs_mul, abs_of_pos hp, ← hρ2]
          gcongr
          calc |x * dx + z * dz| ≤ |x * dx| + |z * dz| := abs_add_le _ _
            _ = X * |dx| + z * |dz| := by rw [abs_mul, abs_mul, abs_of_pos hz]
      _ = _ := by ring
  have ha := abs_nonneg dx
  have hb := abs_nonneg dy
  have hc := abs_nonneg dz
  -- each term separately
  have h1 : |dy| * ρ ^ 2 * z ≤ |dy| * (Q * ρ) := by
    have : ρ ^ 2 * z ≤ Q * ρ := by nlinarith
    nlinarith
  have hYX : Y * X * z ≤ t ^ 2 * (Q * ρ) := by
    have : Y * X ≤ (t * z) * (t * z) := mul_le_mul hy hx hX (by positivity)
    have hz3 : z ^ 3 ≤ Q * ρ := by
      have : z ^ 2 ≤ Q := by nlinarith [sq_nonneg x, sq_nonneg y]
      nlinarith
    nlinarith
  have hYz : Y * z * z ≤ t * (Q * ρ) := by
    have hz3 : z ^ 3 ≤ Q * ρ := by
      have : z ^ 2 ≤ Q := by nlinarith [sq_nonneg x, sq_nonneg y]
      nlinarith
    nlinarith
  calc |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)| * z
      ≤ (|dy| * ρ ^ 2 + Y * X * |dx| + Y * z * |dz|) * z := by gcongr
    _ = |dy| * ρ ^ 2 * z + (Y * X * z) * |dx| + (Y * z * z) * |dz| := by ring
    _ ≤ |dy| * (Q * ρ) + (t ^ 2 * (Q * ρ)) * |dx| + (t * (Q * ρ)) * |dz| := by gcongr
    _ = (|dy| + t * |dz| + t ^ 2 * |dx|) * (Q * ρ) := by ring

/-- Key inequality for the pair condition: `z (ρ² + X Y) ≤ ρ (ρ² + Y²)` when `ρ² = X² + z²`,
`X, Y ≥ 0`, `0 < z`, `ρ ≥ 0`. -/
theorem pair_key {X Y z ρ : ℝ} (hX : 0 ≤ X) (hY : 0 ≤ Y) (hz : 0 < z) (hρ : 0 ≤ ρ)
    (hρ2 : ρ ^ 2 = X ^ 2 + z ^ 2) : z * (ρ ^ 2 + X * Y) ≤ ρ * (ρ ^ 2 + Y ^ 2) := by
  have hρz : z ≤ ρ := by nlinarith [sq_nonneg X]
  have e : ρ * (ρ ^ 2 + Y ^ 2) - z * (ρ ^ 2 + X * Y) =
      (ρ - z) ^ 2 * (2 * ρ + z) / 2 + (ρ - z) * Y ^ 2 + z * (X - Y) ^ 2 / 2 + z * Y ^ 2 / 2 := by
    have : X ^ 2 = ρ ^ 2 - z ^ 2 := by linarith
    linear_combination (-z / 2) * this
  have : 0 ≤ (ρ - z) ^ 2 * (2 * ρ + z) / 2 + (ρ - z) * Y ^ 2 + z * (X - Y) ^ 2 / 2 +
      z * Y ^ 2 / 2 := by
    have := mul_nonneg (sq_nonneg (ρ - z)) (by linarith : (0 : ℝ) ≤ 2 * ρ + z)
    have := mul_nonneg (sub_nonneg.mpr hρz) (sq_nonneg Y)
    have := mul_nonneg hz.le (sq_nonneg (X - Y))
    have := mul_nonneg hz.le (sq_nonneg Y)
    linarith
  linarith

/-- **Corrected φ condition (the planner's pair).** If `T_z > 0`, `|T_y| ≤ t T_z` and both linear
rows hold with budget `K`, i.e. `|Ṫ_x| + t|Ṫ_z| ≤ K` and `|Ṫ_y| + t|Ṫ_z| ≤ K`, then
`|φ̇| ≤ K / T_z`. (The box on `T_x` is not even needed.) -/
theorem phi_rate_bound_pair {x y z dx dy dz t K : ℝ} (hz : 0 < z) (ht : 0 ≤ t)
    (hy : |y| ≤ t * z) (hrx : |dx| + t * |dz| ≤ K) (hry : |dy| + t * |dz| ≤ K) :
    |phiRate x y z dx dy dz| ≤ K / z := by
  have hp : 0 < x ^ 2 + z ^ 2 := by positivity
  set ρ := √(x ^ 2 + z ^ 2) with hρdef
  have hρpos : 0 < ρ := sqrt_pos.mpr hp
  have hρ2 : ρ ^ 2 = x ^ 2 + z ^ 2 := sq_sqrt hp.le
  have hρz : z ≤ ρ := by nlinarith [sq_nonneg x]
  set Q := x ^ 2 + y ^ 2 + z ^ 2 with hQdef
  have hQ : 0 < Q := by rw [hQdef]; positivity
  unfold phiRate
  rw [← hQdef, ← hρdef, abs_div, abs_of_pos (mul_pos hQ hρpos),
    div_le_div_iff₀ (mul_pos hQ hρpos) hz]
  set X := |x|
  set Y := |y|
  have hX : 0 ≤ X := abs_nonneg x
  have hY : 0 ≤ Y := abs_nonneg y
  have hρ2' : ρ ^ 2 = X ^ 2 + z ^ 2 := by rw [hρ2, sq_abs]
  have hQ' : Q = ρ ^ 2 + Y ^ 2 := by rw [hρ2, hQdef, sq_abs]; ring
  have hnum : |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)| ≤
      |dy| * ρ ^ 2 + Y * X * |dx| + Y * z * |dz| := by
    calc |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)|
        ≤ |dy * (x ^ 2 + z ^ 2)| + |y * (x * dx + z * dz)| := abs_sub _ _
      _ ≤ |dy| * ρ ^ 2 + Y * (X * |dx| + z * |dz|) := by
          rw [abs_mul, abs_mul, abs_of_pos hp, ← hρ2]
          gcongr
          calc |x * dx + z * dz| ≤ |x * dx| + |z * dz| := abs_add_le _ _
            _ = X * |dx| + z * |dz| := by rw [abs_mul, abs_mul, abs_of_pos hz]
      _ = _ := by ring
  have ha := abs_nonneg dx
  have hb := abs_nonneg dy
  have hc := abs_nonneg dz
  -- step 1: numerator ≤ K (ρ² + X Y)
  have hYz : Y * z ≤ t * ρ ^ 2 := by
    have : Y * z ≤ t * z * z := mul_le_mul_of_nonneg_right hy hz.le
    nlinarith [sq_nonneg X]
  have hs1 : |dy| * ρ ^ 2 + Y * X * |dx| + Y * z * |dz| ≤ K * (ρ ^ 2 + X * Y) := by
    have e1 : |dy| * ρ ^ 2 ≤ (K - t * |dz|) * ρ ^ 2 :=
      mul_le_mul_of_nonneg_right (by linarith) (sq_nonneg ρ)
    have e2 : Y * X * |dx| ≤ Y * X * (K - t * |dz|) :=
      mul_le_mul_of_nonneg_left (by linarith) (mul_nonneg hY hX)
    have e3 : Y * z * |dz| ≤ t * ρ ^ 2 * |dz| := mul_le_mul_of_nonneg_right hYz hc
    have e4 : 0 ≤ t * |dz| * (X * Y) := by positivity
    nlinarith
  have hK : 0 ≤ K := le_trans (by positivity) hrx
  -- step 2: z (ρ² + X Y) ≤ ρ Q
  have hs2 := pair_key hX hY hz hρpos.le hρ2'
  rw [← hQ'] at hs2
  calc |dy * (x ^ 2 + z ^ 2) - y * (x * dx + z * dz)| * z
      ≤ K * (ρ ^ 2 + X * Y) * z := by gcongr; exact hnum.trans hs1
    _ = K * (z * (ρ ^ 2 + X * Y)) := by ring
    _ ≤ K * (ρ * Q) := by gcongr
    _ = K * (Q * ρ) := by ring

/-- **N2, as used by the planner (pointwise).** With `T_z ≥ T_floor > 0`, the box
`|T_x|, |T_y| ≤ t T_z`, and the two linear rows `|Ṫ_x| + t|Ṫ_z| ≤ ω T_floor`,
`|Ṫ_y| + t|Ṫ_z| ≤ ω T_floor`: both gimbal rates are at most `ω`. -/
theorem gimbal_rate_pair {x y z dx dy dz t F ω : ℝ} (hF : 0 < F) (hz : F ≤ z) (ht : 0 ≤ t)
    (hx : |x| ≤ t * z) (hy : |y| ≤ t * z) (hrx : |dx| + t * |dz| ≤ ω * F)
    (hry : |dy| + t * |dz| ≤ ω * F) :
    |(dx * z - x * dz) / (x ^ 2 + z ^ 2)| ≤ ω ∧ |phiRate x y z dx dy dz| ≤ ω := by
  have hzpos : 0 < z := lt_of_lt_of_le hF hz
  have hω : 0 ≤ ω := by
    have : 0 ≤ ω * F := le_trans (by positivity) hrx
    exact nonneg_of_mul_nonneg_left this hF
  constructor
  · calc |(dx * z - x * dz) / (x ^ 2 + z ^ 2)| ≤ (|dx| + t * |dz|) / F :=
          theta_rate_bound hF hz ht hx
      _ ≤ ω * F / F := by gcongr
      _ = ω := by field_simp
  · calc |phiRate x y z dx dy dz| ≤ ω * F / z := phi_rate_bound_pair hzpos ht hy hrx hry
      _ ≤ ω * F / F := by gcongr
      _ = ω := by field_simp

/-! ## First-order hold on one interval -/

theorem seg_abs_le {a0 a1 b0 b1 l t : ℝ} (hl0 : 0 ≤ l) (hl1 : l ≤ 1) (h0 : |a0| ≤ t * b0)
    (h1 : |a1| ≤ t * b1) : |a0 + l * (a1 - a0)| ≤ t * (b0 + l * (b1 - b0)) := by
  obtain ⟨h0l, h0u⟩ := abs_le.mp h0
  obtain ⟨h1l, h1u⟩ := abs_le.mp h1
  have hm : 0 ≤ 1 - l := by linarith
  rw [abs_le]
  constructor
  · nlinarith [mul_le_mul_of_nonneg_left h0l hm, mul_le_mul_of_nonneg_left h1l hl0]
  · nlinarith [mul_le_mul_of_nonneg_left h0u hm, mul_le_mul_of_nonneg_left h1u hl0]

theorem hasDerivAt_foh (a c s₀ h u : ℝ) :
    HasDerivAt (fun u => a + (u - s₀) / h * c) (c / h) u := by
  have := ((((hasDerivAt_id u).sub_const s₀).div_const h).mul_const c).const_add a
  refine this.congr_deriv ?_
  simp [div_eq_mul_inv]; ring

/-- **N2 for first-order-hold thrust (what the planner imposes).** On one interval
`[s₀, s₀ + h]`, body thrust is linear between the nodes `(x₀,y₀,z₀)` and `(x₁,y₁,z₁)`. If at
both nodes `z ≥ F > 0`, `|x|, |y| ≤ t z`, and the planner's two linear rows hold,
`|Δx| + t|Δz| ≤ ω F h`, `|Δy| + t|Δz| ≤ ω F h`, then for every `u` in the interval
`|θ(u) − θ(s₀)| ≤ ω (u − s₀)` and `|φ(u) − φ(s₀)| ≤ ω (u − s₀)`, with
`θ = arctan (T_x/T_z)`, `φ = arcsin (T_y/‖T‖)` (exact flight-convention angles). -/
theorem foh_gimbal_rate {x₀ y₀ z₀ x₁ y₁ z₁ t F ω s₀ h : ℝ} (hh : 0 < h) (hF : 0 < F)
    (ht : 0 ≤ t) (hz₀ : F ≤ z₀) (hz₁ : F ≤ z₁) (hx₀ : |x₀| ≤ t * z₀) (hx₁ : |x₁| ≤ t * z₁)
    (hy₀ : |y₀| ≤ t * z₀) (hy₁ : |y₁| ≤ t * z₁)
    (hrx : |x₁ - x₀| + t * |z₁ - z₀| ≤ ω * F * h) (hry : |y₁ - y₀| + t * |z₁ - z₀| ≤ ω * F * h) :
    let Tx := fun u => x₀ + (u - s₀) / h * (x₁ - x₀)
    let Ty := fun u => y₀ + (u - s₀) / h * (y₁ - y₀)
    let Tz := fun u => z₀ + (u - s₀) / h * (z₁ - z₀)
    ∀ u ∈ Set.Icc s₀ (s₀ + h),
      |arctan (Tx u / Tz u) - arctan (Tx s₀ / Tz s₀)| ≤ ω * (u - s₀) ∧
      |arcsin (Ty u / √(Tx u ^ 2 + Ty u ^ 2 + Tz u ^ 2)) -
        arcsin (Ty s₀ / √(Tx s₀ ^ 2 + Ty s₀ ^ 2 + Tz s₀ ^ 2))| ≤ ω * (u - s₀) := by
  intro Tx Ty Tz
  -- pointwise constraints along the segment
  have hseg : ∀ u ∈ Set.Icc s₀ (s₀ + h), F ≤ Tz u ∧ |Tx u| ≤ t * Tz u ∧ |Ty u| ≤ t * Tz u := by
    intro u hu
    set l := (u - s₀) / h
    have hl0 : 0 ≤ l := div_nonneg (by linarith [hu.1]) hh.le
    have hl1 : l ≤ 1 := by rw [div_le_one hh]; linarith [hu.2]
    refine ⟨?_, seg_abs_le hl0 hl1 hx₀ hx₁, seg_abs_le hl0 hl1 hy₀ hy₁⟩
    show F ≤ z₀ + l * (z₁ - z₀)
    nlinarith
  have hdx := fun u => hasDerivAt_foh x₀ (x₁ - x₀) s₀ h u
  have hdy := fun u => hasDerivAt_foh y₀ (y₁ - y₀) s₀ h u
  have hdz := fun u => hasDerivAt_foh z₀ (z₁ - z₀) s₀ h u
  have hrx' : |(x₁ - x₀) / h| + t * |(z₁ - z₀) / h| ≤ ω * F := by
    rw [abs_div, abs_div, abs_of_pos hh, ← mul_div_assoc, ← add_div, div_le_iff₀ hh]
    exact hrx
  have hry' : |(y₁ - y₀) / h| + t * |(z₁ - z₀) / h| ≤ ω * F := by
    rw [abs_div, abs_div, abs_of_pos hh, ← mul_div_assoc, ← add_div, div_le_iff₀ hh]
    exact hry
  have hpair : ∀ u ∈ Set.Icc s₀ (s₀ + h),
      |((x₁ - x₀) / h * Tz u - Tx u * ((z₁ - z₀) / h)) / (Tx u ^ 2 + Tz u ^ 2)| ≤ ω ∧
      |phiRate (Tx u) (Ty u) (Tz u) ((x₁ - x₀) / h) ((y₁ - y₀) / h) ((z₁ - z₀) / h)| ≤ ω := by
    intro u hu
    obtain ⟨h1, h2, h3⟩ := hseg u hu
    exact gimbal_rate_pair hF h1 ht h2 h3 hrx' hry'
  have hzpos : ∀ u ∈ Set.Icc s₀ (s₀ + h), 0 < Tz u := fun u hu => lt_of_lt_of_le hF (hseg u hu).1
  intro u hu
  have hs₀ : s₀ ∈ Set.Icc s₀ (s₀ + h) := ⟨le_rfl, by linarith⟩
  constructor
  · have := norm_image_sub_le_of_norm_deriv_le_segment' (f := fun u => arctan (Tx u / Tz u))
      (C := ω) (fun v hv => (hasDerivAt_theta (hdx v) (hdz v) (hzpos v hv)).hasDerivWithinAt)
      (fun v hv => (hpair v (Set.Ico_subset_Icc_self hv)).1) u hu
    simpa [Real.norm_eq_abs] using this
  · have := norm_image_sub_le_of_norm_deriv_le_segment'
      (f := fun u => arcsin (Ty u / √(Tx u ^ 2 + Ty u ^ 2 + Tz u ^ 2)))
      (C := ω) (fun v hv => (hasDerivAt_phi (hdx v) (hdy v) (hdz v)
        (by have := hzpos v hv; positivity)).hasDerivWithinAt)
      (fun v hv => (hpair v (Set.Ico_subset_Icc_self hv)).2) u hu
    simpa [Real.norm_eq_abs] using this

end LcvxSolver
