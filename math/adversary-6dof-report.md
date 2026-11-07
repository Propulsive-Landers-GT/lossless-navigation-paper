# Adversary-6DOF report: does the impossibility extend to torque-coupled (M3) and 6DOF (M4) models?

Author: [adversary-6dof]. Target: Claim B6 ("6DOF inherits B": "6DOF admissible set maps into the 5DOF one; planar arcs are
6DOF-realizable", math/00 §0, §4 remarks). Coordinated with [adversary] in comms/threads/6dof-models.md (they own M1 steps (1)–(5),
Thm A definitions and B*; I own M2/M3/M4). Numerics: numerics/adversary-6dof/ (own venv; casadi/ipopt; full rigid body, quaternion attitude,
Euler equations with J = diag(Jt,Jt,Ja), roll RCS torque, cone or box gimbal, optional gimbal-rate limit).

## 0. Verdict table

| # | Item | Verdict |
|---|---|---|
| V1 | B6 for **kinematic** 6DOF (ω is a control, ‖ω⊥‖ ≤ ω̄, roll arbitrary) | **SURVIVES** (inclusion and realizability both hold; Thm K) |
| V2 | B6 for any model in which ω is a **state** (Euler equations), even with unlimited torque authority | **BROKEN as argued**: P_u needs ‖ḃ(0+)‖ = ω̄ but ω⊥(0) = 0 (agrees with [adversary] thread item 1). |
| V3 | **Pure-TVC M3** (gimbal = the only pitch/yaw torque; GTPL): are P_u, P_{−u} realizable? | **BROKEN.** Gimbal outward ⇒ body accelerates *inward* (Lemma 1). The extreme arcs, the envelope φ(s) = ωs, and the point M are all wrong for M3; M is not even in conv R_M3. |
| V4 | M3 with **independent transverse torque** (RCS/wheels), ω state, axisymmetric J, any roll/coning | **FIXED**: Thm D (min-vertical face, terminal attitude free) and Thm D* (dive-then-brake face, terminal attitude b(tf)=e_z, ω(tf)=0 allowed). Envelope Φ(s) = ∫₀ˢ min(ᾱr, ω̄)dr is quadratic then linear; rigidity holds ("length = distance"). |
| V5 | Pure-TVC M3/M4 (the GTPL-realistic model): is R (hence F) nonconvex? | **Partly FIXED, otherwise OPEN.** Rigorous for terminal ω⊥(tf)=0 with tilt free (Thm E₀, §3.5/§6, via the corrected centre-of-percussion comparison; assumes ε const, ω₃ ≡ 0, unlimited gimbal rate). OPEN for upright at rest, r_z ≥ 0, rate-limited gimbal (now with [proof-tvc]). Numerically CONFIRMED in every tested case (§4). The gap is high order (∝ tf^≈8 at small tf). |
| V6 | Roll + pitch/yaw coning reaching M (or the corrected M_D) | **REFUTED** for kinematic and decoupled models (gyroscopic term does no work on ‖ω⊥‖; rigidity unaffected). Caveat: needs Jxx = Jyy; with non-axisymmetric J roll can pump transverse rate (open, tiny for GTPL). With terminal attitude constraints spin enables loops/U-turns, which matter only quantitatively. |
| V7 | Box gimbal (GTPL ±15°/axis) instead of cone | **SURVIVES with δ := δ* = corner angle** (arccos(cos²15°) = 21.1°), u restricted to diagonal directions; only the π-rotation symmetry G = R_π G is used. Late "brake" phases use the inscribed angle δ_in = 15°. |
| V8 | Faithfulness of the 6DOF statement (boundary data, ω/attitude BCs, tilt caps, throttle/gimbal rate) | **NEEDS FIX** (§5): ω⊥(0)=0 and b(0)=e_z must be stated; terminal-attitude case needs D*/B*; active tilt cap or gimbal-rate limit can break rigidity; slice argument for extra data. |

**Bottom line for the project.** The impossibility theorem is rigorous for kinematic-attitude 5DOF/6DOF and for rigid-body models
with an attitude-torque actuator independent of the gimbal. For the GTPL vehicle as it is (pitch/yaw torque only from TVC), the
statement "F is nonconvex" is numerically solid but **not proved**; the final theorem must not claim it as FORMALIZED/CONFIRMED.
Quantitatively the TVC obstruction is much weaker (gap ≈ 0.06 m/s at tf = 1 s vs metres/second in M1), which matters for any ε-lossless claim.

---

## 1. Model and two basic lemmas

Rigid body, attitude R(t) ∈ SO(3), body thrust axis b = R e₃, body rates ω = (ω₁, ω₂, ω₃), J = diag(Jt, Jt, Ja).
Engine pivot at −L b. Thrust T ∈ [ρ1, ρ2], direction d = R d_b with d_b ∈ G (gimbal set in body frame; cone: angle(d_b, e₃) ≤ δ;
box: per-axis angles in [−δ, δ]). Transverse gimbal vector g := d − (d·b) b.
Torque: τ = (−L b) × (T d) + τ_rcs = −L T (b × g) + τ_rcs, with τ_rcs = τ₃ b (roll RCS) in pure TVC, or τ_rcs = τ⊥ + τ₃ b
with ‖τ⊥‖ ≤ τ̄ in the decoupled model. Euler: J ω̇ + ω × Jω = τ. Velocity increment Δv = ∫ a d, a = T/m, ṁ = −αT.

