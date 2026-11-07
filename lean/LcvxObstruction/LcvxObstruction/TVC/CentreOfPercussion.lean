import Mathlib

/-!
# Pure TVC: the centre-of-percussion identity (claim FLAT; math/06 Lemma 2.1, math/02 Lemma 6.4)

Rigid axisymmetric body, inertia `J = diag(J_t, J_t, J_a)` in body axes, symmetry (thrust) axis
`b` (unit), engine pivot at `-L b` from the centre of mass, thrust force `T = T_a b + T_⊥` with
`T_⊥ ⊥ b`, gravity `-g` (so `g = g₀ e_z` points up). Constant mass `m`, constant `J_t, J_a, L`;
`ε := J_t / (m L)` is the distance from the centre of mass to the centre of percussion.

All statements are **pointwise algebraic identities** at one instant: the kinematic and dynamic
relations (`ḃ = ω × b`, `b̈ = ω̇ × b + ω × ḃ`, Newton, Euler) enter as hypotheses relating the
vectors `b, ḃ, b̈, ω, ω̇, r̈, T` at that instant. Applied at every `t` they give the ODE identity.
Vectors live in `Fin 3 → ℝ` with Mathlib's `crossProduct` (`⨯₃`) and `dotProduct` (`⬝ᵥ`), the
convention of `Positive/TVC.lean` and `Solver/Gyro.lean`; `EuclideanSpace ℝ (Fin 3)` has the same
underlying functions and the same inner product (`⟪x, y⟫ = y ⬝ᵥ x`).

* `cop_identity` (**FLAT, zero roll rate**): if `ω ⬝ b = 0`, `b̈ = ω̇ × b + ω × (ω × b)`,
  `J_t ω̇ = (-L b) × T` (Euler for axisymmetric `J` with `ω₃ = 0`) and `m r̈ = T - m g`, then
  `y = r + ε b` satisfies `ÿ = (T_a/m - ε ‖ω‖²) b - g`.
  (`T_a = T cos μ`, `μ` the gimbal angle.) The lateral thrust drops out entirely.
* `cop_identity_roll` (**with roll rate** `ω₃ = ω ⬝ b`): with the inertial-frame Euler equation
  `d/dt (J ω) = τ`, i.e. `J_t ω̇ + (J_a - J_t)(ω̇₃ b + ω₃ ḃ) = (-L b) × T`, one gets
  `ÿ = (T_a/m - ε ‖ḃ‖²) b + ε (J_a/J_t) ω₃ (b × ḃ) - g` (math/06 Lemma 2.1, the gyroscopic term
  `γ₃`).
* `euler_roll_const`: under the same Euler equation the roll rate is conserved (`J_a ω̇₃ = 0`),
  so `ω₃(0) = 0` gives `ω₃ ≡ 0` (assumption R0 needs no roll control).
* `hasDerivAt_cop`, `cop_boundary`, `tvcSet_eq_preimage_translate`, `convex_tvcSet_iff`: the
  boundary-data map `(r₀, v₀) ↦ (r₀ + ε b₀, v₀ + ε ω₀ × b₀)` is a translation (for the fixed
  initial attitude `b₀` and rate `ω₀`), so the pure-TVC feasible set is a translate of the
  feasible set written in the `y` variables, and convexity transfers both ways.
-/

open Matrix

namespace LcvxObstruction.TVC

/-- Vectors of `ℝ³` as plain coordinate functions. -/
abbrev V3 := Fin 3 → ℝ

