# 10. The landing algorithm: statement and proof

This note proves that the landing algorithm of [`LANDING-ALGORITHM.md`](../LANDING-ALGORITHM.md) (planner F,
`solver/gtpl_guidance/fcg.py`) returns only trajectories the vehicle model can fly. It is self-contained: every step
is elementary, and each lemma lists the test that checks it numerically.

**What is proved.** One theorem (soundness, §3) and one proposition (the price, §9).
**What is not proved** is listed in §10. Nothing here is a "lossless" result; no relaxation is used anywhere.

## 1. Model

World frame with z up, gravity g. Rigid axisymmetric body with unit body axis b (nose direction), transverse inertia
J_t, mass m. The engine pivots at the point L below the centre of mass on the body axis and delivers a thrust vector

    T = T_a b + T_⊥,     T_⊥ ⊥ b,

where T_a is the axial part and T_⊥ the part the gimbal deflects sideways. Roll rate is zero, so the angular velocity
ω is perpendicular to b and ḃ = ω × b. Equations of motion (those of `solver/gtpl_guidance/dynamics.py`):

    (M1)  m r″ = T − m g e₃
    (M2)  J_t ω̇ = (−L b) × T
    (M3)  ṁ = −α ‖T‖

**Assumption CoP.** ε := J_t/(m L) is constant along the flight. (For our vehicle ε = 1.35 m within 1 % over a
descent; §10.)

Actuator limits: T_min ≤ ‖T‖ ≤ T_max, gimbal angle δ with tan δ = ‖T_⊥‖/T_a at most δ_max, tilt of b from vertical at
most θ_max < 90°.

## 2. The program

**Unknown.** A curve y : [0, t_f] → ℝ³, a quintic B-spline with S uniform spans (so y ∈ C⁴, polynomial of degree 5
on each span). Write

    u = y″ + g e₃,   u′ = y‴,   u″ = y⁗.

On a span, u, u′, u″ are polynomials of degree 3, 2, 1. Raise their Bezier control points to degree 3. This gives four
*control tuples* (U, U₁, U₂)ⱼ, j = 0..3, linear in the spline coefficients, with

    (HULL)   (u, u′, u″)(t) = Σⱼ Bⱼ(t) (U, U₁, U₂)ⱼ,    Bⱼ(t) ≥ 0,   Σⱼ Bⱼ(t) = 1,   ∫_span Bⱼ = h/4,

where Bⱼ are the cubic Bernstein polynomials of the span and h is the span length.

**Given data.** Initial position r₀, velocity v₀, body axis b₀, its rate ḃ₀, the angular acceleration β₀ = P₀ b″(0)
the gimbal is producing now, mass m₀; the target r_T; the final time t_f. Per span, four numbers ρ, κ ∈ ℝ, φ > 0,
L_b > 0 (the *references*; any values are allowed).

**Constraints.** p denotes e₃·U. Constants: s = sin θ_max, t_δ = tan δ_max.

Boundary (linear), with f₀ := b₀·u(0), f₀′ := b₀·u′(0):

    (BC1)  y(0) = r₀ + ε b₀,   y′(0) = v₀ + ε ḃ₀
    (BC2)  u(0) = f₀ b₀
    (BC3)  u′(0) − f₀′ b₀ = f₀ ḃ₀
    (BC4)  u″(0) − (b₀·u″(0)) b₀ = f₀ β₀ + 2 f₀′ ḃ₀
    (BC5)  y(t_f) = r_T + ε e₃,   y′(t_f) = 0,   u_xy(t_f) = 0,   u′_xy(t_f) = 0,   u″_xy(t_f) = 0

On every control tuple, with auxiliary scalars e₁, q, k, g₂, s_f, σ:

    (R1)  ‖U_xy‖ ≤ tan θ_max · p
    (R2)  p ≥ L_b
    (R3)  ‖U₁ − ρ U‖ ≤ e₁,     e₁² ≤ q p
    (R4)  ‖U₂ − 2ρ U₁ − κ U − k e₃‖ + s |k| ≤ g₂,     G := g₂ + q
    (R5)  ε G ≤ t_δ (2φ p − φ²)
    (R6)  ‖U‖ ≤ s_f,     ‖( s_f + ε q / L_b ,  ε G / L_b )‖ ≤ σ

