# Claims registry

| ID | Claim (short) | Owner | Where | Status | Attacks / notes |
|---|---|---|---|---|---|
| A | Lossless uniform convex relaxation ⇒ feasible boundary-data set F convex (projection of convex set) | orchestrator | math/00 §3 | CLAIMED | adversary: scope of "uniform"/"lossless" definitions |
| B | 5DOF M1 (no altitude constraint): midpoint M unreachable ⇒ R, F_tf nonconvex (δ+ωtf/2 ≤ π/2 via proof's ball bound) | orchestrator/proof | math/00 §4, math/02 | CONFIRMED (algebra) / SCOPE-BROKEN | adversary: witness arcs start underground for GTPL (ρ1<m0 g) ⇒ vacuous under r_z≥0; numerics: confirmed, gap≈0.31·ωtf·|P_x| |
| B* | Dive-then-brake exposed face: every maximizer of ℓ=∫(s−s*)a d_z has lateral v0≠0 ⇒ F nonconvex for all tf, free tf, with altitude/glide-slope constraints | adversary | math/01 §B* | CLAIMED | needs proof agent rigor + numerics a2 + Lean |
| D | Min-landing-error: for fixed (r0,v0), any STATE-LINEAR relaxation (physical r,v linear in relaxed vars, relaxed landing set convex ⊇ true set L) is lossy at targets q ∈ conv(L)\L; needs only L nonconvex. No joint convexity in q needed; immune to frame rotation (closes loopholes (i),(ii)) | orchestrator | LOG | CLAIMED | proof: write rigorously; adversary: attack; need L nonconvex with altitude constraints |
| OM | Occupation-measure LP is convex and value-exact (Vinter) but NOT state-linear (state lifted to δ_x); consistent with A and D; it's the honest boundary of 'impossibility' | redteam-lift | math/redteam-lift.md | CLAIMED | |
| T | Berning et al. 2023 'Lossless convex guidance for lunar PD' claims LCvx with tilt-rate limits — which rate notion? possible counterexample to impossibility for tilt-angle-only rate models | redteam-reform | | OPEN | |
| B6 | 6DOF inherits B | orchestrator | math/00 §4 remarks | CLAIMED | adversary-6dof |
| C | LCvx holds given a fixed attitude profile b(t) (non-degeneracy condition) | positive | math/04 | CLAIMED | |
| P-Q | M1, b(tf) free: ‖I‖ ≥ G(τ) ∀I∈R; dist(M,R) ≥ Γ=(4a1(tf/4)/ω)sin(δ+ωtf/2)sin²(ωtf/4) for δ+ωtf/2 ≤ π/2 (+M_z≥0) | proof | math/02 §5 | CLAIMED | Lean primary route |
| P-B | Thm B rigorous (rigidity route), both variants (free: δ+ωtf≤π/2; tent: δ+ωtf/2≤π/2) | proof | math/02 §4 | CLAIMED | |
| P-T | Tent variant quantitative: dist(M,R) ≥ min_β max_λ[...] >0 (proved α=0; numerically all tested α) | proof | math/02 §5 | CLAIMED | |
| P-L | M1, b(tf) free: F_tf nonconvex for ALL tf>0, 0<ω<∞, 0≤δ<π, ρ1>0, any α (min-I_z + rigidity + weak* compactness) | proof | math/02 §7 | CLAIMED | |
| P-L0 | Same with ρ1=0, α=0, provided δ+ωtf>π/2 | proof | math/02 §8 | CLAIMED | |
| P-E | Envelope models (M3a: independent transverse torque, axisym J, Ω(0)=0; M4 rate/torque-limited 6DOF): nonconvexity transfers (b(tf) free) | proof | math/02 §6 | CLAIMED | not M3b (gimbal-coupled torque) |
| P-ε | No ε-lossless uniform relaxation for ε < dist(M,R) | proof | math/02 §5 | CLAIMED | |
| P-tf | Free final time on window [ta,tb]: ∪F_t nonconvex if ‖M_tb‖+g0(tb−t)<G_t(t/2) ∀t∈[ta,tb]; joint (θ,tf) relaxation impossible | proof | math/02 §7 | CLAIMED | |
| P-3 | Exact 3DOF with mass, no pointing cone: F_tf convex (Aumann + a≤a_max) ; with cone: open | proof | math/02 §8 | CLAIMED | |
