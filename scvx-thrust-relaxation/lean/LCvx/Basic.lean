import LCvx.Core

/-!
# Lossless convexification of the thrust bound, for nonlinear discrete-time dynamics

A discretized powered-descent problem has a thrust vector `u k` at each of `N` nodes. The
original problem asks for `ρ₁ ≤ ‖u k‖ ≤ ρ₂`, which is nonconvex because of the lower bound. The
LCvx relaxation adds a slack `Γ k`, asks for `‖u k‖ ≤ Γ k` and `ρ₁ ≤ Γ k ≤ ρ₂`, and lets the
slack (not `‖u k‖`) drive mass depletion and cost.

Nothing here assumes linear dynamics. The dynamics, boundary conditions and any active path
constraints are all folded into one equality constraint `F z = y₀`, where `F` only needs a strict
derivative at the point of interest. For 6-DOF powered descent, `F` is the terminal state of the
rigid-body dynamics as a function of the controls (see `LCvx.SixDOF`).

Main results, for a local minimizer `z` of the relaxed problem:

* `slack_eq_lower_of_surjective`: if the thrusts at some set `L` of lossy nodes (`‖u k‖ < Γ k`)
  can steer `F` in every direction to first order, then every slack is at its lower bound
  (`Γ k = ρ₁` for all `k`). That is the degenerate "horizon too long" case.
* `not_surjective_of_free_param`: if some other variable, such as the time of flight, can lower
  the cost on its own, no such set `L` exists at all.
* `card_lossy_lt`: so if every `m` nodes can steer `F`, fewer than `m` nodes are lossy.
* `isLocalMinOn_original`, `isMinOn_original`: a lossless optimum of the relaxed problem is an
  optimum of the original problem.
-/

open Filter Topology Set

-- The instance assumptions are declared once for the whole file; not every lemma uses all of them.
set_option linter.unusedSectionVars false

namespace LCvx

variable {N : ℕ} {E P Y : Type*}
  [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup P] [NormedSpace ℝ P]
  [NormedAddCommGroup Y] [NormedSpace ℝ Y]

/-- Decision vector: a thrust `u k` and a slack `Γ k` per node, and every other decision variable
(time of flight, virtual controls, ...) in `P`. -/
abbrev Dec (N : ℕ) (E P : Type*) := (Fin N → E) × (Fin N → ℝ) × P

/-- Data of a guidance problem with the LCvx thrust relaxation. -/
structure Problem (N : ℕ) (E P Y : Type*) where
  /-- Lower thrust bound. -/
  ρ₁ : ℝ
  /-- Upper thrust bound. -/
  ρ₂ : ℝ
  /-- Constraint on `(u k, Γ k)` at node `k`, such as the gimbal cone `cos δ ‖u‖ ≤ u₁`. -/
  cone : Fin N → Set (E × ℝ)
  /-- Every remaining constraint (state bounds, glide slope, time-of-flight bounds, ...). -/
  other : Set (Dec N E P)
  /-- Equality constraints: dynamics, boundary conditions and active path constraints. -/
  F : Dec N E P → Y
  /-- Right-hand side of the equality constraints. -/
  y₀ : Y
  /-- Cost, for example fuel. -/
  cost : Dec N E P → ℝ

/-- The original problem has no slack. Its mass flow and cost use `‖u k‖`, which is the relaxed
problem evaluated at `Γ k = ‖u k‖`. -/
def embed (x : (Fin N → E) × P) : Dec N E P := (x.1, fun k => ‖x.1 k‖, x.2)

/-- Puts `w k` into the thrust slot of every node `k ∈ L` and zero everywhere else. -/
noncomputable def lossyIncl (L : Finset (Fin N)) : (Fin N → E) →L[ℝ] Dec N E P :=
  (ContinuousLinearMap.pi fun k => if k ∈ L then ContinuousLinearMap.proj k else 0).prod 0

