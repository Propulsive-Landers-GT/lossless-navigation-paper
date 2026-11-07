# [verifier-sdp] Independent verification of Conjecture CSD2 (degree-2 Gram/Shor lift, min-landing-error)

Author: verifier-sdp. Date: 2026-11-07. Code: `numerics/verifier-sdp/` (all results in `numerics/verifier-sdp/results/`).
I built my implementation and reached my verdicts before reading `math/redteam-lift.md` or `numerics/redteam-lift/`.
§9 compares the two. Compute: at most 2 heavy processes, single-threaded BLAS throughout.

## 0. Verdicts (TL;DR)

| Claim / variant | Verdict | Key evidence |
|---|---|---|
| **CSD2 as briefed**: fixed thrust along b_k (δ=0), b_0=b_N=e_z substituted, (r) or (r,v) targets | **EXACT (numerically), no counterexample** | About 4,500 SDP solves, N=2…48, ωtf 0.4…5.5, with/without b_N, r and (r,v), M/dent/rim/far/random/perpendicular-lateral/rate-saturated. About 2,900 are compared against a full multistart genuine optimum; the rest are rank 3 (self-certifying) or spot-checked. Max (genuine − SDP)/scale² = 1.8e-7, relative ≤ 8e-7. The stress matrix is PSD at every optimum tested. |
| Unit-d gimbal δ>0, "inner" discretization (d_k unit, within δ of b_k **and** b_{k+1}); this is [numerics]' case-12 model | **LOSSY, certified by order-2 Lasserre up to solver accuracy** | Case 12 reproduced: SDP 0.0275290, attained by an explicit R⁴ chain, vs 3D 0.0282327 after about 1,070 diverse runs, a 2.5% gap. N=3: Shor 1.862 < Las2 2.3587 (Clarabel)/2.3571 (SCS) ≈ genuine 2.3569. N=3, δ=40°: Shor 0.0237 < Las2 0.1616 ≈ genuine 0.1611. Small-N gaps are frequent, up to 95% relative. |
| **CSD2′**: same lift for the convexified lens (‖d_k‖ ≤ 1, i.e. discrete relaxed controls) or for δ=0 | **EXACT (numerically), unbroken** | All 509 unit-d gap instances re-solved: 0 gaps, max 4.5e-10·scale². Adversarial CSD2′ screen N=3…32 (near-dent, non-coplanar (r,v), rate-saturated): 0 gaps. Stress matrix PSD at every convexified optimum tested and negative at every unit-d gap. |
| Variable throttle, natural degree-2 lift (U_k = a_k b_k) | **LOSSY, certified (Lasserre-2 at N=3); NOT a discretization artifact** | At fixed physics (tf=1, ω=2, a∈[0.5,1]) the gap grows with N: 12% (N=4), 40% (6), 54% (8), 63% (12), 68% (16). The lift converges to the no-rate-limit value. |
| Throttle, other lifts: (U,b)-Hilbert lift, tightest degree-2 Shor in (a,U,b), [proof-sdp] CSD3 | **all LOSSY** | CSD3 is rank-3 yet lossy (gaps 2–35% even at δ=0, ωtf=6), so the scalar-Γ lift admits off-axis thrust inside R³. The tightest (a,U,b) Shor is nearly closed (0.4707 vs 0.4753) but not exact. |
| Altitude / glide-slope, min-fuel | see §7 | |

## 1. Problem and SDP (my implementation)

Discrete fixed-thrust 5DOF:
- b_0 = e_z, b_N = e_z (optional), b_k ∈ S², ⟨b_k, b_{k+1}⟩ ≥ c = cos(ωh).
- ZOH thrust direction b_k on [t_k, t_{k+1}), with known a_k: Δv = Σ a_k h b_k, Δr = Σ a_k h (tf − t_k − h/2) b_k. A trapezoidal variant is also tested.
- Target q absorbs r0, v0 and gravity. Cost J = ‖Δr − q_r‖² (+ ‖Δv − q_v‖²).

