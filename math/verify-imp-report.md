# Independent referee report: impossibility-side claims

Author: [verify-imp]. Date: 2026-11-07 (system clock).
Brief: comms/briefs/verify-imp.md. Scripts and outputs: numerics/verify-imp/ (own venv, one process at a time, BLAS threads = 1).

Method: I re-derived every step from the hypotheses as stated. I checked each inequality, each use of a lemma against that lemma's hypotheses, quantifiers, measurability and edge cases, and whether the regime stated is the regime proved. I recomputed every constant and table numerically.

**Bottom line: no claim is BROKEN.** Every core argument is correct. Seven items need small repairs. The repairs concern regimes and examples that are stated more broadly than they are proved, one table row outside its theorem's hypotheses, and one notational overstatement. Each repair is written out below.

| # | Claim (registry row) | Verdict |
|---|---|---|
| 1a | Thm Q, ball bound and Γ_F (P-Q, P-ε) | **CONFIRMED** |
| 1b | Thm Q_T, tent quantitative (P-T) | **NEEDS FIX** (one table row is outside the hypotheses; the proof is fine) |
| 1c | Thm B variant T (P-B) | **CONFIRMED** |
| 1d | Thm L / L_T, all horizons (P-L); Prop 8.1 (P-L0) | **CONFIRMED** |
| 1e | Free final time: Prop 7.2, Prop 7.3 (P-tf), Cor 10.4 | **CONFIRMED** |
| 1f | RR-LS (RR-LS, LS) | (i), (ii) **CONFIRMED**; (iii) instantiation **NEEDS FIX** (window example) |
| 2a | Thm B*, qualitative + T′ + Step 7 quantitative (B*, P-B*) | **CONFIRMED** |
| 2b | constant c₁ | **CONFIRMED**: 1/(ωϑs*) and 4a_max/(ω a₁₀ sinδ s*) are the same expression, and both are right |
| 2c | Thm B*-env (P-B*env) | **CONFIRMED** |
| 2d | math/01 §B* (adversary version) | **CONFIRMED** in substance (superseded by math/02 §10/§10.6); one side claim relies on L-R1 |
| 3a | Thm D + Def 11.1 (D, P-D); Prop 11.2 | **CONFIRMED** |
| 3b | Cor D.1 (P-D1) | **NEEDS FIX** (two hypotheses left implicit) |
| 3c | Lemma W (S-W), Prop M (S-M), Thm S (S-T, S) | **CONFIRMED**; table reproduced to every printed digit |
| 3d | "certified Ω-ranges (0, Ω_max]" (S-T text, paper §3) | **NEEDS FIX**: the low-Ω end fails for δ > 0 |
| 4a | Thm A-opt (L-Aopt) | **CONFIRMED** (wording: the result is the convex envelope conv V, not the closed envelope V**) |
| 4b | Prop T (L-Aopt) | **NEEDS FIX**: the terminal-attitude variant must be stated (it is the tent variant) |
| 5a | P0-R (P0-R, RR-R0) | variant F **CONFIRMED**; tent "iff" **NEEDS FIX** (the "only if" direction is proved only for δ+ωt_f/2 ≤ π) |
| 5b | P0-F | **CONFIRMED** |
| 5c | P0-X | **CONFIRMED** (two clarifications) |

---

## 1. Thm Q, B(T), all horizons, free final time, RR-LS (math/02 §§4–5, 7–8; math/redteam-reform §4)

### 1a. Thm Q (math/02 §5.2): CONFIRMED
- **Lemma 5.1.** Lemma 4.1(a) is applied with α=δ, β=ω|s−τ|. The condition δ+ω·max(τ,t_f−τ) ≤ π/2 gives α+β ≤ π/2, and it also puts ω|s−τ| ≤ π inside the (AL) range. Since cos(·) ≥ 0, the step a⟨d,c⟩ ≥ a₁⟨d,c⟩ is legitimate. No boundary condition on b is used. ✓
- **Thm Q.**
  - ‖I−M‖ ≥ ‖I‖−‖M‖ = ‖I‖−M_z uses M_z ≥ 0. ✓
  - The witness arcs need δ+ωt_f ≤ π, which follows from 2δ+ωt_f ≤ π. ✓
  - Chebyshev step: h ≥ 0 exactly on [t_f/4, t_f], because c is strictly decreasing on [0,t_f]. a₁ is nondecreasing, so (a₁(s)−a₁(t_f/4))h(s) ≥ 0. ✓
  - I re-derived ∫h = (4/ω)sin(δ+ωt_f/2)sin²(ωt_f/4) via sin x+sin(x+2k) = 2sin(x+k)cos k. ✓
  - Sign condition at α=0: sin(δ+ωt_f) ≥ sin δ ⇔ δ+ωt_f ≤ π−δ. ✓
