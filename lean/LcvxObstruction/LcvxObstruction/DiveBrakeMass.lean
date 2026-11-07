import LcvxObstruction.MassModel

/-!
# Theorem B* with mass depletion (`α > 0`): the face functional with history-dependent bounds

`DiveBrake.lean` proves Theorem B* for acceleration classes with *constant* bounds
`a_min ≤ a ≤ a_max` (constant mass). With mass depletion the min-then-max throttle no longer
attains the pointwise bound `h*` (a throttle history that is minimal on the dive is not the one
whose brake acceleration is maximal), so the core step is restated with the competitor's own
acceleration:

* `PhiFace tf ω δ s* a = ∫₀^tf a(s) φ(s)`, `φ(s) = min(s-s*,0) cos(δ+ωs) + max(s-s*,0)`: the
  maximum of `⟪W(c), e_z⟫` over attitudes for a fixed acceleration profile `a` (math/02 (10.1)).
* `PhiMax_not_mem_WSet` (**core, any acceleration class**): if every `a ∈ Acc` is integrable with
  `a ≥ a_min > 0` and `PhiFace a ≤ V` for all `a ∈ Acc`, then `V e_z` is not a weighted impulse.
  (Equality forces `d_z = cos(δ+ωs)` on the dive and `d = e_z` on the brake; rigidity as in B*.)
* `witnessG_mem_glideSlope`, `not_convex_constrainedLandingSet_of_max`: Theorem B* for any class
  `Acc` that contains a maximiser `â` of `PhiFace` whose dive acceleration is in `[0, A]` and whose
  brake acceleration is `≥ B > g₀`, under `(B + 2 tanγ A) s*² ≤ (B - g₀)(tf - s*)²`.
* Mass model (`AccMass`, explicit `ṁ = -αT`): see the second part of the file.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- The pointwise attitude-maximised weight of the dive-then-brake face. -/
noncomputable def phiW (ω δ sS : ℝ) (s : ℝ) : ℝ :=
  min (s - sS) 0 * Real.cos (δ + ω * s) + max (s - sS) 0

theorem continuous_phiW (ω δ sS : ℝ) : Continuous (phiW ω δ sS) := by
  unfold phiW; fun_prop

/-- The face functional of an acceleration profile: `∫₀^tf a φ`. -/
noncomputable def PhiFace (tf ω δ sS : ℝ) (a : ℝ → ℝ) : ℝ :=
  ∫ s in Icc 0 tf, a s * phiW ω δ sS s

