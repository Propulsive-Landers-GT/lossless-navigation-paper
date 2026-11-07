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

/-! ### The dive-then-brake witnesses -/

/-- Witness throttle: minimum on the dive `s ≤ s*`, maximum on the brake. -/
noncomputable def aW (sS amin amax : ℝ) (s : ℝ) : ℝ := if s ≤ sS then amin else amax

/-- Witness thrust direction: extreme tilt (gimbal `δ` beyond the axis) on the dive, vertical on
the brake. -/
noncomputable def dW (ω δ sS : ℝ) (u : E3) (s : ℝ) : E3 := if s ≤ sS then arcD ω δ u s else ez

/-- Witness body axis: tilt at the maximal rate until `s*`, then hold. -/
noncomputable def bW (ω sS : ℝ) (u : E3) (s : ℝ) : E3 := arcB ω u (min s sS)

theorem measurable_aW (sS amin amax : ℝ) : Measurable (aW sS amin amax) :=
  Measurable.ite measurableSet_Iic measurable_const measurable_const

theorem measurable_dW (ω δ sS : ℝ) (u : E3) : Measurable (dW ω δ sS u) :=
  Measurable.ite measurableSet_Iic (by unfold arcD; fun_prop) measurable_const

theorem norm_dW {ω δ sS : ℝ} {u : E3} (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0) (s : ℝ) :
    ‖dW ω δ sS u s‖ = 1 := by
  unfold dW; split_ifs
  · exact norm_polar hu norm_ez huz _
  · exact norm_ez

theorem inner_ez_arcB {ω : ℝ} {u : E3} (huz : ⟪u, ez⟫ = 0) (x : ℝ) :
    ⟪ez, arcB ω u x⟫ = Real.cos (ω * x) := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  rw [arcB, inner_add_right, real_inner_smul_right, real_inner_smul_right, real_inner_comm,
    huz, hzz]; ring

