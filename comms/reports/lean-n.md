# Report: lean-n (solver claims N1–N7 in Lean)

Date: 2026-11-07 02:36. Brief: comms/briefs/lean-n.md. Map: lean/SOLVER.md.

## Deliverables
- Lean: lean/LcvxObstruction/LcvxObstruction/Solver/{Gimbal,Vectors,Gyro,Relaxation,Axioms}.lean, namespace `LcvxSolver`.
  The four content files are imported in the root `LcvxObstruction.lean`. Full `lake build` is green (18236 jobs).
  No sorry, no axiom. `#print axioms` on all 28 headline theorems gives [propext, Classical.choice, Quot.sound].
- lean/SOLVER.md maps each theorem to its solver/CLAIMS.md row.
- solver/CLAIMS.md: I changed only the "Lean status" column, for rows 5, 6, 7, 8, 10, 15, 16.
- comms/CLAIMS.md: rows N1–N7 added.

## Results
| Claim | Verdict |
|---|---|
| N1 gimbal box | FORMALIZED and sharper. The box gives \|θ\| ≤ δ and **\|φ\| ≤ δ**. The claimed asin(tan δ) also holds. |
| N2 θ axis | FORMALIZED: exact rate formula plus the bound (\|Ṫ_x\|+t\|Ṫ_z\|)/T_floor. |
| N2 φ axis heuristic | **FALSE as stated.** The exact rate is φ̇ = [Ṫ_y(T_x²+T_z²) − T_y(T_xṪ_x+T_zṪ_z)]/(‖T‖²√(T_x²+T_z²)), and the heuristic drops the Ṫ_x cross term. The Lean counterexample uses T=(1,1,1), Ṫ=(1,0,0), t=F=1: heuristic RHS 0, φ̇ = −1/(3√2). GTPL instance: φ̇ = −1.73°/s against a bound of 0. |
| N2 φ corrected | FORMALIZED. (a) \|φ̇\| ≤ (\|Ṫ_y\|+t\|Ṫ_z\|+t²\|Ṫ_x\|)/T_z. (b) The planner imposes the θ row and the φ row together, and that pair implies \|φ̇\| ≤ ω, and \|θ̇\| ≤ ω, pointwise and as FOH increments over an interval (`foh_gimbal_rate`, which needs the box and floor at the nodes only). **The solver's constraints are therefore valid and need no code change; only the wording of row 8 was wrong.** |
| N3 throttle slew | FORMALIZED (derivative, FOH and difference forms). |
| N4 chord bound | FORMALIZED (any real inner-product space). |
| N5 direction acceleration | FORMALIZED (algebraic and derivative forms). The discrete version is not covered (already flagged in solver/CLAIMS.md). |
| N6 gyroscopic term | FORMALIZED: the identity, ω₃ ≡ 0 from the Euler ODE, J_t ω̇_⊥ = τ_⊥, and the integral form (rate linear in torque). |
| N7 3DOF lower bound | FORMALIZED: the abstract form (EReal and ℝ infima, free t_f) and a model form linked to the existing `AttitudeAdmissible`/`Attitude6Admissible`/`constrainedLandingSet(6)` (V₃ ≤ V₅ ≤ V₆). Not covered: the ZOH discretisation of the computed bound, and the log-mass tangent/secant set. |

## Numerical cross-check (outside Lean)
Over 2e5 random samples with δ = 10°, the worst ratio of \|φ̇\| to bound (b) was 0.9998, and to bound (a) 0.9994. A finite-difference check matches the φ̇ formula to 1e-10.

## Communication
- I sent main a DM about the N2 φ-axis BREAK as soon as I found it, and posted a BOARD BREAK at 02:24.
- Final BOARD STATUS posted.

## Remaining limitations
- N6 assumes ω is differentiable on all of ℝ, not absolutely continuous on [0, t_f].
- N2/N3 FOH results cover one interval. Chaining intervals is immediate but not stated.
- The theorems are stated for the planning model's angles. Plant mismatch is out of scope.
