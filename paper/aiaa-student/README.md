# AIAA student-conference version of the paper

`main.pdf` is a 9-page paper on the landing algorithm, written to the rules of the AIAA Regional Student Conferences.
It is a short version of `../main.pdf` (48 pages): it keeps the single convex program, its soundness theorem with a
full proof, and the benchmark against successive convexification, and it reduces the impossibility result to one
section that cites the long paper as an unpublished report.

**It is a draft for the authors to take over, not a finished submission.** Read "Before you submit" below first.

## The rules it was written to

From the AIAA Regional Student Conference Rules (version dated June 2026) and AIAA's manuscript instructions:

| Rule | Status here |
|---|---|
| At most 11 pages, single column, 8.5 x 11 in, including acknowledgments, references and appendices | 9 pages |
| AIAA Meeting Paper format ("Use the Word Template"); deviations may disqualify | Format reproduced in LaTeX from the published instructions (see "Format" below). **Not built from AIAA's own template file.** |
| Every author identified in the first-page footnote by status, role (Contributing Student Author or Mentor Author) and AIAA membership | Placeholders in brackets |
| Undergraduate and Graduate categories: at most two Contributing Student Authors. Team category: three or more, at least half undergraduates. Up to two Mentor Authors, listed after the students. No industry co-authors | Two student placeholders and one mentor placeholder; edit to your category |
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
   proofs, wrote the software, ran the experiments and drafted this text. That is beyond what the writing clause describes,
   and whether the work qualifies for the competition is a question for your faculty advisor and the conference's judging
   chair, not something this draft can settle. The Acknowledgments section states the AI's role plainly; do not soften it.
2. **Rewrite the text in your own words.** If the paper is entered, the manuscript should be yours. Use this draft for
   structure, equations, numbers and figures.
3. **Check everything you sign.** Each author is "fully responsible and accountable for the content of the entire technical
   paper". Work through the proof (Sec. VI; the long form with one test per lemma is `../../math/10-landing-proof.md`), run
   `solver/tests`, and re-run at least `solver/scripts/example_landing.py` and `replay_flat.py`.
4. **Fill in the brackets:** author names, statuses, department, AIAA membership, mentor, and the sentence in the
   Acknowledgments that says what the students did.
5. **Template.** The rules name the Word template. AIAA states that the formatting requirements are identical for Word and
   LaTeX and that submissions are PDFs, but if your region insists on the Word file, the content has to be moved into it.
   To use AIAA's own LaTeX class, open the Overleaf template linked above, download it as a zip, and follow the comment at
   the top of `main.tex`.
6. **Do not add** a paper number or a copyright statement; AIAA stamps both.

## Format

`main.tex` sets, by hand, what AIAA's instructions specify: letter paper, 1 in margins, Times 10 pt, single column, single
spacing, indented paragraphs with no blank lines between them; title bold 24 pt; author names with affiliations in italics;
abstract bold and indented 0.5 in on each side; nomenclature after the abstract; major headings bold 11 pt, centered, Roman
numerals; subheadings bold, flush left, capital letters; captions bold as "Fig. 1" below figures and "Table 1" above tables;
equations numbered at the right; footnote symbols; acknowledgments and references unnumbered. AIAA's template files could not
be downloaded in the environment where this was written (the Overleaf zip and the AIAA Word link both refused), so small
differences from the official class are possible, for example in the exact title size and heading spacing.

## Build

```bash
../../solver/.venv/bin/python make_figures.py
```
```bash
latexmk -pdf main.tex
```

`make_figures.py` plans the example of Fig. 2 with the solver package and reads `../../solver/results/mc_*_flat.json` for
Fig. 3. Every number in the paper comes from `../../solver/RESULTS-FLAT.md`.

## What was cut from the long paper

The definitions and proofs of the impossibility theorems, the machine-checked formalization, the semidefinite lifts, the
fixed-attitude exactness results, the gap laws, planner B and its tables, the ablations, and all but 18 of the references.
The soundness theorem is stated for fixed reference constants (the form the algorithm ships with); the long paper states it
with per-span references.
