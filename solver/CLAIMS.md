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
| 2 | **No single convex program is lossless for 5DOF/6DOF** (Thm A + B*, any cost, altitude/glide slope, upright landing). Lossless means sound *and* complete; a single convex program can still be sound (planner F, rows F1 to F7). | Why no planner here can be exact for every initial state. It does not by itself force an outer loop: B's loop comes from planning in CG coordinates | A, B*, math/02, lean/…/Main.lean | **FORMALIZED** (kinematic 5DOF/6DOF; torque-limited TVC version: B6-TVC proved, B6-TVC-up open) |
| 3 | **Torque balance (Lemma 8.1).** With zero roll rate, J_t b×b̈ = L T×b ⇔ Π_b T = −(J_t/L) Π_b b̈. In body axes: T_x = −k α_y, T_y = +k α_x, k = J_t/L. | Inner problem: the gimbal's lateral thrust is fixed by the angular-acceleration profile | C-6 / Lemma 8.1, math/04 §8 | **FORMALIZED** (`torque_balance_iff`) |
| 4 | **C-6: exact convexity given attitude.** For a fixed attitude profile (and a prescribed mass history) the pure-TVC problem is a convex program in the scalar axial thrust T_a with linear dynamics; no relaxation. Throttle and gimbal limits become an interval L(t) ≤ T_a ≤ U(t); a body-fixed box gimbal is also linear in T_a. | Inner SOCP (`AACG.solve_inner`): every accepted plan is an exact solution of the true dynamics for its attitude | C-6, math/04 §8 | **FORMALIZED** for constant mass (`throttle_interval`, `convex_tvcSet`, `convex_feasData_M3b`). Prescribed time-varying mass: same proof (dynamics stay affine in T_a), **not** in Lean |
| 5 | **NEW N6: linear body-rate dynamics.** Axisymmetric body (J = diag(J_t, J_t, J_z)), no roll torque, ω₃(0) = 0 ⇒ ω₃ ≡ 0 and J_t ω̇_⊥ = τ_⊥ exactly (gyroscopic term ω×Jω vanishes). Hence ω(t) is linear in the angular-acceleration profile and ω(t_f) = 0 is a linear constraint. | Attitude parameterisation, terminal-rate constraint | elementary (ω×Jω = J_t ω×ω = 0 when ω₃ = 0; ω̇₃ = (J_t−J_t)ω₁ω₂/J_z = 0) | **FORMALIZED** (`gyro_vanish`, `gyro_roll_component`, `euler_axisymmetric`, `euler_axisymmetric_integral`; lean/SOLVER.md) |
| 6 | **NEW N1: conservative gimbal box.** \|T_x\| ≤ tan δ_p T_z and \|T_y\| ≤ tan δ_p T_z imply, in the flight-code gimbal convention d = (sin θ cos φ, sin φ, cos θ cos φ), \|θ\| ≤ δ_p and \|φ\| ≤ asin(tan δ_p) (≤ 15° for δ_p ≤ 14.5°). | Gimbal constraints in step and inner problems | elementary (tan θ = T_x/T_z; sin φ = T_y/‖T‖ ≤ tan δ_p T_z/‖T‖) | **FORMALIZED, sharper** (`gimbal_box_angles`: the box gives \|θ\| ≤ δ_p and \|φ\| ≤ δ_p, hence ≤ asin(tan δ_p); `axial_floor` = T_floor) |
| 7 | **NEW N3: throttle-slew sufficient condition.** For first-order-hold body thrust, \|d‖T‖/dt\| ≤ ‖Ṫ‖ ≤ (\|ΔT_x\|+\|ΔT_y\|+\|ΔT_z\|)/h. | Rate constraints (step + inner) | elementary (triangle inequality) | **FORMALIZED** (`throttle_rate_le`, `throttle_slew_foh`, `throttle_slew_increment`, `norm_le_sum_abs`) |
| 8 | **NEW N2: gimbal-rate sufficient condition (corrected).** For FOH thrust with T_z ≥ T_floor, \|T_x\|, \|T_y\| ≤ tan δ_p T_z, the planner imposes the PAIR θ-row \|ΔT_x\| + tan δ_p \|ΔT_z\| ≤ ω h T_floor and φ-row \|ΔT_y\| + tan δ_p \|ΔT_z\| ≤ ω h T_floor; together they imply \|θ̇\| ≤ ω and \|φ̇\| ≤ ω on each FOH interval. (The φ-row *alone* does NOT bound φ̇ — it misses the Ṫ_x cross term; the correct standalone bound is \|φ̇\| ≤ (\|Ṫ_y\|+t\|Ṫ_z\|+t²\|Ṫ_x\|)/T_z.) | Rate constraints | θ: θ̇ = (Ṫ_x T_z − T_x Ṫ_z)/(T_x²+T_z²); φ: exact formula + pair argument, lean/SOLVER.md | θ: **FORMALIZED** (`hasDerivAt_theta`, `theta_rate_bound`). φ heuristic alone: **FALSE** (`phi_rate_heuristic_false`; the Ṫ_x cross term is missing). Corrected: \|φ̇\| ≤ (\|Ṫ_y\|+t\|Ṫ_z\|+t²\|Ṫ_x\|)/T_z (`phi_rate_bound_standalone`). The planner's θ-row + φ-row **pair** ⇒ \|θ̇\|, \|φ̇\| ≤ ω_plan: **FORMALIZED** (`gimbal_rate_pair`, FOH increments `foh_gimbal_rate`). Solver constraints valid, no code change |
| 9 | **CCP restriction of the min-throttle bound (P22 family).** ‖T‖ ≥ n̄ᵀT for any unit n̄ (Cauchy–Schwarz), so n̄ᵀT ≥ ρ₁ is a convex inner approximation of ‖T‖ ≥ ρ₁, exact at T ∥ n̄. | Step subproblem only (the inner problem uses the exact interval of claim 4) | P22 (`bilinear_restriction`, polarization form); the linear-minorant form is Cauchy–Schwarz | P22 **FORMALIZED**; the minorant form is trivial |
| 10 | **NEW N7: 3DOF relaxation is a lower bound.** Every 6DOF-feasible plan is feasible for the 3DOF problem without attitude and without rate limits, with the same throttle range, state constraints and cost; the tangent (lower) / secant (upper) log-mass bounds only enlarge the set. Hence V₃(t_f) ≤ V₆(t_f) and min_tf V₃ ≤ min_tf V₆. | Optimality-gap certificate `LB` in RESULTS | elementary in continuous time | **FORMALIZED** in continuous time (`relaxation_lower_bound`, `value3_le_value6(_freeTime)`, `constrainedLandingSet6_subset_landingSet3`); ZOH discretization of the bound not covered |
| 11 | **Centre-of-percussion identity (FLAT).** With ω₃ ≡ 0 and ε = J_t/(mL) constant, y = r + ε b satisfies ÿ = (T cos μ/m − ε‖ω‖²) b − g. | Tracking controller for B and S; the whole of planner F (rows F1 to F7 below) | FLAT, math/checks/flat_output_tvc.py; also `test_centre_of_percussion_identity` | **FORMALIZED** (`TVC.cop_identity`, `cop_identity_roll`; lean/TVC.md). An earlier version of this row said "not formalized"; the Lean proof was added later and this row was not updated |

