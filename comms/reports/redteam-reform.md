# [redteam-reform] report: can classical LCvx machinery be pushed to 5DOF/6DOF?
Details: math/redteam-reform.md. Scripts: numerics/redteam-reform/. Claims: T, RR-T, RR-P, RR-TVC, RR-LS, RR-R0.

**Bottom line.** I could not make it work. Every route either fails with a proof or reduces to a degenerate exact class. The obstruction is the feasible set itself, not any particular slack.

| Route | Verdict |
|---|---|
| 1. LCvx-style slacks/changes of variables (Γ annulus, z=ln m / σ=Γ/m, ball-relaxed direction or body axis, w=Γd with ‖ẇ‖≤ωσ, thrust-vector rate ‖u̇‖≤ωσ, time-varying cones, SDP/orbitope lifts) | **FAILS.** Each has convex, rotation-invariant constraints. So it accepts the symmetrized B* witness x̄ = (x*+R_πx*)/2, which is infeasible. The lossy set has positive measure, so normality conditions cannot rescue any of them. Mechanism, the **chord shortcut**: once the direction is a rate-limited state, its convex surrogate (a Euclidean speed bound) lets the trajectory cut through the ball instead of following the sphere, and Pontryagin acts on u̇, not on u. |
| 2. Counterexample to Claim B | **None** in the algebra; every step checked. Scope holes: underground witnesses (adversary, confirmed); with an active tilt cap and long tf, or with a free initial attitude, B's M is actually reachable by sliding around the cap. B* with a small switch time s* repairs all of these. I independently re-derived and confirm adversary's B*. |
| 3. Exact classes | **M1 only:** pointing cone θ_p ≤ δ ⇒ F_5DOF = F_3DOF exactly, so classical LCvx is lossless; θ_p > δ ⇒ nonconvex, so the threshold is sharp. **Pure TVC (the real vehicle):** b̈ = k(b−d) is unstable (√k ≈ 1.9–3.0 s⁻¹). The exact class collapses to θ_p = 0. A-posteriori exactness holds only on a measure-zero set (terminal attitude fixed) or an exponentially thin set (~10⁻⁷ rad, terminal attitude free). **ρ1=0 with no down-thrust:** the velocity set R is convex (theorem); full F is OPEN. Large ω, large δ, long tf: no exact regime (only ε-lossless as ω→∞). |
| 4. Free final time | **FAILS.** Lemma RR-LS: x̄ ∈ conv F_{t*} \ ∪_t F_t. So every per-horizon convex family used with a line search accepts an infeasible point. This covers both the feasibility form and the optimization form (min-fuel, min-error). A single program with tf as a jointly convex variable fails as well. Condition: the B* braking condition at the optimal t*. |
| 5. 6DOF | Kinematic 6DOF and any quaternion/dual-quaternion/SO(3)-orbitope lift **FAIL** (projection + Thm A + B*). Torque-limited M3: B* needs a new structure lemma, because the acceleration-bounded tilt class is not closed under max. M3b (gimbal = torque): OPEN, owned by adversary-6dof. |
| T. Berning et al. 2023 | The paper is **3DOF** (per the Wang survey; full text not obtainable). Only a thrust-vector (chord) rate is SOC-representable, and that relaxation is provably **not** uniformly lossless (the original problem reduces to M1 with δ=0 and modulus r/T, so B* applies). Tilt-angle-only rate: its velocity set is exactly the envelope-LCvx set (convex; theorem). For the full (r0,v0) set the envelope SOCP is lossy (DP gap up to 3.4%), and convexity of the true set is OPEN. Full-direction rate is the physical model: a tilt reversal at GTPL tilts costs 1–3 s of a 7 s burn. |

**Useful for the practical phase.** Convex *sandwich* for M1 (pure TVC breaks the inner test, §3.4):
- Inner test: 3DOF LCvx with cone δ about b0. If it is feasible, it is an exact flyable M1 solution.
- Outer test: 3DOF with the time-varying envelope cone. If it is infeasible, the instance is certifiably infeasible.
- The B* witnesses lie in the gap between the two.

**Open, handed to numerics (math/redteam-reform.md §7):**
- tilt-only envelope gap with a pointing cap;
- ties in ρ1=0 full-F maximizers;
- size of the M2 gimbal-rate gap (expected ≲ 0.2 m/s);
- line-search check of x̄* for GTPL.
