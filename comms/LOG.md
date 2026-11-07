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
