# Orchestrator log

- 2026-11-06: All 17 Propulsive-Landers-GT repos fast-forwarded. Workspace created.
- User decisions: survey several 5DOF models; Lean assumes PMP as a labeled hypothesis, everything else formal;
  install Lean+Mathlib; local git only; target whichever of 5/6DOF is most useful for our lander;
  keep iterating until there is a proof of possibility or impossibility.
- Decision: primary model = 5DOF (translation + thrust-axis pitch/yaw). Reason: GTPL lander has 15° TVC
  for pitch/yaw and separate RCS for roll; roll does not change thrust direction. 6DOF follows as corollary.
- Orchestrator sketch (math/00): impossibility of any *uniform* convex relaxation (Thm A + Thm B) via
  nonconvexity of the feasible boundary-condition set under attitude-rate limits and min throttle;
  plus positive Thm C (LCvx given an attitude profile). Launching agents to attack / make rigorous / formalize.
- User: also solve 6DOF after 5DOF (most useful). User approved launching remaining agents.
- Launched agents: lit-review, vehicle-context, adversary, proof, numerics, lean, positive. Lean 4 + Mathlib installed and building.
- User reprioritized: lossless question FIRST (possible vs impossible, fully proved + formalized); practical solver deferred
  (solver agent stopped). User wants adversarial attempts to make it POSSIBLE, not belief in impossibility.
- Added: comms/PROTOCOL.md, AGENTS.md (DM directory), CLAIMS.md (claim lifecycle → FORMALIZED), threads/.
- Launched: redteam-lift (relaxed controls / occupation measures / SDP lifts / conv-hull optimization),
  redteam-reform (LCvx-style reformulations, counterexamples to B), adversary-6dof (torque-coupled M3, 6DOF M4).
- Orchestrator concern flagged: in the real TVC vehicle gimbal angle = torque input, so M1's free gimbal is a relaxation;
  B6 (6DOF transfer) must be re-derived for M3, not assumed.
- Key threat to watch: occupation-measure LP relaxations (convex, value-exact under Vinter-type conditions) vs Claim A.
  Likely resolution: they are exact in VALUE but their feasible set in boundary data is the closure of the convexified
  reachable set, i.e. larger — so not lossless in the feasibility sense; but the definition of "lossless" must be stated carefully.
- User away ~8–9 h; full creative control. Keep-awake requested.
- vehicle-context DONE (context/vehicle.md). Key: vehicle is N2O/paraffin hybrid; ρ1/ρ2≈0.4; gimbal ±15° per axis (BOX);
  J_xx≈63.6 kg m² wet; lever 0.59 m; max pitch/yaw angular accel ≈1–3.5 rad/s² (torque-limited ⇒ M3 is the realistic model);
  usable rate 0.3–0.5 rad/s; tf≈7 s. Existing 3DOF LCvx solutions contain thrust-direction jumps needing ~10³ rad/s²
  (physically impossible) and are NOT tight at the min-thrust arc (296 N vs 400 N bound) — the 5DOF problem is real for us.
  MPC model mismatch (J, lever arm) ×4.6. Saved for the practical phase.
- lit-review interim: no prior 5DOF/6DOF LCvx claim and no impossibility result found; all 6DOF methods are SCP/indirect.
  Occupation-measure LPs: x0 enters as δ_{x0} (nonlinear in x0) ⇒ convex per instance, consistent with Thm A; Thm A must
  state joint convexity explicitly. (Orchestrator note: if μ0 is a decision variable with only its mean pinned to x0, the LP is
  jointly convex but its feasible x0-set is conv(F) ⇒ not lossless — consistent.) Bae et al. Automatica 2025: 3D Dubins
  reachable set = solid of revolution of 2D set (δ=0 special case of our R).
- 2026-11-07 ~00:15. adversary BREAK accepted: Claim B witness arcs start underground for GTPL (ρ1/(m0 g)=0.51) ⇒ vacuous
  with r_z ≥ 0. Fix B* (dive-then-brake exposed face) assigned. Loopholes found in Thm A scope: (i) relaxations exact only on F,
  (ii) symmetry-reduced relaxations. Orchestrator response: Theorem D (min-landing-error, per instance, state-linear relaxations)
  closes both — relaxed landing set convex ⊇ L ⇒ lossy at q ∈ conv(L)\L — needs no joint convexity in q.
  Key conceptual decision: the impossibility class = STATE-LINEAR relaxations (the LCvx paradigm: physical r,v are decision
  variables, appear linearly). Occupation-measure LPs (state lifted to Dirac measures) are convex and value-exact but outside this
  class — to be reported honestly as the boundary of impossibility.
