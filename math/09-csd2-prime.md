# 09. Conjecture CSD2′: exactness of the Hilbert-sphere (Shor) lift for the convexified-lens fixed-thrust problem

Author: [proof-csd2p]. Started 2026-11-07 01:00 (system clock). Status: CLAIMED (proofs below). Attacks welcome.
Inputs: math/08 (Thm 2.1, Thm 2.4, Thm 4.1, Prop 5.1, Prop 6.1, Rem 3.4), math/redteam-lift.md §3.2, math/04 (C-W, C-S).
Scripts: numerics/proof-csd2p/ (picone.py, index_check.py, index_c1.py, mu_unit.py, screen_big.py, summarize_idx.py).

## 0. Verdict

**CSD2′ is not fully proved and not broken.** I found no counterexample. The conjecture is now reduced to one integer equality on a thin residual class of genuine optima. The rest is proved.

| Statement | Status |
|---|---|
| **T1 Alignment lemma.** The lifted infimum is attained by lifted trajectories whose (r,v) readout lies in E = ℝ³. Hence CSD2′ for every target ⇔ R_X ∩ E² = R_3: every lifted trajectory that lands in ℝ³ can be replaced by a 3D one with the same terminal state. This is the (r,v) version of "Π_n = Π_3". | PROVED (§2.1) |
| **T2 Primer-plane fold.** The lift is exact for **every linear objective**, in every model (continuous time, D^unit, D^cvx, D^0). This closes the "general linear, unproved" item of math/08 Cor 3.3 / SDP-F. | PROVED (§2.2) |
| **T3 Continuous-time stress certificate.** Weak duality on the Hilbert sphere: a genuine KKT point with PSD scalar stress Q is a global minimizer in every dimension. Explicit second variation J_red[η] = ∫ν(η̇² − ‖ḃ‖²η²) + ∫κη², with *gimbal curvature* κ = ‖P‖ sin(θ−δ)⁺ cot θ. | PROVED (§3), given KKT multipliers (normal PMP) |
| **T4 Hemisphere (Picone) theorem.** Suppose a genuine optimum b* and its primer P satisfy: ∃c ∈ E with ⟨b*(t),c⟩ > 0 on (0,tf), ⟨P(t),c⟩ ≥ 0, ⟨e_z,c⟩ ≥ 0. Then the lift is exact at w, and b* is globally optimal in every dimension. Special cases: (a) the attitude never crosses the primer plane; (b) **a priori class**: a target whose vertical demand exceeds full upright thrust, with ωtf < π. The discrete version (D^cvx, D^0) is fully rigorous **and needs μ_d ≥ 0, which is exactly the convexified lens**. | PROVED (§4) |
| **T5 Index theorem.** At any genuine KKT point: **neg(Q) = neg(Z) − p₀(C_yw)**. Z is the cable part of the stress. C_yw = Σ_c y_{c,h} w_{c,h}ᵀ is the 2×2 lateral residual/target cross-covariance, and p₀ is its number of eigenvalues ≥ 0. Moreover **k−1 ≤ neg(Z) ≤ k**, where k is the number of times b* crosses the primer plane (the Jacobi field h_m = ⟨b*,m⟩). Hence: k ≤ p₀ ⇒ exact (certified); k ≥ p₀+2 ⇒ the genuine point is beaten in ℝ⁴; k = p₀+1 ⇒ decided by one Sturm count. | PROVED in discrete time (finite-dim, under stated nondegeneracy); continuous-time analogue with proof sketch (§5) |
| **P6 No free singular arcs.** A genuine local optimum has no interval with P ∥ −b, throttled u and slack rate: the 3D tilt into the primer-plane normal improves it. So the Prop 6.1 mechanism has no continuous-time analogue at genuine optima. | PROVED (§6.1) |
| **P7 Why unit-d fails and the convexified lens works.** At a genuine D^unit optimum the norm multiplier μ_d on ‖d_k‖=1 can be negative ("the segment wants to throttle"). The lift realizes the throttle by an E⊥ tilt (math/08 Prop 6.1). In D^cvx and in continuous time μ ≥ 0 by the KKT sign. Every T4/T5 argument uses μ ≥ 0. | PROVED (mechanism) + NUMERICS (all 13 checked unit-d gap instances have μ_d < 0 and Q ≱ 0; their convexified versions have μ_d ≥ 0 and Q ⪰ 0) |
| **Numerics (mine)** | **0 gaps** at large ωtf ∈ {π, 1.5π, 2π, 3π} (N=24; d=b, cvx15, cvx40; terminal and free b(tf); 384 targets, including dent mixtures of support points). The index identity holds on all 151 nondegenerate instances. The Sturm bounds hold on all 107 where h_m ≠ 0 at every node, of which 85% are certified by T5 and the other 15% are in the residual class, all exact (§8). T5 certifies 16 of 17 [numerics] c1 cases (9 of 10 GTPL-realistic set A), including case 12 convexified. The one exception (set A case 6: k=2, p₀=1) is exact numerically. |
| **Open core = Conjecture CSD2″** | At a genuine global optimum with k = p₀ + 1 crossings (terminal attitude: k = 2 and C_yw indefinite), neg(Z) = k − 1. Equivalently, the principal Jacobi solution has no conjugate point in the last lobe. **CSD2′ ⇔ CSD2″** on nondegenerate instances. |

