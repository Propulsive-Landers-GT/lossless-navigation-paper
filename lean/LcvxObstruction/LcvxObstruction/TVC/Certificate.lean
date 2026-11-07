import LcvxObstruction.Abstract

/-!
# Pure TVC, Theorem TVC-1: the non-computational skeleton (math/06 §§2.4, 3, 4.5, 4.7)

This file formalizes the *logical* part of the computer-assisted theorem TVC-1. The analysis
that turns an arbitrary relaxed competitor into finite-dimensional data (math/06 §4.0 localization,
§4.1–4.3 pointwise majorants and torque remainders, §4.4 moments, Lemma 4.6′ discretization) is
**not** formalized here; it enters as the explicit hypothesis structure `TVC1Reduction`. The
certified numerical facts (the `2N × 2N` matrix inequality and the scalar bound defining `U_tot`)
enter only as fields of the explicit hypothesis structure `TVC1Certificate`. They are verified
externally in exact rational / Arb ball arithmetic by `numerics/verify-tvc/exact_cert.py`
(and `moment_check.py` for the scalar moment term); see `math/verify-tvc-report.md` §3.
No `axiom` is introduced.

Contents.
* `qf`, `qfL`: quadratic forms `xᵀ M x` on `Fin n → ℝ`, linear in `M`.
* `sprocedure_finsler` (**S-procedure + Finsler, finite dimensions**): if
  `Σ λ_k G_k + Σ ρ_j m_j m_jᵀ - Q ⪰ 0` then `xᵀQx ≤ Σ λ_k xᵀG_k x + Σ ρ_j (m_j·x)²` for every `x`.
* `sprocedure_finsler_sum` (**separability, TVC-Q1**): the same inequality summed over the
  components of a vector-valued tilt `h = (x_1, …, x_c)`; the bound for the vector equals the sum
  of the scalar bounds, so no planarity is needed.
* `TVC1Certificate`, `TVC1Reduction`, `gain_le_of_certificate`: every zero-lateral relaxed
  competitor has gain `≤ U_tot` (math/06 §4.5 "Use" and §4.7).
* `tvc1_skeleton` (**rotation-midpoint argument**, math/06 Lemma 2.4 + Thm TVC-1): a witness of
  gain `≥ G_w` in the rotation-invariant set `F^X`, a bound `U < G_w` on all relaxed competitors
  with zero lateral data, and `F^X ⊆ F ⊆ F^rel` ⇒ the rotation midpoint is not even
  relaxed-feasible ⇒ `F^X` is not convex ⇒ (Theorem A) no uniform convex relaxation is lossless.
* `rotPi`, `rotPi2`: the rotation `R_π = diag(-1,-1,1)` acting on `(r₀, v₀)`; its fixed points are
  exactly the data with zero lateral components, and `ℓ(θ) = r_{0z} + s* v_{0z}` is invariant.
* `tvc1_main`: everything combined.
-/

open Matrix

namespace LcvxObstruction.TVC

/-! ### Quadratic forms -/

section QuadForm

variable {n : ℕ}

/-- The quadratic form `xᵀ M x`. -/
def qf (M : Matrix (Fin n) (Fin n) ℝ) (x : Fin n → ℝ) : ℝ := x ⬝ᵥ (M *ᵥ x)

/-- `M ↦ xᵀ M x` as a linear map. -/
def qfL (x : Fin n → ℝ) : Matrix (Fin n) (Fin n) ℝ →ₗ[ℝ] ℝ where
  toFun M := qf M x
  map_add' A B := by simp [qf, add_mulVec, dotProduct_add]
  map_smul' c A := by simp [qf, smul_mulVec, dotProduct_smul]

@[simp] theorem qfL_apply (x : Fin n → ℝ) (M : Matrix (Fin n) (Fin n) ℝ) : qfL x M = qf M x := rfl

theorem qf_vecMulVec (m x : Fin n → ℝ) : qf (vecMulVec m m) x = (m ⬝ᵥ x) ^ 2 := by
  simp only [qf, vecMulVec_mulVec, dotProduct_smul, dotProduct_comm x m, op_smul_eq_mul, sq]

theorem qf_nonneg_of_posSemidef {M : Matrix (Fin n) (Fin n) ℝ} (hM : M.PosSemidef)
    (x : Fin n → ℝ) : 0 ≤ qf M x := by
  have := (posSemidef_iff_dotProduct_mulVec.1 hM).2 x
  simpa [qf, star_trivial] using this