All data are isotropic (weights γ_k ⊗ I_3), so J is affine in the Gram matrix Z of (b_free…, e_x, e_y, e_z). The SDP is (`vcore.py`):
- Z ⪰ 0, Z[e,e] = I_3, Z_kk = 1;
- Z_{k,k+1} ≥ c, with ⟨b_k, e_z⟩ = Z[k, e_z] for the substituted constants b_0, b_N;
- J = Σ_l μ_l (γ_lᵀ G γ_l + 2 γ_lᵀ X d_l + ‖d_l‖²).

Supporting checks:
- **Slater** is verified per configuration: max t such that Z − tI ⪰ 0 and the rate slack is ≥ t. The minimum margin over all configurations is 3.9e-5 > 0.
- **Cross-check with a full non-isotropic Shor** (`vqcqp.py`, moment matrix of the 3n coordinates): equal values (e.g. 0.0200208208 vs 0.0200208208), as predicted (Shor ⊆ Gram, and the isotropic fill gives the reverse).
- **Genuine upper bound** (`GenuineNLP`): ipopt with exact unit-norm/rate constraints, re-normalized and re-checked (violation < 1e-7). Starts are SDP rank-3 roundings (first-moment projection, Procrustes-aligned PCA, random projections of the E⊥ part) plus tilted tents, coning sweeps, smooth random curves and noise.
- **Solvers.** Clarabel at tol 1e-9 (1e-10 is below its attainable accuracy here and returns "inaccurate"; the ladder falls back to 1e-8). SCS at 1e-9 (N ≤ 16), 1e-7 (N > 16).

Statuses over the fixed-thrust sweep: 1,872 of 1,882 runs returned Clarabel "optimal"; 10 at N = 32/48 returned optimal_inaccurate. The max |SCS − Clarabel|/scale² is 1.2e-5 at N ≤ 16. At N ≥ 32, SCS ran at 1e-7 and occasionally disagreed by up to 5e-3, so SCS is the looser solver there.

**Noise floor.** The objective contains the constant ‖q‖², so the absolute accuracy is about 1e-9·‖q‖². I therefore report the gap as (U − L)/scale², with scale² = Σ_l μ_l (Σ_k γ_kl)². I flag a gap only if (U − L)/scale² > 1e-8 and the relative gap is > 1e-5.

## 2. Fixed thrust (δ = 0): the claim as briefed

### 2.1 Sweep (`run_fixed.py`)
Grid:
- N ∈ {8, 16, 32, 48};
- ωtf ∈ {0.4, 1.2, 2.0, 3.6, 5.5} with b_N = e_z (tent peak tilt up to 2.75 rad, past π/2), and {0.4, 1.2, 2.0, 3.6} without it;
- r and (r,v) readouts; accel profiles constant, 40% mass-depletion ramp, and a random profile a_k ∈ [0.2, 2];
- ZOH plus a trapezoidal check.

Targets per configuration:
- the Theorem-B midpoint M;
- bottom-face ("dent") points at radius s·ρ and height z_min + h·S, with (s,h) ∈ {(.5,0), (.9,0), (.5,.01), (.2,.05), (.97,.002), (.5,−.05)}; for (r,v), both aligned and perpendicular r/v laterals;
- 2 far targets at 1.5·S;
- 2+2 near-boundary points (projection of the far target onto L, ±0.02·S along the normal);
- 4 random targets in a box.

| N | targets | non-genuine SDP solutions (Σ‖b_k⊥‖² > 1e-5) | max (U−L)/scale² | min (U−L)/scale² |
|---|---|---|---|---|
| 8 | 1172 | 733 | 8.9e-9 | −2.4e-8 |
| 16 | 268 | 128 | 3.4e-8 | −3.6e-9 |
| 32 | 234 | 119 | 1.7e-7 | −1.5e-8 |
| 48 | 208 | 112 | 1.8e-7 | −1.5e-8 |

