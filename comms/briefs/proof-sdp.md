# Brief: PROOF-SDP (saved verbatim-in-substance by proof-sdp, 2026-11-06)

Role: research mathematician agent (convex algebraic geometry / SDP rank / optimal control).
Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research.

Read: comms/PROTOCOL.md (compute budget: <=2 heavy processes, single-threaded BLAS), comms/AGENTS.md,
comms/BOARD.md (redteam-lift posts, esp. "02:10 FIX"), comms/CLAIMS.md (L-SD2, OM, D, TRIV),
math/redteam-lift.md (§3.2 "Hilbert-sphere" lemma, Pi_n = Pi_3 planarization route),
comms/threads/possibility.md, math/02-impossibility-rigorous.md (Theorem D, state-linear class).

Claim (Conjecture CSD2, numerically supported by [redteam-lift]; [verifier-sdp] checking numerics concurrently):
for fixed-thrust 5DOF min-landing-error (body axis b on S^2, rate-limited, thrust along b with fixed
magnitude profile, linear dynamics so final state = linear functional of b(.); cost = squared distance of
final state to a target), the degree-2 Shor lift is exact. The lift is equivalent to the same control problem
with b(t) on the unit sphere of a Hilbert space (any dimension), gravity fixed in a 3D subspace.
Exactness <=> lifted problem always has an optimal solution living in 3 dimensions (Pi_n = Pi_3).

Goal: PROVE or DISPROVE CSD2 in continuous and/or discrete time.
Ideas: (1) folding map b -> (b.e_z, b.e, ||P_perp b||) and whether it preserves the rate constraint;
(2) PMP in the lifted problem, extremals in a fixed 3D subspace; (3) Pataki/Barvinok rank bounds for
path-structured SDPs; (4) counterexamples needing >= 4 dimensions (full (r,v) targets).
Then: extension to VARIABLE throttle; gimbal cone, glide slope, min-fuel.
Position honestly vs Theorem D (state-linear class; moment cost) and Thm A (data q only in objective).
State precisely what it does / does not give.

Deliverables: math/08-sdp-exactness.md; register claims; post DISCOVERY/BREAK on BOARD; message main with
verdict; append Lean-ready lemma list to math/03-lean-blueprint.md ("SDP exactness") if something proved;
coordinate with [verifier-sdp] (BOARD until DM address exists); comms/reports/proof-sdp.md; return verdict.
