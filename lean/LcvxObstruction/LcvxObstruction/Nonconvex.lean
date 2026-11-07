import LcvxObstruction.Model

/-!
# Theorem B: the 5DOF (M1) reachable set is not convex

Regime: `0 < tf`, `0 < ω`, `0 ≤ δ`, `δ + ω tf ≤ π/2`; `a₁` continuous and positive on `[0,tf]`.
Acceleration class `Acc`: every member is integrable with `a ≥ a₁` on `[0,tf]`, and `a₁ ∈ Acc`
(minimum throttle is admissible).

Extreme arcs (for a horizontal unit `u`):
`b_u(s) = sin(ωs) u + cos(ωs) e_z`, `d_u(s) = sin(δ+ωs) u + cos(δ+ωs) e_z`, `a = a₁`.
`P_u = ∫ a₁ d_u`; the midpoint of `P_u` and `P_{-u}` is `M = (∫ a₁ cos(δ+ωs)) e_z`.
We show `M ∉ R`, hence `R` and the landing set `F_tf` are not convex.
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

theorem inner_polar {u z : V} (hu : ‖u‖ = 1) (hz : ‖z‖ = 1) (huz : ⟪u, z⟫ = 0) (θ θ' : ℝ) :
    ⟪Real.sin θ • u + Real.cos θ • z, Real.sin θ' • u + Real.cos θ' • z⟫ = Real.cos (θ - θ') := by
  have hzu : ⟪z, u⟫ = 0 := by rw [real_inner_comm]; exact huz
  have huu : ⟪u, u⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hu]; norm_num
  have hzz : ⟪z, z⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hz]; norm_num
  simp only [inner_add_left, inner_add_right, real_inner_smul_left, real_inner_smul_right, huz,
    hzu, huu, hzz]
  rw [Real.cos_sub]; ring

theorem norm_polar {u z : V} (hu : ‖u‖ = 1) (hz : ‖z‖ = 1) (huz : ⟪u, z⟫ = 0) (θ : ℝ) :
    ‖Real.sin θ • u + Real.cos θ • z‖ = 1 := by
  have h := inner_polar hu hz huz θ θ
  rw [sub_self, Real.cos_zero, real_inner_self_eq_norm_sq] at h
  have h0 := norm_nonneg (Real.sin θ • u + Real.cos θ • z)
  nlinarith

/-- Extreme body-axis arc: tilt away from vertical at the maximal rate `ω` towards `u`. -/
noncomputable def arcB (ω : ℝ) (u : E3) (s : ℝ) : E3 :=
  Real.sin (ω * s) • u + Real.cos (ω * s) • ez

/-- Extreme thrust direction: a further `δ` beyond the body axis, in the same vertical plane. -/
noncomputable def arcD (ω δ : ℝ) (u : E3) (s : ℝ) : E3 :=
  Real.sin (δ + ω * s) • u + Real.cos (δ + ω * s) • ez

theorem cos_mul_abs_sub {ω : ℝ} (hω : 0 ≤ ω) (s s' : ℝ) :
    Real.cos (ω * |s - s'|) = Real.cos (ω * s - ω * s') := by
  rw [← abs_of_nonneg hω, ← abs_mul, Real.cos_abs, abs_of_nonneg hω, mul_sub]

/-- **The extreme arcs are admissible** (in particular the M1 hypotheses are not vacuous). -/
theorem arc_admissible {tf ω δ : ℝ} {u : E3} (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0)
    (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hδπ : δ ≤ π) (hωtf : ω * tf ≤ π) :
    AttitudeAdmissible tf ω δ (arcD ω δ u) (arcB ω u) where
  b_init := by simp [arcB]
  b_unit s _ := norm_polar hu norm_ez huz _
  b_cont := by unfold arcB; fun_prop
  b_rate s hs s' hs' := by
    have habs : |s - s'| ≤ tf := by
      rw [abs_sub_le_iff]; constructor <;> linarith [hs.1, hs.2, hs'.1, hs'.2]
    apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _) (norm_polar hu norm_ez huz _)
      (mul_nonneg hω (abs_nonneg _)) ((mul_le_mul_of_nonneg_left habs hω).trans hωtf)
    rw [inner_polar hu norm_ez huz, cos_mul_abs_sub hω]
  d_meas := by
    apply Continuous.aestronglyMeasurable
    unfold arcD; fun_prop
  d_unit s _ := norm_polar hu norm_ez huz _
  gimbal s _ := by
    apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _) (norm_polar hu norm_ez huz _)
      hδ hδπ
    rw [inner_polar hu norm_ez huz]
    ring_nf; exact le_rfl

