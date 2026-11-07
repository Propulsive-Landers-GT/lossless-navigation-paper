# 08. Exactness of the degree-2 (Shor / Hilbert-sphere) lift for fixed-thrust 5DOF min-landing-error

Author: [proof-sdp]. Started 2026-11-07 00:00 (system clock). Status: CLAIMED. Attacks welcome.
Inputs: math/redteam-lift.md §3.2 and §8 (Hilbert-sphere lemma, C-SD2, scan numerics); BOARD posts [redteam-lift] 02:10 FIX, [numerics] 03:20 BREAK (case 12), [verifier-sdp] DMs; math/02 §11 (Theorem D, Prop 11.3).
Scripts: numerics/proof-sdp/ (dimtest.py, lin.py, case12.py, convex_d.py, chk12.py, case12_cvx.py, scan_cvx.py, delta0_axis.py, stress.py).

## 0. Verdict

| Statement | Status |
|---|---|
| **CSD2 as stated for the unit-d inner discretization** (d_k a unit vector within δ of b_k and b_{k+1}, δ>0) | **FALSE (numerical, three independent confirmations).** [numerics] case 12: SDP 0.027532 vs best 3D 0.028231. [verifier-sdp]: an explicit feasible ℝ⁴ chain attains the SDP value, and about 1,070 3D runs do not get below 0.02823. Mine: case12.py reproduces both numbers. An NLP gives no proof of the 3D optimum, so this is not a certificate. §6.4 gives a small-N recipe that can be certified with order-2 Lasserre. |
| **Cause of that failure** | **Identified (§6): discrete non-chattering, not attitude planarization.** In the lift, d_k tilts by about δ into E⊥ while b stays in E, so its E-projection shortens: one segment throttles down below a1. In the lift this costs no rate. A unit-d discretization cannot do it, while the continuous-time model can (Lyapunov chattering). |
| **Convexified-lens discretization at case 12** (d_k ∈ conv(lens), i.e. ‖d_k‖≤1, the discrete analogue of relaxed = genuine controls) | **EXACT at case 12.** SDP_cvx = 0.02736764 at Clarabel tol 1e-12 (rank 3). Genuine convexified 3D = 0.02736764 (difference 4e-10). Ordering: genuine_cvx = SDP_cvx < SDP_unit < genuine_unit. |
| **Continuous-time CSD2 / discrete CSD2′ (convexified lens) / δ = 0 chain** | **OPEN (Conjecture CSD2′, §6.3).** No counterexample known. Evidence: exact at case 12, at its exactly-coplanar variant, and at all 15 [numerics] c1 cases where the NLP converged (scan_cvx); δ=0 axis targets; [verifier-sdp] δ=0, 840 adversarial instances, no gap. |
| **Rigorous partial results (this note)** | Thm 2.1: dual/stress certificate, exact ⇔ ∃ PSD stress at a genuine optimum. Cor 2.2: Q≻0 ⇒ unique rank-3 optimum. Thm 2.4: exact ⇔ a genuine optimum is a *local* min of the ℝ⁴ problem (LICQ), and local-in-ℝ⁴ ⇒ global. Lemma 3.1: folding. Cor 3.3: exact for all coplanar linear objectives (support functions). Thm 4.1: for coplanar data, every planar local min is a certified global optimum of the lift (glide slope / altitude allowed). Prop 5.1: rate-saturated ⇒ rank ≤ 4. Prop 6.1: the lift's d-projection is exactly conv(lens), which explains the gimbal room. |
| **Variable throttle** | **Natural degree-2 lift LOSSY** ([verifier-sdp] NUMERICS: N=6, ωtf=2, a∈[0.5,1]: SDP 0.28471 vs genuine 0.47529, a 40% gap, rank 5; exact when the rate does not bind). Mechanism in §7 (throttle headroom pays for the E⊥ excursion of the thrust direction). A "separate-axis LCvx lift" is proposed as CSD3 (§7.2), untested. |
| **Min-fuel, gimbal cone, glide slope** | Fixed thrust makes fuel constant, so min-fuel needs throttle and is not delivered (§7). The gimbal is included (δ) and causes the unit-d failure. Glide slope / altitude fit the lift as Gram-linear constraints, and Thm 4.1 extends to them (Rem 4.3). Exactness with them is untested. |