@[simp] lemma lossyIncl_apply (L : Finset (Fin N)) (w : Fin N → E) :
    lossyIncl (P := P) L w = (fun k => if k ∈ L then w k else 0, 0, 0) := by
  ext k
  · by_cases hk : k ∈ L <;> simp [lossyIncl, hk]
  · simp [lossyIncl]
  · simp [lossyIncl]

/-- The nodes where the relaxation is not tight, `‖u k‖ < Γ k`. -/
noncomputable def lossyNodes (z : Dec N E P) : Finset (Fin N) :=
  Finset.univ.filter fun k => ‖z.1 k‖ < z.2.1 k

namespace Problem

variable (π : Problem N E P Y)

/-- Constraints of the relaxed problem at node `k`. -/
def NodeOK (k : Fin N) (u : E) (Γ : ℝ) : Prop :=
  ‖u‖ ≤ Γ ∧ π.ρ₁ ≤ Γ ∧ Γ ≤ π.ρ₂ ∧ (u, Γ) ∈ π.cone k

/-- Feasible set of the relaxed problem. -/
def relaxed : Set (Dec N E P) :=
  {z | (∀ k, π.NodeOK k (z.1 k) (z.2.1 k)) ∧ z ∈ π.other ∧ π.F z = π.y₀}

/-- Feasible set of the original problem, with the nonconvex bound `ρ₁ ≤ ‖u k‖`. -/
def original : Set ((Fin N → E) × P) :=
  {x | (∀ k, π.ρ₁ ≤ ‖x.1 k‖ ∧ ‖x.1 k‖ ≤ π.ρ₂ ∧ (x.1 k, ‖x.1 k‖) ∈ π.cone k) ∧
    embed x ∈ π.other ∧ π.F (embed x) = π.y₀}

/-! ### The relaxation contains the original problem, and is exact when lossless -/

theorem embed_mem_relaxed {x : (Fin N → E) × P} (hx : x ∈ π.original) :
    embed x ∈ π.relaxed :=
  ⟨fun k => ⟨le_rfl, (hx.1 k).1, (hx.1 k).2.1, (hx.1 k).2.2⟩, hx.2.1, hx.2.2⟩

lemma embed_of_lossless {z : Dec N E P} (hloss : ∀ k, ‖z.1 k‖ = z.2.1 k) :
    embed (z.1, z.2.2) = z := by
  ext k <;> simp [embed, hloss]

lemma mem_original_of_lossless {z : Dec N E P} (hz : z ∈ π.relaxed)
    (hloss : ∀ k, ‖z.1 k‖ = z.2.1 k) : (z.1, z.2.2) ∈ π.original := by
  have he := embed_of_lossless hloss
  refine ⟨fun k => ?_, he ▸ hz.2.1, he ▸ hz.2.2⟩
  obtain ⟨-, h1, h2, h3⟩ := hz.1 k
  exact ⟨(hloss k).symm ▸ h1, (hloss k).symm ▸ h2, (hloss k).symm ▸ h3⟩

/-- A lossless local minimizer of the relaxed problem is a local minimizer of the original one. -/
theorem isLocalMinOn_original {z : Dec N E P} (hz : z ∈ π.relaxed)
    (hmin : IsLocalMinOn π.cost π.relaxed z) (hloss : ∀ k, ‖z.1 k‖ = z.2.1 k) :
    IsLocalMinOn (π.cost ∘ embed) π.original (z.1, z.2.2) := by
  have hcont : Continuous (embed : (Fin N → E) × P → Dec N E P) :=
    continuous_fst.prodMk ((continuous_pi fun k =>
      ((continuous_apply k).comp continuous_fst).norm).prodMk continuous_snd)
  have hf : IsLocalMinOn π.cost π.relaxed (embed (z.1, z.2.2)) := by
    rwa [embed_of_lossless hloss]
  exact hf.comp_continuousOn (fun x hx => π.embed_mem_relaxed hx) hcont.continuousOn
    (π.mem_original_of_lossless hz hloss)

