import LCvx.Fixpoint
import Mathlib.Analysis.Calculus.ContDiff.WithLp
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.Analysis.Calculus.ContDiff.Operations
import Mathlib.Analysis.Calculus.ContDiff.RCLike
import Mathlib.Analysis.InnerProductSpace.Calculus

/-!
# 6-DOF powered descent satisfies the hypotheses of `LCvx.Basic`

The rigid-body model of Szmuk, Reynolds & Açıkmeşe (arXiv:1811.10803), with the LCvx slack in
the mass flow, discretized exactly as in `solver/sixdof_lcvx.py`: thrust and slack held constant
over each of `N` intervals, and each interval integrated with `M` RK4 substeps. The time of flight
is `s`, so each substep is `s / (N * M)` long.

The point of this file is that the theorems of `LCvx.Basic` need the equality constraint map `F`
to have a strict derivative. Here `F` is "integrate the 6-DOF dynamics, then read off the terminal
conditions", and we prove it is `C¹` wherever the mass stays positive. Nothing about the
dynamics is linearized or approximated.
-/

open Filter Topology Set

-- The instance assumptions are declared once for the whole file; not every lemma uses all of them.
set_option linter.unusedSectionVars false

namespace LCvx.SixDOF

noncomputable section

/-- `fun_prop` support for vector literals `![a, b, c]`. -/
@[fun_prop]
theorem contDiff_vecCons {k : ℕ} {n : WithTop ℕ∞} :
    ContDiff ℝ n (fun p : ℝ × (Fin k → ℝ) => Matrix.vecCons p.1 p.2) := by
  rw [contDiff_pi]; intro i
  refine Fin.cases ?_ (fun j => ?_) i
  · simp only [Matrix.cons_val_zero]; fun_prop
  · simp only [Matrix.cons_val_succ]; fun_prop

abbrev Vec3 := Fin 3 → ℝ
abbrev Quat := Fin 4 → ℝ
/-- `(m, r, v, q, ω)`: mass, inertial position, inertial velocity, body-to-inertial attitude
quaternion (scalar first) and body angular rate. -/
abbrev State := ℝ × Vec3 × Vec3 × Quat × Vec3
/-- Body-frame thrust, with the Euclidean norm. -/
abbrev Thrust := EuclideanSpace ℝ (Fin 3)

/-- Vehicle constants. -/
structure Params where
  /-- Mass flow per unit thrust, `1 / (Isp g₀)`. -/
  α : ℝ
  /-- Gravity, inertial frame. -/
  g : Vec3
  /-- Principal moments of inertia. -/
  J : Vec3
  /-- Engine position, body frame. -/
  rT : Vec3

def cross (a b : Vec3) : Vec3 :=
  ![a 1 * b 2 - a 2 * b 1, a 2 * b 0 - a 0 * b 2, a 0 * b 1 - a 1 * b 0]

/-- Body-to-inertial rotation of `T` (direction cosine matrix of the quaternion `q`). -/
def rot (q : Quat) (T : Vec3) : Vec3 :=
  ![(1 - 2 * (q 2 ^ 2 + q 3 ^ 2)) * T 0 + 2 * (q 1 * q 2 - q 0 * q 3) * T 1
      + 2 * (q 1 * q 3 + q 0 * q 2) * T 2,
    2 * (q 1 * q 2 + q 0 * q 3) * T 0 + (1 - 2 * (q 1 ^ 2 + q 3 ^ 2)) * T 1
      + 2 * (q 2 * q 3 - q 0 * q 1) * T 2,
    2 * (q 1 * q 3 - q 0 * q 2) * T 0 + 2 * (q 2 * q 3 + q 0 * q 1) * T 1
      + (1 - 2 * (q 1 ^ 2 + q 2 ^ 2)) * T 2]

/-- Attitude kinematics `q̇ = ½ q ⊗ (0, ω)`. -/
def quatRate (q : Quat) (w : Vec3) : Quat :=
  ![-(q 1 * w 0 + q 2 * w 1 + q 3 * w 2) / 2, (q 0 * w 0 + q 2 * w 2 - q 3 * w 1) / 2,
    (q 0 * w 1 - q 1 * w 2 + q 3 * w 0) / 2, (q 0 * w 2 + q 1 * w 1 - q 2 * w 0) / 2]

/-- The relaxed 6-DOF vector field: `ṁ = -α Γ`, `ṙ = v`, `v̇ = C(q) T / m + g`,
`q̇ = ½ q ⊗ ω`, `J ω̇ = r_T × T - ω × J ω`. -/
def field (p : Params) (x : State) (u : Thrust) (Γ : ℝ) : State :=
  (-(p.α * Γ), x.2.2.1, fun i => rot x.2.2.2.1 ![u 0, u 1, u 2] i / x.1 + p.g i,
    quatRate x.2.2.2.1 x.2.2.2.2,
    fun i => (cross p.rT ![u 0, u 1, u 2] i
      - cross x.2.2.2.2 ![p.J 0 * x.2.2.2.2 0, p.J 1 * x.2.2.2.2 1, p.J 2 * x.2.2.2.2 2] i) / p.J i)

/-- RK4 stages, as functions of `q = (x, u, Γ, h)`. -/
def K1 (p : Params) (q : State × Thrust × ℝ × ℝ) : State := field p q.1 q.2.1 q.2.2.1
def K2 (p : Params) (q : State × Thrust × ℝ × ℝ) : State :=
  field p (q.1 + (q.2.2.2 / 2) • K1 p q) q.2.1 q.2.2.1
def K3 (p : Params) (q : State × Thrust × ℝ × ℝ) : State :=
  field p (q.1 + (q.2.2.2 / 2) • K2 p q) q.2.1 q.2.2.1
def K4 (p : Params) (q : State × Thrust × ℝ × ℝ) : State :=
  field p (q.1 + q.2.2.2 • K3 p q) q.2.1 q.2.2.1

/-- One RK4 step of length `h` from `x`, control `u` and slack `Γ` held constant. -/
def rk4 (p : Params) (q : State × Thrust × ℝ × ℝ) : State :=
  q.1 + (q.2.2.2 / 6) • (K1 p q + 2 • K2 p q + 2 • K3 p q + K4 p q)

/-- `j` RK4 substeps of length `h` starting from `x`. -/
def substeps (p : Params) : ℕ → State × Thrust × ℝ × ℝ → State
  | 0, q => q.1
  | j + 1, q => rk4 p (substeps p j q, q.2.1, q.2.2.1, q.2.2.2)

/-- One interval of the discretization: `M` substeps covering time `s / N`. -/
def interval (p : Params) (N M : ℕ) (x : State) (u : Thrust) (Γ s : ℝ) : State :=
  substeps p M (x, u, Γ, s / (N * M))

variable {N : ℕ} {P : Type*} [NormedAddCommGroup P] [NormedSpace ℝ P]

/-- Shooting: the state at node `k`, from initial state `x₀`, for the controls in `z`. The time
of flight is `tof z.2.2`. -/
def traj (p : Params) (M : ℕ) (tof : P → ℝ) (x₀ : State) (z : Dec N Thrust P) : ℕ → State
  | 0 => x₀
  | k + 1 => if h : k < N then
      interval p N M (traj p M tof x₀ z k) (z.1 ⟨k, h⟩) (z.2.1 ⟨k, h⟩) (tof z.2.2)
    else traj p M tof x₀ z k

/-! ### Mass bookkeeping is exact -/

lemma field_mass (p : Params) (x : State) (u : Thrust) (Γ : ℝ) :
    (field p x u Γ).1 = -(p.α * Γ) := rfl

lemma rk4_mass (p : Params) (q : State × Thrust × ℝ × ℝ) :
    (rk4 p q).1 = q.1.1 - q.2.2.2 * (p.α * q.2.2.1) := by
  simp only [rk4, K1, K2, K3, K4, Prod.fst_add, Prod.smul_fst, field_mass]
  simp only [smul_eq_mul, nsmul_eq_mul]
  ring

lemma substeps_mass (p : Params) (j : ℕ) (q : State × Thrust × ℝ × ℝ) :
    (substeps p j q).1 = q.1.1 - j * (q.2.2.2 * (p.α * q.2.2.1)) := by
  induction j with
  | zero => simp [substeps]
  | succ j ih => simp only [substeps, rk4_mass, ih]; push_cast; ring

lemma interval_mass (p : Params) (N M : ℕ) (x : State) (u : Thrust) (Γ s : ℝ) :
    (interval p N M x u Γ s).1 = x.1 - M * (s / (N * M) * (p.α * Γ)) :=
  substeps_mass p M _

/-! ### Smoothness -/

theorem contDiffAt_field (p : Params) {n : WithTop ℕ∞} {y : State × Thrust × ℝ} (hm : y.1.1 ≠ 0) :
    ContDiffAt ℝ n (fun y : State × Thrust × ℝ => field p y.1 y.2.1 y.2.2) y := by
  unfold field rot quatRate cross
  fun_prop (disch := assumption)

