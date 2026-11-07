import LcvxObstruction.Slice.Master
import LcvxObstruction.TheoremD

/-!
# Lemma S for model M1 and Theorem D with hard soft landing (math/07 §3)

We give an explicit instance of model M1 (fixed thrust, constant mass, no gimbal) and explicit
vertical boundary data `ζ_w` such that the landing-offset set `L(ζ_w)` is nonempty (with the
altitude constraint `r_z ≥ 0` along the whole trajectory) but every landing offset, for every
admissible 3D attitude path (coning included), is at distance `≥ 1 m` from the point straight
below. Hence `0 ∈ conv L \ cl L`, `L` is not convex, and every state-linear relaxation of the
minimum-landing-error problem with hard `v(t_f) = 0` is lossy at target `0`.

**Witness.** This file uses a "hold" S-turn instead of the IVT S-turn of math/07 §3, because
its zero-lateral-impulse condition is explicit. The tilt angle is
`φ(s) = max (min (ω s) (2A - ω s)) (-A)`: tilt up at the maximal rate to `A`, tilt back
through zero to `-A`, then hold `-A`. The hold length `h = (1 - cos A)/(ω sin A)` makes
`∫ sin φ = 0`, so the lateral impulse vanishes and the data are vertical. The mean-square tilt
is `≈ 0.035 Ω²`, above the Wirtinger cap `Ω²/4π² ≈ 0.0253 Ω²`. This is the same mechanism as the
single-crossing S-turn of math/07 (`0.0404 Ω²`), with a smaller margin.

**Instance (`lemmaS`).** `a₁ = 12 m/s²` (fixed thrust, e.g. ρ₁ = ρ₂ = 1200 N, m₀ = 100 kg),
`g₀ = 9.81`, `δ = 0`, `ω = 0.1 rad/s`, `A = 0.1 rad`, `T = 3 + h ≈ 3.50 s` (`Ω = ωT ≈ 0.35`).
Minimum-throttle T/W = 1.22 > 1/cos A: this is math/07's high-T/W regime, which GTPL is NOT in.

Main results:
* `witness_admissible`, `witness_lands`, `witness_altitude`: the witness is admissible, lands
  from `ζ_w` at `p_w(u)` for every horizontal unit `u`, and keeps `r_z ≥ 0`.
* `lemmaS`: the full Lemma S statement for the instance.
* `theoremD_hard_landing`: the Theorem D corollary (relaxed value 0, true value ≥ 1 m).
-/

open MeasureTheory Set Real InnerProductGeometry
open scoped RealInnerProductSpace

noncomputable section

namespace LcvxObstruction.Slice

/-! ### The hold S-turn -/

/-- tilt profile: up at rate `ω` to `A`, back down to `-A`, hold. -/
def phi (A ω s : ℝ) : ℝ := max (min (ω * s) (2 * A - ω * s)) (-A)

/-- body axis = thrust direction of the witness, tilting in the vertical plane of `u`. -/
def wB (A ω : ℝ) (u : E3) (s : ℝ) : E3 := Real.sin (phi A ω s) • u + Real.cos (phi A ω s) • ez

/-- hold length that cancels the lateral impulse. -/
def holdT (A ω : ℝ) : ℝ := (1 - Real.cos A) / (ω * Real.sin A)

/-- horizon `T = 3A/ω + h`. -/
def horizon (A ω : ℝ) : ℝ := 3 * A / ω + holdT A ω

theorem continuous_phi (A ω : ℝ) : Continuous (phi A ω) := by
  unfold phi; fun_prop

