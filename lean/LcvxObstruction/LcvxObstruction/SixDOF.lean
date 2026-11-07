import LcvxObstruction.DiveBrake

/-!
# 6DOF (kinematic, rate-limited attitude) corollaries

The full attitude is a linear isometry `A s : E3 →ₗᵢ E3` (body frame → inertial frame; any
roll allowed). The thrust axis is the body z-axis `A s e_z`. Constraints:
* `A 0 e_z = e_z` (upright start, initial roll free);
* continuity of `s ↦ A s x` for every body vector `x`;
* **attitude-rate limit**: every body-fixed direction turns at angular rate at most `ω`,
  `angle (A s x) (A s' x) ≤ ω |s - s'|` for `x ≠ 0` (for a rotation, this is the same as
  `‖Ω‖ ≤ ω` for the angular velocity, so the attitude is ω-Lipschitz in the SO(3) geodesic
  metric);
* an attitude class `Att` (e.g. proper rotations `det = 1`, see `properAttitudes`);
* gimbal `angle (d s) (A s e_z) ≤ δ`.

Projection: a 6DOF-admissible attitude gives an M1-admissible thrust axis
(`Attitude6Admissible.toM1`), so every 6DOF landing set lies inside the 5DOF one.
Lift: the planar witnesses are realised by rotations about the horizontal axis `e_y`
(`rotY`), which have zero roll. Hence Theorems B and B* hold verbatim for 6DOF.
-/

open MeasureTheory Set InnerProductGeometry Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- The horizontal unit vector `e_y`. -/
noncomputable def ey : E3 := EuclideanSpace.single 1 1

