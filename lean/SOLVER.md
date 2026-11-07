# Solver claims N1–N7: Lean formalization map

Author: [lean-n]. Project `lean/LcvxObstruction`. Files: `LcvxObstruction/Solver/{Gimbal,Vectors,Gyro,Relaxation}.lean`.
Namespace `LcvxSolver`. All four files are imported from the root `LcvxObstruction.lean`, and the full `lake build` is green.
The files contain no `sorry` and no new `axiom`. `LcvxObstruction/Solver/Axioms.lean` runs `#print axioms` on every theorem
listed below. Each one reports only `[propext, Classical.choice, Quot.sound]` (checked 2026-11-07).
Row numbers refer to `solver/CLAIMS.md`.

## Conventions
* Body thrust `T = (T_x, T_y, T_z)` uses real coordinates `x y z`, and its rate `Ṫ` uses `dx dy dz`. `t = tan δ ≥ 0`.
* Flight gimbal convention: `d = (sin θ cos φ, sin φ, cos θ cos φ)` with `T = ‖T‖ d`. Hence `θ = arctan(T_x/T_z)` (for `T_z > 0`)
  and `φ = arcsin(T_y/‖T‖)`, which is the same as `rotations.gimbal_angles`.
* `phiRate x y z dx dy dz := (dy(x²+z²) − y(x dx + z dz)) / ((x²+y²+z²)·√(x²+z²))` is the exact φ̇.
* N3–N5 are stated in a general real inner-product space `E`. The coordinate sum bound uses `EuclideanSpace ℝ (Fin 3)`.
* N6 uses `Fin 3 → ℝ` and `⨯₃` (the convention of `Positive/TVC.lean`). Index 2 is the roll (symmetry) axis.

## Theorem map

