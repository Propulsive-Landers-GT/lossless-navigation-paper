# 5DOF Lossless Convexification — model catalog and orchestrator proof sketch

Author: orchestrator (main session). Status: DRAFT, to be attacked by the verifier agent.

## 0. Vehicle context (GTPL monoprop lander)
- TVC gimbal limit δ = 15°, thrust 400–1000 N (min throttle ρ1 > 0 !), dry mass 61 kg
  (`simulations/RocketSimulation/rust_rocket_sim/src/algorithms.rs`).
- Roll is handled by a separate RCS (`control/RCS`), decoupled from thrust direction.
- Current stack: 3DOF LCvx (`guidance/LosslessConvexification`) -> 6DOF MPC tracking.
- **Decision**: primary target is 5DOF = 3D translation + thrust-axis (body z-axis) pitch/yaw.
  Roll does not affect where thrust points for an axisymmetric vehicle, so 6DOF results
  follow as corollaries (6DOF admissible set maps into the 5DOF one; planar arcs are 6DOF-realizable).

## 1. Model catalog (all 5DOF; translational part common)
Common: r̈ = a(t) d(t) + g, with a(t) = T(t)/m(t) the thrust acceleration magnitude,
d(t) ∈ S² the thrust direction, ṁ = -α T, T ∈ [ρ1, ρ2], ρ1 > 0.
Body axis b(t) ∈ S². Gimbal: angle(d(t), b(t)) ≤ δ  (δ < π/2).

- **M0 (3DOF LCvx baseline)**: no b; optional fixed pointing cone angle(d, n̂) ≤ θ. Known LCvx (Açıkmeşe–Ploen 2007, Açıkmeşe–Carson–Blackmore 2013).
- **M1 (kinematic, rate-limited axis)**: b Lipschitz on S² w.r.t. angle: angle(b(s), b(s')) ≤ ω|s−s'|.
  Equivalent to ‖ω_⊥‖ ≤ ω_max for the body angular velocity perpendicular to b. Gimbal fast (d measurable).
- **M2 (M1 + gimbal-rate limits)**: d also rate-limited.
- **M3 (rigid-body, torque-limited)**: J ω̇ = τ, τ from gimbal (τ = ℓ b × T-ish), ‖τ‖ bounded ⇒ angular *acceleration* bounded.
- **M4 (6DOF)**: M3 plus roll. Roll decoupled from d.

## 2. Key definitions
- Boundary data θ = (r0, v0) (initial position/velocity), with b(0), b(tf), m0, tf fixed.
- F_tf = { (r0,v0) : ∃ admissible control landing at r(tf)=0, v(tf)=0 }.
- A **uniform convex relaxation** is a convex set C ⊆ (R³×R³) × Y (Y any real vector space —
  lifted variables, discretization, slack, anything), where boundary data enter jointly-convexly.
  Relaxed problem at θ: minimize any cost over the slice C_θ = {y : (θ,y) ∈ C}.
- **Lossless (feasibility form)**: for every θ, C_θ ≠ ∅ ⇔ θ ∈ F_tf.
  (Standard LCvx lossless ⇒ this, when relaxed optima are attained: if C_θ ≠ ∅ but θ ∉ F_tf,
  the relaxed optimum cannot be original-feasible; if θ ∈ F_tf, the original solution is relaxed-feasible.)

## 3. Theorem A (abstract obstruction) — trivial but the crux
If a uniform convex relaxation is lossless then F_tf = proj_θ(C) is convex.
Proof: linear image of convex set is convex. Cost-independent.

## 4. Theorem B (nonconvexity of 5DOF feasible set, model M1, hence M4)
Setup: b(0) = e_z. Let φ(s) = ωs (or tent φ(s)=min(ωs, ω(tf−s)) if also b(tf)=e_z is imposed).
Assume δ + max φ ≤ π/2, ρ1 > 0.
Let a1(s) = ρ1 / (m0 − αρ1 s) (min-throttle acceleration profile; constant ρ1/m0 if α=0).
Fact: every admissible trajectory has a(s) ≥ a1(s) (T ≥ ρ1 ⇒ m(s) ≤ m0 − αρ1 s).

Velocity-increment set R = { ∫_0^tf a(s) d(s) ds : admissible }. proj_{v0}(F_tf) = −g tf − R,
so R nonconvex ⇒ F_tf nonconvex.

Extreme arcs: for horizontal unit u, b_u(s) = (sin φ(s) u, cos φ(s)), d_u(s) = (sin(δ+φ(s)) u, cos(δ+φ(s))),
a = a1. Endpoints P_u = ( (∫a1 sin(δ+φ)) u , ∫ a1 cos(δ+φ) ).
Midpoint M = (P_u + P_{−u})/2 = (0, ∫ a1 cos(δ+φ)) ∈ conv R.

Claim: M ∉ R.
(1) b(s)·e_z ≥ cos φ(s) (rate bound from both ends). Spherical triangle inequality
    (inner-product form: x·y ≥ cos α, y·z ≥ cos β, α+β ≤ π ⇒ x·z ≥ cos(α+β)) gives d(s)·e_z ≥ cos(δ+φ(s)) ≥ 0.
(2) ∫ a d_z ≥ ∫ a1 cos(δ+φ), equality ⇒ (since a1 > 0) d(s)·e_z = cos(δ+φ(s)) a.e.
(3) Equality in (2) ⇒ equality in the triangle inequality a.e. ⇒ b(s)·e_z = cos φ(s) a.e. ⇒ (continuity) ∀s,
    and d(s) lies in the vertical plane through b(s), tilted further by δ: d_lat(s) = sin(δ+φ(s)) u(s), where
    b(s) = (sin φ(s) u(s), cos φ(s)).
(4) Rigidity: for s<s' on a monotone piece of φ with φ>0, b(s)·b(s') ≥ cos(ω|s−s'|) = cos(φ(s')−φ(s))
    and b(s)·b(s') = cos φ cos φ' + sin φ sin φ' (u·u') ⇒ u·u' ≥ 1 ⇒ u(s) = u(s'). Chain through the peak ⇒ u constant.
