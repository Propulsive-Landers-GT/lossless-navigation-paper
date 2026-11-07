import LcvxObstruction.DiveBrake
import LcvxObstruction.TVC.Certificate
import LcvxObstruction.TVC.Pointwise

/-!
# Pure TVC: a concrete landing-set model for TVC-1 (math/06 §1, PT1–PT6, Lemmas 2.3–2.4)

This file replaces the abstract sets of `tvc1_main` by concrete pure-TVC landing sets and proves
the structural hypotheses that do not involve the hard analysis:

* Model (constant mass, `ω₃ ≡ 0`, unlimited gimbal rate; math/06 PT1–PT6). Controls are the body
  axis `b`, its rate `ḃ` and the thrust acceleration `u = T d / m`, in integral form:
  `b(t) = e_z + ∫₀ᵗ ḃ`, `ḃ(t) = ∫₀ᵗ (-(1/ε) Π_b u - ‖ḃ‖² b)` (this is `ε ∇ḃ = -Π_b u` with
  `b̈ = ∇ḃ - ‖ḃ‖² b`; math/06 Lemma 2.1), `‖b‖ = 1`, upright at rest at both ends
  (`b(0) = b(tf) = e_z`, `ḃ(0) = ḃ(tf) = 0`), and `u(s) ∈ C(b(s))`. Translation: `r̈ = u - g₀ e_z`
  (closed form `position`/`velocity` of `Model.lean` with `a ≡ 1`, `d = u`), landing
  `r(tf) = v(tf) = 0`, optional state constraint `X` along the trajectory.
* `ordinarySet` (`u = a d`, `a ∈ [a₁,a₂]`, unit `d`, `angle d b ≤ δ`) and `relaxedSet`
  (`⟪u,b⟫ ≥ a₁ cos δ`, `‖u‖ ≤ a₂`, `‖Π_b u‖ ≤ ⟪u,b⟫ tan δ`), `ordinarySet_subset_relaxedSet` (PT6).
* `tvcLandingSet C ε tf g₀ X`; `F^X` (ordinary, glide slope), `F` (ordinary, no state constraint),
  `F^rel` (relaxed, no state constraint): `tvcLandingSet_mono_X`, `tvcLandingSet_mono_C`.
* `rotPiE` (`R_π = 2⟪·,e_z⟫e_z - id`, a linear isometry of `ℝ³`) and `tvcLandingSet_rot`:
  the landing sets are `R_π`-invariant (math/06 Lemma 2.4), for any `R_π`-invariant control map
  and state constraint (both control maps and the glide-slope set are).
* `tvc_lambda_identity` (math/06 Lemma 2.3, translational part): `r₀ + s* v₀ = ∫ (s-s*) u + κ'`.
* `tvc1_model` (**Theorem TVC-1 for the concrete sets**): from a witness, the certificate
  `TVC1Certificate` (external exact numerics) and the analytic reduction `TVC1Reduction` stated
  for the concrete relaxed set, `F^X` is not convex and no uniform convex relaxation is lossless.
-/

open MeasureTheory Set InnerProductGeometry Real
open scoped RealInnerProductSpace

namespace LcvxObstruction.TVC

open LcvxObstruction

/-! ### Control sets -/

/-- Ordinary thrust accelerations for body axis `b`: `a d`, `a ∈ [a₁, a₂]`, unit `d` in the
gimbal cone. -/
def ordinarySet (a₁ a₂ δ : ℝ) (b : E3) : Set E3 :=
  {u | ∃ a d, a₁ ≤ a ∧ a ≤ a₂ ∧ ‖d‖ = 1 ∧ angle d b ≤ δ ∧ u = a • d}

/-- The convex relaxed set `𝒞(b)` (math/06 PT6). -/
def relaxedSet (a₁ a₂ δ : ℝ) (b : E3) : Set E3 :=
  {u | a₁ * Real.cos δ ≤ ⟪u, b⟫ ∧ ‖u‖ ≤ a₂ ∧ ‖u - ⟪u, b⟫ • b‖ ≤ ⟪u, b⟫ * Real.tan δ}