**Physical reading.** The lift is exact whenever the optimal attitude crosses the primer plane no more often than the number of nonnegative eigenvalues of C_yw. C_yw ≺ 0 means the trajectory falls short of the target in every lateral direction (the classical "under-reach" regime); then the attitude must not cross the primer plane at all. Overshoot in some lateral direction (C_yw with nonnegative eigenvalues) allows one or two crossings. The GTPL-realistic optima are almost all two-crossing with C_yw ≻ 0, so they are certified by T5.

**What "exact" yields physically (§7).** The certified 3D trajectory has a genuine rate-limited attitude b(t). Its thrust direction u(t) ∈ conv cap(b(t),δ) is relaxed. By Aumann/Lyapunov (C-W), a bang-bang selection u(t) ∈ cap(b(t),δ) with the **same b** gives the **same terminal (r,v)**, exactly and not just approximately. By Filippov–Ważewski the whole state history is approximated uniformly. Only a gimbal-rate limit, which is not in the model, would make this approximate.

## 1. Setting

- Real Hilbert space X ⊇ E := ℝ³ ∋ e_z. The genuine problem is X = E; the lift is X arbitrary (dim X = 4 already suffices for normal extremals, math/08 §5).
- Known thrust-acceleration profile a ∈ L^∞(0,tf), a ≥ a_min > 0 (a known mass profile is allowed). Kernel k(t) := (a(t), a(t)(tf−t)) ∈ ℝ².
- Admissible pairs (b,u):
  - b : [0,tf] → S(X) is Lipschitz with ‖ḃ‖ ≤ ω a.e.;
  - b(0) = e_z, and b(tf) = e_z (case T) or b(tf) free (case F);
  - u is measurable with u(t) ∈ K(b(t)) := {x : ‖x‖ ≤ 1, ⟨x,b⟩ ≥ cos δ}, 0 ≤ δ < π/2. For δ = 0, K(b) = {b}.
- Readout Y(u) := ∫k⊗u dt = (V,R) ∈ X². Cost J_w := ‖Y − w‖², with w ∈ E² (r0, v0 and gravity absorbed).
- Values: V_X(w) := inf over X-admissible pairs, and V_3 := V_E.
- **CSD2′(a): V_X = V_3 for all X.** By math/08 Lemma 1.1, V_X is the value of the degree-2 moment (Shor) relaxation (continuous-time version; for discrete models it is literally the SDP).

Notation at a genuine pair z* = (b,u) ⊂ E:
- residual y := Y − w ∈ E²;
- **primer** P(t) := −k(t)·y = −a(t)(y_v + (tf−t)y_r), which lies in the **primer plane** Π := span(y_v,y_r);
- m := a unit normal of Π in E with ⟨e_z,m⟩ ≥ 0;
- lateral plane E_h := E ∩ e_z^⊥; for x ∈ E and c ∈ {v,r}, write w_x := (⟨w_v,x⟩, ⟨w_r,x⟩) ∈ ℝ², and similarly y_x and Y_x;
- **C_yw** := y_{v,h} w_{v,h}ᵀ + y_{r,h} w_{r,h}ᵀ (2×2 on E_h).

**(H) KKT form of the normal PMP.** There exist multipliers ν ≥ 0, μ_b, λ ≥ 0, μ_u ≥ 0 such that:
- regularity: ν ∈ L^∞, νḃ ∈ W^{1,1}, μ_b, λ, μ_u ∈ L^∞;
- (S_u) μ_u u − (λ/2) b = P a.e. (absent for δ = 0);
- (S_b) (νḃ)˙ = μ_b b − (λ/2) u a.e. (for δ = 0: (νḃ)˙ = μ_b b − P);
- complementary slackness: ν(‖ḃ‖²−ω²) = λ(⟨u,b⟩ − cos δ) = μ_u(‖u‖²−1) = 0 a.e.;
- in case F: (νḃ)(tf) = 0.

