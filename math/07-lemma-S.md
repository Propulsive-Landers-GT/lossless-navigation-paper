# Lemma S (slice nonconvexity, hard soft landing): theorem, proof, regime, constants

Author: [proof-s]. Status: **Theorem S is proved (rigorous, quantitative) in an explicit short-horizon regime.**
That regime requires minimum-throttle thrust-to-weight > 1/cos(δ+ωt_f). **GTPL is NOT in it.**
For GTPL, S holds numerically at dive-then-brake faces ([numerics] s1_slice) but is unproved.
Numerics: `numerics/proof-s/` (own venv).

## 0. Summary

**What S asks.** Model M1, hard landing r(t_f)=(p,0), v(t_f)=0, altitude r_z ≥ 0.
Find vertical data ζ = (r_0=(0,0,h), v_0=(0,0,v_{0z})) whose landing-offset set
L(ζ) = {p : some admissible trajectory from ζ lands at (p,0) with v(t_f)=0} satisfies 0 ∉ cl L(ζ) ≠ ∅.

**Result (Theorem S, §3).** Two ingredients:
- **Master inequality (all 3D maneuvers, coning included).** For every admissible M1 trajectory, the vertical waste gain := ∫a₁ − I_z satisfies
  gain ≤ B + C_m ‖π_m‖², where π_m is the affine function with the same two lateral moments (∫F, ∫sF) as the lateral thrust force F.
  B and C_m are explicit (§2).
- **An explicit planar witness.** A single-crossing S-turn with I_h = 0 whose gain exceeds B.

For the witness's vertical data ζ_w, every landing offset then satisfies |p| ≥ r_S = (M t_f³/(12 C_m))^{1/2}, with M = gain_w − B > 0.
- L(ζ_w) contains the whole circle |p| = |p_w|, so 0 ∈ conv L(ζ_w) \ cl L(ζ_w).
- Theorem D (math/02 §11.2) therefore makes every state-linear relaxation of the minimum-landing-error problem with hard v(t_f)=0 lossy at ζ_w with target q = 0.
  The relaxed error is 0; the true error is ≥ r_S, which is **0.4–1.9 m** in the table of §4.

**How coning is handled.** The only nonconvex step is "maximize a convex quadratic over rate-limited paths". It is bounded by a Wirtinger inequality modulo affine functions (Lemma W):
‖P^⊥ f‖² ≤ (T/2π)² ‖ḟ‖² for f ∈ H¹((0,T); ℝ^N).
This inequality is **componentwise and rotation-invariant**. It therefore bounds 1D, 2D (coning) and even ℝ^N-valued ("Hilbert-lifted") lateral paths with the same constant.
- Coning never needs to be analysed separately.
- The witness wins because a single-crossing S-turn that *does not return to zero tilt* has mean-square lateral tilt (3√2−4)/6·Ω² = 0.0404 Ω².
  The best affine-free path has at most Ω²/(4π²) = 0.0253 Ω².
  (The "amplitude Ω/4 triangle", 1/48 = 0.0208 Ω², used in the earlier comparisons in math/01 §7, is far from Pv-optimal. That is why the margin looked thin.)

**Regime (explicit, checkable):** δ+ωt_f < π/2; (ρ₁/m₀) cos(δ+ωt_f) > g₀ (altitude automatic); the K-condition κ₀ > A' (automatic if ρ₁=ρ₂); and M > 0.
With the constants of §2, M > 0 holds e.g. for ωt_f ≤ 0.55 rad at δ=0, ωt_f ≤ 0.45 rad at δ=5°, ωt_f ≤ 0.30 rad at δ=10°. The analytic constants fail at δ ≥ 15° (see §5 for why and what the S-procedure SDP gives).

**Realism caveat ([adversary]).** The regime needs min-throttle T/W > 1/cos(δ+Ω) > 1, i.e. a vehicle that **cannot hover at minimum throttle**. That excludes essentially every deep-throttling lander, not just GTPL. The theorem settles S as a mathematical statement about M1 and gives certified lossy instances for Theorem D. It does not give a realistic powered-descent instance.

