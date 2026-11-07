import LcvxObstruction.DiveBrake

/-!
# Theorem B*, quantitative (math/02 §10.3 Step 7), constant acceleration bounds

For `δ ≤ π/4`, every boundary datum `θ` of the (unconstrained) landing set satisfies
`‖Λ(θ) − Λ(θ_m)‖ ≥ η₀` where `Λ(θ) = r₀ + s* v₀`, `θ_m` is the midpoint of the dive-then-brake
witnesses, and `η₀ ≥ 0` is any number with `(1 + c₁) η₀ + √(2 W_b η₀) ≤ γ_X`,
`γ_X = (5/32) a_min sin δ s*²`, `c₁ = 1/(ω ϑ s*)`, `ϑ = a_min sin δ / (4 a_max)`,
`W_b = a_max (tf − s*)²/2`.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- If `x ≤ λ A/2 + B/λ` for every `λ > 0` (`A, B ≥ 0`), then `x ≤ √(2AB)`. -/
theorem le_sqrt_of_forall_amgm {x A B : ℝ} (hA : 0 ≤ A) (hB : 0 ≤ B)
    (h : ∀ l : ℝ, 0 < l → x ≤ l * A / 2 + B / l) : x ≤ Real.sqrt (2 * A * B) := by
  rcases le_or_gt x 0 with hx | hx
  · exact hx.trans (Real.sqrt_nonneg _)
  rcases eq_or_lt_of_le hA with hA0 | hA0
  · -- A = 0: x ≤ B/l for all l, impossible for x > 0
    exfalso
    have := h ((B + 1) / x) (by positivity)
    rw [← hA0, mul_zero, zero_div, zero_add, div_div_eq_mul_div] at this
    rw [le_div_iff₀ (by positivity)] at this
    nlinarith
  · have := h (x / A) (by positivity)
    have e : x / A * A / 2 = x / 2 := by field_simp
    rw [e, div_div_eq_mul_div] at this
    have h2 : x / 2 ≤ B * A / x := by linarith
    rw [le_div_iff₀ hx] at h2
    apply Real.le_sqrt_of_sq_le
    nlinarith

