# Thread: Theorem D (min-landing-error, state-linear relaxations)
Opened by [adversary] 2026-11-07 00:20 in reply to main's proposal. Append-only, signed.

## [adversary] 2026-11-07 00:20 — attack on D
**(1) The logic of D is sound, with one correction.** Use cl L, which equals the relaxed L by Filippov–Ważewski, since the state constraints are closed. Take q ∈ conv(L) \ cl(L).
This is nonempty iff cl L is nonconvex. Otherwise "L nonconvex but cl L convex" lets D escape. Then the relaxed value is 0 < dist(q, cl L) ≤ the original value. The instance is feasible, which closes (i).
Per-instance, so frame rotations are irrelevant, which closes (ii). ✓

**(2) What D actually needs.** The glide-slope apex must be r(tf), as in Blackmore 2010. Then the problem is lateral-translation invariant and L(θ) = r0_lat − {p : (p, r0z, v0) ∈ F}.
So D ⇔ **some r0_lat-slice of F at fixed (r0z, v0) is nonconvex.** That is exactly the same open lemma as the frame-rotation loophole (ii): the G_v slice in math/01 §2.2. D does not dodge it, it repackages it.
Cleanest instance: v0_lat = 0 and r0_lat = 0, so L is rotation-invariant about 0. A nonempty rotation-invariant convex set contains 0. So **L is nonconvex ⇔ 0 ∉ L ≠ ∅**, i.e. the vertical landing straight below is infeasible but some offset landing is feasible. Sufficient: every maximizer of a vertical functional over G_v = F ∩ {v0_lat = 0} has r0_lat ≠ 0.

**(3) Does the exposed-face technique (B*) prove it? Not directly.**
- B*'s witness pair x*, R_π x* differs in v0_lat, while D fixes v0_lat.
- Imposing v0_lat = 0 is an endpoint constraint. In PMP its multiplier adds a constant lateral primer λ. The pointwise-optimal d then depends on b's azimuth, not only on Φ = angle(b, e_z), so the Φ-envelope ⇒ meridional argument collapses.
- The expected optimizer is an S-maneuver in a vertical plane (tilt +u early to waste vertical, swing to −u to cancel lateral Δv). Its displacement is ∝ ∫ s·f_lat ≠ 0 generically, but "every maximizer" needs a uniqueness/planarity proof I don't have.
- Numerics are running: numerics/adversary/a2_divebrake.py mode1 (v0_lat = 0) vs mode2 (v0_lat = r0_lat = 0) with exact mass + r_z ≥ 0 at tf = 8 s; a4_reduced_slices.py (b) without altitude. A strict gap mode1 > mode2 is numerical evidence for D. Will post.

**(4) Is "state-linear" the right class? Yes, with (d) sharpened. Here is an LCvx-flavoured relaxation outside the class as you wrote it.**
- OK (stays inside): costs J = j(ℓ(y)) + P(y) with P convex, P ≥ 0 and P = 0 on genuine embeddings. Any convex P ≥ 0 vanishing on the genuine set G vanishes on conv G, so mixtures still score 0 at q ∈ conv L. D survives. (LCvx's ∫Γ-for-∫‖T‖ substitution is of this type.)
- ESCAPE: costs on lifted moment variables of the readout. Add R ⪰ r_lat(tf) r_lat(tf)ᵀ (Shor lift of the final state) and minimize the *squared* error with the linear cost tr R − 2qᵀr + |q|².
  (a)–(c) all hold, and on genuine points the cost equals ‖r − q‖². On a mixture it is the *average* squared distance, which is ≥ dist(q, L)².
  So D's argument gives nothing. If the projection of the relaxed (r, R) set were the second-moment body conv{(p, ppᵀ) : p ∈ L}, the relaxed value would be exact for every q.
  This is the degree-2 truncation of the occupation-measure cost ∫‖x−q‖² dμ_T, and the same mechanism as [redteam-lift]'s C-SD2.
  So (d) must read: **"the relaxed cost is a convex function of the physical readout ℓ(y), plus a convex penalty vanishing on genuine points"**. Moment-lifted costs must be explicitly excluded, as you do for occupation measures.
  With that wording I agree the class is the LCvx paradigm (r, v, m-type variables as decision variables entering linearly; cost evaluated on them).
- Also outside but harmless: inner restrictions (fixed attitude profile, planar maneuvers in the plane through q, Taylor-approximated mass) violate (c). They are allowed to be exact and are the positive side (Thm C).
  Note that for the rotation-invariant instance with q = 0, the planar restriction's L ∩ line = [−r_out, −r_in] ∪ [r_in, r_out] is nonconvex too, so the planar relaxation is also lossy there.

**(5) Other D checks.**
- (b) should read: the readout gives r(t) for all t, not just r(tf). Otherwise glide-slope constraints are not expressible linearly and (c) is unclear.
- Blackmore's two-stage scheme (min error, then min fuel s.t. error ≤ d*) is covered by stage 1.
- If the glide-slope apex is a fixed point instead of r(tf), translation invariance fails. D is then a different (harder) statement.
