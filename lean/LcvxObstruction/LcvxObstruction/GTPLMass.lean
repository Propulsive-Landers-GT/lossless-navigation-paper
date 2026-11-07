import LcvxObstruction.FreeTimeBStar

/-!
# Theorem B* with mass depletion instantiated at GTPL wet constants

Constants (`context/vehicle.md` §1, §2): thrust `ρ₁ = 400 N`, `ρ₂ = 1000 N`, wet mass
`m₀ = 79.88 kg`, dry mass `m_dry = 55.88 kg`, `α = 1/(9.81 · 180)` kg/(N s) (Isp = 180 s, the value
used by the guidance code), gravity `g₀ = 9.81 m/s²`, gimbal cone `δ = 15° = π/12`.
The full-throttle burn condition `m_dry ≤ m₀ − αρ₂ t_f` holds for every `t_f ≤ 42 s`.

* `gtpl_no_lossless_upright_6dof_mass`: for every horizon `0 < t_f ≤ 42 s`, every slew-rate bound
  `ω > 0`, every glide slope `tanγ ≥ 0` and every state constraint `X ⊇ glideSlopeSet tanγ`, no
  uniform convex relaxation is lossless for the kinematic 6DOF (proper rotations, any roll),
  upright-landing, altitude/glide-slope constrained landing set with explicit mass depletion.
* `gtpl_no_lossless_freeTime_mass`: the same conclusion (5DOF) for free final time on any window
  `[t_a, t_b]` with `0 < t_a ≤ t_b ≤ 42 s`.

(The Cardan box `±15°` contains the 15° cone; the cone model is the one formalized here.)
-/

open MeasureTheory Set Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

theorem gtpl_burn {tf : ℝ} (htf : tf ≤ 42) :
    (55.88 : ℝ) ≤ 79.88 - 1 / (9.81 * 180) * 1000 * tf := by
  have : 1 / (9.81 * 180) * 1000 * tf ≤ 1 / (9.81 * 180) * 1000 * 42 :=
    mul_le_mul_of_nonneg_left htf (by norm_num)
  have h2 : 1 / (9.81 * 180) * 1000 * (42 : ℝ) ≤ 24 := by norm_num
  linarith

theorem gtpl_twr : (9.81 : ℝ) < 1000 / 79.88 := by norm_num

theorem gtpl_delta : 0 < π / 12 ∧ π / 12 < π / 2 := by
  constructor <;> linarith [Real.pi_pos]

/-- **GTPL, kinematic 6DOF, upright landing, altitude/glide slope, explicit mass depletion.** -/
theorem gtpl_no_lossless_upright_6dof_mass {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {tf ω tanγ : ℝ} (htf : 0 < tf) (htf42 : tf ≤ 42) (hω : 0 < ω) (htan : 0 ≤ tanγ)
    {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (constrainedLandingSet6Up properAttitudes
      (AccMass 400 1000 (1 / (9.81 * 180)) 79.88 55.88 tf) tf ω (π / 12) (-((9.81 : ℝ) • ez)) X) :=
  no_lossless_relaxation_constrained_upright_6dof_mass htf hω gtpl_delta.1 gtpl_delta.2
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (gtpl_burn htf42) (by norm_num)
    gtpl_twr htan hX R

/-- **GTPL, free final time on a window, altitude/glide slope, explicit mass depletion (5DOF).** -/
theorem gtpl_no_lossless_freeTime_mass {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {ta tb ω tanγ : ℝ} (hta : 0 < ta) (htab : ta ≤ tb) (htb42 : tb ≤ 42) (hω : 0 < ω)
    (htan : 0 ≤ tanγ) {X : Set (E3 × E3)} (hX : glideSlopeSet tanγ ⊆ X)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (⋃ t ∈ Icc ta tb, constrainedLandingSet
      (AccMass 400 1000 (1 / (9.81 * 180)) 79.88 55.88 t) t ω (π / 12) (-((9.81 : ℝ) • ez)) X) :=
  no_lossless_relaxation_freeTime_5dof_mass hta htab hω gtpl_delta.1 gtpl_delta.2
    (by norm_num) (by norm_num) (by norm_num) (by norm_num) (gtpl_burn htb42) (by norm_num)
    gtpl_twr htan hX R

end LcvxObstruction
