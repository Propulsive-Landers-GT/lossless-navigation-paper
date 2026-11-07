# Lean blueprint: positive side (fixed-attitude LCvx)

Author: [positive]. Source: `math/04-positive-results.md` (§2, §4, §5, §7, §8, §10).
Conventions follow `lean/LcvxObstruction/LcvxObstruction/Sphere.lean`: a general real inner-product space
`V` (`[NormedAddCommGroup V] [InnerProductSpace ℝ V]`), with `open scoped RealInnerProductSpace`.
Suggested module: `LcvxObstruction/Positive.lean`, namespace `LcvxPositive`.

**Only labelled hypothesis: PMP**, packaged as a `structure PMPData` (Tier 3) whose fields are exactly the
conclusions (i)–(ii) of (H-PMP) in `math/04` §5.1 that the proofs use. Aumann's theorem (§3 of math/04) is
**not** in Mathlib and is **out of scope**. C-W, C-F and C-U are therefore not Lean targets. Everything below is elementary.

Difficulty: ★ = a few lines, ★★ = routine, ★★★ = needs measure-theory plumbing.

---

## Tier 1 — pointwise finite-dimensional lemmas (the core; formalize first)

```lean
/-- The relaxed cap: ‖T‖ ≤ Γ and ⟪b,T⟫ ≥ c (c = Γ cos δ in applications). -/
def cap (b : V) (Γ c : ℝ) : Set V := {T | ‖T‖ ≤ Γ ∧ c ≤ ⟪b, T⟫}
```

| # | Name | Statement | Proof idea | ★ |
|---|---|---|---|---|
| P1 | `convex_cap` | `Convex ℝ (cap b Γ c)` | intersection of a ball and a half-space (`convex_closedBall`, `convex_halfSpace_ge`) | ★ |
| P2 | `mem_segment_ball_of_norm_lt` | `‖T*‖ < Γ → ∃ s₀ > 0, ∀ s ∈ Icc 0 s₀, ‖T* + s • (T - T*)‖ ≤ Γ` | triangle inequality; `s₀ = min 1 ((Γ-‖T*‖)/(‖T-T*‖+1))` | ★ |
| P3 | `normal_of_max_of_norm_lt` (**C-G**) | `Convex ℝ Q → T* ∈ Q → ‖T*‖ ≤ Γ → (∀ T ∈ Q, ‖T‖ ≤ Γ → ⟪y,T⟫ ≤ ⟪y,T*⟫) → ‖T*‖ < Γ → ∀ T ∈ Q, ⟪y, T - T*⟫ ≤ 0` | P2 + linearity: `s₀ * ⟪y,T-T*⟫ ≤ 0` | ★★ |
| P4 | `eq_neg_smul_of_normal_halfspace` (**Lemma H**) | `b ≠ 0 → c ≤ ⟪b,T*⟫ → (∀ T, c ≤ ⟪b,T⟫ → ⟪y,T-T*⟫ ≤ 0) → ∃ κ ≥ 0, y = -κ • b` | test `T* ± y⊥` with `y⊥ = y - (⟪y,b⟫/‖b‖²) • b`, and `T* + b` | ★★ |
| P5 | `norm_eq_of_isMaxOn_cap` (**C-3**, main) | `b ≠ 0 → IsMaxOn (fun T => ⟪y,T⟫) (cap b Γ c) T* → T* ∈ cap b Γ c → ‖T*‖ = Γ ∨ ∃ κ ≥ 0, y = -κ • b` | `by_contra`; P3 with `Q = {T \| c ≤ ⟪b,T⟫}`; P4 | ★★ |
| P6 | `isMaxOn_cap_unique` (**Lemma U**) | `b ≠ 0 → (¬ ∃ κ ≥ 0, y = -κ • b) → IsMaxOn … T₁ → IsMaxOn … T₂ → T₁ ∈ cap → T₂ ∈ cap → T₁ = T₂` | the midpoint is also a max (P1); P5 gives all three norms `= Γ`; `norm_add_sq_real`/parallelogram ⇒ `‖T₁-T₂‖² = 0` | ★★ |
| P7 | `isMaxOn_cap_of_neg_smul` (**Lemma S**, sharpness) | `‖b‖ = 1 → 0 ≤ κ → 0 ≤ Γ → IsMaxOn (fun T => ⟪-κ • b, T⟫) (cap b Γ (Γ * Real.cos δ)) ((Γ * Real.cos δ) • b)` and `‖(Γ cos δ) • b‖ < Γ` when `0 < δ < π/2`, `0 < Γ` | direct | ★ |
| P8 | `isMaxOn_slice_of_isMaxOn_joint` (**Lemma J**) | if `(T*,Γ*)` maximizes `⟪y,T⟫ - β Γ` on `{(T,Γ) \| T ∈ cap b Γ (Γ cos δ) ∧ ρ₁ ≤ Γ ∧ Γ ≤ ρ₂}` then `IsMaxOn (⟪y,·⟫) (cap b Γ* (Γ* cos δ)) T*` | restrict to the slice `Γ = Γ*` | ★ |
| P9 | `original_feasible_of_lossless` (**L8**) | `T ∈ cap b Γ (Γ cos δ) → ‖T‖ = Γ → ρ₁ ≤ Γ → Γ ≤ ρ₂ → ρ₁ ≤ ‖T‖ ∧ ‖T‖ ≤ ρ₂ ∧ ‖T‖ * cos δ ≤ ⟪b,T⟫` | rewrite | ★ |
| P10 | `not_extreme_of_norm_lt` (half of **Lemma X**) | `∃ d ≠ 0, ⟪b,d⟫ = 0` (true if `finrank ≥ 2`) `→ ‖T‖ < Γ → T ∈ cap → T ∉ (cap b Γ c).extremePoints ℝ` | `T ± ε•d` | ★★ |