**Lemma 0 (speed lemma).** For axisymmetric J: (Jt/2) d/dt ‖ω⊥‖² = ⟨ω⊥, τ⊥⟩, where ω⊥ = (ω₁, ω₂) and ‖ḃ‖ = ‖ω⊥‖.
*Proof.* Euler components: Jt ω̇₁ + (Ja−Jt) ω₂ω₃ = τ₁, Jt ω̇₂ − (Ja−Jt) ω₁ω₃ = τ₂. Multiply by ω₁, ω₂ and add: the gyroscopic terms cancel.
ḃ = R(ω × e₃) = R(ω₂, −ω₁, 0). ∎
Consequences: (i) roll spin cannot increase the transverse rate (it acts like a magnetic force, curving the path of b without doing work);
(ii) ‖ḃ(s)‖ ≤ ‖ω⊥(0)‖ + ∫₀ˢ ‖τ⊥‖/Jt.
In covariant form: Jt ∇ₜḃ = b × τ⊥-part (= −L T g + b×τ⊥,rcs) + Ja ω₃ (b × ḃ).

**Lemma 1 (sign of the TVC torque).** In pure TVC, Jt ∇ₜḃ = −L T g + Ja ω₃ (b × ḃ). So with ω₃ = 0 the body axis accelerates in the
direction **opposite** to the gimbal deflection g. (Proof: b × (b × g) = −g for g ⊥ b.) Physically: thrust deflected toward u at the tail
pushes the tail toward u and the nose toward −u.

**Corollary (V3).** The math/00 extreme arc P_u (b tilting toward u at rate ω̄ from t = 0, d tilted *further* toward u by δ) violates M3
in two independent ways: (a) it needs ‖ḃ(0+)‖ = ω̄ > 0 = ‖ω⊥(0)‖ with ω absolutely continuous; (b) along it g points toward +u for all s,
so by Lemma 1 the tilt toward u is decelerated (ḃ·u decreases) — it cannot even be sustained. Hence P_u ∉ R_M3. Moreover
M ∉ conv R_M3 in general: by Lemma 0 every M3 trajectory has tilt(b(s)) ≤ Φ(s) = ∫₀ˢ min(ᾱ r, ω̄) dr with ᾱ = L ρ2 sin δ*/Jt (any
s with ᾱs < ω̄ gives Φ(s) < ω̄ s), so ∫ a d_z ≥ ∫ a1 cos(δ* + Φ) > ∫ a1 cos(δ + ω̄ s) = M_z for δ* = δ. The face of conv R_M3 lies
strictly above M. The midpoint argument of math/00 is therefore vacuous for M3: it compares R_M3 with a point it never approaches.
The inclusion R_M4 ⊆ R_M1 (when |ω⊥| ≤ ω̄ is imposed) is true but useless: M ∉ R_M1 ⊇ R_M4 gives M ∉ R_M4, which is not a nonconvexity
witness because P_u ∉ R_M4.

**Lemma 2 (no simultaneous envelope in pure TVC).** In pure TVC the pointwise bound angle(d(s), e₃) ≤ δ* + Φ(s) is never attained on a set
of positive measure near s = 0: attaining it needs g outward (toward the tilt direction u) and ḃ·u maximal, but by Lemma 1 outward g
gives d(ḃ·u)/dt = −L T |g|/Jt < 0. So every argument of the form "min-vertical ⇒ pointwise envelope ⇒ rigidity" fails for pure TVC.
The optimal trajectories are global trade-offs (numerically: gimbal fully *inward* first to spin the body up, then flipped fully *outward*; §4).

---

## 2. Theorems that hold (corrected B6)

Standing assumptions: b(0) = e₃, ω⊥(0) = 0 (roll rate ω₃(0) arbitrary), gimbal set G compact with R_π G = G (R_π = rotation by π
about the body axis), δ* := max angle(G, e₃) ∈ (0, π/2) attained at c ∈ G (then also at R_π c), δ_in := largest cone inside G.
Throttle histories form a set independent of attitude, a = T/m > 0 (ρ1 > 0). Boundary data θ = (r0, v0), all other data fixed.
F_tf = {θ : landing feasible}, R = {Δv}, proj_{v0} F_tf = −g tf − R.

**Rotation-midpoint lemma** (as [adversary], math/01 §B*). F, R are invariant under the rotation R_π about e₃ (for the box: R_π maps the
box to itself; initial roll and gimbal state are carried along). If R is convex and x ∈ R then (x + R_π x)/2 ∈ R. Hence: if some linear
functional ℓ invariant under R_π has maximizers on R and *every* maximizer has nonzero lateral component, R (and F_tf) is not convex.

