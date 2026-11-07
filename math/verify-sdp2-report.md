# Referee report VERIFY-SDP2: math/09 (CSD2′ partial proof)

Referee: [verify-sdp2]. Date 2026-11-07 (system clock, started 01:44). Hostile, line-by-line, independent numerics.
Inputs read: comms/PROTOCOL.md, comms/CLAIMS.md (CSD2′, SDP-*, CSD2′-T1…T5, P6, P7, CSD2″), math/09-csd2-prime.md (under
review), math/08-sdp-exactness.md (Thm 2.1, 2.4, Prop 6.1), math/verify-pos6-report.md §3, math/04 (C-W, Aumann),
math/verifier-sdp-report.md §5 (index check on N=16–48 banks).
Numerics: numerics/verify-sdp2/ (own venv, own implementation `core.py`; nothing imported from proof-csd2p, verifier-sdp or
proof-sdp code). Single-threaded BLAS, at most 2 concurrent processes.

## 0. Verdict table

| Result | Verdict | One-line reason |
|---|---|---|
| **T1** alignment / CSD2′ ⇔ R_X ∩ E² = R_3 | **CONFIRMED** | e_z-fixing orthogonal group + extreme points of {X : XᵀX ⪯ Γ}; equivalence needs only closedness of R_3. Wording: "attained" and "R_X compact" are not proved for infinite-dim X and are not needed |
| **T2** primer-plane fold ⇒ every linear objective exact (closes SDP-F) | **CONFIRMED** (scope wording) | fold is norm-preserving, inner-product-increasing, fixes Π pointwise and e_z. Valid for every linear functional of the readout (V,R) (more generally ℓ_i ∈ Π, plus nonnegative ⟨·,e_z⟩ terms under max). NOT for arbitrary ℓ_i ∈ E (e.g. attitude costs ∫⟨b,c(t)⟩ with c(t) spanning E). dim Π ≤ 1: choose m := P_{Π⊥∩E}e_z/‖·‖. Numerics: 180 generic + 11 adversarial instances, fold feasible to 1e-7, objective kept to 1e-14, SDP = NLP3 to 4e-10 |
| **T3** continuous stress certificate, J_red, κ | **CONFIRMED given (H)** (one sign) | Lagrangian ≤ J_w on admissible pairs, stationarity ⇔ (S_u),(S_b) + boundary term, Q⊗I ⪰ 0 ⇒ convex. λ, μ_u, q = κ − ν‖ḃ‖² re-derived (numerically 1e-14). κ = **−**∂²σ/∂ε² (not +). (H) is a hypothesis; the "Derivation" paragraph is a sketch (mixed constraint; normality not automatic in case T) |
| **T4** hemisphere / Picone (Thm 4.1 continuous, Thm 4.4 discrete) | **CONFIRMED** (Thm 4.1 given (H); Thm 4.4 rigorous) | Picone identity, μ_u = 0 slots, density, Schur step on μ_d ≥ 0, Z-matrix lemma all re-done. 600 criterion-true KKT points: all Q ⪰ 0 and exact; 0 of 107 non-global local KKT points pass the criterion; vertical-shortfall hunt: 1,853 KKT points on 60 instances, every one global (value spread ≤ 4.5e-9) |
| T4 Cor 4.3 (a-priori vertical-shortfall class) | **NEEDS FIX (minor)** | algebra correct, but "the lift is exact for these targets" is unconditional while the proof needs a normal KKT multiplier set (H) at some genuine optimum (case T: normality not automatic; discrete: a CQ). Add the hypothesis; give the discrete form (s ∈ {h/2, tf−h/2}) |
| **T5** Thm 5.1 index identity | **CONFIRMED** (discrete, under Z nonsingular, Yres invertible) | Haynsworth + congruence re-derived. C_yw symmetry is a *consequence* of KKT (stationarity along the e_z-rotation), not a hypothesis. Covers on-axis targets (C_yw = 0, p₀ = 2). Numerics: 309/309 under hypotheses, 892/892 incl. singular Z |
| T5 Thm 5.2 Sturm bounds | **NEEDS FIX** | case T: correct under its hypotheses (add D ≻ 0 and strictly negative coupling to the virtual end nodes to the hypothesis list); 124/124. Case F: proof (virtual nodes at *both* ends) does not apply; the correct statement is sharper, **neg Z = k exactly** (proof §5.3), hence in case F: k ≤ p₀ ⇔ exact, no residual class; 64/64. Hypotheses fail at most genuine optima (fresh banks: 188/898; c1: 9/17), and outside them the bounds fail (70/376) and k ≥ p₀+2 occurs at exact optima. The §0/§8 claims "T5 certifies 85% / 16 of 17 c1 cases" must be restated |
| **P6** no free singular arcs | **CONFIRMED** | first- and second-order expansion re-done (τ = εη⟨u,m⟩ + ε²(ηζ − ½cosδ η²) + O(ε³)); cross terms vanish since b ∈ Π ⊥ m on I. Notation: slack ε and variation ε collide |
| **P7** unit-d failure mechanism | **CONFIRMED as mechanism + numerics; NEEDS FIX (minor)** | "the diagonal entry μ_k of Q is negative" is false: Q_kk = C_kk + μ_k; it is the diagonal of Z. Rigorous part: ≥ 3 negative μ_d ⇒ Q ≱ 0 (rank-2 C). Fresh: 8/8 unit-d gap instances have μ_d < 0 (only 1–2 segments, so the rigorous route does not cover them; coupling to b-tilts is numerical), Q ≱ 0; convexified versions exact, μ_d ≥ 0, Q ⪰ 0 |
| **§7** physical meaning (Aumann: genuine b + unit-thrust selection, same terminal state) | **CONFIRMED** (wording) | Aumann for t ↦ k(t)⊗cap(b(t),δ) gives exact equality of (V,R), hence of the terminal (r,v), with the same b. Wording: the selection is a measurable unit-norm direction in cap(b,δ) (extreme-point / Lyapunov "bang-bang"), not a gimbal-saturated ±δ law; it generally chatters (unbounded gimbal bandwidth); exact at the terminal time (or finitely many prescribed times), uniform approximation only of the whole history; discrete D^cvx only to discretization accuracy; Aumann cited, not proved |
| Orchestrator query: non-symmetric C_yw ([verifier-sdp] idx_full) | **No issue with T5** | all 14 records with asym > 1e-6 have C_yw ≈ 0: 12 on-axis targets (|w_h| ~ 1e-15) and 2 with zero lateral residual (|y_h| ≤ 2e-7, recomputed). Asymmetry = normalisation by max|C_yw| ≈ 0. Script should use an absolute scale (§5.4) |