- **Cor 5.2 (ε-lossless).** Correct: π_Θ(C) ⊇ conv F ∋ θ_M.
- **Numerics.** `v1_Q_QT_Bstar.py` reproduces the table exactly: G = 19.77 / 14.89 / 24.99, M_z = 12.10 / 1.06 / 0.91, Γ_F = 7.61 / 13.72 / 23.75. All three rows are in the regime. Row 3 has α>0 and δ+ωt_f > π/2; its sign condition was checked numerically (M_z = 0.91 > 0).

### 1b. Thm Q_T (math/02 §5.3): proof CONFIRMED; table NEEDS FIX
- **Proof.**
  - Since ∠(b(s),e_z) ≤ φ_T(s) from both endpoints, ∠(b(s),v_λ) ≤ A_{λ,β}(s).
  - The identity φ_T(s)+ω|s−t_f/2| = ωt_f/2 gives A ≤ (ωt_f/2+β)/2 ≤ ωt_f/2, hence cos(δ+A) ≥ 0. ✓
  - The bound ‖I−M‖ ≥ ⟨I−M,v_λ⟩ holds for every λ, so the bound is ≥ min_β Q(β). ✓
- **(i), α = 0.**
  - λ=β: H(β,β) ≥ G(t_f/2) = M_z, by the time symmetry. ✓
  - λ=0: min(·) is 1-Lipschitz, so |A_{0,β}−A_{0,0}| ≤ β. ✓
  - κ = (8a₁/ω)sin(δ+ωt_f/4)sin²(ωt_f/8), re-derived. ✓
  - The case split at β = κ/(2A₁) is correct. ✓
- **(ii), α > 0.** Continuity in α holds: H is jointly continuous, the λ-interval [0,β] is a continuous correspondence, and β ranges over a compact set. ✓
- **Table, row (10, 0.3, 15°, 5.66e-4).** This row has δ+ωt_f/2 = 1.762 > π/2, which is **outside the theorem's hypothesis**. There cos(δ+A) < 0 on part of [0,t_f], and the step a⟨d,v_λ⟩ ≥ a₁cos(δ+A) fails, because a ≤ a_max would be needed there. So 10.77 is not a certified bound. Nonconvexity at that horizon is still covered qualitatively by Thm L_T.
- **Table, row (6, 0.3, 15°, 0.03).** It needs (H_m) with ρ₂ < m₀/(αt_f) = 444 N. With the project's ρ₂ = 1000 N, the mass goes negative at full throttle.
- **Recomputation.** `v1` reproduces all four γ_T values: 3.241, 3.268, 3.854, 10.774.
- **Repair.** Delete row 4 or mark it "outside the theorem; the min-max formula is not a valid bound there". State ρ₂ ≤ 444 N for row 3. The analytic α=0 bound (i) is very weak (0.057 against the numerical 3.24) but positive, as claimed.

### 1c. Thm B variant T (math/02 §4): CONFIRMED
I checked Steps 1–6 for φ_T.
- Lemma 4.6 (T) needs ωt_f ≤ π, which follows from δ+ωt_f/2 ≤ π/2. Corollary 4.2 needs φ_T(s) ∈ (0,π) on (0,t_f). ✓
- Rigidity on (0,t_f/2] and on [t_f/2,t_f) uses (AL) with ω|s−s′| ≤ ωt_f/2 ≤ π. The two pieces are chained at t_f/2 through continuity (Step 4). ✓
- Step 6: I_h = (∫a sin(δ+φ_T))u₀ with a ≥ a₁ > 0. ✓
- The Lean-friendly remark (u constant on E∩(0,t_f/2] and on E∩[t_f/2,t_f), plus continuity at t_f/2) is correct.

