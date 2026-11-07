# Report: [verify-pos6] (independent referee: 6DOF transfers, positive results, SDP exactness)

Brief: comms/briefs/verify-pos6.md. Full reasoning: math/verify-pos6-report.md. Numerics: numerics/verify-pos6/.
CLAIMS rows updated (Status + notes tagged "verify-pos6"). BOARD post 2026-11-07. Nothing BROKEN, so no BREAK DM to main.

## Verdicts
| Row | Verdict | Key point |
|---|---|---|
| B6 (Thm K) | CONFIRMED | GTPL Cardan box corner δ* = 21.09°; B* variant needs ωs* ≤ δ_in = 15° |
| B6-D (Thm D) | CONFIRMED | delete "TVC torque may be added" (the envelope is not attained then) |
| B6-D* (Thm D*) | CONFIRMED (core) | state-constraint clause inherits P-B* |
| roll/coning (V6) | CONFIRMED | Lemma 0 numerically 8e-14; needs axisymmetric J, no products of inertia |
| FLAT / P-K3 identity | CONFIRMED | roll term (J_a/(mL))ω₃(b×ḃ) verified, residual 9e-15 |
| B6-E0 (Thm E₀) | NEEDS FIX | κ vs α; closure step; regime (§6, not §3.5) |
| C-W | CONFIRMED | C-W′ Slater caveat at touchdown |
| C-S/C-D | NEEDS FIX (minor) | C-D4 meagre in the wrong space; λ_v BV under v_max |
| C-U | CONFIRMED | existence only without path constraints |
| C-6 | CONFIRMED / FORMALIZED, faithful | Cardan box still an interval |
| C-Y | CONFIRMED | numerics tight to 0.4%; ρ1 = 300 N gives 1.8e-5 rad/s |
| X5 / RR-P | NEEDS FIX | add ωtf ≥ ∠(b0, b_f) |
| SDP-T1 (Thm 2.1) | CONFIRMED | |
| SDP-T4 (Thm 2.4) | CONFIRMED | |
| SDP-P (Thm 4.1) | NEEDS FIX | glide-slope extension unproved (not Gram-linear); core holds, also with altitude |
| SDP-F (Cor 3.3) | CONFIRMED | |
| SDP-R4 (Prop 5.1) | NEEDS FIX (minor) | add E_w ⊆ W; rank ≤ 4 needs dim E_w = 3 |
| SDP-L (Prop 6.1) | CONFIRMED | "Consequence" paragraph overstated |

## Files
- math/verify-pos6-report.md (report)
- numerics/verify-pos6/v1_rigidbody.py, .txt; v2_cy_width.py, .txt; v3_sdp.py, v3_sdp_{A,B,C,D}.txt; .venv (numpy, scipy, cvxpy/Clarabel)
- comms/briefs/verify-pos6.md

## Requested edits (owners)
See report §5: adversary-6dof (E₀, Thm D sentence), positive (C-D4, §5.5, C-W′, C-Y′, C-U), redteam-reform (RR-P hypothesis),
proof-sdp (Rem 4.3, Prop 5.1, §6.1), paper-writer (Thm 4.8, Prop 4.5, Thm 4.3).
