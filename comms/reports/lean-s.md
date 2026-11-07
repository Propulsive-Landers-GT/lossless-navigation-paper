# Report: [lean-s] (A-opt / Prop T, Lemma W, Lemma S, Theorem D with hard landing)

Files: `lean/LcvxObstruction/LcvxObstruction/Slice/{AOpt,Affine,Wirtinger,Master,LemmaS,Axioms}.lean`,
`lean/SLICE.md` (faithfulness map), root imports `Slice.AOpt`, `Slice.LemmaS`.
Full `lake build` green. No `sorry`, no `axiom`. All headline theorems: `[propext, Classical.choice, Quot.sound]`.

## Formalized
1. **Theorem A-opt and Prop T (abstract), math/redteam-lift.md §7** (`AOpt.lean`).
   - Mixing lemma: `mixing`, `mixing_finset`.
   - A-opt: `CostRelaxation.aOpt`, `aOpt_finset`.
   - "V = V** on F" in convex-envelope form: `value_le_convexCombination`.
   - Corollary T-abstract: `no_valueLossless_of_strict`.
   - Theorem D with a general readout cost f∘ρ + convex penalty: `StateLinearRelaxation.lossy_of_gap`. [lean] confirmed that TheoremD.lean already covers the ‖ρy−q‖+P case (`minError_lossy`).
2. **Lemma W** (`Wirtinger.lean`).
   - `periodic_wirtinger`: AC functions with an L² a.e. derivative. Uses Mathlib Parseval on AddCircle plus AC integration by parts.
   - `wirtinger_scalar`: ‖P^⊥g‖² ≤ (T/2π)²∫g'².
   - `wirtinger_lipschitz`: ω-Lipschitz paths into ℝⁿ, any n; ‖P^⊥β‖² ≤ (T/2π)²ω²T.
   - The L² affine-projection layer is in `Affine.lean`.
3. **Prop M, master inequality** (`Master.lean`).
   - Model M1 from Model.lean, α = 0, throttle box [a₁, a₂], any δ, any 3D attitude path.
   - `master_inequality` (C_m = A'κ/(κ−A')) and `master_inequality_fixed` (C_m = A').
   - Landing identities from vertical data: `landing_moments`. Dents: `dent`, `dent_fixed`.
   - Constants are math/07's variant (c): c̄(T), no E₄, δ_e = √(2−2cos δ).
4. **Lemma S and Theorem D with hard v(t_f)=0** (`LemmaS.lean`), for one explicit instance.
   - Instance: a ≡ 12 m/s², g₀ = 9.81, δ = 0, ω = 0.1 rad/s, T = 3 + 10(1−cos 0.1)/sin 0.1 ≈ 3.50 s.
   - `lemmaS` proves:
     - the data ζ_w are vertical, and ωT < π/2, a₁cos(ωT) > g₀;
     - the witness offsets p_w(u) lie in L(ζ_w) with the altitude constraint r_z ≥ 0, for every horizontal unit u;
     - every landing offset satisfies ‖p‖ ≥ 1 m, for any admissible 3D path (coning included) and any state constraint;
     - for X ⊇ {r_z ≥ 0}: 0 ∈ conv L, 0 ∉ cl L, and L is not convex.
   - `theoremD_hard_landing`: every state-linear relaxation containing L(ζ_w) has relaxed min-error 0 at target 0, while every genuine landing has error ≥ 1 m.

## Deviations from the blueprint (no BREAK: no blueprint step was found false)
- Witness: a "hold" S-turn (tilt up to A, back to −A, hold) instead of math/07's IVT single-crossing S-turn. Its I_h = 0 condition is explicit, h = (1−cos A)/(ω sin A). Mean-square tilt is ≈0.035Ω² against the Wirtinger cap 0.0253Ω², the same mechanism with a smaller margin. True dent ≈ 1.38 m; Lean proves 1 m.
- Numerics are done by Mathlib Taylor bounds (`Real.sin_bound`, `Real.cos_bound`, `pi_gt_d2`) on rational arithmetic (`numeric_core`).

## Gaps (not formalized)
- Mass depletion α > 0 in Prop M (E₄, ε_m terms).
- The throttle instance and the math/07 §4 table rows. The master inequality and dent are formalized for throttle; the explicit instance is fixed-thrust.
- Glide slope for the witness; the M1 facts F1–F5 behind Prop T (only the abstract corollary is formalized).
- Physical scope: the instance has min-throttle T/W ≈ 1.22 (cannot hover at min throttle). GTPL is not covered; the GTPL dive-brake S remains numerical (S-GTPL).
