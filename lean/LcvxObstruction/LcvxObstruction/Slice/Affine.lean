import Mathlib

/-!
# L² geometry of affine functions on `[0, T]` (blueprint SW1)

Everything is stated for functions `f : ℝ → E` (`E` a real inner product space) and Lebesgue
integrals over `Icc 0 T`, which is the convention of `Model.lean`.

* `BM T f`: `f` is a.e.-strongly measurable and bounded on `[0,T]` (the standing regularity
  class; every function in the slice argument is of this kind).
* `mom0 T f = ∫ f`, `mom1 T f = ∫ s • f s` (the two lateral moments of math/07 §1).
* `fit T f`: the affine function `c₀ + s • c₁` with the same two moments as `f`; it is the
  `L²((0,T); E)` orthogonal projection `P f` of math/07 (`L2_sub_affLine`, `L2_sub_fit_le`).
* `L2 T f = ∫ ‖f‖²` (the squared `L²` norm).
* `L2_eq_add_fit`: Pythagoras `‖f‖² = ‖P^⊥ f‖² + ‖P f‖²`.
* `L2_fit_of_mom0_eq_zero`: `‖π_{(0,q)}‖² = 12 ‖q‖² / T³`.
* `L2_add_le`: Minkowski in the form needed (`‖u + w‖ ≤ X + Y`).
-/

open MeasureTheory Set Real
open scoped RealInnerProductSpace

noncomputable section

namespace LcvxObstruction.Slice

theorem setIntegral_Icc_eq_intervalIntegral {F : Type*} [NormedAddCommGroup F] [NormedSpace ℝ F]
    {T : ℝ} (hT : 0 ≤ T) (f : ℝ → F) :
    ∫ x in Icc 0 T, f x = ∫ x in (0 : ℝ)..T, f x := by
  rw [integral_Icc_eq_integral_Ioc, intervalIntegral.integral_of_le hT]

/-! ### Bounded measurable functions on `[0,T]` -/

/-- `f` is a.e.-strongly measurable and bounded on `[0,T]`. -/
structure BM {F : Type*} [NormedAddCommGroup F] (T : ℝ) (f : ℝ → F) : Prop where
  meas : AEStronglyMeasurable f (volume.restrict (Icc 0 T))
  bdd : ∃ C, ∀ x ∈ Icc 0 T, ‖f x‖ ≤ C

section BMlemmas

variable {F G : Type*} [NormedAddCommGroup F] [NormedAddCommGroup G] {T : ℝ}

theorem BM.integrableOn {f : ℝ → F} (h : BM T f) : IntegrableOn f (Icc 0 T) := by
  obtain ⟨C, hC⟩ := h.bdd
  refine Integrable.mono' (g := fun _ => C) (integrableOn_const (by simp [Real.volume_Icc])) h.meas ?_
  exact ae_restrict_of_forall_mem measurableSet_Icc hC

theorem BM.of_continuousOn {f : ℝ → F} (h : ContinuousOn f (Icc 0 T)) : BM T f := by
  refine ⟨h.aestronglyMeasurable measurableSet_Icc, ?_⟩
  obtain ⟨C, hC⟩ := isCompact_Icc.exists_bound_of_continuousOn h
  exact ⟨C, hC⟩

theorem BM.of_continuous {f : ℝ → F} (h : Continuous f) : BM T f :=
  BM.of_continuousOn h.continuousOn

theorem BM.const (c : F) : BM T (fun _ => c) := BM.of_continuous continuous_const

theorem BM.add {f g : ℝ → F} (hf : BM T f) (hg : BM T g) : BM T (fun x => f x + g x) := by
  obtain ⟨C₁, h₁⟩ := hf.bdd
  obtain ⟨C₂, h₂⟩ := hg.bdd
  exact ⟨hf.meas.add hg.meas, C₁ + C₂, fun x hx =>
    (norm_add_le _ _).trans (add_le_add (h₁ x hx) (h₂ x hx))⟩