### 1d. Thm L (all horizons) and Thm L_T (math/02 §7); Prop 8.1 (ρ₁=0): CONFIRMED
- **Thm L (1).** Uses ωs ≤ π−δ ≤ π inside (AL). ✓
- **Thm L (2).** The capped arcs satisfy |χ(s)−χ(s′)| ≤ ω|s−s′| with χ ∈ [0,π−δ] and ψ_d−χ = δ. ✓
- **Thm L (3), weak-* continuity of V(T).** m_{T_n} → m_T uniformly (pointwise convergence plus a common Lipschitz constant). Then ∫T_n f_n − ∫T f = ∫T_n(f_n−f) + ∫(T_n−T)f → 0. ✓
- **Thm L (5)–(7).** Equality forces d_z = cos ψ_d a.e., because a_T ≥ ρ₁/m₀ > 0. On (0,s*): Cor 4.2, Lemma 4.4 and Lemma 4.5, using ωs ∈ (0,π−δ). On [s*,t_f], d = −e_z. Hence I_h ≠ 0. ✓
- **Thm L_T.** The set {δ+φ_T < π} is dense, so b_z = cos φ_T everywhere. Tilts lie in (0,π) because ωt_f/2 < π. Rigidity chains through t_f/2. ✓
- **Prop 8.1 (P-L0).** With ρ₁ = 0, equality now forces T = T* wherever cos ψ_d ≠ 0, and d_z = cos ψ_d only where a > 0, i.e. on (s₀,t_f]. Rigidity on (s₀, min(s*,t_f)) gives I_h = (∫a₂ sin(δ+ωs))u₀ ≠ 0, since δ+ωs ∈ (π/2,π) there. ✓ I re-did this step myself, because the written proof is one line.

### 1e. Free final time: CONFIRMED
- **Prop 7.2.** Slices of convex sets are convex. ✓
- **Prop 7.3.**
  - I = M_{t*} + g(t*−t) = (M_{t*,z} + g₀(t−t*))e_z. ✓
  - Lemma 5.1 at horizon t needs δ+ωt/2 ≤ π/2, which follows from t ≤ t_b. ✓
  - The t=t* case needs M_z ≥ 0 (the Thm Q sign condition). That is automatic at α=0.
  - The registry form "‖M_tb‖+g₀(t_b−t) < G_t(t/2)" is a sufficient version (t* = t_b). ✓
  - The window-width estimate after the proof is heuristic and is labelled so.
- **Cor 10.4 (B\* on a window).**
  - (S1)–(S3) are monotone in t_f, with a_max taken at t_b. ✓
  - V*_t is nondecreasing (extend with ρ₂ and d = e_z; the dive part is unchanged because s* is fixed) and locally Lipschitz (by restriction). So ℓ* is continuous and attains its maximum on [t_a,t_b]. ✓
  - If the union were convex, θ_m(t°) ∈ F_{t′} would be a maximizer at horizon t′ > s*. Step 6 at t′ then gives W_h ≠ 0, but Λ_h(θ_m) = 0. ✓ Step 6 at t′ uses only (S1) and s* < t′. (S2)–(S3) are needed only for the witness at t°.

### 1f. RR-LS (math/redteam-reform §4): (i), (ii) CONFIRMED; (iii) NEEDS FIX
- **(i) and (ii).** Pure convexity and linear algebra (PR = −P because R² = I). These are correct, and they match the formalized `not_lineSearch_lossless` / `symmetric_supply`.
- **(iii) and §4.1, the instantiation from B\*. Three defects:**
  1. *The window example is inconsistent with B\*.* The examples "W = [0, t_fuel]" (§4(iii), §4.1) and "W ⊆ [t_a, min(t_b, t_fuel)]" with t_fuel = (m₀−m_dry)/(αρ₁) (paper Cor 3.11) are a problem. B\*'s Step 5 witness brakes at ρ₂, so B\* assumes m₀ − αρ₂t ≥ m_dry. On horizons t ∈ ((m₀−m_dry)/(αρ₂), t_fuel] the witness runs out of fuel. Its "late T = ρ₂" structure, and with it the altitude check, is then not available. Separately, W must lie in (s*, ∞), since the face does not exist for t ≤ s*.
  2. *(H2) is justified by "relaxed-control compactness + Dirac argument".* That is more than is needed, and not written. Cor 10.4's argument is complete: ℓ* is continuous and attained at every t.
  3. *(H3) says "v0_lat ≠ 0".* In the (S1) version, Step 6 gives Λ_h = r₀h + s*v₀h ≠ 0, not v₀h ≠ 0. Either fact gives Px ≠ 0, which is all (H3) needs. Only B\*-env gives v₀h ≠ 0.
- **Repair (replacement statement).** Let W = [t_a,t_b] with s* < t_a, such that (S1)–(S3) hold at t_a with a_max evaluated at t_b. If a dry-mass constraint is imposed, also require m₀ − αρ₂t_b ≥ m_dry. Then (H1)–(H3) hold by Cor 10.4's proof, and no per-horizon family of uniform convex relaxations is lossless on W. The paper's Cor 3.11 "e.g." should be replaced by this window.

## 2. Theorem B\* (math/02 §10, §10.6; math/01 §B\*)