/-- Horizontal part of a unit vector: `‖d − d_z e_z‖ ≤ l/2 + (1 − d_z)/l` for every `l > 0`. -/
theorem norm_lateral_le_amgm {d : E3} (hd : ‖d‖ = 1) {l : ℝ} (hl : 0 < l) :
    ‖d - ⟪d, ez⟫ • ez‖ ≤ l / 2 + (1 - ⟪d, ez⟫) / l := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hdd : ⟪d, d⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hd]; norm_num
  have hsq : ‖d - ⟪d, ez⟫ • ez‖ ^ 2 = 1 - ⟪d, ez⟫ ^ 2 := by
    rw [← real_inner_self_eq_norm_sq]
    simp only [inner_sub_left, inner_sub_right, real_inner_smul_left, real_inner_smul_right, hzz,
      hdd, real_inner_comm d ez]
    ring
  have hz1 : ⟪d, ez⟫ ≤ 1 := inner_le_one_of_unit hd norm_ez
  have hz2 : -1 ≤ ⟪d, ez⟫ := by
    have := neg_le_of_abs_le (abs_real_inner_le_norm d ez); rw [hd, norm_ez] at this; linarith
  set y := ‖d - ⟪d, ez⟫ • ez‖
  have hy : y ^ 2 ≤ 2 * (1 - ⟪d, ez⟫) := by rw [hsq]; nlinarith
  rw [div_add_div _ _ (two_ne_zero) hl.ne', le_div_iff₀ (by positivity)]
  nlinarith [sq_nonneg (y - l)]

/-- **Brake lateral bound** (Step 7 (v)): the horizontal part of the brake impulse
`B = ∫_{(s*,tf]} (s − s*) a d` satisfies `‖B_h‖ ≤ √(2 W_b η_b)`, with
`W_b = a_max (tf − s*)²/2` and `η_b = ∫_{(s*,tf]} (s − s*) a (1 − d_z)`. -/
theorem brake_lateral_le {tf sS amax : ℝ} {a : ℝ → ℝ} {d : ℝ → E3} (hsS : 0 ≤ sS)
    (hsStf : sS ≤ tf) (haI : IntegrableOn a (Icc 0 tf))
    (hdm : AEStronglyMeasurable d (volume.restrict (Icc 0 tf)))
    (hdu : ∀ s ∈ Icc 0 tf, ‖d s‖ = 1) (ha0 : ∀ s ∈ Icc 0 tf, 0 ≤ a s)
    (hamax : ∀ s ∈ Icc 0 tf, a s ≤ amax) :
    ‖(∫ s in Ioc sS tf, (s - sS) • (a s • d s)) -
        ⟪∫ s in Ioc sS tf, (s - sS) • (a s • d s), ez⟫ • ez‖ ≤
      Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) *
        ∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫))) := by
  have hsub : Ioc sS tf ⊆ Icc 0 tf := Ioc_subset_Icc_self.trans (Icc_subset_Icc_left hsS)
  have hmem : ∀ s ∈ Ioc sS tf, s ∈ Icc 0 tf := fun s hs => hsub hs
  have hf0 : IntegrableOn (fun s => a s • d s) (Icc 0 tf) := integrableOn_smul_of_unit haI hdm hdu
  have hf : IntegrableOn (fun s => (s - sS) • (a s • d s)) (Ioc sS tf) :=
    (integrableOn_cont_smul hf0 (c := fun s => s - sS) (by fun_prop)).mono_set hsub
  have hwa : IntegrableOn (fun s => (s - sS) * a s) (Ioc sS tf) :=
    ((haI.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => s - sS) (Icc 0 tf))
      isCompact_Icc)).mono_set hsub
  have hz : IntegrableOn (fun s => ⟪(s - sS) • (a s • d s), ez⟫) (Ioc sS tf) := hf.inner_const ez
  have hηI : IntegrableOn (fun s => (s - sS) * (a s * (1 - ⟪d s, ez⟫))) (Ioc sS tf) := by
    refine (hwa.sub hz).congr_fun (fun s _ => ?_) measurableSet_Ioc
    simp only [Pi.sub_apply, real_inner_smul_left]; ring
  -- the horizontal part as an integral
  have hBh : (∫ s in Ioc sS tf, (s - sS) • (a s • d s)) -
      ⟪∫ s in Ioc sS tf, (s - sS) • (a s • d s), ez⟫ • ez =
      ∫ s in Ioc sS tf, ((s - sS) * a s) • (d s - ⟪d s, ez⟫ • ez) := by
    have hzi : ⟪∫ s in Ioc sS tf, (s - sS) • (a s • d s), ez⟫ =
        ∫ s in Ioc sS tf, ⟪(s - sS) • (a s • d s), ez⟫ := by
      rw [real_inner_comm, ← integral_inner hf]
      exact setIntegral_congr_fun measurableSet_Ioc (fun s _ => real_inner_comm _ _)
    rw [hzi, ← integral_smul_const, ← integral_sub hf (hz.smul_const ez)]
    refine setIntegral_congr_fun measurableSet_Ioc fun s _ => ?_
    simp only [real_inner_smul_left]; module
  rw [hBh]
  refine le_trans (norm_integral_le_integral_norm _) ?_
  have hWb : ∫ s in Ioc sS tf, (s - sS) * a s ≤ amax * (tf - sS) ^ 2 / 2 := by
    have hc : IntegrableOn (fun s => (s - sS) * amax) (Ioc sS tf) :=
      (Continuous.integrableOn_Icc (by fun_prop)).mono_set Ioc_subset_Icc_self
    calc ∫ s in Ioc sS tf, (s - sS) * a s ≤ ∫ s in Ioc sS tf, (s - sS) * amax :=
          setIntegral_mono_on hwa hc measurableSet_Ioc fun s hs =>
            mul_le_mul_of_nonneg_left (hamax s (hmem s hs)) (by linarith [hs.1])
      _ = amax * (tf - sS) ^ 2 / 2 := by
          rw [integral_mul_const, integral_Ioc_sub_self hsStf]; ring
  have hηnn : 0 ≤ ∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫)) :=
    setIntegral_nonneg measurableSet_Ioc fun s hs => mul_nonneg (by linarith [hs.1])
      (mul_nonneg (ha0 s (hmem s hs)) (by linarith [inner_le_one_of_unit (hdu s (hmem s hs)) norm_ez]))
  apply le_sqrt_of_forall_amgm (by have := sq_nonneg (tf - sS); nlinarith [ha0 tf ⟨by linarith, le_rfl⟩, hamax tf ⟨by linarith, le_rfl⟩]) hηnn
  intro l hl
  have hg : IntegrableOn (fun s => l / 2 * ((s - sS) * a s) +
      l⁻¹ * ((s - sS) * (a s * (1 - ⟪d s, ez⟫)))) (Ioc sS tf) :=
    (hwa.const_mul _).add (hηI.const_mul _)
  calc ∫ s in Ioc sS tf, ‖((s - sS) * a s) • (d s - ⟪d s, ez⟫ • ez)‖
      ≤ ∫ s in Ioc sS tf, (l / 2 * ((s - sS) * a s) +
          l⁻¹ * ((s - sS) * (a s * (1 - ⟪d s, ez⟫)))) := by
        refine integral_mono_of_nonneg (ae_of_all _ fun s => norm_nonneg _) hg ?_
        refine ae_restrict_of_forall_mem measurableSet_Ioc fun s hs => ?_
        have hw : 0 ≤ (s - sS) * a s := mul_nonneg (by linarith [hs.1]) (ha0 s (hmem s hs))
        dsimp only
        rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hw]
        have := norm_lateral_le_amgm (hdu s (hmem s hs)) hl
        calc (s - sS) * a s * ‖d s - ⟪d s, ez⟫ • ez‖
            ≤ (s - sS) * a s * (l / 2 + (1 - ⟪d s, ez⟫) / l) := mul_le_mul_of_nonneg_left this hw
          _ = _ := by field_simp
    _ = l / 2 * (∫ s in Ioc sS tf, (s - sS) * a s) +
          l⁻¹ * (∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫))) := by
        rw [integral_add (hwa.const_mul _) (hηI.const_mul _), integral_const_mul, integral_const_mul]
    _ ≤ l * (amax * (tf - sS) ^ 2 / 2) / 2 +
          (∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫))) / l := by
        rw [inv_mul_eq_div]
        have := mul_le_mul_of_nonneg_left hWb (by positivity : (0:ℝ) ≤ l / 2)
        have e2 : l * (amax * (tf - sS) ^ 2 / 2) / 2 = l / 2 * (amax * (tf - sS) ^ 2 / 2) := by ring
        rw [e2]; linarith