/-- **The witnesses are admissible.** -/
theorem witness_admissible {tf ω δ sS : ℝ} {u : E3} (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0)
    (hsS : 0 < sS) (hω : 0 ≤ ω) (hδ : 0 ≤ δ) (hδπ : δ ≤ π) (hωs : ω * sS ≤ δ) :
    AttitudeAdmissible tf ω δ (dW ω δ sS u) (bW ω sS u) where
  b_init := by simp [bW, arcB, min_eq_left hsS.le]
  b_unit s _ := norm_polar hu norm_ez huz _
  b_cont := by unfold bW arcB; fun_prop
  b_rate s hs s' hs' := by
    have hm : |min s sS - min s' sS| ≤ |s - s'| :=
      (abs_min_sub_min_le_max _ _ _ _).trans (by simp)
    have hmS : |min s sS - min s' sS| ≤ sS := by
      rw [abs_sub_le_iff]
      constructor <;> linarith [min_le_right s sS, min_le_right s' sS,
        le_min hs.1 hsS.le, le_min hs'.1 hsS.le]
    calc angle (bW ω sS u s) (bW ω sS u s') ≤ ω * |min s sS - min s' sS| := by
          apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _)
            (norm_polar hu norm_ez huz _) (mul_nonneg hω (abs_nonneg _))
            (by nlinarith [mul_le_mul_of_nonneg_left hmS hω])
          rw [inner_polar hu norm_ez huz, cos_mul_abs_sub hω]
      _ ≤ ω * |s - s'| := mul_le_mul_of_nonneg_left hm hω
  d_meas := (measurable_dW ω δ sS u).aestronglyMeasurable
  d_unit s _ := norm_dW hu huz s
  gimbal s _ := by
    by_cases h : s ≤ sS
    · simp only [dW, bW, h, ↓reduceIte, min_eq_left h]
      apply angle_le_of_cos_le_inner (norm_polar hu norm_ez huz _) (norm_polar hu norm_ez huz _)
        hδ hδπ
      rw [inner_polar hu norm_ez huz]
      ring_nf; exact le_rfl
    · simp only [dW, bW, h, ↓reduceIte, min_eq_right (le_of_lt (not_le.1 h))]
      apply angle_le_of_cos_le_inner norm_ez (norm_polar hu norm_ez huz _) hδ hδπ
      rw [← arcB, inner_ez_arcB huz]
      exact Real.cos_le_cos_of_nonneg_of_le_pi (mul_nonneg hω hsS.le) hδπ hωs

theorem aW_mem_accBox {tf sS amin amax : ℝ} (h : amin ≤ amax) :
    aW sS amin amax ∈ AccBox tf (fun _ => amin) (fun _ => amax) := by
  refine ⟨?_, fun s _ => ?_⟩
  · refine Integrable.mono' (integrableOn_const (C := |amin| + |amax|) measure_Icc_lt_top.ne)
      (measurable_aW sS amin amax).aestronglyMeasurable (ae_of_all _ fun s => ?_)
    unfold aW; split_ifs <;> simp [Real.norm_eq_abs] <;> linarith [abs_nonneg amin, abs_nonneg amax]
  · unfold aW; split_ifs <;> constructor <;> linarith

theorem integrableOn_witness {tf sS amin amax ω δ : ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (h : amin ≤ amax) :
    IntegrableOn (fun s => aW sS amin amax s • dW ω δ sS u s) (Icc 0 tf) :=
  integrableOn_smul_of_unit (aW_mem_accBox (tf := tf) h).1
    (measurable_dW ω δ sS u).aestronglyMeasurable fun s _ => norm_dW hu huz s

/-- The midpoint of the weighted impulses of the two mirror witnesses is `V* e_z`. -/
theorem witness_W_midpoint {tf ω δ sS amin amax : ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (h : amin ≤ amax) :
    (1 / 2 : ℝ) • (∫ s in Icc 0 tf, (s - sS) • (aW sS amin amax s • dW ω δ sS u s)) +
      (1 / 2 : ℝ) • (∫ s in Icc 0 tf, (s - sS) • (aW sS amin amax s • dW ω δ sS (-u) s)) =
      VStar tf ω δ sS amin amax • ez := by
  have h1 : Integrable (fun s => (1 / 2 : ℝ) • ((s - sS) • (aW sS amin amax s • dW ω δ sS u s)))
      (volume.restrict (Icc 0 tf)) :=
    (integrableOn_cont_smul (integrableOn_witness hu huz h) (c := fun s => s - sS)
      (by fun_prop)).smul (1 / 2 : ℝ)
  have h2 : Integrable
      (fun s => (1 / 2 : ℝ) • ((s - sS) • (aW sS amin amax s • dW ω δ sS (-u) s)))
      (volume.restrict (Icc 0 tf)) :=
    (integrableOn_cont_smul (integrableOn_witness (by simpa using hu) (by simpa using huz) h)
      (c := fun s => s - sS) (by fun_prop)).smul (1 / 2 : ℝ)
  rw [← integral_smul, ← integral_smul, ← integral_add h1 h2, VStar, ← integral_smul_const]
  congr 1
  funext s
  by_cases hs : s ≤ sS
  · simp only [aW, dW, hStar, hs, ↓reduceIte, min_eq_left (sub_nonpos.2 hs),
      max_eq_right (sub_nonpos.2 hs), arcD]
    module
  · have hs' : 0 ≤ s - sS := by linarith [not_le.1 hs]
    simp only [aW, dW, hStar, hs, ↓reduceIte, min_eq_right hs', max_eq_left hs']
    module

/-! ### Landing data of a control, and the witnesses' state constraints -/

/-- The boundary data from which the control `(a, d)` lands at `tf` (gravity `g`). -/
noncomputable def landingData (g : E3) (a : ℝ → ℝ) (d : ℝ → E3) (tf : ℝ) : E3 × E3 :=
  (-(tf • (-(tf • g) - ∫ s in Icc 0 tf, a s • d s) + (tf ^ 2 / 2) • g +
      ∫ s in Icc 0 tf, (tf - s) • (a s • d s)),
    -(tf • g) - ∫ s in Icc 0 tf, a s • d s)

theorem landingData_lands (g : E3) (a : ℝ → ℝ) (d : ℝ → E3) (tf : ℝ) :
    position g (landingData g a d tf).1 (landingData g a d tf).2 a d tf = 0 ∧
      velocity g (landingData g a d tf).2 a d tf = 0 := by
  constructor
  · simp only [position, landingData]; abel
  · simp only [velocity, landingData]; abel

theorem integral_Ioc_sub_self {p q : ℝ} (hpq : p ≤ q) (t : ℝ) :
    ∫ s in Ioc p q, (s - t) = ((q - t) ^ 2 - (p - t) ^ 2) / 2 := by
  rw [← intervalIntegral.integral_of_le hpq,
    intervalIntegral.integral_comp_sub_right (fun x => x) t, integral_id]

theorem Ioc_disjoint_Ioc' (t sS tf : ℝ) : Disjoint (Ioc t sS) (Ioc sS tf) :=
  Set.disjoint_left.2 fun _ h1 h2 => absurd h1.2 (not_le.2 h2.1)

/-- **The witness trajectory satisfies the glide-slope constraint** at every time, provided the
switch time is short: `(a_max + 2 tanγ a_min) s*² ≤ (a_max - g₀)(tf - s*)²`. -/
theorem witness_mem_glideSlope {tf ω δ sS amin amax g₀ tanγ : ℝ} {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 ≤ ω) (hδ : 0 ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ ≤ amax)
    (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2)
    {t : ℝ} (ht : t ∈ Icc 0 tf) :
    (position (-(g₀ • ez)) (landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS u) tf).1
        (landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS u) tf).2
        (aW sS amin amax) (dW ω δ sS u) t,
      velocity (-(g₀ • ez)) (landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS u) tf).2
        (aW sS amin amax) (dW ω δ sS u) t) ∈ glideSlopeSet tanγ := by
  set a := aW sS amin amax
  set d := dW ω δ sS u
  have hf := integrableOn_witness (tf := tf) (sS := sS) (ω := ω) (δ := δ) hu huz h
  obtain ⟨hr, hv⟩ := landingData_lands (-(g₀ • ez)) a d tf
  simp only [glideSlopeSet, Set.mem_setOf_eq]
  rw [position_eq_tail ht hf hr hv]
  -- the integrand and its vertical / lateral parts
  set ψ : ℝ → E3 := fun s => (s - t) • (a s • d s) with hψ
  have hψI : IntegrableOn ψ (Icc 0 tf) :=
    integrableOn_cont_smul hf (c := fun s => s - t) (by fun_prop)
  have hψI' : IntegrableOn ψ (Ioc t tf) :=
    hψI.mono_set (Ioc_subset_Icc_self.trans (Icc_subset_Icc_left ht.1))
  set Z : ℝ → ℝ := fun s => ⟪ψ s, ez⟫ with hZ
  set L : ℝ → E3 := fun s => ψ s - Z s • ez with hL
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have hZ_dive : ∀ s, s ≤ sS → Z s = (s - t) * (amin * Real.cos (δ + ω * s)) := fun s hs => by
    simp only [hZ, hψ, a, d, aW, dW, hs, ↓reduceIte, arcD, real_inner_smul_left, inner_add_left, huz,
      hzz]; ring
  have hZ_brake : ∀ s, sS < s → Z s = (s - t) * amax := fun s hs => by
    simp only [hZ, hψ, a, d, aW, dW, not_le.2 hs, ↓reduceIte, real_inner_smul_left, hzz]; ring
  have hL_dive : ∀ s, s ≤ sS → L s = ((s - t) * amin * Real.sin (δ + ω * s)) • u := fun s hs => by
    simp only [hL, hZ_dive s hs, hψ, a, d, aW, dW, hs, ↓reduceIte, arcD]; module
  have hL_brake : ∀ s, sS < s → L s = 0 := fun s hs => by
    simp only [hL, hZ_brake s hs, hψ, a, d, aW, dW, not_le.2 hs, ↓reduceIte]; module
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
  -- case analysis on the time
  rcases le_or_gt sS t with hts | hts
  · -- brake phase only
    have hZeq : ∫ s in Ioc t tf, Z s = amax * c := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hZ_brake s (by linarith [hs.1])),
        integral_mul_const, integral_Ioc_sub_self ht.2]
      simp only [hc]; ring
    have hLeq : ∫ s in Ioc t tf, L s = 0 := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hL_brake s (by linarith [hs.1]))]
      simp
    rw [hZeq, hLeq, norm_zero, mul_zero]
    have : 0 ≤ (amax - g₀) * c := mul_nonneg (by linarith) (by positivity)
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
      positivity
    have hZ2 : ∫ s in Ioc sS tf, Z s = amax * (((tf - t) ^ 2 - (sS - t) ^ 2) / 2) := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hZ_brake s hs.1),
        integral_mul_const, integral_Ioc_sub_self hsStf.le]
      ring
    have hL2 : ∫ s in Ioc sS tf, L s = 0 := by
      rw [setIntegral_congr_fun measurableSet_Ioc (fun s hs => hL_brake s hs.1)]; simp
    have hL1 : ‖∫ s in Ioc t sS, L s‖ ≤ amin * sS * sS := by
      have hb : ∀ s ∈ Ioc t sS, ‖L s‖ ≤ amin * sS := fun s hs => by
        rw [hL_dive s hs.2, norm_smul, hu, mul_one, Real.norm_eq_abs, abs_mul, abs_mul,
          abs_of_nonneg (by linarith [hs.1] : (0:ℝ) ≤ s - t), abs_of_pos hamin]
        have h1 : |Real.sin (δ + ω * s)| ≤ 1 := Real.abs_sin_le_one _
        have h2 : s - t ≤ sS := by linarith [hs.2, ht.1]
        have h3 : 0 ≤ s - t := by linarith [hs.1]
        calc (s - t) * amin * |Real.sin (δ + ω * s)| ≤ sS * amin * 1 := by gcongr
          _ = amin * sS := by ring
      have := norm_setIntegral_le_of_norm_le_const (μ := volume) measure_Ioc_lt_top hb
      rw [Real.volume_real_Ioc_of_le hts.le] at this
      calc ‖∫ s in Ioc t sS, L s‖ ≤ amin * sS * (sS - t) := this
        _ ≤ amin * sS * sS := by
          apply mul_le_mul_of_nonneg_left (by linarith [ht.1]); positivity
    rw [hsplit hZI, hZ2, hsplitV, hL2, add_zero]
    have hmono1 : (tf - sS) ^ 2 ≤ (tf - t) ^ 2 :=
      pow_le_pow_left₀ (by linarith) (by linarith) 2
    have hmono2 : (sS - t) ^ 2 ≤ sS ^ 2 := pow_le_pow_left₀ (by linarith) (by linarith [ht.1]) 2
    have hlat : tanγ * ‖∫ s in Ioc t sS, L s‖ ≤ tanγ * (amin * sS * sS) :=
      mul_le_mul_of_nonneg_left hL1 htan
    have k1 : (amax - g₀) * (tf - sS) ^ 2 ≤ (amax - g₀) * (tf - t) ^ 2 :=
      mul_le_mul_of_nonneg_left hmono1 (by linarith)
    have k2 : amax * (sS - t) ^ 2 ≤ amax * sS ^ 2 :=
      mul_le_mul_of_nonneg_left hmono2 (by linarith)
    have hgc : g₀ * c = g₀ * (tf - t) ^ 2 / 2 := by rw [hc]; ring
    have hkey : tanγ * (amin * sS * sS) ≤
        (∫ s in Ioc t sS, Z s) + amax * (((tf - t) ^ 2 - (sS - t) ^ 2) / 2) - g₀ * c := by
      rw [hgc]
      have e : tanγ * (amin * sS * sS) = (2 * tanγ * amin) * sS ^ 2 / 2 := by ring
      rw [e]
      linarith
    have hnn : 0 ≤ tanγ * (amin * sS * sS) := by positivity
    exact ⟨by linarith, by linarith⟩

