# Agent collaboration protocol

**Top priority (user):** settle whether lossless convexification (LCvx) of 5DOF (then 6DOF) powered descent is
POSSIBLE or IMPOSSIBLE, with a rigorous proof that is adversarially attacked and machine-checked in Lean.
Practical guidance work is deferred until this is done.

## Channels
| Channel | Use |
|---|---|
| `comms/BOARD.md` | Broadcast feed. Short posts: discoveries, breaks, requests, status. Append-only. |
| `comms/threads/<topic>.md` | Longer discussions on one topic (e.g. `threads/occupation-measures.md`). Any agent may open one; announce it on the BOARD. Append-only, signed. |
| `comms/CLAIMS.md` | Registry of every mathematical claim. Status lifecycle below. Edit only your own rows, plus status/attack columns. |
| `comms/AGENTS.md` | Directory: who does what, which files they own, their direct-message address. |
| Direct messages | `SendMessage` with `to:` set to an agent's address from AGENTS.md (or `"main"` for the orchestrator), for targeted questions/handoffs. Also leave a one-line note on the BOARD so the record is complete. |

## Post format
`## [agent-name] YYYY-MM-DD HH:MM — TYPE: subject` where TYPE ∈ {DISCOVERY, BREAK, FIX, REQUEST, ANSWER, STATUS, NUMERICS}.
Body: the claim/result in 1–10 lines, with file paths for details.

## Claim lifecycle (CLAIMS.md)
`CLAIMED` → `ATTACKED` (an adversary/red-team is working on it) → `BROKEN` | `FIXED` → `CONFIRMED`
(survived attack + independent check) → `FORMALIZED` (Lean, sorry-free, `#print axioms` clean).
Only FORMALIZED claims go into the final theorem statement.

## Rules
1. Read BOARD.md, CLAIMS.md and relevant threads before starting work and before finishing.
2. Post a BREAK immediately (and message `main`) if you find a flaw in any CLAIMED/CONFIRMED item.
3. Never silently edit another agent's files. Ask via thread/DM.
4. Don't trust prior literature as proof: we only accept claims we prove ourselves (citations are context).
5. Git: commit only your own files, messages with no AI attribution trailers.

## Compute budget (orchestrator, mandatory)
The machine has 10 cores and was at load ~180 (everything 15× slower). Each agent: **at most 2 concurrent CPU-heavy
processes**, multiprocessing pools with **≤ 2 workers**, set `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1`
for every solver run. Prefer fewer, smarter runs (warm starts, coarse-to-fine) over brute-force sweeps. Kill your own stale runs.
Use the system clock (`date`) for timestamps — never invent them.
