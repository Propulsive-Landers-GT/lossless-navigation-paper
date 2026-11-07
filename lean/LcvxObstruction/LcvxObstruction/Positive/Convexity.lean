import LcvxObstruction.Positive.Cap
import LcvxObstruction.Positive.TVC

/-!
# Positive side: continuous-time convexity of fixed-attitude feasible sets (C-6, C-W(1), C-F)

Source: `math/04` §3 (C-W, C-F) and §8 (C-6).

Setting: constant mass `m`, gravity `g`, horizon `[0, tf]`, double-integrator dynamics written in
closed (Cauchy) form `termState`:
`r(tf) = r₀ + tf v₀ + m⁻¹ ∫ (tf-t) T + (tf²/2) g`, `v(tf) = v₀ + m⁻¹ ∫ T + tf g`.
Controls are admissible (`Adm`) when `T` and `(tf - t) T` are integrable on `[0,tf]` (always true
for bounded measurable thrust). Boundary data `θ = (r₀, v₀)`, convex terminal set `Xf`.

* `convex_feasData` : pointwise convex constraints `T t ∈ K t` a.e. ⇒ the feasible boundary-data
  set is convex.
* `convex_feasData_M3b` (**Theorem C-6**): for a given attitude profile `b(·)` and induced lateral
  thrust `F(·) ⊥ b(·)`, the exact M3b feasible set is convex — no relaxation.
* `AumannInstance` : the **only** use of Aumann's theorem, as an explicit, named hypothesis (never
  an axiom): for measurable `b`, a.e.-measurable bounded `Γ`, every admissible selection of
  `cl conv S_Γ(b)` has an admissible selection of `S_Γ(b)` with the same two moments
  `∫ T`, `∫ (tf-t) T` (Aumann's integral theorem applied to `t ↦ Ψ(t) S_{Γ(t)}(b(t)) ⊆ ℝ⁶`, with
  `Ψ(t) = [(tf-t) I; I]` injective).
* `relaxed_subset_original` (**C-W(1)**): under `AumannInstance`, every relaxed-feasible `θ` is
  original-feasible (and conversely, `original_subset_relaxed`).
* `convex_origFeas` (**C-F**): under `AumannInstance`, the exact fixed-attitude feasible set
  `F_tf(b)` is convex.
-/

open scoped RealInnerProductSpace
open Set MeasureTheory

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

/-- Admissible controls on `[0,tf]`. -/
def Adm (tf : ℝ) (T : ℝ → V) : Prop :=
  IntegrableOn T (Icc 0 tf) ∧ IntegrableOn (fun t => (tf - t) • T t) (Icc 0 tf)

/-- Terminal state of the constant-mass double integrator (Cauchy formula). -/
noncomputable def termState (tf m : ℝ) (g : V) (θ : V × V) (T : ℝ → V) : V × V :=
  (θ.1 + tf • θ.2 + m⁻¹ • (∫ t in Icc 0 tf, (tf - t) • T t) + (tf ^ 2 / 2) • g,
   θ.2 + m⁻¹ • (∫ t in Icc 0 tf, T t) + tf • g)

/-- Feasible boundary data for the pointwise constraint family `K`. -/
def feasData (tf m : ℝ) (g : V) (Xf : Set (V × V)) (K : ℝ → Set V) : Set (V × V) :=
  {θ | ∃ T, Adm tf T ∧ (∀ᵐ t ∂(volume.restrict (Icc 0 tf)), T t ∈ K t) ∧
    termState tf m g θ T ∈ Xf}

theorem Adm.comb {tf : ℝ} {T₁ T₂ : ℝ → V} (h₁ : Adm tf T₁) (h₂ : Adm tf T₂) (a b : ℝ) :
    Adm tf (fun t => a • T₁ t + b • T₂ t) := by
  refine ⟨(h₁.1.smul a).add (h₂.1.smul b), ?_⟩
  have : (fun t => (tf - t) • (a • T₁ t + b • T₂ t)) =
      fun t => a • ((tf - t) • T₁ t) + b • ((tf - t) • T₂ t) := by
    funext t; module
  rw [this]
  exact (h₁.2.smul a).add (h₂.2.smul b)