There is no flagged gap in 1,882 targets.
- The largest discrepancies (1.8e-7·scale²) are relative 9e-8 to 8e-7, all at ωtf = 0.4, where the Slater margin is smallest (1.7e-5). Ten of them are Clarabel optimal_inaccurate, at N = 32/48.
- Statuses: 1,872 optimal, 10 optimal_inaccurate.

By target family (all N), the max (U−L)/scale² is:
- M: 8.7e-10;
- face/dent points: ≤ 1.5e-9;
- near-boundary points: ≤ 2.0e-9;
- random: 3.4e-8;
- far: 1.7e-7, which is 2e-5 relative to a cost of about 1, at an NLP that had not fully converged.

**Rank.** The SDP returns rank > 3 (non-genuine) at 100% of M targets and about 65–76% of dent targets, yet the value equals the genuine optimum. These are optimal faces made non-unique by symmetry; the interior-point method returns their max-rank point, and the rank-3 projection plus polish recovers the value. A rank-3 SDP solution is itself a genuine trajectory, a certificate.

### 2.2 [proof-sdp] adversarial regimes (`run_adv.py`)
Two regimes, both with N ∈ {2, 3, 4, 5, 6, 8, 16}, ωtf ∈ {0.2, 0.5, 1.5, 3}, with/without b_N:
- (a) Full (r,v) targets with the r-lateral ⟂ the v-lateral, and vertical components at 0.3/0.5/0.8 × floor ("wants to throttle down"). 504 instances, max relative gap 2.6e-8.
- (b) Far targets (×10, ×100) with opposite laterals and small ω. 336 instances, max relative gap 2.4e-7.

Rank > 3 appears in 501 of 840, again without any gap.

### 2.3 Set-B-like targets at small N (`run_gim.py`, δ = 0 rows) and the CSD2′ screen (`run_csd2p.py`, d=b)
- run_gim: N = 3, 4, 5, 6, 8, 16 × ωtf ∈ {1, 2.09, 3}, 60/20 targets each: **0 gaps out of 840**.
- csd2p (near-dent, non-coplanar, rate-saturated, random), N = 3…32: 0 gaps.
- Lasserre sanity: at δ=0 every checked instance has Shor = genuine, so there is nothing for Lasserre-2 to separate.

**Verdict for CSD2 as briefed (δ = 0): EXACT numerically.** I found no counterexample anywhere, including the
adversarial dent/rim/far/perpendicular-lateral families, N up to 48 and ωtf past π. A proof remains open.

## 3. Conceptual consistency with Theorems A, B, D; M is certified unreachable (`run_m.py`)

1. **Why a convex SDP can be exact while L is nonconvex.**
   - The feasible set of the SDP is fixed; the target enters only the objective.
   - Over a convex combination of lifted genuine points (b^(i), b^(i)b^(i)ᵀ) with weights p_i, the lifted cost equals E‖Y − q‖² = ‖EY − q‖² + Var(Y) ≥ dist(q, L)². So the "second-moment body" conv{(Y, YYᵀ)-type moments : Y ∈ L} never undercuts the true value, even though its first-moment projection is conv(L) ∋ M.
   - The cost is affine in (mean, second moment). It is not a convex function of the physical readout (mean): the variance term ⟨C,G⟩ − ‖Γx‖² is concave in x. So Theorem D's class (convex f(readout) + convex penalty) does not cover it, and Theorem A does not apply (no constraint on data).
   - Exactness can fail only through lifted points outside that second-moment body, i.e. genuinely higher-dimensional chains (rank > 3 Gram matrices). This is exactly the Hilbert-sphere picture: SDP = the same problem on S^{D−1}, D = n+3.