### Theorem K (kinematic 6DOF; B6 SURVIVES)
Model: attitude R(t) with ω(t) a measurable control, ‖ω⊥‖ ≤ ω̄, ω₃ arbitrary; d ∈ R(t)G. Then b = Re₃ is ω̄-Lipschitz on S² (M1), and
conversely every ω̄-Lipschitz b with b(0) = e₃ is realized (ω⊥ := b × ḃ, ω₃ := 0, a.e.). The gimbal-set argument: math/00 steps (1)–(5)
go through with δ replaced by δ* (angle(d, b) ≤ δ* still gives d·e₃ ≥ cos(δ*+φ)); equality forces d at a δ*-extreme point of G, coplanar
and outward; P_u is realized with zero roll by taking u = horizontal direction of the corner c at t = 0 (and −u for R_π c). Same for B*.
So Thm B and B* hold for kinematic 6DOF with box or cone gimbal. ∎

### Theorem D (decoupled torque, terminal attitude free)
Model: Euler equations with axisymmetric J; transverse torque τ⊥ with ‖τ⊥‖ ≤ τ̄ independent of the gimbal (RCS, wheels; the TVC torque
may be *added* only if bounded and the gimbal deflection is not otherwise constrained — see remark), any roll torque, optional
‖ω⊥‖ ≤ ω̄, gimbal free in G (or rate-limited from a centred start, see remark). Let ᾱ = τ̄/Jt and Φ(s) = ∫₀ˢ min(ᾱr, ω̄)dr.
Assume δ* + Φ(tf) ≤ π/2 and m0 − αρ1 tf ≥ m_dry. Then R and F_tf are not convex.
*Proof.* (1) Lemma 0 ⇒ ‖ḃ(s)‖ ≤ min(ᾱs, ω̄) ⇒ φ(s) := angle(e₃, b(s)) ≤ L(b|[0,s]) ≤ Φ(s).
(2) Spherical triangle inequality: d·e₃ ≥ cos(δ* + Φ(s)) ≥ 0; with a ≥ a1: V := ∫ a d_z ≥ V* := ∫ a1 cos(δ* + Φ).
(3) V* is attained: radial bang arc (τ⊥ = τ̄ about e₃ × u until ω̄, then coast; no roll), d at the corner R(s)c (computation: with
R(s) = rotation about e₃×u by Φ(s), R(s)c = (sin(Φ+δ*) u, cos(Φ+δ*))), T = ρ1. Call its Δv P_u; P_{−u} uses R_π c.
(4) Equality V = V* forces a = a1 a.e. and d_z = cos(δ*+Φ) a.e., hence φ(s) = Φ(s) a.e., hence everywhere (continuity).
(5) Rigidity: L(b|[0,s]) ≥ φ(s) = Φ(s) ≥ L(b|[0,s]), so b|[0,s] has length equal to the distance between its endpoints; it is a
minimizing geodesic (unique since Φ(s) < π), for every s. Nested minimizing geodesics from e₃ share one direction u. Equality in the
triangle inequality puts d in the plane (e₃, u), outward: d = (sin(δ*+Φ) u, cos(δ*+Φ)).
(6) So every point of R with vertical V* equals (∫ a1 sin(δ*+Φ)) u + V* e₃ for a unit u; none has zero lateral part. Rotation-midpoint lemma ⇒
R not convex; F_tf not convex since its v0-projection is an affine image of R. ∎
Remarks. (a) Roll/coning (V6): handled by Lemma 0; no assumption on ω₃. (b) Gimbal rate limit with the gimbal centred at t=0:
replace δ* by δ*(s) = max angle of the reachable gimbal set at time s (box: arccos(cos²(min(γ̇s, δ)))), attained along the diagonal, still
simultaneous with the body arc; the proof is unchanged. (c) If ω⊥(0) ≠ 0 is *data*, take the slice ω⊥(0) = 0: a slice of a convex set by an
affine subspace is convex, so nonconvexity of the slice suffices. (d) Without axisymmetry (Jxx ≠ Jyy, products of inertia) Lemma 0 fails
when ω₃ ≠ 0; the theorem then needs either ω₃ ≡ 0 enforced or a perturbation argument (OPEN, effect O(|Jxx−Jyy| ω₃) — tiny for GTPL).

### Theorem D* (decoupled torque, terminal attitude constrained) — the torque analog of [adversary]'s B*
Same model plus b(tf) = e₃, ω⊥(tf) = 0 (roll free), gimbal rate unlimited. Choose s* > 0 with ᾱ s*² ≤ δ_in, s*·ω̄-cap inactive, 4s* ≤ tf.
Functional ℓ = α_z r0z + β_z v0z with weight w(s) = α_z(s − s*), α_z > 0 (math/01 §B*). Then F_tf is not convex.
*Proof.* Freeze the throttle T* of a maximizer (throttle set independent of attitude). Early: ∫₀^{s*} w a* d_z ≤ ∫₀^{s*} w a* cos(δ*+Φ) (w<0;
step (1)–(2) of Thm D). Late: ∫_{s*}^{tf} w a* d_z ≤ ∫_{s*}^{tf} w a*. Both bounds are attained by ONE attitude history: the bang arc on
[0,s*] (tilt ᾱs*²/2, rate ᾱs*), then reverse torque for s* (stops at tilt ᾱs*² ≤ δ_in), then a rest-to-rest return in 2s*; tilt ≤ δ_in
throughout so d = e₃ ∈ R(s)G is available on (s*, tf]. Hence every maximizer attains both bounds; early equality gives the Thm D rigidity on
[0, s*], late equality gives d = e₃ a.e. Lateral Δv = (∫₀^{s*} a* sin(δ*+Φ)) u ≠ 0. Rotation-midpoint lemma. ∎ (Existence of maximizers:
relaxed controls + Filippov; the maximizing d is unique a.e. so relaxed maximizers are ordinary, as in math/01 §B*.)
State constraints (altitude, glide slope, tilt cap) are handled exactly as in B* (late full-throttle braking).
Not covered: gimbal-rate limits (gimbal state couples early and late phases) — OPEN.