### 2a. Thm B\* (qualitative, T′, Step 7 quantitative): CONFIRMED
**Line-by-line check of the qualitative steps.**
- **Lemma 10.1.** Re-derived from Lemma 3.1(a): Λ = ∫(s−s*)ad + g₀t_f(s*−t_f/2)e_z. ✓
- **Step 1.** δ+ωs ≤ 2δ < π. The signs of w give W_z ≤ V(T). The bound holds on the **unconstrained** F, which is what Step 6 needs. ✓
- **Step 2.** On the brake, ∠(e_z, b(s*)) = ωs* ≤ δ by (S1). The upright variant T′ uses a meridional return on [s*,2s*] with tilt ≤ ωs* ≤ δ. Since d is unchanged, θ\* is unchanged. ✓
- **Step 3.** m(s) ≥ m(s*) − αρ₂(s−s*), so a_T ≤ a_{T♯} pointwise. ✓
- **Step 4.** At α=0, cos(δ+ωs) > 0, so T* = ρ₁ then ρ₂. ✓
- **Step 5.**
  - Brake: d = e_z gives v_h = r_h = 0. With v̇_z ≥ A_b: v_z ≤ −A_b(t_f−t) and r_z ≥ ½A_b(t_f−t)². ✓
  - Dive: d_z > 0 gives v̇_z ≥ −g₀, and (S2) gives v_z < 0. ✓
  - Glide slope: ‖r_h‖ ≤ ½a_max s*² ≤ r_z/tanγ by (S3). ✓
- **Step 6.** Equality forces d_z = cos(δ+ωs) on the dive, because (s*−s)a_T > 0. Rigidity on (0,s*] uses ωs ∈ (0,δ] ⊂ (0,π). On the brake, d_z = 1. So W_h = −(∫(s*−s)a sin(δ+ωs))u₀ ≠ 0, using δ > 0. ✓

**Step 7 (quantitative), checked inequality by inequality.**
- **(i).** ⟨d,c_τ⟩ ≥ cos(δ+ω|s−τ|) ≥ 0 on the dive, because δ+ωs* ≤ 2δ ≤ π/2 (δ ≤ π/4). ✓
- **(ii).** X_z ≥ Z₀ > 0, so X_z cosβ ≤ X_z. ✓
- **(iii).**
  - Mean value theorem with angles in [δ,π/2]: h_τ ≥ ωτ sinδ on s ≥ τ. ✓
  - On [τ/2,τ], h_τ ≥ 0, because |s−τ| ≤ s. ✓
  - On s < τ/2, h_τ ≥ −ω(τ−2s) ≥ −ωτ. ✓
  - The integrals give ωτ[a₁₀ sinδ(s*−τ)²/2 − a_max s*τ/2]. With τ = ϑs* and ϑ = a₁₀ sinδ/(4a_max) ≤ ¼, the bracket equals (a₁₀ sinδ s*²/2)[(1−ϑ)² − ¼] ≥ (5/32)a₁₀ sinδ s*² = γ_X. ✓
- **(iv).** sinβ ≤ β ≤ ωτ, and dividing the positive quantity ωτγ_X − η_dive by sinβ ≤ ωτ gives ‖X_h‖ ≥ γ_X − η_dive/(ωτ). ✓
- **(v).** ‖d_h‖ ≤ √(2(1−d_z)). Cauchy–Schwarz gives ‖B_h‖ ≤ √(B₀)√(2η_brake) ≤ √(2W_bη). ✓
- **(vi).** ‖ΔΛ‖² = ‖W_h‖² + η², and min_{η≥0} max(η, f(η)) = η₀ because f is strictly decreasing. The operator norm of Λ is √(1+s*²). ✓

### 2b. The constant c₁: both forms are correct, and they are equal
- From (iv), c₁ = 1/(ωτ) = 1/(ωϑs*). Substituting ϑ = a₁₀ sinδ/(4a_max) gives c₁ = 4a_max/(ω a₁₀ sinδ s*). The two expressions are identical.
  - math/02 has always had 1/(ωϑs*) (git history).
  - The paper now prints 4a_max/(ω a₁₀ sinδ s*), and paper/sections/B-proof-Bstar.tex prints 1/(ωτ).
  - All three agree.
- **Dimension check.** γ_X and η are lengths, so c₁ must be dimensionless. ωϑs* is dimensionless. ✓ Any version without the factor s* (e.g. 4a_max/(ω a₁₀ sinδ)) would have units of time and be wrong. Numerically that would be 101.6 instead of 155.3 at the GTPL point.
- **Numbers** (`v1`, GTPL, s* = δ/ω = 0.6545 s):

  | t_f | γ_X | c₁ | W_b | η₀ | η₀/√(1+s*²) |
  |---|---|---|---|---|---|
  | 7 | 0.0866 | 155.27 | 264.8 | 1.349e-5 m | 1.128e-5 m |

  This matches Rem 10.2 (γ_X = 0.087, η₀ ≈ 1.3e-5) and Cor D.1's 1.4e-6 m. (S1)–(S3) hold at t_f = 5, 7 and 12.
