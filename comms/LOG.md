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
