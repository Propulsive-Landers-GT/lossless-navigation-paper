# Pure TVC and B* with mass depletion: Lean ↔ mathematics map

Author: [lean-tvc]. Project `lean/LcvxObstruction` (Lean 4 `v4.36.0-rc2`, Mathlib pinned). All files below are imported from
the root `LcvxObstruction.lean`; the full `lake build` is green. No `sorry`, no `axiom`. `#print axioms` for every theorem
listed here (run `lake env lean LcvxObstruction/TVC/Axioms.lean`) gives only `[propext, Classical.choice, Quot.sound]`.

| File | Namespace | Content |
|---|---|---|
| `TVC/CentreOfPercussion.lean` | `LcvxObstruction.TVC` | FLAT: centre-of-percussion identity (zero roll rate and with roll rate), boundary translation |
| `TVC/Certificate.lean` | `LcvxObstruction.TVC` | TVC-1 skeleton: S-procedure/Finsler, separability, certificate and reduction as explicit hypotheses, rotation-midpoint argument, Theorem A link |
| `TVC/Model.lean` | `LcvxObstruction.TVC` | concrete pure-TVC landing sets `F^X ⊆ F ⊆ F^rel`, `R_π` invariance (Lemma 2.4), landing identity (Lemma 2.3), `tvc1_model` |
| `TVC/Discretization.lean` | `LcvxObstruction.TVC` | Lemma 4.6′ analytic inputs (TVC-Q3): cell Wirtinger and cell sup bounds |
| `TVC/Pointwise.lean` | `LcvxObstruction.TVC` | elementary pointwise inequalities of math/06 §4.2–4.3 (blueprint TVC-P1/P2/P3/Q4) and PT6 "⊆" |
| `DiveBrakeMass.lean` | `LcvxObstruction` | B* core and witness for **any** acceleration class with a face maximiser |
| `DiveBrakeMassModel.lean` | `LcvxObstruction` | B* for the explicit mass-depletion model `AccMass` (α > 0), every horizon |
| `DiveBrakeMassVariants.lean` | `LcvxObstruction` | the same for upright landing (T′) and kinematic 6DOF (free / upright terminal attitude) |
| `DiveBrakeQuant.lean` | `LcvxObstruction` | quantitative B* (Step 7): explicit distance from the witness midpoint to the landing set, constant bounds |
| `DiveBrakeQuantMass.lean` | `LcvxObstruction` | quantitative B* for any class with a face maximiser, and for mass depletion |
| `FreeTimeBStar.lean` | `LcvxObstruction` | B* with free final time on a compact window (Cor. 10.4), constant bounds and mass depletion |
| `TVC/Axioms.lean` | — | `#print axioms` for all of the above (not imported from the root) |

---

## 1. FLAT: centre-of-percussion identity (math/06 Lemma 2.1, math/02 Lemma 6.4; CLAIMS row FLAT)

Vectors are `V3 := Fin 3 → ℝ` with Mathlib's `⨯₃` and `⬝ᵥ` (the convention of `Positive/TVC.lean`); `cop_identity_E3` restates
the main identity in `EuclideanSpace ℝ (Fin 3)` with `cross3 x y := toLp (ofLp x ⨯₃ ofLp y)` and the inner product.
All statements are **pointwise algebraic identities at one instant**: the kinematic and dynamic laws enter as hypotheses
relating the vectors `b, ḃ, b̈, ω, ω̇, r̈, T` at that instant. No ODE existence or regularity is involved.

