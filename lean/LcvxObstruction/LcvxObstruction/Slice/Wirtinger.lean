import LcvxObstruction.Slice.Affine

/-!
# Lemma W: Wirtinger's inequality modulo affine functions (math/07 §2, blueprint SW2–SW3)

* `periodic_wirtinger` (SW2): for `h` absolutely continuous on `[0,T]` with `h 0 = h T`,
  `∫ h = 0` and `h' ∈ L²`: `∫ h² ≤ (T/2π)² ∫ h'²`. Proof: Parseval on `AddCircle T`
  (`hasSum_sq_fourierCoeffOn`) and integration by parts for absolutely continuous functions
  (`AbsolutelyContinuousOnInterval.integral_mul_deriv_eq_deriv_mul`).
* `wirtinger_scalar` (SW3, scalar): for `g` absolutely continuous on `[0,T]` with `g' ∈ L²`:
  `‖P^⊥ g‖² ≤ (T/2π)² ∫ g'²`, where `P` is the `L²` projection onto affine functions (`fit`).
* `wirtinger_lipschitz` (Corollary W, any finite dimension): if `β : ℝ → ℝⁿ` (Euclidean) is
  `ω`-Lipschitz on `[0,T]`, then `‖P^⊥ β‖² ≤ (T/2π)² ω² T`. The proof is componentwise, so it
  is insensitive to the dimension of the range (planar S-turns, coning, `ℝ^N`-lifted paths).

Regularity is stated honestly: absolute continuity (with square-integrable a.e. derivative)
for the scalar lemma, Lipschitz for the vector corollary (which is what the slew-rate limit
gives).
-/

open MeasureTheory Set Real Filter Topology
open scoped RealInnerProductSpace

noncomputable section

namespace LcvxObstruction.Slice

/-! ### Fourier coefficients of real functions -/

theorem fourier_neg_coe (T : ℝ) (n : ℤ) (x : ℝ) :
    fourier (-n) (x : AddCircle T) =
      ((Real.cos (2 * π * n * x / T) : ℝ) : ℂ) -
        ((Real.sin (2 * π * n * x / T) : ℝ) : ℂ) * Complex.I := by
  rw [fourier_coe_apply]
  have : 2 * (π : ℂ) * Complex.I * ((-n : ℤ) : ℂ) * (x : ℂ) / (T : ℂ) =
      ((-(2 * π * n * x / T) : ℝ) : ℂ) * Complex.I := by
    push_cast; ring
  rw [this, Complex.exp_mul_I, ← Complex.ofReal_cos, ← Complex.ofReal_sin, Real.cos_neg,
    Real.sin_neg]
  push_cast; ring

theorem IntervalIntegrable.ofReal' {f : ℝ → ℝ} {a b : ℝ} (hf : IntervalIntegrable f volume a b) :
    IntervalIntegrable (fun x => (f x : ℂ)) volume a b :=
  ⟨hf.1.ofReal, hf.2.ofReal⟩