---

## 3. Pure TVC (GTPL-realistic M3/M4): what is and is not known

### 3.1 Why both face arguments fail
- Min-vertical face: Lemma 2.
- Dive-then-brake (B*): the late phase wants d = e₃ with the body tilted. That needs g pointing *toward the vertical* (i.e. −u), whose
  torque tilts the body further: with d ≡ e₃, φ̈ = (L T/Jt) sin φ — an inverted pendulum. The late bound d_z ≤ 1 is unattainable after any
  early tilt (only on the separatrix, in infinite time), so early and late do not decouple.

### 3.2 Angular-momentum identity
With pure TVC, ω₃ ≡ 0 (or axisymmetric) and ω⊥(0) = ω⊥(tf) = 0: ∫₀^{tf} T (b × g) dt = 0 (exactly; integrate Euler). So with terminal
rest attitude the net lateral thrust impulse is generated only through body tilt: to first order, ∫ T g_h = O(tilt·|g|). The lateral part of
Δv at a vertical-minimizer is small (second order) — this is why the TVC gap is much smaller than the M1 gap.

### 3.3 Is the corrected witness point reachable? (numerics, §4)
Bottom-face test: V_min = min Δv_z over R, and V₀ = min{Δv_z : Δv_lat = 0}. R convex ⇒ every horizontal slice of R contains its centre
(rotation-midpoint lemma) ⇒ V₀ = V_min. So V₀ > V_min is a nonconvexity certificate (modulo discretization: the NLP is an inner
approximation, so its V₀ is an upper bound on the true V₀; refinement in N is used as the check).

### 3.4 Small-tf asymptotics (proof programme for pure TVC, rate-unlimited cone gimbal)
Scale ε = tf, K = L ρ1 sin δ / Jt. Leading order forces T = ρ1, |g| = sin δ (direction n(s), relaxed |n| ≤ 1). Body tilt (tangent-plane)
B̈ = −K n + O(ε²K²), B(0) = Ḃ(0) = 0. d_z = cos δ − sin δ ⟨n, B⟩ + O(|B|²), so
V = cos δ ∫ a − sin δ ∫ a ⟨n, B⟩ + O(ε⁵) and the vertical problem reduces to the limit problem
  LP1 (attitude free): maximize ∫₀¹ ⟨n, B⟩ = ∫|A|² − ⟨A(1), ∫A⟩, A(x) = ∫₀ˣ n, |Ȧ| ≤ 1, A(0) = 0;
  LP2 (rest-to-rest): maximize ∫ |Ḃ|², |B̈| ≤ 1, B, Ḃ = 0 at both ends.
Scalar LP1: the one-switch family A = min(x, 2c − x) gives J(c) stationary and maximal at c = 1/2, J = 1/12 (Σ = A(1) = 0: equal time
inward/outward). Scalar LP2: triangle-wave Ḃ (switches at 1/4, 3/4), J = 1/48. Lateral at the limit minimizer:
Δv_lat ≈ a0 [sin δ ε Σ + cos δ ∫ B] (+ mass-variation terms β² ε³, β = αρ1/m0), nonzero along u with |∫B| = K ε³/32 (LP2) —
mass terms are 10⁻⁶ smaller for GTPL. A rigorous theorem needs (i) the vector (2D) rigidity of LP1/LP2 maximizers (numerically checked,
§4; analytic proof OPEN) and (ii) a Γ-convergence/stability estimate. Status: CLAIMED (sketch).

### 3.5 The centre-of-percussion (flat-output) reduction (orchestrator, CLAIMS row FLAT) — attack and repair
**Identity (CONFIRMED).** ε := Jt/(mL), y := r + ε b. With ω₃ ≡ 0 and ε constant:
ÿ = (T cos μ/m − ε‖ω⊥‖²) b − g =: f b − g. Proof: ε b̈ = ε∇ḃ − ε‖ḃ‖² b = −T_⊥/m − ε‖ω⊥‖² b by Lemma 1, so the gimbal's lateral force cancels.
Independent numerical check: numerics/adversary-6dof/flat_check.py, full quaternion/Euler, random controls, tf = 2 s. Residual 9·10⁻⁹.
Corrections: roll spin adds ε(Ja ω₃/Jt)(b × ḃ) (residual 1.5·10⁻² with ω₃ ≈ ±0.6 rad/s), and varying ε(m) adds 2ε̇ḃ + ε̈b (residual 6·10⁻³).
GTPL's true ε is nearly constant (1.352 wet → 1.325 dry), but the theorem must *assume* ε constant.

