# Orchestrator log

- 2026-11-06: All 17 Propulsive-Landers-GT repos fast-forwarded. Workspace created.
- User decisions: survey several 5DOF models; Lean assumes PMP as a labeled hypothesis, everything else formal;
  install Lean+Mathlib; local git only; target whichever of 5/6DOF is most useful for our lander;
  keep iterating until there is a proof of possibility or impossibility.
- Decision: primary model = 5DOF (translation + thrust-axis pitch/yaw). Reason: GTPL lander has 15° TVC
  for pitch/yaw and separate RCS for roll; roll does not change thrust direction. 6DOF follows as corollary.
- Orchestrator sketch (math/00): impossibility of any *uniform* convex relaxation (Thm A + Thm B) via
  nonconvexity of the feasible boundary-condition set under attitude-rate limits and min throttle;
  plus positive Thm C (LCvx given an attitude profile). Launching agents to attack / make rigorous / formalize.
- User: also solve 6DOF after 5DOF (most useful). User approved launching remaining agents.
- Launched agents: lit-review, vehicle-context, adversary, proof, numerics, lean, positive. Lean 4 + Mathlib installed and building.
- User reprioritized: lossless question FIRST (possible vs impossible, fully proved + formalized); practical solver deferred
  (solver agent stopped). User wants adversarial attempts to make it POSSIBLE, not belief in impossibility.
- Added: comms/PROTOCOL.md, AGENTS.md (DM directory), CLAIMS.md (claim lifecycle → FORMALIZED), threads/.
- Launched: redteam-lift (relaxed controls / occupation measures / SDP lifts / conv-hull optimization),
  redteam-reform (LCvx-style reformulations, counterexamples to B), adversary-6dof (torque-coupled M3, 6DOF M4).
- Orchestrator concern flagged: in the real TVC vehicle gimbal angle = torque input, so M1's free gimbal is a relaxation;
  B6 (6DOF transfer) must be re-derived for M3, not assumed.
- Key threat to watch: occupation-measure LP relaxations (convex, value-exact under Vinter-type conditions) vs Claim A.
  Likely resolution: they are exact in VALUE but their feasible set in boundary data is the closure of the convexified
  reachable set, i.e. larger — so not lossless in the feasibility sense; but the definition of "lossless" must be stated carefully.
- User away ~8–9 h; full creative control. Keep-awake requested.
- vehicle-context DONE (context/vehicle.md). Key: vehicle is N2O/paraffin hybrid; ρ1/ρ2≈0.4; gimbal ±15° per axis (BOX);
  J_xx≈63.6 kg m² wet; lever 0.59 m; max pitch/yaw angular accel ≈1–3.5 rad/s² (torque-limited ⇒ M3 is the realistic model);
  usable rate 0.3–0.5 rad/s; tf≈7 s. Existing 3DOF LCvx solutions contain thrust-direction jumps needing ~10³ rad/s²
  (physically impossible) and are NOT tight at the min-thrust arc (296 N vs 400 N bound) — the 5DOF problem is real for us.
  MPC model mismatch (J, lever arm) ×4.6. Saved for the practical phase.
- lit-review interim: no prior 5DOF/6DOF LCvx claim and no impossibility result found; all 6DOF methods are SCP/indirect.
  Occupation-measure LPs: x0 enters as δ_{x0} (nonlinear in x0) ⇒ convex per instance, consistent with Thm A; Thm A must
  state joint convexity explicitly. (Orchestrator note: if μ0 is a decision variable with only its mean pinned to x0, the LP is
  jointly convex but its feasible x0-set is conv(F) ⇒ not lossless — consistent.) Bae et al. Automatica 2025: 3D Dubins
  reachable set = solid of revolution of 2D set (δ=0 special case of our R).
- 2026-11-07 ~00:15. adversary BREAK accepted: Claim B witness arcs start underground for GTPL (ρ1/(m0 g)=0.51) ⇒ vacuous
  with r_z ≥ 0. Fix B* (dive-then-brake exposed face) assigned. Loopholes found in Thm A scope: (i) relaxations exact only on F,
  (ii) symmetry-reduced relaxations. Orchestrator response: Theorem D (min-landing-error, per instance, state-linear relaxations)
  closes both — relaxed landing set convex ⊇ L ⇒ lossy at q ∈ conv(L)\L — needs no joint convexity in q.
  Key conceptual decision: the impossibility class = STATE-LINEAR relaxations (the LCvx paradigm: physical r,v are decision
  variables, appear linearly). Occupation-measure LPs (state lifted to Dirac measures) are convex and value-exact but outside this
  class — to be reported honestly as the boundary of impossibility.
- proof: ball-bound quantitative Thm B (no equality case) — easy Lean route for unconstrained version. numerics: B confirmed,
  ball bound within 18% of NLP. adversary-6dof: in torque-coupled M3, outward gimbal rotates body the other way ⇒ M1 arcs not
  realizable ⇒ B6 needs new proof. lit-review DONE: no prior 5/6DOF LCvx or impossibility; Berning et al. 2023 (Boeing) claims
  LCvx with tilt-rate limits (full text unavailable) — must reconcile.
- ~00:40. adversary on D: sound, but D ⇔ slice lemma S (now the crux). Shor-lift escape ⇒ class (d) sharpened, moment-lifted
  costs excluded explicitly. Orchestrator raised CONING threat to S (azimuth precession at fixed tilt cancels lateral motion);
  expected S provable for small ω·tf where planar single-crossing S-turns dominate (single-crossing ⇒ offset landing).
  Added TRIV: trivial exact convex reformulation always exists ⇒ the possibility question must be about tractable lifts.
- ~01:00. adversary-6dof BREAK: B6 false for pure-TVC M3 (outward gimbal rotates body inward; M1 arcs unrealizable). Fixes:
  Thm K (kinematic attitude), Thm D/D* (independent transverse torque, incl. terminal upright at rest). Pure TVC OPEN; numerics
  show nonconvexity but small gap at tf=1 s. Orchestrator: center-of-percussion (PVTOL flat output) reduction y=r+εb,
  ε=J_t/(mL)≈1.35 m: ÿ=(T cosμ/m−ε|ω|²)b−g exactly (verified, math/checks/flat_output_tvc.py) ⇒ pure TVC ≡ zero-gimbal
  angular-accel-limited model with affine boundary-data map; planar comparison lemma proves bottom-face nonconvexity.
  Sent to adversary-6dof + proof. Remaining: dive-then-brake with terminal upright for pure TVC.
- ~01:30. positive DONE: fixed-attitude LCvx exact (value+feasibility, Aumann); strong lossless under PMP + checkable non-degeneracy;
  per-instance exactness C-U (nonconvexity = choice of attitude); C-6: on real TVC, given b the problem is exactly convex;
  C-Y: 3DOF optimum exactly 6DOF-optimal for GTPL essentially never (initial-rate window ~3.5 µrad/s). Launched lean-positive
  (formalize math/05; PMP & Aumann only as explicit hypotheses) and possibility-rho0 (is LCvx possible when ρ1=0? dichotomy).
- ~01:45. redteam-reform DONE (math/redteam-reform.md): all LCvx-slack routes FAIL; chord-rate & orbitope lifts FAIL; B has no
  algebraic hole (scope hole fixed by B* w/ small s*); RR-LS line-search lemma written; pure-TVC exact class is measure-zero
  (b̈ = k(b−d) unstable, √k≈2–3 s⁻¹); ρ1=0: velocity set convex (theorem), full F OPEN (→ possibility-rho0).
