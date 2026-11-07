# Positive side: Lean formalization map

Author: [lean-positive]. Lean project: `lean/LcvxObstruction`, toolchain `leanprover/lean4:v4.36.0-rc2`,
Mathlib `v4.36.0-rc2`. All files are in `LcvxObstruction/Positive/`, namespace `LcvxPositive`.
Check a file with `lake env lean LcvxObstruction/Positive/<File>.lean` from `lean/LcvxObstruction`.
The files are **not yet** in the root import list `LcvxObstruction.lean`. [lean] owns that file and will add them.

**Hypotheses policy.** The files contain no `sorry` and no `axiom`. Two external theorems appear,
each only as an explicit hypothesis:
* **PMP**, as `structure PMPConclusion`. Its fields are (H-PMP)(i)–(ii) of `math/04` §5.1: the adjoint ODEs `λ̇_r = 0`, `λ̇_v = -λ_r` and the
  a.e. minimum condition on the control-dependent Hamiltonian `λ₀Γ + ⟪λ_v,T⟫/m − αλ_mΓ` over `U(t)`.
* **Aumann's theorem**, as `def AumannInstance`. This is the single instance used in C-W: every admissible selection of
  `cl conv S_Γ(b)` has an admissible selection of `S_Γ(b)` with the same moments `∫T` and `∫(tf−t)T`.

`#print axioms` output for every main theorem is in §3. Each reports exactly
`[propext, Classical.choice, Quot.sound]`.

## 1. Theorem map

