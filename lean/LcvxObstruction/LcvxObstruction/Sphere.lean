import Mathlib

/-!
# Spherical geometry via inner products

All statements are for a general real inner product space `V`; unit vectors play the role of
points of the sphere and `InnerProductGeometry.angle` is the great-circle distance.

* `cos_le_inner_of_angle_le`, `angle_le_of_cos_le_inner`, `angle_eq_of_inner_eq_cos`:
  translation between angle bounds and inner-product bounds for unit vectors.
* `inner_triangle` — (i) spherical triangle inequality in inner-product form
  (deduced from Mathlib's `InnerProductGeometry.angle_le_angle_add_angle`).
* `inner_triangle_eq` — (ii) equality case: tightness forces both legs tight.
* `lateral_eq_of_inner_ge` — (iii) rigidity: with pole `z`, if `x = cos θ z + sin θ u`,
  `y = cos θ' z + sin θ' u'` (`u, u'` unit, `⊥ z`, `sin θ, sin θ' > 0`) and
  `⟪x,y⟫ ≥ cos (θ - θ')`, then `u = u'`. Stated intrinsically with `u := (sin θ)⁻¹ (x - cos θ z)`.
* `inner_triangle_eq_lateral` — (ii') the geometric equality case: `x` lies on the great circle
  through `z` and `y`, beyond `y`.
-/

open InnerProductGeometry Real
open scoped RealInnerProductSpace

namespace LcvxObstruction

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]

/-- For unit vectors the inner product is the cosine of the angle. -/
theorem inner_eq_cos_angle {x y : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) :
    ⟪x, y⟫ = Real.cos (angle x y) := by
  rw [cos_angle, hx, hy]; simp

theorem cos_le_inner_of_angle_le {x y : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) {α : ℝ}
    (h : angle x y ≤ α) (hα : α ≤ π) : Real.cos α ≤ ⟪x, y⟫ := by
  rw [inner_eq_cos_angle hx hy]
  exact Real.cos_le_cos_of_nonneg_of_le_pi (angle_nonneg x y) hα h

theorem angle_le_of_cos_le_inner {x y : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) {α : ℝ}
    (h0 : 0 ≤ α) (hπ : α ≤ π) (h : Real.cos α ≤ ⟪x, y⟫) : angle x y ≤ α := by
  have : angle x y = Real.arccos ⟪x, y⟫ := by rw [angle, hx, hy]; simp
  rw [this]
  calc Real.arccos ⟪x, y⟫ ≤ Real.arccos (Real.cos α) := Real.arccos_le_arccos h
    _ = α := Real.arccos_cos h0 hπ

theorem angle_eq_of_inner_eq_cos {x y : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) {α : ℝ}
    (h0 : 0 ≤ α) (hπ : α ≤ π) (h : ⟪x, y⟫ = Real.cos α) : angle x y = α := by
  rw [angle, hx, hy, h]; simp [Real.arccos_cos h0 hπ]

/-- **(i) Spherical triangle inequality, inner-product form.** -/
theorem inner_triangle {x y z : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) (hz : ‖z‖ = 1)
    {α β : ℝ} (hα : 0 ≤ α) (hβ : 0 ≤ β) (hαβ : α + β ≤ π)
    (hxy : Real.cos α ≤ ⟪x, y⟫) (hyz : Real.cos β ≤ ⟪y, z⟫) :
    Real.cos (α + β) ≤ ⟪x, z⟫ := by
  have h1 := angle_le_of_cos_le_inner hx hy hα (by linarith) hxy
  have h2 := angle_le_of_cos_le_inner hy hz hβ (by linarith) hyz
  apply cos_le_inner_of_angle_le hx hz _ hαβ
  exact (angle_le_angle_add_angle x y z).trans (add_le_add h1 h2)

/-- **(ii) Equality case of the triangle inequality**: if the bound of `inner_triangle` is
attained then both legs are tight. -/
theorem inner_triangle_eq {x y z : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) (hz : ‖z‖ = 1)
    {α β : ℝ} (hα : 0 ≤ α) (hβ : 0 ≤ β) (hαβ : α + β ≤ π)
    (hxy : Real.cos α ≤ ⟪x, y⟫) (hyz : Real.cos β ≤ ⟪y, z⟫)
    (hxz : ⟪x, z⟫ = Real.cos (α + β)) :
    ⟪x, y⟫ = Real.cos α ∧ ⟪y, z⟫ = Real.cos β := by
  have h1 := angle_le_of_cos_le_inner hx hy hα (by linarith) hxy
  have h2 := angle_le_of_cos_le_inner hy hz hβ (by linarith) hyz
  have h3 := angle_eq_of_inner_eq_cos hx hz (by linarith) hαβ hxz
  have htri := angle_le_angle_add_angle x y z
  have e1 : angle x y = α := by linarith
  have e2 : angle y z = β := by linarith
  rw [inner_eq_cos_angle hx hy, inner_eq_cos_angle hy hz, e1, e2]
  exact ⟨rfl, rfl⟩

/-- The unit "lateral direction" of `x` relative to the pole `z`, given that `⟪x,z⟫ = cos θ`:
`(sin θ)⁻¹ • (x - cos θ • z)`. -/
noncomputable def lateral (z x : V) (θ : ℝ) : V := (Real.sin θ)⁻¹ • (x - Real.cos θ • z)

theorem inner_lateral_pole {x z : V} (hz : ‖z‖ = 1) {θ : ℝ} (hxz : ⟪x, z⟫ = Real.cos θ) :
    ⟪lateral z x θ, z⟫ = 0 := by
  have hzz : ⟪z, z⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hz]; norm_num
  simp only [lateral, real_inner_smul_left, inner_sub_left, hxz, real_inner_smul_left, hzz]
  ring

