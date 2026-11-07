import LcvxObstruction.Nonconvex

/-!
# Theorem B*: nonconvexity with altitude / glide-slope constraints (dive-then-brake face)

Model M1 with gravity `g = -g₀ e_z`, an acceleration class whose members satisfy
`a_min ≤ a ≤ a_max` (constant bounds: constant mass, i.e. `α = 0`, `a = T/m₀`), and the
state constraint that the position stays in the glide-slope cone
`{r | r_z ≥ 0, tan γ · ‖r_h‖ ≤ r_z}` for all `t ∈ [0, tf]` (`tan γ = 0` gives altitude only),
or any larger constraint set.

Proof (math/02 §10, qualitative Step 6, with the switch time `s*` satisfying `ω s* ≤ δ`):
* `Λ(θ) := r₀ + s* v₀` equals `W(c) + κ g` for any landing control `c`, with
  `W(c) = ∫ (s - s*) a d` (`lambda_identity`).
* Pointwise, `⟪W, e_z⟫ ≤ V* := ∫ h*` (dive: `d_z ≥ cos(δ+ωs)`, `a ≥ a_min`;
  brake: `d_z ≤ 1`, `a ≤ a_max`), and `V* e_z` is the midpoint of the `W` values of the two
  mirror-image dive-then-brake witnesses.
* If `V* e_z = W(c)`, equality holds a.e.; then `d = e_z` on the brake and the rigidity
  argument of Theorem B on the dive gives a lateral component of `W` that is strictly
  nonzero. Contradiction (`VStar_not_mem_WSet`).
* The witnesses satisfy the state constraints under an explicit smallness condition on `s*`
  (`witness_mem_glideSlope`), which can always be met (`exists_switchTime`).
-/

open MeasureTheory Set InnerProductGeometry Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-! ### State constraints -/

/-- Glide-slope state constraint on `(r, v)`: `r_z ≥ 0` and `tan γ · ‖r_h‖ ≤ r_z`, where
`r_z = ⟪r, e_z⟫` and `r_h = r - r_z e_z`. (`tanγ = 0`: altitude constraint only.) -/
def glideSlopeSet (tanγ : ℝ) : Set (E3 × E3) :=
  {x | 0 ≤ ⟪x.1, ez⟫ ∧ tanγ * ‖x.1 - ⟪x.1, ez⟫ • ez‖ ≤ ⟪x.1, ez⟫}

/-- **State-constrained landing set** `F^X_tf`: boundary data from which an admissible control
lands at `tf` while keeping `(r(t), v(t)) ∈ X` for all `t ∈ [0, tf]`. -/
def constrainedLandingSet (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) (X : Set (E3 × E3)) :
    Set (E3 × E3) :=
  {θ | ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position g θ.1 θ.2 a d t, velocity g θ.2 a d t) ∈ X}

