import LcvxObstruction.Positive.Primer

/-!
# Positive side, Tier 3: strong Theorem C under PMP (C-S, C-D2)

Source: `math/04` §5; blueprint P16–P18 and the optional min-throttle parts.

**The only external hypothesis is PMP**, packaged as the structure `PMPConclusion`, whose fields
are exactly conclusions (i)–(ii) of (H-PMP) in `math/04` §5.1 for the relaxed fixed-attitude
problem `P₁(b;θ)`:

* (i) adjoint equations `λ̇_r = 0`, `λ̇_v = -λ_r` (the `λ_m` equation is not used);
* (ii) for a.e. `t ∈ [0,tf]`, the optimal control `(T(t), Γ(t))` minimizes the
  control-dependent part of the Hamiltonian
  `λ₀ Γ + ⟪λ_v, T⟫/m - α λ_m Γ` over `U(t) = {(S,G) | S ∈ K_G(b t), ρ₁ ≤ G ≤ ρ₂}`.

It is passed as an ordinary argument; nothing here is an `axiom`.

Results:
* `PMPConclusion.neg_lamV_eq`  : the primer `p = -λ_v` is affine, `p(t) = a + t c` (any `b`, any mass).
* `PMPConclusion.isMaxOn_ae`   : `T(t)` maximizes `⟪p(t),·⟫` over `K_{Γ(t)}(b t)` a.e. (Lemma J).
* `PMPConclusion.lossless_ae_off_degenerate` (**C-S(1)**, P16).
* `PMPConclusion.lossless_ae_of_null_degenerate` (**C-S(4)**, P17).
* `PMPConclusion.lossless_ae_of_ND` (**C-D2**, P18).
* `PMPConclusion.min_throttle_of_antiRay` (**C-S(3)** pointwise), `min_throttle_of_primer_zero`
  (**C-S(2)**), `lossy_subset_degenerate_minThrottle` (**C-S(3)**: `L ⊆ D ∩ {Γ = ρ₁}` a.e.).
-/

open scoped RealInnerProductSpace
open Set MeasureTheory Filter

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- **(H-PMP)(i)–(ii)**, the conclusions of the Pontryagin maximum principle used in `math/04` §5,
for a relaxed optimum `(T, Γ)` with mass history `m`, attitude `b`, cone half-angle `δ`, throttle
bounds `ρ₁ ≤ Γ ≤ ρ₂`, mass-flow coefficient `α` on `[0, tf]`.
The adjoint ODEs are stated with `HasDerivAt` on all of `ℝ` (their solutions are affine, so this
is equivalent to the absolutely-continuous a.e. formulation after affine extension). -/
structure PMPConclusion (b T : ℝ → V) (Γ m : ℝ → ℝ) (δ ρ₁ ρ₂ α tf : ℝ) where
  /-- abnormal/normal multiplier `λ₀ ∈ {0,1}` (only `λ₀ ≥ 0` is used) -/
  lam0 : ℝ
  lamR : ℝ → V
  lamV : ℝ → V
  lamM : ℝ → ℝ
  lam0_nonneg : 0 ≤ lam0
  /-- adjoint equation `λ̇_r = 0` -/
  adj_r : ∀ t, HasDerivAt lamR 0 t
  /-- adjoint equation `λ̇_v = -λ_r` -/
  adj_v : ∀ t, HasDerivAt lamV (-lamR t) t
  /-- minimum condition (ii), control-dependent part of the Hamiltonian -/
  min_ae : ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ∀ (S : V) (G : ℝ),
    S ∈ cap (b t) G (G * Real.cos δ) → ρ₁ ≤ G → G ≤ ρ₂ →
    lam0 * Γ t + ⟪lamV t, T t⟫ / m t - α * lamM t * Γ t ≤
      lam0 * G + ⟪lamV t, S⟫ / m t - α * lamM t * G

/-- Feasibility of `(T, Γ)` for the relaxed problem (pointwise control constraints, a.e.). -/
def RelaxedControlFeasible (b T : ℝ → V) (Γ : ℝ → ℝ) (δ ρ₁ ρ₂ tf : ℝ) : Prop :=
  ∀ᵐ t ∂(volume.restrict (Icc 0 tf)),
    T t ∈ cap (b t) (Γ t) (Γ t * Real.cos δ) ∧ ρ₁ ≤ Γ t ∧ Γ t ≤ ρ₂