/-- **Core of Theorem B\* for an arbitrary acceleration class.** If `V` bounds the face functional
of every admissible acceleration, `V e_z` is not the weighted impulse of any admissible control. -/
theorem PhiMax_not_mem_WSet {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin V : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2)
    (hamin : 0 < amin)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s)
    (hmax : ∀ a ∈ Acc, PhiFace tf ω δ sS a ≤ V) :
    V • ez ∉ WSet Acc tf ω δ sS := by
  rintro ⟨a, d, b, ha, hatt, hW⟩
  obtain ⟨haI, hab⟩ := hAcc a ha
  set μ := volume.restrict (Icc (0 : ℝ) tf) with hμ
  have hI0 : Integrable (fun s => a s • d s) μ :=
    integrableOn_smul_of_unit haI hatt.d_meas hatt.d_unit
  have hI : Integrable (fun s => (s - sS) • (a s • d s)) μ :=
    integrableOn_cont_smul hI0 (c := fun s => s - sS) (by fun_prop)
  have hθ_le : ∀ s ∈ Icc 0 tf, s ≤ sS → δ + ω * s ≤ π / 2 := fun s _ hs => by nlinarith
  have hcos_nn : ∀ s ∈ Icc 0 tf, s ≤ sS → 0 ≤ Real.cos (δ + ω * s) := fun s hs h =>
    Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [hs.1, Real.pi_pos], hθ_le s hs h⟩
  have hdz : ∀ s ∈ Icc 0 tf, s ≤ sS → Real.cos (δ + ω * s) ≤ ⟪d s, ez⟫ := fun s hs h =>
    hatt.inner_d_ez hω.le hδ hs (by linarith [hθ_le s hs h, Real.pi_pos])
  have hdz1 : ∀ s ∈ Icc 0 tf, ⟪d s, ez⟫ ≤ 1 := fun s hs =>
    inner_le_one_of_unit (hatt.d_unit s hs) norm_ez
  have hapos : ∀ s ∈ Icc 0 tf, 0 < a s := fun s hs => lt_of_lt_of_le hamin (hab s hs)
  -- vertical component
  set f : ℝ → ℝ := fun s => ⟪ez, (s - sS) • (a s • d s)⟫ with hf
  have hf_eq : ∀ s, f s = (s - sS) * (a s * ⟪d s, ez⟫) := fun s => by
    simp only [hf, real_inner_smul_right]; rw [real_inner_comm (d s) ez]
  have hfI : Integrable f μ := hI.const_inner ez
  set gF : ℝ → ℝ := fun s => a s * phiW ω δ sS s with hgF
  have hgI : Integrable gF μ :=
    haI.mul_continuousOn (continuous_phiW ω δ sS).continuousOn isCompact_Icc
  have hint_f : ∫ s, f s ∂μ = V := by
    rw [hf, integral_inner hI, ← hW, real_inner_smul_right, real_inner_self_eq_norm_sq, norm_ez]
    simp
  have hle : f ≤ᵐ[μ] gF := by
    refine ae_restrict_of_forall_mem measurableSet_Icc fun s hs => ?_
    rw [hf_eq]
    have ha0 := (hapos s hs).le
    simp only [hgF, phiW]
    rcases le_or_gt s sS with h | h
    · rw [min_eq_left (by linarith), max_eq_right (by linarith)]
      have h3 := hdz s hs h
      have hw : s - sS ≤ 0 := by linarith
      have e1 : 0 ≤ a s * (⟪d s, ez⟫ - Real.cos (δ + ω * s)) :=
        mul_nonneg ha0 (by linarith)
      nlinarith [mul_nonpos_of_nonpos_of_nonneg hw e1]
    · rw [min_eq_right (by linarith), max_eq_left (by linarith)]
      have h3 := hdz1 s hs
      have hw : 0 ≤ s - sS := by linarith
      have e1 : 0 ≤ a s * (1 - ⟪d s, ez⟫) := mul_nonneg ha0 (by linarith)
      nlinarith [mul_nonneg hw e1]
  have hint_eq : ∫ s, f s ∂μ = ∫ s, gF s ∂μ := by
    apply le_antisymm (integral_mono_ae hfI hgI hle)
    rw [hint_f]; exact hmax a ha
  have hae : f =ᵐ[μ] gF := (integral_eq_iff_of_ae_le hfI hgI hle).1 hint_eq
  -- a.e. good times
  have hne : ∀ c : ℝ, ∀ᵐ s ∂μ, s ≠ c := fun c => by
    have : ∀ᵐ s ∂(volume : Measure ℝ), s ∈ ({c}ᶜ : Set ℝ) :=
      compl_mem_ae_iff.2 (measure_singleton c)
    filter_upwards [ae_restrict_of_ae this] with s hs using hs
  have hgood : ∀ᵐ s ∂μ, s ∈ Icc 0 tf ∧ 0 < s ∧ s ≠ sS ∧
      (s < sS → ⟪d s, ez⟫ = Real.cos (δ + ω * s)) ∧ (sS < s → d s = ez) := by
    filter_upwards [hae, ae_restrict_mem measurableSet_Icc, hne 0, hne sS] with s h1 h2 h3 h4
    refine ⟨h2, lt_of_le_of_ne h2.1 (Ne.symm h3), h4, ?_, ?_⟩
    · intro hlt
      have h1' := h1
      rw [hf_eq] at h1'
      simp only [hgF, phiW, min_eq_left (by linarith : s - sS ≤ 0),
        max_eq_right (by linarith : s - sS ≤ 0), add_zero] at h1'
      have h8 := hapos s h2
      have hw : s - sS ≠ 0 := by linarith
      have : (s - sS) * (a s * (⟪d s, ez⟫ - Real.cos (δ + ω * s))) = 0 := by linarith
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h hw
      rcases mul_eq_zero.1 h with h | h
      · exact absurd h h8.ne'
      · linarith
    · intro hlt
      have h1' := h1
      rw [hf_eq] at h1'
      simp only [hgF, phiW, min_eq_right (by linarith : 0 ≤ s - sS),
        max_eq_left (by linarith : 0 ≤ s - sS), zero_mul, zero_add] at h1'
      have h8 := hapos s h2
      have hw : s - sS ≠ 0 := by linarith
      have : (s - sS) * (a s * (1 - ⟪d s, ez⟫)) = 0 := by linarith
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h hw
      rcases mul_eq_zero.1 h with h | h
      · exact absurd h h8.ne'
      · exact eq_of_inner_eq_one (hatt.d_unit s h2) norm_ez (by linarith)
  -- positivity of sines on the dive
  have hsin_b : ∀ s, 0 < s → s ≤ sS → 0 < Real.sin (ω * s) := fun s hs hs' =>
    Real.sin_pos_of_pos_of_lt_pi (mul_pos hω hs) (by nlinarith [Real.pi_pos])
  have hsin_d : ∀ s, 0 < s → s ≤ sS → 0 < Real.sin (δ + ω * s) := fun s hs hs' =>
    Real.sin_pos_of_pos_of_lt_pi (by nlinarith [mul_pos hω hs]) (by nlinarith [Real.pi_pos])
  have key : ∀ s, s ∈ Icc 0 tf → 0 < s → s < sS → ⟪d s, ez⟫ = Real.cos (δ + ω * s) →
      ⟪b s, ez⟫ = Real.cos (ω * s) ∧
        lateral ez (d s) (δ + ω * s) = lateral ez (b s) (ω * s) := by
    intro s hs hs0 hss hds
    exact inner_triangle_eq_lateral (hatt.d_unit s hs) (hatt.b_unit s hs) norm_ez hδ
      (mul_pos hω hs0) (by linarith [hθ_le s hs hss.le, Real.pi_pos])
      (cos_le_inner_of_angle_le (hatt.d_unit s hs) (hatt.b_unit s hs) (hatt.gimbal s hs)
        (by linarith [hθ_le s hs hss.le, Real.pi_pos, mul_nonneg hω.le hs.1]))
      (hatt.inner_b_ez hs (by linarith [hθ_le s hs hss.le, Real.pi_pos])) hds
  -- a good time on the dive
  have hgood' : ∀ᵐ s ∂(volume.restrict (Ioo (0 : ℝ) sS)), s ∈ Ioo 0 sS ∧ (s ∈ Icc 0 tf ∧
      0 < s ∧ s ≠ sS ∧ (s < sS → ⟪d s, ez⟫ = Real.cos (δ + ω * s)) ∧ (sS < s → d s = ez)) := by
    filter_upwards [ae_restrict_mem measurableSet_Ioo,
      ae_restrict_of_ae_restrict_of_subset (Ioo_subset_Icc_self.trans
        (Icc_subset_Icc_right hsStf.le)) hgood] with s h1 h2 using ⟨h1, h2⟩
  have hμ0 : volume.restrict (Ioo (0 : ℝ) sS) ≠ 0 := by
    rw [Ne, Measure.restrict_eq_zero, Real.volume_Ioo]; simpa using hsS
  have : (ae (volume.restrict (Ioo (0 : ℝ) sS))).NeBot := ae_neBot.2 hμ0
  obtain ⟨s₀, hs₀I, hs₀, -, -, hds₀, -⟩ := hgood'.exists
  obtain ⟨hbs₀, -⟩ := key s₀ hs₀ hs₀I.1 hs₀I.2 (hds₀ hs₀I.2)
  set u := lateral ez (b s₀) (ω * s₀) with hu_def
  have huz : ⟪u, ez⟫ = 0 := inner_lateral_pole norm_ez hbs₀
  have huu : ⟪u, u⟫ = 1 :=
    inner_lateral_self (hatt.b_unit s₀ hs₀) norm_ez hbs₀ (hsin_b s₀ hs₀I.1 hs₀I.2.le).ne'
  have hlat : ∀ s, s ∈ Icc 0 tf → 0 < s → s < sS → ⟪d s, ez⟫ = Real.cos (δ + ω * s) →
      ⟪u, d s⟫ = Real.sin (δ + ω * s) := by
    intro s hs hs0 hss hds
    obtain ⟨hbs, hld⟩ := key s hs hs0 hss hds
    have hbb : lateral ez (b s) (ω * s) = u := by
      apply lateral_eq_of_inner_ge (hatt.b_unit s hs) (hatt.b_unit s₀ hs₀) norm_ez hbs hbs₀
        (hsin_b s hs0 hss.le) (hsin_b s₀ hs₀I.1 hs₀I.2.le)
      rw [← cos_mul_abs_sub hω.le]
      have habs : |s - s₀| ≤ sS := by
        rw [abs_sub_le_iff]; constructor <;> linarith [hs₀I.1, hs₀I.2]
      exact cos_le_inner_of_angle_le (hatt.b_unit s hs) (hatt.b_unit s₀ hs₀)
        (hatt.b_rate s hs s₀ hs₀) (by nlinarith [Real.pi_pos, abs_nonneg (s - s₀)])
    have hd := eq_cos_smul_add_sin_smul_lateral ez (d s) (hsin_d s hs0 hss.le).ne'
    rw [hld, hbb] at hd
    rw [hd, inner_add_right, real_inner_smul_right, real_inner_smul_right, huz, huu]
    ring
  -- lateral integral: zero, but strictly negative
  set q : ℝ → ℝ := fun s => min (s - sS) 0 * amin * Real.sin (δ + ω * s) with hq
  have hqc : Continuous q := by simp only [hq]; fun_prop
  have hzero : ∫ s, ⟪u, (s - sS) • (a s • d s)⟫ ∂μ = 0 := by
    rw [integral_inner hI, ← hW, real_inner_smul_right, huz, mul_zero]
  have hup : (fun s => ⟪u, (s - sS) • (a s • d s)⟫) ≤ᵐ[μ] q := by
    filter_upwards [hgood] with s ⟨hs, hs0, hss, hdive, hbrake⟩
    simp only [hq, real_inner_smul_right]
    rcases lt_or_gt_of_ne hss with h | h
    · rw [hlat s hs hs0 h (hdive h), min_eq_left (by linarith)]
      have h5 := hab s hs
      have := (hsin_d s hs0 h.le).le
      nlinarith [mul_nonneg (sub_nonneg.2 h5) this]
    · rw [hbrake h, huz, min_eq_right (by linarith)]; simp
  have hneg : ∫ s, q s ∂μ < 0 := by
    have hpos : 0 < ∫ s in Icc 0 sS, -q s := by
      refine integral_Icc_pos hsS hqc.neg.continuousOn fun s hs => ?_
      simp only [hq]
      rw [min_eq_left (by linarith [hs.2])]
      have := hsin_d s hs.1 hs.2.le
      nlinarith [mul_pos (by linarith [hs.2] : (0:ℝ) < sS - s) (mul_pos hamin this)]
    have hnn : ∀ s ∈ Icc 0 tf, 0 ≤ -q s := fun s hs => by
      simp only [hq]
      rcases le_or_gt s sS with h | h
      · rw [min_eq_left (by linarith)]
        have hsin : 0 ≤ Real.sin (δ + ω * s) :=
          Real.sin_nonneg_of_nonneg_of_le_pi (by nlinarith [hs.1])
            (by linarith [hθ_le s hs h, Real.pi_pos])
        nlinarith [mul_nonneg (by linarith : (0:ℝ) ≤ sS - s) (mul_nonneg hamin.le hsin)]
      · rw [min_eq_right (by linarith)]; simp
    have hmono : ∫ s in Icc 0 sS, -q s ≤ ∫ s in Icc 0 tf, -q s :=
      setIntegral_mono_set hqc.neg.continuousOn.integrableOn_Icc
        (ae_restrict_of_forall_mem measurableSet_Icc hnn)
        (Icc_subset_Icc_right hsStf.le).eventuallyLE
    simp only [integral_neg] at hmono hpos
    rw [hμ]
    linarith
  have hmono := integral_mono_ae (hI.const_inner u) hqc.continuousOn.integrableOn_Icc hup
  rw [hzero] at hmono
  linarith

