# Report: [proof-csd2p] — Conjecture CSD2′ (convexified-lens Shor lift, fixed-thrust 5DOF min-landing-error)

Date: 2026-11-07 (system clock). Main document: math/09-csd2-prime.md. Scripts: numerics/proof-csd2p/.

## Verdict
**CSD2′ is not fully proved and not broken.** I found no counterexample. The conjecture is reduced to a residual integer equality (Conjecture CSD2″) on a thin class of genuine optima. Everything else is proved.

## Proved
- **T1 (alignment).** The lifted optimum can be rotated so its terminal (r,v) lies in ℝ³. So CSD2′ for all targets ⇔ R_X ∩ E² = R_3: every lifted trajectory that lands in ℝ³ has a 3D twin with the same terminal state.
- **T2 (primer-plane fold).** The lift is exact for every **linear** objective, in all models, unit-d included. The fold is onto span(primer plane, normal containing e_z) and fixes e_z. This closes the open part of SDP-F.
- **T3 (continuous-time stress).** Under (H), the KKT form of the normal PMP, the scalar stress Q certifies global optimality in every Hilbert space when PSD. Its Jacobi form is J_red = ∫ν(η̇² − ‖ḃ‖²η²) + ∫κη², with gimbal curvature κ = ‖P‖ sin(θ−δ)⁺ cot θ.
- **T4 (hemisphere / Picone).** The lift is exact at w if some genuine optimum has a vector c with ⟨b*(t),c⟩ > 0, ⟨P(t),c⟩ ≥ 0 and ⟨e_z,c⟩ ≥ 0. Special cases:
  - the attitude never crosses the primer plane;
  - **a priori**: vertical-shortfall targets ("cannot brake in time") with ωtf < π.
  - The discrete D^cvx/D^0 version is fully rigorous. **It uses μ_d ≥ 0, which is exactly what the convexified lens provides.**
- **T5 (index identity).** At any genuine KKT point, neg(Q) = neg(Z) − p₀(C_yw), with Sturm bounds k−1 ≤ neg(Z) ≤ k (k = primer-plane crossings, via the Jacobi field ⟨b,m⟩). Consequences:
  - k ≤ p₀ ⇒ exact;
  - k ≥ p₀+2 ⇒ the genuine point is beaten in ℝ⁴;
  - k = p₀+1 ⇒ open; this is the residual class (terminal attitude: k=2, C_yw indefinite).
  - Proved in discrete time under nondegeneracy; continuous-time analogue sketched.
- **P6.** Free singular (throttle-down) arcs cannot occur at genuine continuous-time optima, because the 3D tilt into the primer-plane normal improves them. So the case-12 mechanism has no continuous-time analogue.
- **P7.** Unit-d failure = a negative norm multiplier (the segment "wants to throttle") plus the E⊥ tilt. The convexified lens forces μ ≥ 0.
- **§7, physical meaning.** The exact 3D optimum has a genuine rate-limited attitude and relaxed thrust. Aumann/Lyapunov gives a genuine bang-bang gimbal selection with the **same** terminal state exactly. Filippov–Ważewski gives a uniform approximation of the whole history.

## Numerics
- **Large ωtf (π to 3π) screen**: 384 targets (d=b, cvx15, cvx40; terminal and free attitude), **0 gaps**.
- **Index identity**: holds on all 151 nondegenerate bank instances. The Sturm bounds hold on all 107 instances where h_m ≠ 0 at every node. Of those 107, 91 (85%) are in the certified class k ≤ p₀, and the 16 in the residual class are all exact with neg Z = k−1. No optimum has k ≥ p₀+2. The apparent violations all break T5's hypotheses (attitude running inside the primer plane, or a singular, disconnected Z).
- **[numerics] c1 cases**: 16/17 certified by T5, including 9/10 GTPL-realistic (set A) and case 12 convexified.
- **Unit-d gaps**: 13/13 checked have μ_d < 0 and Q ≱ 0. Their convexified versions have μ_d ≥ 0 and Q ⪰ 0.

## Open
- **CSD2″**: neg(Z) = k−1 at k = p₀+1 optima, i.e. no conjugate point in the last lobe of the principal Jacobi solution.
- Continuous-time rigour of T5 (Sturm–Liouville with possibly degenerate ν).
- Glide-slope / altitude multipliers in Z.
- Variable throttle (the natural lift is lossy, V-THR).

## Files
- math/09-csd2-prime.md
- math/03 section "CSD2′" (CP-1…CP-12)
- CLAIMS rows CSD2′-T1…T5, CSD2″, CSD2′-P6, CSD2′-P7 (CSD2′ status updated)
- numerics/proof-csd2p/
