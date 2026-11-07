# Lean 4 / Mathlib blueprint for the impossibility results (math/02)

Author: [proof]. Audience: [lean]. Every lemma is stated with elementary hypotheses: inner products in `E3 := EuclideanSpace ℝ (Fin 3)`, `Real.cos`/`Real.sin`, interval integrals over `[0, tf]`, and measurability. Names in `code` refer to existing declarations in `lean/LcvxObstruction/` where they already exist (Abstract.lean, Sphere.lean, Model.lean as of 2026-11-07). Proof references are to sections of math/02.

Conventions: `⟪x,y⟫` is the real inner product. `ez = EuclideanSpace.single 2 1`. "unit" means `‖x‖ = 1`. All integrals are `∫ s in (0:ℝ)..tf` or `∫ s in Icc 0 tf` (pick one and stay with it). Functions are `ℝ → ℝ` or `ℝ → E3`.

PMP is never needed. The only analysis used is: monotonicity of the integral (`integral_mono_ae` / `setIntegral_mono_on`), `integral_inner` (inner product commutes with the Bochner integral), FTC for one explicit cos integral, and (Route R only) "a nonnegative integrable function with zero integral vanishes a.e." (`integral_eq_zero_iff_of_nonneg_ae`).

---

## 0. Definitions (D-series)

**D1 (model data).** Real numbers `tf ω δ ρ₁ ρ₂ α m₀ g₀` with `0 < tf`, `0 < ω`, `0 ≤ δ < π/2`, `0 < ρ₁ ≤ ρ₂`, `0 ≤ α`, `m₀ - α*ρ₂*tf > 0`. Gravity `g : E3`.

**D2 (admissible control, M1).** A triple `(T, d, b)` with
- `T : ℝ → ℝ` measurable, `∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂`;
- `d : ℝ → E3` (AE-strongly) measurable, `‖d s‖ = 1` on `Icc 0 tf`;
- `b : ℝ → E3` continuous on `Icc 0 tf`, `‖b s‖ = 1`, `b 0 = ez`;
- (AL) `∀ s s' ∈ Icc 0 tf, ω*|s - s'| ≤ π → Real.cos (ω*|s-s'|) ≤ ⟪b s, b s'⟫`;
- (gimbal) `∀ᵐ s ∂(volume.restrict (Icc 0 tf)), Real.cos δ ≤ ⟪d s, b s⟫`;
- variant T only: `b tf = ez`.
(Existing: `AttitudeAdmissible tf ω δ d b`. Add the T-fields or an abstract acceleration class `Acc`, as `AccLower`/`AccBox` already do.)

**D3 (mass and acceleration).** `m T s := m₀ - α * ∫ t in 0..s, T t` and `a T s := T s / m T s`. To start, the abstract interface `a ∈ AccLower tf a₁`, meaning `a` is measurable and `a₁ s ≤ a s` with `a₁` continuous, positive and monotone, is enough for every route. Lemma L4 discharges it for the mass model.

**D4 (increments and landing).** `I := ∫ a s • d s`, `J := ∫ (tf - s) * a s • d s`. Landing from `θ = (r₀, v₀)` means `v₀ + tf•g + I = 0 ∧ r₀ + tf•v₀ + (tf^2/2)•g + J = 0`. Taking this integrated form as the definition is justified by Lemma 1.1 of math/02. (Existing: `velocity`, `position`, `landingSet`, `reachSet`, `snd_image_landingSet`.)

**D5 (uniform convex relaxation, lossless).** `C : Set (Θ × Y)` convex. Lossless for `F` means `∀ θ, (∃ y, (θ,y) ∈ C) ↔ θ ∈ F`. (Existing: `UniformConvexRelaxation`, `IsLossless`, `theoremA`.)

**D6 (state-linear relaxation of one instance; Theorem D).** Data: `Y` a real vector space, `C : Set Y` convex, `ρ : Y →ᵃ[ℝ] E` affine (E is the readout space, e.g. `E3 × E3` for the terminal state), `P : Y → ℝ` convex on `C` with `0 ≤ P`, and the genuine set `Reach : Set E`. Embedding: `∀ x ∈ Reach, ∃ y ∈ C, ρ y = x ∧ P y = 0`. The relaxed value at a cost `φ : E → ℝ` (convex) is `⨅ y ∈ C, φ (ρ y) + P y`.
Comment block for the file: moment-lifted costs (e.g. Shor lifts `R ⪰ r rᵀ` with a cost linear in `R`) and occupation-measure LPs are *outside* D6, because their costs and terminal constraints are not functions of `ρ y`. This is the stated boundary of the impossibility.