- **Stress test** (`v2_bstar_step7_stress.py`, α=0). I tried five near-face families: brake tilt cancelling W_h, dive coning, inner gimbal, slow dive, extra dive throttle. Steps (iv) and (v) are never violated. The best competitor, the exact brake-tilt canceller, has η = 2.66e-4 m with W_h = 0. That is 19× η₀, consistent with [adversary] a6 (≈2e-4 m): the bound is valid and the gap is genuinely thin.

### 2c. Thm B\*-env (math/02 §10.6): CONFIRMED
- **(2) Late-phase bound.** Lemma 4.1(a) applied to (d, b, −e_z) needs Φ ≥ δ. For Φ < δ the bound is trivial, so d_z ≤ cos((Φ−δ)⁺). ✓ I re-derived the late extremal via Lemma 4.1(b): d = cos(Φ−δ)e_z + sin(Φ−δ)u. ✓
- **(3) Profile bound.** E_p and L_p are the Lipschitz envelopes. Both are matched at s*, so the concatenation is ω-Lipschitz and realizable meridionally. ✓
- **(4) Late T = ρ₂.** This needs ωs* − δ ≤ π/2. It is implied by (S2′) through cos(ωs*) > 0, which [adversary] pointed out and which is written in. ✓
- **(5) Witness feasibility.** (S2′) uses (t_f − 2s*). That is conservative: t_f − s* already suffices for v_z < 0. (S3′) is exactly what the glide slope needs on [0,q], q ≤ 2s*. ✓
- **(6) Midpoint.** If p = Φ(s*) = 0, then Φ is still > 0 on (0,q) with q = s*. Using the unweighted I_h = −v₀h avoids the sign cancellation of W_h. ✓

### 2d. math/01 §B\* (adversary)
- The structure lemma and the free-t_f argument are correct in substance. They are made rigorous by math/02 §10.6 and Cor 10.4.
- The side claim "x̄* ∉ cl F, cl F = F_relaxed" is not proved in math/01. It relies on closedness of F (registry row L-R1, CLAIMED). For δ ≤ π/4, math/02 Step 7 gives dist > 0 directly. Nothing downstream depends on this for δ > π/4.
- The GTPL check (13.8 < 18.3) recomputes correctly with m_dry ≈ 55.6 kg.

## 3. Theorem D and Lemma S

### 3a. Thm D, Def 11.1, Prop 11.2: CONFIRMED
- **Thm D.** The proof is exactly mixture-closure: C is convex, ρ is affine, and P is convex with values in [0,∞]. So P(Σλy_i) ≤ ΣλP(y_i) = 0, and ρ(·) maps onto conv Reach. Convexity of φ is not even needed for the inequality. The strict gap uses cl Reach, as [adversary] corrected. ✓
- **Def 11.1.** It is the right class. Its exclusions (moment-lifted costs, occupation measures, inner restrictions) are stated explicitly, and they match the thread theorem-D items (4)–(5).
- **Prop 11.2.** For v₀h = 0, Λ_h = r₀h is the landing offset (up to sign), and Step 7 gives ‖p‖ ≥ f(η). ✓ This requires δ ≤ π/4, which is stated.

### 3b. Cor D.1: NEEDS FIX (two implicit hypotheses)
- The shift argument is right. θ_m − θ\* = −(r\*₀h, v\*₀h) is purely lateral, so vertical-only constraints are unaffected. The terminal states ±(shift(t_f), shift′(t_f)) average to 0. ‖A′⁻¹‖ ≤ 1+t_f. ✓
- **Repair:**
  1. The quantitative bound uses Step 7, so it needs **δ ≤ π/4**. This should be stated in Cor D.1.
  2. "Constraints depending only on (r_z, v_z), e.g. descent-rate limits" must also be **satisfied by the B\* witness**. B\* certifies only r_z ≥ 0 (and the glide slope). A descent-rate limit can be violated by the witness, whose v_z reaches −A_b(t_f−s*) + g₀s*. Add "and satisfied by the witness trajectory", as §10.1 already does for the extra constraints of B\*.