namespace PMPConclusion

variable {b T : ℝ → V} {Γ m : ℝ → ℝ} {δ ρ₁ ρ₂ α tf : ℝ}
variable (h : PMPConclusion b T Γ m δ ρ₁ ρ₂ α tf)

/-- Primer intercept `a = p(0) = -λ_v(0)`. -/
def a : V := -h.lamV 0
/-- Primer slope `c = λ_r` (constant). -/
def c : V := h.lamR 0

theorem lamR_eq (t : ℝ) : h.lamR t = h.c :=
  is_const_of_deriv_eq_zero (fun s => (h.adj_r s).differentiableAt) (fun s => (h.adj_r s).deriv) t 0

/-- **Affine primer.** `p(t) := -λ_v(t) = a + t c`, for every attitude profile and any mass. -/
theorem neg_lamV_eq (t : ℝ) : -h.lamV t = primer h.a h.c t := by
  have hd : ∀ s, HasDerivAt (fun s => h.lamV s + s • h.c) 0 s := by
    intro s
    have := (h.adj_v s).add ((hasDerivAt_id s).smul_const h.c)
    rw [h.lamR_eq s, one_smul, neg_add_cancel] at this
    exact this
  have := is_const_of_deriv_eq_zero (fun s => (hd s).differentiableAt)
    (fun s => (hd s).deriv) t 0
  simp only [zero_smul, add_zero] at this
  simp only [primer, a]
  rw [← this]; abel

theorem lamV_eq (t : ℝ) : h.lamV t = -primer h.a h.c t := by
  rw [← h.neg_lamV_eq t, neg_neg]

/-- **Lemma J under PMP.** For a.e. `t`, `T(t)` maximizes `⟪p(t),·⟫` over `K_{Γ(t)}(b t)`. -/
theorem isMaxOn_ae (hm : ∀ t, 0 < m t)
    (hΓ : ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ρ₁ ≤ Γ t ∧ Γ t ≤ ρ₂) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)),
      IsMaxOn (fun S => ⟪primer h.a h.c t, S⟫) (cap (b t) (Γ t) (Γ t * Real.cos δ)) (T t) := by
  filter_upwards [h.min_ae, hΓ] with t hmin hf
  rw [isMaxOn_iff]
  intro S hS
  have h1 := hmin S (Γ t) hS hf.1 hf.2
  have h2 : ⟪h.lamV t, T t⟫ / m t ≤ ⟪h.lamV t, S⟫ / m t := by linarith
  have h3 : ⟪h.lamV t, T t⟫ ≤ ⟪h.lamV t, S⟫ := (div_le_div_iff_of_pos_right (hm t)).mp h2
  rw [h.lamV_eq t, inner_neg_left, inner_neg_left] at h3
  linarith

/-- **C-S(1) (P16).** Off the degenerate set `D = {t | p(t) ∈ -ℝ≥0 b(t)}`, a.e. the relaxed
optimum is lossless and `T(t)` is the unique pointwise maximizer. -/
theorem lossless_ae_off_degenerate (hb : ∀ t, b t ≠ 0) (hm : ∀ t, 0 < m t)
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), t ∉ degenerate h.a h.c b →
      ‖T t‖ = Γ t ∧ ∀ S ∈ cap (b t) (Γ t) (Γ t * Real.cos δ),
        IsMaxOn (fun S => ⟪primer h.a h.c t, S⟫) (cap (b t) (Γ t) (Γ t * Real.cos δ)) S →
        S = T t := by
  filter_upwards [h.isMaxOn_ae hm (hfeas.mono fun t ht => ht.2), hfeas] with t hmax hf hD
  refine ⟨norm_eq_of_isMaxOn_cap (hb t) hD hf.1 hmax, ?_⟩
  intro S hS hSmax
  exact isMaxOn_cap_unique (hb t) hD hS hf.1 hSmax hmax