/-- `ω × (ω × b) = (ω ⬝ b) ω - ‖ω‖² b`. -/
theorem cross_cross_self (ω b : V3) : ω ⨯₃ (ω ⨯₃ b) = (ω ⬝ᵥ b) • ω - (ω ⬝ᵥ ω) • b := by
  rw [cross_cross_eq_smul_sub_smul']

/-- `(b × T) × b = T - (b ⬝ T) b` for a unit vector `b`. -/
theorem cross_cross_unit (b T : V3) (hb : b ⬝ᵥ b = 1) : (b ⨯₃ T) ⨯₃ b = T - (b ⬝ᵥ T) • b := by
  rw [cross_cross_eq_smul_sub_smul, hb, one_smul, dotProduct_comm T b]

/-- The torque term: `((-L b) × T) × b = -L T_⊥` when `T = T_a b + T_⊥`, `T_⊥ ⊥ b`, `‖b‖ = 1`. -/
theorem cross_cross_lateral {b T Tp : V3} {Ta : ℝ} (hb : b ⬝ᵥ b = 1) (hTp : b ⬝ᵥ Tp = 0)
    (hT : T = Ta • b + Tp) : (b ⨯₃ T) ⨯₃ b = Tp := by
  have hbT : b ⬝ᵥ T = Ta := by
    rw [hT, dotProduct_add, dotProduct_smul, hb, hTp, smul_eq_mul, mul_one, add_zero]
  rw [cross_cross_unit b T hb, hbT, hT]; abel

theorem torque_cross_b {b T Tp : V3} {L Ta : ℝ} (hb : b ⬝ᵥ b = 1) (hTp : b ⬝ᵥ Tp = 0)
    (hT : T = Ta • b + Tp) : ((-L) • b ⨯₃ T) ⨯₃ b = (-L) • Tp := by
  simp only [map_smul, LinearMap.smul_apply, cross_cross_lateral hb hTp hT]

/-- Newton: `m r̈ = T - m g` gives `r̈ = m⁻¹ T - g`. -/
theorem newton_solve {m : ℝ} {rdd T g : V3} (hm : m ≠ 0) (h : m • rdd = T - m • g) :
    rdd = m⁻¹ • T - g := by
  have : rdd = m⁻¹ • (m • rdd) := by rw [smul_smul, inv_mul_cancel₀ hm, one_smul]
  rw [this, h, smul_sub, smul_smul, inv_mul_cancel₀ hm, one_smul]

/-- **Centre-of-percussion identity (FLAT), zero roll rate.**
Axisymmetric rigid body, `ω ⊥ b`, engine at `-L b`, thrust `T = T_a b + T_⊥` (`T_⊥ ⊥ b`),
`ε = J_t/(m L)`. Then `y = r + ε b` satisfies `ÿ = (T_a/m - ε ‖ω‖²) b - g`. -/
theorem cop_identity {m L Jt Ta : ℝ} {b ω ωd bdd rdd T Tp g : V3}
    (hm : m ≠ 0) (hL : L ≠ 0) (hb : b ⬝ᵥ b = 1) (hωb : ω ⬝ᵥ b = 0)
    (hT : T = Ta • b + Tp) (hTp : b ⬝ᵥ Tp = 0)
    (hbdd : bdd = ωd ⨯₃ b + ω ⨯₃ (ω ⨯₃ b))
    (hEuler : Jt • ωd = (-L) • b ⨯₃ T)
    (hNewton : m • rdd = T - m • g) :
    rdd + (Jt / (m * L)) • bdd = (Ta / m - Jt / (m * L) * (ω ⬝ᵥ ω)) • b - g := by
  have hc : (Jt / (m * L)) • (ωd ⨯₃ b) = (-m⁻¹) • Tp := by
    have e1 : (Jt / (m * L)) • (ωd ⨯₃ b) = (m * L)⁻¹ • ((Jt • ωd) ⨯₃ b) := by
      simp only [map_smul, LinearMap.smul_apply, smul_smul]; congr 1; ring
    rw [e1, hEuler, torque_cross_b hb hTp hT, smul_smul]
    congr 1; field_simp
  have hw : ω ⨯₃ (ω ⨯₃ b) = (-(ω ⬝ᵥ ω)) • b := by
    rw [cross_cross_self, hωb, zero_smul, zero_sub, neg_smul]
  rw [newton_solve hm hNewton, hbdd, smul_add, hc, hw, hT]
  module

/-- Roll-rate conservation: from the inertial Euler equation of an axisymmetric body with
torque `⊥ b`, `J_a ω̇₃ = 0` where `ω̇₃ = d/dt (ω ⬝ b) = ω̇ ⬝ b + ω ⬝ ḃ`. -/
theorem euler_roll_const {L Jt Ja ω3d : ℝ} {b bd ω ωd T : V3}
    (hb : b ⬝ᵥ b = 1) (hbd : bd = ω ⨯₃ b) (hω3d : ω3d = ωd ⬝ᵥ b + ω ⬝ᵥ bd)
    (hEuler : Jt • ωd + (Ja - Jt) • (ω3d • b + (ω ⬝ᵥ b) • bd) = (-L) • b ⨯₃ T) :
    Ja * ω3d = 0 := by
  have hbbd : b ⬝ᵥ bd = 0 := by rw [hbd, dot_cross_self]
  have hωbd : ω ⬝ᵥ bd = 0 := by rw [hbd, dot_self_cross]
  have h := congrArg (fun v => b ⬝ᵥ v) hEuler
  simp only [dotProduct_add, dotProduct_smul, smul_eq_mul, hb, hbbd, dot_self_cross] at h
  rw [dotProduct_comm] at h
  rw [hω3d, hωbd, add_zero] at h ⊢
  linarith

/-- **Centre-of-percussion identity with roll rate** (math/06 Lemma 2.1).
`ω₃ := ω ⬝ b` arbitrary. With `ḃ = ω × b`, `b̈ = ω̇ × b + ω × ḃ`, the inertial-frame Euler equation
`J_t ω̇ + (J_a - J_t)(ω̇₃ b + ω₃ ḃ) = (-L b) × T` (`d/dt(Jω)`, `Jω = J_t ω + (J_a-J_t) ω₃ b`), and
Newton, `y = r + ε b` satisfies
`ÿ = (T_a/m - ε ‖ḃ‖²) b + ε (J_a/J_t) ω₃ (b × ḃ) - g`. -/
theorem cop_identity_roll {m L Jt Ja Ta ω3d : ℝ} {b bd ω ωd bdd rdd T Tp g : V3}
    (hm : m ≠ 0) (hL : L ≠ 0) (hJt : Jt ≠ 0) (hb : b ⬝ᵥ b = 1)
    (hT : T = Ta • b + Tp) (hTp : b ⬝ᵥ Tp = 0)
    (hbd : bd = ω ⨯₃ b) (hbdd : bdd = ωd ⨯₃ b + ω ⨯₃ bd)
    (hEuler : Jt • ωd + (Ja - Jt) • (ω3d • b + (ω ⬝ᵥ b) • bd) = (-L) • b ⨯₃ T)
    (hNewton : m • rdd = T - m • g) :
    rdd + (Jt / (m * L)) • bdd =
      (Ta / m - Jt / (m * L) * (bd ⬝ᵥ bd)) • b
        + (Jt / (m * L) * (Ja / Jt) * (ω ⬝ᵥ b)) • (b ⨯₃ bd) - g := by
  set ω3 := ω ⬝ᵥ b with hω3
  -- `b × ḃ = ω - ω₃ b`, `ḃ × b = -(b × ḃ)`
  have hbxbd : b ⨯₃ bd = ω - ω3 • b := by
    rw [hbd, cross_cross_eq_smul_sub_smul', hb, one_smul]
  have hbdxb : bd ⨯₃ b = -(b ⨯₃ bd) := by rw [cross_anticomm]
  -- `‖ḃ‖² = ‖ω‖² - ω₃²`
  have hbdbd : bd ⬝ᵥ bd = ω ⬝ᵥ ω - ω3 ^ 2 := by
    -- direct: ‖ω × b‖² = ‖ω‖²‖b‖² - (ω⬝b)²
    rw [hbd]
    have := cross_dot_cross ω b ω b
    rw [this, hb, dotProduct_comm b ω, hω3]; ring
  -- `ω × ḃ = ω₃ (b × ḃ) - ‖ḃ‖² b`
  have hωbd : ω ⨯₃ bd = ω3 • (b ⨯₃ bd) - (bd ⬝ᵥ bd) • b := by
    rw [hbdbd, hbxbd, hbd, cross_cross_self]
    try rw [← hω3]
    module
  -- `J_t (ω̇ × b) = -L T_⊥ + (J_a - J_t) ω₃ (b × ḃ)`
  have hJ : Jt • (ωd ⨯₃ b) = (-L) • Tp + ((Ja - Jt) * ω3) • (b ⨯₃ bd) := by
    have e := congrArg (fun v => v ⨯₃ b) hEuler
    simp only [map_add, map_smul, LinearMap.add_apply, LinearMap.smul_apply, cross_self,
      smul_zero, zero_add] at e
    rw [cross_cross_lateral hb hTp hT, hbdxb] at e
    rw [← e]; module
  have hc : (Jt / (m * L)) • (ωd ⨯₃ b) =
      (-m⁻¹) • Tp + ((Ja - Jt) * ω3 / (m * L)) • (b ⨯₃ bd) := by
    have e1 : (Jt / (m * L)) • (ωd ⨯₃ b) = (m * L)⁻¹ • (Jt • (ωd ⨯₃ b)) := by
      rw [smul_smul]; congr 1; ring
    rw [e1, hJ, smul_add, smul_smul, smul_smul]
    congr 2
    · field_simp
    · ring
  rw [newton_solve hm hNewton, hbdd, smul_add, hc, hωbd, hT]
  have hJa : Jt / (m * L) * (Ja / Jt) = Ja / (m * L) := by field_simp
  rw [hJa]
  rw [smul_sub, smul_smul, smul_smul]
  have : (Ja - Jt) * ω3 / (m * L) + Jt / (m * L) * ω3 = Ja / (m * L) * ω3 := by ring
  module

/-! ### The same identity stated in `EuclideanSpace ℝ (Fin 3)` -/

section Euclidean

open scoped RealInnerProductSpace

/-- Cross product on `EuclideanSpace ℝ (Fin 3)`, transported from `⨯₃` on coordinates. -/
noncomputable def cross3 (x y : EuclideanSpace ℝ (Fin 3)) : EuclideanSpace ℝ (Fin 3) :=
  WithLp.toLp 2 (WithLp.ofLp x ⨯₃ WithLp.ofLp y)

theorem inner_eq_dot (x y : EuclideanSpace ℝ (Fin 3)) :
    ⟪x, y⟫ = WithLp.ofLp x ⬝ᵥ WithLp.ofLp y := by
  rw [EuclideanSpace.inner_eq_star_dotProduct, star_trivial, dotProduct_comm]

/-- **FLAT in `EuclideanSpace ℝ (Fin 3)`** (same content as `cop_identity`):
`‖b‖ = 1`, `⟪ω, b⟫ = 0`, `T = T_a b + T_⊥`, `⟪b, T_⊥⟫ = 0`, `b̈ = ω̇ × b + ω × (ω × b)`,
`J_t ω̇ = (-L b) × T`, `m r̈ = T - m g` give
`r̈ + ε b̈ = (T_a/m - ε ‖ω‖²) b - g` with `ε = J_t/(m L)`. -/
theorem cop_identity_E3 {m L Jt Ta : ℝ} {b ω ωd bdd rdd T Tp g : EuclideanSpace ℝ (Fin 3)}
    (hm : m ≠ 0) (hL : L ≠ 0) (hb : ‖b‖ = 1) (hωb : ⟪ω, b⟫ = 0)
    (hT : T = Ta • b + Tp) (hTp : ⟪b, Tp⟫ = 0)
    (hbdd : bdd = cross3 ωd b + cross3 ω (cross3 ω b))
    (hEuler : Jt • ωd = cross3 ((-L) • b) T)
    (hNewton : m • rdd = T - m • g) :
    rdd + (Jt / (m * L)) • bdd = (Ta / m - Jt / (m * L) * ‖ω‖ ^ 2) • b - g := by
  apply (WithLp.equiv 2 (Fin 3 → ℝ)).injective
  have hb' : WithLp.ofLp b ⬝ᵥ WithLp.ofLp b = 1 := by
    rw [← inner_eq_dot, real_inner_self_eq_norm_sq, hb, one_pow]
  have hω2 : ‖ω‖ ^ 2 = WithLp.ofLp ω ⬝ᵥ WithLp.ofLp ω := by
    rw [← inner_eq_dot, real_inner_self_eq_norm_sq]
  rw [inner_eq_dot] at hωb hTp
  have h := cop_identity (m := m) (L := L) (Jt := Jt) (Ta := Ta) (b := WithLp.ofLp b)
    (ω := WithLp.ofLp ω) (ωd := WithLp.ofLp ωd) (bdd := WithLp.ofLp bdd)
    (rdd := WithLp.ofLp rdd) (T := WithLp.ofLp T) (Tp := WithLp.ofLp Tp) (g := WithLp.ofLp g)
    hm hL hb' hωb (by rw [hT]; rfl) hTp (by rw [hbdd]; rfl)
    (by rw [← WithLp.ofLp_smul, hEuler]; simp [cross3]) (by rw [← WithLp.ofLp_smul, hNewton]; rfl)
  rw [hω2]
  simpa using h

end Euclidean

/-! ### Boundary data: the change of variables is a translation -/

/-- If `r' = v` and `b' = ω × b`, then `y = r + ε b` has `y' = v + ε (ω × b)`. -/
theorem hasDerivAt_cop {r b : ℝ → V3} {v ω : V3} {t ε : ℝ}
    (hr : HasDerivAt r v t) (hb : HasDerivAt b (ω ⨯₃ b t) t) :
    HasDerivAt (fun s => r s + ε • b s) (v + ε • (ω ⨯₃ b t)) t :=
  hr.add (hb.const_smul ε)

/-- The boundary-data map `(r, v) ↦ (r + ε b₀, v + ε ω₀ × b₀)` for fixed attitude data `(b₀, ω₀)`:
a translation of `ℝ³ × ℝ³`. -/
def copShift (ε : ℝ) (b₀ ω₀ : V3) : V3 × V3 := (ε • b₀, ε • (ω₀ ⨯₃ b₀))

theorem cop_boundary (ε : ℝ) (b₀ ω₀ r₀ v₀ : V3) :
    (r₀ + ε • b₀, v₀ + ε • (ω₀ ⨯₃ b₀)) = (r₀, v₀) + copShift ε b₀ ω₀ := rfl

/-- Terminal conditions translate as well: at rest upright (`b = b_f`, `ω = 0`),
`r = 0 ∧ v = 0` iff `y = ε b_f ∧ ẏ = 0`. -/
theorem cop_terminal (ε : ℝ) (bf r v : V3) :
    (r + ε • bf = ε • bf ∧ v + ε • ((0 : V3) ⨯₃ bf) = 0) ↔ (r = 0 ∧ v = 0) := by
  simp

/-- **`F_TVC` is a translate of `F_y`.** If a boundary datum `θ = (r₀, v₀)` is feasible for the
TVC problem exactly when its image `θ + copShift ε b₀ ω₀` is feasible for the problem written in
the centre-of-percussion variables (this is what `cop_identity` / `cop_identity_roll` and
`cop_boundary`, `cop_terminal` give, with the attitude boundary data fixed), then
`F_TVC = (· + shift)⁻¹' F_y`. -/
theorem tvcSet_eq_preimage_translate {FT Fy : Set (V3 × V3)} {ε : ℝ} {b₀ ω₀ : V3}
    (h : ∀ θ, θ ∈ FT ↔ θ + copShift ε b₀ ω₀ ∈ Fy) :
    FT = (fun θ => θ + copShift ε b₀ ω₀) ⁻¹' Fy :=
  Set.ext h

/-- Convexity is invariant under the translation: `F_TVC` convex iff `F_y` convex. -/
theorem convex_tvcSet_iff {FT Fy : Set (V3 × V3)} {ε : ℝ} {b₀ ω₀ : V3}
    (h : ∀ θ, θ ∈ FT ↔ θ + copShift ε b₀ ω₀ ∈ Fy) : Convex ℝ FT ↔ Convex ℝ Fy := by
  set c := copShift ε b₀ ω₀
  have hFy : Fy = (fun θ => θ + -c) ⁻¹' FT := by
    ext θ; simp [h]
  constructor
  · intro hc; rw [hFy]; exact hc.translate_preimage_left (-c)
  · intro hc; rw [tvcSet_eq_preimage_translate h]; exact hc.translate_preimage_left c

end LcvxObstruction.TVC
