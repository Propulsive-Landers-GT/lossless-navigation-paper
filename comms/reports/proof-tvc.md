# Report: [proof-tvc] — pure-TVC (GTPL actuation) nonconvexity, upright at rest

Brief: comms/briefs/proof-tvc.md. Write-up: math/06-pure-tvc.md. Numerics: numerics/proof-tvc/. Lean list: math/03-lean-blueprint.md §"Pure TVC".

## Verdict
**NONCONVEX: proved, computer-assisted, for the real GTPL actuation at one horizon.** The model is pure TVC: the gimbal is the only pitch/yaw torque. Landing is upright at rest at both ends, with r_z ≥ 0 and a glide slope. Mass is constant and ε = J_t/(mL) is constant. GTPL wet constants, tf = 1 s, s* = 0.25 s: F^X_tf is not convex, so no uniform state-linear lossless convexification exists at that horizon.

| case | G_w (m) | U_tot (m) | margin | dist(θ_m, F) ≥ |
|---|---|---|---|---|
| cone 15°, roll held (ω3≡0), N=120 | 7.2691e-5 | 6.2736e-5 | 13.7% | 9.6e-6 m |
| Cardan box ±15° (δ*=21.09°), roll held, N=60 | 1.4043e-4 | 1.3286e-4 | 5.4% | 7.3e-6 m |
| cone, competitors may use the roll RCS (ω3 free), N=120 | 7.2691e-5 | 6.9798e-5 | 4.0% | 2.8e-6 m |

Status: **CONFIRMED**. [adversary-6dof] verdict SURVIVES. [verify-tvc] CERTIFIED in exact rational/interval arithmetic (math/verify-tvc-report.md; exact integer Sylvester minors) after repairs W1, W2, W3, all applied:
- W1: the witness is now an ordinary bang-bang control (found independently by [adversary-6dof]); the old witness assumed chattering on partial-torque cells.
- W2: exact upper weight for the free-roll gyro term.
- W3: endpoint sups in the remainders.

Certified margins in dist(θ_m, F): 9.96e-6 m (cone), 7.57e-6 m (box), 2.90e-6 m (free roll). `verify_cert.py` is a float re-check only. The gap is genuinely thin, about 1e-5 m, consistent with B* (math/02 Rem. 10.2).

## Method (what is new)
- **No planarity, rigidity or maximizer characterization.** In flat coordinates y = r + εb, the face functional ℓ = r0z + s* v0z (B*-type, dive then brake) becomes W_z = ∫(s−s*) f b_z. Every competitor with zero lateral data (r0h = v0h = 0, as at the rotation midpoint θ_m) is bounded as follows:
  1. Exact pointwise inequalities give a quadratic form Q(h) in the horizontal tilt h = b_h, plus linear throttle penalties.
  2. The torque bound |ḧ| ≤ K enters through an S-procedure multiplier λ(s), and the two lateral moments through a Finsler multiplier ρ.
  3. **Separability.** Q is a sum over the two components of h, so the vector bound equals the scalar bound. This disposes of coning, loops and two-lobe paths (adversary attack (1)) at no cost.
  4. One 2N×2N SDP certificate covers the problem. Its continuous validity comes from a piecewise-linear cell basis with explicit O(h_c²) cell-local remainders (Wirtinger).
  5. A localization lemma (energy plus Agmon) shrinks the a-priori speed and tilt bounds for any competitor with nonnegative gain. This fixes the adversary's fatal attack A1, where the additive remainder exceeded the gain.
- **Moments.** The Finsler multiplier on the unweighted moment v0h is capped (ρ0 ≈ 1–1.5): throttle modulation near s* is first-order free and can shift that moment. This is genuine competitor freedom, bounded by a bathtub lemma. The weighted moment Λ_h = r0h + s* v0h has a penalty-linear shift, so ρ_w ≫ 1 is allowed. A single ρ on (r0h, v0h) was the reason earlier runs failed.
- **Witness.** An explicit planar dive-then-brake: ρ1 with full gimbal (bang-bang) early, ρ2 late, returning upright at rest. Its gain is computed exactly. It satisfies r_z > 0 (v_z < 0 throughout) and a glide slope with tan γ up to about 100.

