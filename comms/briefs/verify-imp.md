# Brief: verify-imp (independent referee, impossibility side)

You are VERIFY-IMP, an independent referee for a math paper. Workspace: /Users/aneesh/Documents/GitHub/GTPL/lcvx-5dof-research. First save this brief to comms/briefs/verify-imp.md, read comms/PROTOCOL.md (compute budget), comms/CLAIMS.md, paper/CLAIMS-MAP.md, SYNTHESIS.md.

Your job: referee, line by line, the following claims that are currently registered as CLAIMED (written by one agent, not yet independently checked), and decide for each: CONFIRMED (proof correct and complete as stated, possibly with minor fixes you write down), NEEDS FIX (gap/error that you can repair — write the repair), or BROKEN (false or unrepairable as stated — give counterexample or explanation). Be a hostile, careful referee: check every inequality, every hypothesis used, quantifiers, measurability, edge cases, whether the regime stated is the regime proved, whether constants are right (spot-check numerically with small python scripts in numerics/verify-imp/, own venv, ≤2 processes).
Claims (find each in the cited files; CLAIMS IDs in comms/CLAIMS.md):
1. Q — quantitative ball bound and gap Γ (math/02, Thm Q); B variant T (tent/upright terminal); the "all horizons" nonconvexity result (math/02); the free-final-time corollary (math/02) and RR-LS (math/redteam-reform.md §4).
2. B* — dive-then-brake (math/02 §10, §10.6; math/01 §B*), including the quantitative version and the constant c₁ = 1/(ωϑs*) = 4a_max/(ω a₁₀ sin δ s*) that the paper-writer corrected — confirm which is right.
3. Theorem D + state-linear class definition (math/02, comms/threads/theorem-D.md) and Lemma S (math/07 §2–3, Wirtinger lemma W, master inequality, the certified table).
4. A-opt and Prop T (math/redteam-lift.md §7).
5. P0-R, P0-F, P0-X (math/possibility-rho0.md).
Write math/verify-imp-report.md: per claim, verdict + reasoning + any repairs. Update the Status column of each row in comms/CLAIMS.md (CONFIRMED / NEEDS FIX / BROKEN, with "verify-imp" in the notes). Post a BOARD summary and message main immediately on any BROKEN. Write comms/reports/verify-imp.md. Return per-claim verdicts.