**GTPL (task 2): no instance in the proven regime.** ρ₁/m₀ = 5.0 m/s² (wet) to 7.2 m/s² (dry), always < g₀ = 9.81.
- So the pure-waste face starts underground (same mechanism as [adversary]'s BREAK of Thm B).
- For GTPL, S must use dive-then-brake faces. [numerics] s1_slice (exact 3D, coning starts, r_z ≥ 0, 24 restarts) finds strict gaps opt(Pvr) − opt(Pv) = 0.0156 m (t_f=4 s) and 0.0088 m (t_f=8 s), with Pv optimizers landing 1.47 m / 2.39 m off-axis. So S holds numerically for GTPL, with the gap thin in the vertical functional ℓ.
- Rigorous GTPL proof: **open**. The L²/Wirtinger slack (cm–dm in ℓ) exceeds the ℓ-gap (mm–cm), see §5.

**Long horizons (task 3): S does not fail; coning fills the dent only on capped plateau faces.**
- Our certificate is short-horizon: the quadratic majorant degrades with tilt.
- Numerically, strict gaps persist at ωt_f = 1.6 and 3.2 rad ([numerics] s1, dive faces, cap none/30°).
- Coning can close the gap only at faces where the maximizer has a long tilt-capped plateau (Remark 6.2, after [adversary] math/01 §7). There it removes ~87% of it at t_f = 20 s ([adversary] s3), but not all of it. Short-dive faces never reach the cap.
- Dents can exist only at throttle-saturated (face) data (Remark 6.1).

## 1. Setting and notation
M1 as in math/02 §1.2 with g = −g₀e_z, b(0)=e_z, b(t_f) free, α ≥ 0. T := t_f, Ω := ωT, τ(s) := δ+ωs, τ̄ := δ+Ω.
- a₁₀ := ρ₁/m₀; a₁(s) := ρ₁/(m₀−αρ₁s) (min-throttle acceleration); a₂ := ρ₂/(m₀−αρ₂T); ε_m := a₁(T)/a₁₀ − 1.
- Lateral force F := a d_h ∈ ℝ²; I_h := ∫₀ᵀ F, I_z := ∫₀ᵀ a d_z.
- **gain(c) := ∫₀ᵀ a₁ − I_z(c)** is the vertical impulse "wasted" relative to upright minimum throttle.
- L² is L²((0,T); ℝ²) with norm ‖·‖. **P** is the orthogonal projection onto the affine functions {c₀ + c₁ s : c₀, c₁ ∈ ℝ²}; P^⊥ = I − P.
  For f ∈ L², Pf depends only on the moments m(f) := (∫f, ∫sf). Write π_m for the affine function with moments m. Then
  ‖π_m‖² = mᵀG⁻¹m (componentwise), G = [[T, T²/2],[T²/2, T³/3]], so ‖π_{(0,q)}‖² = 12|q|²/T³.

**Landing from vertical data.** By math/02 Lemma 1.1, a trajectory from ζ = ((0,0,h),(0,0,v_{0z})) lands at (p,0) with v(T)=0 iff
- I = (0,0, g₀T − v_{0z}), i.e. I_h = 0 and I_z is fixed by ζ;
- J_h = ∫(T−s)F = p; with I_h = 0 this is ∫sF = −p;
- J_z is fixed by ζ.

Hence **every trajectory from ζ has the same gain**, and m(F) = (0, −p).

## 2. The master inequality (all admissible trajectories, any attitude path in 3D)

**Lemma P1 (pointwise majorant).** Let a ≥ a₁(s) > 0 and d ∈ S² with ∠(d,e_z) ≤ τ(s) < π/2. Then
 −a d_z ≤ −a₁(s) + a₁(s) c̄(s) |d_h|² − (a − a₁(s)) cos τ(s),  c̄(s) := 1/(1+cos τ(s)).
*Proof.* −a d_z = −a₁d_z − (a−a₁)d_z, and d_z ≥ cos τ > 0. Also 1 − d_z = |d_h|²/(1+d_z) ≤ c̄|d_h|². ∎

**Lemma P2 (kinematics).** For every admissible (T,d,b):
- (i) a(s) ≥ a₁(s), because m(s) ≤ m₀ − αρ₁s, and a(s) ≤ a₂;
- (ii) ∠(d(s),e_z) ≤ δ+ωs;
- (iii) β := b_h is Lipschitz with β(0)=0 and |β̇| ≤ |ḃ| ≤ ω a.e. (math/02 Prop 1.2);
- (iv) |d_h − b_h| ≤ |d − b| = 2 sin(∠(d,b)/2) ≤ 2 sin(δ/2).

**Lemma W (Wirtinger modulo affine functions).** For f ∈ H¹((0,T); ℝ^N):
 ‖P^⊥f‖² ≤ (T/2π)² (‖ḟ‖² − |f(T)−f(0)|²/T) ≤ (T/2π)² ‖ḟ‖².
This is sharp, with equality for f = c(1 − cos(2πs/T)).
*Proof.*
1. Let f̃(s) = f(s) − f(0) − (s/T)(f(T)−f(0)). Then f − f̃ is affine, so P^⊥f = P^⊥f̃.
2. Constants are affine, so ‖P^⊥f̃‖ ≤ ‖f̃ − c‖ for every constant c; take c = mean of f̃.
3. f̃(0) = f̃(T) = 0, so f̃ extends to a T-periodic H¹ function. The periodic Wirtinger inequality (Parseval) gives ‖f̃ − mean‖² ≤ (T/2π)²‖f̃'‖².
4. Finally ‖f̃'‖² = ‖ḟ − (f(T)−f(0))/T‖² = ‖ḟ‖² − |f(T)−f(0)|²/T.

Everything is componentwise, so the inequality holds verbatim for ℝ^N-valued f with |·| Euclidean. ∎

**Corollary W.** If |β̇| ≤ ω a.e. on (0,T), then ‖P^⊥β‖ ≤ ωT^{3/2}/(2π), whatever the dimension of the range of β.

**Constants.**
- c₀ := 1/(1+cos δ).
- δ_e := 2 sin(δ/2) + ε_m sin τ̄.
- E₄ := a₁₀(1+ε_m)² ∫₀ᵀ (c̄(s) − c₀) sin²τ(s) ds.
- B := a₁₀ c₀ T (Ω/(2π) + δ_e)² + E₄.
- A' := c₀/a₁₀, κ₀ := cos τ̄ / ((a₂ − a₁₀) sin²τ̄) (κ₀ := +∞ if ρ₁ = ρ₂), and C_m := A'κ₀/(κ₀ − A') (C_m := A' if ρ₁ = ρ₂).

**Proposition M (master inequality).** Assume τ̄ < π/2 and κ₀ > A'. Then every admissible M1 trajectory c (no state constraints needed) satisfies
 gain(c) ≤ B + C_m ‖π_{m(F)}‖².

*Proof.*
1. *Split the throttle.* Put Δ := a − a₁(s) ∈ [0, a₂ − a₁₀] and K := Δ d_h. Then F = a₁(s)d_h + K, and |K| ≤ Δ sin τ̄ ≤ (a₂−a₁₀) sin τ̄.
   Hence Δ cos τ(s) ≥ Δ cos τ̄ ≥ |K| cot τ̄ ≥ κ₀|K|².
   Integrating Lemma P1 gives gain ≤ ∫ a₁c̄|d_h|² − κ₀‖K‖².
2. *Normalize the mass.* Put v := (a₁(s)/a₁₀) d_h, so F = a₁₀v + K. Then a₁|d_h|² = a₁₀(a₁₀/a₁)|v|² ≤ a₁₀|v|², and |v| ≤ (1+ε_m) sin τ(s).
   Writing c̄ = c₀ + (c̄ − c₀) gives gain ≤ a₁₀c₀‖v‖² + E₄ − κ₀‖K‖².
3. *Eliminate K.* ‖v‖² = ‖P^⊥v‖² + ‖Pv‖². Also PF = π_m, so PK = π_m − a₁₀Pv and ‖K‖ ≥ ‖PK‖.
   With x := a₁₀Pv: a₁₀c₀‖Pv‖² − κ₀‖K‖² ≤ A'‖x‖² − κ₀‖x − π_m‖² ≤ (A'κ₀/(κ₀−A'))‖π_m‖², by maximizing a concave quadratic.
4. *Wirtinger.* v = β + ẽ with ẽ := (d_h − b_h) + (a₁/a₁₀ − 1)d_h, and |ẽ| ≤ δ_e pointwise by P2(iv).
   So ‖P^⊥v‖ ≤ ‖P^⊥β‖ + ‖ẽ‖ ≤ ωT^{3/2}/(2π) + δ_eT^{1/2}, by Corollary W.
5. Collect the terms. ∎

*Remarks.*
- (a) Only step 4 touches the nonconvex attitude constraint. Because Lemma W is an L² statement applied componentwise, the bound holds for planar S-turns, coning, multi-crossing paths, and even paths with values in ℝ^N.
- (b) If ρ₁ = ρ₂ then K = 0, a₁₀Pv = π_m, and the same proof gives C_m = A'.
- (c) A variant without E₄ uses c̄(s) ≤ c̄(T) = 1/(1+cos τ̄) in step 2. It is better for δ = 0 at larger Ω (certified up to Ω ≈ 1.0 rad); see `numerics/proof-s/regime.py`.

## 3. Theorem S

**Witness (planar single-crossing S-turn, minimum throttle).**
- Take u = e_x, T(s) ≡ ρ₁ (so a = a₁).
- Tilt profile φ(s) := ωs for s ≤ t₁ and ω(2t₁ − s) for s > t₁. The attitude is b(s) = (sin φ, 0, cos φ). It is planar with |ḃ| = ω, so it is admissible.
- Gimbal outward: d = (sin χ, 0, cos χ), with χ := φ + δ sgn φ. The gimbal angle is δ, and d jumps at the single crossing s = 2t₁, which is allowed.
- Choose t₁ ∈ (0,T) with ∫a₁ sin χ = 0. Such a t₁ exists by the IVT, since the integral is < 0 at t₁ → 0 and > 0 at t₁ = T. Then I_h = 0.
- The witness quantities are gain_w = ∫a₁(1 − cos χ), offset p_w = −∫ s a₁ sin χ e_x, and χ_max := max|χ| ≤ τ̄.
- Small-angle limit: t₁ = (1 − 1/√2)T and gain_w ≈ ½a₁T[(3√2−4)/6·Ω² + O(δΩ) + δ²].

**Theorem S.** Assume:
- (S0) τ̄ = δ + ωT < π/2;
- (S1) (ρ₁/m₀) cos χ_max > g₀;
- (S2) κ₀ > A' (automatic if ρ₁ = ρ₂);
- (S3) M := gain_w − B > 0;
- (S4) if a dry-mass constraint m(T) ≥ m_dry is imposed: m₀ − αρ₁T ≥ m_dry (the witness burns at minimum throttle).

Let ζ_w be the vertical data of the witness: v_{0z} = g₀T − I_z(w), h = ½g₀T² − v_{0z}T − J_z(w). Then:
1. The witness lands from ζ_w at (p_w, 0) with v(T) = 0 and satisfies r_z(t) > 0 on [0,T). By rotation invariance, L(ζ_w) ⊇ {|p| = |p_w|}, so L(ζ_w) ≠ ∅.
2. Every p ∈ L(ζ_w), for any admissible trajectory in 3D, satisfies |p| ≥ r_S := (M T³/(12 C_m))^{1/2} > 0. Hence 0 ∉ cl L(ζ_w), and L(ζ_w) is a nonconvex rotation-invariant set. **This is Lemma S.**
3. With a glide slope with apex at r(T), item 1 also holds if tan γ_gs (1+ε_m) a₁₀ sin χ_max ≤ a₁₀ cos χ_max − g₀. Item 2 needs no state constraint.
4. (Theorem D, hard soft landing.) Every state-linear relaxation (math/02 Def 11.1) of the minimum-landing-error problem from ζ_w with target q = 0 has relaxed value 0. The true value is dist(0, L(ζ_w)) ≥ r_S.

*Proof.*
1. *Witness feasibility.* Along the witness, v̇_z = a₁ cos χ − g₀ > 0 by (S1). So v_z increases to v_z(T) = 0, hence v_z < 0 on [0,T), r_z decreases to 0, and r_z > 0 before T.
   For the glide slope: |v_h(t)| ≤ a₁(T) sin χ_max (T−t) and |r_h(t) − p_w| ≤ ½a₁(T) sin χ_max (T−t)², while r_z(t) ≥ ½(a₁₀ cos χ_max − g₀)(T−t)².
   Rotations about e_z preserve ζ_w and map landings at p_w to landings at Rp_w.
2. *Dent.* Let c be any admissible trajectory from ζ_w landing at (p,0). By §1, gain(c) = gain_w and m(F) = (0, −p), so ‖π_m‖² = 12|p|²/T³. Proposition M gives gain_w ≤ B + 12C_m|p|²/T³.
3. *Theorem D.* Apply math/02 Thm D with φ(x) = ‖x_r‖ + ι{x_v = 0}. Since 0 ∈ conv L(ζ_w), the relaxed value is 0. ∎

**Corollary S (qualitative, small angles).** As Ω, δ → 0 with δ/Ω → 0, M/(a₁₀T) = ½[(3√2−4)/6 − 1/(4π²)]Ω² + o(Ω²) = 0.00755 Ω² + o(Ω²) > 0.
Under (S1)–(S2), S therefore holds for all sufficiently short horizons with small gimbal. The δ ≈ Ω range is covered by the explicit table, not by an asymptotic statement.

## 4. Constants (numerics/proof-s/verify_S.py, regime2.py)

High-T/W demonstration vehicle: m₀ = 100 kg, ρ₁ = 1200 N, ρ₂ = 2500 N (a₁₀ = 12, a₂ = 25 m/s²), g₀ = 9.81. α = 0 unless noted.

| case | T (s) | ω (rad/s) | Ω (rad) | gain_w (m/s) | B (m/s) | margin M | dent r_S (m) | witness |p_w| (m) |
|---|---|---|---|---|---|---|---|---|
| δ=0 | 2 | 0.20 | 0.40 | 0.07758 | 0.06370 | 1.39e-2 | **0.45** | 0.94 |
| δ=0 | 4 | 0.10 | 0.40 | 0.15517 | 0.12741 | 2.78e-2 | **1.80** | 3.74 |
| δ=5° | 2 | 0.15 | 0.30 | 0.25050 | 0.23476 | 1.57e-2 | **0.48** | 1.79 |
| δ=10° | 2 | 0.10 | 0.20 | 0.53864 | 0.52809 | 1.06e-2 | **0.39** | 2.59 |
| δ=10° | 4 | 0.05 | 0.20 | 1.07728 | 1.05617 | 2.11e-2 | **1.57** | 10.38 |
| δ=5°, α=5.66e-4 | 2 | 0.15 | 0.30 | 0.25217 | 0.25240 | −2e-4 | fails | — |

Certified Ω-ranges (T = 2 s, this vehicle): δ=0: Ω ∈ (0, 0.55]; δ=5°: (0, 0.45]; δ=10°: (0, 0.30]; δ=15°, 20°: none with these analytic constants.
The α > 0 row fails only because ε_m enters δ_e linearly, which is crude. With α=0 the same geometry certifies.
r_S is a rigorous lower bound on the minimum landing error at target 0 for this instance. Any state-linear relaxation reports 0.

## 5. Sharpness, failure modes, and the S-procedure

- **Where the analytic bound loses.**
  - (i) The δΩ cross-term uses ‖P^⊥β‖₂ (coefficient 1/π = 0.318) where the witness has 2·mean|β|/Ω = 2(3−2√2) = 0.343. That is an 8% margin.
  - (ii) The pointwise majorant c̄(s) ≥ c₀ produces E₄, which is crude: it assumes the maximal tilt τ(s) at every time.
  - At δ = 15° and Ω = 0.3, the main term is already 11% below the witness, but E₄ (3e-3 a₁T) exceeds the remaining margin (1.8e-3 a₁T).
- **S-procedure (Shor) certificate.** `numerics/proof-s/sproc_pure.py` replaces Lemma W and the pointwise budgets by optimal function multipliers ρ(s), σ(s), solved as a discretized SDP. Results: see the appendix line added after the run.
  This bound is valid for ℝ^N-valued (Hilbert-lifted) paths too, so it is the best any quadratic-multiplier argument can give.
- **Adversarial check of Prop. M.** `numerics/proof-s/attack_S.py` maximizes gain − C_m‖π_m‖² over discretized 3D trajectories (free 2D tangential angular velocity, gimbal anywhere in the cone, L-BFGS-B, 12 random starts). It also computes the best exact-Pvr gain. Results: appendix.

## 6. Long horizons and GTPL

**Remark 6.1 (dents live only at throttle-saturated data; heuristic, not a claim).**
- Suppose a trajectory from ζ lands at p ≠ 0 and has interior throttle (ρ₁ < T < ρ₂) on two windows, plus a window where b is within δ of its required lateral force direction.
- Then gimbal-only lateral corrections can move p continuously toward 0, and the two throttle windows compensate the two vertical constraints (I_z, J_z).
- Hence any ζ with 0 ∉ cl L(ζ) must be throttle-saturated: it lies on the boundary of the Pv-feasible vertical-data set K₁, i.e. on a face max ∫(α+βs) a d_z. Since the vertical data are 2D, the faces are max ∫(α+βs) a d_z. The sign patterns of w = α+βs are:
  - w < 0 throughout: pure waste;
  - w < 0 early, > 0 late: dive-then-brake;
  - w > 0 early, < 0 late: brake-then-dive. This ends at minimum throttle, so it is above ground only for min-T/W > 1 vehicles (correction by [adversary]);
  - w > 0 throughout: upright, lands at 0, degenerate.
- For GTPL (ρ₁ < m g), descent data that start in the air leave only dive-then-brake. [adversary] s4 reports that the altitude-constrained pure-waste face ends at *hop* data (starting on the ground with upward velocity), where gaps are large (0.65 at t_f = 4 s, 2.94 at t_f = 8 s, weighted m/s). That is relevant if lift-off-to-landing guidance is in scope. Not covered by Theorem S.

**Remark 6.2 (when coning fills the dent; after [adversary] math/01 §7).**
- With a tilt cap θ_c, suppose a face maximizer has a plateau at tilt θ_c of length ≳ 2π sin θ_c/ω (one precession period) with outward gimbal.
- The waste depends only on tilt, so the azimuth can be modulated (|ψ̇| ≤ ω/sin θ_c) to cancel both the lateral impulse and the lateral moment of the ramp at zero cost. Then Pv = Pvr at that face.
- Short-dive faces (ωs* < θ_c) never reach the cap. So this mechanism does **not** refute S at long horizons.
- Numerical confirmation ([adversary] s3, exact 3D, 30° cap, pure-dive face, gap opt(Pvr) − opt(Pv) in m/s): t_f = 8 s: 0.69 (planar-only 0.70); 12 s: 0.50 (0.80); 20 s: 0.106 (0.82).
- At 20 s the Pvr optimizer rides the cap and sweeps 359° of azimuth. **So coning fills ~87% of the dent at long capped horizons, but not all of it** in the exact model.

**Answer to task (3).**
- No evidence that S fails at long horizons.
- At capped faces with long plateaus, coning shrinks the dent strongly (87% at t_f = 20 s), but a strict residual remains numerically.
- Short-dive faces are unaffected.
- Our rigorous certificate is limited to short horizons by the quadratic majorant, not by the physics.

**Task (2), GTPL.** No instance in the proven regime. Numerical S at dive-then-brake faces with Pv offsets ~1.5–2.4 m, but an ℓ-gap of ~1 cm.
- At the exact face data, the dent radius equals the Pv-optimal offset (macroscopic). An ℓ-perturbation of the data of size ~1e-2 m closes it.
- So the GTPL min-landing-error relaxation error is large but non-robust: a sliver of instances.
- Rigorous proof for GTPL would need the brake-phase impulse-cancellation cost to be bounded to within the ℓ-gap. The L²/Wirtinger slack is cm–dm. Open.

## 7. Claims registered (CLAIMS.md)
- S-W: Lemma W.
- S-M: Prop. M.
- S-T: Theorem S + table.
- S-GTPL: no GTPL instance in the regime; GTPL S numerical only.
- S-LH: Remarks 6.1–6.2, heuristic.

## Appendix: run log
(filled below)
- `sim_witness.py` independently forward-integrates the witness (RK45, rtol 1e-11) from vertical data with v0_lat = r0_lat = 0.
  - δ=0, T=2, ω=0.2 (demo vehicle): ζ_w = (h, v_{0z}) = (4.280 m, −4.302 m/s). It lands at p_w = (0.9356, 0) m with v(T) = 0 and min r_z = 0 (attained only at T).
  - δ=10°, T=2, ω=0.1: ζ_w = (3.794 m, −3.841 m/s), p_w = 2.595 m.
  - GTPL parameters (models.gtpl): ρ1/m0 = 5.0 < g0, so (S1) fails.
- Fixed-thrust variant (ρ1 = ρ2 = 1200 N, m0 = 100 kg, δ = 0; the cheapest Lean target, C_m = A'): T=2, ω=0.2 gives M = 1.39e-2 and r_S ≥ 0.471 m; T=4, ω=0.1 gives r_S ≥ 1.885 m.
- **S-procedure (Shor) SDP**, `sproc_pure.py`. Discretized, so it is a numerical certificate only, not rigorous. Demo vehicle, δ=0, T=2, Ω=0.4:
  - bound on the Pvr gain = 0.02774 (N=30) / 0.02803 (N=50);
  - analytic B = 0.06370;
  - witness = 0.07758.
  So optimal time-varying multipliers cut the analytic bound by ~2.3×. The true margin is ~64% of the witness gain; the certified margin is 18%.
  The analytic regime is conservative. (The discretized SDP restricts β to piecewise-linear paths, so it is not an upper bound for continuous paths. Its value 0.0146Ω² should not be compared literally with the ≈-feasible coning entry 0.0162Ω² of math/01 §7.)
- **Adversarial NLP** (`attack_S.py`, δ=0, T=2, Ω=0.4, demo vehicle, 3D, 4 starts, N=16): sup found of gain − C_m‖π_m‖² = 0.0338 ≤ B = 0.0637 ✓. Best exactly-Pvr gain found = 0.0254, against witness 0.0776.
  [adversary] a8 (small angle, 24 starts incl. coning): max Pvr = 0.0147Ω² ≤ 0.0253Ω² (Wirtinger), max Pv = 0.0412Ω² ≥ 0.0404Ω² (witness). The bound holds and is ~1.7× loose.
- [adversary] reviewed §2–§3 (Lemma W, P2, K-elimination, same-gain claim, π-norm). **No flaw found: SURVIVES** (math/01 §9; a7_check_S.py reproduces table row 1).
- **S-procedure at δ = 15°** (GTPL gimbal; demo vehicle, T=2, Ω=0.3, N=30): Shor bound = 1.1106 against witness gain 1.2062. Margin 0.096, i.e. 8%.
  So the δ=15° case, which the analytic constants cannot certify, has a positive numerical (discretized) certificate.
  Turning it into a rigorous one needs a continuous-time multiplier certificate (open; the next step suggested for this lemma).
- **Adversarial NLP at δ = 10°** (T=2, Ω=0.2): sup found 0.4496 ≤ B = 0.5281 ✓. Best exactly-Pvr gain found = 0.4402, against witness 0.5386.

---

## 8. Hop instance (pad-launched data, GTPL constants). [proof-s] 2026-11-07 00:37. Verdict: NOT proved. The method's limit is identified quantitatively.

**Task (orchestrator).** M1 with GTPL constants: m₀=80, ρ = 400/1000 N, α = 5.665e-4, δ = 15°, ω = 0.4, t_f = 4 s, r_z ≥ 0.
Hop data: r₀ = 0 (on the pad), v₀ = (0,0,v_{0z}). [numerics] s5 reports L as an annulus with hole 0.55 → 4.99 m for v_{0z} ∈ (7.727, 7.917]. The task is to prove 0 ∉ cl L ≠ ∅ with a certified hole radius.

**8.1 Exact reduction (rigorous).**
- For hop data every landing trajectory has I = (0,0, g₀T − v_{0z}) and M_z := ∫ s a d_z = ½g₀T². The second value is *independent of v_{0z}*, because h = 0.
- So for every s* the functional ℓ_{s*} := ∫(s−s*) a d_z = ½g₀T² − s*(g₀T − v_{0z}) is fixed by the data.
- The hop family is therefore a dive-then-brake face family. The "dive" is the min-throttle coast-up phase, so altitude is never active early, and s* ≈ 2.4 s is long.
- Slice S at hop data ⇔ v_{0z}^{Pvr} < v_{0z}^{Pv}, where v_{0z}^{Pv(r)} := sup v_{0z} over trajectories with I_h = 0 (and ∫sF = 0).

**8.2 Rigorous partial results.**
- **Upright limit.** The upright bang-bang throttle (min, then max; switch fixed by M_z = ½g₀T²) lands at the pad up to v_{0z} = 7.2045 m/s (α=0) / 7.2833 m/s (α>0). Script: `numerics/proof-s/hop_upright.py`.
- **Explicit offset witnesses** (`numerics/proof-s/hop_witness.py`; planar, inner ZOH discretization with N=40; exact mass; φ linear per cell, so the rate and gimbal constraints hold on whole cells, up to 1e-11 float slack; r_z ≥ 0.013 m at the nodes):
  - α=0: v_{0z} = 7.7116 m/s, landing offset 6.58 m;
  - α>0 (GTPL): v_{0z} = 7.7425 m/s, landing offset 4.61 m.
  - So L(v_{0z}) ≠ ∅ up to at least these values. [numerics]' 3D Pv value 7.917 is higher; my planar SLSQP witness is not optimal.
- Together with [numerics]' Pvr = 7.727 (a local NLP value, not certified), this already gives a *numerically* nonconvex instance at v_{0z} ∈ (7.727, 7.742] using my witness.

**8.3 Why Theorem S's machinery does not certify the hole (quantitative).**
I adapted §2 to the hop face:
- dive majorant (Lemma P1) on [0,s*] with weight |w|;
- brake majorant w a d_z ≤ w a₂ − w a₂|u|²/2 − w|K_b|²/(2(a₂−a₁)), with u = d_h = b_h + e and K_b = (a₂−a)u;
- brake attitude coupled to the dive through the Lipschitz b_h;
- both lateral moment constraints.

I then solved the best quadratic-multiplier (Shor / S-procedure) certificate, `numerics/proof-s/hop_sdp.py` (α = 0, N = 30). Results (bound on v_{0z} for landing AT the pad, against the α=0 witness 7.7116):

| s* (s) | Pvr bound | Pv bound | witness |
|---|---|---|---|
| 2.2 | 8.154 | 8.342 | 7.712 |
| 2.4 | 7.879 | 8.293 | 7.712 |
| 2.5 | 8.010 | 8.464 | 7.712 |

(A first version with a weaker brake majorant gave 7.94 at s* = 2.4.)
**The Pvr bound exceeds the witness by ≥ 0.17 m/s, so no certificate of this family closes the hole.** Even the Pv bound overshoots the witness by 0.6 m/s.

Reasons:
- (i) Tilts reach ~1 rad, where the quadratic majorants of 1 − cos are loose (c̄ ≈ 0.75 instead of 0.5).
- (ii) A rotation-invariant quadratic certificate is automatically valid for ℝ^N-valued lateral paths ("Hilbert coning"). The true margin is thin: Pv − Pvr ≈ 0.19 m/s out of a tilt benefit of ≈ 0.63 m/s. So it may be destroyed by the lift itself, not only by the majorants.
- The pure-waste case of §3 worked because its true margin was large (Pvr ≈ 36% of Pv's tilt gain), whereas at hop data Pvr reaches ≈ 70%.

**8.4 What a proof would need (open).** Any proof must exploit that the lateral plane is 2-dimensional, which rules out any purely quadratic/Shor-type argument at these margins. Candidate routes:
- (a) A characterization (rigidity) of Pv maximizers at the hop face, showing they all land offset. Qualitative S then follows by compactness, as in math/02 Thm B*-env. PMP extremal analysis with an affine lateral primer is needed.
- (b) A computer-assisted global bound over 2D-lateral paths, e.g. branch-and-bound on a coarse attitude discretization with validated error terms.
- (c) A non-quadratic exact pointwise inequality, a ball-bound with trajectory-dependent directions c = b(τ) (math/02 Lemma 5.1), combined with the two moment constraints.

None was completed here. **Status of the hop instance: numerical (strong: two independent solvers, [numerics] s5 and my witness), not proved.**

**8.5 Torque-coupled TVC.** Not attempted: the M1 hop case is not certified, and the TVC model only adds coupling. [proof-tvc] informed.