/-- **C-S(4) (P17).** If `D ∩ [0,tf]` is null, the relaxed optimum is lossless a.e. on `[0,tf]`,
and (L8) it is pointwise feasible for the original nonconvex problem `P₀`. -/
theorem lossless_ae_of_null_degenerate (hb : ∀ t, b t ≠ 0) (hm : ∀ t, 0 < m t)
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf)
    (hD : volume (degenerate h.a h.c b ∩ Icc 0 tf) = 0) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ‖T t‖ = Γ t ∧
      ρ₁ ≤ ‖T t‖ ∧ ‖T t‖ ≤ ρ₂ ∧ ‖T t‖ * Real.cos δ ≤ ⟪b t, T t⟫ := by
  have hnot : ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), t ∉ degenerate h.a h.c b := by
    rw [ae_iff]
    simp only [not_not, ofPred_mem_eq]
    rw [Measure.restrict_apply' measurableSet_Icc]
    exact hD
  filter_upwards [h.lossless_ae_off_degenerate hb hm hfeas, hnot, hfeas] with t h1 h2 hf
  have hn := (h1 h2).1
  exact ⟨hn, original_feasible_of_lossless hf.1 hn hf.2.1 hf.2.2⟩

/-- **C-D2 (P18).** Under (ND1), (ND2), a unit axis and a nonzero primer `(a,c) ≠ 0`, every
relaxed optimum is lossless a.e. (and pointwise `P₀`-feasible). -/
theorem lossless_ae_of_ND (hb : ∀ t, ‖b t‖ = 1) (hm : ∀ t, 0 < m t)
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf)
    (hac : ¬ (h.a = 0 ∧ h.c = 0)) (h1 : ND1 b tf) (h2 : ND2 b tf) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ‖T t‖ = Γ t ∧
      ρ₁ ≤ ‖T t‖ ∧ ‖T t‖ ≤ ρ₂ ∧ ‖T t‖ * Real.cos δ ≤ ⟪b t, T t⟫ := by
  have hb0 : ∀ t, b t ≠ 0 := fun t h0 => by
    have := hb t; rw [h0, norm_zero] at this; exact zero_ne_one this
  exact h.lossless_ae_of_null_degenerate hb0 hm hfeas
    (volume_degenerate_eq_zero_of_ND hb hac h1 h2)

/-- **C-S(3), pointwise part.** Constant mass (`α = 0`), `cos δ > 0`: wherever
`p(t) = -κ b(t)` with `κ > 0`, the optimal throttle is at its minimum, `Γ(t) = ρ₁`. -/
theorem min_throttle_of_antiRay (hα : α = 0) (hb : ∀ t, ‖b t‖ = 1) (hm : ∀ t, 0 < m t)
    (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂) (hcos : 0 < Real.cos δ)
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ∀ κ : ℝ, 0 < κ →
      primer h.a h.c t = -κ • b t → Γ t = ρ₁ := by
  filter_upwards [h.min_ae, hfeas] with t hmin hf κ hκ hp
  subst hα
  have hbb : ⟪b t, b t⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hb t]; norm_num
  have hlv : h.lamV t = κ • b t := by rw [h.lamV_eq t, hp, neg_smul, neg_neg]
  have hS := (isMaxOn_cap_of_antiRay (y := (0 : V)) (δ := δ) (hb t) hρ hcos.le ⟨0, le_rfl, by simp⟩).1
  have h1 := hmin _ ρ₁ hS le_rfl hρ12
  simp only [zero_mul, sub_zero, hlv, real_inner_smul_left, real_inner_smul_right, hbb,
    mul_one] at h1
  have hmt := hm t
  have e1 : κ * (Γ t * Real.cos δ) / m t ≤ κ * ⟪b t, T t⟫ / m t :=
    div_le_div_of_nonneg_right (mul_le_mul_of_nonneg_left hf.1.2 hκ.le) hmt.le
  set q : ℝ := κ * Real.cos δ / m t with hq
  have hq0 : 0 < q := by positivity
  have r1 : κ * (Γ t * Real.cos δ) / m t = Γ t * q := by rw [hq]; ring
  have r2 : ρ₁ * Real.cos δ * κ / m t = ρ₁ * q := by rw [hq]; ring
  rw [r1] at e1
  rw [r2] at h1
  have : (h.lam0 + q) * Γ t ≤ (h.lam0 + q) * ρ₁ := by nlinarith
  have hle : Γ t ≤ ρ₁ := le_of_mul_le_mul_left this (by linarith [h.lam0_nonneg])
  exact le_antisymm hle hf.2.1