**D7 (state constraints, for B\*).** `𝒳 := {(r,v) : 0 ≤ r.z ∧ tan γ * ‖r_h‖ ≤ r.z}`. To avoid trajectories, use the closed-form position from the integrals: `r t = r₀ + t•v₀ + (t^2/2)•g + ∫ s in 0..t, (t - s) * a s • d s`.

---

## 1. Abstract layer (A-series), done or nearly done
- **A1 `theoremA`.** Lossless ⇒ `F = Prod.fst '' C`, hence `Convex ℝ F`. ✔ (Abstract.lean)
- **A2 (affine data).** If `ψ : Θ ≃ᵃ[ℝ] Θ` and `C` is lossless for `ψ '' F`, then `Convex ℝ F`. ✔ (`convex_affine_image`)
- **A3 (ε-lossless).** If `F ⊆ fst '' C ⊆ {θ | infDist θ F ≤ ε}`, `θ₁ θ₂ ∈ F`, and `infDist (midpoint θ₁ θ₂) F > ε`, then False. Proof: convexity of `fst '' C`.
- **A4 (Theorem D, abstract).** Under D6, `∀ x ∈ convexHull ℝ Reach, ∃ y ∈ C, ρ y = x ∧ P y = 0`. Proof: induction over finite convex combinations (`convexHull_eq` / `Finset.centerMass`), using that `ρ` is affine and Jensen for `P` together with `P ≥ 0`. Corollary: `relaxedValue ≤ φ x` for `x ∈ convexHull Reach`.
- **A5 (rotation-midpoint).** If `S ⊆ E3×E3` is convex and invariant under `Rπ := diag(-1,-1,1)` acting on both factors, then `x ∈ S → midpoint x (Rπ x) ∈ S`, and the midpoint has zero lateral components. Elementary.
- **A6 (projection; math/02 Lemma 3.1).** `θ ∈ landingSet → -v₀ - tf•g ∈ reachSet`. ✔ (`snd_image_landingSet`). Also `Convex landingSet → Convex reachSet`. ✔

---

## 2. Sphere layer (S-series)
- **S1 (triangle, inner form).** Unit `x y z`, `0 ≤ α`, `0 ≤ β`, `α+β ≤ π`, `cos α ≤ ⟪x,y⟫`, `cos β ≤ ⟪y,z⟫` ⇒ `cos (α+β) ≤ ⟪x,z⟫`. ✔ `inner_triangle`. Proof idea (math/02 L4.1): `⟪x,z⟫ = pq + ⟪x',z'⟫ ≥ pq − √(1−p²)√(1−q²)`, then arccos monotonicity; or use Mathlib's `InnerProductGeometry.angle_le_angle_add_angle`, which is what [lean] uses.
- **S2 (equality case).** In addition `α+β < π`, `0 < β < π`, `⟪x,z⟫ = cos(α+β)` ⇒ `⟪x,y⟫ = cos α`, `⟪y,z⟫ = cos β`, and `x = cos α • y − (sin α / sin β) • (z − cos β • y)`. ✔ `inner_triangle_eq`, `inner_triangle_eq_lateral`. *Needed only for Routes R and B\*-qualitative.*
- **S3 (extremal direction; L4.2).** With `z = ez`, `y = b`, `x = d`, `φ ∈ (0,π)`: `b = cos φ • ez + sin φ • u` and `d = cos(δ+φ) • ez + sin(δ+φ) • u`, with `u := (sin φ)⁻¹ • (b − cos φ • ez)` horizontal and unit. ✔ (`lateral`, `norm_lateral`, `inner_lateral_pole`.)
- **S4 (rigidity; L4.5).** `b = cos ψ•ez + sin ψ•u`, `b' = cos ψ'•ez + sin ψ'•u'`, `u u'` horizontal unit, `0<ψ,ψ'<π`, `cos(ψ−ψ') ≤ ⟪b,b'⟫` ⇒ `u = u'`. Proof: `sin ψ sin ψ' (⟪u,u'⟫ − 1) ≥ 0`, then `‖u−u'‖² = 2 − 2⟪u,u'⟫`. ✔ `lateral_eq_of_inner_ge`.
- **S5 (support step for the ball bound).** Unit `c`, `‖x‖` arbitrary: `⟪x,c⟫ ≤ ‖x‖` (`real_inner_le_norm` + `‖c‖=1`). And `c = cos β • ez + sin β • n` ⇒ `⟪x,c⟫ ≤ x.z * cos β + sin β * ‖x_h‖`. (Used in B\*-Q, step 7(ii).)

