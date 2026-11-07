# [lean-tvc] final report: pure TVC (FLAT, TVC-1 skeleton) and B* with mass depletion

Project: `lean/LcvxObstruction` (Lean 4 v4.36.0-rc2 + Mathlib, unchanged manifest). Build:
`source ~/.elan/env && cd lean/LcvxObstruction && lake build` → green. No `sorry`, no new `axiom`.
Faithfulness map: `lean/TVC.md`. Axiom check: `lake env lean LcvxObstruction/TVC/Axioms.lean` → every theorem listed there
reports `[propext, Classical.choice, Quot.sound]`.

## Outcome by goal

| Goal | Status | Main Lean names |
|---|---|---|
| 1. FLAT (centre of percussion) | **DONE.** Zero-roll identity (in `Fin 3 → ℝ` and in `EuclideanSpace ℝ (Fin 3)`), the roll-rate version with the gyroscopic term, roll-rate conservation, and the boundary translation `F_TVC = F_y − shift`. | `TVC.cop_identity`, `TVC.cop_identity_E3`, `TVC.cop_identity_roll`, `TVC.euler_roll_const`, `TVC.convex_tvcSet_iff` |
| 2. TVC-1 skeleton | **DONE.** S-procedure/Finsler in finite dimensions, separability over tilt components, the rotation-midpoint argument with the Theorem A link, and a concrete pure-TVC landing-set model with `R_π` invariance, ordinary ⊆ relaxed and the landing identity. Numerics enter only as `structure TVC1Certificate`, documented as verified by `numerics/verify-tvc/exact_cert.py` and `moment_check.py`. The analytic reduction (math/06 §4.0–4.4, Lemma 4.6′) enters as `structure TVC1Reduction`. **That reduction is not formalized.** | `TVC.sprocedure_finsler(_sum)`, `TVC.gain_le_of_certificate`, `TVC.tvc1_skeleton`, `TVC.tvc1_main`, `TVC.tvc1_model` / `TVC.tvc1_model_ctrl` (concrete sets; reduction stated for controls, gain `W_z(u) − J₀`), `TVC.tvcLandingSet_rot`, pointwise lemmas in `TVC/Pointwise.lean` |
| (extra) quantitative B* | **DONE** for constant bounds, δ ≤ π/4 (Step 7): `η₀/(1+s*) ≤ dist(θ_m, F)`, `θ_m ∉ closure F`. | `lambda_dist_ge`, `landingSet_dist_ge`, `midpoint_not_mem_closure_landingSet` |
| 3. B* with mass depletion α > 0 | **DONE, beyond scope:** every horizon, plus upright landing, kinematic 6DOF, and free final time on compact windows. | `no_lossless_relaxation_constrained_5dof_mass`, `…_upright_5dof_mass`, `…_6dof_mass`, `…_upright_6dof_mass`, `no_lossless_relaxation_freeTime_5dof(_mass)`, non-vacuity `constrainedLandingSet_mass_nonempty` |

## B* with α > 0: what broke, and the fix

- **What broke.** The constant-bound proof compares every competitor with the pointwise bound
  `h* = (s−s*)a_min cos(δ+ωs)` on the dive and `(s−s*)a_max` on the brake. With ṁ = −αT, no single
  throttle history attains both bounds, so `V* = ∫h*` is not attained and the witness midpoint is not `V* e_z`.
- **Core restated** (`PhiMax_not_mem_WSet`). The proof now uses the competitor's own acceleration:
  `PhiFace(a) = ∫a·φ`. It works for any class that contains a maximiser of PhiFace.
- **Explicit maximiser** for `AccMass`, with no weak-* compactness (math/02 §10.3 Steps 3–4):
  - *Dive identity* (`dive_identity`): `∫₀^{s*} c·T/m = α⁻¹(c(0) log m₀ + ∫ c′ log m)`. It is proved by integration by parts for
    absolutely continuous functions (Mathlib `AbsolutelyContinuousOnInterval`), using Lebesgue differentiation of `m` and the fact
    that `log` is Lipschitz on `[m_dry,∞)`. Since `c′ ≤ 0`, the dive value increases with the mass history.
  - *Comparison* (`exists_sigma_compare`): fix `m(s*)`. Among all histories with that value, min throttle on `[0,σ]` followed by
    max throttle has the pointwise largest mass on `[0,s*]`.
  - *Brake bound* (`brake_le`).
  - *Continuity* (`continuous_wval`): the switch value `w(σ)` is continuous, so it attains its maximum at some `σ*`.
- **Hypotheses:** `0 < ρ₁ < ρ₂`, `α > 0`, `0 < m_dry ≤ m₀ − αρ₂ t_f` (a full-throttle burn stays above dry mass; this is
  verify-imp's window condition), `0 ≤ g₀ < ρ₂/m₀`, `0 < δ < π/2`, `ω > 0`, `tanγ ≥ 0`, and any `X ⊇` glide cone.

## Honest scope / not formalized

- **TVC-1.** Lean checks the logic, the finite-dimensional S-procedure step, and the model-level structure (`R_π` invariance,
  `F^X ⊆ F ⊆ F^rel`, landing identity). Not formalized, and entering as named hypotheses:
  - the reduction of an arbitrary relaxed competitor to certificate data: localization, majorants, torque remainders, moments,
    bathtub, and the Wirtinger discretization (`TVC1Reduction`);
  - the certified matrix and scalar inequalities (`TVC1Certificate`);
  - the witness (`hw`, `hGw`).

  In the concrete model (`TVC/Model.lean`), the attitude ODE appears in integral form as a constraint on `(b, ḃ, u)`. The
  translational dynamics is `r̈ = u − g₀e_z` in closed form. Roll is held (`ω₃ ≡ 0`), mass is constant, and the gimbal rate is
  unlimited.
- **FLAT.** The identity is proved as a pointwise algebraic identity with constant ε. Varying ε(m) is not covered. The FLAT
  identity is not wired into `TVC/Model.lean`, since the model uses `r̈ = u − g₀e_z` directly.
- **B\*.** The quantitative bound (Step 7) is formalized for constant bounds only, not for the mass class. The envelope version (§10.6) is not formalized. `ρ₁ = ρ₂` is excluded only for
  convenience.
- **Stale docs.** `lean/MODEL.md` §6 and `comms/reports/lean.md` still list "B* with α > 0" as a gap. Those files belong to
  [lean], so I did not edit them. `lean/TVC.md` §3 supersedes that bullet.

## Files (all committed, no AI attribution)
`lean/LcvxObstruction/LcvxObstruction/TVC/{CentreOfPercussion,Certificate,Pointwise,Model,Axioms}.lean`,
`lean/LcvxObstruction/LcvxObstruction/{DiveBrakeMass,DiveBrakeMassModel,DiveBrakeMassVariants,FreeTimeBStar,DiveBrakeQuant}.lean`,
root imports in `lean/LcvxObstruction/LcvxObstruction.lean`, `lean/TVC.md`, `comms/briefs/lean-tvc.md`, this report.
`comms/CLAIMS.md` rows B*, P-B*, FLAT, TVC-1 were updated (status column), and BOARD milestones were posted. Both files are
shared and contain other agents' uncommitted edits, so I left them for the orchestrator to commit.
