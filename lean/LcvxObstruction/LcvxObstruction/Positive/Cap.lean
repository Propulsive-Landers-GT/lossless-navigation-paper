import Mathlib

/-!
# Positive side, Tier 1: pointwise lemmas for the relaxed thrust cap

Source: `math/04-positive-results.md` §2, blueprint `math/05-positive-lean-blueprint.md` P1–P10.

All statements are in a general real inner-product space `V`; the headline specialisation to
`EuclideanSpace ℝ (Fin 3)` is `LcvxPositive.C3_headline`.

* `cap b Γ c = {T | ‖T‖ ≤ Γ ∧ c ≤ ⟪b,T⟫}` (relaxed cap, `c = Γ cos δ` in applications).
* `AntiRay b y` : `y ∈ -ℝ≥0 b`, i.e. `∃ κ ≥ 0, y = -κ • b` (includes `y = 0`).
* `normal_of_max_of_norm_lt` (C-G), `eq_neg_smul_of_normal_halfspace` (Lemma H),
  `norm_eq_or_antiRay_of_isMaxOn_cap` (C-3), `isMaxOn_cap_unique` (Lemma U),
  `isMaxOn_cap_of_antiRay` (Lemma S, sharpness), `isMaxOn_slice_of_isMaxOn_joint` (Lemma J),
  `original_feasible_of_lossless` (L8), `extremePoints_cap` (Lemma X).
-/

open scoped RealInnerProductSpace
open Set

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- The relaxed cap `{T | ‖T‖ ≤ Γ ∧ c ≤ ⟪b, T⟫}` (with `c = Γ cos δ` in applications). -/
def cap (b : V) (Γ c : ℝ) : Set V := {T | ‖T‖ ≤ Γ ∧ c ≤ ⟪b, T⟫}

/-- `y` lies on the closed ray `-ℝ≥0 b` (this includes `y = 0`). -/
def AntiRay (b y : V) : Prop := ∃ κ : ℝ, 0 ≤ κ ∧ y = -κ • b

theorem mem_cap {b T : V} {Γ c : ℝ} : T ∈ cap b Γ c ↔ ‖T‖ ≤ Γ ∧ c ≤ ⟪b, T⟫ := Iff.rfl

theorem convex_halfspace (b : V) (c : ℝ) : Convex ℝ {T : V | c ≤ ⟪b, T⟫} := by
  intro x hx y hy s t hs ht hst
  simp only [mem_ofPred_eq, inner_add_right, real_inner_smul_right] at *
  have hc : c = s * c + t * c := by rw [← add_mul, hst, one_mul]
  nlinarith [mul_le_mul_of_nonneg_left hx hs, mul_le_mul_of_nonneg_left hy ht]

theorem convex_normBall (Γ : ℝ) : Convex ℝ {T : V | ‖T‖ ≤ Γ} := by
  intro x hx y hy s t hs ht hst
  simp only [mem_ofPred_eq] at *
  calc ‖s • x + t • y‖ ≤ ‖s • x‖ + ‖t • y‖ := norm_add_le _ _
    _ = s * ‖x‖ + t * ‖y‖ := by
        rw [norm_smul, norm_smul, Real.norm_of_nonneg hs, Real.norm_of_nonneg ht]
    _ ≤ s * Γ + t * Γ := by gcongr
    _ = Γ := by rw [← add_mul, hst, one_mul]

/-- **P1.** The cap is convex. -/
theorem convex_cap (b : V) (Γ c : ℝ) : Convex ℝ (cap b Γ c) :=
  (convex_normBall Γ).inter (convex_halfspace b c)

/-- **P2.** Small steps from an interior point of the ball stay in the ball. -/
theorem norm_add_smul_le_of_norm_lt {Γ : ℝ} {T₀ d : V} (h : ‖T₀‖ < Γ) :
    ∃ s₀ : ℝ, 0 < s₀ ∧ s₀ ≤ 1 ∧ ∀ s, 0 ≤ s → s ≤ s₀ → ‖T₀ + s • d‖ ≤ Γ := by
  refine ⟨min 1 ((Γ - ‖T₀‖) / (‖d‖ + 1)),
    lt_min one_pos (div_pos (by linarith) (by positivity)), min_le_left _ _, ?_⟩
  intro s hs hs'
  have h2 : s ≤ (Γ - ‖T₀‖) / (‖d‖ + 1) := hs'.trans (min_le_right _ _)
  have h3 : s * (‖d‖ + 1) ≤ Γ - ‖T₀‖ := (le_div_iff₀ (by positivity)).mp h2
  calc ‖T₀ + s • d‖ ≤ ‖T₀‖ + ‖s • d‖ := norm_add_le _ _
    _ = ‖T₀‖ + s * ‖d‖ := by rw [norm_smul, Real.norm_of_nonneg hs]
    _ ≤ Γ := by nlinarith [norm_nonneg d]

