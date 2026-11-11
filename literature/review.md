# Literature review: lossless convexification (LCvx) and its extension to 5DOF/6DOF powered descent

Author: [lit-review] agent. Date: 2026-11-06. Bibliography: `literature/refs.bib` (keys in brackets).

## How the sources were verified

- **DOIs.** Every DOI listed here was resolved against the Crossref API (`api.crossref.org/works/<doi>`). Title, authors, venue, volume and pages all matched.
- **arXiv items.** Checked through the arXiv API or the abstract page.
- **Full text read** (pdftotext): ACB 2013 TCST, Blackmore–Açıkmeşe–Carson ACC 2012, the Malyuta et al. CSM tutorial (arXiv 2106.09125), the Malyuta–Yu–Elango–Açıkmeşe survey (arXiv 2108.02335), Lasserre–Henrion–Prieur–Trélat (arXiv math/0703377), Szmuk–Reynolds–Açıkmeşe (arXiv 1811.10803), Kiami (arXiv 2411.18004), Jung et al. (arXiv 2405.01264), Wang's G&C survey (arXiv 2311.05115), and Malyuta–Açıkmeşe semi-continuous (arXiv 1911.09013).
- **Abstract or secondary source only.** Some summaries come only from abstracts or secondary sources. Each is marked *(abstract-level)* or *(secondary)*.
- **Not cited as fact.** Anything I could not verify is marked UNVERIFIED and is not relied on.
- **Inaccessible.** AIAA ARC, ScienceDirect and SIAM full texts returned HTTP 403, so several paywalled papers are summarized from abstracts, tutorials or citing works.

---

## 0. Verdict up front: has anyone already done 5DOF/6DOF LCvx or proved impossibility?

**No to both, as far as I can find (literature through Nov 2026).** Search coverage:
- Crossref bibliographic queries.
- arXiv API full listing for "lossless convexification" (all 17 hits 2019–2026).
- Extended web searches for attitude, thrust-direction rate, 5DOF, 6DOF, quaternion, "exact relaxation", rate constraints and impossibility.
- Recent work from the Açıkmeşe, Harris, Liu/Yang (BIT), Lu, and Mesbahi groups.

Evidence:

1. **Every LCvx theorem on record assumes linear (LTV) dynamics in the convex program.** The thrust direction is a free control in those theorems. It is never a rate-limited state.
   - The CSM tutorial says so directly [malyuta2022csm, §"Nonlinear Dynamics"]: across all the LCvx results it lists, the dynamics barely change from the LTV template (6b).
   - The single nonlinear result [blackmore2012scl] relaxes only the control constraint. The tutorial stresses that the dynamics themselves are not convexified, so the relaxed problem stays nonlinear and must be solved globally by other means (piecewise-affine dynamics plus MILP).
   - That result needs "total observability/controllability of the linearization along *all* feasible trajectories" (Condition 7).
   - So it is per-instance and nonconvex. It is not a convex program at all.
2. **All 6DOF powered-descent methods are local or sequential.** They do not prove losslessness.
   - The families are SCvx, PTR, GuSTO, augmented convex–concave decomposition, indirect, and MPC. Sources: [szmuk2017gnc, szmuk2018gnc, szmuk2020jgcd, reynolds2020dq, reynolds2020ptr, elango2025automatica, elango2025scitech, uzun2025scitech, sagliano2024jgcd, nurre2025arxiv, leemesbahi2017jgcd].
   - LCvx appears only as **"embedded LCvx"**. Only the thrust lower bound or pointing cone is relaxed inside an SCP loop [malyuta2022csm; malyuta2021survey].
3. **The one 5-DOF formulation found** is Jung et al. 2024/2025 [jung2025ijcas]. It models pitch, yaw and throttle as first-order-lag states and solves the problem by SCP. It makes no exactness claim.
4. **The closest "LCvx with rate limits" items:**
   - **(a) Berning, Strohl, Bieniawski 2023** [berning2023scitech], "Lossless Convex Guidance for Lunar Powered Descent".
     - A secondary source [wang2023survey] says it adds maximum tilt rate, maximum tilt acceleration and maximum thrust ramp-rate constraints. It also says the "lossless convexification framework" of Açıkmeşe–Ploen was used to relax the problem into an SOCP.
     - **I could not access the full text** (ARC 403). I could not confirm whether losslessness is *proved* with the rate constraints active, or whether they are simply appended as convex constraints and losslessness observed numerically.
     - **This is the single most important paper for someone with ARC access to read.** See §6 for why it does not contradict Thm A even if its claims hold.
   - **(b) Kiami 2024 (arXiv)** [kiami2024arxiv]. It adds a discrete bound ‖u_{i+1} − u_i‖ ≤ δ(ρ̃_min) on the *thrust/acceleration vector* differences. The bound is a device to keep piecewise-linear controls above ρ_min between nodes. It does not model attitude-rate limits. The result is approximate: violations on ≤ 2n_x+2 edges.
5. **No impossibility theorem exists for LCvx.** The nearest "negative" results:
   - The discrete-time counterexample of Luo–Echigo–Açıkmeşe [luo2026automatica]: violations at up to n_x−1 nodes, and the bound is tight.
   - The remark in [acikmese2013tcst] that guaranteeing losslessness "is not always possible", with no theorem.
   - The infimum-gap ⇔ abnormality results of Palladino–Vinter [palladino2014sicon, palladino2015dcds].
   - The restriction of general-convex-state-constraint LCvx to pointwise-in-time activation [acikmese2011automatica, via malyuta2022csm].

   None of these addresses attitude, nor the convexity of the set of feasible boundary data.

**Conclusion for the project.** An impossibility result for uniform convex relaxations of 5DOF/6DOF landing (Thm A + Thm B) would, to the best of this search, be **new**. So would a precise positive result for fixed attitude profiles (Thm C). The definitional choices in §6 need care, because occupation-measure LPs and per-instance relaxations sit right on the boundary of "uniform".

---

## 1. Exact statements of the general LCvx theorem conditions

Notation follows the CSM tutorial [malyuta2022csm, Part I]. That tutorial collects the theory from [acikmese2011automatica] (its ref [86], Thm 2), [carson2011acc, acikmese2013tcst] ([87, 96]), [harris2013cdc, harris2014automatica] ([88, 89]), [harris2013acc] ([102]) and [blackmore2012scl] ([46]).

### 1.1 Definition of "lossless" as used in the literature

- **[acikmese2013tcst, §I]:** "We refer to this as a lossless convexification of the original control problem, since no part of the feasible region is removed and the optimal solutions of the relaxed problem define optimal solutions to the original problem."
  - Formally (Def. 1 / Lemma 1): F_e, F_f are the feasible sets of the original problems and F_re, F_rf those of the relaxed problems. Then F_f ⊆ F_re-projections.
  - If an optimal relaxed solution satisfies ‖T_c(t)‖ = Γ(t) a.e., it is optimal for the original problem.
  - The theorem guarantees this holds for **every** optimal relaxed solution, possibly after an arbitrarily small perturbation of the dynamics (ω → ω̂).
- **[blackmore2012scl] (ACC version):** "We refer to this as a lossless convexification, since no part of the feasible space of the original problem is removed in the process of rendering the constraints convex." Theorem 1 concludes that the optimal relaxed solution "is the optimal solution to Problem 1".
- **[malyuta2021survey, §2.3]:** "If the reformulation is exact, in other words the solution set is neither reduced nor expanded, the convexification is lossless."
- **[malyuta2022csm]:** Theorem 1 says "The solution of Problem 7 is globally optimal for Problem 6 if Conditions 1 and 2 hold." The goal of LCvx is to prove that the LCvx equality constraint g₁(u) ≤ σ holds with equality at the optimum.
- **Important practical caveats on what "lossless" means in practice:**
  1. It is a statement about **optimal** solutions of a **per-instance** relaxation. The boundary data are fixed.
  2. Free-final-time problems are often solved as a **sequence** of convex programs, via a line search or golden-section search over t_f [blackmore2010jgcd; acikmese2013tcst]. Kunhippurayil–Harris–Jansson [kunhippurayil2021automatica] give a sufficient condition for a *single* fixed-t_f program to suffice. Otherwise they prove only that a sequence suffices *(abstract-level)*.
  3. Some theorems require a small perturbation of the dynamics (ω̂ in [acikmese2013tcst]; random A-perturbation in [luo2026automatica]).
  4. With mass depletion, the GFOLD SOCP replaces ρ₁e^{−z} ≤ σ ≤ ρ₂e^{−z} by a second-order-cone/linear Taylor approximation about z₀(t) = ln(m₀ − αρ₂t) [acikmese2007jgcd, Lemma 2, as quoted in acikmese2013tcst §III and malyuta2022csm eq. 101]. The deployed program is therefore lossless only modulo that (conservative, accurate) approximation.
  5. Discrete-time LCvx is **not** exact in general [luo2026automatica].

### 1.2 Control-constrained LCvx (no state constraints) [acikmese2011automatica, Thm 2], as stated in [malyuta2022csm]

