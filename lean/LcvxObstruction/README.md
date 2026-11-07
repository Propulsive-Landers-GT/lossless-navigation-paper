# LcvxObstruction

Lean 4 / Mathlib formalization for the paper *On the Impossibility of Lossless Convexification for
Attitude-Rate-Limited (5-DOF and 6-DOF) Powered Descent*.

- Toolchain: `leanprover/lean4:v4.36.0-rc2` (pinned in `lean-toolchain`); Mathlib pinned in `lake-manifest.json`.
- No `sorry`, no `axiom`, no `native_decide` anywhere in the sources.

## Check it

```bash
# 1. Install elan (the Lean version manager) if you don't have it:
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh

# 2. In this directory: download prebuilt Mathlib, then build the project (a few minutes).
lake exe cache get
lake build

# 3. Print the headline statements and audit the axioms of every declaration cited in the paper.
lake env lean Verify.lean
```

The last command ends with

```
PASS: all 126 cited declarations exist and depend only on propext, Classical.choice, Quot.sound.
```

and fails with an error if any cited declaration is missing or depends on any other axiom. (A `sorry` would
show up as the axiom `sorryAx`.)

## Where the main results are

| Result | Lean name | File |
|---|---|---|
| Lossless forces convexity (Theorem A) | `not_isLossless_of_not_convex`, `theoremA` | `LcvxObstruction/Abstract.lean` |
| Main Theorem, 5-DOF, altitude/glide slope, every horizon | `no_lossless_relaxation_constrained_5dof` | `LcvxObstruction/Main.lean` |
| Main Theorem, upright landing and kinematic 6-DOF | `no_lossless_relaxation_constrained_{upright_5dof,6dof,upright_6dof}` | `LcvxObstruction/Upright.lean` |
| With explicit mass depletion | `no_lossless_relaxation_constrained_*_mass` | `LcvxObstruction/DiveBrakeMass*.lean` |
| Free final time on a window | `no_lossless_relaxation_freeTime_5dof(_mass)` | `LcvxObstruction/FreeTimeBStar.lean` |
| Instance at the vehicle's constants | `gtpl_no_lossless_upright_6dof_mass`, `gtpl_no_lossless_freeTime_mass` | `LcvxObstruction/GTPLMass.lean` |

The definitions a reader should check first are `UniformConvexRelaxation` and `IsLossless`
(`LcvxObstruction/Abstract.lean`). The notes `../MODEL.md`, `../POSITIVE.md`, `../SLICE.md`, `../SOLVER.md` and
`../TVC.md` map every Lean definition to its mathematical meaning, so you can confirm the formal statements say what
the paper claims.
