import Mathlib

/-!
# Solver claim N6: linear body-rate dynamics for an axisymmetric body without roll torque

Source: `solver/CLAIMS.md` row 5 (N6). Body rates `ω : Fin 3 → ℝ` (index 2 = roll axis, the
symmetry axis), inertia `J = diag(J_t, J_t, J_z)`, Euler's equation
`J ω̇ + ω × (J ω) = τ` with `×` = `⨯₃` (`crossProduct`).

* `gyro_roll_component` : the roll component of `ω × Jω` is `J_t ω₀ω₁ − J_t ω₁ω₀ = 0` for every
  `ω` (axisymmetry), so `J_z ω̇₂ = τ₂`.
* `gyro_vanish` : if `ω₂ = 0` then `ω × (J ω) = 0`.
* `euler_axisymmetric` (ODE consequence): if `τ₂ ≡ 0` and `ω₂(0) = 0` then `ω₂ ≡ 0`, the
  gyroscopic term vanishes identically, and `J_t ω̇_i = τ_i` (`i = 0, 1`) exactly.
* `euler_axisymmetric_integral` : with continuous torque, `ω_i(t) = ω_i(0) + J_t⁻¹ ∫₀ᵗ τ_i`
  (`i = 0, 1`), i.e. the body rate is an affine function of the torque profile and
  `ω(t_f) = 0` is a linear constraint.
-/

open Matrix

namespace LcvxSolver

/-- `J ω` for `J = diag(J_t, J_t, J_z)`. -/
def inertiaMul (Jt Jz : ℝ) (ω : Fin 3 → ℝ) : Fin 3 → ℝ := ![Jt * ω 0, Jt * ω 1, Jz * ω 2]

/-- The roll component of the gyroscopic term vanishes for every `ω` (axisymmetric body). -/
theorem gyro_roll_component (Jt Jz : ℝ) (ω : Fin 3 → ℝ) :
    (ω ⨯₃ inertiaMul Jt Jz ω) 2 = 0 := by
  simp [crossProduct, inertiaMul]; ring

/-- **N6, algebraic identity.** If `ω₂ = 0` then `ω × (J ω) = 0`. -/
theorem gyro_vanish (Jt Jz : ℝ) {ω : Fin 3 → ℝ} (hω : ω 2 = 0) :
    ω ⨯₃ inertiaMul Jt Jz ω = 0 := by
  ext i
  fin_cases i <;> simp [crossProduct, inertiaMul, hω] <;> ring

/-- **N6, ODE consequence.** Euler's equation `J ω̇ + ω × Jω = τ` for `J = diag(J_t,J_t,J_z)`,
`J_z ≠ 0`, with zero roll torque `τ₂ ≡ 0` and `ω₂(0) = 0`. Then `ω₂ ≡ 0`, `ω × Jω ≡ 0`, and
the transverse rates obey the linear equations `J_t ω̇₀ = τ₀`, `J_t ω̇₁ = τ₁`. -/
theorem euler_axisymmetric {Jt Jz : ℝ} (hJz : Jz ≠ 0) {ω dω τ : ℝ → Fin 3 → ℝ}
    (hω : ∀ t, HasDerivAt ω (dω t) t)
    (heuler : ∀ t, inertiaMul Jt Jz (dω t) + ω t ⨯₃ inertiaMul Jt Jz (ω t) = τ t)
    (hτ : ∀ t, τ t 2 = 0) (h0 : ω 0 2 = 0) :
    (∀ t, ω t 2 = 0) ∧ (∀ t, ω t ⨯₃ inertiaMul Jt Jz (ω t) = 0) ∧
      (∀ t, Jt * dω t 0 = τ t 0 ∧ Jt * dω t 1 = τ t 1) := by
  have hcomp : ∀ t i, HasDerivAt (fun s => ω s i) (dω t i) t :=
    fun t i => hasDerivAt_pi.mp (hω t) i
  -- roll rate derivative is zero
  have hd2 : ∀ t, dω t 2 = 0 := by
    intro t
    have h := congrFun (heuler t) 2
    rw [Pi.add_apply, gyro_roll_component, hτ t] at h
    simp [inertiaMul] at h
    rcases h with h | h
    · exact absurd h hJz
    · exact h
  have hconst : ∀ t, ω t 2 = ω 0 2 := by
    intro t
    have hdiff : Differentiable ℝ (fun s => ω s 2) :=
      fun s => (hcomp s 2).differentiableAt
    exact is_const_of_deriv_eq_zero hdiff (fun s => by rw [(hcomp s 2).deriv, hd2 s]) t 0
  have hroll : ∀ t, ω t 2 = 0 := fun t => (hconst t).trans h0
  have hgyro : ∀ t, ω t ⨯₃ inertiaMul Jt Jz (ω t) = 0 := fun t => gyro_vanish Jt Jz (hroll t)
  refine ⟨hroll, hgyro, fun t => ⟨?_, ?_⟩⟩
  · have h := congrFun (heuler t) 0
    rw [Pi.add_apply, hgyro t] at h
    simpa [inertiaMul] using h
  · have h := congrFun (heuler t) 1
    rw [Pi.add_apply, hgyro t] at h
    simpa [inertiaMul] using h

/-- **N6, closed form.** Under the hypotheses of `euler_axisymmetric`, with `J_t ≠ 0` and
continuous transverse torque, `ω_i(t) = ω_i(0) + J_t⁻¹ ∫₀ᵗ τ_i` for `i = 0, 1`: the body rate is
affine in the torque (equivalently, in the angular-acceleration profile `τ/J_t`). -/
theorem euler_axisymmetric_integral {Jt Jz : ℝ} (hJt : Jt ≠ 0) (hJz : Jz ≠ 0)
    {ω dω τ : ℝ → Fin 3 → ℝ} (hω : ∀ t, HasDerivAt ω (dω t) t)
    (heuler : ∀ t, inertiaMul Jt Jz (dω t) + ω t ⨯₃ inertiaMul Jt Jz (ω t) = τ t)
    (hτ : ∀ t, τ t 2 = 0) (h0 : ω 0 2 = 0) (i : Fin 3) (hi : i = 0 ∨ i = 1)
    (hτc : Continuous fun t => τ t i) (t : ℝ) :
    ω t i = ω 0 i + Jt⁻¹ * ∫ s in (0 : ℝ)..t, τ s i := by
  obtain ⟨-, -, hlin⟩ := euler_axisymmetric hJz hω heuler hτ h0
  have hdi : ∀ s, dω s i = Jt⁻¹ * τ s i := by
    intro s
    rcases hi with rfl | rfl
    · rw [← (hlin s).1]; field_simp
    · rw [← (hlin s).2]; field_simp
  have hderiv : ∀ s ∈ Set.uIcc (0 : ℝ) t, HasDerivAt (fun s => ω s i) (Jt⁻¹ * τ s i) s := by
    intro s _
    rw [← hdi s]
    exact hasDerivAt_pi.mp (hω s) i
  have hint : IntervalIntegrable (fun s => Jt⁻¹ * τ s i) MeasureTheory.volume 0 t :=
    (continuous_const.mul hτc).intervalIntegrable 0 t
  have := intervalIntegral.integral_eq_sub_of_hasDerivAt hderiv hint
  rw [intervalIntegral.integral_const_mul] at this
  linarith

end LcvxSolver
