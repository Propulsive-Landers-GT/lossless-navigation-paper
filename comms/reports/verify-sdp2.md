# Report: [verify-sdp2] (referee of math/09, CSD2′ partial proof)

Full report: math/verify-sdp2-report.md. Numerics: numerics/verify-sdp2/ (own venv and code).

## Verdicts
| Result | Verdict |
|---|---|
| T1 alignment, CSD2′ ⇔ R_X∩E² = R_3 | CONFIRMED ("attained"/"compact" wording for infinite-dim X) |
| T2 primer-plane fold, linear objectives exact (closes SDP-F) | CONFIRMED (scope: linear functionals of (V,R); m for dim Π ≤ 1) |
| T3 continuous stress, J_red, κ | CONFIRMED given (H); κ = −∂²σ |
| T4 Thm 4.1 (continuous) / Thm 4.4 (discrete) | CONFIRMED (given (H) / rigorous); case F needs ⟨b_N,c⟩>0 |
| T4 Cor 4.3 a-priori vertical shortfall | NEEDS FIX (minor): add the normality/CQ hypothesis |
| T5 Thm 5.1 index identity | CONFIRMED (C_yw symmetric automatically; on-axis C_yw=0 covered) |
| T5 Thm 5.2 Sturm | case T CONFIRMED (add D≻0 + end couplings); case F NEEDS FIX → neg Z = k exactly ⇒ exact ⇔ k ≤ p₀ |
| T5 numerical claims | NEEDS FIX: hypotheses hold at a minority of optima (188/898; c1 9/17, not 16/17) |
| P6 no free singular arcs | CONFIRMED |
| P7 unit-d mechanism | CONFIRMED as mechanism + numerics; "diagonal of Q" → of Z; ≥3 μ_d<0 ⇒ Q≱0 is the rigorous part |
| §7 physical meaning (Aumann) | CONFIRMED (unit-norm selection in the cap, terminal-time exact, chattering) |

No BROKEN items. CSD2′ remains OPEN and unbroken: 898 fresh optima give 0 gaps.

## Answer to the orchestrator's C_yw query
C_yw symmetry follows from KKT stationarity along the e_z-rotation, so it is not a hypothesis. All 14 non-symmetric records in [verifier-sdp] idx_full have C_yw ≈ 0:
- 12 are on-axis targets;
- 2 have zero lateral residual (I re-solved these; |y_h| ≤ 2e-7).

The asymmetry is an artifact of normalising by max|C_yw|. The on-axis case is covered by Thm 5.1 (M = 0, p₀ = 2). The y_h = 0 case falls outside it (Yres singular), as the theorem correctly states.

## Requested edits
See math/verify-sdp2-report.md §9.
