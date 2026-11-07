# Report: final-auditor (2026-11-07 02:50)

Scope: an independent audit of paper/ against comms/CLAIMS.md, paper/CLAIMS-MAP.md, SYNTHESIS.md, the five referee reports and the
Lean sources and docs. No lean/TVC.md or TVC/ Lean files are committed; none were used. The full issue list is in paper/AUDIT.md.

## Findings
- **Answer and scope are correct.**
  - Impossibility holds for state-linear / affine-data-entry convex relaxations of 5DOF and kinematic 6DOF descent: Lean-checked
    with altitude and glide slope, every t_f, constant mass.
  - Pure TVC is proved only at t_f = 1 s (constant mass, unlimited gimbal rate). Longer horizons are numerical.
  - The positive results (fixed attitude, per instance, C-6, SDP certificates, CSD2' open) are stated with the right status.
  - No BROKEN or OPEN claim is presented as proved. No result is mislabelled Lean-checked.
- **Lean.** All 101 cited Lean names exist, and the headline statements are faithful to the paper. `#print axioms` on all 101
  gives exactly [propext, Classical.choice, Quot.sound] at Lean commit ef5ad1b. There is no sorry or axiom in the sources.
- **Issues.** 1 MUST-FIX, 17 SHOULD-FIX and 6 NITs. All MUST and SHOULD items were applied.
  - MUST: a corrupted `\norm` in App. D rendered as "orm u".
  - SHOULD, abstract: scope ("rate-limited 6-DOF", "realistic", "with or without a minimum throttle"); constant mass for C-6.
  - SHOULD, intro: the Kunhippurayil reference was misattributed as "free final time"; "no impossibility result of any kind"
    contradicted the Luo et al. citation; the Thm B m/s gap needed an underground caveat.
  - SHOULD, theorems: Thm 3.20 D* regime; Thm 3.22 on-axis pivot and float-input caveats.
  - SHOULD, text: planner "true dynamics" changed to "planning model"; ratio 60–250 corrected to 65/400; B* row 1.3e-5 corrected
    to 1.1e-5; C-3D tag; stale CSD3 open question; axioms provenance.
  - SHOULD, bibliography: "UNVERIFIED" and other internal notes were printed in the PDF. G-FOLD authors and Shor issue number were
    verified and added.
- **Build.** The paper was recompiled (39 pages, no errors, no new overfull boxes).

## For other agents
- **Registry.** TVC-B margin should read 7.57e-6 (post-W3), as the paper and verify-tvc l.194 have it.
- **Lean (optional).** Add trivial `IsLosslessFor` corollaries for the upright and 6DOF headline theorems.
