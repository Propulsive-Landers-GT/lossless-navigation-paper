# Report: redteam-lift (lifting and relaxation routes to 5DOF LCvx)

Details: math/redteam-lift.md. Code: numerics/redteam-lift/. CLAIMS rows: OM, L-R1, L-ML, L-Aopt, L-P1, L-ftf, L-SD2.

**Core mechanism (Mixing lemma).** Suppose a convex formulation enters the data θ affinely and contains the
genuine trajectories. Then it contains every mixture (Σλθ_i, ΣλΦ(τ_i)). It cannot tell instance θ from a
mixture of instances with mean θ. Every route is either lossy for this reason, or escapes it by entering θ
nonaffinely (Dirac or Veronese moments). In the latter case Claim A does not apply.

| Route | Convex? | Exact in what sense | vs Claim A |
|---|---|---|---|
| 1 Relaxed controls (Gamkrelidze, Young, Filippov–Ważewski) | No: dynamics stay nonlinear in b | Reachable set = closure of original (F–W hypotheses hold when b is a state). Equality when α=0 (Lyapunov conditional on b). Thm B survives relaxation ⇒ dist(θ_M,F)>0 | Consistent. Rate limit ⇒ b cannot chatter (Arzelà–Ascoli). Joint (b,d) mixtures are convex but lossy |
| 2 Occupation measures / moment–SOS | Yes (LP over measures) | **Dirac entry δ_θ: exact in feasibility and value** (α=0; α>0 up to closure). Affine entry: feasible set = conv F, value = V** | Consistent: δ_θ is nonaffine. **BREAK of the informal statement**: lossless convex formulations exist once data enter nonaffinely |
| 3 SDP lifts (Shor bbᵀ, conv SO(3) orbitope, quaternions) | Yes | Uniform lifts: rank-2 spurious point at θ_M, so no rank-1 guarantee is possible. **Degree-2 min-landing-error lift C-SD2** = the problem on a Hilbert sphere. It excludes θ_M exactly (Prop S1). In its well-posed form it is **numerically exact on every fixed-thrust instance tested** (~45 targets, 3 configs, ≤1e-6 relative). Earlier "gaps" were Slater-failure solver artifacts and are retracted | Uniform: consistent. C-SD2: outside A and D (data only in the objective; variance cost). **Candidate tractable exact convex program (Conjecture CSD2)** |
| 4 Changes of variables / time dilation / θ-reparametrization | n/a | Trajectory-side changes are irrelevant (A quantifies over all Y). Separable monotone θ-maps (like ln m) cannot convexify F (Prop P1). Arbitrary homeomorphisms or δ_θ can convexify anything | The theorem must fix the class: affine or separable monotone. Free tf: θ_M ∈ F_{tf+Δt} if g0 > a1cosδ (GTPL), so free-tf needs a window (proof's P-tf) |
| 5 Cuts / conv(trajectories) / optimization-only losslessness | Yes | Cuts can never remove mixtures. Min over the slice of conv = V**. **Thm A-opt**: value-exact on F ⇒ V = V** on F. **Prop T**: the cost ∫b·e_z violates this, so no uniform relaxation is lossless for all convex costs even on F. Min-fuel: open (numerically no violation: throttle never enters the dent) | Claim A's notion is the right one. The standard LCvx definition plus attainment implies it. The weaker notion still fails in general and gives no infeasibility certificate |

**Recommended theorem (5DOF M1, fixed tf, Thm B regime).** No convex C ⊆ Θ×Y with θ entering affinely (or by
a separable monotone map) is lossless in feasibility. None is lossless in value on F for all convex costs.
Sharpness: with Dirac data entry, an infinite-dimensional lossless LP exists. For fixed-thrust
min-landing-error, its degree-2 truncation (C-SD2, a small SDP of size ~2N+3) appears to be exact already.
That would be a genuine "possible" outside the affine/state-linear class. Practical use: q_SDP is a rigorous
lower bound; q_SDP>0 certifies infeasibility; a projected+polished trajectory that reaches q_SDP certifies
the global optimum.
Open: a proof of CSD2 (planarization Π_n=Π_3), variable throttle (U=a·d is not degree-2), glide slope,
min-fuel value-exactness on F, α>0 relaxation gap at boundary points. Lean-ready A-opt / Prop T: math §7.