/-- **S-procedure with Finsler terms, finite-dimensional form.** If the certificate matrix
`Σ λ_k G_k + Σ ρ_j m_j m_jᵀ - Q` is positive semidefinite, then for every `x`
`xᵀ Q x ≤ Σ λ_k xᵀ G_k x + Σ ρ_j (m_j ⬝ x)²`. (Signs of `λ, ρ` are not needed here; they are
needed when the constraint values are inserted, see `gain_le_of_certificate`.) -/
theorem sprocedure_finsler {K J : ℕ} {Q : Matrix (Fin n) (Fin n) ℝ}
    {G : Fin K → Matrix (Fin n) (Fin n) ℝ} {lam : Fin K → ℝ} {rho : Fin J → ℝ}
    {m : Fin J → Fin n → ℝ}
    (hcert : (∑ k, lam k • G k + ∑ j, rho j • vecMulVec (m j) (m j) - Q).PosSemidef)
    (x : Fin n → ℝ) :
    qf Q x ≤ ∑ k, lam k * qf (G k) x + ∑ j, rho j * (m j ⬝ᵥ x) ^ 2 := by
  have h := qf_nonneg_of_posSemidef hcert x
  have e : qf (∑ k, lam k • G k + ∑ j, rho j • vecMulVec (m j) (m j) - Q) x =
      ∑ k, lam k * qf (G k) x + ∑ j, rho j * (m j ⬝ᵥ x) ^ 2 - qf Q x := by
    rw [← qfL_apply, map_sub, map_add, map_sum, map_sum]
    simp [qf_vecMulVec]
  linarith

/-- **Separability (TVC-Q1).** The scalar certificate applied to each component `x i` of a
vector-valued tilt and summed. -/
theorem sprocedure_finsler_sum {K J c : ℕ} {Q : Matrix (Fin n) (Fin n) ℝ}
    {G : Fin K → Matrix (Fin n) (Fin n) ℝ} {lam : Fin K → ℝ} {rho : Fin J → ℝ}
    {m : Fin J → Fin n → ℝ}
    (hcert : (∑ k, lam k • G k + ∑ j, rho j • vecMulVec (m j) (m j) - Q).PosSemidef)
    (x : Fin c → Fin n → ℝ) :
    ∑ i, qf Q (x i) ≤
      ∑ k, lam k * ∑ i, qf (G k) (x i) + ∑ j, rho j * ∑ i, (m j ⬝ᵥ x i) ^ 2 := by
  calc ∑ i, qf Q (x i)
      ≤ ∑ i, (∑ k, lam k * qf (G k) (x i) + ∑ j, rho j * (m j ⬝ᵥ x i) ^ 2) :=
        Finset.sum_le_sum fun i _ => sprocedure_finsler hcert (x i)
    _ = _ := by
        rw [Finset.sum_add_distrib]; simp only [Finset.mul_sum]
        congr 1 <;> exact Finset.sum_comm

end QuadForm

/-! ### Certificate and reduction hypotheses -/

/-- **Certified numerical data of TVC-1** (math/06 Def. 4.5, §4.6–4.7), for a discretization with
`n` degrees of freedom per tilt component (`n = 2N`), `K` torque cells and `J` Finsler
functionals (`m₀`, `m_w`, clamps).

