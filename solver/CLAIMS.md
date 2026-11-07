# Mathematical claims used by the solver

Every statement the recommended algorithm (planner B, "attitude-aware convex guidance") and the comparison
candidates rely on. "Registry" = row in `comms/CLAIMS.md`; "Lean" = machine-checked status there.
Rows marked **NEW** are introduced by this package and are not yet in the registry (all are elementary; the
orchestrator may register and formalize them). Nothing in the *certificate* depends on an unproved claim: the
certificate re-checks every limit numerically on a fine grid and by a 6DOF replay (see "What the certificate does
and does not prove" at the end).

## Claims the recommended algorithm (B) relies on

| # | Claim | Used where | Registry / proof | Lean status |
|---|---|---|---|---|
| 1 | **Union structure / per-instance exactness (C-U).** The 6DOF feasible set is a union over attitude profiles of convex sets; with the right attitude the convex program is exact. The nonconvexity lives entirely in the attitude choice. | Design of B (outer loop over attitude, convex inner) | C-U, math/04 §9 | CLAIMED (consistent with A/B*) |
| 2 | **No single convex program is lossless for 5DOF/6DOF** (Thm A + B*, any cost, altitude/glide slope, upright landing). | Why B needs an outer loop at all | A, B*, math/02, lean/…/Main.lean | **FORMALIZED** (kinematic 5DOF/6DOF; torque-limited TVC version: B6-TVC proved, B6-TVC-up open) |
| 3 | **Torque balance (Lemma 8.1).** With zero roll rate, J_t b×b̈ = L T×b ⇔ Π_b T = −(J_t/L) Π_b b̈. In body axes: T_x = −k α_y, T_y = +k α_x, k = J_t/L. | Inner problem: the gimbal's lateral thrust is fixed by the angular-acceleration profile | C-6 / Lemma 8.1, math/04 §8 | **FORMALIZED** (`torque_balance_iff`) |
| 4 | **C-6: exact convexity given attitude.** For a fixed attitude profile (and a prescribed mass history) the pure-TVC problem is a convex program in the scalar axial thrust T_a with linear dynamics; no relaxation. Throttle and gimbal limits become an interval L(t) ≤ T_a ≤ U(t); a body-fixed box gimbal is also linear in T_a. | Inner SOCP (`AACG.solve_inner`): every accepted plan is an exact solution of the true dynamics for its attitude | C-6, math/04 §8 | **FORMALIZED** for constant mass (`throttle_interval`, `convex_tvcSet`, `convex_feasData_M3b`). Prescribed time-varying mass: same proof (dynamics stay affine in T_a), **not** in Lean |
| 5 | **NEW N6: linear body-rate dynamics.** Axisymmetric body (J = diag(J_t, J_t, J_z)), no roll torque, ω₃(0) = 0 ⇒ ω₃ ≡ 0 and J_t ω̇_⊥ = τ_⊥ exactly (gyroscopic term ω×Jω vanishes). Hence ω(t) is linear in the angular-acceleration profile and ω(t_f) = 0 is a linear constraint. | Attitude parameterisation, terminal-rate constraint | elementary (ω×Jω = J_t ω×ω = 0 when ω₃ = 0; ω̇₃ = (J_t−J_t)ω₁ω₂/J_z = 0) | not formalized; part of the M3b model assumption in C-6 |
| 6 | **NEW N1: conservative gimbal box.** \|T_x\| ≤ tan δ_p T_z and \|T_y\| ≤ tan δ_p T_z imply, in the flight-code gimbal convention d = (sin θ cos φ, sin φ, cos θ cos φ), \|θ\| ≤ δ_p and \|φ\| ≤ asin(tan δ_p) (≤ 15° for δ_p ≤ 14.5°). | Gimbal constraints in step and inner problems | elementary (tan θ = T_x/T_z; sin φ = T_y/‖T‖ ≤ tan δ_p T_z/‖T‖) | not formalized (certificate re-checks the exact angles) |
| 7 | **NEW N3: throttle-slew sufficient condition.** For first-order-hold body thrust, \|d‖T‖/dt\| ≤ ‖Ṫ‖ ≤ (\|ΔT_x\|+\|ΔT_y\|+\|ΔT_z\|)/h. | Rate constraints (step + inner) | elementary (triangle inequality) | not formalized |
| 8 | **NEW N2: gimbal-rate sufficient condition.** For FOH thrust with T_z ≥ T_floor and \|T_x\| ≤ tan δ_p T_z: \|θ̇\| ≤ (\|ΔT_x\| + tan δ_p \|ΔT_z\|)/(h T_floor). Proved for the θ axis; for the φ axis (sin convention) the same linear condition is used **heuristically**. | Rate constraints | θ: elementary (θ̇ = (Ṫ_x T_z − T_x Ṫ_z)/(T_x²+T_z²)); φ: not proved | not formalized; the certificate checks both axes against 100°/s numerically on the fine grid |
| 9 | **CCP restriction of the min-throttle bound (P22 family).** ‖T‖ ≥ n̄ᵀT for any unit n̄ (Cauchy–Schwarz), so n̄ᵀT ≥ ρ₁ is a convex inner approximation of ‖T‖ ≥ ρ₁, exact at T ∥ n̄. | Step subproblem only (the inner problem uses the exact interval of claim 4) | P22 (`bilinear_restriction`, polarization form); the linear-minorant form is Cauchy–Schwarz | P22 **FORMALIZED**; the minorant form is trivial |
| 10 | **NEW N7: 3DOF relaxation is a lower bound.** Every 6DOF-feasible plan is feasible for the 3DOF problem without attitude and without rate limits, with the same throttle range, state constraints and cost; the tangent (lower) / secant (upper) log-mass bounds only enlarge the set. Hence V₃(t_f) ≤ V₆(t_f) and min_tf V₃ ≤ min_tf V₆. | Optimality-gap certificate `LB` in RESULTS | elementary in continuous time | not formalized. **Caveat:** computed on a ZOH grid (N = 35); the discretization error of the bound is not bounded rigorously (numerically B ≥ LB in every case) |
| 11 | **Centre-of-percussion identity (FLAT).** With ω₃ ≡ 0 and ε = J_t/(mL) constant, y = r + ε b satisfies ÿ = (T cos μ/m − ε‖ω‖²) b − g. | Tracking controller only (not the planner, not the certificate) | FLAT, math/checks/flat_output_tvc.py; also `test_centre_of_percussion_identity` | identity CONFIRMED (numerical/symbolic), not formalized |

## Claims used by the comparison candidates / diagnostics

| # | Claim | Used where | Registry / proof | Lean status |
|---|---|---|---|---|
| 12 | **C-E: lossiness only at minimum throttle.** | Explains baseline A's 296 N "min-thrust" arc | C-E, math/04 §4 | discrete C-E(a) **FORMALIZED** |
| 13 | **C-K2 purification** (≤ ½Σc_i lossy nodes). | `purify()` diagnostic on A | C-K, math/04 §7 | **FORMALIZED** (except "random objective ⇒ extreme point w.p. 1"). Note: A's pointing constraint is a ball, not the cap K_σ(b) of C-K2, so the node count bound is not guaranteed for A |
| 14 | **C-Y: thinness.** A 3DOF thrust history with ‖T‖ ≥ ρ₁ is exactly TVC-realizable only for in-plane initial body rates in a set of diameter ≤ 2δμ_c/sinh(μ_c t_f) (≈ 3.5 µrad/s for GTPL). | Why A and C plans are never exactly flyable, only trackable | C-Y, math/04 §10 | CLAIMED |
| 15 | **NEW N4: chord bound.** ‖a‖, ‖b‖ ≥ ρ and ∠(a,b) = θ ∈ [0, π] ⇒ ‖a − b‖ ≥ 2ρ sin(θ/2). | Sizing of candidate C | elementary (minimise A²+B²−2AB cos θ over A, B ≥ ρ; `test_chord_bound`) | not formalized |
| 16 | **NEW N5: direction-acceleration bound (continuous time).** T = Γe with Γ ≥ ρ, ‖Ṫ‖ ≤ D₁, ‖T̈‖ ≤ D₂, ‖ė‖ ≤ ω ⇒ ‖Π_e ë‖ ≤ (D₂ + 2D₁ω)/ρ. | Sizing of candidate C | elementary (Π_e T̈ = 2Γ̇ė + ΓΠ_e ë) | not formalized; **discrete version not proved** (C's certificate checks the discrete second difference a posteriori). Also note: the thrust direction is not the body axis for pure TVC (claim 14), so N5 does not make C flyable |
| 17 | **Pad-hop nonconvexity is real** (3DOF relaxations accept landings no flyable plan reaches). | Hop results | HOP (NUMERICAL), B6-TVC (PROVED) | numerical only |

## Algorithmic statements (no proof claimed)

- **Monotone merit, feasible iterates (by construction).** B accepts an attitude update only if the exact inner
  problem's merit decreases; every accepted iterate is an exact inner solution, so it is flyable whenever its
  terminal defect is zero. This is a property of the acceptance rule, not a theorem about convergence.
- **SCvx convergence to a KKT point of the 6DOF problem: NOT claimed.** Observed in 8/8 open-loop scenarios
  (B within 0.04% of the best IPOPT multistart optimum), but B can stall at an infeasible point near the edge of the
  feasible set (hop v0z = 5 m/s, d = 6 m: D finds a plan, B does not; see RESULTS.md).
- **Mass fixed point** (inner problems use the mass history of the previous iterate): no convergence proof; the
  residual is measured by the open-loop replay (`replay_dm` ≈ 1e-5 kg, terminal error < 1 mm).
- **Closed-loop robustness** (tracking controller + 1 Hz replans): Monte Carlo evidence only.

## What the certificate does and does not prove

`certify_B` evaluates the returned plan (not the optimiser) on an 8×-finer grid: throttle within [400, 1000] N,
exact flight-convention gimbal angles within the ±15° box, gimbal rate ≤ 100°/s, throttle rate ≤ 2000 N/s, tilt and
glide-slope limits, terminal defects (≤ 1 cm, ≤ 1 cm/s, ≤ 0.5° tilt, zero rate), and an open-loop replay of the
plan's body-frame thrust through the full quaternion rigid-body model (RK4, 4 substeps per quadrature step) that
must land within 5 cm / 5 cm/s / 1°. It therefore certifies **flyability of the plan for the planning model**
(constant J_t/L, no disturbances, rigid gimbal), up to floating-point integration error. It does not certify global
optimality (only the gap to the 3DOF lower bound, claim 10) and it does not cover plant/model mismatch, which the
closed loop handles.
