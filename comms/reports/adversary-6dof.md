# [adversary-6dof] final report (≤1 page)

**Target:** Claim B6 ("6DOF inherits B; planar arcs are 6DOF-realizable"). Full write-up: `math/adversary-6dof-report.md`.
Numerics: `numerics/adversary-6dof/` (full rigid body: quaternion + Euler equations, J = diag(Jt,Jt,Ja), roll RCS, cone or box
gimbal, gimbal-rate limit, terminal upright-at-rest option, altitude constraint; GTPL wet parameters from context/vehicle.md).

## Verdicts
| Item | Verdict |
|---|---|
| B6 for kinematic attitude (ω a control) | **SURVIVES** (Thm K; box gimbal via corner angle δ* = 21.1°, u on the diagonals) |
| B6 for any model in which ω is a state | **BROKEN as argued.** P_u needs ‖ḃ(0+)‖ = ω̄, but ω⊥(0) = 0 |
| Pure TVC M3/M4 (GTPL): extreme arcs P_u, M | **BROKEN.** TVC torque: Jt∇ḃ = −L T g. An outward gimbal accelerates the body *inward*, so P_u ∉ R and M ∉ conv R |
| Independent transverse torque (RCS/wheels), any roll, terminal attitude free | **FIXED**: Thm D (= [proof] P-E). Envelope Φ = ∫₀ˢ min(ᾱr, ω̄); rigidity via length = distance |
| Same, with terminal b(tf) = e_z, ω(tf) = 0 | **FIXED (new)**: Thm D*, the torque analog of [adversary]'s B*. Needs an unlimited gimbal rate; the rate-limited case is open |
| Roll/coning to reach the witness | **REFUTED** (Lemma 0: the gyroscopic term does no work on ‖ω⊥‖). Needs Jxx = Jyy |
| Pure-TVC nonconvexity of F (the GTPL question) | **Rigorous only for terminal ω⊥(tf)=0 with tilt free (Thm E₀, via the corrected FLAT comparison). The upright-at-rest case with r_z ≥ 0 is OPEN (now owned by [proof-tvc]) and numerically CONFIRMED** |
| Faithfulness (BCs, tilt cap, rate caps, wind) | **NEEDS FIX**: the hypotheses must be stated. ω⊥(0) = 0 and b(0) = e_z are required. An active tilt cap breaks rigidity. A gimbal-rate limit decouples only in Thm D. Wind breaks the R_π symmetry |

## Key facts
- In pure TVC every pointwise-envelope argument fails, because maximal tilt of d and maximal tilt rate of b are incompatible (Lemma 2).
  The B* late "brake" phase also fails: holding d = e_z with the body tilted is an inverted pendulum.
- Structure of the min-vertical trajectories, from numerics:
  - The gimbal goes fully *inward* first, which spins the body up, then flips fully *outward*.
  - Box gimbal: the motion is planar along a corner diagonal.
  - With terminal rest attitude the gimbal follows a triangle-wave pattern, and angular-momentum balance gives ∫T b×g = 0, so net lateral impulse comes only through body tilt.
- The TVC nonconvexity is *weak*. The bottom-face gap is 0.06–0.21 m/s at tf = 1 s and scales like ~tf⁸ (observed; asymptotic estimate tf⁷) at small tf (2·10⁻⁴ m/s at tf = 0.5 s).
  In M1 it is ~2 m/s at tf = 2 s. A uniform convex relaxation of pure TVC is therefore *nearly* lossless at short horizons, so ε-lossless statements must use the TVC gap, not the M1 gap.
- Small-tf limit problems (proof programme for pure TVC): LP1/LP2 in report §3.4. The vector rigidity of their maximizers and a Γ-convergence estimate would give a rigorous theorem.

## Numerics (pure TVC; bottom-face gap = V₀(lat=0) − V_min)
- **GTPL-realistic case: tf = 1 s, box gimbal, 100°/s, upright at rest. Gap 0.078 m/s.** All 23 adversarial zero-lateral starts (coning, two-lobe, continuation, random) give the same V₀.
- Cone, free attitude: gap 2.3e-4 at tf = 0.5 s, 5.7e-3 at 0.75 s, 6.2e-2 at 1 s.
- Box, free attitude, tf = 1 s: gap 0.21. Cone, 100°/s, upright, tf = 2 s: gap 0.18.
- Dive-then-brake with r_z ≥ 0 (tf = 5/7 s): see math report §4; it is still running under the compute budget.
- Flat-output identity y = r + εb: confirmed (residual 9e-9).
- FLAT conclusion: BROKEN as stated (terminal-condition mismatch) and FIXED as Theorem E₀ (terminal ω=0, tilt free; Lean-ready, report §6).

## Attack on [proof-tvc] TVC-1 (upright at rest, r_z ≥ 0)
- Fails at the submitted tf = 1 s: the remainder R = 2.97e-4 exceeds the witness gain 7.27e-5. R/G ~ tf^5, so retry at tf ≲ 0.6 s or add a localization lemma.
- It also assumes α = 0 and ω3 ≡ 0 for competitors. Inequalities (a)–(c) are checked OK.

## Recommendation to main
The final theorem may claim the obstruction for kinematic 5DOF/6DOF and for independent-torque rigid bodies (Thm D/D*).
It may also claim pure TVC with terminal ω⊥(tf)=0 and tilt free (Thm E₀; needs ε const, ω3≡0, unlimited gimbal rate). It must state that the GTPL soft-landing case (pure TVC, upright at rest, r_z ≥ 0, 100°/s gimbal) has numerical support only (claim B6-E, = Conj B3b, now with [proof-tvc]). Quantitative ε-lossless bounds must use the TVC gap.
