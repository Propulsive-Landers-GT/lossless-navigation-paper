# numerics/ — numerical evidence for the 5DOF LCvx impossibility question

Owner: [numerics]. Environment: `numerics/.venv` (Python 3.14, numpy, scipy, matplotlib, cvxpy with CLARABEL/ECOS,
casadi 3.8 with ipopt). Compute budget (comms/PROTOCOL.md): `runner.py` uses 2 worker processes by default
(`NUMERICS_WORKERS`) and sets BLAS threads to 1.

Tasks 3 and 4 of the brief (3DOF-LCvx attitude-rate demand statistics, 5DOF-aware guidance prototypes) were
**deferred by the orchestrator**. Only the lossless question (tasks 1 and 2, plus follow-up requests) was run.

## Method

- `models.py`: discretized NLPs in casadi SX, solved with ipopt multistart. Every model returns the velocity and position increments
  `Dv = ∫a d ds` and `Dr = ∫(tf−s) a d ds`. The boundary data follow from them by an affine map:
  v0 = g tf e_z − Dv, r0 = Dv tf − Dr − g tf²/2 e_z. So nonconvexity of the set Q = {(Dv,Dr)} is nonconvexity of F_tf.
  - **M1** (kinematic, full-direction rate limit, angle(b(s),b(s')) ≤ ω|s−s'|), planar and 3D.
    This is an **inner discretization**. b is piecewise geodesic with node-to-node angle ≤ ωh, and d_k must lie within δ of both b_k and b_{k+1}.
    Spherical caps are geodesically convex, so every discrete solution is an admissible continuous-time trajectory.
    The log-mass velocity gain (1/α) ln(m_k/m_{k+1}) is exact.
    Consequence: an NLP distance is an **upper bound** on the true distance to R.
    Options: `tent` (b(tf)=e_z), `tilt_max`, `alt` (r_z(t_k) ≥ 0 at every node, from the implied boundary data), and 3D coning initial guesses.
  - **M1A**: planar, angular-acceleration-limited axis, gimbal decoupled.
  - **M3**: torque-coupled TVC rigid body. ẇ = −(L T/J) b×g, d = √(1−|g|²) b + g, |g| ≤ sin δ, body-frame gimbal rate ≤ ġ_max, optional |w| ≤ ω_max.
    Multiple shooting, RK4. Planar and 3D.
  - **MT**: tilt-angle-rate-only variant. The polar angle of b is ω-Lipschitz and the azimuth is free.
- `runner.py`: process-pool multistart with streaming results.
- Parameters: GTPL central values from `context/vehicle.md` (m0 80 kg, T 400–1000 N, α = 1/(180 g0) = 5.66e-4 s/m, δ 15°,
  J⊥ 63.6 kg m², L 0.589 m, gimbal slew 100°/s). The usable body rate is 0.3–0.5 rad/s, and ω = 0.4 rad/s is used in the constrained studies.
  Mars-like set: m0 1905 kg, Isp 225 s, 6×3100 N cos 27°, throttle 0.3–0.8, g = 3.71, after Açıkmeşe & Ploen 2007.
  Its attitude numbers are assumptions.

## Results (details and numbers in the BOARD posts signed [numerics])

### 1. Theorem B (M1, state-unconstrained) is confirmed. `t1_thmB.py`, `bounds.py`
- GTPL, tf = 2 s, ω = 30°/s (δ+ωtf = 75°): |P_x| = 6.77 and M_z = 6.77 m/s, and dist(M, R) = 2.18–2.23 m/s.
  Discretization check: planar N = 10/20/40/80 gives 2.38/2.27/2.21/2.18; 3D N = 10/20/40/60 gives 2.38/2.26/2.21/2.19.
  The nearest point sits about 2.2 m/s above M, close to the axis. 3D controls gain essentially nothing over planar ones.
  Plots: `results/t1_R_section.png`, `results/t1_N_convergence.png`.
- Gap law over 39 configurations (ω 10–120°/s, ωtf 15–75°, δ 2–30°, ρ1/ρ2 0.05–1, α 0–5e-3):
  **dist(M,R)/|P_x| ≈ 0.31·ωtf**. The gap is nearly independent of δ, ρ1/ρ2 and α, and scales linearly with ρ1 (so it goes to 0 as ρ1 → 0). Plot: `results/t1_gap_sweeps.png`.
- Sandwich: [proof]'s ball bound max_τ G(τ) − |M| is a rigorous lower bound, and the NLP gives an upper bound. LB/NLP = 0.81–0.83 on all 39 configurations, with 0 violations.
- Mars-like, ω = 10°/s: tf = 2/5/7.5 s gives dist = 0.23/2.2/6.0 m/s.

### 2. Beyond the proven regime (state-unconstrained). `t2_beyond.py` (quick runs, low restart counts)
- **Long tf**, M1, no tilt cap: the generalized midpoint gap is 2.1/13.5/18.6 m/s at tf = 2/4/8 s. This regime uses inverted flight.
  With a 30° tilt cap the gap is 1.15/1.56/0.35 m/s. It shrinks because azimuthal sliding along the cap breaks rigidity.
- **Tent** profile b(tf)=e_z: dist(M_tent, R) = 0.66 (tf=2) and 6.24 m/s (tf=5).
- **Free tf**: the math/00 hole point (tf0 = 2 s, which is underground: r0z = −14 m, v0z = +12.8 m/s) is reached for tf' ≥ 4 s.
  So the math/00 witness does not survive free final time. B* is needed there. Plot: `results/t2_free_tf.png`.
- **ρ1 = 0**: no gap found in regime. A gap of 13 m/s appears beyond π/2 (tf = 6, no cap). Caveat: the random-combination index is weak.
- **M1A**: gaps 0.95–1.7 m/s (tf=2) and 8.8–11.9 m/s (tf=4).
- **M3** (torque-coupled, GTPL): every min-Dv_z solution has lateral ≠ 0.
  Gap 3.7 m/s (3D, tf=2). Planar: 0.80–7.98 m/s at tf = 4, depending on the rate cap. R_M3 is nonconvex when there is no altitude constraint.

### 3. With the altitude constraint r_z(t) ≥ 0 (the physically relevant F^X), GTPL, ω = 0.4 rad/s
- **Slice lemma S** (`s1_slice.py`): v0_lat = 0, comparing Pv (only that) with Pvr (also r0_lat = 0).
  There are strict gaps in 3D, with coning guesses, in every case:
  - pure dive: 0.19 m/s (tf=4), 0.98 m/s (tf=8), 0.69 m/s (tf=8 with a 30° cap);
  - dive-then-brake (s* = 1 s): 0.016 m (tf=4) and 0.009 m (tf=8).

  Coning narrows the planar gaps by at most about 30%. `results/s1_slice.json`, `.png`.
- **B\* gap** (rotation midpoint of the divebrake face, r_z ≥ 0): weighted distance 0.010/0.011/0.012 at tf = 4 (N = 20/28/40)
  and 0.0063/0.0070 at tf = 8 (N = 20/40). This is real and stable in N, but **tiny**: about 1 cm/s, roughly 0.3–0.5% of the face's |v0_lat|.
- **Dent of L in meters** at the Pv-optimal vertical data: the lateral landing set there is a thin annulus.
  Its inner radius is ≈ |r0_lat| of the Pv optimizer: 1.47 m (divebrake, tf=4), 2.35 m (divebrake, tf=8), 6.8 m (dive, tf=4), 27–39 m (dive, tf=8).
  These are extreme vertical data, on the edge of vertical feasibility. The set of bad boundary data is a sliver whose thickness in the vertical functional is the Pv/Pvr gap.
- **Realistic interior data** (`d1_landing_set.py`, quick run): r0 = (0,0,50) m, v0 = (4,0,−5) m/s, tf = 7 s, M1.
  L is 104 m wide, and max dist(q, L) over 106 grid points q ∈ conv L is 0.016 m, at isolated points (solver noise). **No dent at realistic interior conditions.**

### 4. Tilt cap, long horizon (`s3_longcap.py`) and face search (`s4_faces.py`)
See the BOARD for the latest numbers (requested by [adversary] / [main]).

## Files
| file | purpose |
|---|---|
| models.py | M1/M1A/M3/MT NLP builders, extreme arcs, parameter sets |
| runner.py | multistart pool (2 workers) |
| t1_thmB.py, replot_t1.py, bounds.py | Task 1: Theorem B, gap sweeps, ball-bound sandwich |
| t2_beyond.py | Task 2: long tf, tent, free tf, slices, ρ1=0, M1A, M3, rotation faces |
| s1_slice.py, s2_followup.py | slice lemma S, B* gap, N-checks, inner radius |
| s3_longcap.py | long-horizon tilt-cap coning test |
| s4_faces.py | scan of R_π-invariant vertical faces of F^X for the largest gap |
| d1_landing_set.py | lateral landing set L for fixed realistic (r0,v0) |
| results/ | json/png outputs |

Caveats: multistart NLP cannot certify global optima. Every reported distance is an upper bound (inner discretization),
and "no gap found" is weak evidence. The underground-witness issue (math/00 P_u starts below ground for GTPL, @adversary)
means that §1–2 bear on the abstract set F_tf, while §3 bears on the physical problem.
