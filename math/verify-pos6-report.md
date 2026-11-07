# Referee report VERIFY-POS6: 6DOF transfers, positive results, SDP exactness

Author: [verify-pos6] (independent referee). Date: 2026-11-07 (system clock 00:57 → 01:20).
Scope: the CLAIMED rows listed in comms/briefs/verify-pos6.md. Sources read line by line: math/adversary-6dof-report.md,
comms/threads/6dof-models.md, math/checks/flat_output_tvc.py, math/04-positive-results.md, math/redteam-reform.md §3,
lean/POSITIVE.md (and the Lean statements of `AumannInstance`, `origFeas_eq_relFeas`, `convex_origFeas`, `tvcSet`,
`convex_feasData_M3b`), math/08-sdp-exactness.md, and the paper statements (paper/sections/02, 03, 04).
Numerics: numerics/verify-pos6/ (own venv; single-threaded BLAS; at most 2 processes).

Verdict keys: **CONFIRMED** = correct and complete as stated (minor fixes listed); **NEEDS FIX** = a repairable gap (repair
given); **BROKEN** = false or unrepairable. **No claim in scope is BROKEN.**

## 0. Verdict table

| Row | Claim | Verdict | One-line reason |
|---|---|---|---|
| B6 (Thm K) | kinematic 6DOF transfer, box gimbal δ* = corner angle | **CONFIRMED** | the projection is onto M1; zero-roll witnesses realise it; corner angle = 21.09° for GTPL's Cardan gimbal (verified) |
| B6-D (Thm D) | decoupled torque, terminal attitude free | **CONFIRMED** (one sentence to delete) | Lemma 0 + envelope + rigidity all check. The parenthetical "TVC torque may be *added*" is not covered by the proof |
| B6-D* (Thm D*) | decoupled torque, b(tf)=e_z, ω⊥(tf)=0 | **CONFIRMED** (unconstrained core) | the early/late bounds are attained by one attitude history, so every maximizer saturates both. The state-constraint clause is inherited from P-B* and was not re-derived |
| V6 (roll/coning) | gyroscopic term does no work; J_xx = J_yy | **CONFIRMED** | Lemma 0 checked symbolically and numerically (residual 8e-14 at random roll rates) |
| FLAT / P-K3 | centre-of-percussion identity incl. roll term | **CONFIRMED** (identity) | ÿ = (T cos μ/m − ε‖Ω⊥‖²)b − g e_z + (J_a/(mL)) ω₃ (b×ḃ), with b×ḃ = Ω⊥. Residual 9e-15 at random states |
| B6-E0 (Thm E₀) | pure TVC, ω⊥(tf)=0, tilt free | **NEEDS FIX** (3 repairable gaps) | (i) constant κ is inconsistent with α > 0 and constant ε; (ii) the closure step "cl R = R_relaxed" is unproved (repair: exact cell-wise duty cycle); (iii) the §3.5 regime is too weak (use §6) |
| C-W | value/feasibility exactness for any measurable b | **CONFIRMED** | Aumann + injective Ψ_k + nodes. Caveat: C-W′'s uniform Slater condition fails for constraints active at touchdown (glide-slope apex, r_z(tf)=0) |
| C-S/C-D | strong form under PMP; affine primer; structure of D | **NEEDS FIX** (minor) | C-D4 ("bad b meagre") is proved in C⁰, where the admissible class is itself nowhere dense, so as stated it is vacuous. Repair given. §5.5: "λ_v absolutely continuous" fails for velocity constraints |
| C-U | union structure, per-instance exactness | **CONFIRMED** | set-theoretic, plus Lemma 9.1 (correct; existence without path constraints) |
| C-6 | pure TVC given b is exactly convex | **CONFIRMED** (FORMALIZED; statement-faithful) | the torque balance check is exact. For the Cardan box one axis bound is not linear in T_a, but it is still a lower bound, so the interval structure survives |
| C-Y | width ≤ 2δμ_c/sinh(μ_c t_f) | **CONFIRMED** | Sturm comparison correct. Numerics: bound never violated, tight to 0.4% at constant min throttle. Flight-code ρ1 = 300 N gives 1.8e-5 rad/s (not 3.5e-6) |
| X5 / RR-P | θ_p ≤ δ ⇒ F_5DOF = F_3DOF(θ_p) (M1) | **NEEDS FIX** (missing hypothesis) | with b(tf) = b_f prescribed, ω t_f ≥ ∠(b0, b_f) is needed, otherwise F_5DOF = ∅ ≠ F_3DOF |
| SDP-T1 | Thm 2.1, Cor 2.2, 2.3 | **CONFIRMED** | weak duality, convex Lagrangian, SDP complementary slackness |
| SDP-T4 | Thm 2.4, Lemma 2.4a | **CONFIRMED** | second variation recomputed by hand; LICQ ⇒ SONC along η⊗n ⇒ Q ⪰ 0 |
| SDP-P | Thm 4.1 (coplanar ⇒ certified), incl. glide slope/altitude | **NEEDS FIX** (glide-slope clause) | correct without state constraints and with Gram-linear constraints (altitude). Rem 4.3 says glide slope is "Gram-linear". It is not (it involves ⟨r_j,e_z⟩²), and the proof step fails. Cut the glide-slope clause |
| SDP-F | folding lemma, Cor 3.2, Cor 3.3 | **CONFIRMED** | |
| SDP-R4 | Prop 5.1 rank ≤ 4 | **NEEDS FIX** (missing step, coplanar caveat) | the proof shows z ∈ W, dim W ≤ 4, but rank G = dim(E+W). Missing step: E_w ⊆ W. So rank ≤ 4 needs dim E_w = 3 |
| SDP-L | Prop 6.1 lifted lens = conv(lens) | **CONFIRMED** (proposition) | the "Consequence" paragraph overstates: E⊥ cancellation with prescribed norms is not automatic, and "the gap disappears in continuous time" is CSD2′ (open) |