## 3. Real-analysis layer (R-series)
- **R1 (cos monotone).** `0 ≤ x ≤ y ≤ π → cos y ≤ cos x`, strict if `x < y` (`Real.cos_lt_cos_of_nonneg_of_le_pi`).
- **R2 (MVT bounds).** For `0 ≤ x ≤ y ≤ π/2`: `cos x − cos y ≥ (y−x) * sin x`, and `cos x − cos y ≤ (y − x)`. (From `Real.sin_le`, `Real.cos_sub_cos`, or the integral of sin.)
- **R3 (explicit integral).** `∫ s in 0..t, cos (δ + ω*s) = (sin(δ+ω t) − sin δ)/ω` (`integral_comp_mul_left`, `integral_cos`).
- **R4 (identity).** `2 sin(δ+k) − sin δ − sin(δ+2k) = 4 sin(δ+k) sin²(k/2)` (`Real.sin_add`, `Real.cos_sq_half` or `sin_sq`).
- **R5 (Chebyshev split).** `a₁` monotone on `[0,tf]`, `h ≤ 0` on `[0,c)`, `h ≥ 0` on `[c,tf]`, both integrable ⇒ `∫ a₁ * h ≥ a₁ c * ∫ h`. Proof: `(a₁ s − a₁ c) * h s ≥ 0` pointwise, then integrate.
- **R6 (zero integral ⇒ a.e.).** `0 ≤ᵐ f`, `∫ f = 0`, integrable ⇒ `f =ᵐ 0`. (`integral_eq_zero_iff_of_nonneg_ae`.) *Route R only.*
- **R7 (a.e. ⇒ everywhere; L4.4).** `f` continuous on `Icc 0 tf`, `f =ᵐ[volume.restrict (Icc 0 tf)] 0` ⇒ `f = 0` on `Icc 0 tf`. Mathlib: `Continuous.ae_eq_iff_eq` / `MeasureTheory.Measure.eq_of_ae_eq_of_continuous`, or prove it via an open set of positive measure. *Optional* (see Route R remark: rigidity on pairs of a.e.-good times avoids it in variant F).

## 4. Model layer (M-series)
- **M1 (tilt envelope; L4.6).** Admissible ⇒ `∀ s ∈ Icc 0 tf, ω*s ≤ π → cos (ω*s) ≤ ⟪b s, ez⟫`. ✔ `AttitudeAdmissible.inner_b_ez`. Variant T: `cos (ω*min s (tf-s)) ≤ ⟪b s, ez⟫`.
- **M2 (pointwise thrust bound).** a.e. `cos(δ + ω*|s − τ|) ≤ ⟪d s, b τ⟫` when `δ + ω*|s−τ| ≤ π`. From S1 with `y = b s`, `z = b τ`. ✔ (`inner_d_ez` is the case τ = 0.)
- **M3 (mass bound; L4.3).** For `T` in D2, `ρ₁/(m₀ − α ρ₁ s) ≤ a T s`. Needs only `∫₀^s T ≥ ρ₁ s` and positivity of `m`.
- **M4 (extreme arcs admissible; L4.7).** For horizontal unit `u` and an ω-Lipschitz `φ ≥ 0` with `φ 0 = 0` (and `φ tf = 0` in variant T), `b_u s := cos(φ s)•ez + sin(φ s)•u` and `d_u s := cos(δ+φ s)•ez + sin(δ+φ s)•u` are admissible. The proof uses `⟪b_u s, b_u s'⟫ = cos(φ s − φ s')` (from `cos_sub`).
- **M5 (midpoint).** `d_u s + d_{−u} s = (2 cos(δ+φ s)) • ez`, hence `midpoint (P_u) (P_{−u}) = (∫ a₁ cos(δ+φ)) • ez`.