/-- **C-S(2).** Constant mass (`α = 0`), PMP nontriviality `(λ₀, λ_r, λ_v) ≢ 0`, and `p ≡ 0`
(`a = c = 0`): then `Γ = ρ₁` a.e. -/
theorem min_throttle_of_primer_zero (hα : α = 0) (hb : ∀ t, ‖b t‖ = 1)
    (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂)
    (hnontriv : h.lam0 ≠ 0 ∨ (∃ t, h.lamR t ≠ 0) ∨ (∃ t, h.lamV t ≠ 0))
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf) (ha : h.a = 0) (hc : h.c = 0) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), Γ t = ρ₁ := by
  have hR : ∀ t, h.lamR t = 0 := fun t => by rw [h.lamR_eq, hc]
  have hV : ∀ t, h.lamV t = 0 := fun t => by rw [h.lamV_eq, ha, hc]; simp [primer]
  have hl0 : 0 < h.lam0 := by
    rcases hnontriv with h0 | ⟨t, ht⟩ | ⟨t, ht⟩
    · exact lt_of_le_of_ne h.lam0_nonneg (Ne.symm h0)
    · exact absurd (hR t) ht
    · exact absurd (hV t) ht
  filter_upwards [h.min_ae, hfeas] with t hmin hf
  subst hα
  have h1 := hmin (ρ₁ • b t) ρ₁ (smul_mem_cap (hb t) hρ) le_rfl hρ12
  simp only [hV, inner_zero_left, zero_div, add_zero, zero_mul, sub_zero] at h1
  exact le_antisymm (le_of_mul_le_mul_left h1 hl0) hf.2.1

/-- **C-S(3).** Constant mass (`α = 0`), unit axis, `cos δ > 0`, PMP nontriviality: the lossy set
is contained, up to a null set, in `D ∩ {Γ = ρ₁}`. -/
theorem lossy_subset_degenerate_minThrottle (hα : α = 0) (hb : ∀ t, ‖b t‖ = 1)
    (hm : ∀ t, 0 < m t) (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂) (hcos : 0 < Real.cos δ)
    (hnontriv : h.lam0 ≠ 0 ∨ (∃ t, h.lamR t ≠ 0) ∨ (∃ t, h.lamV t ≠ 0))
    (hfeas : RelaxedControlFeasible b T Γ δ ρ₁ ρ₂ tf) :
    ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ‖T t‖ < Γ t →
      t ∈ degenerate h.a h.c b ∧ Γ t = ρ₁ := by
  have hb0 : ∀ t, b t ≠ 0 := fun t h0 => by
    have := hb t; rw [h0, norm_zero] at this; exact zero_ne_one this
  by_cases hac : h.a = 0 ∧ h.c = 0
  · filter_upwards [h.min_throttle_of_primer_zero hα hb hρ hρ12 hnontriv hfeas hac.1 hac.2]
      with t ht _
    refine ⟨⟨0, le_rfl, ?_⟩, ht⟩
    simp [primer, hac.1, hac.2]
  · have hZ : ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), primer h.a h.c t ≠ 0 := by
      apply ae_restrict_of_ae
      rw [ae_iff]
      simp only [not_not]
      exact (primer_zero_subsingleton hac).measure_zero _
    filter_upwards [h.isMaxOn_ae hm (hfeas.mono fun t ht => ht.2), hfeas, hZ,
      h.min_throttle_of_antiRay hα hb hm hρ hρ12 hcos hfeas] with t hmax hf hz hmin hlt
    have hD : AntiRay (b t) (primer h.a h.c t) :=
      (norm_eq_or_antiRay_of_isMaxOn_cap (hb0 t) hf.1 hmax).resolve_left hlt.ne
    refine ⟨hD, ?_⟩
    obtain ⟨κ, hκ, hp⟩ := hD
    have hκ0 : 0 < κ := lt_of_le_of_ne hκ (by rintro rfl; simp at hp; exact hz hp)
    exact hmin κ hκ0 hp

end PMPConclusion

end LcvxPositive
