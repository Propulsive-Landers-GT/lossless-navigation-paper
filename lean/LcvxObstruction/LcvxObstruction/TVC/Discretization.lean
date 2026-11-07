import LcvxObstruction.Slice.Wirtinger
import LcvxObstruction.DiveBrakeQuant

/-!
# Pure TVC, Lemma 4.6′ (blueprint TVC-Q3): the cell-local remainder bounds

In the discretization of the TVC-1 certificate (math/06 §4.6, Lemma 4.6′) the control `n = ẍ` is
split on each cell of length `h` as `n = n̄ + n''` with `n''` orthogonal to `{1, t}` on the cell.
Then `ẋ''(t) = ∫_0^t n''` vanishes at both cell ends and has zero cell mean, and

* `cell_wirtinger`: `∫_cell (ẋ'')² ≤ (h/2π)² ∫_cell (n'')²` (Wirtinger with zero ends and zero mean;
  uses the periodic Wirtinger inequality `Slice.periodic_wirtinger` of [lean-s]);
* `cell_sup_bound`: `|x''(t)|² ≤ h³/(4π²) ∫_cell (n'')²` for `t` in the cell, where
  `x''(t) = ∫_0^t ẋ''` (Cauchy–Schwarz in AM-GM form).

The cell is taken as `[0, h]` (translate for a general cell). These are the only analytic inputs of
Lemma 4.6′ besides elementary bookkeeping; the bookkeeping that assembles them into the continuous
certificate is not formalized (it is part of `TVC1Reduction`).
-/

open MeasureTheory Set Real Filter
open scoped RealInnerProductSpace

namespace LcvxObstruction.TVC

