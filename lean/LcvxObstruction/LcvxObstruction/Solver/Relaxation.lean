import LcvxObstruction.SixDOF
import LcvxObstruction.DiveBrake

/-!
# Solver claim N7: the 3DOF relaxation is a lower bound

Source: `solver/CLAIMS.md` row 10 (N7).

* `relaxation_lower_bound` (abstract): if every 6DOF-feasible plan maps to a 3DOF-feasible plan
  with the same cost, then `inf_{F₃} J₃ ≤ inf_{F₆} J₆`. The infima are taken in `EReal`, so an
  empty feasible set has value `⊤` and no boundedness assumption is needed.
  `relaxation_lower_bound_real` is the same statement for `sInf` in `ℝ`.
* `freeTime_lower_bound` : `V₃(t_f) ≤ V₆(t_f)` for every `t_f` gives `inf_{t_f} V₃ ≤ inf_{t_f} V₆`.
* Connection to the model of `Model.lean`/`SixDOF.lean`/`DiveBrake.lean`: `plans3`, `plans5`,
  `plans6` are the sets of translational controls `(a, d)` that soft-land from `θ = (r₀, v₀)` at
  `t_f` and keep `(r, v) ∈ X` on `[0, t_f]`, with
  - 3DOF: `a ∈ Acc`, `d` measurable and unit (no attitude, no rate or gimbal limits);
  - 5DOF: additionally a body axis `b` with `AttitudeAdmissible tf ω δ d b`;
  - 6DOF: additionally an attitude path `A` with `Attitude6Admissible Att tf ω δ d A`.
  `plans6_subset_plans5`, `plans5_subset_plans3` and `value3_le_value6` (same throttle class,
  same state constraints, any cost that depends only on `(a, d)`). On landing sets:
  `constrainedLandingSet6_subset_landingSet3`.

The tangent/secant log-mass bounds used by the solver's discretised 3DOF problem enlarge `F₃`
further, which the abstract theorem covers (any `F₃` containing the image). The time
discretisation error of the computed bound (ZOH grid) is **not** covered.
-/

open MeasureTheory Set

namespace LcvxSolver

open LcvxObstruction

/-! ## Abstract form -/

/-- **N7 (abstract).** If `π` maps every 6DOF-feasible plan to a 3DOF-feasible plan with the same
cost, the 3DOF value is a lower bound on the 6DOF value (infima in `EReal`; empty ↦ `⊤`). -/
theorem relaxation_lower_bound {P₆ P₃ : Type*} (F₆ : Set P₆) (F₃ : Set P₃) (J₆ : P₆ → ℝ)
    (J₃ : P₃ → ℝ) (π : P₆ → P₃) (hmap : ∀ x ∈ F₆, π x ∈ F₃)
    (hcost : ∀ x ∈ F₆, J₃ (π x) = J₆ x) :
    ⨅ y ∈ F₃, (J₃ y : EReal) ≤ ⨅ x ∈ F₆, (J₆ x : EReal) :=
  le_iInf₂ fun x hx => (iInf₂_le (π x) (hmap x hx)).trans_eq (by rw [hcost x hx])

/-- **N7 (abstract, real infimum).** Same, with `sInf` in `ℝ`: needs the 3DOF costs bounded
below and a 6DOF-feasible plan. -/
theorem relaxation_lower_bound_real {P₆ P₃ : Type*} (F₆ : Set P₆) (F₃ : Set P₃) (J₆ : P₆ → ℝ)
    (J₃ : P₃ → ℝ) (π : P₆ → P₃) (hmap : ∀ x ∈ F₆, π x ∈ F₃)
    (hcost : ∀ x ∈ F₆, J₃ (π x) = J₆ x) (hbdd : BddBelow (J₃ '' F₃)) (hne : F₆.Nonempty) :
    sInf (J₃ '' F₃) ≤ sInf (J₆ '' F₆) := by
  apply csInf_le_csInf hbdd (hne.image J₆)
  rintro _ ⟨x, hx, rfl⟩
  exact ⟨π x, hmap x hx, hcost x hx⟩

/-- **N7, free final time.** A pointwise bound `V₃(t_f) ≤ V₆(t_f)` passes to the minimum over
`t_f`. -/
theorem freeTime_lower_bound {ι : Type*} (V₃ V₆ : ι → EReal) (h : ∀ tf, V₃ tf ≤ V₆ tf) :
    ⨅ tf, V₃ tf ≤ ⨅ tf, V₆ tf :=
  iInf_mono h

/-! ## Connection to the model -/

/-- Translational controls `(a, d)` landing softly at `t_f` from `θ` with `(r,v) ∈ X` on `[0,t_f]`. -/
def Lands (g : E3) (X : Set (E3 × E3)) (tf : ℝ) (θ : E3 × E3) (p : (ℝ → ℝ) × (ℝ → E3)) :
    Prop :=
  position g θ.1 θ.2 p.1 p.2 tf = 0 ∧ velocity g θ.2 p.1 p.2 tf = 0 ∧
    ∀ t ∈ Icc 0 tf, (position g θ.1 θ.2 p.1 p.2 t, velocity g θ.2 p.1 p.2 t) ∈ X