/-- The extreme endpoint `P_u = ∫₀^tf a₁ d_u`. -/
noncomputable def arcEndpoint (tf ω δ : ℝ) (a₁ : ℝ → ℝ) (u : E3) : E3 :=
  ∫ s in Icc 0 tf, a₁ s • arcD ω δ u s

/-- The midpoint `M = (∫₀^tf a₁(s) cos(δ+ωs) ds) e_z`. -/
noncomputable def midpointM (tf ω δ : ℝ) (a₁ : ℝ → ℝ) : E3 :=
  (∫ s in Icc 0 tf, a₁ s * Real.cos (δ + ω * s)) • ez

theorem integrableOn_arc {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (ha₁ : ContinuousOn a₁ (Icc 0 tf)) (u : E3) :
    IntegrableOn (fun s => a₁ s • arcD ω δ u s) (Icc 0 tf) := by
  apply ContinuousOn.integrableOn_Icc
  apply ha₁.smul
  apply Continuous.continuousOn
  unfold arcD; fun_prop

theorem midpoint_arcEndpoint {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (ha₁ : ContinuousOn a₁ (Icc 0 tf))
    (u : E3) :
    (1 / 2 : ℝ) • arcEndpoint tf ω δ a₁ u + (1 / 2 : ℝ) • arcEndpoint tf ω δ a₁ (-u) =
      midpointM tf ω δ a₁ := by
  unfold arcEndpoint midpointM
  have h1 : Integrable (fun s => (1 / 2 : ℝ) • (a₁ s • arcD ω δ u s))
      (volume.restrict (Icc 0 tf)) := (integrableOn_arc ha₁ u).smul (1 / 2 : ℝ)
  have h2 : Integrable (fun s => (1 / 2 : ℝ) • (a₁ s • arcD ω δ (-u) s))
      (volume.restrict (Icc 0 tf)) := (integrableOn_arc ha₁ (-u)).smul (1 / 2 : ℝ)
  rw [← integral_smul, ← integral_smul, ← integral_add h1 h2, ← integral_smul_const]
  congr 1
  funext s
  simp only [arcD]
  module

theorem integral_Icc_pos {tf : ℝ} (htf : 0 < tf) {f : ℝ → ℝ} (hf : ContinuousOn f (Icc 0 tf))
    (hpos : ∀ s ∈ Ioo 0 tf, 0 < f s) : 0 < ∫ s in Icc 0 tf, f s := by
  rw [integral_Icc_eq_integral_Ioc, ← intervalIntegral.integral_of_le htf.le]
  exact intervalIntegral.intervalIntegral_pos_of_pos_on (hf.intervalIntegrable_of_Icc htf.le)
    hpos htf

/-- **Key step of Theorem B: the midpoint is not reachable.** -/
theorem midpointM_not_mem_reachSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ}
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s) :
    midpointM tf ω δ a₁ ∉ reachSet Acc tf ω δ := by
  rintro ⟨a, d, b, ha, hatt, hM⟩
  obtain ⟨haI, hale⟩ := hAcc a ha
  set μ := volume.restrict (Icc (0 : ℝ) tf) with hμ
  set c := ∫ s in Icc 0 tf, a₁ s * Real.cos (δ + ω * s) with hc
  have hI : Integrable (fun s => a s • d s) μ :=
    integrableOn_smul_of_unit haI hatt.d_meas hatt.d_unit
  -- bounds on the polar angles
  have hθ_le : ∀ s ∈ Icc 0 tf, δ + ω * s ≤ π / 2 := fun s hs => by nlinarith [hs.2]
  have hcos_nn : ∀ s ∈ Icc 0 tf, 0 ≤ Real.cos (δ + ω * s) := fun s hs =>
    Real.cos_nonneg_of_mem_Icc ⟨by nlinarith [hs.1, Real.pi_pos], hθ_le s hs⟩
  -- vertical component
  set f : ℝ → ℝ := fun s => ⟪ez, a s • d s⟫ with hf
  set g : ℝ → ℝ := fun s => a₁ s * Real.cos (δ + ω * s) with hg
  have hfI : Integrable f μ := hI.const_inner ez
  have hgI : Integrable g μ := by
    apply ContinuousOn.integrableOn_Icc
    exact ha₁c.mul (Continuous.continuousOn (by fun_prop))
  have hint_eq : ∫ s, g s ∂μ = ∫ s, f s ∂μ := by
    rw [hf, integral_inner hI, ← hM, midpointM, real_inner_smul_right,
      real_inner_self_eq_norm_sq, norm_ez]
    simp [hg, hμ]
  have hle : g ≤ᵐ[μ] f := by
    refine ae_restrict_of_forall_mem measurableSet_Icc fun s hs => ?_
    simp only [hf, hg, real_inner_smul_right]
    rw [real_inner_comm (d s) ez]
    have h1 := hatt.inner_d_ez hω.le hδ hs (by linarith [hθ_le s hs, Real.pi_pos])
    have h2 := hale s hs
    have h3 := hcos_nn s hs
    have h4 := ha₁p s hs
    nlinarith
  have hae : g =ᵐ[μ] f := (integral_eq_iff_of_ae_le hgI hfI hle).1 hint_eq
  -- a.e. good times
  have hne0 : ∀ᵐ s ∂μ, s ≠ 0 := by
    have : ∀ᵐ s ∂(volume : Measure ℝ), s ∈ ({0}ᶜ : Set ℝ) :=
      compl_mem_ae_iff.2 (measure_singleton 0)
    filter_upwards [ae_restrict_of_ae this] with s hs using hs
  have hgood : ∀ᵐ s ∂μ, s ∈ Icc 0 tf ∧ 0 < s ∧ ⟪d s, ez⟫ = Real.cos (δ + ω * s) := by
    filter_upwards [hae, ae_restrict_mem measurableSet_Icc, hne0] with s h1 h2 h3
    refine ⟨h2, lt_of_le_of_ne h2.1 (Ne.symm h3), ?_⟩
    simp only [hf, hg, real_inner_smul_right] at h1
    rw [real_inner_comm (d s) ez] at h1
    have h4 := hatt.inner_d_ez hω.le hδ h2 (by linarith [hθ_le s h2, Real.pi_pos])
    have h5 := hale s h2
    have h6 := hcos_nn s h2
    have h7 := ha₁p s h2
    have h8 : 0 < a s := lt_of_lt_of_le h7 h5
    have : a s * (⟪d s, ez⟫ - Real.cos (δ + ω * s)) = 0 := by nlinarith
    rcases mul_eq_zero.1 this with h | h
    · exact absurd h h8.ne'
    · linarith
  -- consequences at a good time
  have hsin_b : ∀ s, 0 < s → s ≤ tf → 0 < Real.sin (ω * s) := fun s hs hs' =>
    Real.sin_pos_of_pos_of_lt_pi (mul_pos hω hs) (by nlinarith [Real.pi_pos])
  have hsin_d : ∀ s, 0 < s → s ≤ tf → 0 < Real.sin (δ + ω * s) := fun s hs hs' =>
    Real.sin_pos_of_pos_of_lt_pi (by nlinarith [mul_pos hω hs]) (by nlinarith [Real.pi_pos])
  have key : ∀ s, s ∈ Icc 0 tf → 0 < s → ⟪d s, ez⟫ = Real.cos (δ + ω * s) →
      ⟪b s, ez⟫ = Real.cos (ω * s) ∧
        lateral ez (d s) (δ + ω * s) = lateral ez (b s) (ω * s) := by
    intro s hs hs0 hds
    exact inner_triangle_eq_lateral (hatt.d_unit s hs) (hatt.b_unit s hs) norm_ez hδ
      (mul_pos hω hs0) (by linarith [hθ_le s hs, Real.pi_pos])
      (cos_le_inner_of_angle_le (hatt.d_unit s hs) (hatt.b_unit s hs) (hatt.gimbal s hs)
        (by linarith [hθ_le s hs, Real.pi_pos, mul_nonneg hω.le hs.1]))
      (hatt.inner_b_ez hs (by linarith [hθ_le s hs, Real.pi_pos])) hds
  -- pick one good time s₀
  have hμ0 : μ ≠ 0 := by
    rw [hμ, Ne, Measure.restrict_eq_zero, Real.volume_Icc]
    simpa using htf
  have : (ae μ).NeBot := ae_neBot.2 hμ0
  obtain ⟨s₀, hs₀, hs₀pos, hds₀⟩ := hgood.exists
  obtain ⟨hbs₀, -⟩ := key s₀ hs₀ hs₀pos hds₀
  set u := lateral ez (b s₀) (ω * s₀) with hu_def
  have huz : ⟪u, ez⟫ = 0 := inner_lateral_pole norm_ez hbs₀
  have huu : ⟪u, u⟫ = 1 :=
    inner_lateral_self (hatt.b_unit s₀ hs₀) norm_ez hbs₀ (hsin_b s₀ hs₀pos hs₀.2).ne'
  -- the lateral component of the thrust is `sin(δ+ωs) u` at every good time
  have hlat : ∀ s, s ∈ Icc 0 tf → 0 < s → ⟪d s, ez⟫ = Real.cos (δ + ω * s) →
      ⟪u, d s⟫ = Real.sin (δ + ω * s) := by
    intro s hs hs0 hds
    obtain ⟨hbs, hld⟩ := key s hs hs0 hds
    have hbb : lateral ez (b s) (ω * s) = u := by
      apply lateral_eq_of_inner_ge (hatt.b_unit s hs) (hatt.b_unit s₀ hs₀) norm_ez hbs hbs₀
        (hsin_b s hs0 hs.2) (hsin_b s₀ hs₀pos hs₀.2)
      rw [← cos_mul_abs_sub hω.le]
      have habs : |s - s₀| ≤ tf := by
        rw [abs_sub_le_iff]; constructor <;> linarith [hs.1, hs.2, hs₀.1, hs₀.2]
      exact cos_le_inner_of_angle_le (hatt.b_unit s hs) (hatt.b_unit s₀ hs₀)
        (hatt.b_rate s hs s₀ hs₀) (by nlinarith [Real.pi_pos, abs_nonneg (s - s₀)])
    have hd := eq_cos_smul_add_sin_smul_lateral ez (d s) (hsin_d s hs0 hs.2).ne'
    rw [hld, hbb] at hd
    rw [hd, inner_add_right, real_inner_smul_right, real_inner_smul_right, huz, huu]
    ring
  -- lateral integral: zero (from `M`) but strictly positive (from the arcs)
  have hzero : ∫ s, ⟪u, a s • d s⟫ ∂μ = 0 := by
    rw [integral_inner hI, ← hM, midpointM, real_inner_smul_right, huz, mul_zero]
  have hlow : (fun s => a₁ s * Real.sin (δ + ω * s)) ≤ᵐ[μ] fun s => ⟪u, a s • d s⟫ := by
    filter_upwards [hgood] with s ⟨hs, hs0, hds⟩
    rw [real_inner_smul_right, hlat s hs hs0 hds]
    exact mul_le_mul_of_nonneg_right (hale s hs) (hsin_d s hs0 hs.2).le
  have hcont : ContinuousOn (fun s => a₁ s * Real.sin (δ + ω * s)) (Icc 0 tf) :=
    ha₁c.mul (Continuous.continuousOn (by fun_prop))
  have hpos : 0 < ∫ s in Icc 0 tf, a₁ s * Real.sin (δ + ω * s) :=
    integral_Icc_pos htf hcont fun s hs =>
      mul_pos (ha₁p s (Ioo_subset_Icc_self hs)) (hsin_d s hs.1 hs.2.le)
  have hmono := integral_mono_ae hcont.integrableOn_Icc (hI.const_inner u) hlow
  rw [hzero] at hmono
  linarith