*Derivation.* In the normal PMP with attitude costate p_b, put ν := ‖Π_b p_b‖/(2ω) on the saturated set and νḃ = ½Π_b p_b. Then (S_b) is the adjoint equation. (S_u) is pointwise KKT for max_{u∈K(b)}⟨P,u⟩ (Slater holds for δ > 0) with a measurable selection. Transversality gives (νḃ)(tf) = 0 in case F.
In the discrete models D^cvx and D^0, (H) is ordinary KKT. It holds at local minima under LICQ, and math/08 stress.py and numerics/proof-csd2p/picone.py recover the multipliers with residual ~1e-13.

## 2. Two reductions

### 2.1 Theorem T1 (alignment)
For every X and every X-admissible (b,u) there is an X-admissible (b′,u′) with Y(u′) ∈ E² and J_w(u′) ≤ J_w(u). Hence V_X(w) = inf{J_w : Y ∈ E²}. Moreover, **CSD2′ for all w ⇔ R_X ∩ E² = R_3**, where R_X := {Y(u)} is the lifted reachable set (compact).

*Proof.*
1. Let O be the group of orthogonal maps of X fixing e_z. Admissibility is O-invariant: the constraints involve only norms, inner products, and e_z. Also ‖UY − w‖² = ‖Y‖² + ‖w‖² − 2(vertical terms) − 2(⟨UV_h, w_{v,h}⟩ + ⟨UR_h, w_{r,h}⟩).
2. Let Γ be the Gram matrix of (V_h, R_h). The pairs (P_{E_h}UV_h, P_{E_h}UR_h) range inside the convex set K_Γ := {X ∈ E_h² : XᵀX ⪯ Γ}. The lateral term is linear on K_Γ, so its maximum is attained at an extreme point.
3. The extreme points of K_Γ satisfy XᵀX = Γ (contractions; ℓ² dimension 2). So the maximizer is the image of (V_h,R_h) under an isometry of span(V_h,R_h) into E_h. Extend it to some U ∈ O.
4. Then UY ∈ E² and J_w(Uu) ≤ J_w(u).
5. For the equivalence: V_X = V_3 for all w ⇔ dist(·, R_X∩E²) = dist(·, R_3) on E² ⇔ the two compact sets coincide (R_3 ⊆ R_X ∩ E² always). ∎

So exactness is a pure **dimension-invariance statement for the terminal state**: any (r,v) reachable through a 4th dimension must be reachable in ℝ³.

### 2.2 Theorem T2 (primer-plane fold: all linear objectives are exact)
Let y ∈ E², Π = span(y_v,y_r), and m ⊥ Π in E with ⟨e_z,m⟩ ≥ 0. Define F(x) := P_Π x + ‖P_{Π^⊥} x‖ m, where Π^⊥ is taken in X. Then:
- ‖Fx‖ = ‖x‖;
- ⟨Fx,Fx′⟩ ≥ ⟨x,x′⟩ (Cauchy–Schwarz on the Π^⊥ parts);
- ⟨Fx,p⟩ = ⟨x,p⟩ for p ∈ Π;
- **F(e_z) = e_z**, because P_{Π^⊥}e_z = ⟨e_z,m⟩m with ⟨e_z,m⟩ ≥ 0.

Apply F pointwise to b and u:
- norms are kept;
- every lower inner-product bound (rate chord ⟨b(t),b(s)⟩, gimbal, ⟨·,e_z⟩) still holds;
- ‖F b(t) − F b(s)‖ ≤ ‖b(t)−b(s)‖, so the rate limit holds;
- the boundary values are fixed;
- ⟨y, Y⟩ = ∫⟨P,u⟩ is unchanged.

The image lies in Π ⊕ ℝm ⊆ E. Hence **sup_X ⟨y,Y⟩ = sup_E ⟨y,Y⟩** for every y, in continuous time and in all discretizations (the discrete objective is Σ⟨P_k,d_k⟩ with P_k ∈ Π). ∎

