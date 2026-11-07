# Report: [proof-sdp] — exactness of the degree-2 Shor / Hilbert-sphere lift (Conjecture CSD2)

Details: math/08-sdp-exactness.md. Scripts: numerics/proof-sdp/. Claims: SDP-T1, SDP-T4, SDP-P, SDP-F, SDP-R4, SDP-L, CSD2′, V-THR (CLAIMS.md). Lean list: math/03 "SDP exactness" (SE-1…SE-8).

## Verdict
1. **CSD2 as stated (unit-d inner discretization, δ>0) is FALSE (numerical).** [numerics] case 12 gives SDP 0.02753 vs 3D 0.02823. [verifier-sdp] built an explicit ℝ⁴ chain, and I reproduced both numbers. This is not a certificate, since the 3D optimum comes from an NLP. §6.4 gives an N=3 construction for an order-2-Lasserre certificate.
2. **The cause is discrete non-chattering, not attitude planarization.** The lift's d_k projects onto conv(lens) (Prop 6.1), so a segment can throttle below a1 by tilting d into E⊥ at no rate cost. Continuous-time controls get the same effect by chattering. With the convexified lens (‖d_k‖≤1), case 12 is EXACT: SDP_cvx = genuine_cvx = 0.0273676 < SDP_unit 0.0275324 < genuine_unit 0.0282320. The same holds at its coplanar variant and at all 15 c1 cases where my convexified NLP converged.
3. **Refined Conjecture CSD2′ is OPEN:** exact for the convexified lens, the δ=0 chain, and continuous time. There is no counterexample, and it agrees with [verifier-sdp]'s 840 δ=0 instances.
4. **Proved:**
   - Thm 2.1 (stress certificate): exact ⇔ PSD stress at a genuine optimum. Q≻0 ⇒ unique rank-3 optimum.
   - Thm 2.4: exact ⇔ a genuine optimum is a local min of the ℝ⁴ problem, and local ⇒ global.
   - Thm 4.1: coplanar data with a planar LICQ local min ⇒ certified global optimum, with glide slope / altitude constraints allowed.
   - Cor 3.3: coplanar support functions are exact (folding).
   - Prop 5.1: rate-saturated ⇒ rank ≤ 4.
   - Remark 3.4: Brouwer rules out pointwise planarization.
5. **Variable throttle:** the natural lift is lossy ([verifier-sdp], 40% gap when the rate binds). I give the mechanism. A separate-axis LCvx lift (CSD3) is proposed and untested. **No min-fuel result.**

## Honest "possible" statement
For fixed-thrust 5DOF min-landing-error, a polynomial-size SDP gives a rigorous lower bound, and an infeasibility certificate when the bound is > 0. The data enter only the objective, which puts it outside Theorem D's state-linear class (it is a second-moment cost) and outside Theorem A's scope. Exactness is certified a posteriori by a rank-3 SDP optimum or by the stress test (stress.py). It is certified a priori for coplanar data with a planar optimum. A uniform exactness theorem is not proved.

## Follow-ups
- Certify the unit-d break at N=3 with Lasserre-2 ([verifier-sdp]).
- Prove CSD2′, i.e. ηᵀQ_λη ≥ 0 at genuine optima of D^cvx / D^0. A path-wise or PMP route is required (Remark 3.4).
- Test CSD3 (separate-axis lift) for variable throttle.
