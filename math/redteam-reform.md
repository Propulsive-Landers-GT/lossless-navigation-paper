# Red-team (reformulation): can classical LCvx machinery be made lossless for 5DOF/6DOF?

Author: [redteam-reform]. Date: 2026-11-07. Status: CLAIMED (each item lists its rigor level).
Scripts: `numerics/redteam-reform/` (`dp_tilt_only.py`, `dp_scan_fine.py`, `envelope_gap.py`, `envelope_gap2.py`).

Notation follows math/00 and math/02. The thrust acceleration is u = a d with a = T/m, and σ = Γ/m is the LCvx slack.
The tilt is Φ(s) = angle(b(s), e_z). F_t ⊂ R⁶ is the set of feasible boundary data (r0, v0) at horizon t. R_π is rotation by π about e_z.

## Summary of verdicts

| Route | Question | Verdict |
|---|---|---|
| 1 | LCvx-style slack or change of variables for the rate-coupled thrust direction | **FAILS** for every jointly convex, rotation-invariant candidate. Each one accepts the symmetrized B\* witness (§1). Mechanism: the "chord shortcut" |
| 2 | Counterexample to Claim B | **None** in the algebra. Scope holes: (i) the witnesses are underground when ρ1 < m g (found first by [adversary], confirmed); (ii) the witness M becomes *reachable* under an active tilt cap with long tf, or with free initial attitude. Both are repaired by B\* with a small switch time s\* (§2) |
| 3 | Exact restricted classes | **WORKS (sharp, M1 ONLY):** pointing cone θ_p ≤ δ ⇒ F_5DOF = F_3DOF, so classical LCvx is exact. θ_p > δ ⇒ nonconvex (§3.1). **Pure TVC (the real vehicle):** the class collapses to θ_p = 0. The a-posteriori exact set is measure-zero (with terminal attitude) or exponentially thin (§3.4). **WORKS (velocity only):** ρ1 = 0 with no down-thrust ⇒ R convex (§3.2). Full F at ρ1 = 0: OPEN. Large ω, large δ, long tf: FAIL (§3.3) |
| 4 | Free final time / line search / dilation | **FAILS** (Lemma RR-LS). A per-tf convex family accepts θ̄ ∈ conv F_{t\*} \ ∪_t F_t. This rules out feasibility-form and min-fuel losslessness on any window where the B\* braking condition holds (§4) |
| 5 | 6DOF (quaternion / dual-quaternion / SO(3) lifts, attitude as a rate-limited input) | **FAILS** for kinematic 6DOF: Thm A + B\* via projection. Torque-coupled M3b: OPEN, owned by [adversary-6dof]. Precise obstacle for B\* in M3: the class is not closed under max (§5) |
| T | Berning–Strohl–Bieniawski 2023 "tilt-rate LCvx" | It is a **3DOF** problem. The only SOC-representable "tilt rate" is a chord (thrust-vector) rate, and that relaxation is provably **not** uniformly lossless. The tilt-angle-only model has an exactly convexifiable velocity set (theorem), but its full (r0,v0) set is not given by the envelope SOCP (DP gap up to 3.4%) (§6) |

---

## 0. Two tools used throughout

**Lemma 0.1 (symmetrization certificate).** Let C ⊆ R⁶ × Y be convex, with (r0, v0) entering linearly, and suppose C is invariant
under the rotation R_π acting on (r0, v0) and on the lifted variables (for example, Y = trajectories of (u, σ, z, w, b, …) with R_π acting on vector-valued signals).
If (x, y) ∈ C, then ((x + R_π x)/2, (y + R_π y)/2) ∈ C. The averaged lifted trajectory is the "vertical part" of y. For example, u_avg(s) = u_z(s) e_z, b_avg(s) = b_z(s) e_z, and σ, z are unchanged.
*Proof.* R_π-invariance plus convexity. ∎
All LCvx-style constraints are norm or affine constraints built from e_z-symmetric data (‖u‖ ≤ σ, ρ1e^{−z} ≤ σ ≤ …, u_z ≥ σ cos θ_p, ‖u̇‖ ≤ ωσ, altitude, glide slope). They are therefore R_π-invariant, and **the midpoint of any rotated pair of feasible lifts is relaxed-feasible.** So a candidate relaxation is lossless only if F contains every symmetrized point x̄ = (x + R_πx)/2 with x ∈ F. B\* shows that F does not.