### 3c. Lemma W, Prop M, Thm S (math/07 §§1–4): CONFIRMED
- **§1.** ‖π_{(0,q)}‖² = 12|q|²/T³ (the (2,2) entry of G⁻¹). Landing from vertical data forces I_h = 0 and ∫sF = −p, so every trajectory has the same gain. ✓
- **Lemma W.** Each step re-derived:
  - P^⊥f = P^⊥f̃, because the difference is affine.
  - ‖P^⊥g‖ ≤ ‖g − const‖, because constants are affine.
  - Periodic Wirtinger applies to f̃ ∈ H¹_per.
  - ‖f̃′‖² = ‖ḟ‖² − |Δ|²/T, since ∫ḟ = Δ.
  - Sharpness: cos(2πs/T) is L²-orthogonal to 1 and to s on [0,T].
  - The componentwise extension to ℝ^N is immediate. ✓
- **Prop M.**
  - P1: 1−d_z = |d_h|²/(1+d_z). ✓
  - Step 1: |K| ≤ Δ sin τ̄ ⇒ Δcos τ ≥ |K|cot τ̄ ≥ κ₀|K|². ✓
  - Step 2: a₁|d_h|² = a₁₀(a₁₀/a₁)|v|² ≤ a₁₀|v|², with c̄ ≥ c₀. ✓
  - Step 3: PF = π_m, and the concave maximization gives max_x A′‖x‖² − κ₀‖x−π‖² = A′κ₀/(κ₀−A′)‖π‖² (I solved it). Maximizing over all affine x gives an upper bound. ✓
  - Step 4: v = β + ẽ with |ẽ| ≤ 2sin(δ/2) + ε_m sin τ̄. ✓
  - Step 5 collects to B. ✓
- **Thm S.**
  - The IVT root t₁ < T/2 exists because for t₁ ≥ T/2 the integral is > 0.
  - Small-angle constants: t₁ = (1−1/√2)T, and the mean-square tilt (3√2−4)/6 = 0.04044. ✓
  - (S1) gives v̇_z > 0, hence altitude. ✓
  - Item 2 needs no state constraint. ✓
- **Item 4 (wording).** The true value is ≥ r_S even if the cost ‖r(T)‖ allowed r_z(T) > 0. The dent bound uses only I_z and the lateral moments, not J_z. Writing it as "= dist(0, L)" is harmless but imprecise.
- **Table** (`v3_lemmaS_table.py`, independent root-finding and quadrature). Every printed number is reproduced: gain_w, B, M, r_S = 0.450 / 1.799 / 0.480 / 0.393 / 1.572, |p_w|, the α>0 failure (M = −2.2e-4), and the fixed-thrust r_S = 0.471 / 1.885.
- **Independent attack on Prop M** (`v4_masterineq_attack.py`; 3D, inner discretization, 6 starts each including S-turn and coning seeds): the best gain − C_m‖π_m‖² found is 0.0343 ≤ B = 0.0637 (δ=0), and 0.4417 ≤ B = 0.5281 (δ=10°). This agrees with proof-s (0.0338 / 0.4496).

### 3d. Certified Ω-ranges: NEEDS FIX
- math/07 §0/§4, the registry row S-T and the paper (§3, after Thm 3.14) claim certification for ωt_f ∈ (0, 0.55] (δ=0), (0, 0.45] (δ=5°) and (0, 0.30] (δ=10°). The **lower end is false for δ > 0.**
- As Ω → 0 at fixed δ > 0:
  - gain_w → a₁₀T(1−cos δ);
  - B → a₁₀T·2sin²(δ/2)·2/(1+cos δ) > gain_w;
  - so M < 0.
- `v3b_lowOmega.py` finds the certified set at T = 2:

  | δ | certified Ω |
  |---|---|
  | 5° | [0.004, 0.46] |
  | 10° | [0.038, 0.34] |
  | 7° | [0.009, 0.42] |
  | 12° | [0.070, 0.27] |
  | 0° | (0, 0.55] (correct as stated) |

  Corollary S is stated correctly: it needs δ/Ω → 0.
- **Repair.** Replace "(0, Ω_max]" by "[Ω_min(δ), Ω_max(δ)]", e.g. "0.04 ≤ ωt_f ≤ 0.30 at δ = 10°". All table rows lie inside the corrected ranges, so no certified instance changes.

## 4. A-opt and Prop T (math/redteam-lift §5, §7)

### 4a. Thm A-opt: CONFIRMED, with a wording fix
- The §7 Lean-ready form is exactly right: the mixing lemma plus VL.
- **Wording.** The §5.2 and paper phrase "V = V** on F" overstates the conclusion slightly.
  - The proof gives V(Σλθ_i) ≤ ΣλV(θ_i) for finite mixtures, i.e. V = conv V on F (the convex envelope).
  - V_rel is convex, but it is not known to be lower semicontinuous, so V ≤ V** (the closed envelope) does not follow.
  - **Repair:** say "agrees with its convex envelope (finite mixtures)", or add lower semicontinuity of V_rel.
  - The paper's Thm 3.15 already writes the finite-mixture inequality, so only the symbol needs care.
