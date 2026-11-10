# Planner F: flat convex guidance

One convex program (an SOCP) per plan, for the gimballed lander, whose every feasible point is a trajectory the
planning model can fly. No relaxation is used, so there is nothing to be "lossless" about: the guarantee comes from
the construction, not from a tightness theorem. Code: `gtpl_guidance/flat.py` (flat map, spline),
`gtpl_guidance/fcg.py` (the program), `gtpl_guidance/flatcert.py` (certificate and replay), `tests/test_flat.py`.
Results: [RESULTS-FLAT.md](RESULTS-FLAT.md).

## 1. The idea in four lines

1. Our vehicle steers with the gimbal, and a gimbal deflection pushes the vehicle sideways as well as turning it.
   That coupling is the usual reason given for 6-DoF landing being nonconvex.
2. There is one point of the vehicle that the sideways push does not accelerate: the centre of percussion,
   ε = J_t/(m L) ≈ 1.35 m above the CG. Its position y = r + ε b obeys y″ = f b − g exactly (claim FLAT,
   machine-checked: `lean/.../TVC/CentreOfPercussion.lean`, `cop_identity`).
3. So in y the gimballed vehicle is exactly a point whose thrust is locked to the body axis: the "fixed engine plus
   independent torque" model, with nothing assumed away. The body axis is the direction of y″ + g, and the gimbal
   angle and throttle are algebraic functions of y and its first four derivatives (the system is differentially flat).
4. Planning y(t) directly makes the dynamics linear and satisfied identically. What remains nonconvex is the set of
   actuator limits, and those are replaced by convex *restrictions* (inner approximations), never relaxations.

## 2. Model

Rigid axisymmetric body, J = diag(J_t, J_t, J_z). Thrust vector T applied at the gimbal pivot, L below the CG on the
body axis b. Roll rate zero (RCS). Mass ṁ = −α‖T‖. World z up, gravity g = 9.80665.

    m r″ = T − m g e₃,        J_t ω̇ = (−L b) × T,        ḃ = ω × b,   ω ⊥ b.

**Assumption CoP.** ε = J_t(m)/(m L(m)) is constant along the flight. The sim-plant table (`context/vehicle.md` §1)
gives ε = 1.352 m wet, 1.340 m at 75 kg and 1.321 m at 70.4 kg, so over a descent (80 → 75 kg) it holds to 1 %.
Planners B and S instead freeze J_t and L at their initial values, which makes ε = J_t/(m L) drift by +6 % over the
same descent. Section 8 measures what each assumption costs against the plant table.

Write T = T_a b + T_⊥ with T_⊥ ⊥ b. Torque balance gives T_⊥ = −(J_t/L) P b″ with P = I − b bᵀ (Lemma 8.1 of
math/04). Substituting,

    y := r + ε b,        y″ = (T_a/m − ε|ḃ|²) b − g e₃.                                   (FLAT)

## 3. The flat map

Given y(t) ∈ C⁴, put u = y″ + g e₃, and write u′, u″ for its derivatives. Then, wherever u ≠ 0,

| quantity | formula |
|---|---|
| specific force, body axis | f = ‖u‖, b = u/f |
| body rate | ḃ = P u′/f, ḟ = b·u′ |
| angular acceleration | P b″ = P(u″ − 2(ḟ/f) u′)/f |
| axial specific thrust | a = f + ε‖ḃ‖² (T_a = m a) |
| lateral specific thrust (gimbal) | ℓ = −ε P b″, gimbal angle δ with tan δ = ‖ℓ‖/a |
| thrust per unit mass | τ = √(a² + ‖ℓ‖²), ln m(t) = ln m₀ − α∫₀ᵗ τ |
| CG | r = y − ε b, v = y′ − ε ḃ |

The mass is a quadrature of the plan, so no mass fixed-point iteration is needed. `flat.flat_map` implements this;
`tests/test_flat.py::test_centre_of_percussion_identity_with_flat_controls` checks it against the rigid-body
derivative `dynamics.deriv` to 1e-9.

## 4. The convex program

**Variable.** y(t) is a clamped uniform quintic B-spline with S spans (S + 5 coefficients per axis; S = 16 by
default, 63 scalars). Quintic means y ∈ C⁴, so the gimbal angle and the throttle are continuous.

**Dynamics.** None to impose. Every spline is a trajectory of (FLAT).

**Boundary conditions, all linear in the coefficients.** With b₀, ḃ₀ the current body axis and its rate, and β₀ the
angular acceleration P b″(0) that the gimbal's current deflection produces:

    y(0) = r₀ + ε b₀,   y′(0) = v₀ + ε ḃ₀,
    u(0) = f₀ b₀,                                   f₀ := b₀·u(0)     (attitude)
    u′(0) − (b₀·u′(0)) b₀ = f₀ ḃ₀                                     (body rate)
    u″(0) − (b₀·u″(0)) b₀ = f₀ β₀ + 2 (b₀·u′(0)) ḃ₀                   (gimbal cannot jump)
    y(t_f) = target + ε e₃,  y′(t_f) = 0,  u_xy(t_f) = u′_xy(t_f) = u″_xy(t_f) = 0   (at rest, upright, no rate, gimbal centred)

