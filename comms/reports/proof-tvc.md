# Report: [proof-tvc] — pure-TVC (GTPL actuation) nonconvexity, upright at rest

Brief: comms/briefs/proof-tvc.md. Write-up: math/06-pure-tvc.md. Numerics: numerics/proof-tvc/. Lean list: math/03-lean-blueprint.md §"Pure TVC".

## Verdict
VERDICT_PLACEHOLDER

## Method (what is new)
- **No planarity, rigidity or maximizer characterization.** In flat coordinates y = r + εb, the face functional ℓ = r0z + s* v0z (B*-type, dive then brake) becomes W_z = ∫(s−s*) f b_z. Every competitor with zero lateral data (r0h = v0h = 0, as at the rotation midpoint θ_m) is bounded as follows:
  1. Exact pointwise inequalities give a quadratic form Q(h) in the horizontal tilt h = b_h, plus linear throttle penalties.
  2. The torque bound |ḧ| ≤ K enters through an S-procedure multiplier λ(s), and the two lateral moments through a Finsler multiplier ρ.
  3. **Separability.** Q is a sum over the two components of h, so the vector bound equals the scalar bound. This disposes of coning, loops and two-lobe paths (adversary attack (1)) at no cost.
  4. One 2N×2N SDP certificate covers the problem. Its continuous validity comes from a piecewise-linear cell basis with explicit O(h_c²) cell-local remainders (Wirtinger).
  5. A localization lemma (energy plus Agmon) shrinks the a-priori speed and tilt bounds for any competitor with nonnegative gain. This fixes the adversary's fatal attack A1, where the additive remainder exceeded the gain.
- **Witness.** An explicit planar dive-then-brake: ρ1 with full gimbal (bang-bang) early, ρ2 late, returning upright at rest. Its gain is computed exactly. It satisfies r_z > 0 (v_z < 0 throughout) and a glide slope with tan γ up to about 100.

## Adversary interaction ([adversary-6dof])
| Attack | Status |
|---|---|
| A1: additive remainder R = 3e-4 > G_w (certificate v1) | FIXED: homogeneous remainders, node-wise ϑ(s), and Lemma 4.0 localization |
| (a) late inequality a2 − p b_z ≥ (…)/(2a2) | checked TRUE by adversary |
| (b) Δp / κ_D absorption | checked OK (constant mass) |
| (c) cell splitting remainder | checked OK. v2 uses the sharper piecewise-linear version |
| A2: mass depletion α > 0 | OPEN. The theorem is for the constant-mass class (§5.5) |
| A3: roll-rate competitors | terms implemented (certificate2.py, ROLL=1). See verdict for certification status |
| Gimbal-rate limit 100°/s | OPEN. The unlimited-class baseline J0 uses instantaneous full deflection, which a centred rate-limited gimbal cannot match (witness gain −4.8e-3 against J0). A class-specific certificate is needed |

## What remains open
OPEN_PLACEHOLDER