/-- **P3 = Lemma C-G (general extreme-point lemma).** If `T⋆ ∈ Q` maximizes `⟪y,·⟫` over
`{‖T‖ ≤ Γ} ∩ Q` (`Q` convex) and `‖T⋆‖ < Γ`, then `y` is in the normal cone of `Q` at `T⋆`. -/
theorem normal_of_max_of_norm_lt {Q : Set V} (hQ : Convex ℝ Q) {Γ : ℝ} {y Ts : V}
    (hTQ : Ts ∈ Q) (hmax : ∀ T ∈ Q, ‖T‖ ≤ Γ → ⟪y, T⟫ ≤ ⟪y, Ts⟫) (hlt : ‖Ts‖ < Γ) :
    ∀ T ∈ Q, ⟪y, T - Ts⟫ ≤ 0 := by
  intro T hT
  obtain ⟨s, hs0, hs1, hball⟩ := norm_add_smul_le_of_norm_lt (d := T - Ts) hlt
  have hmem : Ts + s • (T - Ts) ∈ Q := by
    have := hQ hTQ hT (by linarith : (0:ℝ) ≤ 1 - s) hs0.le (by ring : (1 - s) + s = 1)
    convert this using 1
    simp only [smul_sub, sub_smul, one_smul]; abel
  have h := hmax _ hmem (hball s hs0.le le_rfl)
  rw [inner_add_right, real_inner_smul_right] at h
  by_contra hc
  have := mul_pos hs0 (not_le.mp hc)
  linarith

/-- **P4 = Lemma H.** The normal cone of a half-space `{c ≤ ⟪b,·⟫}` (`b ≠ 0`) at any of its
points is contained in `-ℝ≥0 b`. -/
theorem eq_neg_smul_of_normal_halfspace {b y Ts : V} {c : ℝ} (hb : b ≠ 0)
    (hT : c ≤ ⟪b, Ts⟫) (hN : ∀ T, c ≤ ⟪b, T⟫ → ⟪y, T - Ts⟫ ≤ 0) : AntiRay b y := by
  have hb2 : 0 < ‖b‖ ^ 2 := by have := norm_pos_iff.mpr hb; positivity
  set μ : ℝ := ⟪y, b⟫ / ‖b‖ ^ 2 with hμ
  set yp : V := y - μ • b with hyp
  have hbb : ⟪b, b⟫ = ‖b‖ ^ 2 := real_inner_self_eq_norm_sq b
  have hbyp : ⟪b, yp⟫ = 0 := by
    rw [hyp, inner_sub_right, real_inner_smul_right, hbb, hμ, real_inner_comm]
    field_simp; ring
  have h1 := hN (Ts + yp) (by rw [inner_add_right, hbyp]; linarith)
  have h2 := hN (Ts - yp) (by rw [inner_sub_right, hbyp]; linarith)
  rw [add_sub_cancel_left] at h1
  rw [sub_sub_cancel_left, inner_neg_right] at h2
  have h0 : ⟪y, yp⟫ = 0 := le_antisymm h1 (by linarith)
  have hyy : ⟪y, yp⟫ = ‖yp‖ ^ 2 := by
    have hy : y = yp + μ • b := by rw [hyp]; abel
    calc ⟪y, yp⟫ = ⟪yp + μ • b, yp⟫ := by rw [← hy]
      _ = ‖yp‖ ^ 2 + μ * ⟪b, yp⟫ := by
          rw [inner_add_left, real_inner_smul_left, real_inner_self_eq_norm_sq]
      _ = ‖yp‖ ^ 2 := by rw [hbyp, mul_zero, add_zero]
  have hyp0 : yp = 0 := by
    have : ‖yp‖ ^ 2 = 0 := by rw [← hyy, h0]
    exact norm_eq_zero.mp (pow_eq_zero_iff (n := 2) (by norm_num) |>.mp this)
  have h3 := hN (Ts + b) (by rw [inner_add_right, hbb]; linarith)
  rw [add_sub_cancel_left] at h3
  refine ⟨-μ, ?_, ?_⟩
  · have : μ ≤ 0 := div_nonpos_of_nonpos_of_nonneg h3 hb2.le
    linarith
  · rw [neg_neg]
    exact sub_eq_zero.mp hyp0