/-- One RK4 step is smooth wherever its four stages see a nonzero mass. With `c = h α Γ`, the
stage masses are `m`, `m - c/2`, `m - c/2` and `m - c`. -/
theorem contDiffAt_rk4 (p : Params) {n : WithTop ℕ∞} {q₀ : State × Thrust × ℝ × ℝ}
    (h1 : q₀.1.1 ≠ 0) (h2 : q₀.1.1 - q₀.2.2.2 * (p.α * q₀.2.2.1) / 2 ≠ 0)
    (h4 : q₀.1.1 - q₀.2.2.2 * (p.α * q₀.2.2.1) ≠ 0) :
    ContDiffAt ℝ n (rk4 p) q₀ := by
  have hK1 : ContDiffAt ℝ n (K1 p) q₀ :=
    (contDiffAt_field p (n := n) (y := (q₀.1, q₀.2.1, q₀.2.2.1)) h1).comp
      (f := fun q : State × Thrust × ℝ × ℝ => (q.1, q.2.1, q.2.2.1)) q₀ (by fun_prop)
  have hK2 : ContDiffAt ℝ n (K2 p) q₀ := by
    have hm : (q₀.1 + (q₀.2.2.2 / 2) • K1 p q₀).1 ≠ 0 := by
      convert h2 using 1; simp [K1, field_mass]; ring
    exact (contDiffAt_field p (n := n) hm).comp
      (f := fun q : State × Thrust × ℝ × ℝ => (q.1 + (q.2.2.2 / 2) • K1 p q, q.2.1, q.2.2.1)) q₀
      (by fun_prop)
  have hK3 : ContDiffAt ℝ n (K3 p) q₀ := by
    have hm : (q₀.1 + (q₀.2.2.2 / 2) • K2 p q₀).1 ≠ 0 := by
      convert h2 using 1; simp [K2, field_mass]; ring
    exact (contDiffAt_field p (n := n) hm).comp
      (f := fun q : State × Thrust × ℝ × ℝ => (q.1 + (q.2.2.2 / 2) • K2 p q, q.2.1, q.2.2.1)) q₀
      (by fun_prop)
  have hK4 : ContDiffAt ℝ n (K4 p) q₀ := by
    have hm : (q₀.1 + q₀.2.2.2 • K3 p q₀).1 ≠ 0 := by
      convert h4 using 1; simp [K3, field_mass]; ring
    exact (contDiffAt_field p (n := n) hm).comp
      (f := fun q : State × Thrust × ℝ × ℝ => (q.1 + q.2.2.2 • K3 p q, q.2.1, q.2.2.1)) q₀
      (by fun_prop)
  unfold rk4
  fun_prop

/-- `j` substeps are smooth when the mass is still positive at the end, given `h α Γ ≥ 0`. -/
theorem contDiffAt_substeps (p : Params) {n : WithTop ℕ∞} (j : ℕ) {q₀ : State × Thrust × ℝ × ℝ}
    (hc : 0 ≤ q₀.2.2.2 * (p.α * q₀.2.2.1))
    (hpos : 0 < q₀.1.1 - j * (q₀.2.2.2 * (p.α * q₀.2.2.1))) :
    ContDiffAt ℝ n (substeps p j) q₀ := by
  induction j with
  | zero => exact contDiffAt_fst
  | succ j ih =>
    set c := q₀.2.2.2 * (p.α * q₀.2.2.1)
    have hj : 0 < q₀.1.1 - j * c := by push_cast at hpos; nlinarith
    have hm := substeps_mass p j q₀
    have hrk : ContDiffAt ℝ n (rk4 p) (substeps p j q₀, q₀.2.1, q₀.2.2.1, q₀.2.2.2) := by
      apply contDiffAt_rk4 <;> simp only [hm] <;> push_cast at hpos ⊢ <;> nlinarith
    have hin : ContDiffAt ℝ n
        (fun q : State × Thrust × ℝ × ℝ => (substeps p j q, q.2.1, q.2.2.1, q.2.2.2)) q₀ := by
      have := ih hj
      fun_prop
    exact hrk.comp q₀ hin

/-- One interval, as a function of `(x, u, Γ, s)`. -/
def intervalU (p : Params) (N M : ℕ) (q : State × Thrust × ℝ × ℝ) : State :=
  interval p N M q.1 q.2.1 q.2.2.1 q.2.2.2

theorem contDiffAt_intervalU (p : Params) (N M : ℕ) {n : WithTop ℕ∞}
    {q₀ : State × Thrust × ℝ × ℝ}
    (hc : 0 ≤ q₀.2.2.2 / (N * M) * (p.α * q₀.2.2.1))
    (hpos : 0 < (intervalU p N M q₀).1) :
    ContDiffAt ℝ n (intervalU p N M) q₀ := by
  rw [intervalU, interval_mass] at hpos
  have h := contDiffAt_substeps p (n := n) M
    (q₀ := (q₀.1, q₀.2.1, q₀.2.2.1, q₀.2.2.2 / (N * M))) hc hpos
  exact h.comp q₀ (by fun_prop)

/-- The shooting map is smooth along any trajectory whose node masses stay positive. -/
theorem contDiffAt_traj (p : Params) (M : ℕ) {tof : P → ℝ} (x₀ : State) {n : WithTop ℕ∞}
    (htof : ContDiff ℝ n tof) {z : Dec N Thrust P}
    (hc : ∀ k : Fin N, 0 ≤ tof z.2.2 / (N * M) * (p.α * z.2.1 k))
    (hmass : ∀ k : Fin N, 0 < (traj p M tof x₀ z (k + 1)).1) :
    ∀ k ≤ N, ContDiffAt ℝ n (fun z' => traj p M tof x₀ z' k) z := by
  intro k
  induction k with
  | zero => intro _; exact contDiffAt_const
  | succ k ih =>
    intro hk
    have hkN : k < N := hk
    have heq : (fun z' => traj p M tof x₀ z' (k + 1)) = fun z' : Dec N Thrust P =>
        intervalU p N M (traj p M tof x₀ z' k, z'.1 ⟨k, hkN⟩, z'.2.1 ⟨k, hkN⟩, tof z'.2.2) := by
      funext z'; simp [traj, hkN, intervalU]
    rw [heq]
    have hm := hmass ⟨k, hkN⟩
    simp only [traj, hkN, dite_true] at hm
    have hI := contDiffAt_intervalU p N M (n := n)
      (q₀ := (traj p M tof x₀ z k, z.1 ⟨k, hkN⟩, z.2.1 ⟨k, hkN⟩, tof z.2.2)) (hc ⟨k, hkN⟩) hm
    have hT := ih (Nat.le_of_succ_le hk)
    exact hI.comp (f := fun z' : Dec N Thrust P =>
      (traj p M tof x₀ z' k, z'.1 ⟨k, hkN⟩, z'.2.1 ⟨k, hkN⟩, tof z'.2.2)) z (by fun_prop)

/-! ### The 6-DOF guidance problem as an instance of `LCvx.Problem` -/

/-- Mass along the trajectory: each interval burns `M (s / (N M)) α Γ_k`, whatever the thrust
direction or the rest of the state. -/
lemma traj_mass (p : Params) (M : ℕ) (tof : P → ℝ) (x₀ : State) (z : Dec N Thrust P) (k : ℕ) :
    (traj p M tof x₀ z k).1 = x₀.1 - ∑ j ∈ Finset.range k,
      (if h : j < N then M * (tof z.2.2 / (N * M) * (p.α * z.2.1 ⟨j, h⟩)) else 0) := by
  induction k with
  | zero => simp [traj]
  | succ k ih =>
    rw [Finset.sum_range_succ]
    by_cases hk : k < N
    · simp only [traj, hk, dite_true, interval_mass, ih]; ring
    · simp only [traj, hk, dite_false, ih]; ring

/-- Gimbal constraint: thrust within `δ` of the body x axis (the engine axis). -/
def gimbal (δ : ℝ) : Set (Thrust × ℝ) := {q | Real.cos δ * ‖q.1‖ ≤ q.1 0}

lemma gimbal_smul (δ : ℝ) (q : Thrust × ℝ) (t : ℝ) (ht : 0 < t) (hq : q ∈ gimbal δ) :
    t • q ∈ gimbal δ := by
  simp only [gimbal, Set.mem_ofPred_eq, Prod.smul_fst, norm_smul, Real.norm_eq_abs, abs_of_pos ht,
    PiLp.smul_apply, smul_eq_mul] at hq ⊢
  nlinarith

lemma gimbal_mem_nhds {δ : ℝ} {u : Thrust} (Γ : ℝ) (h : Real.cos δ * ‖u‖ < u 0) :
    gimbal δ ∈ 𝓝 (u, Γ) := by
  have hopen : IsOpen {q : Thrust × ℝ | Real.cos δ * ‖q.1‖ < q.1 0} :=
    isOpen_lt (continuous_const.mul continuous_fst.norm) (by fun_prop)
  exact mem_of_superset (hopen.mem_nhds h) fun q (hq : Real.cos δ * ‖q.1‖ < q.1 0) =>
    show Real.cos δ * ‖q.1‖ ≤ q.1 0 from hq.le

variable {Y : Type*} [NormedAddCommGroup Y] [NormedSpace ℝ Y]

/-- Everything that defines a 6-DOF guidance problem. -/
structure Data (N : ℕ) (P Y : Type*) where
  /-- Vehicle constants. -/
  p : Params
  /-- RK4 substeps per interval. -/
  M : ℕ
  /-- Time of flight as a function of the extra variables (`id` for free final time, a
  constant for fixed final time). -/
  tof : P → ℝ
  /-- Initial state. -/
  x₀ : State
  Tmin : ℝ
  Tmax : ℝ
  /-- Maximum gimbal angle. -/
  δ : ℝ
  /-- Remaining constraints: glide slope, tilt, angular rate, dry mass, time-of-flight bounds. -/
  other : Set (Dec N Thrust P)
  /-- Terminal conditions (and any active path constraints), read off the trajectory. -/
  term : (Fin (N + 1) → State) → Y
  y₀ : Y