/-- Mean value bound: `(y − x) sin m ≤ cos x − cos y` for `−π/2 ≤ m ≤ x ≤ y ≤ π/2`. -/
theorem cos_sub_cos_ge {x y m : ℝ} (hxy : x ≤ y) (hm : -(π / 2) ≤ m) (hmx : m ≤ x)
    (hy : y ≤ π / 2) : (y - x) * Real.sin m ≤ Real.cos x - Real.cos y := by
  rcases eq_or_lt_of_le hxy with h | h
  · subst h; simp
  obtain ⟨c, hc, hcd⟩ := exists_hasDerivAt_eq_slope Real.cos (fun t => -Real.sin t) h
    Real.continuous_cos.continuousOn fun t _ => Real.hasDerivAt_cos t
  have hsc : Real.sin m ≤ Real.sin c :=
    Real.sin_le_sin_of_le_of_le_pi_div_two hm (by linarith [hc.2]) (by linarith [hc.1])
  have hyx : 0 < y - x := by linarith
  rw [eq_div_iff hyx.ne'] at hcd
  nlinarith [mul_le_mul_of_nonneg_left hsc hyx.le]

set_option maxHeartbeats 1600000 in
/-- **Dive lateral bound** (Step 7 (i)–(iv)). For `0 < δ ≤ π/4`, `ω s* ≤ δ`, a competitor with
`a_min ≤ a ≤ a_max` and the dive impulse `X = ∫_{[0,s*]} (s* − s) a d`:
`γ_X − η_d/(ωτ) ≤ ‖X_h‖`, with `τ = ϑ s*`, `ϑ = a_min sin δ/(4 a_max)`,
`γ_X = (5/32) a_min sin δ s*²` and `η_d = X_z − ∫_{[0,s*]} (s* − s) a cos(δ + ωs)`. -/
theorem dive_lateral_ge {tf ω δ sS amin amax : ℝ} {a : ℝ → ℝ} {d b : ℝ → E3}
    (hatt : AttitudeAdmissible tf ω δ d b) (hsS : 0 < sS) (hsStf : sS ≤ tf) (hω : 0 < ω)
    (hδ : 0 < δ) (hδ4 : δ ≤ π / 4) (hωs : ω * sS ≤ δ) (hamin : 0 < amin)
    (haI : IntegrableOn a (Icc 0 tf)) (hab : ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax) :
    5 / 32 * amin * Real.sin δ * sS ^ 2 -
        (⟪∫ s in Icc 0 sS, (sS - s) • (a s • d s), ez⟫ -
          ∫ s in Icc 0 sS, (sS - s) * a s * Real.cos (δ + ω * s)) /
        (ω * (amin * Real.sin δ / (4 * amax) * sS)) ≤
      ‖(∫ s in Icc 0 sS, (sS - s) • (a s • d s)) -
        ⟪∫ s in Icc 0 sS, (sS - s) • (a s • d s), ez⟫ • ez‖ := by
  have hamax : 0 < amax := hamin.trans_le (hab 0 ⟨le_rfl, hsS.le.trans hsStf⟩).1 |>.trans_le
    (hab 0 ⟨le_rfl, hsS.le.trans hsStf⟩).2
  have hsinδ : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ (by linarith [Real.pi_pos])
  have hsin1 : Real.sin δ ≤ 1 := Real.sin_le_one δ
  set ϑ := amin * Real.sin δ / (4 * amax) with hϑ
  have hϑ0 : 0 < ϑ := by positivity
  have hϑ4 : ϑ ≤ 1 / 4 := by
    rw [hϑ, div_le_iff₀ (by positivity)]
    have : amin ≤ amax := (hab 0 ⟨le_rfl, hsS.le.trans hsStf⟩).1.trans (hab 0 ⟨le_rfl, hsS.le.trans hsStf⟩).2
    nlinarith
  set τ := ϑ * sS with hτ
  have hτ0 : 0 < τ := by positivity
  have hτS : τ ≤ sS := by nlinarith
  have hsub : Icc 0 sS ⊆ Icc 0 tf := Icc_subset_Icc_right hsStf
  have hmem : ∀ s ∈ Icc 0 sS, s ∈ Icc 0 tf := fun s hs => hsub hs
  have hτI : τ ∈ Icc 0 tf := ⟨hτ0.le, hτS.trans hsStf⟩
  set c := b τ with hc
  have hcu : ‖c‖ = 1 := hatt.b_unit τ hτI
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  -- integrability
  have hf0 : IntegrableOn (fun s => a s • d s) (Icc 0 tf) :=
    integrableOn_smul_of_unit haI hatt.d_meas hatt.d_unit
  have hf : IntegrableOn (fun s => (sS - s) • (a s • d s)) (Icc 0 sS) :=
    (integrableOn_cont_smul hf0 (c := fun s => sS - s) (by fun_prop)).mono_set hsub
  have haS : IntegrableOn a (Icc 0 sS) := haI.mono_set hsub
  set X := ∫ s in Icc 0 sS, (sS - s) • (a s • d s) with hX
  set Z0 := ∫ s in Icc 0 sS, (sS - s) * a s * Real.cos (δ + ω * s) with hZ0
  set G := ∫ s in Icc 0 sS, (sS - s) * a s * Real.cos (δ + ω * |s - τ|) with hG
  have hIg : ∀ g : ℝ → ℝ, Continuous g →
      IntegrableOn (fun s => (sS - s) * a s * g s) (Icc 0 sS) := fun g hg => by
    have := haS.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => sS - s) (Icc 0 sS))
      isCompact_Icc
    exact this.mul_continuousOn hg.continuousOn isCompact_Icc
  -- (i) support inequality
  have hsupp : ∀ s ∈ Icc 0 sS, Real.cos (δ + ω * |s - τ|) ≤ ⟪d s, c⟫ := fun s hs => by
    have h1 := hatt.gimbal s (hmem s hs)
    have h2 := hatt.b_rate s (hmem s hs) τ hτI
    have hab' : |s - τ| ≤ sS := by
      rw [abs_sub_le_iff]; constructor <;> linarith [hs.1, hs.2]
    apply cos_le_inner_of_angle_le (hatt.d_unit s (hmem s hs)) hcu
      ((angle_le_angle_add_angle (d s) (b s) c).trans (add_le_add h1 h2))
    nlinarith [mul_le_mul_of_nonneg_left hab' hω.le, Real.pi_pos]
  have hGle : G ≤ ⟪X, c⟫ := by
    rw [hX, real_inner_comm, ← integral_inner hf]
    refine setIntegral_mono_on (hIg _ (by fun_prop)) (hf.const_inner c) measurableSet_Icc
      fun s hs => ?_
    rw [real_inner_smul_right, real_inner_smul_right, real_inner_comm (d s) c]
    have hw : 0 ≤ (sS - s) * a s :=
      mul_nonneg (by linarith [hs.2]) (hamin.le.trans (hab s (hmem s hs)).1)
    nlinarith [mul_le_mul_of_nonneg_left (hsupp s hs) hw]
  -- (ii) decomposition along e_z
  set Xh := X - ⟪X, ez⟫ • ez with hXh
  set ch := c - ⟪c, ez⟫ • ez with hch
  have hXhz : ⟪Xh, ez⟫ = 0 := by
    simp only [hXh, inner_sub_left, real_inner_smul_left, hzz]; ring
  have hcz1 : ⟪c, ez⟫ ≤ 1 := inner_le_one_of_unit hcu norm_ez
  have hcz0 : Real.cos (ω * τ) ≤ ⟪c, ez⟫ := hatt.inner_b_ez hτI (by nlinarith [Real.pi_pos])
  have hωτ : ω * τ ≤ π / 2 := by nlinarith [Real.pi_pos]
  have hcos0 : 0 ≤ Real.cos (ω * τ) :=
    Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [Real.pi_pos], hωτ⟩
  have hchn : ‖ch‖ ≤ ω * τ := by
    have hsq : ‖ch‖ ^ 2 = 1 - ⟪c, ez⟫ ^ 2 := by
      rw [← real_inner_self_eq_norm_sq]
      have hcc : ⟪c, c⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hcu]; norm_num
      simp only [hch, inner_sub_left, inner_sub_right, real_inner_smul_left, real_inner_smul_right,
        hzz, hcc, real_inner_comm c ez]
      ring
    have hs2 : ‖ch‖ ^ 2 ≤ Real.sin (ω * τ) ^ 2 := by
      rw [hsq, Real.sin_sq]; nlinarith
    have hsn : 0 ≤ Real.sin (ω * τ) :=
      Real.sin_nonneg_of_nonneg_of_le_pi (by positivity) (by linarith [Real.pi_pos])
    calc ‖ch‖ ≤ Real.sin (ω * τ) := (pow_le_pow_iff_left₀ (norm_nonneg _) hsn two_ne_zero).mp hs2
      _ ≤ ω * τ := Real.sin_le (by positivity)
  have hXz0 : Z0 ≤ ⟪X, ez⟫ := by
    rw [hX, real_inner_comm, ← integral_inner hf]
    refine setIntegral_mono_on (hIg _ (by fun_prop)) (hf.const_inner ez) measurableSet_Icc
      fun s hs => ?_
    rw [real_inner_smul_right, real_inner_smul_right, real_inner_comm (d s) ez]
    have hw : 0 ≤ (sS - s) * a s :=
      mul_nonneg (by linarith [hs.2]) (hamin.le.trans (hab s (hmem s hs)).1)
    have := hatt.inner_d_ez hω.le hδ.le (hmem s hs) (by nlinarith [hs.2, Real.pi_pos])
    nlinarith [mul_le_mul_of_nonneg_left this hw]
  have hZ0nn : 0 ≤ Z0 := setIntegral_nonneg measurableSet_Icc fun s hs => by
    have hc' : 0 ≤ Real.cos (δ + ω * s) := Real.cos_nonneg_of_mem_Icc
      ⟨by nlinarith [hs.1, Real.pi_pos], by nlinarith [hs.2]⟩
    exact mul_nonneg (mul_nonneg (by linarith [hs.2]) (hamin.le.trans (hab s (hmem s hs)).1)) hc'
  have hdecomp : ⟪X, c⟫ ≤ ⟪X, ez⟫ + ‖Xh‖ * ‖ch‖ := by
    have e : ⟪X, c⟫ = ⟪X, ez⟫ * ⟪c, ez⟫ + ⟪Xh, ch⟫ := by
      simp only [hXh, hch, inner_sub_left, inner_sub_right, real_inner_smul_left,
        real_inner_smul_right, hzz, real_inner_comm ez X, real_inner_comm ez c]
      ring
    rw [e]
    have h1 : ⟪X, ez⟫ * ⟪c, ez⟫ ≤ ⟪X, ez⟫ :=
      mul_le_of_le_one_right (hZ0nn.trans hXz0) hcz1
    have h2 := real_inner_le_norm Xh ch
    linarith
  have hωτ0 : 0 < ω * τ := by positivity
  have hωτ0' : 0 < ω * τ := hωτ0
  -- (iii) the gain of the tilted reference
  have hGZ : ω * τ * (5 / 32 * amin * Real.sin δ * sS ^ 2) ≤ G - Z0 := by
    set c1 := ω * τ * Real.sin δ * amin with hc1
    set c2 := ω * τ * amax * sS with hc2
    set q1 : ℝ → ℝ := (Icc τ sS).indicator (fun s => c1 * (sS - s)) with hq1
    set q2 : ℝ → ℝ := (Ico 0 (τ / 2)).indicator (fun _ => -c2) with hq2
    have hq1I : IntegrableOn q1 (Icc 0 sS) :=
      (Continuous.integrableOn_Icc (by fun_prop)).indicator measurableSet_Icc
    have hq2I : IntegrableOn q2 (Icc 0 sS) :=
      (integrableOn_const measure_Icc_lt_top.ne).indicator measurableSet_Ico
    have hkI := hIg (fun s => Real.cos (δ + ω * |s - τ|) - Real.cos (δ + ω * s)) (by fun_prop)
    have hGZeq : G - Z0 = ∫ s in Icc 0 sS,
        (sS - s) * a s * (Real.cos (δ + ω * |s - τ|) - Real.cos (δ + ω * s)) := by
      rw [hG, hZ0, ← integral_sub (hIg _ (by fun_prop)) (hIg _ (by fun_prop))]
      exact setIntegral_congr_fun measurableSet_Icc fun s _ => by ring
    have hq : ∫ s in Icc 0 sS, (q1 s + q2 s) ≤ G - Z0 := by
      rw [hGZeq]
      refine setIntegral_mono_on (hq1I.add hq2I) hkI measurableSet_Icc fun s hs => ?_
      have ha1 := (hab s (hmem s hs)).1
      have ha2 := (hab s (hmem s hs)).2
      have hw : 0 ≤ sS - s := by linarith [hs.2]
      rcases le_or_gt τ s with h1 | h1
      · have e1 : q1 s = c1 * (sS - s) := by simp [hq1, h1, hs.2]
        have e2 : q2 s = 0 := by
          simp only [hq2]; rw [indicator_of_notMem]; intro h; linarith [h.2]
        rw [e1, e2, add_zero, abs_of_nonneg (by linarith : (0:ℝ) ≤ s - τ)]
        have hmv := cos_sub_cos_ge (x := δ + ω * (s - τ)) (y := δ + ω * s) (m := δ)
          (by nlinarith) (by linarith [Real.pi_pos]) (by nlinarith) (by nlinarith [hs.2])
        have hh : ω * τ * Real.sin δ ≤ Real.cos (δ + ω * (s - τ)) - Real.cos (δ + ω * s) := by
          have : δ + ω * s - (δ + ω * (s - τ)) = ω * τ := by ring
          rw [this] at hmv; exact hmv
        have hh0 : 0 ≤ ω * τ * Real.sin δ := by positivity
        have : (sS - s) * amin * (ω * τ * Real.sin δ) ≤
            (sS - s) * a s * (Real.cos (δ + ω * (s - τ)) - Real.cos (δ + ω * s)) := by
          apply mul_le_mul (mul_le_mul_of_nonneg_left ha1 hw) hh hh0
          exact mul_nonneg hw (hamin.le.trans ha1)
        rw [hc1]; nlinarith [this]
      · have e1 : q1 s = 0 := by
          simp only [hq1]; rw [indicator_of_notMem]; intro h; linarith [h.1]
        rw [e1, zero_add, abs_of_neg (by linarith : s - τ < 0)]
        rcases le_or_gt (τ / 2) s with h2 | h2
        · have e2 : q2 s = 0 := by
            simp only [hq2]; rw [indicator_of_notMem]; intro h; linarith [h.2]
          rw [e2]
          have : Real.cos (δ + ω * s) ≤ Real.cos (δ + ω * -(s - τ)) :=
            Real.cos_le_cos_of_nonneg_of_le_pi (by nlinarith) (by nlinarith [hs.2, Real.pi_pos])
              (by nlinarith)
          exact mul_nonneg (mul_nonneg hw (hamin.le.trans ha1)) (by linarith)
        · have e2 : q2 s = -c2 := by simp [hq2, hs.1, h2]
          rw [e2]
          have hab2 : |Real.cos (δ + ω * -(s - τ)) - Real.cos (δ + ω * s)| ≤ ω * τ := by
            refine (Real.abs_cos_sub_cos_le _ _).trans ?_
            rw [show δ + ω * -(s - τ) - (δ + ω * s) = ω * (τ - 2 * s) by ring,
              abs_of_nonneg (by nlinarith [hs.1])]
            nlinarith [hs.1]
          have hlow := neg_le_of_abs_le hab2
          have hwa : (sS - s) * a s ≤ sS * amax := by
            apply mul_le_mul (by linarith [hs.1]) ha2 (hamin.le.trans ha1) hsS.le
          have hwa0 : 0 ≤ (sS - s) * a s := mul_nonneg hw (hamin.le.trans ha1)
          rw [hc2]
          nlinarith [mul_le_mul_of_nonneg_left hlow hwa0, mul_le_mul_of_nonneg_left hwa hωτ0'.le]
    have hint1 : ∫ s in Icc 0 sS, q1 s = c1 * ((sS - τ) ^ 2 / 2) := by
      rw [hq1, setIntegral_indicator measurableSet_Icc,
        show Icc 0 sS ∩ Icc τ sS = Icc τ sS by
          rw [Icc_inter_Icc, max_eq_right hτ0.le, min_self],
        integral_const_mul, integral_Icc_eq_integral_Ioc, ← intervalIntegral.integral_of_le hτS,
        intervalIntegral.integral_sub intervalIntegrable_const intervalIntegral.intervalIntegrable_id]
      simp only [intervalIntegral.integral_const, smul_eq_mul, integral_id]
      ring
    have hint2 : ∫ s in Icc 0 sS, q2 s = -c2 * (τ / 2) := by
      rw [hq2, setIntegral_indicator measurableSet_Ico,
        show Icc 0 sS ∩ Ico 0 (τ / 2) = Ico 0 (τ / 2) by
          ext x; simp only [mem_inter_iff, mem_Icc, mem_Ico]
          constructor
          · rintro ⟨⟨h1, _⟩, _, h4⟩; exact ⟨h1, h4⟩
          · rintro ⟨h1, h2⟩; exact ⟨⟨h1, by linarith⟩, h1, h2⟩,
        setIntegral_const, Real.volume_real_Ico_of_le (by linarith), smul_eq_mul]
      ring
    rw [integral_add hq1I hq2I, hint1, hint2] at hq
    have hamaxϑ : amax * ϑ = amin * Real.sin δ / 4 := by rw [hϑ]; field_simp
    have h916 : 9 / 16 ≤ (1 - ϑ) ^ 2 := by nlinarith
    have hτsq : (sS - τ) ^ 2 = sS ^ 2 * (1 - ϑ) ^ 2 := by rw [hτ]; ring
    have hc2τ : c2 * (τ / 2) = ω * τ * (amin * Real.sin δ * sS ^ 2 / 8) := by
      rw [hc2, hτ]
      have : amax * sS * (ϑ * sS / 2) = (amax * ϑ) * sS ^ 2 / 2 := by ring
      calc ω * (ϑ * sS) * amax * sS * (ϑ * sS / 2)
          = ω * (ϑ * sS) * ((amax * ϑ) * sS ^ 2 / 2) := by ring
        _ = _ := by rw [hamaxϑ]; ring
    rw [hτsq, hc1] at hq
    have hpos : 0 ≤ ω * τ * Real.sin δ * amin * sS ^ 2 := by positivity
    nlinarith [mul_le_mul_of_nonneg_left h916 hpos]
  -- (iv) conclusion
  have hkey : ω * τ * (5 / 32 * amin * Real.sin δ * sS ^ 2) - (⟪X, ez⟫ - Z0) ≤ ‖Xh‖ * ‖ch‖ := by
    linarith
  rw [sub_le_iff_le_add, add_div' _ _ _ hωτ0.ne', le_div_iff₀ hωτ0]
  have : ‖Xh‖ * ‖ch‖ ≤ ‖Xh‖ * (ω * τ) := mul_le_mul_of_nonneg_left hchn (norm_nonneg _)
  nlinarith

/-- `‖v‖ ≥ ‖v_h‖` and `‖v‖ ≥ |v_z|`. -/
theorem norm_ge_lateral_vertical (v : E3) :
    ‖v - ⟪v, ez⟫ • ez‖ ≤ ‖v‖ ∧ |⟪v, ez⟫| ≤ ‖v‖ := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hsq : ‖v‖ ^ 2 = ‖v - ⟪v, ez⟫ • ez‖ ^ 2 + ⟪v, ez⟫ ^ 2 := by
    rw [← real_inner_self_eq_norm_sq, ← real_inner_self_eq_norm_sq]
    simp only [inner_sub_left, inner_sub_right, real_inner_smul_left, real_inner_smul_right, hzz,
      real_inner_comm v ez]
    ring
  constructor
  · exact (pow_le_pow_iff_left₀ (norm_nonneg _) (norm_nonneg _) two_ne_zero).mp
      (by nlinarith [sq_nonneg ⟪v, ez⟫])
  · have := abs_real_inner_le_norm v ez; rw [norm_ez, mul_one] at this; exact this

set_option maxHeartbeats 1600000 in
/-- **Theorem B\*, quantitative (math/02 §10.3 Step 7), constant acceleration bounds.**
For `0 < δ ≤ π/4`, `ω s* ≤ δ`, `0 < a_min ≤ a_max`, every boundary datum `θ` of the unconstrained
landing set satisfies `‖Λ(θ) − Λ(θ_m)‖ ≥ η₀`, where `Λ(θ) = r₀ + s* v₀`, `θ_m` is the midpoint of
the two mirror dive-then-brake witnesses, and `η₀ ≥ 0` is any number with
`(1 + c₁) η₀ + √(2 W_b η₀) ≤ γ_X`. -/
theorem lambda_dist_ge {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ η₀ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ4 : δ ≤ π / 4)
    (hωs : ω * sS ≤ δ) (hamin : 0 < amin) (h : amin ≤ amax)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (hη₀ : 0 ≤ η₀)
    (hη₀γ : (1 + 1 / (ω * (amin * Real.sin δ / (4 * amax) * sS))) * η₀ +
      Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) ≤ 5 / 32 * amin * Real.sin δ * sS ^ 2)
    {θ : E3 × E3} (hθ : θ ∈ landingSet Acc tf ω δ (-(g₀ • ez))) :
    η₀ ≤ ‖(θ.1 + sS • θ.2) -
      (((1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (-ex)) tf).1 +
       sS • ((1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (-ex)) tf).2)‖ := by
  set g := -(g₀ • ez) with hgdef
  obtain ⟨a, d, b, ha, hatt, hr, hv⟩ := hθ
  obtain ⟨haI, hab⟩ := hAcc a ha
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hδπ2 : δ + ω * sS ≤ π / 2 := by linarith
  -- Λ identities
  have hfa : IntegrableOn (fun s => a s • d s) (Icc 0 tf) :=
    integrableOn_smul_of_unit haI hatt.d_meas hatt.d_unit
  have hΛ := lambda_identity (sS := sS) hfa hr hv
  have hΛ₁ := lambda_identity (sS := sS) (integrableOn_witness (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) norm_ex inner_ex_ez h) (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hΛ₂ := lambda_identity (sS := sS) (integrableOn_witness (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) (by simp : ‖-ex‖ = 1) (by simp : ⟪-ex, ez⟫ = 0) h)
    (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hWm := witness_W_midpoint (tf := tf) (ω := ω) (δ := δ) (sS := sS) norm_ex inner_ex_ez h
  set W := ∫ s in Icc 0 tf, (s - sS) • (a s • d s) with hW
  set Vs := VStar tf ω δ sS amin amax with hVs
  have hD : (θ.1 + sS • θ.2) -
      (((1 / 2 : ℝ) • landingData g (aW sS amin amax) (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData g (aW sS amin amax) (dW ω δ sS (-ex)) tf).1 +
       sS • ((1 / 2 : ℝ) • landingData g (aW sS amin amax) (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData g (aW sS amin amax) (dW ω δ sS (-ex)) tf).2) = W - Vs • ez := by
    simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd]
    rw [← hWm]
    linear_combination (norm := module) hΛ - (1 / 2 : ℝ) • hΛ₁ - (1 / 2 : ℝ) • hΛ₂
  rw [hD]
  -- split into dive and brake
  have hsub1 : Icc 0 sS ⊆ Icc 0 tf := Icc_subset_Icc_right hsStf.le
  have hsub2 : Ioc sS tf ⊆ Icc 0 tf := Ioc_subset_Icc_self.trans (Icc_subset_Icc_left hsS.le)
  have hdisj : Disjoint (Icc 0 sS) (Ioc sS tf) :=
    Set.disjoint_left.2 fun x h1 h2 => absurd h1.2 (not_le.2 h2.1)
  have hunion : Icc 0 sS ∪ Ioc sS tf = Icc 0 tf := Icc_union_Ioc_eq_Icc hsS.le hsStf.le
  have hfW : IntegrableOn (fun s => (s - sS) • (a s • d s)) (Icc 0 tf) :=
    integrableOn_cont_smul hfa (c := fun s => s - sS) (by fun_prop)
  set Xv := ∫ s in Icc 0 sS, (sS - s) • (a s • d s) with hXv
  set Bv := ∫ s in Ioc sS tf, (s - sS) • (a s • d s) with hBv
  have hWXB : W = Bv - Xv := by
    rw [hW, ← hunion, setIntegral_union hdisj measurableSet_Ioc (hfW.mono_set hsub1)
      (hfW.mono_set hsub2), hXv, hBv]
    have : ∫ s in Icc 0 sS, (s - sS) • (a s • d s) = -∫ s in Icc 0 sS, (sS - s) • (a s • d s) := by
      rw [← integral_neg]
      exact setIntegral_congr_fun measurableSet_Icc fun s _ => by module
    rw [this]; abel
  -- the deficits
  have hmem1 : ∀ s ∈ Icc 0 sS, s ∈ Icc 0 tf := fun s hs => hsub1 hs
  have hmem2 : ∀ s ∈ Ioc sS tf, s ∈ Icc 0 tf := fun s hs => hsub2 hs
  have haS : IntegrableOn a (Icc 0 sS) := haI.mono_set hsub1
  have haB : IntegrableOn a (Ioc sS tf) := haI.mono_set hsub2
  have hIg1 : ∀ g' : ℝ → ℝ, Continuous g' →
      IntegrableOn (fun s => (sS - s) * a s * g' s) (Icc 0 sS) := fun g' hg' =>
    (haS.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => sS - s) (Icc 0 sS))
      isCompact_Icc).mul_continuousOn hg'.continuousOn isCompact_Icc
  have hfX : IntegrableOn (fun s => (sS - s) • (a s • d s)) (Icc 0 sS) :=
    (integrableOn_cont_smul hfa (c := fun s => sS - s) (by fun_prop)).mono_set hsub1
  have hfB : IntegrableOn (fun s => (s - sS) • (a s • d s)) (Ioc sS tf) := hfW.mono_set hsub2
  have hwaB : IntegrableOn (fun s => (s - sS) * a s) (Ioc sS tf) :=
    (haI.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => s - sS) (Icc 0 tf))
      isCompact_Icc).mono_set hsub2
  set Z0 := ∫ s in Icc 0 sS, (sS - s) * a s * Real.cos (δ + ω * s) with hZ0
  set I2 := ∫ s in Icc 0 sS, (sS - s) * amin * Real.cos (δ + ω * s) with hI2
  set J1 := ∫ s in Ioc sS tf, (s - sS) * amax with hJ1
  set J2 := ∫ s in Ioc sS tf, (s - sS) * a s with hJ2
  set J3 := ∫ s in Ioc sS tf, ⟪(s - sS) • (a s • d s), ez⟫ with hJ3
  set ηb := ∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫)) with hηb
  have hcos0 : ∀ s ∈ Icc 0 sS, 0 ≤ Real.cos (δ + ω * s) := fun s hs =>
    Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [hs.1, Real.pi_pos], by nlinarith [hs.2]⟩
  have hZ0I2 : I2 ≤ Z0 := setIntegral_mono_on
    (Continuous.integrableOn_Icc (f := fun s => (sS - s) * amin * Real.cos (δ + ω * s))
      (by fun_prop))
    (hIg1 _ (by fun_prop)) measurableSet_Icc fun s hs => by
      have := (hab s (hmem1 s hs)).1
      have hw : 0 ≤ (sS - s) := by linarith [hs.2]
      nlinarith [mul_le_mul_of_nonneg_left this (mul_nonneg hw (hcos0 s hs))]
  have hJ12 : J2 ≤ J1 := setIntegral_mono_on hwaB
    ((Continuous.integrableOn_Icc (by fun_prop)).mono_set Ioc_subset_Icc_self) measurableSet_Ioc
    fun s hs => mul_le_mul_of_nonneg_left (hab s (hmem2 s hs)).2 (by linarith [hs.1])
  have hηbeq : ηb = J2 - J3 := by
    rw [hηb, hJ2, hJ3, ← integral_sub hwaB (hfB.inner_const ez)]
    exact setIntegral_congr_fun measurableSet_Ioc fun s _ => by
      simp only [real_inner_smul_left]; ring
  have hBz : ⟪Bv, ez⟫ = J3 := by
    rw [hBv, real_inner_comm, ← integral_inner hfB]
    exact setIntegral_congr_fun measurableSet_Ioc fun s _ => real_inner_comm _ _
  have hVsplit : Vs = -I2 + J1 := by
    have hhI : IntegrableOn (hStar ω δ sS amin amax) (Icc 0 tf) :=
      (continuous_hStar ω δ sS amin amax).integrableOn_Icc
    rw [hVs, VStar, ← hunion, setIntegral_union hdisj measurableSet_Ioc (hhI.mono_set hsub1)
      (hhI.mono_set hsub2), hI2, hJ1, ← integral_neg]
    congr 1
    · exact setIntegral_congr_fun measurableSet_Icc fun s hs => by
        simp only [hStar, min_eq_left (by linarith [hs.2] : s - sS ≤ 0),
          max_eq_right (by linarith [hs.2] : s - sS ≤ 0)]; ring
    · exact setIntegral_congr_fun measurableSet_Ioc fun s hs => by
        simp only [hStar, min_eq_right (by linarith [hs.1] : 0 ≤ s - sS),
          max_eq_left (by linarith [hs.1] : 0 ≤ s - sS)]; ring
  have hXz : Z0 ≤ ⟪Xv, ez⟫ := by
    rw [hXv, real_inner_comm, ← integral_inner hfX]
    refine setIntegral_mono_on (hIg1 _ (by fun_prop)) (hfX.const_inner ez) measurableSet_Icc
      fun s hs => ?_
    rw [real_inner_smul_right, real_inner_smul_right, real_inner_comm (d s) ez]
    have hw : 0 ≤ (sS - s) * a s :=
      mul_nonneg (by linarith [hs.2]) (hamin.le.trans (hab s (hmem1 s hs)).1)
    have := hatt.inner_d_ez hω.le hδ.le (hmem1 s hs) (by nlinarith [hs.2, Real.pi_pos])
    nlinarith [mul_le_mul_of_nonneg_left this hw]
  have hηbnn : 0 ≤ ηb := setIntegral_nonneg measurableSet_Ioc fun s hs =>
    mul_nonneg (by linarith [hs.1]) (mul_nonneg (hamin.le.trans (hab s (hmem2 s hs)).1)
      (by linarith [inner_le_one_of_unit (hatt.d_unit s (hmem2 s hs)) norm_ez]))
  set η := Vs - ⟪W, ez⟫ with hη
  set ηd := ⟪Xv, ez⟫ - Z0 with hηd
  have hWz : ⟪W, ez⟫ = J3 - ⟪Xv, ez⟫ := by rw [hWXB, inner_sub_left, hBz]
  have hηsum : ηd + ηb ≤ η := by
    rw [hη, hWz, hVsplit, hηd, hηbeq]; linarith
  have hηd0 : 0 ≤ ηd := by rw [hηd]; linarith
  -- lateral parts
  have hbr := brake_lateral_le (amax := amax) hsS.le hsStf.le haI hatt.d_meas hatt.d_unit
    (fun s hs => hamin.le.trans (hab s hs).1) (fun s hs => (hab s hs).2)
  have hdv := dive_lateral_ge hatt hsS hsStf.le hω hδ hδ4 hωs hamin haI hab
  rw [← hXv, ← hZ0, ← hηd] at hdv
  rw [← hBv, ← hηb] at hbr
  obtain ⟨hlat, hvert⟩ := norm_ge_lateral_vertical (W - Vs • ez)
  have hDz : ⟪W - Vs • ez, ez⟫ = -η := by
    rw [inner_sub_left, real_inner_smul_left, hzz, hη]; ring
  have hDh : (W - Vs • ez) - ⟪W - Vs • ez, ez⟫ • ez =
      (Bv - ⟪Bv, ez⟫ • ez) - (Xv - ⟪Xv, ez⟫ • ez) := by
    rw [hDz, hη, hWXB, inner_sub_left]; module
  rw [hDz, abs_neg] at hvert
  rw [hDh] at hlat
  have htri := norm_sub_norm_le (Xv - ⟪Xv, ez⟫ • ez) (Bv - ⟪Bv, ez⟫ • ez)
  rw [norm_sub_rev (Xv - ⟪Xv, ez⟫ • ez)] at htri
  have hη0' : 0 ≤ η := by linarith
  rcases le_or_gt η₀ η with hcase | hcase
  · calc η₀ ≤ η := hcase
      _ = |η| := (abs_of_nonneg hη0').symm
      _ ≤ _ := hvert
  · -- η < η₀
    set τ := amin * Real.sin δ / (4 * amax) * sS with hτ
    have hsinδ : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ (by linarith [Real.pi_pos])
    have hτ0 : 0 < ω * τ := by have : 0 < amax := hamin.trans_le h; positivity
    have hsq : Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * ηb) ≤
        Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) := by
      apply Real.sqrt_le_sqrt
      have : 0 ≤ 2 * (amax * (tf - sS) ^ 2 / 2) := by
        have : 0 < amax := hamin.trans_le h; positivity
      exact mul_le_mul_of_nonneg_left (by linarith) this
    have hdiv : ηd / (ω * τ) ≤ 1 / (ω * τ) * η₀ := by
      rw [div_eq_mul_one_div, mul_comm]
      exact mul_le_mul_of_nonneg_left (by linarith) (by positivity)
    have : η₀ ≤ 5 / 32 * amin * Real.sin δ * sS ^ 2 - 1 / (ω * τ) * η₀ -
        Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) := by
      rw [hτ]; nlinarith [hη₀γ]
    linarith