/-- 3DOF plans: throttle in `Acc`, direction measurable and unit; no attitude, no rate limits. -/
def plans3 (Acc : Set (ℝ → ℝ)) (tf : ℝ) (g : E3) (X : Set (E3 × E3)) (θ : E3 × E3) :
    Set ((ℝ → ℝ) × (ℝ → E3)) :=
  {p | p.1 ∈ Acc ∧ AEStronglyMeasurable p.2 (volume.restrict (Icc 0 tf)) ∧
    (∀ s ∈ Icc 0 tf, ‖p.2 s‖ = 1) ∧ Lands g X tf θ p}

/-- 5DOF plans (model M1): additionally a rate-limited body axis with the gimbal cone. -/
def plans5 (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) (X : Set (E3 × E3)) (θ : E3 × E3) :
    Set ((ℝ → ℝ) × (ℝ → E3)) :=
  {p | ∃ b, p.1 ∈ Acc ∧ AttitudeAdmissible tf ω δ p.2 b ∧ Lands g X tf θ p}

/-- 6DOF plans: additionally a rate-limited attitude path in `Att`. -/
def plans6 (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3)
    (X : Set (E3 × E3)) (θ : E3 × E3) : Set ((ℝ → ℝ) × (ℝ → E3)) :=
  {p | ∃ A, p.1 ∈ Acc ∧ Attitude6Admissible Att tf ω δ p.2 A ∧ Lands g X tf θ p}

theorem plans6_subset_plans5 {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))} {Acc : Set (ℝ → ℝ)}
    {tf ω δ : ℝ} {g : E3} {X : Set (E3 × E3)} {θ : E3 × E3} :
    plans6 Att Acc tf ω δ g X θ ⊆ plans5 Acc tf ω δ g X θ :=
  fun _ ⟨_, ha, hA, hL⟩ => ⟨_, ha, hA.toM1, hL⟩

theorem plans5_subset_plans3 {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {g : E3} {X : Set (E3 × E3)}
    {θ : E3 × E3} : plans5 Acc tf ω δ g X θ ⊆ plans3 Acc tf g X θ :=
  fun _ ⟨_, ha, hb, hL⟩ => ⟨ha, hb.d_meas, hb.d_unit, hL⟩

/-- **N7 (model form).** For any cost `J` of the translational controls (e.g. fuel), the 3DOF
value is at most the 5DOF value, which is at most the 6DOF value, for every `t_f`, every datum
`θ`, the same throttle class `Acc` and the same state constraint `X`. -/
theorem value3_le_value6 (J : (ℝ → ℝ) × (ℝ → E3) → ℝ) (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3)))
    (Acc : Set (ℝ → ℝ)) (tf ω δ : ℝ) (g : E3) (X : Set (E3 × E3)) (θ : E3 × E3) :
    ⨅ p ∈ plans3 Acc tf g X θ, (J p : EReal) ≤ ⨅ p ∈ plans5 Acc tf ω δ g X θ, (J p : EReal) ∧
      ⨅ p ∈ plans5 Acc tf ω δ g X θ, (J p : EReal) ≤
        ⨅ p ∈ plans6 Att Acc tf ω δ g X θ, (J p : EReal) :=
  ⟨relaxation_lower_bound _ _ J J id (fun _ hp => plans5_subset_plans3 hp) (fun _ _ => rfl),
   relaxation_lower_bound _ _ J J id (fun _ hp => plans6_subset_plans5 hp) (fun _ _ => rfl)⟩

/-- **N7 (model form, free final time).** Minimising also over `t_f` preserves the bound. -/
theorem value3_le_value6_freeTime (J : (ℝ → ℝ) × (ℝ → E3) → ℝ)
    (Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))) (Acc : Set (ℝ → ℝ)) (ω δ : ℝ) (g : E3)
    (X : Set (E3 × E3)) (θ : E3 × E3) :
    ⨅ tf, ⨅ p ∈ plans3 Acc tf g X θ, (J p : EReal) ≤
      ⨅ tf, ⨅ p ∈ plans6 Att Acc tf ω δ g X θ, (J p : EReal) :=
  freeTime_lower_bound _ _ fun tf =>
    (value3_le_value6 J Att Acc tf ω δ g X θ).1.trans (value3_le_value6 J Att Acc tf ω δ g X θ).2

/-- 3DOF landing set with state constraint `X`. -/
def landingSet3 (Acc : Set (ℝ → ℝ)) (tf : ℝ) (g : E3) (X : Set (E3 × E3)) : Set (E3 × E3) :=
  {θ | (plans3 Acc tf g X θ).Nonempty}

/-- Feasibility form: every datum from which a 6DOF (or 5DOF) landing exists is 3DOF-feasible. -/
theorem constrainedLandingSet6_subset_landingSet3 {Att : Set (ℝ → (E3 →ₗᵢ[ℝ] E3))}
    {Acc : Set (ℝ → ℝ)} {tf ω δ : ℝ} {g : E3} {X : Set (E3 × E3)} :
    constrainedLandingSet6 Att Acc tf ω δ g X ⊆ constrainedLandingSet Acc tf ω δ g X ∧
      constrainedLandingSet Acc tf ω δ g X ⊆ landingSet3 Acc tf g X := by
  constructor
  · rintro θ ⟨a, d, A, ha, hA, hr, hv, hX⟩
    exact ⟨a, d, _, ha, hA.toM1, hr, hv, hX⟩
  · rintro θ ⟨a, d, b, ha, hb, hr, hv, hX⟩
    exact ⟨(a, d), ha, hb.d_meas, hb.d_unit, hr, hv, hX⟩

end LcvxSolver