Also optional: `extremePoints_cap` (= the spherical cap, using strict convexity of the norm) ★★.

## Tier 2 — primer-vector geometry (affine primer; C-D1)

```lean
def primer (a c : V) (t : ℝ) : V := a + t • c
def degenerate (a c : V) (b : ℝ → V) : Set ℝ := {t | ∃ κ ≥ 0, primer a c t = -κ • b t}
```

| # | Name | Statement | ★ |
|---|---|---|---|
| P11 | `primer_zero_subsingleton` | `(a,c) ≠ 0 → Set.Subsingleton {t \| primer a c t = 0}` | ★ |
| P12 | `degenerate_subset_of_dependent` | `c = s • a` (or `a = 0`) `→ degenerate a c b ⊆ {t \| primer a c t = 0} ∪ {t \| b t = e} ∪ {t \| b t = -e}` with `e = a/‖a‖` (resp. `c/‖c‖`), for unit `b` | ★★ |
| P13 | `degenerate_subset_of_independent` | `LinearIndependent ℝ ![a,c] → degenerate a c b ⊆ {t \| b t = -(‖primer a c t‖⁻¹) • primer a c t}`, for unit `b` | ★ |
| P14 | `norm_deriv_gnomonic` | for `β t = ‖a+t•c‖⁻¹ • (a+t•c)` in `ℝ³` (`EuclideanSpace ℝ (Fin 3)`): `‖deriv β t‖ = ‖a ×₃ c‖ / ‖a + t • c‖²` (state with `crossProduct` or as `√(‖a‖²‖c‖²-⟪a,c⟫²)`) | ★★ |
| P15 | `sup_angular_accel_gnomonic` | `x/(1+x²)² ≤ 3√3/16` for all real `x`, with equality at `x² = 1/3` | ★ |

## Tier 3 — time-varying Theorem C (strong form), with PMP as the only hypothesis

```lean
/-- Conclusions of PMP (H-PMP)(i)-(ii) actually used: affine primer + pointwise maximization. -/
structure PMPData (b : ℝ → V) (T : ℝ → V) (Γ : ℝ → ℝ) (δ tf : ℝ) where
  a : V
  c : V
  max_ae : ∀ᵐ t ∂(volume.restrict (Set.Icc 0 tf)),
    IsMaxOn (fun S => ⟪primer a c t, S⟫) (cap (b t) (Γ t) (Γ t * Real.cos δ)) (T t)
  mem_ae : ∀ᵐ t ∂(volume.restrict (Set.Icc 0 tf)), T t ∈ cap (b t) (Γ t) (Γ t * Real.cos δ)
```

| # | Name | Statement | ★ |
|---|---|---|---|
| P16 | `lossless_ae_off_degenerate` (**C-S(1)**) | `(∀ t, b t ≠ 0) → (h : PMPData b T Γ δ tf) → ∀ᵐ t ∂(volume.restrict (Icc 0 tf \ degenerate h.a h.c b)), ‖T t‖ = Γ t` | ★★ (filter plumbing; P5) |
| P17 | `lossless_ae_of_null_degenerate` (**C-S(4)**) | `+ volume (degenerate h.a h.c b ∩ Icc 0 tf) = 0 → ∀ᵐ t ∂(volume.restrict (Icc 0 tf)), ‖T t‖ = Γ t` | ★★ |
| P18 | `lossless_ae_of_ND` (**C-D2**) | if `(h.a,h.c) ≠ 0`, every level set of `b` is null (ND1), and for all independent `a',c'` the set `{t \| b t = gnomonic a' c' t}` is null (ND2), then the conclusion of P17 holds | ★★★ (P11–P13 + measure of a union) |
| P19 | `discrete_lossless_nodewise` (**C-K1**) | finite version: `∀ j : Fin N, IsMaxOn (⟪p j,·⟫) (cap (b j) (σ j) (σ j * cos δ)) (u j) → (¬ ∃ κ ≥ 0, p j = -κ • b j) → ‖u j‖ = σ j` | ★ (P5 per node) |