theorem BM.neg {f : ℝ → F} (hf : BM T f) : BM T (fun x => -f x) := by
  obtain ⟨C, h⟩ := hf.bdd
  exact ⟨hf.meas.neg, C, fun x hx => by rw [norm_neg]; exact h x hx⟩

theorem BM.sub {f g : ℝ → F} (hf : BM T f) (hg : BM T g) : BM T (fun x => f x - g x) := by
  simpa [sub_eq_add_neg] using hf.add hg.neg

theorem BM.smul [NormedSpace ℝ F] {g : ℝ → ℝ} {f : ℝ → F} (hg : BM T g) (hf : BM T f) :
    BM T (fun x => g x • f x) := by
  obtain ⟨C₁, h₁⟩ := hg.bdd
  obtain ⟨C₂, h₂⟩ := hf.bdd
  refine ⟨hg.meas.smul hf.meas, C₁ * C₂, fun x hx => ?_⟩
  rw [norm_smul]
  exact mul_le_mul (h₁ x hx) (h₂ x hx) (norm_nonneg _) ((norm_nonneg _).trans (h₁ x hx))

theorem BM.mul {g f : ℝ → ℝ} (hg : BM T g) (hf : BM T f) : BM T (fun x => g x * f x) :=
  hg.smul hf

theorem BM.clm [NormedSpace ℝ F] [NormedSpace ℝ G] (L : F →L[ℝ] G) {f : ℝ → F} (hf : BM T f) :
    BM T (fun x => L (f x)) := by
  obtain ⟨C, h⟩ := hf.bdd
  refine ⟨L.continuous.comp_aestronglyMeasurable hf.meas, ‖L‖ * C, fun x hx => ?_⟩
  exact (L.le_opNorm _).trans (mul_le_mul_of_nonneg_left (h x hx) (norm_nonneg _))

theorem BM.norm {f : ℝ → F} (hf : BM T f) : BM T (fun x => ‖f x‖) := by
  obtain ⟨C, h⟩ := hf.bdd
  exact ⟨hf.meas.norm, C, fun x hx => by rw [norm_norm]; exact h x hx⟩

theorem BM.pow {f : ℝ → ℝ} (hf : BM T f) (n : ℕ) : BM T (fun x => f x ^ n) := by
  induction n with
  | zero => simpa using BM.const (T := T) (1 : ℝ)
  | succ n ih => simpa [pow_succ] using ih.mul hf

theorem BM.inner {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] {f g : ℝ → E}
    (hf : BM T f) (hg : BM T g) : BM T (fun x => ⟪f x, g x⟫) := by
  obtain ⟨C₁, h₁⟩ := hf.bdd
  obtain ⟨C₂, h₂⟩ := hg.bdd
  refine ⟨hf.meas.inner hg.meas, C₁ * C₂, fun x hx => ?_⟩
  rw [Real.norm_eq_abs]
  exact (abs_real_inner_le_norm _ _).trans
    (mul_le_mul (h₁ x hx) (h₂ x hx) (norm_nonneg _) ((norm_nonneg _).trans (h₁ x hx)))

end BMlemmas

/-! ### Moments, the affine fit and the `L²` norm -/

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]

/-- zeroth moment `∫₀ᵀ f`. -/
def mom0 (T : ℝ) (f : ℝ → E) : E := ∫ x in Icc 0 T, f x

/-- first moment `∫₀ᵀ s • f s`. -/
def mom1 (T : ℝ) (f : ℝ → E) : E := ∫ x in Icc 0 T, x • f x

/-- the affine function `s ↦ c₀ + s • c₁`. -/
def affLine (c₀ c₁ : E) (x : ℝ) : E := c₀ + x • c₁

/-- constant coefficient of the affine function with moments `(m₀, m₁)`. -/
def fitC0 (T : ℝ) (m₀ m₁ : E) : E := (4 / T) • m₀ - (6 / T ^ 2) • m₁