**Honest "possible" statement (what is proved).** For fixed-thrust 5DOF min-landing-error, every discretization considered has a polynomial-size SDP (Gram of size 2N+2, O(N) constraints) whose value is a rigorous lower bound. The data enter only the objective. Exactness is **certified a posteriori** in each of these cases:
- the SDP returns a rank-3 optimum;
- a genuine local solution passes the stress test Q_λ ⪰ 0 (Thm 2.1/2.4, implemented in stress.py);
- for coplanar data (velocity-only, position-only, or targets in the vertical plane through the lateral target direction), a planar local solution satisfies LICQ (Thm 4.1).

A **uniform a-priori exactness theorem is not proved.** For the unit-d inner discretization with δ>0 it is false.

## 1. Setting

### 1.1 Discrete models (vertical = e_z, gravity absorbed into the target)
Grid h = tf/N. Fixed known thrust-acceleration profile a_k > 0. Weights cv_k = h a_k and cr_k = h a_k (tf − (k+½)h). Unknown unit vectors are b_1..b_{N−1} (b_0 = b_N = e_z) and thrust directions d_0..d_{N−1}. Terminal-state readout: V = Σ cv_k d_k, R = Σ cr_k d_k. Target w = (wv, wr) ∈ ℝ⁶, which already contains r0, v0 and gravity. Cost J = ‖V − wv‖² + ‖R − wr‖².
- **D^unit (inner discretization of [redteam-lift]):** ‖d_k‖ = 1, ⟨d_k,b_k⟩ ≥ cos δ, ⟨d_k,b_{k+1}⟩ ≥ cos δ, ⟨b_k,b_{k+1}⟩ ≥ cos ωh.
- **D^cvx (convexified lens):** the same, but ‖d_k‖ ≤ 1. Prop 6.1 shows that {d: ‖d‖≤1, both gimbal half-spaces} = conv(lens). This is the discrete analogue of relaxed controls. In continuous time with α = 0, relaxed and genuine reachable sets coincide (math/redteam-lift.md R2, Lyapunov–Aumann).
- **D^0 (δ = 0 chain):** d_k = b_k (thrust along the body axis). Unknowns are b_1..b_{N−1} only.

All three are instances of the **abstract vector QCQP (VQ)**:
unknown vectors z_1..z_m in a real inner-product space X ⊇ E := ℝ³ (the constants). The constraints are
(i) ‖z_i‖² = 1, or ≤ 1;
(ii) ⟨z_i,z_j⟩ ≥ c_e for e = {i,j} in an edge set 𝓔;
(iii) ⟨z_i,f⟩ ≥ c_f for fixed f ∈ E (here f = e_z).
The cost is f_w(z) = Σ_{ij} C_ij⟨z_i,z_j⟩ − 2Σ_i⟨z_i,ℓ_i⟩ + κ, where C ⪰ 0 (here C = cv cvᵀ + cr crᵀ on the d-block, rank 2) and ℓ_i ∈ E (here ℓ_{d_k} = cv_k wv + cr_k wr).
The **genuine** problem is X = ℝ³. The **lifted** problem allows X arbitrary.
**Data subspace:** E_w := span({e_z} ∪ {ℓ_i}) = span(e_z, wv, wr). It is 3-dimensional unless the lateral parts of wv and wr are parallel ("coplanar data"; this includes velocity-only, position-only and vertical-only targets).

### 1.2 Lemma 1.1 (Shor = Hilbert sphere; [redteam-lift] §3.2, short proof)
The degree-2 Shor relaxation of (VQ) has the moment matrix G = [[I_3, Mᵀ],[M, Y]] ⪰ 0, with M_i = first moments of z_i and Y = second moments. Every constraint and the cost are linear in G. G is exactly the Gram matrix of (e_1,e_2,e_3,z_1,…,z_m) for vectors in ℝ^{3+m} ⊃ E. Conversely, every such Gram matrix is a feasible G.
*Proof.* G ⪰ 0 with top-left block I_3 factors as G = XXᵀ with the first three rows orthonormal. Rotate them onto e_1,e_2,e_3. Each constraint/cost entry is the corresponding inner product. ∎
So **the SDP value is min f_w over (VQ) in X = ℝ^{3+m}, which equals the infimum over every real Hilbert space.** Exactness means this equals the minimum over X = ℝ³. Slater holds for the well-posed form (b_0, b_N substituted by the constant e_z), so strong duality holds with dual attainment, and compactness gives primal attainment.

## 2. Duality: the stress certificate and a local criterion