## Adversary interaction ([adversary-6dof])
| Attack | Status |
|---|---|
| A1: additive remainder R = 3e-4 > G_w (certificate v1) | FIXED: homogeneous remainders, node-wise ϑ(s), and Lemma 4.0 localization |
| (a) late inequality a2 − p b_z ≥ (…)/(2a2) | checked TRUE by adversary |
| (b) Δp / κ_D absorption | checked OK (constant mass) |
| (c) cell splitting remainder | checked OK. v2 uses the sharper piecewise-linear version |
| A2: mass depletion α > 0 | OPEN. The theorem is for the constant-mass class (§5.5) |
| A3: roll-rate competitors | FIXED, certified at N=120 (margin 4%) |
| Gimbal-rate limit 100°/s | OPEN. The unlimited-class baseline J0 uses instantaneous full deflection, which a centred rate-limited gimbal cannot match (witness gain −4.8e-3 against J0). A class-specific certificate is needed |

## What remains open
1. **Mass depletion α>0 / varying ε(m)** (GTPL α=5.66e-4). The late baseline moves by ~4e-3 m, far more than the gap. A certificate for the α>0 class has to carry the competitor's own mass history in the penalty. TVC-1 holds for the constant-mass class, the standard LCvx idealization but not literally GTPL.
2. **Gimbal-rate limit (100°/s, centred).** Even against the rate-limited baseline, the best witness gain is negative (−1.5e-3 at tf=1): without chattering, deflection costs torque. The certificate must use the rate limit itself, via a jerk multiplier |h'''| ≤ aγ̇/ε (math/06 §5.3). Not implemented.
3. **Realistic horizons.** What is done:
   - (A2) dropped via Π ≥ b_z|a2−f|.
   - Bootstrap localization; any tilt cap < 90° behaves like 30°.
   - The ideal zero-lateral ratio stays at 0.70 at tf=3.
   
   But the rigorous runs at tf=2 (uncapped) and tf=3 (capped) FAIL, for two reasons:
   - (i) The moment-shift term: the localized tilt at s* is about 6× the witness tilt, so ρ0 must stay near 0.05.
   - (ii) The discretization floor needs N ≳ 150, where dense interior-point solvers are too big and SCS too inaccurate.
   
   Next: localization relative to G_w with a time-sliced Agmon bound near s*, and a banded SDP or higher-degree cell basis. Uncapped tf > 2.3 s also needs a tumbling-exclusion lemma for (A1). [adversary-6dof]'s numerics show gaps of 2.8e-2/3.3e-2 m at tf=5/7.
4. **Free final time.** Reduced to a condition on a continuum of horizons via RR-LS (math/06 §5.4); not certified.
5. **Formal verification of the SDP certificate** (rational LDLᵀ or interval arithmetic). The rest is Lean-ready (math/03 §Pure TVC).
6. **A non-thin altitude-feasible face** (practical ε-impossibility). Still none known.

## Final state (2026-11-07, ~05:30)
**Certified (exact arithmetic; [verify-tvc] audit; [adversary-6dof] SURVIVES).** GTPL wet constants, tf = 1 s, s* = 0.25 s, constant mass, unlimited gimbal rate, upright at rest, r_z ≥ 0 + glide slope:
- cone, roll held: margin 9.96e-6 m;
- Cardan box, roll held: margin 7.57e-6 m;
- cone, roll free: margin 2.90e-6 m.

In each case F^X_tf is NONCONVEX, so no uniform state-linear lossless convexification exists for that class at that horizon.

**Numerical only.** These use [adversary-6dof]'s full 6DOF model `m3tvc.py`: quaternion attitude, Euler equations, Cardan box gimbal rate-limited to 100°/s from centred, mass depletion, roll free, r_z ≥ 0 at every node, upright at rest. On the dive-then-brake face, the max of ℓ over zero-lateral data is below the free max:

| gimbal (100°/s, centred) | tf (s) | s* (s) | free max ℓ (m) | zero-lateral max ℓ (m) | gap (m) | robustness | source |
|---|---|---|---|---|---|---|---|
| Cardan box | 3 | 0.75 | 8.66714 | 8.65451 | 1.26e-2 | zero-lateral starts agree to 2e-5 | proof-tvc run of `exp3.py` |
| cone | 3 | 0.5 | 9.60118 | 9.59859 | 2.6e-3 | **weak**: zero-lateral starts spread 4e-3, free starts spread 4.5e-3 | proof-tvc run |
| Cardan box | 5 | 0.5 | 31.01143 | 31.00658 | 4.8e-3 | one zero-lateral optimum + continuation | proof-tvc run |
| Cardan box | 5 | 1.0 | 26.44276 | 26.41461 | 2.8e-2 | < 1e-5 | [adversary-6dof] |
| Cardan box | 7 | 1.0 | 58.63996 | 58.60733 | 3.3e-2 | 6e-4 | [adversary-6dof] |

So the realistic rate-limited, mass-depleting GTPL landing set is **nonconvex but unproved**, not "possibly convex on these faces". The free maximizers have nonzero lateral data. The NLPs are discretized, local and started from 2–3 initial guesses, so the gaps are evidence, not certificates. They are 100–300× larger than the certified tf = 1 gap.

**Open.**
1. Long horizons. Rigorous runs fail at tf = 2–3 s because of the moment-shift term and dense-SDP size. Recommended route: a state-space Riccati/dissipation certificate plus the h(s*)-based moment lemma (math/06 §6).
2. Gimbal-rate limit. Needs a jerk multiplier and the vertical baseline (math/06 §5.3).
3. Mass depletion.
4. Free final time.
5. A tumbling-exclusion lemma for uncapped tf > 2.3 s.

## Update (2026-11-07 ~03:05): TVC-2, tf = 2 s with NO tilt cap, CONFIRMED
- **Result.** GTPL wet, constant mass, roll held, 15° cone, unlimited gimbal rate, upright at rest, r_z ≥ 0 + glide slope (tan γ ≤ 37), tf = 2 s, s* = 0.5 s.
  - F^X is nonconvex, with margin 8.06% and dist(θ_m, F) ≥ 9.23e-5 m.
  - [verify-tvc] re-certified it in exact arithmetic (math/verify-tvc-report.md §9).
  - [adversary-6dof] verdict: SURVIVES.
- **New method: a state-space (Riccati/DP) certificate.** The quadratic-form inequality is checked by a backward recursion over the state (x, x', m0, mw) with cellwise-linear controls.
  - It is O(N), with N = 600 fine cells, so the discretization floors are negligible.
  - It is re-run in Arb balls.
  - The multiplier comes from a coarse SDP, used only as a generator.
  - It is combined with: (A2) dropped, bootstrap localization, and (ρ0, ρw) = (0.1, 45) with ζ = ξ = 0.15.
  - Files: numerics/proof-tvc/riccati_cert.py and verify_riccati.py.
- **TVC-3: tf = 3 s, tilt-capped class (cap 80° or 30°), r_z ≥ 0, no glide-slope claim.** CLAIMED, re-audit requested.
  - Result: U = 1.30211e-3 < G_w = 1.35849e-3, margin 4.15%, dist ≥ 4.78e-5 m.
  - Trick: the coarse dense SDP fails numerically at tf=3, so the certified TVC-2 multiplier is reused, extended by zero on (2,3]. M_late dominates there.

## Update (2026-11-07 ~03:30): long horizons certified (state-space Riccati certificate)
All results below assume constant mass, roll held, 15° cone, unlimited gimbal rate, upright at rest and r_z ≥ 0. All are CONFIRMED in exact arithmetic by [verify-tvc] (math/verify-tvc-report.md §9–11).

| ID | tf (s) | class | margin | dist(θ_m, F) ≥ | glide ratio (6DOF sim) |
|---|---|---|---|---|---|
| TVC-1 | 1 | uncapped (cone, box, roll-free) | 13.7 / 5.4 / 4.0 % | 9.96e-6 / 7.57e-6 / 2.90e-6 m | 116 |
| TVC-2 | 2 | **uncapped** | 8.06 % | 9.23e-5 m | 37.8 |
| TVC-3 | 3 | tilt cap 80° or 30° | 4.16 % | 4.79e-5 m | 87.8 |
| TVC-5 | 5 | tilt cap 80° or 30° | 0.20 % | 2.48e-6 m | 299 |

**Method.** The proof chain is that of math/06 §4, with three changes:
- (A2) is dropped;
- localization is bootstrapped;
- the matrix inequality is checked by a backward Riccati/DP recursion over the state (x, x', m0, mw), so the cost is O(N) (up to 1500 cells, h = 1/300) and the discretization floors are negligible.

The multipliers come from a coarse SDP at tf = 2. At tf = 3 and 5 they are reused, extended by zero and block-reduced. These generators are not part of the proof; every final multiplier is checked by the Arb recursion. Code: numerics/proof-tvc/riccati_cert.py and verify_riccati.py.

**Still open.**
- tf ≥ 6 s. tf = 7 was attempted: the certificate fails by 4.8% with the best generator (the tf=5 multiplier), although the Arb recursion passes for every multiplier tried. Kelley cutting planes did not converge. A bundle/trust-region multiplier optimizer on the recursion is the next step.
- Uncapped tf > 2.3 s, which needs a tumbling-exclusion lemma for (A1).
- Mass depletion.
- 100°/s gimbal-rate limit (needs a jerk multiplier).
- Roll-free and box variants beyond tf = 1.
- Free final time.