/-- slope of the affine function with moments `(m₀, m₁)`. -/
def fitC1 (T : ℝ) (m₀ m₁ : E) : E := (12 / T ^ 3) • m₁ - (6 / T ^ 2) • m₀

/-- `P f`: the affine function with the same two moments as `f` (the `L²` projection onto
affine functions). -/
def fit (T : ℝ) (f : ℝ → E) : ℝ → E :=
  affLine (fitC0 T (mom0 T f) (mom1 T f)) (fitC1 T (mom0 T f) (mom1 T f))

/-- the squared `L²(0,T)` norm. -/
def L2 (T : ℝ) (f : ℝ → E) : ℝ := ∫ x in Icc 0 T, ‖f x‖ ^ 2

variable {T : ℝ}

theorem BM.affLine (c₀ c₁ : E) : BM T (affLine c₀ c₁) :=
  BM.of_continuous (continuous_const.add (continuous_id.smul continuous_const))

theorem BM.fit (f : ℝ → E) : BM T (fit T f) := BM.affLine _ _

theorem BM.smul_id {f : ℝ → E} (hf : BM T f) : BM T (fun x => x • f x) :=
  (BM.of_continuous continuous_id).smul hf

theorem L2_nonneg (f : ℝ → E) : 0 ≤ L2 T f :=
  setIntegral_nonneg measurableSet_Icc fun _ _ => sq_nonneg _

theorem integral_affLine (hT : 0 ≤ T) (c₀ c₁ : E) :
    ∫ x in Icc 0 T, affLine c₀ c₁ x = T • c₀ + (T ^ 2 / 2) • c₁ := by
  rw [setIntegral_Icc_eq_intervalIntegral hT]
  simp only [affLine]
  rw [intervalIntegral.integral_add (f := fun _ => c₀) (g := fun x : ℝ => x • c₁)
    intervalIntegrable_const (Continuous.intervalIntegrable (by fun_prop) _ _),
    intervalIntegral.integral_const, intervalIntegral.integral_smul_const, integral_id]
  simp

theorem integral_smul_affLine (hT : 0 ≤ T) (c₀ c₁ : E) :
    ∫ x in Icc 0 T, x • affLine c₀ c₁ x = (T ^ 2 / 2) • c₀ + (T ^ 3 / 3) • c₁ := by
  have h : (fun x : ℝ => x • affLine c₀ c₁ x) = fun x => x • c₀ + (x ^ 2) • c₁ := by
    ext x; simp [affLine, smul_add, smul_smul, sq]
  rw [h, setIntegral_Icc_eq_intervalIntegral hT,
    intervalIntegral.integral_add (f := fun x : ℝ => x • c₀) (g := fun x : ℝ => x ^ 2 • c₁)
      (Continuous.intervalIntegrable (by fun_prop) _ _)
      (Continuous.intervalIntegrable (by fun_prop) _ _),
    intervalIntegral.integral_smul_const, intervalIntegral.integral_smul_const, integral_id,
    integral_pow]
  norm_num

theorem fitC_mom0 (hT : 0 < T) (m₀ m₁ : E) :
    T • fitC0 T m₀ m₁ + (T ^ 2 / 2) • fitC1 T m₀ m₁ = m₀ := by
  simp only [fitC0, fitC1, smul_sub, smul_smul]
  have hT' := hT.ne'
  match_scalars <;> field_simp <;> ring

theorem fitC_mom1 (hT : 0 < T) (m₀ m₁ : E) :
    (T ^ 2 / 2) • fitC0 T m₀ m₁ + (T ^ 3 / 3) • fitC1 T m₀ m₁ = m₁ := by
  simp only [fitC0, fitC1, smul_sub, smul_smul]
  have hT' := hT.ne'
  match_scalars <;> field_simp <;> ring

theorem mom0_fit (hT : 0 < T) (f : ℝ → E) : mom0 T (fit T f) = mom0 T f := by
  rw [mom0, fit, integral_affLine hT.le, fitC_mom0 hT]