/-- An explicit admissible `η₀ > 0` for `lambda_dist_ge`. -/
theorem exists_eta0 {γ c W : ℝ} (hγ : 0 < γ) (hc : 0 ≤ c) (hW : 0 ≤ W) :
    ∃ η₀, 0 < η₀ ∧ (1 + c) * η₀ + Real.sqrt (2 * W * η₀) ≤ γ := by
  refine ⟨min (γ / (2 * (1 + c))) (γ ^ 2 / (8 * (W + 1))), lt_min (by positivity) (by positivity),
    ?_⟩
  set η := min (γ / (2 * (1 + c))) (γ ^ 2 / (8 * (W + 1)))
  have h1 : (1 + c) * η ≤ γ / 2 := by
    have := min_le_left (γ / (2 * (1 + c))) (γ ^ 2 / (8 * (W + 1)))
    calc (1 + c) * η ≤ (1 + c) * (γ / (2 * (1 + c))) := mul_le_mul_of_nonneg_left this (by linarith)
      _ = γ / 2 := by field_simp
  have h2 : Real.sqrt (2 * W * η) ≤ γ / 2 := by
    rw [Real.sqrt_le_left (by positivity)]
    have := min_le_right (γ / (2 * (1 + c))) (γ ^ 2 / (8 * (W + 1)))
    have hη0 : 0 ≤ η := le_min (by positivity) (by positivity)
    calc 2 * W * η ≤ 2 * (W + 1) * (γ ^ 2 / (8 * (W + 1))) :=
          mul_le_mul (by linarith) this hη0 (by positivity)
      _ = (γ / 2) ^ 2 := by field_simp; ring
  linarith