theorem ordinarySet_subset_relaxedSet {a₁ a₂ δ : ℝ} {b : E3} (hb : ‖b‖ = 1) (hδ : δ < π / 2)
    (ha₁ : 0 ≤ a₁) : ordinarySet a₁ a₂ δ b ⊆ relaxedSet a₁ a₂ δ b := by
  rintro u ⟨a, d, h1, h2, hd, hang, rfl⟩
  exact relaxed_contains_ordinary hb hd hang hδ h1 h2 ha₁

/-! ### Admissible controls and landing sets -/

/-- Admissible pure-TVC controls `(b, ḃ, u)` on `[0, tf]` for the control map `C`. -/
structure TVCAdmissible (C : E3 → Set E3) (ε tf : ℝ) (b bd u : ℝ → E3) : Prop where
  u_int : IntegrableOn u (Icc 0 tf)
  b_unit : ∀ s ∈ Icc 0 tf, ‖b s‖ = 1
  b_eq : ∀ t ∈ Icc 0 tf, b t = ez + ∫ s in Icc 0 t, bd s
  bd_eq : ∀ t ∈ Icc 0 tf, bd t =
    ∫ s in Icc 0 t, (-(ε⁻¹) • (u s - ⟪u s, b s⟫ • b s) - ⟪bd s, bd s⟫ • b s)
  bd_init : bd 0 = 0
  b_final : b tf = ez
  bd_final : bd tf = 0
  ctrl : ∀ s ∈ Icc 0 tf, u s ∈ C (b s)

/-- **Pure-TVC landing set** of boundary data `θ = (r₀, v₀)`: some admissible control lands at
`tf` (`r = v = 0`, upright at rest) keeping `(r, v) ∈ X`. Gravity `-g₀ e_z`; `r̈ = u - g₀ e_z`. -/
def tvcLandingSet (C : E3 → Set E3) (ε tf g₀ : ℝ) (X : Set (E3 × E3)) : Set (E3 × E3) :=
  {θ | ∃ b bd u, TVCAdmissible C ε tf b bd u ∧
    position (-(g₀ • ez)) θ.1 θ.2 (fun _ => 1) u tf = 0 ∧
    velocity (-(g₀ • ez)) θ.2 (fun _ => 1) u tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position (-(g₀ • ez)) θ.1 θ.2 (fun _ => 1) u t,
      velocity (-(g₀ • ez)) θ.2 (fun _ => 1) u t) ∈ X}