**Lemma 0.2 (B\* structure lemma; independent re-derivation of [adversary] math/01 §B\*).** I derived this independently and got the same result, by the same exchange argument.
Setting: M1, b(0) = e_z, rate ω, gimbal δ, a > 0, any attitude-independent throttle model, and ℓ = α_z r0z + β_z v0z.
The weight is w(s) = α_z s − β_z, negative on [0, s\*) and positive after. (math/01 uses the opposite sign convention, w < 0 early. Same content.)
Every maximizer of ℓ has Φ on the max-rate tent on [0, q] and is meridional with a single azimuth u. Hence v0_lat = −κu with κ > 0.
Two points of independent confirmation:
- the exchange step needs only that the admissible Φ-class is a **lattice** (closed under max/min) that contains the envelope. So the argument extends verbatim to any time-varying modulus |Φ'| ≤ κ(s). That is used in §6.2 (chord-rate model, κ = r/T(s)).
- the descent condition and the glide-slope condition hold for **every** unconstrained maximizer, because late T = ρ2 is forced. So the constrained maximizers are exactly the unconstrained ones that are feasible. I checked this argument line by line and it is right.

---

## 1. Route 1 — classical LCvx slacks for the attitude-rate-coupled direction

Every candidate below has convex, R_π-invariant constraints, so it accepts x̄\* (Lemma 0.1). x̄\* ∉ cl F (B\*, with the constraint set of §2). Hence the candidate is lossy on an open set of boundary data (int conv F \ cl F ≠ ∅). That rules out "lossless up to a null/degenerate set" as well, so Harris-type normality conditions cannot rescue any of them.

For each candidate I give the **explicit relaxed-feasible certificate** at the witness (the averaged lift) and the point where the PMP losslessness argument breaks.

| # | Candidate (mimics) | Constraints | Certificate at x̄\* | Where the LCvx proof breaks |
|---|---|---|---|---|
| 1a | Annulus slack Γ (Açıkmeşe–Ploen) + direction as state, ball relaxation | ‖u‖ ≤ σ, ρ1/m ≤ σ ≤ ρ2/m; d ∈ ball, ‖ḋ‖ ≤ ω; u = σ d | d_avg = d_z e_z: ‖d_avg‖ ≤ 1 and ‖ḋ_avg‖ ≤ ‖ḋ\*‖ ≤ ω | d is a *state*. Pontryagin maximizes the Hamiltonian over ḋ, and ‖d‖ = 1 is not enforced by any pointwise maximality. The interior of the ball is reachable at no cost |
| 1b | Scaled direction w = Γ d (σ-scaling, as in z = ln m) | ‖w‖ ≤ σ, ‖ẇ‖ ≤ ωσ + \|σ̇\| (or ≤ ωσ_max) | w_avg = w_z e_z, with norms dominated | same as 1a: \|w\| < σ along the chord |
| 1c | Thrust-vector rate on T itself (ramp/"tilt-rate" SOCP) | ‖u̇‖ ≤ ωσ (or ‖Ṫ‖ ≤ r) | u_avg = u_z e_z: ‖u̇_avg‖ = \|u̇_z\| ≤ ‖u̇\*‖ | **chord shortcut**: a speed bound in R³ admits the chord between antipodal-azimuth arcs, which is shorter than the arc on the sphere. See §6.2 |
| 1d | Body axis as a relaxed state + gimbal coupling (convexified) | ‖b‖ ≤ 1, ‖ḃ‖ ≤ ω; gimbal as ‖u − w_b‖ ≤ 2 sin(δ/2) σ with w_b = σ b relaxed to ‖w_b‖ ≤ σ, ‖ẇ_b‖ ≤ ωσ | vertical parts of (b, w_b, u) | same |
| 1e | Time-varying pointing cone (outer envelope, "Kunhippurayil–Harris–Açıkmeşe-style" annular/cone constraints) | u_z ≥ σ cos(δ + Φ̄(s)), Φ̄ = max-rate envelope | u_avg is on the axis: u_z ≥ σ cos(δ+Φ̄) holds a fortiori | No losslessness argument fails *inside* this program: it is a genuine LCvx for the **3DOF problem with a time-varying cone**, and that problem is ⊋ 5DOF. It is the **tightest convex outer relaxation of the velocity set** (§3.2, §6.3) but not of F |
| 1f | Semi-continuous inputs (Malyuta–Açıkmeşe), state-constrained LCvx (Harris–Açıkmeşe) | pointwise input-set relaxations + convex state constraints | as above | These theorems relax *input* sets pointwise. The attitude-rate coupling is a nonconvex *state* constraint (b ∈ S² with bounded speed), which none of these frameworks covers |
| 1g | SDP lift B ⪰ b bᵀ, conv SO(3) orbitope, quaternion LMI | (r0,v0) affine | averaged lift | Thm A (joint convexity), as in math/01 §2.7 |

