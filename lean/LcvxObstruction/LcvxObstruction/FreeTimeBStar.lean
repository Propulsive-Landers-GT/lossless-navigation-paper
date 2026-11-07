import LcvxObstruction.DiveBrakeMassVariants

/-!
# Theorem B*, free final time on a compact window (math/02 Cor. 10.4)

For horizons `t ∈ [t_a, t_b]` with `s* < t_a`, the union `⋃_{t ∈ [t_a,t_b]} F^X_t` of the
state-constrained landing sets is not convex. Proof (Cor. 10.4): `ℓ*(t) = V_max(t) + κ(t)` (the
largest value of `ℓ = r_{0z} + s* v_{0z}` at horizon `t`, `κ(t) = g₀ t (s* - t/2)`) is continuous,
so it attains its maximum at some `t°`; the mirror witnesses at `t°` lie in the union, and if their
midpoint landed at any horizon `t'` in the window, its weighted impulse would be `V e_z` with
`V = V_max(t°) + κ(t°) - κ(t') ≥ V_max(t')`, which `PhiMax_not_mem_WSet` excludes.

* `not_convex_iUnion_of_max` (abstract: any horizon-dependent acceleration class with a continuous
  face value attained by a witness with the B* bounds),
* `not_convex_iUnion_constrainedLandingSet_box` (constant acceleration bounds, `α = 0`),
* `not_convex_iUnion_constrainedLandingSet_mass` (explicit mass depletion, `α > 0`),
* headlines `no_lossless_relaxation_freeTime_5dof(_mass)`.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- **Free-final-time B\*, abstract form.** -/
theorem not_convex_iUnion_of_max {Acc : ℝ → Set (ℝ → ℝ)} {Vmax : ℝ → ℝ}
    {ta tb ω δ sS amin g₀ tanγ A B : ℝ}
    (hsS : 0 < sS) (hsta : sS < ta) (htab : ta ≤ tb) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin)
    (hAcc : ∀ t ∈ Icc ta tb, ∀ a ∈ Acc t, IntegrableOn a (Icc 0 t) ∧ ∀ s ∈ Icc 0 t, amin ≤ a s)
    (hV : ∀ t ∈ Icc ta tb, ∀ a ∈ Acc t, PhiFace t ω δ sS a ≤ Vmax t)
    (hcont : ContinuousOn (fun t => Vmax t + g₀ * t * (sS - t / 2)) (Icc ta tb))
    (hwit : ∀ t ∈ Icc ta tb, ∃ ah ∈ Acc t, PhiFace t ω δ sS ah = Vmax t ∧
      (∀ s ∈ Icc 0 t, s ≤ sS → 0 ≤ ah s ∧ ah s ≤ A) ∧ (∀ s ∈ Icc 0 t, sS < s → B ≤ ah s))
    (hg0 : 0 ≤ g₀) (hg : g₀ ≤ B) (htan : 0 ≤ tanγ)
    (hS : (B + 2 * tanγ * A) * sS ^ 2 ≤ (B - g₀) * (ta - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (⋃ t ∈ Icc ta tb, constrainedLandingSet (Acc t) t ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  set g := -(g₀ • ez) with hgdef
  -- the best horizon
  obtain ⟨t0, ht0, hmax⟩ := isCompact_Icc.exists_isMaxOn (nonempty_Icc.2 htab) hcont
  obtain ⟨ah, hah, hVah, hdive, hbrake⟩ := hwit t0 ht0
  have hsS0 : sS < t0 := lt_of_lt_of_le hsta ht0.1
  have haI := (hAcc t0 ht0 ah hah).1
  have hS0 : (B + 2 * tanγ * A) * sS ^ 2 ≤ (B - g₀) * (t0 - sS) ^ 2 := by
    have : (ta - sS) ^ 2 ≤ (t0 - sS) ^ 2 := pow_le_pow_left₀ (by linarith) (by linarith [ht0.1]) 2
    nlinarith [mul_le_mul_of_nonneg_left this (by linarith : (0:ℝ) ≤ B - g₀)]
  have mem : ∀ v : E3, ‖v‖ = 1 → ⟪v, ez⟫ = 0 →
      landingData g ah (dW ω δ sS v) t0 ∈
        ⋃ t ∈ Icc ta tb, constrainedLandingSet (Acc t) t ω δ g X := fun v hv hvz => by
    refine mem_iUnion₂.2 ⟨t0, ht0, ?_⟩
    exact ⟨_, _, _, hah, witness_admissible hv hvz hsS hω.le hδ hδπ hωs,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witnessG_mem_glideSlope hv hvz hsS hsS0 hω.le hδ hreg haI hdive hbrake
        hg0 hg htan hS0 ht)⟩
  refine not_convex_of_midpoint subset_rfl (mem ex norm_ex inner_ex_ez)
    (mem (-ex) (by simp) (by simp)) ?_
  intro hm
  obtain ⟨t1, ht1, hm1⟩ := mem_iUnion₂.1 hm
  obtain ⟨a, d, b, ha, hatt, hr, hv, -⟩ := hm1
  have hsS1 : sS < t1 := lt_of_lt_of_le hsta ht1.1
  have hAcc1 := hAcc t1 ht1
  have hfa : IntegrableOn (fun s => a s • d s) (Icc 0 t1) :=
    integrableOn_smul_of_unit (hAcc1 a ha).1 hatt.d_meas hatt.d_unit
  have hΛ := lambda_identity (sS := sS) hfa hr hv
  have hΛ₁ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := t0) (sS := sS) (ω := ω)
    (δ := δ) norm_ex inner_ex_ez haI) (landingData_lands g _ _ t0).1 (landingData_lands g _ _ t0).2
  have hΛ₂ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := t0) (sS := sS) (ω := ω)
    (δ := δ) (by simp : ‖-ex‖ = 1) (by simp : ⟪-ex, ez⟫ = 0) haI)
    (landingData_lands g _ _ t0).1 (landingData_lands g _ _ t0).2
  have hW := witnessG_W_midpoint (tf := t0) (ω := ω) (δ := δ) (sS := sS) norm_ex inner_ex_ez haI
  rw [hVah] at hW
  set V := Vmax t0 + g₀ * t0 * (sS - t0 / 2) - g₀ * t1 * (sS - t1 / 2) with hVdef
  have hVge : Vmax t1 ≤ V := by
    have := hmax ht1
    simp only [mem_setOf_eq] at this
    rw [hVdef]; linarith
  apply PhiMax_not_mem_WSet (V := V) hsS hsS1 hω hδ hreg hamin hAcc1
    (fun a ha => (hV t1 ht1 a ha).trans hVge)
  refine ⟨a, d, b, ha, hatt, ?_⟩
  simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd] at hΛ
  rw [hgdef] at hΛ hΛ₁ hΛ₂
  linear_combination (norm := module) hΛ - (1 / 2 : ℝ) • hΛ₁ - (1 / 2 : ℝ) • hΛ₂ - hW

