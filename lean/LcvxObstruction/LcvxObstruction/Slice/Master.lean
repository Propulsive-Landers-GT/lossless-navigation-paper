import LcvxObstruction.Slice.Wirtinger
import LcvxObstruction.DiveBrake

/-!
# Proposition M (master inequality) for model M1 (math/07 §2)

Model M1 exactly as in `Model.lean` (`AttitudeAdmissible`, `AccBox`, `position`, `velocity`),
in the constant-mass case `α = 0`: throttle box `a₁ ≤ a ≤ a₂` with constants `0 < a₁ ≤ a₂`.

Notation: `τ̄ = δ + ω T`, `c̄ = 1/(1 + cos τ̄)` (the variant (c) of math/07 Remark (c), which uses
the constant `c̄(T)` and has no `E₄` term), `A' = c̄ / a₁`,
`B = a₁ c̄ T (ωT/(2π) + √(2 - 2 cos δ))²` (note `√(2-2cos δ) = 2 sin(δ/2)`, the gimbal chord),
lateral thrust force `F s = hor (a s • d s)` (horizontal part).

* `master_inequality` (**Prop. M**, throttle): for every `κ > A'` with
  `κ (a₂ - a₁) sin² τ̄ ≤ cos τ̄`, every admissible trajectory satisfies
  `gain ≤ B + (A' κ / (κ - A')) ‖P F‖²`, where `gain = a₁ T - ∫ a d_z`.
* `master_inequality_fixed` (fixed thrust `a ≡ a₁`): `gain ≤ B + A' ‖P F‖²`.
* `landing_moments`: from vertical data, a landing at `(p, 0)` has `∫ F = 0`, `∫ s F = -p`
  and `∫ a d_z = g₀ T - v₀z` (so all landings from the same data have the same gain).
* `dent_fixed`, `dent`: hence `gain(ζ) ≤ B + C · 12 ‖p‖² / T³` for every landing offset `p`.

No state constraints are used (the bounds hold for the unconstrained landing set, hence for
every constrained one).
-/

open MeasureTheory Set Real InnerProductGeometry
open scoped RealInnerProductSpace

noncomputable section

namespace LcvxObstruction.Slice

/-! ### Horizontal projection -/

/-- The horizontal projection `v ↦ v - ⟪ez, v⟫ ez` as a continuous linear map. -/
def horL : E3 →L[ℝ] E3 := ContinuousLinearMap.id ℝ E3 - (innerSL ℝ ez).smulRight ez

/-- horizontal part of a vector. -/
def hor (v : E3) : E3 := horL v

theorem hor_apply (v : E3) : hor v = v - ⟪ez, v⟫ • ez := by
  simp [hor, horL]

theorem inner_ez_ez : ⟪ez, ez⟫ = 1 := by
  rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num

theorem hor_ez : hor ez = 0 := by rw [hor_apply, inner_ez_ez, one_smul, sub_self]

theorem hor_smul (c : ℝ) (v : E3) : hor (c • v) = c • hor v := horL.map_smul c v

theorem hor_add (v w : E3) : hor (v + w) = hor v + hor w := horL.map_add v w

theorem hor_sub (v w : E3) : hor (v - w) = hor v - hor w := horL.map_sub v w

theorem hor_neg (v : E3) : hor (-v) = -hor v := horL.map_neg v

theorem hor_smul_ez (c : ℝ) : hor (c • ez) = 0 := by rw [hor_smul, hor_ez, smul_zero]

theorem hor_eq_self {p : E3} (hp : ⟪p, ez⟫ = 0) : hor p = p := by
  rw [hor_apply, real_inner_comm, hp, zero_smul, sub_zero]

theorem eq_hor_add (v : E3) : v = hor v + ⟪v, ez⟫ • ez := by
  rw [hor_apply, real_inner_comm]; abel

theorem norm_hor_sq (v : E3) : ‖hor v‖ ^ 2 = ‖v‖ ^ 2 - ⟪v, ez⟫ ^ 2 := by
  rw [hor_apply, norm_sub_sq_real, norm_smul, norm_ez, real_inner_smul_right, real_inner_comm ez v,
    Real.norm_eq_abs, mul_one, sq_abs]
  ring

