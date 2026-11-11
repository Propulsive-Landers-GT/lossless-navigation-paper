# Final audit of the paper (final-auditor, 2026-11-07)

Independent, skeptical pass over paper/main.tex, paper/sections/*.tex and the compiled main.pdf, checked against
comms/CLAIMS.md, paper/CLAIMS-MAP.md, SYNTHESIS.md, the five referee reports (math/verify-imp-report.md,
math/verify-pos6-report.md, math/verify-sdp2-report.md, math/verify-tvc-report.md, math/verifier-sdp-report.md), the Lean
sources and lean/{MODEL,POSITIVE,SLICE,SOLVER}.md. No lean/TVC.md or Lean `TVC/` directory is committed, so nothing from the
in-progress TVC formalization was used or cited.

## Summary verdict
The paper's answer is accurate and properly scoped. LCvx-type lossless convexification of 5DOF / kinematic 6DOF powered descent is
**impossible** within the class of convex programs on the physical state with affine (or separable-monotone) data entry. This holds
for the state-constrained problem at every horizon (Lean-checked, constant mass), and for the real pure-TVC actuation it is proved
only at t_f = 1 s (constant mass, unlimited gimbal rate). It is **possible** in the narrower senses the paper lists: fixed attitude
profile, per instance, occupation measures, the exact convex inner problem for pure TVC, and the SDP certificate results.
Theorem statements match their sources and registry status. No theorem is mislabelled as Lean-checked, and no BROKEN or OPEN
claim is stated as proved. The issues below are scope gaps, stale or misattributed text, one rendering bug and bibliography
hygiene. All MUST-FIX and SHOULD-FIX items have been applied.

## Lean verification
- **Existence.** Every Lean name cited in the paper exists as a declaration in lean/LcvxObstruction: 101 names, taken from
  `\lean{...}` and from the `% CLAIMS ... | Lean:` comments. The only non-matches were Mathlib names and typeset fragments
  (`InnerProductGeometry.angle`, `EuclideanSpace ℝ (Fin 3)`, `Acc` used as a variable name).
- **Faithfulness.** I read the statements of the headline theorems: `no_lossless_relaxation_constrained_{5dof,upright_5dof,6dof,upright_6dof}`,
  `no_losslessFor_relaxation_constrained_5dof`, `exists_switchTime`, `constrainedLandingSet`, `glideSlopeSet`, `AccBox`,
  `AttitudeAdmissible`, `Attitude6Admissible`, `no_lossless_relaxation_5dof(_mass)`, `Slice.lemmaS` and `Slice.theoremD_hard_landing`.
  - The Main Theorem's hypotheses (0<δ<π/2, 0<a_min≤a_max, g₀<a_max, ω>0, t_f>0, tanγ≥0, any X ⊇ glide-slope set, path
    constraint for all t ∈ [0,t_f]) match the Lean statements exactly.
  - The 6DOF Lean model caps the rate of every body vector (total body rate ≤ ω). The paper says so, as verify-pos6 requested.
  - Minor: the optimization (`IsLosslessFor`) form is stated in Lean only for the free-attitude 5DOF case. For the upright and 6DOF
    cases it follows in one line from the Lean-checked `IsLosslessFor.isLossless` (NIT 1 below).
- **Axioms.** I ran `#print axioms` on all 101 cited declarations (scratch file, `lake env lean`, no rebuild, no `lake update`,
  HEAD with Lean files at commit ef5ad1b). Every one reports exactly `[propext, Classical.choice, Quot.sound]`. There are no errors,
  and there is no `sorry`, `admit`, `axiom` or `native_decide` in the sources.

## Issues

### MUST-FIX

1. **App. D (sections/D-proofs-other.tex, Theorem P0-F sketch), rendering bug.** `\norm` had been corrupted to a newline plus
   `orm` in two places (a `\n` escape), so the PDF printed "orm u ≤ a₂ … orm u cos δ". **Fix (applied):**
   `U(b)=\{u:\norm u\le a_2,\ \ip ub\ge\norm u\cos\delta\}`.

### SHOULD-FIX

2. **Abstract, "or rate-limited 6-DOF descent".** This reads as covering every rate-limited 6DOF vehicle, including the real
   pure-TVC rocket, which is proved only at t_f = 1 s. **Fix (applied):** "or kinematic (attitude-rate-limited) 6-DOF descent".
3. **Abstract, "covers the realistic constrained problem".** The formal theorem uses constant acceleration bounds (constant mass)
   and the kinematic model. **Fix (applied):** "covers the state-constrained problem (with constant thrust-acceleration bounds,
   i.e. constant mass)".
4. **Abstract, "with or without a minimum throttle".** This sits in a list that also contains altitude/glide-slope constraints. The
   ρ₁=0 results (P0-F, P-L0) hold only without state constraints. With altitude they need T/W ≳ 2.1, and the GTPL case is open.
   **Fix (applied):** "without a minimum throttle (without state constraints)".
5. **Abstract and Intro contribution 3: C-6 "exactly convex given attitude" omitted constant mass.** math/04 §8 states that
   variable mass makes the problem nonconvex even for fixed b. **Fix (applied):** "with constant mass" added in both places.
6. **Intro, related work: "free final time \cite{kunhippurayil2021automatica}".** That paper is about annular control constraints:
   controllability suffices for a sequence of convex programs, at fixed final time (literature/review.md; Automatica 133:109848).
   **Fix (applied):** "annular control sets under controllability".
7. **Intro: "no impossibility result for lossless convexification of any kind".** This contradicts the paper's own citation of
   the discrete-time counterexamples of Luo–Echigo–Açıkmeşe (§2.5; literature/review.md §0, item 5). **Fix (applied):** "beyond
   the discrete-time counterexamples of \cite{luo2026automatica}".
8. **Intro contribution 2: "gap of metres per second" for Theorem B/Q.** Without a caveat this overstates the physical relevance.
   Those witnesses start underground for GTPL (registry B: SCOPE-BROKEN for r_z ≥ 0). **Fix (applied):** added "(at boundary data
   that start below ground for a lander that cannot hover at minimum throttle)".
9. **Intro scope: "That covers every LCvx formulation in the literature."** This is stronger than §2.5's "Every LCvx formulation we
   know". **Fix (applied):** "…in the literature that we know of (\cref{sec:scope})".
10. **Thm 3.20 (thm:6dyn) (ii), Theorem D\*: missing regime.** verify-pos6 §1.3 confirms D\* only for an explicit attitude history
    that needs ᾱs\* ≤ ω̄, ᾱs\*² ≤ δ_in, 4s\* ≤ t_f, plus the "missing but trivial" δ\*+ᾱs\*²/2 ≤ π/2. **Fix (applied):** "with a
    sufficiently short dive s\* (ᾱs\* ≤ ω, ᾱs\*² ≤ δ_in, 4s\* ≤ t_f, δ\*+ᾱs\*²/2 ≤ π/2)".
11. **Thm 3.22 (thm:TVC1): scope items from verify-tvc §5 were missing.** (a) The model has an on-axis gimbal pivot, so GTPL's
    (−0.02, −0.01) m pivot offset and its products of inertia are ignored. (b) "Margins certified in exact arithmetic" omitted that
    the localization step functions and the physical constants are float inputs (validated, with dominant margins). **Fix
    (applied):** both stated in the theorem and in its parenthetical.
12. **§6 Planner B, step 4: "exact solution of the true dynamics".** The inner solve uses a prescribed mass history (fixed point;
    solver/README.md l.168–169), and §6.3 itself lists mass fixed-point convergence as not guaranteed. **Fix (applied):** "exact
    solution of the planning model (with its prescribed mass history) …; the certificate below checks it against the full dynamics".
13. **§5 hop bullet: "60–250 times the B\* gap".** The source numbers (numerics/README.md: 0.65/0.010 at t_f=4, 2.94/0.007 at t_f=8)
    give about 65× and 420×. **Fix (applied):** "about 65 (t_f=4) and 400 (t_f=8) times".
14. **Table tab:gaps, B\* rigorous row "≥1.3×10⁻⁵".** 1.3e-5 is η₀, the gap in ℓ. The certified distance is
    η₀/√(1+s\*²) ≈ 1.1×10⁻⁵ (math/02 Rem 10.2, s\*=0.654 s). **Fix (applied):** "≥1.1×10⁻⁵ (proved)".
15. **§4 (after Prop 4.5): Claim C-3D (registry CLAIMED, not refereed) carried no status tag.** **Fix (applied):** `\Spending`
    added, and the internal-conventions box updated ("two minor remarks and the side claim C-3D").
16. **§8 Open problem 3: "Is there a tractable exact lift with variable throttle (e.g. the separate-axis lift CSD3)?"** This is
    stale: CSD3 was tested and is lossy (verifier-sdp: 2–35/36 % even at δ=0), as §4.5 of the paper says. **Fix (applied):** the
    question is kept, and the parenthetical now says the natural lift and CSD3 were both found lossy numerically.
17. **§7 axioms provenance.** The text cited only the orchestrator check at commit 19ffe1a, which predates the Slice and Solver
    files cited in Table 2 (tab:lean). **Fix (applied):** added a sentence that this audit re-ran `#print axioms` on all 101 cited
    declarations at ef5ad1b, with the same result.
18. **Bibliography: internal notes printed in the PDF.**
    - `acikmese2013flight` printed "UNVERIFIED: no DOI; citation taken from …" and had author "and others". I verified the paper
      (AAS/AIAA Space Flight Mechanics Meeting 2013; authors Açıkmeşe, Aung, Casoliva, Mohan, Johnson, Scharf, Masten, Scotkin, Wolf,
      Regehr). **Fix (applied):** full author list; note removed.
    - `lyapunov1940` printed "No DOI; verified on mathnet.ru …" and `vinter2000book` printed "Crossref chapter DOIs … verified".
      **Fix (applied):** notes removed or replaced by "Reprint of the 2000 edition".
    - `shor1987`: issue number 6 added. The details were verified against secondary references (Sov. J. Comput. Syst. Sci.
      25(6):1–11, 1987; Russian original in Izv. AN SSSR Tekh. Kibern. 1987, no. 1, 128–139).

### NIT (not applied)

1. **Main Theorem (§1)** says both forms (feasibility and LCvx optimization) for the upright and 6DOF variants. Lean states the
   optimization form only for free-attitude 5DOF. The other cases follow in one line from the Lean-checked
   `IsLosslessFor.isLossless`. A future Lean commit could add the three trivial corollaries.
2. **Intro** says the stored LCvx thrust-direction jump is "15° within one 24 ms step", while §5 says 14.8°. Harmless rounding.
3. **CSD3 gap range.** The paper says "2–35 %". verifier-sdp gives 2–35 % in its summary table and 2–36 % in §5.
4. **Thm 3.22 table.** The Cardan-box margin 7.57e-6 m is the post-W3 value (verify-tvc l.194). The registry row TVC-B still says
   7.58e-6 (pre-W3). The registry should be aligned with the paper.
5. **Prop 2.7 (TRIV), Rem 3.23 (P-3), C-3D** remain unrefereed. They are labelled as such and are not used in any headline result.
6. **`pontryagin1962`** could carry the translator (K. N. Trirogoff) and editor (L. W. Neustadt). `lasserre2001siopt`,
   `demoura2021lean4` (CADE-28, LNCS 12699, 625–635) and `mathlib2020` (CPP 2020, 367–381) are correct as cited.

## Statement-by-statement check (abridged)
Every theorem-like environment was compared with its registry row and proof file. Matches, beyond those fixed above:
- **Abstract section.** Thm A / Cor A, Lem 3.3, Thm B (variant F Lean: δ+ωt_f ≤ π/2, any continuous a₁ > 0, any g; variant T refereed).
- **Theorem Q, Prop L.** Thm Q has the M_z ≥ 0 condition and the γ_T validity restriction. Prop L covers P-L and P-L0.
- **B family.**
  - Thm B\*: hypotheses (S1)–(S3), quantitative part for δ ≤ π/4, and a Lean tag limited to constant acceleration bounds.
  - Cor 3.11: repaired window, s\* < t_a, dry-mass condition.
- **Per-instance results.**
  - Thm D (abstract Lean), Lem W, Thm S: repaired Ω ranges with a positive lower end. The Lean instance is a≡12, δ=0, ω=0.1,
    dent ≥ 1 m, X ⊇ {r_z ≥ 0}, faithful to `Slice.lemmaS` / `theoremD_hard_landing`.
  - Thm A-opt (conv V, not V\*\*) and Prop T (variant T, with variant F using ωt_f).
- **ρ₁ = 0 and 6DOF.**
  - P0-R (repaired tent), P0-F, and P0-X (threshold 2.16/2.38/2.78).
  - Thm 6kin: corner 21.09° and δ_in for B\*.
  - Thm E₀ (constant mass, strict regime, closure step).
- **Pure TVC.** Thm TVC-1: margins 9.96e-6 / 7.57e-6 / 2.90e-6 m and d\* 9.63e-6 / 7.34e-6 / 2.81e-6 m, as in verify-tvc. The
  realistic-model numerics 1.26e-2 / 4.8e-3 / 2.8e-2 / 3.3e-2 m are labelled numerical.
- **Positive side.**
  - C-W (Slater caveat), C-S (meagre set in the admissible class), C-U (no path constraints), C-6, X5 (ωt_f ≥ ∠(b₀,b_f)),
    C-Y (3.5 / 18 µrad/s).
  - Shor lemma, stress theorem, coplanar theorem (glide slope removed), rank ≤ 4 with the E_w step.
  - CSD2′ stated as a conjecture, with T1–T5 / P6 / P7 refereed and the 188/898 and 9/17 counts.
- **Numbers spot-checked against numerics/README.md, solver/RESULTS.md, math/02 Rem 10.2 and the verifier-sdp report: all match.**
  - Gap law 0.31ωt_f, LB/NLP 81–83 %, 2.18–2.23 m/s.
  - Long-horizon 2.1/13.5/18.6 and 1.15/1.56/0.35, tent 0.66/6.24, M3 0.8–8 m/s.
  - B\* face 0.010/0.007, slice 0.016/0.009, hop window (7.727, 7.917], r_in up to 4.99 m, M3 hole 1.74 m, MT disk 10.1 m,
    in-air 104 m / ≤ 0.016 m, coning 0.69/0.50/0.106.
  - Unit-d case 12 (0.027529 vs 0.028231), Lasserre N=3 (1.862 < 2.358 ≈ 2.357), throttle 12→68 %, Las2 0.5759 < 0.6047,
    glide slope 1.19 %.
  - Planner: 0.012 % / mean 0.005 %, ≤ 0.85 % / mean 0.34 %, 1/8, +3.9–12.6 %, 28/95/100 %, 0/100/97 %, 2.42/0.48/0.20 m/s, 11 of 20.
  - γ_X = 0.087 m and η₀ ≈ 1.3e-5 m.

## Build
`latexmk -pdf main.tex`: 39 pages, no errors, no undefined references or citations. The overfull-box warnings are the same
pre-existing set as in build.log (none new).


---

# Addendum, 2026-11-10: paper revision 7

The audit above covers revision 5/6 of the paper. Revision 7 adds material that **was not seen by the final auditor or by
any referee**:

- title extension and the last sentences of the abstract;
- Section 4.5 (Assumption 4.6, the program (8), Theorem 4.7 "Theorem F", Proposition 4.8, two remarks);
- Section 6.3 (planner F, the comparison with B and S with computation time counted, one table, Figure 8);
- Appendix E (proof of Theorem F);
- paragraphs in Sections 1, 2.4, 7 and 8 that refer to the above, and six new references.

What was checked for revision 7, by the session that wrote it:

- **Build.** `make draft` and `make share`: 48 pages each, no errors, no undefined references or citations. Overfull boxes are
  the pre-existing set (Lean identifiers and Table 2).
- **Numbers.** Every number in Section 6.3 and in the new abstract sentences was read off `solver/RESULTS-FLAT.md`, which is
  generated by `solver/scripts/report_flat.py` from `solver/results/*_flat.json`, `replay_flat.json`, `stress_flat.json` and
  `audit_*.json`.
- **Proof.** Appendix E is the LaTeX form of `math/10-landing-proof.md`. Each lemma has a numerical test in
  `solver/tests/test_flat.py` (11 tests, passing). The proof has had no independent reader. Only its first step
  (`TVC.cop_identity`) is machine-checked.
- **References.** The six added entries were resolved against the Crossref API (title, authors, venue, volume, pages). Their
  content is cited at abstract level only (`literature/review.md` §7).
- **Earlier statements revised.** (P2) in Section 6 now says "no single convex program of the class of Theorem A can do so for
  all boundary data" instead of "no single convex program can"; Section 8 item 1 now says the impossibility is about exactness,
  not soundness. Both changes narrow a claim; neither changes a theorem.

Not re-audited: Sections 2 to 5 and Appendices A to D, which are unchanged apart from the cross-references listed above. The Lean
project is unchanged (126 cited declarations); it was not rebuilt for this revision.

## Addendum, revision 7.1 (2026-11-11)

An independent reader worked from the shared PDF alone, then compared it with this repository
(`numerics/independent-check/README.md`, merged as pull request aneesh-iyer29/lossless-work#2).

- **Theorem B\* (Thm 3.7), hypothesis (S1).** The printed condition ωs\* ≤ δ did not give δ + ωs\* ≤ π/2 for δ > π/4, which
  Steps 4 and 5 of Appendix B use. (S1) is now ωs\* ≤ min(δ, π/2 − δ), Step 1 of Appendix B cites it, and the remark on the
  envelope version names the condition it drops. The statement-by-statement check above passed the old (S1); that was a miss.
  The Lean statements already carried the hypothesis, so no formal result changes.
- **Section 5.1.** The quoted distance 2.18 to 2.23 m/s is an upper bound that was still falling with the grid. The
  independent search reaches 2.14 m/s; the sentence now says so and gives the proved lower bound.
- **Lean.** That reader reports `lake build` and `lake env lean Verify.lean` passing on a fresh clone with Lean v4.36.0-rc2
  (126 cited declarations). It has not been rebuilt in the environment that produced this revision.
- **Build.** `make draft` and `make share` rebuilt after these edits.
- **Checked here.** The δ = 80° example was re-derived with a separate script and matches; `c2` and `c3` reproduce the recorded
  outputs exactly; `c4` reaches the same conclusion with small numerical differences (2.3177 m against 2.3174 m); `c1` was not
  rerun.
- **Not covered by the independent check** (its own list): the pure-TVC certificates, the theorems printed as sketches, and
  everything about the planners, including Theorem F.

## Addendum, revision 8 (2026-11-11)

Revision 8 adds one result that was contributed separately (`scvx-thrust-relaxation/`, merged as pull request
Propulsive-Landers-GT/lossless-navigation-paper#5): Section 4.7 with Theorem 4.15 and Table 1, one sentence in the
abstract, and a paragraph in Section 7. Nothing else changes; the paper is 50 pages.

What was checked, by the session that wrote the section:

- **Statement.** Theorem 4.15 paraphrases `sixDOF_free_time`, `sixDOF_fixed_time`, `card_lossy_lt` and `isMinOn_original`
  as described in the folder's README and as declared in `lean/LCvx/SixDOF.lean` and `Basic.lean`. The core lemma
  (`lean/LCvx/Core.lean`) was read line by line; the rest of the Lean was not.
- **Lean.** Sources scanned: no `sorry`, `axiom`, `admit` or `native_decide`. **Not built** (no toolchain here). The tag
  on the theorem says so. These declarations are outside the 126 audited by `Verify.lean`.
- **Table 1.** Every entry was compared with `scvx-thrust-relaxation/solver/results/*.json`. One case (`loose_rate`)
  was re-run and reproduced to nine digits; the 5-DOF reduction check was re-run and reproduced; one interval rank
  certificate was re-run. The other three cases, the full certificates and the two SDP scripts were not re-run, so the
  SDP figures in the last paragraph are quoted from the folder's README.
- **Prior work.** The two comparisons cite entries already in `refs.bib` (`blackmore2012scl`, `luo2026automatica`). The
  folder's README also cites an arXiv paper (2607.12109) that was not checked and is not cited in the paper.
- **Build.** `make draft` and `make share`: 50 pages, no errors, no undefined references.
