import LcvxObstruction.DiveBrakeQuant
import LcvxObstruction.FreeTimeBStar

/-!
# Quantitative Theorem B* for any acceleration class with a face maximiser, and for mass depletion

Step 7 of math/02 §10.3 with the deficit measured against the face maximiser `â`
(Remark 10.3): `V* − W_z(c) ≥ η_d + η_b` because `PhiFace(a) ≤ PhiFace(â) = V*`. The rest of the
proof (`brake_lateral_le`, `dive_lateral_ge`) only uses `a_min ≤ a ≤ a_max` pointwise, so it applies
to the mass-depletion class with `a_min = ρ₁/m₀`, `a_max = ρ₂/m_dry`.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

set_option maxHeartbeats 1600000 in
/-- **Theorem B\*, quantitative, for any acceleration class with bounds `a_min ≤ a ≤ a_max` and a face maximiser `â`** (the witnesses use `â`).
For `0 < δ ≤ π/4`, `ω s* ≤ δ`, `0 < a_min ≤ a_max`, every boundary datum `θ` of the unconstrained
landing set satisfies `‖Λ(θ) − Λ(θ_m)‖ ≥ η₀`, where `Λ(θ) = r₀ + s* v₀`, `θ_m` is the midpoint of
the two mirror dive-then-brake witnesses, and `η₀ ≥ 0` is any number with
`(1 + c₁) η₀ + √(2 W_b η₀) ≤ γ_X`. -/
theorem lambda_dist_ge_of_max {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ η₀ : ℝ} {ah : ℝ → ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 < δ) (hδ4 : δ ≤ π / 4)
    (hωs : ω * sS ≤ δ) (hamin : 0 < amin) (h : amin ≤ amax)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (hah : ah ∈ Acc) (hmax : ∀ a ∈ Acc, PhiFace tf ω δ sS a ≤ PhiFace tf ω δ sS ah)
    (hη₀ : 0 ≤ η₀)
    (hη₀γ : (1 + 1 / (ω * (amin * Real.sin δ / (4 * amax) * sS))) * η₀ +
      Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) ≤ 5 / 32 * amin * Real.sin δ * sS ^ 2)
    {θ : E3 × E3} (hθ : θ ∈ landingSet Acc tf ω δ (-(g₀ • ez))) :
    η₀ ≤ ‖(θ.1 + sS • θ.2) -
      (((1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS (-ex)) tf).1 +
       sS • ((1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS (-ex)) tf).2)‖ := by
  set g := -(g₀ • ez) with hgdef
  obtain ⟨a, d, b, ha, hatt, hr, hv⟩ := hθ
  obtain ⟨haI, hab⟩ := hAcc a ha
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hδπ2 : δ + ω * sS ≤ π / 2 := by linarith
  -- Λ identities
  have hfa : IntegrableOn (fun s => a s • d s) (Icc 0 tf) :=
    integrableOn_smul_of_unit haI hatt.d_meas hatt.d_unit
  have hΛ := lambda_identity (sS := sS) hfa hr hv
  have haIh := (hAcc ah hah).1
  have hΛ₁ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) norm_ex inner_ex_ez haIh) (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hΛ₂ := lambda_identity (sS := sS) (integrableOn_witnessG (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) (by simp : ‖-ex‖ = 1) (by simp : ⟪-ex, ez⟫ = 0) haIh)
    (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hWm := witnessG_W_midpoint (tf := tf) (ω := ω) (δ := δ) (sS := sS) norm_ex inner_ex_ez haIh
  set W := ∫ s in Icc 0 tf, (s - sS) • (a s • d s) with hW
  set Vs := PhiFace tf ω δ sS ah with hVs
  have hD : (θ.1 + sS • θ.2) -
      (((1 / 2 : ℝ) • landingData g ah (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData g ah (dW ω δ sS (-ex)) tf).1 +
       sS • ((1 / 2 : ℝ) • landingData g ah (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData g ah (dW ω δ sS (-ex)) tf).2) = W - Vs • ez := by
    simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd]
    rw [← hWm]
    linear_combination (norm := module) hΛ - (1 / 2 : ℝ) • hΛ₁ - (1 / 2 : ℝ) • hΛ₂
  rw [hD]
  -- split into dive and brake
  have hsub1 : Icc 0 sS ⊆ Icc 0 tf := Icc_subset_Icc_right hsStf.le
  have hsub2 : Ioc sS tf ⊆ Icc 0 tf := Ioc_subset_Icc_self.trans (Icc_subset_Icc_left hsS.le)
  have hdisj : Disjoint (Icc 0 sS) (Ioc sS tf) :=
    Set.disjoint_left.2 fun x h1 h2 => absurd h1.2 (not_le.2 h2.1)
  have hunion : Icc 0 sS ∪ Ioc sS tf = Icc 0 tf := Icc_union_Ioc_eq_Icc hsS.le hsStf.le
  have hfW : IntegrableOn (fun s => (s - sS) • (a s • d s)) (Icc 0 tf) :=
    integrableOn_cont_smul hfa (c := fun s => s - sS) (by fun_prop)
  set Xv := ∫ s in Icc 0 sS, (sS - s) • (a s • d s) with hXv
  set Bv := ∫ s in Ioc sS tf, (s - sS) • (a s • d s) with hBv
  have hWXB : W = Bv - Xv := by
    rw [hW, ← hunion, setIntegral_union hdisj measurableSet_Ioc (hfW.mono_set hsub1)
      (hfW.mono_set hsub2), hXv, hBv]
    have : ∫ s in Icc 0 sS, (s - sS) • (a s • d s) = -∫ s in Icc 0 sS, (sS - s) • (a s • d s) := by
      rw [← integral_neg]
      exact setIntegral_congr_fun measurableSet_Icc fun s _ => by module
    rw [this]; abel
  -- the deficits
  have hmem1 : ∀ s ∈ Icc 0 sS, s ∈ Icc 0 tf := fun s hs => hsub1 hs
  have hmem2 : ∀ s ∈ Ioc sS tf, s ∈ Icc 0 tf := fun s hs => hsub2 hs
  have haS : IntegrableOn a (Icc 0 sS) := haI.mono_set hsub1
  have haB : IntegrableOn a (Ioc sS tf) := haI.mono_set hsub2
  have hIg1 : ∀ g' : ℝ → ℝ, Continuous g' →
      IntegrableOn (fun s => (sS - s) * a s * g' s) (Icc 0 sS) := fun g' hg' =>
    (haS.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => sS - s) (Icc 0 sS))
      isCompact_Icc).mul_continuousOn hg'.continuousOn isCompact_Icc
  have hfX : IntegrableOn (fun s => (sS - s) • (a s • d s)) (Icc 0 sS) :=
    (integrableOn_cont_smul hfa (c := fun s => sS - s) (by fun_prop)).mono_set hsub1
  have hfB : IntegrableOn (fun s => (s - sS) • (a s • d s)) (Ioc sS tf) := hfW.mono_set hsub2
  have hwaB : IntegrableOn (fun s => (s - sS) * a s) (Ioc sS tf) :=
    (haI.continuousOn_mul (by fun_prop : ContinuousOn (fun s : ℝ => s - sS) (Icc 0 tf))
      isCompact_Icc).mono_set hsub2
  set Z0 := ∫ s in Icc 0 sS, (sS - s) * a s * Real.cos (δ + ω * s) with hZ0
  set J2 := ∫ s in Ioc sS tf, (s - sS) * a s with hJ2
  set J3 := ∫ s in Ioc sS tf, ⟪(s - sS) • (a s • d s), ez⟫ with hJ3
  set ηb := ∫ s in Ioc sS tf, (s - sS) * (a s * (1 - ⟪d s, ez⟫)) with hηb
  have hcos0 : ∀ s ∈ Icc 0 sS, 0 ≤ Real.cos (δ + ω * s) := fun s hs =>
    Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [hs.1, Real.pi_pos], by nlinarith [hs.2]⟩
  have hηbeq : ηb = J2 - J3 := by
    rw [hηb, hJ2, hJ3, ← integral_sub hwaB (hfB.inner_const ez)]
    exact setIntegral_congr_fun measurableSet_Ioc fun s _ => by
      simp only [real_inner_smul_left]; ring
  have hBz : ⟪Bv, ez⟫ = J3 := by
    rw [hBv, real_inner_comm, ← integral_inner hfB]
    exact setIntegral_congr_fun measurableSet_Ioc fun s _ => real_inner_comm _ _
  have hVge : -Z0 + J2 ≤ Vs := by
    have hPa : PhiFace tf ω δ sS a = -Z0 + J2 := by
      have hgI : IntegrableOn (fun s => a s * phiW ω δ sS s) (Icc 0 tf) :=
        haI.mul_continuousOn (continuous_phiW ω δ sS).continuousOn isCompact_Icc
      rw [PhiFace, ← hunion, setIntegral_union hdisj measurableSet_Ioc (hgI.mono_set hsub1)
        (hgI.mono_set hsub2), hZ0, hJ2, ← integral_neg]
      congr 1
      · exact setIntegral_congr_fun measurableSet_Icc fun s hs => by
          simp only [phiW, min_eq_left (by linarith [hs.2] : s - sS ≤ 0),
            max_eq_right (by linarith [hs.2] : s - sS ≤ 0)]; ring
      · exact setIntegral_congr_fun measurableSet_Ioc fun s hs => by
          simp only [phiW, min_eq_right (by linarith [hs.1] : 0 ≤ s - sS),
            max_eq_left (by linarith [hs.1] : 0 ≤ s - sS)]; ring
    rw [← hPa, hVs]; exact hmax a ha
  have hXz : Z0 ≤ ⟪Xv, ez⟫ := by
    rw [hXv, real_inner_comm, ← integral_inner hfX]
    refine setIntegral_mono_on (hIg1 _ (by fun_prop)) (hfX.const_inner ez) measurableSet_Icc
      fun s hs => ?_
    rw [real_inner_smul_right, real_inner_smul_right, real_inner_comm (d s) ez]
    have hw : 0 ≤ (sS - s) * a s :=
      mul_nonneg (by linarith [hs.2]) (hamin.le.trans (hab s (hmem1 s hs)).1)
    have := hatt.inner_d_ez hω.le hδ.le (hmem1 s hs) (by nlinarith [hs.2, Real.pi_pos])
    nlinarith [mul_le_mul_of_nonneg_left this hw]
  have hηbnn : 0 ≤ ηb := setIntegral_nonneg measurableSet_Ioc fun s hs =>
    mul_nonneg (by linarith [hs.1]) (mul_nonneg (hamin.le.trans (hab s (hmem2 s hs)).1)
      (by linarith [inner_le_one_of_unit (hatt.d_unit s (hmem2 s hs)) norm_ez]))
  set η := Vs - ⟪W, ez⟫ with hη
  set ηd := ⟪Xv, ez⟫ - Z0 with hηd
  have hWz : ⟪W, ez⟫ = J3 - ⟪Xv, ez⟫ := by rw [hWXB, inner_sub_left, hBz]
  have hηsum : ηd + ηb ≤ η := by
    rw [hη, hWz, hηd, hηbeq]; linarith
  have hηd0 : 0 ≤ ηd := by rw [hηd]; linarith
  -- lateral parts
  have hbr := brake_lateral_le (amax := amax) hsS.le hsStf.le haI hatt.d_meas hatt.d_unit
    (fun s hs => hamin.le.trans (hab s hs).1) (fun s hs => (hab s hs).2)
  have hdv := dive_lateral_ge hatt hsS hsStf.le hω hδ hδ4 hωs hamin haI hab
  rw [← hXv, ← hZ0, ← hηd] at hdv
  rw [← hBv, ← hηb] at hbr
  obtain ⟨hlat, hvert⟩ := norm_ge_lateral_vertical (W - Vs • ez)
  have hDz : ⟪W - Vs • ez, ez⟫ = -η := by
    rw [inner_sub_left, real_inner_smul_left, hzz, hη]; ring
  have hDh : (W - Vs • ez) - ⟪W - Vs • ez, ez⟫ • ez =
      (Bv - ⟪Bv, ez⟫ • ez) - (Xv - ⟪Xv, ez⟫ • ez) := by
    rw [hDz, hη, hWXB, inner_sub_left]; module
  rw [hDz, abs_neg] at hvert
  rw [hDh] at hlat
  have htri := norm_sub_norm_le (Xv - ⟪Xv, ez⟫ • ez) (Bv - ⟪Bv, ez⟫ • ez)
  rw [norm_sub_rev (Xv - ⟪Xv, ez⟫ • ez)] at htri
  have hη0' : 0 ≤ η := by linarith
  rcases le_or_gt η₀ η with hcase | hcase
  · calc η₀ ≤ η := hcase
      _ = |η| := (abs_of_nonneg hη0').symm
      _ ≤ _ := hvert
  · -- η < η₀
    set τ := amin * Real.sin δ / (4 * amax) * sS with hτ
    have hsinδ : 0 < Real.sin δ := Real.sin_pos_of_pos_of_lt_pi hδ (by linarith [Real.pi_pos])
    have hτ0 : 0 < ω * τ := by have : 0 < amax := hamin.trans_le h; positivity
    have hsq : Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * ηb) ≤
        Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) := by
      apply Real.sqrt_le_sqrt
      have : 0 ≤ 2 * (amax * (tf - sS) ^ 2 / 2) := by
        have : 0 < amax := hamin.trans_le h; positivity
      exact mul_le_mul_of_nonneg_left (by linarith) this
    have hdiv : ηd / (ω * τ) ≤ 1 / (ω * τ) * η₀ := by
      rw [div_eq_mul_one_div, mul_comm]
      exact mul_le_mul_of_nonneg_left (by linarith) (by positivity)
    have : η₀ ≤ 5 / 32 * amin * Real.sin δ * sS ^ 2 - 1 / (ω * τ) * η₀ -
        Real.sqrt (2 * (amax * (tf - sS) ^ 2 / 2) * η₀) := by
      rw [hτ]; nlinarith [hη₀γ]
    linarith


/-- **Quantitative Theorem B\* with explicit mass depletion.** With the mass-depletion face
maximiser `â` (min throttle, then max throttle), every point of the unconstrained landing set of the
mass model is at distance `≥ η₀/(1 + s*)` from the witness midpoint, for every `η₀ ≥ 0` with
`(1 + c₁) η₀ + √(2 W_b η₀) ≤ γ_X` computed with `a_min = ρ₁/m₀`, `a_max = ρ₂/m_dry`. -/
theorem landingSet_dist_ge_mass {ρ₁ ρ₂ α m₀ mdry tf ω δ sS g₀ η₀ : ℝ}
    (hρ₁ : 0 < ρ₁) (h12 : ρ₁ < ρ₂) (hα : 0 < α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₂ * tf) (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω)
    (hδ : 0 < δ) (hδ4 : δ ≤ π / 4) (hωs : ω * sS ≤ δ) (hη₀ : 0 ≤ η₀)
    (hη₀γ : (1 + 1 / (ω * (ρ₁ / m₀ * Real.sin δ / (4 * (ρ₂ / mdry)) * sS))) * η₀ +
      Real.sqrt (2 * (ρ₂ / mdry * (tf - sS) ^ 2 / 2) * η₀) ≤
        5 / 32 * (ρ₁ / m₀) * Real.sin δ * sS ^ 2) :
    ∃ ah ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf, ∀ θ ∈ landingSet (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ (-(g₀ • ez)),
      η₀ / (1 + sS) ≤ ‖θ - ((1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS ex) tf +
        (1 / 2 : ℝ) • landingData (-(g₀ • ez)) ah (dW ω δ sS (-ex)) tf)‖ := by
  have hρ₂ : 0 < ρ₂ := hρ₁.trans h12
  have hm0 : mdry ≤ m₀ := by nlinarith [mul_pos (mul_pos hα hρ₂) (hsS.trans hsStf)]
  have hreg : δ + ω * sS ≤ π / 2 := by linarith
  obtain ⟨ah, hah, hmax, -, -⟩ := exists_mass_witness (ω := ω) (δ := δ) hρ₁ h12 hα hmdry hburn
    hsS.le hsStf.le hω.le hδ.le hreg
  have hAcc : ∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, ρ₁ / m₀ ≤ a s ∧ a s ≤ ρ₂ / mdry := by
    intro a ha
    obtain ⟨haI, hlow⟩ := accMass_lower hρ₁ h12 hα hmdry hburn a ha
    obtain ⟨-, T, -, hTb, hm, haT⟩ := ha
    refine ⟨haI, fun s hs => ⟨hlow s hs, ?_⟩⟩
    have hmpos : 0 < massOf α m₀ T s := hmdry.trans_le (hm s hs)
    rw [haT s hs]
    calc T s / massOf α m₀ T s ≤ ρ₂ / massOf α m₀ T s :=
          div_le_div_of_nonneg_right (hTb s hs).2 hmpos.le
      _ ≤ ρ₂ / mdry := div_le_div_of_nonneg_left hρ₂.le hmdry (hm s hs)
  have h : ρ₁ / m₀ ≤ ρ₂ / mdry :=
    div_le_div₀ hρ₂.le h12.le hmdry hm0
  have hm0pos : 0 < m₀ := hmdry.trans_le hm0
  refine ⟨ah, hah, fun θ hθ => ?_⟩
  rw [div_le_iff₀ (by linarith), mul_comm]
  exact (lambda_dist_ge_of_max hsS hsStf hω hδ hδ4 hωs (div_pos hρ₁ hm0pos) h hAcc hah hmax hη₀ hη₀γ
    hθ).trans (norm_lambda_le hsS.le _ _)

end LcvxObstruction