theorem norm_hor_le (v : E3) : ‖hor v‖ ≤ ‖v‖ := by
  have h := norm_hor_sq v
  have : ‖hor v‖ ^ 2 ≤ ‖v‖ ^ 2 := by rw [h]; nlinarith [sq_nonneg ⟪v, ez⟫]
  exact (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp this

theorem integral_hor {f : ℝ → E3} {T : ℝ} (hf : IntegrableOn f (Icc 0 T)) :
    ∫ s in Icc 0 T, hor (f s) = hor (∫ s in Icc 0 T, f s) :=
  horL.integral_comp_comm hf

/-! ### Elementary pointwise inequalities -/

/-- chord ≤ arc for unit vectors. -/
theorem norm_sub_le_angle {x y : E3} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) : ‖x - y‖ ≤ angle x y := by
  have h1 : ‖x - y‖ ^ 2 = 2 - 2 * Real.cos (angle x y) := by
    rw [norm_sub_sq_real, hx, hy, inner_eq_cos_angle hx hy]; ring
  have h2 := Real.one_sub_sq_div_two_le_cos (x := angle x y)
  have h3 : ‖x - y‖ ^ 2 ≤ angle x y ^ 2 := by rw [h1]; linarith
  exact (sq_le_sq₀ (norm_nonneg _) (angle_nonneg x y)).mp h3

/-- gimbal chord: `‖d - b‖² ≤ 2 - 2 cos δ`. -/
theorem norm_sub_sq_le_of_angle {x y : E3} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) {δ : ℝ}
    (h : angle x y ≤ δ) (hδ : δ ≤ π) : ‖x - y‖ ^ 2 ≤ 2 - 2 * Real.cos δ := by
  have := cos_le_inner_of_angle_le hx hy h hδ
  rw [norm_sub_sq_real, hx, hy]; linarith