Lagrangian, with λ_e ≥ 0 on (ii), λ_f ≥ 0 on (iii), μ_i free on (i) (μ_i ≥ 0 for the "≤ 1" form):
L(z) = f_w(z) − Σ_e λ_e(⟨z_i,z_j⟩ − c_e) − Σ_f λ_f(⟨z_i,f⟩ − c_f) + Σ_i μ_i(‖z_i‖² − 1).
This equals Σ_{ij} Q_ij⟨z_i,z_j⟩ − 2Σ_i⟨z_i, ℓ̃_i⟩ + const, with
**Q_λ := C + diag(μ) − ½Σ_e λ_e(E_ij + E_ji)** (the *stress matrix*) and ℓ̃_i = ℓ_i + ½Σ_f λ_f f ∈ E.
Rigidity analogy: inner-product lower bounds are cables, Q_λ is a Connelly stress matrix, and exactness of the lift corresponds to universal rigidity (realizability in no higher dimension).

**Theorem 2.1 (stress certificate).** Let z* be genuine-feasible (in ℝ³) and λ, μ multipliers satisfying KKT:
- stationarity (Q_λ ⊗ I) z* = ℓ̃, i.e. Σ_j Q_ij z*_j = ℓ̃_i for all i;
- complementary slackness;
- λ ≥ 0.
If Q_λ ⪰ 0, then z* minimizes f_w over (VQ) in **every** inner-product space X ⊇ E. Hence the SDP is exact and z* is a global genuine optimum.
Conversely, suppose the SDP is exact (some optimal G has rank 3). Then every dual-optimal multiplier satisfies KKT at the corresponding genuine z* with Q_λ ⪰ 0.
*Proof.* (⇐) Let z be feasible in X. Then f_w(z) ≥ L(z), since the multiplier terms are ≥ 0 on feasible points and the equality terms vanish. L is a convex quadratic on X^m because Q ⪰ 0, and ∇L(z*) = 0, so L(z) ≥ L(z*). Finally L(z*) = f_w(z*) by complementary slackness.
(⇒) The SDP dual slack is S = [[Ξ, −L̃ᵀ],[−L̃, Q_λ]] ⪰ 0, where L̃ is the m×3 matrix of the ℓ̃_i. Complementary slackness tr(G*S) = 0 with G* = [I;Z][I;Z]ᵀ gives S[I;Z] = 0, i.e. QZ = L̃ (stationarity). S ⪰ 0 gives Q ⪰ 0. ∎

**Corollary 2.2 (strict stress ⇒ unique, flat optimum).** If the dual-optimal Q_λ ≻ 0, then every lifted optimum satisfies z = Q_λ⁻¹ ℓ̃ ∈ E^m. So the SDP optimum is unique, has rank 3, and is exact.
*Proof.* Every primal optimum satisfies (Q⊗I)z = ℓ̃ (as in the proof of Thm 2.1, from tr(GS) = 0). ∎

**Corollary 2.3 (structure of the optimal face).** All lifted optima are z = z⁰ + Σ_r k_r ⊗ h_r, with z⁰ = Q⁺ℓ̃ ∈ E^m, {k_r} a basis of ker Q_λ, and h_r ∈ X. The E⊥ part of any lifted optimum lies in (ker Q_λ) ⊗ E⊥. So rank(G*) ≤ 3 + dim ker Q_λ, and a rank > 3 optimum requires a singular stress. (Example: at θ_M the two mirror-image extreme arcs give a kernel direction, and the max-rank interior-point solution mixes them; this is what [redteam-lift] and [verifier-sdp] observed.)

**Lemma 2.4a (second variation along E⊥).** Let z* ∈ E^m be KKT with multipliers (λ,μ). Take η ∈ ℝ^m and a unit n ⊥ E, and set z_i(t) = cos(tη_i) z*_i + sin(tη_i) n. Then z(t) keeps all unit norms, f_w(z(t)) changes only at order t², and L(z(t)) − L(z*) = t² ηᵀQ_λη + O(t⁴).
*Proof.* Expand: z(t) = z* + tη⊗n − ½t² diag(η²) z* + O(t³). Here ∇L(z*) = 0, n ⊥ E ∋ ℓ̃_i, and the Hessian of L is 2Q⊗I. ∎