theorem integral_comb {tf : ℝ} {f₁ f₂ : ℝ → V} (h₁ : IntegrableOn f₁ (Icc 0 tf))
    (h₂ : IntegrableOn f₂ (Icc 0 tf)) (a b : ℝ) :
    ∫ t in Icc 0 tf, (a • f₁ t + b • f₂ t) =
      a • (∫ t in Icc 0 tf, f₁ t) + b • (∫ t in Icc 0 tf, f₂ t) := by
  have := integral_add (μ := volume.restrict (Icc 0 tf)) (f := fun t => a • f₁ t)
    (g := fun t => b • f₂ t) (h₁.smul a) (h₂.smul b)
  rw [this, integral_smul, integral_smul]

theorem termState_comb {tf m : ℝ} {g : V} {θ₁ θ₂ : V × V} {T₁ T₂ : ℝ → V}
    (h₁ : Adm tf T₁) (h₂ : Adm tf T₂) {a b : ℝ} (hab : a + b = 1) :
    termState tf m g (a • θ₁ + b • θ₂) (fun t => a • T₁ t + b • T₂ t) =
      a • termState tf m g θ₁ T₁ + b • termState tf m g θ₂ T₂ := by
  have hmom : (fun t => (tf - t) • (a • T₁ t + b • T₂ t)) =
      fun t => a • ((tf - t) • T₁ t) + b • ((tf - t) • T₂ t) := by
    funext t; module
  have hb : b = 1 - a := by linarith
  subst hb
  simp only [termState]
  rw [hmom, integral_comb h₁.2 h₂.2, integral_comb h₁.1 h₂.1]
  ext
  · simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd]; module
  · simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd]; module

/-- Pointwise convex constraints and a convex terminal set give a convex feasible-data set. -/
theorem convex_feasData {tf m : ℝ} {g : V} {Xf : Set (V × V)} {K : ℝ → Set V}
    (hK : ∀ t, Convex ℝ (K t)) (hXf : Convex ℝ Xf) : Convex ℝ (feasData tf m g Xf K) := by
  rintro θ₁ ⟨T₁, hA₁, hK₁, hX₁⟩ θ₂ ⟨T₂, hA₂, hK₂, hX₂⟩ a b ha hb hab
  refine ⟨fun t => a • T₁ t + b • T₂ t, hA₁.comb hA₂ a b, ?_, ?_⟩
  · filter_upwards [hK₁, hK₂] with t h1 h2 using hK t h1 h2 ha hb hab
  · rw [termState_comb hA₁ hA₂ hab]
    exact hXf hX₁ hX₂ ha hb hab

/-- **Theorem C-6 (continuous time).** For a fixed attitude profile `b` (unit) with induced lateral
thrust `F ⊥ b` (`F = -k Π_b b̈`, Lemma 8.1), the exact gimbal-torque-coupled (M3b) feasible
boundary-data set is convex. -/
theorem convex_feasData_M3b {tf m : ℝ} {g : V} {Xf : Set (V × V)} {b F : ℝ → V}
    {ρ₁ ρ₂ δ : ℝ} (hb : ∀ t, ‖b t‖ = 1) (hbF : ∀ t, ⟪b t, F t⟫ = 0)
    (hρ : 0 ≤ ρ₁) (hρ12 : ρ₁ ≤ ρ₂) (hδ0 : 0 < δ) (hδ1 : δ < Real.pi / 2)
    (hXf : Convex ℝ Xf) :
    Convex ℝ (feasData tf m g Xf (fun t => tvcSet (b t) (F t) ρ₁ ρ₂ δ)) :=
  convex_feasData (fun t => convex_tvcSet (hb t) (hbF t) hρ hρ12 hδ0 hδ1) hXf

/-! ## C-W(1) and C-F under the Aumann hypothesis -/

/-- The lossless cap `S_Γ(b) = {T | ‖T‖ = Γ, Γ cos δ ≤ ⟪b,T⟫}`. -/
def sCap (b : V) (Γ δ : ℝ) : Set V := {T | ‖T‖ = Γ ∧ Γ * Real.cos δ ≤ ⟪b, T⟫}

/-- The original (nonconvex) pointwise thrust set of `P₀(b)`. -/
def origSet (b : V) (ρ₁ ρ₂ δ : ℝ) : Set V :=
  {T | ρ₁ ≤ ‖T‖ ∧ ‖T‖ ≤ ρ₂ ∧ ‖T‖ * Real.cos δ ≤ ⟪b, T⟫}

