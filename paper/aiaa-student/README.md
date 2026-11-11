# Papers for the AIAA Regional Student Conferences

Three papers written to the rules of the AIAA Regional Student Conferences. **Enter either the combined paper or the two
separate ones, not all three:** the combined paper overlaps both of the others almost entirely.

| Folder | Title | Pages | What it claims |
|---|---|---|---|
| `impossibility/` | Lossless Convexification Is Impossible for Attitude-Rate-Limited Powered Descent | 10 | No convex program of the kind LCvx belongs to can be exact once the thrust direction is tied to a body that turns at a finite rate. Proved, and machine-checked in Lean. |
| `algorithm/` | A Sound Single Convex Program for Powered-Descent Guidance of a Gimbaled Lander | 10 | A single convex program that returns only flyable trajectories for a gimbaled lander, with its proof and a benchmark against successive convexification. |
| `combined/` | Powered-Descent Guidance with Attitude Coupling: An Impossibility Theorem and a Sound Single Convex Program | 11 | Both results in one paper: the impossibility theorem with its proof, then the sound convex program with its proof and the closed-loop benchmark. |

All are short versions of the comprehensive paper `../main.pdf` (50 pages). **Each is standalone:** none cites another
or the comprehensive paper, and each carries the proofs and context it needs. The only project reference in either is
the public repository, cited for the Lean sources, the certificates and the software. `aiaa-format.tex` is the page
format they share.

**They are drafts for the authors to take over, not finished submissions.** Read "Before you submit" below first.

## One paper or two

- **`combined/`** tells the whole story in one place: exactness is impossible, soundness is not, and here is the sound
  program. It is exactly at the 11-page limit, so anything added must displace something. To fit, it gives the proof of
  the nonconvexity theorem in five compact steps, states the distance bound without its proof, summarizes the Lean
  formalization in a paragraph instead of a table, drops the vehicle schematic and the example plan, and reports the
  open-loop results in prose. The convex program, the soundness theorem and its five-step proof are complete.
- **`impossibility/` and `algorithm/`** have room for more (10 pages each): the proof of the distance bound, the table of
  Lean declarations, the certificate table, the example plan, the open-loop table.
- `combined/main.tex` is generated. Edit `combined/front.tex` and `combined/back.tex` for the impossibility half, the
  results and the conclusion; the model, the program and the soundness proof are taken from `algorithm/main.tex` by
  `combined/assemble.py`, so those cannot drift apart between the two papers. In the combined paper the thrust per unit
  mass is `τ` and the horizontal unit vector is `n`, to avoid clashing with the algorithm's symbols.

## Why two papers, and how they fit together

- **They are different kinds of result.** The first is a theorem about every possible reformulation. The second is a
  method for one class of vehicle. They have different readers and are judged on different evidence.
- **They are at different levels of maturity.** The impossibility theorem is machine-checked and has had an independent
  reader (`../../numerics/independent-check/`). The soundness theorem of the algorithm has had no reader but its author
  and is machine-checked only in its first step. Keeping them apart stops the weaker result setting the credibility of both.
- **They do not contradict each other, and each says so.** The first proves that no convex program is *exact* (feasible
  at exactly the landings that exist). The second gives a program that is *sound but not exact*: everything it returns is
  flyable, and it rejects some landings that exist. Do not describe the second as "convexifying" the problem.
- **Neither depends on the other.** The impossibility paper outlines the sound program in one paragraph (Sec. IX); the
  algorithm paper gives the dive-then-brake argument for nonconvexity in full (Sec. IV). The center-of-percussion
  identity appears in both. A reader, or a judge, needs only the paper in hand.
- **What each proves inside its page limit.** `impossibility/`: Theorems 1 and 2 with complete proofs, the proof of the
  distance bound, the derivation of the closed-form gap, and the method of the gimbal-only certificates (the
  certificates themselves are computer-assisted and live in the repository). `algorithm/`: the flat map, the convex
  program, the soundness theorem with its five-step proof, and the incompleteness proposition.

Where the long paper's sections went:

| Long paper | Goes to |
|---|---|
| Sections 2 and 3 (models, definitions, Theorems A and B*, extensions, pure thrust-vector control) | `impossibility/`, with the full proofs of Theorems A and B* |
| Section 5 (numerical evidence) | `impossibility/`, two examples only |
| Section 7 (Lean formalization) | `impossibility/`, one section and a table |
| Section 4.5 and Appendix E (the sound convex program and its proof) | `algorithm/` |
| Section 6 (planner comparison, closed loop) | `algorithm/` |
| Section 4.1 to 4.4 and 4.6 (exactness for a fixed attitude, exact subclasses, semidefinite lifts), Section 4.7 (the thrust slack inside successive convexification), the certificates behind the pure-TVC table | Stay in the comprehensive paper only |

## Who can be an author on which paper

