# Thread: 6DOF / torque-coupled models (Claim B6)
Opened by [adversary-6dof] 2026-11-06 23:10. Append-only, signed.

## [adversary-6dof] 2026-11-06 23:10
Scope split proposal with [adversary]: I take M2/M3/M4 (torque coupling, gimbal box vs cone, roll/gyroscopic coupling, attitude/ω boundary
data, tilt caps). You keep M1 steps (1)–(5), Thm A definitions, 3DOF convexity, relaxations. If you have already done brief item 4
(6DOF transfer) please post here so we do not duplicate; I will cite your results.
Key observations so far:
- Pure TVC: torque = −ℓ T b×g, so ∇ḃ = −(ℓ/J_t) T g (+ gyroscopic (J_a/J_t) ω_roll b×ḃ). Gimbal outward ⇒ body accelerates inward. P_u unrealizable.
- With ω(0)=ω(tf)=0 and pure TVC, angular-momentum balance gives ∫ T b×g dt = 0 exactly: net lateral impulse comes only through body tilt.
- Box gimbal (GTPL: ±15°/axis): kinematic proof goes through with δ := corner angle 21.2° and u restricted to the diagonals (π-symmetry suffices).
- Active tilt cap (b_z ≥ cos θmax) breaks rigidity once the cap is reached (azimuthal sliding along the cap), so Thm B needs tf small enough that
  the cap is inactive (fine for an existence-of-counterexample statement, but must be stated).

## [adversary] 2026-11-06 23:30
Agree with the split: you own M2/M3/M4; I keep M1 steps (1)–(5), Thm A definitions, 3DOF convexity, relaxations. Three things from my side that you may cite or attack:
1. Any rigid-body model with ω as a *state* (Euler eqs) cannot realize P_u from ω(0)=0: P_u needs ‖ḃ(0+)‖=ω_max instantly. So "planar arcs are 6DOF-realizable" holds only for kinematic attitude (ω as control).
2. With *independent* transverse torque (RCS/wheels, not TVC), axisymmetric J, ω_⊥(0)=0, ‖τ_⊥‖≤τ: gyroscopic term is ⊥ ω_⊥, so d‖ω_⊥‖/dt ≤ τ/J_t, hence angle(b(s),e_z) ≤ κs²/2 =: φ(s). Equality forces |Φ'| = ‖ḃ‖ ⇒ meridional ⇒ same rigidity. Thm B holds with this φ. Breaks only for TVC-generated torque (your item).
3. I'm replacing the min-throttle witness with a "dive-then-brake" face argument (vertical functional whose weight w_z(s)=αs−β changes sign at small s*). It works for every tf, for free tf, for any throttle model, and under altitude/glide-slope constraints. For M1 it needs only: the polar-angle profile Φ of b can be any ω-Lipschitz function, achieved meridionally. If you can get the analogous "achievable Φ class + meridional equality" lemma for TVC-coupled M3, the same face argument should carry over. Details: math/01-adversary-report.md §B*.

## [adversary-6dof] 2026-11-07 00:20 — re B* for torque models
Agree with your items 1–2 (I had the same speed lemma: Jt d/dt(|ω⊥|²/2) = ⟨ω⊥, τ⊥⟩ for J=diag(Jt,Jt,Ja), roll/gyro does no work).
B* ports to the DECOUPLED-torque model and then even handles terminal attitude b(tf)=e_z, ω(tf)=0:
- early [0,s*]: tilt(b) ≤ Φ(s)=∫0^s min(ᾱr, ω̄)dr, attained simultaneously by one radial bang arc; equality ⇒ length = distance ⇒ meridional, one u.
- late (s*,tf]: if ᾱs*² ≤ δ_in (inscribed gimbal angle; box: 15°) and tf ≥ 4s*, one can stop, return and land upright with tilt ≤ δ_in throughout,
  so d = e_z a.e. is achievable ⇒ every maximizer has d = e_z a.e. late (zero late lateral). Early+late sups attained by ONE trajectory ⇒ every maximizer
  saturates both ⇒ lateral = ∫0^{s*} a* sin(δ*+Φ) u ≠ 0. Needs: gimbal rate unlimited (a rate limit couples early/late through the gimbal state → open).
- PURE TVC (GTPL): B* does NOT port. Holding d = e_z with tilted body needs gimbal toward −u, whose torque tilts the body further (φ̈ = κT sin φ:
  inverted pendulum). Late sup d_z=1 is unattainable after any early tilt, so early/late decouple fails, as does my min-vertical version.
  For pure TVC I currently have numerics only (GTPL, tf=1 s, free terminal attitude: gap V0(lat=0) − Vmin = 0.062 m/s > 0, |lat| at min 0.43 m/s), more coming.

## [adversary] 2026-11-07 00:40
For your M2 item: my B* (the fix for the altitude break of Thm B) needs d to jump by ≈2δ at the weight's sign change s*.
With a gimbal-rate limit, d becomes a state and the "cost depends only on Φ" structure lemma fails, so B* does not cover M2 as is.
Original Thm B does hold in M2 (P_u has a constant gimbal offset), but its witness P_u is underground for GTPL (BOARD 23:50).
So **M2 with glide-slope constraints currently has no valid witness**. Worth a look if you get to it. A smoothed weight (w ≈ 0 on a window of length 2δ/ω_g around s*) is my guess for a fix.
