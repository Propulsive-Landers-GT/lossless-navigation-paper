import LcvxObstruction.DiveBrakeMass

/-!
# Theorem B* with explicit mass depletion (`α > 0`)

Model `AccMass ρ₁ ρ₂ α m₀ m_dry tf` (`MassModel.lean`): thrust `T ∈ [ρ₁, ρ₂]`,
`m(t) = m₀ - α ∫₀ᵗ T`, `a = T/m`, `m ≥ m_dry`. We show that the face functional `PhiFace`
(`DiveBrakeMass.lean`) has a maximiser in `AccMass`, of the explicit form
"min throttle on `[0, σ*]`, max throttle on `(σ*, tf]`" with `σ* ∈ [0, s*]`, and then apply
`not_convex_constrainedLandingSet_of_max`.

Proof of the maximiser (math/02 §10.3 Steps 3–4, made explicit):
* **Dive identity** (`dive_identity`): `T/m = -(1/α) (log m)'` a.e., so integrating by parts
  (absolutely continuous FTC, Mathlib's `AbsolutelyContinuousOnInterval`) with the dive weight
  `c(s) = (s* - s) cos(δ + ωs)` (which vanishes at `s*`),
  `∫₀^{s*} c T/m = (1/α) (c(0) log m₀ + ∫₀^{s*} c' log m)`, with `c' ≤ 0`.
  So the dive part of the face functional is increasing in the mass history `m(·)` pointwise.
* **Brake bound** (`brake_le`): on `(s*, tf]`, `T/m ≤ ρ₂ / (m(s*) - αρ₂(s - s*))`.
* **Comparison** (`mass_le_msig`): for given `M = m(s*)`, the profile with min throttle up to the
  switch `σ` and max throttle after (`m_σ(s*) = M`) has the pointwise largest mass on `[0, s*]`.
* Hence `PhiFace (T/m) ≤ w(σ(T))`, where `w(σ) = PhiFace(a_σ)` is continuous on `[0, s*]`, so it
  attains its maximum at some `σ*`.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace NNReal

namespace LcvxObstruction

/-! ### The dive weight -/

/-- Dive weight `c(s) = (s* - s) cos(δ + ωs)`. -/
noncomputable def cW (ω δ sS : ℝ) (s : ℝ) : ℝ := (sS - s) * Real.cos (δ + ω * s)

/-- Its derivative `c'(s) = -cos(δ+ωs) - ω (s* - s) sin(δ+ωs)`. -/
noncomputable def cWd (ω δ sS : ℝ) (s : ℝ) : ℝ :=
  -Real.cos (δ + ω * s) - ω * (sS - s) * Real.sin (δ + ω * s)

theorem hasDerivAt_cW (ω δ sS s : ℝ) : HasDerivAt (cW ω δ sS) (cWd ω δ sS s) s := by
  have h1 : HasDerivAt (fun s => sS - s) (-1) s := by
    simpa using (hasDerivAt_id s).const_sub sS
  have h2 : HasDerivAt (fun s => Real.cos (δ + ω * s)) (-Real.sin (δ + ω * s) * (ω * 1)) s :=
    (((hasDerivAt_id' s).const_mul ω).const_add δ).cos
  have := h1.mul h2
  rw [show cW ω δ sS = fun s => (sS - s) * Real.cos (δ + ω * s) from rfl]
  convert this using 1
  simp only [cWd]; ring

theorem continuous_cW (ω δ sS : ℝ) : Continuous (cW ω δ sS) := by unfold cW; fun_prop
theorem continuous_cWd (ω δ sS : ℝ) : Continuous (cWd ω δ sS) := by unfold cWd; fun_prop

theorem cWd_nonpos {ω δ sS s : ℝ} (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2)
    (hs : s ∈ Icc 0 sS) : cWd ω δ sS s ≤ 0 := by
  have h1 : δ + ω * s ≤ π / 2 := by nlinarith [hs.2]
  have h0 : 0 ≤ δ + ω * s := by nlinarith [hs.1]
  have hc : 0 ≤ Real.cos (δ + ω * s) := Real.cos_nonneg_of_mem_Icc ⟨by linarith [Real.pi_pos], h1⟩
  have hsn : 0 ≤ Real.sin (δ + ω * s) :=
    Real.sin_nonneg_of_nonneg_of_le_pi h0 (by linarith [Real.pi_pos])
  have : 0 ≤ ω * (sS - s) * Real.sin (δ + ω * s) :=
    mul_nonneg (mul_nonneg hω (by linarith [hs.2])) hsn
  simp only [cWd]; linarith

/-! ### Mass as an interval integral -/

theorem massOf_eq_intervalIntegral {α m₀ : ℝ} {T : ℝ → ℝ} {u : ℝ} (hu : 0 ≤ u) :
    massOf α m₀ T u = m₀ - α * ∫ s in (0 : ℝ)..u, T s := by
  rw [massOf, intervalIntegral.integral_of_le hu, integral_Icc_eq_integral_Ioc]

theorem massOf_zero (α m₀ : ℝ) (T : ℝ → ℝ) : massOf α m₀ T 0 = m₀ := by
  simp [massOf]

/-- `log` is `1/m_dry`-Lipschitz on `[m_dry, ∞)`. -/
theorem lipschitzOnWith_log {mdry : ℝ} (hmdry : 0 < mdry) :
    LipschitzOnWith (Real.toNNReal mdry⁻¹) Real.log (Ici mdry) := by
  refine (convex_Ici mdry).lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (f' := fun x => x⁻¹) (fun x hx => (Real.hasDerivAt_log
      (ne_of_gt (lt_of_lt_of_le hmdry (mem_Ici.1 hx)))).hasDerivWithinAt) fun x hx => ?_
  have hx : mdry ≤ x := hx
  have hx0 : 0 < x := by linarith
  rw [← NNReal.coe_le_coe, coe_nnnorm, Real.norm_eq_abs, abs_inv, abs_of_pos hx0,
    Real.coe_toNNReal _ (by positivity)]
  exact inv_anti₀ hmdry hx

/-! ### The dive identity -/

/-- **Dive identity.** For an integrable thrust history keeping the mass above `m_dry > 0`:
`∫₀^{s*} c(s) T(s)/m(s) ds = (1/α) (c(0) log m₀ + ∫₀^{s*} c'(s) log m(s) ds)`. -/
theorem dive_identity {α m₀ mdry tf ω δ sS : ℝ} {T : ℝ → ℝ} (hα : α ≠ 0) (hmdry : 0 < mdry)
    (hsS : 0 ≤ sS) (hsStf : sS ≤ tf) (hTI : IntegrableOn T (Icc 0 tf))
    (hm : ∀ u ∈ Icc 0 tf, mdry ≤ massOf α m₀ T u) :
    ∫ s in (0 : ℝ)..sS, cW ω δ sS s * (T s / massOf α m₀ T s) =
      α⁻¹ * (cW ω δ sS 0 * Real.log m₀ +
        ∫ s in (0 : ℝ)..sS, cWd ω δ sS s * Real.log (massOf α m₀ T s)) := by
  set m := massOf α m₀ T with hmdef
  have hTi : IntervalIntegrable T volume 0 sS :=
    (hTI.mono_set (by rw [uIcc_of_le hsS]; exact Icc_subset_Icc_right hsStf)).intervalIntegrable
  have huIcc : uIcc 0 sS = Icc 0 sS := uIcc_of_le hsS
  have hmem : ∀ u ∈ uIcc 0 sS, u ∈ Icc 0 tf := fun u hu => by
    rw [huIcc] at hu; exact ⟨hu.1, hu.2.trans hsStf⟩
  -- the mass is absolutely continuous on `[0, s*]`
  have hmAC : AbsolutelyContinuousOnInterval m 0 sS := by
    have h1 : AbsolutelyContinuousOnInterval (fun u => ∫ s in (0 : ℝ)..u, T s) 0 sS :=
      hTi.absolutelyContinuousOnInterval_intervalIntegral (by simp [hsS])
    have hc : AbsolutelyContinuousOnInterval (fun _ : ℝ => m₀) 0 sS :=
      (LipschitzWith.const (α := ℝ) m₀).lipschitzOnWith.absolutelyContinuousOnInterval
    have h2 := hc.sub (h1.const_mul α)
    exact h2.congr fun u hu => by
      simp only [Pi.sub_apply]; exact (massOf_eq_intervalIntegral (hmem u hu).1).symm
  set g := fun u => Real.log (m u) with hg
  have hgAC : AbsolutelyContinuousOnInterval g 0 sS :=
    (lipschitzOnWith_log hmdry).comp_absolutelyContinuousOnInterval
      (fun u hu => mem_Ici.2 (hm u (hmem u hu))) hmAC
  have hcAC : AbsolutelyContinuousOnInterval (cW ω δ sS) 0 sS :=
    ContDiffOn.absolutelyContinuousOnInterval (by unfold cW; fun_prop)
  -- a.e. derivative of `g`
  have hderiv : ∀ᵐ u, u ∈ uIoc (0 : ℝ) sS → deriv g u = -α * (T u / m u) := by
    filter_upwards [hTi.ae_hasDerivAt_integral] with u hu hI
    have hIcc : u ∈ uIcc 0 sS := uIoc_subset_uIcc hI
    have hu0 : 0 < u := by
      rw [uIoc_of_le hsS] at hI; exact hI.1
    have hD := hu hIcc 0 (by simp [hsS])
    have hmD : HasDerivAt m (-α * T u) u := by
      have h := (hD.const_mul α).const_sub m₀
      refine (h.congr_of_eventuallyEq ?_).congr_deriv (by ring)
      filter_upwards [lt_mem_nhds hu0] with x hx
      exact massOf_eq_intervalIntegral hx.le
    have hmpos : 0 < m u := lt_of_lt_of_le hmdry (hm u (hmem u hIcc))
    rw [(hmD.log hmpos.ne').deriv]
    ring
  have hibp := hcAC.integral_mul_deriv_eq_deriv_mul hgAC
  have hcongr1 : ∫ x in (0 : ℝ)..sS, cW ω δ sS x * deriv g x =
      ∫ x in (0 : ℝ)..sS, -α * (cW ω δ sS x * (T x / m x)) := by
    apply intervalIntegral.integral_congr_ae
    filter_upwards [hderiv] with x hx hxI
    rw [hx hxI]; ring
  have hcongr2 : ∫ x in (0 : ℝ)..sS, deriv (cW ω δ sS) x * g x =
      ∫ x in (0 : ℝ)..sS, cWd ω δ sS x * Real.log (m x) := by
    apply intervalIntegral.integral_congr fun x _ => ?_
    rw [(hasDerivAt_cW ω δ sS x).deriv]
  rw [hcongr1, hcongr2, intervalIntegral.integral_const_mul] at hibp
  have hc0 : cW ω δ sS sS = 0 := by simp [cW]
  have hg0 : g 0 = Real.log m₀ := by simp [hg, hmdef, massOf_zero]
  rw [hc0, zero_mul, zero_sub, hg0] at hibp
  rw [eq_inv_mul_iff_mul_eq₀ hα]
  linarith

/-! ### Mass bookkeeping for admissible thrust histories -/

section MassFacts

variable {ρ₁ ρ₂ α m₀ mdry tf : ℝ} {T : ℝ → ℝ}

/-- Additivity: `m(q) = m(p) - α ∫_{(p,q]} T`. -/
theorem massOf_add {p q : ℝ} (hp : 0 ≤ p) (hpq : p ≤ q) (hqtf : q ≤ tf)
    (hTI : IntegrableOn T (Icc 0 tf)) :
    massOf α m₀ T q = massOf α m₀ T p - α * ∫ s in Ioc p q, T s := by
  have hq : 0 ≤ q := hp.trans hpq
  have hs1 : uIcc 0 p ⊆ Icc 0 tf := by
    rw [uIcc_of_le hp]; exact Icc_subset_Icc_right (hpq.trans hqtf)
  have hs2 : uIcc p q ⊆ Icc 0 tf := by
    rw [uIcc_of_le hpq]; exact Icc_subset_Icc hp hqtf
  have h1 : IntervalIntegrable T volume 0 p := (hTI.mono_set hs1).intervalIntegrable
  have h2 : IntervalIntegrable T volume p q := (hTI.mono_set hs2).intervalIntegrable
  rw [massOf_eq_intervalIntegral hq, massOf_eq_intervalIntegral hp,
    ← intervalIntegral.integral_add_adjacent_intervals h1 h2,
    intervalIntegral.integral_of_le hpq]
  ring

theorem integral_Ioc_bounds {p q : ℝ} (hp : 0 ≤ p) (hpq : p ≤ q) (hqtf : q ≤ tf)
    (hTI : IntegrableOn T (Icc 0 tf)) (hTb : ∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂) :
    ρ₁ * (q - p) ≤ ∫ s in Ioc p q, T s ∧ ∫ s in Ioc p q, T s ≤ ρ₂ * (q - p) := by
  have hsub : Ioc p q ⊆ Icc 0 tf := fun s hs => ⟨hp.trans hs.1.le, hs.2.trans hqtf⟩
  have hI := hTI.mono_set hsub
  constructor
  · have := setIntegral_ge_of_const_le_real (c := ρ₁) measurableSet_Ioc measure_Ioc_lt_top.ne
      (fun s hs => (hTb s (hsub hs)).1) hI
    rwa [Real.volume_real_Ioc_of_le hpq] at this
  · have := setIntegral_mono_on hI (integrableOn_const (C := ρ₂) measure_Ioc_lt_top.ne)
      measurableSet_Ioc (fun s hs => (hTb s (hsub hs)).2)
    rw [setIntegral_const, Real.volume_real_Ioc_of_le hpq, smul_eq_mul] at this
    linarith

theorem massOf_bounds {u : ℝ} (hu : u ∈ Icc 0 tf) (hα : 0 ≤ α)
    (hTI : IntegrableOn T (Icc 0 tf)) (hTb : ∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂) :
    m₀ - α * ρ₂ * u ≤ massOf α m₀ T u ∧ massOf α m₀ T u ≤ m₀ - α * ρ₁ * u := by
  have h := massOf_add (α := α) (m₀ := m₀) le_rfl hu.1 hu.2 hTI
  rw [massOf_zero] at h
  obtain ⟨h1, h2⟩ := integral_Ioc_bounds le_rfl hu.1 hu.2 hTI hTb
  rw [h]; constructor <;> nlinarith

end MassFacts

/-! ### The switch profiles: min throttle on `[0, σ]`, max throttle after -/

/-- Thrust of the switch profile. -/
noncomputable def Tsig (ρ₁ ρ₂ σ : ℝ) (s : ℝ) : ℝ := if s ≤ σ then ρ₁ else ρ₂

/-- Mass of the switch profile (closed form). -/
noncomputable def msig (ρ₁ ρ₂ α m₀ σ : ℝ) (u : ℝ) : ℝ :=
  m₀ - α * (ρ₁ * min u σ + ρ₂ * max (u - σ) 0)

/-- Acceleration of the switch profile. -/
noncomputable def aSig (ρ₁ ρ₂ α m₀ σ : ℝ) (s : ℝ) : ℝ := Tsig ρ₁ ρ₂ σ s / msig ρ₁ ρ₂ α m₀ σ s

theorem measurable_Tsig (ρ₁ ρ₂ σ : ℝ) : Measurable (Tsig ρ₁ ρ₂ σ) :=
  Measurable.ite measurableSet_Iic measurable_const measurable_const

theorem continuous_msig (ρ₁ ρ₂ α m₀ σ : ℝ) : Continuous (msig ρ₁ ρ₂ α m₀ σ) := by
  unfold msig; fun_prop

theorem Tsig_bounds {ρ₁ ρ₂ σ : ℝ} (h12 : ρ₁ ≤ ρ₂) (s : ℝ) :
    ρ₁ ≤ Tsig ρ₁ ρ₂ σ s ∧ Tsig ρ₁ ρ₂ σ s ≤ ρ₂ := by
  unfold Tsig; split_ifs <;> constructor <;> linarith

theorem integrableOn_Tsig' (ρ₁ ρ₂ σ : ℝ) {S : Set ℝ} (hS : volume S ≠ ⊤) :
    IntegrableOn (Tsig ρ₁ ρ₂ σ) S := by
  refine Integrable.mono' (integrableOn_const (C := |ρ₁| + |ρ₂|) hS)
    (measurable_Tsig ρ₁ ρ₂ σ).aestronglyMeasurable (ae_of_all _ fun s => ?_)
  unfold Tsig; split_ifs <;> simp [Real.norm_eq_abs]

theorem integrableOn_Tsig (ρ₁ ρ₂ σ tf : ℝ) : IntegrableOn (Tsig ρ₁ ρ₂ σ) (Icc 0 tf) :=
  integrableOn_Tsig' ρ₁ ρ₂ σ measure_Icc_lt_top.ne

theorem intervalIntegrable_Tsig (ρ₁ ρ₂ σ a b : ℝ) :
    IntervalIntegrable (Tsig ρ₁ ρ₂ σ) volume a b :=
  (integrableOn_Tsig' ρ₁ ρ₂ σ measure_Icc_lt_top.ne).intervalIntegrable

theorem massOf_Tsig {ρ₁ ρ₂ α m₀ σ u : ℝ} (hσ : 0 ≤ σ) (hu : 0 ≤ u) :
    massOf α m₀ (Tsig ρ₁ ρ₂ σ) u = msig ρ₁ ρ₂ α m₀ σ u := by
  rw [massOf_eq_intervalIntegral hu, msig]
  congr 2
  rcases le_or_gt u σ with h | h
  · have e : ∫ x in (0 : ℝ)..u, Tsig ρ₁ ρ₂ σ x = ∫ x in (0 : ℝ)..u, ρ₁ := by
      refine intervalIntegral.integral_congr fun x hx => ?_
      rw [uIcc_of_le hu] at hx
      simp [Tsig, hx.2.trans h]
    rw [min_eq_left h, max_eq_right (by linarith), e]
    simp; ring
  · have e1 : ∫ x in (0 : ℝ)..σ, Tsig ρ₁ ρ₂ σ x = ∫ x in (0 : ℝ)..σ, ρ₁ := by
      refine intervalIntegral.integral_congr fun x hx => ?_
      rw [uIcc_of_le hσ] at hx
      simp [Tsig, hx.2]
    have e2 : ∫ x in σ..u, Tsig ρ₁ ρ₂ σ x = ∫ x in σ..u, ρ₂ := by
      rw [intervalIntegral.integral_of_le h.le, intervalIntegral.integral_of_le h.le]
      exact setIntegral_congr_fun measurableSet_Ioc fun x hx => by simp [Tsig, not_le.2 hx.1]
    rw [min_eq_right h.le, max_eq_left (by linarith),
      ← intervalIntegral.integral_add_adjacent_intervals (intervalIntegrable_Tsig ρ₁ ρ₂ σ 0 σ)
        (intervalIntegrable_Tsig ρ₁ ρ₂ σ σ u), e1, e2]
    simp; ring

theorem msig_ge {ρ₁ ρ₂ α m₀ σ u : ℝ} (hσ : 0 ≤ σ) (hu : 0 ≤ u) (h12 : ρ₁ ≤ ρ₂) (hα : 0 ≤ α) :
    m₀ - α * ρ₂ * u ≤ msig ρ₁ ρ₂ α m₀ σ u := by
  unfold msig
  rcases le_or_gt u σ with h | h
  · rw [min_eq_left h, max_eq_right (by linarith)]; nlinarith [mul_nonneg hα hu]
  · rw [min_eq_right h.le, max_eq_left (by linarith)]; nlinarith [mul_nonneg hα hσ]

theorem msig_le {ρ₁ ρ₂ α m₀ σ u : ℝ} (hσ : 0 ≤ σ) (hu : 0 ≤ u) (hρ₁ : 0 ≤ ρ₁) (h12 : ρ₁ ≤ ρ₂)
    (hα : 0 ≤ α) : msig ρ₁ ρ₂ α m₀ σ u ≤ m₀ := by
  unfold msig
  have : 0 ≤ ρ₁ * min u σ + ρ₂ * max (u - σ) 0 :=
    add_nonneg (mul_nonneg hρ₁ (le_min hu hσ)) (mul_nonneg (by linarith) (le_max_right _ _))
  nlinarith

theorem msig_brake {ρ₁ ρ₂ α m₀ σ sS s : ℝ} (hσ : σ ≤ sS) (hs : sS ≤ s) :
    msig ρ₁ ρ₂ α m₀ σ s = msig ρ₁ ρ₂ α m₀ σ sS - α * ρ₂ * (s - sS) := by
  unfold msig
  rw [min_eq_right (hσ.trans hs), max_eq_left (by linarith), min_eq_right hσ,
    max_eq_left (by linarith)]
  ring

section Compare

variable {ρ₁ ρ₂ α m₀ mdry tf sS : ℝ} {T : ℝ → ℝ}

/-- **Comparison with a switch profile.** For any admissible thrust history there is a switch time
`σ ∈ [0, s*]` such that the switch profile has the same mass at `s*` and a pointwise larger mass on
`[0, s*]`. -/
theorem exists_sigma_compare (hα : 0 < α) (h12 : ρ₁ < ρ₂) (hsS : 0 ≤ sS) (hsStf : sS ≤ tf)
    (hTI : IntegrableOn T (Icc 0 tf)) (hTb : ∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂) :
    ∃ σ ∈ Icc 0 sS, msig ρ₁ ρ₂ α m₀ σ sS = massOf α m₀ T sS ∧
      ∀ u ∈ Icc 0 sS, massOf α m₀ T u ≤ msig ρ₁ ρ₂ α m₀ σ u := by
  set M := massOf α m₀ T sS with hM
  obtain ⟨hM1, hM2⟩ := massOf_bounds (m₀ := m₀) ⟨hsS, hsStf⟩ hα.le hTI hTb
  set D := α * (ρ₁ - ρ₂) with hD
  have hDneg : D < 0 := mul_neg_of_pos_of_neg hα (by linarith)
  set σ := (m₀ - α * ρ₂ * sS - M) / D with hσ
  have hσD : σ * D = m₀ - α * ρ₂ * sS - M := div_mul_cancel₀ _ hDneg.ne
  have hσ0 : 0 ≤ σ := div_nonneg_of_nonpos (by linarith) hDneg.le
  have hσS : σ ≤ sS := by
    rw [hσ, div_le_iff_of_neg hDneg]; rw [hD]; nlinarith
  refine ⟨σ, ⟨hσ0, hσS⟩, ?_, fun u hu => ?_⟩
  · unfold msig
    rw [min_eq_right hσS, max_eq_left (by linarith)]
    rw [hD] at hσD; linarith
  · have huI : u ∈ Icc 0 tf := ⟨hu.1, hu.2.trans hsStf⟩
    unfold msig
    rcases le_or_gt u σ with h | h
    · rw [min_eq_left h, max_eq_right (by linarith)]
      have := (massOf_bounds (m₀ := m₀) huI hα.le hTI hTb).2
      linarith
    · rw [min_eq_right h.le, max_eq_left (by linarith)]
      have hadd := massOf_add (α := α) (m₀ := m₀) hu.1 hu.2 hsStf hTI
      have hb := (integral_Ioc_bounds hu.1 hu.2 hsStf hTI hTb).2
      have : α * ∫ s in Ioc u sS, T s ≤ α * (ρ₂ * (sS - u)) := mul_le_mul_of_nonneg_left hb hα.le
      rw [hD] at hσD
      nlinarith

/-- **Brake bound.** On the brake, `T/m ≤ ρ₂ / (m(s*) - αρ₂(s - s*))`, and the denominator stays
above `m_dry`. -/
theorem brake_le (hα : 0 ≤ α) (hρ₂ : 0 ≤ ρ₂) (hmdry : 0 < mdry) (hburn : mdry ≤ m₀ - α * ρ₂ * tf)
    (hsS : 0 ≤ sS) (hTI : IntegrableOn T (Icc 0 tf))
    (hTb : ∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂) (hm : ∀ u ∈ Icc 0 tf, mdry ≤ massOf α m₀ T u)
    {s : ℝ} (hs : s ∈ Ioc sS tf) :
    mdry ≤ massOf α m₀ T sS - α * ρ₂ * (s - sS) ∧
      T s / massOf α m₀ T s ≤ ρ₂ / (massOf α m₀ T sS - α * ρ₂ * (s - sS)) := by
  have hsI : s ∈ Icc 0 tf := ⟨hsS.trans hs.1.le, hs.2⟩
  have hadd := massOf_add (α := α) (m₀ := m₀) hsS hs.1.le hs.2 hTI
  have hb := (integral_Ioc_bounds hsS hs.1.le hs.2 hTI hTb).2
  have hM1 := (massOf_bounds (m₀ := m₀) ⟨hsS, hs.1.le.trans hs.2⟩ hα hTI hTb).1
  have h1 : α * ∫ x in Ioc sS s, T x ≤ α * (ρ₂ * (s - sS)) := mul_le_mul_of_nonneg_left hb hα
  have h2 : α * ρ₂ * s ≤ α * ρ₂ * tf := mul_le_mul_of_nonneg_left hs.2 (mul_nonneg hα hρ₂)
  have hD : mdry ≤ massOf α m₀ T sS - α * ρ₂ * (s - sS) := by nlinarith
  have hDm : massOf α m₀ T sS - α * ρ₂ * (s - sS) ≤ massOf α m₀ T s := by nlinarith
  have hDpos : 0 < massOf α m₀ T sS - α * ρ₂ * (s - sS) := lt_of_lt_of_le hmdry hD
  have hmpos : 0 < massOf α m₀ T s := lt_of_lt_of_le hDpos hDm
  refine ⟨hD, ?_⟩
  calc T s / massOf α m₀ T s ≤ ρ₂ / massOf α m₀ T s :=
        div_le_div_of_nonneg_right (hTb s hsI).2 hmpos.le
    _ ≤ ρ₂ / (massOf α m₀ T sS - α * ρ₂ * (s - sS)) :=
        div_le_div_of_nonneg_left hρ₂ hDpos hDm

theorem continuousOn_massOf (hTI : IntegrableOn T (Icc 0 tf)) :
    ContinuousOn (massOf α m₀ T) (Icc 0 tf) := by
  rcases lt_or_ge tf 0 with h | h
  · rw [Icc_eq_empty (by linarith)]; exact continuousOn_empty _
  have hTi : IntervalIntegrable T volume 0 tf :=
    (hTI.mono_set (by rw [uIcc_of_le h])).intervalIntegrable
  have hc := intervalIntegral.continuousOn_primitive_interval' (a := 0) hTi (by simp [h])
  rw [uIcc_of_le h] at hc
  have h2 : ContinuousOn (fun b => m₀ - α * ∫ x in (0 : ℝ)..b, T x) (Icc 0 tf) :=
    continuousOn_const.sub (continuousOn_const.mul hc)
  exact h2.congr fun u hu => massOf_eq_intervalIntegral hu.1

end Compare

/-! ### Decomposition of the face functional -/

theorem phiFace_decomp {α m₀ tf ω δ sS : ℝ} {a T : ℝ → ℝ} (hsS : 0 ≤ sS) (hsStf : sS ≤ tf)
    (haI : IntegrableOn a (Icc 0 tf)) (ha : ∀ s ∈ Icc 0 tf, a s = T s / massOf α m₀ T s) :
    PhiFace tf ω δ sS a = -(∫ s in (0 : ℝ)..sS, cW ω δ sS s * (T s / massOf α m₀ T s)) +
      ∫ s in sS..tf, (s - sS) * a s := by
  have hgI : IntegrableOn (fun s => a s * phiW ω δ sS s) (Icc 0 tf) :=
    haI.mul_continuousOn (continuous_phiW ω δ sS).continuousOn isCompact_Icc
  have hdisj : Disjoint (Icc 0 sS) (Ioc sS tf) :=
    Set.disjoint_left.2 fun x h1 h2 => absurd h1.2 (not_le.2 h2.1)
  rw [PhiFace, ← Icc_union_Ioc_eq_Icc hsS hsStf, setIntegral_union hdisj measurableSet_Ioc
    (hgI.mono_set (Icc_subset_Icc_right hsStf))
    (hgI.mono_set (Ioc_subset_Icc_self.trans (Icc_subset_Icc_left hsS)))]
  congr 1
  · rw [integral_Icc_eq_integral_Ioc, ← intervalIntegral.integral_of_le hsS,
      ← intervalIntegral.integral_neg]
    refine intervalIntegral.integral_congr fun x hx => ?_
    rw [uIcc_of_le hsS] at hx
    simp only [phiW, cW, min_eq_left (by linarith [hx.2] : x - sS ≤ 0),
      max_eq_right (by linarith [hx.2] : x - sS ≤ 0), add_zero, ha x ⟨hx.1, hx.2.trans hsStf⟩]
    ring
  · rw [intervalIntegral.integral_of_le hsStf]
    refine setIntegral_congr_fun measurableSet_Ioc fun x hx => ?_
    simp only [phiW, min_eq_right (by linarith [hx.1] : 0 ≤ x - sS),
      max_eq_left (by linarith [hx.1] : 0 ≤ x - sS), zero_mul, zero_add]
    ring

/-! ### The reduced value function and its maximiser -/

/-- Value of the switch profile with switch time `σ` (written so that it is continuous in `σ`;
the `max · m_dry` guards are inactive on admissible data). -/
noncomputable def wval (ρ₁ ρ₂ α m₀ mdry tf ω δ sS σ : ℝ) : ℝ :=
  -(α⁻¹ * (cW ω δ sS 0 * Real.log m₀ +
      ∫ u in (0 : ℝ)..sS, cWd ω δ sS u * Real.log (max (msig ρ₁ ρ₂ α m₀ σ u) mdry))) +
    ∫ s in sS..tf, (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ σ sS - α * ρ₂ * (s - sS)) mdry)

theorem continuous_wval {ρ₁ ρ₂ α m₀ mdry tf ω δ sS : ℝ} (hmdry : 0 < mdry) :
    Continuous (wval ρ₁ ρ₂ α m₀ mdry tf ω δ sS) := by
  have hpos : ∀ x : ℝ, max x mdry ≠ 0 := fun x => ne_of_gt (lt_of_lt_of_le hmdry (le_max_right _ _))
  have hm2 : Continuous fun p : ℝ × ℝ => msig ρ₁ ρ₂ α m₀ p.1 p.2 := by unfold msig; fun_prop
  have h1 : Continuous fun σ => ∫ u in (0 : ℝ)..sS,
      cWd ω δ sS u * Real.log (max (msig ρ₁ ρ₂ α m₀ σ u) mdry) := by
    apply intervalIntegral.continuous_parametric_intervalIntegral_of_continuous'
    exact ((continuous_cWd ω δ sS).comp continuous_snd).mul
      ((hm2.max continuous_const).log fun p => hpos _)
  have h2 : Continuous fun σ => ∫ s in sS..tf,
      (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ σ sS - α * ρ₂ * (s - sS)) mdry) := by
    apply intervalIntegral.continuous_parametric_intervalIntegral_of_continuous'
    refine (continuous_snd.sub continuous_const).mul (continuous_const.div ?_ fun p => hpos _)
    exact ((hm2.comp (continuous_fst.prodMk continuous_const)).sub
      (continuous_const.mul (continuous_snd.sub continuous_const))).max continuous_const
  unfold wval
  exact (continuous_const.mul (continuous_const.add h1)).neg.add h2

section Max

variable {ρ₁ ρ₂ α m₀ mdry tf ω δ sS : ℝ}

/-- Every admissible acceleration has face value at most `w(σ)` for some `σ ∈ [0, s*]`. -/
theorem phiFace_le_wval (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 ≤ sS) (hsStf : sS ≤ tf) (hω : 0 ≤ ω)
    (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2) {a : ℝ → ℝ}
    (ha : a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf) :
    ∃ σ ∈ Icc 0 sS, PhiFace tf ω δ sS a ≤ wval ρ₁ ρ₂ α m₀ mdry tf ω δ sS σ := by
  obtain ⟨haI, T, hTI, hTb, hm, haT⟩ := ha
  obtain ⟨σ, hσ, hMσ, hcmp⟩ := exists_sigma_compare (m₀ := m₀) hα h12 hsS hsStf hTI hTb
  refine ⟨σ, hσ, ?_⟩
  rw [phiFace_decomp hsS hsStf haI haT, dive_identity hα.ne' hmdry hsS hsStf hTI hm, wval]
  have hmpos : ∀ u ∈ Icc 0 tf, 0 < massOf α m₀ T u := fun u hu => lt_of_lt_of_le hmdry (hm u hu)
  -- dive comparison
  have hdive : ∫ u in (0 : ℝ)..sS, cWd ω δ sS u * Real.log (max (msig ρ₁ ρ₂ α m₀ σ u) mdry) ≤
      ∫ u in (0 : ℝ)..sS, cWd ω δ sS u * Real.log (massOf α m₀ T u) := by
    apply intervalIntegral.integral_mono_on hsS
    · apply Continuous.intervalIntegrable
      exact (continuous_cWd ω δ sS).mul (((continuous_msig _ _ _ _ σ).max continuous_const).log
        fun x => ne_of_gt (lt_of_lt_of_le hmdry (le_max_right _ _)))
    · apply ContinuousOn.intervalIntegrable
      rw [uIcc_of_le hsS]
      refine (continuous_cWd ω δ sS).continuousOn.mul (ContinuousOn.log ?_ fun u hu => ?_)
      · exact (continuousOn_massOf hTI).mono (Icc_subset_Icc_right hsStf)
      · exact (hmpos u ⟨hu.1, hu.2.trans hsStf⟩).ne'
    · intro u hu
      have huI : u ∈ Icc 0 tf := ⟨hu.1, hu.2.trans hsStf⟩
      apply mul_le_mul_of_nonpos_left _ (cWd_nonpos hω hδ hreg hu)
      exact Real.log_le_log (hmpos u huI) ((hcmp u hu).trans (le_max_left _ _))
  -- brake comparison
  have hbrake : ∫ s in sS..tf, (s - sS) * a s ≤
      ∫ s in sS..tf, (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ σ sS - α * ρ₂ * (s - sS)) mdry) := by
    apply intervalIntegral.integral_mono_on hsStf
    · have : IntervalIntegrable a volume sS tf :=
        (haI.mono_set (by rw [uIcc_of_le hsStf]; exact Icc_subset_Icc_left hsS)).intervalIntegrable
      exact this.continuousOn_mul (by fun_prop)
    · apply Continuous.intervalIntegrable
      refine (continuous_id.sub continuous_const).mul (continuous_const.div ?_ fun x => ?_)
      · fun_prop
      · exact ne_of_gt (lt_of_lt_of_le hmdry (le_max_right _ _))
    · intro s hs
      rcases eq_or_lt_of_le hs.1 with h | h
      · subst h; simp
      · have hsI : s ∈ Ioc sS tf := ⟨h, hs.2⟩
        obtain ⟨hD, hle⟩ := brake_le hα.le (by linarith) hmdry hburn hsS hTI hTb hm hsI
        rw [hMσ, max_eq_left hD, haT s ⟨hsS.trans h.le, hs.2⟩]
        exact mul_le_mul_of_nonneg_left hle (by linarith)
  have hαi : 0 < α⁻¹ := inv_pos.2 hα
  nlinarith [mul_le_mul_of_nonneg_left hdive hαi.le]

/-- Admissibility of the switch profiles. -/
theorem aSig_mem (hρ₁ : 0 ≤ ρ₁) (h12 : ρ₁ ≤ ρ₂) (hα : 0 ≤ α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) {σ : ℝ} (hσ : 0 ≤ σ) :
    aSig ρ₁ ρ₂ α m₀ σ ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf := by
  have hmge : ∀ s ∈ Icc 0 tf, mdry ≤ msig ρ₁ ρ₂ α m₀ σ s := fun s hs => by
    have := msig_ge (m₀ := m₀) hσ hs.1 h12 hα
    have : α * ρ₂ * s ≤ α * ρ₂ * tf := mul_le_mul_of_nonneg_left hs.2 (mul_nonneg hα (by linarith))
    linarith
  refine ⟨?_, Tsig ρ₁ ρ₂ σ, integrableOn_Tsig ρ₁ ρ₂ σ tf, fun s _ => Tsig_bounds h12 s,
    fun s hs => by rw [massOf_Tsig hσ hs.1]; exact hmge s hs,
    fun s hs => by rw [aSig, massOf_Tsig hσ hs.1]⟩
  refine Integrable.mono' (integrableOn_const (C := ρ₂ / mdry) measure_Icc_lt_top.ne)
    ((measurable_Tsig ρ₁ ρ₂ σ).div (continuous_msig _ _ _ _ σ).measurable).aestronglyMeasurable
    (ae_restrict_of_forall_mem measurableSet_Icc fun s hs => ?_)
  have hmpos : 0 < msig ρ₁ ρ₂ α m₀ σ s := lt_of_lt_of_le hmdry (hmge s hs)
  obtain ⟨hT1, hT2⟩ := Tsig_bounds (σ := σ) h12 s
  rw [Real.norm_eq_abs, aSig, abs_of_nonneg (div_nonneg (by linarith) hmpos.le)]
  calc Tsig ρ₁ ρ₂ σ s / msig ρ₁ ρ₂ α m₀ σ s ≤ ρ₂ / msig ρ₁ ρ₂ α m₀ σ s :=
        div_le_div_of_nonneg_right hT2 hmpos.le
    _ ≤ ρ₂ / mdry := div_le_div_of_nonneg_left (by linarith) hmdry (hmge s hs)

/-- The switch profiles attain the reduced value. -/
theorem phiFace_aSig (hρ₁ : 0 < ρ₁) (h12 : ρ₁ ≤ ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 ≤ sS) (hsStf : sS ≤ tf) {σ : ℝ}
    (hσ : σ ∈ Icc 0 sS) :
    PhiFace tf ω δ sS (aSig ρ₁ ρ₂ α m₀ σ) = wval ρ₁ ρ₂ α m₀ mdry tf ω δ sS σ := by
  obtain ⟨haI, -, -, -, -, -⟩ := aSig_mem (m₀ := m₀) (mdry := mdry) (tf := tf) hρ₁.le h12 hα.le
    hmdry hburn hσ.1
  have hmge : ∀ s ∈ Icc 0 tf, mdry ≤ msig ρ₁ ρ₂ α m₀ σ s := fun s hs => by
    have := msig_ge (m₀ := m₀) hσ.1 hs.1 h12 hα.le
    have : α * ρ₂ * s ≤ α * ρ₂ * tf :=
      mul_le_mul_of_nonneg_left hs.2 (mul_nonneg hα.le (by linarith))
    linarith
  have haT : ∀ s ∈ Icc 0 tf, aSig ρ₁ ρ₂ α m₀ σ s =
      Tsig ρ₁ ρ₂ σ s / massOf α m₀ (Tsig ρ₁ ρ₂ σ) s := fun s hs => by
    rw [aSig, massOf_Tsig hσ.1 hs.1]
  have hm : ∀ u ∈ Icc 0 tf, mdry ≤ massOf α m₀ (Tsig ρ₁ ρ₂ σ) u := fun u hu => by
    rw [massOf_Tsig hσ.1 hu.1]; exact hmge u hu
  have e1 : ∫ u in (0 : ℝ)..sS, cWd ω δ sS u * Real.log (massOf α m₀ (Tsig ρ₁ ρ₂ σ) u) =
      ∫ u in (0 : ℝ)..sS, cWd ω δ sS u * Real.log (max (msig ρ₁ ρ₂ α m₀ σ u) mdry) := by
    refine intervalIntegral.integral_congr fun u hu => ?_
    rw [uIcc_of_le hsS] at hu
    have huI : u ∈ Icc 0 tf := ⟨hu.1, hu.2.trans hsStf⟩
    simp only [massOf_Tsig hσ.1 hu.1, max_eq_left (hmge u huI)]
  have e2 : ∫ s in sS..tf, (s - sS) * aSig ρ₁ ρ₂ α m₀ σ s =
      ∫ s in sS..tf, (s - sS) * (ρ₂ / max (msig ρ₁ ρ₂ α m₀ σ sS - α * ρ₂ * (s - sS)) mdry) := by
    refine intervalIntegral.integral_congr fun s hs => ?_
    rw [uIcc_of_le hsStf] at hs
    rcases eq_or_lt_of_le hs.1 with h | h
    · subst h; simp
    · have hsI : s ∈ Icc 0 tf := ⟨hsS.trans h.le, hs.2⟩
      rw [← msig_brake hσ.2 h.le, max_eq_left (hmge s hsI), aSig]
      simp [Tsig, not_le.2 (lt_of_le_of_lt hσ.2 h)]
  rw [phiFace_decomp hsS hsStf haI haT,
    dive_identity hα.ne' hmdry hsS hsStf (integrableOn_Tsig ρ₁ ρ₂ σ tf) hm, wval, e1, e2]

/-- **Existence of the face maximiser in the mass-depletion class**, of switch form. -/
theorem exists_max_phiFace_mass (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 ≤ sS) (hsStf : sS ≤ tf) (hω : 0 ≤ ω)
    (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2) :
    ∃ σ ∈ Icc 0 sS, ∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      PhiFace tf ω δ sS a ≤ PhiFace tf ω δ sS (aSig ρ₁ ρ₂ α m₀ σ) := by
  obtain ⟨σs, hσs, hmax⟩ := isCompact_Icc.exists_isMaxOn (nonempty_Icc.2 hsS)
    (continuous_wval (ρ₁ := ρ₁) (ρ₂ := ρ₂) (α := α) (m₀ := m₀) (tf := tf) (ω := ω) (δ := δ)
      (sS := sS) hmdry).continuousOn
  refine ⟨σs, hσs, fun a ha => ?_⟩
  obtain ⟨σ, hσ, hle⟩ := phiFace_le_wval hρ₁ h12 hα hmdry hburn hsS hsStf hω hδ hreg ha
  rw [phiFace_aSig hρ₁ h12.le hα hmdry hburn hsS hsStf hσs]
  exact hle.trans (hmax hσ)

end Max

/-! ### Theorem B* with mass depletion -/

/-- **Theorem B\* with explicit mass depletion (`α > 0`).** Thrust `ρ₁ ≤ T ≤ ρ₂` (`0 < ρ₁ < ρ₂`),
`ṁ = -αT` (`α > 0`), dry mass `m_dry` with `m_dry ≤ m₀ - αρ₂ tf` (a full-throttle burn over the
horizon stays above the dry mass), gravity `-g₀ e_z` with `0 ≤ g₀ ≤ ρ₂/m₀`, switch time `s*` with
`ω s* ≤ δ`, `δ + ω s* ≤ π/2` and the smallness condition
`(ρ₂/m₀ + 2 tanγ ρ₂/m_dry) s*² ≤ (ρ₂/m₀ - g₀)(tf - s*)²`. Then for every state-constraint set
`X ⊇ glideSlopeSet tanγ` the constrained landing set of the mass-depletion model is not convex. -/
theorem not_convex_constrainedLandingSet_mass {ρ₁ ρ₂ α m₀ mdry tf ω δ sS g₀ tanγ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω)
    (hωs : ω * sS ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ ρ₂ / m₀)
    (htan : 0 ≤ tanγ)
    (hS : (ρ₂ / m₀ + 2 * tanγ * (ρ₂ / mdry)) * sS ^ 2 ≤ (ρ₂ / m₀ - g₀) * (tf - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (constrainedLandingSet (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hρ₂ : 0 < ρ₂ := hρ₁.trans h12
  have htf : 0 < tf := hsS.trans hsStf
  have hm0 : mdry ≤ m₀ := by nlinarith [mul_pos (mul_pos hα hρ₂) htf]
  have hm0pos : 0 < m₀ := hmdry.trans_le hm0
  obtain ⟨σ, hσ, hmax⟩ := exists_max_phiFace_mass (ω := ω) (δ := δ) hρ₁ h12 hα hmdry hburn
    hsS.le hsStf.le hω.le hδ hreg
  have hmge : ∀ s ∈ Icc 0 tf, mdry ≤ msig ρ₁ ρ₂ α m₀ σ s := fun s hs => by
    have := msig_ge (m₀ := m₀) hσ.1 hs.1 h12.le hα.le
    have : α * ρ₂ * s ≤ α * ρ₂ * tf := mul_le_mul_of_nonneg_left hs.2 (by positivity)
    linarith
  -- every admissible acceleration is `≥ ρ₁/m₀ > 0`
  have hAcc : ∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, ρ₁ / m₀ ≤ a s := by
    intro a ha
    obtain ⟨haI, hlow⟩ := accMass_spec hρ₁.le hα.le hmdry a ha
    refine ⟨haI, fun s hs => le_trans ?_ (hlow s hs)⟩
    have hpos : 0 < m₀ - α * ρ₁ * s := by
      have : α * ρ₁ * s ≤ α * ρ₂ * tf :=
        mul_le_mul (mul_le_mul_of_nonneg_left h12.le hα.le) hs.2 hs.1 (by positivity)
      linarith
    have : m₀ - α * ρ₁ * s ≤ m₀ := by nlinarith [mul_nonneg (mul_nonneg hα.le hρ₁.le) hs.1]
    exact div_le_div_of_nonneg_left hρ₁.le hpos this
  refine not_convex_constrainedLandingSet_of_max (amin := ρ₁ / m₀) (A := ρ₂ / mdry)
    (B := ρ₂ / m₀) hsS hsStf hω hωs hreg (by positivity) hAcc
    (aSig_mem hρ₁.le h12.le hα.le hmdry hburn hσ.1) hmax ?_ ?_ hg0 hg htan hS hX
  · intro s hs _
    have hmpos : 0 < msig ρ₁ ρ₂ α m₀ σ s := hmdry.trans_le (hmge s hs)
    obtain ⟨hT1, hT2⟩ := Tsig_bounds (σ := σ) h12.le s
    refine ⟨div_nonneg (by linarith) hmpos.le, ?_⟩
    calc aSig ρ₁ ρ₂ α m₀ σ s ≤ ρ₂ / msig ρ₁ ρ₂ α m₀ σ s :=
          div_le_div_of_nonneg_right hT2 hmpos.le
      _ ≤ ρ₂ / mdry := div_le_div_of_nonneg_left hρ₂.le hmdry (hmge s hs)
  · intro s hs hss
    have hmpos : 0 < msig ρ₁ ρ₂ α m₀ σ s := hmdry.trans_le (hmge s hs)
    have hT : Tsig ρ₁ ρ₂ σ s = ρ₂ := by simp [Tsig, not_le.2 (lt_of_le_of_lt hσ.2 hss)]
    rw [aSig, hT]
    exact div_le_div_of_nonneg_left hρ₂.le hmpos (msig_le hσ.1 hs.1 hρ₁.le h12.le hα.le)

/-- **Main theorem, state-constrained, explicit mass depletion, every horizon.** For every
`tf > 0`, gimbal `0 < δ < π/2`, slew rate `ω > 0`, throttle `0 < ρ₁ < ρ₂`, `α > 0`,
`0 < m_dry ≤ m₀ - αρ₂ tf`, gravity `0 ≤ g₀ < ρ₂/m₀`, `tanγ ≥ 0`, and every `X ⊇ glideSlopeSet tanγ`,
no uniform convex relaxation is lossless for the constrained landing set of the mass-depletion
model. -/
theorem no_lossless_relaxation_constrained_5dof_mass {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {ρ₁ ρ₂ α m₀ mdry tf ω δ g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsStf, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := ρ₂ / mdry) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet_mass hρ₁ h12 hα hmdry hburn hsS hsStf hω hωs hreg hg0 hg.le
      htan hS hX) R

/-- LCvx (optimisation) form, every cost `J`. -/
theorem no_losslessFor_relaxation_constrained_5dof_mass {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {ρ₁ ρ₂ α m₀ mdry tf ω δ g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) (J : E3 × E3 → Y → ℝ) :
    ¬ R.IsLosslessFor J
      (constrainedLandingSet (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) :=
  fun hL => no_lossless_relaxation_constrained_5dof_mass htf hω hδ hδ2 hρ₁ h12 hα hmdry hburn
    hg0 hg htan hX R hL.isLossless

end LcvxObstruction