*Remarks.*
- math/08 folded onto E_w ⊕ ℝ (dimension 4). The point here is to fold onto the **primer plane** plus the one direction that contains e_z's out-of-plane part.
- This does not finish the quadratic case. At a lifted optimum the fold enlarges the m-moments of the readout, ∫k‖P_{Π^⊥}u‖ ≥ |∫k u_m|, so it costs (Ỹ_m − w_m)². This is Remark 3.4 (Brouwer) in disguise.

## 3. Continuous-time stress (Theorem T3)

**Lagrangian.**
L(b,u) := J_w + ∫ν(‖ḃ‖²−ω²) − ∫λ(⟨u,b⟩−cos δ) + ∫μ_u(‖u‖²−1) + ∫μ_b(‖b‖²−1).
- On X-admissible pairs, L ≤ J_w.
- L = 𝒬(b,u) − 2⟨w,Y⟩ + const, with 𝒬 = Q⊗I_X and the **scalar stress**
  **Q[η,ζ] = |∫kζ|² + ∫νη̇² + ∫(μ_b η² − λ ηζ + μ_u ζ²)**
  on ℋ := {(η,ζ) ∈ H¹×L² : η(0)=0, and η(tf)=0 in case T}.

**Proposition 3.1.** Under (H), z* is a stationary point of L on {b(0)=e_z (, b(tf)=e_z)} in every X:
- E-directions: by (S_u), (S_b), and integration by parts (the boundary term vanishes by the boundary conditions or by (νḃ)(tf)=0);
- E⊥-directions: z* and w lie in E.

If Q ⪰ 0 on ℋ, then L is convex and J_w(z) ≥ L(z) ≥ L(z*) = J_w(z*) for all X-admissible z. So **z* is a global minimizer in every dimension and CSD2′ holds at w.** ∎

**Geometry of Q.** Dot (S_b) with b to get μ_b = (λ/2)⟨u,b⟩ − ν‖ḃ‖². Where μ_u > 0, complete the square in ζ:
Q[η,ζ] = |∫kζ|² + J_red[η] + ∫μ_u(ζ − λη/(2μ_u))², with J_red[η] := ∫νη̇² + qη² and q := μ_b − λ²/(4μ_u).
At a gimbal-active unit-thrust point, let θ := ∠(b,P) > δ. In the plane span(b,P), (S_u) gives:
- λ = 2‖P‖ sin(θ−δ)/sin δ;
- μ_u = ‖P‖ sin θ / sin δ;
- **q = κ − ν‖ḃ‖², with κ := ‖P‖ sin(θ−δ) cot θ.**
Where θ ≤ δ, λ = 0 and κ = 0. For δ = 0, κ = ⟨P,b⟩.

Interpretation:
- κ is the second derivative of the Hamiltonian σ(b,P) = ‖P‖cos(θ−δ)⁺ under an out-of-plane rotation of b, the **gimbal curvature**. It is ≥ 0 iff θ ≤ π/2.
- −ν‖ḃ‖² is the sphere's Jacobi (curvature) term.

So J_red[η] = ∫ν(η̇² − ‖ḃ‖²η²) + ∫κη² is the Jacobi form of rate-limited motion on a sphere with a primer-dependent potential.
**Exactness fails exactly when E⊥ tilting is cheaper than any genuine variation.** That can happen through long saturated arcs (Wirtinger: ωT > π) or anti-aligned primers (θ > π/2, κ < 0).

## 4. Theorem T4 (hemisphere / Picone certificate)

**Theorem 4.1.** Let z* = (b,u) be genuine, satisfying (H). Suppose there is c ∈ E with
- (i) h(t) := ⟨b(t),c⟩ > 0 for t ∈ (0,tf) (case F: for t ∈ (0,tf]),
- (ii) ⟨P(t),c⟩ ≥ 0 a.e.,
- (iii) ⟨e_z,c⟩ ≥ 0 (automatic in continuous time; it is used only for the discrete boundary terms).

Then Q ⪰ 0. So z* is a global minimizer of J_w over admissible pairs in every Hilbert space: the lift is exact at w, and z* is a genuine global optimum.

*Proof.*
1. Dot (S_u) and (S_b) with c. With h_u := ⟨u,c⟩:
   μ_u h_u − (λ/2)h = ⟨P,c⟩ and −(νḣ)˙ + μ_b h − (λ/2)h_u = 0.
2. Where μ_u = 0, (S_u) gives λb = −2P. Then ⟨P,c⟩ = −(λ/2)h, and (i)+(ii) force λ = 0 (and P = 0). So with the convention λ²/μ_u := 0 there:
   **J_red h = −(νḣ)˙ + qh = (λ/(2μ_u))⟨P,c⟩ ≥ 0** on (0,tf).
