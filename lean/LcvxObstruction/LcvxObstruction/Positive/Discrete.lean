import LcvxObstruction.Positive.Cap

/-!
# Positive side, Tier 1/4: discrete-time results (C-K1, C-K2, C-E(a))

Source: `math/04` §4 and §7; blueprint P19, P20, P21.

* `discrete_lossless_nodewise` (**C-K1**, P19): nodewise KKT test. At every node whose discrete
  primer `p_j ∉ -ℝ≥0 b_j`, the relaxed SOCP solution is lossless and nodewise unique.
* `isMaxOn_of_normal_joint` : the KKT stationarity condition in `(u_j, σ_j)` implies the nodewise
  maximization used by C-K1.
* `zoh_r`, `zoh_v`, `zoh_pairing`, `zoh_primer_affine` : for the ZOH double integrator the
  gradient of the terminal pairing `⟪ν_r, r_N⟫ + ⟪ν_v, v_N⟫` in `u_j` is affine in `j`.
* `exchange_min_throttle` (**C-E(a)**, discrete, P20): lossy nodes of a fuel-optimal relaxed
  solution are at minimum throttle.
* `purification_count` (**C-K2**, P21): an extreme point `ū` of the optimal-face set
  `S = {u | u_j ∈ K_{σ_j}(b_j), A u ∈ X}` has `n · #lossy + dim M ≤ dim W`, where `n + 1 = dim E`
  and `M` is any subspace of two-sided feasible directions of `X` at `A ū` (so
  `dim W - dim M = Σ c_i`). In `ℝ³` with only a 6-dimensional terminal equality constraint:
  at most 3 lossy nodes (`purification_three`).
-/

open scoped RealInnerProductSpace
open Set Module

namespace LcvxPositive

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-! ## C-K1: nodewise test -/

/-- KKT stationarity in `(u_j, σ_j)` (normal-cone form) restricted to `σ = σ_j` gives nodewise
maximization of `⟪p_j, ·⟫` over the cap. -/
theorem isMaxOn_of_normal_joint {b p u : V} {σ r δ ρ₁ ρ₂ : ℝ}
    (hN : ∀ S G, S ∈ cap b G (G * Real.cos δ) → ρ₁ ≤ G → G ≤ ρ₂ →
      ⟪p, S - u⟫ + r * (G - σ) ≤ 0) (hσ : ρ₁ ≤ σ ∧ σ ≤ ρ₂) :
    IsMaxOn (fun S => ⟪p, S⟫) (cap b σ (σ * Real.cos δ)) u := by
  rw [isMaxOn_iff]
  intro S hS
  have := hN S σ hS hσ.1 hσ.2
  rw [inner_sub_right, sub_self, mul_zero, add_zero] at this
  linarith

/-- **C-K1 (P19).** Nodewise lossless test: if at node `j` the control `u j` maximizes
`⟪p j, ·⟫` over `K_{σ j}(b j)` and `p j ∉ -ℝ≥0 b j`, then `‖u j‖ = σ j` and `u j` is the unique
maximizer. -/
theorem discrete_lossless_nodewise {N : ℕ} {b p u : Fin N → V} {σ : Fin N → ℝ} {δ : ℝ}
    (hb : ∀ j, b j ≠ 0) (hmem : ∀ j, u j ∈ cap (b j) (σ j) (σ j * Real.cos δ))
    (hmax : ∀ j, IsMaxOn (fun S => ⟪p j, S⟫) (cap (b j) (σ j) (σ j * Real.cos δ)) (u j)) :
    ∀ j, ¬ AntiRay (b j) (p j) → ‖u j‖ = σ j ∧
      ∀ S ∈ cap (b j) (σ j) (σ j * Real.cos δ),
        IsMaxOn (fun S => ⟪p j, S⟫) (cap (b j) (σ j) (σ j * Real.cos δ)) S → S = u j := by
  intro j hj
  exact ⟨norm_eq_of_isMaxOn_cap (hb j) hj (hmem j) (hmax j),
    fun S hS hSm => isMaxOn_cap_unique (hb j) hj hS (hmem j) hSm (hmax j)⟩

/-! ## ZOH double integrator: the discrete primer is affine -/

