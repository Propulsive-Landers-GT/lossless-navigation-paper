# Adversary report on math/00 (Theorem A, Theorem B, scope of "impossible")

Author: [adversary]. Target: `math/00-model-catalog-and-proof-sketch.md` §§2–4 (Claims A, B in `comms/CLAIMS.md`).
Cross-references: `math/02-impossibility-rigorous.md` ([proof]), `math/redteam-lift.md` ([redteam-lift]),
`comms/threads/6dof-models.md` ([adversary-6dof] owns M2–M4). Numerics: `numerics/adversary/`.

Verdict legend: **SURVIVES** = no flaw found. **NEEDS FIX** = true, but the statement or its scope must change.
**BROKEN** = false as stated.

## Summary of verdicts

| # | Attack | Verdict |
|---|---|---|
| 1.1 | Spherical triangle inequality, inner-product form | SURVIVES |
| 1.2 | Equality case ⇒ b on the e_z–d geodesic; a.e. → everywhere | SURVIVES |
| 1.3 | Rigidity u(s) const (incl. through the tent peak), measurability | SURVIVES |
| 1.4 | Gimbal chattering (d merely measurable) | SURVIVES (argument is pointwise a.e.) |
| 1.5 | Mass bound a ≥ a1 and its equality case | SURVIVES (needs m0 − αρ1 tf ≥ m_dry stated) |
| 1.6 | δ + max φ ≤ π/2 | NEEDS FIX: it is a convenience only, and it confines Thm B to tf ≲ 2.5–3.3 s for GTPL. B* below removes it |
| 1.7 | **Witness P_u under altitude / glide-slope constraint** | **BROKEN for the real soft-landing problem.** P_u starts 42–148 m underground for GTPL. Fixed by B* |
| 1.8 | Trying to reach M | SURVIVES. My attempts failed; [numerics]/[proof] pin dist(M,R) ≈ 1.8–2.2 m/s at GTPL tf = 2 s |
| 2.1 | "Uniform" = jointly convex with affine data entry | NEEDS FIX: the restriction must be stated, since with arbitrary data maps the notion is vacuous |
| 2.2 | Symmetry-reduced (rotating-frame) relaxations | **NEEDS FIX / OPEN.** Not covered by the Thm B witness. See §2.2 and A4 numerics |
| 2.3 | Lossless for a.e. θ / ε-lossless | SURVIVES (positive-measure open gap) |
| 2.4 | Lossless only at optimality / only on F | NEEDS FIX: Thm A excludes only detection-sound losslessness. "Exact on F" is open for min-fuel |
| 2.5 | Free final time, line search, dilation | SURVIVES with B* (math/00's witness fails here; B* does not) |
| 2.6 | Occupation measures / Young measures / moment-SOS | SURVIVES (no contradiction): data enter as δ_θ, which is non-affine |
| 2.7 | SDP lift of b bᵀ, quaternion/orbitope lifts | SURVIVES (data still affine, so Thm A applies) |
| 2.8 | Discretization | NEEDS FIX: state the theorem in continuous time plus a uniform-in-N corollary. Discrete 3DOF LCvx is also not exact |
| 3 | Does Thm A "prove too much" for 3DOF? | SURVIVES: exact continuous-time 3DOF F is convex (proved without pointing/fuel limit; numerically with fixed direction and mass) |
| 4 | 6DOF transfer | NEEDS FIX: true for kinematic attitude and independent-torque models, false/open for TVC-generated torque (P_u unrealizable) |
| 5 | Well-posedness | Only well-posed after fixing 5 choices; strongest statements in §5 |

---

## 1. Theorem B, step by step (model M1, as stated: no state constraints)

**1.1 Triangle inequality (step 1).** For unit x, y, z with x·y ≥ cos α, y·z ≥ cos β, α, β ≥ 0 and α + β ≤ π, we get
x·z ≥ cos(α+β). This is the triangle inequality for the geodesic metric arccos(x·y) on S², because arccos is decreasing on
[−1,1]. The rate bound gives angle(b(s), e_z) ≤ ωs (and ≤ ω(tf−s) in the tent case). It needs ωs ≤ π, which is implied by the hypotheses. **SURVIVES.**

**1.2 Equality case and a.e. → everywhere (steps 2–3).** The chain is ∫a d_z ≥ ∫a cos(δ+φ) ≥ ∫a1 cos(δ+φ).
The first inequality is pointwise. The second uses cos(δ+φ) ≥ 0 together with a ≥ a1. Equality forces a(d_z − cos(δ+φ)) = 0 a.e., hence d_z = cos(δ+φ) a.e. (since a > 0).
Equality in the geodesic triangle inequality, with 0 < δ+φ < π, puts b(s) on the unique minimizing geodesic from e_z to d(s), with
angle(b, e_z) = φ(s) and angle(b, d) = δ. Uniqueness holds because d ≠ ±e_z. The set where φ = 0 is {0} (or {0, tf}), which is null.
Both sides of b(s)·e_z = cos φ(s) are continuous, so a.e. equality gives equality everywhere. **SURVIVES.**

**1.3 Rigidity (step 4).** On a branch with |φ'| = ω and φ > 0:
cos(φ'−φ) ≤ b·b' = cos φ cos φ' + sin φ sin φ' (u·u'). This forces u·u' ≥ 1, so u = u'. Here u(s) = b_lat/|b_lat| is continuous wherever φ > 0, so there is no measurability issue.
On the tent, both branches are meridional and meet at the peak, where φ = ωtf/2 > 0 and u is continuous. So u is constant. **SURVIVES.**
(The cleaner general form, used in B* below: if Φ(s) := angle(b(s), e_z) satisfies |Φ'| = ‖ḃ‖ a.e., then the azimuthal speed
sin Φ·|ψ'| vanishes, so b is meridional wherever Φ ∈ (0, π).)

**1.4 Gimbal chattering.** d is only measurable, but every step is a pointwise a.e. bound on d(s). Chattering inside the cone cannot push
d_z below cos(δ+φ). Chattering *does* matter for closure: R is not obviously closed. This does not affect "M ∉ R". For the open-gap
statements (2.3) one needs M ∉ cl R. That holds because the relaxed system (d ∈ conv of the cap) has the same minimum of d_z, attained only at
the same extreme point. By Filippov–Ważewski, cl R = R_relaxed, which is compact. **SURVIVES.**

**1.5 Mass.** T ≥ ρ1 ⇒ m(s) ≤ m0 − αρ1 s ⇒ a = T/m ≥ a1. Equality a.e. ⇔ T = ρ1 a.e. P_u is admissible only if
m0 − αρ1 tf ≥ m_dry. This hypothesis is missing from math/00. **SURVIVES (add the hypothesis).**
More robust form: the argument needs only that the scalar throttle set is independent of attitude and that ∫a cos(δ+φ) has a
minimizer a* > 0. So Thm B also holds for the Taylor-approximated mass constraints of Açıkmeşe–Ploen 2007. This matters for §3.

**1.6 δ + max φ ≤ π/2.** This is used only so that cos(δ+φ) ≥ 0 and the min-throttle bound points the right way. For GTPL (δ = 15°,
usable ω ≈ 0.3–0.5 rad/s) the condition means tf ≤ 2.6–4.4 s (ramp), while real burns are 7–12 s (context/vehicle.md).
[proof]'s Thm L removes it for the state-free model by another route. B* removes it and also handles state constraints. **NEEDS FIX.**

**1.7 BREAK: P_u violates r_z ≥ 0 for GTPL.** Along P_u, net vertical acceleration = a1 cos(δ+φ) − g. For GTPL,
a1/g = ρ1/(m0 g) = 400/(80·9.81) = 0.51 < 1, so this is negative throughout. With v(tf) = 0, the vehicle is rising before touchdown, so
r_z(s) < 0 for all s < tf. `numerics/adversary/a1_Pu_altitude.py` gives:
ramp, tf = 3.27 s: r0z = −41.7 m, v0z = +22.8 m/s. Tent, tf = 6.54 s: r0z = −148 m.
Every LCvx soft-landing formulation (ACP 2007, ACB 2013, Malyuta et al. tutorial) imposes a glide-slope cone, which contains r_z ≥ 0.
So P_u ∉ F_glide, and Thm B (and [proof]'s ball bound, which uses the same M) says nothing about F_glide whenever ρ1 < m0 g.
That covers essentially every real lander, including GTPL. The algebra of math/00 is fine. Its *applicability* is broken. Fix: B*.

### B*. Repaired witness: the "dive-then-brake" exposed face

Setting: M1 with b(0) = e_z, rate ω < ∞, gimbal cone δ ∈ (0, π/2), and any scalar throttle model in which the admissible throttle
histories T(·) do not depend on attitude, a = T/m > 0 (ρ1 > 0), α ≥ 0. Terminal attitude may be free or fixed to e_z. There are optional rotation-invariant
state constraints (altitude, glide-slope cone about e_z, tilt cap), and optional free tf ∈ [t1, t2].

**Functional.** For any vertical α_z, β_z,
ℓ(r0, v0) = α_z r0z + β_z v0z = c(tf) + ∫_0^tf w(s) a(s) d_z(s) ds, with w(s) = α_z s − β_z.
The weight is affine and independent of tf (derivation: r0 = −v0 tf − g tf²/2 − ∫(tf−s) a d, v0 = −g tf − ∫ a d).
Take α_z > 0 and β_z = α_z s* with a small s* > 0, so w < 0 on [0, s*) and w > 0 on (s*, tf].
ℓ is invariant under rotations about e_z, and so is F.

**Lemma (rotation-midpoint).** If F is invariant under the rotation R_π about e_z and convex, then for every x ∈ F the point
x̄ = (x + R_π x)/2 is in F. x̄ has zero lateral components and the same vertical components as x. (This needs no closedness.)

**Lemma (structure of every maximizer).** Work in the state-unconstrained problem. Let (T*, b*, d*) maximize ℓ; maximizers exist in relaxed
controls, and a relaxed maximizer is an ordinary control (see below). Freeze T*. Then m and a* > 0 are fixed, and (b*, d*) must maximize
∫ w a* d_z. For fixed b, the optimal d is unique wherever w ≠ 0. On early times it is tilted to angle Φ+δ, away from e_z along b's
meridian. On late times it is d = e_z when Φ ≤ δ, and tilted to angle Φ−δ toward b otherwise. Here Φ(s) := angle(b(s), e_z).
Hence the objective depends on b only through Φ: J(Φ) = ∫ g(s, Φ(s)) ds. Here g(s, ·) is strictly increasing for s < s* (provided Φ+δ < π), non-increasing for
s > s*, and strictly decreasing where Φ > δ.
The achievable Φ are exactly the ω-Lipschitz functions with Φ(0) = 0, and each one is achieved by a meridional path.
- Early [0, s*]: replace Φ* by the envelope E(s) = min(ωs, Φ*(s*) + ω(s*−s)). E is ω-Lipschitz, E ≥ Φ*, and it matches at s*.
  It is realized meridionally, ending at b*(s*). If Φ* ≠ E on a set of positive measure, J strictly increases, so Φ* = E.
- Late: replace Φ* by min(Φ*, max(Φ*(s*) − ω(s−s*), 0)). J does not decrease, and it strictly increases unless Φ* = Φ*(s*) − ω(s−s*) wherever Φ* > δ.
- On both pieces, |Φ*'| = ω ≥ ‖ḃ*‖ ≥ |Φ*'|. So b* is meridional with one azimuth u on the connected interval (0, q), q = first time Φ* ≤ δ.
- Hence lateral Δv = ∫_0^{s*} a* sin(Φ+δ) u + ∫_{s*}^{q} a* sin(Φ−δ) u + 0 = κu with κ > 0. So v0_lat ≠ 0. (Use this *unweighted* increment. In the weighted moment W_h = −X_h + B_h, the two pieces have opposite signs; [proof] caught this.)
Relaxed controls: the cost is linear in d, and the maximizing d is unique, so the relaxed d-measure is a Dirac. A throttle measure can be replaced by its
mean T̄ ∈ [ρ1, ρ2], which gives the same ṁ and the same velocity. Thus relaxed maximizers are ordinary trajectories, and x* ∈ F.

**Theorem B\*.** F (fixed tf, any tf > 0; or ∪_{tf∈[t1,t2]} F_tf) is nonconvex. Moreover x̄* ∉ cl F, so int(conv F) \ cl F ≠ ∅
whenever int F ≠ ∅.
*Proof.* Let x* be a maximizer and x̄* its rotation-midpoint. If x̄* ∈ cl F = F_relaxed, then x̄* is a relaxed maximizer (ℓ is
rotation-invariant) with zero lateral data. That contradicts the structure lemma. For free tf: a maximizer over (tf, control) is a fixed-tf
maximizer at its own tf*, and the weight w does not depend on tf. ∎
**With state constraints.** If at least one unconstrained maximizer satisfies the constraints, then the constrained maximizers are a
subset of the unconstrained ones, and the same proof applies. Sufficient conditions, shown for every unconstrained maximizer:
- Late throttle is forced to ρ2. More T raises a now and lowers m later, and w·d_z ≥ 0 on the late window.
- Late tilt satisfies Φ − δ ≤ ωs*.
- If ρ2 cos(ωs*)/m0 > g and s*(ρ2/m_dry + g) < (tf − s*)(ρ2 cos(ωs*)/m0 − g), then v_z < 0 on [0, tf), so r_z > 0.
- Lateral motion vanishes on [q, tf] with q ≤ 2s*, so a glide-slope cone of any half-angle < 90° is satisfied for small s*.
- The tilt cap θ_max is inactive if 2ωs* < θ_max.
GTPL check (tf = 8 s, s* = 0.5 s, ω = 0.4): 13.8 < 18.3. ✓
**Numerics (A2, `a2_divebrake.py`):** see §6 below.

**Known limits of B\*.**
- *Gimbal-rate limits (M2).* B\*'s optimal d jumps by up to 2δ at s* (outward tilt → vertical). With a gimbal rate limit (GTPL clamp 100°/s), d is a
  state, the pointwise d-optimization is no longer separable, and the structure lemma must be redone. Original B is unaffected: P_u has a constant gimbal offset, so P_u ∈ M2 ⊂ M1.
  But the altitude break of B persists in M2. → flagged to [adversary-6dof], who owns M2.
- *Throttle slew limits* (GTPL 2000 N/s). The structure lemma only freezes T*, so it is unaffected. The altitude sufficient condition used "late T = ρ2". With slew
  limits, replace ρ2 by the slew-limited lower envelope of T on [s*, tf]. That envelope is still forced upward, since the late objective is monotone in T.
- Tilt cap: ωs* < θmax suffices, because E ≤ ωs on [0, s*] and late Φ ≤ Φ(s*).

Status of B*: an analytic argument at the level of rigor of math/00, independent of [proof]'s Thm L. Handed to [proof] for a
rigorous write-up. It is the version that should be formalized if the theorem is meant to cover the glide-slope-constrained problem.

**1.8 Attempts to reach M.** I tried three things:
- Chattering b. It cannot help, because b is a Lipschitz state.
- Inward gimbal plus extra throttle to cancel lateral impulse. It raises d_z at first order.
- Non-planar b paths with azimuth sweeping. These lose |Φ'| = ω, so they lose vertical waste at first order. The rigidity lemma is exactly this.
[numerics] (100–200 ipopt restarts, inner discretization) finds dist(M, R) ≈ 2.2 m/s at GTPL tf = 2 s. [proof]'s ball bound gives ≥ 1.8.
The nearest reachable point lies ≈ 2.2 m/s *above* M on the axis. **SURVIVES.**

---

## 2. Definitions: is "uniform convex relaxation, lossless (feasibility form)" the right formalization?

**2.1 Data entry.** Theorem A is a tautology (a projection of a convex set is convex). All its content is in the definition.
With an arbitrary data map ψ, "C convex in (ψ(θ), y)" is vacuous. If ψ is a homeomorphism with ψ(F) convex, take C = ψ(F) × {0}.
F_tf is a compact set homeomorphic to a ball here, so such a ψ exists. The occupation-measure LP is the natural instance (δ_θ entry, 2.6).
So the theorem must say: *(r0, v0) enter affinely*, as initial states of the linear translational dynamics, which is what every LCvx paper does.
[redteam-lift] P1 extends this to coordinatewise-monotone maps (e.g. z = ln m–type changes).
z0 = ln m0 is irrelevant, because m0 is fixed in F_tf. If m0 is made data, the statement must be in the coordinates actually used.
**NEEDS FIX (wording).**

**2.2 Symmetry reduction (rotating frame): a live loophole.** A legitimate, cheap scheme: given θ, rotate about e_z so that
v0_lat ∥ +x, solve a convex program whose data (r0', v0x' ≥ 0, v0z) enter *affinely*, then rotate back. This is a uniform convex
relaxation of the problem restricted to the half-space H = {v0y = 0, v0x ≥ 0}. It needs only F ∩ H to be convex.
Neither P_u, P_{−u} nor the B* pair lies in H as a pair: each of x and R_π x has v0_lat ≠ 0, in opposite directions.
So **neither Thm B nor B* excludes it.** Theorem A still applies to F ∩ H.
To close the loophole one must show the nonconvexity of slices such as G_v = F ∩ {v0_lat = 0} ⊂ H, and G_r = F ∩ {r0_lat = 0} for the
r0-aligned reduction, etc. Each G is rotation-invariant, so the midpoint lemma reduces this to a face problem with the extra linear constraint.
Numerical test A4 (§6):
(a) the velocity cross-section of R in the meridian half-plane;
(b) min Δv_z over G_v, with and without r0_lat = 0.
A strict gap in (b) shows G_v and F ∩ H are nonconvex. **NEEDS FIX / OPEN** pending a proof (see §6 for the evidence).

**2.3 Lossless for a.e. θ, or ε-lossless.** Let P = proj C ⊇ F be convex. If P \ F is null, or P ⊆ F^ε, a contradiction follows from
int(conv F) \ cl F ≠ ∅ (B*, or [proof] Prop 5.3), or from ε < dist(M, R) (Cor ε). This is robust to measure-zero and
nowhere-dense exception sets. It is *not* robust to exception sets D that are allowed to contain the whole gap. That is the content of 2.4.
**SURVIVES.**

**2.4 "Lossless at optimality" vs feasibility form.** The standard LCvx statement is "if the relaxed problem is feasible, its
optimum is optimal for the original", stated for every θ with C_θ ≠ ∅. With attainment (compact C_θ under thrust bounds), this
implies the feasibility form ([proof] Prop 1.5, [redteam-lift] §5.2). So **Thm A targets the right notion for LCvx as defined.**
A strictly weaker notion is *not* excluded: exact on F, arbitrary off F. A relaxation of this kind certifies infeasibility a posteriori, by finding that the relaxed solution is not original-feasible.
It is a complete decision procedure, so it is practically almost as useful.
Necessary condition (value function V_J; the relaxed value is convex): V_J restricted to F must extend convexly to conv F.
For cost 0 this is trivially satisfiable.
For attitude-sensitive costs it fails ([redteam-lift] Prop T).
For **min-fuel** it reduces to F ∩ conv F_min ⊆ F_min, where F_min is the min-throttle data set. This is **open**; numerically it holds on the axis ([redteam-lift] §5.4).
So the honest statement is: *no detection-sound (feasibility-form) lossless uniform relaxation, and no relaxation that is value-exact on F for all convex costs.*
"Exact on F for min-fuel" is unresolved. **NEEDS FIX (state the notion; flag the open case).**

**2.5 Free final time, line search, dilation.**
- Line search over tf is an outer nonconvex search, not a uniform convex program. For each fixed tf, Theorem A applies to F_tf.
- A single convex program over (θ, tf) would need ∪_t F_t convex. [redteam-lift] §4.3 shows that math/00's M *does* become reachable at a longer tf, so the witness fails.
- B* does not fail, because its weight w(s) = α_z s − β_z is tf-independent. Any maximizer over (tf, control) on a compact window is a fixed-tf maximizer, so it has lateral v0 ≠ 0, and ∪_{t∈[t1,t2]} F_t is nonconvex.
- Dilation (tf as a decision variable, multiplying the dynamics) is bilinear. If tf is made data, it enters nonaffinely, and B* applies tf-by-tf anyway.

**SURVIVES with B\*** (not with math/00's witness).

**2.6 Occupation measures, relaxed controls, moment-SOS.**
- Relaxed controls (Young measures in u) do not convexify state constraints such as b ∈ S² with a Lipschitz bound. By Filippov–Ważewski, the relaxed reachable set is cl F, which is still nonconvex.
- In the occupation-measure LP (Lewis–Vinter, Vinter 1993, Lasserre–Henrion–Prieur–Trélat 2008), the initial measure is μ0 = δ_θ. The LP is linear in (μ0, μ, μT), but θ ↦ δ_θ is not affine. Its exactness is "LP value = relaxed value for Dirac initial data". By the superposition principle, the LP-feasible initial measures are the probability measures on cl F. So ½δ_{θ+} + ½δ_{θ−} is feasible while δ_{θM} is not. No contradiction with Thm A.
- If one encodes θ affinely through the mean, ∫x dμ0 = θ, the feasible θ-set becomes conv cl F. That is exactly the loss Thm A predicts.
- Truncated moment relaxations take θ through monomials (Veronese map). Such data entry can represent nonconvex semialgebraic F exactly in principle, but finite truncations are only outer approximations.

**SURVIVES**, and it *shows that the affine-entry clause in 2.1 is essential*: with δ_θ entry an exact convex (infinite-dimensional) formulation of 5DOF exists. (Agrees with [lit-review] and [redteam-lift] §2.)

**2.7 SDP lifts (B ⪰ bbᵀ, conv SO(3) orbitope, quaternion LMI).** (r0, v0) still enter affinely, so Thm A applies, and Thm B/B* make every such lift
lossy. Per-instance Dirac-lifted Shor relaxations (θθᵀ as data) fall under 2.1/2.6. **SURVIVES.**

**2.8 Discretization.** Practical LCvx solves a discretized SOCP. Its losslessness is relative to the *discretized* nonconvex problem, and it is
not exact even in 3DOF: Luo–Echigo–Açıkmeşe (Automatica 2026, via [lit-review]) prove violations at up to n_x − 1 nodes. Note that
with N = 1 the discrete 3DOF data set is an annulus, which is nonconvex. So "Theorem A ⇒ discrete LCvx is not exactly lossless" is *true even for 3DOF*.
The 5DOF theorem must therefore be stated in **continuous time**, plus a corollary that separates 5DOF from 3DOF:
for any discretization family whose discrete feasible sets converge (Hausdorff) to the continuous F, the gap of any affine-entry
convex relaxation is ≥ dist(x̄*, cl F) − o(1) > 0 uniformly in N. In 3DOF it → 0.
The rigidity lemma has a discrete analogue: node-wise b_k·b_{k+1} ≥ cos(ωh) with polar angles kωh forces a common meridian.
**NEEDS FIX (wording).**

---

## 3. Does the obstruction prove too much (exact 3DOF)?

Model: r̈ = T/m + g, ‖T‖ ∈ [ρ1, ρ2], ṁ = −α‖T‖, fixed tf, continuous time, exact (no Taylor approximation).
- **No pointing constraint, fuel limit not binding: F is convex (proof).** Let σmax(s) = ρ2/(m0 − αρ2 s). Every admissible
  trajectory has ‖u‖ = ‖T‖/m ≤ σmax pointwise, since T ≤ ρ2 and m ≥ m0 − αρ2 s. So F ⊆ A := {data of u : ‖u(s)‖ ≤ σmax(s)}, which is convex.
  Conversely, full throttle T ≡ ρ2 with measurable d ∈ S² realizes exactly σmax(s)d(s). By Aumann's theorem (nonatomic
  Lebesgue measure), the set of moments (∫u, ∫(tf−s)u) over selections of s ↦ σmax(s)S² equals the set for selections of its convex hull.
  So A = F. F is convex and compact. (Also noted in [proof] §8.)
- **Fixed direction d ≡ e_z (pointing angle 0) with mass depletion:** the reachable set {(∫σ, ∫(tf−s)σ)} is bounded by the burn-early
  and burn-late curves. A chord test over all pairs found **no violation** for GTPL α or for α up to ×9.5 (final mass ratio 0.46).
  `a3_1d_mass.py`, `a3b_pairs.py`. The ×20 run in `results_a3.txt` is invalid: the mass went negative. Convex numerically.
- With a binding fuel limit and/or pointing cap θ < π/2 together with α > 0: σmax-domination fails, and the union over throttle
  histories might be nonconvex. **Open**, not refuted.
  But ACP 2007 / ACB 2013 do *not* claim losslessness for the exact mass constraint. They use a conservative Taylor
  approximation (both bounds become inner approximations because z ≥ z0(t)). The approximated problem has convex F whenever their theorem applies.
- B and B* hold for that approximated throttle model too (§1.5, B*: any attitude-independent throttle set).

**Conclusion.** In continuous time, the exact 3DOF F is convex wherever we can check, and the 5DOF F is not, with α = 0 or > 0 and
for every throttle model. The obstruction is attitude-specific. It does not prove too much in continuous time. In discrete time it
"proves" 3DOF non-exactness too, which is true (2.8). Hence the theorem must be continuous-time. **SURVIVES.**

---

## 4. 6DOF (coordinated with [adversary-6dof], who owns M2–M4)

- **Kinematic 6DOF** (ω is a control, ‖Ω‖ ≤ ω): ‖ḃ‖ = ‖Ω × b‖ ≤ ω, so F_6 ⊆ F_M1. Planar arcs with zero roll are realizable, so B and B* transfer.
  With a per-axis box limit |Ω_i| ≤ ω_max: use ω = √2 ω_max with u along a body diagonal. Only the R_π symmetry is needed. ✓
- **Rigid body, Ω a state:** P_u needs ‖ḃ(0+)‖ = ω instantly, so it is unrealizable from Ω(0) = 0. math/00's remark "planar arcs are
  6DOF-realizable" is false here.
- **Independent transverse torque** (RCS/wheels), axisymmetric J, Ω_⊥(0) = 0: the gyroscopic term is ⊥ Ω_⊥, so d‖Ω_⊥‖/dt ≤ τ/J_t.
  The achievable Φ class is Φ(0) = Φ'(0) = 0 with |Φ''| ≤ κ (meridional), and non-meridional motion only slows Φ.
  The equality ⇒ meridional argument holds, and B* goes through with the envelope taken in this class. (Consistent with [proof] Thm E.)
- **TVC-generated torque (GTPL's actual pitch/yaw actuator):** an outward gimbal rotates the body *inward* (J_t b̈ ∝ −ℓ T g_⊥).
  The extreme "max tilt + outward gimbal" arc is dynamically impossible, and d and b are coupled.
  The B* face argument needs a new structure lemma: optimal Φ forced to an envelope, and equality ⇒ meridional, in the coupled class. **OPEN — owned by [adversary-6dof].**
  For GTPL this is the physically faithful model, so the 6DOF claim B6 is **NEEDS FIX** for it.

---

## 5. Is "possible vs impossible" well-posed? Strongest defensible statements

It is well-posed only after fixing five choices:
1. data entry (affine vs lifted);
2. lossless notion (detection-sound / a.e. / ε / exact-on-F / value-exact);
3. uniform vs per-instance;
4. continuous vs discrete time;
5. attitude model (kinematic vs TVC-torque).

**Strongest impossibility I can defend** (B* for the state-constrained and long-tf parts, [proof] Thm Q/L for the quantitative part):
> In continuous time, consider model M1 (kinematic thrust axis, ω < ∞, gimbal cone δ ∈ (0, π/2), b(0) = e_z, ρ1 > 0, α ≥ 0, any
> attitude-independent throttle model). Fix any tf > 0, or take free tf in a compact window. Allow optional rotation-invariant altitude/glide-slope/tilt-cap
> constraints, under the explicit braking condition of B*. Then there is **no convex set C ⊆ R⁶ × Y (Y any vector space) with (r0, v0) entering affinely**
> that is any of the following:
> (i) lossless in the feasibility sense;
> (ii) lossless up to a null set or a nowhere-dense set;
> (iii) ε-lossless for ε below an explicit gap;
> (iv) value-exact on F for every convex cost.
> The same holds for kinematic 6DOF and for independent-torque rigid-body models.
> Not covered:
> - symmetry-reduced (frame-rotating) relaxations, unless the slice nonconvexity of §2.2 is proved;
> - "exact on F for min-fuel";
> - TVC-torque-coupled dynamics.

**Strongest possibility I can defend:**
- (P1) Per-instance: for a fixed attitude profile b(·), the problem is a 3DOF problem with a time-varying cone. With α = 0 its F_b is convex (Aumann) and LCvx-type relaxations are available (Thm C, [positive]). Uniformity is lost: the profile is chosen per θ.
- (P2) Non-affine data entry: an exact infinite-dimensional convex (LP) formulation exists, namely occupation measures with δ_θ, exact up to closure. Its finite truncations converge from outside.
- (P3) Not excluded by anything proved so far: a relaxation exact on F for min-fuel that is feasible on conv F \ F. Also not excluded: a frame-rotating relaxation, if F ∩ H is convex.
- (P4) Trivially, outer convex relaxations such as the time-varying cone d·e_z ≥ ‖d‖ cos(δ + φ(s)) are ε-lossless for ε ≥ their Hausdorff gap.

**Bottom line:** under the LCvx-faithful definitions, **impossible** is the correct answer for kinematic 5DOF. But only B* (not math/00's B)
establishes it for the glide-slope-constrained, long-tf problem that GTPL actually solves. The two named loopholes (2.2, 2.4) and the TVC-coupled
model must be either closed or stated as exclusions.

---

## 6. Numerics (numerics/adversary/)

| Script | Question | Result |
|---|---|---|
| a1_Pu_altitude.py | Is P_u above ground (GTPL)? | No: r0z = −41.7 m (ramp, 3.27 s), −148 m (tent, 6.54 s). `results_a1.txt` |
| a3_1d_mass.py, a3b_pairs.py | Exact 1D rocket with mass: is the (Δv, Δr) set convex? | Yes, numerically, up to mass ratio 0.46. `results_a3.txt` |
| a2_divebrake.py | B* / S with exact mass, r_z ≥ 0, tf = 8 s: max ℓ for U, Pv, Pvr | killed (machine load ≈ 280); superseded by [numerics] s1_slice.py (ipopt, 48 starts, 35% coning). Script kept for reproduction |
| a4_reduced_slices.py | Symmetry-reduction loophole (§2.2), velocity cross-section | killed for the same reason; superseded by s1_slice.py |
| a5_coning.py | Small-angle Pv vs Pvr with planar/coning/random starts | Pure dive: tf = 3: gap 23% (cap none/0.6). tf = 8: 39% (no cap), 31% (cap 0.6). tf = 20, cap 0.6: **gap 0** (Pv = Pvr = 69.89): coning on the cap fills the dent, as predicted in §7 item 3. Pv optimizers are often non-planar but still land offset. Dive-brake (w = s − s*, tf = 8): s* = 0.5: Pv = 0.006743 > Pvr = 0.006405 (5%); s* = 1.5: 0.0914 > 0.0788 (14%), with cap none/0.6. So S holds numerically in the dive-brake regime, where no plateau forms. (tf = 20 rows were stopped: machine load.) Local solver with multistart: evidence, not proof |
| a6_gap_heuristic.py | Size of the B* gap under r_z ≥ 0 (cost to cancel W_h = −X_h + B_h by brake tilts) | GTPL: 2e-4 m at s* = δ/ω; 1.2e-2 m at the S2 limit (tf = 8); 1.0e-2 m at tf = 12. Sign fixed per [proof]: the late tail partially cancels the dive moment. `results_a6.txt` |

---

## 7. Slice lemma S (≡ Theorem D ≡ closing the frame-rotation loophole) and the coning threat

**Reduction.** Take the glide-slope apex at r(tf), which makes the problem lateral-translation invariant. Then main's Theorem D (min-landing-error,
state-linear relaxations) and the frame-rotation loophole (§2.2) both reduce to the following lemma.
S: *some r0_lat-slice of F at fixed (r0z, v0) is nonconvex.*
Cleanest instance: v0_lat = r0_lat = 0. There L is rotation-invariant, so S ⇔ 0 ∉ L ≠ ∅. A nonempty rotation-invariant convex planar set contains 0.
Face formulation: let Pv = max of a vertical functional over G_v = F ∩ {v0_lat = 0}, and Pvr = the same with r0_lat = 0 added.
**Pv > Pvr strictly ⇒ S** holds at the vertical data of a Pv-maximizer. The midpoint lemma applies to G_v, which is rotation-invariant.

**Why B\* does not transfer.** The v0_lat = 0 endpoint constraint has a PMP multiplier λ ∈ R² (a constant lateral primer).
The pointwise-optimal d then depends on b's azimuth relative to λ, not only on Φ. So the envelope ⇒ meridional argument is lost.

**Coning vs S-turn: small-angle quantification** (pure-dive weight w ≡ −1, α = 0, constant a; tilt vectors β (body) and θ (thrust) in R²,
|β'| ≤ ω, |θ − β| ≤ δ; waste ∝ ∫|θ|²). Write Ω := ωtf. Mean of |θ|² over [0, tf] for the outward gimbal θ = β + δβ̂:

| strategy | Δv_lat = 0 | Δr_lat = 0 | mean |θ|² |
|---|---|---|---|
| rigid ramp (Thm B face) | no | no | Ω²/3 + δΩ + δ² |
| planar S, 1 crossing (triangle, amplitude Ω/4) | yes | **no** (lands offset) | Ω²/48 + δΩ/4 + δ² |
| planar, 2 crossings (amplitude Ω/6) | yes | yes | Ω²/108 + δΩ/6 + δ² |
| coning at ρ = Ω/(2π+1) after a ramp (one revolution) | ≈ yes | ≈ yes (phase/modulation) | ≈ 0.0162 Ω² + 0.236 δΩ + δ² |
| coning on a tilt cap θc, tf ≫ (θc + 2π sin θc)/ω | yes | yes | → (θc + δ)² = the *unconstrained* capped max |

Readings:
1. Pure dive, no cap: the best known Pv candidate (1-crossing S) beats the best known Pvr candidate (coning) by about 0.005Ω² + 0.014δΩ. This is a **lower** bound on neither side, so it is not a proof.
2. Main's estimate is right in spirit. Coning beats multi-crossing planar maneuvers for Pvr. So any proof of S must beat coning, not just planar S-turns.
3. **Pure dive with an active tilt cap and long tf: S FAILS at that face.** The unconstrained maximizer is "ramp to the cap, then sit on it". On the plateau the azimuth is free, with |ψ'| ≤ ω/sin θc. If the plateau lasts long enough to cancel both lateral moments, then Pv = Pvr = U, and the axial point is attained.
   This is exactly the plateau failure of rigidity flagged by [adversary-6dof]. Such faces cannot witness S.
4. **Dive-then-brake with small s\* (my recommended witness for S).**
   - The waste window [0, s*) is shorter than one coning revolution at any tilt it can reach (Φ ≤ ωs*, period 2π sin Φ/ω > s*... ). Coning is not available there.
   - In the late window (w > 0), lateral cancellation is cheapest with the gimbal alone at b ≈ e_z. That costs only *second order*: loss w a(1 − cos ε) for lateral ε.
   - Early outward tilt gains first order: sin δ sin Φ per unit time. So every Pv-maximizer has early lateral impulse ℓ_e ≠ 0 (marginal argument: linear gain beats quadratic cancellation cost).
   - For fixed b, the late subproblem is convex after Lyapunov/Aumann. Its pointwise optimum with multiplier λ gives lateral contributions in a single direction ≈ −ℓ̂_e, with nonnegative weights concentrated where w is large (s ~ tf).
   - Hence r0_lat ≈ t̄·ℓ_e + O(s*² a_max) with t̄ = O(tf), which is ≠ 0 for s* small. So Pv > Pvr and S holds.
   - This is a **sketch**. The missing pieces are a quantitative lower bound on |ℓ_e| at every maximizer, and control of b's tilt in the late window. The regime is s* ≪ tf with no plateau (ωs* < θc).
5. Practical relevance for GTPL: the dive-then-brake witness has mild tilts and lands with r_z > 0 (B* conditions). Its slice "dent" is second-order small: a strict gap, but tiny. A quantitative bound would be needed before claiming a usable ε.

**Status of S:** OPEN.
- Expected TRUE in the dive-then-brake regime. a5 small-angle: gaps of 5% at s* = 0.5 and 14% at s* = 1.5 (tf = 8, with or without cap).
- FALSE at capped long-plateau pure-dive faces. a5: tf = 20, cap 0.6 rad gives a gap of exactly 0, with coning on the cap.
Numerical tests:
- [numerics] s1_slice.py: exact mass, r_z ≥ 0, planar vs 3D, about 35% coning starts, tf ∈ {2, …, 12}, cap none/30°.
- mine: a5_coning.py, small-angle with planar/coning/random starts.


---

## 8. Attack on [proof] math/02 §10 (rigorous B*) and §11 (Theorem D, Def 11.1, Prop 11.2)

**§10 SURVIVES.** I checked Steps 1–7 line by line: the bound d_z ≥ cos(δ+ωs) on the dive, attainment, the late-throttle comparison, state-constraint
verification (S2)/(S3), the support bound with c_τ = b(ϑs*), and the h_τ estimates giving γ_X = (5/32) a10 sin δ s*².
The Cauchy–Schwarz brake bound and the max(η, f(η)) ≥ η0 step also hold. Cor 10.4 (free tf) is correct: ℓ is horizon-independent up to κ(t), and Step 6 holds at every horizon.

**Quantitative thinness: NEEDS FIX (the most important practical finding).**
- The restriction (S1) ωs* ≤ δ caps s* at δ/ω = 0.65 s for GTPL, and the gap at this face scales like s*⁴.
- The real gap is ≈ |X_h|²/(2B0): the cheapest lateral-zero competitor keeps the dive and cancels the weighted lateral moment by small brake tilts, and Cauchy–Schwarz is tight.
- a6, sign-corrected (W_h = −X_h + B_h), gives 2e-4 m at s* = 0.654 s, 1.4e-3 m at 1 s, 1.2e-2 m at the S2 limit (tf = 8), and 1.0e-2 m at tf = 12.
- So the envelope version (now [proof] §10.6, B*-env, checked by me: SURVIVES, but it should state ωs* − δ ≤ π/2, which (S2') implies) buys about 2 orders of magnitude. Even so, **every altitude-feasible face found so far has a gap of at most centimetres**, because GTPL's full-throttle T/W is low (A_b = 2.7 m/s²) and the brake must be long.
- The metre-per-second gaps of Thm Q exist only at underground faces.
- Consequence: the qualitative impossibility (exact / a.e. / feasibility-form) is proven under altitude constraints. "No ε-lossless relaxation" is proven only for ε ≈ 1e-5 m (rigorous), with ≈ 1 cm expected at these faces. *Practical* impossibility for GTPL is not established. An ε-lossless outer relaxation with ε at the centimetre level is not excluded by anything we have.
- Requested: [numerics] to compute dist(θ_m, F^X) directly and search other R_π-invariant faces of F^X (e.g. weights with two sign changes, glide-slope-active faces) for a larger gap.

**§11.**
- Def 11.1 and Thm D are correct. The proof is mixture-closure of an affine readout plus a convex penalty that vanishes on conv(genuine).
- Def 11.1's exclusions (i)–(iii) match thread theorem-D (4). One more case to list under (i): epigraph lifts, where the cost is a lifted coordinate constrained jointly with moment variables, as in the Prop 11.3 hull trick.
- Cor D.1 is correct, but its cost penalizes v(tf) softly, which is not the LCvx soft-landing problem, and its gap is ~η0/((1+tf)√(1+s*²)) ~ 1e-6 m.
- Prop 11.2 is a correct reduction of S. I agree S is open. The small-angle evidence (a5) favours S at short pure-dive horizons even with coning. At long capped plateaus S fails at those faces (§7). [numerics] s1_slice.py is the decisive test.


**Update (from [numerics] s1_slice.py: exact 3D model, exact mass, r_z ≥ 0, about 35% coning starts).** These are strict gaps, with Pvr worse than Pv:
- Pure dive: 0.19 m/s at tf = 4; 0.98 m/s at tf = 8 with no cap; 0.69 m/s at tf = 8 with a 30° cap.
- Dive-then-brake: 0.016 m at tf = 4 and 0.009 m at tf = 8, in units of the functional.
- Coning narrows the planar gaps by at most about 30% and never closes them.

The tf = 8 capped result is consistent with §7 item 3. Filling the dent requires the plateau to fit one revolution on the cap, i.e. tf ≳ (θc + 2π sin θc)/ω ≈ 9.2 s for θc = 30° and ω = 0.4. That is not met at tf = 8. a5 shows the dent closing at tf = 20 with a 0.6 rad cap.

So S is numerically TRUE at every face tested in the exact model. The expected failure region (capped, tf ≳ 10–20 s, pure dive) is untested in 3D. For a proof of S, use a dive-then-brake face or a short-horizon face.