3. Picone identity for η ∈ C_c^∞(0,tf) (case F: smooth, vanishing near 0):
   ∫νη̇² + qη² = ∫ν(η̇ − ηḣ/h)² + ∫(J_red h/h)η² ≥ 0.
   Integrate ∫(−(νḣ)˙)η²/h by parts. In case F the boundary term [νḣη²/h](tf) vanishes because (νḃ)(tf) = 0.
4. Then Q[η,ζ] ≥ |∫kζ|² + J_red[η] + ∫μ_u(ζ−λη/2μ_u)² ≥ 0 on a dense subspace of ℋ. Q is continuous on ℋ, so Q ⪰ 0 on ℋ. Apply Prop 3.1. ∎

**Corollary 4.2 (geometric forms).**
- (a) **No primer-plane crossing:** take c = m (⟨P,m⟩ ≡ 0). If ⟨b*(t),m⟩ > 0 on (0,tf), the lift is exact.
- (b) **Common hemisphere:** if all b*(t) and all P(t) lie in one open hemisphere (pole c with ⟨e_z,c⟩ ≥ 0), the lift is exact.
- In general the test is an LP in c ∈ ℝ³ (picone.py: `criterion`).

**Corollary 4.3 (a-priori class: vertical shortfall).**
Case T with ωtf < π (case F with ωtf < π/2): then b_z > 0 on [0,tf] for every admissible path. Suppose the target satisfies
- w_{v,z} ≥ ∫a, and
- w_{v,z} + tf w_{r,z} ≥ ∫a(t)(1 + tf(tf−t))dt (the vertical demand exceeds full upright thrust in both moments).
Then every genuine normal KKT optimum satisfies (ii) with c = e_z: P_z = −a(y_{v,z} + (tf−t)y_{r,z}) is affine in t up to the factor a, and it is ≥ 0 at both ends. So **the lift is exact for these targets**: "cannot brake in time" data, the classical min-landing-error use case.

**Theorem 4.4 (discrete version: rigorous, D^cvx and D^0).**
Let z* be a genuine KKT point of D^cvx (or D^0) with multipliers λ ≥ 0 (cables, gimbal, and the fixed-vector constraints λ_f) and μ_d ≥ 0. Suppose ∃c with
- ⟨b_k,c⟩ > 0 (1 ≤ k ≤ N−1),
- ⟨e_z,c⟩ ≥ 0,
- ⟨P_k,c⟩ ≥ 0, where P_k := −(cv_k y_v + cr_k y_r).
Then Q ⪰ 0, and the SDP is exact at w (math/08 Thm 2.1).

*Proof.*
1. Write Q = Z + ΓΓᵀ, with Γ = [cv cr] on the thrust slots and Z = diag(μ) − ½Σ_e λ_e(E_ij+E_ji) a **Z-matrix**.
2. Stationarity Qz* = ℓ̃ dotted with c gives:
   - (Zh_c)_{d_k} = ⟨P_k,c⟩ + ½Σλ_f⟨e_z,c⟩ ≥ 0;
   - (Zh_c)_{b_k} = ½Σλ_f⟨e_z,c⟩ ≥ 0.
3. Eliminate the d-slots: D = diag(μ_d) ≥ 0. A slot with μ_d = 0 has λ_k = λ′_k = 0 by step 2 and positivity of h_b, so its row is zero. The Schur complement S = Z_bb − Z_bd D⁺ Z_db is again a Z-matrix.
4. S h_b = (Zh)_b − Z_bd D⁺ (Zh)_d ≥ 0 with h_b > 0.
5. A symmetric Z-matrix with a positive supersolution is PSD, by
   xᵀSx = Σ(Sh)_i x_i²/h_i + ½Σ_{i≠j}(−S_ij)h_ih_j(x_i/h_i − x_j/h_j)².
6. So Z ⪰ 0, hence Q ⪰ 0. ∎

**The convexified lens is used exactly once: μ_d ≥ 0.** In D^unit, μ_d is a free multiplier of an equality constraint, and the Schur step fails. This is the stress-level form of math/08 Prop 6.1 (§6.2).

## 5. Theorem T5 (index identity, crossings, and the open core)