Mass. With z₀ = ln m₀ and t_s the start of span s, define the affine expressions

    z_up,s = z₀ − α ( y′_z(t_s) − y′_z(0) + g t_s ),        z_lo,s = z₀ − α (h/4) Σ_{spans ≤ s} Σⱼ σⱼ.

Fix numbers z_min,s < z_max,s and ẑ_s, let c_s be the chord of e^(−z) on [z_min,s, z_max,s] and τ_s the tangent of
e^(−z) at ẑ_s. On every tuple of span s:

    (R7)  z_min,s ≤ z_lo,s ≤ z_max,s,     p ≥ T_min · c_s(z_lo,s),     σ ≤ T_max · τ_s(z_up,s),     z_lo,S ≥ ln m_dry

**Objective.** Minimise (h/4) Σ σ (plus soft penalties on sampled state constraints, which play no role below).

All constraints are linear or second-order-cone, so this is an SOCP. Call it (P).

## 3. The theorem

Let y be feasible for (P). Define on [0, t_f], with P = I − b bᵀ:

    f = ‖u‖,   b = u / f,   ḃ = P u′ / f,
    a = f + ε ‖ḃ‖²,   ℓ = −ε P b″,   τ = √(a² + ‖ℓ‖²),
    m(t) = m₀ exp(−α ∫₀ᵗ τ),   T_a = m a,   T_⊥ = m ℓ.                                   (FLAT MAP)

> **Theorem F (soundness).** Suppose assumption CoP holds and y is feasible for (P). Then the model (M1)–(M3),
> started from (r₀, v₀, b₀, ḃ₀, m₀) and driven by the thrust T = T_a b + T_⊥ of the flat map, has the unique solution
>
>     r = y − ε b,   body axis b,   mass m,
>
> and this solution
> 1. starts with the gimbal where it is now: T_⊥(0) = −m₀ ε β₀;
> 2. ends at the target at rest, upright, with zero body rate and a centred gimbal:
>    r(t_f) = r_T, v(t_f) = 0, b(t_f) = e₃, ḃ(t_f) = 0, T_⊥(t_f) = 0;
> 3. satisfies **at every instant** t ∈ [0, t_f]:  T_min ≤ ‖T‖ ≤ T_max,  tan δ ≤ t_δ,  tilt ≤ θ_max;
> 4. burns at most m₀ (1 − exp(−α (h/4) Σ σ)) of propellant, and ends above the dry mass.

The proof is Lemmas 1 to 6.

## 4. Lemma 1: the centre of percussion

> **Lemma 1.** Under (M1), (M2) with ω ⊥ b and assumption CoP, the point y = r + ε b satisfies
> y″ = (T_a/m − ε‖ḃ‖²) b − g e₃, and T_⊥ = −m ε P b″.

*Proof.* Since ω ⊥ b, b″ = ω̇ × b + ω × (ω × b) = ω̇ × b − ‖ω‖² b, so P b″ = ω̇ × b and ‖ḃ‖ = ‖ω‖. From (M2),
J_t ω̇ × b = −L (b × T) × b = −L (b × T_⊥) × b = −L T_⊥, because (b × x) × b = x for x ⊥ b. Hence
T_⊥ = −(J_t/L) P b″ = −m ε P b″. Put this in (M1): r″ = (T_a/m) b − ε P b″ − g e₃ = (T_a/m) b − ε (b″ + ‖ḃ‖² b) − g e₃.
With ε constant, y″ = r″ + ε b″ = (T_a/m − ε‖ḃ‖²) b − g e₃. ∎

The gimbal's sideways force has dropped out. *Checked:* Lean `TVC.cop_identity` (pointwise identity, constant mass);
`tests/test_flat.py::test_centre_of_percussion_identity_with_flat_controls` (against `dynamics.deriv`, mass depleting,
J_t = ε m L).

## 5. Lemma 2: the flat map is the solution

