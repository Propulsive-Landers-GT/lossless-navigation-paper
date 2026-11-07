import LcvxObstruction.Main

/-!
# Explicit mass depletion: deriving `a ≥ a₁` (math/02 Lemma 4.3)

Thrust magnitude `T` with `ρ₁ ≤ T ≤ ρ₂` on `[0, tf]`, mass `m(t) = m₀ - α ∫₀ᵗ T`
(`ṁ = -α T`), dry-mass constraint `m(t) ≥ m_dry > 0`, acceleration `a = T / m`.
Then every admissible `a` satisfies `a(s) ≥ a₁(s) := ρ₁ / (m₀ - α ρ₁ s)`, and the min-throttle
profile `T ≡ ρ₁` realises `a = a₁`. So Theorem B applies to this model
(`no_lossless_relaxation_5dof_mass`).
-/

open MeasureTheory Set Real

namespace LcvxObstruction

/-- Mass at time `t` under thrust history `T`: `m₀ - α ∫₀ᵗ T`. -/
noncomputable def massOf (α m₀ : ℝ) (T : ℝ → ℝ) (t : ℝ) : ℝ := m₀ - α * ∫ s in Icc 0 t, T s

/-- **Mass-depletion acceleration class.** `a` is admissible iff there is an integrable thrust
history `T ∈ [ρ₁, ρ₂]` keeping the mass above `m_dry`, with `a = T / m` on `[0, tf]`.
(Integrability of `a` is listed explicitly; it is automatic since `|a| ≤ ρ₂/m_dry`.) -/
def AccMass (ρ₁ ρ₂ α m₀ mdry tf : ℝ) : Set (ℝ → ℝ) :=
  {a | IntegrableOn a (Icc 0 tf) ∧ ∃ T : ℝ → ℝ, IntegrableOn T (Icc 0 tf) ∧
    (∀ s ∈ Icc 0 tf, ρ₁ ≤ T s ∧ T s ≤ ρ₂) ∧ (∀ s ∈ Icc 0 tf, mdry ≤ massOf α m₀ T s) ∧
    ∀ s ∈ Icc 0 tf, a s = T s / massOf α m₀ T s}

/-- Minimum-throttle acceleration `a₁(s) = ρ₁ / (m₀ - α ρ₁ s)`. -/
noncomputable def aMinMass (ρ₁ α m₀ : ℝ) (s : ℝ) : ℝ := ρ₁ / (m₀ - α * ρ₁ * s)

theorem massOf_const (α m₀ c : ℝ) {t : ℝ} (ht : 0 ≤ t) :
    massOf α m₀ (fun _ => c) t = m₀ - α * c * t := by
  simp only [massOf, setIntegral_const, Real.volume_real_Icc_of_le ht, sub_zero, smul_eq_mul]
  ring

