# 5DOF / 6DOF Lossless Convexification — research workspace

Goal: either prove that lossless convexification (LCvx) extends to the 5DOF (and 6DOF) powered-descent
problem for the GTPL monoprop lander, or prove that it cannot — and machine-check the result in Lean 4 / Mathlib.

## Layout
| Path | Contents |
|---|---|
| `comms/LOG.md` | Orchestrator decision log (append-only) |
| `comms/BOARD.md` | Shared message board between agents (append-only, signed) |
| `comms/briefs/` | Exact brief given to each subagent |
| `comms/reports/` | Final report from each subagent |
| `context/` | GTPL vehicle parameters and existing guidance stack |
| `literature/` | Literature review, bibliography |
| `math/` | Model catalog, proofs, verification reports |
| `numerics/` | Python experiments (reachable sets, counterexamples, algorithms) |
| `lean/LcvxObstruction/` | Lean 4 + Mathlib formalization |
| `paper/` | Paper draft (LaTeX) |

Start with `math/00-model-catalog-and-proof-sketch.md`.