/-! ### Theorem B* -/

/-- Generic step: a set squeezed between two points of `S` and a superset `T` that misses their
midpoint is not convex. -/
theorem not_convex_of_midpoint {E : Type*} [AddCommGroup E] [Module ℝ E] {S T : Set E}
    (hST : S ⊆ T) {x y : E} (hx : x ∈ S) (hy : y ∈ S)
    (hm : (1 / 2 : ℝ) • x + (1 / 2 : ℝ) • y ∉ T) : ¬ Convex ℝ S := fun hconv =>
  hm (hST (hconv hx hy (by norm_num) (by norm_num) (by norm_num)))

/-- **Step 6 of Theorem B\*:** the midpoint of the two mirror witness data is not even
unconstrained-feasible. -/
theorem witness_midpoint_not_mem_landingSet {Acc : Set (ℝ → ℝ)}
    {tf ω δ sS amin amax g₀ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hδ : 0 ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax) :
    (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS ex) tf +
      (1 / 2 : ℝ) • landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (-ex)) tf ∉
      landingSet Acc tf ω δ (-(g₀ • ez)) := by
  set g := -(g₀ • ez)
  rintro ⟨a, d, b, ha, hatt, hr, hv⟩
  have hfa : IntegrableOn (fun s => a s • d s) (Icc 0 tf) :=
    integrableOn_smul_of_unit (hAcc a ha).1 hatt.d_meas hatt.d_unit
  have hΛ := lambda_identity (sS := sS) hfa hr hv
  have hΛ₁ := lambda_identity (sS := sS) (integrableOn_witness (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) norm_ex inner_ex_ez h) (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hΛ₂ := lambda_identity (sS := sS) (integrableOn_witness (tf := tf) (sS := sS) (ω := ω)
    (δ := δ) (by simp : ‖-ex‖ = 1) (by simp : ⟪-ex, ez⟫ = 0) h)
    (landingData_lands g _ _ tf).1 (landingData_lands g _ _ tf).2
  have hW := witness_W_midpoint (tf := tf) (ω := ω) (δ := δ) (sS := sS) norm_ex inner_ex_ez h
  apply VStar_not_mem_WSet hsS hsStf hω hδ hreg hamin hAcc
  refine ⟨a, d, b, ha, hatt, ?_⟩
  simp only [Prod.fst_add, Prod.snd_add, Prod.smul_fst, Prod.smul_snd] at hΛ
  rw [← hW]
  linear_combination (norm := module) hΛ - (1 / 2 : ℝ) • hΛ₁ - (1 / 2 : ℝ) • hΛ₂

/-- **Theorem B\* (state-constrained nonconvexity).** Constant acceleration bounds
`0 < a_min ≤ a_max` (constant mass), gravity `-g₀ e_z` with `g₀ ≤ a_max`, gimbal `δ`, slew rate
`ω > 0`, switch time `s* ∈ (0, tf)` with `ω s* ≤ δ`, `δ + ω s* ≤ π/2` and the smallness
condition `hS`. Then for every state-constraint set `X` containing the glide-slope set
(e.g. altitude only, `tanγ = 0`), the constrained landing set is **not convex**.
The acceleration class `Acc` is arbitrary subject to: members are integrable with
`a_min ≤ a ≤ a_max`, and the min-then-max throttle profile is admissible. -/
theorem not_convex_constrainedLandingSet {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ tanγ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ ≤ amax)
    (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (haW : aW sS amin amax ∈ Acc) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X) :
    ¬ Convex ℝ (constrainedLandingSet Acc tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have mem : ∀ v : E3, ‖v‖ = 1 → ⟪v, ez⟫ = 0 →
      landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS v) tf ∈
        constrainedLandingSet Acc tf ω δ (-(g₀ • ez)) X :=
    fun v hv hvz => ⟨_, _, _, haW, witness_admissible hv hvz hsS hω.le hδ hδπ hωs,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witness_mem_glideSlope hv hvz hsS hsStf hω.le hδ hreg hamin h hg htan hS ht)⟩
  exact not_convex_of_midpoint constrainedLandingSet_subset (mem ex norm_ex inner_ex_ez)
    (mem (-ex) (by simp) (by simp))
    (witness_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg hamin h hAcc)

