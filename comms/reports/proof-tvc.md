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

RATELIM_TABLE

So the realistic rate-limited, mass-depleting GTPL landing set is **nonconvex but unproved**, not "possibly convex on these faces". The free maximizers have nonzero lateral data. The NLPs are discretized, local and started from 2–3 initial guesses, so the gaps are evidence, not certificates. They are 100–300× larger than the certified tf = 1 gap.

**Open.**
1. Long horizons. Rigorous runs fail at tf = 2–3 s because of the moment-shift term and dense-SDP size. Recommended route: a state-space Riccati/dissipation certificate plus the h(s*)-based moment lemma (math/06 §6).
2. Gimbal-rate limit. Needs a jerk multiplier and the vertical baseline (math/06 §5.3).
3. Mass depletion.
4. Free final time.
5. A tumbling-exclusion lemma for uncapped tf > 2.3 s.
