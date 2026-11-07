# [numerics] report (≤1 page)

**Scope.** These are tasks 1–2 of the brief plus requests from main, adversary and proof agents. Tasks 3–4 (3DOF LCvx rate statistics, 5DOF guidance prototypes) were deferred by the orchestrator and **not run**.
Code is in `numerics/`, with details in `numerics/README.md`.
Method: casadi/ipopt multistart on an **inner** discretization, so every NLP solution is an admissible trajectory and every reported distance is an *upper* bound. Mass depletion uses the exact log-mass velocity gain. GTPL parameters come from `context/vehicle.md`.

**1. Theorem B (M1, no state constraints) is confirmed, with no contradiction.**
GTPL, tf = 2 s, ω = 30°/s: dist(M, R) ≈ 2.2 m/s while |P_x| = 6.8 m/s. The value is stable under refinement: N = 10→80 gives 2.38→2.18.
Gap law over 39 configurations: dist/|P_x| ≈ 0.31·ωtf. It is nearly independent of δ, ρ1/ρ2 and α, and scales with ρ1.
[proof]'s ball bound is a rigorous lower bound. It equals 0.81–0.83 × the NLP value in every configuration, so the true gap is pinned to within 18%.
Mars-like set: 0.2/2.2/6.0 m/s at tf = 2/5/7.5 s.

**2. Beyond the proven regime (state-unconstrained).**
- The set stays nonconvex for a long tf without a tilt cap (13–19 m/s, with inverted flight), for the tent profile (6.2 m/s at tf = 5), for the accel-limited axis M1A, and for the torque-coupled TVC model M3 (3.7 m/s, 3D, tf = 2).
- With a 30° tilt cap and long tf, the bottom-face gap shrinks because the axis can slide in azimuth along the cap.
- The math/00 hole point is underground. Under free tf it is reached for tf' ≥ 4 s, so a free-tf statement needs B*.
- With ρ1 = 0 no gap was found inside the regime δ+ωtf ≤ π/2 (weak test), but a gap appears beyond it.

**3. Physically admissible data (altitude path constraint r_z ≥ 0), GTPL, ω = 0.4 rad/s.**
- **Slice lemma S.** In 3D, including coning starts, there are strict Pvr > Pv gaps in every case.
  - Pure dive: 0.19 m/s (tf = 4) and 0.98 m/s (tf = 8).
  - Dive-then-brake: 0.016 m and 0.009 m.
  - With a 30° cap the pure-dive gap goes 0.69 → 0.50 → **0.11 m/s** at tf = 8 → 12 → 20, while the planar gap stays at 0.8. The Pvr optimizer cones through a full 359° azimuth sweep, so the adversary's coning-fill mechanism is real at long horizons on a cap.
- **B\* face.** The rotation-midpoint gap is 0.012 (tf = 4) and 0.007 (tf = 8), stable in N. It is real but about 1 cm/s.
- **Face scan of F^X.** The pure-dive face under r_z ≥ 0 is pinned at **r0z = 0, v0z > 0** (ground-launched hop data). Its rotation-midpoint gap is **0.65 (tf = 4) and 2.9 (tf = 8)** weighted m/s, the largest physically admissible gap found.
  Concretely, launched straight up at 8.2 m/s with tf = 4 s, the vehicle cannot land back on the pad but can land about 21 m away. The cause is that a1 = ρ1/m = 5 < g.
  The fast-and-low and upright faces have gap 0.
- **Realistic in-air descent data** (50 m altitude, −5 m/s, tf = 7 s, 4 m/s crossrange): the lateral landing set L is about 104 m wide, and no dent exceeds solver noise (≤ 0.016 m).

**Bottom line for "possible vs impossible".**
- Numerically, F_tf is nonconvex in every rate-limited model tested (M1, M1A, M3, tent, free tf via B*). This holds with r_z ≥ 0 too, so a uniform state-linear convex relaxation cannot be lossless; the numerics agree with A + B/B*/S.
- The practically sized nonconvexity (≥ 0.1 m/s) lives in near-liftoff and boundary-of-feasibility data.
- For typical in-air descent conditions the observed nonconvexity is centimetre-level or invisible. An ε-lossless uniform relaxation with ε of a few cm/s on descent data has **not** been ruled out numerically.
- Caveats: multistart NLP cannot certify global optima, and "no gap found" is weak evidence.
