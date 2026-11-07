import LcvxObstruction.SixDOF
import LcvxObstruction.Abstract

/-!
# Theorem B* with upright landing (`b(tf) = e_z`), variant T'

Same as `DiveBrake.lean`, but the admissible attitude must also end upright, `b(tf) = e_z`
(for 6DOF: `A tf e_z = e_z`). The witnesses tilt at the maximal rate for `s*`, then return along
the same meridian on `[s*, 2s*]` and stay upright, so they need `2 s* ≤ tf`. The thrust stays
vertical during the whole brake, and the gimbal angle `ω·φ(s) ≤ ω s* ≤ δ`. The trajectory and the
midpoint argument are unchanged.
-/

open MeasureTheory Set InnerProductGeometry Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- State-constrained landing set with **upright terminal attitude** `b(tf) = e_z`. -/
def constrainedLandingSetUp (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) (X : Set (E3 × E3)) :
    Set (E3 × E3) :=
  {θ | ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b ∧ b tf = ez ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position g θ.1 θ.2 a d t, velocity g θ.2 a d t) ∈ X}

/-- 6DOF version: attitude ends with the body axis upright. -/
def constrainedLandingSet6Up (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (Acc : Set (ℝ → ℝ))
    (tf ω δ : ℝ) (g : E3) (X : Set (E3 × E3)) : Set (E3 × E3) :=
  {θ | ∃ a d A, a ∈ Acc ∧ Attitude6Admissible Att tf ω δ d A ∧ A tf ez = ez ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position g θ.1 θ.2 a d t, velocity g θ.2 a d t) ∈ X}