- **Side claim** "standard LCvx definition + attainment ⇒ Claim A feasibility form". Correct: C_{θ_M} ≠ ∅ because θ_M ∈ conv F ⊆ π_Θ C, and an attained optimum there cannot be original-feasible.

### 4b. Prop T: CONFIRMED for the tent variant; NEEDS FIX (state the variant)
- **Steps checked.**
  - F1–F2: equality forces b_z = cos φ everywhere (continuity), then rigidity.
  - F3: F(b_u) is convex and compact (Aumann). The pointwise maximizer of (ad)_z over S_{b_u}(s) is unique: a = a₂, with d at tilt (φ−δ)⁺. So the maximizer over K(b_u) is unique, θ\*_u, with lateral part ≠ 0 iff max φ > δ.
  - (1): every F(b_{u′}) has the same maximal I_z, so θ′ would have to equal θ\*_{u′}.
  - (2): b ≡ e_z, a = a₂cos ψ ∈ [a₁,a₂] matches θ′ in both I and J.
  - (3): Arzelà–Ascoli for b_n plus weak-* limits for u_n. The limit lies in co S_{b_u} and is de-relaxed by Aumann.
  - (4): mixing gives value ≤ Λ. All ✓.
- **Gap: the attitude boundary variant is never stated.**
  - The hypotheses ωt_f/2 > δ and a₂cos(ωt_f/2−δ) ≥ a₁ are correct only for φ = φ_T, i.e. **b(t_f) = e_z**.
  - In variant F (φ = ωs), step (2) needs a₂cos(ωt_f−δ) ≥ a₁, and F3 needs ωt_f > δ. The stated hypotheses do not imply these, so step (2) can fail.
  - **Repair:** state "variant T (b(0) = b(t_f) = e_z), φ = φ_T". Optionally add "variant F with ωt_f in place of ωt_f/2 in the first and third hypotheses". The hypothesis δ + ωt_f/2 ≤ π/2 is not used (harmless).
  - The same fix applies to paper Prop 3.16 and the registry row L-Aopt.

## 5. ρ₁ = 0 (math/possibility-rho0.md)

### 5a. P0-R: variant F CONFIRMED; tent "iff" NEEDS FIX
- **Lemma 0.1.** The star-shape and compactness claims are correct.
- **Lemma 0.2.** Correct. A supporting hyperplane exists at every boundary point of a closed convex set in ℝⁿ, even with empty interior, and t*x ∈ ∂conv S.
- **(⇐).** For each ψ, the pointwise sup is attained by one geodesic b\*. At every maximizer, u is a.e. determined:
  - b(s) is pinned on the minor arc wherever θ−ωs ∈ (δ, δ+π/2);
  - u = a₂ψ where θ−ωs < δ;
  - u = 0 where θ−ωs > δ+π/2. The tie set θ−ωs = δ+π/2 is a single point, where a nonzero u ⊥ ψ could otherwise sit.
  - For ψ = e_z the face is {a₂t_f e_z}, and for ψ = −e_z it is {0}.
  - R_env: the support functions agree, and R ⊆ R_env. ✓
- **(⇒), variant F.** This is Prop 8.1, re-checked in 1d. ✓
- **Tent variant.** (⇐) works verbatim with φ_T: the tent geodesic attains the bound, and the −e_z face is {0} iff δ+ωt_f/2 ≤ π/2.
  - **(⇒) is not written anywhere.** The L_T argument adapted to ρ₁ = 0 (equality on (s₀, t_f−s₀), rigidity chained through t_f/2) proves it only for **π/2 < δ+ωt_f/2 ≤ π**.
  - For δ+ωt_f/2 > π the witness can pass through −e_z, as in Prop 7.1, and the "only if" direction is open.
  - **Repair:** "Tent: convex if δ+ωt_f/2 ≤ π/2; nonconvex if π/2 < δ+ωt_f/2 ≤ π; open beyond." This also applies to paper Prop 3.17's parenthetical.