theorem tvcLandingSet_mono_X {C : E3 → Set E3} {ε tf g₀ : ℝ} {X X' : Set (E3 × E3)}
    (h : X ⊆ X') : tvcLandingSet C ε tf g₀ X ⊆ tvcLandingSet C ε tf g₀ X' :=
  fun _ ⟨b, bd, u, hadm, hr, hv, hX⟩ => ⟨b, bd, u, hadm, hr, hv, fun t ht => h (hX t ht)⟩

theorem tvcLandingSet_mono_C {C C' : E3 → Set E3} {ε tf g₀ : ℝ} {X : Set (E3 × E3)}
    (h : ∀ b : E3, ‖b‖ = 1 → C b ⊆ C' b) :
    tvcLandingSet C ε tf g₀ X ⊆ tvcLandingSet C' ε tf g₀ X :=
  fun _ ⟨b, bd, u, hadm, hr, hv, hX⟩ => ⟨b, bd, u,
    { hadm with ctrl := fun s hs => h _ (hadm.b_unit s hs) (hadm.ctrl s hs) }, hr, hv, hX⟩

/-! ### The rotation `R_π` -/

/-- `R_π x = 2⟪x, e_z⟫ e_z - x` (rotation by `π` about `e_z`). -/
noncomputable def rotPiL : E3 →ₗ[ℝ] E3 where
  toFun x := (2 * ⟪x, ez⟫) • ez - x
  map_add' x y := by simp only [inner_add_left]; module
  map_smul' c x := by simp only [real_inner_smul_left, RingHom.id_apply]; module

theorem inner_rotPiL_ez (x : E3) : ⟪rotPiL x, ez⟫ = ⟪x, ez⟫ := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  simp only [rotPiL, LinearMap.coe_mk, AddHom.coe_mk, inner_sub_left, real_inner_smul_left, hzz]
  ring

theorem rotPiL_invol (x : E3) : rotPiL (rotPiL x) = x := by
  have h := inner_rotPiL_ez x
  simp only [rotPiL, LinearMap.coe_mk, AddHom.coe_mk] at h ⊢
  rw [h]; module

theorem norm_rotPiL (x : E3) : ‖rotPiL x‖ = ‖x‖ := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  have : ‖rotPiL x‖ ^ 2 = ‖x‖ ^ 2 := by
    rw [← real_inner_self_eq_norm_sq, ← real_inner_self_eq_norm_sq]
    simp only [rotPiL, LinearMap.coe_mk, AddHom.coe_mk, inner_sub_left, inner_sub_right,
      real_inner_smul_left, real_inner_smul_right, hzz, real_inner_comm x ez]
    ring
  exact (pow_left_inj₀ (norm_nonneg _) (norm_nonneg _) two_ne_zero).mp this

/-- `R_π` as a linear isometry equivalence of `ℝ³`. -/
noncomputable def rotPiE : E3 ≃ₗᵢ[ℝ] E3 :=
  { LinearEquiv.ofInvolutive rotPiL (fun x => rotPiL_invol x) with
    norm_map' := norm_rotPiL }

theorem rotPiE_apply (x : E3) : rotPiE x = (2 * ⟪x, ez⟫) • ez - x := rfl

theorem rotPiE_ez : rotPiE ez = ez := by
  have hzz : ⟪ez, ez⟫ = 1 := by rw [real_inner_self_eq_norm_sq, norm_ez]; norm_num
  rw [rotPiE_apply, hzz]; module

theorem inner_rotPiE_ez (x : E3) : ⟪rotPiE x, ez⟫ = ⟪x, ez⟫ := inner_rotPiL_ez x

theorem rotPiE_invol (x : E3) : rotPiE (rotPiE x) = x := rotPiL_invol x

/-- Fixed points of `R_π`: exactly the vertical vectors (zero horizontal part). -/
theorem rotPiE_fixed_iff (x : E3) : rotPiE x = x ↔ x = ⟪x, ez⟫ • ez := by
  rw [rotPiE_apply]
  constructor
  · intro h
    linear_combination (norm := module) (-(1 / 2 : ℝ)) • h
  · intro h
    linear_combination (norm := module) (-2 : ℝ) • h

theorem rotPiE_integral {μ : Measure ℝ} (φ : ℝ → E3) :
    ∫ x, rotPiE (φ x) ∂μ = rotPiE (∫ x, φ x ∂μ) :=
  rotPiE.toLinearIsometry.integral_comp_comm φ

/-- `R_π` on boundary data. -/
noncomputable def rotPiE2 : E3 × E3 →ₗ[ℝ] E3 × E3 :=
  LinearMap.prodMap rotPiE.toLinearEquiv.toLinearMap rotPiE.toLinearEquiv.toLinearMap

@[simp] theorem rotPiE2_apply (θ : E3 × E3) : rotPiE2 θ = (rotPiE θ.1, rotPiE θ.2) := rfl

theorem rotPiE2_invol (θ : E3 × E3) : rotPiE2 (rotPiE2 θ) = θ := by
  simp only [rotPiE2_apply, rotPiE_invol]

/-! ### `R_π` invariance of the landing sets (math/06 Lemma 2.4) -/

theorem rot_position (g₀ : ℝ) (r₀ v₀ : E3) (u : ℝ → E3) (t : ℝ) :
    position (-(g₀ • ez)) (rotPiE r₀) (rotPiE v₀) (fun _ => 1) (fun s => rotPiE (u s)) t =
      rotPiE (position (-(g₀ • ez)) r₀ v₀ (fun _ => 1) u t) := by
  simp only [position, one_smul, map_add, map_smul, map_neg, rotPiE_ez]
  congr 1
  rw [← rotPiE_integral]
  congr 1; funext s; rw [map_smul]

theorem rot_velocity (g₀ : ℝ) (v₀ : E3) (u : ℝ → E3) (t : ℝ) :
    velocity (-(g₀ • ez)) (rotPiE v₀) (fun _ => 1) (fun s => rotPiE (u s)) t =
      rotPiE (velocity (-(g₀ • ez)) v₀ (fun _ => 1) u t) := by
  simp only [velocity, one_smul, map_add, map_smul, map_neg, rotPiE_ez]
  congr 1
  rw [← rotPiE_integral]

theorem glideSlopeSet_rot {tanγ : ℝ} {x : E3 × E3} (hx : x ∈ glideSlopeSet tanγ) :
    (rotPiE x.1, rotPiE x.2) ∈ glideSlopeSet tanγ := by
  simp only [glideSlopeSet, mem_ofPred_eq] at hx ⊢
  rw [inner_rotPiE_ez]
  refine ⟨hx.1, ?_⟩
  have : rotPiE x.1 - ⟪x.1, ez⟫ • ez = rotPiE (x.1 - ⟪x.1, ez⟫ • ez) := by
    rw [map_sub, map_smul, rotPiE_ez]
  rw [this, LinearIsometryEquiv.norm_map]
  exact hx.2

theorem ordinarySet_rot {a₁ a₂ δ : ℝ} {b u : E3} (h : u ∈ ordinarySet a₁ a₂ δ b) :
    rotPiE u ∈ ordinarySet a₁ a₂ δ (rotPiE b) := by
  obtain ⟨a, d, h1, h2, hd, hang, rfl⟩ := h
  refine ⟨a, rotPiE d, h1, h2, by rw [LinearIsometryEquiv.norm_map, hd], ?_, by rw [map_smul]⟩
  rw [show angle (rotPiE d) (rotPiE b) = angle d b from
    rotPiE.toLinearIsometry.angle_map d b]
  exact hang

theorem relaxedSet_rot {a₁ a₂ δ : ℝ} {b u : E3} (h : u ∈ relaxedSet a₁ a₂ δ b) :
    rotPiE u ∈ relaxedSet a₁ a₂ δ (rotPiE b) := by
  obtain ⟨h1, h2, h3⟩ := h
  have hin : ⟪rotPiE u, rotPiE b⟫ = ⟪u, b⟫ := LinearIsometryEquiv.inner_map_map _ _ _
  refine ⟨by rw [hin]; exact h1, by rw [LinearIsometryEquiv.norm_map]; exact h2, ?_⟩
  rw [hin, show rotPiE u - ⟪u, b⟫ • rotPiE b = rotPiE (u - ⟪u, b⟫ • b) by
    rw [map_sub, map_smul], LinearIsometryEquiv.norm_map]
  exact h3

/-- **`R_π` invariance of pure-TVC landing sets** (math/06 Lemma 2.4), for any control map and
state constraint that are `R_π`-invariant. -/
theorem tvcLandingSet_rot {C : E3 → Set E3} {ε tf g₀ : ℝ} {X : Set (E3 × E3)}
    (hC : ∀ b u, u ∈ C b → rotPiE u ∈ C (rotPiE b))
    (hX : ∀ x ∈ X, (rotPiE x.1, rotPiE x.2) ∈ X) {θ : E3 × E3}
    (hθ : θ ∈ tvcLandingSet C ε tf g₀ X) : rotPiE2 θ ∈ tvcLandingSet C ε tf g₀ X := by
  obtain ⟨b, bd, u, hadm, hr, hv, hXt⟩ := hθ
  refine ⟨fun s => rotPiE (b s), fun s => rotPiE (bd s), fun s => rotPiE (u s), ?_, ?_, ?_, ?_⟩
  · refine
      { u_int := ?_
        b_unit := fun s hs => by rw [LinearIsometryEquiv.norm_map]; exact hadm.b_unit s hs
        b_eq := fun t ht => by
          rw [hadm.b_eq t ht, map_add, rotPiE_ez, rotPiE_integral]
        bd_eq := fun t ht => by
          rw [hadm.bd_eq t ht, ← rotPiE_integral]
          congr 1; funext s
          simp only [LinearIsometryEquiv.inner_map_map, map_sub, map_smul]
        bd_init := by rw [hadm.bd_init, map_zero]
        b_final := by rw [hadm.b_final, rotPiE_ez]
        bd_final := by rw [hadm.bd_final, map_zero]
        ctrl := fun s hs => hC _ _ (hadm.ctrl s hs) }
    exact hadm.u_int.norm.mono'
      (rotPiE.continuous.comp_aestronglyMeasurable hadm.u_int.aestronglyMeasurable)
      (ae_of_all _ fun s => by rw [LinearIsometryEquiv.norm_map])
  · simp only [rotPiE2_apply]; rw [rot_position, hr, map_zero]
  · simp only [rotPiE2_apply]; rw [rot_velocity, hv, map_zero]
  · intro t ht
    simp only [rotPiE2_apply]
    rw [rot_position, rot_velocity]
    exact hX (position (-(g₀ • ez)) θ.1 θ.2 (fun _ => 1) u t,
      velocity (-(g₀ • ez)) θ.2 (fun _ => 1) u t) (hXt t ht)

/-! ### Landing identity (math/06 Lemma 2.3, translational part) -/

/-- If an admissible control lands from `θ`, then `r₀ + s* v₀ = ∫ (s - s*) u + (tf²/2 - s* tf) g`.
In particular `ℓ(θ) = ⟪r₀ + s* v₀, e_z⟫ = ∫ (s - s*) ⟪u, e_z⟫ + κ` with `κ = g₀ tf (s* - tf/2)`. -/
theorem tvc_lambda_identity {C : E3 → Set E3} {ε tf g₀ sS : ℝ} {X : Set (E3 × E3)}
    {θ : E3 × E3} (hθ : θ ∈ tvcLandingSet C ε tf g₀ X) :
    ∃ b bd u, TVCAdmissible C ε tf b bd u ∧
      θ.1 + sS • θ.2 = (∫ s in Icc 0 tf, (s - sS) • u s) + (tf ^ 2 / 2 - sS * tf) • -(g₀ • ez) := by
  obtain ⟨b, bd, u, hadm, hr, hv, -⟩ := hθ
  refine ⟨b, bd, u, hadm, ?_⟩
  have hf : IntegrableOn (fun s => (fun _ => (1 : ℝ)) s • u s) (Icc 0 tf) := by
    simpa using hadm.u_int
  have := lambda_identity (sS := sS) hf hr hv
  simpa using this

/-! ### TVC-1 for the concrete sets -/

/-- The face functional `ℓ(θ) = ⟪r₀ + s* v₀, e_z⟫` on `ℝ³ × ℝ³`. -/
noncomputable def ellE (sS : ℝ) : E3 × E3 →ₗ[ℝ] ℝ where
  toFun θ := ⟪θ.1 + sS • θ.2, ez⟫
  map_add' x y := by simp only [Prod.fst_add, Prod.snd_add, smul_add]; rw [← inner_add_left]; congr 1; abel
  map_smul' c x := by simp only [Prod.smul_fst, Prod.smul_snd, RingHom.id_apply, smul_eq_mul]; rw [← real_inner_smul_left]; congr 1; module

theorem ellE_rot (sS : ℝ) (θ : E3 × E3) : ellE sS (rotPiE2 θ) = ellE sS θ := by
  simp only [ellE, LinearMap.coe_mk, AddHom.coe_mk, rotPiE2_apply]
  rw [show rotPiE θ.1 + sS • rotPiE θ.2 = rotPiE (θ.1 + sS • θ.2) by rw [map_add, map_smul],
    inner_rotPiE_ez]

/-- Zero lateral data (`r_{0h} = v_{0h} = 0`) is exactly `R_π θ = θ`. -/
theorem rotPiE2_fixed_iff (θ : E3 × E3) :
    rotPiE2 θ = θ ↔ θ.1 = ⟪θ.1, ez⟫ • ez ∧ θ.2 = ⟪θ.2, ez⟫ • ez := by
  rw [← rotPiE_fixed_iff, ← rotPiE_fixed_iff, Prod.ext_iff]; simp

/-- **Theorem TVC-1 for the concrete pure-TVC landing sets.** Ordinary controls `ordinarySet`,
relaxed `relaxedSet` (`0 ≤ a₁`, `δ < π/2`), state constraint `X ⊇ glideSlopeSet tanγ` with
`X` `R_π`-invariant. Given a witness `θ_w ∈ F^X` with gain `ℓ(θ_w) - κ ≥ G_w`, the certified data
`C : TVC1Certificate` with `C.U < G_w` (external exact numerics), and the analytic reduction for the
concrete relaxed set (not formalized), `F^X` is not convex and no uniform convex relaxation (any
lifted space, any cost) is lossless for it. -/
theorem tvc1_model {a₁ a₂ δ ε tf g₀ sS κ : ℝ} {n K J : ℕ} {X : Set (E3 × E3)}
    (ha₁ : 0 ≤ a₁) (hδ : δ < π / 2) (hXrot : ∀ x ∈ X, (rotPiE x.1, rotPiE x.2) ∈ X)
    (C : TVC1Certificate n K J)
    (hred : TVC1Reduction C 2 (fun θ => ellE sS θ - κ)
      (tvcLandingSet (relaxedSet a₁ a₂ δ) ε tf g₀ univ) {θ | rotPiE2 θ = θ})
    {θw : E3 × E3} (hw : θw ∈ tvcLandingSet (ordinarySet a₁ a₂ δ) ε tf g₀ X) {Gw : ℝ}
    (hGw : Gw ≤ ellE sS θw - κ) (hmargin : C.U < Gw) :
    mid θw (rotPiE2 θw) ∉ tvcLandingSet (relaxedSet a₁ a₂ δ) ε tf g₀ univ ∧
      ¬ Convex ℝ (tvcLandingSet (ordinarySet a₁ a₂ δ) ε tf g₀ X) ∧
      ∀ (Y : Type*) [AddCommGroup Y] [Module ℝ Y] (R : UniformConvexRelaxation (E3 × E3) Y),
        ¬ R.IsLossless (tvcLandingSet (ordinarySet a₁ a₂ δ) ε tf g₀ X) ∧
          ∀ Jc, ¬ R.IsLosslessFor Jc (tvcLandingSet (ordinarySet a₁ a₂ δ) ε tf g₀ X) :=
  tvc1_skeleton (F := tvcLandingSet (ordinarySet a₁ a₂ δ) ε tf g₀ univ)
    (tvcLandingSet_mono_X (subset_univ X))
    (tvcLandingSet_mono_C fun _ hb => ordinarySet_subset_relaxedSet hb hδ ha₁)
    rotPiE2 (fun θ hθ => tvcLandingSet_rot (fun _ _ h => ordinarySet_rot h) hXrot hθ)
    rotPiE2_invol (ellE sS) κ (ellE_rot sS) hw hGw hmargin
    fun θ hθ hfix => gain_le_of_certificate C hred θ hθ hfix

/-- The glide-slope constraint is `R_π`-invariant, so `tvc1_model` applies with
`X = glideSlopeSet tanγ`. -/
theorem glideSlopeSet_rotInvariant (tanγ : ℝ) :
    ∀ x ∈ glideSlopeSet tanγ, (rotPiE x.1, rotPiE x.2) ∈ glideSlopeSet tanγ :=
  fun _ hx => glideSlopeSet_rot hx

end LcvxObstruction.TVC