**BREAK of the claimed conclusion.** "F_TVC is a translate of F_y" needs b(tf), ω(tf) prescribed, so that y(tf) = ε e₃ and ẏ(tf) = 0.
The comparison trajectory (same T, |μ|, always accelerating outward) violates those terminal conditions.
With terminal attitude free, v0z = g tf + ε ḃ_z(tf) − ∫ f b_z. The boundary term is ordered against the comparison, because the planar arc has the more negative ḃ_z(tf).
So the lemma as posed proves nonconvexity only for "bring the centre of percussion to rest", which is not the landing set.

**FIX: Theorem E₀ (pure TVC, terminal rate zero, tilt free).** Assume:
- ε constant, ω₃ ≡ 0, J axisymmetric;
- gimbal rate unlimited (cone, or box used along a diagonal);
- b(0) = e₃, ω⊥(0) = 0;
- terminal r = v = 0 and ω⊥(tf) = 0, b(tf) free;
- regime: length(b) < π along all trajectories (e.g. Lρ2 sin δ* tf²/(2Jt) < π; only monotonicity of cos on [0,π] is used since f_p = f_q), and f ≥ 0, which holds if a rate cap ‖ω⊥‖ ≤ ω̄ with ε ω̄² ≤ ρ1 cos δ*/m0 is imposed, or tf is short enough that ε(Lρ2 sin δ* tf/Jt)² ≤ ρ1 cos δ*/m0.

Then F_tf is not convex.
*Proof.*
1. Here proj_{v0} F_tf = g tf e₃ − R_y with R_y = {∫ f b}, because y(tf) = ε b(tf) only enters the position, which is projected out, and ẏ(tf) = 0.
2. Comparison: given q, let p be the planar meridian with the same T and |μ| and ω_p := ‖ω⊥,q‖. It is realized in relaxed controls by chattering the gimbal sign at full |μ|; the speed lemma gives |d‖ω_q‖/dt| ≤ LT sin|μ|/Jt.
   Then f_p = f_q, φ_p = length(b_q) ≥ angle(b_q, e₃), and ω_p(tf) = 0.
   So f_p cos φ_p ≤ f_q b_{z,q}, with strict inequality wherever length > angle.
3. Hence every relaxed minimizer of ∫ f b_z is a meridian (one u), and it rotates, since v ≡ 0 is strictly improvable.
   Its lateral part is ∫ f sin φ u ≠ 0.
4. Relaxed minimizers exist (Filippov) and cl R = R_relaxed. The rotation-midpoint lemma on cl R gives the result. ∎

Still OPEN in pure TVC:
- upright terminal b(tf) = e₃, because φ_p(tf) = length > 0;
- gimbal-rate limits, because sign chattering is not admissible;
- ω₃ ≠ 0, because the gyroscopic force has a vertical component (b×ḃ)_z ≠ 0 off-meridian and can lower the cost;
- the min-throttle witness lies underground for GTPL ([adversary] BOARD 23:50).

With b(tf) = e₃, ω(tf) = 0 the problem is *exactly* the y-model with rest-to-rest attitude. Its small-tf limit is:
maximize ε∫|Ḃ|² + (a0 cos δ/2)∫|B|² s.t. |B̈| ≤ K, B, Ḃ = 0 at both ends. This matches LP2 of §3.4.
Planar rigidity of this LP plus a stability estimate would close the realistic case.

---

## 4. Numerics (numerics/adversary-6dof/)
All runs use the full rigid body: quaternion attitude, Euler equations with J = diag(63.6, 63.6, 3.74), L = 0.589 m, roll RCS ±3 N m (roll free).
Other settings: GTPL wet m0 = 79.88 kg, 400–1000 N, α = 5.66e-4, piecewise-constant controls, RK4 multiple shooting, ipopt, 7 or more starts.
Test: the bottom face of R. V_min = min Δv_z, and V₀ = min{Δv_z : Δv_lat = 0}. V₀ > V_min ⇒ R is nonconvex (§3.3).

| tf [s] | gimbal | gimbal rate | terminal attitude | V_min [m/s] | lat at min | V₀(lat=0) | **gap** | max tilt |
|---|---|---|---|---|---|---|---|---|
| 0.5 | cone 15° | ∞ | free | 2.40545 | 0.046 | 2.40567 | 2.3e-4 | 3.8° |
| 0.75 | cone | ∞ | free | 3.57365 | 0.166 | 3.57936 | 5.7e-3 | 9.2° |
| 1.0 | cone | ∞ | free | 4.67692 | 0.425 | 4.73844 | 6.2e-2 | 17.9° |
| 1.0 | cone | 100°/s | free | 4.72833 | 0.392 | 4.78693 | 5.9e-2 | 15.6° |
| 1.0 | box ±15° | ∞ | free | 4.36440 | 0.533 | 4.57338 | 2.1e-1 | 24.9° |
| 1.0 | cone | ∞ | upright at rest | 4.81451 | 0.144 | 4.83066 | 1.6e-2 | 3.4° |
| **1.0** | **box ±15°** | **100°/s** | **upright at rest** | 4.81513 | 0.140 | 4.89357 | **7.8e-2** | 3.6° |
| 2.0 | cone | 100°/s | upright at rest | 9.45557 | 0.947 | 9.63250 | 1.8e-1 | 12.0° |

