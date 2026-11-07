import LcvxObstruction.Sphere

/-!
# The 5DOF model M1 (kinematic, rate-limited thrust axis)

Time interval `[0, tf]`. Physical space `E3 = ℝ³` (Euclidean), `ez` the vertical unit vector.

Controls:
* `a : ℝ → ℝ` thrust-acceleration magnitude `T/m`, drawn from an admissible class `Acc`
  (e.g. `AccLower tf a₁`: integrable with `a ≥ a₁`; or `AccBox tf a₁ a₂`: `a₁ ≤ a ≤ a₂`;
  or the explicit mass-depletion class of `MassModel.lean`);
* `d : ℝ → E3` thrust direction, measurable, unit, within the gimbal cone
  `angle (d s) (b s) ≤ δ`;
* `b : ℝ → E3` body (thrust) axis, continuous, unit, `b 0 = ez`, slew-rate limited:
  `angle (b s) (b s') ≤ ω |s - s'|` (Lipschitz in the great-circle metric).

Dynamics `r̈ = a d + g` in integral form, boundary data `θ = (r₀, v₀)`, landing `r(tf) = v(tf) = 0`.
-/

open MeasureTheory Set InnerProductGeometry Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

/-- Physical 3-space `ℝ³` with the Euclidean inner product. -/
abbrev E3 := EuclideanSpace ℝ (Fin 3)

/-- The vertical (up) unit vector `e_z`. -/
noncomputable def ez : E3 := EuclideanSpace.single 2 1

/-- A horizontal unit vector `e_x`. -/
noncomputable def ex : E3 := EuclideanSpace.single 0 1

@[simp] theorem norm_ez : ‖ez‖ = 1 := by simp [ez]
@[simp] theorem norm_ex : ‖ex‖ = 1 := by simp [ex]
@[simp] theorem inner_ex_ez : ⟪ex, ez⟫ = 0 := by
  rw [ex, ez, EuclideanSpace.inner_single_left]; simp

/-- **Attitude/direction admissibility in model M1** on `[0, tf]` with slew-rate bound `ω` and
gimbal limit `δ`. -/
structure AttitudeAdmissible (tf ω δ : ℝ) (d b : ℝ → E3) : Prop where
  /-- Initial attitude is upright. -/
  b_init : b 0 = ez
  /-- The body axis is a unit vector. -/
  b_unit : ∀ s ∈ Icc 0 tf, ‖b s‖ = 1
  /-- The body axis is continuous (also implied by `b_rate`). -/
  b_cont : ContinuousOn b (Icc 0 tf)
  /-- Slew-rate limit: the body axis moves at angular rate at most `ω`. -/
  b_rate : ∀ s ∈ Icc 0 tf, ∀ s' ∈ Icc 0 tf, angle (b s) (b s') ≤ ω * |s - s'|
  /-- The thrust direction is (Lebesgue) measurable on `[0, tf]`. -/
  d_meas : AEStronglyMeasurable d (volume.restrict (Icc 0 tf))
  /-- The thrust direction is a unit vector. -/
  d_unit : ∀ s ∈ Icc 0 tf, ‖d s‖ = 1
  /-- Gimbal constraint: thrust within angle `δ` of the body axis. -/
  gimbal : ∀ s ∈ Icc 0 tf, angle (d s) (b s) ≤ δ

/-- Abstract acceleration class: integrable on `[0,tf]` and bounded below by `a₁`. -/
def AccLower (tf : ℝ) (a₁ : ℝ → ℝ) : Set (ℝ → ℝ) :=
  {a | IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s}

/-- Box acceleration class: integrable on `[0,tf]` with `a₁ ≤ a ≤ a₂`. -/
def AccBox (tf : ℝ) (a₁ a₂ : ℝ → ℝ) : Set (ℝ → ℝ) :=
  {a | IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, a₁ s ≤ a s ∧ a s ≤ a₂ s}

/-- **Velocity-increment (thrust-impulse) set** `R = {∫₀^tf a d : admissible}` for the
acceleration class `Acc`. -/
def reachSet (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) : Set E3 :=
  {w | ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b ∧ w = ∫ s in Icc 0 tf, a s • d s}

/-- Velocity at time `t` for gravity `g`, initial velocity `v₀`:
`v(t) = v₀ + t g + ∫₀ᵗ a(s) d(s) ds` (the solution of `v̇ = a d + g`). -/
noncomputable def velocity (g v₀ : E3) (a : ℝ → ℝ) (d : ℝ → E3) (t : ℝ) : E3 :=
  v₀ + t • g + ∫ s in Icc 0 t, a s • d s