> **Lemma 2.** Let y ∈ C⁴ with u ≠ 0 on [0, t_f], and define b, ḃ, a, ℓ, m, T_a, T_⊥ by the flat map. Then
> (r, b, m) with r = y − ε b solves (M1)–(M3) under the thrust T = T_a b + T_⊥, with ω = b × ḃ. It is the only
> solution with these initial values.

*Proof.* Differentiating u = f b twice and projecting with P shows that the flat-map ḃ is the derivative of b and
gives P b″ = P(u″ − 2 (f′/f) u′)/f with f′ = b·u′. Take ω = b × ḃ; it is perpendicular to b and ω × b = ḃ.

(M2): ω̇ = b × b″ = b × P b″. The thrust gives (−L b) × T = −L b × T_⊥ = L m ε b × P b″ = J_t b × P b″ = J_t ω̇,
using m ε L = J_t.

(M1): m r″ = m (y″ − ε b″) = m (f b − g e₃ − ε b″). The thrust gives
T − m g e₃ = m (f + ε‖ḃ‖²) b − m ε (b″ + ‖ḃ‖² b) − m g e₃ = m f b − m ε b″ − m g e₃. Equal.

(M3): ‖T‖ = m τ and ṁ = −α τ m by the definition of m.

The right-hand sides of (M1)–(M3) are locally Lipschitz in the state for a given thrust history, so the solution is
unique (Picard–Lindelöf). ∎

*Checked:* `test_flat_map_matches_finite_differences_of_the_body_axis`; and by the open-loop replay, which integrates
(M1)–(M3) numerically with the flat-map thrust as the only input and lands within 23 nm of the target on 16
problems (`solver/RESULTS-FLAT.md` §2).

## 6. Lemma 3: boundary conditions

> **Lemma 3.** If y satisfies (BC1)–(BC5), (R1) and (R2) at t = 0 and t = t_f, and b₀ is within θ_max of vertical, then
> b(0) = b₀, ḃ(0) = ḃ₀, P b″(0) = β₀, r(0) = r₀, r′(0) = v₀, and conclusions 1 and 2 of Theorem F hold.

*Proof.* A Bezier end point is the curve's value, so (R2) gives u_z(0) ≥ L_b > 0. (BC2) says u(0) is a multiple f₀ of
b₀; its z-component is positive and b₀ has positive z-component, so f₀ > 0, f(0) = f₀ and b(0) = b₀.
(BC3) is P₀ u′(0) = f₀ ḃ₀, so ḃ(0) = P₀ u′(0)/f₀ = ḃ₀, and f′(0) = f₀′.
(BC4) is P₀ u″(0) = f₀ β₀ + 2 f₀′ ḃ₀, so P b″(0) = (P₀ u″(0) − 2 f₀′ ḃ₀)/f₀ = β₀, hence T_⊥(0) = −m₀ ε β₀.
(BC1) then gives r(0) = y(0) − ε b₀ = r₀ and r′(0) = y′(0) − ε ḃ₀ = v₀.
At t_f: u_xy = 0 and u_z ≥ L_b > 0 give b = e₃, so P projects onto the horizontal plane. u′_xy = 0 gives ḃ = 0, and
then u″_xy = 0 gives P b″ = 0, so T_⊥ = 0. Finally r = y − ε e₃ = r_T and r′ = y′ − ε ḃ = 0. ∎

*Checked:* `flatcert.check_limits` reports the boundary residuals of every plan (below 1e-11).

## 7. Lemma 4: five pointwise bounds

Fix one instant. Let u, u′, u″ ∈ ℝ³ with p := u_z > 0, and let f, b, ḃ, P b″, a, ℓ, τ be given by the flat map.

> **Lemma 4.** For all real ρ, κ, k, every s ≥ sin(tilt), every 0 < L_b ≤ p and every φ, with x := u′ − ρ u,
> q ≥ ‖x‖²/p and G ≥ ‖u″ − 2ρu′ − κu − k e₃‖ + s|k| + q:
>
> - (B1) f ‖ḃ‖ ≤ ‖x‖
> - (B2) f ‖ḃ‖² ≤ q
> - (B3) f ‖P b″‖ ≤ G
> - (B4) p ≤ τ ≤ ‖( ‖u‖ + ε q/L_b ,  ε G/L_b )‖
> - (B5) 2φp − φ² ≤ f²

