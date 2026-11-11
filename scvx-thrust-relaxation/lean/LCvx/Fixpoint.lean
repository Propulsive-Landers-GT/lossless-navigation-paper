import LCvx.Basic
import Mathlib.Analysis.Convex.Function
import Mathlib.Analysis.Calculus.Deriv.Comp
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.Calculus.Deriv.Add

/-!
# From a converged SCvx iterate to the LCvx theorems

The theorems in `LCvx.Basic` assume a local minimizer. Successive convexification (SCvx/PTR)
does not hand you one directly. At convergence it hands you a point `w` that solves its own
convex subproblem: minimize `f + h` over a convex set `K`, where `f` is the cost (fuel plus a
virtual-control penalty) and `h` is the trust-region penalty, centred at `w` itself.

`isMinOn_of_isMinOn_add` removes the trust-region penalty: since `h` has zero derivative at `w`,
`w` also minimizes `f` alone over `K`. `Problem.isMinOn_of_fixed_point` then passes to the
linearized relaxed problem (no virtual control, no trust region), where the theorems of
`LCvx.Basic` apply with the same derivative `F'` as the nonlinear problem.
-/

open Filter Topology Set

set_option linter.unusedSectionVars false

namespace LCvx

/-- If `z` minimizes `f + h` over a convex set `C`, `f` is convex on `C`, and `h` has zero
derivative at `z`, then `z` minimizes `f` alone over `C`. -/
theorem isMinOn_of_isMinOn_add {X : Type*} [NormedAddCommGroup X] [NormedSpace ℝ X]
    {C : Set X} {f h : X → ℝ} {z : X} (hC : Convex ℝ C) (hf : ConvexOn ℝ C f)
    (hh : HasFDerivAt h (0 : X →L[ℝ] ℝ) z) (hz : z ∈ C) (hmin : IsMinOn (f + h) C z) :
    IsMinOn f C z := by
  rw [isMinOn_iff] at hmin ⊢
  intro y hy
  by_contra hlt
  have hδ : 0 < f z - f y := sub_pos.mpr (not_le.mp hlt)
  -- `h` along the segment from `z` to `y` has derivative `0` at the start.
  have hp : HasDerivAt (fun t : ℝ => z + t • (y - z)) (y - z) 0 := by
    simpa using HasDerivAt.const_add z ((hasDerivAt_id (0 : ℝ)).smul_const (y - z))
  have hh' : HasFDerivAt h (0 : X →L[ℝ] ℝ) (z + (0 : ℝ) • (y - z)) := by simpa using hh
  have hg : HasDerivAt (fun t : ℝ => h (z + t • (y - z))) 0 0 := by
    have := hh'.comp_hasDerivAt (0 : ℝ) hp
    rw [zero_apply] at this
    exact this
  -- So `h` changes by less than `t (f z - f y) / 2` over a short step `t`.
  have hsmall := hg.isLittleO.def (half_pos hδ)
  have h1 : ∀ᶠ t in 𝓝 (0 : ℝ), t < 1 := Iio_mem_nhds one_pos
  have hnear : ∀ᶠ t in 𝓝[>] (0 : ℝ), t < 1 ∧
      ‖h (z + t • (y - z)) - h (z + (0 : ℝ) • (y - z)) - (t - 0) • (0 : ℝ)‖
        ≤ (f z - f y) / 2 * ‖t - 0‖ :=
    (h1.and hsmall).filter_mono nhdsWithin_le_nhds
  obtain ⟨t, ⟨ht1, hht⟩, ht0⟩ := (hnear.and self_mem_nhdsWithin).exists
  have ht0 : (0 : ℝ) < t := ht0
  simp only [zero_smul, add_zero, sub_zero, smul_zero, Real.norm_eq_abs, abs_of_pos ht0] at hht
  -- Convexity of `f` along the segment, and minimality of `f + h` at `z`.
  have hseg : z + t • (y - z) = (1 - t) • z + t • y := by module
  have hmem : z + t • (y - z) ∈ C := hC.add_smul_sub_mem hz hy ⟨ht0.le, ht1.le⟩
  have hconv : f (z + t • (y - z)) ≤ (1 - t) * f z + t * f y := by
    rw [hseg]
    simpa [smul_eq_mul] using hf.2 hz hy (by linarith) ht0.le (by ring)
  have hm := hmin _ hmem
  simp only [Pi.add_apply] at hm
  have habs := (abs_le.mp hht).2
  nlinarith

variable {N : ℕ} {E P Y : Type*}
  [NormedAddCommGroup E] [NormedSpace ℝ E]
  [NormedAddCommGroup P] [NormedSpace ℝ P]
  [NormedAddCommGroup Y] [NormedSpace ℝ Y]

/-- **Converged SCvx iterates are minimizers.** Let `π` be the linearized relaxed problem at
`z` (thrust relaxation, linearized dynamics, no virtual control, no trust region). The solver
works in its own variables `W` (states, controls, virtual controls, ...). Suppose its last
subproblem, a convex cost `f` plus a trust-region penalty `h` that is flat at the reference
`w = e z`, returned that reference. If `e` sends every feasible point of `π` to a feasible point
of the subproblem with the same cost, then `z` minimizes `π.cost` over `π.relaxed`. -/
theorem Problem.isMinOn_of_fixed_point (π : Problem N E P Y) {z : Dec N E P}
    {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W]
    {K : Set W} {f h : W → ℝ} {w : W} (e : Dec N E P → W)
    (hK : Convex ℝ K) (hf : ConvexOn ℝ K f) (hh : HasFDerivAt h (0 : W →L[ℝ] ℝ) w)
    (hw : w ∈ K) (hfix : IsMinOn (f + h) K w)
    (he : MapsTo e π.relaxed K) (hez : e z = w)
    (hfe : ∀ z' ∈ π.relaxed, f (e z') = π.cost z') (hz : z ∈ π.relaxed) :
    IsMinOn π.cost π.relaxed z := by
  have h1 := isMinOn_of_isMinOn_add hK hf hh hw hfix
  rw [isMinOn_iff] at h1 ⊢
  intro z' hz'
  rw [← hfe z hz, ← hfe z' hz', hez]
  exact h1 _ (he hz')

/-- An affine map `x ↦ c + F' (x - x₀)` has strict derivative `F'` everywhere. -/
theorem hasStrictFDerivAt_affine {X : Type*} [NormedAddCommGroup X] [NormedSpace ℝ X]
    (c : Y) (F' : X →L[ℝ] Y) (x₀ x : X) :
    HasStrictFDerivAt (fun x => c + F' (x - x₀)) F' x := by
  have := (F'.hasStrictFDerivAt.comp x ((hasStrictFDerivAt_id x).sub_const x₀)).const_add c
  simpa using this

end LCvx