| math/04 | Lean theorem (file) | Status / how it compares to the paper |
|---|---|---|
| §2 C-G (general extreme-point lemma) | `normal_of_max_of_norm_lt` (Cap) | **Equal.** Any real inner-product space, any convex `Q`. |
| §2 Lemma H | `eq_neg_smul_of_normal_halfspace` (Cap) | Equal. |
| §2 **C-3** | `norm_eq_or_antiRay_of_isMaxOn_cap`, `norm_eq_of_isMaxOn_cap` (Cap) | **Equal.** Any space, `b ≠ 0`, any `Γ, c`, as the paper remarks. |
| §2 Lemma U | `isMaxOn_cap_unique` (Cap) | Equal. |
| §2 Lemma S (sharpness) | `isMaxOn_cap_of_antiRay`, `norm_lt_of_sharp` (Cap) | Equal. Also `isMaxOn_cap_of_antiRay_boundary`: in the exceptional case there is also a norm-Γ maximizer, so uniqueness genuinely fails. |
| §2 C-3 headline in ℝ³ | `C3_headline` (Cap) | `EuclideanSpace ℝ (Fin 3)`, `‖b‖=1`, `0<δ<π/2`, `Γ>0`. Proves (1) a maximizer exists, (2) off `−ℝ≥0 b` it is lossless, (3) it is unique, (4) on `−ℝ≥0 b` (including `y=0`) a lossy maximizer exists. |
| §2 Lemma J | `isMaxOn_slice_of_isMaxOn_joint` (Cap) | Equal. |
| §2 L8 | `original_feasible_of_lossless` (Cap) | Equal. |
| §2 Lemma X | `extremePoints_cap`, `not_mem_extremePoints_of_norm_lt`, `mem_extremePoints_of_norm_eq` (Cap); `cap_subset_closure_convexHull_sCap` (Convexity) | Equal, given the hypothesis "some `d ≠ 0` with `d ⊥ b` exists" (true when dim ≥ 2; `exists_perp_three` proves it in ℝ³). The hull form uses Mathlib's Krein–Milman. It is stated with `closure (convexHull …)`, which is enough for C-W. |
| §2 compactness/existence | `isCompact_cap`, `exists_isMaxOn_cap` (Cap) | Extra. |
| §5.3 C-D1(a) | `primer_zero_subsingleton` (Primer) | Equal. |
| §5.3 C-D1(b) | `degenerate_subset_of_dependent` (Primer) | Equal. Uses `¬ LinearIndependent ℝ ![a,c]` with `(a,c) ≠ 0`, unit `b`. |
| §5.3 C-D1(c) | `degenerate_subset_of_independent` (Primer) | Equal. Gnomonic line `−(a+tc)/‖a+tc‖`. |
| §5.3 ND1, ND2 ⇒ `|D|=0` | `ND1`, `ND2`, `volume_degenerate_eq_zero_of_ND` (Primer) | Equal. ND2 is quantified over all independent `(a',c')` with `+` sign, as in the paper; `−𝒜=𝒜` is proved inline. |
| §10 C-3D'(c) bound | `x_div_one_add_sq_sq_le`, `x_div_one_add_sq_sq_eq` (Primer) | Equal (`x/(1+x²)² ≤ 3√3/16`, equality at `x=1/√3`). |
| §5.1 affine primer | `PMPConclusion.neg_lamV_eq`, `lamR_eq` (PMP) | Equal. Derived from the adjoint ODEs, for any `b` and any mass. **Weaker hypothesis form:** the ODEs are assumed with `HasDerivAt` on all of ℝ, not as absolutely continuous a.e. solutions on `[0,tf]`. The solutions are affine, so after affine extension this is the same content. |
| §5.2 **C-S(1)** | `PMPConclusion.lossless_ae_off_degenerate` (PMP) | Equal: lossless and unique pointwise maximizer for a.e. `t ∉ D`. Any `α` (mass). Requires `m t > 0` and a.e. `ρ₁ ≤ Γ ≤ ρ₂`. |
| §5.2 C-S(2) | `PMPConclusion.min_throttle_of_primer_zero` (PMP) | **Constant mass only** (`α = 0`), with nontriviality `(λ₀,λ_r,λ_v) ≢ 0` as a hypothesis. The paper's `α>0` branch needs the `λ_m` adjoint and transversality, which are not formalized. |
| §5.2 **C-S(3)** | `PMPConclusion.min_throttle_of_antiRay`, `lossy_subset_degenerate_minThrottle` (PMP) | Equal (`α = 0`): `L ⊆ D ∩ {Γ = ρ₁}` a.e. |
| §5.2 **C-S(4)** | `PMPConclusion.lossless_ae_of_null_degenerate` (PMP) | **Weaker.** Proves lossless a.e. and *pointwise* `P₀`-feasibility a.e. (L8). It does not state "`P₀`-optimal", because that needs a formal problem-level definition of `P₀`/`P₁`. The optimality step is one line in the paper. |
| §5.3 **C-D2** | `PMPConclusion.lossless_ae_of_ND` (PMP) | Equal for the case `(a,c) ≠ 0`. The `p ≡ 0` alternative is C-S(2). |
| §5.3 C-D3, C-D4 (analytic criteria, meagre) | — | **Not formalized.** |
| §4 **C-E(a)** | `exchange_min_throttle` (Discrete) | **Discrete-time version** (cost `∑ w_j σ_j`, `w_j>0`, dynamics depending on `u` only). The continuous-time measure version is not formalized. |
| §4 C-E(b) (log-mass) | — | **Not formalized.** |
| §7 **C-K1** | `discrete_lossless_nodewise`, `isMaxOn_of_normal_joint` (Discrete) | Equal, given nodewise stationarity (KKT/Slater is assumed: normal-cone condition as hypothesis). |
| §7 ZOH primer affine | `zoh_v_eq`, `zoh_r_eq`, `zoh_pairing`, `zoh_primer_affine` (Discrete) | Equal. The ZOH recursion is solved in closed form, and the gradient of the terminal pairing is `h²(N−j−½)ν_r + hν_v`, affine in `j`. |
| §7 **C-K2** | `purification_count` (Discrete) | **Equal, general form:** `n·#lossy + dim M ≤ dim W` for an extreme point of `S = {u_j ∈ K_{σ_j}(b_j), Au ∈ X}`, `dim E = n+1`, `X` convex, `M` any subspace of two-sided feasible directions at `Aū`. With `M = lin F` this is `2#lossy ≤ Σ c_i`. |
| §7 C-K2 (≤ 3) | `exists_purified`, `purification_three` (Discrete) | Equal: a purified optimum exists (Krein–Milman), with ≤ 3 lossy nodes for a 6-dim terminal equality in ℝ³. Gives ≤ ⌊m/2⌋ for an `m`-dim equality, which is ≤ `n_x − 1` whenever `m ≥ 2`. The "random linear objective gives an extreme point with prob. 1" step is **not formalized**. |
| §3 **C-W(1)** | `relaxed_subset_original`, `original_subset_relaxed`, `origFeas_eq_relFeas` (Convexity) | Under `AumannInstance`: relaxed-feasible θ ⇔ original-feasible θ. **Scope:** constant mass, no nodewise state constraints, dynamics in closed (Cauchy) form, admissible = `T` and `(tf−t)T` integrable. C-W(2)–(4) (value/attainment, nodewise constraints, log-mass) are not formalized. |
| §3 **C-F** | `convex_origFeas`, `convex_relFeas` (Convexity) | Equal for constant mass, convex terminal set, measurable unit `b`, dim ≥ 2, under `AumannInstance`. The Taylor-convexified-mass variant is not formalized. |
| §8 Lemma 8.1 | `torque_balance_iff` (TVC) | Equal, in coordinates `Fin 3 → ℝ` with `⨯₃`, `⬝ᵥ` (`b⬝b = 1`, `k ≠ 0`). |
| §8 **C-6** | `throttle_interval`, `gimbal_bound_iff_cot`, `convex_tvcSet` (TVC); `convex_feasData_M3b` (Convexity) | Pointwise: the exact thrust set `{ρ₁≤‖T‖≤ρ₂, cone, Π_bT = F}` is the interval `κcosδ ≤ T_a sinδ, √(ρ₁²−κ²) ≤ T_a ≤ √(ρ₂²−κ²)` and is convex. Trajectory level: `F^{M3b}(b)` is convex (constant mass, closed-form dynamics, convex terminal set). `F` is a given function with `F ⊥ b`, and Lemma 8.1 identifies it as `−kΠ_b b̈`. These are linked in prose only: Lemma 8.1 is in `Fin 3 → ℝ` and C-6 is in a general inner-product space. The convexity of the fuel integrand is not stated separately. |
| §8 Cor. 8.2 | `tvcSet_upright` (TVC) | Equal. |
| §11 deferred CCP | `bilinear_restriction`, `bilinear_restriction_eq`, `convex_ccpSet`, `ccpSet_subset`, `mem_ccpSet_self` (Bilinear) | Equal (P22) plus the convexity of the restricted set and the feasibility/monotonicity of the iterates. |
| §5.4, §5.5, §6 C-X, §9 C-U, §10 C-3D, C-Y | — | **Not formalized.** C-Y needs the Sturm/Wronskian comparison P25–P26. C-X is a numerical/instance claim. C-U and C-3D are short set-theoretic arguments that were not prioritized. |
| blueprint P14 (gnomonic speed) | — | **Not formalized.** |