/-! ### Constant acceleration bounds (`α = 0`) -/

theorem phiFace_le_VStar {tf ω δ sS amin amax : ℝ} (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) {a : ℝ → ℝ} (haI : IntegrableOn a (Icc 0 tf))
    (hab : ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax) :
    PhiFace tf ω δ sS a ≤ VStar tf ω δ sS amin amax := by
  refine setIntegral_mono_on (haI.mul_continuousOn (continuous_phiW ω δ sS).continuousOn
    isCompact_Icc) (continuous_hStar ω δ sS amin amax).integrableOn_Icc measurableSet_Icc
    fun s hs => ?_
  obtain ⟨h1, h2⟩ := hab s hs
  simp only [phiW, hStar]
  rcases le_or_gt s sS with h | h
  · rw [min_eq_left (by linarith), max_eq_right (by linarith)]
    have hc : 0 ≤ Real.cos (δ + ω * s) := Real.cos_nonneg_of_mem_Icc
      ⟨by nlinarith [hs.1, Real.pi_pos], by nlinarith⟩
    have : (s - sS) * Real.cos (δ + ω * s) ≤ 0 := mul_nonpos_of_nonpos_of_nonneg (by linarith) hc
    nlinarith [mul_le_mul_of_nonpos_right h1 this]
  · rw [min_eq_right (by linarith), max_eq_left (by linarith)]
    nlinarith [mul_le_mul_of_nonneg_right h2 (by linarith : (0:ℝ) ≤ s - sS)]