**Jacobi field of the primer-plane normal.** For c = m, ⟨P,m⟩ ≡ 0, so **J_red h_m = 0**: h_m := ⟨b,m⟩ is an exact Jacobi field. It is the infinitesimal rotation in the (m,n) plane, a symmetry of the lifted extremal flow because P ⊥ m, n. It fails the Dirichlet condition: h_m(0) = h_m(tf) = ⟨e_z,m⟩ =: ζ₀ ≥ 0.
**Lateral fields.** For x ∈ E_h, h_x := ⟨b,x⟩ ∈ ℋ and J_red h_x = −g·y_x, where g := (λ/2μ_u)k. Discretely: Z h_x = −Γ y_x.

**Theorem 5.1 (index identity; discrete, rigorous).** Let z* be a genuine KKT point of D^cvx or D^0. Assume Z is nonsingular and Yres : x ↦ y_x (E_h → ℝ²) is invertible. Then
  **neg(Q) = neg(Z) − p₀(C_yw)**, where p₀ := #{eigenvalues of C_yw ≥ 0}.
*Proof.*
1. Z⁻¹Γ y_x = −h_x, so ΓᵀZ⁻¹Γ = −Ymap Yres⁻¹, where Ymap : x ↦ Y_x = Γᵀh_x.
2. Haynsworth inertia on [[Z,Γ],[Γᵀ,−I]] gives neg(Z+ΓΓᵀ) = neg(Z) − (neg+zero)(M), with M := I + ΓᵀZ⁻¹Γ.
3. M = (Yres − Ymap)Yres⁻¹ = −Wmap Yres⁻¹. By congruence, YresᵀMYres = −YresᵀWmap = −C_yw.
4. (C_yw is symmetric at every KKT point: this is stationarity under rotations about e_z.) Sylvester's law gives (neg+zero)(M) = p₀(C_yw). ∎

*Continuous analogue.* The same algebra holds for Q_red = J_red + g(I+G)⁻¹gᵀ with G = ∫kkᵀ/μ_u. Indeed ⟨g,J_red⁻¹g⟩ = −YmapYres⁻¹ − G, and M is congruent to −C_yw again.

**Theorem 5.2 (Sturm bounds).** Assume the Schur-reduced chain S (tridiagonal on b_1..b_{N−1}) has strictly negative off-diagonals; in continuous time, ν ≥ ν₀ > 0. Let k be the number of sign changes of h_m along the attitude chain (crossings of the primer plane), and assume h_m ≠ 0 at every node (no node lies in Π). Then
  **k − 1 ≤ neg(Z) = neg(S) ≤ k**, and neg(Z) = 0 if k = 0 and ζ₀ > 0.
*Proof.*
1. neg(Z) = neg(S) by Haynsworth with D ≻ 0.
2. h_m solves the homogeneous Jacobi recurrence of S, extended by the virtual end nodes carrying ζ₀.
3. Discrete Sturm oscillation: neg(S) is the number of generalized zeros of the principal solution φ (φ_0 = 0).
4. Sturm separation: zeros of φ and h_m interlace, which gives both bounds. The case k = 0 is also Thm 4.4 with c = m. ∎
The lower bound has a form-level proof that needs no spectral theory: between consecutive crossings, w_i := h_m·1_{[t_i,t_{i+1}]} satisfy J_red ≡ 0 on W = span{w_i}, and no w ∈ W is in the kernel (kinks with ν(t_i) > 0). A symmetric form vanishing on W without kernel has index ≥ dim W.

**Corollary 5.3 (classification of genuine KKT points).**
- **k ≤ p₀(C_yw) ⇒ Q ⪰ 0 ⇒ exact at w**, and z* is globally optimal in every dimension. This contains T4(a), since k = 0 forces p₀ = 0.
- **k ≥ p₀ + 2 ⇒ neg(Q) ≥ 1.** By math/08 Thm 2.4 (LICQ), z* is not a local minimizer in ℝ⁴. If z* were the genuine global optimum, CSD2′ would fail at w. (Never observed at numerically global optima.)
- **k = p₀ + 1:** exact ⇔ neg(Z) = k − 1, i.e. the principal solution has no generalized zero after the last crossing. In case T, k is even, so this residual class is **k = 2 with C_yw indefinite**.

**Conjecture CSD2″.** At every target, some genuine global optimum satisfies neg(Z) = p₀(C_yw). (On nondegenerate instances CSD2′ ⇔ CSD2″, by Thm 5.1 + math/08 Thm 2.1/2.4.)
After Cor 5.3, only the residual class remains. Numerically (§8) it occurs on 16 of 107 fully nondegenerate instances, always with neg(Z) = k−1 = p₀ (exact).