Every field below is a statement about explicit finite data. **These facts are not proved in
Lean: they are verified externally in exact rational / Arb ball arithmetic by
`numerics/verify-tvc/exact_cert.py`** (matrix inequality by exact integer Sylvester minors,
remainder and absorption conditions in Arb) **and `numerics/verify-tvc/moment_check.py`**
(scalar moment term, piecewise LP duality); see `math/verify-tvc-report.md` §3. A Lean user
must supply them as a term of this structure. -/
structure TVC1Certificate (n K J : ℕ) where
  /-- discretized gain form `𝒬` (scalar form of math/06 §4.2–4.3, incl. λ-weighted remainders) -/
  Q : Matrix (Fin n) (Fin n) ℝ
  /-- cell torque forms `G_k(x) = ∫_{cell k} n²` -/
  G : Fin K → Matrix (Fin n) (Fin n) ℝ
  /-- S-procedure multipliers `λ_k` (piecewise constant `λ(s)`) -/
  lam : Fin K → ℝ
  /-- a-priori torque bounds per cell, `c_k = (1+κ) N̄_k² · |cell k|` -/
  c : Fin K → ℝ
  /-- Finsler multipliers `ρ₀, ρ_w, ρ_c, …` -/
  rho : Fin J → ℝ
  /-- Finsler functionals (`m₀`, `m_w`, clamp rows) as vectors -/
  mom : Fin J → Fin n → ℝ
  /-- a-priori bound `Pen_max` on the penalty -/
  Penmax : ℝ
  /-- velocity parts `M^v_j` of the moment bounds -/
  Mv : Fin J → ℝ
  /-- penalty-driven moment shifts (`μ₀^max(Pen)`, `c_w Pen`, …) -/
  shift : Fin J → ℝ → ℝ
  /-- the certified bound `U_tot` -/
  U : ℝ
  lam_nonneg : ∀ k, 0 ≤ lam k
  rho_nonneg : ∀ j, 0 ≤ rho j
  /-- **the certified matrix inequality** (exact_cert.py: `-M ≻ 0` by exact minors) -/
  matrix_ineq : (∑ k, lam k • G k + ∑ j, rho j • vecMulVec (mom j) (mom j) - Q).PosSemidef
  /-- **the certified scalar bound** `V_λ + max_Pen [Σ ρ_j (M^v_j + shift_j(Pen))² - Pen] ≤ U_tot`
  with `V_λ = Σ λ_k c_k` -/
  scalar_ineq : ∀ P, 0 ≤ P → P ≤ Penmax →
    ∑ k, lam k * c k + ∑ j, rho j * (Mv j + shift j P) ^ 2 - P ≤ U

/-- **Analytic reduction of a competitor to certificate data (NOT formalized here).**
For every relaxed competitor `θ ∈ F^rel` with zero lateral data (`θ ∈ Z`), math/06 §4.0–4.4,
§4.7 and Lemma 4.6′ produce: discrete tilt coordinates `x i` for the `c` horizontal components,
a penalty `P ∈ [0, Pen_max]`, an early throttle credit `D` and cell excesses `e_k` with
* (§4.1–4.3) `gain θ ≤ Σ_i 𝒬(x_i) - P - D`,
* (§4.3, torque) `Σ_i G_k(x_i) ≤ c_k + e_k` on every cell,
* (§4.5 (i), absorption) `Σ_k λ_k e_k ≤ D`,
* (§4.4, §4.7, moments) `Σ_i (m_j ⬝ x_i)² ≤ (M^v_j + shift_j(P))²`.
This structure records that reduction as a hypothesis; its fields are the elementary but long
real-analysis lemmas of math/06 that remain to be formalized. -/
structure TVC1Reduction {X : Type*} {n K J : ℕ} (C : TVC1Certificate n K J) (c : ℕ)
    (gain : X → ℝ) (Frel Z : Set X) : Prop where
  reduce : ∀ θ ∈ Frel, θ ∈ Z → ∃ (x : Fin c → Fin n → ℝ) (P D : ℝ) (e : Fin K → ℝ),
    0 ≤ P ∧ P ≤ C.Penmax ∧
    gain θ ≤ ∑ i, qf C.Q (x i) - P - D ∧
    (∀ k, ∑ i, qf (C.G k) (x i) ≤ C.c k + e k) ∧
    ∑ k, C.lam k * e k ≤ D ∧
    ∀ j, ∑ i, (C.mom j ⬝ᵥ x i) ^ 2 ≤ (C.Mv j + C.shift j P) ^ 2

/-- **Competitor bound (math/06 §4.5 "Use", §4.7).** Given the certificate and the reduction, every
zero-lateral relaxed competitor has gain `≤ U_tot`. -/
theorem gain_le_of_certificate {X : Type*} {n K J c : ℕ} (C : TVC1Certificate n K J)
    {gain : X → ℝ} {Frel Z : Set X} (hred : TVC1Reduction C c gain Frel Z) :
    ∀ θ ∈ Frel, θ ∈ Z → gain θ ≤ C.U := by
  intro θ hθ hZ
  obtain ⟨x, P, D, e, hP0, hP1, hgain, htorque, habs, hmom⟩ := hred.reduce θ hθ hZ
  have hS := sprocedure_finsler_sum C.matrix_ineq x
  have h1 : ∑ k, C.lam k * ∑ i, qf (C.G k) (x i) ≤ ∑ k, C.lam k * C.c k + ∑ k, C.lam k * e k := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_le_sum fun k _ => by
      rw [← mul_add]; exact mul_le_mul_of_nonneg_left (htorque k) (C.lam_nonneg k)
  have h2 : ∑ j, C.rho j * ∑ i, (C.mom j ⬝ᵥ x i) ^ 2 ≤
      ∑ j, C.rho j * (C.Mv j + C.shift j P) ^ 2 :=
    Finset.sum_le_sum fun j _ => mul_le_mul_of_nonneg_left (hmom j) (C.rho_nonneg j)
  have h3 := C.scalar_ineq P hP0 hP1
  linarith