**No BROKEN item.** The math/09 verdict "CSD2′ not fully proved, not broken" stands. Repairs below are statement-level.

---

## 1. T1 (alignment): CONFIRMED

- Step 1. O := {U orthogonal on X, Ue_z = e_z}. Every constraint is a norm, an inner product or an inner product with e_z, so O
  preserves admissibility. ⟨UV, e_z⟩ = ⟨V, Uᵀe_z⟩ = ⟨V, e_z⟩, so only the lateral term changes. V_h here is the component of V in
  e_z^⊥ ⊂ X, which may have E⊥ parts. Correct.
- Step 2. K_Γ = {X ∈ E_h² : XᵀX ⪯ Γ} is an LMI set ([[Γ, Xᵀ],[X, I]] ⪰ 0), hence convex and compact. The lateral term is linear on it.
- Step 3. Extreme points satisfy XᵀX = Γ. For Γ ≻ 0, X = YΓ^{1/2} with ‖Y‖_op ≤ 1, whose extreme points are orthogonal. For rank Γ = 1,
  X = y gᵀ/‖g‖² with ‖y‖ ≤ 1, extreme points ‖y‖ = 1. Any X with XᵀX = Γ is the image of an isometry span(V_h,R_h) → E_h, which extends to
  some U ∈ O (finite-dimensional partial isometry inside e_z^⊥, complements of equal Hilbert dimension). Correct.
- Step 5. V_X(w) = inf{‖Y−w‖² : Y ∈ R_X ∩ E²} and V_3(w) = dist²(w, R_3). (⇐) trivial. (⇒) for Y ∈ R_X ∩ E² take w = Y: V_3(Y) = 0, so
  Y ∈ cl R_3 = R_3 (R_3 compact in finite dimension: Arzelà–Ascoli for b, weak-* for u, K(b) convex). R_3 ⊆ R_X ∩ E² always.
- **Wording:** the §0 table says the lifted infimum is "attained", and §2.1 calls R_X "compact". Neither is proved for infinite-dimensional
  X (Arzelà–Ascoli fails; weak limits of unit vectors leave the sphere), and neither is used. For finite-dim X both hold. Replace by
  "V_X(w) = inf over lifted pairs with Y ∈ E²".

## 2. T2 (primer-plane fold): CONFIRMED (scope wording)

