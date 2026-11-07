import LcvxObstruction.Positive.Cap

/-!
# Positive side, Tier 2: primer-vector geometry (Prop. C-D1, C-D3' pieces)

Source: `math/04` §5.3 and §10; blueprint P11–P15.

* `primer a c t = a + t • c` (the affine primer `p = -λ_v`).
* `degenerate a c b = {t | p(t) ∈ -ℝ≥0 b(t)}` (the set `D` of Theorem C-S).
* `primer_zero_subsingleton` (C-D1(a)), `degenerate_subset_of_dependent` (C-D1(b)),
  `degenerate_subset_of_independent` (C-D1(c)), `degenerate_subset` (the general inclusion
  `D ⊆ Z ∪ {b = -p/‖p‖}`).
* `volume_degenerate_eq_zero_of_ND` : (ND1) + (ND2) ⇒ `|D ∩ [0,tf]| = 0` (the measure-theoretic
  core of Corollary C-D2).
* `x_div_one_add_sq_sq_le` (P15): `x/(1+x²)² ≤ 3√3/16`.
-/

open scoped RealInnerProductSpace
open Set MeasureTheory

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- The affine primer vector `p(t) = a + t c`. -/
def primer (a c : V) (t : ℝ) : V := a + t • c

/-- The degenerate set `D = {t | p(t) ∈ -ℝ≥0 b(t)}`. -/
def degenerate (a c : V) (b : ℝ → V) : Set ℝ := {t | AntiRay (b t) (primer a c t)}

