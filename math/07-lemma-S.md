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

**GTPL (task 2): no instance in the proven regime.** ρ₁/m₀ = 5.0 m/s² (wet) to 7.2 m/s² (dry), always < g₀ = 9.81.
- So the pure-waste face starts underground (same mechanism as [adversary]'s BREAK of Thm B).
- For GTPL, S must use dive-then-brake faces. [numerics] s1_slice (exact 3D, coning starts, r_z ≥ 0, 24 restarts) finds strict gaps opt(Pvr) − opt(Pv) = 0.0156 m (t_f=4 s) and 0.0088 m (t_f=8 s), with Pv optimizers landing 1.47 m / 2.39 m off-axis. So S holds numerically for GTPL, with the gap thin in the vertical functional ℓ.
- Rigorous GTPL proof: **open**. The L²/Wirtinger slack (cm–dm in ℓ) exceeds the ℓ-gap (mm–cm), see §5.

**Long horizons (task 3): S does not fail; coning fills the dent only on capped plateau faces.**
- Our certificate is short-horizon: the quadratic majorant degrades with tilt.
- Numerically, strict gaps persist at ωt_f = 1.6 and 3.2 rad ([numerics] s1, dive faces, cap none/30°).
- Coning can close the gap only at faces where the maximizer has a long tilt-capped plateau (Remark 6.2, after [adversary] math/01 §7). Short-dive faces never reach the cap.
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
- (S3) M := gain_w − B > 0.

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
- Hence any ζ with 0 ∉ cl L(ζ) must be throttle-saturated: it lies on the boundary of the Pv-feasible vertical-data set K₁, i.e. on a face max ∫(α+βs) a d_z. Since the vertical data are 2D, the faces are exactly the pure-waste (β=0) and dive-then-brake (α<0<β) families.
- For GTPL (ρ₁ < m g) the pure-waste face is underground, leaving only dive-then-brake.

**Remark 6.2 (when coning fills the dent; after [adversary] math/01 §7).**
- With a tilt cap θ_c, suppose a face maximizer has a plateau at tilt θ_c of length ≳ 2π sin θ_c/ω (one precession period) with outward gimbal.
- The waste depends only on tilt, so the azimuth can be modulated (|ψ̇| ≤ ω/sin θ_c) to cancel both the lateral impulse and the lateral moment of the ramp at zero cost. Then Pv = Pvr at that face.
- Short-dive faces (ωs* < θ_c) never reach the cap. So this mechanism does **not** refute S at long horizons.
- [numerics] s1 at t_f = 8 s (cap 30°, plateau shorter than one period) still shows strict gaps.

**Answer to task (3).**
- No evidence that S fails at long horizons.
- The dent closes only at capped faces with long plateaus.
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