theorem mom1_fit (hT : 0 < T) (f : ℝ → E) : mom1 T (fit T f) = mom1 T f := by
  rw [mom1, fit, integral_smul_affLine hT.le, fitC_mom1 hT]

theorem mom0_sub {f g : ℝ → E} (hf : BM T f) (hg : BM T g) :
    mom0 T (fun x => f x - g x) = mom0 T f - mom0 T g :=
  integral_sub hf.integrableOn hg.integrableOn

theorem mom1_sub {f g : ℝ → E} (hf : BM T f) (hg : BM T g) :
    mom1 T (fun x => f x - g x) = mom1 T f - mom1 T g := by
  simp only [mom1, smul_sub]
  exact integral_sub hf.smul_id.integrableOn hg.smul_id.integrableOn

theorem mom0_add {f g : ℝ → E} (hf : BM T f) (hg : BM T g) :
    mom0 T (fun x => f x + g x) = mom0 T f + mom0 T g :=
  integral_add hf.integrableOn hg.integrableOn

theorem mom1_add {f g : ℝ → E} (hf : BM T f) (hg : BM T g) :
    mom1 T (fun x => f x + g x) = mom1 T f + mom1 T g := by
  simp only [mom1, smul_add]
  exact integral_add hf.smul_id.integrableOn hg.smul_id.integrableOn

theorem mom0_smul (c : ℝ) (f : ℝ → E) : mom0 T (fun x => c • f x) = c • mom0 T f :=
  integral_smul c f

theorem mom1_smul (c : ℝ) (f : ℝ → E) : mom1 T (fun x => c • f x) = c • mom1 T f := by
  simp only [mom1, smul_comm _ c]
  exact integral_smul c _

/-- `P` is additive. -/
theorem fit_add {f g : ℝ → E} (hf : BM T f) (hg : BM T g) (x : ℝ) :
    fit T (fun x => f x + g x) x = fit T f x + fit T g x := by
  simp only [fit, affLine, fitC0, fitC1, mom0_add hf hg, mom1_add hf hg, smul_add, smul_sub]
  abel

/-- `P` commutes with subtraction. -/
theorem fit_sub {f g : ℝ → E} (hf : BM T f) (hg : BM T g) (x : ℝ) :
    fit T (fun x => f x - g x) x = fit T f x - fit T g x := by
  simp only [fit, affLine, fitC0, fitC1, mom0_sub hf hg, mom1_sub hf hg, smul_add, smul_sub]
  abel

/-- `P` is homogeneous. -/
theorem fit_smul (c : ℝ) (f : ℝ → E) (x : ℝ) :
    fit T (fun x => c • f x) x = c • fit T f x := by
  simp only [fit, affLine, fitC0, fitC1, mom0_smul, mom1_smul, smul_add, smul_sub, smul_comm c]

/-- Integrating against an affine function only sees the two moments. -/
theorem integral_inner_affLine {f : ℝ → E} (hf : BM T f) (d₀ d₁ : E) :
    ∫ x in Icc 0 T, ⟪f x, affLine d₀ d₁ x⟫ = ⟪mom0 T f, d₀⟫ + ⟪mom1 T f, d₁⟫ := by
  have h : (fun x => ⟪f x, affLine d₀ d₁ x⟫) = fun x => ⟪d₀, f x⟫ + ⟪d₁, x • f x⟫ := by
    ext x
    simp only [affLine, inner_add_right, real_inner_smul_right, real_inner_smul_left]
    rw [real_inner_comm d₀, real_inner_comm d₁]
  rw [h, integral_add (Integrable.const_inner d₀ hf.integrableOn) (Integrable.const_inner d₁ hf.smul_id.integrableOn),
    integral_inner hf.integrableOn, integral_inner hf.smul_id.integrableOn,
    real_inner_comm d₀, real_inner_comm d₁]
  rfl