**Theorem 2.4 (exactness is a local, second-order property in ℝ⁴; local-to-global).**
SDP exact at w ⇔ some genuine global minimizer is a local minimizer of (VQ) posed in ℝ⁴ = E ⊕ ℝn.
(⇐ needs LICQ at that minimizer.) Moreover, *any* genuine KKT point satisfying LICQ that is a local minimizer in ℝ⁴ is a global minimizer of the lifted problem in every dimension. Local implies global.
*Proof.*
(⇐) Let z* be the minimizer. LICQ in ℝ⁴ at z* (gradients are unchanged) gives unique multipliers and the second-order necessary condition on the critical cone. Every direction η⊗n is critical: it is orthogonal to every constraint gradient, because ⟨z*_i, n⟩ = ⟨f, n⟩ = 0. So ηᵀQη ≥ 0 for all η, i.e. Q ⪰ 0. Apply Thm 2.1.
(⇒) A rank-3 optimal G gives a genuine global minimizer z′. Thm 2.1 (⇒) gives Q ⪰ 0 at z′, hence z′ is a global minimizer in ℝ⁴. ∎
*Use:* a counterexample to exactness at w is exactly a target where **every** genuine optimum has an E⊥ descent direction (ηᵀQη < 0). stress.py computes Q from a numerical solution, which gives a cheap a-posteriori test.

## 3. Folding

**Lemma 3.1 (folding).** Let E ⊆ X be a closed subspace, X ⊇ E ⊕ ℝn with n ⊥ E. Define F(x) := P_E x + ‖P_{E⊥}x‖ n. Then:
- ‖F(x)‖ = ‖x‖;
- F fixes E pointwise;
- ⟨F(x),f⟩ = ⟨x,f⟩ for f ∈ E;
- ⟨F(x),F(y)⟩ ≥ ⟨x,y⟩ for all x, y.
*Proof.* ⟨F x, F y⟩ − ⟨x,y⟩ = ‖P⊥x‖‖P⊥y‖ − ⟨P⊥x, P⊥y⟩ ≥ 0 by Cauchy–Schwarz. ∎
Hence F maps every lifted-feasible configuration of (VQ) to a feasible configuration in E ⊕ ℝn: norms are kept, every cable inner product grows, and the fixed-vector constraints are unchanged.

**Corollary 3.2 (linear objectives).** If C = 0 (cost Σ⟨z_i,ℓ_i⟩ with ℓ_i ∈ E_w), the lifted optimum equals the optimum in E_w ⊕ ℝ, a space of dimension dim E_w + 1.

**Corollary 3.3 (support functions with coplanar data are exact).** For every direction y = (y_v,y_r) whose laterals are parallel (so dim span(e_z,y_v,y_r) ≤ 2), the SDP with linear objective computes the support function h_{Reach}(y) of the genuine reachable set of (V,R) exactly, in D^unit, D^cvx and D^0. For general directions it computes the ℝ⁴ support function. lin.py: N=8, four directions with dim E_w = 3, ℝ³ = ℝ⁴ = SDP to 1e-9. So exactness held there too, though unproved.

**Remark 3.4 (why pointwise maps cannot finish the proof).** A proof of ℝ⁴ → ℝ³ by a pointwise map S³₊ → S² that fixes S² would be a retraction of a closed 3-ball onto its boundary sphere. By Brouwer no continuous such map exists. Any planarization argument must therefore be path-wise or global (PMP/duality). This is why Thm 2.1/2.4 is the right tool. Applied to the quadratic cost, the fold also goes the wrong way: (Σc_k‖P⊥d_k‖)² ≥ ‖Σc_k P⊥d_k‖².

## 4. Planar optima are certified (coplanar data)

**Theorem 4.1 (planar ⇒ certified, local ⇒ global).** Assume coplanar data: E_w ⊆ Π, a 2-plane containing e_z. Let z* be a genuine configuration with all z*_i ∈ Π, and suppose
- z* is a local minimizer of the genuine problem in ℝ³,
- LICQ holds at z*.
Then Q_λ ⪰ 0. Hence z* is the global minimizer of the lifted problem in every dimension, so of the genuine problem too, and the SDP is exact at w.
*Proof.* Let n be the unit normal of Π in ℝ³. Every direction η⊗n is critical (Thm 2.4 proof, with n now a *genuine* direction). The genuine second-order necessary condition gives ηᵀQ_λη ≥ 0 for all η. Apply Thm 2.1. ∎
Only the genuine SONC along n is used. So it suffices that z* is KKT within Π and that Q_λ ⪰ 0 holds along the normal (a direct test).

**Corollary 4.2.** For velocity-only, position-only, and vertical-plane (r,v) targets, the SDP is exact at every target that has a planar genuine optimum satisfying LICQ. A planar local solution found by any local method is then certified globally optimal. Exactness can fail at coplanar data only where every genuine optimum is non-planar (coning) or degenerate. By Cor 2.3, the lifted optimum then has a singular stress, and its E⊥ part lies in ker Q.

