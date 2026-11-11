import LCvx.Basic

/-!
# A concrete instance: the hypotheses can all hold, and the degenerate case is real

One node, scalar thrust `u`, slack `Γ`, thrust bounds `[1, 2]`, cost `Γ`, and one equality
constraint `u = 0` (the vehicle must not thrust at all). The relaxed problem's minimizer is
`u = 0, Γ = 1`: lossy, since `‖u‖ = 0 < 1 = Γ`.

Every hypothesis of `slack_eq_lower_of_surjective` holds here, so the theorem is not vacuous,
and its conclusion `Γ = ρ₁` is what happens. The original problem (`1 ≤ |u|` and `u = 0`) has no
feasible point at all, so with a fixed horizon the relaxation can really be lossy: the theorem's
"every slack at `ρ₁`" branch cannot be dropped.
-/

open Filter Topology Set

namespace LCvx.Example

/-- `u = 0` with thrust in `[1, 2]` and cost `Γ`. The extra variable `p : ℝ` is unused. -/
noncomputable def toy : Problem 1 ℝ ℝ ℝ where
  ρ₁ := 1
  ρ₂ := 2
  cone := fun _ => univ
  other := univ
  F := fun z => z.1 0
  y₀ := 0
  cost := fun z => z.2.1 0

/-- The minimizer: no thrust, slack at its lower bound. -/
def zstar : Dec 1 ℝ ℝ := (fun _ => 0, fun _ => 1, 0)

/-- The equality constraint map is linear: it reads off the thrust at node 0. -/
noncomputable def F' : Dec 1 ℝ ℝ →L[ℝ] ℝ :=
  (ContinuousLinearMap.proj 0).comp (ContinuousLinearMap.fst ℝ (Fin 1 → ℝ) ((Fin 1 → ℝ) × ℝ))

lemma zstar_mem : zstar ∈ toy.relaxed :=
  ⟨fun k => by simp [Problem.NodeOK, toy, zstar], mem_univ _, by simp [toy, zstar]⟩

lemma zstar_min : IsMinOn toy.cost toy.relaxed zstar := by
  rw [isMinOn_iff]
  intro z hz
  simpa [toy, zstar] using (hz.1 0).2.1

lemma zstar_lossy : ‖zstar.1 0‖ < zstar.2.1 0 := by simp [zstar]

