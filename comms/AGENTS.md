# Agent directory
DM address = value for SendMessage `to:`. The orchestrator is `main`.

| Name | DM address | Role | Owns |
|---|---|---|---|
| orchestrator | main | Coordinates, decides, integrates, final paper | math/00, comms/LOG.md, CLAIMS.md structure |
| lit-review | a039637854af06161 (DONE) | Literature deep research | literature/ |
| vehicle-context | abdf90416c1aaeb23 (DONE) | GTPL vehicle parameters | context/ |
| adversary | ac6fe7796e3cdced3 | Attack 5DOF proof + definitions of lossless | math/01-adversary-report.md |
| adversary-6dof | ad0b31b3fb8ad5d4e | Attack torque-coupled (M3) and 6DOF (M4) extensions | math/adversary-6dof-report.md |
| proof | a51bef97d1e1b50bb (DONE) | Rigorous proofs + Lean blueprint | math/02, math/03 |
| lean | a10df47e8217a3091 | Lean 4 formalization (impossibility) | lean/ |
| numerics | ae8a82476e9301937 | Numerical confirmation/refutation, test candidates | numerics/ |
| positive | a36be30f2acce31b5 (DONE) | Possibility theory: fixed-attitude LCvx, exact subclasses | math/04, math/05 |
| redteam-lift | a574fe3d602d3e65c | Make LCvx work via lifting/relaxed controls/occupation measures | math/redteam-lift.md |
| redteam-reform | a6585a8a748ed0c83 (DONE) | Make LCvx work via reformulation; hunt counterexamples to Claim B | math/redteam-reform.md |
| lean-positive | a1021d973096b337d | Lean formalization of positive results (PMP as explicit hypothesis) | lean/LcvxObstruction/LcvxObstruction/Positive/ |
| possibility-rho0 | a792931e985b589b0 | Is 5DOF LCvx possible when min throttle ρ1=0? (sharp dichotomy) | math/possibility-rho0.md |
| proof-tvc | a237537bb0f864d13 | Pure-TVC (real GTPL 6DOF) nonconvexity: upright at rest, r_z≥0 | math/06-pure-tvc.md |
| solver | (paused) | Practical landing algorithm — deferred until lossless question settled | solver/ |
