# [numerics] report (≤1 page)

**Scope.** Tasks 1–2 of the brief, plus requests from main, adversary, proof-s and redteam-lift. Tasks 3–4 (3DOF LCvx rate statistics, 5DOF guidance prototypes) were deferred by the orchestrator and **not run**.
Code: `numerics/` (see `numerics/README.md`).
Method: casadi/ipopt multistart on an **inner** discretization, so every NLP point is an admissible trajectory and every distance is an upper bound. Mass depletion uses the exact log-mass velocity gain. GTPL parameters come from `context/vehicle.md`.

**1. Theorem B (M1, no state constraints) is confirmed; nothing contradicts it.**
- GTPL, tf = 2 s, ω = 30°/s: dist(M, R) ≈ 2.2 m/s against |P_x| = 6.8. Refining N from 10 to 80 moves it from 2.38 to 2.18.
- Gap law over 39 configurations: dist/|P_x| ≈ 0.31·ωtf, nearly independent of δ, ρ1/ρ2 and α, and ∝ ρ1.
- [proof]'s ball bound, a rigorous lower bound, is 0.81–0.83 × the NLP value everywhere.
- Mars-like set: 0.2 / 2.2 / 6.0 m/s at tf = 2 / 5 / 7.5 s.

**2. Beyond the proven regime (no state constraints).** R stays nonconvex for:
- long tf (13–19 m/s, using inverted flight);
- the tent profile (6.2 m/s);
- the acceleration-limited model M1A;
- the torque-coupled model M3 (3.7 m/s).

With a 30° tilt cap the bottom-face gap shrinks through azimuthal sliding. The math/00 hole point is underground and is reached under free tf, so free tf needs B*. With ρ1 = 0 no gap appears inside δ+ωtf ≤ π/2.

**3. Physically admissible data (r_z ≥ 0), GTPL, ω = 0.4 rad/s.**
- **Slice lemma S** holds numerically in 3D with coning starts:
  - pure-dive Pvr − Pv gap: 0.19 m/s (tf = 4) and 0.98 m/s (tf = 8);
  - dive-then-brake: 0.016 m and 0.009 m;
  - on a 30° cap: 0.69 → 0.50 → 0.11 m/s at tf = 8 → 12 → 20 (planar ≈ 0.8). The coning fill is real but partial; at tf = 20 the optimizer sweeps 359° of azimuth.
- **B\* face:** rotation-midpoint gap 0.012 / 0.007, stable in N. Real, but about 1 cm/s.
- **Largest witness: the pure-dive face**, which is pinned at r0z = 0, v0z > 0 (ground-launched hop). Its gap is **0.65 (tf = 4) and 2.9 (tf = 8)** weighted m/s.
- **Landing set L in meters**, at the pad with v0_lat = 0 and tf = 4: L is an annulus whose hole, landing back on the pad, has radius **0.55 → 5.0 m** as v0z goes from 7.75 to 7.90 m/s. The bad window is v0z ∈ (7.73, 7.92].
  - Torque-coupled M3 at v0z = 8.0: hole of 1.74 m.
  - Tilt-angle-rate-only model: L is convex.
- **Realistic in-air descent** (50 m, −5 m/s, 4 m/s crossrange, tf = 7): L is about 104 m wide with no dent above solver noise.

**4. Candidate convexification (degree-2 Shor lift, CSD2):**
- **Exact on 21 of 22 instances**, including all realistic above-ground targets.
- **Lossy on one near-dent instance:** SDP optimum of rank 4 at 0.02753, against a best 3D value of 0.02823 over 480 restarts (2.5% gap). So Conjecture CSD2 is false in general, but the lift remains an a-posteriori certificate when the optimum has rank 3.

**Bottom line.**
- Every rate-limited model tested (M1, M1A, M3) gives a nonconvex F_tf, also under r_z ≥ 0. That is consistent with "no uniform state-linear convex relaxation is lossless" (A + B/B*/S).
- The nonconvexity is metre-scale only near the edge of feasibility: hop or near-liftoff data, and slivers about 0.2 m/s thick.
- For typical in-air descent data it is cm-level or invisible. An ε-lossless relaxation with ε of a few cm/s on descent data is **not** excluded by the numerics.
- The tilt-angle-rate-only model looks convex.
- Caveat: a multistart NLP cannot certify global optima, so "no gap found" is weak evidence.