**The common mechanism ("chord shortcut").** LCvx works because the nonconvex set is an *input* set, and the maximum principle selects an extreme point of its convex hull. Adding a rate limit turns the direction into a state on S². The geodesic (angular) speed bound on S² has no convex representation. Its convex surrogate (a Euclidean speed bound in the ball) lets the trajectory cut through the interior. At the B/B\* witness the relaxed trajectory is exactly the axis projection of the two rotated arcs. Its norm is cos(Φ+δ) times the bound, and it moves along the chord (the axis), never on the sphere. No slack can price this, because the nonconvexity lives in F itself (Thm A).

## 2. Route 2 — trying to break Claim B

I checked every step of math/00 §4 and math/02 §4. No algebraic hole:
- (1) inner-product triangle inequality: correct for α + β ≤ π.
- (2) a ≥ a1 from m(s) ≤ m0 − αρ1 s.
- (3) the equality case is a.e., and continuity of b upgrades it to every s.
- (4) rigidity: dist(b(s), e_z) = ωs with modulus ω forces a geodesic. This is a triangle-inequality equality and holds while ωs < π.
- (5) lateral ≠ 0.
- Gimbal chattering within the cone is already allowed (d measurable), and the equality case forces d a.e.
Loopholes found (scope, not algebra):
1. **Underground witnesses** (ρ1 < m g sec(δ+φ)). Found by [adversary] and accepted. My computation agrees: along P_u, z̈ < 0 throughout with ż(tf) = 0, so ż > 0 and z < 0 for all s < tf.
2. **Active tilt cap with long tf.** With angle(b, e_z) ≤ θ_c and ωtf > θ_c, rigidity holds only on [0, θ_c/ω]. After that, b may slide along the cap circle at azimuthal rate ω/sin θ_c while keeping d_z = cos(θ_c+δ). The lateral sum from the rising phase, L1 = ∫_0^{θ_c/ω} a1 sin(δ+ωs) ds · u0, can be cancelled on the circle once tf − θ_c/ω exceeds the time needed to swing the azimuth by > π. That time is about π sin θ_c/ω plus the cancellation dwell. **Then M_cap := (0, ∫a1 cos(δ + min(ωs, θ_c))) ∈ R: the B witness fails.**
3. **Free initial attitude.** If b(0) is a decision variable in a cap of radius θ_c, then M_cap is reached by circling the cap boundary from time 0. This needs ω tf ≥ 2π sin θ_c (uniform azimuth sweep).
**Repair (both 2 and 3):** use B\* with a small switch time s\*, 2ωs\* < θ_c − (0 or δ). If b(0) is free in the cap, the exchange argument gives Φ̂ = min(θ_c, p + ω(s\* − s)) on [0, s\*]. The azimuth can then turn by at most ωs\*/sin θ_c < π/2 on the plateau, and it is constant on the max-rate descent (meridional). So every lateral increment lies in an open half-plane about u(0), and v0_lat ≠ 0. The rest of B\* is unchanged. **Verdict: Claim B is algebraically correct, but should be retired in favour of B\*, which covers 1–3.**

## 3. Route 3 — exact restricted classes