/-- Original feasible boundary data `F_tf(b)`. -/
def origFeas (tf m : ℝ) (g : V) (Xf : Set (V × V)) (b : ℝ → V) (ρ₁ ρ₂ δ : ℝ) : Set (V × V) :=
  feasData tf m g Xf (fun t => origSet (b t) ρ₁ ρ₂ δ)

/-- Relaxed feasible boundary data (controls `(T, Γ)`, `Γ` a.e.-measurable). -/
def relFeas (tf m : ℝ) (g : V) (Xf : Set (V × V)) (b : ℝ → V) (ρ₁ ρ₂ δ : ℝ) : Set (V × V) :=
  {θ | ∃ (T : ℝ → V) (Γ : ℝ → ℝ), AEMeasurable Γ (volume.restrict (Icc 0 tf)) ∧ Adm tf T ∧
    (∀ᵐ t ∂(volume.restrict (Icc 0 tf)),
      T t ∈ cap (b t) (Γ t) (Γ t * Real.cos δ) ∧ ρ₁ ≤ Γ t ∧ Γ t ≤ ρ₂) ∧
    termState tf m g θ T ∈ Xf}

variable [MeasurableSpace V]

/-- **[Aumann], as an explicit named hypothesis.** The instance of Aumann's integral theorem
used in `math/04` §3 (C-W): for a measurable attitude `b` and an a.e.-measurable, essentially
bounded throttle `Γ`, every admissible selection of `cl conv S_{Γ(t)}(b(t))` can be replaced by an
admissible selection of `S_{Γ(t)}(b(t))` with the same moments `∫ T` and `∫ (tf - t) T` (hence the
same terminal state). It is a hypothesis of the theorems below, never an axiom. -/
def AumannInstance (tf δ : ℝ) : Prop :=
  ∀ (b : ℝ → V) (Γ : ℝ → ℝ), Measurable b → AEMeasurable Γ (volume.restrict (Icc 0 tf)) →
    (∃ R, ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), |Γ t| ≤ R) →
    ∀ T : ℝ → V, Adm tf T →
      (∀ᵐ t ∂(volume.restrict (Icc 0 tf)), T t ∈ closure (convexHull ℝ (sCap (b t) (Γ t) δ))) →
      ∃ T' : ℝ → V, Adm tf T' ∧
        (∀ᵐ t ∂(volume.restrict (Icc 0 tf)), T' t ∈ sCap (b t) (Γ t) δ) ∧
        ∫ t in Icc 0 tf, T' t = ∫ t in Icc 0 tf, T t ∧
        ∫ t in Icc 0 tf, (tf - t) • T' t = ∫ t in Icc 0 tf, (tf - t) • T t

/-- **Lemma X, hull form.** In finite dimension, if `b` has a nonzero orthogonal vector, the cap is
the closed convex hull of the lossless cap. -/
theorem cap_subset_closure_convexHull_sCap [FiniteDimensional ℝ V] {b d : V} {Γ δ : ℝ}
    (hd : d ≠ 0) (hbd : ⟪b, d⟫ = 0) :
    cap b Γ (Γ * Real.cos δ) ⊆ closure (convexHull ℝ (sCap b Γ δ)) := by
  have hKM := closure_convexHull_extremePoints (isCompact_cap b Γ (Γ * Real.cos δ))
    (convex_cap b Γ (Γ * Real.cos δ))
  have hext : (cap b Γ (Γ * Real.cos δ)).extremePoints ℝ ⊆ sCap b Γ δ := by
    rw [extremePoints_cap hd hbd]
    rintro T ⟨hT, hn⟩
    exact ⟨hn, hT.2⟩
  calc cap b Γ (Γ * Real.cos δ) = closure (convexHull ℝ _) := hKM.symm
    _ ⊆ closure (convexHull ℝ (sCap b Γ δ)) := closure_mono (convexHull_mono hext)

/-- Original-feasible data are relaxed-feasible (take `Γ = ‖T‖`). -/
theorem original_subset_relaxed {tf m : ℝ} {g : V} {Xf : Set (V × V)} {b : ℝ → V}
    {ρ₁ ρ₂ δ : ℝ} : origFeas tf m g Xf b ρ₁ ρ₂ δ ⊆ relFeas tf m g Xf b ρ₁ ρ₂ δ := by
  rintro θ ⟨T, hA, hK, hX⟩
  refine ⟨T, fun t => ‖T t‖, hA.1.aestronglyMeasurable.norm.aemeasurable, hA, ?_, hX⟩
  filter_upwards [hK] with t ht
  exact ⟨⟨le_rfl, ht.2.2⟩, ht.1, ht.2.1⟩

/-- **C-W(1).** Under `AumannInstance`, for a measurable unit attitude profile in a space of
dimension ≥ 2 (nonzero orthogonal vectors exist), every relaxed-feasible boundary datum is
original-feasible. -/
theorem relaxed_subset_original [FiniteDimensional ℝ V] {tf m δ : ℝ} {g : V}
    {Xf : Set (V × V)} {b : ℝ → V} {ρ₁ ρ₂ : ℝ}
    (hA : AumannInstance (V := V) tf δ) (hbm : Measurable b)
    (hperp : ∀ t, ∃ d : V, d ≠ 0 ∧ ⟪b t, d⟫ = 0) :
    relFeas tf m g Xf b ρ₁ ρ₂ δ ⊆ origFeas tf m g Xf b ρ₁ ρ₂ δ := by
  rintro θ ⟨T, Γ, hΓm, hAdm, hK, hX⟩
  have hbound : ∃ R, ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), |Γ t| ≤ R := by
    refine ⟨|ρ₁| + |ρ₂|, ?_⟩
    filter_upwards [hK] with t ht
    rw [abs_le]
    constructor <;> cases abs_cases ρ₁ <;> cases abs_cases ρ₂ <;> linarith [ht.2.1, ht.2.2]
  have hhull : ∀ᵐ t ∂(volume.restrict (Icc 0 tf)),
      T t ∈ closure (convexHull ℝ (sCap (b t) (Γ t) δ)) := by
    filter_upwards [hK] with t ht
    obtain ⟨d, hd, hbd⟩ := hperp t
    exact cap_subset_closure_convexHull_sCap hd hbd ht.1
  obtain ⟨T', hAdm', hS, hm0, hm1⟩ := hA b Γ hbm hΓm hbound T hAdm hhull
  refine ⟨T', hAdm', ?_, ?_⟩
  · filter_upwards [hS, hK] with t hs ht
    refine ⟨hs.1 ▸ ht.2.1, hs.1 ▸ ht.2.2, ?_⟩
    rw [hs.1]; exact hs.2
  · have : termState tf m g θ T' = termState tf m g θ T := by
      simp only [termState, hm0, hm1]
    rw [this]; exact hX

