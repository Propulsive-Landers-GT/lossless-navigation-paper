# Report: [proof-tvc] — pure-TVC (GTPL actuation) nonconvexity, upright at rest

Brief: comms/briefs/proof-tvc.md. Write-up: math/06-pure-tvc.md. Numerics: numerics/proof-tvc/. Lean list: math/03-lean-blueprint.md §"Pure TVC".

## Verdict
**NONCONVEX: proved, computer-assisted, for the real GTPL actuation at one horizon.** The model is pure TVC: the gimbal is the only pitch/yaw torque. Landing is upright at rest at both ends, with r_z ≥ 0 and a glide slope. Mass is constant and ε = J_t/(mL) is constant. GTPL wet constants, tf = 1 s, s* = 0.25 s: F^X_tf is not convex, so no uniform state-linear lossless convexification exists at that horizon.

| case | G_w (m) | U_tot (m) | margin | dist(θ_m, F) ≥ |
|---|---|---|---|---|
| cone 15°, roll held (ω3≡0), N=120 | 7.269e-5 | 6.274e-5 | 13.7% | 9.6e-6 m |
| Cardan box ±15° (δ*=21.09°), roll held, N=60 | 1.404e-4 | 1.329e-4 | 5.4% | 7.3e-6 m |
| cone, competitors may use the roll RCS (ω3 free), N=120 | 7.269e-5 | 6.980e-5 | 4.0% | 2.8e-6 m |

Each certificate was re-verified in a fresh process with no solver (eigenvalue and Cholesky checks, U recomputed): `numerics/proof-tvc/verify_cert.py`. The gap is genuinely thin, about 1e-5 m, consistent with B* (math/02 Rem. 10.2).

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
2. **Gimbal-rate limit (100°/s, centred).** Needs a class-specific baseline and certificate.
3. **Realistic horizons (5–8 s).** The crude a-priori (A1)/(A2) fail for tf ≳ 1.5 s, and the SDP size grows with tf. [adversary-6dof]'s numerics show clear gaps of 2.8e-2 m (tf=5) and 3.3e-2 m (tf=7), about 100× the tf=1 gap, so certification there should be easier once (A1)/(A2) are replaced by a bootstrapped localization.
4. **Free final time.** Reduced to a condition on a continuum of horizons via RR-LS (math/06 §5.4); not certified.
5. **Formal verification of the SDP certificate** (rational LDLᵀ or interval arithmetic). The rest is Lean-ready (math/03 §Pure TVC).
6. **A non-thin altitude-feasible face** (practical ε-impossibility). Still none known.
