import LcvxObstruction.DiveBrakeMassModel
import LcvxObstruction.Upright

/-!
# Theorem B* with mass depletion: upright landing and kinematic 6DOF variants

Same witnesses as `Upright.lean` / `SixDOF.lean` (dive-then-brake attitude, upright return for
variant T', zero-roll rotation lift for 6DOF), with the mass-depletion throttle `aSig σ*` of
`DiveBrakeMassModel.lean` in place of the constant min-then-max profile.

* `witnessG_midpoint_not_mem_landingSet`: midpoint of the mirror witnesses (any face maximiser `â`)
  is not unconstrained-feasible.
* `accMass_lower`, `exists_mass_witness`: the mass class has `a ≥ ρ₁/m₀ > 0`, and a face maximiser
  with `0 ≤ â ≤ ρ₂/m_dry` on the dive and `â ≥ ρ₂/m₀` on the brake.
* `no_lossless_relaxation_constrained_upright_5dof_mass`,
  `no_lossless_relaxation_constrained_6dof_mass`,
  `no_lossless_relaxation_constrained_upright_6dof_mass`: headline theorems, every `tf > 0`.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- Step 6 of Theorem B* for any acceleration class with a face maximiser `â`. -/
theorem witnessG_midpoint_not_mem_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin g₀ : ℝ}
    {ah : ℝ → ℝ} (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s)
    (hah : ah ∈ Acc) (hmax : ∀ a ∈ Acc, PhiFace tf ω δ sS a ≤ PhiFace tf ω δ sS ah) :
    (1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS ex) tf +
      (1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS (-ex)) tf ∉
      landingSet Acc tf ω δ (-(g₀ • ez)) := by
  set g := -(g₀ • ez)
  have haI := (hAcc ah hah).1
  rintro ⟨a, d, b, ha, hatt, hr, hv⟩
  have hfa : IntegrableOn (fun s => a s • d s) (Icc 0 tf) :=
    integrableOn_smul_of_unit (hAcc a ha).1 hatt.d_meas hatt.d_unit
  have hΛ := lambda_identity (sS := sS) hfa hr hv
  have hΛ₁ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) norm_ex inner_ex_ez haI) (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hΛ₂ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) (by simp : ‖-ex‖ = 1) (by simp : ⟪-ex, ez⟫ = 0) haI)
    (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hW := witnessG_W_midpoint (tf := tf) (ω := ω) (δ := δ) (sS := sS) norm_ex inner_ex_ez haI
  apply PhiMax_not_mem_WSet hsS hsStf hω hδ hreg hamin hAcc hmax
  refine ⟨a, d, b, ha, hatt, ?_⟩
  simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd] at hΛ
  rw [← hW]
  linear_combination (norm := module) hΛ - (1 / 2 : ℝ) • hΛ₁ - (1 / 2 : ℝ) • hΛ₂

section Mass

variable {ρ₁ ρ₂ α m₀ mdry tf ω δ sS : ℝ}

theorem accMass_lower (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) :
    ∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, ρ₁ / m₀ ≤ a s := by
  intro a ha
  obtain ⟨haI, hlow⟩ := accMass_spec hρ₁.le hα.le hmdry a ha
  refine ⟨haI, fun s hs => le_trans ?_ (hlow s hs)⟩
  have hρ₂ : 0 < ρ₂ := hρ₁.trans h12
  have hpos : 0 < m₀ - α * ρ₁ * s := by
    have : α * ρ₁ * s ≤ α * ρ₂ * tf :=
      mul_le_mul (mul_le_mul_of_nonneg_left h12.le hα.le) hs.2 hs.1 (by positivity)
    linarith
  have : m₀ - α * ρ₁ * s ≤ m₀ := by nlinarith [mul_nonneg (mul_nonneg hα.le hρ₁.le) hs.1]
  exact div_le_div_of_nonneg_left hρ₁.le hpos this