/-- Joint convexity of the relaxed control constraint in `(T, Γ)`. -/
theorem cap_comb {b T₁ T₂ : V} {Γ₁ Γ₂ δ a a' : ℝ} (ha : 0 ≤ a) (ha' : 0 ≤ a')
    (h₁ : T₁ ∈ cap b Γ₁ (Γ₁ * Real.cos δ)) (h₂ : T₂ ∈ cap b Γ₂ (Γ₂ * Real.cos δ)) :
    a • T₁ + a' • T₂ ∈ cap b (a * Γ₁ + a' * Γ₂) ((a * Γ₁ + a' * Γ₂) * Real.cos δ) := by
  refine ⟨?_, ?_⟩
  · calc ‖a • T₁ + a' • T₂‖ ≤ ‖a • T₁‖ + ‖a' • T₂‖ := norm_add_le _ _
      _ = a * ‖T₁‖ + a' * ‖T₂‖ := by
          rw [norm_smul, norm_smul, Real.norm_of_nonneg ha, Real.norm_of_nonneg ha']
      _ ≤ a * Γ₁ + a' * Γ₂ := by gcongr; exact h₁.1; exact h₂.1
  · rw [inner_add_right, real_inner_smul_right, real_inner_smul_right]
    nlinarith [mul_le_mul_of_nonneg_left h₁.2 ha, mul_le_mul_of_nonneg_left h₂.2 ha']

/-- The relaxed feasible set is convex (no hypotheses beyond convexity of `Xf`). -/
theorem convex_relFeas {tf m : ℝ} {g : V} {Xf : Set (V × V)} {b : ℝ → V} {ρ₁ ρ₂ δ : ℝ}
    (hXf : Convex ℝ Xf) : Convex ℝ (relFeas tf m g Xf b ρ₁ ρ₂ δ) := by
  rintro θ₁ ⟨T₁, Γ₁, hm₁, hA₁, hK₁, hX₁⟩ θ₂ ⟨T₂, Γ₂, hm₂, hA₂, hK₂, hX₂⟩ a a' ha ha' haa
  refine ⟨fun t => a • T₁ t + a' • T₂ t, fun t => a * Γ₁ t + a' * Γ₂ t,
    (hm₁.const_mul a).add (hm₂.const_mul a'), hA₁.comb hA₂ a a', ?_, ?_⟩
  · filter_upwards [hK₁, hK₂] with t h1 h2
    have e1 : ρ₁ = a * ρ₁ + a' * ρ₁ := by rw [← add_mul, haa, one_mul]
    have e2 : ρ₂ = a * ρ₂ + a' * ρ₂ := by rw [← add_mul, haa, one_mul]
    refine ⟨cap_comb ha ha' h1.1 h2.1, ?_, ?_⟩
    · nlinarith [mul_le_mul_of_nonneg_left h1.2.1 ha, mul_le_mul_of_nonneg_left h2.2.1 ha']
    · nlinarith [mul_le_mul_of_nonneg_left h1.2.2 ha, mul_le_mul_of_nonneg_left h2.2.2 ha']
  · rw [termState_comb hA₁ hA₂ haa]
    exact hXf hX₁ hX₂ ha ha' haa

/-- **C-W(1), equality form.** Under `AumannInstance`: `F_tf(b)` (original) equals the relaxed
feasible set. -/
theorem origFeas_eq_relFeas [FiniteDimensional ℝ V] {tf m δ : ℝ} {g : V}
    {Xf : Set (V × V)} {b : ℝ → V} {ρ₁ ρ₂ : ℝ}
    (hA : AumannInstance (V := V) tf δ) (hbm : Measurable b)
    (hperp : ∀ t, ∃ d : V, d ≠ 0 ∧ ⟪b t, d⟫ = 0) :
    origFeas tf m g Xf b ρ₁ ρ₂ δ = relFeas tf m g Xf b ρ₁ ρ₂ δ :=
  (original_subset_relaxed).antisymm (relaxed_subset_original hA hbm hperp)

/-- **C-F.** Under `AumannInstance` (constant mass, measurable attitude, dim ≥ 2, convex terminal
set), the exact fixed-attitude feasible boundary-data set `F_tf(b)` is convex. -/
theorem convex_origFeas [FiniteDimensional ℝ V] {tf m δ : ℝ} {g : V}
    {Xf : Set (V × V)} {b : ℝ → V} {ρ₁ ρ₂ : ℝ}
    (hA : AumannInstance (V := V) tf δ) (hbm : Measurable b)
    (hperp : ∀ t, ∃ d : V, d ≠ 0 ∧ ⟪b t, d⟫ = 0) (hXf : Convex ℝ Xf) :
    Convex ℝ (origFeas tf m g Xf b ρ₁ ρ₂ δ) := by
  rw [origFeas_eq_relFeas hA hbm hperp]
  exact convex_relFeas hXf

/-- In `ℝ³` every vector has a nonzero orthogonal vector (discharges `hperp`). -/
theorem exists_perp_three (b : EuclideanSpace ℝ (Fin 3)) :
    ∃ d : EuclideanSpace ℝ (Fin 3), d ≠ 0 ∧ ⟪b, d⟫ = 0 := by
  by_cases hb : b = 0
  · refine ⟨EuclideanSpace.single 0 1, ?_, by simp [hb]⟩
    intro h
    have := congrArg (fun v => v 0) h
    simp at this
  · have : Fact (Module.finrank ℝ (EuclideanSpace ℝ (Fin 3)) = 2 + 1) := ⟨by simp⟩
    have hK : Module.finrank ℝ (ℝ ∙ b)ᗮ = 2 := Submodule.finrank_orthogonal_span_singleton hb
    have hne : (ℝ ∙ b)ᗮ ≠ ⊥ := by
      intro h0; rw [h0, finrank_bot] at hK; exact absurd hK (by norm_num)
    obtain ⟨d, hd, hd0⟩ := (Submodule.ne_bot_iff _).mp hne
    exact ⟨d, hd0, (Submodule.mem_orthogonal_singleton_iff_inner_right).mp hd⟩

end LcvxPositive