- F(x) = P_Π x + ‖P_{Π⊥}x‖ m. Since m ⊥ Π: ‖Fx‖ = ‖x‖; ⟨Fx,Fx′⟩ − ⟨x,x′⟩ = ‖P⊥x‖‖P⊥x′‖ − ⟨P⊥x,P⊥x′⟩ ≥ 0; ⟨Fx,p⟩ = ⟨x,p⟩ for p ∈ Π.
  For dim Π = 2: e_z ∈ E and Π ⊆ E give P_{Π⊥}e_z ∈ E ∩ Π⊥ = ℝm, so F(e_z) = ⟨e_z,m⟩m + P_Π e_z = e_z (⟨e_z,m⟩ ≥ 0). Correct.
- Constraints: unit/≤1 norms kept; rate ‖Fb(t)−Fb(s)‖² = 2 − 2⟨Fb(t),Fb(s)⟩ ≤ ‖b(t)−b(s)‖² (unit vectors), so the Lipschitz constant ω
  survives; gimbal ⟨Fu,Fb⟩ ≥ ⟨u,b⟩ ≥ cos δ; discrete chord and both lens half-spaces likewise; boundary values fixed. Objective
  ⟨y,Y⟩ = Σ_c ∫k_c⟨y_c,u⟩ unchanged because y_c ∈ Π. Image ⊆ Π ⊕ ℝm = E. Correct, in continuous time and D^unit, D^cvx, D^0.
- **Scope (wording fix).** "Every linear objective" must read "every linear functional of the readout (V,R)", equivalently costs
  Σ⟨z_i,ℓ_i⟩ with all ℓ_i ∈ Π = span(y_v,y_r). Since ⟨Fx,e_z⟩ ≥ ⟨x,e_z⟩ (not =), terms c⟨z_i,e_z⟩ are allowed only with the sign that the
  fold improves. A general linear cost on the attitude (ℓ_{b_k} spanning E, e.g. ∫⟨b,c(t)⟩ with varying c) is not covered.
  The SDP-F open item was the readout case with dim E_w = 3, which T2 does close.
- **Degenerate Π.** If dim Π ≤ 1 the text's "m ⊥ Π in E" is ambiguous; F(e_z) = e_z needs m := P_{Π⊥∩E}e_z/‖·‖ (any m if e_z ∈ Π). Add.
- **Numerics (t2_linear.py → t2_linear.txt).**
  - 180 generic instances: unit15, unit40, cvx15, cvx40, d0; case T/F; N=4,7; ωtf=1, 2.5, 5; ramp thrust profile; random y with
    non-parallel laterals. Constructive check: the SDP factor (ranks 3–10) folded is feasible in ℝ³ to ≤ 1.1e-7 (solver accuracy),
    objective kept to ≤ 2e-14, and SDP = best 3D NLP to ≤ 3.7e-10 relative.
  - Adversarial: case 12 (unit-d *quadratic* gap instance) along its own residual direction ±y and a random direction, and 8 N=3
    unit-d instances (δ=15°, 40°). All exact.
  - The fold of the rank-4 quadratic optimum of case 12 is feasible with ⟨y,Y⟩ kept exactly, but its quadratic cost is 2450.8 vs
    SDP 0.0275. This illustrates the §2.2 remark that the fold does not finish the quadratic case.

## 3. T3 (continuous stress): CONFIRMED given (H); one sign

- Sign of each multiplier term on admissible pairs: ν(‖ḃ‖²−ω²) ≤ 0, −λ(⟨u,b⟩−cos δ) ≤ 0, μ_u(‖u‖²−1) ≤ 0, μ_b term = 0. So L ≤ J_w.
- L = 𝒬 − 2⟨w,Y⟩ + const with Q[η,ζ] = |∫kζ|² + ∫νη̇² + ∫(μ_bη² − ληζ + μ_uζ²). Re-derived.
- First variation in (η,ζ) ∈ ℋ⊗X: ζ-part gives μ_u u − (λ/2)b = P (P = −k·y); η-part after integration by parts gives
  (νḃ)˙ = μ_b b − (λ/2)u, with boundary term 2⟨νḃ,η⟩|_{tf} killed by η(tf)=0 (T) or (νḃ)(tf)=0 (F). E⊥ components vanish. Then
  L(z) = L(z*) + 𝒬(z−z*) ≥ L(z*) = J_w(z*) (complementary slackness). Correct.