/-- The mass-depletion face maximiser with its witness bounds. -/
theorem exists_mass_witness (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 ≤ sS) (hsStf : sS ≤ tf) (hω : 0 ≤ ω)
    (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2) :
    ∃ ah ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      (∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf, PhiFace tf ω δ sS a ≤ PhiFace tf ω δ sS ah) ∧
      (∀ s ∈ Icc 0 tf, s ≤ sS → 0 ≤ ah s ∧ ah s ≤ ρ₂ / mdry) ∧
      (∀ s ∈ Icc 0 tf, sS < s → ρ₂ / m₀ ≤ ah s) := by
  have hρ₂ : 0 < ρ₂ := hρ₁.trans h12
  obtain ⟨σ, hσ, hmax⟩ := exists_max_phiFace_mass (ω := ω) (δ := δ) hρ₁ h12 hα hmdry hburn
    hsS hsStf hω hδ hreg
  have hmge : ∀ s ∈ Icc 0 tf, mdry ≤ msig ρ₁ ρ₂ α m₀ σ s := fun s hs => by
    have := msig_ge (m₀ := m₀) hσ.1 hs.1 h12.le hα.le
    have : α * ρ₂ * s ≤ α * ρ₂ * tf := mul_le_mul_of_nonneg_left hs.2 (by positivity)
    linarith
  refine ⟨aSig ρ₁ ρ₂ α m₀ σ, aSig_mem hρ₁.le h12.le hα.le hmdry hburn hσ.1, hmax,
    fun s hs _ => ?_, fun s hs hss => ?_⟩
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

end Mass

/-! ### Upright landing (variant T'), 5DOF -/