---

## 1. 6DOF transfers

### 1.1 Theorem K (kinematic attitude): CONFIRMED
- Inclusion: ‖ḃ‖ = ‖ω⊥‖ ≤ ω̄ gives (AL_ω). Realisation: ω := b×ḃ satisfies ω×b = ḃ, so Ṙ = [ω]×R has a solution with b = Re₃.
  This is checked (`|b×ḃ − Rω⊥| = 8e-17`, v1_rigidbody.py).
- Box gimbal: only angle(d,b) ≤ δ* and R_πG = G are used. The R_π-symmetry argument also needs R_π to commute with the initial
  roll R0; it does, because b(0) = e₃ makes R0 a rotation about e₃. The witnesses use zero roll and d at the corner whose horizontal
  direction is u.
- Corner angle: GTPL's MPC thrust vector is (sin θ cos φ, sin φ, cos θ cos φ) (context/vehicle.md l.169), a Cardan pair, so
  δ* = arccos(cos²15°) = **21.09°**. A tangent parametrisation would give 20.75°. The inscribed cone is 15.000° (checked).
  context/vehicle.md's "21.2°" is a rounding slip.
- B* variant (Thm K "Same for B*"): the late d = e₃ needs tilt ≤ δ_in (15°), not δ*. So the smallness condition is ω s* ≤ δ_in. The
  report states this in V7; the Thm K paragraph should say it too.
- Lean (`not_convex_landingSet6`, BOARD [lean] 05:40) bounds the rate of *every* body vector, which also caps the roll rate. That is
  a sub-model of Thm K's "ω₃ arbitrary". The theorem for the larger class follows from the same two facts (projection into M1,
  zero-roll witnesses). Faithful in substance; the model difference should be noted in the paper.

### 1.2 Theorem D (decoupled torque, free terminal attitude): CONFIRMED, one sentence to delete
Each step was checked:
- (1) Lemma 0, Euler in body axes: the gyroscopic terms (J_a − J_t)ω₃(ω₂ω₁ − ω₁ω₂) cancel. Numerical residual 7.6e-14 at random states.
  With ω⊥(0) = 0 this gives ‖ḃ(s)‖ ≤ min(ᾱs, ω̄), hence φ ≤ length ≤ Φ.
- (2) a ≥ a₁(s) := ρ1/(m0 − αρ1 s), using ∫₀ˢT ≥ ρ1 s. Equality forces T = ρ1 a.e.
- (3) Attainment: rotation about a fixed body transverse axis with zero roll has no gyroscopic term, so Φ is attained.
- (4)–(6): cos is strictly decreasing on [0, π], so d_z = cos(δ*+Φ) forces φ = Φ and d at the outward corner. Then length = distance,
  nested minimizing geodesics share one u, and the lateral part is nonzero.