/-- The relaxed 6-DOF problem. Cost is `-m_N`, so minimizing it maximizes landed mass. -/
def Data.toProblem (D : Data N P Y) : Problem N Thrust P Y where
  ρ₁ := D.Tmin
  ρ₂ := D.Tmax
  cone := fun _ => gimbal D.δ
  other := D.other
  F := fun z => D.term fun k => traj D.p D.M D.tof D.x₀ z k
  y₀ := D.y₀
  cost := fun z => -(traj D.p D.M D.tof D.x₀ z N).1

/-- Propellant per unit slack: `M (s / (N M)) α`, which is `s α / N` for `N, M ≠ 0`. -/
def Data.κ (D : Data N P Y) (s : ℝ) : ℝ := D.M * (s / (N * D.M)) * D.p.α

lemma Data.cost_eq (D : Data N P Y) (z : Dec N Thrust P) :
    D.toProblem.cost z = -D.x₀.1 + D.κ (D.tof z.2.2) * ∑ j, z.2.1 j := by
  simp only [Data.toProblem, traj_mass, Data.κ, Finset.mul_sum]
  rw [← Fin.sum_univ_eq_sum_range
    (fun j => if h : j < N then (D.M : ℝ) * (D.tof z.2.2 / (N * D.M) * (D.p.α * z.2.1 ⟨j, h⟩))
      else 0)]
  simp only [Fin.is_lt, dite_true, Fin.eta]
  rw [neg_sub, sub_eq_neg_add]
  congr 1
  exact Finset.sum_congr rfl fun j _ => by ring

lemma Data.κ_pos (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0) {s : ℝ}
    (hs : 0 < s) : 0 < D.κ s := by
  unfold Data.κ
  have : (0 : ℝ) < N := by exact_mod_cast Nat.pos_of_ne_zero hN
  have : (0 : ℝ) < D.M := by exact_mod_cast Nat.pos_of_ne_zero hM
  positivity

variable [CompleteSpace Y]

/-- The equality constraint map (terminal conditions of the integrated 6-DOF dynamics) has a
strict derivative at any point whose node masses are positive. -/
theorem Data.hasStrictFDerivAt_F (D : Data N P Y) (hα : 0 ≤ D.p.α) (htof : ContDiff ℝ 1 D.tof)
    (hterm : ContDiff ℝ 1 D.term) {z : Dec N Thrust P} (hs : 0 ≤ D.tof z.2.2)
    (hΓ : ∀ k, 0 ≤ z.2.1 k) (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ z (k + 1)).1) :
    HasStrictFDerivAt D.toProblem.F (fderiv ℝ D.toProblem.F z) z := by
  have hc : ∀ k : Fin N, 0 ≤ D.tof z.2.2 / (N * D.M) * (D.p.α * z.2.1 k) := fun k => by
    have := hΓ k; positivity
  have htraj : ContDiffAt ℝ 1
      (fun z' => fun k : Fin (N + 1) => traj D.p D.M D.tof D.x₀ z' k) z :=
    contDiffAt_pi.2 fun k => contDiffAt_traj D.p D.M D.x₀ htof hc hmass k (Nat.lt_succ_iff.1 k.2)
  exact (hterm.contDiffAt.comp z htraj).hasStrictFDerivAt (by norm_num)

/-- **6-DOF LCvx, fixed time of flight.** Let `z` be a local minimizer of the relaxed 6-DOF
problem, with the path constraints in `other` inactive and the mass positive at every node. If
the thrusts at a set `L` of lossy, gimbal-inactive nodes can steer the terminal conditions in
every direction to first order, then every slack equals `T_min`: the degenerate case where the
time of flight is longer than the vehicle can use. -/
theorem sixDOF_fixed_time (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) (htof : ContDiff ℝ 1 D.tof) (hterm : ContDiff ℝ 1 D.term)
    {z : Dec N Thrust P} (hz : z ∈ D.toProblem.relaxed)
    (hmin : IsLocalMinOn D.toProblem.cost D.toProblem.relaxed z)
    (hother : D.other ∈ 𝓝 z) (hs : 0 < D.tof z.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ z (k + 1)).1)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ Real.cos D.δ * ‖z.1 j‖ < z.1 j 0)
    (hsurj : Function.Surjective (fderiv ℝ D.toProblem.F z ∘L lossyIncl L)) :
    ∀ k, z.2.1 k = D.Tmin := by
  have hΓ : ∀ k, 0 ≤ z.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  refine Problem.slack_eq_lower_of_surjective (π := D.toProblem) hTmin
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hz hmin hother ?_ ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩)
    (D.hasStrictFDerivAt_F hα.le htof hterm hs.le hΓ hmass) hsurj
  · intro u u' Γ p'
    simp only [Data.cost_eq]
  · intro Γ hle hne
    rw [D.cost_eq, D.cost_eq]
    have hlt : ∑ j, Γ j < ∑ j, z.2.1 j := by
      obtain ⟨i, hi⟩ := Function.ne_iff.mp hne
      exact Finset.sum_lt_sum (fun j _ => hle j) ⟨i, Finset.mem_univ _, lt_of_le_of_ne (hle i) hi⟩
    have := D.κ_pos hα hN hM hs
    nlinarith

/-- **6-DOF LCvx, free time of flight** (the problem Szmuk et al. solve). The extra variable is
the time of flight itself, strictly inside its bounds. Then no set of lossy, gimbal-inactive
nodes can steer the terminal conditions in every direction: landing slightly sooner would
otherwise save propellant. No degenerate case remains. -/
theorem sixDOF_free_time (D : Data N ℝ Y) (htof : D.tof = id) (hα : 0 < D.p.α) (hN : N ≠ 0)
    (hM : D.M ≠ 0) (hTmin : 0 < D.Tmin) (hterm : ContDiff ℝ 1 D.term)
    {z : Dec N Thrust ℝ} (hz : z ∈ D.toProblem.relaxed)
    (hmin : IsLocalMinOn D.toProblem.cost D.toProblem.relaxed z)
    (hother : D.other ∈ 𝓝 z) (hs : 0 < z.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ z (k + 1)).1)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ Real.cos D.δ * ‖z.1 j‖ < z.1 j 0) :
    ¬ Function.Surjective (fderiv ℝ D.toProblem.F z ∘L lossyIncl L) := by
  have hΓ : ∀ k, 0 ≤ z.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  have htof' : ContDiff ℝ 1 D.tof := htof ▸ contDiff_id
  have hsum : 0 < ∑ j, z.2.1 j := by
    have : Nonempty (Fin N) := ⟨⟨0, Nat.pos_of_ne_zero hN⟩⟩
    exact Finset.sum_pos (fun j _ => hTmin.trans_le (hz.1 j).2.1) Finset.univ_nonempty
  refine Problem.not_surjective_of_free_param (π := D.toProblem)
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hz hmin hother ?_ (-1) ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩)
    (D.hasStrictFDerivAt_F hα.le htof' hterm (by rw [htof]; exact hs.le) hΓ hmass)
  · intro u u' Γ p'
    simp only [Data.cost_eq]
  · filter_upwards [self_mem_nhdsWithin] with t ht
    have ht' : (0 : ℝ) < t := ht
    rw [D.cost_eq, D.cost_eq, htof]
    have hκ := D.κ_pos hα hN hM ht'
    have e : D.κ (id (z.2.2 + t • (-1 : ℝ))) = D.κ (id z.2.2) - D.κ t := by
      simp only [Data.κ, id, smul_eq_mul]; ring
    rw [e]
    nlinarith [mul_pos hκ hsum]

/-! ### Converged SCvx iterates

The theorems above assume a local minimum of the nonlinear relaxed problem. A converged PTR
iterate is instead a point that solves its own convex subproblem. The results below apply to
that point directly, with the same derivative `fderiv ℝ D.toProblem.F zr` of the true 6-DOF
terminal map (the solver uses the exact Jacobian of its RK4 map, which is this derivative). -/

/-- The convex problem PTR solves around `zr`, without its trust-region penalty and virtual
control: the same thrust and gimbal constraints, the terminal map linearized at `zr`, the fuel
cost linearized at `zr`, and the subproblem's own path constraints `otherLin`. -/
def Data.linProblem (D : Data N P Y) (zr : Dec N Thrust P) (otherLin : Set (Dec N Thrust P)) :
    Problem N Thrust P Y where
  ρ₁ := D.Tmin
  ρ₂ := D.Tmax
  cone := fun _ => gimbal D.δ
  other := otherLin
  F := fun z => D.toProblem.F zr + fderiv ℝ D.toProblem.F zr (z - zr)
  y₀ := D.y₀
  cost := fun z => -D.x₀.1 + D.κ (D.tof zr.2.2) * ∑ j, z.2.1 j
    + D.κ (D.tof z.2.2 - D.tof zr.2.2) * ∑ j, zr.2.1 j

/-- The subproblem's cost is the first-order expansion of the true cost `-m_N`: the two differ
by a product of two first-order changes (in time of flight and in total slack). -/
lemma Data.cost_sub_linProblem_cost (D : Data N P Y) (zr z : Dec N Thrust P)
    (otherLin : Set (Dec N Thrust P)) :
    D.toProblem.cost z - (D.linProblem zr otherLin).cost z =
      D.κ (D.tof z.2.2 - D.tof zr.2.2) * (∑ j, z.2.1 j - ∑ j, zr.2.1 j) := by
  rw [D.cost_eq]
  simp only [Data.linProblem, Data.κ]
  ring

lemma Data.mem_linProblem_relaxed (D : Data N P Y) {zr : Dec N Thrust P}
    {otherLin : Set (Dec N Thrust P)} (hz : zr ∈ D.toProblem.relaxed) (ho : zr ∈ otherLin) :
    zr ∈ (D.linProblem zr otherLin).relaxed :=
  ⟨hz.1, ho, by
    change D.toProblem.F zr + fderiv ℝ D.toProblem.F zr (zr - zr) = D.y₀
    rw [sub_self, map_zero, add_zero]
    exact hz.2.2⟩

/-- **Converged PTR iterate, free time of flight.** `zr` is feasible for the relaxed 6-DOF
problem, and the solver's last subproblem (variables `W`, convex feasible set `K`, convex cost
`f`, trust-region penalty `h` flat at `w = e zr`) returned its own reference. `e` embeds the
linearized relaxed problem into the subproblem with matching cost, and the subproblem's path
constraints are inactive at `zr`. Then no set of lossy, gimbal-inactive nodes can steer the
terminal conditions in every direction, measured with the true 6-DOF derivative. -/
theorem sixDOF_ptr_free_time (D : Data N ℝ Y) (htof : D.tof = id) (hα : 0 < D.p.α)
    (hN : N ≠ 0) (hM : D.M ≠ 0) (hTmin : 0 < D.Tmin)
    {zr : Dec N Thrust ℝ} (hz : zr ∈ D.toProblem.relaxed)
    {otherLin : Set (Dec N Thrust ℝ)} (hother : otherLin ∈ 𝓝 zr)
    {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W] {K : Set W} {f h : W → ℝ} {w : W}
    (e : Dec N Thrust ℝ → W) (hK : Convex ℝ K) (hf : ConvexOn ℝ K f)
    (hh : HasFDerivAt h (0 : W →L[ℝ] ℝ) w) (hw : w ∈ K) (hfix : IsMinOn (f + h) K w)
    (he : MapsTo e (D.linProblem zr otherLin).relaxed K) (hez : e zr = w)
    (hfe : ∀ z ∈ (D.linProblem zr otherLin).relaxed, f (e z) = (D.linProblem zr otherLin).cost z)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖zr.1 j‖ < zr.2.1 j ∧ Real.cos D.δ * ‖zr.1 j‖ < zr.1 j 0) :
    ¬ Function.Surjective (fderiv ℝ D.toProblem.F zr ∘L lossyIncl L) := by
  set π := D.linProblem zr otherLin with hπ
  have hzl : zr ∈ π.relaxed := D.mem_linProblem_relaxed hz (mem_of_mem_nhds hother)
  have hmin := (π.isMinOn_of_fixed_point e hK hf hh hw hfix he hez hfe hzl).isLocalMinOn
  have hsum : 0 < ∑ j, zr.2.1 j := by
    have : Nonempty (Fin N) := ⟨⟨0, Nat.pos_of_ne_zero hN⟩⟩
    exact Finset.sum_pos (fun j _ => hTmin.trans_le (hz.1 j).2.1) Finset.univ_nonempty
  refine Problem.not_surjective_of_free_param (π := π)
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hzl hmin hother (fun _ _ _ _ => rfl) (-1) ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩)
    (hasStrictFDerivAt_affine _ _ _ _)
  filter_upwards [self_mem_nhdsWithin] with t ht
  have ht' : (0 : ℝ) < t := ht
  have hκ := D.κ_pos hα hN hM ht'
  have e1 : D.κ (D.tof (zr.2.2 + t • (-1 : ℝ)) - D.tof zr.2.2) = -D.κ t := by
    simp only [htof, id, Data.κ, smul_eq_mul]; ring
  have e0 : D.κ (D.tof zr.2.2 - D.tof zr.2.2) = 0 := by simp [Data.κ]
  simp only [hπ, Data.linProblem, e1, e0]
  nlinarith [mul_pos hκ hsum]