/-- The switch-time conditions of Theorem B* can be met for **every** horizon `tf > 0`
(given `0 < δ < π/2`, `ω > 0`, `g₀ < a_max`). -/
theorem exists_switchTime {tf ω δ amin amax g₀ tanγ : ℝ} (htf : 0 < tf) (hω : 0 < ω)
    (hδ : 0 < δ) (hδ2 : δ < π / 2) (hg : g₀ < amax) :
    ∃ sS, 0 < sS ∧ sS < tf ∧ ω * sS ≤ δ ∧ δ + ω * sS ≤ π / 2 ∧
      (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2 ∧ 2 * sS ≤ tf := by
  set K := amax + 2 * tanγ * amin
  set D := amax - g₀ with hD
  have hD0 : 0 < D := by linarith
  set ε := D * tf / (4 * (|K| + 1)) with hεdef
  have hK1 : 0 < |K| + 1 := by positivity
  have hε : 0 < ε := by positivity
  set sS := min (min (tf / 2) (δ / ω)) (min ((π / 2 - δ) / ω) ε) with hsS
  have h1 : sS ≤ tf / 2 := (min_le_left _ _).trans (min_le_left _ _)
  have h2 : sS ≤ δ / ω := (min_le_left _ _).trans (min_le_right _ _)
  have h3 : sS ≤ (π / 2 - δ) / ω := (min_le_right _ _).trans (min_le_left _ _)
  have h4 : sS ≤ ε := (min_le_right _ _).trans (min_le_right _ _)
  have h0 : 0 < sS := lt_min (lt_min (by positivity) (by positivity))
    (lt_min (div_pos (by linarith) hω) hε)
  refine ⟨sS, h0, by linarith, ?_, ?_, ?_, by linarith⟩
  · have := (le_div_iff₀ hω).1 h2; linarith
  · have := (le_div_iff₀ hω).1 h3; linarith
  · have e1 : |K| * ε ≤ D * tf / 4 := by
      have : |K| * ε = (D * tf / 4) * (|K| / (|K| + 1)) := by
        rw [hεdef]; field_simp
      rw [this]
      exact mul_le_of_le_one_right (by positivity) ((div_le_one hK1).2 (by linarith))
    have e2 : tf ^ 2 / 4 ≤ (tf - sS) ^ 2 := by nlinarith
    have e3 : K * sS ^ 2 ≤ |K| * sS ^ 2 := mul_le_mul_of_nonneg_right (le_abs_self K) (sq_nonneg _)
    have e4 : |K| * sS ^ 2 ≤ |K| * ε * sS := by
      rw [sq, ← mul_assoc]
      exact mul_le_mul_of_nonneg_right (mul_le_mul_of_nonneg_left h4 (abs_nonneg K)) h0.le
    have e5 : |K| * ε * sS ≤ D * tf / 4 * (tf / 2) :=
      mul_le_mul e1 h1 h0.le (by positivity)
    nlinarith

end LcvxObstruction