- μ_b = (λ/2)⟨u,b⟩ − ν‖ḃ‖² (dot (S_b) with b; ⟨(νḃ)˙,b⟩ = −ν‖ḃ‖²). Completing the square gives q. In the plane (b,P) at a gimbal-active
  point: μ_u sin δ = ‖P‖sin θ, μ_u cos δ − λ/2 = ‖P‖cos θ, hence λ = 2‖P‖sin(θ−δ)/sin δ, μ_u = ‖P‖sin θ/sin δ, and
  (λ/2)cos δ − λ²/(4μ_u) = ‖P‖sin(θ−δ)cot θ = κ. Checked numerically over 2000 random (δ,θ,‖P‖): 1.7e-14 (t3_kappa.py).
- **Sign fix.** With b_ε = cos ε b + sin ε n out of the plane, cos θ_ε = cos ε cos θ, so σ_ε = σ − ½κε² + O(ε⁴): **κ = −∂²σ/∂ε²**
  (finite differences confirm to 1.6e-5). "κ is the second derivative of the Hamiltonian σ" should read "of −σ" (the cost curvature).
- **(H) is a hypothesis, not derived.** The "Derivation" paragraph is a sketch. Two gaps: the mixed state–control constraint
  ⟨u,b⟩ ≥ cos δ needs a PMP for mixed constraints (uniform Slater holds: u = ½(1+cos δ)b, so Dmitruk/Clarke–de Pinho type results
  apply); normality is automatic in case F, not in case T (b(tf) = e_z is a terminal constraint). T3 is correctly labelled "given
  (H)" in the CLAIMS row. Keep that label wherever T3/T4 are quoted (paper).
- §1's "dim X = 4 already suffices for normal extremals (math/08 §5)" is not established (verify-pos6: rank ≤ 4 needs dim E_w = 3
  plus nondegeneracy). It is not used. Delete or qualify.

## 4. T4 (hemisphere / Picone)

### 4.1 Thm 4.1 (continuous): CONFIRMED given (H)
- Step 1 identities re-derived. Step 2: on {μ_u > 0}, J_red h = (λ/2)h_u − λ²h/(4μ_u) = (λ/2μ_u)⟨P,c⟩ ≥ 0. On {μ_u = 0}: λb = −2P, so
  ⟨P,c⟩ = −(λ/2)h ≥ 0 with h > 0 forces λ = 0 = P. Correct.
- Picone identity expanded and checked term by term. The boundary term at tf (case F) vanishes since ⟨(νḃ)(tf),c⟩ = 0.
- **Integrability (add one line).** q = κ − ν‖ḃ‖² is unbounded where θ → π (cot θ → −∞), so J_red[η] with q is not a priori finite.
  On supp η ⋐ (0,tf), h ≥ h_K > 0. Condition (ii) then keeps P/‖P‖ away from −b, so θ ≤ π − ε_K and q ∈ L^∞(supp η). The algebraic
  identity μ_uζ² − ληζ = μ_u(ζ − λη/2μ_u)² − λ²η²/(4μ_u) holds pointwise. Q itself (no q) is continuous on ℋ, so density finishes the
  proof. The argument is right; it just needs saying.
- Cor 4.2 (a), (b): correct. (a) needs strict ⟨b*,m⟩ > 0; if ⟨e_z,m⟩ = 0, either orientation of m is allowed.

### 4.2 Thm 4.4 (discrete D^cvx, D^0): CONFIRMED (rigorous)
- Q = Z + ΓΓᵀ, Z a Z-matrix (cables −λ/2 ≤ 0; the free μ_b diagonal does not matter).
- (Zh_c)_{d_k} = ⟨P_k,c⟩ + ½Σλ_f⟨e_z,c⟩ and (Zh_c)_{b_k} = ½Σλ_f⟨e_z,c⟩ follow from Qz* = ℓ̃. Z_dd = diag(μ_d): there are no d–d cables.
  A μ_d = 0 slot has −½(λ_kh_{b_k} + λ′_kh_{b_{k+1}}) ≥ 0, hence a zero row. For d_0 and d_{N−1} in case T, the gimbal to e_z sits in
  ℓ̃, not Z. Generalized Schur (range condition holds), S again a Z-matrix, Sh_b ≥ 0 with h_b > 0, and the quadratic-form identity:
  all re-done.
- **Fixes (minor).**
  - In case F, b_N is a variable: the hypothesis must include ⟨b_N,c⟩ > 0. The LP should, and my implementation does, include it.
  - "μ_d ≥ 0, which is exactly the convexified lens" is an implication, not an equivalence. The same proof certifies any D^unit
    KKT point whose μ_d happen to be ≥ 0. Such a point is also a D^cvx KKT point.