These are linear because f₀ and ḟ₀ = b₀·u′(0) are themselves linear in the coefficients. The initial position and
velocity enter affinely, as in LCvx; the initial attitude enters through coefficients.

**Limits, as a restriction on control tuples.** On each span, u, u′, u″ are polynomials of degree 3, 2, 1. Their
Bezier control points, degree-elevated to cubic, give four tuples (U, U₁, U₂) per span with

    (u, u′, u″)(t) = Σⱼ Bⱼ(t) (U, U₁, U₂)ⱼ,    Bⱼ ≥ 0,  Σⱼ Bⱼ = 1.                          (HULL)

Per span there are four given scalars: ρ, κ, φ > 0 and L_b > 0 (the *references*, section 6). With p = e₃·U, and
auxiliary variables e₁, q, k, g₂, s_f, σ per tuple, the program imposes

| # | constraint | what it guarantees | proof |
|---|---|---|---|
| R1 | ‖U_xy‖ ≤ tan θ_max · p | tilt ≤ θ_max | exact: tan(tilt) = ‖u_xy‖/u_z |
| R2 | p ≥ L_b, p ≥ T_min·c(z_lo) | T ≥ T_min | T/m = τ ≥ a ≥ f ≥ p; mass bound of §5 |
| R3 | ‖U₁ − ρU‖ ≤ e₁, e₁² ≤ q p | f‖ḃ‖ ≤ e₁, f‖ḃ‖² ≤ q | B1, B2 |
| R4 | ‖U₂ − 2ρU₁ − κU − k e₃‖ + s_θ\|k\| ≤ g₂, G := g₂ + q | f‖P b″‖ ≤ G | B3 |
| R5 | ε G ≤ tan δ_plan (2φp − φ²) | gimbal angle ≤ δ_plan | B5 |
| R6 | ‖U‖ ≤ s_f, ‖(s_f + εq/L_b, εG/L_b)‖ ≤ σ, σ ≤ T_max·t(z_up) | T ≤ T_max | B4, §5 |

s_θ = sin θ_max. The objective is ∫σ, an upper bound on the fuel divided by α (plus a soft penalty on the sampled
state constraints, §7).

**The bounds.** Let x = u′ − ρu. For any real ρ, κ, k, any s ≥ sin(tilt), and p = u_z ≤ f:

- **B1.** f ḃ = P u′ = P x (because P u = 0), so f‖ḃ‖ ≤ ‖x‖.
- **B2.** f‖ḃ‖² = ‖P x‖²/f ≤ ‖x‖²/p.
- **B3.** From u″ = f̈ b + 2ḟ ḃ + f b″: f P b″ = P u″ − 2ḟ ḃ. Write ḟ = ρf + b·x. Then
  f P b″ = P(u″ − 2ρu′) − 2(b·x) P x/f. First term: P(u″ − 2ρu′) = P(u″ − 2ρu′ − κu − k e₃) + k P e₃, and
  ‖P e₃‖ = sin(tilt) ≤ s, so it is at most ‖u″ − 2ρu′ − κu − k e₃‖ + s\|k\|. Second term:
  2\|b·x\|‖P x‖ ≤ ‖x‖², so it is at most ‖x‖²/f ≤ ‖x‖²/p.
- **B4.** a = f + ε‖ḃ‖² ≤ f + ε‖x‖²/(f p) ≤ ‖u‖ + ε q/L_b, and ‖ℓ‖ = ε‖P b″‖ ≤ ε G/f ≤ ε G/L_b, using f ≥ p ≥ L_b.
- **B5.** f² ≥ p² ≥ 2φp − φ² (tangent of a convex function). So R5 gives ε f‖P b″‖ ≤ tan δ_plan f², that is
  ‖ℓ‖ ≤ tan δ_plan · f ≤ tan δ_plan · a. A gimbal cone of half-angle δ_plan lies inside the per-axis box (claim N1).

`tests/test_flat.py::test_pointwise_bounds_used_by_the_restriction` checks B1 to B5 on 4000 random points.

**Every instant, not only nodes.** Each of R1 to R6 is a convex set in (U, U₁, U₂, auxiliaries) whose parameters are
constant on the span. By (HULL), the point (u, u′, u″)(t) with the Bernstein-weighted auxiliaries lies in the same
set for every t in the span. So the bounds B1 to B5 apply at every instant. No inter-node violation is possible, and
none has to be checked.

## 5. Mass

