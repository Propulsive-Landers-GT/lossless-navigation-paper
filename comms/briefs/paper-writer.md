# Brief: PAPER-WRITER

Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research.

Read: SYNTHESIS.md (backbone), comms/CLAIMS.md, comms/LOG.md, comms/PROTOCOL.md, math/00 … math/08, math/redteam-*.md, math/possibility-rho0.md, math/adversary-6dof-report.md, math/01-adversary-report.md, lean/MODEL.md, literature/review.md, literature/refs.bib, context/vehicle.md, numerics/README.md (plots in numerics/results/).

Write a research paper draft in paper/ (LaTeX, AIAA-style or clean article class; main.tex + sections/*.tex + refs.bib curated from literature/refs.bib; figures copied into paper/figures/ from numerics/results/). Authors: placeholder "Propulsive Landers at Georgia Tech". Working title along the lines of "On the Impossibility of Lossless Convexification for Attitude-Constrained (5-DOF/6-DOF) Powered Descent" — choose the best accurate title.

Content (rigorous and honest; will be scrutinized):
1. Introduction: LCvx background (Açıkmeşe–Ploen 2007, Açıkmeşe–Carson–Blackmore 2013, etc.), why 5DOF/6DOF matters, contribution summary.
2. Problem formulation: model catalog (M1 kinematic rate-limited axis + gimbal cone; pure TVC rigid body; 6DOF), boundary data, definitions: uniform/state-linear convex relaxation, affine (or separable-monotone) data entry, lossless (feasibility/detection-sound; optimization form), why these capture LCvx and what they exclude (occupation measures/moment lifts, nonaffine data entry — trivial convex-hull reformulation remark).
3. Main impossibility results: Theorem A, Theorem B + ball bound Q, Theorem B* (dive-then-brake, altitude/glide slope, any tf, free-tf window, RR-LS line search), Theorem D + Lemma S (Wirtinger), Theorem A-opt/Prop T, rho1 = 0 results (P0-R, P0-F), 6DOF transfers, pure-TVC via centre-of-percussion (actual scope). Full proofs/sketches; long proofs in appendices adapted from math/02, math/07, etc.
4. What IS possible: Theorem C (C-W, C-S under PMP), C-U, C-6, X5, SDP lifts (degree-2 lossy with gimbal in unit-d discretization and with variable throttle, certified at N=3; CSD2' open; Thm 4.1 coplanar subclass; certificates).
5. Numerical evidence: gap laws, beyond-regime, GTPL-specific results, figures.
6. Machine-checked formalization: Lean 4/Mathlib names, scope, #print axioms, PMP-as-hypothesis convention, faithfulness mapping. Only claim what compiles (ask [lean] via DM a10df47e8217a3091 if unsure, or `source ~/.elan/env && cd lean/LcvxObstruction && lake env lean <file>`).
7. Discussion: guidance design implications, open problems (pure TVC upright landing, GTPL-constant rigor, CSD2', min-fuel value-losslessness, long horizons/coning).

Rules: every theorem stated must correspond to a CLAIMS row with status PROVED/CONFIRMED/FORMALIZED; label numerical-only results as such. Mark each theorem in a comment with CLAIMS ID and Lean name. Keep paper/CLAIMS-MAP.md (paper theorem -> CLAIMS ID -> status -> proof file -> Lean name). In-progress results (proof-tvc pure-TVC upright case, Lean B*/Lemma S, CSD2') as clearly marked TODO boxes. Compile with latexmk/pdflatex+bibtex if available; don't install anything large. Commit paper/ files (no AI attribution trailers). Post a BOARD STATUS when the draft exists. Write comms/reports/paper-writer.md. Return a summary with paper structure and any claim unable to support.