/-- A lossless global minimizer of the relaxed problem is a global minimizer of the original. -/
theorem isMinOn_original {z : Dec N E P}
    (hmin : IsMinOn π.cost π.relaxed z) (hloss : ∀ k, ‖z.1 k‖ = z.2.1 k) :
    IsMinOn (π.cost ∘ embed) π.original (z.1, z.2.2) := by
  intro x hx
  have := hmin (π.embed_mem_relaxed hx)
  simp only [Function.comp_apply, embed_of_lossless hloss]
  exact this

/-! ### Trial points -/

/-- Direction that shrinks the thrust and slack of every node in `D` toward zero and moves the
other variables along `dp`. -/
def scaleDir (z : Dec N E P) (D : Finset (Fin N)) (dp : P) : Dec N E P :=
  (fun k => if k ∈ D then -z.1 k else 0, fun k => if k ∈ D then -z.2.1 k else 0, dp)

section Trial

variable (z : Dec N E P) (L D : Finset (Fin N)) (dp : P) (w : Fin N → E) (t : ℝ)

lemma trial_u (k : Fin N) : (z + lossyIncl L w + t • scaleDir z D dp).1 k =
    (if k ∈ D then (1 - t) • z.1 k else z.1 k) + (if k ∈ L then w k else 0) := by
  simp only [scaleDir, lossyIncl_apply, Prod.fst_add, Prod.smul_fst, Pi.add_apply,
    Pi.smul_apply]
  split_ifs <;> simp [sub_smul] <;> abel

lemma trial_Γ (k : Fin N) : (z + lossyIncl L w + t • scaleDir z D dp).2.1 k =
    if k ∈ D then (1 - t) * z.2.1 k else z.2.1 k := by
  simp only [scaleDir, lossyIncl_apply, Prod.snd_add, Prod.smul_snd, Prod.fst_add,
    Prod.smul_fst, Pi.add_apply, Pi.smul_apply, Pi.zero_apply]
  split_ifs <;> ring

lemma trial_p : (z + lossyIncl L w + t • scaleDir z D dp).2.2 = z.2.2 + t • dp := by
  simp [scaleDir]

end Trial

variable {π}

/-- If every other constraint has slack at `z`, every trial point near `z` satisfies it. -/
lemma trial_mem_of_nhds {z : Dec N E P} (hother : π.other ∈ 𝓝 z) (L D : Finset (Fin N))
    (dp : P) : ∀ᶠ p : (Fin N → E) × ℝ in 𝓝 0, 0 < p.2 →
      z + lossyIncl L p.1 + p.2 • scaleDir z D dp ∈ π.other := by
  have hc : ContinuousAt (fun p : (Fin N → E) × ℝ => z + lossyIncl L p.1 + p.2 • scaleDir z D dp)
      0 := ((continuous_const.add ((lossyIncl L).continuous.comp continuous_fst)).add
        (continuous_snd.smul continuous_const)).continuousAt
  exact (hc.eventually_mem (by
    simpa only [Prod.fst_zero, Prod.snd_zero, map_zero, zero_smul, add_zero] using hother)).mono
    fun p hp _ => hp