theorem constrainedLandingSetUp_subset {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {g : E3}
    {X : Set (E3 × E3)} : constrainedLandingSetUp Acc tf ω δ g X ⊆ landingSet Acc tf ω δ g :=
  fun _ ⟨a, d, b, ha, hatt, _, hr, hv, _⟩ => ⟨a, d, b, ha, hatt, hr, hv⟩

theorem constrainedLandingSet6Up_subset {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {Acc : Set (ℝ → ℝ)}
    {tf ω δ : ℝ} {g : E3} {X : Set (E3 × E3)} :
    constrainedLandingSet6Up Att Acc tf ω δ g X ⊆ landingSet Acc tf ω δ g :=
  fun _ ⟨a, d, A, ha, hA, _, hr, hv, _⟩ => ⟨a, d, _, ha, hA.toM1, hr, hv⟩

/-- Tilt profile of the upright witness: up to `s*`, back down by `2 s*`, then zero. -/
noncomputable def phiUp (sS : ℝ) (s : ℝ) : ℝ := max 0 (min s (2 * sS - s))

theorem phiUp_lipschitz (sS s s' : ℝ) : |phiUp sS s - phiUp sS s'| ≤ |s - s'| := by
  unfold phiUp
  refine (abs_max_sub_max_le_max _ _ _ _).trans ?_
  rw [sub_self, abs_zero]
  refine max_le (abs_nonneg _) ((abs_min_sub_min_le_max _ _ _ _).trans ?_)
  rw [show 2 * sS - s - (2 * sS - s') = -(s - s') by ring, abs_neg, max_self]

theorem phiUp_nonneg (sS s : ℝ) : 0 ≤ phiUp sS s := le_max_left _ _

theorem phiUp_le (sS s : ℝ) : phiUp sS s ≤ sS ∨ phiUp sS s = 0 := by
  unfold phiUp
  rcases le_total (min s (2 * sS - s)) 0 with h | h
  · right; exact max_eq_left h
  · left; rw [max_eq_right h]
    rcases le_total s sS with h' | h'
    · exact (min_le_left _ _).trans h'
    · exact (min_le_right _ _).trans (by linarith)

theorem phiUp_le' {sS : ℝ} (hsS : 0 ≤ sS) (s : ℝ) : phiUp sS s ≤ sS := by
  rcases phiUp_le sS s with h | h
  · exact h
  · rw [h]; exact hsS

theorem phiUp_of_le {sS s : ℝ} (hs0 : 0 ≤ s) (hs : s ≤ sS) : phiUp sS s = s := by
  unfold phiUp
  rw [min_eq_left (by linarith), max_eq_right hs0]

theorem phiUp_of_ge {sS s : ℝ} (hs : 2 * sS ≤ s) : phiUp sS s = 0 := by
  unfold phiUp
  exact max_eq_left (le_trans (min_le_right _ _) (by linarith))

/-- Upright witness body axis. -/
noncomputable def bWU (ω sS : ℝ) (u : E3) (s : ℝ) : E3 := arcB ω u (phiUp sS s)

theorem witness_admissible_upright {tf ω δ sS : ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (hsS : 0 < sS) (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hδπ : δ ≤ π)
    (hωs : ω * sS ≤ δ) :
    AttitudeAdmissible tf ω δ (dW ω δ sS u) (bWU ω sS u) where
  b_init := by simp [bWU, arcB, phiUp_of_le le_rfl hsS.le]
  b_unit s _ := norm_polar hu norm_ez huz _
  b_cont := by unfold bWU arcB phiUp; fun_prop
  b_rate s hs s' hs' := by
    have hmS : |phiUp sS s - phiUp sS s'| ≤ sS := by
      rw [abs_sub_le_iff]
      constructor <;> linarith [phiUp_le' hsS.le s, phiUp_le' hsS.le s', phiUp_nonneg sS s,
        phiUp_nonneg sS s']
    calc angle (bWU ω sS u s) (bWU ω sS u s') ≤ ω * |phiUp sS s - phiUp sS s'| := by
          apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _)
            (norm_polar hu norm_ez huz _) (mul_nonneg hω (abs_nonneg _))
            (by nlinarith [mul_le_mul_of_nonneg_left hmS hω])
          rw [inner_polar hu norm_ez huz, cos_mul_abs_sub hω]
      _ ≤ ω * |s - s'| := mul_le_mul_of_nonneg_left (phiUp_lipschitz sS s s') hω
  d_meas := (measurable_dW ω δ sS u).aestronglyMeasurable
  d_unit s _ := norm_dW hu huz s
  gimbal s hs := by
    by_cases h : s ≤ sS
    · simp only [dW, bWU, h, ↓reduceIte, phiUp_of_le hs.1 h]
      apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _) (norm_polar hu norm_ez huz _)
        hδ hδπ
      rw [inner_polar hu norm_ez huz]
      ring_nf; exact le_rfl
    · simp only [dW, bWU, h, ↓reduceIte]
      apply angle_le_of_cos_le_inner norm_ez (norm_polar hu norm_ez huz _) hδ hδπ
      rw [← arcB, inner_ez_arcB huz]
      exact Real.cos_le_cos_of_nonneg_of_le_pi (mul_nonneg hω (phiUp_nonneg _ _)) hδπ
        ((mul_le_mul_of_nonneg_left (phiUp_le' hsS.le s) hω).trans hωs)

/-- **Theorem B\*, upright landing (variant T').** -/
theorem not_convex_constrainedLandingSetUp {Acc : Set (ℝ → ℝ)}
    {tf ω δ sS amin amax g₀ tanγ : ℝ}
    (hsS : 0 < sS) (h2sS : 2 * sS ≤ tf) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ ≤ amax)
    (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (haW : aW sS amin amax ∈ Acc) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (constrainedLandingSetUp Acc tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have hsStf : sS < tf := by linarith
  have mem : ∀ v : E3, ‖v‖ = 1 → ⟪v, ez⟫ = 0 →
      landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS v) tf ∈
        constrainedLandingSetUp Acc tf ω δ (-(g₀ • ez)) X :=
    fun v hv hvz => ⟨_, _, _, haW, witness_admissible_upright hv hvz hsS hω.le hδ hδπ hωs,
      by simp [bWU, arcB, phiUp_of_ge h2sS],
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witness_mem_glideSlope hv hvz hsS hsStf hω.le hδ hreg hamin h hg htan hS ht)⟩
  exact not_convex_of_midpoint constrainedLandingSetUp_subset (mem ex norm_ex inner_ex_ez)
    (mem (-ex) (by simp) (by simp))
    (witness_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg hamin h hAcc)

/-- **Theorem B\*, upright landing, 6DOF.** -/
theorem not_convex_constrainedLandingSet6Up {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))}
    {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ tanγ : ℝ}
    (hsS : 0 < sS) (h2sS : 2 * sS ≤ tf) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ ≤ amax)
    (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (haW : aW sS amin amax ∈ Acc) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (hAtt : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) → (fun s => rotY (σ * (ω * phiUp sS s))) ∈ Att) :
    ¬ Convex ℝ (constrainedLandingSet6Up Att Acc tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have hsStf : sS < tf := by linarith
  have mem : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (σ • ex)) tf ∈
        constrainedLandingSet6Up Att Acc tf ω δ (-(g₀ • ez)) X := by
    intro σ hσ
    have hu : ‖σ • ex‖ = 1 := by rcases hσ with rfl | rfl <;> simp
    have huz : ⟪σ • ex, ez⟫ = 0 := by rw [real_inner_smul_left, inner_ex_ez, mul_zero]
    have hd : AttitudeAdmissible tf ω δ (dW ω δ sS (σ • ex))
        (fun s => rotY (σ * (ω * phiUp sS s)) ez) := by
      have := witness_admissible_upright (tf := tf) hu huz hsS hω.le hδ hδπ hωs
      convert this using 2 with s
      rw [rotY_ez_pm σ _ hσ]; rfl
    refine ⟨_, _, _, haW, lift_admissible (φ := phiUp sS) σ hσ (by unfold phiUp; fun_prop)
      (phiUp_of_le le_rfl hsS.le) (fun s _ s' _ => phiUp_lipschitz sS s s')
      (fun s hs s' hs' => ?_) hω.le (hAtt σ hσ) hd, ?_,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witness_mem_glideSlope hu huz hsS hsStf hω.le hδ hreg hamin h hg htan
        hS ht)⟩
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
    (witness_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg hamin h hAcc)

/-! ### Headline: upright landing, every horizon -/

open UniformConvexRelaxation in
/-- **Main theorem, state-constrained, upright landing (5DOF).** Same hypotheses as
`no_lossless_relaxation_constrained_5dof`; additionally the attitude must end upright. -/
theorem no_lossless_relaxation_constrained_upright_5dof {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ < amax) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSetUp (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ
      (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, -, hωs, hreg, hS, h2⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSetUp hsS h2 hω hωs hreg hamin h hg.le htan hS
      (fun _ ha => ha) (aW_mem_accBox h) hX) R

open UniformConvexRelaxation in
/-- **Main theorem, state-constrained, upright landing, 6DOF** (proper rotations, any roll,
attitude-rate limit `ω`). -/
theorem no_lossless_relaxation_constrained_upright_6dof {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ < amax) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet6Up properAttitudes
      (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, -, hωs, hreg, hS, h2⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet6Up hsS h2 hω hωs hreg hamin h hg.le htan hS
      (fun _ ha => ha) (aW_mem_accBox h) hX
      (fun σ _ => rotY_path_mem_proper (fun s => σ * (ω * phiUp sS s)))) R

open UniformConvexRelaxation in
/-- **Main theorem, state-constrained, 6DOF** (terminal attitude free). -/
theorem no_lossless_relaxation_constrained_6dof {Y : Type*} [AddCommGroup Y]
    [Module ℝ Y] {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 < δ)
    (hδ2 : δ < π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ < amax) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet6 properAttitudes
      (AccBox tf (fun _ => amin) (fun _ => amax)) tf ω δ (-(g₀ • ez)) X) := by
  obtain ⟨sS, hsS, hsStf, hωs, hreg, hS, -⟩ :=
    exists_switchTime (amin := amin) (tanγ := tanγ) htf hω hδ hδ2 hg
  exact not_isLossless_of_not_convex
    (not_convex_constrainedLandingSet6 hsS hsStf hω hωs hreg hamin h hg.le htan hS
      (fun _ ha => ha) (aW_mem_accBox h) hX
      (fun σ _ => rotY_path_mem_proper (fun s => σ * (ω * min s sS)))) R

end LcvxObstruction