**Remark 4.3 (state constraints).** Thm 4.1 holds verbatim with additional constraints of the form q(r_j) ≤ 0, q quadratic and invariant under rotations about e_z. Here r_j = Σκ_{jk}d_k + (constant in E) are node positions. Examples: glide slope ‖r_{j,h}‖² ≤ cot²γ ⟨r_j,e_z⟩² with ⟨r_j,e_z⟩ ≥ 0, and altitude ⟨r_j,e_z⟩ ≥ 0. All of these are Gram-linear, and their gradients are orthogonal to η⊗n at planar configurations. Hard terminal velocity V = wv also fits as a Gram-linear constraint, but LICQ fails there (zero gradient of ‖V−wv‖²). Use the soft form.

## 5. Rank ≤ 4 under rate saturation (discrete PMP)

**Proposition 5.1.** In D^unit (and in D^cvx with ‖d_k‖ = 1 active), let a lifted KKT configuration have multipliers with:
- ν_k > 0 on ⟨b_k,b_{k+1}⟩ ≥ cos ωh for 1 ≤ k ≤ N−2;
- μ^d_k ≠ 0;
- 1 + λ_kλ′_k/(2μ^d_kν_k) ≠ 0.
Here λ, λ′ are the gimbal multipliers. Then all b_k, d_k lie in W := span(e_z, b_1, y_v, y_r), where y_v = V − wv and y_r = R − wr. So dim W ≤ 4, and the optimal Gram has rank ≤ 4.
*Proof.* Stationarity:
- for d_k: 2μ^d_k d_k = λ_k b_k + λ′_k b_{k+1} − 2(cv_k y_v + cr_k y_r);
- for b_k: ν_k b_{k+1} = 2μ^b_k b_k − ν_{k−1}b_{k−1} − λ_k d_k − λ′_{k−1}d_{k−1}.
Substitute the first into the second. Under the stated nondegeneracy this solves for b_{k+1} and d_k in W. Induct from b_0 = e_z and b_1. ∎
The same holds in continuous time for normal extremals with a.e.-unique maximizers. There (b, costate) evolve in span(b, costate, primer), with primer ∈ span(y_v,y_r), so extremals live in span(e_z, λ_b(0), y_v, y_r).
This matches the rank-4 optimum of [numerics] case 12. The extra vector b_1 (or λ_b(0)) is exactly what remains to be controlled. Exactness holds iff it can be chosen in span(e_z, y_v, y_r).

## 6. Where the 4th dimension comes from: gimbal-lens chattering

### 6.1 Proposition 6.1 (lifted lens = convex hull of the lens)
Let b, b′ ∈ E and Λ_H := {d ∈ S(X): ⟨d,b⟩ ≥ cos δ, ⟨d,b′⟩ ≥ cos δ} with dim X > 3. Then
P_E(Λ_H) = K := {x ∈ E: ‖x‖ ≤ 1, ⟨x,b⟩ ≥ cos δ, ⟨x,b′⟩ ≥ cos δ} = conv(lens), where lens = K ∩ S².
*Proof.* (⊆) ⟨P_E d, b⟩ = ⟨d,b⟩ and ‖P_E d‖ ≤ 1. (⊇) d = x + √(1−‖x‖²) n. K is compact and convex. Its extreme points lie on the sphere. Indeed, the polyhedron P = {⟨x,b⟩ ≥ cos δ, ⟨x,b′⟩ ≥ cos δ} has no vertices (two half-spaces in ℝ³), so every face of P has dimension ≥ 1. A point x ∈ K with ‖x‖ < 1 is in the relative interior of a face of P, hence the midpoint of a short segment in that face that stays inside the open ball, so x is not extreme. Krein–Milman gives K = conv(ext K) ⊆ conv(lens) ⊆ K. ∎

**Consequence.** With b held in E (no rate cost at all), each d_k in the lift may take *any* E-projection in conv(lens_k), i.e. any thrust magnitude down to cos δ_eff. The only price is the E⊥ moments ‖Σcv_k P⊥d_k‖² + ‖Σcr_k P⊥d_k‖². These vanish once the E⊥ parts are arranged to cancel: one extra dimension and N ≥ 3 suffice, with a sign pattern in the kernel of the 2×N weight matrix.
So the unit-d SDP contains a penalty-free copy of a large part of the **convexified** model D^cvx. The genuine D^unit has no chattering: each segment is one unit vector.
- In continuous time, chattering of d inside cap(b,δ) gives exactly conv(cap) (Lyapunov), so the gap disappears in the limit and this "room" corresponds to nothing physical.
- **With δ = 0 the lens degenerates to a point.** Any E⊥ tilt of the thrust is a tilt of b and pays the rate constraint on both sides, so the mechanism is absent. This is consistent with [verifier-sdp]'s 840 gap-free δ=0 instances.