/-! ### The rotation-midpoint argument -/

/-- Midpoint of two boundary data. -/
noncomputable def mid {X : Type*} [AddCommGroup X] [Module ℝ X] (x y : X) : X := (1 / 2 : ℝ) • x + (1 / 2 : ℝ) • y

/-- **Skeleton of Theorem TVC-1.** `F^X ⊆ F ⊆ F^rel`; `Rot` a linear involution preserving `F^X`;
`gain = ℓ - κ` with `ℓ` linear and `Rot`-invariant; a witness `θ_w ∈ F^X` with gain `≥ G_w`; every
relaxed competitor with zero lateral data (`Rot θ = θ`) has gain `≤ U`; and `U < G_w`. Then the
rotation midpoint `θ_m = ½(θ_w + Rot θ_w)` is not relaxed-feasible, `F^X` is not convex, and no
uniform convex relaxation (any lifted space `Y`, any cost) is lossless for `F^X`. -/
theorem tvc1_skeleton {X : Type*} [AddCommGroup X] [Module ℝ X]
    {FX F Frel : Set X} (hXF : FX ⊆ F) (hFrel : F ⊆ Frel)
    (Rot : X →ₗ[ℝ] X) (hinv : ∀ θ ∈ FX, Rot θ ∈ FX) (hinvol : ∀ θ, Rot (Rot θ) = θ)
    (ℓ : X →ₗ[ℝ] ℝ) (κ : ℝ) (hℓ : ∀ θ, ℓ (Rot θ) = ℓ θ)
    {θw : X} (hw : θw ∈ FX) {Gw U : ℝ} (hGw : Gw ≤ ℓ θw - κ) (hU : U < Gw)
    (hbound : ∀ θ ∈ Frel, Rot θ = θ → ℓ θ - κ ≤ U) :
    mid θw (Rot θw) ∉ Frel ∧ ¬ Convex ℝ FX ∧
      ∀ (Y : Type*) [AddCommGroup Y] [Module ℝ Y] (R : UniformConvexRelaxation X Y),
        ¬ R.IsLossless FX ∧ ∀ Jc : X → Y → ℝ, ¬ R.IsLosslessFor Jc FX := by
  have hfix : Rot (mid θw (Rot θw)) = mid θw (Rot θw) := by
    simp only [mid, map_add, map_smul, hinvol]; abel
  have hgain : ℓ (mid θw (Rot θw)) = ℓ θw := by
    simp only [mid, map_add, map_smul, hℓ, smul_eq_mul]; ring
  have hnot : mid θw (Rot θw) ∉ Frel := fun hm => by
    have := hbound _ hm hfix
    rw [hgain] at this; linarith
  have hnc : ¬ Convex ℝ FX := fun hconv =>
    hnot (hFrel (hXF (hconv hw (hinv θw hw) (by norm_num) (by norm_num) (by norm_num))))
  exact ⟨hnot, hnc, fun Y _ _ R =>
    ⟨not_isLossless_of_not_convex hnc R, fun Jc => not_isLosslessFor_of_not_convex hnc R Jc⟩⟩

/-! ### The concrete rotation `R_π` on boundary data `(r₀, v₀)` -/

/-- `R_π = diag(-1, -1, 1)`, rotation by `π` about `e_z`, on `ℝ³`. -/
def rotPi : (Fin 3 → ℝ) →ₗ[ℝ] (Fin 3 → ℝ) where
  toFun x := ![-x 0, -x 1, x 2]
  map_add' x y := by ext i; fin_cases i <;> simp <;> ring
  map_smul' c x := by ext i; fin_cases i <;> simp

/-- `R_π` acting on boundary data `θ = (r₀, v₀)`. -/
def rotPi2 : (Fin 3 → ℝ) × (Fin 3 → ℝ) →ₗ[ℝ] (Fin 3 → ℝ) × (Fin 3 → ℝ) :=
  LinearMap.prodMap rotPi rotPi

