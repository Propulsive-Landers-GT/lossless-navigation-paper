# [lit-review] Final report (2026-11-06)

Full review: `literature/review.md`. Bibliography: `literature/refs.bib` (about 110 entries; DOIs Crossref-checked; UNVERIFIED ones flagged).

## Bottom line
**Nobody has published LCvx for 5DOF/6DOF (attitude-rate-limited) powered descent, and nobody has proved it impossible.** Search covered Crossref, the full arXiv listing for "lossless convexification" (2019–2026), and extended web searches. An impossibility theorem for uniform convex relaxations would be new.

## Facts that support the impossibility conjecture
1. **Linear dynamics everywhere.** Every LCvx theorem assumes LTV dynamics with the thrust direction as a *free control*. The proofs rest on the PMP plus controllability or normality (Conditions 1–6, exact statements in review §1).
   - The tutorial [Malyuta et al. 2022 CSM] says so explicitly. The only nonlinear result [Blackmore–Açıkmeşe–Carson 2012 SCL] keeps the dynamics nonconvex and needs MILP.
   - That result also does not cover state-dependent control sets (gimbal cone about the body axis).
   - TCST 2013 *assumes* translation/attitude decoupling ("attitude maneuvers … done very quickly").
2. **The mechanism is Lyapunov/Aumann.** Linear reachable sets with nonconvex control sets are convex and equal the relaxed ones [Aumann 1965; Yang–Liu 2022 Automatica]. A rate-limited thrust axis b ∈ S² destroys the linear structure.
3. **Thm B is Dubins geometry.** Bae et al., *Automatica* 178 (2025) 112359, show the position reachable set of 3D curvature-bounded curves is the solid of revolution of the planar Dubins set (Cockayne–Hall 1975).
   - With δ = 0 and constant a, our velocity-increment set R is exactly this set. The planar midpoint argument is elementary (review §4.2).
   - Neither paper states convexity, so we must prove it ourselves.
4. **Filippov–Ważewski.** Convexifying the velocity set changes the reachable set only up to closure. No pointwise or chattering relaxation of the state-dependent thrust set can make R convex.
5. **No 6DOF method claims exactness.** All are local: SCvx, PTR, dual-quaternion SCP, ACCD, indirect. The only explicit 5-DOF model (Jung et al. 2025, pitch/yaw/throttle lags) uses SCP.
6. **A second, cost-based route.** If the relaxation's objective is jointly convex in (θ, y), uniform losslessness also forces the optimal fuel cost J*(r₀, v₀) to be convex [Fiacco–Kyparisis 1986].

## Things that threaten it, or that the definitions must handle
- **A. Berning, Strohl, Bieniawski, "Lossless Convex Guidance for Lunar Powered Descent", AIAA SciTech 2023 (DOI 10.2514/6.2023-2004).** A survey reports it uses the LCvx framework with *maximum tilt rate, tilt acceleration and thrust ramp rate* in one SOCP. **I could not access the full text.**
  - Likely it bounds the rate of the *tilt angle* (or of the thrust vector) and does not prove losslessness.
  - If only the tilt angle from vertical is rate-limited, the azimuth is free, step (4) of Thm B fails, and M lies in the closure of R. That would be a genuinely different, possibly LCvx-able, constraint.
  - **Action: someone with AIAA ARC access should read it. Numerics should test the "tilt-angle-rate only" variant.**
- **B. Occupation-measure LPs** (Vinter 1993; Lasserre–Henrion–Prieur–Trélat 2008).
  - They are convex per instance, and θ enters as δ_θ, so they are *not* jointly convex in (θ, y) and evade Thm A.
  - They equal the original value only if the velocity sets are convex (LHPT Thm 2.3). Otherwise they give the relaxed value. A gap is possible only in abnormal cases (Palladino–Vinter 2014).
  - Moment truncations are approximate.
  - **The impossibility theorem must state "uniform = jointly convex in (θ, y)".**
- **C. Meaning of "lossless" in practice.** Literature LCvx is per-instance and often a *sequence* of convex programs (t_f line search, prioritized stages). It may need ε-perturbed dynamics (TCST 2013's ω̂). The GFOLD SOCP is lossless only modulo a Taylor approximation of the e^{−z} mass bounds. Discrete-time LCvx can fail at up to n_x−1 nodes (Luo–Echigo–Açıkmeşe, Automatica 2026; tight).
  - Numerics: allow for these effects before declaring a counterexample.
- **D. Small-time convexity results** (Polyak 2001; Gusev–Osipov 2019) need small *L²* control budgets around zero. With min throttle ρ₁ > 0 they do not apply. This is why ρ₁ > 0 matters, and the adversary should probe ρ₁ = 0.

## Positive route (Thm C)
With b(t) fixed, the thrust set is a time-varying cone ∩ annulus. Support:
- TCST 2013 Lemma 3 (pointwise extreme points).
- Harris 2021 TAC (exact extreme-point relaxations under normality, including control-affine nonlinear systems).
- Malyuta–Açıkmeşe 2020 (semi-continuous inputs, strong observability).
- Yang–Liu 2024 TAC (augmented convex-hull relaxation).

The analytic zero-set Lemma 2 of TCST 2013 must be replaced by an explicit primer-vector non-degeneracy condition p(t) ≠ −α b(t), as planned in math/04.

## Unresolved items
- Full texts not read: Berning 2023, Lin et al. 2026 (DOI 10.2514/6.2026-112394; metadata only, GT authors), Reynolds–Mesbahi 2020 (planar optimal descent with attitude; worth reading for extremal structure).
- Chinese-language full texts: none accessed; nothing relevant surfaced in English abstracts.
- UNVERIFIED (no DOI): Ważewski 1961, Patsko–Pyatko–Fedotov 2003, Polyak 2004, the GFOLD 2013 AAS flight-test paper, and Harris's 2014 PhD thesis.