### 4.3 Cor 4.3 (a-priori vertical shortfall): NEEDS FIX (minor)
- ωtf < π (T) / < π/2 (F) ⇒ b_z > 0: correct (geodesic distance ≤ ω min(t, tf−t)). With V_z ≤ ∫a and
  V_z + tf R_z ≤ ∫a(1 + tf(tf−t)), the affine factor −(y_{v,z} + (tf−t)y_{r,z}) is ≥ 0 at both ends. So P_z ≥ 0 at **every feasible**
  configuration, and c = e_z satisfies (i)–(iii) at every KKT point. Correct.
- **Gap.** The conclusion "the lift is exact for these targets" needs at least one genuine optimum carrying multipliers (H). That is
  automatic in case F (modulo the mixed-constraint PMP) but not in case T; in the discrete model it needs a CQ (e.g. MFCQ) at the
  optimum. **Repair:** "…exact at every such target at which some genuine optimum is a normal KKT point (H) (case F: always)".
- **Discrete form (add).** P_{k,z} ≥ 0 ∀k holds for every feasible point if w_{v,z} + s w_{r,z} ≥ Σ_k(cv_k + s cr_k) for
  s ∈ {h/2, tf − h/2} (the range of cr_k/cv_k).
- **Numerics (t4_short.py, t4_short_31.jsonl).** A sharp test: T4 implies that in this class *every* KKT point is global.
  - Setup: 60 instances, case T up to ωtf = 0.97π, case F up to 0.98·π/2, cvx15/25/40 and d0, N = 6/8/10, three thrust profiles,
    opposed large lateral demands, 30 starts each.
  - Result: 1,853 converged KKT points. Within each instance the local values agree to ≤ 4.5e-9 (relative). The criterion is true at
    all of them (min margin 0.86) and Q ⪰ 0 at all of them. SDP = NLP3 to ≤ 5e-11.

### 4.4 T4 on general fresh instances (t45.py, t45F.py; an45.py)
- Banks: 950 instances (t45_A, t45_B, t45F_F1). D^cvx δ ∈ {15,25,40}° and D^0; N ∈ {5,7,9}; thrust profiles const / mass-depletion
  1/(1−0.3t) / ramp-up / ramp-down; targets random, dent mixtures of two support points, vertical-shortfall, lateral overshoot; case
  T (70%) and F, plus a case-F-only run.
- 898 genuine optima with KKT residual < 1e-5:
  - all exact (relative gap ≤ 1e-5);
  - LP criterion true at 600, and at all 600 Q ⪰ 0 with SDP = NLP3;
  - 107 further non-global local KKT points found: **none passes the criterion** (a pass would have broken T4).

## 5. T5 (index identity, Sturm bounds)

### 5.1 Thm 5.1: CONFIRMED (under Z nonsingular, Yres invertible)
- Zh_x = −Γy_x from stationarity dotted with lateral x (λ_f e_z drops). Γᵀh_x = Y_x. ΓᵀZ⁻¹Γ = −Ymap Yres⁻¹.
- Haynsworth on [[Z,Γ],[Γᵀ,−I]]: neg Q + 2 = neg Z + pos M, zero Q = zero M. Hence neg Q = neg Z − (neg+zero)(M).
- M = −Wmap Yres⁻¹ is symmetric, YresᵀMYres = −C_yw, and Sylvester gives (neg+zero)(M) = p₀. Re-derived.
- **On the symmetry of C_yw (orchestrator query).** It is not a hypothesis and cannot fail at a KKT point.
  - The infinitesimal rotation about e_z, z ↦ Jz, keeps every constraint value fixed. KKT then gives ⟨∇f, Jz*⟩ = 0, i.e.
    Σ_c⟨Jy_c, w_c⟩ = 0, i.e. C_yw[0,1] = C_yw[1,0] exactly. The same holds at any local minimizer, without CQ.
  - Numerically non-symmetric C_yw therefore means non-convergence or C_yw ≈ 0. §5.4 shows it is always the latter in the
    [verifier-sdp] data.
- **Degenerate on-axis case w_h = 0 (C_yw = 0).** Wmap = 0 ⇒ M = 0 ⇒ p₀ = 2 and zero(Q) ≥ 2, the rotational symmetry. Thm 5.1 covers
  it whenever Z is nonsingular and Yres is invertible: neg Q = neg Z − 2. With Thm 5.2 (case T) every on-axis optimum with k ≤ 2 is
  certified. Worth a sentence in math/09.
- **Degenerate case y_h = 0 (lateral target reached exactly).** Yres is singular and the primer plane is vertical or undefined.
  Thm 5.1 does not apply, and the hypothesis is stated correctly. In that case Zh_x = 0 for every lateral x, so Z is singular unless
  b ≡ e_z. Such optima are certified only by T4 with c = e_z (when P_z ≥ 0) or by the direct stress test.
