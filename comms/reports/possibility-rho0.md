# Report: possibility-rho0 (ρ1 = 0 regime)

**Question.** Take ρ1 = 0 (the engine can switch off), constant mass, and the short horizon δ+ωtf ≤ π/2. Is the 5DOF landing set F_tf convex, which would make it a uniform-LCvx-possible regime?

**Answer: no.** Switching off makes the velocity set convex, but not the landing set.

| Claim | Statement | Status |
|---|---|---|
| P0-R | R convex **iff** δ+ωtf ≤ π/2 (tent: δ+ωtf/2 ≤ π/2). Then R = R_env, the 3DOF time-varying envelope set, so the envelope SOCP is exact for velocity-only targets. | proved (RR-R0 + converse + identification) |
| P0-F | ρ1=0, α=0, b(tf) free, 0≤δ<π/4, 0<ωtf<π/2−2δ: F_tf **nonconvex**, so no lossless uniform convex relaxation exists (Thm A). | proved |
| P0-X | Same with altitude r_z ≥ 0: nonconvex if T/W ≥ 1/(cos(δ+ωtf)(1−x*²)) ≈ 2.1. | proved; numerics give ≳1.7; **GTPL 1.27 open** |
| P0-T | Tent variant b(tf)=e_z | ties found numerically |
| P0-TVC | Pure TVC, small gimbal / strong torque, free terminal attitude | proved (asymptotic); GTPL constants open |

**How P0-F works.**
- Exposed faces of K correspond to affine primers. Use the sign-change primer p(s) = (s−σ)p̂, i.e. maximize ⟨p̂, r0+σv0⟩ over F, with p̂ pointing δ below the horizontal.
- θ = ∠(p̂, b) reduces the face exactly to a 1D problem in β* = β(σ). Optimal paths are lower/upper Lipschitz envelopes.
- The thrust on/off boundary (where the gimbal can no longer point within 90° of the primer) is a *convex kink* of the pointwise payoff. It produces two competing maximizers.
- An IVT in σ gives a tie. The linear functional ⟨p̂, I⟩ separates the two maximizer groups. Connectedness of convex sets then shows the face is not contained in K.

**Physical reading.** Both witnesses steer by coasting while the body rotates, which is exactly what ρ1 = 0 adds.

**Size.** At GTPL-like numbers (ω = 0.4 rad/s, δ = 15°, tf = 1.5 s) the 3D NLP gives dist(θ_m, F) ≤ 0.045, against a witness separation of 10.8 (m, m/s). Nonconvex, but thin (as in B*).

**Consequences for the program.**
1. The dichotomy "5DOF LCvx possible iff ρ1 = 0" is **false**. Impossibility does not depend on min throttle.
2. The only exact convex object at ρ1 = 0 is the velocity set (R = R_env).
3. Practical impossibility for GTPL (T/W 1.27, altitude constraint, TVC) is still open here, and every gap found is thin. This matches the [adversary] / [numerics] picture.

Files: math/possibility-rho0.md; numerics/possibility-rho0/ (face.py, face2.py, lateral.py, dp.py, p5–p13, out_*.txt; own .venv).