/-- Maximality on the cap, unfolded. -/
theorem le_of_isMaxOn {b y Ts T : V} {Γ c : ℝ}
    (hmax : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) Ts) (hT : T ∈ cap b Γ c) :
    ⟪y, T⟫ ≤ ⟪y, Ts⟫ := isMaxOn_iff.mp hmax T hT

/-- **P5 = Lemma C-3 (headline, general form).** Every maximizer of `⟪y,·⟫` over the cap
(`b ≠ 0`, any `Γ`, `c`) has `‖T⋆‖ = Γ`, unless `y ∈ -ℝ≥0 b`. -/
theorem norm_eq_or_antiRay_of_isMaxOn_cap {b y Ts : V} {Γ c : ℝ} (hb : b ≠ 0)
    (hmem : Ts ∈ cap b Γ c) (hmax : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) Ts) :
    ‖Ts‖ = Γ ∨ AntiRay b y := by
  rcases eq_or_lt_of_le hmem.1 with h | h
  · exact Or.inl h
  · right
    refine eq_neg_smul_of_normal_halfspace hb hmem.2 ?_
    intro T hT
    exact normal_of_max_of_norm_lt (convex_halfspace b c) hmem.2
      (fun T hT hTn => le_of_isMaxOn hmax ⟨hTn, hT⟩) h T hT

/-- C-3 in the form used downstream: off the anti-ray every maximizer is lossless. -/
theorem norm_eq_of_isMaxOn_cap {b y Ts : V} {Γ c : ℝ} (hb : b ≠ 0) (hy : ¬ AntiRay b y)
    (hmem : Ts ∈ cap b Γ c) (hmax : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) Ts) :
    ‖Ts‖ = Γ :=
  (norm_eq_or_antiRay_of_isMaxOn_cap hb hmem hmax).resolve_right hy

/-- Parallelogram step: if `‖T₁‖ = ‖T₂‖ = ‖½(T₁+T₂)‖ = Γ` then `T₁ = T₂`. -/
theorem eq_of_norm_midpoint {T₁ T₂ : V} {Γ : ℝ} (h1 : ‖T₁‖ = Γ) (h2 : ‖T₂‖ = Γ)
    (hm : ‖(1/2 : ℝ) • (T₁ + T₂)‖ = Γ) : T₁ = T₂ := by
  have hm' : ‖T₁ + T₂‖ = 2 * Γ := by
    rw [norm_smul, Real.norm_of_nonneg (by norm_num)] at hm; linarith
  have hadd := norm_add_sq_real T₁ T₂
  have hsub := norm_sub_sq_real T₁ T₂
  rw [hm', h1, h2] at hadd
  rw [h1, h2] at hsub
  have : ‖T₁ - T₂‖ ^ 2 = 0 := by nlinarith
  exact sub_eq_zero.mp (norm_eq_zero.mp (pow_eq_zero_iff (n := 2) (by norm_num) |>.mp this))

/-- **P6 = Lemma U (uniqueness).** Off the anti-ray, the maximizer over the cap is unique. -/
theorem isMaxOn_cap_unique {b y T₁ T₂ : V} {Γ c : ℝ} (hb : b ≠ 0) (hy : ¬ AntiRay b y)
    (hm1 : T₁ ∈ cap b Γ c) (hm2 : T₂ ∈ cap b Γ c)
    (hx1 : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) T₁)
    (hx2 : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) T₂) : T₁ = T₂ := by
  set M : V := (1/2 : ℝ) • (T₁ + T₂)
  have hM : M ∈ cap b Γ c := by
    have := convex_cap b Γ c hm1 hm2 (by norm_num : (0:ℝ) ≤ 1/2) (by norm_num : (0:ℝ) ≤ 1/2)
      (by norm_num)
    simpa [M, smul_add] using this
  have e12 := le_of_isMaxOn hx1 hm2
  have e21 := le_of_isMaxOn hx2 hm1
  have hxM : IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ c) M := by
    rw [isMaxOn_iff]
    intro T hT
    have := le_of_isMaxOn hx1 hT
    simp only [M, real_inner_smul_right, inner_add_right]
    linarith
  exact eq_of_norm_midpoint (norm_eq_of_isMaxOn_cap hb hy hm1 hx1)
    (norm_eq_of_isMaxOn_cap hb hy hm2 hx2) (norm_eq_of_isMaxOn_cap hb hy hM hxM)