- Robustness, row in bold (exp2.py): 23 zero-lateral starts all converge to the same V₀ = 4.893566.
  The starts include coning gimbal patterns at 0.5–5 rev per tf, two-lobe and perpendicular-lobe patterns, continuation from the minimizer, and random starts.
  So roll/coning/two-lobe strategies do not reach the centre.
- Structure of the minimizers: planar (box: along a corner diagonal). With free attitude the gimbal is fully inward (toward −u) for about 55–58% of tf, then flips fully outward.
  Upright at rest gives a rate-limited triangle-wave gimbal (+ corner → − corner → + corner).
  This matches the limit problems LP1/LP2 of §3.4.
- Scaling at small tf (cone, free): the lateral part at the minimizer grows like tf³, and the gap like tf^≈8.
  The TVC obstruction is therefore extremely weak at short horizons.
- Limit problems (limit_problems.py, N = 200, 2D vector controls, multistart):
  - LP1 best J = 0.083343 (planar 1/12 = 0.083333);
  - LP2 best J = 0.020834 (planar 1/48).
  - The 1e-5 excess is a switch-interval discretization artifact (the planar discrete optimum is exactly 1/12). No nonplanar maximizer beats the planar one. ∫B ≠ 0 (LP2: 1/32).
- Flat-output identity check: flat_check.py (§3.5).
- Not completed (killed under the compute budget): N = 120 refinement, decoupled-torque sanity check, tf = 3 bottom face, and the ω(tf)=0-only check of Thm E₀.
  The inner discretization makes V₀(NLP) an upper bound on the true V₀, so a refinement study is still owed. The gap at tf = 0.5 s (2e-4) is the least reliable.
- **Dive-then-brake face with r_z ≥ 0 at every node, upright at rest, box ±15°, 100°/s gimbal from centred, roll free** (exp3.py, N = 80, s* = 1 s, maximize ℓ = r0z + s*·v0z):

  | tf | max ℓ (free) | lateral data at max | r0z | max ℓ with r0_lat = v0_lat = 0 | **gap in ℓ** | spread over zero-lateral starts |
  |---|---|---|---|---|---|---|
  | 5 s | 26.44276 | \|v0_lat\| = 1.34, \|r0_lat\| = 1.46 | 33.4 m | 26.41461 | **2.8e-2 m** | < 1e-5 |
  | 7 s | 58.63996 | \|v0_lat\| = 1.98, \|r0_lat\| = 2.14 | 72.8 m | 58.60733 | **3.3e-2 m** | 6e-4 |

  This is the GTPL-realistic problem, with the altitude constraint and realistic horizons. The rotation-midpoint test says F is nonconvex, with a gap far above solver spread.
  Two caveats. (i) The NLP is an inner approximation, so both maxima are lower bounds and the gap is not certified. (ii) Only 2–3 starts were run per side under the compute budget.


---

## 5. Faithfulness of the 6DOF obstruction statement (brief item 4)
- **Boundary data that vary**: only θ = (r0, v0), entering affinely. Fixed: m0, q0 (including roll), ω0, gimbal state, throttle state, tf.
  Theorems need b(0) = e₃ and ω⊥(0) = 0 (roll rate free). If ω0, q0 are also data, nonconvexity of the slice suffices.
- **Initial gimbal / throttle state**: with rate limits these are data. Thm D handles a centred rate-limited gimbal; a throttle slew limit
  (GTPL 2000 N/s) replaces a1 by the pointwise-minimal ramp T_low(s) = max(ρ1, T0 − Ṫ s), still attained by one profile — fine.
- **Terminal attitude**: math/00's tent (b(tf) = e₃) is not realizable with torque limits (requires an instantaneous U-turn of ḃ,
  which is continuous). Thm D* (decoupled) and B* (kinematic) cover b(tf) = e₃, ω(tf) = 0; pure TVC: OPEN (numerics only). Final roll is
  never needed (free); if final roll is constrained, zero-roll arcs satisfy it whenever q0's roll equals the target.
- **Tilt cap** b_z ≥ cos θmax: once active, b can slide azimuthally along the cap at maximal tilt, so rigidity is lost; theorems need
  Φ(s*) (or Φ(tf)) < θmax. **Angular-rate cap** ‖ω⊥‖ ≤ ω̄: harmless (in Φ). A cap on the tilt-angle *rate* only (not on ‖ω⊥‖) allows free
  azimuth motion (see [lit-review] 00:05) — in the kinematic model that breaks rigidity; in torque models Lemma 0 still bounds ‖ḃ‖, so Thm D/D*
  survive.