### 6.2 Case 12 decoded (case12.py, convex_d.py, chk12.py, case12_cvx.py)
[numerics] case 12: N=16, tf=4, ω=30°/s, δ=15°, a=11; wv = (32.1819; 5.0939, 21.9914), wr = (64.9080; 8.2825, 44.1701) (vertical first). The two laterals are 2.4° apart.
- SDP_unit = 0.0275324. Eigenvalues 27.72, 4.725, 1.475, 0.0781, then 0, so rank 4.
- The 4th coordinates (E⊥) of the factor: b_k ≤ 0.04, but d_14 = −0.246 ≈ −sin 14.2° and d_13 = +0.103. The bulk of the middle d's sit at +0.03…0.05. E⊥ moments: Σcv d⁴ = 6e-8 and Σcr d⁴ = −1.3e-5, so they cancel.
- An ℝ⁴ polish from the factor gives 0.0275285 (feasible to 1e-8), consistent with [verifier-sdp]'s explicit ℝ⁴ chain.
- Best unit-d 3D: 0.0282320 (16 starts plus the projected SDP). This matches [numerics] 0.0282306.
- **Convexified genuine 3D: 0.02736764, with |d_14| = 0.9703 and all other |d_k| = 1.** The optimum wants to throttle down segment 14 by 3%.
- **SDP_cvx at Clarabel tol 1e-12: 0.02736764 (rank 3).** The objective evaluated at the NLP Gram is 0.027367637. Exact.
So genuine_cvx = SDP_cvx (0.0273676) < SDP_unit (0.0275324) < genuine_unit (0.0282320). The unit-d "gap" is the discrete chattering deficit of the unit-d inner discretization. The lift recovers 70% of it, and the convexified lift recovers all of it. **Attitude planarization is not what fails at case 12.**

### 6.3 Conjecture CSD2′ (refined)
(a) Continuous time, fixed thrust profile, α arbitrary (known a(t)): the Hilbert-sphere relaxation (b an AL_ω path in S(X), u ∈ conv cap(b,δ)) has the same min-landing-error value as the genuine 5DOF problem.
(b) Discrete: the Shor relaxation of D^cvx (G_dd ≤ 1) is exact. The same for D^0 (δ = 0).
Evidence: case 12 (exact after convexification); [verifier-sdp] δ=0, 840 adversarial instances; scan_cvx (§9); [redteam-lift] scans. By Thm 2.4, CSD2′ is equivalent to: *genuine optima of D^cvx / D^0 admit no E⊥ second-order descent* (ηᵀQ_λη ≥ 0).

### 6.4 Recipe for a rigorous small-N counterexample to the unit-d statement (sent to [verifier-sdp])
N = 3 (unknowns b_1, b_2, d_0, d_1, d_2). The 2×3 weight matrix [cv; cr] has kernel α ∝ (1,−2,1) for constant a. Choose non-coplanar unit x̂_k ∈ ℝ³ inside the lenses of some genuine b's with slack. Set μ_k = √(1 − t²α_k²) and target w = (Σcv_k μ_k x̂_k, Σcr_k μ_k x̂_k).
- The lift attains cost 0 with d_k = μ_k x̂_k + tα_k e_4: the E⊥ moments vanish and the b's are unchanged.
- In the genuine model, the solutions of Λ(d) = w form d = d^p + α⊗u, u ∈ ℝ³. Unit norms impose three quadratic equations, whose lifted solution set is an interval in s = ‖u‖². The genuine solutions are its two endpoints only. Choose x̂, t so the gimbal/rate constraints exclude both endpoints.
- Then the genuine minimum is > 0 = SDP, certifiable by order-2 Lasserre (15 variables) or by interval arithmetic on the 1-parameter family.
This would make the unit-d BREAK rigorous. It does **not** bear on CSD2′.

## 7. Variable throttle, min-fuel