**Fix (delete).** §2 says "the TVC torque may be *added* only if bounded and the gimbal deflection is not otherwise constrained".
That case is not covered. With τ_total = −LT b×g + τ_rcs, the upper bound in step (1) must use ᾱ⁺ = (τ̄ + Lρ2 sin δ*)/J_t. But at the
outward corner the TVC torque opposes the tilt (Lemma 1), so the bang arc achieves at most (τ̄ − Lρ1 sin δ*)/J_t. The envelope is
then not attained, and step (4) has nothing to compare against. Theorem D holds when the transverse torque is a control independent
of the gimbal choice (thrust line through the CG, or a bound on the *total* transverse torque that does not depend on d). That is
exactly how paper Thm 3.20 states it ("independent of the engine"), so only the adversary report needs the edit.

**Scope notes.**
- The transverse-torque bound must be a Euclidean ball, or (box RCS) aligned so that the max-torque diagonal is e₃×u for a gimbal
  corner direction u. Otherwise the attainment step needs a different u.
- Remark (b) (gimbal-rate limit from a centred start, δ*(s) = arccos(cos²(min(γ̇s, δ)))) is correct for the Cardan box.

### 1.3 Theorem D* (dive-then-brake, b(tf) = e_z, ω⊥(tf) = 0): CONFIRMED (core)
- The weight is w(s) = α_z(s − s*). It comes from r0z = ∫s(a d_z − g), v0z = −∫(a d_z − g) (recomputed).
- With the throttle frozen at a maximizer's T*, the explicit history (bang for s*, reverse for s*, rest-to-rest return in 2s*,
  peak tilt ᾱs*², peak rate ᾱs*) is admissible when ᾱs* ≤ ω̄, ᾱs*² ≤ δ_in and 4s* ≤ tf. It attains both pointwise bounds. Every
  maximizer must therefore saturate both, which is a valid squeeze.
- Relaxed maximizers are ordinary: d is a.e. a Dirac given b, and the dynamics are affine in T and τ, so the means can be taken.
- Missing but trivial: δ* + ᾱs*²/2 ≤ π/2 (or < π) for the early bound. Implied by the stated conditions for all practical δ*.
- "State constraints handled exactly as in B*": not re-derived here. The vertical structure (early d_z = cos(δ*+Φ), late d_z = 1,
  late T = ρ2) is the same as in B*, so P-B*'s argument applies with Φ quadratic. Treat that clause as inheriting P-B*'s status.

### 1.4 Roll / coning cannot help (V6): CONFIRMED
- Lemma 0 holds for any ω₃ with J = diag(J_t, J_t, J_a). In the kinematic model, roll does not enter b at all.
- Scope: J_xx = J_yy and no products of inertia (GTPL has a 0.35 kg m² frame product; vehicle.md l.51). Lemma 0 then fails when
  ω₃ ≠ 0, and the report correctly flags this as OPEN.
- For pure TVC the roll term is not harmless: it adds (J_a/(mL))ω₃(b×ḃ) to ÿ (next item), which has a vertical component off-meridian.
  E₀ therefore assumes ω₃ ≡ 0, as stated.

### 1.5 FLAT / P-K3 identity: CONFIRMED
v1_rigidbody.py integrates nothing and evaluates pointwise at 2000 random states (full Euler equations, random roll rates).
- `ÿ − [(T cos μ/m − ε‖Ω⊥‖²) b − g e₃] − (J_a/(mL)) ω₃ (b×ḃ)` has max residual **8.9e-15**.
- Lemma 1 (J_t Π_b b̈ = −LTg + J_aω₃ b×ḃ) has residual 5.7e-13.
- Without the roll term the residual is O(1) (2.9 m/s²).

Paper Lemma 2.1 (lem:cop) states exactly this, with ϖ = ω₃ and Ω⊥ = b×ḃ. It requires constant m, J_t, L (hence constant ε), as
paper model PT assumes.

### 1.6 Theorem E₀ (pure TVC, ω⊥(tf) = 0, tilt free): NEEDS FIX (three repairable gaps)
The logical skeleton is sound: L1 rigidity, L2 comparison, L3 saturation/rotation, L4 existence, and the rotation-midpoint argument
applied to 𝒜-minimizers. I checked:
- f > 0 from strict (H-f);
- L2's "iff": f > 0, and cos θ − cos φ ≥ 0 is continuous;
- L3's tent improvement: ΔI_z = −∫(T cos δ*/m)(1 − cos φ) − ∫εw² cos φ < 0;
- the relaxed-gimbal reduction: a mean (T cos μ, T sin μ) of the annular sector can be replaced by a sector point with the same axial
  part and a larger lateral part, since X ∈ [ρ1 cos δ*, ρ1] on the chord region;
