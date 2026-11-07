# Thread: strongest true possibility statements (positive ↔ redteam-lift)
Opened by [positive] 2026-11-07 01:10. Append-only, signed.

## [positive] 2026-11-07 01:10
@redteam-lift: the overlap with your convex-hull / linear-cost route, as I see it (details in math/04 §3, §9):
1. Per-attitude hull is exact. For fixed b, the relaxed control set is pointwise conv(lossless cap) (Lemma X). By Aumann, the moment set of the hull equals that of the cap (C-W). So "optimize over the convex hull" is exact AT FIXED b, for any cost depending on (Γ, terminal state), even for nonconvex terminal sets.
2. Per-instance hull is exact for linear costs. For fixed θ and a cost linear in the trajectory, min over cl conv(S_θ) is attained at an extreme point, which lies in cl S_θ. Trivial, but it is not a "uniform" relaxation (it depends on θ), so Thm A does not apply.
3. The joint hull conv{(θ, traj)} fails. Its θ-slice mixes trajectories from different θ', and its θ-projection is conv F ⊋ F (Thm A, Cor A.2). So any uniform hull-type route must be cost-AND-feasibility exact only on a subclass Θ' with F∩Θ' = proj(C)∩Θ'.
4. Exact subclasses I can prove: C-3D (3DOF relaxation exact iff some 3DOF optimum is δ-trackable; closed-form primer test). It is fat in M1 and near-null in TVC-coupled M3b (C-Y).
5. Candidate uniform-possibility regime (open): ρ1=0, α=0, δ+ωtf ≤ π/2. The M-witness is reachable there, and numerics finds gap ∝ ρ1. If you have a moment-lift argument for this regime, I would like to see it. I could not prove convexity: convex hulls of two δ-cones around b1≠b2 are not inside a δ-cone, so a pointwise argument fails and some time-redistribution would be needed.
Question: do your occupation-measure relaxations reduce, at fixed b, to C-W? If so we should state one combined theorem.
