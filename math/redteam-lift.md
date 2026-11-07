# Red-team LIFT: lifting and relaxation routes to 5DOF LCvx

Author: [redteam-lift], 2026-11-06. Status: CLAIMED (attack welcome). Model: M1 of math/00 (rate-limited axis b,
gimbal cone δ, T∈[ρ1,ρ2], ρ1>0). Data θ=(r0,v0). Tent case b(0)=b(tf)=e_z, φ(s)=ω·min(s,tf−s) unless stated.
For the quantitative statements α=0, a1=ρ1/m0, a2=ρ2/m0.

## 0. Common frame and the mixing lemma

𝒯 = admissible trajectories τ=(b,T,d). θ(τ) = data from which τ lands. F = θ(𝒯) (= F_tf).
A **uniform relaxation** is a pair (C,Φ): C ⊆ Θ×Y convex (Y any real vector space), Φ: 𝒯→Y any map
(lifts, Gram matrices, occupation measures, discretizations, slacks), such that (θ(τ),Φ(τ)) ∈ C for every τ.
This is the *relaxation property*. It is how every formulation in this note relates to the original.

**Mixing lemma (ML).** For τ_1..τ_k ∈ 𝒯 and convex weights λ_i: (Σλ_iθ(τ_i), Σλ_iΦ(τ_i)) ∈ C.
If J: Y→ℝ∪{+∞} is convex and J∘Φ = cost, then J(ΣλΦ(τ_i)) ≤ Σλ_i cost(τ_i).
*Proof.* C is convex. Jensen. ∎

ML is the whole obstruction. A convex formulation whose data enter affinely cannot tell instance θ apart
from a *mixture* of instances θ_i with mean θ. Every route below either (a) has affine data and so contains
the mixtures (lossy), or (b) blocks mixtures by entering θ nonaffinely (the Dirac/Veronese entry). Then
Claim A does not apply.

Witness used throughout: P_{±u} = θ(τ_{±u}) (min-throttle, max-tilt arcs), θ_M = ½(P_u+P_{−u}) ∉ F (Thm B).

## 1. Relaxed controls / Young measures / Gamkrelidze chattering

State x=(r,v,m,b). Control w=(T,d,ω_⊥). Velocity set
f(x,U(x)) = {(v, Td/m+g, −αT, ω_⊥×b) : T∈[ρ1,ρ2], ∠(d,b)≤δ, ω_⊥⊥b, ‖ω_⊥‖≤ω}.

**1.1 Filippov–Ważewski hypotheses hold.** x ↦ f(x,U(x)) has nonempty compact values and is Lipschitz in the
Hausdorff metric. The cone cap(b,δ) moves isometrically with b. The tangent ball moves Lipschitz-ly on S².
Growth is bounded. So the relaxed reachable set equals the closure of the original one (Filippov 1967 /
Ważewski; cited as context). Nothing breaks here.

**1.2 The relaxation only convexifies the thrust, never b.** The (thrust, ω_⊥) parts act on disjoint
coordinates and have independent control sets, so co f(x,U) = co{(Td/m,−αT)} × (tangent ball). The ball is
already convex. So a relaxed trajectory has a *genuine* rate-limited b(·) and a Young measure ν_s on
(T,d) ∈ [ρ1,ρ2]×cap(b(s),δ).

