# Is 5DOF / 6DOF lossless convexification possible? — living synthesis

Orchestrator-maintained. Every item links to the file with the proof. Status keys:
**LEAN** = machine-checked (sorry-free, standard axioms only) · **PROVED** = rigorous proof that survived adversarial attack ·
**NUMERICAL** = strong numerical evidence only · **OPEN**.

## Short answer (current)

1. **Impossible in the LCvx sense.** Classical LCvx keeps the physical state (r, v, m) as decision variables, enters
   boundary data affinely, and relaxes the control constraints. No relaxation of that kind can be lossless for 5DOF
   with a finite attitude rate — with a minimum throttle ρ1 > 0 (B, B*), and even with ρ1 = 0 (P0-F: the vehicle can coast while it rotates, which creates a different nonconvex kink). The obstruction: the set of feasible boundary conditions is
   nonconvex, because the vehicle cannot "chatter" its thrust direction (math/00, math/02).
2. **The obstruction is genuine but, under ground constraints, thin for GTPL.** With r_z ≥ 0 the proven dent is
   ≈1e-5 m (rigorous) to ≈1 cm (heuristic) for the kinematic model. Large (m/s-level) gaps exist only for
   trajectories that would start underground (math/01, math/02 §10).
3. **Possible in other senses:**
   - **Fixed attitude profile:** given b(t), the convex relaxation is exact (Thm C, math/04). On the real TVC vehicle,
     given b(t), the problem is exactly convex with no relaxation needed (C-6).
   - **Per instance:** the nonconvexity is entirely the choice of attitude profile (C-U).
   - **Infinite-dimensional lifts:** occupation-measure LPs with point-mass data entry are exact (generic; not practical).
   - **Tractable SDP lift:** the degree-2 SDP (Shor) lift is NOT exact in general (fails with gimbal and with
     variable throttle), but survives for fixed thrust with no gimbal and is exact on realistic in-air targets, which
     makes it a global-optimality / infeasibility certificate rather than a general solution.

## Results table