theorem phi_lip {A ω : ℝ} (hω : 0 ≤ ω) (s s' : ℝ) :
    |phi A ω s - phi A ω s'| ≤ ω * |s - s'| := by
  unfold phi
  refine (abs_max_sub_max_le_abs _ _ _).trans ((abs_min_sub_min_le_max _ _ _ _).trans ?_)
  have h1 : |ω * s - ω * s'| = ω * |s - s'| := by rw [← mul_sub, abs_mul, abs_of_nonneg hω]
  have h2 : |2 * A - ω * s - (2 * A - ω * s')| = ω * |s - s'| := by
    rw [show 2 * A - ω * s - (2 * A - ω * s') = -(ω * s - ω * s') by ring, abs_neg, h1]
  rw [h1, h2, max_self]

theorem abs_phi_le {A ω : ℝ} (hA : 0 ≤ A) (s : ℝ) : |phi A ω s| ≤ A := by
  unfold phi
  rw [abs_le]
  constructor
  · exact (neg_le_neg_iff.mpr le_rfl).trans (le_max_right _ _)
  · refine max_le ?_ (by linarith)
    rcases le_total (ω * s) A with h | h
    · exact (min_le_left _ _).trans h
    · exact (min_le_right _ _).trans (by linarith)

theorem phi_zero {A ω : ℝ} (hA : 0 ≤ A) : phi A ω 0 = 0 := by
  simp [phi, hA]

theorem norm_wB {A ω : ℝ} {u : E3} (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0) (s : ℝ) :
    ‖wB A ω u s‖ = 1 :=
  norm_polar hu norm_ez huz _

/-- **The witness is admissible** (δ = 0, d = b). -/
theorem witness_admissible {A ω T : ℝ} (hA : 0 ≤ A) (hω : 0 ≤ ω) {u : E3} (hu : ‖u‖ = 1)
    (huz : ⟪u, ez⟫ = 0) : AttitudeAdmissible T ω 0 (wB A ω u) (wB A ω u) where
  b_init := by simp [wB, phi_zero hA]
  b_unit s _ := norm_wB hu huz s
  b_cont := by unfold wB; have := continuous_phi A ω; fun_prop
  b_rate s _ s' _ := by
    rcases le_or_gt π (ω * |s - s'|) with h | h
    · exact (angle_le_pi _ _).trans h
    · apply angle_le_of_cos_le_inner (norm_wB hu huz s) (norm_wB hu huz s')
        (mul_nonneg hω (abs_nonneg _)) h.le
      rw [wB, wB, inner_polar hu norm_ez huz, ← Real.cos_abs (phi A ω s - phi A ω s')]
      exact Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg _) h.le (phi_lip hω s s')
  d_meas := by
    apply Continuous.aestronglyMeasurable
    unfold wB; have := continuous_phi A ω; fun_prop
  d_unit s _ := norm_wB hu huz s
  gimbal s _ := by
    rw [angle_self (by rw [← norm_ne_zero_iff, norm_wB hu huz s]; norm_num)]

/-! ### The two integrals of the tilt profile -/

section Integrals

variable {A ω : ℝ}

theorem phi_piece1 (hA : 0 ≤ A) (hω : 0 < ω) {s : ℝ} (hs : s ∈ uIcc 0 (A / ω)) :
    phi A ω s = ω * s := by
  rw [uIcc_of_le (div_nonneg hA hω.le)] at hs
  have h1 : ω * s ≤ A := by
    have := mul_le_mul_of_nonneg_left hs.2 hω.le
    rwa [mul_div_cancel₀ _ hω.ne'] at this
  have h0 : 0 ≤ ω * s := mul_nonneg hω.le hs.1
  unfold phi
  rw [min_eq_left (by linarith), max_eq_left (by linarith)]

theorem phi_piece2 (hA : 0 ≤ A) (hω : 0 < ω) {s : ℝ} (hs : s ∈ uIcc (A / ω) (3 * A / ω)) :
    phi A ω s = 2 * A - ω * s := by
  rw [uIcc_of_le (by gcongr; linarith)] at hs
  have h1 : A ≤ ω * s := by
    have := mul_le_mul_of_nonneg_left hs.1 hω.le
    rwa [mul_div_cancel₀ _ hω.ne'] at this
  have h2 : ω * s ≤ 3 * A := by
    have := mul_le_mul_of_nonneg_left hs.2 hω.le
    rwa [mul_div_cancel₀ _ hω.ne'] at this
  unfold phi
  rw [min_eq_right (by linarith), max_eq_left (by linarith)]

theorem phi_piece3 (hω : 0 < ω) {T s : ℝ} (hT : 3 * A / ω ≤ T)
    (hs : s ∈ uIcc (3 * A / ω) T) : phi A ω s = -A := by
  rw [uIcc_of_le hT] at hs
  have h1 : 3 * A ≤ ω * s := by
    have := mul_le_mul_of_nonneg_left hs.1 hω.le
    rwa [mul_div_cancel₀ _ hω.ne'] at this
  unfold phi
  rw [max_eq_right]
  exact (min_le_right _ _).trans (by linarith)

theorem integral_split {f : ℝ → ℝ} (hf : Continuous f) (a b c d : ℝ) :
    ∫ x in a..d, f x = (∫ x in a..b, f x) + (∫ x in b..c, f x) + ∫ x in c..d, f x := by
  rw [intervalIntegral.integral_add_adjacent_intervals (hf.intervalIntegrable _ _)
      (hf.intervalIntegrable _ _),
    intervalIntegral.integral_add_adjacent_intervals (hf.intervalIntegrable _ _)
      (hf.intervalIntegrable _ _)]

/-- `∫₀ᵀ sin φ = (1 - cos A)/ω - (T - 3A/ω) sin A`. -/
theorem integral_sin_phi (hA : 0 ≤ A) (hω : 0 < ω) {T : ℝ} (hT : 3 * A / ω ≤ T) :
    ∫ s in (0 : ℝ)..T, Real.sin (phi A ω s) =
      (1 - Real.cos A) / ω - (T - 3 * A / ω) * Real.sin A := by
  have hω' := hω.ne'
  rw [integral_split (f := fun s => Real.sin (phi A ω s))
    (Real.continuous_sin.comp (continuous_phi A ω)) 0 (A / ω) (3 * A / ω) T]
  have p1 : ∫ x in (0 : ℝ)..A / ω, Real.sin (phi A ω x) = ∫ x in (0 : ℝ)..A / ω, Real.sin (ω * x) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece1 hA hω hs])
  have p2 : ∫ x in A / ω..3 * A / ω, Real.sin (phi A ω x) =
      ∫ x in A / ω..3 * A / ω, Real.sin (2 * A - ω * x) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece2 hA hω hs])
  have p3 : ∫ x in 3 * A / ω..T, Real.sin (phi A ω x) = ∫ x in 3 * A / ω..T, Real.sin (-A) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece3 hω hT hs])
  rw [p1, p2, p3]
  rw [intervalIntegral.integral_comp_mul_left (fun x => Real.sin x) hω.ne',
    intervalIntegral.integral_comp_sub_mul (fun x => Real.sin x) hω.ne',
    integral_sin, integral_sin, intervalIntegral.integral_const, smul_eq_mul, smul_eq_mul,
    smul_eq_mul, Real.sin_neg]
  have e1 : ω * (A / ω) = A := mul_div_cancel₀ _ hω.ne'
  have e2 : 2 * A - ω * (3 * A / ω) = -A := by field_simp <;> ring
  have e3 : 2 * A - ω * (A / ω) = A := by field_simp <;> ring
  rw [mul_zero, e2, e3, e1, Real.cos_neg, Real.cos_zero]
  field_simp <;> ring

/-- `∫₀ᵀ cos φ = 3 sin A/ω + (T - 3A/ω) cos A`. -/
theorem integral_cos_phi (hA : 0 ≤ A) (hω : 0 < ω) {T : ℝ} (hT : 3 * A / ω ≤ T) :
    ∫ s in (0 : ℝ)..T, Real.cos (phi A ω s) =
      3 * Real.sin A / ω + (T - 3 * A / ω) * Real.cos A := by
  have hω' := hω.ne'
  rw [integral_split (f := fun s => Real.cos (phi A ω s))
    (Real.continuous_cos.comp (continuous_phi A ω)) 0 (A / ω) (3 * A / ω) T]
  have p1 : ∫ x in (0 : ℝ)..A / ω, Real.cos (phi A ω x) = ∫ x in (0 : ℝ)..A / ω, Real.cos (ω * x) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece1 hA hω hs])
  have p2 : ∫ x in A / ω..3 * A / ω, Real.cos (phi A ω x) =
      ∫ x in A / ω..3 * A / ω, Real.cos (2 * A - ω * x) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece2 hA hω hs])
  have p3 : ∫ x in 3 * A / ω..T, Real.cos (phi A ω x) = ∫ x in 3 * A / ω..T, Real.cos (-A) :=
    intervalIntegral.integral_congr (fun s hs => by simp only [phi_piece3 hω hT hs])
  rw [p1, p2, p3]
  rw [intervalIntegral.integral_comp_mul_left (fun x => Real.cos x) hω.ne',
    intervalIntegral.integral_comp_sub_mul (fun x => Real.cos x) hω.ne',
    integral_cos, integral_cos, intervalIntegral.integral_const, smul_eq_mul, smul_eq_mul,
    smul_eq_mul, Real.cos_neg]
  have e1 : ω * (A / ω) = A := mul_div_cancel₀ _ hω.ne'
  have e2 : 2 * A - ω * (3 * A / ω) = -A := by field_simp <;> ring
  have e3 : 2 * A - ω * (A / ω) = A := by field_simp <;> ring
  rw [mul_zero, e2, e3, e1, Real.sin_neg, Real.sin_zero]
  field_simp <;> ring