- **Aerodynamic torque**: if present and attitude-independent at leading order it is an extra bounded transverse torque — add to τ̄;
  it breaks the R_π symmetry only if it has a preferred horizontal direction (wind). With wind, symmetry is lost and the rotation-midpoint
  lemma does not apply directly (OPEN; use a zero-wind instance, which suffices for an existence statement).
- **Box vs cone**: only R_π G = G is used (V7). For a box, the 5DOF model without a roll state is ill-defined (the box orientation in the
  world frame is the roll angle); either fix roll (then u ∈ corner diagonals) or let roll be free (then the effective set is the cone of
  half-angle δ*).

---

## 6. Theorem E₀ in Lean-ready form (pure TVC, terminal rate zero, tilt free) — for [lean]

Everything is stated in centre-of-percussion coordinates. The physical → y map is a separate lemma (L0) so the formal core stays
ODE-free. Notation: e₃ = (0,0,1), S² ⊂ ℝ³ the unit sphere, I = [0, tf], "a.e." = Lebesgue-a.e. on I.

**Parameters (all real).**
- tf > 0, m0 > 0, 0 < ρ1 ≤ ρ2, α ≥ 0 with m0 − αρ2 tf > 0;
- ε > 0 (= Jt/(mL), constant), κ > 0 (= L/Jt), δ* ∈ (0, π/2) (cone half-angle, or box corner angle);
- ω̄ > 0 (rate cap; take ω̄ = κρ2 sin δ*·tf if there is no cap).

**Hypotheses.**
- (H-f) ε ω̄² < ρ1 cos δ*/m0 (thrust term dominates the centripetal term, so f > 0).
- (H-π) ω̄ tf ≤ π/2 (every body-axis curve has length ≤ π/2, so b_z ≥ 0). L1 and L2 alone need only < π; L3 and L4 use b_z ≥ 0.

**Definition (abstract admissible class 𝒜).** A tuple q = (T, μ, w, b) with:
1. T : I → [ρ1, ρ2] and μ : I → [0, δ*] measurable;
2. m(s) := m0 − α∫₀ˢ T;
3. w : I → [0, ω̄] absolutely continuous, w(0) = 0, w(tf) = 0, |ẇ| ≤ κ T sin μ a.e.;
4. b : I → S² absolutely continuous, b(0) = e₃, ‖ḃ‖ = w a.e.

Define f_q := T cos μ / m − ε w² and the output I(q) := ∫₀^{tf} f_q(s) b(s) ds ∈ ℝ³.
Write I_z = ⟨I, e₃⟩ and I_lat = I − I_z e₃.

**Definition (planar subclass 𝒫).** q ∈ 𝒜 with b(s) = sin φ(s) u + cos φ(s) e₃, φ(s) := ∫₀ˢ w, for a fixed unit u ⊥ e₃.

**Lemma L0 (physical model ⊆ 𝒜; planar 𝒜 ⊆ physical closure).** [ODE part; may be taken as the modelling interface]
(a) Every physical relaxed trajectory gives an element of 𝒜 with I(q) = Δẏ = −v0 + g tf e₃ − ... Precisely, v0 = g tf e₃ − I(q).
   It needs: ε const, ω₃ ≡ 0, axisymmetric J, b(0) = e₃, ω⊥(0) = 0, landing r(tf) = v(tf) = 0, ω⊥(tf) = 0, and w := ‖ω⊥‖.
   Ingredients: the flat-output identity ÿ = f b − g, the speed lemma |d‖ω⊥‖/dt| ≤ κ T sin|μ|, and ẏ(tf) = 0.
(b) Every q ∈ 𝒫 is the output of a physical relaxed trajectory: chatter the gimbal sign along ±u at magnitude μ.
   Hence proj_{v0} cl F_tf = g tf e₃ − I(𝒜_phys), with I(𝒫) ⊆ I(𝒜_phys) ⊆ I(𝒜).

