# [verifier-sdp] final report (≤1 page)

**Target:** CLAIMS L-SD2 / Conjecture CSD2: the degree-2 Gram/Shor lift is exact for fixed-thrust 5DOF min-landing-error. The full write-up is `math/verifier-sdp-report.md`; the code and results are in `numerics/verifier-sdp/`.

I wrote an independent implementation and reached my verdicts before reading redteam-lift's code or report:
- Gram SDP with b_0, b_N substituted, Slater verified;
- Clarabel at 1e-9 plus SCS;
- full-Shor cross-check;
- ipopt multistart with rank-3 rounding;
- my own order-2 Lasserre.

## Verdicts
| Item | Verdict |
|---|---|
| CSD2 as briefed (thrust along b_k, δ=0) | **EXACT numerically, no counterexample.** About 4,500 SDP solves, N=2..48, ωtf up to 5.5, (r) and (r,v), Thm-B midpoint M, dent/face, rim, far, random, perpendicular-lateral and rate-saturated targets. Max (genuine − SDP)/scale² = 1.8e-7 (relative ≤ 8e-7). |
| Unit-d gimbal, inner discretization (d_k unit, within δ of b_k and b_{k+1}): [numerics] case 12 | **LOSSY, certified up to solver accuracy.** Case 12 reproduced: SDP 0.0275290, attained by an explicit R⁴ chain, vs best 3D 0.0282327 from about 1,070 runs incl. homotopy and basin hopping (2.5%). Order-2 Lasserre at N=3: Shor 1.862 < Las2 2.3587 (Clarabel) / 2.3571 (SCS) ≈ genuine 2.3569; δ=40°: 0.0237 < 0.1616 ≈ 0.1611. Small-N gaps are frequent (up to 95%). |
| CSD2′ (convexified lens ‖d_k‖ ≤ 1 = discrete relaxed controls, or δ=0) | **UNBROKEN.** All 509 unit-d gap instances have 0 gap after convexification (max 4.5e-10·scale²); case 12 gives 0.0273674 at rank 3. An adversarial screen at N=3..32 found 0 gaps. Stress matrix: PSD at every convexified/δ=0 optimum, negative at every unit-d gap (34/34). |
| Variable throttle, natural lift (U=a b) | **LOSSY, certified by Las2 at N=3.** It is not a discretization artifact: at fixed physics the gap grows with N, 12/40/54/63/68% at N=4/6/8/12/16, and the lift tends to the no-rate-limit value. |
| Other throttle lifts | (U,b)-Hilbert: lossy. Tightest (a,U,b) Shor: lossy (1%). **[proof-sdp] CSD3: lossy** (rank 3, gaps 2–36% at δ=0, even with ωtf=6). |
| Altitude r_z ≥ 0 (12 active scenarios), glide slope | exact (rank 1) whenever feasible. See report §7. |
| Min-fuel (throttle) | A linear (first-moment) landing constraint is feasible at the unreachable M, i.e. lossy (Thm D). A lifted landing constraint is infeasible at M (correct) but leaves small gaps at high rank. See report §7. |
| Thm B consistency | The SDP value at M is > 0 and equals the true dist²(M, L) on all 32 configurations (N ≤ 48). The state-linear version gives 0. The variance term is what makes it consistent with A/D. |

## Discrepancies with redteam-lift
- Their "CSD2 false in general (Π_4 ≠ Π_3)" applies only to the unit-d gimbal discretization. With δ=0 or the convexified lens there is no gap.
- "Throttle does not enter the dent" (a reachable-set statement) does not carry over to lifts: every degree-2 throttle lift is lossy.