theorem constrainedLandingSet_subset {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {g : E3}
    {X : Set (E3 × E3)} : constrainedLandingSet Acc tf ω δ g X ⊆ landingSet Acc tf ω δ g :=
  fun _ ⟨a, d, b, ha, hatt, hr, hv, _⟩ => ⟨a, d, b, ha, hatt, hr, hv⟩

/-! ### Landing identities -/

theorem integrableOn_cont_smul {tf : ℝ} {f : ℝ → E3} (hf : IntegrableOn f (Icc 0 tf))
    {c : ℝ → ℝ} (hc : Continuous c) : IntegrableOn (fun s => c s • f s) (Icc 0 tf) :=
  hf.continuousOn_smul hc.continuousOn isCompact_Icc

/-- **Lemma 10.1.** If the control lands from `(r₀, v₀)` at `tf`, then
`r₀ + s* v₀ = ∫ (s - s*) a d + (tf²/2 - s* tf) g`. -/
theorem lambda_identity {g r₀ v₀ : E3} {a : ℝ → ℝ} {d : ℝ → E3} {tf sS : ℝ}
    (hf : IntegrableOn (fun s => a s • d s) (Icc 0 tf))
    (hr : position g r₀ v₀ a d tf = 0) (hv : velocity g v₀ a d tf = 0) :
    r₀ + sS • v₀ =
      (∫ s in Icc 0 tf, (s - sS) • (a s • d s)) + (tf ^ 2 / 2 - sS * tf) • g := by
  have hK : (∫ s in Icc 0 tf, (s - sS) • (a s • d s)) =
      (tf - sS) • (∫ s in Icc 0 tf, a s • d s) - ∫ s in Icc 0 tf, (tf - s) • (a s • d s) := by
    have h1 : Integrable (fun s => (tf - sS) • (a s • d s)) (volume.restrict (Icc 0 tf)) :=
      integrableOn_cont_smul hf (c := fun _ => tf - sS) (by fun_prop)
    have h2 : Integrable (fun s => (tf - s) • (a s • d s)) (volume.restrict (Icc 0 tf)) :=
      integrableOn_cont_smul hf (c := fun s => tf - s) (by fun_prop)
    rw [← integral_smul, ← integral_sub h1 h2]
    congr 1; funext s; module
  simp only [position, velocity] at hr hv
  have hv' : v₀ = -(tf • g) - ∫ s in Icc 0 tf, a s • d s := by
    rw [← sub_eq_zero, ← hv]; abel
  have hr' : r₀ = -(tf • v₀) - (tf ^ 2 / 2) • g - ∫ s in Icc 0 tf, (tf - s) • (a s • d s) := by
    rw [← sub_eq_zero, ← hr]; abel
  rw [hK, hr', hv']
  module

theorem Icc_Ioc_disjoint (t tf : ℝ) : Disjoint (Icc 0 t) (Ioc t tf) :=
  Set.disjoint_left.2 fun _ h1 h2 => absurd h1.2 (not_le.2 h2.1)

/-- **Tail form of the trajectory.** If the control lands at `tf`, then for `t ∈ [0, tf]`,
`r(t) = ∫_t^tf (s - t) a d ds + ((tf - t)²/2) g`. -/
theorem position_eq_tail {g r₀ v₀ : E3} {a : ℝ → ℝ} {d : ℝ → E3} {tf t : ℝ}
    (ht : t ∈ Icc 0 tf) (hf : IntegrableOn (fun s => a s • d s) (Icc 0 tf))
    (hr : position g r₀ v₀ a d tf = 0) (hv : velocity g v₀ a d tf = 0) :
    position g r₀ v₀ a d t =
      (∫ s in Ioc t tf, (s - t) • (a s • d s)) + ((tf - t) ^ 2 / 2) • g := by
  have hφ : IntegrableOn (fun s => (s - t) • (a s • d s)) (Icc 0 tf) :=
    integrableOn_cont_smul hf (c := fun s => s - t) (by fun_prop)
  have hsplit : (∫ s in Icc 0 tf, (s - t) • (a s • d s)) =
      (∫ s in Icc 0 t, (s - t) • (a s • d s)) + ∫ s in Ioc t tf, (s - t) • (a s • d s) := by
    rw [← setIntegral_union (Icc_Ioc_disjoint t tf) measurableSet_Ioc
      (hφ.mono_set (Icc_subset_Icc_right ht.2)) (hφ.mono_set (Ioc_subset_Icc_self.trans (Icc_subset_Icc_left ht.1))),
      Icc_union_Ioc_eq_Icc ht.1 ht.2]
  have hneg : (∫ s in Icc 0 t, (s - t) • (a s • d s)) =
      -∫ s in Icc 0 t, (t - s) • (a s • d s) := by
    rw [← integral_neg]; congr 1; funext s; module
  have hfull : (∫ s in Icc 0 tf, (s - t) • (a s • d s)) =
      (tf - t) • (∫ s in Icc 0 tf, a s • d s) - ∫ s in Icc 0 tf, (tf - s) • (a s • d s) := by
    have h1 : Integrable (fun s => (tf - t) • (a s • d s)) (volume.restrict (Icc 0 tf)) :=
      integrableOn_cont_smul hf (c := fun _ => tf - t) (by fun_prop)
    have h2 : Integrable (fun s => (tf - s) • (a s • d s)) (volume.restrict (Icc 0 tf)) :=
      integrableOn_cont_smul hf (c := fun s => tf - s) (by fun_prop)
    rw [← integral_smul, ← integral_sub h1 h2]
    congr 1; funext s; module
  have htail : (∫ s in Ioc t tf, (s - t) • (a s • d s)) =
      (tf - t) • (∫ s in Icc 0 tf, a s • d s) - (∫ s in Icc 0 tf, (tf - s) • (a s • d s)) +
        ∫ s in Icc 0 t, (t - s) • (a s • d s) := by
    rw [← hfull, hsplit, hneg]; abel
  simp only [position, velocity] at hr hv ⊢
  have hv' : v₀ = -(tf • g) - ∫ s in Icc 0 tf, a s • d s := by
    rw [← sub_eq_zero, ← hv]; abel
  have hr' : r₀ = -(tf • v₀) - (tf ^ 2 / 2) • g - ∫ s in Icc 0 tf, (tf - s) • (a s • d s) := by
    rw [← sub_eq_zero, ← hr]; abel
  rw [htail, hr', hv']
  module

/-! ### The supporting functional and the core non-membership -/

/-- Pointwise maximiser of `(s - s*) a d_z`: `(s-s*) a_min cos(δ+ωs)` on the dive `s ≤ s*`,
`(s-s*) a_max` on the brake `s ≥ s*` (written with `min`/`max` so it is continuous). -/
noncomputable def hStar (ω δ sS amin amax : ℝ) (s : ℝ) : ℝ :=
  min (s - sS) 0 * amin * Real.cos (δ + ω * s) + max (s - sS) 0 * amax

/-- `V* = ∫₀^tf h*`, the maximal value of `⟪W(c), e_z⟫`. -/
noncomputable def VStar (tf ω δ sS amin amax : ℝ) : ℝ :=
  ∫ s in Icc 0 tf, hStar ω δ sS amin amax s

/-- The set of weighted impulses `W(c) = ∫₀^tf (s - s*) a d` of admissible controls. -/
def WSet (Acc : Set (ℝ → ℝ)) (tf ω δ sS : ℝ) : Set E3 :=
  {w | ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b ∧
    w = ∫ s in Icc 0 tf, (s - sS) • (a s • d s)}

theorem continuous_hStar (ω δ sS amin amax : ℝ) : Continuous (hStar ω δ sS amin amax) := by
  unfold hStar; fun_prop

theorem inner_le_one_of_unit {x y : E3} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) : ⟪x, y⟫ ≤ 1 := by
  have := real_inner_le_norm x y
  rw [hx, hy, mul_one] at this; exact this