theorem inner_lateral_self {x z : V} (hx : ‖x‖ = 1) (hz : ‖z‖ = 1) {θ : ℝ}
    (hxz : ⟪x, z⟫ = Real.cos θ) (hs : Real.sin θ ≠ 0) :
    ⟪lateral z x θ, lateral z x θ⟫ = 1 := by
  have hzx : ⟪z, x⟫ = Real.cos θ := by rw [real_inner_comm]; exact hxz
  have hxx : ⟪x, x⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hx]; norm_num
  have hzz : ⟪z, z⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hz]; norm_num
  simp only [lateral, real_inner_smul_left, real_inner_smul_right, inner_sub_left,
    inner_sub_right, hxz, hzx, hxx, hzz]
  have := Real.sin_sq_add_cos_sq θ
  field_simp
  linarith

theorem norm_lateral {x z : V} (hx : ‖x‖ = 1) (hz : ‖z‖ = 1) {θ : ℝ}
    (hxz : ⟪x, z⟫ = Real.cos θ) (hs : Real.sin θ ≠ 0) : ‖lateral z x θ‖ = 1 := by
  have h := inner_lateral_self hx hz hxz hs
  rw [real_inner_self_eq_norm_sq] at h
  have h0 := norm_nonneg (lateral z x θ)
  nlinarith

/-- Reconstruction: `x = cos θ • z + sin θ • lateral z x θ` (when `sin θ ≠ 0`). -/
theorem eq_cos_smul_add_sin_smul_lateral (z x : V) {θ : ℝ} (hs : Real.sin θ ≠ 0) :
    x = Real.cos θ • z + Real.sin θ • lateral z x θ := by
  simp only [lateral, smul_smul, mul_inv_cancel₀ hs, one_smul]
  abel