/-- **Theorem B (5DOF, model M1).** The velocity-increment set `R` is not convex. -/
theorem not_convex_reachSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ}
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s)
    (ha₁ : a₁ ∈ Acc) : ¬ Convex ℝ (reachSet Acc tf ω δ) := by
  intro hconv
  have hωtf : ω * tf ≤ π := by linarith [Real.pi_pos]
  have hδπ : δ ≤ π := by nlinarith [Real.pi_pos]
  have mem : ∀ u : E3, ‖u‖ = 1 → ⟪u, ez⟫ = 0 → arcEndpoint tf ω δ a₁ u ∈ reachSet Acc tf ω δ :=
    fun u hu huz => ⟨a₁, arcD ω δ u, arcB ω u, ha₁, arc_admissible hu huz hω.le hδ hδπ hωtf, rfl⟩
  have h := hconv (mem ex norm_ex inner_ex_ez) (mem (-ex) (by simp) (by simp))
    (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num)
  rw [midpoint_arcEndpoint ha₁c] at h
  exact midpointM_not_mem_reachSet htf hω hδ hreg ha₁c ha₁p hAcc h

/-- **Theorem B for the landing set.** For any gravity vector `g`, the set `F_tf` of initial
positions/velocities from which a soft landing at time `tf` is possible is not convex. -/
theorem not_convex_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s)
    (ha₁ : a₁ ∈ Acc) : ¬ Convex ℝ (landingSet Acc tf ω δ g) := fun hF =>
  not_convex_reachSet htf hω hδ hreg ha₁c ha₁p hAcc ha₁
    (convex_reachSet_of_convex_landingSet g hF)

end LcvxObstruction
