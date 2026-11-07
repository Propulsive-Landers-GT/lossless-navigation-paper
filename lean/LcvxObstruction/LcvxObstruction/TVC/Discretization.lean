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

/-- `∫_0^h |n| ≤ √(h ∫_0^h n²)` (Cauchy–Schwarz, AM-GM form). -/
theorem integral_abs_le_sqrt {h : ℝ} (hh : 0 < h) {n : ℝ → ℝ}
    (hn : IntervalIntegrable n volume 0 h) (hn2 : IntervalIntegrable (fun x => n x ^ 2) volume 0 h) :
    ∫ x in (0 : ℝ)..h, |n x| ≤ Real.sqrt (h * ∫ x in (0 : ℝ)..h, n x ^ 2) := by
  set S := ∫ x in (0 : ℝ)..h, n x ^ 2 with hS
  have hS0 : 0 ≤ S := intervalIntegral.integral_nonneg hh.le fun u _ => sq_nonneg _
  have e : h * S = 2 * h * (S / 2) := by ring
  rw [e]
  apply le_sqrt_of_forall_amgm hh.le (by positivity)
  intro l hl
  calc ∫ x in (0 : ℝ)..h, |n x| ≤ ∫ x in (0 : ℝ)..h, (l / 2 + n x ^ 2 / (2 * l)) := by
        apply intervalIntegral.integral_mono_on hh.le hn.abs
          (intervalIntegrable_const.add (hn2.div_const _))
        intro u _
        rw [div_add_div _ _ (two_ne_zero) (by positivity : (2 * l) ≠ 0),
          le_div_iff₀ (by positivity)]
        nlinarith [sq_nonneg (|n u| - l), sq_abs (n u), abs_nonneg (n u)]
    _ = l * h / 2 + S / 2 / l := by
        rw [intervalIntegral.integral_add intervalIntegrable_const (hn2.div_const _),
          intervalIntegral.integral_const, intervalIntegral.integral_div]
        simp only [sub_zero, smul_eq_mul, hS]
        field_simp