/-- **Lemma P1 + throttle split (SP1, SP3).** -/
theorem pointwise_majorant {a a₁ a₂ cτ κ : ℝ} {d : E3} (hd : ‖d‖ = 1) (hdz : cτ ≤ ⟪d, ez⟫)
    (hcτ : 0 < cτ) (ha₁ : 0 ≤ a₁) (ha : a₁ ≤ a) (ha' : a ≤ a₂) (hκ0 : 0 ≤ κ)
    (hκ : κ * (a₂ - a₁) * (1 - cτ ^ 2) ≤ cτ) :
    a₁ - a * ⟪d, ez⟫ ≤ a₁ / (1 + cτ) * ‖hor d‖ ^ 2 - κ * ‖(a - a₁) • hor d‖ ^ 2 := by
  set z := ⟪d, ez⟫
  have hn : ‖hor d‖ ^ 2 = 1 - z ^ 2 := by rw [norm_hor_sq, hd]; ring
  have hz1 : z ≤ 1 := by
    have := real_inner_le_norm d ez; rw [hd, norm_ez] at this; linarith
  have hK : ‖(a - a₁) • hor d‖ ^ 2 = (a - a₁) ^ 2 * (1 - z ^ 2) := by
    rw [norm_smul, mul_pow, Real.norm_eq_abs, sq_abs, hn]
  rw [hn, hK]
  have hzpos : 0 < z := lt_of_lt_of_le hcτ hdz
  -- `a₁ (1 - z) ≤ a₁ (1 - z²)/(1 + cτ)`
  have h1 : a₁ * (1 - z) ≤ a₁ / (1 + cτ) * (1 - z ^ 2) := by
    have : (1 - z) * (1 + cτ) ≤ 1 - z ^ 2 := by nlinarith
    rw [div_mul_eq_mul_div, le_div_iff₀ (by linarith)]
    nlinarith
  -- `κ (a - a₁)² (1 - z²) ≤ (a - a₁) z`
  have h2 : κ * ((a - a₁) ^ 2 * (1 - z ^ 2)) ≤ (a - a₁) * z := by
    have e1 : 1 - z ^ 2 ≤ 1 - cτ ^ 2 := by nlinarith
    have e2 : 0 ≤ 1 - z ^ 2 := by nlinarith
    have e3 : 0 ≤ a - a₁ := by linarith
    have e4 : a - a₁ ≤ a₂ - a₁ := by linarith
    calc κ * ((a - a₁) ^ 2 * (1 - z ^ 2)) = (a - a₁) * (κ * (a - a₁) * (1 - z ^ 2)) := by ring
      _ ≤ (a - a₁) * (κ * (a₂ - a₁) * (1 - cτ ^ 2)) := by
          apply mul_le_mul_of_nonneg_left _ e3
          have : κ * (a - a₁) ≤ κ * (a₂ - a₁) := mul_le_mul_of_nonneg_left e4 hκ0
          calc κ * (a - a₁) * (1 - z ^ 2) ≤ κ * (a₂ - a₁) * (1 - z ^ 2) :=
                mul_le_mul_of_nonneg_right this e2
            _ ≤ κ * (a₂ - a₁) * (1 - cτ ^ 2) :=
                mul_le_mul_of_nonneg_left e1 (mul_nonneg hκ0 (by linarith))
      _ ≤ (a - a₁) * cτ := mul_le_mul_of_nonneg_left hκ e3
      _ ≤ (a - a₁) * z := mul_le_mul_of_nonneg_left hdz e3
  nlinarith

/-- Maximizing a concave quadratic: `A'‖x‖² - κ‖π - x‖² ≤ (A'κ/(κ - A')) ‖π‖²`. -/
theorem concave_quad {A' κ : ℝ} (hA : 0 ≤ A') (hκ : A' < κ) (x q : E3) :
    A' * ‖x‖ ^ 2 - κ * ‖q - x‖ ^ 2 ≤ A' * κ / (κ - A') * ‖q‖ ^ 2 := by
  have hD : 0 < κ - A' := by linarith
  have hsq : 0 ≤ ‖(κ - A') • x - κ • q‖ ^ 2 := sq_nonneg _
  rw [norm_sub_sq_real, norm_smul, norm_smul, real_inner_smul_left, real_inner_smul_right,
    Real.norm_eq_abs, Real.norm_eq_abs, abs_of_pos hD, abs_of_pos (by linarith : 0 < κ)] at hsq
  rw [norm_sub_sq_real, real_inner_comm, div_mul_eq_mul_div, le_div_iff₀ hD]
  nlinarith [sq_nonneg ‖x‖, sq_nonneg ‖q‖]

/-! ### The master inequality -/

/-- `c̄ = 1/(1 + cos τ̄)`. -/
def cbar (τ : ℝ) : ℝ := 1 / (1 + Real.cos τ)

/-- the constant `B` of Prop. M (variant (c), `α = 0`). -/
def slackB (T ω δ a₁ : ℝ) : ℝ :=
  a₁ * cbar (δ + ω * T) * T * (ω * T / (2 * π) + √(2 - 2 * Real.cos δ)) ^ 2

/-- lateral (horizontal) thrust acceleration `F = hor (a d)`. -/
def latForce (a : ℝ → ℝ) (d : ℝ → E3) (s : ℝ) : E3 := hor (a s • d s)

section Master

variable {T ω δ a₁ a₂ : ℝ} {a : ℝ → ℝ} {d b : ℝ → E3}

theorem cos_tau_pos (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hT : 0 < T) (hτ : δ + ω * T < π / 2) :
    0 < Real.cos (δ + ω * T) :=
  Real.cos_pos_of_mem_Ioo ⟨by nlinarith [Real.pi_pos], hτ⟩

theorem inner_d_ez_ge (hadm : AttitudeAdmissible T ω δ d b) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hτ : δ + ω * T < π / 2) {s : ℝ} (hs : s ∈ Icc 0 T) :
    Real.cos (δ + ω * T) ≤ ⟪d s, ez⟫ := by
  have hsT : ω * s ≤ ω * T := mul_le_mul_of_nonneg_left hs.2 hω
  have h1 := hadm.inner_d_ez hω hδ hs (by linarith [Real.pi_pos])
  refine le_trans ?_ h1
  exact Real.cos_le_cos_of_nonneg_of_le_pi (by nlinarith [hs.1]) (by linarith [Real.pi_pos])
    (by linarith)

theorem bm_of_accBox (ha : a ∈ AccBox T (fun _ => a₁) (fun _ => a₂)) (ha₁ : 0 ≤ a₁) : BM T a := by
  refine ⟨ha.1.aestronglyMeasurable, a₂, fun s hs => ?_⟩
  have := ha.2 s hs
  rw [Real.norm_eq_abs, abs_of_nonneg (by linarith [this.1])]
  exact this.2

theorem bm_d (hadm : AttitudeAdmissible T ω δ d b) : BM T d :=
  ⟨hadm.d_meas, 1, fun s hs => (hadm.d_unit s hs).le⟩

theorem bm_b (hadm : AttitudeAdmissible T ω δ d b) : BM T b :=
  BM.of_continuousOn hadm.b_cont

/-- `hor ∘ b` is `ω`-Lipschitz (slew-rate limit; Lemma P2(iii)). -/
theorem hor_b_lipschitz (hadm : AttitudeAdmissible T ω δ d b) :
    ∀ x ∈ Icc 0 T, ∀ y ∈ Icc 0 T, ‖hor (b x) - hor (b y)‖ ≤ ω * |x - y| := by
  intro x hx y hy
  rw [← hor_sub]
  exact (norm_hor_le _).trans ((norm_sub_le_angle (hadm.b_unit x hx) (hadm.b_unit y hy)).trans
    (hadm.b_rate x hx y hy))

/-- **Proposition M (master inequality), throttle version.** -/
theorem master_inequality {κ : ℝ} (hT : 0 < T) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hτ : δ + ω * T < π / 2) (ha₁ : 0 < a₁)
    (hκ : cbar (δ + ω * T) / a₁ < κ)
    (hκ2 : κ * (a₂ - a₁) * Real.sin (δ + ω * T) ^ 2 ≤ Real.cos (δ + ω * T))
    (ha : a ∈ AccBox T (fun _ => a₁) (fun _ => a₂)) (hadm : AttitudeAdmissible T ω δ d b) :
    a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ ≤ slackB T ω δ a₁ +
      cbar (δ + ω * T) / a₁ * κ / (κ - cbar (δ + ω * T) / a₁) * L2 T (fit T (latForce a d)) := by
  set τ := δ + ω * T with hτdef
  set cτ := Real.cos τ
  set cb := cbar τ with hcb
  have hcτ : 0 < cτ := cos_tau_pos hω hδ hT hτ
  have hcb_pos : 0 < cb := by rw [hcb, cbar]; positivity
  set A' := cb / a₁ with hA'
  have hA'0 : 0 ≤ A' := by positivity
  have hκ0 : 0 ≤ κ := by linarith
  have ha₁' := ha₁.ne'
  have hsin : 1 - cτ ^ 2 = Real.sin τ ^ 2 := by rw [← Real.sin_sq_add_cos_sq τ]; ring
  -- regularity
  have hBa := bm_of_accBox ha ha₁.le
  have hBd := bm_d hadm
  set v : ℝ → E3 := fun s => hor (d s) with hv
  set K : ℝ → E3 := fun s => (a s - a₁) • v s with hK
  have hBv : BM T v := hBd.clm horL
  have hBK : BM T K := (hBa.sub (BM.const a₁)).smul hBv
  have hBF : BM T (latForce a d) := (hBa.smul hBd).clm horL
  have hF : latForce a d = fun s => a₁ • v s + K s := by
    funext s; simp only [latForce, hv, hK, hor_smul]; module
  have hab : ∀ s ∈ Icc 0 T, a₁ ≤ a s ∧ a s ≤ a₂ := ha.2
  -- Step 1: integrate the pointwise majorant
  have hint_ad : IntegrableOn (fun s => a s • d s) (Icc 0 T) :=
    integrableOn_smul_of_unit ha.1 hadm.d_meas hadm.d_unit
  have hgain : a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ =
      ∫ s in Icc 0 T, (a₁ - a s * ⟪d s, ez⟫) := by
    have h1 : ∫ s in Icc 0 T, a s * ⟪d s, ez⟫ = ⟪∫ s in Icc 0 T, a s • d s, ez⟫ := by
      rw [real_inner_comm, ← integral_inner hint_ad]
      congr 1; funext s; rw [real_inner_smul_right, real_inner_comm]
    rw [integral_sub (integrableOn_const (by simp [Real.volume_Icc])) ((hBa.mul (hBd.inner (BM.const ez))).integrableOn), h1,
      setIntegral_const, Real.volume_real_Icc_of_le hT.le, sub_zero, smul_eq_mul, mul_comm]
  have hstep1 : a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ ≤ a₁ * cb * L2 T v - κ * L2 T K := by
    rw [hgain, L2, L2, ← integral_const_mul, ← integral_const_mul,
      ← integral_sub (hBv.integrableOn_normSq.const_mul _) (hBK.integrableOn_normSq.const_mul _)]
    refine setIntegral_mono_on ((BM.const a₁).sub (hBa.mul (hBd.inner (BM.const ez)))).integrableOn
      ((hBv.integrableOn_normSq.const_mul _).sub (hBK.integrableOn_normSq.const_mul _))
      measurableSet_Icc fun s hs => ?_
    have := pointwise_majorant (hadm.d_unit s hs) (inner_d_ez_ge hadm hω hδ hτ hs) hcτ ha₁.le
      (hab s hs).1 (hab s hs).2 hκ0 (by rw [hsin]; exact hκ2)
    simp only [hv, hK]
    calc a₁ - a s * ⟪d s, ez⟫ ≤ a₁ / (1 + cτ) * ‖hor (d s)‖ ^ 2 -
          κ * ‖(a s - a₁) • hor (d s)‖ ^ 2 := this
      _ = a₁ * cb * ‖hor (d s)‖ ^ 2 - κ * ‖(a s - a₁) • hor (d s)‖ ^ 2 := by
          rw [hcb, cbar]; ring
  -- Step 2/3: eliminate `K`
  have hfitF : ∀ s, fit T (latForce a d) s = a₁ • fit T v s + fit T K s := by
    intro s
    rw [hF, fit_add ((BM.const a₁).smul hBv) hBK, fit_smul]
  have hstep3 : a₁ * cb * L2 T (fit T v) - κ * L2 T (fit T K) ≤
      A' * κ / (κ - A') * L2 T (fit T (latForce a d)) := by
    rw [L2, L2, L2, ← integral_const_mul, ← integral_const_mul, ← integral_const_mul,
      ← integral_sub ((BM.fit v).integrableOn_normSq.const_mul _)
        ((BM.fit K).integrableOn_normSq.const_mul _)]
    refine setIntegral_mono_on (((BM.fit v).integrableOn_normSq.const_mul _).sub
      ((BM.fit K).integrableOn_normSq.const_mul _))
      ((BM.fit _).integrableOn_normSq.const_mul _) measurableSet_Icc fun s _ => ?_
    have hq := concave_quad hA'0 hκ (a₁ • fit T v s) (fit T (latForce a d) s)
    have e1 : fit T (latForce a d) s - a₁ • fit T v s = fit T K s := by rw [hfitF]; abel
    rw [e1, norm_smul, mul_pow, Real.norm_eq_abs, sq_abs, hA'] at hq
    have e2 : cb / a₁ * (a₁ ^ 2 * ‖fit T v s‖ ^ 2) = a₁ * cb * ‖fit T v s‖ ^ 2 := by
      field_simp <;> ring
    rw [e2] at hq
    exact hq
  -- Step 4: Wirtinger + gimbal chord
  set β : ℝ → E3 := fun s => hor (b s) with hβ
  set e : ℝ → E3 := fun s => hor (d s - b s) with he
  have hBβ : BM T β := (bm_b hadm).clm horL
  have hBe : BM T e := (hBd.sub (bm_b hadm)).clm horL
  have hve : ∀ s, v s - fit T v s = (β s - fit T β s) + (e s - fit T e s) := by
    intro s
    have hvbe : v = fun s => β s + e s := by
      funext s; simp only [hv, hβ, he, hor_sub]; abel
    have h1 : v s = β s + e s := congrFun hvbe s
    have h2 : fit T v s = fit T β s + fit T e s := by rw [hvbe]; exact fit_add hBβ hBe s
    rw [h1, h2]; abel
  have hW : L2 T (fun s => β s - fit T β s) ≤ (ω * T * √T / (2 * π)) ^ 2 := by
    have := wirtinger_lipschitz hT hω (hor_b_lipschitz hadm)
    calc L2 T (fun s => β s - fit T β s) ≤ (T / (2 * π)) ^ 2 * (ω ^ 2 * T) := this
      _ = (ω * T * √T / (2 * π)) ^ 2 := by
          rw [div_pow, div_pow, mul_pow, mul_pow, Real.sq_sqrt hT.le]; ring
  have hδπ : δ ≤ π := by nlinarith [Real.pi_pos]
  have hE : L2 T (fun s => e s - fit T e s) ≤ (√(2 - 2 * Real.cos δ) * √T) ^ 2 := by
    refine (L2_sub_fit_le_L2 hT hBe).trans ?_
    have hc : 0 ≤ 2 - 2 * Real.cos δ := by nlinarith [Real.cos_le_one δ]
    rw [mul_pow, Real.sq_sqrt hc, Real.sq_sqrt hT.le, L2]
    calc ∫ s in Icc 0 T, ‖e s‖ ^ 2 ≤ ∫ s in Icc 0 T, (2 - 2 * Real.cos δ) :=
          setIntegral_mono_on hBe.integrableOn_normSq (integrableOn_const (by simp [Real.volume_Icc])) measurableSet_Icc
            fun s hs => by
              have h1 : ‖e s‖ ≤ ‖d s - b s‖ := norm_hor_le _
              have h2 := norm_sub_sq_le_of_angle (hadm.d_unit s hs) (hadm.b_unit s hs)
                (hadm.gimbal s hs) hδπ
              nlinarith [norm_nonneg (e s)]
      _ = (2 - 2 * Real.cos δ) * T := by
          rw [setIntegral_const, Real.volume_real_Icc_of_le hT.le, sub_zero, smul_eq_mul,
            mul_comm]
  have hPerp : L2 T (fun s => v s - fit T v s) ≤
      (ω * T * √T / (2 * π) + √(2 - 2 * Real.cos δ) * √T) ^ 2 := by
    have := L2_add_le (hBβ.sub (BM.fit β)) (hBe.sub (BM.fit e)) (by positivity) (by positivity)
      hW hE
    simpa only [← hve] using this
  -- Step 5: collect
  have hPyth := L2_eq_add_fit hT hBv
  have hPythK := L2_eq_add_fit hT hBK
  have hKnn := L2_nonneg (T := T) (fun s => K s - fit T K s)
  have hB : a₁ * cb * (ω * T * √T / (2 * π) + √(2 - 2 * Real.cos δ) * √T) ^ 2 =
      slackB T ω δ a₁ := by
    rw [slackB, ← hτdef, ← hcb]
    have : (ω * T * √T / (2 * π) + √(2 - 2 * Real.cos δ) * √T) =
        √T * (ω * T / (2 * π) + √(2 - 2 * Real.cos δ)) := by ring
    rw [this, mul_pow, Real.sq_sqrt hT.le]; ring
  have hacb : 0 ≤ a₁ * cb := by positivity
  calc a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ ≤ a₁ * cb * L2 T v - κ * L2 T K := hstep1
    _ = a₁ * cb * L2 T (fun s => v s - fit T v s) +
          (a₁ * cb * L2 T (fit T v) - κ * L2 T (fit T K)) -
          κ * L2 T (fun s => K s - fit T K s) := by rw [hPyth, hPythK]; ring
    _ ≤ a₁ * cb * (ω * T * √T / (2 * π) + √(2 - 2 * Real.cos δ) * √T) ^ 2 +
          A' * κ / (κ - A') * L2 T (fit T (latForce a d)) - 0 := by
        linarith [mul_le_mul_of_nonneg_left hPerp hacb, mul_nonneg hκ0 hKnn]
    _ = slackB T ω δ a₁ + A' * κ / (κ - A') * L2 T (fit T (latForce a d)) := by
        rw [hB]; ring

