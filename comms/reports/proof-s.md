# [proof-s] report: Lemma S

**Verdict.** Lemma S is **TRUE and proved rigorously** in an explicit regime. In that regime every state-linear relaxation of the minimum-landing-error problem with *hard* v(t_f)=0 is lossy by a macroscopic, certified amount. **GTPL is outside that regime.** For GTPL, S holds only numerically (thin in the vertical functional), and its rigorous proof is open. Details: math/07-lemma-S.md.

## What is proved (Theorem S, math/07 §3)
- **Master inequality (Prop. M), valid for every admissible M1 trajectory with any 3D attitude path (coning included), any throttle, α ≥ 0:**
  gain := ∫a₁ − I_z ≤ B + C_m‖π_{m(F)}‖².
  Here π is the affine function carrying the two lateral moments (∫F, ∫sF) of the lateral force F = a d_h. B and C_m are explicit.
- **Key tool: Lemma W.** ‖P^⊥f‖² ≤ (T/2π)²‖ḟ‖² for f ∈ H¹((0,T);ℝ^N), where P is the projection onto affine functions. The proof is three lines via periodic Wirtinger, and the inequality is sharp.
  It is componentwise and rotation-invariant, so planar S-turns, coning, and even ℝ^N-lifted paths obey the same bound. Coning never has to be analysed.
- **Witness.** A planar single-crossing S-turn that does NOT return to zero tilt (tilt ramps to ωt₁ and then reverses for the rest of the horizon), with I_h = 0.
  Its mean-square tilt is (3√2−4)/6·Ω² = 0.0404Ω², against the Wirtinger cap Ω²/4π² = 0.0253Ω².
  The "triangle of amplitude Ω/4" used in earlier comparisons gives only Ω²/48, which is why the S-turn-vs-coning margin looked thin.
- **Conclusion.** At the witness's vertical data ζ_w, every landing offset satisfies |p| ≥ r_S = (M T³/(12C_m))^{1/2}, where M = gain_w − B.
  So L(ζ_w) ⊇ circle, 0 ∉ cl L(ζ_w), and Theorem D gives relaxed error 0 against true error ≥ r_S.
- **Regime.**
  - δ+ωt_f < π/2.
  - (ρ₁/m₀)cos(δ+ωt_f) > g₀: min-throttle T/W > 1, so the altitude constraint holds automatically. The glide slope (apex r(t_f)) holds under an explicit inequality.
  - κ₀ > A' (throttle condition).
  - M > 0. For a demo vehicle with a₁ = 12 and a₂ = 25 m/s²: ωt_f ≤ 0.55 rad (δ=0), ≤ 0.45 (δ=5°), ≤ 0.30 (δ=10°).
  - **Certified dents r_S = 0.39–1.80 m** (T = 2–4 s).
- **Small-angle corollary.** M/(a₁T) = 0.00755Ω² + o(Ω²) > 0 when δ/Ω → 0.

**Adversary verdict:** Theorem S SURVIVES ([adversary] math/01 §9). Its a7 reproduces table row 1 and a8 confirms the bound empirically (~1.7× loose).
**Realism caveat:** the regime needs min-throttle T/W > 1 (the vehicle cannot hover at minimum throttle). That excludes essentially every throttleable lander, not only GTPL.
**Numerical extension:** the S-procedure (discretized SDP) certifies δ = 15° at Ω = 0.3 with an 8% margin. Not yet rigorous.

## GTPL (task 2)
- **No realistic GTPL instance in the proven regime.** ρ₁/m₀ = 5.0–7.2 m/s² < g₀, so the pure-waste face is underground.
- S for GTPL must use dive-then-brake faces. [numerics] s1_slice finds strict gaps there (exact 3D, coning starts, r_z ≥ 0): 0.016 m at t_f = 4 s and 0.009 m at t_f = 8 s, with Pv optimizers landing 1.5 / 2.4 m off-axis.
- So the GTPL dent is macroscopic at the exact face data but non-robust: a data perturbation of ~1 cm in ℓ closes it.
- My L²/Wirtinger slack in that setting is cm–dm, so a rigorous GTPL proof is open.

## Long horizons (task 3)
- No evidence that S fails.
- At tilt-capped faces with long plateaus, coning fills most of the dent but not all of it ([adversary] s3, exact 3D, 30° cap: the gap falls from 0.69 m/s at 8 s to 0.106 m/s at 20 s, against 0.82 for planar maneuvers alone). Short-dive faces never reach the cap.
- [adversary] s4: the altitude-constrained pure-waste face for GTPL ends at hop data (starting on the ground, moving up), where gaps are large. This matters if lift-off-to-landing guidance is in scope.
- Dents can only live at throttle-saturated (face) data (heuristic Remark 6.1).
- The certificate itself is short-horizon because the quadratic majorant of 1 − cos degrades with tilt.

## Weak points (please attack)
- E₄ (pointwise majorant slack) blocks δ ≥ 15° with the analytic constants.
- α > 0 enters crudely, through ε_m in δ_e.
- Variant F only: the witness ends tilted. The b(t_f) = e_z variant needs a modified witness.
- The S-procedure SDP (sproc_pure.py) and the adversarial NLP check (attack_S.py) are numerical, not proofs. Results are in the math/07 appendix.

## Files
- math/07-lemma-S.md.
- math/03-lean-blueprint.md, section "Lemma S" (SW1–SS4; the only analytic input is periodic Wirtinger).
- numerics/proof-s/{verify_S.py, regime.py, regime2.py, attack_S.py, sproc_pure.py, sigmaP.py, eig_*.py}.
- CLAIMS rows S (status updated), S-W, S-M, S-T, S-GTPL, S-LH.

## Follow-up: hop instance (pad-launched GTPL data), math/07 §8
- **Verdict: NOT proved.** [numerics] s5 shows a ring-shaped landing set at r0 = 0 (on the pad), v0z ≈ 7.73–7.92 m/s, tf = 4 s. Its hole remains numerical.
- **Rigorous pieces:**
  - exact reduction (M_z = ½g tf² is fixed, so this is a dive-then-brake face family);
  - upright pad-landing limit 7.2045 / 7.2833 m/s (α = 0 / α > 0);
  - planar offset witnesses v0z = 7.7116 m/s (lands 6.58 m off) and 7.7425 m/s (lands 4.61 m off).
- **Method limit:** the best Shor/S-procedure certificate bounds pad landing by v0z ≤ 7.88 m/s, above the witness at 7.71. So quadratic and Wirtinger arguments cannot close the hole.
  - Tilts reach about 1 rad, where the quadratic majorants are loose.
  - The ℝ^N-lift is automatic, and the true margin is thin.
- **What a proof needs:** an argument that uses the 2D lateral plane, either rigidity of the Pv maximizers or a validated branch-and-bound.
- **TVC version:** not attempted; [proof-tvc] informed.
- **CLAIMS:** S-HOP, status OPEN.