(5) Then ∫ a d_lat = (∫ a sin(δ+φ)) u ≠ 0, but M has zero lateral component. Contradiction. ∎

Remarks / sanity checks:
- ω = ∞ (no rate limit): (4) fails, chattering between ±u gives M — consistent with 3DOF LCvx working.
- Argument is cost-independent and holds with or without mass depletion, with gravity (affine shift).
- 6DOF: rate-limited angular velocity ⇒ body axis satisfies M1 bound; planar arcs realizable with zero roll.
- Small tf only (δ + ωtf ≤ π/2); enough for impossibility of a *uniform* LCvx at that tf.
  Larger tf / free tf: to be investigated numerically.
- Non-uniform "relaxations" (e.g. fixing the attitude profile per instance) are NOT excluded — and are the
  basis of the positive result.

## 5. Theorem C (positive): LCvx given an attitude profile
Fix b(·). Constraint d(t) ∈ cone(b(t), δ) with T ∈ [ρ1,ρ2] relaxed to ‖T‖ ≤ Γ, b(t)·T ≥ Γ cos δ, ρ1 ≤ Γ ≤ ρ2.
Pointwise lemma (Lemma 3 of ACB 2013) unchanged; the analytic zero-set argument must be replaced by an
explicit non-degeneracy condition: the primer vector p(t) (affine in t for the double integrator) satisfies
p(t) ∦ −b(t) except on a null set. To be written up rigorously by the positive-result agent.

## 6. Open questions for agents
- Does nonconvexity persist for large tf and for free final time? (numerics)
- Is ρ1 > 0 necessary? With ρ1 = 0, is R convex? (numerics + math)
- M3 (torque-limited) rigidity analog.
- Quantitative gap dist(M, R) ⇒ no ε-lossless uniform relaxation for small ε.