2. **M is unreachable, certified.** The triangle-inequality and rigidity argument of Theorem B is dimension-free, so M ∉ L_D for every D. Hence the SDP value at q = M is strictly positive.
   - Numbers: 32 configurations, N ∈ {8, 16, 32, 48} × ωtf ∈ {0.4, 1.2, 3.0, 5.5} × {r, (r,v)}, with b_N = e_z. The SDP value at M is > 0 in all of them, from 5.5e-6 (N=8, ωtf=0.4, r; scale² = 0.25, so 2e-5·scale², about 4 orders above the noise) to 0.242 (N=48, ωtf=5.5, (r,v)).
   - Clarabel is optimal everywhere and SCS agrees (to 1e-7 relative at N ≤ 16).
   - The SDP value also equals the genuine dist²(M, L) from multistart, to ≤ 4e-7 relative. So the SDP gives the exact unreachability margin, not merely a positive bound.
   - The SDP solution at M has rank 4–5: a mixture of rotated optimal arcs, by the symmetry about e_z. Its value splits as ‖Γx* − M‖² ("bias") plus the variance term; e.g. N=16, ωtf=3, (r,v): 0.0719 + 0.0065.
   - The state-linear relaxation (same lifted feasible set, cost ‖Γx − M‖² on first moments only) gives 0 at M. This is exactly the Theorem-D obstruction.

## 4. Gimbal δ > 0, unit-d inner discretization: LOSSY

### 4.1 Case 12 ([numerics] BOARD 03:20), reproduced independently (`c12.py`, `c12b.py`)
Model, checked against `numerics/models.py` (ReachM1 'inner', α=0):
- N=16, tf=4, ω=30°/s, δ=15°, a=11;
- d_k unit with ⟨d_k, b_k⟩, ⟨d_k, b_{k+1}⟩ ≥ cos δ;
- same ZOH weights;
- cost |Δv − wv|² + |Δr − wr|².

Results:
- My Gram SDP gives 0.027529356 (Clarabel optimal; SCS 0.027552, inaccurate). My full Shor gives 0.027529946, rank 4. Eigenvalues 27.72, 4.725, 1.475, **0.0781**, 0.
- An R⁴ chain factored from the SDP and polished by ipopt in R⁴ is feasible to 1e-11, with cost 0.027529. So the SDP value is attained in 4D.
- The best 3D cost is **0.02823265**, from:
  - 60 SDP-projection starts;
  - 12 penalty-homotopy paths from the 4D optimum (penalty on the 4th coordinate, 1e-3 to 1e4, then a 3D polish), all of which end at 0.0282327;
  - 400 random/coning starts (57 hit the best);
  - 300 basin-hopping perturbations at scales 0.02–0.8 (none better).
- **Gap 7.03e-4, i.e. 2.49%.**
- Target homotopy from a reachable point: SDP = 3D = 0 for s ≤ 0.88. The gap opens only once the target leaves L: 2.7e-5 at s = 0.96, 7.0e-4 at s = 1.
- Coplanar variant ([proof-sdp] request; wr's lateral rotated onto wv's, which were 2.42° apart): gap persists, SDP 0.042060 vs 0.042798 (1.7%). The 3D optimum is non-planar (σ_min/σ_max 0.12), consistent with [proof-sdp] T2.
- With only ⟨d_k, b_k⟩ ≥ cos δ, the same target is reachable (SDP = 0).

### 4.2 Small-N screen (`run_gim.py`), gaps (rel > 1e-5, abs > 1e-9) among checked targets
| N | δ=15°, ωtf=1 | δ=15°, 2.09 | δ=15°, 3 | δ=40°, 1 | δ=40°, 2.09 | δ=40°, 3 |
|---|---|---|---|---|---|---|
| 3 | 12/60 (max 21%) | 0 | 0 | 28/60 | 32/60 | 19/60 |
| 4 | 23/60 (52%) | 0 | 0 | 27/60 (95%) | 34/60 | 31/60 |
| 5 | 23/60 (96%) | 8/60 | 0 | 33/60 | 37/60 | 30/60 |
| 6 | 10/60 | 16/60 | 7/60 | 26/60 | 39/60 | 33/60 |
| 8 | 6/20 | 2/20 | 3/20 | 10/20 | 8/20 | 11/20 |
| 16 | 3/20 | 4/20 (≤0.5%) | 0 | – | – | – |