### 7.1 The natural lift is lossy ([verifier-sdp] NUMERICS, DM 2026-11-07)
Variables z_k = (a_k, U_k), ‖U_k‖² = a_k², a_k ∈ [a1,a2] with RLT, rate U_k·U_{k+1} ≥ cos(ωh) a_k a_{k+1}, b_0 = b_N = e_z substituted. N=6, ωtf=2, a∈[0.5,1], (r,v) target: SDP 0.28471 (Clarabel and SCS, rank 5) vs genuine 0.47529 (300 starts agree). The same lift is rank 1 and exact when ωtf = 6 or ω = ∞, i.e. when the rate does not bind.
**Mechanism (exact algebra).** Replace U_k by (a_k/cos ε_k)(cos ε_k û_k + sin ε_k n), n ⊥ E. This is allowed while a_k/cos ε_k ≤ a2, i.e. with throttle headroom. The E-part of every U_k is unchanged, so the E-readout and E-cost are unchanged. The normalized rate constraint becomes cos ε_k cos ε_{k+1}⟨û_k,û_{k+1}⟩ + sin ε_k sin ε_{k+1} ≥ cos ωh, so the E-direction may turn by more than ωh per step whenever ε_k ε_{k+1} > 0. The only costs are the E⊥ moments (Σ c_k a_k tan ε_k)², which cancel with sign patterns or a second extra dimension.
With fixed thrust the compensation a_k/cos ε_k is impossible: the E-part shrinks, i.e. a forced throttle-down. With a separate axis b and δ>0 the tilt of b costs gimbal (cos ε ⟨d,b̂⟩ ≥ cos δ). Either way, the rate gain then competes with first-order-in-ε² losses, and in every test so far the losses won.
**So "convex lift of variable-throttle 5DOF by the natural degree-2 moments" is lossy whenever the rate limit binds.**
**Certified ([verifier-sdp], DM 00:40):** order-2 Lasserre, which is a valid lower bound on the genuine problem, separates the two values at N=3. Shor gives 0.5759, while Las2 = NLP = 0.6047. So Shor < genuine optimum rigorously, up to solver accuracy.

**[verifier-sdp] summary for the fixed-thrust lifts (DM 00:40):**
- δ=0: about 2,900 targets with no gap (N=2..32, |gap| ≤ 1e-7·scale²).
- unit-d with δ>0: gaps are frequent at small N and small ωtf (20–40% of targets at N=3/4, δ=15°, ωtf=1, up to 50% relative; up to 95% at δ=40°), and rare at ωtf ≥ 2.09.
- The coplanar variant of case 12 was reproduced: gap 1.7%, non-planar 3D optimum.
- Lasserre-2 on the unit-d gaps and convexified-lens checks on all gap instances are in progress.
This pattern fits Prop 6.1. The lens chattering room scales with δ and matters most when the rate cannot substitute for it.

**[verifier-sdp] follow-up (DM, after 00:40):**
- **Convexified lens on all 509 unit-d gap instances:** zero gaps. Max (genuine_cvx − SDP_cvx) = 4.5e-10·scale², including N=4, δ=40°, ωtf=1, where the unit-d values are 0.033 vs 0.725.
- **Case 12 convexified:** SDP 0.0273674 (rank 3) vs NLP 0.0273682. Independent agreement with §6.2.
- **CSD2′ screen at N=3..8** (δ=0; convexified with δ=15° and 40°; near-dent, non-coplanar and rate-saturated targets): 0 gaps. N=16–32 is running.
- **Unit-d break, Lasserre-2 at N=3** (δ=15°, ωtf=1): Shor 0.070544 < Las2 0.08734 (Clarabel optimal_inaccurate; about 1% above the multistart 0.08646, so solver accuracy is about 1%) ≈ genuine. The 24% separation far exceeds that inaccuracy, so the unit-d failure of CSD2 is **certified up to solver accuracy**. An SCS cross-check and a δ=40° instance are pending.
So every known gap disappears under convexification. CSD2′ is unbroken on about 2,900 δ=0 and more than 509 convexified instances.

### 7.2 Conjecture CSD3 (separate-axis LCvx lift, untested)
Keep the body axis b_k as unit vectors with the rate on b (no throttle compensation possible). Put the thrust u_k in the classical LCvx set relative to b_k: ⟨u_k,b_k⟩ ≥ Γ_k cos δ, ‖u_k‖ ≤ Γ_k, a1 ≤ Γ_k ≤ a2. Lift Γ_k as a scalar moment, with ‖u_k‖² ≤ S_k, S_k ≥ Γ_k² and RLT S_k ≤ (a1+a2)Γ_k − a1a2. At fixed b this is the lossless C-W relaxation (math/04). The mechanism of §7.1 is blocked because the rate acts on unit b's. Whether the joint lift is exact is open. Requested from [verifier-sdp].

### 7.3 Min-fuel
With fixed thrust, fuel = ∫a is constant, so min-fuel is meaningless. Min-fuel requires throttle (§7.1/7.2), and the natural lift is lossy. **Nothing here gives a tractable exact min-fuel 5DOF formulation.**

