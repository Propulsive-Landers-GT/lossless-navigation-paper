# Agent directory
DM address = value for SendMessage `to:`. The orchestrator is `main`.

| Name | DM address | Role | Owns |
|---|---|---|---|
| orchestrator | main | Coordinates, decides, integrates, final paper | math/00, comms/LOG.md, CLAIMS.md structure |
| lit-review | a039637854af06161 (DONE) | Literature deep research | literature/ |
| vehicle-context | abdf90416c1aaeb23 (DONE) | GTPL vehicle parameters | context/ |
| adversary | ac6fe7796e3cdced3 (DONE) | Attack 5DOF proof + definitions of lossless | math/01-adversary-report.md |
| adversary-6dof | ad0b31b3fb8ad5d4e | Attack torque-coupled (M3) and 6DOF (M4) extensions | math/adversary-6dof-report.md |
| proof | a51bef97d1e1b50bb (DONE) | Rigorous proofs + Lean blueprint | math/02, math/03 |
| lean | a10df47e8217a3091 (DONE) | Lean 4 formalization (impossibility) | lean/ |
| numerics | ae8a82476e9301937 (DONE) | Numerical confirmation/refutation, test candidates | numerics/ |
| positive | a36be30f2acce31b5 (DONE) | Possibility theory: fixed-attitude LCvx, exact subclasses | math/04, math/05 |
| redteam-lift | a574fe3d602d3e65c (DONE) | Make LCvx work via lifting/relaxed controls/occupation measures | math/redteam-lift.md |
| redteam-reform | a6585a8a748ed0c83 (DONE) | Make LCvx work via reformulation; hunt counterexamples to Claim B | math/redteam-reform.md |
| lean-positive | a1021d973096b337d (DONE) | Lean formalization of positive results (PMP as explicit hypothesis) | lean/LcvxObstruction/LcvxObstruction/Positive/ |
| possibility-rho0 | a792931e985b589b0 (DONE) | Is 5DOF LCvx possible when min throttle ρ1=0? (sharp dichotomy) | math/possibility-rho0.md |
| proof-tvc | a237537bb0f864d13 (DONE) | Pure-TVC (real GTPL 6DOF) nonconvexity: upright at rest, r_z≥0 | math/06-pure-tvc.md |
| proof-s | a8a27205fe1b681a6 (DONE) | Prove slice Lemma S (per-instance min-landing-error impossibility, hard v(tf)=0) | math/07-lemma-S.md |
| verifier-sdp | a1cc9c46da966f49c (DONE) | Independent numerical attempt to break SDP-lift exactness (CSD2) | numerics/verifier-sdp/, math/verifier-sdp-report.md |
| proof-sdp | ae94d2bcd8785d34a (DONE) | Prove/disprove CSD2 (degree-2 Shor lift exact for fixed-thrust 5DOF min-landing-error), extend to throttle | math/08-sdp-exactness.md |
| lean-s | a40abab87ad7b4bb3 (DONE) | Lean: A-opt/Prop T, Wirtinger lemma, Lemma S, Thm D w/ penalty | lean/LcvxObstruction/LcvxObstruction/Slice/ |
| paper-writer | a41a31397861a8637 (DONE, draft) | LaTeX paper draft from SYNTHESIS + proofs; only proven/formalized claims | paper/ |
| verify-imp | afee825a20ce8c68e (DONE) | Referee impossibility-side CLAIMED rows (Q, B*, D, S, A-opt, P0-*) | math/verify-imp-report.md |
| verify-pos6 | ab5886d8970d683d2 (DONE) | Referee 6DOF, positive, SDP CLAIMED rows | math/verify-pos6-report.md |
| proof-csd2p | a913db127233c94a0 (DONE) | Prove refined SDP conjecture CSD2′ (convexified lens, continuous time) | math/09-csd2-prime.md |
| verify-tvc | ae6c370b5cd20db43 (DONE) | Audit pure-TVC computer-assisted proof, exact-arithmetic re-check | math/verify-tvc-report.md |
| verify-sdp2 | ac7006c94fa6b776a (DONE) | Referee math/09 (CSD2′ partial proof) | math/verify-sdp2-report.md |
| lean-n | a7b44976cb8dca63a (DONE) | Lean: solver claims N1–N7 (gimbal box, rate bounds, chord, gyro, 3DOF lower bound) | lean/…/Solver/, lean/SOLVER.md |
| lean-tvc | a7f04cecd56f668ff (DONE) | Lean: centre-of-percussion identity, TVC-1 skeleton (certificate as explicit hypothesis), B* with mass depletion | lean/…/TVC/, lean/TVC.md |
| final-auditor | ad5ce73a9500d2594 (DONE) | Independent audit of paper vs registry vs Lean; applies fixes | paper/AUDIT.md |
| solver-v2 | aa3239f000bdac159 (DONE) | Practical deliverable: simplest certifiably-feasible landing algorithm (attitude outer loop + exact convex inner) + 6DOF closed loop | solver/ |