## Claims used by the comparison candidates / diagnostics

| # | Claim | Used where | Registry / proof | Lean status |
|---|---|---|---|---|
| 12 | **C-E: lossiness only at minimum throttle.** | Explains baseline A's 296 N "min-thrust" arc | C-E, math/04 §4 | discrete C-E(a) **FORMALIZED** |
| 13 | **C-K2 purification** (≤ ½Σc_i lossy nodes). | `purify()` diagnostic on A | C-K, math/04 §7 | **FORMALIZED** (except "random objective ⇒ extreme point w.p. 1"). Note: A's pointing constraint is a ball, not the cap K_σ(b) of C-K2, so the node count bound is not guaranteed for A |
| 14 | **C-Y: thinness.** A 3DOF thrust history with ‖T‖ ≥ ρ₁ is exactly TVC-realizable only for in-plane initial body rates in a set of diameter ≤ 2δμ_c/sinh(μ_c t_f) (≈ 3.5 µrad/s for GTPL). | Why A and C plans are never exactly flyable, only trackable | C-Y, math/04 §10 | CLAIMED |
| 15 | **NEW N4: chord bound.** ‖a‖, ‖b‖ ≥ ρ and ∠(a,b) = θ ∈ [0, π] ⇒ ‖a − b‖ ≥ 2ρ sin(θ/2). | Sizing of candidate C | elementary (minimise A²+B²−2AB cos θ over A, B ≥ ρ; `test_chord_bound`) | **FORMALIZED** (`chord_bound`) |
| 16 | **NEW N5: direction-acceleration bound (continuous time).** T = Γe with Γ ≥ ρ, ‖Ṫ‖ ≤ D₁, ‖T̈‖ ≤ D₂, ‖ė‖ ≤ ω ⇒ ‖Π_e ë‖ ≤ (D₂ + 2D₁ω)/ρ. | Sizing of candidate C | elementary (Π_e T̈ = 2Γ̇ė + ΓΠ_e ë) | continuous time **FORMALIZED** (`dir_accel_bound`, `dir_accel_bound_calculus`); discrete version not proved |
| 17 | **Pad-hop nonconvexity is real** (3DOF relaxations accept landings no flyable plan reaches). | Hop results | HOP (NUMERICAL), B6-TVC (PROVED) | numerical only |