/-- Linear interpolation error: `|g(t) − ℓ(t)| ≤ M t (h − t)/2` on `[0, h]` when `|g''| ≤ M`,
`ℓ` the chord through `(0, g 0)` and `(h, g h)`. -/
theorem interp_error {h M : ℝ} (hh : 0 < h) {g g1 g2 : ℝ → ℝ}
    (hg : ∀ x, HasDerivAt g (g1 x) x) (hg1 : ∀ x, HasDerivAt g1 (g2 x) x)
    (hM : ∀ x ∈ Icc 0 h, |g2 x| ≤ M) {t : ℝ} (ht : t ∈ Icc 0 h) :
    |g t - (g 0 + (g h - g 0) / h * t)| ≤ M * (t * (h - t)) / 2 := by
  set k := (g h - g 0) / h
  -- ψ± = g − ℓ ± M s(h−s)/2
  have key : ∀ σ : ℝ, (σ = 1 ∨ σ = -1) →
      0 ≤ σ * (g t - (g 0 + k * t)) + M * (t * (h - t)) / 2 := by
    intro σ hσ
    have hσ2 : σ ^ 2 = 1 := by rcases hσ with rfl | rfl <;> norm_num
    set ψ : ℝ → ℝ := fun s => σ * (g s - (g 0 + k * s)) + M * (s * (h - s)) / 2 with hψ
    have hψ1 : ∀ s, HasDerivAt ψ (σ * (g1 s - k) + M * (h - 2 * s) / 2) s := fun s => by
      have := (((hg s).sub ((hasDerivAt_id s).const_mul k |>.const_add (g 0))).const_mul σ).add
        ((((hasDerivAt_id s).mul ((hasDerivAt_id s).const_sub h))).const_mul M |>.div_const 2)
      exact this.congr_deriv (by simp only [id]; ring)
    have hdψ : deriv ψ = fun s => σ * (g1 s - k) + M * (h - 2 * s) / 2 :=
      funext fun s => (hψ1 s).deriv
    have hψ2 : ∀ s, HasDerivAt (deriv ψ) (σ * g2 s - M) s := fun s => by
      rw [hdψ]
      have := (((hg1 s).sub_const k).const_mul σ).add
        ((((hasDerivAt_id s).const_mul 2).const_sub h).const_mul M |>.div_const 2)
      exact this.congr_deriv (by ring)
    have hconc : ConcaveOn ℝ (Icc 0 h) ψ := by
      refine concaveOn_of_deriv2_nonpos (convex_Icc 0 h)
        (fun s _ => (hψ1 s).continuousAt.continuousWithinAt)
        (fun s _ => (hψ1 s).differentiableAt.differentiableWithinAt)
        (fun s _ => (hψ2 s).differentiableAt.differentiableWithinAt) fun s hs => ?_
      rw [Function.iterate_succ_apply', Function.iterate_one, (hψ2 s).deriv]
      have hs' : s ∈ Icc 0 h := interior_subset hs
      have := hM s hs'
      have : σ * g2 s ≤ |g2 s| := by
        rcases hσ with rfl | rfl
        · simpa using le_abs_self (g2 s)
        · simpa using neg_le_abs (g2 s)
      linarith
    have hψ0 : ψ 0 = 0 := by simp [hψ]
    have hkh : k * h = g h - g 0 := div_mul_cancel₀ _ hh.ne'
    have hψh : ψ h = 0 := by simp only [hψ]; rw [hkh]; ring
    have ha : (0 : ℝ) ≤ 1 - t / h := by rw [sub_nonneg, div_le_one hh]; exact ht.2
    have hcomb := hconc.2 (left_mem_Icc.2 hh.le) (right_mem_Icc.2 hh.le) ha
      (div_nonneg ht.1 hh.le) (show (1 - t / h) + t / h = 1 by ring)
    have e : (1 - t / h) • (0 : ℝ) + (t / h) • h = t := by
      simp only [smul_eq_mul, mul_zero, zero_add]; exact div_mul_cancel₀ _ hh.ne'
    rw [e, hψ0, hψh] at hcomb
    simp only [smul_zero, add_zero] at hcomb
    simpa [hψ] using hcomb
  have h1 := key 1 (Or.inl rfl)
  have h2 := key (-1) (Or.inr rfl)
  rw [abs_le]; constructor <;> linarith

/-- **Finsler remainder on a cell** (TVC-Q3). If `n ⊥ {1, t}` on `[0, h]` and `|g''| ≤ M`, then
`|∫_0^h g n| ≤ (M h²/8) √(h ∫_0^h n²)`. -/
theorem cell_finsler_remainder {h M : ℝ} (hh : 0 < h) {n g g1 g2 : ℝ → ℝ}
    (hn : IntervalIntegrable n volume 0 h) (hn2 : IntervalIntegrable (fun x => n x ^ 2) volume 0 h)
    (h0 : ∫ x in (0 : ℝ)..h, n x = 0) (h1 : ∫ x in (0 : ℝ)..h, x * n x = 0)
    (hg : ∀ x, HasDerivAt g (g1 x) x) (hg1 : ∀ x, HasDerivAt g1 (g2 x) x)
    (hM : ∀ x ∈ Icc 0 h, |g2 x| ≤ M) :
    |∫ x in (0 : ℝ)..h, g x * n x| ≤ M * h ^ 2 / 8 * Real.sqrt (h * ∫ x in (0 : ℝ)..h, n x ^ 2) := by
  have hgc : Continuous g := continuous_iff_continuousAt.2 fun x => (hg x).continuousAt
  set k := (g h - g 0) / h
  set e : ℝ → ℝ := fun x => g x - (g 0 + k * x) with he
  have hec : Continuous e := by simp only [he]; fun_prop
  have hM0 : 0 ≤ M := (abs_nonneg _).trans (hM 0 (left_mem_Icc.2 hh.le))
  -- ∫ g n = ∫ e n
  have hlin : ∫ x in (0 : ℝ)..h, g x * n x = ∫ x in (0 : ℝ)..h, e x * n x := by
    have hsplit : ∫ x in (0 : ℝ)..h, g x * n x =
        ∫ x in (0 : ℝ)..h, (e x * n x + (g 0 * n x + k * (x * n x))) := by
      refine intervalIntegral.integral_congr fun x _ => ?_
      simp only [he]; ring
    have hI1 : IntervalIntegrable (fun x => e x * n x) volume 0 h :=
      hn.continuousOn_mul hec.continuousOn
    have hI2 : IntervalIntegrable (fun x => x * n x) volume 0 h :=
      hn.continuousOn_mul continuous_id.continuousOn
    rw [hsplit, intervalIntegral.integral_add hI1 ((hn.const_mul _).add (hI2.const_mul _)),
      intervalIntegral.integral_add (hn.const_mul _) (hI2.const_mul _),
      intervalIntegral.integral_const_mul, intervalIntegral.integral_const_mul, h0, h1]
    ring
  rw [hlin]
  have hbound : ∀ x ∈ Icc 0 h, |e x| ≤ M * h ^ 2 / 8 := fun x hx => by
    have := interp_error hh hg hg1 hM hx
    refine this.trans ?_
    have : x * (h - x) ≤ h ^ 2 / 4 := by nlinarith [sq_nonneg (2 * x - h)]
    nlinarith
  calc |∫ x in (0 : ℝ)..h, e x * n x| ≤ ∫ x in (0 : ℝ)..h, |e x * n x| :=
        intervalIntegral.abs_integral_le_integral_abs hh.le
    _ ≤ ∫ x in (0 : ℝ)..h, M * h ^ 2 / 8 * |n x| := by
        apply intervalIntegral.integral_mono_on hh.le (hn.continuousOn_mul hec.continuousOn).abs
          (hn.abs.const_mul _)
        intro x hx
        rw [abs_mul]
        exact mul_le_mul_of_nonneg_right (hbound x hx) (abs_nonneg _)
    _ = M * h ^ 2 / 8 * ∫ x in (0 : ℝ)..h, |n x| := intervalIntegral.integral_const_mul _ _
    _ ≤ M * h ^ 2 / 8 * Real.sqrt (h * ∫ x in (0 : ℝ)..h, n x ^ 2) :=
        mul_le_mul_of_nonneg_left (integral_abs_le_sqrt hh hn hn2) (by positivity)

end LcvxObstruction.TVC