*Proof.* Note p = u_z ≤ ‖u‖ = f.

(B1) f ḃ = P u′ = P x because P u = 0. A projection does not increase length.

(B2) f ‖ḃ‖² = ‖P x‖²/f ≤ ‖x‖²/p ≤ q.

(B3) From the proof of Lemma 2, f P b″ = P u″ − 2 f′ ḃ. Write f′ = b·u′ = ρ f + b·x. Then
2 f′ ḃ = 2ρ P u′ + 2 (b·x) P x / f, so

    f P b″ = P(u″ − 2ρ u′) − 2 (b·x) P x / f.

First term: P(u″ − 2ρu′) = P(u″ − 2ρu′ − κu − k e₃) + k P e₃, and ‖P e₃‖ = sin(tilt) ≤ s, so its length is at most
‖u″ − 2ρu′ − κu − k e₃‖ + s|k|. Second term: b·x and P x are the parts of x along and across b, so
2 |b·x| ‖P x‖ ≤ ‖x‖², and the term is at most ‖x‖²/f ≤ ‖x‖²/p ≤ q.

(B4) τ ≥ a ≥ f ≥ p. For the upper bound, a = f + ε‖ḃ‖² ≤ ‖u‖ + ε q/f ≤ ‖u‖ + ε q/L_b by (B2), and
‖ℓ‖ = ε‖P b″‖ ≤ ε G/f ≤ ε G/L_b by (B3). The norm is monotone in both entries.

(B5) f² ≥ p² and p² − (2φp − φ²) = (p − φ)² ≥ 0. ∎

*Checked:* `test_pointwise_bounds_used_by_the_restriction` (4000 random points, random ρ, κ, k, s, L_b, φ).

## 8. Lemmas 5 and 6: every instant, and the mass

> **Lemma 5 (hull).** Let K be a convex set of points (U, U₁, U₂, auxiliaries) whose description is the same for the
> four control tuples of a span. If the four tuples, each with its own auxiliaries, lie in K, then for every t in the
> span the point ((u, u′, u″)(t), Σⱼ Bⱼ(t) auxⱼ) lies in K.

*Proof.* By (HULL) it is a convex combination of four points of K. ∎

The sets defined by (R1)–(R6) are convex (norm bounds by affine functions, one rotated cone) and their parameters
ρ, κ, φ, L_b, s, t_δ are constant on a span. So at every instant t there are numbers e₁, q, k, g₂, s_f, σ(t) = Σⱼ Bⱼ(t) σⱼ
for which (R1)–(R6) hold with (U, U₁, U₂) replaced by (u, u′, u″)(t). By (R1), sin(tilt) ≤ sin θ_max = s. So Lemma 4
applies at every instant, with q ≥ ‖x‖²/p from (R3) and G as in (R4):

    tilt ≤ θ_max                                   (R1)
    ε f ‖P b″‖ ≤ ε G ≤ t_δ (2φp − φ²) ≤ t_δ f²      (B3), (R5), (B5)     ⟹   ‖ℓ‖ ≤ t_δ f ≤ t_δ a,  i.e.  tan δ ≤ t_δ
    p(t) ≤ τ(t) ≤ σ(t)                              (B4), (R6)

*Checked:* `test_bezier_control_polygons_reproduce_every_derivative`; `test_single_solve_is_flyable_at_every_instant`
(dense grid, 2001 instants); `solver/scripts/stress_flat.py` (300 random problems, each solved with default and with random references; 458 of the 600 solves feasible, no violation).

> **Lemma 6 (mass).** Let z = ln m. For every span s and every t in it:  z_lo,s ≤ z(t) ≤ z_up,s,  hence
> T_min ≤ m(t) τ(t) ≤ T_max. Moreover m(t_f) ≥ m₀ exp(−α (h/4) Σ σ) ≥ m_dry.