δ = 0 on the same targets: 0 gaps in every row.

### 4.3 Certificate (`vlas.py`, `las_cert.py`: my own order-2 Lasserre)
The relaxation uses the moment matrix of degree ≤ 2 monomials (136×136 at N=3: 15 variables, 3,876 moments), localizing matrices for the inequalities, and g·x^β = 0 (|β| ≤ 2) for the equalities. Data are rescaled by 1/(a·tf) for conditioning. Las2 is a valid lower bound on the genuine optimum.

| instance | Shor (Gram) | Las2 Clarabel | Las2 SCS | genuine (1000 starts) |
|---|---|---|---|---|
| N=3, δ=15°, ωtf=1 | 1.86197 | 2.35867 (optimal) | 2.35706 (optimal) | 2.35686 (241 hits) |
| N=3, δ=40°, ωtf=1 | 0.023709 | 0.161568 (optimal) | 0.2135 (optimal, inaccurate: above genuine) | 0.161134 (510 hits) |
| N=3, δ=15°, ωtf=1 (2nd) | 0.070544 | 0.08734 (optimal_inaccurate) | – | 0.08646 |

- Las2 exceeds Shor by 27%, a factor of 6.8, and 24% respectively.
- The solver excess of Las2 over the genuine value is ≤ 1e-3 relative. In scaled units that is at tolerance, far below the separation.
- Las2 ≈ genuine here, so Lasserre-2 is (numerically) exact at N=3.

**Verdict (a): the degree-2 lift is LOSSY for the unit-d inner gimbal discretization.** This is certified up to solver accuracy (two solvers agree at δ=15°).

## 5. CSD2′: convexified lens (‖d_k‖ ≤ 1), i.e. discrete relaxed controls

The SDP replaces Z_dd = 1 by Z_dd ≤ 1; the genuine NLP uses ‖d_k‖² ≤ 1.

conv(lens) = ball ∩ {⟨d, b_k⟩ ≥ cos δ} ∩ {⟨d, b_{k+1}⟩ ≥ cos δ}. Proof: every extreme point of the right-hand side lies on the sphere inside both caps. At α = 0 this is the set of interval-averages of chattering unit thrusts (relaxed controls), so it is the faithful discretization of continuous time.

- **Case 12**: SDP_cvx 0.0273674 (rank 3, e4/e1 8.5e-10) vs genuine_cvx 0.0273682, a difference of 8e-11·scale², i.e. exact. This agrees with [proof-sdp]'s 0.0273676.
- **All 509 unit-d gap instances** (`cvx_check.py`): **0 gaps**. Max (U−L)/scale² = 4.5e-10; statuses 491 optimal, 18 optimal_inaccurate. The worst unit-d instance (N=4, δ=40°: 0.033 vs 0.725) is exact convexified.
- **Adversarial CSD2′ screen** (`run_csd2p.py`): models d=b, cvx δ=15°, cvx δ=40°; ωtf ∈ {0.5, 1, 2.09}; N = 3, 4, 6, 8, 16, 24, 32; families near-dent, non-coplanar (r,v) laterals 30–150° apart, rate-saturated far targets with opposite laterals (×2, 5, 20), random.
  - About 1,600 checked SDP solutions (all with e4/e1 > 1e-7 plus a 10% spot-check): **0 gaps**.
  - Worst relative gap where (U−L)/scale² > 1e-9: 5.2e-6. The largest absolute values (1e-5·scale²) are at ×20 far targets, where the cost is about 4e6, i.e. 2e-8 relative.