**Original problem (Problem 6):**
- min m(t_f, x(t_f)) + ζ ∫ ℓ(g₁(u)) dt
- subject to ẋ = A(t)x + B(t)u + E(t)w
- ρ_min ≤ g₁(u), g₀(u) ≤ ρ_max
- x(0) = x₀, b(t_f, x(t_f)) = 0

Here g₀, g₁ are convex, ℓ is convex and nondecreasing, b is affine, and ζ ∈ {0,1}.

**Relaxation (Problem 7):** add a slack σ, impose ρ_min ≤ σ, g₀(u) ≤ ρ_max, g₁(u) ≤ σ, and use the cost ζ ∫ ℓ(σ).

**Standing assumptions:**
- **Assumption 1:** ∇_x b[t_f] has full row rank.
- **Assumption 2:** ℓ(z) > 0 for z ≠ 0.

**Conditions:**
- **Condition 1:** {A(·), B(·)} is *totally controllable*: any state can be steered to any state in any finite interval [0, t_f]. For LTI systems this is ordinary controllability.
- **Condition 2:** The vector m_LCvx = (∇_x m[t_f], ∇_t m[t_f] + ζℓ(σ(t_f))) and the columns of B_LCvx = (∇_x b[t_f]ᵀ; ∇_t b[t_f]ᵀ) are linearly independent. This is a transversality-based non-degeneracy condition.

**Theorem 1:** Conditions 1 and 2 imply that the solution of Problem 7 is globally optimal for Problem 6.

### 1.3 Pointing constraint [carson2011acc; acikmese2013tcst]

**Original constraint:** n̂_uᵀu ≥ n̂_g g₀(u). For thrust this is n̂ᵀT ≥ ‖T‖ cos θ.

**Relaxation:** n̂_uᵀu ≥ σ n̂_g.

**Condition 3:** Let N span null(n̂_uᵀ). Then {A(·), B(·)N} must be totally controllable.

**Theorem 2:** Conditions 1, 2 and 3 imply losslessness.

**In [acikmese2013tcst] specifically (Theorem 1):**
- The dynamics are those of a planet rotating at rate ω. LCvx holds for the perturbed ω̂ defined case-by-case in their eq. (21), *provided the optimal state trajectory lies in int X*.
- **Lemma 2 (the key analytic step).** For λ̇ = −A(ω̂)ᵀλ, y = Bᵀλ:
  - (i) y is analytic, so either y ≡ 0 or y has countably many zeros.
  - (ii) y(t) = −α(t)n̂ (α > 0) holds only at countably many instants.
- **Lemma 3 (pointwise extreme-point lemma).** max yᵀT_c over U(Γ) = {‖T_c‖ ≤ Γ, n̂ᵀT_c ≥ Γ cos θ}, with y ≠ 0 and y ≠ −αn̂, is attained at an extreme point. Extreme points satisfy ‖T_c‖ = Γ.
- The translation–attitude decoupling is an explicit modeling assumption (§II): "translational dynamics are decoupled from rotational (attitude) dynamics … any attitude maneuver required to point the thruster … can be done very quickly."

### 1.4 State constraints

**Affine state constraints Hx ≤ h** [harris2013cdc, harris2014automatica]:
- **Condition 4:** For each facet with h_i ≠ 0, there is a cyclic-coordinate translation making it a subspace.
- **Condition 5:** For each facet F_i, choose (F_i, G_i, H_i) so that u = F_i x + G_i v + H_i w keeps x on the facet. Then the dual system λ̇ = −(A+BF_i)ᵀλ − (CF_i)ᵀμ, y = (BG_i)ᵀλ + (CG_i)ᵀμ has **no transmission zeros**.
- **Theorem 3:** Conditions 2 and 5 imply LCvx.

**Quadratic state constraints x₂ᵀHx₂ ≤ 1** (double-integrator-like structure; A, B, H invertible) [harris2013acc]:
- **Condition 6:** a modified transversality condition.

**General convex X** [acikmese2011automatica]:
- LCvx holds if the state constraint is active only at **isolated** instants and Conditions 1 and 2 hold (Theorem 5).
- If ζ = 0, a two-step algorithm is used.

**Mixed constraints y = Cx + Du** [kunhippurayil2022ctt]:
- Strong observability is a sufficient condition for non-singularity and LCvx.

**Time-optimal problems with state constraints** [woodford2022tac]:
- Strong-observability-based geometric conditions *(abstract-level)*.

### 1.5 Nonlinear dynamics [blackmore2012scl]

**Problem:** ẋ = f(t, x, u, g(u)), with 0 < ρ₁ ≤ g(u) ≤ ρ₂. The relaxation is g(u) ≤ Γ, with ρ₁ ≤ Γ ≤ ρ₂ and f(t, x, u, Γ).

**Condition 1 (ACC 2012):** "The pair [−(∇_x f), (∇_u f)] is totally observable on [0, t_f] for all sequences of x and u satisfying (7)–(10)."

**Theorem 1 (ACC 2012):** If Condition 1 holds and l(t, Γ) ≠ 0 for all Γ ∈ [ρ₁, ρ₂], the optimum of Problem 2 is optimal for Problem 1. In the CSM it reads "Conditions 2 and 7 imply Theorem 6".

**Corollaries** covering the dynamics classes where the condition holds automatically:
- **Corollary 1:** x = (x₁, x₂), f = (f₁(t, x), f₂(t, x, u)), with null ∇_u f₂ = {0} and null ∇_{x₂} f₁ = {0}. This needs 2m ≥ n.
- **Corollary 2:** a mass-like extra state with a null(M) = {0} condition.

Examples: rocket landing with nonlinear gravity, drag and mass depletion, and a UAV stall-speed bound.

**Relevance to us.**
- The 5DOF state includes b ∈ S² with ḃ = ω × b, and the thrust control is constrained relative to the *state* b (gimbal cone). That is a **state-dependent control set**, which is outside the class f(t, x, u, g(u)) with fixed control set {ρ₁ ≤ g(u) ≤ ρ₂}.
- Even where the result applies, the relaxed problem is nonconvex.
- The proof also only rules out y ≡ 0 on intervals. It does not show the zero set is null, a subtlety handled by analyticity in the linear case.

### 1.6 Other relaxation families

| Paper | Scope |
|---|---|
| Malyuta–Açıkmeşe [malyuta2020ifac] (arXiv 1911.09013) | Semi-continuous inputs: each input is either off or in {ρ₁ ≤ ‖u_i‖ ≤ ρ₂, pointing-cone}, with overlapping cones allowed. Linear dynamics. Assumptions: C_i full row rank, ρ_{i1} < ρ_{i2}. Conditions: strong observability of the adjoint, plus pointing-cone conditions and a cost condition. Earlier arXiv 1902.02726 [malyuta2019arxiv] covers disjoint semi-continuous inputs. |
| Harris [harris2021tac] | Disconnected control sets. Exact "extreme point relaxations" when the system is *normal*. Control-set approximations and small dynamics perturbations restore normality. Covers linear systems **and nonlinear systems affine in the control** *(abstract-level)*. |
| Kunhippurayil–Harris–Jansson [kunhippurayil2021automatica] | Annular control constraints, fixed final time. A sufficient condition for a single convex program; controllability suffices for a sequence of programs *(abstract-level)*. |
| Yang & Liu [yang2024tac] | Linear systems with general nonconvex control sets. An "augmented convex-hull relaxation" (auxiliary state plus terminal constraint) is exact under a checkable control-set property *(abstract-level)*. |
| Yang, Liu, Lin [yang2024jgcd] | Exact relaxation by problem reconstruction (JGCD 2024; abstract not retrieved). |
| Yang et al. [yang2025taes] | Unified sufficient conditions. They reduce to controllability, normality and strong observability *(abstract-level)*. |
| Arenas-Uribe, Poonawala, Hoagg [arenasuribe2025arxiv] | LTV systems with discrete-valued inputs; geometric conditions plus normality *(abstract-level)*. |
| Luo–Echigo–Açıkmeşe [luo2026automatica] | Discrete-time LCvx. After a random perturbation of A, violations occur at ≤ n_x−1 nodes ("normal" case). Long-horizon cases need bisection on the value function. A counterexample shows the bound is tight. |
| Luo–Spada–Açıkmeşe [luo2025lcsys] | Discrete-time LCvx for pointing constraints. |
| Kiami [kiami2024arxiv] | First-order-hold controls. Problem 5 adds ‖u_{i+1} − u_i‖ ≤ 2√(ρ̃_min² − ρ_min²). Assumption 1: a feasible point with ‖u_i‖ < ρ_max; (A, B₀+AB₁) controllable; full-rank equality Jacobian. Theorem 2: violations on ≤ 2n_x+2 edges in O(log(Δρ/ε)) solves. |
| Upadhyay, Ganguly, Chatterjee [upadhyay2026arxiv] | Annular LCvx with piecewise-constant digital control; exact for linear systems. 3DOF landing example. |
| Liu–Shen–Lu [liu2016jgcd] | Entry problem with bank angle (u₁, u₂) = (cos β, sin β). The relaxation ‖u‖² ≤ 1 is proved active ("assurance of active control constraint"). Same idea for missiles [liu2016taes] and rocket landing with aerodynamic controls [liu2019jgcd]. A unit-circle control is relaxed to the disk with no rate limit on the angle, which is structurally the 3DOF LCvx trick. |
| Kim–Mesbahi [kim2004tac] | Attitude keep-out constraint qᵀMq ≤ 0 replaced exactly by qᵀ(M+μI)q ≤ μ **given ‖q‖ = 1** [malyuta2021survey §2.3]. The unit-norm constraint and attitude dynamics stay nonconvex, and the method optimizes greedily one step at a time [malyuta2021survey §3.4; kim2010taes]. |