theorem norm_lambda_le {sS : ℝ} (hsS : 0 ≤ sS) (θ θ' : E3 × E3) :
    ‖(θ.1 + sS • θ.2) - (θ'.1 + sS • θ'.2)‖ ≤ (1 + sS) * ‖θ - θ'‖ := by
  have e : (θ.1 + sS • θ.2) - (θ'.1 + sS • θ'.2) = (θ - θ').1 + sS • (θ - θ').2 := by
    simp only [Prod.fst_sub, Prod.snd_sub, smul_sub]; abel
  rw [e]
  calc ‖(θ - θ').1 + sS • (θ - θ').2‖ ≤ ‖(θ - θ').1‖ + ‖sS • (θ - θ').2‖ := norm_add_le _ _
    _ ≤ ‖θ - θ'‖ + sS * ‖θ - θ'‖ := by
        rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg hsS]
        exact add_le_add (norm_fst_le _) (mul_le_mul_of_nonneg_left (norm_snd_le _) hsS)
    _ = (1 + sS) * ‖θ - θ'‖ := by ring

/-- **Quantitative Theorem B\* (distance form).** Under the hypotheses of `lambda_dist_ge`, every
point of the unconstrained landing set (hence of every state-constrained one) is at distance at
least `η₀/(1 + s*)` from the witness midpoint `θ_m` (product max-norm on `ℝ³ × ℝ³`); in particular
there is a ball around `θ_m` disjoint from the landing set. -/
theorem landingSet_dist_ge {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ η₀ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ4 : δ ≤ π / 4)
    (hωs : ω * sS ≤ δ) (hamin : 0 < amin) (h : amin ≤ amax)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (hη₀ : 0 ≤ η₀)
    (hη₀γ : (1 + 1 / (ω * (amin * Real.sin δ / (4 * amax) * sS))) * η₀ +
      Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) ≤ 5 / 32 * amin * Real.sin δ * sS ^ 2)
    {θ : E3 × E3} (hθ : θ ∈ landingSet Acc tf ω δ (-(g₀ • ez))) :
    η₀ / (1 + sS) ≤ ‖θ - ((1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (-ex)) tf)‖ := by
  rw [div_le_iff₀ (by linarith), mul_comm]
  exact (lambda_dist_ge hsS hsStf hω hδ hδ4 hωs hamin h hAcc hη₀ hη₀γ hθ).trans
    (norm_lambda_le hsS.le _ _)