---

## 5. Theorems and the recommended order

### Route Q (ball bound) — math/02 Thm Q. Recommended first target for the unconstrained model.
Hypotheses: D1, variant F, `δ + ω*tf/2 ≤ π/2`, and `0 ≤ ∫ a₁ cos(δ+ω s)` (automatic when `a₁` is constant).
- **Q1 (support bound, Lemma 5.1).** For any admissible `(a,d,b)` and `τ := tf/2`: `G ≤ ‖I‖`, where `G := ∫ a₁ s * cos(δ + ω*|s − tf/2|)`. Proof: `⟪I, b τ⟫ = ∫ a s * ⟪d s, b τ⟫` (`integral_inner`); integrand `≥ a₁ s * cos(…)` a.e. by M2, M3 and `cos ≥ 0`; then S5. **Does not use `b 0 = ez`.**
- **Q2 (strict gap).** `∫ a₁ cos(δ+ω s) < G`, i.e. `‖M‖ < G`. Constant `a₁`: R3 on both integrals plus R4, giving gap `= (4a₁/ω) sin(δ+ωtf/2) sin²(ωtf/4) > 0`. Avoiding R3, `∫₀^tf c(|s−tf/2|) = 2∫₀^{tf/2} c` by symmetry, and `∫₀^{tf/2} (c(x) − c(x+tf/2)) > 0` by R1 also works. Monotone `a₁`: R5 with `c = tf/4`. [lean]'s note is correct: `cos(δ+ω|s−tf/2|) ≥ cos(δ+ωs)` fails pointwise for `s < tf/4`, so R5 or symmetry is needed.
- **Q3.** `M ∉ reachSet` (from Q1, Q2 and `‖M‖ = |M_z|`), so `¬ Convex reachSet`, so `¬ Convex landingSet` (A6), so no lossless uniform convex relaxation (A1). Quantitative version: `infDist M reachSet ≥ G − ‖M‖` (A3).

### Route R (rigidity) — math/02 Thm B. [lean]'s current route; covers variant T for every α.
Hypotheses: D1, `δ + max φ ≤ π/2`. Steps (math/02 §4.2): (1) M1 + S1 + M3 give `a d_z ≥ a₁ cos(δ+φ)`; (2) R6 gives `d_z = cos(δ+φ)` a.e.; (3) S2/S3 on the good set; (4) R7, or rigidity between pairs of good times (variant F); (5) S4 ⇒ constant `u`; (6) `⟪I,u⟫ ≥ ∫ a₁ sin(δ+φ) > 0 = ⟪M,u⟫`. Variant T: chaining through `tf/2` needs `tf/2` to be a good time, so use R7 (continuity of `b`) at `tf/2`.

### Route B\* (state-constrained main theorem) — math/02 §10. Target after Q.
Use the **quantitative** proof (Step 7). It needs no S2, S4, R6, R7, and no compactness. Fix `s*` with `ω s* ≤ δ ≤ π/4`, put `w s := s − s*`, `Λ θ := r₀ + s* • v₀`.
- **B1 (identity, Lemma 10.1).** Landing ⇒ `Λ θ = ∫ w s * a s • d s + κ • ez`, `κ = g₀ tf (s* − tf/2)` (algebra on D4).
- **B2 (direction bound, (10.1)).** `(∫ w a d).z ≤ V(a) := −∫₀^{s*} (s*−s) a cos(δ+ωs) + ∫_{s*}^{tf} (s−s*) a`, via M1, S1 and `d_z ≤ 1`; deficits `η_dive, η_brake ≥ 0`.
- **B3 (late throttle).** Abstract version: replacing `a` on `(s*,tf]` by `a_max` increases `V`. With the interface `a ≤ a_max` this is immediate. With the mass model, prove `a_T ≤ a_{T♯}` pointwise on `(s*,tf]`.
- **B4 (witness admissible and state-feasible).** M4 with `φ = ω min(s, s*)`, `d = ez` after `s*`; then the explicit altitude/glide-slope inequalities (S1)–(S3) of math/02 §10.2. Pure real-number inequalities on closed-form `r(t)`.
- **B5 (lateral lower bound, Step 7 (i)–(v)).** With `c = b(ϑ s*)`: `‖X_h‖ ≥ γ_X − η_dive/(ωϑs*)` (M2, S5, R2), and `‖B_h‖ ≤ √(2 W_b η_brake)` (Cauchy–Schwarz: `integral_mul_le_Lp_mul_Lq` with p = q = 2, or the scalar `∫ √(fg) ≤ √(∫f ∫g)`, plus `√(1−x²) ≤ √(2(1−x))`).
- **B6 (conclusion).** `‖Λ θ − Λ θ_m‖ ≥ η₀` for all landing `θ`, so `θ_m ∉ landingSet`. With A5 and the witnesses, `¬ Convex (landingSet ∩ constraints)`.
Start with `α = 0` (constant `a₁ = ρ₁/m₀`, `a_max = ρ₂/m₀`, explicit `T*`).