/-- ZOH velocity recursion `v_{k+1} = v_k + h w_k` (with `w = u + g`). -/
noncomputable def zoh_v (h : ℝ) (v0 : V) (w : ℕ → V) : ℕ → V
  | 0 => v0
  | k + 1 => zoh_v h v0 w k + h • w k

/-- ZOH position recursion `r_{k+1} = r_k + h v_k + (h²/2) w_k`. -/
noncomputable def zoh_r (h : ℝ) (r0 v0 : V) (w : ℕ → V) : ℕ → V
  | 0 => r0
  | k + 1 => zoh_r h r0 v0 w k + h • zoh_v h v0 w k + (h ^ 2 / 2) • w k

theorem zoh_v_eq (h : ℝ) (v0 : V) (w : ℕ → V) (n : ℕ) :
    zoh_v h v0 w n = v0 + ∑ j ∈ Finset.range n, h • w j := by
  induction n with
  | zero => simp [zoh_v]
  | succ n ih => rw [zoh_v, ih, Finset.sum_range_succ, add_assoc]

theorem zoh_r_eq (h : ℝ) (r0 v0 : V) (w : ℕ → V) (n : ℕ) :
    zoh_r h r0 v0 w n = r0 + ((n : ℝ) * h) • v0 +
      ∑ j ∈ Finset.range n, (h ^ 2 * ((n : ℝ) - j - 1/2)) • w j := by
  induction n with
  | zero => simp [zoh_r]
  | succ n ih =>
    rw [zoh_r, ih, zoh_v_eq, Finset.sum_range_succ, smul_add, Finset.smul_sum]
    have : ∑ j ∈ Finset.range n, (h ^ 2 * (((n + 1 : ℕ) : ℝ) - j - 1/2)) • w j =
        ∑ j ∈ Finset.range n, ((h ^ 2 * ((n : ℝ) - j - 1/2)) • w j + h • h • w j) := by
      apply Finset.sum_congr rfl
      intro j _
      rw [smul_smul, ← add_smul]
      congr 1
      push_cast
      ring
    rw [this, Finset.sum_add_distrib]
    push_cast
    module

/-- The terminal pairing is affine in the controls with node weight
`q_j = h² (N - j - ½) ν_r + h ν_v`. -/
theorem zoh_pairing (h : ℝ) (r0 v0 νr νv : V) (w : ℕ → V) (N : ℕ) :
    ⟪νr, zoh_r h r0 v0 w N⟫ + ⟪νv, zoh_v h v0 w N⟫ =
      (⟪νr, r0 + ((N : ℝ) * h) • v0⟫ + ⟪νv, v0⟫) +
      ∑ j ∈ Finset.range N, ⟪(h ^ 2 * ((N : ℝ) - j - 1/2)) • νr + h • νv, w j⟫ := by
  rw [zoh_r_eq, zoh_v_eq]
  simp only [inner_add_right, inner_sum, inner_add_left, real_inner_smul_left,
    real_inner_smul_right, Finset.sum_add_distrib]
  ring

/-- **Discrete primer is affine (C-K1, ZOH, no state constraints).** The discrete primer
`p_j = -(h² (N - j - ½) ν_r + h ν_v)` equals `primer`-form `a + j c` with
`a = -(h²(N - ½) ν_r + h ν_v)`, `c = h² ν_r`. -/
theorem zoh_primer_affine (h : ℝ) (νr νv : V) (N j : ℕ) :
    -((h ^ 2 * ((N : ℝ) - j - 1/2)) • νr + h • νv) =
      -((h ^ 2 * ((N : ℝ) - 1/2)) • νr + h • νv) + (j : ℝ) • (h ^ 2 • νr) := by
  module

/-! ## C-E(a): exchange (PMP-free) -/