/-- For small `w` and small `t > 0`, the trial point `z + ι w + t • d` satisfies the node
constraints, as long as the lossy nodes in `L` have slack in the cone constraint and the scaled
nodes in `D` have slack above `ρ₁`. It satisfies the other constraints when `hother` says so:
for instance because they all have slack (`trial_mem_of_nhds`), or because the trial points do
not move the quantities they constrain. -/
theorem eventually_trial_mem (hcone : ∀ k (q : E × ℝ) (t : ℝ), 0 < t → q ∈ π.cone k →
      t • q ∈ π.cone k)
    {z : Dec N E P} (hz : z ∈ π.relaxed) (L D : Finset (Fin N)) (dp : P)
    (hother : ∀ᶠ p : (Fin N → E) × ℝ in 𝓝 0, 0 < p.2 →
      z + lossyIncl L p.1 + p.2 • scaleDir z D dp ∈ π.other)
    (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    (hD : ∀ i ∈ D, π.ρ₁ < z.2.1 i) :
    ∀ᶠ p : (Fin N → E) × ℝ in 𝓝 0, 0 < p.2 →
      (∀ k, π.NodeOK k ((z + lossyIncl L p.1 + p.2 • scaleDir z D dp).1 k)
        ((z + lossyIncl L p.1 + p.2 • scaleDir z D dp).2.1 k)) ∧
      z + lossyIncl L p.1 + p.2 • scaleDir z D dp ∈ π.other := by
  set T : (Fin N → E) × ℝ → Dec N E P := fun p => z + lossyIncl L p.1 + p.2 • scaleDir z D dp
    with hT
  have hTc : Continuous T :=
    (continuous_const.add ((lossyIncl L).continuous.comp continuous_fst)).add
      (continuous_snd.smul continuous_const)
  have hT0 : T 0 = z := by ext k <;> simp [hT]
  -- Node constraints, one node at a time.
  have hnode : ∀ k, ∀ᶠ p in 𝓝 (0 : (Fin N → E) × ℝ), 0 < p.2 →
      π.NodeOK k ((T p).1 k) ((T p).2.1 k) := by
    intro k
    obtain ⟨hk1, hk2, hk3, hk4⟩ := hz.1 k
    have hΓ0 : 0 ≤ z.2.1 k := (norm_nonneg _).trans hk1
    have e1 : ∀ᶠ p in 𝓝 (0 : (Fin N → E) × ℝ), p.2 < 1 := by
      have hc : ContinuousAt (fun p : (Fin N → E) × ℝ => p.2) 0 := continuous_snd.continuousAt
      exact hc.eventually_mem (s := Iio 1) (by simpa using Iio_mem_nhds (one_pos : (0 : ℝ) < 1))
    have e2 : ∀ᶠ p in 𝓝 (0 : (Fin N → E) × ℝ), k ∈ D → π.ρ₁ < (1 - p.2) * z.2.1 k := by
      by_cases hkD : k ∈ D
      · have hc : ContinuousAt (fun p : (Fin N → E) × ℝ => (1 - p.2) * z.2.1 k) 0 :=
          ((continuous_const.sub continuous_snd).mul continuous_const).continuousAt
        exact (hc.eventually_mem (by simpa using Ioi_mem_nhds (hD k hkD))).mono
          fun p hp _ => hp
      · exact Eventually.of_forall fun p h => absurd h hkD
    have e3 : ∀ᶠ p in 𝓝 (0 : (Fin N → E) × ℝ), k ∈ L →
        ‖(T p).1 k‖ < (T p).2.1 k ∧ ((T p).1 k, (T p).2.1 k) ∈ π.cone k := by
      by_cases hkL : k ∈ L
      · obtain ⟨hlt, hnhds⟩ := hL k hkL
        have hc : ContinuousAt (fun p => ((T p).1 k, (T p).2.1 k)) 0 :=
          (((continuous_apply k).comp (continuous_fst.comp hTc)).prodMk
            ((continuous_apply k).comp (continuous_fst.comp (continuous_snd.comp hTc))))
            |>.continuousAt
        have hopen : IsOpen {q : E × ℝ | ‖q.1‖ < q.2} :=
          isOpen_lt continuous_fst.norm continuous_snd
        have hmem : {q : E × ℝ | ‖q.1‖ < q.2} ∩ π.cone k ∈ 𝓝 ((T 0).1 k, (T 0).2.1 k) := by
          rw [hT0]; exact inter_mem (hopen.mem_nhds hlt) hnhds
        exact (hc.eventually_mem hmem).mono fun p hp _ => ⟨hp.1, hp.2⟩
      · exact Eventually.of_forall fun p h => absurd h hkL
    filter_upwards [e1, e2, e3] with p h1 h2 h3 hpos
    have hu := trial_u z L D dp p.1 p.2 k
    have hΓ := trial_Γ z L D dp p.1 p.2 k
    have h1t : 0 < 1 - p.2 := by linarith
    -- the slack bounds hold in every case
    have hlo : π.ρ₁ ≤ (T p).2.1 k := by
      rw [hΓ]; split_ifs with hkD
      · exact (h2 hkD).le
      · exact hk2
    have hhi : (T p).2.1 k ≤ π.ρ₂ := by
      rw [hΓ]; split_ifs with hkD
      · nlinarith
      · exact hk3
    by_cases hkL : k ∈ L
    · exact ⟨(h3 hkL).1.le, hlo, hhi, (h3 hkL).2⟩
    · refine ⟨?_, hlo, hhi, ?_⟩
      · rw [hu, hΓ]; split_ifs with hkD
        · simp only [add_zero, norm_smul, Real.norm_eq_abs, abs_of_pos h1t]
          exact mul_le_mul_of_nonneg_left hk1 h1t.le
        · simpa using hk1
      · rw [hu, hΓ]; split_ifs with hkD
        · simpa using hcone k _ _ h1t hk4
        · simpa using hk4
  filter_upwards [Filter.eventually_all.2 hnode, hother] with p hp hpo hpos
  exact ⟨fun k => hp k hpos, hpo hpos⟩

/-- The relaxed feasible set, written in the form the core lemma uses. -/
lemma relaxed_eq {z : Dec N E P} (hz : z ∈ π.relaxed) :
    π.relaxed = {z' | z' ∈ {z' | (∀ k, π.NodeOK k (z'.1 k) (z'.2.1 k)) ∧ z' ∈ π.other} ∧
      π.F z' = π.F z} := by
  ext z'
  simp [relaxed, hz.2.2, and_assoc]

/-! ### Main theorems -/

variable [CompleteSpace E] [CompleteSpace Y]

/-- **LCvx at one node.** Let `z` be a local minimizer of the relaxed problem. Suppose the cost
ignores `u`, and strictly drops whenever the slacks drop. Let `L` be a set of lossy nodes
(`‖u k‖ < Γ k`) where the cone constraint is not active, and `i` any node. If the thrusts at the
nodes of `L` already move `F` in every direction to first order, then the slack at `i` sits at
the lower bound `ρ₁`.

The other constraints only have to hold at the trial points that move the thrusts in `L` and
shrink node `i` (`hother`). Constraints that those moves cannot reach, such as path constraints
at earlier nodes of a causal system, may be active. -/
theorem slack_eq_lower_at (hρ₁ : 0 ≤ π.ρ₁)
    (hcone : ∀ k (q : E × ℝ) (t : ℝ), 0 < t → q ∈ π.cone k → t • q ∈ π.cone k)
    {z : Dec N E P} (hz : z ∈ π.relaxed) (hmin : IsLocalMinOn π.cost π.relaxed z)
    (hcost_u : ∀ u u' Γ p, π.cost (u, Γ, p) = π.cost (u', Γ, p))
    (hcost_Γ : ∀ Γ, Γ ≤ z.2.1 → Γ ≠ z.2.1 → π.cost (z.1, Γ, z.2.2) < π.cost z)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    (i : Fin N) (hother : ∀ᶠ p : (Fin N → E) × ℝ in 𝓝 0, 0 < p.2 →
      z + lossyIncl L p.1 + p.2 • scaleDir z {i} 0 ∈ π.other)
    {F' : Dec N E P →L[ℝ] Y} (hF : HasStrictFDerivAt π.F F' z)
    (hsurj : Function.Surjective (F' ∘L lossyIncl L)) :
    z.2.1 i = π.ρ₁ := by
  by_contra hi
  have hlt : π.ρ₁ < z.2.1 i := lt_of_le_of_ne (hz.1 i).2.1 (Ne.symm hi)
  have hΓi : 0 < z.2.1 i := hρ₁.trans_lt hlt
  have key := eventually_trial_mem hcone hz L {i} 0 hother hL (by simpa using hlt)
  refine not_isLocalMinOn_of_surjective (lossyIncl L) (scaleDir z {i} 0) hF hsurj ?_
    (relaxed_eq hz ▸ hmin)
  filter_upwards [key] with p hp hpos
  refine ⟨hp hpos, ?_⟩
  have hΓ' := trial_Γ z L {i} 0 p.1 p.2
  have hp' : (z + lossyIncl L p.1 + p.2 • scaleDir z {i} 0).2.2 = z.2.2 := by
    rw [trial_p, smul_zero, add_zero]
  calc π.cost (z + lossyIncl L p.1 + p.2 • scaleDir z {i} 0)
      = π.cost (z.1, (z + lossyIncl L p.1 + p.2 • scaleDir z {i} 0).2.1, z.2.2) := by
        rw [← hp']; exact hcost_u _ z.1 _ _
    _ < π.cost z := by
      apply hcost_Γ
      · intro k
        rw [hΓ' k]
        split_ifs
        · nlinarith [mul_nonneg hpos.le ((norm_nonneg _).trans (hz.1 k).1)]
        · exact le_rfl
      · intro heq
        have := congrFun heq i
        simp only [hΓ' i, Finset.mem_singleton_self, ↓reduceIte] at this
        nlinarith [mul_pos hpos hΓi]

/-- **LCvx, fixed time of flight.** Same as `slack_eq_lower_at`, with every other constraint
slack at `z`: then every slack sits at the lower bound `ρ₁`. -/
theorem slack_eq_lower_of_surjective (hρ₁ : 0 ≤ π.ρ₁)
    (hcone : ∀ k (q : E × ℝ) (t : ℝ), 0 < t → q ∈ π.cone k → t • q ∈ π.cone k)
    {z : Dec N E P} (hz : z ∈ π.relaxed) (hmin : IsLocalMinOn π.cost π.relaxed z)
    (hother : π.other ∈ 𝓝 z)
    (hcost_u : ∀ u u' Γ p, π.cost (u, Γ, p) = π.cost (u', Γ, p))
    (hcost_Γ : ∀ Γ, Γ ≤ z.2.1 → Γ ≠ z.2.1 → π.cost (z.1, Γ, z.2.2) < π.cost z)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    {F' : Dec N E P →L[ℝ] Y} (hF : HasStrictFDerivAt π.F F' z)
    (hsurj : Function.Surjective (F' ∘L lossyIncl L)) :
    ∀ k, z.2.1 k = π.ρ₁ := fun i =>
  slack_eq_lower_at hρ₁ hcone hz hmin hcost_u hcost_Γ L hL i
    (trial_mem_of_nhds hother L {i} 0) hF hsurj

/-- **LCvx, free time of flight.** Same setting, but now some other variable can lower the cost
by itself: moving `p` along `dp` (for example, landing slightly sooner) strictly reduces the
cost. Then no set of lossy nodes can steer `F` in every direction, with no degenerate case. -/
theorem not_surjective_of_free_param
    (hcone : ∀ k (q : E × ℝ) (t : ℝ), 0 < t → q ∈ π.cone k → t • q ∈ π.cone k)
    {z : Dec N E P} (hz : z ∈ π.relaxed) (hmin : IsLocalMinOn π.cost π.relaxed z)
    (hother : π.other ∈ 𝓝 z)
    (hcost_u : ∀ u u' Γ p, π.cost (u, Γ, p) = π.cost (u', Γ, p))
    (dp : P) (hdec : ∀ᶠ t in 𝓝[>] (0 : ℝ), π.cost (z.1, z.2.1, z.2.2 + t • dp) < π.cost z)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    {F' : Dec N E P →L[ℝ] Y} (hF : HasStrictFDerivAt π.F F' z) :
    ¬ Function.Surjective (F' ∘L lossyIncl L) := by
  intro hsurj
  have key := eventually_trial_mem hcone hz L ∅ dp (trial_mem_of_nhds hother L ∅ dp) hL (by simp)
  have hdec' : ∀ᶠ p in 𝓝 (0 : (Fin N → E) × ℝ), 0 < p.2 →
      π.cost (z.1, z.2.1, z.2.2 + p.2 • dp) < π.cost z := by
    rw [eventually_nhdsWithin_iff] at hdec
    have ht : Tendsto (fun p : (Fin N → E) × ℝ => p.2) (𝓝 0) (𝓝 0) := by
      simpa using (continuous_snd.tendsto (0 : (Fin N → E) × ℝ))
    exact ht.eventually hdec
  refine not_isLocalMinOn_of_surjective (lossyIncl L) (scaleDir z ∅ dp) hF hsurj ?_
    (relaxed_eq hz ▸ hmin)
  filter_upwards [key, hdec'] with p hp hc hpos
  refine ⟨hp hpos, ?_⟩
  have hp' := trial_p z L ∅ dp p.1 p.2
  have hΓ' : (z + lossyIncl L p.1 + p.2 • scaleDir z ∅ dp).2.1 = z.2.1 := funext fun k => by
    simp only [trial_Γ, Finset.notMem_empty, ↓reduceIte]
  calc π.cost (z + lossyIncl L p.1 + p.2 • scaleDir z ∅ dp)
      = π.cost (z.1, z.2.1, z.2.2 + p.2 • dp) := by
        rw [← hp', ← hΓ']; exact hcost_u _ z.1 _ _
    _ < π.cost z := hc hpos

/-- **Losslessness, fixed time of flight.** If some slack is strictly above `ρ₁` (the solution
is not the degenerate all-minimum-thrust one), no set of cone-inactive lossy nodes can steer `F`
in every direction. -/
theorem not_surjective_of_nondegenerate (hρ₁ : 0 ≤ π.ρ₁)
    (hcone : ∀ k (q : E × ℝ) (t : ℝ), 0 < t → q ∈ π.cone k → t • q ∈ π.cone k)
    {z : Dec N E P} (hz : z ∈ π.relaxed) (hmin : IsLocalMinOn π.cost π.relaxed z)
    (hother : π.other ∈ 𝓝 z)
    (hcost_u : ∀ u u' Γ p, π.cost (u, Γ, p) = π.cost (u', Γ, p))
    (hcost_Γ : ∀ Γ, Γ ≤ z.2.1 → Γ ≠ z.2.1 → π.cost (z.1, Γ, z.2.2) < π.cost z)
    (hnd : ∃ k, π.ρ₁ < z.2.1 k)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    {F' : Dec N E P →L[ℝ] Y} (hF : HasStrictFDerivAt π.F F' z) :
    ¬ Function.Surjective (F' ∘L lossyIncl L) := by
  intro hsurj
  obtain ⟨k, hk⟩ := hnd
  have := slack_eq_lower_of_surjective hρ₁ hcone hz hmin hother hcost_u hcost_Γ L hL hF hsurj k
  linarith

/-- **Counting lossy nodes.** Suppose any `m` nodes can steer `F` in every direction (a
controllability property of the linearized dynamics), and the cone constraint is inactive at the
lossy nodes. If no set of cone-inactive lossy nodes can steer `F` (which the two theorems above
give), then fewer than `m` nodes are lossy. -/
theorem card_lossy_lt {z : Dec N E P} {F' : Dec N E P →L[ℝ] Y} (m : ℕ)
    (hspan : ∀ L : Finset (Fin N), L.card = m → Function.Surjective (F' ∘L lossyIncl L))
    (hno : ∀ L ⊆ lossyNodes z, ¬ Function.Surjective (F' ∘L lossyIncl L)) :
    (lossyNodes z).card < m := by
  by_contra h
  obtain ⟨L, hLsub, hLcard⟩ := Finset.exists_subset_card_eq (not_lt.mp h)
  exact hno L hLsub (hspan L hLcard)

/-- The lossy nodes satisfy the hypothesis `hL` of the main theorems whenever the cone
constraint is inactive at each of them. -/
lemma lossy_hL {z : Dec N E P} (hcone_in : ∀ j ∈ lossyNodes z, π.cone j ∈ 𝓝 (z.1 j, z.2.1 j))
    (L : Finset (Fin N)) (hL : L ⊆ lossyNodes z) :
    ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π.cone j ∈ 𝓝 (z.1 j, z.2.1 j) := fun j hj =>
  ⟨by simpa [lossyNodes] using hL hj, hcone_in j (hL hj)⟩

end Problem

end LCvx