## 2. Places where Lean is weaker than the paper (summary)
1. PMP adjoint ODEs are assumed globally differentiable. The paper assumes absolutely continuous solutions with a.e. derivatives. The content is equivalent because the solutions are affine.
2. C-S(2): `α = 0` only, and the nontriviality hypothesis is phrased for `(λ₀,λ_r,λ_v)`.
3. C-S(4): "optimal for P₀" is reduced to pointwise feasibility a.e.
4. C-E: discrete-time (a) only. (b) is missing.
5. C-K2: the generic-objective uniqueness ("probability 1") claim is missing. Existence of a purified extreme point is proved.
6. C-W/C-F: constant mass, closed-form dynamics, no state constraints, Aumann as a hypothesis, only the feasibility statement (1).
7. C-6: Lemma 8.1 (coordinates) and the convexity theorem (abstract `F ⊥ b`) are not joined into one formal statement.
8. Not formalized: C-D3, C-D4, C-X, C-U, C-3D, C-Y, P14, P25, P26.

No blueprint lemma was found to be false. One minor mis-statement: P24's caveat ("the κ=0 case needs `T_a>0` separately") is unnecessary in the `⟪b,T⟫ ≥ ‖T‖cos δ` formulation. With `0 ≤ ρ₁` the interval form holds for all κ, including κ = 0.

## 3. `#print axioms` output
See `LcvxObstruction/Positive/Axioms.lean`. Output recorded on 2026-11-07:

```
'LcvxPositive.normal_of_max_of_norm_lt' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.eq_neg_smul_of_normal_halfspace' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.norm_eq_or_antiRay_of_isMaxOn_cap' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.isMaxOn_cap_unique' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.isMaxOn_cap_of_antiRay' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.isMaxOn_cap_of_antiRay_boundary' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.isMaxOn_slice_of_isMaxOn_joint' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.original_feasible_of_lossless' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.extremePoints_cap' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.C3_headline' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.primer_zero_subsingleton' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.degenerate_subset_of_dependent' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.degenerate_subset_of_independent' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.volume_degenerate_eq_zero_of_ND' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.x_div_one_add_sq_sq_le' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.neg_lamV_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.lossless_ae_off_degenerate' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.lossless_ae_of_null_degenerate' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.lossless_ae_of_ND' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.min_throttle_of_primer_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.PMPConclusion.lossy_subset_degenerate_minThrottle' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'LcvxPositive.discrete_lossless_nodewise' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.zoh_r_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.zoh_pairing' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.exchange_min_throttle' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.purification_count' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.purification_three' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.bilinear_restriction' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.convex_ccpSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.torque_balance_iff' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.throttle_interval' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.convex_tvcSet' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.convex_feasData_M3b' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.relaxed_subset_original' depends on axioms: [propext, Classical.choice, Quot.sound]
'LcvxPositive.convex_origFeas' depends on axioms: [propext, Classical.choice, Quot.sound]
```