/-- **P7 = Lemma S (sharpness).** If `y = -κ b` (`κ ≥ 0`, `‖b‖ = 1`, `Γ ≥ 0`, `cos δ ≥ 0`) then
`T♭ = (Γ cos δ) b` is a maximizer over `cap b Γ (Γ cos δ)`. -/
theorem isMaxOn_cap_of_antiRay {b y : V} {Γ δ : ℝ} (hb : ‖b‖ = 1) (hΓ : 0 ≤ Γ)
    (hcos : 0 ≤ Real.cos δ) (hy : AntiRay b y) :
    (Γ * Real.cos δ) • b ∈ cap b Γ (Γ * Real.cos δ) ∧
    IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) ((Γ * Real.cos δ) • b) := by
  obtain ⟨κ, hκ, rfl⟩ := hy
  have hbb : ⟪b, b⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hb]; norm_num
  refine ⟨⟨?_, ?_⟩, ?_⟩
  · rw [norm_smul, hb, mul_one, Real.norm_of_nonneg (mul_nonneg hΓ hcos)]
    exact mul_le_of_le_one_right hΓ (Real.cos_le_one δ)
  · rw [real_inner_smul_right, hbb, mul_one]
  · rw [isMaxOn_iff]
    intro T hT
    simp only [real_inner_smul_left, real_inner_smul_right, hbb, mul_one]
    nlinarith [hT.2]

/-- In the sharp regime `0 < δ < π/2`, `Γ > 0`, the maximizer `T♭` of Lemma S is lossy. -/
theorem norm_lt_of_sharp {b : V} {Γ δ : ℝ} (hb : ‖b‖ = 1) (hΓ : 0 < Γ) (hδ0 : 0 < δ)
    (hδ1 : δ < Real.pi / 2) : ‖(Γ * Real.cos δ) • b‖ < Γ := by
  have hc0 : 0 < Real.cos δ := Real.cos_pos_of_mem_Ioo ⟨by linarith, hδ1⟩
  have hc1 : Real.cos δ < 1 := by
    rw [← Real.cos_zero]
    exact Real.cos_lt_cos_of_nonneg_of_le_pi le_rfl (by linarith [Real.pi_pos]) hδ0
  rw [norm_smul, hb, mul_one, Real.norm_of_nonneg (by positivity)]
  nlinarith

/-- **P8 = Lemma J (joint ⇒ conditional).** A maximizer of `⟪y,T⟫ - βΓ` over the joint relaxed
control set maximizes `⟪y,·⟫` over its own slice `cap b Γ⋆ (Γ⋆ cos δ)`. -/
theorem isMaxOn_slice_of_isMaxOn_joint {b y : V} {β δ ρ₁ ρ₂ : ℝ} {Ts : V} {Γs : ℝ}
    (hmax : IsMaxOn (fun p : V × ℝ => ⟪y, p.1⟫ - β * p.2)
      {p : V × ℝ | p.1 ∈ cap b p.2 (p.2 * Real.cos δ) ∧ ρ₁ ≤ p.2 ∧ p.2 ≤ ρ₂} (Ts, Γs))
    (hmem : Ts ∈ cap b Γs (Γs * Real.cos δ) ∧ ρ₁ ≤ Γs ∧ Γs ≤ ρ₂) :
    IsMaxOn (fun T => ⟪y, T⟫) (cap b Γs (Γs * Real.cos δ)) Ts := by
  rw [isMaxOn_iff] at hmax ⊢
  intro T hT
  have := hmax (T, Γs) ⟨hT, hmem.2⟩
  simp only at this
  linarith

/-- **P9 = L8 (lossless ⇒ original-feasible).** -/
theorem original_feasible_of_lossless {b T : V} {Γ δ ρ₁ ρ₂ : ℝ}
    (hT : T ∈ cap b Γ (Γ * Real.cos δ)) (hn : ‖T‖ = Γ) (h1 : ρ₁ ≤ Γ) (h2 : Γ ≤ ρ₂) :
    ρ₁ ≤ ‖T‖ ∧ ‖T‖ ≤ ρ₂ ∧ ‖T‖ * Real.cos δ ≤ ⟪b, T⟫ := by
  rw [hn]; exact ⟨h1, h2, hT.2⟩

