# Final report: [verify-imp] (independent referee, impossibility side)

Brief: comms/briefs/verify-imp.md. Full referee report: **math/verify-imp-report.md**. Scripts and outputs: numerics/verify-imp/
(own venv; v1_Q_QT_Bstar, v2_bstar_step7_stress, v3_lemmaS_table, v3b_lowOmega, v4_masterineq_attack, v5_p0F_p0X, update_claims; *_out.txt).

**No claim is BROKEN.** Verdicts:

| Claim | Verdict |
|---|---|
| Thm Q (P-Q, P-ε) | CONFIRMED (table reproduced exactly) |
| Thm Q_T (P-T) | proof CONFIRMED; table NEEDS FIX (row 4 outside δ+ωtf/2≤π/2; row 3 needs ρ2≤444 N) |
| Thm B variant T (P-B) | CONFIRMED |
| Thm L, L_T, Prop 8.1 (P-L, P-L0) | CONFIRMED |
| Free tf: Prop 7.2/7.3 (P-tf), Cor 10.4 | CONFIRMED |
| RR-LS / LS | (i),(ii) CONFIRMED; (iii) NEEDS FIX (window must satisfy s*<t_a, m0−αρ2 t_b≥m_dry; t_fuel via ρ1 invalid; also paper Cor 3.11) |
| Thm B* qualitative + T′ + Step 7 (B*, P-B*) | CONFIRMED |
| c₁ | 1/(ωϑs*) = 4a_max/(ω a10 sinδ s*): identical, both correct |
| Thm B*-env (P-B*env) | CONFIRMED |
| Thm D, Def 11.1, Prop 11.2 (D, P-D) | CONFIRMED |
| Cor D.1 (P-D1) | NEEDS FIX (state δ≤π/4; extra vertical constraints must be met by witness) |
| Lemma W, Prop M, Thm S (S-W, S-M, S-T, S) | CONFIRMED; table reproduced; Ω-ranges NEEDS FIX (positive lower end for δ>0) |
| Thm A-opt (L-Aopt) | CONFIRMED (conclusion = convex envelope, not closed V**) |
| Prop T (L-Aopt) | NEEDS FIX: holds for tent variant b(tf)=e_z; must be stated |
| P0-R (P0-R, RR-R0) | variant F CONFIRMED; tent only-if NEEDS FIX (proved only for δ+ωtf/2≤π) |
| P0-F | CONFIRMED |
| P0-X | CONFIRMED (clarify altitude step holds for every control; "≈2.1" is small-T value) |

Registry: Status column of the 24 rows above updated with verify-imp tags. BOARD post 01:16.
Compute: all runs finished, single process each; nothing running.
