# numerics/independent-check: a second look at the impossibility result

November 2026. I read the shared 40-page PDF of the paper (dated 7 November 2026, an earlier build than the
committed `paper/main-share.pdf`) on its own, re-derived the proofs by hand, and tried to break the theorems with
a simulator written from that PDF alone (`m1.py`). Only after that did I open this repository,
build the Lean project and compare its statements with the printed ones.

The headline result held. One hypothesis was missing from the printed Theorem B*.

## The missing hypothesis in Theorem B*

The printed theorem asked for (S1) ωs* ≤ δ, (S2) and (S3). Its proof in Appendix B also needs δ + ωs* ≤ π/2:

- Step 4 takes minimum throttle on the dive as the maximiser of the face functional. That holds only while
  cos(δ + ωs) ≥ 0. Once the thrust points below the horizon, more throttle raises the face value.
- Step 5 uses v̇_z ≥ −g0 on the dive, which needs d_z ≥ 0.

(S1) gives δ + ωs* ≤ 2δ, so the proof was complete only for δ ≤ 45°. `c2_bstar_delta80.py` is a case with
δ = 80°, ω = 1 rad/s, s* = δ/ω where the printed (S1)-(S3) all hold. There the written witness reaches a face
value of 7.20 against a maximum of 15.38, and the control that does reach the maximum starts 4.8 m below ground
(`c2_out.txt`).

The conclusion of the theorem is still true in that case, because a smaller s* satisfies every condition
(`exists_switchTime`). The Lean statement `not_convex_constrainedLandingSet` already carries
`δ + ω * sS ≤ π / 2`, so only the printed text was short. (S1) now reads ωs* ≤ min(δ, π/2 − δ), and Step 1 of
Appendix B uses it.

## Attacks that failed

`m1.py` parametrises M1 controls so that every parameter vector is an admissible continuous-time control
(piecewise-geodesic body axis at rate ≤ ω, gimbal offset ≤ δ, throttle in its box, constant mass). Each script
runs a multistart search for a control the theorem says cannot exist. Distances are Euclidean in (r0, v0), metres
and m/s mixed.

| Script | Claim | Proved bound | Closest the search got |
|---|---|---|---|
| `c1_bstar_attack.py` | Theorem B*: midpoint θ_m is not landable. δ = 40°, ω = 1 rad/s, s* = 0.5 s, a ∈ [6, 20], t_f = 1.5 s | 6.4e-4 | 0.0415 (42 starts), 0.0428 on a grid twice as fine |
| `c1_bstar_attack.py` | Same, δ = 15°, ω = 0.4 rad/s, s* = δ/ω, a ∈ [5, 12.5], t_f = 4 s | 3.8e-5 | 0.0200 (32 starts) |
| `c3_thmB.py` | Theorem B and the ball bound, t_f = 2 s, ω = 30°/s, δ = 15° | 1.81 m/s | 2.14 m/s |
| `c4_lemmaS.py` | Lean instance of Lemma S: every soft landing from ζ_w is at least 1 m off axis | 1 m (Lean), r_S ≈ 1.38 m | 2.32 m |

Calibration for `c1`: the same search reaches a randomly chosen landable datum to within 3e-9 from every start
(1e-11 at best). It reaches the witness
datum θ*, which has the same maximal ℓ as θ_m and is landable, to 5e-4 in the first case and 2.4e-3 in the
second. The witnesses themselves, integrated with `solve_ivp`, land with an error of 2.6e-14 m and stay
inside the 30° glide slope.

`c3` gives 2.14 m/s where Sec. 5.1 quotes 2.18-2.23. The sequence in `numerics/README.md`
(2.38 / 2.27 / 2.21 / 2.18 for N = 10 / 20 / 40 / 80) is still falling, so the two agree. `c3` uses constant mass.

## Lean

On a fresh clone, with Lean v4.36.0-rc2 and the Mathlib revision pinned in `lake-manifest.json`, `lake build`
completes and `lake env lean Verify.lean` prints `PASS: all 126 cited declarations exist and depend only on
propext, Classical.choice, Quot.sound.` The sources contain no `sorry` and no `axiom` declaration.

The statements I compared by hand with the paper: `theoremA`, `IsLossless`, `IsLosslessFor`,
`AttitudeAdmissible`, `landingSet`, `constrainedLandingSet`, `glideSlopeSet`,
`no_lossless_relaxation_constrained_5dof` and its upright and 6-DOF variants, `exists_switchTime`,
`landingSet_dist_ge`, `gtpl_no_lossless_upright_6dof_mass`, `gtpl_no_lossless_freeTime_mass`, `Slice.lemmaS`,
`Slice.theoremD_hard_landing`, `TVC.tvc1_main`. They say what the paper says they say. `tvc1_main` takes the
certificate, the reduction and the witness as hypotheses, as Sec. 7.3 states.

## Not checked

- The pure-TVC certificates and their exact-arithmetic numerics.
- Theorems printed only as sketches: P0-F, the torque-limited 6-DOF theorems (independent transverse torque, E0),
  C-S, and the SDP results (Shor lift, stress certificate, coplanar data).
- The planner results in Sections 5 and 6.
- An attempt on P0-F (ρ1 = 0) was inconclusive and is not included: the search could not reliably reach data
  known to be landable, so its failure to reach the midpoint showed nothing.

## Running

Python 3.13, numpy 2.3, scipy 1.18. From this folder:

    python c2_bstar_delta80.py     # seconds
    python c4_lemmaS.py            # a few minutes
    python c3_thmB.py              # several minutes
    python c1_bstar_attack.py      # about 1.5 hours

Each `cN_out.txt` is the output of the matching script.