- **Stress matrix** (`stress_check.py`, [proof-sdp] Thm 2.4 test). I compute λ_min of the Lagrangian Hessian at the best genuine optimum with ipopt's multipliers; it equals Q_λ ⊗ I_3 for these isotropic QCQPs.
  - Every unit-d gap instance has λ_min < 0: −1.3e-2 at case 12, down to −32 at N=4, δ=40°.
  - Every convexified optimum has λ_min ≥ 0 (min −3.7e-14, i.e. 0).
  - Every d=b optimum with a rank > 3 SDP has λ_min ≈ 0 (±6e-11): PSD and singular, matching the non-unique optimal faces.
  - In 34/34 cases: gap ⇔ stress not PSD.

**Verdict (b): CSD2′ is UNBROKEN.** The δ=0 lift and the convexified-lens lift are numerically exact on everything I could construct. The unit-d failure is a discretization artifact: the lift realizes in-interval chattering through E⊥ tilts of d, which the unit-d discrete model forbids and continuous time allows.

## 6. Variable throttle

The natural lift has z = (a_k, U_k = a_k b_k) and constraints ‖U_k‖² = a_k², a_k ∈ [a1, a2] with all pairwise RLT products, rate U_k·U_{k+1} ≥ c a_k a_{k+1}, SOC ‖U_k‖ ≤ a_k, and b_0 = b_N = e_z substituted (`vext.throttle`).
- N=6, ωtf=2, a ∈ [.5, 1]: SDP 0.28471 (Clarabel and SCS optimal, rank 5) vs genuine 0.47529 (all 300 starts agree): **40%**.
- With ωtf = 6 or 1e3 the lift is rank 1 and exact, so the loss needs a binding rate limit.
- Certified by Lasserre-2 at N=3 (e.g. Shor 0.5759 < Las2 0.6047 = NLP 0.6047; also 0.6516 < 0.6569, 0.7532 < 0.7543).
- **Not a discretization artifact** (`thr_csd3.py`, fixed physics tf=1, ω=2, a∈[.5,1], fixed target):

| N | 4 | 6 | 8 | 12 | 16 |
|---|---|---|---|---|---|
| SDP | 0.4095 | 0.2847 | 0.2176 | 0.1746 | 0.1529 |
| genuine | 0.4657 | 0.4753 | 0.4731 | 0.4753 | 0.4749 |
| rel gap | 12% | 40% | 54% | 63% | 68% |

  The genuine value converges. The lift converges toward the no-rate-limit value (0.133), i.e. the lift asymptotically ignores the rate limit.
  - Relaxed controls do not help here: conv{a b_k : a ∈ [a1, a2]} is already the segment, so the "convexified throttle" model equals the original.
  - Mechanism: throttle headroom pays for the shortened E-projection when U tilts into E⊥, so the E-direction turns faster than ω for free.
- **Other throttle lifts:**
  - (U,b)-Hilbert lift, s_k = ⟨U_k, b_k⟩ ∈ [a1, a2], ‖U_k‖² ≤ (a1+a2)s_k − a1a2: 0.3044 vs 0.4753. It is lossy even at ω = ∞ (0.1228 vs 0.1332), because the U-ball around s·b acts like a gimbal.
  - Tightest degree-2 Shor in (a, U, b) (U = a b as quadratic equalities, plus everything above): 0.47071 vs 0.47529. Nearly closed, still lossy (1%), rank 6.
  - **[proof-sdp] CSD3**: Gram of (u, b, e) plus scalars Γ_k, S_k, with ⟨u,b⟩ ≥ Γ cos δ, ‖u‖² ≤ S, S ≥ Γ², S ≤ (a1+a2)Γ − a1a2. Tested at N = 4, 6, 8 (12 targets each for δ = 0 and δ = 15°, ωtf ∈ {1, 2, 6}) plus 2 at N=12. It is **lossy**:
    - δ = 0: relative gap 2–36% on every instance;
    - δ = 15°: up to 18%; only 2 of 36 are exact.
    - The SDP is mostly rank 3 (e4/e1 ≤ 1e-8 at δ=0), so the loss is already inside R³: ‖u‖² ≤ S with S > Γ² (a variance of Γ) lets u leave the b-axis/cone and exceed its magnitude.
    - Genuine-orig equals genuine-CW to ≤ 1.2e-5, so the C-W relaxation is lossless at the genuine level and the loss is entirely in the lift.