/-- `|f̂(n)|² = (A² + B²)/T²` with `A = ∫ cos(2πnx/T) f`, `B = ∫ sin(2πnx/T) f`. -/
theorem norm_sq_fourierCoeffOn_ofReal {T : ℝ} (hT : 0 < T) {f : ℝ → ℝ}
    (hf : IntervalIntegrable f volume 0 T) (n : ℤ) :
    ‖fourierCoeffOn hT (fun x => (f x : ℂ)) n‖ ^ 2 =
      ((∫ x in (0 : ℝ)..T, Real.cos (2 * π * n * x / T) * f x) ^ 2 +
        (∫ x in (0 : ℝ)..T, Real.sin (2 * π * n * x / T) * f x) ^ 2) / T ^ 2 := by
  rw [fourierCoeffOn_eq_integral]
  set A := ∫ x in (0 : ℝ)..T, Real.cos (2 * π * n * x / T) * f x
  set B := ∫ x in (0 : ℝ)..T, Real.sin (2 * π * n * x / T) * f x
  have hA : IntervalIntegrable (fun x => Real.cos (2 * π * n * x / T) * f x) volume 0 T :=
    hf.continuousOn_mul (by fun_prop)
  have hB : IntervalIntegrable (fun x => Real.sin (2 * π * n * x / T) * f x) volume 0 T :=
    hf.continuousOn_mul (by fun_prop)
  have hpt : ∀ x : ℝ, fourier (-n) (x : AddCircle (T - 0)) • (f x : ℂ) =
      ((Real.cos (2 * π * n * x / T) * f x : ℝ) : ℂ) -
        ((Real.sin (2 * π * n * x / T) * f x : ℝ) : ℂ) * Complex.I := by
    intro x
    rw [fourier_neg_coe, sub_zero, smul_eq_mul]
    push_cast; ring
  have hint : ∫ x in (0 : ℝ)..T, fourier (-n) (x : AddCircle (T - 0)) • (f x : ℂ) =
      (A : ℂ) - (B : ℂ) * Complex.I := by
    simp_rw [hpt]
    rw [intervalIntegral.integral_sub (IntervalIntegrable.ofReal' hA)
      ((IntervalIntegrable.ofReal' hB).mul_const _),
      intervalIntegral.integral_mul_const, intervalIntegral.integral_ofReal,
      intervalIntegral.integral_ofReal]
  rw [hint, sub_zero, norm_smul, mul_pow, sub_eq_add_neg, ← neg_mul, ← Complex.ofReal_neg,
    Complex.norm_add_mul_I]
  rw [Real.sq_sqrt (by positivity), norm_div, norm_one, Real.norm_eq_abs, abs_of_pos hT]
  field_simp

/-! ### Integration by parts against `cos`, `sin` -/

theorem cos_mul_ac (k T : ℝ) : AbsolutelyContinuousOnInterval (fun x => Real.cos (k * x)) 0 T :=
  ContDiffOn.absolutelyContinuousOnInterval
    ((Real.contDiff_cos.comp (contDiff_const.mul contDiff_id)).contDiffOn)

theorem sin_mul_ac (k T : ℝ) : AbsolutelyContinuousOnInterval (fun x => Real.sin (k * x)) 0 T :=
  ContDiffOn.absolutelyContinuousOnInterval
    ((Real.contDiff_sin.comp (contDiff_const.mul contDiff_id)).contDiffOn)

theorem deriv_cos_mul (k x : ℝ) : deriv (fun x => Real.cos (k * x)) x = -Real.sin (k * x) * k := by
  have := ((hasDerivAt_id x).const_mul k).cos
  simp only [id, mul_one] at this
  exact this.deriv

theorem deriv_sin_mul (k x : ℝ) : deriv (fun x => Real.sin (k * x)) x = Real.cos (k * x) * k := by
  have := ((hasDerivAt_id x).const_mul k).sin
  simp only [id, mul_one] at this
  exact this.deriv

theorem sin_int_mul_two_pi' (n : ℤ) : Real.sin (n * (2 * π)) = 0 := by
  rw [show (n : ℝ) * (2 * π) = ((2 * n : ℤ) : ℝ) * π by push_cast; ring]
  exact Real.sin_int_mul_pi _

theorem cos_ibp {T : ℝ} (hT : 0 < T) {h : ℝ → ℝ} (hac : AbsolutelyContinuousOnInterval h 0 T)
    (hper : h 0 = h T) (n : ℤ) :
    ∫ x in (0 : ℝ)..T, Real.cos (2 * π * n * x / T) * deriv h x =
      (2 * π * n / T) * ∫ x in (0 : ℝ)..T, Real.sin (2 * π * n * x / T) * h x := by
  set k := 2 * π * n / T with hk
  have hkx : ∀ x : ℝ, 2 * π * n * x / T = k * x := by intro x; rw [hk]; ring
  simp_rw [hkx]
  rw [(cos_mul_ac k T).integral_mul_deriv_eq_deriv_mul hac]
  simp_rw [deriv_cos_mul]
  have hkT : k * T = n * (2 * π) := by rw [hk, div_mul_cancel₀ _ hT.ne']; ring
  rw [hkT, Real.cos_int_mul_two_pi, mul_zero, Real.cos_zero, hper]
  have : (fun x => -Real.sin (k * x) * k * h x) = fun x => -(k * (Real.sin (k * x) * h x)) := by
    ext x; ring
  rw [this, intervalIntegral.integral_neg, intervalIntegral.integral_const_mul]
  ring

theorem sin_ibp {T : ℝ} (hT : 0 < T) {h : ℝ → ℝ} (hac : AbsolutelyContinuousOnInterval h 0 T)
    (n : ℤ) :
    ∫ x in (0 : ℝ)..T, Real.sin (2 * π * n * x / T) * deriv h x =
      -((2 * π * n / T) * ∫ x in (0 : ℝ)..T, Real.cos (2 * π * n * x / T) * h x) := by
  set k := 2 * π * n / T with hk
  have hkx : ∀ x : ℝ, 2 * π * n * x / T = k * x := by intro x; rw [hk]; ring
  simp_rw [hkx]
  rw [(sin_mul_ac k T).integral_mul_deriv_eq_deriv_mul hac]
  simp_rw [deriv_sin_mul]
  have hkT : k * T = n * (2 * π) := by rw [hk, div_mul_cancel₀ _ hT.ne']; ring
  rw [hkT, sin_int_mul_two_pi', mul_zero, Real.sin_zero]
  have : (fun x => Real.cos (k * x) * k * h x) = fun x => k * (Real.cos (k * x) * h x) := by
    ext x; ring
  rw [this, intervalIntegral.integral_const_mul]
  ring

/-! ### SW2: periodic Wirtinger -/

/-- **Periodic Wirtinger inequality (SW2).** -/
theorem periodic_wirtinger {T : ℝ} (hT : 0 < T) {h : ℝ → ℝ}
    (hac : AbsolutelyContinuousOnInterval h 0 T) (hper : h 0 = h T)
    (hmean : ∫ x in (0 : ℝ)..T, h x = 0)
    (hd : IntervalIntegrable (fun x => deriv h x ^ 2) volume 0 T) :
    ∫ x in (0 : ℝ)..T, h x ^ 2 ≤ (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv h x ^ 2 := by
  have hcont : ContinuousOn h (Icc 0 T) := by
    simpa [uIcc_of_le hT.le] using hac.continuousOn
  have hhi : IntervalIntegrable h volume 0 T := hcont.intervalIntegrable_of_Icc hT.le
  have hdi : IntervalIntegrable (deriv h) volume 0 T := hac.intervalIntegrable_deriv
  have hL2 : MemLp (fun x => (h x : ℂ)) 2 (volume.restrict (Ioc 0 T)) := by
    rw [memLp_two_iff_integrable_sq_norm]
    · simp only [Complex.norm_real, Real.norm_eq_abs, sq_abs]
      exact ((hcont.pow 2).integrableOn_Icc).mono_set Ioc_subset_Icc_self
    · exact ((Complex.continuous_ofReal.comp_continuousOn hcont).mono
        Ioc_subset_Icc_self).aestronglyMeasurable measurableSet_Ioc
  have hL2' : MemLp (fun x => ((deriv h x : ℝ) : ℂ)) 2 (volume.restrict (Ioc 0 T)) := by
    rw [memLp_two_iff_integrable_sq_norm]
    · simp only [Complex.norm_real, Real.norm_eq_abs, sq_abs]
      exact (intervalIntegrable_iff_integrableOn_Ioc_of_le hT.le).mp hd
    · have hmd : Measurable (deriv h) := measurable_deriv h
      exact (Complex.measurable_ofReal.comp hmd).aestronglyMeasurable
  have P1 := hasSum_sq_fourierCoeffOn hT hL2
  have P2 := hasSum_sq_fourierCoeffOn hT hL2'
  simp only [Complex.norm_real, Real.norm_eq_abs, sq_abs, sub_zero, smul_eq_mul] at P1 P2
  have hterm : ∀ n : ℤ, ‖fourierCoeffOn hT (fun x => (h x : ℂ)) n‖ ^ 2 ≤
      (T / (2 * π)) ^ 2 * ‖fourierCoeffOn hT (fun x => ((deriv h x : ℝ) : ℂ)) n‖ ^ 2 := by
    intro n
    rw [norm_sq_fourierCoeffOn_ofReal hT hhi, norm_sq_fourierCoeffOn_ofReal hT hdi]
    rcases eq_or_ne n 0 with rfl | hn
    · have h0 : ((∫ x in (0 : ℝ)..T, Real.cos (2 * π * ((0 : ℤ) : ℝ) * x / T) * h x) ^ 2 +
          (∫ x in (0 : ℝ)..T, Real.sin (2 * π * ((0 : ℤ) : ℝ) * x / T) * h x) ^ 2) / T ^ 2 = 0 := by
        simp [hmean]
      rw [h0]; positivity
    · rw [cos_ibp hT hac hper n, sin_ibp hT hac n]
      set A := ∫ x in (0 : ℝ)..T, Real.cos (2 * π * n * x / T) * h x
      set B := ∫ x in (0 : ℝ)..T, Real.sin (2 * π * n * x / T) * h x
      have hn1 : (1 : ℝ) ≤ (n : ℝ) ^ 2 := by
        have : (1 : ℤ) ≤ n ^ 2 := by
          have := Int.one_le_abs hn; nlinarith [sq_abs n]
        exact_mod_cast this
      have e : (T / (2 * π)) ^ 2 * ((((2 * π * n / T) * B) ^ 2 +
          (-((2 * π * n / T) * A)) ^ 2) / T ^ 2) = (n : ℝ) ^ 2 * ((A ^ 2 + B ^ 2) / T ^ 2) := by
        field_simp
        ring
      rw [e]
      have : 0 ≤ (A ^ 2 + B ^ 2) / T ^ 2 := by positivity
      nlinarith
  have hle := hasSum_le hterm P1 (P2.mul_left ((T / (2 * π)) ^ 2))
  have hT' := hT.ne'
  calc ∫ x in (0 : ℝ)..T, h x ^ 2 = T * (T⁻¹ * ∫ x in (0 : ℝ)..T, h x ^ 2) := by
        rw [← mul_assoc, mul_inv_cancel₀ hT', one_mul]
    _ ≤ T * ((T / (2 * π)) ^ 2 * (T⁻¹ * ∫ x in (0 : ℝ)..T, deriv h x ^ 2)) :=
        mul_le_mul_of_nonneg_left hle hT.le
    _ = (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv h x ^ 2 := by
        rw [mul_left_comm, ← mul_assoc T, mul_inv_cancel₀ hT', one_mul]

/-! ### SW3: Wirtinger modulo affine functions, scalar -/

theorem affine_ac (c s T : ℝ) : AbsolutelyContinuousOnInterval (fun x => c + x * s) 0 T :=
  ContDiffOn.absolutelyContinuousOnInterval (by fun_prop)

/-- **Lemma W, scalar form (SW3).** For `g` absolutely continuous on `[0,T]` with square
integrable derivative: `‖g - P g‖² ≤ (T/2π)² ∫ g'²`. -/
theorem wirtinger_scalar {T : ℝ} (hT : 0 < T) {g : ℝ → ℝ}
    (hac : AbsolutelyContinuousOnInterval g 0 T)
    (hd : IntervalIntegrable (fun x => deriv g x ^ 2) volume 0 T) :
    L2 T (fun x => g x - fit T g x) ≤ (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv g x ^ 2 := by
  have hT' := hT.ne'
  have hcont : ContinuousOn g (Icc 0 T) := by
    simpa [uIcc_of_le hT.le] using hac.continuousOn
  have hgi : IntervalIntegrable g volume 0 T := hcont.intervalIntegrable_of_Icc hT.le
  have hdi : IntervalIntegrable (deriv g) volume 0 T := hac.intervalIntegrable_deriv
  set s := (g T - g 0) / T with hs
  set c := T⁻¹ * ∫ x in (0 : ℝ)..T, (g x - x * s) with hc
  set h : ℝ → ℝ := fun x => g x - (c + x * s) with hh
  have hhac : AbsolutelyContinuousOnInterval h 0 T := hac.sub (affine_ac c s T)
  have hper : h 0 = h T := by
    simp only [hh, hs]; field_simp <;> ring
  have hlin : IntervalIntegrable (fun x : ℝ => x * s) volume 0 T :=
    (continuous_id.mul continuous_const).intervalIntegrable _ _
  have hmean : ∫ x in (0 : ℝ)..T, h x = 0 := by
    have e : h = fun x => (g x - x * s) - c := by ext x; simp only [hh]; ring
    rw [e, intervalIntegral.integral_sub (hgi.sub hlin) intervalIntegrable_const,
      intervalIntegral.integral_const, hc, sub_zero, smul_eq_mul, ← mul_assoc,
      mul_inv_cancel₀ hT', one_mul, sub_self]
  -- a.e. derivative of `h`
  have hderiv : ∀ᵐ x, x ∈ uIoc 0 T → deriv h x = deriv g x - s := by
    filter_upwards [hac.ae_differentiableAt] with x hx hxI
    have hgx := (hx (uIoc_subset_uIcc hxI)).hasDerivAt
    have : HasDerivAt h (deriv g x - (0 + 1 * s)) x :=
      hgx.sub ((hasDerivAt_const x c).add ((hasDerivAt_id x).mul_const s))
    rw [this.deriv]; ring
  have hd2 : IntervalIntegrable (fun x => (deriv g x - s) ^ 2) volume 0 T := by
    have e : (fun x => (deriv g x - s) ^ 2) =
        fun x => deriv g x ^ 2 - (2 * s) * deriv g x + s ^ 2 := by ext x; ring
    rw [e]
    exact (hd.sub (hdi.const_mul _)).add intervalIntegrable_const
  have hdh : IntervalIntegrable (fun x => deriv h x ^ 2) volume 0 T := by
    refine hd2.congr_ae ?_
    rw [Filter.EventuallyEq, ae_restrict_iff' measurableSet_uIoc]
    filter_upwards [hderiv] with x hx hxI
    rw [hx hxI]
  have hW := periodic_wirtinger hT hhac hper hmean hdh
  have hint : ∫ x in (0 : ℝ)..T, deriv h x ^ 2 = ∫ x in (0 : ℝ)..T, (deriv g x - s) ^ 2 := by
    refine intervalIntegral.integral_congr_ae ?_
    filter_upwards [hderiv] with x hx hxI
    rw [hx hxI]
  have hexp : ∫ x in (0 : ℝ)..T, (deriv g x - s) ^ 2 =
      (∫ x in (0 : ℝ)..T, deriv g x ^ 2) - s ^ 2 * T := by
    have e : (fun x => (deriv g x - s) ^ 2) =
        fun x => deriv g x ^ 2 - (2 * s) * deriv g x + s ^ 2 := by ext x; ring
    rw [e, intervalIntegral.integral_add (hd.sub (hdi.const_mul _)) intervalIntegrable_const,
      intervalIntegral.integral_sub hd (hdi.const_mul _), intervalIntegral.integral_const_mul,
      hac.integral_deriv_eq_sub, intervalIntegral.integral_const, smul_eq_mul, hs]
    field_simp <;> ring
  -- compare with the best affine approximation
  have hBM : BM T g := BM.of_continuousOn hcont
  have hfit := L2_sub_fit_le hT hBM c s
  have hL2h : L2 T (fun x => g x - affLine c s x) = ∫ x in (0 : ℝ)..T, h x ^ 2 := by
    rw [L2, setIntegral_Icc_eq_intervalIntegral hT.le]
    congr 1; ext x
    simp only [affLine, smul_eq_mul, Real.norm_eq_abs, sq_abs, hh]
  rw [hL2h] at hfit
  calc L2 T (fun x => g x - fit T g x) ≤ ∫ x in (0 : ℝ)..T, h x ^ 2 := hfit
    _ ≤ (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv h x ^ 2 := hW
    _ = (T / (2 * π)) ^ 2 * ((∫ x in (0 : ℝ)..T, deriv g x ^ 2) - s ^ 2 * T) := by
        rw [hint, hexp]
    _ ≤ (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv g x ^ 2 := by
        apply mul_le_mul_of_nonneg_left _ (by positivity)
        nlinarith [sq_nonneg s]

/-! ### Corollary W: Lipschitz paths in any finite dimension -/

section Vector

variable {ι : Type*} [Fintype ι]

/-- Coordinates commute with the affine projection. -/
theorem fit_apply {T : ℝ} {β : ℝ → EuclideanSpace ℝ ι} (hβ : BM T β) (i : ι) (x : ℝ) :
    fit T β x i = fit T (fun y => β y i) x := by
  have h0 : mom0 T β i = mom0 T (fun y => β y i) := by
    have := (EuclideanSpace.proj (𝕜 := ℝ) i).integral_comp_comm hβ.integrableOn
    simpa [mom0] using this.symm
  have h1 : mom1 T β i = mom1 T (fun y => β y i) := by
    have := (EuclideanSpace.proj (𝕜 := ℝ) i).integral_comp_comm hβ.smul_id.integrableOn
    simpa [mom1] using this.symm
  simp only [fit, affLine, fitC0, fitC1, PiLp.add_apply, PiLp.smul_apply, PiLp.sub_apply,
    smul_eq_mul, h0, h1]

/-- **Corollary W.** If `β : ℝ → ℝⁿ` is `ω`-Lipschitz on `[0,T]`, then
`‖P^⊥ β‖² ≤ (T/2π)² ω² T`, whatever the dimension of the range. -/
theorem wirtinger_lipschitz {T ω : ℝ} (hT : 0 < T) (hω : 0 ≤ ω) {β : ℝ → EuclideanSpace ℝ ι}
    (hβ : ∀ x ∈ Icc 0 T, ∀ y ∈ Icc 0 T, ‖β x - β y‖ ≤ ω * |x - y|) :
    L2 T (fun x => β x - fit T β x) ≤ (T / (2 * π)) ^ 2 * (ω ^ 2 * T) := by
  set K : NNReal := ⟨ω, hω⟩
  have hlip : LipschitzOnWith K β (Icc 0 T) :=
    LipschitzOnWith.of_dist_le_mul fun x hx y hy => by
      rw [dist_eq_norm, Real.dist_eq]; exact hβ x hx y hy
  have hBM : BM T β := BM.of_continuousOn hlip.continuousOn
  have hcomp : ∀ i, LipschitzOnWith K (fun y => β y i) (uIcc 0 T) := by
    intro i
    rw [uIcc_of_le hT.le]
    refine LipschitzOnWith.of_dist_le_mul fun x hx y hy => ?_
    rw [Real.dist_eq, Real.dist_eq]
    calc |β x i - β y i| = ‖(β x - β y) i‖ := by rw [PiLp.sub_apply, Real.norm_eq_abs]
      _ ≤ ‖β x - β y‖ := PiLp.norm_apply_le _ _
      _ ≤ ω * |x - y| := hβ x hx y hy
  have hac : ∀ i, AbsolutelyContinuousOnInterval (fun y => β y i) 0 T := fun i =>
    (hcomp i).absolutelyContinuousOnInterval
  -- a.e. bound on the sum of squared derivatives
  have hbound : ∀ᵐ x, x ∈ Ioc 0 T → ∑ i, deriv (fun y => β y i) x ^ 2 ≤ ω ^ 2 := by
    have hall : ∀ᵐ x, ∀ i, x ∈ uIcc 0 T → DifferentiableAt ℝ (fun y => β y i) x :=
      ae_all_iff.mpr fun i => (hac i).ae_differentiableAt
    have hne : ∀ᵐ x : ℝ, x ≠ T := by rw [ae_iff]; simp
    filter_upwards [hall, hne] with x hx hxT hxI
    have hxIoo : x ∈ Ioo 0 T := ⟨hxI.1, lt_of_le_of_ne hxI.2 hxT⟩
    have hxIcc : x ∈ uIcc 0 T := by rw [uIcc_of_le hT.le]; exact Ioo_subset_Icc_self hxIoo
    have htend : Tendsto (fun y => ∑ i, (slope (fun y => β y i) x y) ^ 2) (𝓝[≠] x)
        (𝓝 (∑ i, deriv (fun y => β y i) x ^ 2)) := by
      refine tendsto_finsetSum _ fun i _ => ?_
      exact (hasDerivAt_iff_tendsto_slope.mp (hx i hxIcc).hasDerivAt).pow 2
    refine le_of_tendsto htend ?_
    have hnhds : Icc 0 T ∈ 𝓝[≠] x := nhdsWithin_le_nhds (Icc_mem_nhds hxIoo.1 hxIoo.2)
    filter_upwards [hnhds, self_mem_nhdsWithin] with y hy hyx
    have hyx' : y - x ≠ 0 := sub_ne_zero.mpr hyx
    have hsum : ∑ i, (slope (fun y => β y i) x y) ^ 2 = ‖β y - β x‖ ^ 2 / (y - x) ^ 2 := by
      rw [EuclideanSpace.norm_sq_eq, Finset.sum_div]
      refine Finset.sum_congr rfl fun i _ => ?_
      rw [slope_def_field, PiLp.sub_apply, Real.norm_eq_abs, sq_abs, div_pow]
    rw [hsum, div_le_iff₀ (lt_of_le_of_ne (sq_nonneg _) (Ne.symm (pow_ne_zero 2 hyx')))]
    have h1 := hβ y hy x (Ioo_subset_Icc_self hxIoo)
    have h2 : ‖β y - β x‖ ^ 2 ≤ (ω * |y - x|) ^ 2 := pow_le_pow_left₀ (norm_nonneg _) h1 2
    rw [mul_pow, sq_abs] at h2
    exact h2
  have hmeas : ∀ i, AEStronglyMeasurable (fun x => deriv (fun y => β y i) x ^ 2)
      (volume.restrict (Ioc 0 T)) := fun i =>
    ((measurable_deriv _).pow_const 2).aestronglyMeasurable
  have hdi : ∀ i, IntervalIntegrable (fun x => deriv (fun y => β y i) x ^ 2) volume 0 T := by
    intro i
    rw [intervalIntegrable_iff_integrableOn_Ioc_of_le hT.le]
    refine Integrable.mono' (g := fun _ => ω ^ 2) (integrableOn_const (by simp [Real.volume_Ioc])) (hmeas i) ?_
    rw [ae_restrict_iff' measurableSet_Ioc]
    filter_upwards [hbound] with x hx hxI
    rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
    refine le_trans ?_ (hx hxI)
    exact Finset.single_le_sum (f := fun i => deriv (fun y => β y i) x ^ 2)
      (fun j _ => sq_nonneg _) (Finset.mem_univ i)
  -- split the norm into coordinates
  have hsplit : L2 T (fun x => β x - fit T β x) =
      ∑ i, L2 T (fun x => β x i - fit T (fun y => β y i) x) := by
    simp only [L2]
    rw [← integral_finsetSum]
    · refine setIntegral_congr_fun measurableSet_Icc fun x _ => ?_
      rw [EuclideanSpace.norm_sq_eq]
      refine Finset.sum_congr rfl fun i _ => ?_
      rw [PiLp.sub_apply, fit_apply hBM]
    · intro i _
      have hBi : BM T (fun y => β y i) := hBM.clm (EuclideanSpace.proj (𝕜 := ℝ) i)
      exact (hBi.sub (BM.fit _)).integrableOn_normSq
  have hsumint : ∑ i, ∫ x in (0 : ℝ)..T, deriv (fun y => β y i) x ^ 2 ≤ ω ^ 2 * T := by
    rw [← intervalIntegral.integral_finsetSum fun i _ => hdi i,
      intervalIntegral.integral_of_le hT.le]
    have hint : IntegrableOn (fun x => ∑ i, deriv (fun y => β y i) x ^ 2) (Ioc 0 T) :=
      integrable_finsetSum _ fun i _ =>
        (intervalIntegrable_iff_integrableOn_Ioc_of_le hT.le).mp (hdi i)
    calc ∫ x in Ioc 0 T, ∑ i, deriv (fun y => β y i) x ^ 2 ≤ ∫ x in Ioc 0 T, ω ^ 2 :=
          setIntegral_mono_ae_restrict hint (integrableOn_const (by simp [Real.volume_Ioc]))
            ((ae_restrict_iff' measurableSet_Ioc).mpr hbound)
      _ = ω ^ 2 * T := by
          rw [setIntegral_const, Real.volume_real_Ioc_of_le hT.le, smul_eq_mul]; ring
  rw [hsplit]
  calc ∑ i, L2 T (fun x => β x i - fit T (fun y => β y i) x)
      ≤ ∑ i, (T / (2 * π)) ^ 2 * ∫ x in (0 : ℝ)..T, deriv (fun y => β y i) x ^ 2 :=
        Finset.sum_le_sum fun i _ => wirtinger_scalar hT (hac i) (hdi i)
    _ = (T / (2 * π)) ^ 2 * ∑ i, ∫ x in (0 : ℝ)..T, deriv (fun y => β y i) x ^ 2 := by
        rw [Finset.mul_sum]
    _ ≤ (T / (2 * π)) ^ 2 * (ω ^ 2 * T) :=
        mul_le_mul_of_nonneg_left hsumint (by positivity)

end Vector

end LcvxObstruction.Slice