**1.3 Proposition R1 (Thm B survives relaxation; strict gap).** θ_M ∉ F_rel. Since F_rel is compact,
dist(θ_M, F) ≥ dist(θ_M, F_rel) > 0.
*Proof.* Steps (1)–(3) of math/00 §4 are linear inequalities in ν_s, so they hold ν_s-a.e. They use
∫T dν_s ≥ ρ1, m(s) ≤ m0−αρ1 s, and d_z ≥ cos(δ+φ) on supp ν_s. Equality in the vertical bound forces
T=ρ1 and d = the unique great-circle point ν_s-a.e. So ν_s is a Dirac, b_z = cos φ, and steps (4)–(5)
(about the genuine b) go through unchanged. F_rel is compact: relaxed trajectories form a compact set in C⁰
(Filippov), and the endpoint map is continuous. ∎
(This independently recovers proof's P-ε/P-Q gap, non-constructively.)

**1.4 Proposition R2 (no relaxation gap when α=0).** Fix b(·). With α=0, the data map is
τ ↦ affine(∫(1,s)⊗(a d) ds). By Lyapunov–Aumann, ∫ co S_b = ∫ S_b for S_b(s) = {a d : a∈[a1,a2], d∈cap(b(s),δ)}.
So every relaxed endpoint, together with its fuel ∫a, is attained exactly by an ordinary control. Hence
F_rel = F and V_rel = V (α=0). For α>0 we only claim this up to closure.

**1.5 Where the hypotheses fail (b as a control).** Suppose b is modeled as a control rather than a state.
Then the rate limit ∠(b(s),b(s'))≤ω|s−s'| is a constraint on the control *path*, not a pointwise set
U(t,x). Filippov–Ważewski does not apply. The admissible b's form an equi-Lipschitz family, which is
compact in C⁰ (Arzelà–Ascoli). Weak and strong limits coincide, and every Young-measure limit is a Dirac on
an admissible b. So chattering in b is impossible. *This is exactly why the 3DOF trick fails:* in 3DOF, d
chatters freely between ±u. In M1, d is tied to b within δ, and b cannot chatter.
To "relax (b,d) jointly" you need two-time joint measures γ_{s,s'} that encode ∫b·b′dγ ≥ cos(ω|s−s'|).
Then γ = ½δ_{τ_u}+½δ_{τ_{−u}} is feasible and reaches θ_M. That is ML with affine data, so it is lossy.

**Verdict 1:** (i) Gamkrelidze relaxation is NOT a convex program: dynamics stay nonlinear in b, and only
the thrust set is convexified. (ii) Its reachable set is exact: closure for α>0, equality for α=0.
(iii) It is consistent with Claim B (R1) and gives dist(θ_M,F)>0. The trajectory-level joint relaxation is
convex but lossy, consistent with Claim A.

## 2. Occupation measures / moment–SOS (the serious threat)

Liouville LP P(μ0). Find measures μ on [0,tf]×X×W (occupation) and μ_T on X such that, ∀ φ ∈ C¹,
∫φ(tf,·)dμ_T − ∫φ(0,·)dμ0 = ∫(∂_tφ + ∇_xφ·f(x,w)) dμ, with supp μ_T ⊆ target {r=0,v=0}.
Minimize ∫ℓ dμ. The constraints are linear in (μ0,μ,μ_T). Two ways to enter θ:

- **(Dirac entry)** μ0 = δ_{(θ,m0,b0)}. Write P_δ(θ).
- **(Affine entry)** μ0 ∈ 𝒫(X0) is a decision variable with ∫(r,v)dμ0 = θ. Write P_aff(θ). This is the
  only way to make the LP jointly convex in (θ, measures), i.e. a uniform relaxation in Claim A's sense.

**Proposition O1 (affine entry is lossy, exactly by conv).** {θ : P_aff(θ) feasible} ⊇ conv F. Its value
is ≤ V**(θ), the closed convex envelope of V (V=+∞ off F). In particular P_aff(θ_M) is feasible.
*Proof.* ML with Φ(τ) = occupation measure of τ. ∎
(Superposition (Bernard 2008; Lasserre–Henrion–Prieur–Trélat 2008, Thm 2.3) also gives "⊆ cl conv F" and
"= V**". Cited, not needed.)

**Proposition O2 (Dirac entry is lossless, and nonaffine).** {θ : P_δ(θ) feasible} ⊇ F trivially. By the
superposition principle (cited) it equals F_rel, and inf P_δ(θ) = V_rel(θ) (Vinter 1993; LHPT 2008).
With R2: for M1 with α=0, P_δ is exact in both feasibility and value. For α>0 it is exact up to closure.
The optimal μ is a mixture of optimal relaxed trajectories that *all start at θ*. When the optimum is
unique, μ is its occupation measure and can be decoded.

**Reconciliation with Claim B / Vinter.** No contradiction. Vinter's value equality is a per-instance
statement with Dirac data. The map θ ↦ δ_θ is not affine: ½δ_{P_u}+½δ_{P_{−u}} ≠ δ_{θ_M}. So
{(θ,μ0,μ,μ_T)} is not convex, and Claim A's hypothesis fails. In moment form, the data enter as the
Veronese vector v_k(θ) = (θ^β)_{|β|≤k}. The order-1 truncation (first moments only) *is* P_aff, which is
lossy (O1). F's nonconvexity is seen only by moments of order ≥ 2. The Dirac constraint is
"Var_{μ0}(r,v) = 0", i.e. ∫‖x‖²dμ0 ≤ ‖θ‖². That is a reverse-convex constraint in θ, and the nonconvexity
lives there.

**Lemma O3 (Dirac convexity is vacuous).** For every compact S ⊆ Θ, S = {θ : δ_θ ∈ 𝒫(S)}, and 𝒫(S) is
convex and weak*-closed. (δ_θ ∈ 𝒫(S) ⇔ θ ∈ S.) So "convex after the embedding θ↦δ_θ" constrains nothing,
and no impossibility theorem can quantify over such entries. The same holds trivially for any per-instance
formulation: C_θ = {y*(θ)} is convex. Per-instance convexity is meaningful only for a *fixed formula* (data
entering through a fixed map that does not encode F), as with v_k(θ).

**Lossless in the user's sense?** Per instance, yes: P_δ is a convex LP whose optimum equals the true
optimum (α=0) and returns a solution, modulo uniqueness. But it is infinite-dimensional. Each moment–SOS
truncation is an SDP that gives a monotone lower bound converging to V (LHPT). For the solution set this is
an outer approximation v_k^{-1}(K_k), a semialgebraic set that can be nonconvex. Finite-order exactness is
not guaranteed. It is not a uniform LCvx.

**Verdict 2:** (i) convex per instance; (ii) Dirac version exact in feasibility and value (α=0), affine
version exact in neither (it computes conv F and V**); (iii) consistent with Claim A. The informal claim
"no convex formulation can be lossless" is FALSE. The theorem must say *data enter affinely* (order-1). See
BREAK post.

## 3. SDP / attitude lifts (bbᵀ, conv SO(3) orbitope, quaternions, Shor)

**3.1 Uniform lifts are lossy.** Any lift with θ affine is a uniform relaxation (Shor on Gram matrices,
Lasserre at any order, conv SO(3) as a 4×4 spectrahedron (Saunderson–Parrilo–Willsky), quaternion moment
matrices). Each one contains ½(Φ(τ_u)+Φ(τ_{−u})) at θ_M by ML. That point's moment matrix has rank 2.
**No rank-1 point exists in the slice at θ_M**, since θ_M ∉ F. So no rank-1 guarantee (S-lemma, sparsity /
acyclic sign patterns, etc.) can hold uniformly in θ.

**3.2 Hilbert-sphere lemma (new).** Take a degree-2 Shor relaxation with unit-vector variables b_k, d_k.
Every PSD moment matrix Z with Z₁₁=1 is E[zzᵀ] for a random vector z, so constraints become inner-product
constraints in H = L²(Ω;ℝ³). The constants span a copy of ℝ³ ⊂ H. Constraints of the form ‖b_k‖=1,
⟨b_k,b_{k+1}⟩≥cos ωh, ⟨d_k,b_k⟩≥cos δ, b_0=e_z depend only on traces. Any trace-Gram is realizable,
because any ℝⁿ embeds isometrically in H with ℝ³ fixed. So **Shor = the same problem posed on the unit
sphere of ℝⁿ (n arbitrary), with gravity/vertical in ℝ³**:
- uniform Shor (terminal constraint on first moments) ⇔ the endpoint's *orthogonal projection* onto ℝ³
  equals the target. Tilting into a 4th dimension projects to lateral 0, which is how θ_M is "reached";
- Dirac-lifted Shor **C-SD2** adds Var(Σ h a1 d_k) = 0 (equivalently E[(Σ)(Σ)ᵀ] = wwᵀ, a quadratic data
  entry). Then the endpoint must *lie in* ℝ³.

The spherical triangle inequality and its equality case hold on the sphere of any real Hilbert space. So
Thm B's proof runs verbatim in H. **Proposition S1:** C-SD2 is infeasible at (the discrete) θ_M
(fixed-thrust model a≡a1). Equality forces d_k = cos(δ+φ_k)e_z + sin(δ+φ_k)η with one unit η ⊥ ℝ-vertical
(rigidity in H). Then Σ h a1 d_k = M_z e_z + cη with c>0, which must equal the constant M = M_z e_z. That
forces η=0, a contradiction. ∎

**Proposition S2 (exactness ⇔ dimension invariance).** By symmetry under rotations of H fixing e_z, the
n-dim reachable set is {(z,x) : (z,‖x‖) ∈ Π_n} (velocity-only; add the lateral Gram invariants for (r,v)).
C-SD2's feasible set is the ℝ³ slice. So **C-SD2 is lossless ⇔ Π_n = Π_3 ∀n**, a clean geometric
statement: a rate-limited axis in higher dimensions reaches no new (vertical, lateral-radius) pairs.
**Min-landing-error form.** The feasible Gram set is θ-independent. The data enter only the objective
E‖S_v−w_v‖²+E‖S_r−w_r‖² = ⟨A,G⟩ − 2⟨w, mean(G)⟩ + ‖w‖², which is linear in G with coefficients affine in
w. So C-SD2 is the degree-2 moment (Shor) truncation of min-landing-error. It evades Claim D only through
the variance term (the cost is not a function of the linear physical state mean(G)). It is the same object
as [adversary]'s R ⪰ rrᵀ lift (threads/theorem-D.md item 4). Exactness ⇔ the relaxed (mean, second moment)
body equals conv{(x,‖x‖²) : x ∈ L} on its lower side.

**Numerics (mine, numerics/redteam-lift/; fixed thrust a1=5, α=0, δ=15°, ω=30°/s unless noted):**
- dimlift.py (velocity-only, NLP in ℝⁿ): the axis-lowest point and the inner annulus radii are identical
  for n=3,4,5 (to 1e-9 / 1e-5). Free throttle gives the same values: throttle does not enter the dent.
- csd2.py (velocity-only SDP vs NLP, N=16): at θ_M, P_u, and 12 points inside and outside the dent, the
  SDP value equals the NLP dist² to ≤2% at dist² ~1e-3, and to 1e-4 elsewhere (run_csd2_N16.txt). Uniform
  Shor returns 0 everywhere, i.e. it is lossy.
- **CORRECTION (2026-11-07 ~02:00).** My first (r,v) runs reported "gaps" of 1e-4 to 1e-3 relative
  (e.g. N=16 rand0: SDP 7.7729e-2 vs NLP 7.8046e-2). These were **solver artifacts**. In that
  formulation b_0 = b_N = e_z was imposed through Gram equalities. That kills Slater (no strictly
  feasible G), and Clarabel returned "optimal_inaccurate" values that were too low (SCS was even
  further off). In the well-posed formulation (sdp_clean.py: b_0, b_N replaced by the constant e_z;
  Slater holds) both solvers report "optimal", and the values agree with the genuine optima to ≤1e-6
  relative. Examples: N=16 rand0 0.0780472 vs genuine 0.0780469; N=3 j=5 0.4419871 vs 0.4419864;
  N=4 j=3 0.1118619 vs 0.1118615.
- scan_clean.py (well-posed SDP lower bound vs genuine upper bound from rank-3 projection + SLSQP polish,
  feasible to 1e-10): 3 configurations (N=16 tf=4 δ=15°; N=16 tf=3 δ=40°; N=20 tf=5 δ=15°), about 35
  targets (random mixtures of rotated extreme arcs, random (r,v), θ_M). **On every target the two agree
  to within solver tolerance (|relgap| ≤ 1e-6, absolute ≤ 2e-6), or both are ≈0 (reachable targets).**
  At symmetric targets (θ_M) the optimum is not unique, so the max-rank interior-point solution does
  not project to a genuine trajectory. There the SDP value matches the multistart NLP instead (53.6018
  vs 53.602; 15.5508 vs 15.551).
- The order-2 Lasserre runs (lasserre2.py) were started to certify a gap. They were stopped once the
  gap turned out to be an artifact.

- **[numerics] case 12 (BOARD 03:20), independently checked (case12_check.py).** Fixed thrust a=11,
  N=16, tf=4, ω=30°/s, δ=15°, an asymmetric target near a mixture of rotated extreme arcs.
  The well-posed SDP gives 0.0275290 with eigenvalues 27.72, 4.725, 1.475, **0.0781**, 0, …, i.e. exact
  rank 4. I factored the Gram into an explicit **4D** trajectory: rate and gimbal satisfied to ~2e-7, unit
  norms to 1e-8, cost 0.0275278. SLSQP polishing in ℝ⁴ returns 0.02752899 = SDP. So the SDP value is
  *attained by a genuine trajectory of the 4-dimensional problem*, as Lemma S2 predicts. In ℝ³, 480 NLP
  restarts ([numerics]) give 0.0282306 (gap 2.5% relative).
  So C-SD2 is exact iff the ℝ³ optimum equals the ℝ⁴ optimum, and here it apparently does not.
  **Π_4 ≠ Π_3 (numerically): Conjecture CSD2 is FALSE in general.** Rigorous status: the SDP is a valid
  lower bound and the 4D realization is exact. The only uncertified step is the 3D global optimum
  (an NLP). A small-N analog plus an order-2 Lasserre bound would make it a theorem.

**Verdict 3 (final):** uniform lifts are NOT lossless (rank-2 spurious points at θ_M; consistent with A).
The degree-2 min-landing-error lift C-SD2 is exactly "the 5DOF problem on a higher-dimensional sphere":
- it excludes the Thm B witness (S1);
- it is exact whenever the higher-dimensional optimum planarizes into ℝ³. That was the case on ~55 of 56
  instances tested, including all GTPL-realistic above-ground targets ([numerics] set A);
- it is **not exact in general**: [numerics] case 12 has a 4D optimum that is 2.5% better than the best 3D
  trajectory found.
So it is a tractable, very tight, but lossy convexification. It is valuable as an a-posteriori certificate
(§8): a rank-3 optimum certifies global optimality, and q_SDP > 0 certifies infeasibility. It is not a
lossless LCvx. Finite-order exactness of the moment route therefore fails already at degree 2 on this
instance. Higher orders converge (LHPT), but there is no finite-order guarantee. Variable throttle and
glide slope remain open.

## 4. Changes of variables, time dilation, reparametrizing θ

**4.1 Trajectory-side changes are irrelevant.** Claim A quantifies over all Y and Φ. Time dilation, tilt
or velocity as the independent variable, thrust direction as a state, polar coordinates: each only changes
(Y,Φ). If the result is convex with θ affine, A applies. (None of them linearizes M1 anyway. Dilation
σ·(ad+g) is bilinear.)

**4.2 Which θ-reparametrizations are legitimate.** Any compact S is a convex body's preimage under
θ↦δ_θ (O3). Any set homeomorphic to a convex set is convex after a homeomorphism. So the theorem must fix
the class. LCvx practice uses affine entry: r(0)=r0, v(0)=v0 as linear equalities. The only nonlinear
change in the literature is z=ln m, which is coordinatewise monotone. **Proposition P1 (separable
monotone changes don't help).** Let ψ(θ) = (ψ_r(r0), ψ_v(v0)) with ψ_v(v) = (ψ1(v_x),ψ2(v_y),ψ3(v_z)),
each continuous and strictly monotone, in a frame whose third axis is vertical. Then ψ(F) is nonconvex.
*Proof.* proj_v ψ(F) = ψ_v(proj_v F) (separability). Thm B's equality case shows the extreme slice
proj_vF ∩ {v_z = g0tf − z_min} is exactly the circle {−cu} of radius c>0. Take u = e_x. The ψ-midpoint of
ψ_v(P_{±u}) is ψ_v(x*,0,·) with |x*|<c, which is not on the circle. So proj_v ψ(F) is nonconvex, and so is
ψ(F) (a projection of a convex set is convex). ∎ So the theorem should read "affine (or separable
monotone) data entry".

**4.3 Free final time: the witness does not extend.** (Velocity-only landing, α=0.) Appending Δt with
b≡e_z, d=e_z, a=k∈[a1,a2] gives R_{tf+Δt} ⊇ R_tf + kΔt e_z. Suppose g0 > a1cosδ (GTPL: a1 = 5 < 9.8).
Choose (0, a1 tf cosδ) ∈ R_tf (b vertical, chattering d) and Δt = (a1tf cosδ − z_min)/(g0 − a1cosδ). Then
v0_M ∈ F_{tf+Δt}, so θ_M ∈ ∪_t F_t. Any free-tf impossibility needs a window condition like proof's P-tf,
and in practice the line search over tf must be included in the statement.

**Verdict 4:** no route. The theorem must restrict data entry to affine or separable-monotone (P1) and
must state fixed tf (or a P-tf-type window).

## 5. Cuts, conv of the trajectory set, and optimization-only losslessness

**5.1 Cuts cannot work.** A convex constraint valid for all genuine (θ(τ),Φ(τ)) is satisfied by every
mixture (ML). No valid cut removes (θ_M, ½ΣΦ(τ_{±u})).

**5.2 conv(graph) and its slices.** K = cl conv{(θ(τ),Φ(τ))}. The extreme points of K are genuine. But the
extreme points of the *slice* K_θ are not: they lie in ≤6-dim faces of K, i.e. they are mixtures of ≤7
genuine trajectories. min_{K_θ} J = V**(θ). This answers the brief's question: a linear objective's
minimum over K is attained at a genuine point, but over K_θ it need not be.

**Theorem A-opt (value-lossless on F ⇒ V = V** on F).** If a uniform relaxation (C,Φ,J) has
min_{C_θ} J = V(θ) for all θ ∈ F, then V(θ) ≤ V**(θ) on F. If it also always returns a genuine solution,
no nontrivial mixture attains V(θ). *Proof:* ML. ∎ Note: the standard LCvx definition ("relaxed optimum is
optimal for the original") together with attainment (C_θ closed and bounded, which holds under thrust
bounds) already implies Claim A's feasibility form. At θ_M the relaxed optimum exists and is not
original-feasible. **So Claim A's definition is not too strong for LCvx as defined.** Only a strictly
weaker notion, "exact on F and arbitrary off F (no infeasibility certificate)", could escape. 5.3 kills it
for general costs.

**5.3 Proposition T (attitude-sensitive cost: even value-lossless fails).** Cost ℓ(τ) = ∫₀^tf b·e_z ds
("maximize mean tilt"). Assume ωtf/2 > δ, δ+ωtf/2 ≤ π/2, and a2cos(ωtf/2−δ) ≥ a1 (α=0). Then there is
θ' ∈ F such that every uniform relaxation (C,Φ,J) with convex J∘Φ = ℓ has value at θ' ≤ Λ := ∫cos φ <
V(θ'). The relaxation is not even value-lossless on F.
*Proof.* ℓ ≥ Λ, with equality iff b = b_u for a constant u (math/00 step 4 rigidity). F(b_u) is convex and
compact (Aumann). Let L = vertical velocity increment. Its pointwise maximizer over S_{b_u}(s) is unique:
a=a2, with d tilted ψ(s) = (φ(s)−δ)_+ toward u. So max_{F(b_u)} L = Z' := ∫a2 cos ψ is attained only at
θ*_u, whose lateral part is ∝ u and nonzero. Put θ' = ½(θ*_u+θ*_{−u}). It lies on the axis with L = Z'.
(1) θ' ∉ F_tilt = ∪_u F(b_u): its maximizers are off-axis. (2) θ' ∈ F: take b≡e_z, d=e_z,
a(s) = a2cosψ(s) ∈ [a1,a2]. This matches θ' in both r and v. (3) V(θ') > Λ: if τ_n has ℓ → Λ, then
(Arzelà–Ascoli and weak* thrust limits) b_n → b_u uniformly, and the limit thrust is a selection of
co S_{b_u}, so θ' ∈ F(b_u) (Aumann). That is impossible. (4) ML: ½(Φ(τ*_u)+Φ(τ*_{−u})) ∈ C_{θ'} with
J ≤ Λ. ∎ So no uniform relaxation is lossless for *all* convex costs, even only on F.

**5.4 Min-fuel (open, numerically clean so far).** V_fuel ≥ ρ1tf, with equality exactly on F_min
(min-throttle data; compact). Theorem A-opt gives: value-lossless on F for fuel ⇒ F ∩ conv F_min ⊆ F_min.
By rotational symmetry, axis ∩ conv S = conv π_axis(S). A sufficient test for failure: free throttle reaches
an axis point below the min-throttle axis point. **Numerics (mine): no.** At the GTPL point above,
z_c(free throttle) = z_c(min throttle) = 17.42075. So min-fuel may satisfy V = V** on F. Even then, the
relaxation would be spuriously feasible on conv F∖F (θ_M) with no infeasibility certificate. For guidance
that is not LCvx, and K has no known tractable description.

**Verdict 5:** cuts impossible. Optimizing over conv is exact iff V = V** on F, which is false for
attitude-sensitive costs (Prop T) and open for min-fuel (numerically holds on the axis test). Claim A's
feasibility definition is the right one for LCvx (it is implied by the standard definition plus
attainment). Add A-opt as a companion theorem.

## 6. Recommended statement of the impossibility theorem

*For M1 (hence the rate-limited 6DOF envelope models) at fixed tf in the Thm B regime: there is no convex
C ⊆ Θ×Y, with θ entering affinely (or through a separable monotone map), that is lossless in the
feasibility sense. There is also none that is lossless in optimal value on F for all convex costs (Prop T).
Sharpness: (a) with Dirac/Veronese data entry, a lossless convex formulation exists (occupation LP P_δ,
infinite-dim); (b) the order-1 truncation is exactly the affine case and is lossy by conv; (c) at degree 2,
the min-landing-error Shor lift C-SD2 (= the problem on a higher-dimensional sphere) excludes the Thm B
witness and is exact whenever the optimum planarizes into ℝ³ (almost all tested instances), but not in
general ([numerics] case 12: rank-4 optimum, 2.5% gap). So it is a certificate, not a lossless LCvx.*

## 7. Lean-ready statements (finite-dimensional / abstract)

Setting. `T` is any type (admissible trajectories). `Θ`, `Y` are real vector spaces (finite-dim is fine).
`θ : T → Θ`, `Φ : T → Y`, `c : T → ℝ` (cost). `C : Set (Θ × Y)` is convex, `J : Y → ℝ` is convex.
Relaxation property: `hrel : ∀ τ, (θ τ, Φ τ) ∈ C`, `hJ : ∀ τ, J (Φ τ) = c τ`. Let `F := Set.range θ`.

**Lemma ML (mixing, two-point).** For τ₁ τ₂ : T and λ ∈ [0,1], put x := λ•θ τ₁ + (1−λ)•θ τ₂ and
y := λ•Φ τ₁ + (1−λ)•Φ τ₂. Then (x,y) ∈ C and J y ≤ λ·c τ₁ + (1−λ)·c τ₂.
*Proof.* `Convex` of C applied to the two members from `hrel`, `ConvexOn` of J, rewrite with `hJ`. ∎

**Definition (value-lossless on F, infimum-free form).**
`VL : ∀ x y, (x,y) ∈ C → x ∈ F → ∃ τ, θ τ = x ∧ c τ ≤ J y`.
"Every relaxed point over a feasible datum is dominated by a genuine trajectory at the same datum." It
follows from V_rel = V on F plus attainment of V (true for M1 with α=0: compactness of relaxed
trajectories plus Lyapunov, §1). It is implied by the standard LCvx guarantee.
(Infimum form, if preferred. V_rel(x) := inf{J y | (x,y)∈C} is convex on proj C (from ML).
V_rel ≤ V on F (from hrel). If V_rel = V on F, then V = V** on F, i.e. V(Σλᵢxᵢ) ≤ Σλᵢ V(xᵢ) whenever
xᵢ ∈ F and Σλᵢxᵢ ∈ F. Use `EReal` or assume J bounded below.)

**Theorem A-opt.** Under VL, for τ₁ τ₂ and λ ∈ [0,1] with x := λ•θ τ₁+(1−λ)•θ τ₂ ∈ F, there is τ with
θ τ = x and c τ ≤ λ·c τ₁ + (1−λ)·c τ₂.
*Proof.* ML gives (x,y) ∈ C with J y ≤ λc τ₁+(1−λ)c τ₂. Apply VL at (x,y). ∎

**Corollary T-abstract (no value-lossless uniform relaxation).** Suppose there are τ₊ τ₋ : T and Λ : ℝ with
(h1) c τ₊ = Λ and c τ₋ = Λ,
(h2) x' := ½•θ τ₊ + ½•θ τ₋ ∈ F,
(h3) ∀ τ, θ τ = x' → Λ < c τ.
Then no (C, J, Φ) satisfying hrel, hJ, convexity and VL exists.
*Proof.* A-opt with λ = ½ gives τ with θ τ = x' and c τ ≤ Λ, which contradicts h3. ∎
(The feasibility version, Claim A, is the same skeleton with c ≡ 0 and "x' ∉ F" in place of h2+h3.)

**Model facts that discharge h1–h3 for M1 (Prop T, §5.3).** These are the analytic inputs. Each is a
separate lemma for [lean]/[proof].
- (F1) ℓ(τ) = ∫ b·e_z ≥ Λ := ∫cos φ, from the angle bound ∠(b(s),e_z) ≤ φ(s) (math/03 spherical lemma).
- (F2) ℓ(τ) = Λ ⇒ b = b_u for a constant u (rigidity, math/00 step 4).
- (F3) For fixed b_u, the data set F(b_u) is convex and compact, and the vertical-velocity functional L
  has a unique maximizer θ*_u over it, with lateral part ∝ u and nonzero when ωtf/2 > δ (Aumann plus a
  unique pointwise argmax).
- (F4) x' = ½(θ*_u+θ*_{−u}) ∈ F, via b≡e_z, d=e_z, a = a2cos((φ−δ)_+) ∈ [a1,a2].
- (F5) Strictness h3: if θτ = x' then ℓ(τ) > Λ. By F2 equality would force x' ∈ F(b_u), and x' is not a
  maximizer location. The infimum form needs compactness to get a uniform ε; the VL form needs only the
  pointwise strict inequality.
Take τ_± = the maximizers in F3 (ℓ(τ_±) = Λ, so h1 holds).

## 8. How the C-SD2 (degree-2 Shor) certificate is used in practice

For each instance, solve C-SD2 in its **well-posed form** (b_0 = b_N = e_z substituted, not imposed by
Gram equalities, so Slater holds; see the §3.2 correction). Constraints are θ-independent and the data
enter only the objective.
Its value q_SDP(w) ≤ q*(w) (the true min landing error²) always holds, because ℝ³ ⊂ H.
1. **Rank-3 (flat) optimum ⇒ certified global optimum.** If the optimal Gram has rank 3, i.e. all
   b_k, d_k lie in the span of the constants, then its coordinates in that span are a genuine
   trajectory. Its cost equals q_SDP ≤ q*, so it is globally optimal.
2. **Not flat ⇒ certified gap.** Project onto the constants' span, normalize, and polish with an NLP to
   get an upper bound q_NLP. The true optimum lies in [q_SDP, q_NLP]. In practice the optimum is
   rarely exactly rank 3 (non-unique optima give max-rank interior-point solutions), but projection +
   SLSQP closed the bracket to ≤1e-6 relative on every generic target tested. Symmetric targets need
   a rank-reduction step or a random tie-breaking perturbation first.
3. **Infeasibility certificate.** q_SDP(w) > 0 ⇒ w is unreachable (θ ∉ F), rigorously. Example: at θ_M,
   q_SDP = 53.6 (N=16, (r,v)), certifying the Thm B witness. Uniform (affine-data) relaxations can never
   do this (mixing lemma).
Limits: fixed thrust magnitude only (U=a·d is not degree-2 in the Hilbert form); intermediate state
constraints (glide slope) involve non-deterministic partial sums in H and need extra variance terms.