theorem inner_lateral {x y z : V} (hz : ‖z‖ = 1) {θ θ' : ℝ}
    (hxz : ⟪x, z⟫ = Real.cos θ) (hyz : ⟪y, z⟫ = Real.cos θ') :
    ⟪lateral z x θ, lateral z y θ'⟫ =
      (Real.sin θ)⁻¹ * (Real.sin θ')⁻¹ * (⟪x, y⟫ - Real.cos θ * Real.cos θ') := by
  have hzy : ⟪z, y⟫ = Real.cos θ' := by rw [real_inner_comm]; exact hyz
  have hzz : ⟪z, z⟫ = 1 := by rw [real_inner_self_eq_norm_sq, hz]; norm_num
  simp only [lateral, real_inner_smul_left, real_inner_smul_right, inner_sub_left,
    inner_sub_right, hxz, hzy, hzz]
  ring

/-- **(iii) Rigidity.** Let `z` be a unit pole and `x, y` unit vectors at polar angles `θ, θ'`
(`⟪x,z⟫ = cos θ`, `⟪y,z⟫ = cos θ'`) off the poles (`sin θ, sin θ' > 0`). If
`⟪x, y⟫ ≥ cos (θ - θ')`, i.e. `angle x y ≤ |θ - θ'|`, the smallest value permitted by the triangle
inequality, then `x` and `y` have the same lateral (azimuthal) direction. -/
theorem lateral_eq_of_inner_ge {x y z : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) (hz : ‖z‖ = 1)
    {θ θ' : ℝ} (hxz : ⟪x, z⟫ = Real.cos θ) (hyz : ⟪y, z⟫ = Real.cos θ')
    (hs : 0 < Real.sin θ) (hs' : 0 < Real.sin θ') (h : Real.cos (θ - θ') ≤ ⟪x, y⟫) :
    lateral z x θ = lateral z y θ' := by
  set u := lateral z x θ
  set u' := lateral z y θ'
  have huu : ⟪u, u⟫ = 1 := inner_lateral_self hx hz hxz hs.ne'
  have hu'u' : ⟪u', u'⟫ = 1 := inner_lateral_self hy hz hyz hs'.ne'
  have huu' : 1 ≤ ⟪u, u'⟫ := by
    rw [inner_lateral hz hxz hyz, Real.cos_sub] at *
    have hpos : 0 < Real.sin θ * Real.sin θ' := mul_pos hs hs'
    rw [← mul_inv, le_inv_mul_iff₀ hpos]
    linarith
  have hu'u : ⟪u', u⟫ = ⟪u, u'⟫ := real_inner_comm _ _
  have : ⟪u - u', u - u'⟫ ≤ 0 := by
    simp only [inner_sub_left, inner_sub_right, huu, hu'u', hu'u]
    linarith
  exact sub_eq_zero.mp (real_inner_self_nonpos.mp this)

/-- **(ii') Geometric equality case.** If the triangle bound `⟪x,z⟫ ≥ cos (α+β)` is attained
with `0 < β`, `0 < α + β < π`, then `x` and `y` lie on a common half great circle from `z`:
both have the same lateral direction `u` (so `x = cos(α+β) z + sin(α+β) u` and
`y = cos β z + sin β u`), i.e. `x` lies in the plane of `y, z`, beyond `y`. -/
theorem inner_triangle_eq_lateral {x y z : V} (hx : ‖x‖ = 1) (hy : ‖y‖ = 1) (hz : ‖z‖ = 1)
    {α β : ℝ} (hα : 0 ≤ α) (hβ : 0 < β) (hαβ : α + β < π)
    (hxy : Real.cos α ≤ ⟪x, y⟫) (hyz : Real.cos β ≤ ⟪y, z⟫)
    (hxz : ⟪x, z⟫ = Real.cos (α + β)) :
    ⟪y, z⟫ = Real.cos β ∧ lateral z x (α + β) = lateral z y β := by
  obtain ⟨-, e2⟩ := inner_triangle_eq hx hy hz hα hβ.le hαβ.le hxy hyz hxz
  refine ⟨e2, lateral_eq_of_inner_ge hx hy hz hxz e2 ?_ ?_ ?_⟩
  · exact Real.sin_pos_of_pos_of_lt_pi (by linarith) hαβ
  · exact Real.sin_pos_of_pos_of_lt_pi hβ (by linarith)
  · simpa using hxy

end LcvxObstruction