/-- **P10 (half of Lemma X).** If some nonzero `d ⊥ b` exists, an interior-norm point of the
cap is not extreme. -/
theorem not_mem_extremePoints_of_norm_lt {b T d : V} {Γ c : ℝ} (hd : d ≠ 0) (hbd : ⟪b, d⟫ = 0)
    (hlt : ‖T‖ < Γ) : T ∉ (cap b Γ c).extremePoints ℝ := by
  intro hT
  obtain ⟨s, hs0, -, hball⟩ := norm_add_smul_le_of_norm_lt (d := d) hlt
  obtain ⟨s', hs'0, -, hball'⟩ := norm_add_smul_le_of_norm_lt (d := -d) hlt
  set e := min s s'
  have he0 : 0 < e := lt_min hs0 hs'0
  have hTc := (mem_extremePoints.mp hT).1
  have hp : T + e • d ∈ cap b Γ c :=
    ⟨hball e he0.le (min_le_left _ _), by
      rw [inner_add_right, real_inner_smul_right, hbd]; linarith [hTc.2]⟩
  have hm : T - e • d ∈ cap b Γ c :=
    ⟨by simpa [sub_eq_add_neg, smul_neg] using hball' e he0.le (min_le_right _ _), by
      rw [inner_sub_right, real_inner_smul_right, hbd]; linarith [hTc.2]⟩
  have hseg : T ∈ openSegment ℝ (T + e • d) (T - e • d) := by
    refine ⟨1/2, 1/2, by norm_num, by norm_num, by norm_num, ?_⟩
    module
  have := ((mem_extremePoints.mp hT).2 _ hp _ hm hseg).1
  have : e • d = 0 := by simpa using this
  rcases smul_eq_zero.mp this with h | h
  · exact he0.ne' h
  · exact hd h

