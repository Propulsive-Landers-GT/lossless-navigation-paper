# What can be published from this repository

Last updated 2026-11-11. This file lists every paper that exists or could be written from the work here, where it
lives, how solid its evidence is, and what it still needs. For the results themselves see `SYNTHESIS.md`.

## At a glance

| # | Paper | Where | Length | State |
|---|---|---|---|---|
| 0 | Comprehensive paper: every result in the repository | `paper/main.pdf` (internal), `paper/main-share.pdf` (shareable) | 50 pages | Written, revision 8. Not peer reviewed. |
| 1 | Lossless Convexification Is Impossible for Attitude-Rate-Limited Powered Descent | `paper/aiaa-student/impossibility/` | 10 pages, AIAA format | Written as a draft for the authors to take over. Standalone. |
| 2 | A Sound Single Convex Program for Powered-Descent Guidance of a Gimbaled Lander | `paper/aiaa-student/algorithm/` | 10 pages, AIAA format | Written as a draft for the authors to take over. Standalone. |
| 1+2 | Powered-Descent Guidance with Attitude Coupling: An Impossibility Theorem and a Sound Single Convex Program | `paper/aiaa-student/combined/` | 11 pages, AIAA format | Written as a draft. Standalone. The single-paper alternative to 1 and 2; do not enter it alongside them. |
| 3 | The LCvx thrust slack inside 6-DOF successive convexification | `scvx-thrust-relaxation/` (results and Lean proof); Section 4.7 of paper 0 | Not written as a paper | Candidate. The work is complete enough to write up. |

Papers 1, 2 and the combined paper do not cite each other or paper 0. Each cites only the public repository, for the Lean sources, the
certificates and the software.

## Paper 0: the comprehensive paper

- **Purpose.** The one document that holds everything: the impossibility theorems with full proofs, what is exactly
  convex, the semidefinite lifts, the numerical evidence, the planner study, the sound convex program with its proof
  (Section 4.5, Appendix E), the thrust slack inside successive convexification (Section 4.7), and the formalization.
- **Evidence.** Each statement carries a status tag: Lean-checked, proved, proved but not refereed, numerical, or open.
  `paper/CLAIMS-MAP.md` maps every statement to its proof and Lean name, and `paper/AUDIT.md` records what each
  revision changed and how it was checked.
- **Before it goes anywhere.** At 50 pages it fits a journal or a preprint server, not a conference. It should not be
  posted alongside papers 1 and 2 without deciding which is the version of record, because the three overlap.

## Paper 1: impossibility

- **Claim.** No convex program of the kind LCvx belongs to can be exact once the thrust direction is tied to a body
  that turns at a finite rate.
- **Evidence.** The strongest in the repository: machine-checked in Lean (126 declarations), read and attacked by an
  independent reviewer (`numerics/independent-check/`), who corrected one hypothesis and rebuilt the Lean project.
- **Honest limits, stated in the paper.** The proved gap is tiny for descents that begin in the air. For a vehicle
  steered only by its gimbal the result is certified at four final times under simplifying assumptions and is
  otherwise numerical.
- **Still needs.** The authors' own rewrite; a reader for the condensed proofs in this form.

## Paper 2: the landing algorithm

- **Claim.** A conservative single-SOCP planner for a specified gimbaled-lander model, with guarantees on thrust
  magnitude, gimbal angle and tilt that hold at every instant, fast enough to replan at the control rate.
- **What is new and what is not.** Flatness, splines and a single SOCP with continuous-time guarantees exist for
  quadcopters (Freire and Xu, 2023). New here are the convex restrictions for the gimbal-angle limit and for throttle
  limits with depleting mass on a vehicle that turns itself by deflecting its thrust, and their proof.
- **Evidence.** Proved on paper (`math/10-landing-proof.md`), tested numerically (27 tests, replays, a 600-solve stress
  test), benchmarked in simulation against successive convexification.
- **Honest limits, stated in the paper.** The soundness theorem has had no independent reader and is machine-checked
  only in its first step. Slew-rate limits are checked per plan, not guaranteed. Nothing has run on hardware. It is
  worse than successive convexification on hop fuel and on minimum flight time.
- **Still needs.** An independent check of the theorem, in the style of `numerics/independent-check/`; confirmation
  from measured mass properties that the center of percussion stays put; ideally hardware or flight data.

## The combined paper (1+2)

- **Claim.** Both of the above, as one argument: exactness is impossible, soundness is attainable, and here is the program.
- **Evidence and limits.** Those of papers 1 and 2. Its Limitations section states both sets.
- **Trade-off.** It is at the 11-page limit. Compared with the separate papers it omits the proof of the distance bound,
  the Lean and certificate tables, the vehicle schematic, the example plan and the open-loop table.
- **Sources.** Its program and soundness proof are taken from paper 2's source by a script, so the two stay identical.

## Paper 3 (candidate): the thrust slack inside successive convexification

- **Claim.** In 6-DOF successive convexification the lower thrust bound need not be linearized: the LCvx slack can be
  kept as exact convex constraints, and at a local minimum or a converged iterate the number of nodes where it is not
  tight is bounded.
- **Evidence.** Its own Lean project, interval-arithmetic rank certificates, and four solved cases with no lossy node.
  One case and two checks were re-run when the work was merged; the Lean project was built by its author only.
- **Why it is a separate paper.** It is about what survives inside the iterative method, not about replacing it, and
  it uses a different vehicle (the test case of Szmuk et al.). It complements paper 1 and does not depend on paper 2.
- **Still needs.** To be written, by or with its author; a comparison paragraph against the continuous-time result of
  Blackmore, Açıkmeşe and Carson (2012) and the discrete linear result of Luo, Echigo and Açıkmeşe (2026), both
  already discussed in the folder's README; a second build of its Lean project.

## Smaller pieces that could stand alone

These are in paper 0 and are not planned as papers; they are listed so they are not forgotten.

- The computer-assisted certificates for the gimbal-only vehicle (`math/06-pure-tvc.md`, `numerics/proof-tvc/`,
  `numerics/verify-tvc/`), with the open problems of a rate-limited certificate and longer final times.
- The semidefinite lifts and the CSD2' conjecture (`math/08-sdp-exactness.md`, `math/09-csd2-prime.md`).

## Before submitting anything to an AIAA student conference

`paper/aiaa-student/README.md` has the full list. The points that decide whether a submission is possible at all:

- **Eligibility.** The rules require the primary concept and a substantive portion of the work to be the students'
  own, and AIAA's policy limits AI in writing mainly to improving readability. Here an AI system derived the proofs,
  wrote the software, ran the experiments and drafted the text. Whether that can be entered is for the faculty advisor
  and the judging chair to decide. Each paper's Acknowledgments states the AI's role.
- **Authorship across two papers.** Outside the Team category a student may be a Contributing Student Author on one
  paper only.
- **Credit.** The independent check behind paper 1 and all of candidate paper 3 are another contributor's work.