/-- **6DOF attitude/direction admissibility** for an attitude path `A` in the class `Att`. -/
structure Attitude6Admissible (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (tf ω δ : ℝ) (d : ℝ → E3)
    (A : ℝ → (E3 →ₗᵢ[ℝ] E3)) : Prop where
  /-- The attitude path belongs to the admissible class (e.g. proper rotations). -/
  mem : A ∈ Att
  /-- Initially upright (initial roll free). -/
  init : A 0 ez = ez
  /-- The attitude is continuous. -/
  cont : ∀ x, ContinuousOn (fun s => A s x) (Icc 0 tf)
  /-- Attitude-rate limit: every body-fixed direction turns at rate at most `ω`. -/
  rate : ∀ s ∈ Icc 0 tf, ∀ s' ∈ Icc 0 tf, ∀ x : E3, x ≠ 0 →
    angle (A s x) (A s' x) ≤ ω * |s - s'|
  d_meas : AEStronglyMeasurable d (volume.restrict (Icc 0 tf))
  d_unit : ∀ s ∈ Icc 0 tf, ‖d s‖ = 1
  /-- Gimbal: thrust within `δ` of the body z-axis. -/
  gimbal : ∀ s ∈ Icc 0 tf, angle (d s) (A s ez) ≤ δ

/-- 6DOF landing set (no state constraints). -/
def landingSet6 (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) :
    Set (E3 × E3) :=
  {θ | ∃ a d A, a ∈ Acc ∧ Attitude6Admissible Att tf ω δ d A ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0}

/-- 6DOF state-constrained landing set. -/
def constrainedLandingSet6 (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ)
    (g : E3) (X : Set (E3 × E3)) : Set (E3 × E3) :=
  {θ | ∃ a d A, a ∈ Acc ∧ Attitude6Admissible Att tf ω δ d A ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position g θ.1 θ.2 a d t, velocity g θ.2 a d t) ∈ X}

/-- **Projection (Thm 6.2, kinematic):** the thrust axis of a 6DOF-admissible attitude is
M1-admissible. -/
theorem Attitude6Admissible.toM1 {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {tf ω δ : ℝ} {d : ℝ → E3}
    {A : ℝ → (E3 →ₗᵢ[ℝ] E3)} (h : Attitude6Admissible Att tf ω δ d A) :
    AttitudeAdmissible tf ω δ d (fun s => A s ez) where
  b_init := h.init
  b_unit s _ := by simp
  b_cont := h.cont ez
  b_rate s hs s' hs' := h.rate s hs s' hs' ez (by
    intro h0; have := norm_ez; rw [h0, norm_zero] at this; exact zero_ne_one this)
  d_meas := h.d_meas
  d_unit := h.d_unit
  gimbal := h.gimbal

theorem landingSet6_subset {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ}
    {g : E3} : landingSet6 Att Acc tf ω δ g ⊆ landingSet Acc tf ω δ g :=
  fun _ ⟨a, d, A, ha, hA, hr, hv⟩ => ⟨a, d, _, ha, hA.toM1, hr, hv⟩

theorem constrainedLandingSet6_subset {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {Acc : Set (ℝ → ℝ)}
    {tf ω δ : ℝ} {g : E3} {X : Set (E3 × E3)} :
    constrainedLandingSet6 Att Acc tf ω δ g X ⊆ landingSet Acc tf ω δ g :=
  fun _ ⟨a, d, A, ha, hA, hr, hv, _⟩ => ⟨a, d, _, ha, hA.toM1, hr, hv⟩

/-! ### Rotations about `e_y` -/

/-- The underlying map of the rotation about `e_y` by angle `φ`
(`e_z ↦ sin φ e_x + cos φ e_z`). -/
noncomputable def rotYfun (φ : ℝ) (x : E3) : E3 :=
  (Real.cos φ * x 0 + Real.sin φ * x 2) • ex + x 1 • ey +
    (-Real.sin φ * x 0 + Real.cos φ * x 2) • ez

theorem rotYfun_apply (φ : ℝ) (x : E3) :
    rotYfun φ x 0 = Real.cos φ * x 0 + Real.sin φ * x 2 ∧ rotYfun φ x 1 = x 1 ∧
      rotYfun φ x 2 = -Real.sin φ * x 0 + Real.cos φ * x 2 := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [rotYfun, ex, ey, ez]

/-- The rotation about `e_y` as a linear map. -/
noncomputable def rotYlin (φ : ℝ) : E3 →ₗ[ℝ] E3 where
  toFun := rotYfun φ
  map_add' x y := by simp only [rotYfun, PiLp.add_apply]; module
  map_smul' c x := by simp only [rotYfun, PiLp.smul_apply, smul_eq_mul, RingHom.id_apply]; module

theorem inner_rotYfun (φ ψ : ℝ) (x y : E3) : ⟪rotYfun φ x, rotYfun ψ y⟫ =
    x 1 * y 1 + Real.cos (φ - ψ) * (x 0 * y 0 + x 2 * y 2) +
      Real.sin (φ - ψ) * (x 2 * y 0 - x 0 * y 2) := by
  simp only [EuclideanSpace.inner_eq_star_dotProduct, rotYfun, ex, ey, ez]
  simp [Fin.sum_univ_three, dotProduct, Real.cos_sub, Real.sin_sub]
  ring

/-- Rotation about `e_y` by angle `φ`, as a linear isometry. -/
noncomputable def rotY (φ : ℝ) : E3 →ₗᵢ[ℝ] E3 :=
  (rotYlin φ).isometryOfInner fun x y => by
    change ⟪rotYfun φ x, rotYfun φ y⟫ = ⟪x, y⟫
    rw [inner_rotYfun, sub_self, Real.cos_zero, Real.sin_zero]
    simp only [EuclideanSpace.inner_eq_star_dotProduct]
    simp [Fin.sum_univ_three, dotProduct]
    ring

theorem rotY_apply (φ : ℝ) (x : E3) : rotY φ x = rotYfun φ x := rfl

theorem rotY_ez (φ : ℝ) : rotY φ ez = Real.sin φ • ex + Real.cos φ • ez := by
  simp [rotY_apply, rotYfun, ez]

theorem rotY_zero_ez : rotY 0 ez = ez := by simp [rotY_ez]

theorem norm_sq_coords (x : E3) : ‖x‖ ^ 2 = x 0 ^ 2 + x 1 ^ 2 + x 2 ^ 2 := by
  rw [EuclideanSpace.norm_sq_eq]; simp [Fin.sum_univ_three]

/-- A rotation about `e_y` by `φ - ψ` moves every vector by an angle at most `|φ - ψ|`. -/
theorem angle_rotY_le {φ ψ : ℝ} (hπ : |φ - ψ| ≤ π) {x : E3} (hx : x ≠ 0) :
    angle (rotY φ x) (rotY ψ x) ≤ |φ - ψ| := by
  have hn : 0 < ‖x‖ ^ 2 := by positivity
  unfold angle
  rw [LinearIsometry.norm_map, LinearIsometry.norm_map, rotY_apply, rotY_apply, inner_rotYfun]
  calc Real.arccos ((x 1 * x 1 + Real.cos (φ - ψ) * (x 0 * x 0 + x 2 * x 2) +
          Real.sin (φ - ψ) * (x 2 * x 0 - x 0 * x 2)) / (‖x‖ * ‖x‖))
      ≤ Real.arccos (Real.cos |φ - ψ|) := by
        apply Real.arccos_le_arccos
        rw [Real.cos_abs, le_div_iff₀ (by nlinarith), ← sq, norm_sq_coords]
        have := Real.cos_le_one (φ - ψ)
        nlinarith [sq_nonneg (x 1), mul_nonneg (sq_nonneg (x 1)) (sub_nonneg.2 this)]
    _ = |φ - ψ| := Real.arccos_cos (abs_nonneg _) hπ

theorem continuous_rotY_apply {φ : ℝ → ℝ} (hφ : Continuous φ) (x : E3) :
    Continuous fun s => rotY (φ s) x := by
  simp only [rotY_apply, rotYfun]; fun_prop

/-- The attitude class of proper rotations (`det = 1`). -/
def properAttitudes : Set (ℝ → (E3 →ₗᵢ[ℝ] E3)) :=
  {A | ∀ s, LinearMap.det (A s).toLinearMap = 1}

theorem det_rotY (φ : ℝ) : LinearMap.det (rotY φ).toLinearMap = 1 := by
  rw [← LinearMap.det_toMatrix (EuclideanSpace.basisFun (Fin 3) ℝ).toBasis, Matrix.det_fin_three]
  simp only [LinearMap.toMatrix_apply, OrthonormalBasis.coe_toBasis,
    OrthonormalBasis.coe_toBasis_repr, EuclideanSpace.basisFun_apply,
    EuclideanSpace.basisFun_repr]
  simp [rotY_apply, rotYfun, ex, ey, ez]
  nlinarith [Real.sin_sq_add_cos_sq φ]

/-- The rotation paths used as witnesses are proper rotations. -/
theorem rotY_path_mem_proper (f : ℝ → ℝ) : (fun s => rotY (f s)) ∈ properAttitudes :=
  fun s => det_rotY (f s)

/-! ### Lifting the witnesses -/

/-- 6DOF lift of an M1 witness whose body axis is `arcB ω (±e_x) (φ s)`-type: the attitude
`rotY (± ω φ(s))`. We state the lift for a general Lipschitz angle profile `φ` with
`|φ s - φ s'| ≤ |s - s'|` and `φ 0 = 0`. -/
theorem lift_admissible {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {tf ω δ : ℝ} {d : ℝ → E3}
    {φ : ℝ → ℝ} (σ : ℝ) (hσ : σ = 1 ∨ σ = -1) (hφc : Continuous φ) (hφ0 : φ 0 = 0)
    (hφL : ∀ s ∈ Icc 0 tf, ∀ s' ∈ Icc 0 tf, |φ s - φ s'| ≤ |s - s'|)
    (hφb : ∀ s ∈ Icc 0 tf, ∀ s' ∈ Icc 0 tf, ω * |φ s - φ s'| ≤ π) (hω : 0 ≤ ω)
    (hAtt : (fun s => rotY (σ * (ω * φ s))) ∈ Att)
    (hd : AttitudeAdmissible tf ω δ d (fun s => rotY (σ * (ω * φ s)) ez)) :
    Attitude6Admissible Att tf ω δ d (fun s => rotY (σ * (ω * φ s))) where
  mem := hAtt
  init := by simp [hφ0, rotY_zero_ez]
  cont x := (continuous_rotY_apply (by fun_prop) x).continuousOn
  rate s hs s' hs' x hx := by
    have habs : |σ * (ω * φ s) - σ * (ω * φ s')| = ω * |φ s - φ s'| := by
      rw [← mul_sub, ← mul_sub, abs_mul, abs_mul, abs_of_nonneg hω]
      rcases hσ with rfl | rfl <;> simp
    calc angle (rotY (σ * (ω * φ s)) x) (rotY (σ * (ω * φ s')) x)
        ≤ |σ * (ω * φ s) - σ * (ω * φ s')| := angle_rotY_le (by rw [habs]; exact hφb s hs s' hs') hx
      _ = ω * |φ s - φ s'| := habs
      _ ≤ ω * |s - s'| := mul_le_mul_of_nonneg_left (hφL s hs s' hs') hω
  d_meas := hd.d_meas
  d_unit := hd.d_unit
  gimbal := hd.gimbal

theorem rotY_ez_pm (σ x : ℝ) (hσ : σ = 1 ∨ σ = -1) :
    rotY (σ * x) ez = Real.sin x • (σ • ex) + Real.cos x • ez := by
  rcases hσ with rfl | rfl <;> simp [rotY_ez, Real.sin_neg, Real.cos_neg]

/-! ### Theorem B for 6DOF (no state constraints) -/

/-- The midpoint of the two extreme-arc landing data is not 5DOF-feasible. -/
theorem arc_midpoint_not_mem_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s) :
    (1 / 2 : ℝ) • landingData g a₁ (arcD ω δ ex) tf +
      (1 / 2 : ℝ) • landingData g a₁ (arcD ω δ (-ex)) tf ∉ landingSet Acc tf ω δ g := by
  rintro ⟨a, d, b, ha, hatt, -, hv⟩
  apply midpointM_not_mem_reachSet htf hω hδ hreg ha₁c ha₁p hAcc
  refine ⟨a, d, b, ha, hatt, ?_⟩
  have hm := midpoint_arcEndpoint (ω := ω) (δ := δ) ha₁c ex
  simp only [velocity, landingData, Prod.snd_add, Prod.smul_snd] at hv
  simp only [arcEndpoint] at hm
  rw [← hm]
  linear_combination (norm := module) -hv

/-- **Theorem B, 6DOF.** -/
theorem not_convex_landingSet6 {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {Acc : Set (ℝ → ℝ)}
    {tf ω δ : ℝ} {a₁ : ℝ → ℝ} (g : E3)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (ha₁c : ContinuousOn a₁ (Icc 0 tf)) (ha₁p : ∀ s ∈ Icc 0 tf, 0 < a₁ s)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s)
    (ha₁ : a₁ ∈ Acc)
    (hAtt : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) → (fun s => rotY (σ * (ω * s))) ∈ Att) :
    ¬ Convex ℝ (landingSet6 Att Acc tf ω δ g) := by
  have hωtf : ω * tf ≤ π := by linarith [Real.pi_pos]
  have hδπ : δ ≤ π := by nlinarith [Real.pi_pos]
  have mem : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      landingData g a₁ (arcD ω δ (σ • ex)) tf ∈ landingSet6 Att Acc tf ω δ g := by
    intro σ hσ
    have hu : ‖σ • ex‖ = 1 := by rcases hσ with rfl | rfl <;> simp
    have huz : ⟪σ • ex, ez⟫ = 0 := by rw [real_inner_smul_left, inner_ex_ez, mul_zero]
    have hd : AttitudeAdmissible tf ω δ (arcD ω δ (σ • ex))
        (fun s => rotY (σ * (ω * id s)) ez) := by
      have := arc_admissible (tf := tf) hu huz hω.le hδ hδπ hωtf
      convert this using 2 with s
      rw [rotY_ez_pm σ _ hσ]; rfl
    refine ⟨a₁, _, _, ha₁, lift_admissible (φ := id) σ hσ continuous_id rfl
      (fun s _ s' _ => le_rfl) (fun s hs s' hs' => ?_) hω.le (hAtt σ hσ) hd,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2⟩
    have : |s - s'| ≤ tf := by rw [abs_sub_le_iff]; constructor <;> linarith [hs.1, hs.2, hs'.1, hs'.2]
    simp only [id]; nlinarith [abs_nonneg (s - s')]
  have m1 := mem 1 (Or.inl rfl)
  have m2 := mem (-1) (Or.inr rfl)
  rw [one_smul] at m1
  rw [neg_one_smul] at m2
  exact not_convex_of_midpoint landingSet6_subset m1 m2
    (arc_midpoint_not_mem_landingSet g htf hω hδ hreg ha₁c ha₁p hAcc)

/-! ### Theorem B* for 6DOF (altitude / glide-slope constrained) -/

/-- **Theorem B\*, 6DOF.** -/
theorem not_convex_constrainedLandingSet6 {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))}
    {Acc : Set (ℝ → ℝ)} {tf ω δ sS amin amax g₀ tanγ : ℝ}
    (hsS : 0 < sS) (hsStf : sS < tf) (hω : 0 < ω) (hωs : ω * sS ≤ δ)
    (hreg : δ + ω * sS ≤ π / 2) (hamin : 0 < amin) (h : amin ≤ amax) (hg : g₀ ≤ amax)
    (htan : 0 ≤ tanγ)
    (hS : (amax + 2 * tanγ * amin) * sS ^ 2 ≤ (amax - g₀) * (tf - sS) ^ 2)
    (hAcc : ∀ a ∈ Acc, IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, amin ≤ a s ∧ a s ≤ amax)
    (haW : aW sS amin amax ∈ Acc) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (hAtt : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) → (fun s => rotY (σ * (ω * min s sS))) ∈ Att) :
    ¬ Convex ℝ (constrainedLandingSet6 Att Acc tf ω δ (-(g₀ • ez)) X) := by
  have hδ : 0 ≤ δ := le_trans (mul_nonneg hω.le hsS.le) hωs
  have hδπ : δ ≤ π := by linarith [Real.pi_pos, mul_nonneg hω.le hsS.le]
  have mem : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      landingData (-(g₀ • ez)) (aW sS amin amax) (dW ω δ sS (σ • ex)) tf ∈
        constrainedLandingSet6 Att Acc tf ω δ (-(g₀ • ez)) X := by
    intro σ hσ
    have hu : ‖σ • ex‖ = 1 := by rcases hσ with rfl | rfl <;> simp
    have huz : ⟪σ • ex, ez⟫ = 0 := by rw [real_inner_smul_left, inner_ex_ez, mul_zero]
    have hd : AttitudeAdmissible tf ω δ (dW ω δ sS (σ • ex))
        (fun s => rotY (σ * (ω * (fun s => min s sS) s)) ez) := by
      have := witness_admissible (tf := tf) hu huz hsS hω.le hδ hδπ hωs
      convert this using 2 with s
      rw [rotY_ez_pm σ _ hσ]; rfl
    refine ⟨_, _, _, haW, lift_admissible (φ := fun s => min s sS) σ hσ (by fun_prop)
      (min_eq_left hsS.le) (fun s _ s' _ => (abs_min_sub_min_le_max _ _ _ _).trans (by simp))
      (fun s hs s' hs' => ?_) hω.le (hAtt σ hσ) hd,
      (landingData_lands _ _ _ _).1, (landingData_lands _ _ _ _).2,
      fun t ht => hX (witness_mem_glideSlope hu huz hsS hsStf hω.le hδ hreg hamin h hg htan
        hS ht)⟩
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
    (witness_midpoint_not_mem_landingSet hsS hsStf hω hδ hreg hamin h hAcc)

end LcvxObstruction