The rules limit this, so decide before you edit the title blocks:

- In the High School, Undergraduate and Graduate categories a student may be a Contributing Student Author on **one**
  paper only. Two papers in those categories need two different sets of students (at most two students per paper).
- In the Team category (three or more students, at least half undergraduates) a student may be on more than one paper.
- Individuals or teams presenting more than one paper cannot win more than one award.
- A paper cannot be entered if it has been presented at another conference or accepted for publication.

## The rules it was written to

From the AIAA Regional Student Conference Rules (version dated June 2026) and AIAA's manuscript instructions:

| Rule | Status here |
|---|---|
| At most 11 pages, single column, 8.5 x 11 in, including acknowledgments, references and appendices | 10, 10 and 11 pages |
| AIAA Meeting Paper format ("Use the Word Template"); deviations may disqualify | Format reproduced in LaTeX from the published instructions (see "Format" below). **Not built from AIAA's own template file.** |
| Every author identified in the first-page footnote by status, role (Contributing Student Author or Mentor Author) and AIAA membership | Placeholders in brackets |
| Undergraduate and Graduate categories: at most two Contributing Student Authors. Team category: three or more, at least half undergraduates. Up to two Mentor Authors, listed after the students. No industry co-authors | Two student placeholders and one mentor placeholder in each paper; edit to your category |
| A student is a Contributing Student Author on one paper only, except in the Team category | See "Who can be an author on which paper" |
| Not presented at another society's or region's conference, and not accepted for publication | For you to confirm |
| Must follow the AIAA policy on the use of artificial intelligence | **See "Before you submit"** |
| Abstract: one paragraph, no citations, symbols defined | Done |
| Figures: no background or border, caption below, axis labels in words with units after a comma, text at least 8 pt | Done |
| Tables: title above. References numbered in order of citation, all authors listed | Done |