| Lean | Hypotheses | Conclusion | Mathematics |
|---|---|---|---|
| `cop_identity` | `m ≠ 0`, `L ≠ 0`, `b⬝b = 1`, `ω⬝b = 0` (zero roll rate), `T = T_a b + T_⊥`, `b⬝T_⊥ = 0`, `b̈ = ω̇×b + ω×(ω×b)`, `J_t ω̇ = (−L b)×T` (Euler, axisymmetric `J`, `ω₃ = 0`), `m r̈ = T − m g` | `r̈ + ε b̈ = (T_a/m − ε (ω⬝ω)) b − g`, `ε = J_t/(mL)` | FLAT identity, `T_a = T cos μ` |
| `cop_identity_E3` | same, in `EuclideanSpace ℝ (Fin 3)` (`‖b‖ = 1`, `⟪ω,b⟫ = 0`, …) | `r̈ + ε b̈ = (T_a/m − ε‖ω‖²) b − g` | same |
| `cop_identity_roll` | as above but roll rate `ω₃ = ω⬝b` free; `ḃ = ω×b`, `b̈ = ω̇×b + ω×ḃ`; inertial Euler `J_t ω̇ + (J_a − J_t)(ω̇₃ b + ω₃ ḃ) = (−L b)×T` (i.e. `d/dt(Jω) = τ` with `Jω = J_t ω + (J_a−J_t)ω₃ b`); `J_t ≠ 0` | `r̈ + ε b̈ = (T_a/m − ε‖ḃ‖²) b + ε (J_a/J_t) ω₃ (b×ḃ) − g` | math/06 Lemma 2.1: `ÿ = f b + γ₃ − g₀e_z`, `γ₃ = ε(J_a/J_t)ω₃ b×ḃ` |
| `euler_roll_const` | same Euler equation, `ω̇₃ = ω̇⬝b + ω⬝ḃ` | `J_a ω̇₃ = 0` | roll rate conserved; R0 (`ω₃ ≡ 0`) needs no roll torque |
| `hasDerivAt_cop` | `r' = v`, `b' = ω×b` | `(r + εb)' = v + ε ω×b` | boundary velocity of `y` |
| `cop_boundary`, `cop_terminal` | — | `(r₀,v₀) ↦ (r₀+εb₀, v₀+εω₀×b₀)` is translation by `copShift ε b₀ ω₀`; at rest upright, `r = v = 0 ⇔ y = εb_f, ẏ = 0` | affine boundary-data map |
| `tvcSet_eq_preimage_translate`, `convex_tvcSet_iff` | `∀θ, θ ∈ F_TVC ↔ θ + shift ∈ F_y` | `F_TVC = (·+shift)⁻¹' F_y`; `Convex F_TVC ↔ Convex F_y` | "F_TVC is a translate of F_y" |

Scope: constant `m, J_t, J_a, L` (so constant `ε`); axisymmetric inertia, pivot on the symmetry axis. The link
"`θ ∈ F_TVC ↔ θ + shift ∈ F_y`" for a concrete trajectory-level definition of `F_TVC` is the hypothesis of
`convex_tvcSet_iff`; it is what `cop_identity(_roll)` + `cop_boundary` + `cop_terminal` give pointwise, but no
trajectory-level pure-TVC landing set is defined in Lean. Mass depletion (`ε(m)` varying, extra `2ε̇ḃ + ε̈b`) is not covered.

## 2. TVC-1: the non-computational skeleton (math/06 §§2.4, 3, 4.5, 4.7; CLAIMS row TVC-1)

