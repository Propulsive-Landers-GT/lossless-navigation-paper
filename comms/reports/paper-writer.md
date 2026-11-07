# Report: [paper-writer]: LaTeX paper draft

Brief: comms/briefs/paper-writer.md. Output: paper/. Build: `cd paper && latexmk -pdf main.tex`. This uses TeX Live 2025, already installed; nothing was installed. It compiles cleanly to 30 pages (paper/main.pdf), with no undefined references or citations and 4 minor overfull boxes.

## Title
"On the Impossibility of Lossless Convexification for Attitude-Rate-Limited (5-DOF and 6-DOF) Powered Descent".
I chose "attitude-rate-limited" over "attitude-constrained" on purpose. Pointwise attitude constraints never obstruct (Aumann). The obstruction comes from the rate limit coupling different times.

## Structure (files in paper/sections/)
1. `01-introduction`: LCvx background, why 5/6DOF matters (GTPL numbers), the mechanism in one paragraph, contributions, honest scope.
2. `02-formulation`: models M0/M1/M3a/M4-kin/PT, centre-of-percussion lemma, feasible sets, Defs (uniform relaxation, affine/separable-monotone entry, lossless in three forms, state-linear), Prop "LCvx form ⇒ feasibility form", what the class captures and excludes, TRIV.
3. `03-impossibility`: Thm A; reduction lemma; Thm B (sketch); Thm Q; Prop L; Thm B* (+ formal-version remark, thin-gap remark); free tf + RR-LS; Thm D, Lemma W, Thm S; A-opt, Prop T; ρ1=0 (P0-R, P0-F, P0-X in text); 6DOF (kinematic, independent torque); pure TVC (Thm E0, TODO box for TVC-1); 3DOF consistency.
4. `04-possibility`: C-W, C-S/C-D, C-U, C-6, X5 (M1 only) + C-Y/C-3D; SDP lifts (Shor = Hilbert sphere, stress certificate, coplanar Thm 4.1, where exactness fails, TODO box for CSD2′).
5. `05-numerics`: everything labelled numerical. Gap law, ball-bound sandwich, beyond regime, constrained gaps table, hop ring, MT convex, in-air no dent, pure-TVC upright numerics, what 3DOF LCvx asks of the vehicle. 5 figures copied to paper/figures/.
6. `06-formalization`: conventions, Lean theorem table (only what [lean] confirmed builds), PMP/Aumann-as-hypothesis convention, TODO box for pending Lean (SixDOF, Slice, Positive axiom audit), what is not formalized.
7. `07-discussion`: guidance implications (attitude outer loop + exact convex inner, SDP certificates), open problems.
- Appendices: A (Thm B, Q proofs), B (B* proof incl. quantitative and window), C (Lemma W, master inequality, Thm S, certified table), D (P0-F, C-W, C-6 sketches).