## 8. Positioning

- **Theorem D (math/02 §11).** The lifted cost is f_w = E‖(V,R) − w‖², i.e. tr(second moment) − 2⟨w, mean⟩ + ‖w‖². This is a function of the lifted second moment, not of the mean readout. It is precisely the case excluded in §11.1 (i) (the [adversary] R ⪰ rrᵀ lift). Theorem D does not apply, and no contradiction arises. With a state-linear relaxation (cost on the mean only), the "uniform Shor" value is 0 at θ_M. With the second-moment cost it is 53.6 > 0 ([redteam-lift] S1).
- **Theorem A.** The lifted feasible set is θ-independent and θ enters only the objective. No claim about convexity of F is made, and the relaxation is not uniform in A's sense.
- **Prop 11.3 (TRIV).** Unlike the trivial convex-hull reformulation, this is a fixed, explicit, polynomial-size SDP (n = 2N+2 for D^unit). Its value is always a valid lower bound and certifies infeasibility of exact landing when > 0. Exactness is certified a posteriori by Thm 2.1/2.4/4.1. It is therefore a genuine *tractable certificate*, but **not** (yet) a theorem-backed tractable *exact* formulation, except under the hypotheses of Thm 4.1 / Cor 3.3, or a posteriori.
- **What it does not give:**
  - variable throttle (natural lift lossy);
  - min-fuel;
  - hard terminal velocity (fits, but LICQ fails; use a soft weight);
  - a priori exactness (open = CSD2′);
  - exactness for the unit-d discretization with δ > 0 (false numerically).

## 9. Numerics (mine; Clarabel tol 1e-11 unless noted; NLP = SLSQP multistart, feasibility 1e-8)
- dimtest/run1: D^unit, N=2,3, 12 far (r,v) targets with dim E_w = 3. SDP = NLP3 = NLP4 = NLP5 to 1e-8.
- run2: shortened vertical targets (μ·full thrust), N=3..5, ω ∈ {2,30}°/s. All exact (mostly reachable, cost 0).
- lin.py: linear objectives (far targets), N=8, dim E_w = 3. SDP = NLP3 = NLP4 to 1e-9 (Cor 3.3 covers only dim E_w = 2).
- case12 / convex_d / chk12: §6.2.
- **scan_cvx (scan_cvx.txt): [numerics]' c1 cases with N ≤ 24 (0–17, 21).**
  - On every case where the convexified NLP converged (15 of 18), SDP_cvx = genuine_cvx to ≤ 2e-8 relative, or both are ≈ 0 (cases 14, 17, reachable). Cases 1, 3, 11: my NLP found no feasible point from the SDP warm start. There SDP_unit = SDP_cvx, at large costs.
  - The convexified optimum uses |d_k| < 1 exactly at the cases where SDP_unit ≠ SDP_cvx: case 12 (0.9703), case 13 (0.9883; this is [numerics]' "missed optimum" case, where SDP_unit 2.32447 > SDP_cvx 2.32318 = genuine_cvx), and cases 14, 17 (reachable).
  - Clarabel reports "optimal_inaccurate" at tol 1e-11. The values agree with the NLP to the digits shown.
- **Coplanar variant of case 12** (wr's lateral rotated onto wv's lateral, so dim E_w = 2):
  - unit-d: SDP 0.0420587 vs NLP3 0.0427975 (gap 1.7%). The 3D optimum is NON-planar (out-of-plane 0.20), consistent with Thm 4.1 / Cor 4.2.
  - convexified: SDP_cvx 0.04187844 = genuine_cvx 0.04187844. The genuine optimum is non-planar (0.21) and the SDP optimum has rank 4 (ev4/ev1 = 1.4e-2). This is the mirror-pair mixture of Cor 2.3, and its value is exact.
- **Stress test (stress.py, stress_demo.py):** at the unit-d 3D optimum of case 12 (stationarity residual 1.3e-6, 33 active constraints), the lowest eigenvalue of Q_λ is −0.0065 < 0. So that genuine optimum has an E⊥ descent direction, as Thm 2.4 predicts for a lossy instance. The same holds at the coplanar variant (−0.0052).
- **delta0_axis (δ=0 chain, N=16, tf=8, ω=30°/s, axis (r,v) targets at 50/70/85% of full vertical thrust; these force two-moment lateral cancellation):** SDP = NLP3 = NLP4 to ≤ 5e-7. The SDP optima have rank > 3 (rotational symmetry mixtures, Cor 2.3), but their values are exact.