| Row | Claim | Lean theorem (file) | Status / comparison with the claim |
|---|---|---|---|
| 6 | **N1** conservative gimbal box | `gimbal_box_angles` (Gimbal) | **Stronger than claimed.** Hypotheses: `0 ≤ δ < π/2`, `|θ| ≤ π`, `|φ| ≤ π/2`, `s ≥ 0`, `T = s·d(θ,φ)`, `T_z > 0`, `|T_x|,|T_y| ≤ tan δ·T_z`. Conclusion: `|θ| ≤ δ`, **`|φ| ≤ δ`**, and `|φ| ≤ arcsin(tan δ)`. The claimed bound asin(tan δ) is valid but loose: the box already gives `|tan φ| ≤ tan δ·cos θ ≤ tan δ`. |
| 6/8 | planner axial floor `T_floor` | `axial_floor` (Gimbal) | If `‖T‖ ≥ T_min` and the box holds, then `T_z ≥ T_min·cos(arctan(√2 tan δ))`. This is `aacg._ta_floor`. |
| 8 | **N2** θ axis, exact rate | `hasDerivAt_theta` (Gimbal) | `d/ds arctan(T_x/T_z) = (Ṫ_x T_z − T_x Ṫ_z)/(T_x²+T_z²)` when `T_z > 0`. |
| 8 | **N2** θ axis, bound | `theta_rate_bound` (Gimbal) | Equal to the claim: `T_z ≥ F > 0` and `|T_x| ≤ tT_z` give `|θ̇| ≤ (|Ṫ_x| + t|Ṫ_z|)/F`. |
| 8 | **N2** φ axis, exact rate | `hasDerivAt_phi` (Gimbal) | `d/ds arcsin(T_y/‖T‖) = phiRate …` when `T_x²+T_z² > 0`. |
| 8 | **N2** φ axis, solver heuristic | `phi_rate_heuristic_false` (Gimbal) | **FALSE as stated.** The claim `|φ̇| ≤ (|Ṫ_y| + t|Ṫ_z|)/F` fails at `t = F = 1`, `T = (1,1,1)`, `Ṫ = (1,0,0)`: the right side is 0, but `φ̇ = −1/(3√2)`. The formula is missing the `Ṫ_x` cross term `−T_y T_x Ṫ_x/(‖T‖²√(T_x²+T_z²))`. GTPL instance (δ_p = 10°, T_floor = 426.93 N, `T = (tF,tF,F)`, `Ṫ = (ω_plan F,0,0)`): heuristic bound 0, actual φ̇ = −1.73°/s. |
| 8 | **N2** φ axis, corrected (standalone) | `phi_rate_bound_standalone` (Gimbal) | `T_z > 0` and `|T_x|,|T_y| ≤ tT_z` give `|φ̇| ≤ (|Ṫ_y| + t|Ṫ_z| + t²|Ṫ_x|)/T_z`. |
| 8 | **N2** φ axis, corrected (planner's pair of rows) | `phi_rate_bound_pair`, `gimbal_rate_pair` (Gimbal) | **The planner's constraint set is valid.** With `T_z ≥ F > 0`, `|T_y| ≤ tT_z`, `|Ṫ_x| + t|Ṫ_z| ≤ ωF` and `|Ṫ_y| + t|Ṫ_z| ≤ ωF` (both rows of `aacg._rate_constraints` / `reference_nlp`), we get `|φ̇| ≤ ω`. `gimbal_rate_pair` also gives `|θ̇| ≤ ω`. Key step: `pair_key`, `z(ρ²+XY) ≤ ρ(ρ²+Y²)` with `ρ² = X²+z²`. |
| 8 | **N2** first-order hold, one interval | `foh_gimbal_rate` (Gimbal) | Body thrust is linear between two nodes. The box and floor are required only at the nodes, and the two rows are stated in increments `|Δx| + t|Δz| ≤ ωFh`, `|Δy| + t|Δz| ≤ ωFh`. Conclusion for the exact angles, for all `u ∈ [s₀, s₀+h]`: `|θ(u)−θ(s₀)| ≤ ω(u−s₀)` and `|φ(u)−φ(s₀)| ≤ ω(u−s₀)`. This matches what `certify_B` measures, which is finite differences of angles. |
| 7 | **N3** throttle slew (continuous) | `hasDerivAt_norm_of_ne`, `throttle_rate_le` (Vectors) | `d‖T‖/dt = ⟪T,Ṫ⟫/‖T‖` and `|d‖T‖/dt| ≤ ‖Ṫ‖` at points where `T ≠ 0`. |
| 7 | **N3** coordinate bound | `norm_le_sum_abs` (Vectors) | `‖v‖ ≤ |v₀|+|v₁|+|v₂|` in ℝ³. |
| 7 | **N3** FOH / difference forms | `throttle_slew_foh`, `throttle_slew_increment` (Vectors) | Equal to the claim: `|d‖T‖/dt| ≤ ‖ΔT‖/h ≤ Σ|ΔT_i|/h` on a FOH interval, and `|‖T₁‖−‖T₀‖| ≤ ‖ΔT‖ ≤ Σ|ΔT_i|`. |
| 15 | **N4** chord bound | `chord_bound` (Vectors) | Equal (any real inner-product space): `0 ≤ ρ ≤ ‖a‖, ‖b‖` gives `2ρ sin(angle a b / 2) ≤ ‖a − b‖`. `angle` is `InnerProductGeometry.angle`. |
| 16 | **N5** direction acceleration (algebraic) | `dir_accel_bound` (Vectors) | Equal, pointwise. Assumes `‖e‖ = 1`, `⟪e,ė⟫ = 0`, `T₁ = Γ̇e + Γė`, `T₂ = Γ̈e + 2Γ̇ė + Γë`, `Γ ≥ ρ > 0`, `‖T₁‖ ≤ D₁`, `‖T₂‖ ≤ D₂`, `‖ė‖ ≤ ω`. Concludes `‖ë − ⟪e,ë⟫e‖ ≤ (D₂ + 2D₁ω)/ρ`. The bound `|Γ̇| ≤ D₁` is derived, not assumed. |
| 16 | **N5** (calculus) | `dir_accel_bound_calculus`, `inner_deriv_eq_zero_of_unit` (Vectors) | The same conclusion from `HasDerivAt` hypotheses on `Γ`, `e`, `T = Γe`, with `‖e(u)‖ = 1` for all `u`. The relations above are derived by uniqueness of derivatives. **Not covered:** the discrete (second-difference) version, as `solver/CLAIMS.md` already says. |
| 5 | **N6** gyroscopic term | `gyro_roll_component`, `gyro_vanish` (Gyro) | For `J = diag(J_t,J_t,J_z)`: the roll component of `ω×Jω` is 0 for every `ω`, and `ω₂ = 0` gives `ω×Jω = 0`. |
| 5 | **N6** ODE consequence | `euler_axisymmetric` (Gyro) | Euler `Jω̇ + ω×Jω = τ` with `J_z ≠ 0`, `τ₂ ≡ 0`, `ω₂(0) = 0` gives `ω₂ ≡ 0`, `ω×Jω ≡ 0`, and `J_t ω̇_i = τ_i` for `i = 0,1`. Hypothesis form: `ω` differentiable on all of ℝ (`HasDerivAt` everywhere). |
| 5 | **N6** linearity in torque | `euler_axisymmetric_integral` (Gyro) | If additionally `τ_i` is continuous and `J_t ≠ 0`: `ω_i(t) = ω_i(0) + J_t⁻¹∫₀ᵗτ_i`. So `ω(t_f) = 0` is linear in the torque (angular-acceleration) profile. |
| 10 | **N7** abstract | `relaxation_lower_bound` (EReal infima, so an empty set gives ⊤), `relaxation_lower_bound_real` (ℝ `sInf`, needs bounded below and nonempty), `freeTime_lower_bound` (Relaxation) | Equal: if every 6DOF-feasible plan maps to a 3DOF-feasible plan of equal cost, then `inf F₃ ≤ inf F₆`, and the same holds after minimising over `t_f`. |
| 10 | **N7** model form | `plans6_subset_plans5`, `plans5_subset_plans3`, `value3_le_value6`, `value3_le_value6_freeTime`, `constrainedLandingSet6_subset_landingSet3` (Relaxation) | Uses the existing model (`position`/`velocity`, `AttitudeAdmissible`, `Attitude6Admissible`, `constrainedLandingSet(6)`). The 3DOF plan set has the same throttle class `Acc` and the same state constraint `X`, with `d` measurable and unit and no attitude, rate or gimbal limits. For any cost depending on `(a, d)`: `V₃ ≤ V₅ ≤ V₆`, also with free `t_f`. **Not covered:** the solver's ZOH discretisation (N = 35) of the bound, and the claim that the solver's log-mass tangent/secant set actually contains the true mass dynamics. The model here has mass inside `Acc`. |

## What changes in `solver/CLAIMS.md`
* Row 8 (N2): the φ-axis heuristic is **false**, see `phi_rate_heuristic_false`. The solver code itself is safe, because it always
  imposes the θ row and the φ row together, and that pair implies `|φ̇| ≤ ω_plan` (`phi_rate_bound_pair`, `foh_gimbal_rate`).
  No code change is needed. Only the description of the claim was wrong.
* Row 6 (N1): the bound can be sharpened to `|φ| ≤ δ_p`. The claimed `asin(tan δ_p)` remains true.