## 6. Discretization

### 6.1 Proposition P6 (no free singular arcs at genuine optima)
Let z* be a genuine local minimizer, continuous time, δ > 0. Then there is no interval I on which all of the following hold:
- P = −‖P‖b ≠ 0;
- ‖u‖ ≤ 1 − ε;
- ‖ḃ‖ ≤ ω − ε.

*Proof.*
1. On I, b ∈ Π, so the constant m is ⊥ b and ⊥ ḃ.
2. Take the 3D variation b′ = cos(εη)b + sin(εη)m, u′ = u − τb + εζm, with τ chosen so that ⟨u′,b′⟩ = cos δ and η, ζ ∈ C_c^∞(I).
3. First order: ΔJ = −2ε∫‖P‖η⟨u,m⟩. So ⟨u,m⟩ = 0 a.e. on I.
4. Second order, with ∫kη = 0 and ζ = Mη: ΔJ = ε²[|∫kζ|² − 2∫‖P‖(ζη − ½cos δ η²)] < 0 for M > cos δ/2.
5. Rate and norm slack keep b′, u′ admissible. This contradicts local minimality. ∎

The same variation with n in place of m is exactly the lift's improvement direction from math/08 Prop 6.1. **At genuine optima it is already available in 3D**, so continuous-time convexified optima are immune to the case-12 mechanism. A single singular node can still occur in discrete D^cvx (case 12: |d_14| = 0.97). It carries no gap because of the C-diagonal.

### 6.2 Proposition P7 (why unit-d fails, why the convexified lens works)
In D^unit the multiplier μ_k on ‖d_k‖² = 1 is free, and μ_k = ⟨P_k,d_k⟩ + ½(λ_k⟨d_k,b_k⟩ + λ′_k⟨d_k,b_{k+1}⟩). Suppose μ_k < 0, i.e. relaxing to ‖d_k‖ ≤ 1 would lower the cost to first order: the segment "wants to throttle". Then:
- (a) z* is not a KKT point of D^cvx. The genuine D^cvx optimum is strictly better (case 12: 0.0273676 < 0.0282327).
- (b) The lift contains a penalty-free copy of that throttle (Prop 6.1). The diagonal entry μ_k of Q is negative. With three such segments, or one coupled with the b-tilts, Q ≱ 0. By math/08 Thm 2.4 the genuine unit-d optimum is then beaten in ℝ⁴.
- (c) In D^cvx, μ_d ≥ 0 by the KKT sign. Every certificate in §4–§5 uses μ_d ≥ 0 (Schur step). In continuous time, μ_u ≥ 0 holds for the relaxed set K(b) automatically. By Aumann, relaxed and genuine thrust give the same readout, so the continuous genuine (unit-u) problem has the same value as the convexified one.

**NUMERICS (mu_unit.py).**
- Case 12 and 12 random unit-d gap instances from [verifier-sdp]'s bank. At the genuine unit-d optimum: #μ_d<0 ≥ 1 and λ_min(Q) < 0 in every case.
- The convexified versions: μ_d ≥ 0 and λ_min(Q) ≥ −1e-14 (PSD), with SDP_cvx = genuine_cvx.

So **the unit-d gap is exactly "negative norm multiplier + E⊥ tilt"**. Convexification removes it at the root (KKT sign), not by luck.

## 7. Physical meaning of exactness

If the lift is exact at w with genuine optimum z* = (b,u):
1. **b** is a genuine rate-limited attitude path in S², with b(0) = b(tf) = e_z.
2. **u(t) ∈ conv cap(b(t),δ)** is a relaxed thrust direction (‖u‖ < 1 means time-sharing between gimbal directions).
   - **Exact realization:** by Aumann's theorem, ∫k⊗K(b) = ∫k⊗cap(b) for the nonatomic Lebesgue measure. So some measurable unit u′(t) ∈ cap(b(t),δ) gives **the same terminal (r,v)**, with the same b. This is C-W of math/04 with b fixed. The value of the genuine (unit-thrust, unit-gimbal-direction) problem therefore equals the certified value **exactly**, and the infimum is attained.
   - **Approximation:** by Filippov–Ważewski, genuine trajectories are C⁰-dense in relaxed ones. A piecewise-constant chattering u′ can be chosen with ‖(r,v) − (r′,v′)‖_∞ ≤ ε.
   - Under a gimbal-rate limit (not modelled), only the approximate statement survives.