/-- A norm-`Γ` point of the cap is extreme (strict convexity of the Euclidean ball). -/
theorem mem_extremePoints_of_norm_eq {b T : V} {Γ c : ℝ} (hT : T ∈ cap b Γ c) (hn : ‖T‖ = Γ) :
    T ∈ (cap b Γ c).extremePoints ℝ := by
  refine mem_extremePoints.mpr ⟨hT, ?_⟩
  rintro x₁ hx₁ x₂ hx₂ ⟨a, c', ha, hc, hac, rfl⟩
  -- strict convexity: ‖a x₁ + c' x₂‖ = Γ with ‖xᵢ‖ ≤ Γ forces x₁ = x₂
  have h1 := hx₁.1
  have h2 := hx₂.1
  have hsq : ‖a • x₁ + c' • x₂‖ ^ 2 = a ^ 2 * ‖x₁‖ ^ 2 + 2 * (a * c') * ⟪x₁, x₂⟫
      + c' ^ 2 * ‖x₂‖ ^ 2 := by
    rw [norm_add_sq_real, norm_smul, norm_smul, real_inner_smul_left, real_inner_smul_right,
      Real.norm_of_nonneg ha.le, Real.norm_of_nonneg hc.le]; ring
  have hd := norm_sub_sq_real x₁ x₂
  have hcs : ⟪x₁, x₂⟫ ≤ ‖x₁‖ * ‖x₂‖ := real_inner_le_norm x₁ x₂
  have hΓ : 0 ≤ Γ := (norm_nonneg _).trans h1
  rw [hn] at hsq
  have n1 := norm_nonneg x₁
  have n2 := norm_nonneg x₂
  -- Γ² = ‖·‖² ≤ (a‖x₁‖ + c'‖x₂‖)² ≤ Γ², so all inequalities are tight
  have hac' : c' = 1 - a := by linarith
  subst hac'
  have key : ‖x₁ - x₂‖ ^ 2 = 0 := by
    have hx1 : ‖x₁‖ ^ 2 ≤ Γ ^ 2 := pow_le_pow_left₀ n1 h1 2
    have hx2 : ‖x₂‖ ^ 2 ≤ Γ ^ 2 := pow_le_pow_left₀ n2 h2 2
    have hpos : 0 < a * (1 - a) := mul_pos ha hc
    -- Γ² = a²‖x₁‖² + 2a(1-a)⟪x₁,x₂⟫ + (1-a)²‖x₂‖²
    -- ‖x₁ - x₂‖² = ‖x₁‖² + ‖x₂‖² - 2⟪x₁,x₂⟫
    -- a(1-a)‖x₁-x₂‖² = a‖x₁‖² + (1-a)‖x₂‖² - Γ² ≤ 0
    have : a * (1 - a) * ‖x₁ - x₂‖ ^ 2 ≤ 0 := by nlinarith
    have hnn := sq_nonneg ‖x₁ - x₂‖
    nlinarith
  have hx : x₁ = x₂ :=
    sub_eq_zero.mp (norm_eq_zero.mp (pow_eq_zero_iff (n := 2) (by norm_num) |>.mp key))
  subst hx
  constructor <;> (rw [← add_smul, show a + (1 - a) = 1 by ring, one_smul])

/-- **Lemma X.** If `b` has a nonzero orthogonal vector (e.g. `finrank ≥ 2`), the extreme points
of the cap are exactly its norm-`Γ` points (the lossless cap `S_Γ(b)`). -/
theorem extremePoints_cap {b d : V} {Γ c : ℝ} (hd : d ≠ 0) (hbd : ⟪b, d⟫ = 0) :
    (cap b Γ c).extremePoints ℝ = {T | T ∈ cap b Γ c ∧ ‖T‖ = Γ} := by
  ext T
  constructor
  · intro hT
    have hTc := (mem_extremePoints.mp hT).1
    refine ⟨hTc, ?_⟩
    rcases eq_or_lt_of_le hTc.1 with h | h
    · exact h
    · exact absurd hT (not_mem_extremePoints_of_norm_lt hd hbd h)
  · rintro ⟨hT, hn⟩
    exact mem_extremePoints_of_norm_eq hT hn

/-- The exceptional case also admits a lossless maximizer (so uniqueness genuinely fails there):
if `y = -κ b`, `‖b‖ = 1`, `0 ≤ δ ≤ π`... we give the explicit boundary point
`Γ (cos δ b + sin δ e)` with `e` a unit vector orthogonal to `b`. -/
theorem isMaxOn_cap_of_antiRay_boundary {b e y : V} {Γ δ : ℝ} (hb : ‖b‖ = 1) (he : ‖e‖ = 1)
    (hbe : ⟪b, e⟫ = 0) (hΓ : 0 ≤ Γ) (hy : AntiRay b y) :
    let T := Γ • (Real.cos δ • b + Real.sin δ • e)
    T ∈ cap b Γ (Γ * Real.cos δ) ∧ ‖T‖ = Γ ∧
    IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T := by
  intro T
  obtain ⟨κ, hκ, rfl⟩ := hy
  have hbb : ⟪b, b⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hb]; norm_num
  have hee : ⟪e, e⟫ = 1 := by rw [real_inner_self_eq_norm_sq, he]; norm_num
  have heb : ⟪e, b⟫ = 0 := by rw [real_inner_comm]; exact hbe
  have hbT : ⟪b, T⟫ = Γ * Real.cos δ := by
    simp only [T, real_inner_smul_right, inner_add_right, hbb, hbe]; ring
  have hnT : ‖T‖ = Γ := by
    have : ‖T‖ ^ 2 = Γ ^ 2 := by
      rw [← real_inner_self_eq_norm_sq]
      simp only [T, real_inner_smul_right, real_inner_smul_left, inner_add_right,
        inner_add_left, hbb, hbe, heb, hee]
      have := Real.sin_sq_add_cos_sq δ
      nlinarith
    have := norm_nonneg T
    nlinarith [sq_nonneg (‖T‖ - Γ), sq_nonneg (‖T‖ + Γ)]
  refine ⟨⟨hnT.le, hbT.ge⟩, hnT, ?_⟩
  rw [isMaxOn_iff]
  intro S hS
  simp only [real_inner_smul_left, neg_mul, hbT]
  nlinarith [hS.2]

/-! ## Existence of a maximizer (finite dimension) -/

theorem isClosed_cap (b : V) (Γ c : ℝ) : IsClosed (cap b Γ c) := by
  have h1 : IsClosed {T : V | ‖T‖ ≤ Γ} := isClosed_le continuous_norm continuous_const
  have h2 : IsClosed {T : V | c ≤ ⟪b, T⟫} :=
    isClosed_le continuous_const (continuous_const.inner continuous_id)
  exact h1.inter h2