/-- All hypotheses hold, and the conclusion is `Γ = ρ₁`. -/
theorem toy_slack_eq_lower : ∀ k, zstar.2.1 k = toy.ρ₁ :=
  Problem.slack_eq_lower_of_surjective (π := toy) (by simp [toy])
    (fun _ _ _ _ _ => mem_univ _) zstar_mem zstar_min.isLocalMinOn (by simp [toy])
    (fun _ _ _ _ => rfl)
    (fun Γ hle hne => by
      have h0 : Γ 0 < 1 := lt_of_le_of_ne (hle 0) fun h => hne (funext fun k => by
        rw [Subsingleton.elim k 0]; exact h)
      simpa [toy, zstar] using h0)
    {0} (fun j _ => by rw [Subsingleton.elim j 0]; exact ⟨zstar_lossy, by simp [toy]⟩)
    (F' := F') (by exact F'.hasStrictFDerivAt)
    (fun y => ⟨fun _ => y, by simp [F', lossyIncl]⟩)

/-- The original problem is infeasible, so the relaxed optimum cannot be lossless here. -/
theorem toy_original_empty : toy.original = ∅ := by
  ext x
  simp only [Problem.original, toy, embed, Set.mem_ofPred_eq, mem_empty_iff_false, iff_false]
  rintro ⟨hk, -, h0⟩
  have := (hk 0).1
  rw [h0, norm_zero] at this
  norm_num at this

/-! ### The steering hypothesis cannot be dropped

Same node, but now the equality constraint pins the slack, `Γ = 3/2`, and the thrust does not
enter it. The thrust cannot steer the constraint at all, and the minimizer `u = 0, Γ = 3/2` is
lossy with its slack strictly above `ρ₁`. Every other hypothesis of the theorems holds, so the
steering condition is needed: it is a property of the solution, not something that follows from
the rest of the setup. -/

/-- `Γ = 3/2` with thrust in `[1, 2]` and cost `Γ`. -/
noncomputable def toy2 : Problem 1 ℝ ℝ ℝ where
  ρ₁ := 1
  ρ₂ := 2
  cone := fun _ => univ
  other := univ
  F := fun z => z.2.1 0
  y₀ := 3 / 2
  cost := fun z => z.2.1 0

noncomputable def z2 : Dec 1 ℝ ℝ := (fun _ => 0, fun _ => 3 / 2, 0)

/-- The constraint map reads off the slack, so it is blind to the thrust. -/
noncomputable def G' : Dec 1 ℝ ℝ →L[ℝ] ℝ :=
  (ContinuousLinearMap.proj 0).comp ((ContinuousLinearMap.fst ℝ (Fin 1 → ℝ) ℝ).comp
    (ContinuousLinearMap.snd ℝ (Fin 1 → ℝ) ((Fin 1 → ℝ) × ℝ)))

theorem toy2_sharp :
    z2 ∈ toy2.relaxed ∧ IsMinOn toy2.cost toy2.relaxed z2 ∧ ‖z2.1 0‖ < z2.2.1 0 ∧
      toy2.ρ₁ < z2.2.1 0 ∧ ¬ Function.Surjective (G' ∘L lossyIncl {0}) := by
  refine ⟨⟨fun k => ?_, mem_univ _, by simp [toy2, z2]⟩, ?_, by norm_num [z2],
    by norm_num [toy2, z2], ?_⟩
  · simp only [Problem.NodeOK, toy2, z2]; norm_num
  · rw [isMinOn_iff]
    intro z hz
    have := hz.2.2
    simp only [toy2] at this
    simp [toy2, z2, this]
  · intro hs
    obtain ⟨w, hw⟩ := hs 1
    simp [G', lossyIncl] at hw

/-! ### An active state constraint can make the optimum lossy

Two nodes, a scalar integrator: the state after node 0 is `u₀`, the final state is `u₀ + u₁`.
The path constraint `u₀ ≤ 1/2` (a state bound at node 1) is active at the optimum, the terminal
condition is `u₀ + u₁ = 5/2`, thrust is in `[1, 2]`, and the cost is `Γ₀ + Γ₁`.

The minimizer `u = (1/2, 2), Γ = (1, 2)` is lossy at node 0, is not degenerate (`Γ₁ > ρ₁`), and
the lossy thrust can steer the terminal condition. The only hypothesis that fails is that the
path constraint has slack. The original problem has no feasible point at all. So an active state
constraint after a lossy node can break losslessness, and no guarantee can cover the nodes before
an active path constraint without steering it as well (as `sixDOF_fold` requires). -/

/-- Path constraint `u₀ ≤ 1/2`, terminal condition `u₀ + u₁ = 5/2`. -/
noncomputable def toy3 : Problem 2 ℝ ℝ ℝ where
  ρ₁ := 1
  ρ₂ := 2
  cone := fun _ => univ
  other := {z | z.1 0 ≤ 1 / 2}
  F := fun z => z.1 0 + z.1 1
  y₀ := 5 / 2
  cost := fun z => z.2.1 0 + z.2.1 1

noncomputable def z3 : Dec 2 ℝ ℝ := (![1 / 2, 2], ![1, 2], 0)

/-- The terminal map `u₀ + u₁`. -/
noncomputable def F3' : Dec 2 ℝ ℝ →L[ℝ] ℝ :=
  (ContinuousLinearMap.proj (R := ℝ) (φ := fun _ : Fin 2 => ℝ) 0 +
    ContinuousLinearMap.proj (R := ℝ) (φ := fun _ : Fin 2 => ℝ) 1).comp
    (ContinuousLinearMap.fst ℝ (Fin 2 → ℝ) ((Fin 2 → ℝ) × ℝ))

theorem toy3_sharp :
    z3 ∈ toy3.relaxed ∧ IsMinOn toy3.cost toy3.relaxed z3 ∧ ‖z3.1 0‖ < z3.2.1 0 ∧
      toy3.ρ₁ < z3.2.1 1 ∧ Function.Surjective (F3' ∘L lossyIncl {0}) ∧
      toy3.original = ∅ := by
  refine ⟨⟨fun k => ?_, ?_, ?_⟩, ?_, ?_, ?_, ?_, ?_⟩
  · fin_cases k <;> norm_num [Problem.NodeOK, toy3, z3]
  · simp [toy3, z3]
  · simp [toy3, z3]; norm_num
  · rw [isMinOn_iff]
    rintro z ⟨hn, ho, hF⟩
    simp only [toy3, Set.mem_ofPred_eq] at ho hF
    have h1 := (hn 1).1
    have h0 := (hn 0).2.1
    have h1' := (hn 1).2.2.1
    simp only [toy3] at h0 h1'
    have hu1 : 2 ≤ z.1 1 := by linarith
    have hn1 : (2 : ℝ) ≤ ‖z.1 1‖ := by
      rw [Real.norm_eq_abs]; exact le_trans hu1 (le_abs_self _)
    simp only [toy3, z3]
    norm_num
    linarith
  · simp [z3]; norm_num
  · simp [toy3, z3]
  · intro y
    refine ⟨fun _ => y, ?_⟩
    simp [F3', lossyIncl]
  · ext x
    simp only [Problem.original, toy3, embed, Set.mem_ofPred_eq, mem_empty_iff_false, iff_false]
    rintro ⟨hk, ho, hF⟩
    have h0 := (hk 0).1
    have h1 := (hk 1).2.1
    rw [Real.norm_eq_abs] at h0 h1
    rcases le_or_gt 0 (x.1 0) with hx | hx
    · rw [abs_of_nonneg hx] at h0; linarith
    · rw [abs_of_neg hx] at h0
      have : x.1 1 ≤ 2 := le_trans (le_abs_self _) h1
      linarith

end LCvx.Example