/-! ### Witnesses with an arbitrary throttle profile -/

theorem integrableOn_witnessG {tf ω δ sS : ℝ} {ah : ℝ → ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (haI : IntegrableOn ah (Icc 0 tf)) :
    IntegrableOn (fun s => ah s • dW ω δ sS u s) (Icc 0 tf) :=
  integrableOn_smul_of_unit haI (measurable_dW ω δ sS u).aestronglyMeasurable
    fun s _ => norm_dW hu huz s

/-- The midpoint of the weighted impulses of the two mirror witnesses (throttle `â`) is
`PhiFace â • e_z`. -/
theorem witnessG_W_midpoint {tf ω δ sS : ℝ} {ah : ℝ → ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (haI : IntegrableOn ah (Icc 0 tf)) :
    (1 / 2 : ℝ) • (∫ s in Icc 0 tf, (s - sS) • (ah s • dW ω δ sS u s)) +
      (1 / 2 : ℝ) • (∫ s in Icc 0 tf, (s - sS) • (ah s • dW ω δ sS (-u) s)) =
      PhiFace tf ω δ sS ah • ez := by
  have h1 : Integrable (fun s => (1 / 2 : ℝ) • ((s - sS) • (ah s • dW ω δ sS u s)))
      (volume.restrict (Icc 0 tf)) :=
    (integrableOn_cont_smul (integrableOn_witnessG hu huz haI) (c := fun s => s - sS)
      (by fun_prop)).smul (1 / 2 : ℝ)
  have h2 : Integrable
      (fun s => (1 / 2 : ℝ) • ((s - sS) • (ah s • dW ω δ sS (-u) s)))
      (volume.restrict (Icc 0 tf)) :=
    (integrableOn_cont_smul (integrableOn_witnessG (by simpa using hu) (by simpa using huz) haI)
      (c := fun s => s - sS) (by fun_prop)).smul (1 / 2 : ℝ)
  rw [← integral_smul, ← integral_smul, ← integral_add h1 h2, PhiFace, ← integral_smul_const]
  congr 1
  funext s
  by_cases hs : s ≤ sS
  · simp only [dW, phiW, hs, ↓reduceIte, min_eq_left (sub_nonpos.2 hs),
      max_eq_right (sub_nonpos.2 hs), arcD]
    module
  · have hs' : 0 ≤ s - sS := by linarith [not_le.1 hs]
    simp only [dW, phiW, hs, ↓reduceIte, min_eq_right hs', max_eq_left hs']
    module

/-- **The witness trajectory with throttle `â` satisfies the glide-slope constraint.**
Assumptions: `â` integrable, `0 ≤ â ≤ A` on the dive, `â ≥ B ≥ g₀ ≥ 0` on the brake, and
`(B + 2 tanγ A) s*² ≤ (B - g₀)(tf - s*)²`. -/
theorem witnessG_mem_glideSlope {tf ω δ sS g₀ tanγ A B : ℝ} {ah : ℝ → ℝ} {u : E3}
    (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0) (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 ≤ ω)
    (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2) (haI : IntegrableOn ah (Icc 0 tf))
    (hdive : ∀ s ∈ Icc 0 tf, s ≤ sS → 0 ≤ ah s ∧ ah s ≤ A)
    (hbrake : ∀ s ∈ Icc 0 tf, sS < s → B ≤ ah s) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ B)
    (htan : 0 ≤ tanγ)
    (hS : (B + 2 * tanγ * A) * sS ^ 2 ≤ (B - g₀) * (tf - sS) ^ 2)
    {t : ℝ} (ht : t ∈ Icc 0 tf) :
    (position (-(g₀ • ez)) (landingData (-(g₀ • ez)) ah (dW ω δ sS u) tf).1
        (landingData (-(g₀ • ez)) ah (dW ω δ sS u) tf).2 ah (dW ω δ sS u) t,
      velocity (-(g₀ • ez)) (landingData (-(g₀ • ez)) ah (dW ω δ sS u) tf).2
        ah (dW ω δ sS u) t) ∈ glideSlopeSet tanγ := by
  set a := ah
  set d := dW ω δ sS u
  have hf := integrableOn_witnessG (tf := tf) (sS := sS) (ω := ω) (δ := δ) hu huz haI
  obtain ⟨hr, hv⟩ := landingData_lands (-(g₀ • ez)) a d tf
  simp only [glideSlopeSet, Set.mem_ofPred_eq]
  rw [position_eq_tail ht hf hr hv]
  have hA0 : 0 ≤ A := (hdive 0 ⟨le_rfl, hsStf.le.trans' hsS.le⟩ hsS.le).1.trans
    (hdive 0 ⟨le_rfl, hsStf.le.trans' hsS.le⟩ hsS.le).2
  set ψ : ℝ → E3 := fun s => (s - t) • (a s • d s) with hψ
  have hψI : IntegrableOn ψ (Icc 0 tf) :=
    integrableOn_cont_smul hf (c := fun s => s - t) (by fun_prop)
  have hψI' : IntegrableOn ψ (Ioc t tf) :=
    hψI.mono_set (Ioc_subset_Icc_self.trans (Icc_subset_Icc_left ht.1))
  set Z : ℝ → ℝ := fun s => ⟪ψ s, ez⟫ with hZ
  set L : ℝ → E3 := fun s => ψ s - Z s • ez with hL
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hZ_dive : ∀ s, s ≤ sS → Z s = (s - t) * (a s * Real.cos (δ + ω * s)) := fun s hs => by
    simp only [hZ, hψ, d, dW, hs, ↓reduceIte, arcD, real_inner_smul_left, inner_add_left, huz,
      hzz]; ring
  have hZ_brake : ∀ s, sS < s → Z s = (s - t) * a s := fun s hs => by
    simp only [hZ, hψ, d, dW, not_le.2 hs, ↓reduceIte, real_inner_smul_left, hzz]; ring
  have hL_dive : ∀ s, s ≤ sS → L s = ((s - t) * a s * Real.sin (δ + ω * s)) • u := fun s hs => by
    simp only [hL, hZ_dive s hs, hψ, d, dW, hs, ↓reduceIte, arcD]; module
  have hL_brake : ∀ s, sS < s → L s = 0 := fun s hs => by
    simp only [hL, hZ_brake s hs, hψ, d, dW, not_le.2 hs, ↓reduceIte]; module
  have hZI : IntegrableOn Z (Ioc t tf) := by
    have : IntegrableOn (fun s => ⟪ez, ψ s⟫) (Ioc t tf) := Integrable.const_inner ez hψI'
    exact this.congr_fun (fun s _ => real_inner_comm _ _) measurableSet_Ioc
  have hLI : IntegrableOn L (Ioc t tf) := hψI'.sub (hZI.smul_const ez)
  set R := ∫ s in Ioc t tf, ψ s with hR
  have hRz : ⟪R, ez⟫ = ∫ s in Ioc t tf, Z s := by
    rw [hR, real_inner_comm, ← integral_inner hψI']
    exact setIntegral_congr_fun measurableSet_Ioc (fun s _ => real_inner_comm _ _)
  have hRh : R - ⟪R, ez⟫ • ez = ∫ s in Ioc t tf, L s := by
    rw [hRz, hR, hL, integral_sub hψI' (hZI.smul_const ez), integral_smul_const]
  set c := (tf - t) ^ 2 / 2 with hc
  have hrz : ⟪R + c • -(g₀ • ez), ez⟫ = (∫ s in Ioc t tf, Z s) - g₀ * c := by
    rw [inner_add_left, hRz, real_inner_smul_left, inner_neg_left, real_inner_smul_left, hzz]
    ring
  have hrh : R + c • -(g₀ • ez) - ⟪R + c • -(g₀ • ez), ez⟫ • ez = ∫ s in Ioc t tf, L s := by
    rw [← hRh, inner_add_left, real_inner_smul_left, inner_neg_left, real_inner_smul_left, hzz]
    module
  rw [hrh, hrz]
  have hmemI : ∀ s ∈ Ioc t tf, s ∈ Icc 0 tf := fun s hs => ⟨by linarith [hs.1, ht.1], hs.2⟩
  -- brake lower bound on any sub-interval `Ioc p tf` with `sS ≤ p`, `t ≤ p`
  have hZbr : ∀ p, sS ≤ p → t ≤ p → p ≤ tf →
      B * (((tf - t) ^ 2 - (p - t) ^ 2) / 2) ≤ ∫ s in Ioc p tf, Z s := by
    intro p hp htp hptf
    have hcI : IntegrableOn (fun s => (s - t) * B) (Ioc p tf) :=
      (Continuous.integrableOn_Icc (by fun_prop)).mono_set Ioc_subset_Icc_self
    have hZI' : IntegrableOn Z (Ioc p tf) := hZI.mono_set (Ioc_subset_Ioc_left htp)
    calc B * (((tf - t) ^ 2 - (p - t) ^ 2) / 2) = ∫ s in Ioc p tf, (s - t) * B := by
          rw [integral_mul_const, integral_Ioc_sub_self hptf]; ring
      _ ≤ ∫ s in Ioc p tf, Z s := by
          refine setIntegral_mono_on hcI hZI' measurableSet_Ioc fun s hs => ?_
          rw [hZ_brake s (by linarith [hs.1])]
          exact mul_le_mul_of_nonneg_left
            (hbrake s ⟨by linarith [hs.1, ht.1], hs.2⟩ (by linarith [hs.1]))
            (by linarith [hs.1])
  rcases le_or_gt sS t with hts | hts
  · -- brake phase only
    have hZge := hZbr t hts le_rfl ht.2
    have hLeq : ∫ s in Ioc t tf, L s = 0 := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hL_brake s (by linarith [hs.1]))]
      simp
    rw [hLeq, norm_zero, mul_zero]
    have : 0 ≤ (B - g₀) * c := mul_nonneg (by linarith) (by positivity)
    simp only [sub_self, ne_eq, OfNat.ofNat_ne_zero, not_false_eq_true, zero_pow, sub_zero] at hZge
    rw [← hc] at hZge
    constructor <;> nlinarith
  · -- dive then brake
    have hsplit : ∀ {F : ℝ → ℝ}, IntegrableOn F (Ioc t tf) →
        ∫ s in Ioc t tf, F s = (∫ s in Ioc t sS, F s) + ∫ s in Ioc sS tf, F s := by
      intro F hF
      rw [← setIntegral_union (Ioc_disjoint_Ioc' t sS tf) measurableSet_Ioc
        (hF.mono_set (Ioc_subset_Ioc_right hsStf.le)) (hF.mono_set (Ioc_subset_Ioc_left hts.le)),
        Ioc_union_Ioc_eq_Ioc hts.le hsStf.le]
    have hsplitV : ∫ s in Ioc t tf, L s = (∫ s in Ioc t sS, L s) + ∫ s in Ioc sS tf, L s := by
      rw [← setIntegral_union (Ioc_disjoint_Ioc' t sS tf) measurableSet_Ioc
        (hLI.mono_set (Ioc_subset_Ioc_right hsStf.le)) (hLI.mono_set (Ioc_subset_Ioc_left hts.le)),
        Ioc_union_Ioc_eq_Ioc hts.le hsStf.le]
    have hZ1 : 0 ≤ ∫ s in Ioc t sS, Z s := by
      refine setIntegral_nonneg measurableSet_Ioc fun s hs => ?_
      rw [hZ_dive s hs.2]
      have : 0 ≤ Real.cos (δ + ω * s) :=
        Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [ht.1, hs.1, Real.pi_pos], by nlinarith [hs.2]⟩
      have : 0 ≤ s - t := by linarith [hs.1]
      have : 0 ≤ a s := (hdive s ⟨by linarith [hs.1, ht.1], by linarith [hs.2]⟩ hs.2).1
      positivity
    have hZ2 := hZbr sS le_rfl hts.le hsStf.le
    have hL2 : ∫ s in Ioc sS tf, L s = 0 := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hL_brake s hs.1)]; simp
    have hL1 : ‖∫ s in Ioc t sS, L s‖ ≤ A * sS * sS := by
      have hb : ∀ s ∈ Ioc t sS, ‖L s‖ ≤ A * sS := fun s hs => by
        have hsI : s ∈ Icc 0 tf := ⟨by linarith [hs.1, ht.1], by linarith [hs.2]⟩
        obtain ⟨ha0, haA⟩ := hdive s hsI hs.2
        rw [hL_dive s hs.2, norm_smul, hu, mul_one, Real.norm_eq_abs, abs_mul, abs_mul,
          abs_of_nonneg (by linarith [hs.1] : (0:ℝ) ≤ s - t), abs_of_nonneg ha0]
        have h1 : |Real.sin (δ + ω * s)| ≤ 1 := Real.abs_sin_le_one _
        have h2 : s - t ≤ sS := by linarith [hs.2, ht.1]
        have h3 : 0 ≤ s - t := by linarith [hs.1]
        calc (s - t) * a s * |Real.sin (δ + ω * s)| ≤ sS * A * 1 := by gcongr
          _ = A * sS := by ring
      have := norm_setIntegral_le_of_norm_le_const (μ := volume) measure_Ioc_lt_top hb
      rw [Real.volume_real_Ioc_of_le hts.le] at this
      calc ‖∫ s in Ioc t sS, L s‖ ≤ A * sS * (sS - t) := this
        _ ≤ A * sS * sS := by
          apply mul_le_mul_of_nonneg_left (by linarith [ht.1]); positivity
    rw [hsplit hZI, hsplitV, hL2, add_zero]
    have hmono1 : (tf - sS) ^ 2 ≤ (tf - t) ^ 2 :=
      pow_le_pow_left₀ (by linarith) (by linarith) 2
    have hmono2 : (sS - t) ^ 2 ≤ sS ^ 2 := pow_le_pow_left₀ (by linarith) (by linarith [ht.1]) 2
    have hlat : tanγ * ‖∫ s in Ioc t sS, L s‖ ≤ tanγ * (A * sS * sS) :=
      mul_le_mul_of_nonneg_left hL1 htan
    have k1 : (B - g₀) * (tf - sS) ^ 2 ≤ (B - g₀) * (tf - t) ^ 2 :=
      mul_le_mul_of_nonneg_left hmono1 (by linarith)
    have hB0 : 0 ≤ B := le_trans hg0 hg
    have k2 : B * (sS - t) ^ 2 ≤ B * sS ^ 2 := mul_le_mul_of_nonneg_left hmono2 hB0
    have hgc : g₀ * c = g₀ * (tf - t) ^ 2 / 2 := by rw [hc]; ring
    have hkey : tanγ * (A * sS * sS) ≤
        (∫ s in Ioc t sS, Z s) + (∫ s in Ioc sS tf, Z s) - g₀ * c := by
      rw [hgc]
      have e : tanγ * (A * sS * sS) = (2 * tanγ * A) * sS ^ 2 / 2 := by ring
      rw [e]
      nlinarith
    have hnn : 0 ≤ tanγ * (A * sS * sS) := by positivity
    exact ⟨by linarith, by linarith⟩

/-- **Theorem B\* for any acceleration class with a face maximiser.** Assume the members of `Acc`
are integrable with `a ≥ a_min > 0`, and `â ∈ Acc` maximises `PhiFace` over `Acc`, with
`0 ≤ â ≤ A` on the dive and `â ≥ B ≥ g₀` on the brake. Under the switch-time conditions, the
state-constrained landing set is not convex, for every `X ⊇ glideSlopeSet tanγ`. -/
theorem not_convex_constrainedLandingSet_of_max {Acc : Set (ℝ → ℝ)}
    {tf ω δ sS amin g₀ tanγ A B : ℝ} {ah : ℝ → ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s)
    (hah : ah ∈ Acc) (hmax : ∀ a ∈ Acc, PhiFace tf ω δ sS a ≤ PhiFace tf ω δ sS ah)
    (hdive : ∀ s ∈ Icc 0 tf, s ≤ sS → 0 ≤ ah s ∧ ah s ≤ A)
    (hbrake : ∀ s ∈ Icc 0 tf, sS < s → B ≤ ah s) (hg0 : 0 ≤ g₀) (hg : g₀ ≤ B)
    (htan : 0 ≤ tanγ)
    (hS : (B + 2 * tanγ * A) * sS ^ 2 ≤ (B - g₀) * (tf - sS) ^ 2)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (constrainedLandingSet Acc tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have haI := (hAcc ah hah).1
  set g := -(g₀ • ez)
  have mem : ∀ v : E3, ‖v‖ = 1 → ⟪v, ez⟫ = 0 →
      landingData g ah (dW ω δ sS v) tf ∈ constrainedLandingSet Acc tf ω δ g X :=
    fun v hv hvz => ⟨_, _, _, hah, witness_admissible hv hvz hsS hω.le hδ hδπ hωs,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witnessG_mem_glideSlope hv hvz hsS hsStf hω.le hδ hreg haI hdive hbrake hg0 hg
        htan hS ht)⟩
  refine not_convex_of_midpoint constrainedLandingSet_subset (mem ex norm_ex inner_ex_ez)
    (mem (-ex) (by simp) (by simp)) ?_
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

end LcvxObstruction