/-- **Converged PTR iterate, fixed time of flight.** Same setting with the time of flight held
fixed. If the thrusts at a set of lossy, gimbal-inactive nodes can steer the terminal conditions
in every direction, every slack is at `T_min`. -/
theorem sixDOF_ptr_fixed_time (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) {zr : Dec N Thrust P} (hz : zr ∈ D.toProblem.relaxed)
    (hs : 0 < D.tof zr.2.2) {otherLin : Set (Dec N Thrust P)} (hother : otherLin ∈ 𝓝 zr)
    {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W] {K : Set W} {f h : W → ℝ} {w : W}
    (e : Dec N Thrust P → W) (hK : Convex ℝ K) (hf : ConvexOn ℝ K f)
    (hh : HasFDerivAt h (0 : W →L[ℝ] ℝ) w) (hw : w ∈ K) (hfix : IsMinOn (f + h) K w)
    (he : MapsTo e (D.linProblem zr otherLin).relaxed K) (hez : e zr = w)
    (hfe : ∀ z ∈ (D.linProblem zr otherLin).relaxed, f (e z) = (D.linProblem zr otherLin).cost z)
    (L : Finset (Fin N)) (hL : ∀ j ∈ L, ‖zr.1 j‖ < zr.2.1 j ∧ Real.cos D.δ * ‖zr.1 j‖ < zr.1 j 0)
    (hsurj : Function.Surjective (fderiv ℝ D.toProblem.F zr ∘L lossyIncl L)) :
    ∀ k, zr.2.1 k = D.Tmin := by
  set π := D.linProblem zr otherLin with hπ
  have hzl : zr ∈ π.relaxed := D.mem_linProblem_relaxed hz (mem_of_mem_nhds hother)
  have hmin := (π.isMinOn_of_fixed_point e hK hf hh hw hfix he hez hfe hzl).isLocalMinOn
  refine Problem.slack_eq_lower_of_surjective (π := π) hTmin
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hzl hmin hother (fun _ _ _ _ => rfl) ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩)
    (hasStrictFDerivAt_affine _ _ _ _) hsurj
  intro Γ hle hne
  have hlt : ∑ j, Γ j < ∑ j, zr.2.1 j := by
    obtain ⟨i, hi⟩ := Function.ne_iff.mp hne
    exact Finset.sum_lt_sum (fun j _ => hle j) ⟨i, Finset.mem_univ _, lt_of_le_of_ne (hle i) hi⟩
  have hκ := D.κ_pos hα hN hM hs
  simp only [hπ, Data.linProblem, sub_self]
  nlinarith

/-! ### Active path constraints

Path constraints (glide slope, tilt, angular rate, dry mass) restrict the state at each node,
modelled as `traj z k ∈ path k`. The dynamics are causal: the state at node `k` depends only on
controls at earlier nodes. So perturbing only nodes at or after `m` leaves every path constraint
up to node `m` exactly as it was, and those may be active. Later ones must have slack, or be
moved into `term` as equalities. -/

