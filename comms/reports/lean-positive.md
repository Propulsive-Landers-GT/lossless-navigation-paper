# Report: [lean-positive]

Brief: comms/briefs/lean-positive.md. Full theorem-to-paper map with caveats: lean/POSITIVE.md.

## What is machine-checked
Lean 4 (v4.36.0-rc2) + Mathlib. All files are under lean/LcvxObstruction/LcvxObstruction/Positive/, namespace `LcvxPositive`. None contains `sorry` or `axiom`.

| File | Content |
|---|---|
| Cap.lean | Tier 1: C-G, Lemma H, **C-3** (general space), U, S (+ the exceptional case also has a lossless maximizer), J, L8, Lemma X (extreme points), compactness/existence, **`C3_headline`** (ℝ³) |
| Primer.lean | C-D1(a)(b)(c), ND1/ND2 ⇒ `|D ∩ [0,tf]| = 0`, P15 (`x/(1+x²)² ≤ 3√3/16`, equality) |
| PMP.lean | `structure PMPConclusion` (H-PMP (i)–(ii)); affine primer; C-S(1), C-S(2) (α=0), C-S(3) (α=0), C-S(4) (weak form), C-D2 |
| Discrete.lean | C-K1 nodewise test; ZOH closed form + affine discrete primer; C-E(a) discrete; **C-K2 purification** (general codimension form, existence of a purified optimum, ≤3 lossy nodes in ℝ³) |
| Bilinear.lean | P22: CCP lower model, equality at the base point, convexity of the restricted set, iterate feasibility |
| TVC.lean | Lemma 8.1 (coordinates), P24 throttle interval, **C-6 pointwise convexity**, Cor. 8.2 |
| Convexity.lean | Continuous-time convex feasible-data framework (closed-form dynamics), **C-6 trajectory-level** (F^{M3b}(b) convex), `AumannInstance` hypothesis, **C-W(1)** and **C-F** (constant mass) |
| Axioms.lean | `#print axioms` for 35 main theorems. All report `[propext, Classical.choice, Quot.sound]` |

## Hypotheses
- PMP enters only as `PMPConclusion`, an argument to the theorems. Its fields are the adjoint ODEs and the a.e. Hamiltonian minimum condition. The ODEs are stated with `HasDerivAt` on ℝ; the solutions are affine, so this is equivalent.
- Aumann enters only as `AumannInstance`, a hypothesis of C-W(1)/C-F. It is the moment-matching instance used in math/04 §3, and it requires measurable `b` and a.e.-measurable bounded `Γ`.

## Gaps (Lean weaker than the paper)
C-S(2) is formalized only for α=0. C-S(4) gives lossless + pointwise P₀-feasible, not "P₀-optimal". C-E is discrete (a) only. C-K2's "random objective w.p. 1" is missing. C-W covers feasibility part (1) only, at constant mass. In C-6, Lemma 8.1 and the convexity theorem are joined only in prose. Not formalized at all: C-D3, C-D4, C-X, C-U, C-3D, C-Y (Sturm comparison P25–P26), P14.

## Blueprint audit
No lemma of math/05 is false. P24's remark that "the κ=0 case needs Ta>0 separately" is unnecessary with the inner-product cone constraint and 0 ≤ ρ₁. The blueprint's P21 needed a two-sided-direction subspace `M` to state the Σc_i version; the formal statement adds it.

## Coordination
The root import file was not edited. [lean] has been asked to add the `LcvxObstruction.Positive.*` imports. I built only my own modules (`lake build LcvxObstruction.Positive.<M>`).