| Lean | Content | Mathematics |
|---|---|---|
| `qf M x`, `qfL x` | `xᵀMx` on `Fin n → ℝ`, linear in `M` | quadratic forms of the discretized certificate |
| `sprocedure_finsler` | `(Σ_k λ_k G_k + Σ_j ρ_j m_j m_jᵀ − Q).PosSemidef → xᵀQx ≤ Σ_k λ_k xᵀG_kx + Σ_j ρ_j (m_j⬝x)²` for all `x` | S-procedure (torque multipliers λ) + Finsler (moment multipliers ρ), finite-dimensional |
| `sprocedure_finsler_sum` | the same summed over the `c` components `x i` of a vector tilt | TVC-Q1 separability: the vector bound equals the sum of scalar bounds (no planarity) |
| `structure TVC1Certificate n K J` | data `Q, G_k, λ_k, c_k, ρ_j, m_j, Pen_max, M^v_j, shift_j, U` with `λ, ρ ≥ 0`, **`matrix_ineq`** (the PSD condition above) and **`scalar_ineq`** (`Σλ_kc_k + Σρ_j(M^v_j + shift_j P)² − P ≤ U` for `P ∈ [0, Pen_max]`) | Def. 4.5 + §4.7 `U_tot`. **These two fields are the certified numerics. They are NOT proved in Lean: they are verified externally in exact rational / Arb ball arithmetic by `numerics/verify-tvc/exact_cert.py` (matrix, by exact integer Sylvester minors; remainders, absorption, V_λ in Arb) and `numerics/verify-tvc/moment_check.py` (moment term), see math/verify-tvc-report.md §3.** |
| `structure TVC1Reduction C c gain Frel Z` | for every `θ ∈ F^rel ∩ Z` there are `x : Fin c → Fin n → ℝ`, `P ∈ [0, Pen_max]`, `D`, `e_k` with `gain θ ≤ Σ_i 𝒬(x_i) − P − D`, `Σ_i G_k(x_i) ≤ c_k + e_k`, `Σ_k λ_k e_k ≤ D`, `Σ_i (m_j⬝x_i)² ≤ (M^v_j + shift_j P)²` | **the analytic reduction of a competitor to certificate data, NOT formalized**: §4.0 localization, §4.1–4.3 majorants and homogeneous torque remainders, §4.4 moments, §4.5 absorption (i), §4.7 bathtub, Lemma 4.6′ discretization (Wirtinger) |
| `gain_le_of_certificate` | `TVC1Certificate` + `TVC1Reduction` ⇒ `∀ θ ∈ F^rel ∩ Z, gain θ ≤ U` | §4.5 "Use" + §4.7: every zero-lateral relaxed competitor has gain ≤ U_tot |
| `tvc1_skeleton` | `F^X ⊆ F ⊆ F^rel`, `Rot` linear involution preserving `F^X`, `ℓ` linear `Rot`-invariant, witness `θ_w ∈ F^X` with `ℓθ_w − κ ≥ G_w`, `∀ θ ∈ F^rel, Rot θ = θ → ℓθ − κ ≤ U`, `U < G_w` ⇒ `mid θ_w (Rot θ_w) ∉ F^rel`, `¬Convex F^X`, and for every `Y`, `R : UniformConvexRelaxation X Y`: `¬R.IsLossless F^X` and `¬R.IsLosslessFor J F^X` for every cost `J` | Lemma 2.4 + Theorem TVC-1 conclusion + Theorem A |
| `rotPi`, `rotPi2`, `rotPi2_invol`, `rotPi2_fixed_iff` | `R_π = diag(−1,−1,1)` on `(r₀,v₀)`; `R_π θ = θ ⇔ r_{0h} = v_{0h} = 0` | "zero lateral data" = fixed points of `R_π` |
| `ellFace`, `ellFace_rotPi2` | `ℓ(θ) = r_{0z} + s* v_{0z}`, `R_π`-invariant | the face functional `Λ_z` |
| `tvc1_main` | everything combined, on `ℝ³ × ℝ³`, gain `ℓ − κ` | **Theorem TVC-1, conditional on `TVC1Certificate` (external exact numerics) and `TVC1Reduction` (unformalized analysis)** |

**Concrete model (`TVC/Model.lean`).** Boundary data `θ = (r₀,v₀) ∈ E3 × E3`.

