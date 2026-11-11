import Mathlib.Analysis.Calculus.InverseFunctionTheorem.FDeriv
import Mathlib.Topology.Order.LocalExtr
import Mathlib.Analysis.Calculus.FDeriv.Linear
import Mathlib.Analysis.Calculus.FDeriv.Comp
import Mathlib.Analysis.Calculus.FDeriv.Add
import Mathlib.Analysis.Calculus.FDeriv.Prod

/-!
# Core perturbation lemma

Let `z₀` be a point satisfying the equality constraint `F z = F z₀`. Suppose the derivative of `F`
at `z₀` is already onto when restricted to a set of "free" directions `ι`. Then any small move
`t • d` can be undone, as far as `F` is concerned, by a small move along `ι`. If every such
combined move stays inside `S` and strictly lowers `J`, then `z₀` cannot be a local minimizer of
`J` over `S ∩ {F = F z₀}`.

The tool is Mathlib's surjective-derivative open mapping theorem
(`HasStrictFDerivAt.map_nhds_eq_of_surj`), applied to `(w, t) ↦ (F (z₀ + ι w + t • d), t)`.
-/

open Filter Topology Set

namespace LCvx

variable {X Y W : Type*}
  [NormedAddCommGroup X] [NormedSpace ℝ X]
  [NormedAddCommGroup Y] [NormedSpace ℝ Y] [CompleteSpace Y]
  [NormedAddCommGroup W] [NormedSpace ℝ W] [CompleteSpace W]

theorem not_isLocalMinOn_of_surjective
    {J : X → ℝ} {F : X → Y} {F' : X →L[ℝ] Y} {S : Set X} {z₀ : X}
    (ι : W →L[ℝ] X) (d : X)
    (hF : HasStrictFDerivAt F F' z₀)
    (hsurj : Function.Surjective (F' ∘L ι))
    (hgood : ∀ᶠ p : W × ℝ in 𝓝 0, 0 < p.2 →
      z₀ + ι p.1 + p.2 • d ∈ S ∧ J (z₀ + ι p.1 + p.2 • d) < J z₀) :
    ¬ IsLocalMinOn J {z | z ∈ S ∧ F z = F z₀} z₀ := by
  intro hmin
  -- The affine family of trial points.
  set A : W × ℝ →L[ℝ] X := ι.coprod ((ContinuousLinearMap.id ℝ ℝ).smulRight d) with hA
  have hAp : ∀ p : W × ℝ, A p = ι p.1 + p.2 • d := fun p => by simp [hA]
  -- `G p = (F (z₀ + A p), p.2)` has a surjective strict derivative at `0`.
  set G : W × ℝ → Y × ℝ := fun p => (F (z₀ + A p), p.2) with hG
  have hGd : HasStrictFDerivAt G ((F' ∘L A).prod (ContinuousLinearMap.snd ℝ W ℝ)) 0 := by
    have h1 : HasStrictFDerivAt (fun p : W × ℝ => z₀ + A p) A 0 :=
      A.hasStrictFDerivAt.const_add z₀
    have hF0 : HasStrictFDerivAt F F' (z₀ + A 0) := by simpa using hF
    exact (hF0.comp (0 : W × ℝ) h1).prodMk (ContinuousLinearMap.snd ℝ W ℝ).hasStrictFDerivAt
  have hrange : ((F' ∘L A).prod (ContinuousLinearMap.snd ℝ W ℝ)).range = ⊤ := by
    rw [LinearMap.range_eq_top]
    rintro ⟨y, t⟩
    obtain ⟨w, hw⟩ := hsurj (y - t • F' d)
    refine ⟨(w, t), ?_⟩
    simp only [ContinuousLinearMap.comp_apply] at hw
    simp [hAp, map_add, map_smul, hw]
  have hmap := hGd.map_nhds_eq_of_surj hrange
  have hG0 : G 0 = (F z₀, 0) := by simp [hG]
  -- A neighbourhood of `z₀` on which `z₀` minimizes `J` over the feasible set.
  obtain ⟨U, hU, hUmin⟩ : ∃ U ∈ 𝓝 z₀, ∀ z ∈ U, z ∈ S → F z = F z₀ → J z₀ ≤ J z := by
    have := hmin
    rw [IsLocalMinOn, IsMinFilter, eventually_nhdsWithin_iff] at this
    exact ⟨_, this, fun z hz hS hFz => hz ⟨hS, hFz⟩⟩
  -- Trial parameters that are good and land in `U`.
  set V : Set (W × ℝ) :=
    {p | (0 < p.2 → z₀ + ι p.1 + p.2 • d ∈ S ∧ J (z₀ + ι p.1 + p.2 • d) < J z₀) ∧ z₀ + A p ∈ U}
  have hV : V ∈ 𝓝 (0 : W × ℝ) := by
    refine hgood.and ?_
    have hc : ContinuousAt (fun p : W × ℝ => z₀ + A p) 0 :=
      (continuous_const.add A.continuous).continuousAt
    exact hc.preimage_mem_nhds (by simpa using hU)
  have himg : G '' V ∈ 𝓝 (F z₀, (0 : ℝ)) := by
    rw [← hG0, ← hmap]
    exact image_mem_map hV
  -- Points `(F z₀, t)` with small `t > 0` are hit by `G` on `V`.
  have hline : ∀ᶠ t in 𝓝 (0 : ℝ), (F z₀, t) ∈ G '' V := by
    have hc : ContinuousAt (fun t : ℝ => (F z₀, t)) 0 :=
      (continuous_const.prodMk continuous_id).continuousAt
    exact hc.preimage_mem_nhds himg
  obtain ⟨t, ht, htpos⟩ := ((hline.filter_mono nhdsWithin_le_nhds).and self_mem_nhdsWithin).exists
    (f := 𝓝[>] (0 : ℝ))
  obtain ⟨p, ⟨hpgood, hpU⟩, hp⟩ := ht
  simp only [hG, Prod.mk.injEq] at hp
  obtain ⟨hpF, hpt⟩ := hp
  have hp2 : 0 < p.2 := hpt ▸ htpos
  obtain ⟨hpS, hpJ⟩ := hpgood hp2
  have := hUmin _ hpU (by simpa [hAp, add_assoc] using hpS) hpF
  rw [hAp, ← add_assoc] at this
  exact absurd this (not_le.mpr hpJ)

end LCvx
