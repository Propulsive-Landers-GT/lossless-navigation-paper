# [adversary] final report (≤1 page). Full text: math/01-adversary-report.md

**Target:** math/00 Theorem A (lossless uniform convex relaxation ⇒ F convex) and Theorem B (5DOF F_tf nonconvex via M = ½(P_u + P_−u)).

**Algebra of Thm B: SURVIVES.** I checked each step: the spherical triangle inequality, its equality case, a.e. ⇒ everywhere by continuity, rigidity through the tent peak,
measurability of u, gimbal chattering (all bounds are pointwise a.e.), and a ≥ a1 with its equality case. One hypothesis is missing: m0 − αρ1 tf ≥ m_dry.
I could not reach M. [numerics] and [proof] pin dist(M, R) ≈ 1.8–2.2 m/s at GTPL tf = 2 s.

**BREAK (scope): the witness P_u is underground for GTPL.** ρ1/(m0 g) = 0.51, so along P_u the vehicle rises toward touchdown.
r0z = −41.7 m (ramp, tf = 3.27 s) and −148 m (tent) (a1_Pu_altitude.py). Under the standard glide-slope / r_z ≥ 0 constraint, P_u ∉ F.
Thm B, and every result built on M, says nothing about the real soft-landing problem. Thm B also needs δ + ωtf ≤ π/2, i.e. tf ≲ 3 s for GTPL, while real burns are 7–12 s.

**FIX: Theorem B\* (dive-then-brake exposed face), approved by main, handed to [proof].**
- Construction: maximize the rotation-invariant ℓ = ∫(s − s*) a d_z. Freeze the throttle; the cost then depends on b only through Φ = angle(b, e_z).
- Envelope replacement forces |Φ'| = ‖ḃ‖. So b is meridional, every maximizer has lateral v0 ≠ 0, and the rotation-midpoint lies outside cl F.
- Scope: valid for every tf, for free tf, for any attitude-independent throttle/mass model (incl. Taylor-approximated mass), and for b(tf) free or fixed.
- With altitude/glide-slope/tilt-cap constraints it needs an explicit braking condition (GTPL tf = 8 s: 13.8 < 18.3 ✓). Rigorous in math/02 §10 (with ωs* ≤ δ) and §10.6 (envelope version). I checked both: they SURVIVE.
**Thin gap (key caveat):** under r_z ≥ 0, every face found so far has a gap of ≤ ~1 cm (rigorous 1e-5 m; heuristic a6). The m/s gaps live only at underground faces. So *practical* ε-impossibility for GTPL is NOT established.

**Definitions (Thm A): the math SURVIVES, the scope NEEDS FIX.**
1. Data must enter **affinely** (or separable-monotone). With δ_θ entry (occupation measures) an exact infinite-dimensional convex LP exists. That is consistent with Thm A, since θ ↦ δ_θ is non-affine. With affine mean-entry, that LP feasible set is conv cl F, exactly the loss Thm A predicts.
2. A.e.-lossless and ε-lossless: SURVIVE, because the gap contains an open set.
3. Thm A excludes **detection-sound** losslessness. Standard LCvx claims exactly this, so it is the right target. "Exact on F, feasible off F" is not excluded: it fails for attitude-sensitive costs ([redteam-lift] Prop T), and is **open for min-fuel**.
4. **Frame-rotating relaxations** (rotate so v0_lat ∥ +x) need only F ∩ H convex. Neither B nor B* covers them. Main's Theorem D (min-landing-error, state-linear) is per-instance and frame-free, but reduces to the same open lemma: some r0_lat-slice of F is nonconvex (equivalently, landing straight below is infeasible while an offset landing is feasible). The B* technique does not give it directly, because the lateral endpoint multiplier breaks the Φ-only structure. Coning threat (§7): S fails at capped long-plateau pure-dive faces. Small-angle a5 shows S holding despite coning for pure dive at tf = 3 and 8 (no cap): Pv > Pvr by 23–39%, and at dive-brake faces (tf = 8) by 5–14%. At tf = 20 with a 0.6 rad cap the gap is 0. [numerics] s1_slice.py is decisive.
5. D's class needs (d) sharpened. An **escape**: a Shor lift R ⪰ r(tf)r(tf)ᵀ with squared-error cost tr R − 2qᵀr is (a)–(c)-compliant and immune to D's argument. Moment-lifted costs must be excluded explicitly (comms/threads/theorem-D.md).
6. Discretization: discrete 3DOF LCvx is not exact either (with N = 1 the data set is an annulus; Luo–Echigo–Açıkmeşe 2026). So state the theorem in continuous time, with a uniform-in-N gap corollary.
7. Free tf / line search / dilation: math/00's witness fails ([redteam-lift] §4.3). B* survives because its weight is tf-independent.

**3DOF does not prove too much:**
- The exact continuous-time 3DOF F (with mass, no pointing cone, no binding fuel limit) is convex: σmax domination + Aumann.
- The 1D rocket with mass is convex numerically up to mass ratio 0.46.
- Fuel limit or pointing cone with α > 0: open, not refuted.

**6DOF:**
- Kinematic attitude, and independent-torque rigid body with Ω_⊥(0) = 0: transfers.
- Rigid body with Ω as a state: P_u is unrealizable, so math/00's remark is wrong.
- TVC-generated torque (GTPL's actual actuator) is OPEN; owned by [adversary-6dof].

**Strongest defensible statements.**
- Impossible: in continuous time, M1/kinematic-6DOF/independent-torque, b(0) = e_z, ρ1 > 0, any tf or a free-tf window, with glide-slope constraints under B*'s condition: no convex relaxation with (r0, v0) entering affinely is lossless (feasibility form, a.e., or value-exact for all convex costs). ε-lossless is excluded only for tiny ε under altitude constraints (≈1e-5 m rigorous, ≈1 cm heuristic); without them it is excluded for ε up to about 2 m/s.
- Possible: per-instance fixed attitude (Thm C); non-affine (Dirac/moment) data entry. Not excluded: exact-on-F for min-fuel, and frame-rotating relaxations.