3. **Discrete D^cvx:** any d ∈ conv lens(b_k,b_{k+1}) is a convex combination of **two** lens points. Take the line through d along b_k × b_{k+1}: it keeps both gimbal inner products constant and leaves K only through the sphere. Time-sharing within segment k reproduces the V-readout exactly and the R-readout to O(h²) per segment. So D^cvx solutions are realizable to discretization accuracy.
4. **Rank > 3 SDP optima** (symmetric mixtures, Cor 2.3 of math/08) are still exact in value. A genuine optimum is recovered from any rank-3 projection plus a local polish, and then certified a posteriori by T4/T5.

## 8. Numerics (numerics/proof-csd2p/)

- **screen_big.py**:
  - setup: large ωtf ∈ {π, 1.5π, 2π, 3π}, N = 24, tf = 4, a = 11;
  - models: d=b and cvx15 (terminal), cvx40 and cvx15 (free b(tf));
  - targets: 24 per configuration (dent mixtures of rotated extreme arcs; mixtures of 2 and 3 genuine support points; random box);
  - SDP (Clarabel) vs 3D multistart (14 random + SDP-factor starts);
  - result: **384 targets, 0 gaps (rel ≤ 1e-4)**. Logs A.log, B.log; data results_{A,B}.jsonl.
- **picone_bank.py, picone_bank2.py**: the T4 LP criterion at genuine optima over [verifier-sdp]'s banks.
  - The criterion holds on ~2/3 of the N ≤ 8 bank. In every such instance Q ⪰ 0 (consistency check of T4).
  - Failures are two-crossing optima (overshoot / anti-aligned primers, e.g. case 12: angle(b,P) = 140–180°).
- **index_check.py, summarize_idx.py, summarize_strict.py**: T5 at genuine optima (D^cvx, D^0). 260 instances from [verifier-sdp]'s banks (incl. the 509 former unit-d gap targets, convexified) and my large-ωtf screen. Results: idx3.jsonl.
  - **Identity.** neg(Q) = neg(Z) − p₀(C_yw) holds on all 151 instances with C_yw nonsingular and the primer plane well defined. The raw-table failures are degenerate: C_yw singular, i.e. coplanar data or e_z ∈ Π.
  - **Sturm bounds.** Restricted to the 107 instances where h_m ≠ 0 at every interior node, k−1 ≤ neg Z ≤ k holds 107/107.
    - 91 of these (85%) are in the certified class k ≤ p₀.
    - 16 are in the residual class k = p₀+1. **All 16 have neg Z = k−1 (exact)**.
    - No optimum has k ≥ p₀+2. Observed (k, neg Z, p₀): (0,0,0), (2,2,2), (2,1,1), and (1,1,1), (1,2,2) with free b(tf).
  - **Apparent violations** (k=0 with neg Z>0, etc.) all violate T5's hypotheses. Either h_m = 0 (to 1e-13) at some nodes, i.e. the attitude runs *inside* the primer plane, so the crossing count is undefined, or Z is singular with a disconnected chain. These are not counterexamples. When the attitude lies in Π on an interval, m is a genuine normal there, as in the planar case of math/08 Thm 4.1.
- **index_c1.py** ([numerics] c1 cases, cvx15): 16/17 certified by T5. This includes set A cases 0–5 and 7–9 (GTPL-realistic) and set B case 12 (k = 2, C_yw ≻ 0). Case 6 (set A) is in the residual class and is exact numerically.
- **mu_unit.py**: §6.2.

## 9. Positioning

- **Relation to math/08.**
  - T1/T2 settle the linear and support-function part (SDP-F).
  - T4 generalizes Thm 4.1 (coplanar planar optima ⇒ certified). Planar optima have the attitude inside a plane containing e_z. The criterion is about the primer plane instead, and needs no planarity of the data.
  - T5 makes "Q ⪰ 0 at a genuine optimum" (math/08 Thm 2.4) into a countable condition: crossings vs. the sign pattern of a 2×2 matrix.
- **Relation to Theorems A/D.** Unchanged (math/08 §8). The lift is not state-linear (variance cost), and exactness here is per-target (a posteriori, or a priori on the class of Cor 4.3).
- **Not covered:** variable throttle (the natural lift is lossy, V-THR), glide slope / altitude (Gram-linear, but T4/T5 would need their multipliers in Z; not attempted), mass coupling beyond a known profile.

## 10. Lean-ready lemma list
See math/03, section "CSD2′" (appended).