- **Numerics.**
  - Fresh banks: identity 309/309 with all Thm 5.1 hypotheses (Z nonsingular, |det Yres| > 1e-3 relative); 892/892 when singular Z
    is allowed. The singular parts decouple; this is not claimed in math/09.
  - [verifier-sdp] idx_full: 178/178 under the filters.

### 5.2 Thm 5.2, case T: CONFIRMED under its hypotheses (state them all)
- S is tridiagonal: each d_k links only b_k and b_{k+1}. h_m extended by the virtual nodes h_0 = h_N = ζ₀ solves the homogeneous
  recurrence. Interlacing of the principal solution with h_m gives k−1 ≤ neg S ≤ k. Correct.
- The hypotheses actually used are:
  - D = diag(μ_d) ≻ 0 (needed for neg Z = neg S);
  - strictly negative off-diagonals of S, **including the couplings of b_1 and b_{N−1} to the virtual end nodes**;
  - h_m ≠ 0 at every node, and ζ₀ > 0.
  The statement lists only the second and third. Add D ≻ 0 and the end couplings.
- Numerics: 124/124 instances satisfying all hypotheses obey the bounds. Of these, 72 are in the certified class (k ≤ p₀) and 52 in
  the residual class (k=2, p₀=1); all 52 residual have neg Z = k−1 (exact), extending [proof-csd2p]'s 16/16 and [verifier-sdp]'s
  35/35. Observed (k, neg Z, p₀, neg Q) ∈ {(0,0,0,0), (2,1,1,0), (2,2,2,0)}.

### 5.3 Thm 5.2, case F: NEEDS FIX, and the correct statement is sharper
- In case F there is no virtual node at N: b_N is a variable, and its row of Zh_m = 0 is homogeneous (natural boundary condition).
  The proof as written (virtual nodes at both ends) does not apply.
- **Correct statement (proved here).** Assume S is tridiagonal on b_1..b_N with strictly negative off-diagonals, including the
  coupling S_{1,0} to the virtual node b_0 = e_z; D ≻ 0; and ψ := (ζ₀, h_m(b_1), …, h_m(b_N)) has no zero entry. Then
  **neg Z = neg S = k** (the number of sign changes of ψ).
- *Proof.* Factor S = UDUᵀ from the bottom: d_N = S_NN, d_j = S_jj − S_{j,j+1}²/d_{j+1}. Rows N, N−1, … of Sψ = 0 (row 1 including
  the virtual term S_{1,0}ζ₀) give by induction d_j = −S_{j,j−1}ψ_{j−1}/ψ_j for j = N, …, 1. Since −S_{j,j−1} > 0, d_j < 0 ⇔
  ψ_{j−1}ψ_j < 0. Sylvester gives neg S = #{d_j < 0} = k. ∎
- **Consequence.** In case F, Thm 5.1 gives neg Q = k − p₀, so on nondegenerate instances **exact ⇔ k ≤ p₀** and
  **k ≥ p₀ + 1 ⇒ beaten in ℝ⁴**. There is no residual class, so CSD2″ in case F reads "k ≤ p₀ at some genuine global optimum".
- Numerics: 64/64 case-F instances satisfying the hypotheses have neg Z = k exactly (28 in t45_A/B, 36 in t45F). Observed
  (k, neg Z, p₀) ∈ {(0,0,0), (1,1,1), (2,2,2)}.
- **Remove from math/09 §8** the "observed (1,2,2) with free b(tf)". It comes from an excluded instance with h_m ≡ 0 (to 1e-11) at
  all interior nodes; I reproduce exactly this kind of instance (attitude inside Π) with h_min ≈ 1e-8 to 1e-11.

### 5.4 Scope of T5 in practice: NEEDS FIX (claims in §0/§8 and CLAIMS)
- The T5 hypotheses (Z nonsingular, connected chain, D ≻ 0, h_m ≠ 0) **fail at most genuine optima**. At every node with slack rate
  and slack gimbal, the multipliers vanish and the chain disconnects.
  - Fresh banks: all hypotheses hold at 188 of 898 optima; the failures are dominated by "Z singular + chain disconnected" (351
    in t45_A/B alone).
  - proof-csd2p's own idx3.jsonl: the "107/107 Sturm" set contains only 38 instances with Z nonsingular (summarize_strict.py with
    the Z filter).
  - c1 cases recomputed independently (c1_check.py): all 17 exact with neg Q = 0. But Thm 5.1's hypotheses hold for 11/17, and
    Thm 5.1+5.2 for 9/17 (cases 1, 3, 5, 7, 10, 11, 15, 16, 21). Cases 12 and 13 have a throttled node (μ_d = 0). Cases
    0, 2, 4, 6, 8, 9 have singular Z. Only case 4 passes the T4 LP.