theorem phiFace_aW (tf ω δ sS amin amax : ℝ) :
    PhiFace tf ω δ sS (aW sS amin amax) = VStar tf ω δ sS amin amax := by
  refine setIntegral_congr_fun measurableSet_Icc fun s _ => ?_
  simp only [phiW, hStar, aW]
  split_ifs with h
  · rw [min_eq_left (by linarith), max_eq_right (by linarith)]; ring
  · rw [min_eq_right (by linarith), max_eq_left (by linarith)]; ring

theorem continuousOn_VStar {ta tb ω δ sS amin amax : ℝ} (hta : 0 ≤ ta) :
    ContinuousOn (fun t => VStar t ω δ sS amin amax) (Icc ta tb) := by
  have hc := intervalIntegral.continuous_primitive (μ := volume)
    (fun a b => (continuous_hStar ω δ sS amin amax).intervalIntegrable a b) 0
  refine hc.continuousOn.congr fun t ht => ?_
  simp only [VStar]
  rw [integral_Icc_eq_integral_Ioc, intervalIntegral.integral_of_le (hta.trans ht.1)]

/-- **Free-final-time Theorem B\*, constant acceleration bounds.** -/
theorem not_convex_iUnion_constrainedLandingSet_box {ta tb ω δ sS amin amax g₀ tanγ : ℝ}
    (hsS : 0 < sS) (hsta : sS < ta) (htab : ta ≤ tb) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg0 : 0 ≤ g₀)
    (hg : g₀ ≤ amax) (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (ta - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (⋃ t ∈ Icc ta tb,
      constrainedLandingSet (AccBox t (fun _ => amin) (fun _ => amax)) t ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  refine not_convex_iUnion_of_max (Acc := fun t => AccBox t (fun _ => amin) (fun _ => amax))
    (Vmax := fun t => VStar t ω δ sS amin amax)
    (amin := amin) (A := amin) (B := amax) hsS hsta htab hω hωs hreg hamin
    (fun t _ a ha => ⟨ha.1, fun s hs => (ha.2 s hs).1⟩)
    (fun t _ a ha => phiFace_le_VStar hω.le hδ hreg ha.1 ha.2)
    ((continuousOn_VStar (by linarith)).add (by fun_prop))
    (fun t _ => ⟨aW sS amin amax, aW_mem_accBox h, phiFace_aW t ω δ sS amin amax,
      fun s _ hs => by simp [aW, hs, hamin.le], fun s _ hs => by simp [aW, not_le.2 hs]⟩)
    hg0 hg htan hS hX

/-! ### Explicit mass depletion (`α > 0`) -/

theorem continuous_wval₂ {ρ₁ ρ₂ α m₀ mdry ω δ sS : ℝ} (hmdry : 0 < mdry) :
    Continuous fun p : ℝ × ℝ => wval ρ₁ ρ₂ α m₀ mdry p.1 ω δ sS p.2 := by
  have hpos : ∀ x : ℝ, max x mdry ≠ 0 := fun x => ne_of_gt (lt_of_lt_of_le hmdry (le_max_right _ _))
  have hm2 : Continuous fun p : ℝ × ℝ => msig ρ₁ ρ₂ α m₀ p.1 p.2 := by unfold msig; fun_prop
  have h1 : Continuous fun σ => ∫ u in (0 : ℝ)..sS,
      cWd ω δ sS u * Real.log (max (msig ρ₁ ρ₂ α m₀ σ u) mdry) := by
    apply intervalIntegral.continuous_parametric_intervalIntegral_of_continuous'
    exact ((continuous_cWd ω δ sS).comp continuous_snd).mul
      ((hm2.max continuous_const).log fun p => hpos _)
  have h2 : Continuous fun p : ℝ × ℝ => ∫ s in sS..p.1,
      (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ p.2 sS - α * ρ₂ * (s - sS)) mdry) := by
    apply intervalIntegral.continuous_parametric_intervalIntegral_of_continuous
      (f := fun (p : ℝ × ℝ) (s : ℝ) =>
        (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ p.2 sS - α * ρ₂ * (s - sS)) mdry)) _ continuous_fst
    refine (continuous_snd.sub continuous_const).mul (continuous_const.div ?_ fun p => hpos _)
    exact ((hm2.comp ((continuous_snd.comp continuous_fst).prodMk continuous_const)).sub
      (continuous_const.mul (continuous_snd.sub continuous_const))).max continuous_const
  unfold wval
  exact (continuous_const.mul (continuous_const.add (h1.comp continuous_snd))).neg.add h2

/-- **Free-final-time Theorem B\*, explicit mass depletion.** Window `[t_a, t_b]` with
`s* < t_a`, dry mass `m_dry ≤ m₀ - αρ₂ t_b`. -/
theorem not_convex_iUnion_constrainedLandingSet_mass {ρ₁ ρ₂ α m₀ mdry ta tb ω δ sS g₀ tanγ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tb) (hsS : 0 < sS) (hsta : sS < ta) (htab : ta ≤ tb)
    (hω : 0 < ω) (hωs : ω * sS ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (hg0 : 0 ≤ g₀)
    (hg : g₀ ≤ ρ₂ / m₀) (htan : 0 ≤ tanγ)
    (hS : (ρ₂ / m₀ + 2 * tanγ * (ρ₂ / mdry)) * sS ^ 2 ≤ (ρ₂ / m₀ - g₀) * (ta - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (⋃ t ∈ Icc ta tb,
      constrainedLandingSet (AccMass ρ₁ ρ₂ α m₀ mdry t) t ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hρ₂ : 0 < ρ₂ := hρ₁.trans h12
  have hburnt : ∀ t ∈ Icc ta tb, mdry ≤ m₀ - α * ρ₂ * t := fun t ht => by
    have : α * ρ₂ * t ≤ α * ρ₂ * tb := mul_le_mul_of_nonneg_left ht.2 (by positivity)
    linarith
  have hm0 : 0 < m₀ := by
    have := hburnt ta ⟨le_rfl, htab⟩
    nlinarith [mul_pos (mul_pos hα hρ₂) (hsS.trans hsta)]
  set W : ℝ → ℝ → ℝ := fun t σ => wval ρ₁ ρ₂ α m₀ mdry t ω δ sS σ with hWdef
  have hWc : ∀ t, ContinuousOn (W t) (Icc 0 sS) := fun t =>
    (continuous_wval (ρ₁ := ρ₁) (ρ₂ := ρ₂) (α := α) (m₀ := m₀) (tf := t) (ω := ω) (δ := δ)
      (sS := sS) hmdry).continuousOn
  have hbdd : ∀ t, BddAbove (W t '' Icc 0 sS) := fun t =>
    (isCompact_Icc.image_of_continuousOn (hWc t)).bddAbove
  refine not_convex_iUnion_of_max (Acc := fun t => AccMass ρ₁ ρ₂ α m₀ mdry t)
    (Vmax := fun t => sSup (W t '' Icc 0 sS)) (amin := ρ₁ / m₀) (A := ρ₂ / mdry)
    (B := ρ₂ / m₀) hsS hsta htab hω hωs hreg (by positivity)
    (fun t ht => accMass_lower hρ₁ h12 hα hmdry (hburnt t ht))
    (fun t ht a ha => ?_) ?_ (fun t ht => ?_) hg0 hg htan hS hX
  · obtain ⟨σ, hσ, hle⟩ := phiFace_le_wval hρ₁ h12 hα hmdry (hburnt t ht) hsS.le
      (hsta.le.trans ht.1) hω.le hδ hreg ha
    exact hle.trans (le_csSup (hbdd t) (mem_image_of_mem _ hσ))
  · have : Continuous fun t => sSup (W t '' Icc 0 sS) :=
      isCompact_Icc.continuous_sSup (continuous_wval₂ hmdry)
    exact (this.add (by fun_prop)).continuousOn
  · have htS : sS ≤ t := hsta.le.trans ht.1
    obtain ⟨σ, hσ, hσeq⟩ := (isCompact_Icc.image_of_continuousOn (hWc t)).sSup_mem
      ((nonempty_Icc.2 hsS.le).image _)
    have hmge : ∀ s ∈ Icc 0 t, mdry ≤ msig ρ₁ ρ₂ α m₀ σ s := fun s hs => by
      have := msig_ge (m₀ := m₀) hσ.1 hs.1 h12.le hα.le
      have : α * ρ₂ * s ≤ α * ρ₂ * t := mul_le_mul_of_nonneg_left hs.2 (by positivity)
      linarith [hburnt t ht]
    refine ⟨aSig ρ₁ ρ₂ α m₀ σ, aSig_mem hρ₁.le h12.le hα.le hmdry (hburnt t ht) hσ.1, ?_,
      fun s hs _ => ?_, fun s hs hss => ?_⟩
    · rw [phiFace_aSig hρ₁ h12.le hα hmdry (hburnt t ht) hsS.le htS hσ]
      exact hσeq
    · have hmpos : 0 < msig ρ₁ ρ₂ α m₀ σ s := hmdry.trans_le (hmge s hs)
      obtain ⟨hT1, hT2⟩ := Tsig_bounds (σ := σ) h12.le s
      refine ⟨div_nonneg (by linarith) hmpos.le, ?_⟩
      calc aSig ρ₁ ρ₂ α m₀ σ s ≤ ρ₂ / msig ρ₁ ρ₂ α m₀ σ s :=
            div_le_div_of_nonneg_right hT2 hmpos.le
        _ ≤ ρ₂ / mdry := div_le_div_of_nonneg_left hρ₂.le hmdry (hmge s hs)
    · have hmpos : 0 < msig ρ₁ ρ₂ α m₀ σ s := hmdry.trans_le (hmge s hs)
      have hT : Tsig ρ₁ ρ₂ σ s = ρ₂ := by simp [Tsig, not_le.2 (lt_of_le_of_lt hσ.2 hss)]
      rw [aSig, hT]
      exact div_le_div_of_nonneg_left hρ₂.le hmpos (msig_le hσ.1 hs.1 hρ₁.le h12.le hα.le)

/-! ### Headlines: free final time -/

/-- **Main theorem, free final time on a window, constant acceleration bounds.** For every
window `0 < t_a ≤ t_b` there is a switch time, and no uniform convex relaxation is lossless for
the union of the state-constrained landing sets over the window. -/
theorem no_lossless_relaxation_freeTime_5dof {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {ta tb ω δ amin amax g₀ tanγ : ℝ} (hta : 0 < ta) (htab : ta ≤ tb) (hω : 0 < ω)
    (hδ : 0 < δ) (hδ2 : δ < π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg0 : 0 ≤ g₀)
    (hg : g₀ < amax) (htan : 0 ≤ tanγ) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (⋃ t ∈ Icc ta tb,
      constrainedLandingSet (AccBox t (fun _ => amin) (fun _ => amax)) t ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsta, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) hta hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_iUnion_constrainedLandingSet_box hsS hsta htab hω hωs hreg hamin h hg0 hg.le htan
      hS hX) R

/-- **Main theorem, free final time on a window, explicit mass depletion.** -/
theorem no_lossless_relaxation_freeTime_5dof_mass {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {ρ₁ ρ₂ α m₀ mdry ta tb ω δ g₀ tanγ : ℝ} (hta : 0 < ta) (htab : ta ≤ tb) (hω : 0 < ω)
    (hδ : 0 < δ) (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α)
    (hmdry : 0 < mdry) (hburn : mdry ≤ m₀ - α * ρ₂ * tb) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀)
    (htan : 0 ≤ tanγ) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (⋃ t ∈ Icc ta tb,
      constrainedLandingSet (AccMass ρ₁ ρ₂ α m₀ mdry t) t ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsta, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := ρ₂ / mdry) (tanγ := tanγ) hta hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_iUnion_constrainedLandingSet_mass hρ₁ h12 hα hmdry hburn hsS hsta htab hω hωs hreg
      hg0 hg.le htan hS hX) R

end LcvxObstruction