- proof: ball-bound quantitative Thm B (no equality case) — easy Lean route for unconstrained version. numerics: B confirmed,
  ball bound within 18% of NLP. adversary-6dof: in torque-coupled M3, outward gimbal rotates body the other way ⇒ M1 arcs not
  realizable ⇒ B6 needs new proof. lit-review DONE: no prior 5/6DOF LCvx or impossibility; Berning et al. 2023 (Boeing) claims
  LCvx with tilt-rate limits (full text unavailable) — must reconcile.
- ~00:40. adversary on D: sound, but D ⇔ slice lemma S (now the crux). Shor-lift escape ⇒ class (d) sharpened, moment-lifted
  costs excluded explicitly. Orchestrator raised CONING threat to S (azimuth precession at fixed tilt cancels lateral motion);
  expected S provable for small ω·tf where planar single-crossing S-turns dominate (single-crossing ⇒ offset landing).
  Added TRIV: trivial exact convex reformulation always exists ⇒ the possibility question must be about tractable lifts.
- ~01:00. adversary-6dof BREAK: B6 false for pure-TVC M3 (outward gimbal rotates body inward; M1 arcs unrealizable). Fixes:
  Thm K (kinematic attitude), Thm D/D* (independent transverse torque, incl. terminal upright at rest). Pure TVC OPEN; numerics
  show nonconvexity but small gap at tf=1 s. Orchestrator: center-of-percussion (PVTOL flat output) reduction y=r+εb,
  ε=J_t/(mL)≈1.35 m: ÿ=(T cosμ/m−ε|ω|²)b−g exactly (verified, math/checks/flat_output_tvc.py) ⇒ pure TVC ≡ zero-gimbal
  angular-accel-limited model with affine boundary-data map; planar comparison lemma proves bottom-face nonconvexity.
  Sent to adversary-6dof + proof. Remaining: dive-then-brake with terminal upright for pure TVC.
- ~01:30. positive DONE: fixed-attitude LCvx exact (value+feasibility, Aumann); strong lossless under PMP + checkable non-degeneracy;
  per-instance exactness C-U (nonconvexity = choice of attitude); C-6: on real TVC, given b the problem is exactly convex;
  C-Y: 3DOF optimum exactly 6DOF-optimal for GTPL essentially never (initial-rate window ~3.5 µrad/s). Launched lean-positive
  (formalize math/05; PMP & Aumann only as explicit hypotheses) and possibility-rho0 (is LCvx possible when ρ1=0? dichotomy).
- ~01:45. redteam-reform DONE (math/redteam-reform.md): all LCvx-slack routes FAIL; chord-rate & orbitope lifts FAIL; B has no
  algebraic hole (scope hole fixed by B* w/ small s*); RR-LS line-search lemma written; pure-TVC exact class is measure-zero
  (b̈ = k(b−d) unstable, √k≈2–3 s⁻¹); ρ1=0: velocity set convex (theorem), full F OPEN (→ possibility-rho0).
- ~02:00. proof DONE (math/02 v2, math/03): B* rigorous w/ altitude+glide slope, all tf, upright landing, free tf (bounded),
  kinematic/indep-torque 6DOF — but gap ~1e-5 m for GTPL (uses gimbal; thin dent is physical). Thm D w/ state-linear class.
  Open: Lemma S (soft per-instance), pure TVC, ρ1=0.
- ORCHESTRATOR VERIFIED: lean Main.lean builds; no_lossless_relaxation_5dof (+ optimisation form, box class) depend only on
  [propext, Classical.choice, Quot.sound]. Scope: M1, b(0)=e_z, no altitude constraint, fixed tf, δ+ωtf ≤ π/2.
- redteam-lift: F-W applies (b stays genuine); α=0 relaxation exact given b; theorem must state affine data entry; degree-2
  Shor lift tight but lossy (1e-4..1e-3 rel) — certificate only; Theorem A-opt (value-lossless on F ⇒ V=V** on F) + Prop T.