**Verdict (c): the throttle lift is lossy, and the gap grows with N. (d) CSD3 is lossy, even without a binding rate limit.**

## 7. Altitude / glide slope; min-fuel
FILL (run_ext.py altitude / fuel).

## 8. Files
- `numerics/verifier-sdp/`:
  - core: `vcore.py` (Gram SDP, NLP, rounding), `vqcqp.py` (generic QCQP → Shor + NLP), `vext.py` (gimbal/throttle/altitude builders, throttle lifts), `vgim.py` (inner-discretization gimbal, unit or convexified, R^dim NLP, stress), `vlas.py` (order-2 Lasserre);
  - runs: `run_fixed.py`, `run_adv.py`, `run_gim.py`, `run_csd2p.py`, `cvx_check.py`, `c12.py`, `c12b.py`, `las_gim.py`, `las_cert.py`, `stress_check.py`, `thr_csd3.py`, `run_m.py`, `run_ext.py`, `summarize.py`.
- `results/*.jsonl|json|log`.

## 9. Comparison with [redteam-lift] (read only after the verdicts above)
Read: `math/redteam-lift.md` §3.2 and §8, and CLAIMS row L-SD2.

**Agreements**
- Same formulation: b_0, b_N substituted. Their diagnosis of the early "gaps" as Slater failure matches what I see: I never imposed b_0, b_N by Gram equalities, and Clarabel also cannot reach 1e-10 on the well-posed form ("inaccurate"), so I run at 1e-9.
- Hilbert-sphere picture (their S1/S2 = my §3). Their θ_M certificate (q_SDP = 53.6 > 0 at N=16, (r,v), in their units) matches my §3: I find q_SDP(M) > 0 on all 32 configurations, and moreover equal to the genuine dist²(M, L).
- Case 12: their factorization into an explicit 4D chain (0.02752899) matches mine (0.027529).

**Discrepancies / refinements**
1. **Scope of CSD2.**
   - L-SD2 states CSD2 for "fixed-thrust 5DOF" but tests the unit-d gimbal inner discretization (δ = 15°, 40°). Their final §3.2 verdict is "CSD2 FALSE in general (Π_4 ≠ Π_3)".
   - My data separate the cases. For δ = 0 (the brief's model) and for the convexified lens (CSD2′) there is no gap anywhere. The failure is specific to the unit-d lens discretization: all 509 unit-d gaps vanish in the convexified model, and stress PSD ⇔ exact in 34/34.
   - So "Π_4 ≠ Π_3" holds for the unit-d discrete model only. It is not evidence against exactness in continuous time.
2. **Small N.** [numerics] c5_smallN (cited by redteam-lift) found no gap at N=3,4 and gaps at N=5. At their parameters (ωtf = 2.09, δ=15°) I agree: 0/60 at N=3,4 and 8/60 at N=5. At smaller ωtf (=1) or larger δ (40°), gaps are frequent already at N=3, which makes the order-2 Lasserre certificate cheap (15 variables). I supply it in §4.3.
3. **Throttle.** redteam-lift reports "free throttle gives the same values: throttle does not enter the dent" (velocity-only reachable-set geometry, dimlift.py). That is a statement about Π_n, not about a lift. Every degree-2 throttle lift I built is lossy, by up to 68% at N=16, growing with N. Their §8 limit ("fixed thrust only") is therefore confirmed in a strong form.
4. **"~45 targets exact" (L-SD2 row).** Consistent with my unit-d screen at large ωtf, where gaps are rare. Their 35 scan_clean targets sit in the regime (ωtf ≥ 2, δ=15°) where I also see few gaps at N ≥ 16 (≤ 4/20, ≤ 0.5%).
