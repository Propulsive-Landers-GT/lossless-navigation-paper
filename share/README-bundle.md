# Supplementary archive: impossibility of lossless convexification for 5-DOF / 6-DOF powered descent, and a sound single convex program

This archive accompanies the paper `paper.pdf`. It contains everything needed to check the paper's
machine-checked and computer-assisted results.

```
paper.pdf                 the paper
lean/                     Lean 4 / Mathlib formalization
  LcvxObstruction/        the Lake project (build here)
    Verify.lean           one-command audit of every cited theorem
  MODEL.md, POSITIVE.md,  maps from each Lean definition to its mathematical meaning
  SLICE.md, SOLVER.md, TVC.md
certificates/             computer-assisted proofs for the pure-TVC (gimbal-torque) model
  proof-tvc/              certificate construction: scripts, multipliers, witnesses
  verify-tvc/             independent exact-arithmetic re-verification
  notes/                  derivation (06-pure-tvc.md) and verification log (verify-tvc-report.md)
  requirements.txt
landing/                  the sound single convex program (paper Section 4.5, Section 6.3, Appendix E)
  LANDING-ALGORITHM.md    the algorithm in plain terms, with the vehicle's constants
  math/10-landing-proof.md  Theorem F and its proof, each lemma tied to a test
  AUDIT-2026-11.md        audit of the impossibility result; mistakes found; follow-up questions
  solver/                 code (gtpl_guidance/), tests, experiment scripts, results, RESULTS-FLAT.md
```

## 1. The machine-checked theorems (about 10 minutes)

```bash
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh     # installs Lean's version manager, if needed
cd lean/LcvxObstruction
lake exe cache get                                         # prebuilt Mathlib (~5 GB download)
lake build
lake env lean Verify.lean
```

`Verify.lean` prints the headline statements and finishes with
`PASS: all 126 cited declarations exist and depend only on propext, Classical.choice, Quot.sound.`
It reports an error if any cited declaration is missing or relies on `sorry` or any other axiom.

Start with these definitions and theorems:

- `UniformConvexRelaxation`, `IsLossless` in `Abstract.lean`: what "a lossless convex relaxation" means.
- `not_isLossless_of_not_convex` (`Abstract.lean`): a lossless relaxation forces the feasible set to be convex.
- `no_lossless_relaxation_constrained_{5dof,upright_5dof,6dof,upright_6dof}` (`Main.lean`, `Upright.lean`):
  the Main Theorem.
- `gtpl_no_lossless_upright_6dof_mass` (`GTPLMass.lean`): the same result at the vehicle's constants
  (400-1000 N, 79.88 / 55.88 kg, Isp 180 s, 15 degree gimbal cone, any burn up to 42 s), with mass depletion.

## 2. The computer-assisted pure-TVC certificates (optional)

These establish the paper's pure-TVC results (Section 3.8: horizons of 1 and 2 s, and 3 and 5 s with a tilt cap;
constant mass, unlimited gimbal rate). They are not part of the Lean development.

```bash
cd certificates
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd verify-tvc
../.venv/bin/python exact_cert.py 120 cone 0 1.5 100     # t_f = 1 s: exact PSD check + remainders
../.venv/bin/python moment_check.py 120 cone 0 1.5 100   # t_f = 1 s: moment term and final margin
../.venv/bin/python witness_check.py cone 1              # t_f = 1 s: witness gain in interval arithmetic
```

The full list of commands, including the Riccati certificates for 2, 3 and 5 s (`riccati_exact.py`,
`loc_check2.py`, `TF=... witness_check.py`), and the expected outputs, are in
`notes/verify-tvc-report.md` (sections 7 and 9-11). The mathematics behind each certificate is in
`notes/06-pure-tvc.md`. Both notes are working documents from the project and refer to other project files by
their original paths.

## Status of each result

The paper tags every result as Lean-checked, proved (pen-and-paper), proved (computer-assisted),
numerical evidence only, or open. Only the Lean-checked results are verified by step 1.

## 3. The sound single convex program (optional)

Theorem F of the paper (Section 4.5) is proved on paper in Appendix E and in `landing/math/10-landing-proof.md`. It is not
machine-checked, apart from its first step (`TVC.cop_identity` in the Lean project). What can be checked here is that the
code does what the theorem says, and the paper's benchmark numbers.

```bash
cd landing/solver
```
```bash
python3 -m venv .venv && .venv/bin/pip install numpy scipy cvxpy clarabel ecos casadi matplotlib pytest
```
```bash
OMP_NUM_THREADS=1 .venv/bin/python -m pytest -q
```
```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/example_landing.py
```
```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/replay_flat.py
```
```bash
OMP_NUM_THREADS=1 .venv/bin/python scripts/stress_flat.py
```
```bash
.venv/bin/python scripts/report_flat.py
```

- `pytest`: 27 tests; `tests/test_flat.py` checks each lemma of the proof numerically.
- `example_landing.py`: plans one descent with one SOCP and flies it closed loop with disturbances.
- `replay_flat.py`: feeds the planned throttle and gimbal commands to the full rigid body with no feedback; the landing error
  is at most a few tens of nanometres.
- `stress_flat.py`: 300 random problems, every plan evaluated at 1201 instants against the planning limits; expects no violation.
- `report_flat.py`: prints every table of `RESULTS-FLAT.md` (and of the paper's Section 6.3) from the stored results. The
  commands that regenerate those results (about two hours on four cores) are listed at the top of `RESULTS-FLAT.md`.

The paths inside `landing/` are those of the project repository with `solver/` kept as is; `LANDING-ALGORITHM.md` and
`AUDIT-2026-11.md` refer to `math/`, `lean/` and `paper/` by their repository paths.
