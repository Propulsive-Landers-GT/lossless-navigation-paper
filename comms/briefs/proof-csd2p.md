# Brief: PROOF-CSD2P (saved by proof-csd2p, 2026-11-07)

Role: research mathematician (optimal control on manifolds, PMP in Hilbert spaces, SDP rank theory).
Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research.

Read: comms/PROTOCOL.md (compute budget: <=2 heavy processes, single-threaded BLAS), comms/AGENTS.md,
comms/BOARD.md (posts by [redteam-lift], [numerics], [verifier-sdp], [proof-sdp]), comms/CLAIMS.md (L-SD2, CSD2', SDP-*),
math/08-sdp-exactness.md (Thm 2.1 PSD stress, Thm 2.4 local-in-R^4 <=> exact, Thm 4.1 coplanar subclass,
Prop 5.1 rank <= 4, Prop 6.1 discretization mechanism, Remark 3.4 Brouwer obstruction to pointwise planarization),
math/redteam-lift.md §3 (Hilbert-sphere lemma).

Conjecture CSD2' (numerical support: [verifier-sdp] 0 gaps on 509 former unit-d gap instances after convexifying
the gimbal lens; 0 gaps on adversarial screens N=3..8): for FIXED-THRUST 5DOF min-landing-error — thrust magnitude
profile given, thrust direction d(t) in the convexified gimbal lens (||d|| <= 1, <d,b> >= ..., relaxed/chattering
controls), body axis b(t) on S^2 with full-direction rate limit omega, b(0)=b(tf)=e_z (also free b(tf)), linear
dynamics with gravity, cost ||(r,v)(tf) - q||^2 — the degree-2 Shor lift (equivalently the problem on the unit
sphere of a Hilbert space with gravity in a fixed 3D subspace E) is EXACT in continuous time (and in the
convexified-lens discretization).

Goal: PROVE CSD2' (continuous time first; then discretization), or find a counterexample.
Suggested route: PMP for the lifted problem on the Hilbert sphere; costates lambda_r const, lambda_v affine,
lambda = 2((r,v)(tf) - q); show E-perp component of terminal state vanishes at optimum or optimal b can be taken
in E. Use (i) convexity in d given b (C-W, Lyapunov-Aumann), (ii) maximization condition (b moves toward primer,
bdot in span(b,p) off singular), (iii) singular arcs separately, (iv) Thm 2.4 + second-order argument that a 3D
extremal with the convexified lens has PSD stress (Thm 2.1). Remark 3.4: no POINTWISE folding works -> proof must
be path-level. Explain why unit-d discretization fails (Prop 6.1) but chattering fixes it. Clarify physical meaning
of "exact" (relaxed gimbal controls approximable by genuine ones; closure).

Coordinate with [verifier-sdp] (DM a1cc9c46da966f49c). Deliverables: math/09-csd2-prime.md, CLAIMS rows,
BOARD DISCOVERY/BREAK, message main with verdict, Lean-ready lemma list appended to math/03 ("CSD2'"),
comms/reports/proof-csd2p.md. Return the verdict.