| ID | Statement | Model / scope | Status | Where |
|---|---|---|---|---|
| A | Lossless uniform convex relaxation (affine data entry) ⇒ feasible boundary-data set convex | abstract | **LEAN** | lean/…/Abstract.lean |
| B | Midpoint of extreme min-throttle arcs unreachable ⇒ F_tf nonconvex | M1 kinematic 5DOF, no altitude constraint, δ+ωtf ≤ π/2 | **LEAN** (`no_lossless_relaxation_5dof`) | lean/…/Main.lean |
| Q | Quantitative gap Γ (ball bound) ⇒ no ε-lossless relaxation for ε<Γ | M1, no altitude constraint | PROVED | math/02 |
| B* | Dive-then-brake exposed face ⇒ F nonconvex with altitude/glide slope, any tf, upright landing, bounded free-tf window | M1; kinematic 6DOF; independent-torque 6DOF | PROVED (Lean pending) | math/02 §10, math/01 §B* |
| RR-LS | Line search over tf cannot rescue LCvx (needs B*'s braking condition / time window) | M1 | PROVED (Lean pending) | math/redteam-reform.md §4 |
| A-opt, T | Value-lossless on F ⇒ V = V** on F; cost ∫b·e_z violates it | abstract / M1 | PROVED | math/redteam-lift.md §7 |
| D | Per-instance min-landing-error: state-linear relaxations lossy | M1 | PROVED for terminal-error cost; hard-v(tf)=0 version needs Lemma S | math/02, threads/theorem-D.md |
| S | Straight-below landing infeasible, offset feasible (vertical instance) ⇒ Theorem D with hard v(tf)=0 lossy by ≥ r_S (0.4–1.8 m) | M1; δ+ωtf<π/2; min-throttle T/W > 1/cos(δ+ωtf); certified ωtf ≤ 0.55 (δ=0) … 0.30 (δ=10°). Handles coning (Wirtinger lemma) | PROVED (adversary: no flaw) | math/07-lemma-S.md |
| S-GTPL | Lemma S at GTPL constants (hovering possible at min throttle) | M1 | NUMERICAL (gap ≈1 cm in ℓ; optimizers land 1.5–2.4 m off-axis) | math/07, numerics s1 |
| FLAT | Centre-of-percussion identity: pure TVC ≡ zero-gimbal, torque-limited point thrust along b | pure TVC, ω3 ≡ 0, ε const | identity verified numerically (5e-15) | math/checks/flat_output_tvc.py |
| B6-TVC | Pure-TVC F nonconvex | terminal r=v=0, ω⊥(tf)=0, tilt free | PROVED (adversary-6dof) | math/adversary-6dof-report.md |
| B6-TVC-up | Pure-TVC F nonconvex, upright at rest + r_z ≥ 0 (**the real GTPL case**) | pure TVC | OPEN (proof-tvc) | math/06 (pending) |
| C | LCvx exact given attitude profile b(t); strong form under PMP + checkable non-degeneracy | M1 | PROVED (Lean in progress) | math/04, math/05 |
| C-Y | 3DOF LCvx optimum exactly 6DOF-flyable for GTPL essentially never | pure TVC | PROVED | math/04 |
| X5 | Pointing cone ≤ gimbal ⇒ 5DOF = 3DOF, LCvx exact | M1 only (pure TVC: effective gimbal 0) | PROVED | math/redteam-reform.md |
| P0-R | ρ1 = 0: velocity set R convex iff δ+ωtf ≤ π/2 | M1 | PROVED | math/possibility-rho0.md |
| P0-F | ρ1 = 0 still gives nonconvex F_tf (coast-while-rotating; thrust on/off kink) ⇒ no 'possible iff ρ1=0' dichotomy | M1, α=0, δ<π/4, ωtf<π/2−2δ | PROVED | math/possibility-rho0.md |
| P0-X | ρ1 = 0 with r_z ≥ 0: nonconvex for T/W ≳ 2.1 (numerics ≳1.7); GTPL T/W 1.27 open | M1 | PROVED (regime) | math/possibility-rho0.md |
| CSD2 | Degree-2 SDP lift exact for min-landing-error | M1 | **FALSE with gimbal** (case 12: 2.5% gap, SDP value attained by an explicit feasible R⁴ chain; independently reproduced) and **FALSE with variable throttle** (gaps up to 40%). Survives only for fixed thrust + δ=0 (840 adversarial instances, no gap); proof in progress. Exact on all realistic in-air targets tested ⇒ useful certificate (rank-3 ⇒ certified global optimum) | BOARD 03:20, math/verifier-sdp-report.md, math/08 (pending) |
| HOP | Largest physically admissible nonconvexity under r_z ≥ 0: ground-launched hop data (r0z=0, v0z>0): rotation-midpoint gaps 0.65 (tf=4) / 2.9 (tf=8) weighted m/s; in-air descents: cm-level or none | M1 | NUMERICAL | numerics/README.md (pending) |

## What breaks LCvx, in one paragraph
LCvx works for 3DOF because the thrust direction is a free control. The relaxed (filled-in) thrust set is achievable
on average by rapid switching (Lyapunov/Aumann), so the reachable set is already convex. In 5DOF the thrust direction
is tied to a body axis that rotates at a finite rate (or with finite angular acceleration on the real TVC vehicle),
so it cannot switch. With a minimum throttle, "wasting" vertical impulse requires tilting, and maximal tilt forces a
single tilt direction. The average of a left-tilting and a right-tilting maneuver is therefore not flyable, yet any
convex program that contains both must contain their average.

## Practical implications for GTPL (preliminary; practical phase deferred)
- The current 3DOF guidance asks for thrust-direction changes ~10³× faster than the vehicle can rotate, and is not
  relaxation-tight on min-thrust arcs (context/vehicle.md).
- The theory points to: an attitude-profile outer loop + an exactly convex inner problem (C-6/C-U), with SDP-lift
  certificates (if CSD2 holds) to certify global optimality or infeasibility.