### 3.1 Pointing-cone dichotomy (THEOREM RR-P — **M1 ONLY**, rigorous)
**Scope warning.** This theorem is for the kinematic model M1, where the gimbal is decoupled from the body torque. The body can stay upright while the gimbal points anywhere in its cone. It does **not** hold for the real pure-TVC vehicle, where the gimbal angle is the torque input. For pure TVC the class collapses to θ_p = 0; see §3.4.
Model: M1 plus the standard LCvx pointing constraint angle(d, e_z) ≤ θ_p. Fixed b0 := b(0), optional b(tf) = b_f. Any throttle/mass model and any rotation-invariant convex state constraints.
**(a) If θ_p ≤ δ and angle(b0, e_z), angle(b_f, e_z) ≤ δ − θ_p, then F_5DOF = F_3DOF(θ_p)** (the 3DOF problem with pointing cone θ_p).
*Proof.* "⊆": the pointing constraint is present in both. "⊇": take b moving from b0 to b_f along the minor geodesic at speed ≤ ω, which stays in cap(e_z, δ−θ_p) by geodesic convexity, or b ≡ b0 if b_f is free. Then for every s, cap(e_z, θ_p) ⊆ cone(b(s), δ) (triangle inequality), so every 3DOF thrust history is 5DOF-admissible. ∎
Consequently **any LCvx guarantee for the 3DOF problem with pointing cone θ_p transfers verbatim to 5DOF.** Examples: Açıkmeşe–Ploen, Açıkmeşe–Carson–Blackmore 2013, and Harris–Açıkmeşe with state constraints, each under its own normality hypotheses. The 3DOF solution is realized with the body held still and the gimbal doing all the pointing. For GTPL (box gimbal ±15°/axis) the inscribed cone is δ = 15°, so the class is "thrust within 15° of vertical, started upright".
**(b) If θ_p > δ (and ρ1 > 0, plus the B\* braking condition), F_tf is nonconvex for every tf for which the condition holds.**
*Proof.* B\* with s\* small enough that the dive tilt Φ+δ stays below θ_p (ω s\* < θ_p − δ). On [0, s\*] the integrand −w a cos(min(Φ+δ, θ_p)) is then strictly increasing in Φ, so the exchange argument and rigidity go through unchanged. ∎
So **θ_p = δ is the sharp threshold** for M1: below it 5DOF *is* 3DOF, above it no uniform LCvx exists.
**Caveat (M2, gimbal-rate limits).** With a gimbal slew limit ω_g, d itself is rate-limited, and B\* applied to d (with δ = 0, modulus ω_g, cap θ_p) gives nonconvexity again. The size of the nonconvexity is set by the rigid phase of d, of duration θ_p/ω_g. A crude estimate of the gap, scaling numerics' law 0.31·ωtf·|P_x| to this phase: Γ_M2 ~ a1 θ_p²/ω_g. For GTPL (a1 ≈ 5, θ_p = 0.26 rad, ω_g = 1.75 rad/s) that is ≈ 0.05–0.2 m/s, i.e. **practically negligible**. Not proven. [numerics] please check.

### 3.2 ρ1 = 0, no down-thrust: velocity set convex (THEOREM RR-R0, rigorous sketch)
M1 with α = 0, ρ1 = 0, ρ2 > 0, b(0) = e_z, b(tf) free or = e_z, and δ + Φ̄(s) ≤ π/2 for all s (or a pointing cap ≤ π/2). **Then R = {∫ a d} is convex.**
*Proof.* (i) R is compact and star-shaped about 0: scale a by λ ∈ [0, 1].
(ii) For every unit e, the maximizer endpoint of e·∫a d is unique. Pointwise e·d ≤ c(s) := cos(max(ψ_e − δ − Φ̄(s), 0)). Here a = ρ2/m where c > 0 and a = 0 where c ≤ 0 (c ≤ 0 happens only for e outside the closed upper reachable region). Where c > 0 and e lies outside cap(δ + Φ̄(s)), equality forces b(s) at tilt Φ̄(s) in e's azimuth: rigid, via the geodesic equality case. Where e lies inside the cap, d = e. Ties (c = 0) occur on a null set. Every exposed face of conv R is therefore a point of R.
(iii) ∂conv R ⊆ R, and star-shapedness gives conv R ⊆ R. ∎
Meaning: the velocity-increment obstruction is entirely a **min-throttle** (or down-thrust, P-L0) phenomenon. **Full F at ρ1 = 0: OPEN.** The weights there are time-varying, e(s) = e1 + (tf − s)e2. Uniqueness of 5DOF maximizers is no longer clear, because the relaxed optimum may require azimuth rotation, and ties between distinct compromises are not excluded. Test proposed for [numerics] (§7).

