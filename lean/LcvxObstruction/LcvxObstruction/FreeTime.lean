import LcvxObstruction.Abstract

/-!
# Lemma RR-LS: line search over the final time cannot be lossless

(math/redteam-reform.md §4.) Horizons `t ∈ W` (any index type `ι`, any subset `W`); for each `t`
the true feasible set `F t ⊆ X`, and a per-horizon uniform convex relaxation `C t`
(lifted space `Y t`, which may depend on `t`). Line search over `t` accepts the datum `x` iff
some relaxed slice `(C t).slice x` with `t ∈ W` is nonempty. The free-final-time feasible set
is `⋃_{t ∈ W} F t`.

(i) `not_lineSearch_lossless`: if some `x̄ ∈ convexHull (F t*)` (`t* ∈ W`) is infeasible at every
horizon, then no per-horizon family whose relaxations contain the `F t` is lossless for line
search.

(ii) `symmetric_supply`: such an `x̄` exists under the symmetry hypotheses (H1)-(H3):
a linear involution `R` preserving every `F t`, an `R`-invariant linear functional `ℓ` with a
maximiser over the graph, and every maximiser has nonzero "lateral part" `x - R x`.
-/

namespace LcvxObstruction

open UniformConvexRelaxation

variable {X : Type*} [AddCommGroup X] [Module ℝ X] {ι : Type*}

/-- **RR-LS (i), abstract kill.** -/
theorem not_lineSearch_lossless {Y : ι → Type*} [∀ t, AddCommGroup (Y t)] [∀ t, Module ℝ (Y t)]
    (W : Set ι) (F : ι → Set X) (C : ∀ t, UniformConvexRelaxation X (Y t))
    (hcont : ∀ t ∈ W, ∀ x ∈ F t, ((C t).slice x).Nonempty)
    {t₀ : ι} (ht₀ : t₀ ∈ W) {x : X} (hx : x ∈ convexHull ℝ (F t₀))
    (hxF : ∀ t ∈ W, x ∉ F t) :
    ¬ ∀ x, (∃ t ∈ W, ((C t).slice x).Nonempty) ↔ ∃ t ∈ W, x ∈ F t := by
  intro h
  have hG : Convex ℝ (Prod.fst '' (C t₀).C) := (C t₀).convex.linear_image (LinearMap.fst ℝ X (Y t₀))
  have hsub : F t₀ ⊆ Prod.fst '' (C t₀).C := fun z hz => by
    obtain ⟨y, hy⟩ := hcont t₀ ht₀ z hz
    exact ⟨(z, y), hy, rfl⟩
  obtain ⟨⟨x', y⟩, hy, rfl⟩ := convexHull_min hsub hG hx
  obtain ⟨t, ht, hxt⟩ := (h x').1 ⟨t₀, ht₀, y, hy⟩
  exact hxF t ht hxt

/-- **RR-LS (ii), symmetric supply of the bad point.** -/
theorem symmetric_supply (W : Set ι) (F : ι → Set X) (R : X →ₗ[ℝ] X) (hRR : ∀ x, R (R x) = x)
    (hRF : ∀ t ∈ W, ∀ x ∈ F t, R x ∈ F t) (ℓ : X →ₗ[ℝ] ℝ) (hℓR : ∀ x, ℓ (R x) = ℓ x)
    {t₀ : ι} (ht₀ : t₀ ∈ W) {x₀ : X} (hx₀ : x₀ ∈ F t₀)
    (hmax : ∀ t ∈ W, ∀ x ∈ F t, ℓ x ≤ ℓ x₀)
    (hlat : ∀ t ∈ W, ∀ x ∈ F t, (∀ t' ∈ W, ∀ x' ∈ F t', ℓ x' ≤ ℓ x) → x - R x ≠ 0) :
    (1 / 2 : ℝ) • (x₀ + R x₀) ∈ convexHull ℝ (F t₀) ∧
      ∀ t ∈ W, (1 / 2 : ℝ) • (x₀ + R x₀) ∉ F t := by
  constructor
  · have h1 := subset_convexHull ℝ (F t₀) hx₀
    have h2 := subset_convexHull ℝ (F t₀) (hRF t₀ ht₀ x₀ hx₀)
    have := (convex_convexHull ℝ (F t₀)) h1 h2 (by norm_num : (0:ℝ) ≤ 1 / 2)
      (by norm_num : (0:ℝ) ≤ 1 / 2) (by norm_num)
    rwa [← smul_add] at this
  · intro t ht hmem
    have hℓ : ℓ ((1 / 2 : ℝ) • (x₀ + R x₀)) = ℓ x₀ := by
      rw [map_smul, map_add, hℓR]; simp only [smul_eq_mul]; ring
    apply hlat t ht _ hmem (fun t' ht' x' hx' => hℓ ▸ hmax t' ht' x' hx')
    rw [map_smul, map_add, hRR, add_comm (R x₀) x₀, sub_self]

/-- **RR-LS, combined.** Under (H1)-(H3), no per-horizon family of uniform convex relaxations
containing the true sets is lossless for line search over the final time. -/
theorem not_lineSearch_lossless_of_symmetry {Y : ι → Type*} [∀ t, AddCommGroup (Y t)]
    [∀ t, Module ℝ (Y t)] (W : Set ι) (F : ι → Set X) (C : ∀ t, UniformConvexRelaxation X (Y t))
    (hcont : ∀ t ∈ W, ∀ x ∈ F t, ((C t).slice x).Nonempty)
    (R : X →ₗ[ℝ] X) (hRR : ∀ x, R (R x) = x) (hRF : ∀ t ∈ W, ∀ x ∈ F t, R x ∈ F t)
    (ℓ : X →ₗ[ℝ] ℝ) (hℓR : ∀ x, ℓ (R x) = ℓ x)
    {t₀ : ι} (ht₀ : t₀ ∈ W) {x₀ : X} (hx₀ : x₀ ∈ F t₀)
    (hmax : ∀ t ∈ W, ∀ x ∈ F t, ℓ x ≤ ℓ x₀)
    (hlat : ∀ t ∈ W, ∀ x ∈ F t, (∀ t' ∈ W, ∀ x' ∈ F t', ℓ x' ≤ ℓ x) → x - R x ≠ 0) :
    ¬ ∀ x, (∃ t ∈ W, ((C t).slice x).Nonempty) ↔ ∃ t ∈ W, x ∈ F t := by
  obtain ⟨h1, h2⟩ := symmetric_supply W F R hRR hRF ℓ hℓR ht₀ hx₀ hmax hlat
  exact not_lineSearch_lossless W F C hcont ht₀ h1 h2

end LcvxObstruction