| Lean | Content | math/06 |
|---|---|---|
| `ordinarySet a₁ a₂ δ b`, `relaxedSet a₁ a₂ δ b`, `ordinarySet_subset_relaxedSet` | `{a d}` (gimbal cone) ⊆ `𝒞(b)` | PT2, PT6 |
| `TVCAdmissible C ε tf b ḃ u` | `u` integrable, `‖b‖ = 1`, `b(t) = e_z + ∫₀ᵗ ḃ`, `ḃ(t) = ∫₀ᵗ(−ε⁻¹Π_b u − ‖ḃ‖² b)`, `ḃ(0) = 0`, `b(tf) = e_z`, `ḃ(tf) = 0`, `u(s) ∈ C(b(s))` | PT1, PT3 (R0), PT4, Lemma 2.1 (`ε∇ḃ = −Π_b u`) |
| `tvcLandingSet C ε tf g₀ X` | some admissible control lands (`position`/`velocity` of `Model.lean` with `a ≡ 1`, `d = u`, gravity `−g₀e_z`, i.e. `r̈ = u − g₀e_z`) with `(r,v) ∈ X` on `[0,tf]` | PT4, PT5 |
| `tvcLandingSet_mono_X`, `tvcLandingSet_mono_C` | `F^X ⊆ F ⊆ F^rel` | "relaxed ⊇ ordinary" |
| `rotPiE`, `rotPiE_fixed_iff`, `rotPiE2_fixed_iff`, `tvcLandingSet_rot`, `ordinarySet_rot`, `relaxedSet_rot`, `glideSlopeSet_rotInvariant` | `R_π = 2⟪·,e_z⟫e_z − id` (linear isometry); landing sets are `R_π`-invariant; fixed points = zero lateral data | Lemma 2.4 |
| `tvc_lambda_identity` | `r₀ + s*v₀ = ∫(s−s*)u + (tf²/2 − s*tf)(−g₀e_z)` | Lemma 2.3 (translational part) |
| `Wz`, `ellE_eq_Wz` | `ℓ(θ) = W_z(u) + g₀tf(s* − tf/2)` with `W_z(u) = ∫(s−s*)⟪u,e_z⟫` | Lemma 2.3, §4.1 |
| `TVC1ReductionCtrl`, `TVC1ReductionCtrl.toReduction`, `tvc1_model_ctrl` | the reduction hypothesis stated for relaxed **controls** (gain `W_z(u) − J₀`, zero-lateral landing data); implies `TVC1Reduction` with `κ = J₀ + g₀tf(s* − tf/2)`; TVC-1 with a witness given as an ordinary control with `W_z(u_w) − J₀ ≥ G_w` | Theorem TVC-1 (control form) |
| `tvc1_model` | `tvc1_skeleton` instantiated with the concrete `F^X` (ordinary, any `R_π`-invariant `X`), `F` (ordinary, `X = univ`), `F^rel` (relaxed), `ℓ = ⟪r₀ + s*v₀, e_z⟫`: from witness + `TVC1Certificate` + `TVC1Reduction` (for the concrete `F^rel`) ⇒ `¬Convex F^X`, no lossless uniform relaxation | Theorem TVC-1 |

Also not formalized: the witness (`θ_w ∈ F^X` with gain `G_w`; math/06 §4.8, certified in Arb by `witness_check.py`) enters as the
hypotheses `hw`, `hGw` of `tvc1_main`; `F^X ⊆ F ⊆ F^rel` and `R_π`-invariance of `F^X` are hypotheses (no concrete pure-TVC landing set
is defined in Lean). So `tvc1_main` formalizes the **logic** of TVC-1, with all model content and numerics as named hypotheses.

`TVC/Pointwise.lean` (elementary inequalities used inside the reduction):