/-- **Cell Wirtinger bound** (TVC-Q3). If `∫_0^h n = 0` and `∫_0^h t n = 0` (`n ⊥ {1, t}`), then
`v(t) = ∫_0^t n` satisfies `∫_0^h v² ≤ (h/2π)² ∫_0^h n²`. -/
theorem cell_wirtinger {h : ℝ} (hh : 0 < h) {n : ℝ → ℝ} (hn : IntervalIntegrable n volume 0 h)
    (hn2 : IntervalIntegrable (fun x => n x ^ 2) volume 0 h)
    (h0 : ∫ x in (0 : ℝ)..h, n x = 0) (h1 : ∫ x in (0 : ℝ)..h, x * n x = 0) :
    ∫ t in (0 : ℝ)..h, (∫ s in (0 : ℝ)..t, n s) ^ 2 ≤
      (h / (2 * π)) ^ 2 * ∫ t in (0 : ℝ)..h, n t ^ 2 := by
  set v : ℝ → ℝ := fun t => ∫ s in (0 : ℝ)..t, n s with hv
  have hvac : AbsolutelyContinuousOnInterval v 0 h :=
    hn.absolutelyContinuousOnInterval_intervalIntegral (by simp [hh.le])
  -- a.e. derivative
  have hder : ∀ᵐ x, x ∈ uIoc (0 : ℝ) h → deriv v x = n x := by
    filter_upwards [hn.ae_hasDerivAt_integral] with x hx hxI
    exact (hx (uIoc_subset_uIcc hxI) 0 (by simp [hh.le])).deriv
  have hderI : ∀ᵐ x ∂(volume.restrict (uIoc (0 : ℝ) h)), deriv v x = n x := by
    rw [ae_restrict_iff' measurableSet_uIoc]; exact hder
  have hper : v 0 = v h := by simp [hv, h0]
  -- zero mean: ∫ v = ∫ (h - s) n = 0, by parts with g(t) = t - h
  have hgac : AbsolutelyContinuousOnInterval (fun t : ℝ => t - h) 0 h :=
    ContDiffOn.absolutelyContinuousOnInterval (by fun_prop)
  have hibp := hvac.integral_mul_deriv_eq_deriv_mul hgac
  have hdg : ∀ x, deriv (fun t : ℝ => t - h) x = 1 := fun x => by
    simp
  simp only [hdg, mul_one] at hibp
  have hmean : ∫ x in (0 : ℝ)..h, v x = 0 := by
    rw [hibp]
    have e : ∫ x in (0 : ℝ)..h, deriv v x * (x - h) = ∫ x in (0 : ℝ)..h, (x * n x - h * n x) := by
      apply intervalIntegral.integral_congr_ae
      filter_upwards [hder] with x hx hxI
      rw [hx hxI]; ring
    rw [e, intervalIntegral.integral_sub (hn.continuousOn_mul (by fun_prop))
      (hn.const_mul h), intervalIntegral.integral_const_mul, h0, h1]
    simp [hv]
  have hd2 : IntervalIntegrable (fun x => deriv v x ^ 2) volume 0 h := by
    rw [intervalIntegrable_iff] at hn2 ⊢
    refine Integrable.congr hn2 ?_
    filter_upwards [hderI] with x hx
    rw [hx]
  have hW := Slice.periodic_wirtinger hh hvac hper hmean hd2
  have e2 : ∫ x in (0 : ℝ)..h, deriv v x ^ 2 = ∫ x in (0 : ℝ)..h, n x ^ 2 := by
    apply intervalIntegral.integral_congr_ae
    filter_upwards [hder] with x hx hxI
    rw [hx hxI]
  rw [e2] at hW
  exact hW

/-- **Cell sup bound** (TVC-Q3). Under the hypotheses of `cell_wirtinger`, for `t ∈ [0, h]`,
`(∫_0^t v)² ≤ h³/(4π²) ∫_0^h n²` with `v(t) = ∫_0^t n`. -/
theorem cell_sup_bound {h : ℝ} (hh : 0 < h) {n : ℝ → ℝ} (hn : IntervalIntegrable n volume 0 h)
    (hn2 : IntervalIntegrable (fun x => n x ^ 2) volume 0 h)
    (h0 : ∫ x in (0 : ℝ)..h, n x = 0) (h1 : ∫ x in (0 : ℝ)..h, x * n x = 0)
    {t : ℝ} (ht : t ∈ Icc 0 h) :
    (∫ u in (0 : ℝ)..t, ∫ s in (0 : ℝ)..u, n s) ^ 2 ≤
      h ^ 3 / (4 * π ^ 2) * ∫ x in (0 : ℝ)..h, n x ^ 2 := by
  set v : ℝ → ℝ := fun u => ∫ s in (0 : ℝ)..u, n s with hv
  have hvc : ContinuousOn v (Icc 0 h) := by
    have := intervalIntegral.continuousOn_primitive_interval' (a := 0) hn (by simp [hh.le])
    rwa [uIcc_of_le hh.le] at this
  have hvI : IntervalIntegrable v volume 0 h := hvc.intervalIntegrable_of_Icc hh.le
  have hv2I : IntervalIntegrable (fun u => v u ^ 2) volume 0 h :=
    (hvc.pow 2).intervalIntegrable_of_Icc hh.le
  have hW := cell_wirtinger hh hn hn2 h0 h1
  set S := ∫ u in (0 : ℝ)..h, v u ^ 2 with hS
  have hS0 : 0 ≤ S := intervalIntegral.integral_nonneg hh.le fun u _ => sq_nonneg _
  -- |∫_0^t v| ≤ ∫_0^h |v| ≤ √(h S)
  have habs : |∫ u in (0 : ℝ)..t, v u| ≤ ∫ u in (0 : ℝ)..h, |v u| := by
    have hsub : IntervalIntegrable (fun u => |v u|) volume 0 t :=
      (hvI.abs).mono_set (by rw [uIcc_of_le ht.1, uIcc_of_le hh.le]; exact Icc_subset_Icc_right ht.2)
    calc |∫ u in (0 : ℝ)..t, v u| ≤ ∫ u in (0 : ℝ)..t, |v u| :=
          intervalIntegral.abs_integral_le_integral_abs ht.1
      _ ≤ ∫ u in (0 : ℝ)..h, |v u| :=
          intervalIntegral.integral_mono_interval le_rfl ht.1 ht.2
            (ae_of_all _ fun u => abs_nonneg _) hvI.abs
  have hcs : ∫ u in (0 : ℝ)..h, |v u| ≤ Real.sqrt (2 * h * (S / 2)) := by
    apply le_sqrt_of_forall_amgm hh.le (by positivity)
    intro l hl
    calc ∫ u in (0 : ℝ)..h, |v u| ≤ ∫ u in (0 : ℝ)..h, (l / 2 + v u ^ 2 / (2 * l)) := by
          apply intervalIntegral.integral_mono_on hh.le hvI.abs
            (intervalIntegrable_const.add (hv2I.div_const _))
          intro u _
          rw [div_add_div _ _ (two_ne_zero) (by positivity : (2 * l) ≠ 0),
            le_div_iff₀ (by positivity)]
          nlinarith [sq_nonneg (|v u| - l), sq_abs (v u), abs_nonneg (v u)]
      _ = l * h / 2 + S / 2 / l := by
          rw [intervalIntegral.integral_add intervalIntegrable_const (hv2I.div_const _),
            intervalIntegral.integral_const, intervalIntegral.integral_div]
          simp only [sub_zero, smul_eq_mul, hS]
          field_simp
  have hsq : (∫ u in (0 : ℝ)..t, v u) ^ 2 ≤ h * S := by
    have h1' := habs.trans hcs
    have e : 2 * h * (S / 2) = h * S := by ring
    rw [e] at h1'
    calc (∫ u in (0 : ℝ)..t, v u) ^ 2 = |∫ u in (0 : ℝ)..t, v u| ^ 2 := (sq_abs _).symm
      _ ≤ Real.sqrt (h * S) ^ 2 := pow_le_pow_left₀ (abs_nonneg _) h1' 2
      _ = h * S := Real.sq_sqrt (by positivity)
  calc (∫ u in (0 : ℝ)..t, v u) ^ 2 ≤ h * S := hsq
    _ ≤ h * ((h / (2 * π)) ^ 2 * ∫ t in (0 : ℝ)..h, n t ^ 2) := mul_le_mul_of_nonneg_left hW hh.le
    _ = h ^ 3 / (4 * π ^ 2) * ∫ x in (0 : ℝ)..h, n x ^ 2 := by
        field_simp; ring

end LcvxObstruction.TVC