## Claims the landing algorithm (planner F) relies on

Statement and proofs: [`../math/10-landing-proof.md`](../math/10-landing-proof.md) (Theorem F, Lemmas 1 to 6). None is
in Lean except row F1. Each is checked numerically by `tests/test_flat.py`.

| # | Claim | Used where | Proof | Status |
|---|---|---|---|---|
| F1 | **FLAT.** With zero roll rate and ε = J_t/(mL) constant, y = r + ε b satisfies y″ = (T_a/m − ε‖ḃ‖²) b − g. | The whole planner: dynamics are linear in y | registry FLAT | **FORMALIZED** (`TVC.cop_identity`), constant mass. With depleting mass the identity needs ε constant, i.e. J_t ∝ m L (assumption CoP, proof §1); checked against `dynamics.deriv` with J_t = ε m L by `test_centre_of_percussion_identity_with_flat_controls` and by the open-loop replay |
| F2 | **Flat map.** b = u/‖u‖, ḃ = P u′/f, P b″ = P(u″ − 2(ḟ/f)u′)/f, a = f + ε‖ḃ‖², ℓ = −ε P b″, with u = y″ + g e₃. | Reference generation, certificate | proof, Lemma 2 | checked against finite differences (`test_flat_map_matches_finite_differences_of_the_body_axis`) |
| F3 | **Linear boundary conditions.** Initial attitude, body rate and gimbal deflection, and the upright / zero-rate / centred-gimbal touchdown, are linear equalities in the spline coefficients. | Boundary rows of the SOCP | proof, Lemma 3 (f₀ and ḟ₀ are linear in the coefficients) | checked by `check_limits` (boundary residual ≤ 1e-11) |
| F4 | **Bounds B1 to B5.** For any ρ, κ, k and p = u_z: f‖ḃ‖ ≤ ‖u′ − ρu‖; f‖ḃ‖² ≤ ‖u′ − ρu‖²/p; f‖P b″‖ ≤ ‖u″ − 2ρu′ − κu − k e₃‖ + sin(tilt)\|k\| + ‖u′ − ρu‖²/p; p ≤ T/m ≤ ‖(‖u‖ + εq/L_b, εG/L_b)‖; 2φp − φ² ≤ f². | Restriction rows R2 to R6 | proof, Lemma 4 | elementary; 4000 random points in `test_pointwise_bounds_used_by_the_restriction` |
| F5 | **Every instant.** A constraint that is jointly convex in (u, u′, u″) with parameters constant on a span, imposed on the four degree-elevated Bezier control tuples of the span, holds at every time in the span. | Why no inter-node check is needed | proof, Lemma 5 (convex-hull property of the Bernstein basis) | control polygons checked by `test_bezier_control_polygons_reproduce_every_derivative`; dense-grid check in `test_single_solve_is_flyable_at_every_instant` |
| F6 | **Mass bracket.** z_lo ≤ ln m ≤ z_up with z_up = z₀ − α∫p and z_lo = z₀ − α∫σ, both affine in the variables; a chord of e^(−z) bounds the lower throttle limit and a tangent the upper one. | Throttle limits with depleting mass; fuel bound | proof, Lemma 6 | elementary; fuel bound checked in the same test |
| F7 | **Sound, not complete.** Every feasible point of the SOCP is a trajectory of the planning model within the planning limits. The converse fails, as Theorem A requires. | What F guarantees | proof, Theorem F and the Proposition of §9 | soundness by construction; incompleteness measured in RESULTS-FLAT.md |

Not claimed for F: any bound on gimbal slew or throttle slew (certificate only), continuous-time satisfaction of the
altitude floor and glide slope (sampled, soft), or anything about plants that violate assumption CoP.

## Algorithmic statements (no proof claimed)

- **Monotone merit, feasible iterates (by construction).** B accepts an attitude update only if the exact inner
  problem's merit decreases; every accepted iterate is an exact inner solution, so it is flyable whenever its
  terminal defect is zero. This is a property of the acceptance rule, not a theorem about convergence.
- **SCvx convergence to a KKT point of the 6DOF problem: NOT claimed.** Observed in 8/8 open-loop scenarios
  (B within 0.012% of the best IPOPT multistart optimum) and 20/20 hop cells (B and IPOPT agree on feasibility).
  An early run without the initial-gimbal condition showed one stall at an infeasible stationary point of the merit
  where IPOPT found a plan (`results/hop_map_v1.json`), so stalls near the feasibility edge are possible.
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