### Theorem D (per-instance)
A4 + Corollary D.1. D.1 needs B6 and the affine map `A'(Δr,Δv) = (Δr + tf•Δv, Δv)` with `‖A'⁻¹‖ ≤ 1 + tf`.

### 6DOF transfer (math/02 Thm 6.2) and the TVC flat output (Lemma 6.4)
- **K1 (projection).** If `b = R e₃` with `‖Ω_⊥‖ ≤ ω`, then `b` satisfies (AL). This is the ODE direction of Prop 1.2, and the partition argument is heavy. Recommendation: state 6DOF admissibility *directly* via (AL) on `b = R e₃`, i.e. define the 6DOF class as attitude paths whose axis satisfies (AL). Prop 1.2 then stays a paper lemma.
- **K2 (lift).** `R(t) = rotation about fixed axis k = ez × u by angle φ(t)` gives `R(t) e₃ = b_u(t)` (Rodrigues' formula, cross-product algebra).
- **K3 (center-of-percussion identity, Lemma 6.4; pure algebra in ℝ³).** Given unit `b`, `n ⊥ b` unit, `d = cos μ•b + sin μ•n`, `Ω_⊥ ⊥ b`, roll rate `r`, define `b̈ := −(L T sin μ / J_t)•n − ‖Ω_⊥‖²•b + (J_a/J_t) r•Ω_⊥`. Then `(T/m)•d + g + (J_t/(m L))•b̈ = (T cos μ/m − (J_t/(mL))‖Ω_⊥‖²)•b + g + (J_a/(mL)) r•Ω_⊥`. This is a one-line `module`/`ring` identity once `k L T / J_t = T/m` is substituted. The *derivation* of `b̈` from Euler's equations (math/02 proof of Lemma 6.4) uses `cross_cross` (`(a×b)×c = ⟪a,c⟫b − ⟪b,c⟫a`) for the vectors `(b × d) × b = sin μ • n`, `Ω × (Ω_⊥ × b) = −‖Ω_⊥‖²•b + r•Ω_⊥`, and `(Ω_⊥ × b) × b = −Ω_⊥`.

---

## 6. Suggested file plan
`Abstract.lean` (A1–A5, D5, D6), `Sphere.lean` (S1–S5), `Calc.lean` (R1–R5), `Model.lean` (D1–D4, M1–M5), `BallBound.lean` (Q1–Q3), `Rigidity.lean` (Route R), `DiveBrake.lean` (B1–B6), `TheoremD.lean`, `Percussion.lean` (K3). Main statement for the paper: `theorem no_lossless_uniform_relaxation_constrained` (from B6 + A1), plus the unconstrained `…_ballBound` (Q3).

---

## Lemma S (per-instance slice nonconvexity, hard soft landing), [proof-s], math/07-lemma-S.md

The target is Theorem S (math/07 §3): an explicit instance with 0 ∉ cl L ≠ ∅. Everything below is real analysis on `L²((0,T); ℝ²)` plus one Fourier fact. **No PMP, no rigidity, no compactness.** Coning is handled automatically because every estimate is componentwise.
Suggested file: `LemmaS.lean`. Start with α = 0 and ρ₁ = ρ₂ (then K ≡ 0, ε_m = 0, C_m = A'). Add K and α afterwards.

- **SW1 (affine projection).** `P : L²(0,T;ℝ²) →L[ℝ] L²` is the orthogonal projection onto `span{1, s}` (componentwise). The facts needed are:
  - `P f` depends only on `m f := (∫ f, ∫ s • f)`, with `‖P f‖² = m fᵀ G⁻¹ m f`;
  - `G⁻¹₂₂ = 12/T³`, so `‖π_{(0,q)}‖² = 12‖q‖²/T³`;
  - `‖P^⊥ f‖ ≤ ‖f − c‖` for every constant `c`.
  Use `orthogonalProjection` onto a finite-dimensional submodule, or work directly with the explicit 2×2 Gram matrix. Elementary.
- **SW2 (periodic Wirtinger).** For `g ∈ H¹` (or `C¹`, enough for the witness side, but the competitor side needs Lipschitz `g`) with `g 0 = g T`: `‖g − mean g‖² ≤ (T/(2π))² ‖g'‖²`.
  Mathlib route: transfer to `AddCircle T` and use Parseval (`tsum_sq_fourierCoeff`) together with `fourierCoeff` of the derivative (`fourierCoeffOn_of_hasDerivAt` exists for intervals). For Lipschitz `g`, use absolute continuity (`LipschitzWith` → a.e. derivative, FTC `integral_eq_sub_of_hasDerivAt_of_le` or `LipschitzOnWith.ae_differentiableWithinAt`).
  **This is the only nontrivial analytic input.** Fallback: prove it for piecewise-C¹ `g` and state Lipschitz attitude paths through a density argument, or assume SW2 as a hypothesis lemma first.
- **SW3 (Lemma W).** `‖P^⊥ f‖² ≤ (T/(2π))² ‖f'‖²`. From SW1 (affine invariance + constant comparison) and SW2 applied to `f̃ = f − f 0 − (s/T)(f T − f 0)`, using `‖f̃'‖² = ‖f'‖² − ‖f T − f 0‖²/T ≤ ‖f'‖²`. Componentwise, so any `EuclideanSpace ℝ (Fin N)`.
- **SP1 (pointwise majorant, Lemma P1).** For `a ≥ a₁ > 0`, unit `d` with `cos τ ≤ d_z`, `0 < cos τ`: `−a d_z ≤ −a₁ + a₁ ‖d_h‖²/(1 + cos τ) − (a − a₁) cos τ`. Pure algebra using `‖d_h‖² + d_z² = 1`.
- **SP2 (kinematics, Lemma P2).**
  - (ii) `cos(δ+ωs) ≤ (d s)_z` from S-series spherical triangle lemmas (existing `Sphere.lean`) with (AL) at `s, 0`.
  - (iii) `b_h` is `ω`-Lipschitz (from (AL): `‖b s − b s'‖ = 2 sin(∠/2) ≤ ω|s − s'|`, and the projection is 1-Lipschitz).
  - (iv) `‖d_h − b_h‖ ≤ ‖d − b‖ ≤ 2 sin(δ/2)` (from `⟪d,b⟫ ≥ cos δ`: `‖d−b‖² = 2 − 2⟪d,b⟫`).
- **SP3 (throttle split).** With `K := (a − a₁) • d_h`: `‖K‖ ≤ (a₂ − a₁₀) sin τ̄` and `(a − a₁) cos τ̄ ≥ κ₀ ‖K‖²`. Scalar inequalities.
- **SM (Prop. M, master inequality).** `gain ≤ B + C_m ‖π_{m F}‖²`. Integrate SP1 (`integral_mono`), split `v = β + ẽ`, then:
  - triangle inequality in L²;
  - SW3 for β with `‖β'‖² ≤ ω² T`;
  - `‖ẽ‖² ≤ δ_e² T`;
  - eliminate `K` by the concave quadratic maximization `A'‖x‖² − κ₀‖x − π‖² ≤ (A'κ₀/(κ₀−A'))‖π‖²` (complete the square).
- **SS1 (witness).** Explicit planar trajectory (existing `M4`-style meridional constructions): φ piecewise linear, outward gimbal, `t₁` from IVT (`intermediate_value_Icc`) applied to the continuous map `t₁ ↦ ∫ a₁ sin χ_{t₁}`.
  `gain_w` has a closed form for α = 0 (integrals of `cos` of affine functions). The **numerical** inequality `gain_w > B` for a concrete parameter set is checked by `norm_num` on rational bounds of `sin`/`cos` (Mathlib `Real.sin_bound`, `Real.cos_bound`, or `interval_cases`-free Taylor bounds).
- **SS2 (altitude of the witness).** `v̇_z ≥ a₁₀ cos χ_max − g₀ > 0` ⇒ `r_z ≥ 0` (monotonicity, FTC).
- **SS3 (Theorem S).** For any trajectory from `ζ_w` landing at `(p, 0)`: `gain = gain_w`, `m F = (0, −p)` (from D4 algebra). So `‖p‖² ≥ M T³/(12 C_m)`. Then `0 ∉ closure L` (closed ball argument), and `L` is not convex (rotation by π, `A5`-style midpoint).
- **SS4 (Theorem D hard).** Combine SS3 with existing D6/`TheoremD`: relaxed value `0` at target `0`, original `≥ r_S`.

Recommended order: SP1, SP2, SP3 (algebra) → SW1 → SW3 assuming SW2 → SM → SS1–SS4 for one concrete row of math/07 §4 (δ = 0, T = 2, ω = 0.2, ρ₁ = ρ₂ variant is the cheapest: then `C_m = A'`). Discharge SW2 last.

---

## Pure TVC (gimbal-only pitch/yaw torque; math/06-pure-tvc.md, Theorem TVC-1) — added by [proof-tvc]

Scope: constant mass, constant ε = J_t/(mL), axisymmetric J, relaxed thrust-acceleration control u ∈ C(b), landing upright at rest. The theorem is **computer-assisted**: one finite-dimensional matrix inequality (an SDP certificate, 2N×2N) is checked numerically. Everything else is elementary real analysis and ℝ³ algebra. Suggested file: `PureTVC.lean`.

**Definitions**
- PT-D1 `TVCAdmissible`: b ∈ C¹([0,tf]; S²), ḃ absolutely continuous. u measurable with u(s) ∈ C(b(s)) := {u : ⟪u,b⟫ ≥ a₁cos δ, ‖u‖ ≤ a₂, ‖Π_b u‖ ≤ ⟪u,b⟫ tan δ}. Coupling ε∇ḃ = −Π_b u (+ gyro term in variant R1). Boundary conditions b(0)=b(tf)=e_z, ḃ(0)=ḃ(tf)=0.
- PT-D2 Landing in integral form: v₀ = g₀ tf e_z − ∫ (f b + γ₃) and r₀ = ∫ s (f b + γ₃) − ½ g₀ tf² e_z, with f = ⟪u,b⟫ − ε‖ḃ‖². (Taking these as the definition of F avoids the ODE; equivalence with the ODE is TVC-K1.)
- PT-D3 `Lambda θ := r₀ + s*•v₀`, `W_z`, `J0`, gain `W_z − J0`.

**Lemmas (all elementary)**
- TVC-K1 (= blueprint K3 plus derivation). Given ε∇ḃ = −Π_b u, the centre of percussion satisfies ÿ = f b + γ₃ − g₀e_z. Pure ℝ³ algebra: `cross_cross`, and ⟪b,b̈⟫ = −‖ḃ‖² from ‖b‖ = 1.
- TVC-L1 (speed lemma). d/dt‖ḃ‖ ≤ ‖Π_b u‖/ε ≤ a₂ sin δ/ε a.e. Hence ‖ḃ(s)‖ ≤ K₂ min(s, tf−s) and angle(b(s), e_z) ≤ K₂ min(s,tf−s)²/2. Uses `norm_sub_le` and an integral comparison; ⟪γ₃, ḃ⟫ = 0.
- TVC-L2 (landing identity). Λ(θ) = ∫ (s − s*)(f b + γ₃) + κ e_z. Same algebra as blueprint B1.
- TVC-L3 (midpoint). F is R_π-invariant, so θ_m := ½(θ + R_πθ) has r₀ₕ = v₀ₕ = 0 and ℓ(θ_m) = ℓ(θ). Reuse A5.
- TVC-P1 (pointwise, early). For unit b with b_z ≥ c > 0 and h = b_h: 1 − b_z = ‖h‖²/(1+b_z), and ‖ḃ‖² ≤ ‖ḣ‖²/b_z² (since ḃ_z = −⟪h,ḣ⟫/b_z).
- TVC-P2 (pointwise, late). For 0 ≤ p ≤ √(a₂² − |q|²) and 0 ≤ b_z = √(1−|h|²): a₂ − p b_z ≥ (|q|² b_z² + a₂²|h|²)/(2a₂). Uses `Real.sqrt_le_sqrt` and a₂ − √Y ≥ (a₂² − Y)/(2a₂).
- TVC-P3. If f ≥ 0 then a₂ − f b_z ≥ |a₂ − f|.
- TVC-P4 (torque in tilt coordinates). ḧ = −q_h/ε + (J_a/J_t)ω₃(b×ḃ)_h − ‖ḃ‖²h, so |‖ḧ‖ − ‖q_h‖/ε| ≤ v̄²‖h‖ + c₃‖ḣ‖. Then (x+y)² ≤ (1+κ)x² + (1+1/κ)y², and (x−y)₊² ≥ (1−ϑ)x² − (1/ϑ − 1)y².
- TVC-P5 (gyro, R1). |(h×ḣ)_z| ≤ ‖h‖‖ḣ‖ ≤ ½(g‖h‖² + ‖ḣ‖²/g).
- TVC-Q1 (separability). If a scalar quadratic inequality (C) holds for all x = I²n with n ∈ L², then it holds for ℝ²-valued h componentwise, and summing gives the vector inequality. Uses `EuclideanSpace` norms as sums of squares.
- TVC-Q2 (moment shift). For D ≥ 0 with D ≤ D_max and any η > 0: ∫ s^j σ D ≤ D_max ∫_{|w|<η} s^j σ + η⁻¹ sup_{|w|≥η}(s^j σ/ω_D) · ∫ ω_D |w| D. Split the integral and apply `integral_mono`.
- TVC-Q3 (discretization remainder; piecewise-linear version used by certificate2.py). Let n'' be orthogonal to {1, t} on each cell of length h. Then İ n'' and I²n'' are cell-local, ‖İn''‖²_cell ≤ (h/2π)²‖n''‖²_cell (Wirtinger with zero mean and zero endpoints), ‖I²n''‖²_∞,cell ≤ h³/(4π²)‖n''‖²_cell, and |∫ g n''| ≤ sup|g''| (h²/8)√tf ‖n''‖. The Wirtinger step is the only nontrivial analytic input; it can be replaced by the weaker constant h²/2 (Cauchy–Schwarz) at the cost of a larger N.
- TVC-Q4 (splitting). If S ⪰ 0 then S(a+b) ≤ (1+τ)S(a) + (1+1/τ)S(b), and −S(a+b) ≤ −(1−τ')S(a) + (1/τ' − 1)S(b).
- TVC-C (certificate, NUMERICAL). The 2N×2N matrix inequality
  (1+τ)K₊ + (1−τ')K₋ − (1−τ')ρGᵀG − (1−τ')ρ_cCᵀC + (1+τ)Σλ_kL_k ⪯ diag(W(λ + M_late))
  holds for the stored λ (`numerics/proof-tvc/cert2_*.npz`). In Lean this is an axiom-free `decide`-style check only if entries are rationalized and an LDLᵀ certificate with rational arithmetic is supplied. Interim: treat it as an explicit hypothesis `CertHolds`, like `PMPData` in the positive blueprint.
- TVC-W (witness). The explicit planar control has gain G_w and satisfies r_z > 0 and the glide slope. A closed-form piecewise-quadratic ψ makes this a finite computation, but its integrand is transcendental (cos ψ), so interval bounds are needed. Interim: explicit hypothesis.
- TVC-Main. CertHolds ∧ G_w > U_tot ⇒ θ_m ∉ F ⇒ ¬Convex F^X ⇒ no lossless uniform relaxation (A1).

Recommended order: K1, L2, L3, P1–P5, Q1, Q2, Q4 (pure inequalities) first; Q3 next; C and W as hypotheses.