- **Outside the hypotheses the crossing count carries no information.** Among 376 optima violating them with h_m ≠ 0, the Sturm
  bound fails in 70. Optima with k ≥ p₀+2 occur (e.g. (k, neg Z, p₀) = (4,0,0), (2,0,0), (6,0,0)) and are exact with Q ⪰ 0.
- **Repair.**
  - §0 "T5 certifies 16 of 17 c1 cases / 85%" → "the direct stress test (math/08 Thm 2.1) certifies all 17; T5's hypotheses hold
    at 9 of them".
  - Cor 5.3 and the "Physical reading" must carry the nondegeneracy hypotheses explicitly. In particular "k ≥ p₀+2 ⇒ beaten"
    is false without them.
  - Optional extension: on a disconnected chain, apply Thm 5.1/5.2 per connected component (interior components carry kernel
    vectors).
  - Index scripts must compute p₀ with an absolute tolerance (scale ‖y_h‖·‖w_h‖ or ‖Q‖), never relative to max|C_yw|. That
    relative normalisation produced the spurious "non-symmetric C_yw, p₀ = 1".
- **The [verifier-sdp] asymmetric records (orchestrator query).** asym_check.py re-solved both non-axis records with my code.
  - In idx_full.jsonl, 14 records have asym > 1e-6:
    - 12 are on-axis targets (|w_h| ≤ 3.6e-15), where C_yw ≡ 0 and the correct p₀ = 2, so neg Q = 2 − 2 = 0, as observed;
    - 2 are non-axis targets (cvx40, N=16, 24) with zero lateral residual, |y_h| = 2.2e-7 and 7.8e-13 (asym_check.txt), so C_yw ≈ 0
      and Yres is singular, outside Thm 5.1.
  - None is evidence against T5.
- Continuous analogue of T5: sketch only, correctly labelled; not refereed as a theorem.

## 6. P6 (no free singular arcs): CONFIRMED
- On I: P = −‖P‖b ∈ Π ⇒ b, ḃ ∈ Π ⊥ m. Optimality forces ⟨u,b⟩ = cos δ (otherwise move u toward −b).
- With b′ = cos(εη)b + sin(εη)m, u′ = u − τb + εζm, and ⟨u′,b′⟩ = cos δ:
  τ = εη⟨u,m⟩ + ε²(ηζ − ½cos δ η²) + O(ε³), and ΔJ = −2∫‖P‖τ + |∫k⊗Δu|².
- The b-component of ΔY is O(ε²). Its cross term with the m-component vanishes because ⟨m, b(s)⟩ = 0 on I. So
  ΔJ = −2ε∫‖P‖η⟨u,m⟩ + ε²[|∫kζ|² − 2∫‖P‖(ηζ − ½cos δ η²)] + O(ε³).
- ⟨u,m⟩ = 0 a.e. Then ζ = Mη with ∫kη = 0 (two linear conditions) gives ΔJ/ε² = −2(M − ½cos δ)∫‖P‖η² < 0. Norm and rate slack make it
  admissible.
- Notation: the slack ε in the statement and the variation ε in the proof collide. Rename one.

## 7. P7 (unit-d mechanism): CONFIRMED as mechanism; NEEDS FIX (minor)
- μ_k = ⟨P_k,d_k⟩ + ½(λ_k⟨d_k,b_k⟩ + λ′_k⟨d_k,b_{k+1}⟩): re-derived from 2μ_kd_k = λ_kb_k + λ′_kb_{k+1} + 2P_k.
- (a) "not a D^cvx KKT point" needs uniqueness of the multipliers (LICQ). Then D^cvx is strictly better.
- (b) **False as written:** "the diagonal entry μ_k of Q is negative". Q_kk = cv_k² + cr_k² + μ_k can be positive; μ_k is the diagonal of
  Z. The rigorous fact: with ≥ 3 segments having μ_d < 0, Q restricted to those d-slots is diag(μ) + (rank ≤ 2) and so has a negative
  eigenvalue. Fewer negative μ_d need the coupling to the b-tilts, which is numerical.