The min-throttle parts C-S(2)–(3) need PMP's Hamiltonian minimization over Γ as well. They are optional, with
`PMPData` extended by a field `minΓ : ∀ᵐ t, IsMinOn (fun G => (λ₀ + κ t * cos δ / m) * G) (Icc ρ₁ ρ₂) (Γ t)`.
Then use the one-line fact `0 < coeff → IsMinOn (coeff * ·) (Icc ρ₁ ρ₂) G → G = ρ₁` ★.

## Tier 4 — PMP-free finite-dimensional results

| # | Name | Statement | ★ |
|---|---|---|---|
| P20 | `exchange_min_throttle` (**C-E(a)**, discrete) | Let `Feas : (Fin N → V) → (Fin N → ℝ) → Prop` be such that `Feas u σ ↔ (∀ j, u j ∈ cap (b j) (σ j) (σ j * cos δ) ∧ ρ₁ ≤ σ j ∧ σ j ≤ ρ₂) ∧ Dyn u` (dynamics depend on `u` only, constant mass). If `(u,σ)` minimizes `∑ j, σ j` over `Feas`, and `0 ≤ cos δ`, then `∀ j, ‖u j‖ < σ j → σ j = ρ₁` | ★★ (replace `σ j` by `max ρ₁ ‖u j‖`) |
| P21 | `purification_count` (**C-K2**, no state constraints) | Let `L : (Fin N → V) →ₗ[ℝ] W` with `finrank W = m`. Let `S = {u \| (∀ j, u j ∈ cap (b j) (σ j) (σ j*cos δ)) ∧ L u = y}`. If `ū ∈ S.extremePoints ℝ` and each `b j` has a 2-dim orthogonal complement (`finrank V = 3`, `b j ≠ 0`), then `2 * #{j \| ‖ū j‖ < σ j} ≤ m` | ★★★ (rank–nullity on `⨁_{j∈J} (b j)ᗮ`) |
| P22 | `bilinear_restriction` (CCP validity; supports deferred algorithms) | `⟪w,u⟫ ≥ ¼ (‖w₀+u₀‖² + 2 ⟪w₀+u₀, (w+u)-(w₀+u₀)⟫) - ¼ ‖w-u‖²`, with equality at `(w,u)=(w₀,u₀)`. Hence the convex constraint "RHS ≥ σ cos δ" implies `⟪w,u⟫ ≥ σ cos δ` | ★ (polarization `⟪w,u⟫ = ¼‖w+u‖² - ¼‖w-u‖²` and `‖x‖² ≥ ‖x₀‖² + 2⟪x₀,x-x₀⟫`) |

## Tier 5 — TVC coupling (M3b), optional

| # | Name | Statement | ★ |
|---|---|---|---|
| P23 | `torque_balance_iff` (**Lemma 8.1**) | in `ℝ³`, for unit `b`: `b ×₃ B = (1/k) • (T ×₃ b) ↔ T - ⟪b,T⟫•b = -k • (B - ⟪b,B⟫•b)`, where `B` stands for `b̈` | ★★ |
| P24 | `throttle_interval` (**C-6**) | for `F ⊥ b`, `‖F‖ = κ`: `(ρ₁ ≤ ‖Ta•b+F‖ ≤ ρ₂ ∧ angle (Ta•b+F) b ≤ δ) ↔ Ta ∈ Icc (max (κ*cot δ) √(ρ₁²-κ²)₊) √(ρ₂²-κ²)` (for `0<δ<π/2`, `κ ≤ ρ₂`; the `κ=0` case needs `Ta>0` separately) | ★★ |
| P25 | `sturm_comparison_sinh` (**C-Y core**) | `e` twice differentiable on `[0,tf]`, `e 0 = 0`, `deriv e 0 = η > 0`, `e'' t = q t * e t` with `q t ≥ μ² > 0` ⇒ `e t ≥ (η/μ) * sinh (μ t)` on `[0,tf]` | ★★★ (Wronskian `(e' w - e w')' ≥ 0`) |
| P26 | `thin_rates` (**C-Y**) | from P25 with `\|e tf\| ≤ 2δ`: `η ≤ 2 δ μ / sinh (μ tf)` | ★ |

## Suggested order
P1 → P2 → P3 → P4 → P5 (headline lemma) → P6, P7, P9 → P19 (discrete headline) → P11–P13 → P16, P17 →
P20 → P22 → P25, P26 → P21 → P18.
**Headline targets:** P5 (pointwise Lemma-3 analog, no hypotheses), P19 (discrete nodewise LCvx),
P17 (continuous-time strong Theorem C under `PMPData`), P20 (PMP-free min-throttle exchange).