/-- The midpoint has a neighbourhood free of landing data: `θ_m ∉ closure F`. -/
theorem midpoint_not_mem_closure_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ4 : δ ≤ π / 4)
    (hωs : ω * sS ≤ δ) (hamin : 0 < amin) (h : amin ≤ amax)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax) :
    ((1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS ex) tf +
      (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (-ex)) tf) ∉
      closure (landingSet Acc tf ω δ (-(g₀ • ez))) := by
  have hsinδ : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ (by linarith [Real.pi_pos])
  have hamax : 0 < amax := hamin.trans_le h
  obtain ⟨η₀, hη₀, hγ⟩ := exists_eta0 (γ := 5 / 32 * amin * Real.sin δ * sS ^ 2)
    (c := 1 / (ω * (amin * Real.sin δ / (4 * amax) * sS)))
    (W := amax * (tf - sS) ^ 2 / 2) (by positivity) (by positivity) (by positivity)
  rw [Metric.mem_closure_iff]
  push_neg
  refine ⟨η₀ / (1 + sS), by positivity, fun θ hθ => ?_⟩
  rw [dist_comm, dist_eq_norm]
  exact landingSet_dist_ge hsS hsStf hω hδ hδ4 hωs hamin h hAcc hη₀.le hγ hθ

end LcvxObstruction