- (c) correct: K(b) = conv cap(b,δ), μ_u ≥ 0 by KKT sign.
- Numerics (p7_unit.py, p7_unit.jsonl): 8 fresh unit-d gap instances (N=3–5, δ=40°, gaps 0.16%–34%).
  - At the genuine unit-d optimum (LICQ holds): 1–2 negative μ_d, λ_min(Q) < 0.
  - After convexifying the lens: exact (|gap| ≤ 2e-8), μ_d ≥ 0, λ_min(Q) ≥ −5e-12.
  - None had ≥ 3 negative μ_d, so the "three segments" route covers none of them. "The unit-d gap is exactly μ_d < 0 + E⊥ tilt" is an
    empirical statement (13 + 8 instances), not a theorem.

## 8. §7 physical meaning: CONFIRMED (wording)
- For fixed genuine b, F(t) := k(t)⊗cap(b(t),δ) ⊂ ℝ⁶ is measurable, compact-valued, integrably bounded. conv F(t) = k(t)⊗K(b(t)), since
  x ↦ k⊗x is linear and conv cap = K(b). Aumann gives ∫F = ∫conv F, so a measurable unit selection u′ ∈ cap(b,δ) reproduces (V,R)
  exactly, hence the terminal (r,v) and, with a known a(t), the mass history. The genuine value equals the certified value and is
  attained. Correct; Aumann is cited (as in math/04 C-W, CONFIRMED by verify-pos6).
- **Wording.**
  - "Bang-bang gimbal selection" should read "full-thrust (unit-norm) direction selection in cap(b,δ)", the extreme points of K(b).
    It need not saturate the gimbal at δ, and it generally chatters (unbounded gimbal rate and bandwidth, as the text notes).
  - Exactness holds at tf (or at any finite set of prescribed times, by applying Aumann per subinterval). The whole state history is
    only uniformly approximated (Filippov–Ważewski).
  - In D^cvx the realization is to discretization accuracy only (§7.3, correct: the line along b_k × b_{k+1} keeps both lens inner
    products).

## 9. Requested edits (owner: proof-csd2p; I did not edit math/09)
1. T1: drop "attained"/"compact" for infinite-dimensional X, or restrict to finite dim.
2. T2: "every linear functional of the readout (V,R)" (ℓ_i ∈ Π); define m for dim Π ≤ 1.
3. T3: κ = −∂²σ; keep "given (H)" everywhere; qualify the "Derivation" (mixed-constraint PMP, normality in case T); delete or
   qualify "dim X = 4 suffices".
4. T4: integrability remark (§4.1); Thm 4.4 case F needs ⟨b_N,c⟩ > 0; "μ_d ≥ 0 is implied by, not equivalent to, the convexified
   lens"; **Cor 4.3: add the (H)/CQ hypothesis**, discrete form.
5. T5: add D ≻ 0 and the end couplings to Thm 5.2; **case F: replace by neg Z = k (proof §5.3) ⇒ exact ⇔ k ≤ p₀**; restate the
   §0/§8 certification counts (§5.4); remove "(1,2,2) with free b(tf)"; note the on-axis case (C_yw = 0, p₀ = 2) and that C_yw
   symmetry is a consequence of rotation stationarity; fix p₀'s tolerance in index_check.py.
6. P6: rename one ε. P7(b): "diagonal of Z"; state the ≥3-segment fact; mark the mechanism as empirical.
7. §7: "unit-norm selection in cap", not "bang-bang gimbal"; terminal-time (finitely many times) exactness.

## 10. Numerics index (numerics/verify-sdp2/)
| Script | Output | Content |
|---|---|---|
| core.py | — | independent D^unit/D^cvx/D^0 models (case T/F, arbitrary a_k), Gram SDP (Clarabel 1e-10), SLSQP multistart, KKT recovery, stress Q, Z, primer, h_m, C_yw, LP criterion |
| t2_linear.py | t2_linear.txt | T2: 180 generic + 11 adversarial linear objectives; constructive fold of SDP factors |
| t3_kappa.py | t3_kappa.txt | T3 pointwise algebra (λ, μ_u, q = κ) and κ = −σ_εε |
| t45.py, t45F.py, t45_lib.py, an45.py | t45_A/B.jsonl, t45F_F1.jsonl (+ .log) | T4 criterion, T5 identity/Sturm, exactness on 950 fresh instances |
| t4_short.py | t4_short_31.jsonl, t4_short.log | Cor 4.3 class: every KKT point global (1,853 points) |
| c1_check.py | c1_check.log | [numerics] c1 cases: which certificate actually applies |
| p7_unit.py | p7_unit.jsonl, p7_unit.log | P7 on fresh unit-d gap instances |
| asym_check.py | asym_check.txt | the two non-axis "non-symmetric C_yw" records of [verifier-sdp] |