### 3.3 Other regimes
- **Large ω:** finite ω still gives nonconvexity (B\*). The gap → 0 roughly linearly in 1/ω for a fixed geometry ([numerics]' law). So the relaxation is ε-lossless asymptotically but never exact.
- **Large δ:** helps only through 3.1 (δ ≥ θ_p). Otherwise B\* holds for all δ < π.
- **Long tf:** B\* holds for every tf (and P-L for b(tf) free).
- **"Attitude never binds":** Θ_nb := F_3DOF(cap(b0, δ)) is convex, ⊆ F_5DOF, and decidable by one SOCP. That gives a **sound inner test**: if the 3DOF LCvx with cone δ about b0 is feasible, it is an exact 5DOF solution. Paired with the outer test 1e (time-varying envelope cone, an infeasibility certificate), this is a convex **sandwich** Θ_nb ⊆ F ⊆ F_env. The B\* witnesses lie strictly in the gap, so the sandwich cannot close in general. This is the best a single convex program can do, and it is useful for the practical phase.

### 3.4 The honest exact class for pure TVC (M3b, gimbal = torque input)
Body dynamics: the engine sits at −L b and the thrust is T d. The torque is −LT b × d, so the transverse angular acceleration is
  b̈_⊥ = −k(t) d_⊥ (+ centripetal terms), k = L T / J_t,
where d_⊥ is the part of d perpendicular to b. A gimbal tilted toward +u accelerates the body toward −u. For small angles, e := b − d obeys **b̈ = k (b − d)**. Relative to the commanded thrust direction, the body axis is an **unstable** second-order system with rate √k. For GTPL (L = 0.589 m, J_t = 63.6 kg m² wet), √k = 1.92 s⁻¹ at 400 N and 3.04 s⁻¹ at 1000 N.

**Proposition RR-TVC.** Assumptions: classical (3DOF, physical-coordinate) LCvx, as in the current GTPL guidance; pure TVC with ρ1 > 0; boundary data (r0, v0) with fixed (b0, ω0). The relaxed optimum is exactly realizable only on the following sets of boundary data:
(a) with terminal attitude constraints b(tf) = e_z, ω(tf) = 0: a set of **measure zero**, under the generic-submersion assumption below;
(b) with free terminal attitude: an **exponentially thin** open set, of width ~ δ e^{−√k tf} around a codimension-2 manifold. For GTPL at tf = 7 s that is about 4·10⁻⁷ rad of initial attitude.
The **uniform** exact class (the analogue of RR-P) is θ_p = 0 (pure vertical thrust) with b0 = e_z and ω0 = 0.
*Argument (linearized; rigorous for the linearized model, heuristic for the nonlinear one).*
- The LCvx optimum fixes d\*(·) = u\*/‖u\*‖ from (r0, v0) alone, ignoring (b0, ω0).
- Realizability needs a body path b with angle(b, d\*) ≤ δ solving b̈ = k(b − d\*) from (b0, ω0). Given d\*, this ODE determines b uniquely, with 4 transverse constants all fixed by the initial data.
- (a) The 4 terminal conditions must then hold as equalities. They are 4 equations on the 6-dimensional (r0, v0) space, so the solution set has codimension ≥ 1 (codimension 4 if the map is a submersion, which is the generic case and is assumed here, not proven). Either way the set has measure zero.
- (b) Staying within δ over [0, tf] forces the unstable-mode coefficient c to satisfy |c| e^{√k tf} ≲ δ.
- Uniform class: with θ_p > 0, any nonvertical thrust needs d ≠ b at some time. That excites the unstable mode, so F_TVC(θ_p) ≠ F_3DOF(θ_p). (Convexity of F_TVC(θ_p) is the open M3b question.) With θ_p = 0 we have d ≡ e_z, and b stays at e_z iff b0 = e_z and ω0 = 0. That gives F_TVC = F_3DOF(0), which is exact and convex but degenerate (1D vertical landing). ∎
**Flat-coordinate reading.** The orchestrator's CLAIMS row FLAT uses y = r + (J_t/(mL)) b, with ÿ = (T cos μ/m − ε‖ω‖²) b − g. A relaxed LCvx optimum posed in y is bang-bang, ‖u\*‖ ∈ {ρ1/m, ρ2/m} a.e. Turning (ω ≠ 0) gives f < T/m. That is fatal on ρ2-arcs. On ρ1-arcs it would need T > ρ1 and a different mass history. So exact realizability forces ω ≡ 0, i.e. a **constant thrust direction**. The set of (r0, v0) whose optimum has constant direction b0 has dimension ≤ 3 (2 scalar impulses plus tf), so it has measure zero in R⁶.
**Conclusion.** For the real vehicle, classical LCvx is exact only on a negligible set. Its relaxed optimum is generically *not* flyable without a tracking error, which is consistent with the 24 ms azimuth flips in context/vehicle.md §5.4.

## 4. Route 4 — free final time
**Lemma RR-LS (line search cannot be lossless). For [proof]/[lean]: pure set theory plus linear algebra.**
Setting:
- W is a set of horizons.
- For each t ∈ W, F_t ⊆ X := R⁶ is the true feasible set.
- A *per-horizon relaxation family* is {C_t}_{t∈W} with C_t ⊆ X × Y_t convex, X entering linearly, and F_t ⊆ G_t := proj_X C_t.
- Line search accepts A := ∪_{t∈W} G_t. Write F_W := ∪_{t∈W} F_t.
(i) *Abstract kill.* If ∃ t\* ∈ W and x̄ ∈ conv(F_{t\*}) \ F_W, then x̄ ∈ A \ F_W, so no per-horizon family is feasibility-lossless. For any cost with attained relaxed optima, the relaxed optimum at x̄ (over t and y) is not original-feasible, so the family is not lossless in optimization form either.
*Proof.* G_{t\*} is convex and contains F_{t\*}, so it contains conv F_{t\*} ∋ x̄. And x̄ ∉ F_W by hypothesis. ∎
(ii) *Symmetric supply of x̄.* Hypotheses:
- (H1) R is a linear involution of X (here R_π) with R F_t = F_t for all t.
- (H2) ℓ is a linear functional with ℓ ∘ R = ℓ, attaining its maximum ℓ\* over the graph Gr := {(t, x) : t ∈ W, x ∈ F_t} at some (t\*, x\*).
- (H3) Every maximizer (t, x) ∈ Gr of ℓ satisfies Px ≠ 0, where P := (I − R)/2 (the lateral projection).
Then x̄ := (x\* + R x\*)/2 ∈ conv(F_{t\*}) \ F_W.
*Proof.* x̄ ∈ conv F_{t\*} because x\*, R x\* ∈ F_{t\*} (H1). Suppose x̄ ∈ F_{t'} with t' ∈ W. Then ℓ(x̄) = (ℓ(x\*) + ℓ(Rx\*))/2 = ℓ\*, so (t', x̄) is a maximizer. But P x̄ = (Px\* + PRx\*)/2 = (Px\* − Px\*)/2 = 0, since PR = −P, contradicting (H3). ∎
(iii) *B\* gives (H1)–(H3).*
- (H1): rotation invariance of the dynamics, of b(0) = e_z, and of the altitude/glide/tilt/fuel constraints.
- (H2): W compact (e.g. [t1, min(t2, t_fuel)], t_fuel = (m0 − m_dry)/(αρ1), since every flight burns ≥ αρ1 per second), plus closedness of Gr from relaxed-control compactness and B\*'s Dirac argument.
- (H3): a graph maximizer (t\*, x\*) is a fixed-t\* maximizer, because ℓ does not depend on t. If the B\* braking condition holds at t\*, the structure lemma gives v0_lat ≠ 0. A sufficient uniform condition: the braking condition holds for every t ∈ W.
**Verdict for free final time: FAILS** (both as a single program with tf as a decision variable, and as an LCvx-style line search).

### 4.1 Other remarks on free final time
- **Single program with tf (or 1/tf, or dilation) as a jointly convex decision variable:** each slice F_t would be convex. FAILS (math/02 Prop 7.2).
- **Line search over tf (the actual Açıkmeşe–Ploen practice).** Theorem A does not apply directly, because the accepted set is a union ∪_t G_t of convex sets G_t ⊇ F_t. The general statement: the family is feasibility-lossless iff G_t ⊆ F_free for all t. Since G_t ⊇ conv F_t, this **requires conv F_t ⊆ F_free := ∪_{t'} F_{t'} for every t in the window.**
  **B\* violates this.** On a compact window W (for example W = [0, t_fuel], with t_fuel = (m0 − m_dry)/(αρ1), since every flight burns ≥ αρ1 per second), maximize ℓ over (t, control). The weight w does not depend on t, so a maximizer x\* at t\* exists and is a fixed-t\* maximizer, hence structured. Then x̄\* ∈ conv F_{t\*}. If x̄\* ∈ F_{t'} for some t' ∈ W, it would be a maximizer with zero lateral data, which is a contradiction. So x̄\* ∈ conv F_{t\*} \ F_free.
  **Every per-tf convex family therefore accepts x̄\* at t = t\*, although x̄\* is infeasible at every horizon.** This covers feasibility form and, a fortiori, min-fuel and min-error optimization form: a relaxed optimum at x̄\* cannot be original-feasible.
  Condition: the B\* braking/descent condition must hold at t\*. Sufficient: it holds for every t ∈ W, which is true for small s\* when ρ2 cos(2ωs\*)/m0 > g and min W ≫ s\*.
  - *Earlier attempt, superseded:* for the state-unconstrained min-fuel line search I first had a separate proof (x̄_M at t with relaxed fuel ≤ αρ1 t < J\*). It is not needed now.
  - *Earlier open question, resolved:* I had worried that min-fuel losslessness with a ground constraint hinges on a parameter-dependent "lateral helps fuel" sign. My 1D calculation: d(fuel)/d(fall-phase vertical thrust) ∝ a1/(g−a1) + (2a1 − a2)/(a2 − g). This is +0.43 at m = 75 kg and −0.9 at m = 90 kg for GTPL thrusts. The feasibility argument above makes the sign irrelevant to the impossibility question.
- **Verdict: FAILS.** Free final time is not an escape, given the window condition.

## 5. Route 5 — 6DOF
- **Kinematic 6DOF (ω a control, ‖Ω‖ ≤ ω):** ‖ḃ‖ ≤ ‖Ω‖, so F_6 ⊆ F_M1. The B\* maximizers are planar with zero roll, so they are 6DOF-realizable. Hence max_{F_6} ℓ = max_{F_M1} ℓ, every F_6 maximizer is an M1 maximizer (structured), and B\* transfers. **Any quaternion/dual-quaternion/SO(3)-orbitope lift with (r0,v0) affine is jointly convex ⇒ Thm A ⇒ FAILS.**
- "Attitude as input with rate limits" is M1 itself: FAILS.
- **Torque-limited (M3a, independent torque):** Claim B transfers with envelope κs²/2 (proof agent, adversary). **B\* does not transfer verbatim.** Its exchange step needs the admissible Φ-class to be closed under max/min. The class {|Φ''| ≤ κ, Φ(0) = Φ'(0) = 0} is not, because the max of two such functions has a velocity jump. A replacement structure lemma needs bang-bang uniqueness of the 1D tilt problem. Then the saturated radial acceleration leaves no budget for tangential acceleration, which gives meridional motion. **OPEN** (owned by [adversary-6dof]).
- **TVC-coupled M3b:** OPEN, owned by [adversary-6dof] (see their BREAK).

## 6. Claim T — Berning–Strohl–Bieniawski 2023 and rate notions

### 6.1 What the paper is
Full text unobtainable: AIAA paywall, no arXiv/NTRS/ResearchGate copy, and the METU 2025 thesis that cites it contains no rate constraints. The Wang et al. survey (arXiv 2311.05115, §PDG, p.21) says it is a **3DOF** fuel-optimal problem with max tilt rate, max tilt acceleration, max thrust ramp rate, inverse-square gravity and a minimum altitude, "relaxed into an SOCP" with the Açıkmeşe–Ploen framework. Inverse-square gravity alone makes the dynamics nonlinear, so even the 3DOF problem is not covered by the classical LCvx theorems without approximation.
**There is no 5DOF losslessness theorem there to reconcile.**

### 6.2 Which rate notions are SOC-representable, and losslessness of each
| Notion | Constraint | SOC-representable? | Lossless? |
|---|---|---|---|
| Thrust ramp | \|σ̇\| ≤ k (or ΔΓ) | yes (linear) | does not touch direction; standard |
| Thrust-vector ("chord") rate / accel | ‖u̇‖ ≤ ωσ, ‖ü‖ ≤ … (finite differences) | yes | **No (proved).** The original problem (‖T‖ ∈ [ρ1,ρ2], ‖Ṫ‖ ≤ r, T(0) given) has direction rate \|ḋ\| ≤ ‖Ṫ_⊥‖/‖T‖ ≤ r/T(s). It is M1 with δ = 0 and time-varying modulus κ = r/T, and B\* applies (Lemma 0.2, lattice). The SOCP accepts the averaged witness: ‖u̇_avg‖ ≤ ‖u̇\*‖ ≤ ωσ (chord shortcut). Any reported tightness must be instance-wise/empirical, or must assume that min-thrust and rate constraints are never simultaneously active |
| Tilt envelope | u_z ≥ σ cos(θ0 + ωt) | yes | lossless for the 3DOF time-varying-cone problem (classical). As a model of a rate limit it is only an outer bound |
| Tilt-angle rate (azimuth free) | \|d/dt arccos(u_z/‖u‖)\| ≤ ω | **no** (arccos of a ratio). Only linearized/SCP versions exist | see 6.3 |
| Full direction rate | ‖ḋ‖ ≤ ω on S² (‖ω_⊥‖ ≤ ω) | no | impossible (A + B\*) |

### 6.3 The tilt-angle-only model (azimuth may jump)
Model M1-tilt: Φ is ω-Lipschitz with Φ(0) = 0, azimuth is arbitrary measurable, d has tilt in [Φ−δ, Φ+δ] ∩ [0, π], and a ∈ [a1, a2].
**THEOREM RR-T (velocity set, rigorous sketch).** With α = 0, R_tilt = R_env := {∫ u : u(s) ∈ conv{a d : tilt(d) ≤ δ + ωs}}, so R_tilt is convex.
With α > 0, R_tilt = R_env^α (equality per throttle history), and its convexity reduces to the 3DOF-with-cone question (math/02 P-3).
*Proof.*
(i) R_tilt ⊆ R_env, and both are compact and rotation-invariant about e_z.
(ii) **Laterally down-closed:** flip the azimuth by π on a set A. By Lyapunov, {∫_A a d_lat} is a convex set containing 0 and y_lat, so the lateral part takes every value λ y_lat, λ ∈ [−1, 1], at the same vertical. Rotation then fills the disk.
(iii) For e ≠ ±e_z the maximizer of e·∫u over R_env is pointwise unique a.e.: azimuth of e, tilt min(ψ_e, δ+ωs), a = a2 or a1 by the sign of e·d. It is realized by the **monotone** tilt Φ = min(ωs, (ψ_e − δ)_+), which is ω-Lipschitz. So every exposed point of R_env lies in R_tilt.
(iv) In the meridian half-plane, the only flat boundary pieces of the section of R_env come from e = ±e_z (horizontal top/bottom disks). Their rims are limits of exposed points, so they lie in the closed set R_tilt, and so do the disks by (ii).
(v) The meridian section of R_env is {ρ ≤ ρ_max(z)}. Its boundary curve lies in R_tilt, and (ii) fills the rest. ∎
So **for velocity data alone, a tilt-rate-only limit IS exactly convexifiable** by the classical envelope LCvx. The B witness M is reachable by azimuth chattering, as [lit-review] predicted.

**But not for full (r0, v0).** Exposed faces of F_env correspond to weights e(s) = e1 + (tf−s)e2. Their folded tilt χ(s) = atan2(|e_h|, e_z) can jump: when the weight line passes through the origin, χ jumps from atan c to π − atan c. The envelope optimum then needs a tilt jump, while M1-tilt cannot jump.
Exact DP (Lipschitz grid, globally optimal) against the envelope support, GTPL-like a1 = 5, a2 = 12.5, ω = 0.4, δ = 15°, tf = 7:
- support gap up to **3.4%** (s0 = 5, c = 0.3, χ jump 147°);
- 0.2–0.4% for a 90° jump;
- ≈ 0 for weights with smooth χ (DP discretization bias ≈ −0.05%).
(`envelope_gap.py`, `envelope_gap2.py`.) So **the envelope SOCP is lossy for M1-tilt**. The lossy faces involve down-pointing weights (χ > 90°). With a pointing cap θ_p ≤ 90° the gap may vanish. Not tested.
**Convexity of F_tilt itself: OPEN.** A DP scan of the V-shaped weight family (κ ∈ [0, 4], s0 ∈ [3, 5]) shows the optimal dip depth varying continuously, with no tie and no evidence of a non-singleton face (`dp_scan_fine.py`). I conjecture F_tilt convex at least with θ_p ≤ π/2. Even then, no convex program is known for it, since tilt-angle rate is not SOC-representable. **So this is not yet a "possible" result.**

### 6.4 Why full-direction rate is the physical model, and whether the gap matters for GTPL
With b = (sin θ cos ψ, sin θ sin ψ, cos θ), the transverse body rate is ‖ω_⊥‖ = ‖ḃ‖ = (θ̇² + sin²θ ψ̇²)^{1/2}. A tilt-only limit drops sin²θ ψ̇², which permits instantaneous azimuth flips at nonzero tilt. That is precisely the maneuver that cancels lateral thrust in the B/B\* witnesses.
At GTPL tilts θ ≤ 15–25°, the cheapest tilt reversal (azimuth +π) runs through vertical, an angle of 2θ = 0.52–0.87 rad. At ω = 0.3–0.5 rad/s that takes **1.0–2.9 s, i.e. 10–40% of tf ≈ 7 s.** The stored 3DOF solutions do it in 24 ms (context/vehicle.md §5.4).
Numerics' gap law (dist ≈ 0.31·ωtf·|P_x| for the full-direction model, versus 0 for the tilt-only velocity set) is first order in ωtf. **The two models differ materially for GTPL**, and the small sin θ does not make the tilt-only model a good approximation.

## 7. Requests for [numerics]
1. **RR-T full-F test:** with a pointing cap θ_p ∈ {30°, 60°, 90°}, recompute the envelope-vs-DP support gap of §6.3 for jumping-χ weights. Does the gap vanish when down-pointing is excluded?
2. **RR-R0 full-F test (ρ1 = 0):** search for ties in 5DOF maximizers for weights e(s) whose horizontal azimuth rotates. For example, take e1 ⟂ e2 horizontal, plus a vertical part. Report any non-singleton face, or a midpoint distance > 0.
3. **RR-P caveat:** estimate dist(x̄\*, F) for M2 with ω_g = 100°/s and θ_p = 15° (expected ≲ 0.2 m/s).
4. **Line-search check:** for GTPL with r_z ≥ 0, take the B\* pair at its optimal t\* and verify that x̄\* is infeasible for every t ∈ [1, 15] s (NLP), while each fixed-t envelope SOCP accepts it at t\*.