---

## 2. Core LCvx papers

For each paper: citation and DOI, a summary of what it proves, and relevance to 5DOF/6DOF.

**[acikmese2007jgcd]** Açıkmeşe, B., Ploen, S. R. "Convex Programming Approach to Powered Descent Guidance for Mars Landing." *JGCD* 30(5):1353–1366, 2007. DOI 10.2514/1.27553. *(secondary/abstract-level; full text not accessed)*
- First lossless convexification. The minimum-fuel 3DOF soft-landing problem with ρ₁ ≤ ‖T‖ ≤ ρ₂ is relaxed via a slack Γ and solved as a single SOCP, using a change of variables (σ = Γ/m, z = ln m) and a Taylor approximation of the e^{−z} bounds.
- Assumptions: point mass, constant gravity, free thrust direction, linear dynamics after the change of variables.
- **Relevance:** baseline M0. Attitude is a "proxy" (thrust direction), with no rate limit.

**[acikmese2005gnc]** Açıkmeşe, B., Ploen, S. "A Powered Descent Guidance Algorithm for Mars Pinpoint Landing." AIAA GNC 2005. DOI 10.2514/6.2005-6288.
- Conference precursor of the 2007 paper.

**[blackmore2010jgcd]** Blackmore, L., Açıkmeşe, B., Scharf, D. P. "Minimum-Landing-Error Powered-Descent Guidance for Mars Landing Using Convex Optimization." *JGCD* 33(4):1161–1171, 2010. DOI 10.2514/1.47202. *(secondary)*
- Prioritized problem: first minimize landing error ‖Er(t_f) − q‖, then minimize fuel at that error.
- Both stages are lossless SOCPs; t_f is found by line search.
- **Relevance:** "lossless" here already involves a *sequence* of convex programs (two stages plus a t_f search).

**[acikmese2008gnc]** Açıkmeşe, Scharf, Blackmore, Wolf. "Enhancements on the Convex Programming Based Powered Descent Guidance Algorithm for Mars Landing." AIAA/AAS Astrodynamics 2008. DOI 10.2514/6.2008-6426.
- Adds planet rotation and related enhancements. Context only.

**[acikmese2011automatica]** Açıkmeşe, B., Blackmore, L. "Lossless convexification of a class of optimal control problems with non-convex control constraints." *Automatica* 47(2):341–347, 2011. DOI 10.1016/j.automatica.2010.10.037 (ACC 2010 version: DOI 10.1109/ACC.2010.5530931).
- General LTV theorem (§1.2), plus the general-convex-state-constraint result (isolated activation).
- **Relevance:** the general template. Its controllability and transversality hypotheses are the ones Thm C (fixed attitude) must reproduce.

**[carson2011acc]** Carson, J. M., Açıkmeşe, B., Blackmore, L. "Lossless convexification of Powered-Descent Guidance with non-convex thrust bound and pointing constraints." *ACC 2011*, 2651–2656. DOI 10.1109/ACC.2011.5990959.
- Adds the thrust-pointing cone n̂ᵀT ≥ ‖T‖ cos θ, nonconvex for θ > 90°. It is relaxed to the half-space n̂ᵀT ≥ Γ cos θ.

**[acikmese2013tcst]** Açıkmeşe, B., Carson, J. M., Blackmore, L. "Lossless Convexification of Nonconvex Control Bound and Pointing Constraints of the Soft Landing Optimal Control Problem." *IEEE TCST* 21(6):2104–2113, 2013. DOI 10.1109/TCST.2012.2237346. *(full text read)*
- Unifies the upper/lower thrust bound, pointing, state constraints and planet rotation. Theorem 1, Lemmas 2 and 3 are in §1.3.
- Assumptions: controllable [A(ω̂), B]; optimal state in int X; perturbation ω̂ when n̂ is degenerate with respect to ω; attitude decoupled.
- **Relevance:** Lemma 3 is exactly the pointwise lemma Thm C needs, with a time-varying cone axis b(t). The analytic zero-set argument (Lemma 2) breaks once n̂ → b(t) is a general time-varying state, because y(t) = −α(t)b(t) is no longer a statement about an analytic function against a fixed direction.
- The paper also notes that losslessness was observed but not proved when state constraints are active.

**[carson2011aero]** Carson, Açıkmeşe, Blackmore, Wolf. "Capabilities of convex Powered-Descent Guidance algorithms for pinpoint and precision landing." IEEE Aerospace Conf. 2011. DOI 10.1109/AERO.2011.5747244.
- Capability study. Context.

**[blackmore2012scl]** Blackmore, L., Açıkmeşe, B., Carson, J. M. "Lossless convexification of control constraints for a class of nonlinear optimal control problems." *Systems & Control Letters* 61(8):863–870, 2012. DOI 10.1016/j.sysconle.2012.04.010 (ACC 2012 version: DOI 10.1109/ACC.2012.6314722; ACC full text read).
- See §1.5. The *control* relaxation stays lossless for nonlinear dynamics ẋ = f(t, x, u, g(u)) under total observability of [−∇_x f, ∇_u f] along all feasible trajectories.
- The relaxed problem is nonconvex and is solved globally with MILP on piecewise-affine dynamics.
- **Relevance:** the only nonlinear LCvx. It is **not** a convex relaxation, and it does not cover state-dependent control sets (gimbal relative to the body axis). It therefore poses no threat to the impossibility conjecture, and it is the natural "per-instance" positive analogue.

**[harris2013acc]** Harris, M. W., Açıkmeşe, B. "Lossless convexification for a class of optimal control problems with quadratic state constraints." *ACC 2013*, 3415–3420. DOI 10.1109/ACC.2013.6580359.

**[harris2013cdc]** Harris, M. W., Açıkmeşe, B. "Lossless convexification for a class of optimal control problems with linear state constraints." *CDC 2013*, 7113–7118. DOI 10.1109/CDC.2013.6761017.

**[harris2014automatica]** Harris, M. W., Açıkmeşe, B. "Lossless convexification of non-convex optimal control problems for state constrained linear systems." *Automatica* 50(9):2304–2311, 2014. DOI 10.1016/j.automatica.2014.06.008.
- These three papers are LCvx with persistently active affine or quadratic state constraints (Conditions 4–6).
- Linear dynamics are essential: the facet-sticking analysis uses linear geometric control theory and transmission zeros.

**[harris2014jgcd]** Harris, M. W., Açıkmeşe, B. "Minimum Time Rendezvous of Multiple Spacecraft Using Differential Drag." *JGCD* 37(2):365–373, 2014. DOI 10.2514/1.61505.
- LCvx-type relaxation for differential-drag rendezvous with linearized relative dynamics. Context.

**[harris2014jota]** Harris, M. W., Açıkmeşe, B. "Maximum Divert for Planetary Landing Using Convex Optimization." *JOTA* 162(3):975–995, 2014 (Crossref issue date 2013). DOI 10.1007/s10957-013-0501-7.
- Maximum-divert problem with velocity (quadratic) state constraints. LCvx is proven when the constraints are active.

**[kunhippurayil2021automatica]** Kunhippurayil, S., Harris, M. W., Jansson, O. "Lossless convexification of optimal control problems with annular control constraints." *Automatica* 133:109848, 2021. DOI 10.1016/j.automatica.2021.109848. *(abstract-level)*
- Note the authors: Jansson, not Açıkmeşe.
- Fixed-final-time annular constraints. Single-program LCvx holds under a sufficient condition; otherwise a sequence of convex programs is needed.

**[kunhippurayil2022ctt]** Kunhippurayil, S., Harris, M. W. "Strong observability as a sufficient condition for non-singularity and lossless convexification in optimal control with mixed constraints." *Control Theory Technol.* 20(4):475–487, 2022. DOI 10.1007/s11768-022-00115-w.

**[harris2021tac]** Harris, M. W. "Optimal Control on Disconnected Sets Using Extreme Point Relaxations and Normality Approximations." *IEEE TAC* 66(12):6063–6070, 2021. DOI 10.1109/TAC.2021.3059682. *(abstract-level)*
- Exact extreme-point relaxations under normality. Covers linear systems and nonlinear systems affine in the control.
- **Relevance:** with the attitude fixed, the 5DOF thrust set {T : ρ₁ ≤ ‖T‖ ≤ ρ₂, ∠(T, b(t)) ≤ δ} is exactly the kind of set this treats. It supports Thm C.

**[woodford2022tac]** Woodford, N. T., Harris, M. W. "Geometric Properties of Time-Optimal Controls With State Constraints Using Strong Observability." *IEEE TAC* 67(12):6881–6887, 2022. DOI 10.1109/TAC.2021.3134627. *(abstract-level)*
- Linear dynamics, state equality constraints, control inequality constraints. Strong observability yields geometric properties that enable exact convex relaxations.

