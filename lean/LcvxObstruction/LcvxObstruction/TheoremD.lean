import Mathlib

/-!
# Theorem D (abstract): state-linear relaxations of a single instance are lossy

Setting (blueprint D6). One fixed problem instance (fixed initial state). `Reach ⊆ E` is the
set of *genuine* reachable readouts (e.g. terminal states `(r(tf), v(tf))`).
A **state-linear relaxation** consists of
* a convex set `C` in a real vector space `Y` (relaxed decision variables, any lifting),
* an affine readout `ρ : Y →ᵃ E` (the physical state is an affine function of the relaxed
  variables),
* a penalty `P : Y → ℝ`, convex and nonnegative on `C`,
such that every genuine readout is represented by a relaxed point with zero penalty.

Theorem D: every point of `convexHull Reach` is then also represented with zero penalty.
So for the *minimum landing error* cost `‖ρ y - q‖ + P y`, with a target `q` in
`convexHull Reach` but outside `closure Reach`, the relaxed optimum value is `0`, while every
genuine point has error at least `infDist q Reach > 0`, and every relaxed optimum reads out
a non-genuine state. So the relaxation is not lossless.

Out of scope (the stated boundary of the impossibility): costs or terminal constraints that
are not functions of `ρ y` (moment / Shor lifts with costs linear in `R ⪰ r rᵀ`,
occupation-measure LPs).
-/

open Set Metric

namespace LcvxObstruction

variable {Y E : Type*} [AddCommGroup Y] [Module ℝ Y]

/-- A **state-linear relaxation** of one instance, with readout space `E`. -/
structure StateLinearRelaxation (Y E : Type*) [AddCommGroup Y] [Module ℝ Y] [AddCommGroup E]
    [Module ℝ E] where
  /-- Relaxed feasible set. -/
  C : Set Y
  convex : Convex ℝ C
  /-- Affine readout of the physical (terminal) state. -/
  ρ : Y →ᵃ[ℝ] E
  /-- Convex nonnegative penalty (e.g. slack cost, zero on genuine points). -/
  P : Y → ℝ
  P_convex : ConvexOn ℝ C P
  P_nonneg : ∀ y ∈ C, 0 ≤ P y

namespace StateLinearRelaxation

variable [AddCommGroup E] [Module ℝ E]

/-- The relaxation **contains** the genuine set `Reach`: each genuine readout is attained by a
relaxed point of zero penalty. -/
def Contains (S : StateLinearRelaxation Y E) (Reach : Set E) : Prop :=
  ∀ x ∈ Reach, ∃ y ∈ S.C, S.ρ y = x ∧ S.P y = 0

/-- The set of readouts attained with zero penalty is convex. -/
theorem convex_zeroPenaltyReadouts (S : StateLinearRelaxation Y E) :
    Convex ℝ {x | ∃ y ∈ S.C, S.ρ y = x ∧ S.P y = 0} := by
  have hZ : Convex ℝ {y ∈ S.C | S.P y ≤ 0} := S.P_convex.convex_le 0
  have := hZ.affine_image S.ρ
  convert this using 1
  ext x
  constructor
  · rintro ⟨y, hy, rfl, h0⟩
    exact ⟨y, ⟨hy, h0.le⟩, rfl⟩
  · rintro ⟨y, ⟨hy, h0⟩, rfl⟩
    exact ⟨y, hy, rfl, le_antisymm h0 (S.P_nonneg y hy)⟩

/-- **Theorem D (abstract).** A state-linear relaxation containing `Reach` represents every
point of `convexHull Reach` with zero penalty. -/
theorem convexHull_subset (S : StateLinearRelaxation Y E) {Reach : Set E}
    (h : S.Contains Reach) :
    ∀ x ∈ convexHull ℝ Reach, ∃ y ∈ S.C, S.ρ y = x ∧ S.P y = 0 :=
  fun _ hx => convexHull_min (fun x hx => h x hx) S.convex_zeroPenaltyReadouts hx

end StateLinearRelaxation

section MinError

variable [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- **Corollary D.1 (minimum landing error is lossy).** Let `q ∈ convexHull Reach`,
`q ∉ closure Reach`. For the relaxed cost `y ↦ ‖ρ y - q‖ + P y`:
(1) the relaxed problem attains value `0`;
(2) every genuine point has error `≥ infDist q Reach > 0` (so the true optimal value is
    `≥ infDist q Reach > 0`);
(3) every relaxed optimum reads out a state outside `closure Reach` (non-genuine). -/
theorem minError_lossy (S : StateLinearRelaxation Y E) {Reach : Set E}
    (h : S.Contains Reach) {q : E} (hq : q ∈ convexHull ℝ Reach) (hq' : q ∉ closure Reach) :
    (∃ y ∈ S.C, ‖S.ρ y - q‖ + S.P y = 0) ∧
    0 < infDist q Reach ∧
    (∀ x ∈ Reach, infDist q Reach ≤ ‖x - q‖) ∧
    (∀ y ∈ S.C, (∀ y' ∈ S.C, ‖S.ρ y - q‖ + S.P y ≤ ‖S.ρ y' - q‖ + S.P y') →
      S.ρ y ∉ closure Reach) := by
  have hne : Reach.Nonempty := by
    by_contra h0
    rw [not_nonempty_iff_eq_empty] at h0
    simp [h0] at hq
  obtain ⟨y₀, hy₀, hρ₀, hP₀⟩ := S.convexHull_subset h q hq
  refine ⟨⟨y₀, hy₀, by simp [hρ₀, hP₀]⟩, ?_, ?_, ?_⟩
  · exact lt_of_le_of_ne infDist_nonneg (Ne.symm ((mem_closure_iff_infDist_zero hne).not.mp hq'))
  · intro x hx
    rw [← dist_eq_norm, dist_comm]
    exact infDist_le_dist_of_mem hx
  · intro y hy hopt hcl
    have h1 := hopt y₀ hy₀
    rw [hρ₀, hP₀, sub_self, norm_zero, add_zero] at h1
    have h2 : ‖S.ρ y - q‖ = 0 := le_antisymm (by linarith [S.P_nonneg y hy]) (norm_nonneg _)
    rw [norm_eq_zero, sub_eq_zero] at h2
    exact hq' (h2 ▸ hcl)

/-- Orchestrator's form: a convex `K ⊇ L` containing a point `q ∈ convexHull L \ L` of a
closed `L` has `inf_{x∈K} ‖x - q‖ = 0 < infDist q L`. -/
theorem convex_superset_gap {K L : Set E} (hK : Convex ℝ K) (hKL : L ⊆ K) (hL : IsClosed L)
    {q : E} (hq : q ∈ convexHull ℝ L) (hq' : q ∉ L) :
    q ∈ K ∧ 0 < infDist q L := by
  refine ⟨convexHull_min hKL hK hq, ?_⟩
  have hne : L.Nonempty := by
    by_contra h0
    rw [not_nonempty_iff_eq_empty] at h0
    simp [h0] at hq
  rw [← hL.closure_eq] at hq'
  exact lt_of_le_of_ne infDist_nonneg (Ne.symm ((mem_closure_iff_infDist_zero hne).not.mp hq'))

end MinError

end LcvxObstruction