/-- **P11 = C-D1(a).** If `(a,c) ≠ 0` the primer vanishes at most once. -/
theorem primer_zero_subsingleton {a c : V} (h : ¬ (a = 0 ∧ c = 0)) :
    Set.Subsingleton {t | primer a c t = 0} := by
  intro t ht t' ht'
  have ht : a + t • c = 0 := ht
  have ht' : a + t' • c = 0 := ht'
  by_contra hne
  have h1 : (t - t') • c = 0 := by
    calc (t - t') • c = (a + t • c) - (a + t' • c) := by rw [sub_smul]; abel
      _ = 0 := by rw [ht, ht', sub_zero]
  have hc : c = 0 := (smul_eq_zero.mp h1).resolve_left (sub_ne_zero.mpr hne)
  have ha : a = 0 := by rw [hc, smul_zero, add_zero] at ht; exact ht
  exact h ⟨ha, hc⟩

/-- For a unit axis, a nonzero primer on the anti-ray determines the axis: `b = -p/‖p‖`. -/
theorem eq_neg_normalize_of_antiRay {b p : V} (hb : ‖b‖ = 1) (hp : p ≠ 0) (h : AntiRay b p) :
    b = -(‖p‖⁻¹ • p) := by
  obtain ⟨κ, hκ, rfl⟩ := h
  have hκ0 : κ ≠ 0 := by rintro rfl; simp at hp
  have hn : ‖-κ • b‖ = κ := by rw [norm_smul, hb, mul_one, Real.norm_eq_abs, abs_neg, abs_of_nonneg hκ]
  rw [hn, smul_smul, ← neg_smul, inv_mul_eq_div, neg_div, neg_neg, div_self hκ0, one_smul]

/-- General inclusion: for a unit axis, `D ⊆ {p = 0} ∪ {b = -p/‖p‖}`. -/
theorem degenerate_subset {a c : V} {b : ℝ → V} (hb : ∀ t, ‖b t‖ = 1) :
    degenerate a c b ⊆ {t | primer a c t = 0} ∪ {t | b t = -(‖primer a c t‖⁻¹ • primer a c t)} := by
  intro t ht
  by_cases hp : primer a c t = 0
  · exact Or.inl hp
  · exact Or.inr (eq_neg_normalize_of_antiRay (hb t) hp ht)

/-- **P13 = C-D1(c).** For linearly independent `a, c`, the primer never vanishes and
`D ⊆ {b = β}` with the gnomonic line `β(t) = -(a+tc)/‖a+tc‖`. -/
theorem degenerate_subset_of_independent {a c : V} {b : ℝ → V} (hb : ∀ t, ‖b t‖ = 1)
    (hind : LinearIndependent ℝ ![a, c]) :
    degenerate a c b ⊆ {t | b t = -(‖primer a c t‖⁻¹ • primer a c t)} := by
  intro t ht
  have hp : primer a c t ≠ 0 := by
    intro h0
    have := (LinearIndependent.pair_iff.mp hind) 1 t (by simpa [primer] using h0)
    exact one_ne_zero this.1
  exact eq_neg_normalize_of_antiRay (hb t) hp ht

/-- If the primer is everywhere a multiple of a fixed unit vector `e`, the axis on `D \ Z`
is `±e`. -/
theorem eq_or_eq_neg_of_antiRay_smul {b e : V} {φ : ℝ} (hb : ‖b‖ = 1) (he : ‖e‖ = 1)
    (hφ : φ ≠ 0) (h : AntiRay b (φ • e)) : b = e ∨ b = -e := by
  have hp : φ • e ≠ 0 := smul_ne_zero hφ (by intro h0; rw [h0, norm_zero] at he; exact zero_ne_one he)
  have := eq_neg_normalize_of_antiRay hb hp h
  rw [norm_smul, he, mul_one, smul_smul, Real.norm_eq_abs] at this
  rcases lt_or_gt_of_ne hφ with hneg | hpos
  · left
    rw [abs_of_neg hneg, inv_neg, neg_mul, inv_mul_cancel₀ hφ] at this
    simpa using this
  · right
    rw [abs_of_pos hpos, inv_mul_cancel₀ hφ] at this
    simpa using this

/-- For linearly dependent `(a,c) ≠ 0` the primer is a multiple of one unit vector. -/
theorem exists_unit_of_dependent {a c : V} (h : ¬ (a = 0 ∧ c = 0))
    (hdep : ¬ LinearIndependent ℝ ![a, c]) :
    ∃ e : V, ‖e‖ = 1 ∧ ∀ t, ∃ φ : ℝ, primer a c t = φ • e := by
  rw [LinearIndependent.pair_iff] at hdep
  push Not at hdep
  obtain ⟨s, u, hsu, hne⟩ := hdep
  by_cases ha : a = 0
  · have hc : c ≠ 0 := fun hc => h ⟨ha, hc⟩
    refine ⟨‖c‖⁻¹ • c, by rw [norm_smul, norm_inv, norm_norm, inv_mul_cancel₀ (norm_ne_zero_iff.mpr hc)], ?_⟩
    intro t
    refine ⟨t * ‖c‖, ?_⟩
    rw [smul_smul, mul_assoc, mul_inv_cancel₀ (norm_ne_zero_iff.mpr hc), mul_one]
    simp [primer, ha]
  · have hu : u ≠ 0 := by
      intro hu0
      rw [hu0, zero_smul, add_zero] at hsu
      exact hne ((smul_eq_zero.mp hsu).resolve_right ha) hu0
    have hcmul : c = (-(s / u)) • a := by
      have : u • c = -(s • a) := eq_neg_of_add_eq_zero_right hsu
      calc c = u⁻¹ • (u • c) := by rw [smul_smul, inv_mul_cancel₀ hu, one_smul]
        _ = (-(s / u)) • a := by rw [this, smul_neg, smul_smul, neg_smul, div_eq_inv_mul]
    refine ⟨‖a‖⁻¹ • a, by rw [norm_smul, norm_inv, norm_norm, inv_mul_cancel₀ (norm_ne_zero_iff.mpr ha)], ?_⟩
    intro t
    refine ⟨(1 + t * (-(s / u))) * ‖a‖, ?_⟩
    rw [smul_smul, mul_assoc, mul_inv_cancel₀ (norm_ne_zero_iff.mpr ha), mul_one]
    simp only [primer, hcmul, smul_smul, add_smul, one_smul]

/-- **P12 = C-D1(b).** For linearly dependent `(a,c) ≠ 0`, `D ⊆ Z ∪ b⁻¹{e} ∪ b⁻¹{-e}`. -/
theorem degenerate_subset_of_dependent {a c : V} {b : ℝ → V} (hb : ∀ t, ‖b t‖ = 1)
    (h : ¬ (a = 0 ∧ c = 0)) (hdep : ¬ LinearIndependent ℝ ![a, c]) :
    ∃ e : V, ‖e‖ = 1 ∧
      degenerate a c b ⊆ {t | primer a c t = 0} ∪ ({t | b t = e} ∪ {t | b t = -e}) := by
  obtain ⟨e, he, hφ⟩ := exists_unit_of_dependent h hdep
  refine ⟨e, he, ?_⟩
  intro t ht
  obtain ⟨φ, hp⟩ := hφ t
  by_cases h0 : primer a c t = 0
  · exact Or.inl h0
  · right
    have hφ0 : φ ≠ 0 := by rintro rfl; rw [zero_smul] at hp; exact h0 hp
    have ht' : AntiRay (b t) (φ • e) := hp ▸ ht
    exact eq_or_eq_neg_of_antiRay_smul (hb t) he hφ0 ht'

/-- Non-degeneracy (ND1): `b` does not dwell, i.e. every level set meets `[0,tf]` in a null set. -/
def ND1 (b : ℝ → V) (tf : ℝ) : Prop := ∀ e : V, volume ({t | b t = e} ∩ Icc 0 tf) = 0

/-- Non-degeneracy (ND2): `b` does not follow a gnomonic line `(a+tc)/‖a+tc‖`
(`a, c` independent) on a set of positive measure. -/
def ND2 (b : ℝ → V) (tf : ℝ) : Prop :=
  ∀ a c : V, LinearIndependent ℝ ![a, c] →
    volume ({t | b t = ‖primer a c t‖⁻¹ • primer a c t} ∩ Icc 0 tf) = 0

/-- **Core of Corollary C-D2 (P18, measure part).** Under (ND1) and (ND2), for a unit axis and
`(a,c) ≠ 0`, the degenerate set is null in `[0,tf]`. -/
theorem volume_degenerate_eq_zero_of_ND {a c : V} {b : ℝ → V} {tf : ℝ} (hb : ∀ t, ‖b t‖ = 1)
    (h : ¬ (a = 0 ∧ c = 0)) (h1 : ND1 b tf) (h2 : ND2 b tf) :
    volume (degenerate a c b ∩ Icc 0 tf) = 0 := by
  have hZ : volume {t | primer a c t = 0} = 0 := (primer_zero_subsingleton h).measure_zero _
  by_cases hind : LinearIndependent ℝ ![a, c]
  · have hind' : LinearIndependent ℝ ![-a, -c] := by
      rw [LinearIndependent.pair_iff] at hind ⊢
      intro s u hsu
      have := hind (-s) (-u) (by rw [neg_smul, neg_smul, ← smul_neg, ← smul_neg]; exact hsu)
      exact ⟨neg_eq_zero.mp this.1, neg_eq_zero.mp this.2⟩
    have hset : degenerate a c b ∩ Icc 0 tf ⊆
        {t | b t = ‖primer (-a) (-c) t‖⁻¹ • primer (-a) (-c) t} ∩ Icc 0 tf := by
      rintro t ⟨ht, ht'⟩
      refine ⟨?_, ht'⟩
      have := degenerate_subset_of_independent hb hind ht
      have hp : primer (-a) (-c) t = -primer a c t := by simp [primer, smul_neg]; abel
      simp only [mem_ofPred_eq] at this ⊢
      rw [hp, norm_neg, smul_neg]
      exact this
    exact measure_mono_null hset (h2 _ _ hind')
  · obtain ⟨e, -, hsub⟩ := degenerate_subset_of_dependent hb h hind
    have hset : degenerate a c b ∩ Icc 0 tf ⊆
        {t | primer a c t = 0} ∪ (({t | b t = e} ∩ Icc 0 tf) ∪ ({t | b t = -e} ∩ Icc 0 tf)) := by
      rintro t ⟨ht, ht'⟩
      rcases hsub ht with h0 | h0 | h0
      · exact Or.inl h0
      · exact Or.inr (Or.inl ⟨h0, ht'⟩)
      · exact Or.inr (Or.inr ⟨h0, ht'⟩)
    refine measure_mono_null hset ?_
    exact measure_union_null hZ (measure_union_null (h1 e) (h1 (-e)))

/-- **P15.** `x/(1+x²)² ≤ 3√3/16` for all real `x` (peak angular acceleration of a gnomonic
line, `math/04` C-3D'(c)). -/
theorem x_div_one_add_sq_sq_le (x : ℝ) : x / (1 + x ^ 2) ^ 2 ≤ 3 * Real.sqrt 3 / 16 := by
  have hs : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
  have hs0 : 0 < Real.sqrt 3 := Real.sqrt_pos.mpr (by norm_num)
  have hpos : 0 < (1 + x ^ 2) ^ 2 := by positivity
  rw [div_le_iff₀ hpos]
  -- 3√3 (1+x²)² - 16 x = 3√3 (x - √3/3)² (x² + (2√3/3) x + 3)
  have hq : 0 < x ^ 2 + (2 * Real.sqrt 3 / 3) * x + 3 := by
    nlinarith [sq_nonneg (x + Real.sqrt 3 / 3)]
  have key : 3 * Real.sqrt 3 / 16 * (1 + x ^ 2) ^ 2 - x =
      3 * Real.sqrt 3 / 16 * ((x - Real.sqrt 3 / 3) ^ 2 * (x ^ 2 + (2 * Real.sqrt 3 / 3) * x + 3)) := by
    have h3 : Real.sqrt 3 ^ 3 = 3 * Real.sqrt 3 := by rw [pow_succ, hs]
    have h4 : Real.sqrt 3 ^ 4 = 9 := by rw [show (4:ℕ) = 2 * 2 from rfl, pow_mul, hs]; norm_num
    ring_nf
    rw [hs, h3, h4]
    ring
  have : 0 ≤ 3 * Real.sqrt 3 / 16 * ((x - Real.sqrt 3 / 3) ^ 2 * (x ^ 2 + (2 * Real.sqrt 3 / 3) * x + 3)) := by
    positivity
  linarith

/-- Equality in P15 at `x = 1/√3`. -/
theorem x_div_one_add_sq_sq_eq : (1 / Real.sqrt 3) / (1 + (1 / Real.sqrt 3) ^ 2) ^ 2
    = 3 * Real.sqrt 3 / 16 := by
  have hs : Real.sqrt 3 ^ 2 = 3 := Real.sq_sqrt (by norm_num)
  have hs0 : Real.sqrt 3 ≠ 0 := (Real.sqrt_pos.mpr (by norm_num)).ne'
  field_simp
  rw [hs]
  ring_nf

end LcvxPositive