*Proof.* ż = −α τ, and p ≤ τ ≤ σ(t) at every instant.
Upper bracket: z(t) ≤ z(t_s) = z₀ − α∫₀^{t_s} τ ≤ z₀ − α∫₀^{t_s} u_z = z_up,s, because ∫₀^{t_s} u_z = y′_z(t_s) − y′_z(0) + g t_s.
Lower bracket: z(t) ≥ z(t_{s+1}) = z₀ − α∫₀^{t_{s+1}} τ ≥ z₀ − α∫₀^{t_{s+1}} σ(t) dt = z_lo,s, because ∫_span Σⱼ Bⱼ σⱼ = (h/4) Σⱼ σⱼ.
Lower throttle: e^(−z) is decreasing and convex, and z_lo,s ∈ [z_min,s, z_max,s] by (R7), so
1/m(t) = e^(−z(t)) ≤ e^(−z_lo,s) ≤ c_s(z_lo,s). By Lemma 5 applied to the linear row of (R7),
p(t) ≥ T_min c_s(z_lo,s) ≥ T_min/m(t), so ‖T‖ = m τ ≥ m p ≥ T_min.
Upper throttle: 1/m(t) = e^(−z(t)) ≥ e^(−z_up,s) ≥ τ_s(z_up,s), a tangent lying below a convex function. So
σ(t) ≤ T_max τ_s(z_up,s) ≤ T_max/m(t), and ‖T‖ = m τ ≤ m σ ≤ T_max.
Fuel: z(t_f) ≥ z_lo,S = z₀ − α (h/4) Σ σ ≥ ln m_dry. ∎

*Checked:* fuel bound asserted in `test_single_solve_is_flyable_at_every_instant`; throttle range on the dense grid.

**Proof of Theorem F.** (R2) gives u_z ≥ L_b > 0 at every instant (Lemma 5), so u ≠ 0 and the flat map is defined.
Lemma 2 gives the solution and its uniqueness. Lemma 3 gives conclusions 1 and 2. Lemmas 4 and 5 give the gimbal and
tilt parts of conclusion 3, and Lemma 6 gives the throttle part and conclusion 4. ∎

## 9. The price

> **Proposition (incompleteness).** Fix b₀, ḃ₀, β₀, m₀, t_f and the references. The set of (r₀, v₀) for which (P) is
> feasible is convex and contained in the set of initial states from which the model can land within its limits.
> Whenever the latter set is not convex, the containment is strict.

*Proof.* (r₀, v₀) enter (P) only through the right-hand side of (BC1), so the feasible set of (P) in the joint space
of (r₀, v₀, variables) is convex and its projection onto (r₀, v₀) is convex. Containment is Theorem F. A convex set
cannot equal a nonconvex one. ∎

The landable set of our vehicle is not convex (Theorems A and B\* of `math/02`, machine-checked for the rate-limited
model; reproduced numerically on this model in `AUDIT-2026-11.md` §2). So (P) must refuse some landings that exist.
Where the loss comes from:

- (R2), (R7) bound the thrust from below by its vertical part, so (P) never plans to shed thrust by tilting.
- (B3) bounds the interaction of throttle changes with rotation instead of computing it.
- Control polygons contain the curves they bound.

Measured size: 0.10 % of fuel on average at the operating final time, and 0.04 to 0.22 s of extra flight time at the
minimum final time for in-air descents, up to 0.4 s on 4 s pad hops (`solver/RESULTS-FLAT.md`).

## 10. What is not proved

| item | status |
|---|---|
| Gimbal slew rate and throttle slew rate | not constrained by (P); evaluated exactly on each plan by `flatcert.check_limits`, and a replan that fails is not flown |
| Altitude floor and glide slope on the CG | imposed at sampled instants with a soft slack, as in planners B and S |
| Assumption CoP for the real vehicle | modelling assumption. Sim-plant table: ε = 1.352 m (wet), 1.340 m (75 kg), 1.321 m (70.4 kg). To be confirmed from measured mass properties |
| Rigid, lag-free gimbal; zero roll rate; no aerodynamics; exact state knowledge | outside the model; handled by the tracking loop and replanning, tested by Monte Carlo only |
| Machine checking | Lemma 1 is in Lean (constant mass). Lemmas 2 to 6 and Theorem F are proved here on paper and tested numerically, not formalised |
| Optimality | none claimed. The fuel is an upper bound; the gap to the 6-DoF optimum is measured, not bounded |
