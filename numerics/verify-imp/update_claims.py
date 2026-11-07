"""verify-imp: prefix verdicts to the Status column and append notes for the refereed rows of comms/CLAIMS.md.
Splits each row from the right (Status and Notes are the last two cells)."""
import re, sys
P = "comms/CLAIMS.md"
V = {
 "B*":     ("CONFIRMED", "math/02 §10 Steps 1–7, T′, §10.6 env re-derived; c1=1/(ωϑs*)=4a_max/(ωa10 sinδ s*) (identical, dimensionless); η0=1.35e-5 m GTPL recomputed; 'x̄*∉cl F' for δ>π/4 rests on L-R1"),
 "D":      ("CONFIRMED", "Thm D + Def 11.1 correct (mixture-closure, cl Reach); Prop 11.2 correct"),
 "LS":     ("NEEDS FIX", "abstract (i),(ii) correct; B* instantiation needs window s*<t_a and m0−αρ2·t_b≥m_dry (t_fuel via ρ1 is not valid), see math/verify-imp-report.md §1f"),
 "P-Q":    ("CONFIRMED", "every step + table re-derived (v1: Γ_F 7.61/13.72/23.75)"),
 "P-B":    ("CONFIRMED", "variant T Steps 1–6 checked (rigidity chained at tf/2)"),
 "P-T":    ("NEEDS FIX", "proof + α=0 bound correct; table row (10,0.3,15°) violates δ+ωtf/2≤π/2 (not a certified bound); α=0.03 row needs ρ2≤444 N for (H_m)"),
 "P-L":    ("CONFIRMED", "Thm L and L_T checked incl. weak-* continuity"),
 "P-L0":   ("CONFIRMED", "Prop 8.1 equality step re-done (a=a2 forced on (s0,tf])"),
 "P-ε":    ("CONFIRMED", "Cor 5.2"),
 "P-tf":   ("CONFIRMED", "Prop 7.2/7.3 and Cor 10.4 checked; t=t* case needs M_z≥0"),
 "S":      ("CONFIRMED", "Thm S in regime (see S-T for the Ω-range fix); Prop 11.2 reduction correct"),
 "P-B*":   ("CONFIRMED", "Steps 1–7 + Cor 10.4 line by line; stress test v2: bound valid, 19× loose (brake canceller η=2.7e-4 m)"),
 "P-D":    ("CONFIRMED", ""),
 "P-D1":   ("NEEDS FIX", "state δ≤π/4 (uses Step 7) and that extra vertical constraints (e.g. descent-rate) are satisfied by the B* witness"),
 "RR-LS":  ("NEEDS FIX", "(i),(ii) correct; (iii): window example [0,t_fuel] wrong (needs t>s*, m0−αρ2 t≥m_dry), (H2) via Cor 10.4 continuity, (H3) gives Λ_h≠0 (not v0_lat≠0) in S1-version"),
 "RR-R0":  ("CONFIRMED", "= P0-R variant F"),
 "L-Aopt": ("NEEDS FIX", "A-opt correct but conclusion is V=conv V (finite mixtures), not V** unless V_rel lsc; Prop T correct only for tent variant b(tf)=e_z (state it; variant F needs ωtf in place of ωtf/2)"),
 "P-B*env":("CONFIRMED", "§10.6 steps (1)–(6) checked"),
 "P0-R":   ("NEEDS FIX", "variant F iff CONFIRMED (incl. R=R_env); tent 'only if' proved only for π/2<δ+ωtf/2≤π (L_T argument), open beyond"),
 "P0-F":   ("CONFIRMED", "all estimates re-derived; ties + separation reproduced (v5)"),
 "P0-X":   ("CONFIRMED", "left maximizer may coast (β*_L>0) — altitude still holds since d_z≥cos(δ+T) for every control; '≈2.1' is the small-T value (2.16/2.38/2.78 at T=.1/.3/.5, δ=15°)"),
 "S-W":    ("CONFIRMED", "proof + sharpness checked"),
 "S-M":    ("CONFIRMED", "Steps 1–5 checked; independent 3D attack v4: 0.0343≤B=0.0637, 0.4417≤0.5281"),
 "S-T":    ("CONFIRMED (table) / NEEDS FIX (Ω-ranges)", "table reproduced to all digits (v3); certified Ω-ranges have a positive lower end for δ>0: δ=5° [0.004,0.46], δ=10° [0.038,0.34] (T=2) — '(0,Ω_max]' false"),
}
txt = open(P).read().split("\n")
seen = set()
for i, line in enumerate(txt):
    m = re.match(r"^\| ([^|]+?) \|", line)
    if not m:
        continue
    rid = m.group(1).strip()
    if rid not in V or rid in seen:
        continue
    head, status, notes, tail = line.rsplit("|", 3)
    verdict, note = V[rid]
    status = f" **{verdict}** (verify-imp, math/verify-imp-report.md); {status.strip()} "
    nn = notes.strip()
    add = f"verify-imp 2026-11-07: {verdict}" + (f" — {note}" if note else "")
    notes = f" {nn}; {add} " if nn else f" {add} "
    txt[i] = "|".join([head, status, notes, tail])
    seen.add(rid)
missing = set(V) - seen
print("updated", len(seen), "missing", missing)
open(P, "w").write("\n".join(txt))