### 5b. P0-F: CONFIRMED
- **Lemma 2.1 (1D reduction).** The great-circle realization needs φ₀ − β ∈ [0,π]. In the P0-F regime, φ₀ − β < π/2+δ+T < π. ✓
- **Envelope/monotonicity argument.** At a maximizer, c_e(β(s)) = c_e(L_{β\*}(s)) a.e., since c_e is nonincreasing and the integrals are equal. That is what the separation step needs, even where c_e is flat. ✓
- **Endpoint computations.**
  - σ = T: E(0) < E(−T) strictly (L₀ > L_{−T} on (T/2,T)). ✓
  - σ = T/2: sin(2δ+s) − sin⁺(2δ−s) ≤ 2 sin s in both cases (s ≤ 2δ and s > 2δ). ✓
  - ∫(h−s)sin s = h − sin h and ∫t sin(h+t) = sin 2h − sin h − h cos 2h, which give f(h). ✓
  - The Taylor bounds give f ≥ h³(½ − ⅔h²). ✓
- **Strictness and separation.**
  - −τ_c is not a maximizer, by strict decrease of E. ✓
  - The maximizer set is closed and misses −τ_c, so both groups are compact. ✓
  - Pairwise ⟨p̂,I⟩_L < ⟨p̂,I⟩_R and compactness give strict separation. ✓
  - The face is disconnected, so K is not convex. ✓
- **Numerics** (`v5_p0F_p0X.py`, independent envelope quadrature). Ties are found at σ_c/T = 0.668–0.81 for (δ,T) ∈ {(0,.6),(5°,.6),(15°,.6),(15°,.9),(30°,.4),(40°,.1)}, and both groups are always separated by ⟨p̂,I⟩. min f/h³ = 0.281, matching the doc's 0.28.
- Remark 3's γ > 0 holds for the midpoint of the extremal pair: ⟨p̂,·⟩ there lies strictly between the two groups, so the point is off the face and hence outside the compact K.

### 5c. P0-X: CONFIRMED (two clarifications)
- **Integrands and inequalities.** The early integrand is sin⁺(−L); the late one is sin(2δ+β) on β ∈ [−T,T] ⊂ (−2δ, π/2−2δ).
  - L_t′ ≥ ½cos(2δ+T)τ². ✓
  - |E′| ≤ (σ−β\*)(σ+3β\*)/8 ≤ ½σ(σ−β\*), re-derived (the boundary terms cancel at the kink). ✓
  - The definition of β₀ has a factor-2 margin. ✓
  - Small-σ end: β₀ = 0, so L_t(β\*) ≤ L_t(0). ✓
  - V(−σ) − V(σ) = (σ − sin σ) − 2 sin σ ∫t cos(2δ+t). ✓
  - x\* → 1/(1+6^{−1/2}) = 0.7101. ✓
  - Altitude, for t < σ_c: concavity in x = t_f − t reduces the check to the endpoints, which gives exactly g ≤ a₂κ₀(1 − (σ_c/t_f)²). ✓
- **Clarification 1.** The left maximizer is **not** necessarily β\* = −σ_c. Numerically β\*_L > 0 (e.g. +0.007 at δ = 15°, T = 0.3), so it coasts at the end of the early phase, and its attitude there is not pinned. The altitude argument still holds, because d_z ≥ cos(δ+ωs) ≥ cos(δ+T) > 0 for **every** admissible control. The proof should say "for every admissible control", not "both witnesses have d_z > 0".
- **Clarification 2.** The threshold 1/(cos(δ+T)(1−x\*²)) is ≈ 2.1 only as T → 0. At δ = 15° it is 2.16 / 2.38 / 2.78 at T = 0.1 / 0.3 / 0.5 (`v5`). The registry and paper "≈2.1" should read "≈2.1 for small ωt_f, increasing with ωt_f".

---

## Repairs to propagate (owners)
- **[proof] math/02:**
  - Q_T table, row 4 (outside hypothesis) and row 3 (ρ₂ ≤ 444 N);
  - Cor D.1 (δ ≤ π/4; extra vertical constraints satisfied by the witness).
- **[proof-s] math/07 §0/§4 and row S-T:** certified Ω-ranges have a positive lower end for δ > 0.
- **[redteam-lift] §5.2/§5.3 and row L-Aopt:** "V = V**" should read "V = conv V (finite mixtures)"; Prop T must state b(t_f) = e_z.
- **[redteam-reform] §4(iii)/§4.1 and [paper-writer] Cor 3.11:** the window must satisfy s* < t_a and m₀ − αρ₂t_b ≥ m_dry; t_fuel defined through ρ₁ is not a valid upper end.
- **[possibility-rho0] §1 and paper Prop 3.17:** the tent "iff" holds only up to δ + ωt_f/2 ≤ π; P0-X altitude step should say "every admissible control"; the "≈2.1" is the small-T value.
- **[paper-writer]:** Thm 3.14's ranges, Prop 3.16's variant, Prop 3.17's tent parenthetical, Cor 3.11's window. The c₁ in Thm 3.7 is correct as printed.