theorem eq_of_inner_eq_one {x y : E3} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) (h : ⟪x, y⟫ = 1) :
    x = y := by
  have hxx : ⟪x, x⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hx]; norm_num
  have hyy : ⟪y, y⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hy]; norm_num
  have hyx : ⟪y, x⟫ = 1 := by rw [real_inner_comm]; exact h
  have : ⟪x - y, x - y⟫ ≤ 0 := by
    simp only [inner_sub_left, inner_sub_right, hxx, hyy, h, hyx]; norm_num
  exact sub_eq_zero.mp (real_inner_self_nonpos.mp this)

/-- **Core of Theorem B\*.** `V* e_z` is not the weighted impulse of any admissible control. -/
theorem VStar_not_mem_WSet {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * sS ≤ π / 2)
    (hamin : 0 < amin)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax) :
    VStar tf ω δ sS amin amax • ez ∉ WSet Acc tf ω δ sS := by
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
  -- vertical component
  set f : ℝ → ℝ := fun s => ⟪ez, (s - sS) • (a s • d s)⟫ with hf
  have hf_eq : ∀ s, f s = (s - sS) * (a s * ⟪d s, ez⟫) := fun s => by
    simp only [hf, real_inner_smul_right]; rw [real_inner_comm (d s) ez]
  have hfI : Integrable f μ := hI.const_inner ez
  have hhI : Integrable (hStar ω δ sS amin amax) μ :=
    (continuous_hStar ω δ sS amin amax).continuousOn.integrableOn_Icc
  have hint_eq : ∫ s, hStar ω δ sS amin amax s ∂μ = ∫ s, f s ∂μ := by
    rw [hf, integral_inner hI, ← hW, real_inner_smul_right, real_inner_self_eq_norm_sq, norm_ez]
    simp [VStar, hμ]
  have hle : f ≤ᵐ[μ] hStar ω δ sS amin amax := by
    refine ae_restrict_of_forall_mem measurableSet_Icc fun s hs => ?_
    rw [hf_eq]
    obtain ⟨h1, h2⟩ := hab s hs
    simp only [hStar]
    rcases le_or_gt s sS with h | h
    · rw [min_eq_left (by linarith), max_eq_right (by linarith)]
      have h3 := hdz s hs h
      have h4 := hcos_nn s hs h
      have hw : s - sS ≤ 0 := by linarith
      have e1 : 0 ≤ a s * (⟪d s, ez⟫ - Real.cos (δ + ω * s)) :=
        mul_nonneg (by linarith) (by linarith)
      have e2 : 0 ≤ Real.cos (δ + ω * s) * (a s - amin) := mul_nonneg h4 (by linarith)
      nlinarith [mul_nonpos_of_nonpos_of_nonneg hw e1, mul_nonpos_of_nonpos_of_nonneg hw e2]
    · rw [min_eq_right (by linarith), max_eq_left (by linarith)]
      have h3 := hdz1 s hs
      have hw : 0 ≤ s - sS := by linarith
      have e1 : a s * ⟪d s, ez⟫ ≤ amax := by nlinarith
      nlinarith [mul_le_mul_of_nonneg_left e1 hw]
  have hae : f =ᵐ[μ] hStar ω δ sS amin amax :=
    (integral_eq_iff_of_ae_le hfI hhI hle).1 hint_eq.symm
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
      simp only [hStar, min_eq_left (by linarith : s - sS ≤ 0),
        max_eq_right (by linarith : s - sS ≤ 0)] at h1'
      obtain ⟨h5, -⟩ := hab s h2
      have h6 := hdz s h2 hlt.le
      have h7 := hcos_nn s h2 hlt.le
      have h8 : 0 < a s := lt_of_lt_of_le hamin h5
      have hw : s - sS ≠ 0 := by linarith
      have e : amin * Real.cos (δ + ω * s) = a s * ⟪d s, ez⟫ := by
        have := mul_left_cancel₀ hw (by linarith [h1'] : (s - sS) * (amin * Real.cos (δ + ω * s))
          = (s - sS) * (a s * ⟪d s, ez⟫))
        linarith
      have : a s * (⟪d s, ez⟫ - Real.cos (δ + ω * s)) = 0 := by nlinarith
      rcases mul_eq_zero.1 this with h | h
      · exact absurd h h8.ne'
      · linarith
    · intro hlt
      have h1' := h1
      rw [hf_eq] at h1'
      simp only [hStar, min_eq_right (by linarith : 0 ≤ s - sS),
        max_eq_left (by linarith : 0 ≤ s - sS)] at h1'
      obtain ⟨h5, h5'⟩ := hab s h2
      have h6 := hdz1 s h2
      have h8 : 0 < a s := lt_of_lt_of_le hamin h5
      have hw : s - sS ≠ 0 := by linarith
      have e : amax = a s * ⟪d s, ez⟫ := by
        have := mul_left_cancel₀ hw (by linarith [h1'] : (s - sS) * amax
          = (s - sS) * (a s * ⟪d s, ez⟫))
        linarith
      have : a s * (1 - ⟪d s, ez⟫) = 0 := by nlinarith
      rcases mul_eq_zero.1 this with h | h
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
      obtain ⟨h5, -⟩ := hab s hs
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

end LcvxObstruction