theorem rotPi_rotPi (x : Fin 3 → ℝ) : rotPi (rotPi x) = x := by
  ext i; fin_cases i <;> simp [rotPi]

theorem rotPi2_invol (θ : (Fin 3 → ℝ) × (Fin 3 → ℝ)) : rotPi2 (rotPi2 θ) = θ := by
  simp [rotPi2, rotPi_rotPi]

/-- Fixed points of `R_π` are exactly the vectors with zero horizontal part. -/
theorem rotPi_fixed_iff (x : Fin 3 → ℝ) : rotPi x = x ↔ x 0 = 0 ∧ x 1 = 0 := by
  constructor
  · intro h
    have h0 := congrFun h 0
    have h1 := congrFun h 1
    simp [rotPi] at h0 h1
    constructor <;> linarith
  · rintro ⟨h0, h1⟩
    ext i; fin_cases i <;> simp [rotPi, h0, h1]

/-- **Zero lateral data ⇔ fixed by `R_π`**: `R_π θ = θ` iff `r_{0h} = v_{0h} = 0`. -/
theorem rotPi2_fixed_iff (θ : (Fin 3 → ℝ) × (Fin 3 → ℝ)) :
    rotPi2 θ = θ ↔ (θ.1 0 = 0 ∧ θ.1 1 = 0) ∧ (θ.2 0 = 0 ∧ θ.2 1 = 0) := by
  rw [← rotPi_fixed_iff, ← rotPi_fixed_iff, Prod.ext_iff]
  simp [rotPi2]

/-- The face functional `ℓ(θ) = r_{0z} + s* v_{0z}`. -/
def ellFace (sS : ℝ) : (Fin 3 → ℝ) × (Fin 3 → ℝ) →ₗ[ℝ] ℝ where
  toFun θ := θ.1 2 + sS * θ.2 2
  map_add' x y := by simp; ring
  map_smul' c x := by simp; ring

theorem ellFace_rotPi2 (sS : ℝ) (θ : (Fin 3 → ℝ) × (Fin 3 → ℝ)) :
    ellFace sS (rotPi2 θ) = ellFace sS θ := by
  simp [ellFace, rotPi2, rotPi]

/-! ### TVC-1, combined -/

/-- **Theorem TVC-1 (conditional on the externally certified data and the analytic reduction).**
Boundary data `θ = (r₀, v₀) ∈ ℝ³ × ℝ³`; `F^X ⊆ F ⊆ F^rel` (state-constrained, unconstrained and
relaxed pure-TVC landing sets); `F^X` invariant under `R_π`; gain `ℓ(θ) - κ` with
`ℓ = r_{0z} + s* v_{0z}` and `κ` the constant (`κ + J₀` of math/06); a witness `θ_w ∈ F^X` with
gain `≥ G_w`; a certificate `C` with `C.U < G_w`; and the reduction of every zero-lateral relaxed
competitor to certificate data. Then `θ_m ∉ F^rel`, `F^X` is not convex, and no uniform convex
relaxation is lossless. -/
theorem tvc1_main {n K J c : ℕ} {FX F Frel : Set ((Fin 3 → ℝ) × (Fin 3 → ℝ))}
    (hXF : FX ⊆ F) (hFrel : F ⊆ Frel) (hinv : ∀ θ ∈ FX, rotPi2 θ ∈ FX)
    (sS κ : ℝ) (C : TVC1Certificate n K J)
    (hred : TVC1Reduction C c (fun θ => ellFace sS θ - κ) Frel {θ | rotPi2 θ = θ})
    {θw : (Fin 3 → ℝ) × (Fin 3 → ℝ)} (hw : θw ∈ FX) {Gw : ℝ}
    (hGw : Gw ≤ ellFace sS θw - κ) (hmargin : C.U < Gw) :
    mid θw (rotPi2 θw) ∉ Frel ∧ ¬ Convex ℝ FX ∧
      ∀ (Y : Type*) [AddCommGroup Y] [Module ℝ Y]
        (R : UniformConvexRelaxation ((Fin 3 → ℝ) × (Fin 3 → ℝ)) Y),
        ¬ R.IsLossless FX ∧ ∀ Jc, ¬ R.IsLosslessFor Jc FX :=
  tvc1_skeleton hXF hFrel rotPi2 hinv rotPi2_invol (ellFace sS) κ (ellFace_rotPi2 sS) hw hGw
    hmargin fun θ hθ hfix => gain_le_of_certificate C hred θ hθ hfix

end LcvxObstruction.TVC
