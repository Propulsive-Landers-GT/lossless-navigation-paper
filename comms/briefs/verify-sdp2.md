# Brief: VERIFY-SDP2 (independent hostile referee)

Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research. Read comms/PROTOCOL.md (compute budget: <=2 heavy processes, single-threaded BLAS), comms/CLAIMS.md (CSD2', SDP-* rows and the new rows from proof-csd2p), math/08-sdp-exactness.md (background: Thm 2.1, 2.4, Prop 6.1), math/09-csd2-prime.md (UNDER REVIEW), math/verify-pos6-report.md SDP section (prior refereeing of math/08), math/04-positive-results.md (C-W, Aumann).

Referee, line by line, each result in math/09:
- T1 (rotation of the lifted optimum so the terminal (r,v) lies in R^3; CSD2' <=> R_X ∩ E^2 = R_3)
- T2 (fold onto the primer plane fixing e_z => lift exact for every LINEAR objective in all models; closes SDP-F)
- T3 (continuous-time stress certificate / Jacobi form ∫ν(η̇² − |ḃ|²η²) + ∫κη², κ = ‖P‖ sin(θ−δ) cot θ)
- T4 (hemisphere/Picone exactness criterion: ∃c with <b*(t),c> > 0, <P(t),c> >= 0, <e_z,c> >= 0; a-priori class of vertical-shortfall targets with ωtf < π; discrete version requires μ_d >= 0 <=> convexified lens)
- T5 (discrete index identity neg(Q) = neg(Z) − p0(C_yw), Sturm bounds k−1 <= neg Z <= k, k = number of primer-plane crossings; k <= p0 => exact; k >= p0+2 => beaten in R^4)
- P6 (no free singular arcs at genuine continuous-time optima)
- P7 (unit-d failure mechanism)
- the physical claim that exactness yields a genuine attitude plus a bang-bang gimbal selection with the same terminal state via Aumann (exact, not approximate).

For each: CONFIRMED / NEEDS FIX (with repair) / BROKEN (with counterexample). Spot-check numerically with own scripts (numerics/verify-sdp2/, own venv) — e.g. test T2 (linear objectives exact) and the T4 criterion on random instances including adversarial ones, and the T5 index identity on fresh instances not in proof-csd2p's banks.

Deliverables: math/verify-sdp2-report.md; update relevant CLAIMS rows' status ("verify-sdp2" in notes); post a BOARD summary; message main immediately on any BROKEN; write comms/reports/verify-sdp2.md; return per-result verdicts.