/-- Position at time `t`: `r(t) = r₀ + t v₀ + (t²/2) g + ∫₀ᵗ (t - s) a(s) d(s) ds`
(Cauchy's formula for the solution of `r̈ = a d + g`, `r(0) = r₀`, `ṙ(0) = v₀`). -/
noncomputable def position (g r₀ v₀ : E3) (a : ℝ → ℝ) (d : ℝ → E3) (t : ℝ) : E3 :=
  r₀ + t • v₀ + (t ^ 2 / 2) • g + ∫ s in Icc 0 t, (t - s) • (a s • d s)

/-- **Landing feasibility set** `F_tf ⊆ ℝ³ × ℝ³` of boundary data `θ = (r₀, v₀)` from which an
admissible control achieves `r(tf) = 0`, `v(tf) = 0`. -/
def landingSet (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) : Set (E3 × E3) :=
  {θ | ∃ a d b, a ∈ Acc ∧ AttitudeAdmissible tf ω δ d b ∧
    position g θ.1 θ.2 a d tf = 0 ∧ velocity g θ.2 a d tf = 0}

/-! ### Basic consequences -/

theorem integrableOn_smul_of_unit {tf : ℝ} {a : ℝ → ℝ} {d : ℝ → E3}
    (ha : IntegrableOn a (Icc 0 tf)) (hd : AEStronglyMeasurable d (volume.restrict (Icc 0 tf)))
    (hu : ∀ s ∈ Icc 0 tf, ‖d s‖ = 1) : IntegrableOn (fun s => a s • d s) (Icc 0 tf) := by
  refine Integrable.mono' ha.norm (ha.aestronglyMeasurable.smul hd) ?_
  refine ae_restrict_of_forall_mem measurableSet_Icc fun s hs => ?_
  rw [norm_smul, hu s hs, mul_one]

theorem AttitudeAdmissible.inner_b_ez {tf ω δ : ℝ} {d b : ℝ → E3}
    (h : AttitudeAdmissible tf ω δ d b) {s : ℝ} (hs : s ∈ Icc 0 tf)
    (hπ : ω * s ≤ π) : Real.cos (ω * s) ≤ ⟪b s, ez⟫ := by
  have h0 : (0 : ℝ) ∈ Icc 0 tf := ⟨le_rfl, hs.1.trans hs.2⟩
  have := h.b_rate s hs 0 h0
  rw [sub_zero, abs_of_nonneg hs.1, h.b_init] at this
  exact cos_le_inner_of_angle_le (h.b_unit s hs) norm_ez this hπ

theorem AttitudeAdmissible.inner_d_ez {tf ω δ : ℝ} {d b : ℝ → E3}
    (h : AttitudeAdmissible tf ω δ d b) (hω : 0 ≤ ω) (hδ : 0 ≤ δ) {s : ℝ} (hs : s ∈ Icc 0 tf)
    (hπ : δ + ω * s ≤ π) : Real.cos (δ + ω * s) ≤ ⟪d s, ez⟫ := by
  have hb := h.inner_b_ez hs (by linarith)
  have hg := cos_le_inner_of_angle_le (h.d_unit s hs) (h.b_unit s hs) (h.gimbal s hs)
    (by nlinarith [hs.1])
  exact inner_triangle (h.d_unit s hs) (h.b_unit s hs) norm_ez hδ (mul_nonneg hω hs.1) hπ hg hb

/-! ### The projection of the landing set onto `v₀` -/

theorem integral_add_const {tf : ℝ} (htf : 0 ≤ tf) {f : ℝ → E3} (hf : IntegrableOn f (Icc 0 tf))
    (g : E3) : ∫ s in Icc 0 tf, (f s + g) = (∫ s in Icc 0 tf, f s) + tf • g := by
  rw [integral_add hf (integrableOn_const (by simp)), setIntegral_const,
    Real.volume_real_Icc_of_le htf, sub_zero]

/-- `proj_{v₀} F_tf = -tf • g - R`. -/
theorem snd_image_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} (g : E3) :
    Prod.snd '' landingSet Acc tf ω δ g = {v | ∃ w ∈ reachSet Acc tf ω δ, v = -w - tf • g} := by
  ext v
  constructor
  · rintro ⟨⟨r₀, v₀⟩, ⟨a, d, b, ha, hatt, -, hv⟩, rfl⟩
    refine ⟨∫ s in Icc 0 tf, a s • d s, ⟨a, d, b, ha, hatt, rfl⟩, ?_⟩
    simp only [velocity] at hv
    simp only
    rw [← sub_eq_zero, ← hv]
    abel
  · rintro ⟨w, ⟨a, d, b, ha, hatt, rfl⟩, rfl⟩
    set v₀ := -(∫ s in Icc 0 tf, a s • d s) - tf • g
    refine ⟨(-(tf • v₀ + (tf ^ 2 / 2) • g + ∫ s in Icc 0 tf, (tf - s) • (a s • d s)), v₀),
      ⟨a, d, b, ha, hatt, ?_, ?_⟩, rfl⟩
    · simp only [position]; abel
    · simp only [velocity, v₀]; abel

/-- If the landing set is convex then so is the reachable velocity-increment set `R`. -/
theorem convex_reachSet_of_convex_landingSet {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ}
    (g : E3) (hF : Convex ℝ (landingSet Acc tf ω δ g)) : Convex ℝ (reachSet Acc tf ω δ) := by
  have h1 := hF.linear_image (LinearMap.snd ℝ E3 E3)
  simp only [LinearMap.coe_snd] at h1
  rw [snd_image_landingSet g] at h1
  let f : E3 →ᵃ[ℝ] E3 :=
    { toFun := fun w => -w - tf • g
      linear := -LinearMap.id
      map_vadd' := by
        intro p v; simp only [vadd_eq_add, LinearMap.neg_apply, LinearMap.id_apply]; abel }
  have h2 := h1.affine_preimage f
  convert h2 using 1
  ext w
  simp only [mem_preimage]
  constructor
  · intro hw; exact ⟨w, hw, rfl⟩
  · rintro ⟨w', hw', he⟩
    have : w = w' := by
      have he' : -w - tf • g = -w' - tf • g := he
      simpa using he'
    rw [this]; exact hw'

end LcvxObstruction
