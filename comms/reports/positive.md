# [positive] report: when lossless convexification IS possible

Files: `math/04-positive-results.md` (theorems and proofs), `math/05-positive-lean-blueprint.md` (26 Lean lemmas; PMP is the only hypothesis, packaged as `PMPData`), `numerics/positive/c_x_sharpness_purification.py`, `comms/threads/possibility.md`. Claims are registered as rows C-* in `comms/CLAIMS.md`.

**Proved: fixed attitude profile b(t) (Theorem C), model M1.**
- **C-3 pointwise lemma** (elementary, any inner-product space). On {‖T‖≤Γ, ⟨b,T⟩≥Γcosδ}, every maximizer of ⟨y,T⟩ has ‖T‖=Γ, unless y ∈ −ℝ₊b. In that case the maximizer is unique, and the exception is sharp. It follows from a general lemma: a maximizer strictly inside the ball forces y into the normal cone of the other constraint.
- **C-W, weak form, no PMP.** For *any* measurable b, the relaxation has the same optimal value and the same feasible boundary data as the original. A lossless optimum exists with the same Γ, mass and terminal state. Nodewise state constraints are handled exactly; path constraints in value under Slater. The proof uses Aumann's theorem, which is cited and not formalized.
  - **C-F:** F_tf(b) is convex for each fixed b (constant mass or Taylor-convexified mass).
- **C-E, PMP-free.** The relaxation can only be lossy at minimum throttle ("thrusting below ρ1"). With mass, it can also be lossy on an arc followed by max-throttle saturation.
- **C-S/C-D, strong form, under PMP.** The primer is affine, p = a + ct, for every b and with mass. Every relaxed optimum is lossless off D = {p ∈ −ℝ₊b}. With α=0, the lossy set ⊆ D ∩ {Γ=ρ1}.
  - D is characterized exactly. It has positive measure only if (i) p ≡ 0, which forces min throttle throughout, (ii) b dwells at one direction, or (iii) b runs along a "gnomonic line" (a+ct)/‖a+ct‖.
  - The conditions are checkable a priori: for analytic b, a non-planar profile (det(b,ḃ,b̈) ≢ 0) suffices. The bad set of profiles is meagre.
- **C-X, sharpness.** Fixed upright cone, vertical descent, too much time: the interior-point solver returns a lossy optimum (19 nodes, all at Γ=ρ1). This explains the looseness of the stored GTPL solutions on the min-thrust arc.
- **C-K, discrete time.** KKT gives a nodewise test with an affine discrete primer. One purification SOCP (Γ fixed, random linear objective) leaves ≤3 lossy nodes (≤ ½Σcᵢ with state constraints). Numerically it took 19 → 0.

**Proved: possibility beyond fixed b.**
- **C-U.** F = ∪_b F(b), with every F(b) convex, and V = min_b V(b). The convex program at the optimal attitude b*(θ) is exact. So **non-uniform (per-instance) LCvx exists, and all of the nonconvexity in Claims A/B/Q/L sits in the choice of attitude.** The M1 optimum exists for α=0.
- **C-6, gimbal-torque-coupled 6DOF TVC (M3b), constant mass.** Torque balance forces Π_bT = −(J⊥/ℓ)Π_b b̈. Given b, the exact 6DOF problem is a convex scalar-throttle program with no relaxation, and F^{M3b}(b) is convex. Holding the body upright with a 15° cone makes the usable cone δ_eff = 0, which confirms the orchestrator's caveat.
- **C-3D, exact subclass for uniform 3DOF LCvx.** V₅ = V₃ iff some 3DOF optimum is δ-trackable by an admissible attitude profile. There is an O(1) closed-form certificate: ω_req = ‖a×c‖/min‖a+ct‖² ≤ ω and ∠(b₀, p̂(0)) ≤ δ. The peak angular acceleration of a primer arc is (3√3/8)Ω².
- **C-Y, thinness under TVC coupling.** A prescribed planar thrust history with ‖T‖ ≥ ρ1 is TVC-realizable only for in-plane initial body rates in a set of diameter ≤ 2δμc/sinh(μc t_f), where μc² = ℓρ1cosδ/J⊥. For GTPL this is 3.5 µrad/s. So 3DOF LCvx is exactly 6DOF-optimal only on a near-null set; in M1 the exact subclass is large.

**Consistency.** Nothing found contradicts Claims A/B/Q/L. Both the relaxation's lossiness and the Theorem B witness live on min-throttle arcs.

**Open / conjectures.**
- Q1: with ρ1=0, α=0 and δ+ωt_f ≤ π/2, is F^{M1} convex? That would be a uniform-possibility regime.
- Q2: is F(b) convex with exact mass dynamics?
- Q3: quantitative bounds on V₆−V₃.
- Q4: is the M1 exact subclass open?

**Deferred per orchestrator: algorithm.** The recommended future design follows from C-U: an attitude-profile outer loop, with each step solving the exact convex inner program (Thm C or C-6), purification, and a certified gap V(b)−V₃. Candidate update rules are a dual-weighted safe attitude step, or CCP on the bilinear constraint ⟨w,u⟩ ≥ σcosδ (Lean P22 validates the restriction). This is not developed until the lossless question is closed.