- adversary-6dof: FLAT identity confirmed (needs ε const, ω3≡0); translate requires prescribed terminal attitude; rigorous
  pure-TVC nonconvexity for tilt-free terminal. OPEN: upright terminal + altitude (the GTPL case) → launched proof-tvc.
- 23:32 (system clock; earlier agent timestamps partly invented). adversary report final (math/01): A & B* SURVIVE with scope
  (continuous time, affine data entry, detection-sound lossless); gap under r_z≥0 ≈1e-5 m rigorous / ≈1 cm heuristic ⇒ a
  PRACTICALLY significant impossibility for GTPL is NOT established. Open loopholes: exact-only-on-F for min-fuel; rotating
  frame (⇔ Lemma S). Coning closes the dent at long horizons with tilt cap (small-angle evidence). Discretized LCvx not exact
  either ⇒ statements in continuous time. Machine load ~180/10 cores ⇒ compute budget imposed.
- 23:54 redteam-lift DONE. RETRACTED its "Shor lossy" claim (solver artifacts from killing Slater). New Conjecture CSD2:
  degree-2 Shor/Hilbert-sphere SDP lift is numerically EXACT (≤1e-6 rel, ~35 targets) for FIXED-THRUST 5DOF min-landing-error;
  certifies θ_M unreachable. Tractable "possible" outside A/D scope (data only in objective; moment cost). Not covered:
  throttle, glide slope, proof. Also: theorem must state affine/separable-monotone data entry (δ_θ lifts convexify anything);
  Theorem A-opt + Prop T (no relaxation lossless for all convex costs even on F). Free tf: θ_M reachable at tf+Δt for GTPL ⇒
  free-tf impossibility needs a time window. Launched verifier-sdp (independent impl., adversarial) + proof-sdp (prove CSD2).
- 23:57 possibility-rho0 DONE: ρ1=0 does NOT give uniform LCvx. R convex iff δ+ωtf ≤ π/2 (then 3DOF envelope SOCP exact for
  velocity-only targets), but F_tf nonconvex (coast-while-rotating kink), also with r_z ≥ 0 for T/W ≳ 2.1. Gap thin (~0.045 vs 10.8).
  ⇒ Impossibility is driven by finite attitude rate itself, not by the min-throttle constraint.
- 00:13 proof-s DONE: Lemma S PROVED (Wirtinger-mod-affine lemma covers planar/coning/lifted paths; master inequality;
  single-crossing S-turn witness) in regime min-throttle T/W > 1/cos(δ+ωtf), ωtf ≤ 0.3–0.55 ⇒ Theorem D (hard v(tf)=0) lossy by
  0.4–1.8 m. Adversary found no flaw. GTPL (hover-capable) outside regime; numerical only. Coning fills ~87% of dent at tf=20 s.
  Pattern: rigorous impossibility in idealized regimes; thin-but-real numerically at GTPL constants.
- 00:16 numerics: CSD2 likely BROKEN (case 12 near dent: SDP rank 4, 2.5% below 480-restart NLP); exact on 21/22 incl. all
  realistic in-air targets. Lemma S numerically holds in 3D w/ coning (partial fill at long tf). Largest admissible nonconvexity:
  ground-launched hops (2.9 weighted m/s at tf=8); in-air descents cm-level. Routed case 12 to verifier-sdp + proof-sdp.