/-- The residual `f - P f` has vanishing moments. -/
theorem integral_inner_sub_fit_affLine (hT : 0 < T) {f : ℝ → E} (hf : BM T f) (d₀ d₁ : E) :
    ∫ x in Icc 0 T, ⟪f x - fit T f x, affLine d₀ d₁ x⟫ = 0 := by
  rw [integral_inner_affLine (hf.sub (BM.fit f)), mom0_sub hf (BM.fit f),
    mom1_sub hf (BM.fit f), mom0_fit hT, mom1_fit hT]
  simp

theorem BM.integrableOn_normSq {f : ℝ → E} (hf : BM T f) :
    IntegrableOn (fun x => ‖f x‖ ^ 2) (Icc 0 T) :=
  (hf.norm.pow 2).integrableOn

/-- **Pythagoras for the affine projection.** For every affine `A`,
`‖f - A‖² = ‖f - P f‖² + ‖P f - A‖²`. -/
theorem L2_sub_affLine (hT : 0 < T) {f : ℝ → E} (hf : BM T f) (d₀ d₁ : E) :
    L2 T (fun x => f x - affLine d₀ d₁ x) =
      L2 T (fun x => f x - fit T f x) + L2 T (fun x => fit T f x - affLine d₀ d₁ x) := by
  set c₀ := fitC0 T (mom0 T f) (mom1 T f)
  set c₁ := fitC1 T (mom0 T f) (mom1 T f)
  have hv : (fun x => fit T f x - affLine d₀ d₁ x) = affLine (c₀ - d₀) (c₁ - d₁) := by
    ext x; simp only [fit, affLine, c₀, c₁, smul_sub]; abel
  have hu : BM T (fun x => f x - fit T f x) := hf.sub (BM.fit f)
  have hpt : (fun x => ‖f x - affLine d₀ d₁ x‖ ^ 2) = fun x =>
      ‖f x - fit T f x‖ ^ 2 + 2 * ⟪f x - fit T f x, affLine (c₀ - d₀) (c₁ - d₁) x⟫ +
        ‖affLine (c₀ - d₀) (c₁ - d₁) x‖ ^ 2 := by
    ext x
    rw [← congrFun hv x, ← norm_add_sq_real]
    congr 1; abel
  have i1 : IntegrableOn (fun x => ‖f x - fit T f x‖ ^ 2) (Icc 0 T) := hu.integrableOn_normSq
  have i2 : IntegrableOn (fun x => 2 * ⟪f x - fit T f x, affLine (c₀ - d₀) (c₁ - d₁) x⟫)
      (Icc 0 T) := (hu.inner (BM.affLine _ _)).integrableOn.const_mul 2
  have i3 : IntegrableOn (fun x => ‖affLine (c₀ - d₀) (c₁ - d₁) x‖ ^ 2) (Icc 0 T) :=
    (BM.affLine _ _).integrableOn_normSq
  have i12 : IntegrableOn (fun x => ‖f x - fit T f x‖ ^ 2 +
      2 * ⟪f x - fit T f x, affLine (c₀ - d₀) (c₁ - d₁) x⟫) (Icc 0 T) := i1.add i2
  rw [L2, hpt, integral_add i12 i3,
    integral_add (f := fun x => ‖f x - fit T f x‖ ^ 2) i1 i2,
    integral_const_mul, integral_inner_sub_fit_affLine hT hf, L2, L2]
  have hv' : ∀ x, fit T f x - affLine d₀ d₁ x = affLine (c₀ - d₀) (c₁ - d₁) x :=
    fun x => congrFun hv x
  simp only [hv', mul_zero, add_zero]

/-- `P f` is the best affine approximation: `‖P^⊥ f‖ ≤ ‖f - A‖` for every affine `A`. -/
theorem L2_sub_fit_le (hT : 0 < T) {f : ℝ → E} (hf : BM T f) (d₀ d₁ : E) :
    L2 T (fun x => f x - fit T f x) ≤ L2 T (fun x => f x - affLine d₀ d₁ x) := by
  rw [L2_sub_affLine hT hf d₀ d₁]
  linarith [L2_nonneg (T := T) (fun x => fit T f x - affLine d₀ d₁ x)]

/-- `‖P^⊥ f‖ ≤ ‖f‖`. -/
theorem L2_sub_fit_le_L2 (hT : 0 < T) {f : ℝ → E} (hf : BM T f) :
    L2 T (fun x => f x - fit T f x) ≤ L2 T f := by
  have := L2_sub_fit_le hT hf 0 0
  simpa [affLine] using this

/-- **Pythagoras**: `‖f‖² = ‖P^⊥ f‖² + ‖P f‖²`. -/
theorem L2_eq_add_fit (hT : 0 < T) {f : ℝ → E} (hf : BM T f) :
    L2 T f = L2 T (fun x => f x - fit T f x) + L2 T (fit T f) := by
  have := L2_sub_affLine hT hf 0 0
  simpa [affLine] using this

/-- `L²` norm of an affine function. -/
theorem L2_affLine (hT : 0 ≤ T) (c₀ c₁ : E) :
    L2 T (affLine c₀ c₁) = T * ‖c₀‖ ^ 2 + T ^ 2 * ⟪c₀, c₁⟫ + T ^ 3 / 3 * ‖c₁‖ ^ 2 := by
  have h : (fun x => ‖affLine c₀ c₁ x‖ ^ 2) =
      fun x => ‖c₀‖ ^ 2 + (2 * ⟪c₀, c₁⟫) * x + ‖c₁‖ ^ 2 * x ^ 2 := by
    ext x
    rw [affLine, norm_add_sq_real, norm_smul, real_inner_smul_right, mul_pow, Real.norm_eq_abs,
      sq_abs]
    ring
  rw [L2, h, setIntegral_Icc_eq_intervalIntegral hT,
    intervalIntegral.integral_add (f := fun x : ℝ => ‖c₀‖ ^ 2 + (2 * ⟪c₀, c₁⟫) * x)
      (g := fun x : ℝ => ‖c₁‖ ^ 2 * x ^ 2) (Continuous.intervalIntegrable (by fun_prop) _ _)
      (Continuous.intervalIntegrable (by fun_prop) _ _),
    intervalIntegral.integral_add (f := fun _ : ℝ => ‖c₀‖ ^ 2)
      (g := fun x : ℝ => (2 * ⟪c₀, c₁⟫) * x) intervalIntegrable_const
      (Continuous.intervalIntegrable (by fun_prop) _ _),
    intervalIntegral.integral_const, intervalIntegral.integral_const_mul,
    intervalIntegral.integral_const_mul, integral_id, integral_pow]
  simp only [smul_eq_mul]
  ring

/-- `‖π_{(0,q)}‖² = 12 ‖q‖² / T³`. -/
theorem L2_fit_of_mom0_eq_zero (hT : 0 < T) {f : ℝ → E} (h0 : mom0 T f = 0) :
    L2 T (fit T f) = 12 / T ^ 3 * ‖mom1 T f‖ ^ 2 := by
  rw [fit, L2_affLine hT.le, fitC0, fitC1, h0]
  simp only [smul_zero, zero_sub, sub_zero, norm_neg, norm_smul, inner_neg_left,
    real_inner_smul_left, real_inner_smul_right, real_inner_self_eq_norm_sq, Real.norm_eq_abs]
  rw [abs_of_pos (by positivity : (0 : ℝ) < 6 / T ^ 2),
    abs_of_pos (by positivity : (0 : ℝ) < 12 / T ^ 3)]
  have hT' := hT.ne'
  field_simp
  ring

/-! ### Minkowski -/

theorem norm_add_sq_le_weighted (a b : E) {t : ℝ} (ht : 0 < t) :
    ‖a + b‖ ^ 2 ≤ (1 + t) * ‖a‖ ^ 2 + (1 + 1 / t) * ‖b‖ ^ 2 := by
  rw [norm_add_sq_real]
  have h1 : ⟪a, b⟫ ≤ ‖a‖ * ‖b‖ := real_inner_le_norm a b
  have h2 : 2 * (‖a‖ * ‖b‖) ≤ t * ‖a‖ ^ 2 + 1 / t * ‖b‖ ^ 2 := by
    have : 0 ≤ (t * ‖a‖ - ‖b‖) ^ 2 / t := div_nonneg (sq_nonneg _) ht.le
    have e : (t * ‖a‖ - ‖b‖) ^ 2 / t = t * ‖a‖ ^ 2 + 1 / t * ‖b‖ ^ 2 - 2 * (‖a‖ * ‖b‖) := by
      field_simp; ring
    linarith
  nlinarith

theorem L2_add_le_weighted {f g : ℝ → E} (hf : BM T f) (hg : BM T g) {t : ℝ} (ht : 0 < t) :
    L2 T (fun x => f x + g x) ≤ (1 + t) * L2 T f + (1 + 1 / t) * L2 T g := by
  rw [L2, L2, L2, ← integral_const_mul, ← integral_const_mul,
    ← integral_add (hf.integrableOn_normSq.const_mul _) (hg.integrableOn_normSq.const_mul _)]
  refine setIntegral_mono_on (hf.add hg).integrableOn_normSq
    ((hf.integrableOn_normSq.const_mul _).add (hg.integrableOn_normSq.const_mul _))
    measurableSet_Icc fun x _ => norm_add_sq_le_weighted _ _ ht

/-- **Minkowski**: `‖f‖ ≤ X`, `‖g‖ ≤ Y` ⇒ `‖f + g‖ ≤ X + Y` (squared form). -/
theorem L2_add_le {f g : ℝ → E} (hf : BM T f) (hg : BM T g) {X Y : ℝ} (hX : 0 ≤ X) (hY : 0 ≤ Y)
    (hfX : L2 T f ≤ X ^ 2) (hgY : L2 T g ≤ Y ^ 2) :
    L2 T (fun x => f x + g x) ≤ (X + Y) ^ 2 := by
  have key : ∀ η > 0, L2 T (fun x => f x + g x) ≤ (X + Y + 2 * η) ^ 2 := by
    intro η hη
    have hXη : 0 < X + η := by linarith
    have hYη : 0 < Y + η := by linarith
    have h := L2_add_le_weighted (T := T) hf hg (div_pos hYη hXη)
    have hf' : L2 T f ≤ (X + η) ^ 2 := hfX.trans (by nlinarith)
    have hg' : L2 T g ≤ (Y + η) ^ 2 := hgY.trans (by nlinarith)
    have e : (1 + (Y + η) / (X + η)) * (X + η) ^ 2 + (1 + 1 / ((Y + η) / (X + η))) * (Y + η) ^ 2
        = (X + Y + 2 * η) ^ 2 := by
      field_simp; ring
    calc L2 T (fun x => f x + g x)
        ≤ (1 + (Y + η) / (X + η)) * L2 T f + (1 + 1 / ((Y + η) / (X + η))) * L2 T g := h
      _ ≤ (1 + (Y + η) / (X + η)) * (X + η) ^ 2 + (1 + 1 / ((Y + η) / (X + η))) * (Y + η) ^ 2 := by
          gcongr
      _ = (X + Y + 2 * η) ^ 2 := e
  have ht : Filter.Tendsto (fun η : ℝ => (X + Y + 2 * η) ^ 2) (nhdsWithin 0 (Ioi 0))
      (nhds ((X + Y + 2 * 0) ^ 2)) :=
    ((continuous_const.add (continuous_const.mul continuous_id)).pow 2).tendsto 0
      |>.mono_left nhdsWithin_le_nhds
  have := ge_of_tendsto ht (Filter.eventually_of_mem self_mem_nhdsWithin fun η hη => key η hη)
  simpa using this

end LcvxObstruction.Slice