**[malyuta2020ifac]** Malyuta, D., Açıkmeşe, B. "Lossless Convexification of Optimal Control Problems with Semi-continuous Inputs." *IFAC-PapersOnLine* 53(2):6843–6850, 2020. DOI 10.1016/j.ifacol.2020.12.341 (arXiv 1911.09013; read).
- See §1.6. Linear dynamics.

**[malyuta2019arxiv]** Malyuta, D., Szmuk, M., Açıkmeşe, B. "Lossless convexification of non-convex optimal control problems with disjoint semi-continuous inputs." arXiv:1902.02726, 2019.

**[malyuta2022csm]** Malyuta, D., Reynolds, T. P., Szmuk, M., Lew, T., Bonalli, R., Pavone, M., Açıkmeşe, B. "Convex Optimization for Trajectory Generation: A Tutorial on Generating Dynamically Feasible Trajectories Reliably and Efficiently." *IEEE Control Systems Magazine* 42(5):40–113, 2022. DOI 10.1109/MCS.2022.3187542 (arXiv 2106.09125; read).
- The canonical statement of LCvx Conditions 1–7 and Theorems 1–6 (§1).
- States explicitly that LCvx results assume linear dynamics apart from [blackmore2012scl], and that nonconvex state constraints are open.
- Introduces "embedded LCvx" (only the input bound or pointing cone convexified inside SCP).

**[malyuta2021survey]** Malyuta, D., Yu, Y., Elango, P., Açıkmeşe, B. "Advances in trajectory optimization for space vehicle control." *Annual Reviews in Control* 52:282–315, 2021. DOI 10.1016/j.arcontrol.2021.04.013 (arXiv 2108.02335; read).
- States the definition of lossless (§2.3) and gives the Kim–Mesbahi quaternion example.
- §3.1: "an inherent limitation of 3-DoF PDG is that the computed trajectory cannot incorporate attitude constraints other than those on the thrust vector, which serves as an attitude proxy". It says 6DOF work moved to SCP.

**[luo2026automatica]** Luo, D., Echigo, K., Açıkmeşe, B. "Revisiting Lossless Convexification: Theoretical guarantees for discrete-time optimal control problems." *Automatica* 183:112537, 2026. DOI 10.1016/j.automatica.2025.112537 (arXiv 2410.09748).
- See §1.6.
- **Relevance to numerics:** a discretized relaxed SOCP can violate the nonconvex constraints at up to n_x−1 nodes even in the linear 3DOF case. So numerical "losslessness checks" must allow for this.

**[luo2025lcsys]** Luo, D., Spada, F., Açıkmeşe, B. "Discrete-Time Lossless Convexification for Pointing Constraints." *IEEE Control Systems Letters* 9:246–251, 2025. DOI 10.1109/LCSYS.2025.3569751 (arXiv 2501.06931).

**[kiami2024arxiv]** Kiami, S. "Lossless Convexification for Linear Systems with Piecewise Linear Controls." arXiv:2411.18004 (v2 Sep 2025).
- See §1.6. The control-difference constraint acts on the thrust *vector*, not the attitude.

**[upadhyay2026arxiv]** Upadhyay, V., Ganguly, S., Chatterjee, D. "Exact Solutions to a Class of Constrained Optimal Control Problems via Lossless Convexification for Digital Control." arXiv:2607.12109, 2026 (abstract lists Automatica). Linear and 3DOF.

**[yang2024tac]** Yang, R., Liu, X. "Convex Hull Relaxation of Optimal Control Problems With General Nonconvex Control Constraints." *IEEE TAC* 69(6):4028–4034, 2024. DOI 10.1109/TAC.2023.3342061. *(abstract-level)*

**[yang2024jgcd]** Yang, R., Liu, X., Lin, D. "Exact Relaxation of Nonconvex Optimal Control Problems Based on Problem Reconstruction." *JGCD* 47(4):761–769, 2024. DOI 10.2514/1.G007788. (Abstract not retrieved.)

**[yang2025taes]** Yang, R., Wen, W., Yang, P., Zhao, Z., Huang, F. "Unified Sufficient Conditions for Exact Convex Relaxation of Nonconvex Optimal Control Problems." *IEEE TAES* 61(6):17924–17937, 2025. DOI 10.1109/TAES.2025.3607718. *(abstract-level)*

**[yang2022automatica]** Yang, R., Liu, X. "Reachable set computation of linear systems with nonconvex constraints via convex optimization." *Automatica* 146:110632, 2022. DOI 10.1016/j.automatica.2022.110632. *(secondary snippet)*
- For linear systems with nonconvex control constraints, the original and relaxed systems have equal reachable sets at any fixed t_f, and these sets are convex and compact. This is the Lyapunov/Aumann mechanism.
- **Relevance:** the exact *linear* counterpart of our Thm B. The reachable set is convex for linear dynamics and becomes nonconvex once the thrust axis is a rate-limited state.

**[arenasuribe2025arxiv]** Arenas-Uribe, F., Poonawala, H. A., Hoagg, J. B. "Geometric Conditions for Lossless Convexification in Linear Optimal Control with Discrete-Valued Inputs …" arXiv:2511.07711 (v3 May 2026).

**[liu2016jgcd, liu2016taes, liu2019jgcd]** Liu, X., Shen, Z., Lu, P., "Entry Trajectory Optimization by Second-Order Cone Programming", *JGCD* 39(2):227–241, 2016, DOI 10.2514/1.G001210. Also Liu, Shen, Lu, "Exact convex relaxation for optimal flight of aerodynamically controlled missiles", *IEEE TAES* 52(4):1881–1892, 2016, DOI 10.1109/TAES.2016.150741. Also Liu, X., "Fuel-Optimal Rocket Landing with Aerodynamic Controls", *JGCD* 42(1):65–77, 2019, DOI 10.2514/1.G003537.
- Exact relaxations of angle-type controls (bank angle; AoA plus thrust). These are proved by PMP inside SCP.
- The angle is a control without a rate limit. These are "embedded" exact relaxations, not convex programs.

---

## 3. Work involving attitude, thrust-direction rate, thrust rate, 5DOF, 6DOF

**[berning2023scitech]** Berning, A. W., Strohl, L., Bieniawski, S. R. "Lossless Convex Guidance for Lunar Powered Descent." AIAA SciTech 2023 Forum, AIAA 2023-2004. DOI 10.2514/6.2023-2004. **Full text NOT accessed (ARC 403).**
- Per [wang2023survey, §PDG], it is 3DOF minimum-fuel lunar PDG with maximum tilt rate, maximum tilt acceleration, maximum thrust ramp rate, inverse-square gravity and a minimum altitude. "The lossless convexification framework from [Açıkmeşe–Ploen] was used to relax the problem into an SOCP."
- **Relevance (highest priority to read):**
  - It is a *single uniform SOCP* with tilt-rate constraints. If it is lossless for a *full* thrust-direction rate limit, Thm A + Thm B predict this is impossible, at least for min-throttle + short horizon.
  - Likely resolutions: (i) "tilt rate" is the rate of the *tilt angle from vertical*, a scalar; (ii) the rate constraint is imposed on the thrust *vector* or acceleration (a convex surrogate), so losslessness is with respect to that surrogate; (iii) losslessness is claimed numerically, not proved.
  - (i) is especially important. If only the tilt *angle* rate is bounded, the azimuth can rotate arbitrarily fast. The rigidity step (4) of Thm B then fails, and chattering in azimuth reaches M in the closure. See §6 for the consequence.

**[strohl2022scitech]** Strohl, L., Doll, J., Fritz, M., Berning, A. W., White, S., Bieniawski, S. R. "Implementation of a Six Degree of Freedom Precision Lunar Landing Algorithm Using Dual Quaternion Representation." AIAA SciTech 2022, DOI 10.2514/6.2022-1831. *(title-level)*
- A 6DOF dual-quaternion landing algorithm, presumably SCP.

**[jung2025ijcas]** Jung, K.-W., Lee, S.-D., Jung, C.-G., Lee, C.-H. "Optimal Landing Guidance of Reusable Launch Vehicles With Dual-convex Optimization." *Int. J. Control Autom. Syst.* 23(8):2198–2218, 2025. DOI 10.1007/s12555-024-0628-3 (arXiv 2405.01264, titled "Model Predictive Guidance for Fuel-Optimal Landing of Reusable Launch Vehicles"; read).
- The tracking problem uses "a 5-DOF dynamics model, wherein the pitch, yaw, and engine throttle are augmented to the state variables" (first-order lags τ_θ, τ_T). Solved with SCP.
- **Relevance:** the only explicit 5-DOF powered-landing formulation found. It is not lossless.

**[szmuk2016gnc]** Szmuk, M., Açıkmeşe, B., Berning, A. W. "Successive Convexification for Fuel-Optimal Powered Landing with Aerodynamic Drag and Non-Convex Constraints." AIAA GNC 2016, DOI 10.2514/6.2016-0378.
- SCvx with thrust slew-rate (thrust-rate) constraints. LCvx handles only the minimum-thrust bound [malyuta2021survey].

