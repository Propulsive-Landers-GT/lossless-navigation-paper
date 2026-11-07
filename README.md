# Lossless convexification for 5-DOF / 6-DOF powered descent

Research workspace of Propulsive Landers at Georgia Tech (GTPL). The question was whether lossless convexification
(LCvx), which solves 3-DOF powered-descent guidance exactly as one convex program, extends to 5-DOF and 6-DOF
landers whose thrust direction is tied to a finite-rate attitude. The answer is a proof, machine-checked in Lean 4.

**Answer: impossible in the LCvx sense.** No convex program that takes the initial position and velocity the way LCvx
does (affine data entry, any lifted variables, any cost) is lossless for 5-DOF or kinematic 6-DOF descent. This holds
with throttle limits, gimbal cone, altitude and glide-slope constraints, upright landing, any burn time, mass depletion,
free final time, and at GTPL's actual constants. For the real gimbal-torque (pure TVC) vehicle the same nonconvexity is
proved by exact-arithmetic computer-assisted certificates at 1, 2, 3 and 5 s. A practical planner built on what *is*
exactly convex (the problem for a fixed attitude profile) is in `solver/`.

## Start here

| If you want | Read |
|---|---|
| The answer and its exact scope, in two pages | [`FINAL-REPORT.md`](FINAL-REPORT.md) |
| The status of every individual claim (Lean / proved / numerical / open) | [`SYNTHESIS.md`](SYNTHESIS.md) |
| The paper (shareable version, 40 pages) | [`paper/main-share.pdf`](paper/main-share.pdf) |
| To check the proofs yourself | [Checking the results](#checking-the-results) below |
| The guidance algorithm for the lander | [`solver/README.md`](solver/README.md), [`solver/RESULTS.md`](solver/RESULTS.md), [`solver/RESULTS-SCVX.md`](solver/RESULTS-SCVX.md) (vs standard SCvx) |
| How the work was done, conversation included | [`session-transcript/`](session-transcript/) and [`comms/`](comms/) |

## Repository map

### Top level
| Path | Contents |
|---|---|
| `FINAL-REPORT.md` | User-facing summary: the answer, what is possible, effect size for GTPL, practical algorithm, open problems. |
| `SYNTHESIS.md` | Living results table. One row per claim with its model, scope, status and the file holding the proof. |
| `context/vehicle.md` | GTPL vehicle parameters (mass, thrust, Isp, inertia, gimbal) and notes on the existing guidance stack, including the flight MPC's ~4.6x angular-authority mismatch. |
| `literature/` | `review.md`: literature review of LCvx and 6-DOF guidance with verified sources. `refs.bib`: bibliography. |
| `session-transcript/` | Export of the full Claude Code session that produced this work (see its README). |

### `paper/`: the paper
| Path | Contents |
|---|---|
| `main-share.pdf` | **Shareable version.** Reader-facing status tags, a "how to check" box and a methods statement; no internal pointers. |
| `main.pdf` | Internal draft: same content plus pointers to project files and referee status tags. |
| `main.tex`, `sections/*.tex`, `refs.bib`, `figures/` | LaTeX sources. Sections: 01 introduction, 02 formulation, 03 impossibility, 04 possibility, 05 numerics, 055 practice (planner B), 06 formalization, 07 discussion; appendices A-D hold the proofs. |
| `Makefile` | `make draft` builds `main.pdf`; `make share` builds `main-share.pdf`. Edit `\paperauthors` in `main.tex` to set the author line. |
| `CLAIMS-MAP.md` | Maps every theorem in the paper to its registry row, proof file and Lean name. |
| `AUDIT.md` | Final independent audit of the paper against the proofs and the Lean code. |

### `lean/`: the machine-checked proofs
| Path | Contents |
|---|---|
| `LcvxObstruction/` | Lake project (Lean `v4.36.0-rc2`, Mathlib pinned). 44 source files, no `sorry`, no `axiom`. |
| `LcvxObstruction/Verify.lean` | One-command audit: prints the headline statements and checks all 126 declarations cited in the paper use only `propext`, `Classical.choice`, `Quot.sound`. |
| `LcvxObstruction/README.md` | Build instructions and a table of where each main theorem lives. |
| `MODEL.md` | Faithfulness map: what each Lean definition means mathematically (models, relaxations, landing sets). |
| `POSITIVE.md`, `SLICE.md`, `SOLVER.md`, `TVC.md` | The same for the positive results, Lemma S / Theorem D / A-opt, the solver's claims, and the pure-TVC files. |

Key Lean files (all under `lean/LcvxObstruction/LcvxObstruction/`):

| File | What it proves |
|---|---|
| `Abstract.lean` | Definitions of `UniformConvexRelaxation` and `IsLossless`; Theorem A: lossless forces the feasible set to be convex. |
| `Nonconvex.lean`, `Main.lean` | Theorem B and the Main Theorem for 5-DOF with altitude/glide slope (`no_lossless_relaxation_constrained_5dof`). |
| `DiveBrake.lean`, `Upright.lean`, `SixDOF.lean` | The dive-then-brake counterexample; upright landing; kinematic 6-DOF. |
| `MassModel.lean`, `DiveBrakeMass*.lean` | The same results with explicit mass depletion. |
| `FreeTime.lean`, `FreeTimeBStar.lean` | Line search over final time; free-final-time windows. |
| `DiveBrakeQuant*.lean` | Quantitative distance bounds. |
| `GTPLMass.lean` | The impossibility at GTPL's constants (`gtpl_no_lossless_upright_6dof_mass`, `gtpl_no_lossless_freeTime_mass`). |
| `TheoremD.lean`, `Slice/` | Per-instance obstruction, Lemma S, Wirtinger inequality, value-losslessness (A-opt). |
| `Positive/` | What is possible: cap lemmas, PMP-based results (PMP as an explicit hypothesis), fixed-attitude convexity, discrete KKT. |
| `TVC/` | Centre-of-percussion identity and the logical skeleton of the pure-TVC theorem. |
| `Solver/` | The 28 elementary claims planner B relies on. |

### `math/`: pen-and-paper proofs and verification reports
| File | Contents |
|---|---|
| `00-model-catalog-and-proof-sketch.md` | Survey of 5-DOF/6-DOF models and the first proof sketch. |
| `01-adversary-report.md` | Adversarial attack on the impossibility proof (found the underground-witness flaw, fixed by Theorem B*). |
| `02-impossibility-rigorous.md` | Full impossibility proofs: Theorems A, B, B*, Q, 6-DOF transfer. |
| `03-lean-blueprint.md`, `05-positive-lean-blueprint.md` | Plans for the Lean formalization. |
| `04-positive-results.md` | What is possible: Theorem C, C-6 (exact convexity given attitude), C-U, C-Y, C-K. |
| `06-pure-tvc.md` | Pure-TVC (gimbal-torque) model: certificates at 1, 2, 3, 5 s, rate-limited numerics, open problems. |
| `07-lemma-S.md` | Lemma S and the hard-landing Theorem D. |
| `08-sdp-exactness.md`, `09-csd2-prime.md` | SDP (moment) lifts: when they are exact, the CSD2' conjecture and its partial proofs. |
| `possibility-rho0.md` | The zero-minimum-throttle case (still nonconvex). |
| `adversary-6dof-report.md` | Attack on the 6-DOF transfer; pure-TVC Theorem E0. |
| `redteam-lift.md`, `redteam-reform.md` | Attempts to *make* LCvx work (lifts, reformulations, line search); all failed with proofs. |
| `verify-*.md`, `verifier-sdp-report.md` | Independent referee reports on every proof (imp, pos6, sdp2, tvc), including the exact-arithmetic re-certification of the TVC results. |
| `checks/flat_output_tvc.py` | Symbolic check of the centre-of-percussion identity. |

### `numerics/`: numerical experiments
`numerics/README.md` describes the models (M1, M1A, M3, MT) and the experiments. Top-level scripts (`t1_*`, `t2_*`,
`s1_*`-`s5_*`, `c1_*`-`c6_*`, `d1_*`) run the reachable-set studies, the hop ring and the SDP checks; plots and data are in
`results/`. Each subdirectory belongs to one agent and holds its scripts and outputs:

| Directory | Contents |
|---|---|
| `proof-tvc/` | Pure-TVC certificate construction (SDP at 1 s; Riccati recursion at 2, 3, 5 s); witnesses; rate-limited numerics in `ratelim_numerics/`. |
| `verify-tvc/` | Independent exact-arithmetic re-verification of those certificates (`exact_cert.py`, `riccati_exact.py`, `witness_check.py`, ...). |
| `adversary/`, `adversary-6dof/` | Numerics behind the adversarial reports, including the full 6-DOF TVC model `m3tvc.py`. |
| `redteam-lift/`, `redteam-reform/` | Numerics for the attempts to make LCvx work. |
| `proof/`, `proof-s/`, `proof-sdp/`, `proof-csd2p/`, `possibility-rho0/`, `positive/` | Numerics supporting the corresponding math notes. |
| `verify-imp/`, `verify-pos6/`, `verify-sdp2/`, `verifier-sdp/` | Referees' independent re-computations. |

### `solver/`: planner B (attitude-aware convex guidance)
| Path | Contents |
|---|---|
| `README.md` | How the planner works and how to run it. |
| `RESULTS.md` | Open-loop, closed-loop Monte Carlo (in-air 100% vs 28% for current guidance; pad hops 97% vs 0%) and hop-map results. |
| `RESULTS-SCVX.md` | Head-to-head with standard 6DOF successive convexification: a tie on fuel and feasibility, SCvx as good or slightly better in closed loop, B about 2x faster per replan. |
| `CLAIMS.md` | Every mathematical claim the planner relies on, with its proof and Lean status. |
| `PORTING.md` | Notes for porting to the flight computer (hard time budget, fallback). |
| `gtpl_guidance/` | The package: `aacg.py` (planner B), `scvx6dof.py` (standard 6DOF SCvx baseline), `lcvx3dof.py` (current flight LCvx re-implementation), `certify.py`, `sim6dof.py`, `reference_nlp.py` (IPOPT baseline), `dynamics.py`, `attitude.py`, `params.py`. |
| `scripts/`, `results/`, `tests/` | Experiment drivers, their outputs, and 15 pytest tests (`cd solver && pytest`). |

### `share/`: the supplementary archive for readers of the paper
`share/make_bundle.sh` builds `share/dist/lcvx-impossibility-supplement.zip` (paper, Lean project with `Verify.lean`,
TVC certificate scripts and notes, `README-bundle.md` as its README). `share/dist/` is not committed; rebuild it with the script.

### `comms/`: how the agents coordinated
The work was done by an orchestrator and a team of specialist subagents (27 final reports) (provers, adversaries, red teams, Lean
formalizers, numerics, referees, paper writer). Everything they said to each other is here.

| Path | Contents |
|---|---|
| `PROTOCOL.md` | Rules: claim lifecycle, signing, compute budget. |
| `AGENTS.md` | Directory of agents and their roles. |
| `CLAIMS.md` | The claims registry: every claim with status CLAIMED / CONFIRMED / FORMALIZED / BROKEN / OPEN. |
| `BOARD.md` | Shared message board (append-only, signed posts). |
| `LOG.md` | Orchestrator decision log. |
| `threads/` | Focused discussions (6-DOF models, possibility, Theorem D). |
| `briefs/` | The exact brief given to each subagent. |
| `reports/` | Each subagent's final report. |

## Checking the results

**Lean proofs** (about 10 minutes; needs [elan](https://github.com/leanprover/elan)):
```bash
cd lean/LcvxObstruction
lake exe cache get
lake build
lake env lean Verify.lean
```
Expected last line: `PASS: all 126 cited declarations exist and depend only on propext, Classical.choice, Quot.sound.`

**Pure-TVC certificates** (optional; Python with numpy, scipy, mpmath, python-flint, casadi; see
`share/requirements-certificates.txt`):
```bash
cd numerics/verify-tvc
python exact_cert.py 120 cone 0 1.5 100
```
The full command list is in `math/verify-tvc-report.md`, sections 7 and 9-11.

**Paper:** `cd paper && make share` (needs a TeX distribution with latexmk).

**Planner:** `cd solver && pytest`.

Python environments (`.venv/`) and Lean build caches (`.lake/`) are not committed; recreate them as above.

## Status and open problems
Machine-checked, proved, numerical and open results are listed claim by claim in `SYNTHESIS.md`. The main open items:
pure TVC at 7 s, with the 100 deg/s gimbal-rate limit and with mass depletion (nonconvex numerically, unproved); the
hop-ring hole at GTPL constants; the CSD2' residual class; convergence of planner B. The paper has not been peer reviewed.