| Lean | Statement | math/06 |
|---|---|---|
| `early_tilt_identity` | `H = 1 − b_z²`, `1 + b_z ≠ 0` ⇒ `1 − b_z = H/(1 + b_z)` | §4.2 early, P1 |
| `speed_sq_le` | `b_z² + ‖h‖² = 1`, `b_z ḃ_z = −⟪h,ḣ⟫`, `|⟪h,ḣ⟫| ≤ ‖h‖‖ḣ‖` ⇒ `(‖ḣ‖² + ḃ_z²) b_z² ≤ ‖ḣ‖²` | P1: `v² ≤ ‖ḣ‖²/b_z²` |
| `late_majorant` | `a₂ > 0`, `p² + q² ≤ a₂²`, `b_z² + H = 1` ⇒ `(q²b_z² + a₂²H)/(2a₂) ≤ a₂ − p b_z` | P2 |
| `late_pi_ge`, `late_pi_ge_of_nonneg` | `f ≤ a₂`, `a₂ ≥ 0`, `b_z ≤ 1` ⇒ `b_z|a₂ − f| ≤ a₂ − f b_z`; and `|a₂ − f| ≤ a₂ − f b_z` if `f ≥ 0` | P3, §5.6 ((A2) dropped) |
| `sq_add_le_split`, `sq_sub_pos_ge_split` | `(x+y)² ≤ (1+κ)x² + (1+1/κ)y²`; `(1−ϑ)x² − (1/ϑ−1)y² ≤ (x−y)²` | §4.3, Q4 |
| `cell_wirtinger` (`TVC/Discretization.lean`) | `n ⊥ {1,t}` on a cell `[0,h]` ⇒ `∫(∫_0^t n)² ≤ (h/2π)² ∫ n²` (zero ends + zero mean; via [lean-s]'s `Slice.periodic_wirtinger`) | Lemma 4.6′, TVC-Q3 |
| `cell_sup_bound` | same hypotheses ⇒ `(∫_0^t ∫_0^u n)² ≤ h³/(4π²) ∫ n²` on the cell | Lemma 4.6′, TVC-Q3 |
| `relaxed_contains_ordinary` | unit `b, d`, `angle d b ≤ δ < π/2`, `0 ≤ a₁ ≤ a ≤ a₂` ⇒ `u = a d` has `⟪u,b⟫ ≥ a₁cos δ`, `‖u‖ ≤ a₂`, `‖u − ⟪u,b⟫b‖ ≤ ⟪u,b⟫ tan δ` | PT6 "⊆" (ordinary ⊆ relaxed) |

## 3. B* with mass depletion α > 0 (math/02 §10; CLAIMS rows B*, P-B*)

Previously B* was formalized only for constant acceleration bounds (constant mass). The mass-depletion version is now proved.

**Why the old proof did not adapt directly.** `VStar_not_mem_WSet` compares every competitor with the pointwise bound
`h* = (s−s*) a_min cos(δ+ωs)` (dive) / `(s−s*) a_max` (brake). With mass depletion no single throttle history attains both the
minimal dive acceleration and the maximal brake acceleration, so `V* = ∫h*` is not attained and the witness midpoint is not
`V* e_z`. The fix (math/02 §10.3 Steps 3–4) compares each competitor with its **own** acceleration, and needs a maximiser of the
resulting functional over the mass class; we construct it explicitly instead of using weak-* compactness.

| Lean | Content | Mathematics |
|---|---|---|
| `phiW`, `PhiFace tf ω δ s* a` | `φ(s) = min(s−s*,0)cos(δ+ωs) + max(s−s*,0)`; `PhiFace a = ∫₀^tf a φ` | `V(T)` of (10.1): the attitude-maximised `⟪W, e_z⟫` for fixed throttle |
| `PhiMax_not_mem_WSet` | `Acc` members integrable with `a ≥ a_min > 0`; `PhiFace a ≤ V` on `Acc` ⇒ `V e_z ∉ WSet` | Step 6 for any acceleration class |
| `witnessG_W_midpoint`, `witnessG_mem_glideSlope` | mirror witnesses with arbitrary throttle `â`: midpoint of `W` is `PhiFace â • e_z`; glide slope holds if `0 ≤ â ≤ A` (dive), `â ≥ B ≥ g₀ ≥ 0` (brake), `(B + 2tanγ A)s*² ≤ (B − g₀)(tf − s*)²` | Steps 2, 5 |
| `not_convex_constrainedLandingSet_of_max` | B* for any class containing a face maximiser with those bounds | Theorem B*, abstract |
| `dive_identity` | `T` integrable, `m ≥ m_dry > 0` on `[0,tf]`, `α ≠ 0`: `∫₀^{s*} c T/m = α⁻¹(c(0) log m₀ + ∫₀^{s*} c′ log m)`, `c = (s*−s)cos(δ+ωs)` | integration by parts with `T/m = −α⁻¹(log m)′`; uses Mathlib's `AbsolutelyContinuousOnInterval.integral_mul_deriv_eq_deriv_mul`, Lebesgue differentiation, `log` Lipschitz on `[m_dry,∞)` |
| `cWd_nonpos` | `c′ ≤ 0` on `[0, s*]` | dive value increasing in the mass history |
| `exists_sigma_compare` | for admissible `T` there is `σ ∈ [0,s*]` with `m_σ(s*) = m_T(s*)` and `m_T ≤ m_σ` on `[0,s*]` (`m_σ`: min throttle on `[0,σ]`, max after) | comparison (new; replaces compactness) |
| `brake_le` | on `(s*,tf]`: `T/m ≤ ρ₂/(m(s*) − αρ₂(s−s*))`, denominator `≥ m_dry` | Step 3 |
| `phiFace_decomp`, `wval`, `continuous_wval`, `phiFace_le_wval`, `phiFace_aSig` | `PhiFace(T/m) ≤ w(σ_T)`, `PhiFace(a_σ) = w(σ)`, `w` continuous | Step 4 |
| `exists_max_phiFace_mass` | ∃ `σ* ∈ [0,s*]`: `aSig σ*` maximises `PhiFace` over `AccMass` | the maximiser `T*` (explicit switch form) |
| `aSig_mem` | switch profiles are in `AccMass` | admissibility of the witness |
| `not_convex_constrainedLandingSet_mass` | hypotheses below + `s*` conditions ⇒ `¬Convex (constrainedLandingSet (AccMass …) …)` | **Theorem B*, α > 0** |
| `no_lossless_relaxation_constrained_5dof_mass`, `no_losslessFor_…_mass` | headline, every `tf > 0` | **Main theorem, state-constrained, mass depletion** |
| `no_lossless_relaxation_constrained_upright_5dof_mass` | with `b(tf) = e_z` (variant T′) | |
| `no_lossless_relaxation_constrained_6dof_mass`, `…_upright_6dof_mass` | kinematic 6DOF (proper rotations, any roll), free / upright terminal attitude | |

Hypotheses of the headlines: `tf > 0`, `ω > 0`, `0 < δ < π/2`, `0 < ρ₁ < ρ₂`, `α > 0`, `0 < m_dry ≤ m₀ − αρ₂ tf` (a full-throttle
burn over the whole horizon stays above dry mass; this is the condition verify-imp asked for), `0 ≤ g₀ < ρ₂/m₀`
(full-throttle thrust-to-weight > 1 at the initial mass), `tanγ ≥ 0`, any `X ⊇ glideSlopeSet tanγ`. Switch-time conditions used
by `not_convex_constrainedLandingSet_mass`: `0 < s* < tf`, `ωs* ≤ δ`, `δ + ωs* ≤ π/2`,
`(ρ₂/m₀ + 2tanγ·ρ₂/m_dry) s*² ≤ (ρ₂/m₀ − g₀)(tf − s*)²` (always satisfiable, `exists_switchTime`).
`ρ₁ = ρ₂` (no throttling) is excluded only for convenience (the comparison divides by `ρ₁ − ρ₂`); α = 0 is the existing theorem.

## 3a. B*, free final time on a compact window (math/02 Cor. 10.4; CLAIMS rows P-B*, LS)

| Lean | Content |
|---|---|
| `not_convex_iUnion_of_max` | abstract: horizon-dependent class `Acc t` (`t ∈ [t_a,t_b]`, `s* < t_a`), face bound `PhiFace_t a ≤ V_max(t)`, `t ↦ V_max(t) + g₀ t (s* − t/2)` continuous on the window, a witness attaining `V_max(t)` with the B* bounds ⇒ `⋃_{t ∈ [t_a,t_b]} F^X_t` not convex. Proof: maximise `ℓ*(t)` at `t°`; a midpoint landing at `t'` would have `W = V e_z`, `V = V_max(t°) + κ(t°) − κ(t') ≥ V_max(t')`, excluded by `PhiMax_not_mem_WSet` at horizon `t'` |
| `phiFace_le_VStar`, `phiFace_aW`, `continuousOn_VStar` | constant-bounds instance ingredients |
| `constrainedLandingSet_mass_nonempty` | non-vacuity: under the headline hypotheses the mass-depletion constrained set is nonempty |
| `not_convex_iUnion_constrainedLandingSet_box`, `no_lossless_relaxation_freeTime_5dof` | free final time, constant bounds (`α = 0`), every window `0 < t_a ≤ t_b` |
| `continuous_wval₂`, `not_convex_iUnion_constrainedLandingSet_mass`, `no_lossless_relaxation_freeTime_5dof_mass` | free final time, mass depletion; `V_max(t) = sup_{σ∈[0,s*]} w_t(σ)` is continuous in `t` (`IsCompact.continuous_sSup`); needs `m_dry ≤ m₀ − αρ₂ t_b` (the verify-imp window condition) |

"Free final time" here means: the boundary-data set of the free-`t_f` problem with `t_f ∈ [t_a,t_b]` is the union of the
fixed-horizon sets, and that union is not convex, so (Theorem A) no single uniform convex relaxation of the free-time problem is
lossless. (The line-search variant RR-LS is in `FreeTime.lean`; its concrete hypotheses (H2)/(H3) are not instantiated here.)

## 3b. B*, quantitative (math/02 §10.3 Step 7; CLAIMS row P-B*)

Constant acceleration bounds `0 < a_min ≤ a_max` (any class `Acc` whose members satisfy them), `0 < δ ≤ π/4`, `ωs* ≤ δ`,
`0 < s* < t_f`. Notation: `ϑ = a_min sin δ/(4a_max)`, `τ = ϑs*`, `c₁ = 1/(ωτ)`, `γ_X = (5/32) a_min sin δ s*²`,
`W_b = a_max(t_f − s*)²/2`, `Λ(θ) = r₀ + s*v₀`, `θ_m` = midpoint of the two mirror dive-then-brake witnesses (min-then-max
throttle).

| Lean | Content | Step 7 |
|---|---|---|
| `le_sqrt_of_forall_amgm`, `norm_lateral_le_amgm` | AM-GM replacements for Cauchy–Schwarz | (v) |
| `brake_lateral_le` | `‖B_h‖ ≤ √(2W_b η_b)`, `η_b = ∫_{(s*,tf]}(s−s*)a(1−d_z)` | (v) |
| `cos_sub_cos_ge` | `(y−x) sin m ≤ cos x − cos y` for `−π/2 ≤ m ≤ x ≤ y ≤ π/2` (MVT) | (iii) |
| `dive_lateral_ge` | `γ_X − η_d/(ωτ) ≤ ‖X_h‖`, `η_d = X_z − ∫_{[0,s*]}(s*−s)a cos(δ+ωs)`, via the tilted reference `c_τ = b(τ)` | (i)–(iv) |
| `lambda_dist_ge` | for every `θ ∈ F_tf` (unconstrained) and every `η₀ ≥ 0` with `(1+c₁)η₀ + √(2W_bη₀) ≤ γ_X`: `η₀ ≤ ‖Λ(θ) − Λ(θ_m)‖` | (vi) |
| `norm_lambda_le`, `landingSet_dist_ge` | `η₀/(1+s*) ≤ ‖θ − θ_m‖` (max-norm on `ℝ³ × ℝ³`; math/02 uses `√(1+s*²)` with the Euclidean product norm) | distance form |
| `exists_eta0`, `midpoint_not_mem_closure_landingSet` | an explicit `η₀ > 0` exists; `θ_m ∉ closure F_tf` | "x̄* ∉ cl F" (δ ≤ π/4) |
| `lambda_dist_ge_of_max` | the same bound for any class with `a_min ≤ a ≤ a_max` and a face maximiser `â` (witnesses with throttle `â`; deficit `PhiFace(â) − W_z ≥ η_d + η_b`, Remark 10.3) | Step 7, general |
| `landingSet_dist_ge_mass` | mass depletion: with the mass face maximiser `â`, `dist(θ_m, F_tf) ≥ η₀/(1+s*)` for `a_min = ρ₁/m₀`, `a_max = ρ₂/m_dry` | Step 7, α > 0 |

## 4. Not formalized (honest list)

* TVC-1: the analytic reduction (`TVC1Reduction`), the witness, the certified numerics (`TVC1Certificate`), and a concrete
  trajectory-level pure-TVC landing set. Lean checks only the logical skeleton and the finite-dimensional S-procedure step.
* FLAT with varying `ε(m)`; FLAT link to a trajectory-level `F_TVC` (taken as hypothesis in `convex_tvcSet_iff`).
* B*: envelope version (§10.6); free final time is formalized only on compact windows (unbounded free time has no such face, Cor. 10.4 remark).