theorem isCompact_cap [ProperSpace V] (b : V) (Γ c : ℝ) : IsCompact (cap b Γ c) := by
  apply Metric.isCompact_of_isClosed_isBounded (isClosed_cap b Γ c)
  refine (Metric.isBounded_closedBall (x := (0 : V)) (r := Γ)).subset ?_
  intro T hT
  simpa [Metric.mem_closedBall, dist_zero_right] using hT.1

/-- With `‖b‖ = 1`, `Γ ≥ 0` and `cos δ ≤ 1`, the point `Γ b` lies in the cap. -/
theorem smul_mem_cap {b : V} {Γ δ : ℝ} (hb : ‖b‖ = 1) (hΓ : 0 ≤ Γ) :
    Γ • b ∈ cap b Γ (Γ * Real.cos δ) := by
  have hbb : ⟪b, b⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hb]; norm_num
  refine ⟨by rw [norm_smul, hb, mul_one, Real.norm_of_nonneg hΓ], ?_⟩
  rw [real_inner_smul_right, hbb, mul_one]
  exact mul_le_of_le_one_right hΓ (Real.cos_le_one δ)

theorem exists_isMaxOn_cap [ProperSpace V] {b : V} (y : V) {Γ δ : ℝ} (hb : ‖b‖ = 1)
    (hΓ : 0 ≤ Γ) : ∃ T ∈ cap b Γ (Γ * Real.cos δ),
      IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T :=
  (isCompact_cap b Γ _).exists_isMaxOn ⟨_, smul_mem_cap hb hΓ⟩
    (continuous_const.inner continuous_id).continuousOn

/-! ## Headline: C-3 in `ℝ³` -/

/-- **C-3 (headline).** In `ℝ³ = EuclideanSpace ℝ (Fin 3)`, with `‖b‖ = 1`, `0 < δ < π/2`,
`Γ > 0`, and `K = {T | ‖T‖ ≤ Γ ∧ Γ cos δ ≤ ⟪b,T⟫}`:
1. a maximizer of `⟪y,·⟫` over `K` exists;
2. if `y ∉ -ℝ≥0 b`, every maximizer has `‖T‖ = Γ`;
3. if `y ∉ -ℝ≥0 b`, the maximizer is unique;
4. if `y ∈ -ℝ≥0 b` (including `y = 0`), there is a maximizer with `‖T‖ < Γ` (the exception is
   genuine). -/
theorem C3_headline (y b : EuclideanSpace ℝ (Fin 3)) {Γ δ : ℝ} (hb : ‖b‖ = 1) (hΓ : 0 < Γ)
    (hδ0 : 0 < δ) (hδ1 : δ < Real.pi / 2) :
    (∃ T ∈ cap b Γ (Γ * Real.cos δ), IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T) ∧
    (¬ AntiRay b y → ∀ T ∈ cap b Γ (Γ * Real.cos δ),
        IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T → ‖T‖ = Γ) ∧
    (¬ AntiRay b y → ∀ T₁ ∈ cap b Γ (Γ * Real.cos δ), ∀ T₂ ∈ cap b Γ (Γ * Real.cos δ),
        IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T₁ →
        IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T₂ → T₁ = T₂) ∧
    (AntiRay b y → ∃ T ∈ cap b Γ (Γ * Real.cos δ),
        IsMaxOn (fun T => ⟪y, T⟫) (cap b Γ (Γ * Real.cos δ)) T ∧ ‖T‖ < Γ) := by
  have hb0 : b ≠ 0 := by intro h; rw [h, norm_zero] at hb; exact zero_ne_one hb
  have hcos : 0 ≤ Real.cos δ := (Real.cos_pos_of_mem_Ioo ⟨by linarith, hδ1⟩).le
  refine ⟨exists_isMaxOn_cap y hb hΓ.le, ?_, ?_, ?_⟩
  · intro hy T hT hmax; exact norm_eq_of_isMaxOn_cap hb0 hy hT hmax
  · intro hy T₁ h1 T₂ h2 hx1 hx2; exact isMaxOn_cap_unique hb0 hy h1 h2 hx1 hx2
  · intro hy
    obtain ⟨hm, hx⟩ := isMaxOn_cap_of_antiRay (δ := δ) hb hΓ.le hcos hy
    exact ⟨_, hm, hx, norm_lt_of_sharp hb hΓ hδ0 hδ1⟩

end LcvxPositive