/-- **C-E(a), discrete (P20).** Constant mass, cost `∑ w_j σ_j` with `w_j > 0`, dynamics
depending on `u` only, `cos δ ≥ 0`. At an optimum, every lossy node is at minimum throttle. -/
theorem exchange_min_throttle {N : ℕ} {b u : Fin N → V} {σ w : Fin N → ℝ} {δ ρ₁ ρ₂ : ℝ}
    (Dyn : (Fin N → V) → Prop) (hw : ∀ j, 0 < w j) (hcos : 0 ≤ Real.cos δ)
    (hfeas : (∀ j, u j ∈ cap (b j) (σ j) (σ j * Real.cos δ) ∧ ρ₁ ≤ σ j ∧ σ j ≤ ρ₂) ∧ Dyn u)
    (hopt : ∀ (u' : Fin N → V) (σ' : Fin N → ℝ),
      ((∀ j, u' j ∈ cap (b j) (σ' j) (σ' j * Real.cos δ) ∧ ρ₁ ≤ σ' j ∧ σ' j ≤ ρ₂) ∧ Dyn u') →
      ∑ j, w j * σ j ≤ ∑ j, w j * σ' j) :
    ∀ j, ‖u j‖ < σ j → σ j = ρ₁ := by
  intro j hlt
  by_contra hne
  have hgt : ρ₁ < σ j := lt_of_le_of_ne (hfeas.1 j).2.1 (Ne.symm hne)
  set g : ℝ := max ρ₁ ‖u j‖
  have hg : g < σ j := max_lt hgt hlt
  let σ' : Fin N → ℝ := Function.update σ j g
  have hσ' : ∀ i, σ' i ≤ σ i := by
    intro i
    by_cases hi : i = j
    · subst hi; simp [σ', hg.le]
    · simp [σ', Function.update_of_ne hi]
  have hfeas' : (∀ i, u i ∈ cap (b i) (σ' i) (σ' i * Real.cos δ) ∧ ρ₁ ≤ σ' i ∧ σ' i ≤ ρ₂)
      ∧ Dyn u := by
    refine ⟨fun i => ?_, hfeas.2⟩
    obtain ⟨⟨h1, h2⟩, h3, h4⟩ := hfeas.1 i
    by_cases hi : i = j
    · subst hi
      simp only [σ', Function.update_self]
      refine ⟨⟨le_max_right _ _, ?_⟩, le_max_left _ _, hg.le.trans h4⟩
      exact le_trans (mul_le_mul_of_nonneg_right hg.le hcos) h2
    · simp only [σ', Function.update_of_ne hi]
      exact ⟨⟨h1, h2⟩, h3, h4⟩
  have hlt' : ∑ i, w i * σ' i < ∑ i, w i * σ i := by
    apply Finset.sum_lt_sum
    · intro i _; exact mul_le_mul_of_nonneg_left (hσ' i) (hw i).le
    · refine ⟨j, Finset.mem_univ _, ?_⟩
      simp only [σ', Function.update_self]
      exact mul_lt_mul_of_pos_left hg (hw j)
  have := hopt u σ' hfeas'
  linarith

/-! ## C-K2: purification -/

section Purification

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [FiniteDimensional ℝ E]
variable {W : Type*} [AddCommGroup W] [Module ℝ W] [FiniteDimensional ℝ W]

/-- Extension by zero from the lossy nodes `J` into all nodes. -/
def embedJ {N : ℕ} (J : Finset (Fin N)) (K : Fin N → Submodule ℝ E) :
    ((j : J) → K j) →ₗ[ℝ] (Fin N → E) where
  toFun v i := if h : i ∈ J then (v ⟨i, h⟩ : E) else 0
  map_add' v v' := by funext i; by_cases h : i ∈ J <;> simp [h]
  map_smul' r v := by funext i; by_cases h : i ∈ J <;> simp [h]

omit [FiniteDimensional ℝ E] in
theorem embedJ_injective {N : ℕ} (J : Finset (Fin N)) (K : Fin N → Submodule ℝ E) :
    Function.Injective (embedJ J K) := by
  rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
  intro v hv
  funext ⟨i, hi⟩
  have := congrFun hv i
  simp only [embedJ, LinearMap.coe_mk, AddHom.coe_mk, hi, dite_true, Pi.zero_apply] at this
  exact Subtype.ext this

/-- **C-K2 (P21), general form.** Let `E` have dimension `n+1`, `A : (Fin N → E) →ₗ W` linear,
`X ⊆ W` convex, and `S = {u | (∀ j, u_j ∈ K_{σ_j}(b_j)) ∧ A u ∈ X}` (`b_j ≠ 0`, arbitrary cap
levels `c_j`). Let `M ≤ W` be a subspace of two-sided feasible directions of `X` at `A ū`
(e.g. the lineality space of the minimal face of `X` containing `A ū`; `dim W - dim M = Σ c_i`).
If `ū` is an extreme point of `S`, then `n · #{j | ‖ū_j‖ < σ_j} + dim M ≤ dim W`. -/
theorem purification_count {n N : ℕ} [Fact (finrank ℝ E = n + 1)]
    {b : Fin N → E} {σ cc : Fin N → ℝ} (hb : ∀ j, b j ≠ 0)
    (A : (Fin N → E) →ₗ[ℝ] W) {X : Set W} (hX : Convex ℝ X) (M : Submodule ℝ W)
    {ubar : Fin N → E}
    (hext : ubar ∈ ({u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u ∈ X} : Set (Fin N → E)).extremePoints ℝ)
    (hM : ∀ d ∈ M, ∃ ε : ℝ, 0 < ε ∧ A ubar + ε • d ∈ X ∧ A ubar - ε • d ∈ X) :
    n * (Finset.univ.filter (fun j => ‖ubar j‖ < σ j)).card + finrank ℝ M ≤ finrank ℝ W := by
  classical
  set S : Set (Fin N → E) := {u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u ∈ X} with hSdef
  set J := Finset.univ.filter (fun j => ‖ubar j‖ < σ j) with hJ
  have huS : ubar ∈ S := (mem_extremePoints.mp hext).1
  by_contra hcon
  push Not at hcon
  -- J is nonempty (otherwise the bound is `dim M ≤ dim W`)
  have hJne : J.Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro h0
    rw [h0, Finset.card_empty, mul_zero, zero_add] at hcon
    exact absurd (Submodule.finrank_le M) (not_le.mpr hcon)
  let K : Fin N → Submodule ℝ E := fun j => (ℝ ∙ b j)ᗮ
  have hK : ∀ j, finrank ℝ (K j) = n := fun j => Submodule.finrank_orthogonal_span_singleton (hb j)
  let f : ((j : J) → K j) →ₗ[ℝ] W ⧸ M := M.mkQ ∘ₗ A ∘ₗ embedJ J K
  have hdom : finrank ℝ ((j : J) → K j) = n * J.card := by
    rw [Module.finrank_pi_fintype]
    simp only [hK, Finset.sum_const, Finset.card_univ, Fintype.card_coe, smul_eq_mul]
    ring
  have hcod : finrank ℝ (W ⧸ M) + finrank ℝ M = finrank ℝ W :=
    Submodule.finrank_quotient_add_finrank M
  have hker : LinearMap.ker f ≠ ⊥ := LinearMap.ker_ne_bot_of_finrank_lt (by omega)
  obtain ⟨v, hvk, hv0⟩ := (Submodule.ne_bot_iff _).mp hker
  set du := embedJ J K v with hdu
  have hdu0 : du ≠ 0 := by
    intro h0
    exact hv0 (embedJ_injective J K (by rw [← hdu, h0, map_zero]))
  have hAdu : A du ∈ M := by
    have : f v = 0 := hvk
    simpa [f, Submodule.mkQ_apply, Submodule.Quotient.mk_eq_zero] using this
  obtain ⟨ε₀, hε₀, hp0, hm0⟩ := hM _ hAdu
  -- uniform slack on the lossy nodes
  set η : ℝ := J.inf' hJne (fun j => σ j - ‖ubar j‖) with hη
  have hη0 : 0 < η := by
    rw [hη, Finset.lt_inf'_iff]
    intro j hj
    have : ‖ubar j‖ < σ j := (Finset.mem_filter.mp hj).2
    linarith
  set ε₁ : ℝ := η / (‖du‖ + 1)
  have hε₁ : 0 < ε₁ := div_pos hη0 (by positivity)
  set ε : ℝ := min ε₀ ε₁
  have hε : 0 < ε := lt_min hε₀ hε₁
  have hεdu : ε * ‖du‖ ≤ η := by
    have h1 : ε ≤ ε₁ := min_le_right _ _
    have h2 : ε₁ * (‖du‖ + 1) = η := div_mul_cancel₀ _ (by positivity)
    nlinarith [norm_nonneg du]
  -- membership of `ubar ± ε du` in S
  have hcomp : ∀ s : ℝ, |s| ≤ ε → ubar + s • du ∈ S ∨ True := fun _ _ => Or.inr trivial
  clear hcomp
  have hdu_out : ∀ j, j ∉ J → du j = 0 := by
    intro j hj
    simp [hdu, embedJ, hj]
  have hdu_in : ∀ j, j ∈ J → ⟪b j, du j⟫ = 0 := by
    intro j hj
    have : du j = (v ⟨j, hj⟩ : E) := by simp [hdu, embedJ, hj]
    rw [this]
    exact (Submodule.mem_orthogonal_singleton_iff_inner_right).mp (v ⟨j, hj⟩).2
  have hcapmove : ∀ s : ℝ, |s| ≤ ε → ∀ j, ubar j + s • du j ∈ cap (b j) (σ j) (cc j) := by
    intro s hs j
    have hu := huS.1 j
    by_cases hj : j ∈ J
    · refine ⟨?_, ?_⟩
      · have hηj : η ≤ σ j - ‖ubar j‖ := by rw [hη]; exact Finset.inf'_le _ hj
        calc ‖ubar j + s • du j‖ ≤ ‖ubar j‖ + |s| * ‖du j‖ := by
              refine (norm_add_le _ _).trans ?_
              rw [norm_smul, Real.norm_eq_abs]
          _ ≤ ‖ubar j‖ + ε * ‖du‖ := by
              gcongr
              exact norm_le_pi_norm du j
          _ ≤ σ j := by linarith
      · rw [inner_add_right, real_inner_smul_right, hdu_in j hj, mul_zero, add_zero]
        exact hu.2
    · rw [hdu_out j hj, smul_zero, add_zero]; exact hu
  have hXmove : ∀ s : ℝ, s = ε ∨ s = -ε → A (ubar + s • du) ∈ X := by
    intro s hs
    rw [map_add, map_smul]
    have key : ∀ z ∈ X, A ubar + ε • A du = (1 - ε / ε₀) • A ubar + (ε / ε₀) • z →
        A ubar + ε • A du ∈ X := by
      intro z hz heq
      rw [heq]
      exact hX huS.2 hz (by
        have : ε / ε₀ ≤ 1 := (div_le_one hε₀).mpr (min_le_left _ _)
        linarith) (div_nonneg hε.le hε₀.le) (by ring)
    rcases hs with rfl | rfl
    · refine key _ hp0 ?_
      rw [smul_add, smul_smul, div_mul_cancel₀ _ hε₀.ne']
      module
    · have key' : A ubar + ε • (-A du) = (1 - ε / ε₀) • A ubar + (ε / ε₀) • (A ubar - ε₀ • A du) := by
        rw [smul_sub, smul_smul, div_mul_cancel₀ _ hε₀.ne']
        module
      have hmem : A ubar + ε • (-A du) ∈ X := by
        rw [key']
        exact hX huS.2 hm0 (by
          have : ε / ε₀ ≤ 1 := (div_le_one hε₀).mpr (min_le_left _ _)
          linarith) (div_nonneg hε.le hε₀.le) (by ring)
      rw [neg_smul, ← smul_neg]
      exact hmem
  have hplus : ubar + ε • du ∈ S :=
    ⟨fun j => by simpa using hcapmove ε (by rw [abs_of_pos hε]) j, hXmove ε (Or.inl rfl)⟩
  have hminus : ubar + (-ε) • du ∈ S :=
    ⟨fun j => by simpa using hcapmove (-ε) (by rw [abs_neg, abs_of_pos hε]) j,
      hXmove (-ε) (Or.inr rfl)⟩
  have hseg : ubar ∈ openSegment ℝ (ubar + ε • du) (ubar + (-ε) • du) := by
    refine ⟨1/2, 1/2, by norm_num, by norm_num, by norm_num, ?_⟩
    module
  have heq := ((mem_extremePoints.mp hext).2 _ hplus _ hminus hseg).1
  have : ε • du = 0 := by
    have := congrArg (fun z => z - ubar) heq
    simpa using this
  rcases smul_eq_zero.mp this with h | h
  · exact hε.ne' h
  · exact hdu0 h

/-- Existence of a purified optimum: a nonempty compact `S` has an extreme point
(Krein–Milman, finite dimension), so the bound of `purification_count` is attained by some
element of the optimal face. Terminal-equality form (`X = {y}`, `M = ⊥`). -/
theorem exists_purified {n N : ℕ} [Fact (finrank ℝ E = n + 1)]
    {b : Fin N → E} {σ cc : Fin N → ℝ} (hb : ∀ j, b j ≠ 0)
    (A : (Fin N → E) →ₗ[ℝ] W) [TopologicalSpace W] [IsTopologicalAddGroup W]
    [ContinuousSMul ℝ W] [T2Space W] (y : W)
    (hne : ({u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u = y} : Set (Fin N → E)).Nonempty) :
    ∃ ubar, ((∀ j, ubar j ∈ cap (b j) (σ j) (cc j)) ∧ A ubar = y) ∧
      n * (Finset.univ.filter (fun j => ‖ubar j‖ < σ j)).card ≤ finrank ℝ W := by
  set S : Set (Fin N → E) := {u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u = y}
  have hAc : Continuous A := A.continuous_of_finiteDimensional
  have hclosed : IsClosed S := by
    have h1 : IsClosed {u : Fin N → E | ∀ j, u j ∈ cap (b j) (σ j) (cc j)} := by
      simp only [ofPred_forall]
      exact isClosed_iInter fun j => (isClosed_cap (b j) (σ j) (cc j)).preimage (continuous_apply j)
    exact h1.inter (isClosed_eq hAc continuous_const)
  have hbdd : Bornology.IsBounded S := by
    rw [Metric.isBounded_iff_subset_closedBall 0]
    refine ⟨∑ j, |σ j|, fun u hu => ?_⟩
    rw [Metric.mem_closedBall, dist_zero_right]
    refine (pi_norm_le_iff_of_nonneg (by positivity)).mpr fun j => ?_
    calc ‖u j‖ ≤ σ j := (hu.1 j).1
      _ ≤ |σ j| := le_abs_self _
      _ ≤ ∑ j, |σ j| := Finset.single_le_sum (f := fun j => |σ j|) (fun j _ => abs_nonneg _)
          (Finset.mem_univ j)
  have hcpt : IsCompact S := Metric.isCompact_of_isClosed_isBounded hclosed hbdd
  obtain ⟨ubar, hext⟩ := hcpt.extremePoints_nonempty hne
  refine ⟨ubar, (mem_extremePoints.mp hext).1, ?_⟩
  have hext' : ubar ∈ ({u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u ∈ ({y} : Set W)} :
      Set (Fin N → E)).extremePoints ℝ := by
    simpa only [mem_singleton_iff] using hext
  have := purification_count (n := n) hb A (convex_singleton y) ⊥ hext'
    (fun d hd => ⟨1, one_pos, by
      rw [(Submodule.mem_bot ℝ).mp hd, smul_zero, add_zero]
      exact (mem_extremePoints.mp hext).1.2, by
      rw [(Submodule.mem_bot ℝ).mp hd, smul_zero, sub_zero]
      exact (mem_extremePoints.mp hext).1.2⟩)
  rw [finrank_bot, add_zero] at this
  exact this

end Purification

instance fact_finrank_three : Fact (finrank ℝ (EuclideanSpace ℝ (Fin 3)) = 2 + 1) :=
  ⟨by simp⟩

/-- **C-K2 headline (no state constraints).** In `ℝ³`, with the terminal state (a
6-dimensional linear image of the controls, `finrank W = 6`) prescribed, the optimal face of the
discrete relaxed SOCP contains a solution with **at most 3 lossy nodes**. -/
theorem purification_three {N : ℕ} {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W]
    [FiniteDimensional ℝ W] (hW : finrank ℝ W = 6)
    {b : Fin N → EuclideanSpace ℝ (Fin 3)} {σ cc : Fin N → ℝ} (hb : ∀ j, b j ≠ 0)
    (A : (Fin N → EuclideanSpace ℝ (Fin 3)) →ₗ[ℝ] W) (y : W)
    (hne : ({u | (∀ j, u j ∈ cap (b j) (σ j) (cc j)) ∧ A u = y} :
      Set (Fin N → EuclideanSpace ℝ (Fin 3))).Nonempty) :
    ∃ ubar, ((∀ j, ubar j ∈ cap (b j) (σ j) (cc j)) ∧ A ubar = y) ∧
      (Finset.univ.filter (fun j => ‖ubar j‖ < σ j)).card ≤ 3 := by
  obtain ⟨ubar, hS, hcount⟩ := exists_purified (n := 2) hb A y hne
  exact ⟨ubar, hS, by omega⟩

end LcvxPositive