z = ln m obeys ż = −ατ. Two affine functions of the variables bracket it:

    z_up(t) = z₀ − α ∫₀ᵗ p = z₀ − α (y′_z(t) − y′_z(0) + g t)        (τ ≥ p)
    z_lo(t) = z₀ − α ∫₀ᵗ σ                                           (τ ≤ σ; ∫_span Σ Bⱼσⱼ = (h/4) Σ σⱼ)

and z_lo ≤ z ≤ z_up. On span s the program uses z_up at the span start and z_lo at the span end, which are valid for
the whole span because z decreases.

- Lower throttle: p ≥ T_min · c(z_lo), where c is the chord of e^(−z) over an interval [z_min, z_max] that the program
  forces z_lo into. A chord lies above a convex function, so p ≥ T_min e^(−z) = T_min/m.
- Upper throttle: σ ≤ T_max · t(z_up), where t is a tangent of e^(−z). A tangent lies below, so σ ≤ T_max/m.

The interval is 6 % wide over 8 s, so chord and tangent are within 0.05 % of e^(−z). Fuel: m₀ − m(t_f) ≤
m₀(1 − e^(−α∫σ)), which the objective minimises. Dry mass: z_lo(t_f) ≥ ln m_dry.

## 6. References: tightness, not feasibility

ρ, κ, φ, L_b are free parameters of the restriction. **Any values give a sound program.** They decide only how much
of the true feasible set the restriction keeps:

| reference | best value | effect when it is off |
|---|---|---|
| ρ | ḟ/f, the throttle's log-rate | throttle changes are charged against the gimbal budget (R3, R4) |
| κ | (f̈ − 2ρḟ)/f − ‖ḃ‖² | same, for throttle curvature |
| φ | p | less gimbal authority credited (R5); none lost at p = φ |
| L_b | just below p | lateral thrust and centripetal terms over-estimated (R6) |

Default (no information): ρ = κ = 0, φ = 7.5 m/s², L_b = T_min/m₀. In closed loop the previous plan supplies them.
Because they are scalars about the *throttle* history, not a linearisation point in state space, a stale or wrong
reference cannot make a plan unflyable and cannot make an iteration diverge. `FCG.plan(refine=k)` re-solves k times
with references from the best plan so far and keeps the cheapest; each pass is flyable, so it can stop any time.
One pass is already within about 0.1 % of the refined fuel (RESULTS-FLAT.md §1).

This is the difference from successive convexification. SCvx linearises the dynamics about a trajectory, so its
iterates satisfy the true dynamics only at convergence, and it needs virtual control, a trust region, penalty weights
and an initial trajectory. Planner F has none of these.

## 7. What is guaranteed, and what is not

Guaranteed for every feasible point of the SOCP, at every instant, for the planning model of §2:

- exact dynamics, exact initial position, velocity, attitude, body rate and gimbal deflection;
- touchdown at the target at rest, upright, with zero body rate and a centred gimbal;
- throttle within [T_min_plan, T_max_plan], gimbal within the δ_plan cone, tilt within θ_max;
- true fuel at most the program's bound.

Not part of the convex guarantee (checked on every plan by `flatcert.check_limits`):

- **gimbal slew and throttle slew.** They depend on y⁽⁵⁾. No convex bound is imposed; the certificate evaluates them
  exactly on a dense grid. Observed peaks: 42°/s against a 100°/s limit and about 150 N/s against 2000 N/s
  (RESULTS-FLAT.md).
- **altitude floor and glide slope** on the CG. Imposed at sampled points with a soft slack, as planners B and S do.
  The altitude bound used is conservative (r_z ≥ y_z − ε).

Outside the model: the CoP assumption (§2), a rigid and lag-free gimbal, zero roll rate, no aerodynamics. The closed
loop handles these, as for every other planner here.

## 8. Relation to the impossibility theorem

Theorem A and B\* (math/02, Lean) say: no convex program that takes (r₀, v₀) affinely is both *sound* (feasible only
if a flyable plan exists) and *complete* (feasible whenever one exists), because the set of landable initial states
is not convex. LCvx is such a pair for 3-DoF. Planner F takes (r₀, v₀) affinely, so the theorem applies to it: it is
sound, therefore it cannot be complete. The theorem does not say a single convex program cannot be sound.

Where the completeness goes:

- **Minimum throttle while tilted** (R2 uses u_z in place of ‖u‖): costs a factor cos(tilt), at most 6 % of
  T_min at 20°.
- **Throttle and rotation at the same time** (R3, R4): the cross term is bounded, not computed. With good references
  the loss is second order.
- **Control polygons** are slightly larger than the curves they bound.

Measured cost: at the operating final time (minimum + 0.5 s) F uses 0.0 to 0.25 % more fuel than the 6-DoF optimum.
Its minimum feasible final time is 0.03 to 0.22 s later than the true minimum on in-air descents, and up to 0.5 s
later on pad hops (RESULTS-FLAT.md §1, §3). When F reports infeasible it returns no plan; it never returns a plan that
cannot be flown.