Sources: [Regional Student Conference rules (PDF)](https://aiaa.org/wp-content/uploads/2025/03/regional-student-conference-rules_June-2026Final_.pdf),
[AIAA technical presenter resources](https://aviation.aiaa.org/call-for-content/technical-presenter-resources/),
[AIAA LaTeX template for technical conferences](https://www.overleaf.com/latex/templates/latex-template-for-the-preparation-of-papers-for-aiaa-technical-conferences/rsssbwthkptn),
[AIAA ethical standards, Section 3 on AI](https://aiaa.org/publications/publish-with-aiaa/ethical-standards-for-publication-of-aiaa-technical-papers/).
Your region's call for papers may add its own deadlines and requirements; check it.

## Before you submit

1. **Eligibility of AI-produced work. Ask before you invest more time.** The rules say that "the primary concept of a paper
   must be the work of the Contributing Student Author(s)", that "a substantive portion of the work" must have been performed
   by them, and that the Judging Chair may check this. AIAA's AI policy says that AI used in the writing process "should be
   used primarily to improve readability, grammar, and language", that AI tools used in the research must be fully described,
   and that the use must be disclosed at submission and in the Acknowledgments. In this project an AI system derived the
   proofs, wrote the software, ran the experiments and drafted both texts. That is beyond what the writing clause describes,
   and whether the work qualifies for the competition is a question for your faculty advisor and the conference's judging
   chair, not something these drafts can settle. Splitting the work into two papers does not change the question. The
   Acknowledgments section of each paper states the AI's role plainly; do not soften it.
2. **Rewrite the text in your own words.** If a paper is entered, the manuscript should be yours. Use these drafts for
   structure, equations, numbers and figures.
3. **Check everything you sign.** Each author is "fully responsible and accountable for the content of the entire technical
   paper". For `algorithm/`: work through the proof (Sec. VI; the long form with one test per lemma is
   `../../math/10-landing-proof.md`), run `solver/tests`, and re-run at least `solver/scripts/example_landing.py` and
   `replay_flat.py`. For `impossibility/`: work through Secs. IV and V, build the Lean project
   (`../../lean/LcvxObstruction`, commands in `../../AUDIT-2026-11.md`), and run
   `../../numerics/independent-check/c2_bstar_delta80.py`.
4. **Name the independent reviewer only with permission.** The Acknowledgments of `impossibility/` has a placeholder for
   the person who found the missing condition in Theorem 2. Under the rules they are a contributor to acknowledge, or an
   author if they meet the authorship rules and the category allows it. That is for you and them to decide.
5. **Fill in the brackets:** author names, statuses, department, AIAA membership, mentor, the sentence in each
   Acknowledgments that says what the students did.
6. **Template.** The rules name the Word template. AIAA states that the formatting requirements are identical for Word and
   LaTeX and that submissions are PDFs, but if your region insists on the Word file, the content has to be moved into it.
   To use AIAA's own LaTeX class, open the Overleaf template linked above, download it as a zip, and follow the comment at
   the top of `aiaa-format.tex`.
7. **Do not add** a paper number or a copyright statement; AIAA stamps both.

## Format

`aiaa-format.tex` sets, by hand, what AIAA's instructions specify: letter paper, 1 in margins, Times 10 pt, single column, single
spacing, indented paragraphs with no blank lines between them; title bold 24 pt; author names with affiliations in italics;
abstract bold and indented 0.5 in on each side; nomenclature after the abstract; major headings bold 11 pt, centered, Roman
numerals; subheadings bold, flush left, capital letters; captions bold as "Fig. 1" below figures and "Table 1" above tables;
equations numbered at the right; footnote symbols; acknowledgments and references unnumbered. AIAA's template files could not
be downloaded in the environment where this was written (the Overleaf zip and the AIAA Word link both refused), so small
differences from the official class are possible, for example in the exact title size and heading spacing.

## Build

From `paper/` (builds all three; the combined paper is assembled first):

```bash
make student
```

or, for one paper, from its folder:

```bash
../../../solver/.venv/bin/python make_figures.py
```
```bash
latexmk -pdf main.tex
```

`algorithm/make_figures.py` plans the example of its Fig. 2 with the solver package and reads
`solver/results/mc_*_flat.json` for Fig. 3; every number in that paper comes from `solver/RESULTS-FLAT.md`.
`impossibility/make_figures.py` computes Fig. 1 from the closed-form witness of Theorem 2 and reads
`solver/results/audit_hop_ring.json` for Fig. 2.

## Review feedback on the first draft, and what was changed

An external review of the first algorithm draft (2026-11-11) raised four points. All three papers were revised.

| Point raised | Change |
|---|---|
| A closely related quadcopter paper (Freire and Xu, IEEE TCST 2023) was missing; "flatness, splines and one SOCP" is not new | Cited and compared in the introduction of `algorithm/` and `combined/`. The novelty claim is now the convex restrictions for the gimbal-angle limit and for throttle limits with depleting mass on the gimbaled body, with their proof. The two devices taken from that paper are named. |
| The impossibility result was delegated to an unpublished report | Both papers are standalone. `algorithm/` gives the argument in Sec. IV, states exactly what is proved, certified and only observed, and presents the result as motivation: its guarantee does not depend on it. `combined/` contains the proof. |
| "Every feasible plan is flyable" needs its assumptions | The abstract and conclusion now state them: a model with a constant center-of-percussion offset; throttle, gimbal-angle and tilt limits only; slew rates checked per plan; path constraints at sampled instants. The text no longer says the assumption "holds to 1%"; it says the guarantee does not extend to that variation. |
| The landing accuracy is practical evidence, not theory, and equals SCvx at matched rates | The papers now explain the mechanism without playing the result down: a single plan is as accurate as an SCvx plan, and the order-of-magnitude closed-loop gain is a direct benefit of the low computational cost (about 40 ms per plan instead of about 1 s), which allows frequent, current corrections. They add that this is the relevant comparison on a compute-limited flight computer and that the margin widens on slower hardware (fourfold-slower test: SCvx fails 4 of 30 hops, the planner none). |
| Results need independent verification | Cannot be fixed by editing. The limitations now say the proof and experiments have not been reproduced and point to the public code, tests, result files and scripts. |

## Where the numbers in `impossibility/` come from

| Statement | Source |
|---|---|
| Theorems 1 and 2, extensions, Table 1 | `../sections/03-impossibility.tex`, `../sections/B-proof-Bstar.tex`; Lean names checked against `../../lean/LcvxObstruction` |
| Condition (S1) and the account of how it was corrected | `../../numerics/independent-check/README.md`; `../../comms/CLAIMS.md` row CORR-2 |
| Search distances 0.020 and 10^-8, bound 3.8e-5 | `../../numerics/independent-check/c1_out.txt` (the 1.5-hour search was not rerun here; the bound was recomputed by hand) |
| Bounds 1.3e-5 m, 1.81 m/s, and the 2.14 m/s search | `../sections/03-impossibility.tex` (the remark after Theorem B*, and Theorem Q); `../../numerics/independent-check/c3_out.txt` (rerun, identical) |
| Table 2 | `../sections/03-impossibility.tex`, Theorems TVC-1, 2, 3, 5 |
| Fig. 2 and the 3-DOF and planner-F statements about it | `../../solver/results/audit_hop_ring.json` |

## What was left out of the two papers

From `impossibility/`: the unconstrained theorems B and Q beyond one example, the all-horizon and zero-minimum-throttle
results, the torque-limited 6-DOF theorem, the proofs of the distance bound and of the pure-TVC certificates, the
semidefinite lifts, and the detailed scope discussion. From `algorithm/`: planner B and its tables, the ablations, and
the per-span form of the soundness theorem (the paper states it for the fixed constants the algorithm ships with).