- 00:23 verifier-sdp independently CONFIRMED case 12 (explicit feasible R⁴ chain attains SDP value; ~1070 3D runs can't).
  SDP lift LOSSY with gimbal and with variable throttle (40%); survives δ=0 fixed thrust (840 instances). proof-sdp refocused on δ=0.
- 00:23 numerics DONE (numerics/README.md). Key practical: pad-launched hop ⇒ landing set is a ring with hole up to ~5 m
  (M1), 1.74 m (torque-coupled TVC); in-air descent no measurable dent. B* gap ~1 cm/s. Gap law dist/|P_x| ≈ 0.31 ωtf.
- 00:33 redteam-lift concurs: CSD2 refuted (with gimbal); exact ~55/56 incl. all GTPL in-air targets ⇒ certificate only.
  Note (orchestrator): only degree-2 is refuted, and only with gimbal; "no finite order exact" is not proven. The small-N order-2
  Lasserre certification is with verifier-sdp (numerics is done).
- 00:34 proof-sdp: case-12 gap is a discretization artifact (unit-d discrete model forbids chattering); convexified-lens
  model exact on case 12. CSD2′ OPEN. Proved Thm 2.1/2.4 (exact ⇔ PSD stress ⇔ local min in R⁴), Thm 4.1 (coplanar data ⇒
  planar LICQ local min is certified global, w/ glide slope). Sent CSD2′ to verifier-sdp to attack.
- 00:35 proof-sdp DONE. Variable-throttle degree-2 lift CERTIFIED lossy at N=3 (Lasserre-2). δ=0: ~2,900 targets, no gap. CSD2′ check running in verifier-sdp (watch δ=40°, N=4 instance).
- 00:38 proof-s hop verdict: NOT PROVED (quadratic/Shor certificates provably too loose: tilts ~1 rad, lifted paths). Rigorous: reduction, upright-pad limit 7.20/7.28 m/s, explicit offset witnesses (4.6–6.6 m off). Ring for v0z∈(7.727,7.742] numerical. Needs 2D rigidity or validated B&B.
- 00:38 Launched paper-writer (paper/, CLAIMS-MAP.md; placeholders for in-progress results).
- 00:54 lean-positive DONE: 35 theorems sorry-free; ORCHESTRATOR VERIFIED C3_headline & convex_origFeas axioms = standard 3. Gaps listed in lean/POSITIVE.md.
- 00:57 paper-writer DONE: paper/main.pdf (30 pp) compiles; CLAIMS-MAP.md. Flagged many SYNTHESIS-'PROVED' rows still CLAIMED in registry ⇒ launched verify-imp + verify-pos6 referees for an independent confirmation sweep.
- 00:59 verifier-sdp: CSD2′ survives (509 former gaps → 0 in convexified lens; screens N=3..8 0 gaps). Unit-d break near-rigorous (Las2 at N=3). Launched proof-csd2p.
- 01:13 lean DONE: B* (altitude+glide slope, every tf), upright, kinematic 6DOF, mass model, Thm D abstract, RR-LS abstract — 37 headline theorems. ORCHESTRATOR VERIFIED full lake build + #print axioms (standard 3) for the six constrained/6DOF/mass headline theorems. CORE OUTCOME NOW MACHINE-CHECKED.
- 01:14 Core lossless outcome machine-checked ⇒ per user's ordering, practical phase started: solver-v2 (attitude-aware convex guidance built on C-6/C-K, vs 3DOF LCvx + rate constraints, vs nonconvex reference; 6DOF closed-loop Monte Carlo). Theory extensions (pure TVC, CSD2′, Lemma S Lean, referees) continue in parallel.
- 01:17 verify-imp DONE: 0 BROKEN, 7 NEEDS FIX (Q_T table rows, RR-LS example window/fuel at ρ2, Cor D.1 needs δ≤π/4 + vertical-constraint note, Lemma S certified Ω-ranges have positive lower ends for δ>0, A-opt is finite-mixture envelope not V**, Prop T upright-only, P0-R upright 'iff' partial). B* constant c1 confirmed (both forms equal). 24 rows updated.
- 01:19 verify-pos6 DONE: 0 BROKEN; 14 CONFIRMED, 6 NEEDS FIX (E₀: const mass + closure step; C-S meagre-set in admissible class; X5 needs ωtf ≥ ∠(b0,bf); SDP Thm 4.1 glide-slope clause unproved; Prop 5.1 rank ≤4 needs step/3D data). Sent E₀ fixes to proof-tvc; sent all referee fixes + new Lean results to paper-writer for revision.
- 01:24 lean-s DONE: Wirtinger (Parseval), master inequality, Lemma S explicit instance, Thm D hard landing, A-opt. ORCHESTRATOR VERIFIED build + axioms (standard 3).
- 01:27 paper rev 2 DONE (34 pp; referee fixes; boxed machine-checked headline). adversary-6dof: GTPL-realistic pure TVC (box, 100°/s, upright at rest, r_z≥0) nonconvex numerically at tf=5/7 (≈3 cm). proof-tvc certificate at tf=1 in progress.
- 01:32 numerics (follow-up): unit-d SDP gaps at N=5 (5–15%); sparse order-2 Lasserre bounds lie between SDP and 3D but solver 'inaccurate' ⇒ unit-d break remains numerical, not certified (needs MOSEK or substitution reformulation). Does not affect CSD2′ (convexified lens).