theorem not_convex_constrainedLandingSetUp_mass {ρ₁ ρ₂ α m₀ mdry tf ω δ sS g₀ tanγ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 < sS) (h2sS : 2 * sS ≤ tf) (hω : 0 < ω)
    (hωs : ω * sS ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ ρ₂ / m₀)
    (htan : 0 ≤ tanγ)
    (hS : (ρ₂ / m₀ + 2 * tanγ * (ρ₂ / mdry)) * sS ^ 2 ≤ (ρ₂ / m₀ - g₀) * (tf - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (constrainedLandingSetUp (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have hsStf : sS < tf := by linarith
  have hm0 : 0 < m₀ := by nlinarith [mul_pos (mul_pos hα (hρ₁.trans h12)) (hsS.trans hsStf)]
  obtain ⟨ah, hah, hmax, hdive, hbrake⟩ := exists_mass_witness (ω := ω) (δ := δ) hρ₁ h12 hα
    hmdry hburn hsS.le hsStf.le hω.le hδ hreg
  have haI := (accMass_lower hρ₁ h12 hα hmdry hburn ah hah).1
  have mem : ∀ v : E3, ‖v‖ = 1 → ⟪v, ez⟫ = 0 →
      landingData (-(g₀ • ez)) ah (dW ω δ sS v) tf ∈
        constrainedLandingSetUp (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X :=
    fun v hv hvz => ⟨_, _, _, hah, witness_admissible_upright hv hvz hsS hω.le hδ hδπ hωs,
      by simp [bWU, arcB, phiUp_of_ge h2sS],
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witnessG_mem_glideSlope hv hvz hsS hsStf hω.le hδ hreg haI hdive hbrake
        hg0 hg htan hS ht)⟩
  exact not_convex_of_midpoint constrainedLandingSetUp_subset (mem ex norm_ex inner_ex_ez)
    (mem (-ex) (by simp) (by simp))
    (witnessG_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg (by positivity)
      (accMass_lower hρ₁ h12 hα hmdry hburn) hah hmax)

/-! ### Kinematic 6DOF, terminal attitude free and upright -/

theorem not_convex_constrainedLandingSet6_mass {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))}
    {ρ₁ ρ₂ α m₀ mdry tf ω δ sS g₀ tanγ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω)
    (hωs : ω * sS ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ ρ₂ / m₀)
    (htan : 0 ≤ tanγ)
    (hS : (ρ₂ / m₀ + 2 * tanγ * (ρ₂ / mdry)) * sS ^ 2 ≤ (ρ₂ / m₀ - g₀) * (tf - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (hAtt : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) → (fun s => rotY (σ * (ω * min s sS))) ∈ Att) :
    ¬ Convex ℝ (constrainedLandingSet6 Att (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have hm0 : 0 < m₀ := by nlinarith [mul_pos (mul_pos hα (hρ₁.trans h12)) (hsS.trans hsStf)]
  obtain ⟨ah, hah, hmax, hdive, hbrake⟩ := exists_mass_witness (ω := ω) (δ := δ) hρ₁ h12 hα
    hmdry hburn hsS.le hsStf.le hω.le hδ hreg
  have haI := (accMass_lower hρ₁ h12 hα hmdry hburn ah hah).1
  have mem : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      landingData (-(g₀ • ez)) ah (dW ω δ sS (σ • ex)) tf ∈
        constrainedLandingSet6 Att (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X := by
    intro σ hσ
    have hu : ‖σ • ex‖ = 1 := by rcases hσ with rfl | rfl <;> simp
    have huz : ⟪σ • ex, ez⟫ = 0 := by rw [real_inner_smul_left, inner_ex_ez, mul_zero]
    have hd : AttitudeAdmissible tf ω δ (dW ω δ sS (σ • ex))
        (fun s => rotY (σ * (ω * (fun s => min s sS) s)) ez) := by
      have := witness_admissible (tf := tf) hu huz hsS hω.le hδ hδπ hωs
      convert this using 2 with s
      rw [rotY_ez_pm σ _ hσ]; rfl
    refine ⟨_, _, _, hah, lift_admissible (φ := fun s => min s sS) σ hσ (by fun_prop)
      (min_eq_left hsS.le) (fun s _ s' _ => (abs_min_sub_min_le_max _ _ _ _).trans (by simp))
      (fun s hs s' hs' => ?_) hω.le (hAtt σ hσ) hd,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witnessG_mem_glideSlope hu huz hsS hsStf hω.le hδ hreg haI hdive hbrake
        hg0 hg htan hS ht)⟩
    have hmS : |min s sS - min s' sS| ≤ sS := by
      rw [abs_sub_le_iff]
      constructor <;> linarith [min_le_right s sS, min_le_right s' sS,
        le_min hs.1 hsS.le, le_min hs'.1 hsS.le]
    nlinarith [mul_le_mul_of_nonneg_left hmS hω.le]
  have m1 := mem 1 (Or.inl rfl)
  have m2 := mem (-1) (Or.inr rfl)
  rw [one_smul] at m1
  rw [neg_one_smul] at m2
  exact not_convex_of_midpoint constrainedLandingSet6_subset m1 m2
    (witnessG_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg (by positivity)
      (accMass_lower hρ₁ h12 hα hmdry hburn) hah hmax)

theorem not_convex_constrainedLandingSet6Up_mass {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))}
    {ρ₁ ρ₂ α m₀ mdry tf ω δ sS g₀ tanγ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 < sS) (h2sS : 2 * sS ≤ tf) (hω : 0 < ω)
    (hωs : ω * sS ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ ρ₂ / m₀)
    (htan : 0 ≤ tanγ)
    (hS : (ρ₂ / m₀ + 2 * tanγ * (ρ₂ / mdry)) * sS ^ 2 ≤ (ρ₂ / m₀ - g₀) * (tf - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (hAtt : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) → (fun s => rotY (σ * (ω * phiUp sS s))) ∈ Att) :
    ¬ Convex ℝ
      (constrainedLandingSet6Up Att (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have hsStf : sS < tf := by linarith
  have hm0 : 0 < m₀ := by nlinarith [mul_pos (mul_pos hα (hρ₁.trans h12)) (hsS.trans hsStf)]
  obtain ⟨ah, hah, hmax, hdive, hbrake⟩ := exists_mass_witness (ω := ω) (δ := δ) hρ₁ h12 hα
    hmdry hburn hsS.le hsStf.le hω.le hδ hreg
  have haI := (accMass_lower hρ₁ h12 hα hmdry hburn ah hah).1
  have mem : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      landingData (-(g₀ • ez)) ah (dW ω δ sS (σ • ex)) tf ∈
        constrainedLandingSet6Up Att (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X := by
    intro σ hσ
    have hu : ‖σ • ex‖ = 1 := by rcases hσ with rfl | rfl <;> simp
    have huz : ⟪σ • ex, ez⟫ = 0 := by rw [real_inner_smul_left, inner_ex_ez, mul_zero]
    have hd : AttitudeAdmissible tf ω δ (dW ω δ sS (σ • ex))
        (fun s => rotY (σ * (ω * phiUp sS s)) ez) := by
      have := witness_admissible_upright (tf := tf) hu huz hsS hω.le hδ hδπ hωs
      convert this using 2 with s
      rw [rotY_ez_pm σ _ hσ]; rfl
    refine ⟨_, _, _, hah, lift_admissible (φ := phiUp sS) σ hσ (by unfold phiUp; fun_prop)
      (phiUp_of_le le_rfl hsS.le) (fun s _ s' _ => phiUp_lipschitz sS s s')
      (fun s hs s' hs' => ?_) hω.le (hAtt σ hσ) hd, ?_,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witnessG_mem_glideSlope hu huz hsS hsStf hω.le hδ hreg haI hdive hbrake
        hg0 hg htan hS ht)⟩
    · have hmS : |phiUp sS s - phiUp sS s'| ≤ sS := by
        rw [abs_sub_le_iff]
        constructor <;> linarith [phiUp_le' hsS.le s, phiUp_le' hsS.le s', phiUp_nonneg sS s,
          phiUp_nonneg sS s']
      nlinarith [mul_le_mul_of_nonneg_left hmS hω.le]
    · simp only [phiUp_of_ge h2sS, mul_zero, rotY_zero_ez]
  have m1 := mem 1 (Or.inl rfl)
  have m2 := mem (-1) (Or.inr rfl)
  rw [one_smul] at m1
  rw [neg_one_smul] at m2
  exact not_convex_of_midpoint constrainedLandingSet6Up_subset m1 m2
    (witnessG_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg (by positivity)
      (accMass_lower hρ₁ h12 hα hmdry hburn) hah hmax)

/-! ### Headlines, every horizon -/

/-- **Main theorem, state-constrained, upright landing, explicit mass depletion (5DOF).** -/
theorem no_lossless_relaxation_constrained_upright_5dof_mass {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {ρ₁ ρ₂ α m₀ mdry tf ω δ g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless
      (constrainedLandingSetUp (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, -, hωs, hreg, hS, h2⟩ :=
    exists_switchTime (amin := ρ₂ / mdry) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSetUp_mass hρ₁ h12 hα hmdry hburn hsS h2 hω hωs hreg hg0 hg.le
      htan hS hX) R

/-- **Main theorem, state-constrained, kinematic 6DOF (proper rotations), explicit mass
depletion**, terminal attitude free. -/
theorem no_lossless_relaxation_constrained_6dof_mass {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {ρ₁ ρ₂ α m₀ mdry tf ω δ g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet6 properAttitudes (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ
      (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsStf, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := ρ₂ / mdry) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet6_mass hρ₁ h12 hα hmdry hburn hsS hsStf hω hωs hreg hg0
      hg.le htan hS hX (fun σ _ => rotY_path_mem_proper (fun s => σ * (ω * min s sS)))) R

/-- **Main theorem, state-constrained, upright landing, kinematic 6DOF, explicit mass
depletion.** -/
theorem no_lossless_relaxation_constrained_upright_6dof_mass {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {ρ₁ ρ₂ α m₀ mdry tf ω δ g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hg0 : 0 ≤ g₀) (hg : g₀ < ρ₂ / m₀) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet6Up properAttitudes (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ
      (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, -, hωs, hreg, hS, h2⟩ :=
    exists_switchTime (amin := ρ₂ / mdry) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet6Up_mass hρ₁ h12 hα hmdry hburn hsS h2 hω hωs hreg hg0
      hg.le htan hS hX (fun σ _ => rotY_path_mem_proper (fun s => σ * (ω * phiUp sS s)))) R

end LcvxObstruction