## Conventions for the orchestrator
- Every theorem environment has a `% CLAIMS: … | Lean: …` comment.
- In draft mode each theorem title carries a coloured status tag. `\showstatusfalse` removes the tags and the project-note pointers (`\pnote`).
- paper/CLAIMS-MAP.md has the full table: paper label → registry row → registry status → synthesis status → proof file → Lean name.
- Placeholders are tcolorbox "TODO" boxes:
  - §3 pure-TVC TVC-1 (math/06 CERT_TABLE_PLACEHOLDER, proof-tvc verdict placeholder);
  - §4 CSD2′ (verifier-sdp run_csd2p.py outcome);
  - §6 pending Lean (SixDOF, Slice/*, Positive axiom output).

## Claims I could not support (or supported only conditionally)
1. **Registry/synthesis mismatch (main issue).** The brief says every theorem must correspond to a PROVED/CONFIRMED/FORMALIZED row. Only these rows meet that literally:
   - A, Lemma 3.3, B (variant F), B* qualitative, D (abstract): FORMALIZED;
   - B* Steps 1–7 / Cor 10.4, S/S-M/S-T: survived adversary, "PROVED IN REGIME".

   Many results that SYNTHESIS.md lists as PROVED are still **CLAIMED** in comms/CLAIMS.md:
   - Q, P-L, B variant T, RR-LS (its Lean form is committed), A-opt/T;
   - P0-R/P0-F, B6-K/D/D*, B6-E0;
   - C-W, C-S (both now partially formalized), C-U, X5, SDP-T1/T4/4.1. C-6, C-F and C-K are now FORMALIZED in the registry (commit b0dd184).

   I stated them as theorems with an orange tag "[proved in project notes; registry status CLAIMED]" and marked them ⚠ in CLAIMS-MAP.md. Please either upgrade those registry rows or tell me which to demote.
2. **Not supported, kept as TODO/numerics/open:**
   - B6-TVC-up / TVC-1 (registry OPEN; math/06 certificate table is a placeholder);
   - S-GTPL and the hop-instance hole (numerical; proof-s says the hole is not certifiable by quadratic methods);
   - CSD2′ (open);
   - OM exactness (registry: superposition principle cited, not proved), mentioned only as context;
   - P0-TVC/P0-T (text mentions only);
   - min-fuel value-losslessness (open).
3. **Lean:** I claim only what [lean] confirmed (DM): Abstract, Sphere, Nonconvex/Main (B), DiveBrake/Main (B*), TheoremD at eb2f850, all with axioms [propext, Classical.choice, Quot.sound]. FreeTime (517f1bb) is listed as sorry-free with its axiom check after the next full build. SixDOF (PENDING per [lean]) and Slice/* (lean-s, uncommitted) appear only in the TODO box. Positive/* (commit 455a288): the orchestrator recorded the clean audit (35 theorems, standard axioms) in lean/POSITIVE.md (commit b0dd184). The paper now lists them in the Lean table, and C-6 / C-F / C-K are tagged Lean-checked (constant mass; PMP and Aumann as explicit hypotheses). I stopped my own redundant audit run. Note: lean's final report (comms/reports/lean.md) lists SixDOF as proven, but lean's DM to me said PENDING and the file is uncommitted, so it stays in the TODO box.
4. **Small fixes I made relative to sources while transcribing:**
   - The B* constant c1 = 1/(ωϑs*) = 4a_max/(ω a10 sinδ s*).
   - "Inner discretization ⇒ NLP distances are upper bounds" is stated in the paper wherever numerics are cited.
5. **Bibliography:** paper/refs.bib is curated from literature/refs.bib (39 entries). I added 5 standard references not in the lit-review bib: Shor 1987, Lasserre 2001, Pontryagin et al. 1962, de Moura–Ullrich (Lean 4, CADE 2021), and mathlib (CPP 2020). They are marked in the file and should be checked. acikmese2013flight carries the lit-review's UNVERIFIED note.
6. **Vehicle:** context/vehicle.md says the vehicle is a hybrid, not a monoprop. The paper says only "small throttleable TVC lander" and uses the central parameter set (80 kg, 400–1000 N, ±15° box, J⊥ 63.6, L 0.589).

---
## Revision 2 (2026-11-07, after referee reports and new Lean results)
- **Referee repairs applied.** All NEEDS FIX items from math/verify-imp-report.md and math/verify-pos6-report.md:
  - Q_T scope (only the in-hypothesis value is quoted);
  - Cor 3.11 window (s* < t_a, (S1)–(S3) at t_a with a_max at t_b, m0−αρ2 t_b ≥ m_dry; the ρ1-fuel window is explicitly rejected);
  - Cor D.1 (δ ≤ π/4; extra vertical constraints must be satisfied by the witness);
  - Thm S Ω-ranges with positive lower ends, and the reason for them;
  - A-opt (conv V over finite mixtures, not V**);
  - Prop T (variant T; variant F with ωtf);
  - P0-R tent (convex ≤ π/2, nonconvex up to π, open beyond);
  - P0-X threshold values;
  - E₀ (constant mass, roll restriction, strict regime, duty-cycle closure step written in App. D);
  - C-S (meagre in the admissible class; BV adjoint under velocity constraints);
  - C-W′ touchdown-Slater caveat;
  - C-U without path constraints;
  - X5 with ωtf ≥ ∠(b0,b_f);
  - Thm 4.8 without the glide-slope clause (Gram-linear constraints only; glide slope a posteriori);
  - Prop 5.1 rank ≤ 4 only for 3D data (≤ 5 coplanar), with the added step;
  - Prop 6.1 consequence toned down;
  - Cardan corner angle 21.09°;
  - C-Y 3.5e-6 / 1.8e-5 rad/s (the paper never contained the "TVC torque may be added" remark).
- **Tags.** CONFIRMED rows are now tagged "proved; independently refereed". Repaired rows are tagged "proved; refereed, statement as repaired". Only TRIV (Prop 2.7) and P-3 (Rem 3.22) keep the orange "not refereed" tag.
- **Headline.** A machine-checked Main Theorem is stated in the introduction and pointed to from the abstract:
  - `no_lossless_relaxation_constrained_5dof` and its LCvx form;
  - the `_upright_5dof`, `_constrained_6dof` and `_upright_6dof` versions.
- **Lean table (§6).** Rewritten with Upright.lean, SixDOF.lean, MassModel.lean (`no_lossless_relaxation_5dof_mass`), `position_eq_integral_velocity`, and Slice/* (Lemma W, master inequality, `Slice.lemmaS` + `theoremD_hard_landing` for the explicit fixed-thrust instance, abstract A-opt and Prop T). The pending-Lean placeholder is removed.
- **Remaining placeholders:**
  1. pure TVC upright at rest with r_z ≥ 0 (TVC-1, proof-tvc);
  2. Conjecture CSD2′ (evidence updated: 0 gaps on 509 former unit-d gap instances; prover running).
- The PDF is now 33 pages and compiles cleanly. paper/CLAIMS-MAP.md is rewritten (revision 2).