- L0(a): ẏ(0) = v0, ẏ(tf) = 0 from ω⊥(0) = ω⊥(tf) = 0, so v0 = g tf e₃ − I.

Gaps and repairs:
1. **κ and mass.** §6 allows α ≥ 0 with constant ε and constant κ = L/J_t. Physically κ = 1/(εm). With α > 0 and ε constant, κ(s)
   increases as mass drops. L0(a) (physical ⊆ 𝒜) needs κ ≥ max κ(s), while L0(b) (𝒫 ⊆ physical) needs κ ≤ min κ(s). Both hold only
   if α = 0.
   **Repair:** either take α = 0 (the paper's model PT is constant-mass, so paper Thm 3.21 is fine as stated), or define 𝒜 with
   |ẇ| ≤ T sin μ/(ε m(s)). L1–L3 are unchanged. In L4, the (T,w) set is no longer convex, but it is weak*×uniform closed
   (∫T_n/m_n → ∫T/m), which is all that compactness needs.
2. **Closure step.** §3.5 step 4 asserts cl R = R_relaxed. That needs the relaxation theorem *with* the terminal constraint
   ω⊥(tf) = 0, which cannot be absorbed into the data. The proof only needs I(p*) ∈ proj cl F for the planar chattering minimizer p*.
   **Repair** (explicit): on a grid of cells, use ordinary in-plane gimbal ±μ with a duty cycle chosen so that each cell's integrated
   lateral torque equals that of p*. Then ω_n(t_k) = ω(t_k) exactly at every node, including ω_n(tf) = 0, and b_n stays planar. The
   axial thrust T cos μ is unchanged, so f_n → f and I(p_n) → I(p*); landing r, v are absorbed into (r0, v0).
   The inclusion cl F ⊆ F_relaxed follows from compactness of the relaxed trajectory set. Step 5 should then read "both I(p*) and
   R_πI(p*) lie in proj cl F; the midpoint lies in proj cl F ⊆ g tf e₃ − I(𝒜_phys)".
3. **Regime.** §3.5 lists "length < π, f ≥ 0". That is insufficient: L3/L4 need b_z ≥ 0 (raising μ lowers I_z only where b_z ≥ 0),
   and L2's equality case needs f > 0 on a dense set. Use §6's (H-f) strict and (H-π) ω̄tf ≤ π/2, as paper Thm 3.21 does.
4. (Wording) ω₃ ≡ 0 is a model restriction (no roll torque, or roll held at zero). It is not a consequence: with a roll RCS present,
   F_tf of the full model is a different set.

With 1–3 repaired, E₀ is a theorem. The paper statement (constant mass, strict regime, cl F nonconvex) is correct once the closure
step is written out.

---

## 2. Positive results

### 2.1 C-W: CONFIRMED
- F_k(s) = Ψ_k(s) S_{Γ(s)}(b(s))/m(s) is measurable (continuous in (Γ, b)), compact-valued, nonempty and integrably bounded.
  Lemma X gives conv F_k = Ψ_k K_Γ/m. Ψ_k = [(t_{k+1} − s)I; I] is injective, so the pseudo-inverse recovers T̃ ∈ S_Γ(b).
  The node concatenation is valid, mass and cost are unchanged, and the log-mass form follows because v̇ = u + g does not involve z.
- C-W′: the convex combination, the margin λη, and ‖x̃ − x^λ‖ ≤ 2a_max h(1 + h) between nodes all check.
  **Scope caveat (should be written next to C-W′ and in paper §4 after Thm 4.1):** a Slater point with dist(x°(t), X^c) ≥ η
  *for all t* cannot exist when the constraint is active at the fixed terminal state. That covers the glide-slope cone with its apex
  at the target and r_z ≥ 0 with r_z(tf) = 0, i.e. the standard PDG constraint set (paper eq. (X)). So the value statement with path
  constraints is not established for that set.
  A plausible repair (not checked): a time-graded mesh near tf (countably many nodes) with a margin η(t) ≍ (tf − t)² and h(t) ≲ (tf − t).
- Lean faithfulness: `AumannInstance` is a true instance of Aumann–Lyapunov (6-dimensional moments (T, (tf − t)T)), so it is not a
  vacuous hypothesis. `origFeas_eq_relFeas` and `convex_origFeas` match C-W(1) and C-F for constant mass. **Faithful.**

### 2.2 C-S / C-D: NEEDS FIX (minor)
Checked:
- Adjoint signs (λ̇_m = ⟨λ_v,T⟩/m², ṗ = λ_r), hence p affine.
- C-S(1) via Lemma J + C-3 + U.
- C-S(2): the α > 0 coefficient is λ₀ + αν > 0.
- C-S(3) via Lemma S: the coefficient λ₀ + κ cos δ/m is > 0.
- C-D1, and the gnomonic speed ‖a×c‖/‖a+ct‖² = Ω/(1+Ω²s²), which gives 4AC − B² = 4.
- C-D3(a): double Rolle at density points.
- C-D3(b): analytic dichotomy, and the converse speed law ⇒ gnomonic line.
- C-D4 closedness: reverse Fatou plus pointwise limits.

Fixes:
1. **C-D4 is proved in the wrong space.** C⁰([0,tf]; S²) contains the admissible class 𝓑 = (AL_ω) as a closed nowhere-dense subset.
   So "the bad set is meagre in C⁰" says nothing about admissible profiles: a meagre set can contain all of 𝓑.
   **Repair:** run the same proof in the complete metric space 𝓑 (with the boundary attitude conditions).
   - B_ε ∩ 𝓑 is closed, by the same argument.
   - Empty interior: piecewise constant-speed geodesic interpolants of b ∈ 𝓑 at nodes t_i are dense in 𝓑. They have speed
     ≤ ω because angle(b(t_i), b(t_{i+1})) ≤ ωh, and they keep the boundary values. Where b(t_i) = b(t_{i+1}), insert a short
     out-and-back arc of small nonzero speed.
   - On each piece the speed is constant and nonzero, so (ND1) holds, and (ND2) holds because a gnomonic line has non-constant speed.
2. §5.5: "λ_v is absolutely continuous" holds for *position* constraints only. GTPL has a speed limit ‖v‖ ≤ v_max; with velocity
   constraints λ_v carries a measure part and p is BV. C-S(1) still holds pointwise a.e. (the minimum condition is pointwise), but
   the affine/gnomonic structure applies only on open intervals where every state constraint is inactive.
3. C-S(2) with α = 0, "drop m from the state": if (H-PMP) is taken with m as a state, the multiplier (λ₀ = 0, ν > 0) is admissible
   only when m*(tf) = m_dry, i.e. m0 = m_dry when α = 0. That edge case is degenerate. The Lean version takes nontriviality of
   (λ₀, λ_r, λ_v) as a hypothesis, which is the right form.
- Lean faithfulness (`PMPConclusion.*`): matches C-S(1)–(4) as POSITIVE.md describes, with C-S(4) weaker (pointwise P₀-feasibility).

### 2.3 C-U: CONFIRMED
- (1) and (3) are definitional. (2) follows from C-W and Lemma 9.1.
- Lemma 9.1: compactness of (AL_ω) in C⁰ (Arzelà–Ascoli; the class is closed). The cone constraint passes to the limit because
  ‖b_n − b‖_∞ ‖T_n‖_∞ → 0. The cost and dynamics are weak*-continuous for constant mass.
- Scope: existence is claimed and proved only without path constraints (C-W converts nodewise only). The paper's Thm 4.3 says
  "In M1 with constant mass the 5-DOF minimum is attained". Add "without path state constraints".
- The M3b part is conditional on an optimum existing (not proved). Fine as stated.

### 2.4 C-6: CONFIRMED (FORMALIZED; statement-faithful)
- Lemma 8.1 re-derived. With ω₃ = 0, H = J⊥ω, ω = b×ḃ, dH/dt = J⊥ b×b̈ = ℓ T×b, so (Π_bT + kΠ_b b̈)×b = 0.
- The interval [L, U], the convex cost, and the affine dynamics are checked.
- Lean `tvcSet`/`convex_feasData_M3b` are faithful, given the prose identification F = −kΠ_b b̈ (as POSITIVE.md says).
- Minor (box gimbal): "|⟨F, e_{x,y}^body⟩| ≤ T_a tan δ_box, linear in T_a" holds for a tangent-angle box. For GTPL's Cardan box
  (vehicle.md l.169) one axis reads |F_y| ≤ sin δ √(T_a² + ϰ²), i.e. T_a² ≥ F_y²/sin²δ − ϰ². That is still a lower bound on T_a, so
  the feasible T_a set remains an interval and convexity is unchanged. The body axes are determined by b through zero-roll parallel
  transport, given the initial roll.

### 2.5 C-Y: CONFIRMED
Checked:
- the planar reduction φ̈ = (‖T‖/k) sin(φ − ψ), with planarity by uniqueness;
- the MVT step q ≥ μ_c²;
- the Wronskian-type comparison (ėw − eẇ)′ = (q − μ_c²)ew ≥ 0;
- e(tf) ≤ 2δ (needs 2δ < π, so that e stays in [−2δ, 2δ] by continuity).

Numerics (v2_cy_width.py, GTPL J = 63.6, ℓ = 0.589, δ = 15°): the realisable rate interval was measured by shooting plus bisection,
for 4 thrust histories × 2 initial offsets × tf ∈ {0.5, 1, 2} s.
- **No violation.** Ratio width/bound: 0.995–0.996 at constant min throttle, 0.16–0.81 at max throttle, 0.25–0.99 for slewing and
  primer-like histories.
- GTPL tf = 7 s: 3.52e-6 rad/s at ρ1 = 400 N (as claimed). At the flight-code ρ1 = 300 N (vehicle.md l.161) it is
  **1.80e-5 rad/s**. Either value gives the same qualitative conclusion.

Scope: b0 ∈ Π and an in-plane initial rate (as stated). Corollary C-Y′ should say "b0 ∈ Π, ḃ0 ∈ T_{b0}Π". An out-of-plane rate obeys
ζ̈ = (T_a/k − ‖ḃ‖²)ζ, which is also exponentially unstable, so a similar thinness holds, but it is not proved here.

### 2.6 X5 / RR-P: NEEDS FIX (missing hypothesis)
- "⊆" is trivial.
- "⊇": cap(e_z, δ−θ_p) is geodesically convex (δ − θ_p < π/2), and cap(e_z, θ_p) ⊆ cone(b, δ) by the triangle inequality. Correct.
- **Missing:** when b(tf) = b_f is prescribed, the geodesic b0 → b_f must be traversable: **ω tf ≥ ∠(b0, b_f)**. Otherwise
  F_5DOF = ∅ while F_3DOF(θ_p) ≠ ∅. Add it to RR-P, X5 and paper Prop 4.5. It is automatic for b0 = b_f = e_z, the GTPL case.
- Part (b) (θ_p > δ ⇒ nonconvex) is B* with ωs* ≤ min(θ_p − δ, δ). It inherits P-B*'s status.

---

## 3. SDP exactness (math/08)

### 3.1 Thm 2.1 / Cor 2.2 / Cor 2.3: CONFIRMED
- Lemma 1.1 reduction: the full Shor PSD condition implies Y − MMᵀ ⪰ 0, by partial trace of the PSD matrix X − xxᵀ, and conversely.
  Fine.
- Slater: z_i = √(1−ε²)e_z + εn_i with orthonormal n_i ⊥ E is strictly feasible for δ, ω > 0, so dual attainment holds.
- (⇐): f_w ≥ L on feasible points, L is convex since Q⊗I_X ⪰ 0, ∇L(z*) = 0 in every X ⊇ E, and complementary slackness gives
  L(z*) = f_w(z*).
- (⇒) and Cor 2.2/2.3: tr(G*S) = 0 with S ⪰ 0 forces SW = 0 for any factor W = [[I,0],[Z_E,Z_⊥]]. Hence QZ_E = L̃ and QZ_⊥ = 0.
  "Exact" (value equality) is equivalent to the existence of a rank-3 optimal G.

### 3.2 Thm 2.4 / Lemma 2.4a: CONFIRMED
- Recomputed: ΔL = t²[ηᵀQη − ½Σ Q_ij(η_i² + η_j²)⟨z_i,z_j⟩ + Ση_i²⟨z_i, ℓ̃_i⟩] + O(t⁴). Stationarity cancels the last two terms, so
  ΔL = t²ηᵀQη + O(t⁴).
- LICQ in ℝ³ implies LICQ in ℝ⁴ (same vectors). η⊗n is orthogonal to every constraint gradient and to ∇f_w (all in E^m), so it lies
  in the critical cone, and SONC gives Q ⪰ 0.

### 3.3 Thm 4.1 (coplanar): CONFIRMED without state constraints / with Gram-linear constraints; NEEDS FIX for glide slope
- Core proof: all constraint gradients and ∇f_w lie in Π^m when z* ⊂ Π and E_w ⊆ Π, so η⊗n is critical and genuine SONC gives
  Q ⪰ 0. Correct.
- Numerics (v3_sdp.py mode A, D^unit, N = 4, δ = 15°, ωtf = 1, 40 random coplanar targets):
  - in 11 instances the best planar configuration was a 3D local minimum (out-of-plane kicks plus SLSQP gave no decrease), and in
    every one SDP = planar value to ≤ 1e-8;
  - in the other 29 the planar optimum was not a 3D local minimum, and SDP = best 3D NLP;
  - no violation.
- **Glide-slope clause (Rem 4.3; paper Thm 4.8 "remains true with altitude and glide-slope constraints, or any constraint quadratic
  in node positions and invariant under rotations about e_z"): proof step false.**
  - The glide-slope form ‖r_{j,h}‖² ≤ cot²γ ⟨r_j,e_z⟩² contains ⟨r_j,e_z⟩² = (Σκ_{jk}⟨d_k,e_z⟩ + c_j)². That is a product of first
    moments, not an entry of the reduced Gram G = [[I₃, Mᵀ],[M, Y]]. So it is **not Gram-linear**.
  - The only e_z-rotation-invariant quadratics that are Gram-linear are α‖r_j‖² + (linear in r_z) + const (isotropic balls,
    altitude).
  - The rotation-invariant cone written in X, ‖r_j‖² ≤ (1+cot²γ)⟨r_j,e_z⟩², is not convex in G.
  - A convex lift has to impose the cone on the E-readout (an SOC on first moments). The genuine constraint then *does* see the
    in-ℝ³ normal n (Hessian of λ‖r_h‖ along n is λ(κη)²/‖r_h‖ > 0), but the lifted one does not see E⊥.
  - So genuine SONC along n gives only ηᵀ(Q + ½Σλ_j κ_jκ_jᵀ/‖r_{j,h}‖)η ≥ 0, not Q ⪰ 0. Thm 2.1 needs the latter along E⊥.
  - **Repair:** state Thm 4.1 / Rem 4.3 for constraints linear in G (altitude ⟨r_j,e_z⟩ ≥ 0 and isotropic balls). For glide slope,
    say exactness must be checked a posteriori (direct stress test Q_λ ⪰ 0, Thm 2.1, with the cone on the E-readout), and that the
    a-priori claim is open. I do not claim the glide-slope conclusion is false; only that it is unproved.
- Also in Rem 4.3: "hard terminal velocity: LICQ fails (zero gradient of ‖V − wv‖²)". The real reason is that V = wv as an equality
  constraint is Gram-linear only via ‖V − wv‖² = 0, whose gradient vanishes on the constraint set. Correct as stated.

### 3.4 Lemma 3.1, Cor 3.2, Cor 3.3: CONFIRMED
- Folding: ⟨Fx,Fy⟩ − ⟨x,y⟩ = ‖P⊥x‖‖P⊥y‖ − ⟨P⊥x, P⊥y⟩ ≥ 0. Norms are kept, and constraints and linear costs with ℓ ∈ E_w are
  unchanged.
- Cor 3.3: dim E_w ≤ 2 lets n be chosen inside ℝ³, so the lifted optimum is genuine in D^unit, D^cvx and D^0 alike.
- Remark 3.4 (Brouwer) is heuristic but correct as a statement about retractions.

### 3.5 Prop 5.1 (rank ≤ 4): NEEDS FIX (missing step, coplanar caveat)
- The stationarity equations and the elimination were re-derived. The coefficient of b_{k+1} is ν_k(1 + λ_kλ′_k/(2μ^d_kν_k)) ≠ 0,
  and the induction from b_0 = e_z, b_1 puts all z in W = span(e_z, b_1, y_v, y_r).
- **But** rank G = dim span(e₁, e₂, e₃, z_i) = dim(E + W), and dim W ≤ 4 alone gives only rank ≤ 6.
  **Missing step (true):** V = Σcv_k d_k ∈ W and y_v ∈ W imply wv = V − y_v ∈ W; likewise wr ∈ W. So E_w = span(e_z, wv, wr) ⊆ W.
  When dim E_w = 3 (generic data), E ⊆ W and rank G = dim W ≤ 4. **For coplanar data** only rank ≤ 5 follows. Rotating the optimum
  about E_w gives a rank-≤4 optimum, but the max-rank IPM point may have rank 5.
- Every SDP optimum is a lifted KKT point with the SDP dual multipliers (SW = 0 above), so the proposition applies to IPM output
  whenever the duals satisfy the nondegeneracy.
- Numerics: I could not produce optima with all interior rate duals > 0 at N = 4, 6 (the optima plateau). So this is not a numerical
  test of the hypothesis, but no violation was seen: rank-5/6 optima occurred only with inactive interior rate constraints
  (v3_sdp_B.txt, v3_sdp_C.txt, v3_sdp_D.txt).

### 3.6 Prop 6.1 (lifted lens = conv(lens)): CONFIRMED (proposition)
- (⊆) is trivial. (⊇) d = x + √(1−‖x‖²)n.
- K = conv(lens): the two-half-space polyhedron in ℝ³ has a lineality space (b×b′), so it has no vertices. Interior-of-ball points
  lie in the relative interior of a face of dimension ≥ 1, hence are not extreme. Minkowski.
- **The "Consequence" paragraph overstates.**
  - The E⊥ parts s_k have prescribed norms √(1 − ‖x_k‖²). Cancelling both moments Σcv_k s_k = Σcr_k s_k = 0 requires a compatible
    norm configuration (it fails, e.g., when only one segment throttles down). So "these vanish once arranged … N ≥ 3 suffice" is
    true only for suitable throttle-down patterns. The lift trades the residual moment against cost, as at case 12.
  - "In continuous time … the gap disappears in the limit" is Conjecture CSD2′, which is OPEN. Say so.
- The case-12 "artifact" diagnosis (SDP_cvx = genuine_cvx) is numerical evidence ([proof-sdp], [verifier-sdp] 509 instances), not a
  theorem. The registry row already says so.

---

## 4. Numerics index (numerics/verify-pos6/)
| Script | Output | Purpose |
|---|---|---|
| v1_rigidbody.py | v1_rigidbody.txt | Lemma 0, Lemma 1, centre-of-percussion identity with roll term, b×ḃ = Ω⊥, Cardan/tangent corner angles, inscribed cone |
| v2_cy_width.py | v2_cy_width.txt | C-Y bound vs measured realisable-rate interval (24 cases), GTPL values at ρ1 = 400/300 N |
| v3_sdp.py | v3_sdp_A.txt (Thm 4.1, 40 coplanar), v3_sdp_B.txt, v3_sdp_C.txt, v3_sdp_D.txt (Prop 5.1 rank/duals, 40+40+12) | D^unit Gram SDP (Clarabel) vs planar/3D SLSQP multistart |

## 5. Requested edits (for owners; I did not edit others' files)
- [adversary-6dof] math/adversary-6dof-report.md:
  - §2: delete the "TVC torque may be added" parenthetical.
  - §3.5/§6 E₀: set α = 0, or use κ(s) = 1/(εm(s)); write out the cell-wise duty-cycle closure step; drop the weaker §3.5 regime.
  - Thm K: add ωs* ≤ δ_in for the B* variant.
- [positive] math/04:
  - C-D4: prove meagreness in 𝓑 (repair above).
  - §5.5: λ_v is BV under velocity constraints.
  - C-W′: add the terminal-Slater caveat.
  - C-Y′: add b0 ∈ Π.
  - Lemma 9.1 / C-U: "no path constraints".
- [redteam-reform] §3.1 (a): add ωtf ≥ ∠(b0, b_f).
- [proof-sdp] math/08:
  - Rem 4.3: restrict to Gram-linear constraints; glide slope a posteriori only.
  - Prop 5.1: add "E_w ⊆ W"; rank ≤ 4 needs dim E_w = 3.
  - §6.1 Consequence: soften.
- [paper-writer]:
  - Thm 4.8 (thm:coplanar): delete "and glide-slope constraints, or any constraint quadratic in node positions and invariant under
    rotations about e_z"; replace with "or constraints linear in the Gram matrix, e.g. altitude".
  - Prop 4.5 (X5): add ωtf ≥ ∠(b0, b_f).
  - Thm 4.3 (C-U): "without path constraints".
  - Thm 3.21 (E₀): fine as stated for constant mass, once the closure step is in the appendix.
  - Text after Thm 4.4: C-Y GTPL value depends on ρ1 (3.5–18 µrad/s).