**Lemma L1 (length ≥ angle).** For q ∈ 𝒜, let θ(s) := arccos⟨b(s), e₃⟩. Then θ(s) ≤ φ(s) := ∫₀ˢ w for all s.
If θ(s) = φ(s) for all s ∈ I, then b(s) = sin φ(s) u + cos φ(s) e₃ for one unit u ⊥ e₃, on {φ > 0}.
(Proof of the rigidity: nested minimizing geodesics, using φ < π from (H-π). Inner-product form, as in math/02 Prop. 1.2:
⟨b(s), b(s')⟩ ≥ cos(φ(s') − φ(s)), which forces u(s) = u(s').)

**Lemma L2 (comparison).** For q = (T, μ, w, b) ∈ 𝒜 and unit u ⊥ e₃, let p := (T, μ, w, b_p) with b_p = sin φ u + cos φ e₃. Then:
- p ∈ 𝒫 and f_p = f_q;
- I_z(p) ≤ I_z(q);
- equality holds iff θ_q = φ on I.

*Proof.* f > 0 by (H-f) and m ≤ m0. Also cos φ ≤ cos θ_q pointwise (L1 and cos decreasing on [0, π]). Integrate.
For "iff": continuity, and f > 0.

**Lemma L3 (μ saturates; minimizers rotate).**
- Raising μ to δ* keeps w admissible and lowers f pointwise, so I_z decreases (weakly), since b_z ≥ 0 by (H-π).
- Any q with w ≡ 0 is strictly improved: keep T, set μ = δ*, and take w = tent with slope κρ1 sin δ*·η for small η > 0.
- Hence every minimizer of I_z over 𝒜 has w ≢ 0.

**Lemma L4 (existence).** I_z attains its infimum on 𝒫.
*Proof.* T in the weak-* compact set of L^∞ functions with values in [ρ1, ρ2]. For μ = δ* (L3), the pairs (T, w) form a closed convex set,
since the constraint |ẇ| ≤ κ sin δ* T is linear in T. w is equi-Lipschitz (|ẇ| ≤ κρ2 sin δ*), so Arzelà–Ascoli applies.
Then m → m uniformly, cos φ → cos φ uniformly, and ∫ T·(cos δ*/m) cos φ is weak-*–uniform continuous.

**Theorem E₀.** Assume the parameters, (H-f) and (H-π), and Lemma L0. Then F_tf (pure TVC, landing r = v = 0, ω⊥(tf) = 0, tilt free)
is not convex. In fact the relaxed set cl F_tf is not convex.

*Proof.*
1. Let p* ∈ 𝒫 minimize I_z over 𝒫 (L4). By L2 it also minimizes over 𝒜.
2. Every minimizer q over 𝒜 has θ_q = φ_q (L2 equality case), hence b_q is meridional along one u_q (L1).
   Then I_lat(q) = (∫ f_q sin φ_q) u_q.
3. This lateral part is nonzero: f_q > 0, and φ_q > 0 on a set of positive measure because w_q ≢ 0 (L3).
4. Rotation by π about e₃ maps 𝒜 to itself and 𝒫 to itself (u ↦ −u), and preserves I_z.
5. Suppose cl F_tf were convex. Then I(𝒜_phys) would be convex. The midpoint of I(p*) and R_π I(p*) is I_z(p*) e₃, and it would equal I(q)
   for some q ∈ 𝒜_phys ⊆ 𝒜. That q minimizes I_z and has I_lat(q) = 0, contradicting step 3.
6. F_tf ⊆ cl F_tf, and cl of a convex set is convex, so F_tf is not convex either. ∎

**Formalization notes.**
- L1–L4 and the Theorem are ODE-free, apart from "absolutely continuous" and "a.e.".
- L1 is exactly the inner-product rigidity lemma already in math/03; reuse it.
- L0 is the only place where rigid-body dynamics enter. Suggest stating it as a structure field (hypothesis) of the physical model, as was done for the PMP in lean-positive.
- For a box gimbal, δ* = corner angle. 𝒫 must use u along a corner diagonal (fixed roll), and R_π preserves the box.
- Not covered:
  - b(tf) = e₃, because φ_p(tf) > 0;
  - gimbal-rate limits, because sign chattering is not admissible;
  - ω₃ ≠ 0, because the gyroscopic force has a vertical component off-meridian;
  - altitude/glide-slope constraints, because the minimizer sits at min-throttle-like profiles, which are underground for GTPL.

---

## 7. Attack on [proof-tvc]'s TVC-1 route (upright at rest, r_z ≥ 0; SDP/S-procedure certificate)
Route: B* face ℓ = r0z + s* v0z in y-coordinates. Explicit planar witness with gain G_w. For every zero-lateral relaxed competitor:
W_z − J0 ≤ Q(h) + R − Pen, with Q bounded by an S-procedure (torque bound) and a Finsler multiplier (moments). The vector problem is separable,
and continuity is handled by a cell-average split.
- **FATAL at the submitted parameters** (tf = 1, s* = 0.25): R = 2.97e-4 > G_w = 7.27e-5, so U_total ≥ R > G_w. The cause is the worst-case
  a-priori curvature ē = v̄² sin φ̄, with v̄ = K2 min(s, tf−s). Scaling R/G ~ tf^5 suggests it can pass at tf ≲ 0.6 s, or with a localization lemma.
- **Scope (mass)**: the witness and bounds take α = 0 and ε const. Under GTPL depletion, a = T/m exceeds ρ2/m0 by ≈0.7% per second, which is
  ~10³× the gap. As written, the result is for an idealized class (α = 0), not for GTPL.
- **Scope (roll)**: ω₃ ≡ 0 is imposed on competitors. The gyroscopic term w ε(Ja/Jt)ω₃ (h×ḣ)_z is quadratic and non-separable, and must be bounded into Q.
- (a) late inequality a2 − p b_z ≥ (|q|² cos²φ̄ + a2²|h|²)/(2a2): **TRUE**. With x = q/a2, y = |h|:
  1 − √(1−x²)√(1−y²) ≥ y²/2 + cos φ·x²/2. It needs a ≤ a2, b_z ≥ 0, and Jensen for relaxed gimbals.
- (b) Δp/κ_D absorption: OK under constant mass. (c) cell-average splitting: checked, OK.
- Gimbal-rate limits: the competitor class shrinks (fine), but the witness must be rate-feasible from a centred gimbal. With 100°/s it is not; G_w must be recomputed.