/-- The state at node `k` depends only on the thrusts and slacks at earlier nodes and on the
time-of-flight variable. -/
lemma traj_eq_of_agree (p : Params) (M : ℕ) (tof : P → ℝ) (x₀ : State) {z z' : Dec N Thrust P}
    (hp : z'.2.2 = z.2.2) (k : ℕ)
    (hagree : ∀ j : Fin N, (j : ℕ) < k → z'.1 j = z.1 j ∧ z'.2.1 j = z.2.1 j) :
    traj p M tof x₀ z' k = traj p M tof x₀ z k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    have ih' := ih fun j hj => hagree j (Nat.lt_succ_of_lt hj)
    by_cases hk : k < N
    · obtain ⟨hu, hΓ⟩ := hagree ⟨k, hk⟩ (Nat.lt_succ_self k)
      simp only [traj, hk, dite_true, ih', hu, hΓ, hp]
    · simp only [traj, hk, dite_false, ih']

/-- The trial points used in the proofs move only the lossy nodes `L` and node `i`. If those are
all at or after `m`, every earlier node and the time-of-flight variable stay put. -/
lemma trial_agree {zr : Dec N Thrust P} {L : Finset (Fin N)} {i : Fin N} {m : ℕ}
    (hLm : ∀ j ∈ L, m ≤ (j : ℕ)) (him : m ≤ (i : ℕ)) (w : Fin N → Thrust) (t : ℝ) :
    (zr + lossyIncl L w + t • Problem.scaleDir zr {i} 0).2.2 = zr.2.2 ∧
    ∀ j : Fin N, (j : ℕ) < m → (zr + lossyIncl L w + t • Problem.scaleDir zr {i} 0).1 j = zr.1 j ∧
      (zr + lossyIncl L w + t • Problem.scaleDir zr {i} 0).2.1 j = zr.2.1 j := by
  refine ⟨by rw [Problem.trial_p, smul_zero, add_zero], fun j hj => ?_⟩
  have hjL : j ∉ L := fun h => absurd (hLm j h) (not_le.mpr hj)
  have hji : j ∉ ({i} : Finset (Fin N)) := by
    simp only [Finset.mem_singleton]; rintro rfl; exact absurd him (not_le.mpr hj)
  exact ⟨by rw [Problem.trial_u]; simp [hjL, hji], by rw [Problem.trial_Γ]; simp [hji]⟩

/-- **6-DOF LCvx with active path constraints.** Path constraints may be active at nodes up to
`m` and must have slack after `m` (or be moved into `term`). Take lossy, gimbal-inactive nodes
`L` and a node `i`, all at or after `m`. If the thrusts at `L` can steer the terminal conditions
in every direction, the slack at `i` is `T_min`. The time of flight is not perturbed, so this
holds with free or fixed time of flight. -/
theorem sixDOF_tail (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) (htof : ContDiff ℝ 1 D.tof) (hterm : ContDiff ℝ 1 D.term)
    {z : Dec N Thrust P} (hz : z ∈ D.toProblem.relaxed)
    (hmin : IsLocalMinOn D.toProblem.cost D.toProblem.relaxed z) (hs : 0 < D.tof z.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ z (k + 1)).1)
    (path : ℕ → Set State) (m : ℕ)
    (hother : ∀ z' : Dec N Thrust P, z'.2.2 = z.2.2 →
      (∀ k ≤ N, traj D.p D.M D.tof D.x₀ z' k ∈ path k) → z' ∈ D.other)
    (hfeas : ∀ k ≤ N, traj D.p D.M D.tof D.x₀ z k ∈ path k)
    (hslack : ∀ k ≤ N, m < k → path k ∈ 𝓝 (traj D.p D.M D.tof D.x₀ z k))
    (L : Finset (Fin N)) (hLm : ∀ j ∈ L, m ≤ (j : ℕ))
    (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ Real.cos D.δ * ‖z.1 j‖ < z.1 j 0)
    (hsurj : Function.Surjective (fderiv ℝ D.toProblem.F z ∘L lossyIncl L))
    (i : Fin N) (him : m ≤ (i : ℕ)) :
    z.2.1 i = D.Tmin := by
  have hΓ : ∀ k, 0 ≤ z.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  have hc : ∀ k : Fin N, 0 ≤ D.tof z.2.2 / (N * D.M) * (D.p.α * z.2.1 k) := fun k => by
    have := hΓ k; positivity
  refine Problem.slack_eq_lower_at (π := D.toProblem) hTmin
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hz hmin
    (fun u u' Γ p' => by simp only [Data.cost_eq]) ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩) i ?_
    (D.hasStrictFDerivAt_F hα.le htof hterm hs.le hΓ hmass) hsurj
  · intro Γ hle hne
    rw [D.cost_eq, D.cost_eq]
    have hlt : ∑ j, Γ j < ∑ j, z.2.1 j := by
      obtain ⟨l, hl⟩ := Function.ne_iff.mp hne
      exact Finset.sum_lt_sum (fun j _ => hle j) ⟨l, Finset.mem_univ _, lt_of_le_of_ne (hle l) hl⟩
    have := D.κ_pos hα hN hM hs
    nlinarith
  · set T : (Fin N → Thrust) × ℝ → Dec N Thrust P :=
      fun q => z + lossyIncl L q.1 + q.2 • Problem.scaleDir z {i} 0 with hT
    have hTc : Continuous T :=
      (continuous_const.add ((lossyIncl L).continuous.comp continuous_fst)).add
        (continuous_snd.smul continuous_const)
    have hT0 : T 0 = z := by ext k <;> simp [hT]
    have hk : ∀ k ∈ Finset.range (N + 1), ∀ᶠ q in 𝓝 (0 : (Fin N → Thrust) × ℝ),
        traj D.p D.M D.tof D.x₀ (T q) k ∈ path k := by
      intro k hk
      have hkN : k ≤ N := Nat.lt_succ_iff.mp (Finset.mem_range.mp hk)
      by_cases hkm : k ≤ m
      · refine Eventually.of_forall fun q => ?_
        obtain ⟨hp, hag⟩ := trial_agree (zr := z) hLm him q.1 q.2
        rw [traj_eq_of_agree D.p D.M D.tof D.x₀ hp k
          (fun j hj => hag j (lt_of_lt_of_le hj hkm))]
        exact hfeas k hkN
      · have hcont : ContinuousAt (fun q => traj D.p D.M D.tof D.x₀ (T q) k) 0 :=
          ((contDiffAt_traj D.p D.M D.x₀ htof hc hmass k hkN).continuousAt).comp_of_eq
            hTc.continuousAt hT0
        refine hcont.eventually_mem ?_
        show path k ∈ 𝓝 (traj D.p D.M D.tof D.x₀ (T 0) k)
        rw [hT0]
        exact hslack k hkN (not_le.mp hkm)
    filter_upwards [(Filter.eventually_all_finset (Finset.range (N + 1))).2 hk] with q hq _
    exact hother _ (trial_agree (zr := z) hLm him q.1 q.2).1
      fun k hk => hq k (Finset.mem_range.2 (Nat.lt_succ_of_le hk))

/-- The trajectory of the dynamics linearized at `zr`: what the solver's subproblem propagates. -/
def Data.linTraj (D : Data N P Y) (zr z : Dec N Thrust P) (k : ℕ) : State :=
  traj D.p D.M D.tof D.x₀ zr k + fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr (z - zr)

/-- The linearized dynamics are causal too: a change that leaves the time-of-flight variable and
every node before `k` alone does not move the linearized state at node `k`. -/
lemma fderiv_traj_eq_zero (D : Data N P Y) {zr : Dec N Thrust P} (k : ℕ)
    (hdiff : DifferentiableAt ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr)
    {v : Dec N Thrust P} (hv2 : v.2.2 = 0)
    (hv : ∀ j : Fin N, (j : ℕ) < k → v.1 j = 0 ∧ v.2.1 j = 0) :
    fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr v = 0 := by
  have hconst : (fun t : ℝ => traj D.p D.M D.tof D.x₀ (zr + t • v) k) =
      fun _ => traj D.p D.M D.tof D.x₀ zr k := by
    funext t
    refine traj_eq_of_agree D.p D.M D.tof D.x₀ (by simp [hv2]) k fun j hj => ?_
    obtain ⟨h1, h2⟩ := hv j hj
    simp [h1, h2]
  have hline : HasDerivAt (fun t : ℝ => zr + t • v) v 0 := by
    simpa using HasDerivAt.const_add zr ((hasDerivAt_id (0 : ℝ)).smul_const v)
  have h' : HasFDerivAt (fun z' => traj D.p D.M D.tof D.x₀ z' k)
      (fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr) (zr + (0 : ℝ) • v) := by
    simpa using hdiff.hasFDerivAt
  have h0 := h'.comp_hasDerivAt (0 : ℝ) hline
  have h1 : HasDerivAt (fun t : ℝ => traj D.p D.M D.tof D.x₀ (zr + t • v) k)
      (fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr v) 0 := h0
  rw [hconst] at h1
  exact h1.unique (hasDerivAt_const (0 : ℝ) (traj D.p D.M D.tof D.x₀ zr k))

/-- **Converged PTR iterate with active path constraints.** The subproblem's path constraints
act on the linearized trajectory, may be active at nodes up to `m`, and must have slack after
`m`. Then the conclusion of `sixDOF_tail` holds at the converged iterate, with the true 6-DOF
derivative. -/
theorem sixDOF_ptr_tail (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) (htof : ContDiff ℝ 1 D.tof)
    {zr : Dec N Thrust P} (hz : zr ∈ D.toProblem.relaxed) (hs : 0 < D.tof zr.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ zr (k + 1)).1)
    (path : ℕ → Set State) (m : ℕ) {otherLin : Set (Dec N Thrust P)}
    (hother : ∀ z' : Dec N Thrust P, z'.2.2 = zr.2.2 →
      (∀ k ≤ N, D.linTraj zr z' k ∈ path k) → z' ∈ otherLin)
    (hfeas : ∀ k ≤ N, traj D.p D.M D.tof D.x₀ zr k ∈ path k)
    (hslack : ∀ k ≤ N, m < k → path k ∈ 𝓝 (traj D.p D.M D.tof D.x₀ zr k))
    {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W] {K : Set W} {f h : W → ℝ} {w : W}
    (e : Dec N Thrust P → W) (hK : Convex ℝ K) (hf : ConvexOn ℝ K f)
    (hh : HasFDerivAt h (0 : W →L[ℝ] ℝ) w) (hw : w ∈ K) (hfix : IsMinOn (f + h) K w)
    (he : MapsTo e (D.linProblem zr otherLin).relaxed K) (hez : e zr = w)
    (hfe : ∀ z ∈ (D.linProblem zr otherLin).relaxed, f (e z) = (D.linProblem zr otherLin).cost z)
    (L : Finset (Fin N)) (hLm : ∀ j ∈ L, m ≤ (j : ℕ))
    (hL : ∀ j ∈ L, ‖zr.1 j‖ < zr.2.1 j ∧ Real.cos D.δ * ‖zr.1 j‖ < zr.1 j 0)
    (hsurj : Function.Surjective (fderiv ℝ D.toProblem.F zr ∘L lossyIncl L))
    (i : Fin N) (him : m ≤ (i : ℕ)) :
    zr.2.1 i = D.Tmin := by
  have hΓ : ∀ k, 0 ≤ zr.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  have hc : ∀ k : Fin N, 0 ≤ D.tof zr.2.2 / (N * D.M) * (D.p.α * zr.2.1 k) := fun k => by
    have := hΓ k; positivity
  have hdiff : ∀ k ≤ N, DifferentiableAt ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr :=
    fun k hk => (contDiffAt_traj D.p D.M D.x₀ htof hc hmass k hk).differentiableAt (by norm_num)
  set π := D.linProblem zr otherLin with hπ
  have hzo : zr ∈ otherLin := hother zr rfl fun k hk => by
    simpa [Data.linTraj] using hfeas k hk
  have hzl : zr ∈ π.relaxed := D.mem_linProblem_relaxed hz hzo
  have hmin := (π.isMinOn_of_fixed_point e hK hf hh hw hfix he hez hfe hzl).isLocalMinOn
  refine Problem.slack_eq_lower_at (π := π) hTmin
    (fun _ q t ht hq => gimbal_smul D.δ q t ht hq) hzl hmin (fun _ _ _ _ => rfl) ?_ L
    (fun j hj => ⟨(hL j hj).1, gimbal_mem_nhds _ (hL j hj).2⟩) i ?_
    (hasStrictFDerivAt_affine _ _ _ _) hsurj
  · intro Γ hle hne
    have hlt : ∑ j, Γ j < ∑ j, zr.2.1 j := by
      obtain ⟨l, hl⟩ := Function.ne_iff.mp hne
      exact Finset.sum_lt_sum (fun j _ => hle j) ⟨l, Finset.mem_univ _, lt_of_le_of_ne (hle l) hl⟩
    have hκ := D.κ_pos hα hN hM hs
    simp only [hπ, Data.linProblem, sub_self]
    nlinarith
  · set T : (Fin N → Thrust) × ℝ → Dec N Thrust P :=
      fun q => zr + lossyIncl L q.1 + q.2 • Problem.scaleDir zr {i} 0 with hT
    have hTc : Continuous T :=
      (continuous_const.add ((lossyIncl L).continuous.comp continuous_fst)).add
        (continuous_snd.smul continuous_const)
    have hT0 : T 0 = zr := by ext k <;> simp [hT]
    have hk : ∀ k ∈ Finset.range (N + 1), ∀ᶠ q in 𝓝 (0 : (Fin N → Thrust) × ℝ),
        D.linTraj zr (T q) k ∈ path k := by
      intro k hk
      have hkN : k ≤ N := Nat.lt_succ_iff.mp (Finset.mem_range.mp hk)
      by_cases hkm : k ≤ m
      · refine Eventually.of_forall fun q => ?_
        obtain ⟨hp, hag⟩ := trial_agree (zr := zr) hLm him q.1 q.2
        have hzero : fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr (T q - zr) = 0 := by
          refine fderiv_traj_eq_zero D k (hdiff k hkN)
            (show (T q).2.2 - zr.2.2 = 0 by rw [show (T q).2.2 = zr.2.2 from hp, sub_self])
            fun j hj => ?_
          obtain ⟨h1, h2⟩ := hag j (lt_of_lt_of_le hj hkm)
          simp only [Prod.fst_sub, Prod.snd_sub, Pi.sub_apply]
          exact ⟨by rw [h1, sub_self], by rw [h2, sub_self]⟩
        simpa [Data.linTraj, hzero] using hfeas k hkN
      · have hcont : ContinuousAt (fun q => D.linTraj zr (T q) k) 0 := by
          unfold Data.linTraj
          exact (continuous_const.add ((fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k)
            zr).continuous.comp (hTc.sub continuous_const))).continuousAt
        refine hcont.eventually_mem ?_
        show path k ∈ 𝓝 (D.linTraj zr (T 0) k)
        rw [hT0]
        simpa [Data.linTraj] using hslack k hkN (not_le.mp hkm)
    filter_upwards [(Filter.eventually_all_finset (Finset.range (N + 1))).2 hk] with q hq _
    exact hother _ (trial_agree (zr := zr) hLm him q.1 q.2).1
      fun k hk => hq k (Finset.mem_range.2 (Nat.lt_succ_of_le hk))

/-! ### Holding active constraints as equalities

An inequality constraint that is active at the optimum can be held at its value by moving it into
the equality map `F`. The feasible set only shrinks and still contains the optimum, so a local
minimum stays a local minimum (`IsLocalMinOn.mono`), and the constraint no longer needs slack.
The price is that the lossy thrusts must also steer its value. This covers a lossy node sitting on
the gimbal limit (hold `gimFun` there) and active path constraints anywhere after the perturbed
nodes. -/

/-- The gimbal constraint as a function: `gimbal δ` is `gimFun δ u ≤ 0`. -/
def gimFun (δ : ℝ) (u : Thrust) : ℝ := Real.cos δ * ‖u‖ - u 0

lemma mem_gimbal_iff (δ : ℝ) (q : Thrust × ℝ) : q ∈ gimbal δ ↔ gimFun δ q.1 ≤ 0 := by
  simp only [gimbal, gimFun, Set.mem_ofPred_eq, sub_nonpos]

lemma contDiffAt_gimFun (δ : ℝ) {n : WithTop ℕ∞} {u : Thrust} (hu : u ≠ 0) :
    ContDiffAt ℝ n (gimFun δ) u := by
  unfold gimFun
  exact (contDiffAt_const.mul (contDiffAt_norm ℝ hu)).sub (by fun_prop)

/-- **Folding, general form.** `π0` has the 6-DOF node constraints (`gimbal δ` at every node).
With the time-of-flight variable held at `z.2.2`, its other constraints are `pc c ≤ 0`, and `pc c`
depends only on the nodes before `node c` (causality). Hold as equalities the constraints in
`Act` and the gimbal limit at the nodes in `G` by appending them to `F`. Then path constraints
may be active at nodes up to `m`, those in `Act` may be active anywhere, and a lossy node may sit
on the gimbal limit if it is in `G`. If the lossy thrusts at `L` steer the augmented map in every
direction, the slack at every node `i ≥ m` is at its lower bound. -/
theorem fold_core (π0 : Problem N Thrust P Y) (δ : ℝ) (hcone0 : ∀ k, π0.cone k = gimbal δ)
    (hρ₁ : 0 ≤ π0.ρ₁) {z : Dec N Thrust P} (hz : z ∈ π0.relaxed)
    (hmin : IsLocalMinOn π0.cost π0.relaxed z)
    (hcost_u : ∀ u u' Γ p, π0.cost (u, Γ, p) = π0.cost (u', Γ, p))
    (hcost_Γ : ∀ Γ, Γ ≤ z.2.1 → Γ ≠ z.2.1 → π0.cost (z.1, Γ, z.2.2) < π0.cost z)
    {C : ℕ} (pc : Fin C → Dec N Thrust P → ℝ) (node : Fin C → ℕ)
    (hother : ∀ z' : Dec N Thrust P, z'.2.2 = z.2.2 → (∀ c, pc c z' ≤ 0) → z' ∈ π0.other)
    (hfeas : ∀ c, pc c z ≤ 0)
    (hcausal : ∀ c (z' : Dec N Thrust P), z'.2.2 = z.2.2 →
      (∀ j : Fin N, (j : ℕ) < node c → z'.1 j = z.1 j ∧ z'.2.1 j = z.2.1 j) → pc c z' = pc c z)
    (hcont : ∀ c, ContinuousAt (pc c) z)
    (m : ℕ) (Act : Finset (Fin C)) (hslack : ∀ c, c ∉ Act → m < node c → pc c z < 0)
    (G : Finset (Fin N)) (L : Finset (Fin N)) (hLm : ∀ j ∈ L, m ≤ (j : ℕ))
    (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ (j ∈ G ∨ Real.cos δ * ‖z.1 j‖ < z.1 j 0))
    {A' : Dec N Thrust P →L[ℝ] Y × ((Act → ℝ) × (G → ℝ))}
    (hF : HasStrictFDerivAt (fun z' : Dec N Thrust P =>
      (π0.F z', fun c : Act => pc c z', fun j : G => gimFun δ (z'.1 j))) A' z)
    (hsurj : Function.Surjective (A' ∘L lossyIncl L)) (i : Fin N) (him : m ≤ (i : ℕ)) :
    z.2.1 i = π0.ρ₁ := by
  set Fa : Dec N Thrust P → Y × ((Act → ℝ) × (G → ℝ)) :=
    fun z' => (π0.F z', fun c : Act => pc c z', fun j : G => gimFun δ (z'.1 j)) with hFa
  let π' : Problem N Thrust P (Y × ((Act → ℝ) × (G → ℝ))) :=
    { ρ₁ := π0.ρ₁, ρ₂ := π0.ρ₂
      cone := fun k => if k ∈ G then univ else gimbal δ
      other := {z' | z'.2.2 = z.2.2 ∧ ∀ c, c ∉ Act → pc c z' ≤ 0}
      F := Fa, y₀ := Fa z, cost := π0.cost }
  -- The folded problem's feasible set sits inside the original one and contains `z`.
  have hsub : π'.relaxed ⊆ π0.relaxed := by
    rintro z' ⟨hn, ⟨hp, ho⟩, hFz⟩
    have h1 : π0.F z' = π0.F z := congrArg Prod.fst hFz
    have h2 : ∀ c : Act, pc c z' = pc c z := fun c => congrFun (congrArg (fun x => x.2.1) hFz) c
    have h3 : ∀ j : G, gimFun δ (z'.1 j) = gimFun δ (z.1 j) :=
      fun j => congrFun (congrArg (fun x => x.2.2) hFz) j
    refine ⟨fun k => ?_, hother z' hp fun c => ?_, h1.trans hz.2.2⟩
    · obtain ⟨a, b, c, d⟩ := hn k
      refine ⟨a, b, c, ?_⟩
      rw [hcone0 k]
      by_cases hk : k ∈ G
      · have hzk := (hz.1 k).2.2.2
        rw [hcone0 k, mem_gimbal_iff] at hzk
        rw [mem_gimbal_iff]
        exact (h3 ⟨k, hk⟩).symm ▸ hzk
      · simpa [π', hk] using d
    · by_cases hc : c ∈ Act
      · rw [h2 ⟨c, hc⟩]; exact hfeas c
      · exact ho c hc
  have hz' : z ∈ π'.relaxed := by
    refine ⟨fun k => ?_, ⟨rfl, fun c _ => hfeas c⟩, rfl⟩
    obtain ⟨a, b, c, d⟩ := hz.1 k
    refine ⟨a, b, c, ?_⟩
    by_cases hk : k ∈ G
    · simp [π', hk]
    · simpa [π', hk, hcone0 k] using d
  have hmin' : IsLocalMinOn π'.cost π'.relaxed z := hmin.mono hsub
  have hcone' : ∀ k (q : Thrust × ℝ) (t : ℝ), 0 < t → q ∈ π'.cone k → t • q ∈ π'.cone k := by
    intro k q t ht hq
    by_cases hk : k ∈ G
    · simp [π', hk]
    · simp only [π', hk, ↓reduceIte] at hq ⊢
      exact gimbal_smul δ q t ht hq
  have hL' : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ π'.cone j ∈ 𝓝 (z.1 j, z.2.1 j) := by
    intro j hj
    refine ⟨(hL j hj).1, ?_⟩
    by_cases hjG : j ∈ G
    · simp [π', hjG]
    · simpa [π', hjG] using gimbal_mem_nhds (z.2.1 j) ((hL j hj).2.resolve_left hjG)
  -- Trial points keep the constraints that are not folded.
  have hother' : ∀ᶠ q : (Fin N → Thrust) × ℝ in 𝓝 0, 0 < q.2 →
      z + lossyIncl L q.1 + q.2 • Problem.scaleDir z {i} 0 ∈ π'.other := by
    set T : (Fin N → Thrust) × ℝ → Dec N Thrust P :=
      fun q => z + lossyIncl L q.1 + q.2 • Problem.scaleDir z {i} 0 with hT
    have hTc : Continuous T :=
      (continuous_const.add ((lossyIncl L).continuous.comp continuous_fst)).add
        (continuous_snd.smul continuous_const)
    have hT0 : T 0 = z := by ext k <;> simp [hT]
    have hc : ∀ c ∈ (Finset.univ : Finset (Fin C)), ∀ᶠ q in 𝓝 (0 : (Fin N → Thrust) × ℝ),
        c ∉ Act → pc c (T q) ≤ 0 := by
      intro c _
      by_cases hcm : node c ≤ m
      · refine Eventually.of_forall fun q _ => ?_
        obtain ⟨hp, hag⟩ := trial_agree (zr := z) hLm him q.1 q.2
        rw [hcausal c (T q) hp fun j hj => hag j (lt_of_lt_of_le hj hcm)]
        exact hfeas c
      · by_cases hcA : c ∈ Act
        · exact Eventually.of_forall fun q h => absurd hcA h
        · have hcq : ContinuousAt (fun q => pc c (T q)) 0 :=
            (hcont c).comp_of_eq hTc.continuousAt hT0
          have hneg : pc c (T 0) < 0 := by rw [hT0]; exact hslack c hcA (not_le.mp hcm)
          exact (hcq.eventually_lt continuousAt_const hneg).mono fun q hq _ => hq.le
    filter_upwards [(Filter.eventually_all_finset Finset.univ).2 hc] with q hq _
    exact ⟨(trial_agree (zr := z) hLm him q.1 q.2).1, fun c hcA => hq c (Finset.mem_univ c) hcA⟩
  exact Problem.slack_eq_lower_at (π := π') hρ₁ hcone' hz' hmin' hcost_u hcost_Γ L hL' i
    hother' hF hsurj

/-- **6-DOF LCvx with folded constraints, local minimum.** Path constraints are
`g c (state at node c) ≤ 0` with `g c` smooth. Those in `Act` and the gimbal limit at the nodes
in `G` are held as equalities. If the lossy thrusts at `L` (all at or after `m`, each either
gimbal-inactive or in `G`) can steer the terminal conditions together with those held values,
every slack from node `m` on is `T_min`. -/
theorem sixDOF_fold (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) (htof : ContDiff ℝ 1 D.tof) (hterm : ContDiff ℝ 1 D.term)
    {z : Dec N Thrust P} (hz : z ∈ D.toProblem.relaxed)
    (hmin : IsLocalMinOn D.toProblem.cost D.toProblem.relaxed z) (hs : 0 < D.tof z.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ z (k + 1)).1)
    {C : ℕ} (g : Fin C → State → ℝ) (hg : ∀ c, ContDiff ℝ 1 (g c)) (node : Fin C → ℕ)
    (hnode : ∀ c, node c ≤ N)
    (hother : ∀ z' : Dec N Thrust P, z'.2.2 = z.2.2 →
      (∀ c, g c (traj D.p D.M D.tof D.x₀ z' (node c)) ≤ 0) → z' ∈ D.other)
    (hfeas : ∀ c, g c (traj D.p D.M D.tof D.x₀ z (node c)) ≤ 0)
    (m : ℕ) (Act : Finset (Fin C))
    (hslack : ∀ c, c ∉ Act → m < node c → g c (traj D.p D.M D.tof D.x₀ z (node c)) < 0)
    (G : Finset (Fin N)) (hG : ∀ j ∈ G, z.1 j ≠ 0)
    (L : Finset (Fin N)) (hLm : ∀ j ∈ L, m ≤ (j : ℕ))
    (hL : ∀ j ∈ L, ‖z.1 j‖ < z.2.1 j ∧ (j ∈ G ∨ Real.cos D.δ * ‖z.1 j‖ < z.1 j 0))
    (hsurj : Function.Surjective (fderiv ℝ (fun z' : Dec N Thrust P =>
      (D.toProblem.F z', fun c : Act => g c (traj D.p D.M D.tof D.x₀ z' (node c)),
        fun j : G => gimFun D.δ (z'.1 j))) z ∘L lossyIncl L))
    (i : Fin N) (him : m ≤ (i : ℕ)) :
    z.2.1 i = D.Tmin := by
  have hΓ : ∀ k, 0 ≤ z.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  have hc : ∀ k : Fin N, 0 ≤ D.tof z.2.2 / (N * D.M) * (D.p.α * z.2.1 k) := fun k => by
    have := hΓ k; positivity
  have hT : ∀ k ≤ N, ContDiffAt ℝ 1 (fun z' => traj D.p D.M D.tof D.x₀ z' k) z :=
    fun k hk => contDiffAt_traj D.p D.M D.x₀ htof hc hmass k hk
  have hF0 : ContDiffAt ℝ 1 D.toProblem.F z :=
    hterm.contDiffAt.comp z (contDiffAt_pi.2 fun k => hT k (Nat.lt_succ_iff.1 k.2))
  have hFa : ContDiffAt ℝ 1 (fun z' : Dec N Thrust P =>
      (D.toProblem.F z', fun c : Act => g c (traj D.p D.M D.tof D.x₀ z' (node c)),
        fun j : G => gimFun D.δ (z'.1 j))) z :=
    hF0.prodMk ((contDiffAt_pi.2 fun c : Act => (hg c).contDiffAt.comp z (hT _ (hnode c))).prodMk
      (contDiffAt_pi.2 fun j : G => (contDiffAt_gimFun D.δ (hG j j.2)).comp z
        (f := fun z' : Dec N Thrust P => z'.1 j) (by fun_prop)))
  refine fold_core D.toProblem D.δ (fun _ => rfl) hTmin hz hmin
    (fun u u' Γ p' => by simp only [Data.cost_eq]) ?_
    (fun c z' => g c (traj D.p D.M D.tof D.x₀ z' (node c))) node hother hfeas
    (fun c z' hp hag => by
      simp only [traj_eq_of_agree D.p D.M D.tof D.x₀ hp (node c) hag])
    (fun c => ((hg c).continuous.continuousAt).comp (hT _ (hnode c)).continuousAt)
    m Act hslack G L hLm hL (hFa.hasStrictFDerivAt (by norm_num)) hsurj i him
  intro Γ hle hne
  rw [D.cost_eq, D.cost_eq]
  have hlt : ∑ j, Γ j < ∑ j, z.2.1 j := by
    obtain ⟨l, hl⟩ := Function.ne_iff.mp hne
    exact Finset.sum_lt_sum (fun j _ => hle j) ⟨l, Finset.mem_univ _, lt_of_le_of_ne (hle l) hl⟩
  have := D.κ_pos hα hN hM hs
  nlinarith

/-- **6-DOF LCvx with folded constraints, converged PTR iterate.** Same as `sixDOF_fold`, at a
converged PTR iterate whose subproblem imposes the path constraints on the linearized
trajectory. The steering condition is the same as in `sixDOF_fold`: it uses the derivative of the
true 6-DOF dynamics, which is also the derivative of the subproblem's linearized constraints. -/
theorem sixDOF_ptr_fold (D : Data N P Y) (hα : 0 < D.p.α) (hN : N ≠ 0) (hM : D.M ≠ 0)
    (hTmin : 0 ≤ D.Tmin) (htof : ContDiff ℝ 1 D.tof) (hterm : ContDiff ℝ 1 D.term)
    {zr : Dec N Thrust P} (hz : zr ∈ D.toProblem.relaxed) (hs : 0 < D.tof zr.2.2)
    (hmass : ∀ k : Fin N, 0 < (traj D.p D.M D.tof D.x₀ zr (k + 1)).1)
    {C : ℕ} (g : Fin C → State → ℝ) (hg : ∀ c, ContDiff ℝ 1 (g c)) (node : Fin C → ℕ)
    (hnode : ∀ c, node c ≤ N) {otherLin : Set (Dec N Thrust P)}
    (hother : ∀ z' : Dec N Thrust P, z'.2.2 = zr.2.2 →
      (∀ c, g c (D.linTraj zr z' (node c)) ≤ 0) → z' ∈ otherLin)
    (hfeas : ∀ c, g c (traj D.p D.M D.tof D.x₀ zr (node c)) ≤ 0)
    (m : ℕ) (Act : Finset (Fin C))
    (hslack : ∀ c, c ∉ Act → m < node c → g c (traj D.p D.M D.tof D.x₀ zr (node c)) < 0)
    (G : Finset (Fin N)) (hG : ∀ j ∈ G, zr.1 j ≠ 0)
    {W : Type*} [NormedAddCommGroup W] [NormedSpace ℝ W] {K : Set W} {f h : W → ℝ} {w : W}
    (e : Dec N Thrust P → W) (hK : Convex ℝ K) (hf : ConvexOn ℝ K f)
    (hh : HasFDerivAt h (0 : W →L[ℝ] ℝ) w) (hw : w ∈ K) (hfix : IsMinOn (f + h) K w)
    (he : MapsTo e (D.linProblem zr otherLin).relaxed K) (hez : e zr = w)
    (hfe : ∀ z ∈ (D.linProblem zr otherLin).relaxed, f (e z) = (D.linProblem zr otherLin).cost z)
    (L : Finset (Fin N)) (hLm : ∀ j ∈ L, m ≤ (j : ℕ))
    (hL : ∀ j ∈ L, ‖zr.1 j‖ < zr.2.1 j ∧ (j ∈ G ∨ Real.cos D.δ * ‖zr.1 j‖ < zr.1 j 0))
    (hsurj : Function.Surjective (fderiv ℝ (fun z' : Dec N Thrust P =>
      (D.toProblem.F z', fun c : Act => g c (traj D.p D.M D.tof D.x₀ z' (node c)),
        fun j : G => gimFun D.δ (z'.1 j))) zr ∘L lossyIncl L))
    (i : Fin N) (him : m ≤ (i : ℕ)) :
    zr.2.1 i = D.Tmin := by
  have hΓ : ∀ k, 0 ≤ zr.2.1 k := fun k => (norm_nonneg _).trans (hz.1 k).1
  have hc : ∀ k : Fin N, 0 ≤ D.tof zr.2.2 / (N * D.M) * (D.p.α * zr.2.1 k) := fun k => by
    have := hΓ k; positivity
  have hT : ∀ k ≤ N, ContDiffAt ℝ 1 (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr :=
    fun k hk => contDiffAt_traj D.p D.M D.x₀ htof hc hmass k hk
  have hdT : ∀ k ≤ N, DifferentiableAt ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' k) zr :=
    fun k hk => (hT k hk).differentiableAt (by norm_num)
  have hF0 : ContDiffAt ℝ 1 D.toProblem.F zr :=
    hterm.contDiffAt.comp zr (contDiffAt_pi.2 fun k => hT k (Nat.lt_succ_iff.1 k.2))
  have hlin0 : ∀ k, D.linTraj zr zr k = traj D.p D.M D.tof D.x₀ zr k := fun k => by
    simp [Data.linTraj]
  set π := D.linProblem zr otherLin with hπ
  have hzo : zr ∈ otherLin := hother zr rfl fun c => by rw [hlin0]; exact hfeas c
  have hzl : zr ∈ π.relaxed := D.mem_linProblem_relaxed hz hzo
  have hmin := (π.isMinOn_of_fixed_point e hK hf hh hw hfix he hez hfe hzl).isLocalMinOn
  -- The subproblem's augmented constraint map has the derivative of the true one.
  set Fn : Dec N Thrust P → Y × ((Act → ℝ) × (G → ℝ)) := fun z' =>
    (D.toProblem.F z', fun c : Act => g c (traj D.p D.M D.tof D.x₀ z' (node c)),
      fun j : G => gimFun D.δ (z'.1 j)) with hFn
  set Fl : Dec N Thrust P → Y × ((Act → ℝ) × (G → ℝ)) := fun z' =>
    (π.F z', fun c : Act => g c (D.linTraj zr z' (node c)),
      fun j : G => gimFun D.δ (z'.1 j)) with hFl
  have hgim : ∀ j : G, HasFDerivAt (fun z' : Dec N Thrust P => gimFun D.δ (z'.1 j))
      ((fderiv ℝ (gimFun D.δ) (zr.1 j)).comp ((ContinuousLinearMap.proj (j : Fin N)).comp
        (ContinuousLinearMap.fst ℝ (Fin N → Thrust) ((Fin N → ℝ) × P)))) zr := fun j => by
    have hg1 : HasFDerivAt (gimFun D.δ) (fderiv ℝ (gimFun D.δ) (zr.1 j)) (zr.1 j) :=
      ((contDiffAt_gimFun D.δ (n := 1) (hG j j.2)).differentiableAt (by norm_num)).hasFDerivAt
    have hp : HasFDerivAt (fun z' : Dec N Thrust P => z'.1 j)
        ((ContinuousLinearMap.proj (j : Fin N)).comp
          (ContinuousLinearMap.fst ℝ (Fin N → Thrust) ((Fin N → ℝ) × P))) zr :=
      ((ContinuousLinearMap.proj (j : Fin N)).comp
        (ContinuousLinearMap.fst ℝ (Fin N → Thrust) ((Fin N → ℝ) × P))).hasFDerivAt
    exact hg1.comp zr hp
  have hgk : ∀ c : Act, HasFDerivAt (g c) (fderiv ℝ (g c) (traj D.p D.M D.tof D.x₀ zr (node c)))
      (traj D.p D.M D.tof D.x₀ zr (node c)) := fun c =>
    ((hg c).differentiable (by norm_num) _).hasFDerivAt
  have hFnD : HasFDerivAt Fn _ zr := (hF0.differentiableAt (by norm_num)).hasFDerivAt.prodMk
    ((hasFDerivAt_pi.2 fun c : Act => (hgk c).comp zr (hdT _ (hnode c)).hasFDerivAt).prodMk
      (hasFDerivAt_pi.2 hgim))
  have hFlD : HasFDerivAt Fl (fderiv ℝ Fn zr) zr := by
    rw [hFnD.fderiv]
    refine (hasStrictFDerivAt_affine _ _ _ _).hasFDerivAt.prodMk
      ((hasFDerivAt_pi.2 fun c : Act => ?_).prodMk (hasFDerivAt_pi.2 hgim))
    have hlin : HasFDerivAt (fun z' => D.linTraj zr z' (node c))
        (fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' (node c)) zr) zr :=
      (hasStrictFDerivAt_affine _ _ _ _).hasFDerivAt
    have hgc : HasFDerivAt (g c) (fderiv ℝ (g c) (traj D.p D.M D.tof D.x₀ zr (node c)))
        (D.linTraj zr zr (node c)) := by
      rw [hlin0]; exact hgk c
    exact hgc.comp zr hlin
  have hFlC : ContDiffAt ℝ 1 Fl zr := by
    have haff : ∀ k, ContDiff ℝ 1 (fun z' => D.linTraj zr z' k) := fun k => by
      unfold Data.linTraj
      exact contDiff_const.add ((fderiv ℝ _ zr).contDiff.comp (contDiff_id.sub contDiff_const))
    refine ContDiffAt.prodMk ?_ (ContDiffAt.prodMk ?_ ?_)
    · exact (contDiff_const.add ((fderiv ℝ D.toProblem.F zr).contDiff.comp
        (contDiff_id.sub contDiff_const))).contDiffAt
    · exact contDiffAt_pi.2 fun c : Act => ((hg c).comp (haff _)).contDiffAt
    · exact contDiffAt_pi.2 fun j : G => (contDiffAt_gimFun D.δ (hG j j.2)).comp zr
        (f := fun z' : Dec N Thrust P => z'.1 j) (by fun_prop)
  have hFl : HasStrictFDerivAt Fl (fderiv ℝ Fn zr) zr := by
    have := hFlC.hasStrictFDerivAt (by norm_num)
    rwa [hFlD.fderiv] at this
  refine fold_core π D.δ (fun _ => rfl) hTmin hzl hmin (fun _ _ _ _ => rfl) ?_
    (fun c z' => g c (D.linTraj zr z' (node c))) node hother (fun c => by rw [hlin0]; exact hfeas c)
    (fun c z' hp hag => ?_)
    (fun c => ((hg c).continuous.comp (by
      unfold Data.linTraj
      exact continuous_const.add ((fderiv ℝ _ zr).continuous.comp
        (continuous_id.sub continuous_const)))).continuousAt)
    m Act (fun c hc hm => by rw [hlin0]; exact hslack c hc hm) G L hLm hL hFl hsurj i him
  · intro Γ hle hne
    have hlt : ∑ j, Γ j < ∑ j, zr.2.1 j := by
      obtain ⟨l, hl⟩ := Function.ne_iff.mp hne
      exact Finset.sum_lt_sum (fun j _ => hle j) ⟨l, Finset.mem_univ _, lt_of_le_of_ne (hle l) hl⟩
    have hκ := D.κ_pos hα hN hM hs
    simp only [hπ, Data.linProblem, sub_self]
    nlinarith
  · have hzero : fderiv ℝ (fun z' => traj D.p D.M D.tof D.x₀ z' (node c)) zr (z' - zr) = 0 := by
      refine fderiv_traj_eq_zero D (node c) (hdT _ (hnode c))
        (show z'.2.2 - zr.2.2 = 0 by rw [hp, sub_self]) fun j hj => ?_
      obtain ⟨h1, h2⟩ := hag j hj
      simp only [Prod.fst_sub, Prod.snd_sub, Pi.sub_apply]
      exact ⟨by rw [h1, sub_self], by rw [h2, sub_self]⟩
    simp only [Data.linTraj, hzero, sub_self, map_zero]

end

end LCvx.SixDOF
