# [proof] report (2026-11-07)

Deliverables: `math/02-impossibility-rigorous.md` (v2, about 480 lines), `math/03-lean-blueprint.md`, and the checks in `numerics/proof/` (`gap_check.py`, `mass3dof_check.py`, `bstar_constants.py`). Brief: `comms/briefs/proof.md`. Claims: CLAIMS rows P-*.

## Proven (rigorous, in math/02)
- **Thm A** and the projection Lemma 3.1, with the quantitative form dist(θ_M,F) ≥ dist(M,R). Prop 1.2 shows the angle-Lipschitz condition is equivalent to ḃ=Ω×b with ‖Ω⊥‖≤ω.
- **Thm B** (rigidity route; sketch steps (1)–(5) made rigorous). Covers both variants: free b(tf) with δ+ωtf≤π/2, and tent with δ+ωtf/2≤π/2, for any α, g and b0.
- **Thm Q (new, the ball bound).** ‖I‖ ≥ ∫a1 cos(δ+ω|s−τ|) for every reachable I. This gives dist(M,R) ≥ Γ = (4a1(tf/4)/ω) sin(δ+ωtf/2) sin²(ωtf/4), with regime δ+ωtf/2≤π/2. It needs no equality case and no rigidity. [numerics] found it within 18% of NLP on 39 configs. Thm Q_T (tent) is proven for α=0 and conditional (checked numerically) for α>0. Cor ε: no ε-lossless uniform relaxation exists for ε < Γ.
- **Thm L:** free terminal attitude, every tf>0, δ<π. **Thm L_T:** tent with δ+ωtf/2≤π (the witness fails when ωtf ≥ 2π). **Prop 8.1:** nonconvexity also holds with ρ1=0 once δ+ωtf>π/2.
- **Thm E / 6.2 (6DOF transfer).** Holds for kinematic 6DOF (M4-kin, both variants, returning exactly to R0) and for M3a/M4-dyn (independent transverse torque, axisymmetric, Ω(0)=0, free terminal attitude). The latter has envelope εs²/2, and the gyroscopic term does no work on ‖Ω⊥‖.
- **Thm B\* (main theorem, after the adversary's BREAK).** This is the dive-then-brake exposed face, made rigorous in the version with ωs* ≤ δ. F is nonconvex **with altitude and glide-slope constraints**, for every tf, with upright landing, and for free tf on compact windows. The quantitative version needs no equality case, rigidity or compactness, but the gap is tiny (~1e-5 m for GTPL; the face is genuinely thin).
- **Thm D** (state-linear class, Def 11.1, with moment lifts and occupation measures explicitly excluded) and **Cor D.1**, an unconditional per-instance lossiness result (terminal-error cost, altitude-type constraints).
- **Prop 11.3**, the trivial exact convex reformulation, which is not state-linear.
- **Lemma 6.4**, the TVC flat output.
- **Prop 8.2**, exact 3DOF: F is convex for α=0 (any control set), and for α≥0 with free direction (a ≤ a_max plus Aumann).

## Conjectured / open
- **Lemma S** (hard v(tf)=0 per-instance D): only an exact reduction is proven (Prop 11.2).
- **M3b pure-TVC** (the GTPL actuation): Lemma 6.4 reduces it to a zero-gimbal, torque-limited tent problem, which is open.
- M3 with Ω⊥(0)≠0 or prescribed terminal attitude.
- Unbounded free tf.
- Exact 3DOF with mass and a pointing cone (the 1D vertical slice is convex; partial analytic proof).
- ρ1=0 at short horizons.

## Changes forced by attacks (log)
1. [adversary] BREAK (P_u underground for GTPL). Thm B/Q are kept, now labelled "unconstrained"; Thm B\* added as the main theorem; the summary and weaknesses were rewritten.
2. [adversary-6dof] BREAK on B6. Restated as kinematic/decoupled-torque only; M3b marked open (§6.4).
3. Orchestrator's TVC identity: corrected. It omits the roll-rate term (J_a/(mL)) r Ω⊥, so the exact cancellation needs r ≡ 0.
4. [lean]: Q2 needs a rearrangement or Chebyshev step, not a pointwise comparison. Already handled; made explicit in the blueprint.

## Weaknesses
- The constrained obstruction (B\*, B\*-env) is qualitatively proven but thin: rigorous gap ~1e-5 m, heuristic ≲ 1 cm (adversary a6, corrected). Practical ε-impossibility for GTPL is not established. Cor D.1 uses soft v(tf) and its gap is ~1e-6 m.
- The impossibility holds only for uniform / state-linear relaxations with affine data entry. Per-instance hull or moment relaxations are not refuted.
- M1 is kinematic. The real GTPL actuation (M3b) is not yet covered.