/-- **Lemma 4.3:** every mass-depletion acceleration dominates `a₁`. -/
theorem accMass_spec {ρ₁ ρ₂ α m₀ mdry tf : ℝ} (hρ₁ : 0 ≤ ρ₁) (hα : 0 ≤ α) (hmdry : 0 < mdry) :
    ∀ a ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf,
      IntegrableOn a (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, aMinMass ρ₁ α m₀ s ≤ a s := by
  rintro a ⟨haI, T, hTI, hTb, hm, ha⟩
  refine ⟨haI, fun s hs => ?_⟩
  have hsub : Icc 0 s ⊆ Icc 0 tf := Icc_subset_Icc_right hs.2
  have hint : ρ₁ * s ≤ ∫ σ in Icc 0 s, T σ := by
    have := setIntegral_ge_of_const_le (c := ρ₁) measurableSet_Icc measure_Icc_lt_top.ne
      (fun σ hσ => (hTb σ (hsub hσ)).1) (hTI.mono_set hsub)
    rwa [Real.volume_real_Icc_of_le hs.1, sub_zero, smul_eq_mul, mul_comm] at this
  have hmle : massOf α m₀ T s ≤ m₀ - α * ρ₁ * s := by
    simp only [massOf]; nlinarith
  have hmpos : 0 < massOf α m₀ T s := lt_of_lt_of_le hmdry (hm s hs)
  rw [ha s hs, aMinMass]
  calc ρ₁ / (m₀ - α * ρ₁ * s) ≤ ρ₁ / massOf α m₀ T s :=
        div_le_div_of_nonneg_left hρ₁ hmpos hmle
    _ ≤ T s / massOf α m₀ T s := div_le_div_of_nonneg_right (hTb s hs).1 hmpos.le

/-- `a₁` is continuous and positive on `[0, tf]` when the min-throttle burn keeps the mass above
`m_dry > 0`. -/
theorem aMinMass_props {ρ₁ α m₀ mdry tf : ℝ} (hρ₁ : 0 < ρ₁) (hα : 0 ≤ α) (hmdry : 0 < mdry)
    (hburn : mdry ≤ m₀ - α * ρ₁ * tf) :
    ContinuousOn (aMinMass ρ₁ α m₀) (Icc 0 tf) ∧ ∀ s ∈ Icc 0 tf, 0 < aMinMass ρ₁ α m₀ s := by
  have hpos : ∀ s ∈ Icc 0 tf, 0 < m₀ - α * ρ₁ * s := fun s hs => by
    have : α * ρ₁ * s ≤ α * ρ₁ * tf := mul_le_mul_of_nonneg_left hs.2 (by positivity)
    linarith
  refine ⟨?_, fun s hs => div_pos hρ₁ (hpos s hs)⟩
  apply ContinuousOn.div continuousOn_const (by fun_prop)
  exact fun s hs => (hpos s hs).ne'

/-- The min-throttle profile is admissible: `a₁ ∈ AccMass`. -/
theorem aMinMass_mem {ρ₁ ρ₂ α m₀ mdry tf : ℝ} (hρ₁ : 0 < ρ₁) (h12 : ρ₁ ≤ ρ₂) (hα : 0 ≤ α)
    (hmdry : 0 < mdry) (hburn : mdry ≤ m₀ - α * ρ₁ * tf) :
    aMinMass ρ₁ α m₀ ∈ AccMass ρ₁ ρ₂ α m₀ mdry tf := by
  obtain ⟨hc, -⟩ := aMinMass_props hρ₁ hα hmdry hburn
  refine ⟨hc.integrableOn_Icc, fun _ => ρ₁, integrableOn_const measure_Icc_lt_top.ne,
    fun s _ => ⟨le_rfl, h12⟩, fun s hs => ?_, fun s hs => ?_⟩
  · rw [massOf_const α m₀ ρ₁ hs.1]
    have : α * ρ₁ * s ≤ α * ρ₁ * tf := mul_le_mul_of_nonneg_left hs.2 (by positivity)
    linarith
  · rw [massOf_const α m₀ ρ₁ hs.1, aMinMass]

/-- **Main theorem with explicit mass depletion** (no state constraints, `b(tf)` free):
no uniform convex relaxation is lossless for the 5DOF landing set of the mass-depletion model. -/
theorem no_lossless_relaxation_5dof_mass {Y : Type*} [AddCommGroup Y] [Module ℝ Y]
    {ρ₁ ρ₂ α m₀ mdry tf ω δ : ℝ} (g : E3) (hρ₁ : 0 < ρ₁) (h12 : ρ₁ ≤ ρ₂) (hα : 0 ≤ α)
    (hmdry : 0 < mdry) (hburn : mdry ≤ m₀ - α * ρ₁ * tf)
    (htf : 0 < tf) (hω : 0 < ω) (hδ : 0 ≤ δ) (hreg : δ + ω * tf ≤ π / 2)
    (R : UniformConvexRelaxation (E3 × E3) Y) :
    ¬ R.IsLossless (landingSet (AccMass ρ₁ ρ₂ α m₀ mdry tf) tf ω δ g) := by
  obtain ⟨hc, hp⟩ := aMinMass_props hρ₁ hα hmdry hburn
  exact no_lossless_relaxation_5dof g htf hω hδ hreg hc hp (accMass_spec hρ₁.le hα hmdry)
    (aMinMass_mem hρ₁ h12 hα hmdry hburn) R

end LcvxObstruction
