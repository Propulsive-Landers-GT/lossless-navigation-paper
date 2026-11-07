import LcvxObstruction.Model

/-!
# Faithfulness of the closed-form trajectory

`Model.lean` defines the position by Cauchy's formula
`r(t) = r₀ + t v₀ + (t²/2) g + ∫₀ᵗ (t - s) a d`. Here we prove it equals `r₀ + ∫₀ᵗ v(s) ds`
with `v(s) = v₀ + s g + ∫₀ˢ a d`. So `position` really is the double integral of the
acceleration, i.e. the (Carathéodory) solution of `r̈ = a d + g`, `r(0) = r₀`, `ṙ(0) = v₀`
(`position_eq_integral_velocity`). The key step is Fubini (`integral_primitive`).
-/

open MeasureTheory Set

namespace LcvxObstruction

/-- **Fubini for the primitive:** `∫₀ᵗ ∫₀ˢ f = ∫₀ᵗ (t - σ) f(σ) dσ`, and the primitive is
integrable on `[0, t]`. -/
theorem integral_primitive {t : ℝ} (ht : 0 ≤ t) {f : ℝ → E3} (hf : IntegrableOn f (Icc 0 t)) :
    IntegrableOn (fun s => ∫ σ in Icc 0 s, f σ) (Icc 0 t) ∧
      ∫ s in Icc 0 t, (∫ σ in Icc 0 s, f σ) = ∫ σ in Icc 0 t, (t - σ) • f σ := by
  set μ := volume.restrict (Icc (0 : ℝ) t) with hμ
  set S : Set (ℝ × ℝ) := {p | p.2 ≤ p.1} with hSdef
  have hS : MeasurableSet S := measurableSet_le measurable_snd measurable_fst
  set G : ℝ × ℝ → E3 := S.indicator (fun p => f p.2) with hGdef
  have hG : Integrable G (μ.prod μ) := (Integrable.comp_snd hf μ).indicator hS
  have h1 : ∀ s ∈ Icc 0 t, ∫ σ in Icc 0 s, f σ = ∫ σ, G (s, σ) ∂μ := by
    intro s hs
    have e : (fun σ => G (s, σ)) = (Iic s).indicator f := by
      funext σ
      simp only [hGdef, hSdef, Set.indicator, mem_setOf_eq, mem_Iic]
    rw [e, hμ, setIntegral_indicator measurableSet_Iic]
    congr 2
    ext σ
    simp only [mem_Icc, mem_inter_iff, mem_Iic]
    constructor
    · rintro ⟨h0, h1⟩; exact ⟨⟨h0, h1.trans hs.2⟩, h1⟩
    · rintro ⟨⟨h0, -⟩, h1⟩; exact ⟨h0, h1⟩
  have h2 : ∀ σ ∈ Icc 0 t, ∫ s, G (s, σ) ∂μ = (t - σ) • f σ := by
    intro σ hσ
    have e : (fun s => G (s, σ)) = (Ici σ).indicator (fun _ => f σ) := by
      funext s
      simp only [hGdef, hSdef, Set.indicator, mem_setOf_eq, mem_Ici]
    rw [e, hμ, setIntegral_indicator measurableSet_Ici, setIntegral_const]
    have : Icc 0 t ∩ Ici σ = Icc σ t := by
      ext s; simp only [mem_Icc, mem_inter_iff, mem_Ici]
      constructor
      · rintro ⟨⟨-, h1⟩, h2⟩; exact ⟨h2, h1⟩
      · rintro ⟨h1, h2⟩; exact ⟨⟨hσ.1.trans h1, h2⟩, h1⟩
    rw [this, Real.volume_real_Icc_of_le hσ.2]
  have hint : Integrable (fun s => ∫ σ, G (s, σ) ∂μ) μ := hG.integral_prod_left
  refine ⟨hint.congr ?_, ?_⟩
  · exact (ae_restrict_of_forall_mem measurableSet_Icc fun s hs => (h1 s hs).symm)
  · calc ∫ s in Icc 0 t, (∫ σ in Icc 0 s, f σ) = ∫ s, ∫ σ, G (s, σ) ∂μ ∂μ :=
          setIntegral_congr_fun measurableSet_Icc h1
      _ = ∫ σ, ∫ s, G (s, σ) ∂μ ∂μ := integral_integral_swap (f := fun s σ => G (s, σ)) hG
      _ = ∫ σ in Icc 0 t, (t - σ) • f σ := setIntegral_congr_fun measurableSet_Icc h2

/-- **`position` is the integral of `velocity`.** -/
theorem position_eq_integral_velocity {g r₀ v₀ : E3} {a : ℝ → ℝ} {d : ℝ → E3} {t : ℝ}
    (ht : 0 ≤ t) (hf : IntegrableOn (fun s => a s • d s) (Icc 0 t)) :
    position g r₀ v₀ a d t = r₀ + ∫ s in Icc 0 t, velocity g v₀ a d s := by
  obtain ⟨hFI, hF⟩ := integral_primitive ht hf
  have hc1 : IntegrableOn (fun _ : ℝ => v₀) (Icc 0 t) := integrableOn_const measure_Icc_lt_top.ne
  have hc2 : IntegrableOn (fun s : ℝ => s • g) (Icc 0 t) :=
    (continuous_id.smul continuous_const).continuousOn.integrableOn_Icc
  have hid : ∫ s in Icc 0 t, s = t ^ 2 / 2 := by
    rw [integral_Icc_eq_integral_Ioc, ← intervalIntegral.integral_of_le ht, integral_id]; ring
  have h12 : IntegrableOn (fun s : ℝ => v₀ + s • g) (Icc 0 t) := hc1.add hc2
  simp only [position, velocity]
  rw [integral_add h12 hFI, integral_add hc1 hc2, setIntegral_const,
    Real.volume_real_Icc_of_le ht, sub_zero, integral_smul_const, hid, hF]
  abel

end LcvxObstruction