theorem integral_sin_phi_horizon (hA : 0 < A) (hA' : A < π) (hω : 0 < ω) :
    ∫ s in (0 : ℝ)..horizon A ω, Real.sin (phi A ω s) = 0 := by
  have hsA : 0 < Real.sin A := Real.sin_pos_of_pos_of_lt_pi hA hA'
  have hh : 0 ≤ holdT A ω := by
    unfold holdT
    exact div_nonneg (by linarith [Real.cos_le_one A]) (by positivity)
  have hω' := hω.ne'
  have hs' := hsA.ne'
  rw [integral_sin_phi hA.le hω (by unfold horizon; linarith)]
  unfold horizon holdT
  field_simp <;> ring

end Integrals

/-! ### Witness data and landing -/

section Witness

variable (A ω a₁ g₀ : ℝ)

/-- `∫₀ᵀ cos φ`. -/
def Ccos : ℝ := ∫ s in Icc 0 (horizon A ω), Real.cos (phi A ω s)
/-- `∫₀ᵀ (T - s) cos φ`. -/
def Jcos : ℝ := ∫ s in Icc 0 (horizon A ω), (horizon A ω - s) * Real.cos (phi A ω s)
/-- `∫₀ᵀ (T - s) sin φ`. -/
def Jsin : ℝ := ∫ s in Icc 0 (horizon A ω), (horizon A ω - s) * Real.sin (phi A ω s)

/-- vertical initial velocity of the witness data. -/
def v0z : ℝ := g₀ * horizon A ω - a₁ * Ccos A ω
/-- initial altitude of the witness data. -/
def r0z : ℝ := horizon A ω ^ 2 / 2 * g₀ - horizon A ω * v0z A ω a₁ g₀ - a₁ * Jcos A ω

/-- the vertical boundary data `ζ_w = ((0,0,r0z), (0,0,v0z))`. -/
def zetaW : E3 × E3 := (r0z A ω a₁ g₀ • ez, v0z A ω a₁ g₀ • ez)

/-- the landing offset of the witness turning towards `u`. -/
def pW (u : E3) : E3 := (a₁ * Jsin A ω) • u

end Witness

theorem integral_smul_wB {T c : ℝ} (A ω : ℝ) (u : E3) (w : ℝ → ℝ) (hw : Continuous w) :
    ∫ s in Icc 0 T, w s • (c • wB A ω u s) =
      (c * ∫ s in Icc 0 T, w s * Real.sin (phi A ω s)) • u +
        (c * ∫ s in Icc 0 T, w s * Real.cos (phi A ω s)) • ez := by
  have hpt : (fun s => w s • (c • wB A ω u s)) = fun s =>
      (c * (w s * Real.sin (phi A ω s))) • u + (c * (w s * Real.cos (phi A ω s))) • ez := by
    funext s; simp only [wB, smul_add, smul_smul]; congr 1 <;> ring_nf
  have hcs : Continuous (fun s => c * (w s * Real.sin (phi A ω s))) := by
    have := continuous_phi A ω; fun_prop
  have hcc : Continuous (fun s => c * (w s * Real.cos (phi A ω s))) := by
    have := continuous_phi A ω; fun_prop
  have i1 : IntegrableOn (fun s => (c * (w s * Real.sin (phi A ω s))) • u) (Icc 0 T) :=
    (hcs.smul continuous_const).integrableOn_Icc
  have i2 : IntegrableOn (fun s => (c * (w s * Real.cos (phi A ω s))) • ez) (Icc 0 T) :=
    (hcc.smul continuous_const).integrableOn_Icc
  rw [hpt, integral_add i1 i2,
    integral_smul_const, integral_smul_const, integral_const_mul, integral_const_mul]

theorem integral_c_wB {T c : ℝ} (A ω : ℝ) (u : E3) :
    ∫ s in Icc 0 T, c • wB A ω u s =
      (c * ∫ s in Icc 0 T, Real.sin (phi A ω s)) • u +
        (c * ∫ s in Icc 0 T, Real.cos (phi A ω s)) • ez := by
  have h := integral_smul_wB (T := T) (c := c) A ω u (fun _ => 1) continuous_const
  have e1 : (fun s => (fun _ => (1 : ℝ)) s • (c • wB A ω u s)) = fun s => c • wB A ω u s := by
    funext s; exact one_smul ℝ _
  have e2 : (fun s => (fun _ => (1 : ℝ)) s * Real.sin (phi A ω s)) =
      fun s => Real.sin (phi A ω s) := by funext s; exact one_mul _
  have e3 : (fun s => (fun _ => (1 : ℝ)) s * Real.cos (phi A ω s)) =
      fun s => Real.cos (phi A ω s) := by funext s; exact one_mul _
  rw [e1, e2, e3] at h
  exact h

theorem hor_zetaW (A ω a₁ g₀ : ℝ) :
    hor (zetaW A ω a₁ g₀).1 = 0 ∧ hor (zetaW A ω a₁ g₀).2 = 0 :=
  ⟨hor_smul_ez _, hor_smul_ez _⟩

/-- **The witness lands** from `ζ_w` at `p_w(u)` with `v(T) = 0`. -/
theorem witness_lands {A ω a₁ g₀ : ℝ} (hA : 0 < A) (hA' : A < π) (hω : 0 < ω) {u : E3} :
    position (-g₀ • ez) (zetaW A ω a₁ g₀).1 (zetaW A ω a₁ g₀).2 (fun _ => a₁) (wB A ω u)
        (horizon A ω) = pW A ω a₁ u ∧
      velocity (-g₀ • ez) (zetaW A ω a₁ g₀).2 (fun _ => a₁) (wB A ω u) (horizon A ω) = 0 := by
  set T := horizon A ω
  have hS : ∫ s in Icc 0 T, Real.sin (phi A ω s) = 0 := by
    rw [setIntegral_Icc_eq_intervalIntegral (by
      unfold T horizon holdT
      have : 0 ≤ (1 - Real.cos A) / (ω * Real.sin A) := div_nonneg
        (by linarith [Real.cos_le_one A])
        (mul_nonneg hω.le (Real.sin_pos_of_pos_of_lt_pi hA hA').le)
      positivity)]
    exact integral_sin_phi_horizon hA hA' hω
  have hI := integral_c_wB (T := T) (c := a₁) A ω u
  have hJ := integral_smul_wB (T := T) (c := a₁) A ω u (fun s => T - s) (by fun_prop)
  dsimp only [position, velocity, zetaW, v0z, r0z, pW, Jsin, Jcos, Ccos]
  rw [hI, hJ, hS]
  constructor
  · module
  · module

/-- the altitude constraint set `{r_z ≥ 0}`. -/
def altitudeSet : Set (E3 × E3) := {x | 0 ≤ ⟪x.1, ez⟫}

theorem horizon_nonneg {A ω : ℝ} (hA : 0 < A) (hA' : A < π) (hω : 0 < ω) :
    3 * A / ω ≤ horizon A ω := by
  unfold horizon holdT
  have : 0 ≤ (1 - Real.cos A) / (ω * Real.sin A) := div_nonneg
    (by linarith [Real.cos_le_one A]) (mul_nonneg hω.le (Real.sin_pos_of_pos_of_lt_pi hA hA').le)
  linarith

theorem integral_Ioc_sub (t T : ℝ) (htT : t ≤ T) (c : ℝ) :
    ∫ s in Ioc t T, (s - t) * c = (T - t) ^ 2 / 2 * c := by
  rw [← intervalIntegral.integral_of_le htT, intervalIntegral.integral_mul_const,
    intervalIntegral.integral_comp_sub_right (fun x => x) t, integral_id]
  ring

/-- **The witness stays above ground**, provided `a₁ cos A ≥ g₀`. -/
theorem witness_altitude {A ω a₁ g₀ : ℝ} (hA : 0 < A) (hA' : A < π) (hω : 0 < ω)
    (ha₁ : 0 ≤ a₁) (halt : g₀ ≤ a₁ * Real.cos A) {u : E3} (huz : ⟪u, ez⟫ = 0) :
    ∀ t ∈ Icc 0 (horizon A ω),
      (position (-g₀ • ez) (zetaW A ω a₁ g₀).1 (zetaW A ω a₁ g₀).2 (fun _ => a₁) (wB A ω u) t,
        velocity (-g₀ • ez) (zetaW A ω a₁ g₀).2 (fun _ => a₁) (wB A ω u) t) ∈ altitudeSet := by
  intro t ht
  set T := horizon A ω
  set ζ := zetaW A ω a₁ g₀
  obtain ⟨hr, hv⟩ := witness_lands (a₁ := a₁) (g₀ := g₀) hA hA' hω (u := u)
  have hcw : Continuous (fun s => a₁ • wB A ω u s) := by
    unfold wB; have := continuous_phi A ω; fun_prop
  have hint : IntegrableOn (fun s => (fun _ => a₁) s • wB A ω u s) (Icc 0 T) :=
    hcw.integrableOn_Icc
  -- shift the landing point to the origin
  have hr0 : position (-g₀ • ez) (ζ.1 - pW A ω a₁ u) ζ.2 (fun _ => a₁) (wB A ω u) T = 0 := by
    simp only [position] at hr ⊢; rw [← sub_eq_zero.mpr hr]; abel
  have htail := position_eq_tail ht hint hr0 hv
  have hshift : position (-g₀ • ez) ζ.1 ζ.2 (fun _ => a₁) (wB A ω u) t =
      position (-g₀ • ez) (ζ.1 - pW A ω a₁ u) ζ.2 (fun _ => a₁) (wB A ω u) t + pW A ω a₁ u := by
    simp only [position]; abel
  have hc2 : Continuous (fun s => (s - t) • ((fun _ => a₁) s • wB A ω u s)) := by
    unfold wB; have := continuous_phi A ω; fun_prop
  have hz : ⟪∫ s in Ioc t T, (s - t) • ((fun _ => a₁) s • wB A ω u s), ez⟫ =
      ∫ s in Ioc t T, (s - t) * (a₁ * Real.cos (phi A ω s)) := by
    rw [real_inner_comm, ← integral_inner ((hc2.integrableOn_Icc (a := t) (b := T)).mono_set
      Ioc_subset_Icc_self)]
    congr 1; funext s
    simp only [wB, smul_add, smul_smul, inner_add_right, real_inner_smul_right,
      real_inner_comm u ez, huz, inner_ez_ez]
    ring
  have hpos : ⟪position (-g₀ • ez) ζ.1 ζ.2 (fun _ => a₁) (wB A ω u) t, ez⟫ =
      (∫ s in Ioc t T, (s - t) * (a₁ * Real.cos (phi A ω s))) - (T - t) ^ 2 / 2 * g₀ := by
    rw [hshift, htail, inner_add_left, inner_add_left, hz, pW]
    simp only [real_inner_smul_left, huz, inner_ez_ez]
    ring
  have hTt : t ≤ T := ht.2
  have hcont : Continuous (fun s => (s - t) * (a₁ * Real.cos (phi A ω s))) := by
    have := continuous_phi A ω; fun_prop
  have hlow : (T - t) ^ 2 / 2 * g₀ ≤ ∫ s in Ioc t T, (s - t) * (a₁ * Real.cos (phi A ω s)) := by
    rw [← integral_Ioc_sub t T hTt g₀]
    refine setIntegral_mono_on ((Continuous.integrableOn_Icc (by fun_prop)).mono_set
      Ioc_subset_Icc_self) ((hcont.integrableOn_Icc (a := t) (b := T)).mono_set
      Ioc_subset_Icc_self) measurableSet_Ioc fun s hs => ?_
    have hcos : Real.cos A ≤ Real.cos (phi A ω s) := by
      rw [← Real.cos_abs (phi A ω s)]
      exact Real.cos_le_cos_of_nonneg_of_le_pi (abs_nonneg _) hA'.le (abs_phi_le hA.le s)
    have : g₀ ≤ a₁ * Real.cos (phi A ω s) := halt.trans (mul_le_mul_of_nonneg_left hcos ha₁)
    exact mul_le_mul_of_nonneg_left this (by linarith [hs.1])
  show 0 ≤ ⟪position (-g₀ • ez) ζ.1 ζ.2 (fun _ => a₁) (wB A ω u) t, ez⟫
  rw [hpos]; linarith

/-- `L(ζ)` is monotone in the state constraint. -/
theorem landingOffsets_mono' {Acc : Set (ℝ → ℝ)} {T ω δ g₀ : ℝ} {ζ : E3 × E3}
    {X X' : Set (E3 × E3)} (h : X ⊆ X') :
    landingOffsets Acc T ω δ g₀ ζ X ⊆ landingOffsets Acc T ω δ g₀ ζ X' :=
  fun _ ⟨hp, a, d, b, ha, hadm, hr, hv, hX⟩ =>
    ⟨hp, a, d, b, ha, hadm, hr, hv, fun t ht => h (hX t ht)⟩

/-- **The witness offsets belong to `L(ζ_w)`** (with the altitude constraint). -/
theorem pW_mem {A ω a₁ g₀ : ℝ} (hA : 0 < A) (hA' : A < π) (hω : 0 < ω) (ha₁ : 0 ≤ a₁)
    (halt : g₀ ≤ a₁ * Real.cos A) {u : E3} (hu : ‖u‖ = 1) (huz : ⟪u, ez⟫ = 0) :
    pW A ω a₁ u ∈ landingOffsets (AccBox (horizon A ω) (fun _ => a₁) (fun _ => a₁))
      (horizon A ω) ω 0 g₀ (zetaW A ω a₁ g₀) altitudeSet := by
  obtain ⟨hr, hv⟩ := witness_lands (a₁ := a₁) (g₀ := g₀) hA hA' hω (u := u)
  refine ⟨by rw [pW, real_inner_smul_left, huz, mul_zero], fun _ => a₁, wB A ω u, wB A ω u,
    ⟨integrableOn_const (by simp [Real.volume_Icc]), fun _ _ => ⟨le_rfl, le_rfl⟩⟩,
    witness_admissible hA.le hω.le hu huz, hr, hv,
    witness_altitude hA hA' hω ha₁ halt huz⟩

/-! ### The concrete instance -/

theorem sin_tenth : 1 / 10 - 1 / 6000 ≤ Real.sin (1 / 10) ∧
    Real.sin (1 / 10) ≤ 1 / 10 - 1 / 6000 + 1 / 10 ^ 7 := by
  constructor
  · have := Real.sin_ge_sub_cube (x := 1 / 10) (by norm_num)
    norm_num at this ⊢; linarith
  · have := Real.sin_bound (x := 1 / 10) (by rw [abs_of_pos (by norm_num)]; norm_num)
    rw [abs_le] at this
    norm_num at this ⊢; linarith [this.2]

theorem cos_tenth : 1 - 1 / 200 ≤ Real.cos (1 / 10) ∧
    Real.cos (1 / 10) ≤ 1 - 1 / 200 + 5 / 960000 := by
  constructor
  · have := Real.one_sub_sq_div_two_le_cos (x := 1 / 10)
    norm_num at this ⊢; linarith
  · have := Real.cos_bound (x := 1 / 10) (by rw [abs_of_pos (by norm_num)]; norm_num)
    rw [abs_le] at this
    norm_num at this ⊢; linarith [this.2]

/-- the horizon of the instance, `T = 3 + h ≈ 3.50 s`. -/
def instT : ℝ := horizon (1 / 10) (1 / 10)

/-- fixed thrust `a ≡ 12 m/s²`. -/
def instAcc : Set (ℝ → ℝ) := AccBox instT (fun _ => 12) (fun _ => 12)

/-- the vertical data `ζ_w`. -/
def instZeta : E3 × E3 := zetaW (1 / 10) (1 / 10) 12 (981 / 100)

/-- the landing-offset set `L(ζ_w)` of the instance under the state constraint `X`
(`ω = 0.1 rad/s`, `δ = 0`, `g₀ = 9.81`). -/
def instL (X : Set (E3 × E3)) : Set E3 :=
  landingOffsets instAcc instT (1 / 10) 0 (981 / 100) instZeta X

theorem pi_gt : (314 / 100 : ℝ) < π := by
  have := Real.pi_gt_d2; norm_num at this ⊢; linarith

/-- The numerical heart of the instance, with all transcendental quantities abstracted. -/
theorem numeric_core {sA cA w T Ω cb πv P : ℝ}
    (hs1 : 1 / 10 - 1 / 6000 ≤ sA) (hs2 : sA ≤ 1 / 10 - 1 / 6000 + 1 / 10 ^ 7)
    (hc1 : 1 - 1 / 200 ≤ cA) (hc2 : cA ≤ 1 - 1 / 200 + 5 / 960000)
    (hw : w = (1 - cA) / sA) (hT : T = 3 + 10 * w) (hΩ : Ω = 3 / 10 + w)
    (hπ : 314 / 100 < πv) (hcbpos : 0 < cb) (hcbhi : cb ≤ 1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2))
    (hdent : 12 * T - (981 / 100 * T - (981 / 100 * T - 12 * (30 * sA + 10 * w * cA))) ≤
      12 * cb * T * (Ω / (2 * πv)) ^ 2 + cb / 12 * (12 / T ^ 3 * P)) :
    1 ≤ P := by
  have hspos : 0 < sA := by linarith
  have hw0 : 0 ≤ w := by rw [hw]; exact div_nonneg (by linarith) hspos.le
  have hwhi : w ≤ 30 / 599 := by rw [hw, div_le_iff₀ hspos]; nlinarith
  have hTpos : 0 < T := by rw [hT]; linarith
  have hT3 : 27 ≤ T ^ 3 := by
    have : 3 ≤ T := by rw [hT]; linarith
    have h := pow_le_pow_left₀ (by norm_num : (0 : ℝ) ≤ 3) this 3
    norm_num at h; linarith
  have hΩ0 : 0 ≤ Ω := by rw [hΩ]; linarith
  have hΩhi : Ω ≤ 3 / 10 + 30 / 599 := by rw [hΩ]; linarith
  have hπ0 : 0 < πv := by linarith
  -- lower bound for the witness term
  have hL : 3 * (1 / 6000 - 1 / 10 ^ 7) + (1 / 200 - 5 / 960000) ^ 2 /
      (1 / 10 - 1 / 6000 + 1 / 10 ^ 7) ≤ 3 * (1 / 10 - sA) + (1 - cA) * w := by
    have e : (1 - cA) * w = (1 - cA) ^ 2 / sA := by rw [hw]; ring
    have hn : (1 / 200 - 5 / 960000 : ℝ) ^ 2 ≤ (1 - cA) ^ 2 :=
      pow_le_pow_left₀ (by norm_num) (by linarith) 2
    have h1 : (1 / 200 - 5 / 960000 : ℝ) ^ 2 / (1 / 10 - 1 / 6000 + 1 / 10 ^ 7) ≤
        (1 - cA) ^ 2 / sA := by
      rw [div_le_div_iff₀ (by norm_num) hspos]
      nlinarith [mul_le_mul_of_nonneg_right hn hspos.le,
        mul_le_mul_of_nonneg_left hs2 (sq_nonneg (1 - cA))]
    rw [e]; linarith
  -- upper bound for the Wirtinger term
  have hU : cb * Ω ^ 3 / (4 * πv ^ 2) ≤
      (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) * (3 / 10 + 30 / 599) ^ 3 /
        (4 * (314 / 100) ^ 2) := by
    have e1 : Ω ^ 3 ≤ (3 / 10 + 30 / 599) ^ 3 := pow_le_pow_left₀ hΩ0 hΩhi 3
    have hA : cb * Ω ^ 3 ≤ (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) * (3 / 10 + 30 / 599) ^ 3 :=
      mul_le_mul hcbhi e1 (pow_nonneg hΩ0 3) (by norm_num)
    have hB : 4 * (314 / 100 : ℝ) ^ 2 ≤ 4 * πv ^ 2 := by nlinarith
    calc cb * Ω ^ 3 / (4 * πv ^ 2)
        ≤ (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) * (3 / 10 + 30 / 599) ^ 3 / (4 * πv ^ 2) :=
          div_le_div_of_nonneg_right hA (by positivity)
      _ ≤ _ := div_le_div_of_nonneg_left (by norm_num) (by norm_num) hB
  -- the gain minus the slack
  have hgainB : 12 * T - (981 / 100 * T - (981 / 100 * T - 12 * (30 * sA + 10 * w * cA))) -
      12 * cb * T * (Ω / (2 * πv)) ^ 2 =
      120 * ((3 * (1 / 10 - sA) + (1 - cA) * w) - cb * Ω ^ 3 / (4 * πv ^ 2)) := by
    have hTΩ : T = 10 * Ω := by rw [hT, hΩ]; ring
    have hπ' := hπ0.ne'
    rw [hTΩ, hΩ]
    field_simp
    ring
  have hnum : (0.0225 : ℝ) ≤ 120 * ((3 * (1 / 6000 - 1 / 10 ^ 7) + (1 / 200 - 5 / 960000) ^ 2 /
      (1 / 10 - 1 / 6000 + 1 / 10 ^ 7)) - (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) *
        (3 / 10 + 30 / 599) ^ 3 / (4 * (314 / 100) ^ 2)) := by norm_num
  have hM : (0.0225 : ℝ) ≤ cb / 12 * (12 / T ^ 3 * P) := by
    have h' : 12 * T - (981 / 100 * T - (981 / 100 * T -
        12 * (30 * sA + 10 * w * cA))) - 12 * cb * T * (Ω / (2 * πv)) ^ 2 ≤
        cb / 12 * (12 / T ^ 3 * P) := by linarith
    rw [hgainB] at h'
    linarith
  have hT0 := hTpos.ne'
  have e : cb / 12 * (12 / T ^ 3 * P) = cb * P / T ^ 3 := by
    field_simp
  rw [e, le_div_iff₀ (by positivity)] at hM
  have h3 : (1 : ℝ) / (2 - (3 / 10 + 30 / 599) ^ 2 / 2) ≤ 0.0225 * 27 := by norm_num
  have hT27 : 0.0225 * 27 ≤ 0.0225 * T ^ 3 := by linarith
  rcases le_or_gt 0 P with hP0 | hP0
  · have h4 : cb * P ≤ (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) * P :=
      mul_le_mul_of_nonneg_right hcbhi hP0
    have h5 : (0.0225 : ℝ) * 27 ≤ (1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2)) * P := by linarith
    have h6 : (0 : ℝ) < 1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2) := by norm_num
    nlinarith
  · have : cb * P < 0 := mul_neg_of_pos_of_neg hcbpos hP0
    nlinarith

/-- **The dent of the instance: every landing offset is at least 1 m from the origin.** -/
theorem instL_norm_ge {X : Set (E3 × E3)} {p : E3} (hp : p ∈ instL X) : 1 ≤ ‖p‖ := by
  obtain ⟨hs1, hs2⟩ := sin_tenth
  obtain ⟨hc1, hc2⟩ := cos_tenth
  set sA := Real.sin (1 / 10) with hsA
  set cA := Real.cos (1 / 10) with hcA
  have hspos : 0 < sA := by linarith
  have hs0 : sA ≠ 0 := hspos.ne'
  set w := (1 - cA) / sA with hw
  have hw0 : 0 ≤ w := div_nonneg (by linarith) hspos.le
  have hwhi : w ≤ 30 / 599 := by
    rw [hw, div_le_iff₀ hspos]; nlinarith
  have hT : instT = 3 + 10 * w := by
    rw [instT, horizon, holdT, hw, ← hsA, ← hcA]; field_simp <;> ring
  have hTpos : 0 < instT := by rw [hT]; linarith
  set Ω := 1 / 10 * instT with hΩ
  have hΩw : Ω = 3 / 10 + w := by rw [hΩ, hT]; ring
  have hΩ0 : 0 ≤ Ω := by rw [hΩw]; linarith
  have hΩhi : Ω ≤ 3 / 10 + 30 / 599 := by rw [hΩw]; linarith
  have hτ : 0 + 1 / 10 * instT < π / 2 := by
    rw [zero_add, ← hΩ]; linarith [pi_gt]
  have hdent := dent_fixed (g₀ := 981 / 100) hTpos (by norm_num) le_rfl hτ (by norm_num)
    (hor_zetaW _ _ _ _).1 (hor_zetaW _ _ _ _).2 hp
  -- the gain of the instance
  have hCc : Ccos (1 / 10) (1 / 10) = 30 * sA + 10 * w * cA := by
    rw [Ccos, setIntegral_Icc_eq_intervalIntegral (by rw [← instT]; exact hTpos.le),
      integral_cos_phi (by norm_num) (by norm_num) (horizon_nonneg (by norm_num)
        (by linarith [pi_gt]) (by norm_num)), ← instT, hT, ← hsA, ← hcA]
    field_simp <;> ring
  have hv0 : ⟪(zetaW (1 / 10) (1 / 10) 12 (981 / 100)).2, ez⟫ =
      981 / 100 * instT - 12 * Ccos (1 / 10) (1 / 10) := by
    simp only [zetaW, v0z, real_inner_smul_left, inner_ez_ez, mul_one, instT]
  rw [hv0, hCc] at hdent
  have hslack : slackB instT (1 / 10) 0 12 =
      12 * cbar (0 + 1 / 10 * instT) * instT * (Ω / (2 * π)) ^ 2 := by
    rw [slackB, Real.cos_zero, show (2 : ℝ) - 2 * 1 = 0 by norm_num, Real.sqrt_zero, add_zero]
  rw [hslack] at hdent
  have hcosΩ : 1 - (3 / 10 + 30 / 599) ^ 2 / 2 ≤ Real.cos Ω := by
    have := Real.one_sub_sq_div_two_le_cos (x := Ω)
    have : Ω ^ 2 ≤ (3 / 10 + 30 / 599) ^ 2 := pow_le_pow_left₀ hΩ0 hΩhi 2
    linarith
  have hcbpos : 0 < cbar (0 + 1 / 10 * instT) := by
    rw [cbar, zero_add, ← hΩ]
    have : 0 < 1 + Real.cos Ω := by nlinarith
    positivity
  have hcbhi : cbar (0 + 1 / 10 * instT) ≤ 1 / (2 - (3 / 10 + 30 / 599) ^ 2 / 2) := by
    rw [cbar, zero_add, ← hΩ]
    apply one_div_le_one_div_of_le (by norm_num)
    linarith
  have hP := numeric_core hs1 hs2 hc1 hc2 hw hT hΩw pi_gt hcbpos hcbhi hdent
  nlinarith [norm_nonneg p]

/-- **Lemma S (formal, explicit instance of model M1).**
For the instance (`a ≡ 12 m/s²`, `g₀ = 9.81`, `δ = 0`, `ω = 0.1 rad/s`, `T = instT ≈ 3.50 s`)
and the vertical data `ζ_w = instZeta`:
1. `ζ_w` is vertical, and the regime holds: `ωT < π/2`, and min-throttle `a₁ cos(ωT) > g₀`;
2. for every horizontal unit `u`, the offset `p_w(u)` lies in `L(ζ_w)`, even with the altitude
   constraint `r_z ≥ 0` along the trajectory;
3. every landing offset under any state constraint, for every admissible 3D attitude path,
   satisfies `‖p‖ ≥ 1` (the dent);
4. hence, for every state constraint `X ⊇ {r_z ≥ 0}`: `0 ∈ conv L(ζ_w)`, `0 ∉ cl L(ζ_w)`,
   and `L(ζ_w)` is not convex. -/
theorem lemmaS :
    hor instZeta.1 = 0 ∧ hor instZeta.2 = 0 ∧ 1 / 10 * instT < π / 2 ∧
      981 / 100 < 12 * Real.cos (1 / 10 * instT) ∧
      (∀ u : E3, ‖u‖ = 1 → ⟪u, ez⟫ = 0 → pW (1 / 10) (1 / 10) 12 u ∈ instL altitudeSet) ∧
      (∀ X, ∀ p ∈ instL X, 1 ≤ ‖p‖) ∧
      (∀ X, altitudeSet ⊆ X →
        (0 : E3) ∈ convexHull ℝ (instL X) ∧ (0 : E3) ∉ closure (instL X) ∧
          ¬ Convex ℝ (instL X)) := by
  obtain ⟨hs1, hs2⟩ := sin_tenth
  obtain ⟨hc1, hc2⟩ := cos_tenth
  have hpi := pi_gt
  have hA' : (1 / 10 : ℝ) < π := by linarith
  have halt : (981 / 100 : ℝ) ≤ 12 * Real.cos (1 / 10) := by linarith
  have hmem : ∀ u : E3, ‖u‖ = 1 → ⟪u, ez⟫ = 0 → pW (1 / 10) (1 / 10) 12 u ∈ instL altitudeSet :=
    fun u hu huz => pW_mem (by norm_num) hA' (by norm_num) (by norm_num) halt hu huz
  -- the regime facts
  have hw : (1 - Real.cos (1 / 10)) / Real.sin (1 / 10) ≤ 30 / 599 := by
    rw [div_le_iff₀ (by linarith)]; nlinarith
  have hw0 : 0 ≤ (1 - Real.cos (1 / 10)) / Real.sin (1 / 10) :=
    div_nonneg (by linarith) (by linarith)
  have hs0 : Real.sin (1 / 10) ≠ 0 := (by linarith : (0 : ℝ) < Real.sin (1 / 10)).ne'
  have hΩ : 1 / 10 * instT = 3 / 10 + (1 - Real.cos (1 / 10)) / Real.sin (1 / 10) := by
    rw [instT, horizon, holdT]; field_simp <;> ring
  have hΩhi : 1 / 10 * instT ≤ 3 / 10 + 30 / 599 := by rw [hΩ]; linarith
  have hΩ0 : 0 ≤ 1 / 10 * instT := by rw [hΩ]; linarith
  refine ⟨(hor_zetaW _ _ _ _).1, (hor_zetaW _ _ _ _).2, by linarith, ?_, hmem,
    fun X p hp => instL_norm_ge hp, fun X hX => ?_⟩
  · have := Real.one_sub_sq_div_two_le_cos (x := 1 / 10 * instT)
    have : (1 / 10 * instT) ^ 2 ≤ (3 / 10 + 30 / 599) ^ 2 := pow_le_pow_left₀ hΩ0 hΩhi 2
    nlinarith
  · -- two antipodal witnesses
    have hex := hmem ex norm_ex inner_ex_ez
    have hmex := hmem (-ex) (by rw [norm_neg, norm_ex]) (by rw [inner_neg_left, inner_ex_ez,
      neg_zero])
    have h1 : pW (1 / 10) (1 / 10) 12 ex ∈ instL X := landingOffsets_mono' hX hex
    have h2 : pW (1 / 10) (1 / 10) 12 (-ex) ∈ instL X := landingOffsets_mono' hX hmex
    have hneg : pW (1 / 10) (1 / 10) 12 (-ex) = -pW (1 / 10) (1 / 10) 12 ex := by
      rw [pW, pW, smul_neg]
    have hmid : (1 / 2 : ℝ) • pW (1 / 10) (1 / 10) 12 ex +
        (1 / 2 : ℝ) • pW (1 / 10) (1 / 10) 12 (-ex) = 0 := by
      rw [hneg, smul_neg, add_neg_cancel]
    have hsub : instL X ⊆ {p : E3 | 1 ≤ ‖p‖} := fun p hp => instL_norm_ge hp
    have hclosed : IsClosed {p : E3 | 1 ≤ ‖p‖} := isClosed_le continuous_const continuous_norm
    refine ⟨?_, ?_, ?_⟩
    · rw [← hmid]
      exact (convex_convexHull ℝ _) (subset_convexHull ℝ _ h1) (subset_convexHull ℝ _ h2)
        (by norm_num) (by norm_num) (by norm_num)
    · intro h0
      have := closure_minimal hsub hclosed h0
      norm_num at this
    · intro hconv
      have h0 := hconv h1 h2 (by norm_num : (0 : ℝ) ≤ 1 / 2) (by norm_num : (0 : ℝ) ≤ 1 / 2)
        (by norm_num)
      rw [hmid] at h0
      have := instL_norm_ge h0
      norm_num at this

/-- **Theorem D with hard soft landing `v(t_f) = 0` is lossy** (math/07 Thm S item 4).
Let `X ⊇ {r_z ≥ 0}` be any state constraint and let `S` be any state-linear relaxation (math/02
Def. 11.1: convex relaxed set, affine readout of the terminal position, convex penalty
vanishing on genuine points) of the minimum-landing-error problem from `ζ_w` whose zero-penalty
readouts contain the genuine landing offsets `L(ζ_w)`. Then for the target `q = 0`:
the relaxed problem attains error `0`, while every genuine landing has error `≥ 1 m`, and every
relaxed optimum reads out a non-genuine landing point. -/
theorem theoremD_hard_landing {Y : Type*} [AddCommGroup Y] [Module ℝ Y] {X : Set (E3 × E3)}
    (hX : altitudeSet ⊆ X) (S : StateLinearRelaxation Y E3) (h : S.Contains (instL X)) :
    (∃ y ∈ S.C, ‖S.ρ y - 0‖ + S.P y = 0) ∧
      (∀ x ∈ instL X, 1 ≤ ‖x - 0‖) ∧ 1 ≤ Metric.infDist (0 : E3) (instL X) ∧
      (∀ y ∈ S.C, (∀ y' ∈ S.C, ‖S.ρ y - 0‖ + S.P y ≤ ‖S.ρ y' - 0‖ + S.P y') →
        S.ρ y ∉ closure (instL X)) := by
  obtain ⟨-, -, -, -, hmem, hdent, hgeo⟩ := lemmaS
  obtain ⟨hq, hq', -⟩ := hgeo X hX
  obtain ⟨h1, -, -, h4⟩ := minError_lossy S h hq hq'
  have hne : (instL X).Nonempty :=
    ⟨_, landingOffsets_mono' hX (hmem ex norm_ex inner_ex_ez)⟩
  refine ⟨h1, fun x hx => by rw [sub_zero]; exact hdent X x hx, ?_, h4⟩
  rw [Metric.le_infDist hne]
  intro y hy
  rw [dist_comm, dist_eq_norm, sub_zero]
  exact hdent X y hy

end LcvxObstruction.Slice