**[szmuk2017gnc]** Szmuk, M., Eren, U., Açıkmeşe, B. "Successive Convexification for Mars 6-DoF Powered Descent Landing Guidance." AIAA GNC 2017, DOI 10.2514/6.2017-1500.
- First SCvx 6DOF PDG.

**[szmuk2018gnc]** Szmuk, M., Açıkmeşe, B. "Successive Convexification for 6-DoF Mars Rocket Powered Landing with Free-Final-Time." AIAA GNC 2018, DOI 10.2514/6.2018-0617.

**[szmuk2019scitech]** Szmuk, M., Reynolds, T., Açıkmeşe, B., Mesbahi, M., Carson, J. M. "Successive Convexification for 6-DoF Powered Descent Guidance with Compound State-Triggered Constraints." AIAA SciTech 2019, DOI 10.2514/6.2019-0926.

**[szmuk2020jgcd]** Szmuk, M., Reynolds, T. P., Açıkmeşe, B. "Successive Convexification for Real-Time Six-Degree-of-Freedom Powered Descent Guidance with State-Triggered Constraints." *JGCD* 43(8):1399–1413, 2020. DOI 10.2514/1.G004549 (arXiv 1811.10803; read).
- Model: rigid body with quaternion q_{B←I} ∈ S³ and angular velocity ω_B (Euler's equations). Gimbaled single engine.
- Constraints: 0 < T_min ≤ ‖T_B‖ ≤ T_max; gimbal cone cos δ_max ‖T_B‖ ≤ e₁·T_B; tilt via quaternion components; ‖ω_B‖₂ ≤ ω_max.
- Solved by SCvx with virtual control and trust region. No global or lossless guarantee.
- **Relevance:** the standard 6DOF model, essentially our M3/M4. The ‖ω‖ ≤ ω_max bound induces the M1 Lipschitz bound on the body axis.

**[reynolds2020dq]** Reynolds, T. P., Szmuk, M., Malyuta, D., Mesbahi, M., Açıkmeşe, B., Carson, J. M. "Dual Quaternion-Based Powered Descent Guidance with State-Triggered Constraints." *JGCD* 43(9):1584–1599, 2020. DOI 10.2514/1.G004536.
- Dual quaternions move nonconvexity from constraints into dynamics [malyuta2021survey]. Includes thrust-rate constraints. SCP.

**[reynolds2020ptr]** Reynolds, T., Malyuta, D., Mesbahi, M., Açıkmeşe, B., Carson, J. M. "A Real-Time Algorithm for Non-Convex Powered Descent Guidance." AIAA SciTech 2020, DOI 10.2514/6.2020-0844.
- Penalized trust region (PTR). Real-time 6DOF implementation details.

**[reynolds2020planar]** Reynolds, T. P., Mesbahi, M. "Optimal Planar Powered Descent with Independent Thrust and Torque." *JGCD* 43(7):1225–1231, 2020. DOI 10.2514/1.G004701. *(secondary: [malyuta2021survey])*
- Finds optimal solutions of a planar landing problem *including attitude dynamics*. Used to compare SCP with the global optimum.
- **Relevance:** the closest existing optimal-structure study of a "translation + attitude" landing problem. Its planar setting is a 2D analogue of M3 with independent torque. It should be read for its extremal structure: bang-bang torque arcs mean the attitude-rate limit is active, the Dubins-like regime.

**[malyuta2019scitech]** Malyuta, D., Reynolds, T., Szmuk, M., Mesbahi, M., Açıkmeşe, B., Carson, J. M. "Discretization Performance and Accuracy Analysis for the Rocket Powered Descent Guidance Problem." AIAA SciTech 2019, DOI 10.2514/6.2019-0925.

**[reynolds2019los]** Reynolds, T., Szmuk, M., Malyuta, D., Mesbahi, M., Açıkmeşe, B., Carson, J. M. "A State-Triggered Line of Sight Constraint for 6-DoF Powered Descent Guidance Problems." AIAA SciTech 2019, DOI 10.2514/6.2019-0924.

**[mao2016cdc]** Mao, Y., Szmuk, M., Açıkmeşe, B. "Successive convexification of non-convex optimal control problems and its convergence properties." *CDC 2016*, 3636–3641. DOI 10.1109/CDC.2016.7798816.
- SCvx convergence to KKT points, with local guarantees only.

**[mao2017ifac]** Mao, Y., Dueri, D., Szmuk, M., Açıkmeşe, B. "Successive Convexification of Non-Convex Optimal Control Problems with State Constraints." *IFAC-PapersOnLine* 50(1):4063–4069, 2017. DOI 10.1016/j.ifacol.2017.08.789.

**[elango2025automatica]** Elango, P., Luo, D., Kamath, A. G., Uzun, S., Kim, T., Açıkmeşe, B. "Continuous-time successive convexification for constrained trajectory optimization." *Automatica* 180:112464, 2025. DOI 10.1016/j.automatica.2025.112464.

**[elango2025scitech]** Elango, P., Vinod, A., Di Cairano, S., Weiss, A. "Continuous-Time Successive Convexification for Passively-Safe Six-Degree-of-Freedom Powered-Descent Guidance." AIAA SciTech 2025, DOI 10.2514/6.2025-1894.

**[uzun2025scitech]** Uzun, S., Açıkmeşe, B., Carson, J. M. "Sequential Convex Programming for 6-DoF Powered Descent Guidance With Continuous-time Compound State-Triggered Constraints." AIAA SciTech 2025, DOI 10.2514/6.2025-1895 (arXiv 2510.09610).

**[sagliano2024jgcd]** Sagliano, M., Seelbinder, D., Theil, S., Lu, P. "Six-Degree-of-Freedom Rocket Landing Optimization via Augmented Convex–Concave Decomposition." *JGCD* 47(1):20–35, 2024. DOI 10.2514/1.G007570 (SciTech 2023 version: DOI 10.2514/6.2023-2005). *(abstract read)*
- Augmented convex–concave decomposition for the nonlinear equality constraints of 6DOF landing. A sequential method, no exactness claim.

**[leemesbahi2012cdc, leemesbahi2017jgcd]** Lee, U., Mesbahi, M., "Dual quaternions, rigid body mechanics, and powered-descent guidance", *CDC 2012*, 3386–3391, DOI 10.1109/CDC.2012.6425996. Also "Constrained Autonomous Precision Landing via Dual Quaternions and Model Predictive Control", *JGCD* 40(2):292–308, 2017, DOI 10.2514/1.G001879.
- Certain coupled rotation–translation constraints are convex in dual-quaternion coordinates. MPC uses piecewise-affine dynamics [szmuk2020jgcd intro].

**[zhang2021jgcd]** Zhang, Y., Huang, J., Cui, H. "Trajectory Design via Convex Optimization for Six-Degree-of-Freedom Asteroid Powered Landing." *JGCD* 44(4):779–792, 2021. DOI 10.2514/1.G004434. *(title-level)*
- Chinese-group 6DOF convex (sequential) work.

**[nurre2025arxiv]** Nurre, N. P., Taheri, E. "Constrained Fuel and Time Optimal 6DOF Powered Descent Guidance Using Indirect Optimization." arXiv:2501.14173, 2025.
- Indirect method with interior penalties for tilt, gimbal and angular-velocity-magnitude constraints. Benchmarked against DIDO. Local.

**[lu2018jgcd]** Lu, P. "Propellant-Optimal Powered Descent Guidance." *JGCD* 41(4):813–826, 2018. DOI 10.2514/1.G003243.

**[lu2020jgcd]** Lu, P. "Theory of Fractional-Polynomial Powered Descent Guidance." *JGCD* 43(3):398–409, 2020. DOI 10.2514/1.G004556.

**[lucallan2023]** Lu, P., Callan, R. "Propellant-Optimal Powered Descent Guidance Revisited." AIAA SciTech 2023, DOI 10.2514/6.2023-2006.

**[lu2026scitech]** Lu, P. "Implementable Epsilon-Propellant-Optimal Powered Descent Guidance." AIAA SciTech 2026, DOI 10.2514/6.2026-0967.
- Lu's line is 3DOF analytic, semi-analytic or indirect guidance, not attitude-coupled LCvx. *(title/secondary-level)*

**[ito2023jgcd]** Ito, T., Sakai, S. "Optimal Powered Descent Guidance Under Thrust Pointing Constraint." *JGCD* 46(4):695–708, 2023. DOI 10.2514/1.G006727 (abstract read).
- 3D propellant-optimal PDG with an upward-pointing constraint. Active–inactive–active switching structure. 3DOF.

**[leparoux2022arxiv]** Leparoux, C., Hérissé, B., Jean, F. "Structure of optimal control for planetary landing with control and state constraints." arXiv:2204.06794.
- PMP structure (Max–Min–Max or Max–Singular–Max) with glide-slope and pointing constraints. 3DOF.

**[choi2023arxiv]** Choi, J., Kim, J.-H. "Powered Descent Guidance via First-Order Optimization with Expansive Projection." arXiv:2310.00397.
- A first-order alternative to LCvx. 3DOF.

**[acikmese2013flight / scharf2014aero]** GFOLD flight tests. Scharf, D. P., et al. "ADAPT demonstrations of onboard large-divert Guidance with a VTVL rocket." IEEE Aerospace 2014, DOI 10.1109/AERO.2014.6836462. The Açıkmeşe et al. 2013 AAS flight-test paper has no DOI and is UNVERIFIED (cited in [malyuta2022csm]).

**[kraisler2025arxiv]** Kraisler, S., Mesbahi, M., Açıkmeşe, B. "Intrinsic Successive Convexification: Trajectory Optimization on Smooth Manifolds." arXiv:2503.12711.
- SCP intrinsically on manifolds such as SO(3). Local.

**[lin2026rsc]** Lin, A., Adekola, F., Farkas, J., Melling, P., Marwah, N. "Evaluating Numerical Solving Methods for Optimal Powered Descent." 2026 AIAA Regional Student Conferences. DOI 10.2514/6.2026-112394.
- Crossref confirms the metadata: first author affiliated with Georgia Tech; no abstract deposited. The ARC page returned 403, and web search found no abstract or full text.
- **Content unknown.** I cannot say which methods it compares or what it concludes. Not used as evidence.

**Chinese-language and other work.** Searches surfaced Chinese-group work in English (BIT: Liu, Yang, Lin; HIT/BIT: Zhang, Huang, Cui). It also surfaced a 2026 *Chinese Space Science and Technology* paper (Zhang et al., vol. 46(3):143–156, DOI prefix 10.16708) using "variable-thrust lossless convex programming" with tilt-angle and glide-slope constraints. That paper is *title/snippet-level only and UNVERIFIED in content*. Nothing claimed exactness with attitude-rate constraints.

---

## 4. Mathematical background for the impossibility proof

### 4.1 Why LCvx works for linear systems: Lyapunov, Aumann, bang-bang

- **[lyapunov1940]** Liapounoff, A. A. "Sur les fonctions-vecteurs complètement additives." *Izv. Akad. Nauk SSSR Ser. Mat.* 4(6):465–478, 1940. mathnet.ru im3907 (no DOI).
  - The range of a nonatomic finite-dimensional vector measure is compact and convex.
- **[aumann1965]** Aumann, R. J. "Integrals of set-valued functions." *JMAA* 12(1):1–12, 1965. DOI 10.1016/0022-247X(65)90049-1.
  - ∫F = ∫conv F for measurable set-valued F on a nonatomic space. Hence the reachable set of ẋ = Ax + Bu, u ∈ U (U possibly nonconvex), is convex and equals that of the relaxed system u ∈ conv U.
  - This is the mechanism behind LCvx. The relaxed and original *reachable sets* coincide, and PMP then shows *optimal* relaxed controls are extreme points.
- **[halkin1964]** Halkin, H. "A Generalization of LaSalle's 'Bang-Bang' Principle." *SIAM J. Control* 2(2):199–202, 1964. DOI 10.1137/0302018.
- **[lasalle1960]** LaSalle, J. P. "The 'bang-bang' principle." *IFAC Proc.* 1(1):503–507, 1960. DOI 10.1016/S1474-6670(17)70095-X.
- **[hermeslasalle1969]** Hermes, H., LaSalle, J. P. *Functional Analysis and Time Optimal Control.* Academic Press, Math. in Sci. & Eng. vol. 56, 1969 (Crossref chapter DOIs, e.g. 10.1016/S0076-5392(08)60051-X).
- **[neustadt1963]** Neustadt, L. W. "The existence of optimal controls in the absence of convexity conditions." *JMAA* 7(1):110–117, 1963. DOI 10.1016/0022-247X(63)90081-7.
- **[hermes1967]** Hermes, H. "On the Closure and Convexity of Attainable Sets in Finite and Infinite Dimensions." *SIAM J. Control* 5(3):409–417, 1967. DOI 10.1137/0305025 (errata 10.1137/0306037).
  - Attainable sets of *nonlinear* systems are generally not convex. Convexity results need linear structure.
- **[yang2022automatica]** (see §2): linear systems with nonconvex control constraints have convex reachable sets equal to the relaxed ones.

**Relevance.** In our model the thrust direction is bound to the state b(t), which evolves on S² with bounded speed. The map control ↦ ∫ a d ds is then no longer linear in a "free" control. The Lyapunov/Aumann argument fails, and the reachable set R can be nonconvex (Thm B). In the limit ω_max → ∞ the axis is free, and R is the 3DOF set, which is convex by Aumann (consistent with math/00 remark).

### 4.2 Dubins-car reachable sets

- **[dubins1957]** Dubins, L. E. "On Curves of Minimal Length with a Constraint on Average Curvature, and with Prescribed Initial and Terminal Positions and Tangents." *Amer. J. Math.* 79(3):497–516, 1957. DOI 10.2307/2372560.
- **[cockayne1975]** Cockayne, E. J., Hall, G. W. C. "Plane Motion of a Particle Subject to Curvature Constraints." *SIAM J. Control* 13(1):197–220, 1975. DOI 10.1137/0313012.
  - The reachable set at time t of the unit-speed, curvature-bounded planar particle (free terminal heading). Its boundary is made of CS- and CC-type arcs *(secondary: [bae2025automatica])*.
- **[sussmann1995]** Sussmann, H. J. "Shortest 3-dimensional paths with a prescribed curvature bound." *CDC 1995*, vol. 4, 3306–3312. DOI 10.1109/CDC.1995.478997.
  - Structure of minimum-time 3D curvature-bounded paths: helicoidal arcs and CSC/CCC.
- **[bae2025automatica]** Bae, J., Bai, J. H., Lee, B.-Y., Lee, J.-Y., Lee, C.-H. "On the reachability of 3-dimensional paths with a prescribed curvature bound." *Automatica* 178:112359, 2025. DOI 10.1016/j.automatica.2025.112359 (arXiv 2403.18707; abstract and parts of HTML read).
  - Every boundary point of the reachable set *with* terminal direction is reached by H, CSC or CCC curves or their subsegments.
  - The **position-only** reachable set "is simply a solid of revolution of its two-dimensional counterpart, the Dubins car".
  - The boundary is reached by CS, CC or their subsegments, with the CC curves planar (Thm 9). Unit speed, curvature ≤ 1, length exactly t_f.
  - The paper does **not** discuss convexity.
  - **Relevance:** with δ = 0 (no gimbal), constant a, and the velocity increment R = ∫ a d ds, d is the unit tangent of a curve whose curvature is bounded by ω/a. So R is exactly the Bae et al. set (scaled). The extreme arcs P_u of math/00 §4 are their planar "C" arcs.
  - The midpoint argument is essentially the planar fact below, revolved. Gimbal δ > 0 and throttle variation are extensions this paper does not cover.
- **Planar nonconvexity, elementary** (my derivation, consistent with the Cockayne–Hall boundary structure; for verifier use, not a citation):
  - Take a unit-speed curve with heading |ψ(s)| ≤ ωs (from ψ(0) = 0 and |ψ̇| ≤ ω), t < π/ω.
  - Then x(t) = ∫cos ψ ≥ sin(ωt)/ω, with equality iff |ψ(s)| = ωs a.e. Continuity then forces a single-sided full turn, so y(t) ≠ 0.
  - Hence the midpoint (sin(ωt)/ω, 0) of the two full-turn endpoints is unreachable. The fixed-time Dubins reachable set is nonconvex for every t ∈ (0, π/ω).
- **[patsko2023jcssi]** Patsko, V. S., Fedotov, A. A. "Three-Dimensional Reachability Set For a Dubins Car: Reduction of the General Case of Rotation Constraints to the Canonical Case." *J. Comput. Syst. Sci. Int.* 62(3):445–468, 2023. DOI 10.1134/S1064230723030115.
- **[fedotov2011intech]** Fedotov, A., Patsko, V., Turova, V. "Reachable Sets for Simple Models of Car Motion." In *Recent Advances in Mobile Robotics*, InTech, 2011. DOI 10.5772/26278.
  - Numerical and analytic reachable sets for Dubins and Reeds–Shepp cars, which show visibly nonconvex shapes *(title-level)*.
- **[patsko2019med]** Patsko, V. S., Fedotov, A. A. "Reachable set for Dubins car and its application to observation problem with incomplete information." *MED 2019*, 489–494. DOI 10.1109/MED.2019.8798511.
- Patsko, Pyatko, Fedotov 2003, "Three-dimensional reachability set for a nonlinear control system", *J. Comput. Syst. Sci. Int.* 42(3). Cited by [bae2025automatica]; **UNVERIFIED** (no DOI found).

### 4.3 Small-time convexity results (potential threat to "nonconvexity for small t_f")

- **[polyak2001]** Polyak, B. T. "Convexity of Nonlinear Image of a Small Ball with Applications to Optimization." *Set-Valued Analysis* 9(1–2):159–168, 2001. DOI 10.1023/A:1011287523150.
  - The image of a sufficiently small ball under a C^{1,1} map with surjective derivative is convex.
  - Applied to reachable sets under **L²-bounded** controls in later work. Polyak 2004, *Dyn. Contin. Discrete Impuls. Syst.*, is **UNVERIFIED**.
- **[gusev2019aip]** Gusev, M. I., Osipov, I. O. "On convexity of small-time reachable sets of nonlinear control systems." *AIP Conf. Proc.* 2164:060007, 2019. DOI 10.1063/1.5130809. *(title-level)*
  - Related work by the same authors treats small L² balls and Gramian conditions *(secondary)*.
- **[azhmyakov2007ecc]** Azhmyakov, V., Flockerzi, D., Raisch, J. "On convexity of reachable sets for nonlinear control systems." *ECC 2007*, 3275–3280. DOI 10.23919/ECC.2007.7068803. A later counterexample for the closed-loop variant is reported *(secondary)*.
- **Relevance.** These convexity results need *small integral (L²) control budgets*, with controls near zero and a linearization that is controllable around zero control. Our setting has **geometric pointwise bounds with a nonzero minimum throttle**: the control is far from the origin of a convex set, with |a| ≥ a₁ > 0. Small-time convexity therefore does not apply. This is exactly why ρ₁ > 0 matters in Thm B.
  - The adversary may test whether, with ρ₁ = 0 or with a small L² rate budget, convexity reappears.

### 4.4 Convexity of value or feasibility functions of parametric convex programs

- **Projection fact (Thm A).** If C ⊆ Θ × Y is convex, proj_Θ C is convex, and v(θ) = inf{f(θ, y) : (θ, y) ∈ C} is convex when f is jointly convex.
  - Standard; see Fiacco–Kyparisis **[fiacco1986jota]**, "Convexity and concavity properties of the optimal value function in parametric nonlinear programming", *JOTA* 48(1):95–126, 1986, DOI 10.1007/BF00938592.
  - Also Kyparisis–Fiacco 1987 *Math. Prog.* 39(3):285–304, DOI 10.1007/BF02592078 (generalized convexity).
- **Corollary we can use.** For a uniform lossless relaxation with an objective jointly convex in (θ, y), both the feasible set F_tf **and** the optimal-cost function θ ↦ J*(θ) of the original problem must be convex. Nonconvexity of either refutes uniform losslessness. This gives a second, cost-based route to impossibility even where F happens to be convex.

### 4.5 Relaxation, occupation measures, infimum gaps (requested by orchestrator for red-teamers)

- **[warga1962jmaa]** Warga, J. "Relaxed variational problems." *JMAA* 4(1):111–128, 1962. DOI 10.1016/0022-247X(62)90033-1.
- **[filippov1967]** Filippov, A. F. "Classical Solutions of Differential Equations with Multi-Valued Right-Hand Side." *SIAM J. Control* 5(4):609–621, 1967. DOI 10.1137/0305040. Together with Ważewski (1961–62, Bull. Acad. Polon. Sci.; **UNVERIFIED**, no DOI):
  - **Filippov–Ważewski relaxation theorem.** For Lipschitz F with compact values, trajectories of ẋ ∈ conv F(x) are uniform limits of trajectories of ẋ ∈ F(x). So the relaxed reachable set is the closure of the original one.
  - Textbook source: Vinter, *Optimal Control* **[vinter2000book]** (Birkhäuser; Crossref chapter DOIs under 10.1007/978-0-8176-8086-2).
  - **Relevance:** for M1 as a differential inclusion in (r, v, b), convexifying the velocity set (pointwise LCvx relaxation at the current b) changes the reachable set only by closure. It cannot convexify R. Nonconvexity of F_tf survives *any* pointwise convexification of the control set, which is an important complement to Thm A.
- **[palladino2014sicon]** Palladino, M., Vinter, R. B. "Minimizers That Are Not Also Relaxed Minimizers." *SICON* 52(4):2164–2179, 2014. DOI 10.1137/130909627.
- **[palladino2015dcds]** Palladino, M., Vinter, R. B. "When are minimizing controls also minimizing relaxed controls?" *DCDS-A* 35(9):4573–4592, 2015. DOI 10.3934/dcds.2015.35.4573.
  - An infimum gap between the original and relaxed problems implies the PMP holds only in abnormal form. Normality implies no gap.
  - This is the endpoint-constrained subtlety in Filippov–Ważewski: exact endpoint constraints can create a gap.
- **[lewisvinter1980]** Lewis, R. M., Vinter, R. B. "Relaxation of optimal control problems to equivalent convex programs." *JMAA* 74(2):475–493, 1980. DOI 10.1016/0022-247X(80)90143-2.
- **[vinter1993sicon]** Vinter, R. "Convex Duality and Nonlinear Optimal Control." *SICON* 31(2):518–538, 1993. DOI 10.1137/0331024.
  - The weak (occupation-measure) LP formulation for differential inclusions and its duality with HJB subsolutions.
- **[lasserre2008sicon]** Lasserre, J. B., Henrion, D., Prieur, C., Trélat, E. "Nonlinear Optimal Control via Occupation Measures and LMI-Relaxations." *SICON* 47(4):1643–1666, 2008. DOI 10.1137/070685051 (arXiv math/0703377; read).
  - Theorem 2.3: the LP P is solvable with no duality gap. It equals the OCP value if f(t, x, U) is convex for all (t, x) and an associated cost is convex (attributed to Vinter).
  - Theorem 3.6: the moment-SOS LMI values increase to min P (Putinar condition).
  - The initial condition enters as δ_{(0, x₀)} on the right-hand side of the Liouville constraint.
- **[gaitsgory2009sicon]** Gaitsgory, V., Quincampoix, M. *SICON* 48(4):2480–2512, 2009. DOI 10.1137/070696209.
- **[henrionkorda2014tac]** Henrion, D., Korda, M. "Convex Computation of the Region of Attraction of Polynomial Control Systems." *IEEE TAC* 59(2):297–312, 2014. DOI 10.1109/TAC.2013.2283095.
  - An infinite-dimensional LP over measures whose optimum characterizes the backward reachable set (ROA) of initial states. Moment-SOS gives converging *outer approximations*.
  - **Relevance:** the existing convex machinery for sets like F_tf. It yields convex outer bounds, never exact convex descriptions, of nonconvex sets.
- **[korda2014sicon]** Korda, M., Henrion, D., Jones, C. N. *SICON* 52(5):2944–2969, 2014. DOI 10.1137/130914565.

### 4.6 Convex hulls of rotation groups and spheres (for lifted relaxations)

- **[sanyal2011orbitopes]** Sanyal, R., Sottile, F., Sturmfels, B. "Orbitopes." *Mathematika* 57(2):275–314, 2011. DOI 10.1112/S002557931100132X.
- **[saunderson2015siopt]** Saunderson, J., Parrilo, P. A., Willsky, A. S. "Semidefinite Descriptions of the Convex Hull of Rotation Matrices." *SIAM J. Optim.* 25(3):1314–1343, 2015. DOI 10.1137/14096339X.
  - conv SO(n) is doubly spectrahedral with explicit minimum-size representations. For n = 3 it is a 4×4 LMI in the quaternion outer product qqᵀ.
- **[kim2004tac]** Kim, Y., Mesbahi, M. "Quadratically Constrained Attitude Control via Semidefinite Programming." *IEEE TAC* 49(5):731–735, 2004. DOI 10.1109/TAC.2004.825959.
- **[kim2010taes]** Kim, Y., Mesbahi, M., Singh, G., Hadaegh, F. Y. "On the Convex Parameterization of Constrained Spacecraft Reorientation." *IEEE TAES* 46(3):1097–1109, 2010. DOI 10.1109/TAES.2010.5545176.
- **[sun2015gnc]** Sun, C., Dai, R. "Spacecraft Attitude Control under Constrained Zones via Quadratically Constrained Quadratic Programming." AIAA GNC 2015, DOI 10.2514/6.2015-2010. *(title-level)*
- **[tam2016actaastro]** Tam, M., Lightsey, E. G. "Constrained spacecraft reorientation using mixed integer convex programming." *Acta Astronautica* 127:31–40, 2016. DOI 10.1016/j.actaastro.2016.04.003.
- **Relevance.** Lifting b ∈ S² to its convex hull (the unit ball), or R ∈ SO(3) to conv SO(3), gives a convex set. But the rate constraint ⟨b(s), b(s')⟩ ≥ cos(ω|s−s'|) is not jointly convex in the lifted variables unless it is lifted to second moments (Gram/PSD lifts).
  - Even then, by Thm A, any lift in which (r₀, v₀) enter jointly convexly cannot be lossless if F_tf is nonconvex. Lifts are relevant only to *non-uniform* (per-instance) or *approximate* relaxations.

### 4.7 Existing "impossibility of lossless convexification" results

None found. Closest:
- The tight counterexample in discrete-time LCvx [luo2026automatica].
- The remark in [acikmese2013tcst].
- The open problem of nonconvex state constraints [malyuta2022csm].
- In optimal power flow, SDP relaxations are known to be inexact in general, with counterexamples and NP-hardness (found by web search; not a control result; not catalogued).

---

## 5. Gaps and things I could not verify

1. **Berning–Strohl–Bieniawski 2023:** the full text is needed to see how "tilt rate" is defined and whether losslessness with rate constraints is proved. Top priority for anyone with ARC access.
2. **Lin et al. 2026** (DOI 10.2514/6.2026-112394): only metadata is available.
3. **Abstract-level only:** Reynolds–Mesbahi 2020 (planar optimal), Harris 2021 TAC, Kunhippurayil 2021, Woodford–Harris 2022, Yang–Liu 2024 TAC and JGCD, Yang et al. 2025 TAES.
4. **UNVERIFIED (no DOI found):** Ważewski 1961/62; Patsko–Pyatko–Fedotov 2003; Polyak 2004; Harris PhD thesis (UT Austin, 2014, cited in [malyuta2022csm]); the GFOLD 2013 AAS flight-test paper.
5. **Chinese-language journals:** no full texts accessed. No claim of attitude-rate LCvx surfaced in English abstracts or titles.

## 6. Implications for the project (my assessment, not cited fact)

- **Definition of "uniform".** In all literature LCvx results with free t_f, the convex program is solved per instance, and often as a *sequence* (t_f search, two-stage priorities).
  - At **fixed t_f**, the standard 3DOF SOCP is uniform in our sense: r₀, v₀ enter as affine equality constraints. Thm A applies to it, and it is consistent because the 3DOF F_tf is convex (Aumann).
  - Occupation-measure LPs [lasserre2008sicon; henrionkorda2014tac] are convex in the measures for each θ, but θ enters through δ_θ, which is nonlinear in θ. They are *not* uniform, so they evade Thm A. Their moment truncations are only approximate, and for M1 even the infinite LP only attains the *relaxed* value. That value equals the original value under normality ([palladino2014sicon]), but the extracted solution may be a chattering measure, not a classical trajectory.
  - So the impossibility statement should be phrased explicitly as **joint convexity in (θ, y)**, and per-instance relaxations should be discussed separately.
- **Which rate limit.** The model M1 bounds the full angular rate of the body axis (‖ω_⊥‖ ≤ ω_max, as in [szmuk2020jgcd], ‖ω_B‖ ≤ ω_max).
  - A bound only on the *tilt angle from vertical* (possibly what [berning2023scitech] calls tilt rate) leaves the azimuth free. Step (4) of Thm B fails, and M should lie in the closure of R.
  - So "LCvx with tilt-rate limits" may be genuinely possible for that weaker constraint without contradicting Thm B. Numerics should test this case.
- **Filippov–Ważewski complements Thm A.** No *pointwise* convexification of the (state-dependent) control set changes the closure of the reachable set. The nonconvexity in Thm B is intrinsic to the state-space geometry (b ∈ S², rate-limited), not to the control set.
- **Positive route (Thm C).** Supported by [acikmese2013tcst, Lemma 3], [harris2021tac] (normality-based exact extreme-point relaxations with time-varying sets) and [malyuta2020ifac]. A time-varying cone axis b(t) needs the non-degeneracy condition "primer vector p(t) ≠ −α b(t) on a positive-measure set" to replace the analytic Lemma 2 of [acikmese2013tcst].
- **Cost-based route.** Even if F_tf were convex in some regime (large t_f), a uniform lossless relaxation whose objective is jointly convex in (θ, y) also forces θ ↦ J*(θ) to be convex [fiacco1986jota]. A nonconvex fuel-optimal cost in (r₀, v₀) would also refute uniform LCvx.

---

## 7. Addendum, 2026-11-10: differential flatness and spline planning

Added for the sound single convex program of `math/10-landing-proof.md` (paper Section 4.5). Every DOI below was resolved
against the Crossref API on 2026-11-10; title, authors, venue, volume and pages matched. **All summaries are abstract-level
or secondary**: IEEE Xplore returned an empty page and ScienceDirect returned HTTP 403, so no full text was read.

**[fliess1995ijc]** Fliess, M., Lévine, J., Martin, P., Rouchon, P. "Flatness and defect of non-linear systems: introductory
theory and examples." *Int. J. Control* 61(6):1327–1361, 1995. DOI 10.1080/00207179508921959.
- The standard reference for differential flatness: a system is flat if its state and input are functions of an output and
  finitely many of its derivatives.

**[martin1996automatica]** Martin, P., Devasia, S., Paden, B. "A different look at output tracking: control of a VTOL aircraft."
*Automatica* 32(1):101–107, 1996. DOI 10.1016/0005-1098(95)00099-2. *(abstract-level)*
- Planar VTOL aircraft. A flat output is found and related to the Huygens centre of oscillation. The centre-of-percussion
  point y = r + (J_t/(mL)) b of this project (claim FLAT) is the same point for the 3-D gimballed rigid body.
- **Relevance:** the flatness of the planar thrust-vectored body is known. This project's claim is not the identity itself.

**[mellinger2011icra]** Mellinger, D., Kumar, V. "Minimum snap trajectory generation and control for quadrotors." ICRA 2011,
pp. 2520–2525. DOI 10.1109/ICRA.2011.5980409.
- Planning polynomial flat outputs for a multirotor by a quadratic program; actuator limits are not guaranteed between nodes.

**[desiderio2013tcst]** Desiderio, D., Lovera, M. "Guidance and control for planetary landing: flatness-based approach."
*IEEE Trans. Control Syst. Technol.* 21(4):1280–1294, 2013. DOI 10.1109/TCST.2012.2202664. *(abstract-level; search summary)*
- Flatness of the descent equations is used for trajectory generation and feedforward tracking in planetary landing. A search
  summary describes an altitude-domain model and notes that the nonzero lower thrust bound makes the problem nonconvex.
- **Relevance:** flatness-based landing guidance exists. From the abstract-level information it is not a single convex program
  with a minimum-throttle guarantee for a gimballed rigid body. Full text needed to be sure.

**[vanloock2015acc]** Van Loock, W., Pipeleers, G., Swevers, J. "Optimal motion planning for differentially flat systems with
guaranteed constraint satisfaction." ACC 2015, pp. 4245–4250. DOI 10.1109/ACC.2015.7171996. *(abstract-level)*
- Flat outputs parametrized as B-splines, with constraints imposed through the spline coefficients so that they hold at all
  times and not only at grid points.
- **Relevance:** the control-polygon device of Lemma 5 in `math/10` is this known technique.

**[freire2023tcst]** Freire, V., Xu, X. "Flatness-based quadcopter trajectory planning and tracking with continuous-time
safety guarantees." *IEEE Transactions on Control Systems Technology* 31(6):2319–2334, 2023. DOI 10.1109/TCST.2023.3250954;
arXiv:2111.00951. *(preprint read in full, 2026-11-11; pointed out by an external reviewer of the AIAA draft)*
- Quadcopter with thrust and body rates as inputs, constant mass, yaw fixed. The position is planned as a B-spline and one SOCP
  is solved; constraints on "virtual control points" hold in continuous time by the convex-hull property (their Theorem 1).
- Tilt limit: a second-order cone on the acceleration (their Lemma 3). Upper thrust: a ball on acceleration plus gravity. Lower
  thrust: imposed on the vertical acceleration only, which they note sacrifices part of the feasible region (Lemma 5, Remark 2).
  Body rates: a bound on the jerk divided by a per-segment lower bound on thrust (Lemma 6).
- **Relevance: the closest prior work found, and it was missing from the first drafts.** It already has flatness, B-splines, a
  single SOCP, continuous-time thrust and attitude guarantees, and the vertical-component lower thrust bound that our program
  also uses. It means "flatness + splines + one SOCP" cannot be claimed as new.
- **What it does not contain** (our contribution, as now stated in the papers): a vehicle whose torque comes from deflecting
  the thrust, hence the centre-of-percussion output; the gimbal-angle limit, which involves the fourth derivative of the flat
  output relative to the thrust; the centripetal and lateral terms in the thrust magnitude; and force limits with depleting mass.

**[wang2026asr]** Wang, C., Chen, Z. "B-spline-based convex programming for fuel-optimal powered descent guidance."
*Advances in Space Research* 78(4):3919–3934, 2026. DOI 10.1016/j.asr.2026.06.014. *(abstract-level; search summary)*
- B-spline parametrization inside sequential convex programming for fuel-optimal powered descent; only part of the state is
  parametrized and the rest follows from the dynamics.
- **Relevance:** the closest recent powered-descent work found that uses B-splines. It iterates; no soundness claim was found.

**What was searched and not found.** Extended web searches (2026-11-10) for flatness, thrust-vector control, centre of
percussion or oscillation, rocket landing, convex optimization and B-spline convex-hull constraints, in combination, returned
no paper that (i) uses the centre-of-percussion flat output of a gimballed lander for descent planning as one convex program,
or (ii) proves that such a program returns only trajectories that meet the minimum-throttle and gimbal limits. This is a
search result, not a proof of novelty: AIAA ARC and several publishers were not searchable in full text, and the
flatness-based landing papers above were not read in full.

**Effect on §0.** The verdict of §0 is unchanged: no LCvx theorem and no impossibility theorem for attitude-rate-limited
descent was found. The addendum concerns sound convex restrictions, which §0 did not address.