/-- **Proposition M, fixed thrust** (`a ≡ a₁`, so `K ≡ 0` and `C_m = A'`). -/
theorem master_inequality_fixed (hT : 0 < T) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hτ : δ + ω * T < π / 2) (ha₁ : 0 < a₁)
    (ha : a ∈ AccBox T (fun _ => a₁) (fun _ => a₁)) (hadm : AttitudeAdmissible T ω δ d b) :
    a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ ≤ slackB T ω δ a₁ +
      cbar (δ + ω * T) / a₁ * L2 T (fit T (latForce a d)) := by
  set A' := cbar (δ + ω * T) / a₁ with hA'
  set X := L2 T (fit T (latForce a d))
  have hX : 0 ≤ X := L2_nonneg _
  have hcτ := cos_tau_pos hω hδ hT hτ
  have hA'0 : 0 ≤ A' := by rw [hA', cbar]; positivity
  have key : ∀ t > 0, a₁ * T - ⟪∫ s in Icc 0 T, a s • d s, ez⟫ ≤
      slackB T ω δ a₁ + A' * X + A' ^ 2 * X / t := by
    intro t ht
    have h := master_inequality (κ := A' + t) hT hω hδ hτ ha₁ (by linarith)
      (by simp only [sub_self, mul_zero, zero_mul]; exact hcτ.le) ha hadm
    have ht' := ht.ne'
    have e : A' * (A' + t) / (A' + t - A') * X = A' * X + A' ^ 2 * X / t := by
      rw [show A' + t - A' = t by ring]; field_simp <;> ring
    rw [← hA', e] at h
    linarith
  refine le_of_forall_pos_le_add fun ε hε => ?_
  have ht : 0 < (A' ^ 2 * X + 1) / ε := by positivity
  have h := key _ ht
  have : A' ^ 2 * X / ((A' ^ 2 * X + 1) / ε) ≤ ε := by
    rw [div_div_eq_mul_div, div_le_iff₀ (by positivity)]
    nlinarith [mul_nonneg (sq_nonneg A') hX]
  linarith

end Master

/-! ### Landing from vertical data -/

/-- **Landing offsets** `L(ζ)`: the horizontal points `p` at which a trajectory of model M1 from
the data `ζ = (r₀, v₀)` can land at rest at time `T` (`r(T) = p`, `v(T) = 0`), gravity
`-g₀ e_z`, with the state constraint `(r(t), v(t)) ∈ X` for all `t ∈ [0,T]`
(`X = univ`: no constraint; `X = {r_z ≥ 0}`: altitude). -/
def landingOffsets (Acc : Set (ℝ → ℝ)) (T ω δ g₀ : ℝ) (ζ : E3 × E3) (X : Set (E3 × E3)) :
    Set E3 :=
  {p | ⟪p, ez⟫ = 0 ∧ ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible T ω δ d b ∧
    position (-g₀ • ez) ζ.1 ζ.2 a d T = p ∧ velocity (-g₀ • ez) ζ.2 a d T = 0 ∧
    ∀ t ∈ Icc 0 T, (position (-g₀ • ez) ζ.1 ζ.2 a d t, velocity (-g₀ • ez) ζ.2 a d t) ∈ X}

theorem landingOffsets_mono {Acc : Set (ℝ → ℝ)} {T ω δ g₀ : ℝ} {ζ : E3 × E3}
    {X : Set (E3 × E3)} : landingOffsets Acc T ω δ g₀ ζ X ⊆ landingOffsets Acc T ω δ g₀ ζ univ :=
  fun _ ⟨hp, a, d, b, ha, hadm, hr, hv, _⟩ => ⟨hp, a, d, b, ha, hadm, hr, hv, fun _ _ => trivial⟩

/-- The landing-offset set is the horizontal slice of the landing set `F_T` of `Model.lean`
(translation invariance). -/
theorem mem_landingOffsets_univ_iff {Acc : Set (ℝ → ℝ)} {T ω δ g₀ : ℝ} {ζ : E3 × E3} {p : E3} :
    p ∈ landingOffsets Acc T ω δ g₀ ζ univ ↔
      ⟪p, ez⟫ = 0 ∧ (ζ.1 - p, ζ.2) ∈ landingSet Acc T ω δ (-g₀ • ez) := by
  constructor
  · rintro ⟨hp, a, d, b, ha, hadm, hr, hv, -⟩
    refine ⟨hp, a, d, b, ha, hadm, ?_, hv⟩
    simp only [position] at hr ⊢
    rw [← hr]; abel
  · rintro ⟨hp, a, d, b, ha, hadm, hr, hv⟩
    refine ⟨hp, a, d, b, ha, hadm, ?_, hv, fun _ _ => trivial⟩
    simp only [position] at hr ⊢
    rw [← sub_eq_zero, ← hr]; abel

/-- **Landing identities from vertical data.** -/
theorem landing_moments {T g₀ : ℝ} (hT : 0 < T) {ζ : E3 × E3} (hζ1 : hor ζ.1 = 0)
    (hζ2 : hor ζ.2 = 0) {a : ℝ → ℝ} {d : ℝ → E3} {p : E3} (hp : ⟪p, ez⟫ = 0)
    (hint : IntegrableOn (fun s => a s • d s) (Icc 0 T))
    (hr : position (-g₀ • ez) ζ.1 ζ.2 a d T = p) (hv : velocity (-g₀ • ez) ζ.2 a d T = 0) :
    mom0 T (latForce a d) = 0 ∧ mom1 T (latForce a d) = -p ∧
      ⟪∫ s in Icc 0 T, a s • d s, ez⟫ = g₀ * T - ⟪ζ.2, ez⟫ := by
  simp only [velocity, position] at hv hr
  have hI : ∫ s in Icc 0 T, a s • d s = -ζ.2 + (g₀ * T) • ez := by
    calc ∫ s in Icc 0 T, a s • d s
        = (ζ.2 + T • -g₀ • ez + ∫ s in Icc 0 T, a s • d s) - ζ.2 - T • -g₀ • ez := by abel
      _ = 0 - ζ.2 - T • -g₀ • ez := by rw [hv]
      _ = -ζ.2 + (g₀ * T) • ez := by module
  have hint2 : IntegrableOn (fun s => (T - s) • (a s • d s)) (Icc 0 T) :=
    integrableOn_cont_smul hint (c := fun s => T - s) (by fun_prop)
  have hint3 : IntegrableOn (fun s => s • (a s • d s)) (Icc 0 T) :=
    integrableOn_cont_smul hint (c := fun s => s) (by fun_prop)
  have hJ : hor (∫ s in Icc 0 T, (T - s) • (a s • d s)) = p := by
    have e : ∫ s in Icc 0 T, (T - s) • (a s • d s) =
        p - ζ.1 - T • ζ.2 - (T ^ 2 / 2) • (-g₀ • ez) := by
      rw [← hr]; abel
    rw [e, hor_sub, hor_sub, hor_sub, hor_smul, hor_smul, hor_smul, hor_ez, hζ1, hζ2,
      hor_eq_self hp]
    simp
  refine ⟨?_, ?_, ?_⟩
  · rw [mom0]
    simp only [latForce]
    rw [integral_hor hint, hI, hor_add, hor_neg, hζ2, hor_smul_ez]; simp
  · rw [mom1]
    simp only [latForce]
    have e : (fun s => s • hor (a s • d s)) = fun s => hor (s • (a s • d s)) := by
      funext s; simp only [hor_smul]
    rw [e, integral_hor hint3]
    have e2 : ∫ s in Icc 0 T, s • (a s • d s) =
        T • (∫ s in Icc 0 T, a s • d s) - ∫ s in Icc 0 T, (T - s) • (a s • d s) := by
      rw [← integral_smul, ← integral_sub (integrableOn_cont_smul hint (c := fun _ => T) (by fun_prop)) hint2]
      congr 1; funext s; module
    rw [e2, hor_sub, hor_smul, hJ, ← integral_hor hint, show (∫ s in Icc 0 T, hor (a s • d s)) =
      mom0 T (latForce a d) from rfl]
    have h0 : mom0 T (latForce a d) = 0 := by
      rw [mom0]; simp only [latForce]
      rw [integral_hor hint, hI, hor_add, hor_neg, hζ2, hor_smul_ez]; simp
    rw [h0]; simp
  · rw [hI, inner_add_left, inner_neg_left, real_inner_smul_left, inner_ez_ez]; ring

/-- **The dent, fixed thrust.** Every landing offset `p` from vertical data `ζ` satisfies
`gain(ζ) ≤ B + A' · 12 ‖p‖² / T³` with `gain(ζ) = a₁ T - (g₀ T - v₀z)`. -/
theorem dent_fixed {T ω δ a₁ g₀ : ℝ} (hT : 0 < T) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hτ : δ + ω * T < π / 2) (ha₁ : 0 < a₁) {ζ : E3 × E3} (hζ1 : hor ζ.1 = 0)
    (hζ2 : hor ζ.2 = 0) {X : Set (E3 × E3)} {p : E3}
    (hp : p ∈ landingOffsets (AccBox T (fun _ => a₁) (fun _ => a₁)) T ω δ g₀ ζ X) :
    a₁ * T - (g₀ * T - ⟪ζ.2, ez⟫) ≤
      slackB T ω δ a₁ + cbar (δ + ω * T) / a₁ * (12 / T ^ 3 * ‖p‖ ^ 2) := by
  obtain ⟨hpz, a, d, b, ha, hadm, hr, hv, -⟩ := hp
  have hint := integrableOn_smul_of_unit ha.1 hadm.d_meas hadm.d_unit
  obtain ⟨h0, h1, h2⟩ := landing_moments hT hζ1 hζ2 hpz hint hr hv
  have hM := master_inequality_fixed hT hω hδ hτ ha₁ ha hadm
  rw [h2, L2_fit_of_mom0_eq_zero hT h0, h1, norm_neg] at hM
  exact hM

/-- **The dent, throttle** (any admissible `κ`). -/
theorem dent {T ω δ a₁ a₂ g₀ κ : ℝ} (hT : 0 < T) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hτ : δ + ω * T < π / 2) (ha₁ : 0 < a₁) (hκ : cbar (δ + ω * T) / a₁ < κ)
    (hκ2 : κ * (a₂ - a₁) * Real.sin (δ + ω * T) ^ 2 ≤ Real.cos (δ + ω * T))
    {ζ : E3 × E3} (hζ1 : hor ζ.1 = 0) (hζ2 : hor ζ.2 = 0) {X : Set (E3 × E3)} {p : E3}
    (hp : p ∈ landingOffsets (AccBox T (fun _ => a₁) (fun _ => a₂)) T ω δ g₀ ζ X) :
    a₁ * T - (g₀ * T - ⟪ζ.2, ez⟫) ≤ slackB T ω δ a₁ +
      cbar (δ + ω * T) / a₁ * κ / (κ - cbar (δ + ω * T) / a₁) * (12 / T ^ 3 * ‖p‖ ^ 2) := by
  obtain ⟨hpz, a, d, b, ha, hadm, hr, hv, -⟩ := hp
  have hint := integrableOn_smul_of_unit ha.1 hadm.d_meas hadm.d_unit
  obtain ⟨h0, h1, h2⟩ := landing_moments hT hζ1 hζ2 hpz hint hr hv
  have hM := master_inequality hT hω hδ hτ ha₁ hκ hκ2 ha hadm
  rw [h2, L2_fit_of_mom0_eq_zero hT h0, h1, norm_neg] at hM
  exact hM

end LcvxObstruction.Slice
