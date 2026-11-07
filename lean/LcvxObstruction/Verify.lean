/-
Verify.lean: one-command check of the formal results cited in the paper.

  lake env lean Verify.lean

1. Prints the statements of the headline theorems (so you can read exactly what is proved).
2. For every Lean declaration cited in the paper (126 names), checks that it exists and that its
   proof depends only on Lean's three standard axioms: propext, Classical.choice, Quot.sound.
   Any `sorry` would show up here as the axiom `sorryAx`; any custom axiom would also be reported.
The command fails with an error if any declaration is missing or uses another axiom.
-/
import LcvxObstruction
open Lean Elab Command

/-! ## Headline statements -/
#check @LcvxObstruction.gtpl_no_lossless_upright_6dof_mass
#check @LcvxObstruction.gtpl_no_lossless_freeTime_mass
#check @LcvxObstruction.no_lossless_relaxation_constrained_5dof
#check @LcvxObstruction.no_lossless_relaxation_constrained_upright_6dof
#check @LcvxObstruction.not_isLossless_of_not_convex
#print LcvxObstruction.UniformConvexRelaxation
#print LcvxObstruction.UniformConvexRelaxation.IsLossless

#print axioms LcvxObstruction.gtpl_no_lossless_upright_6dof_mass

/-! ## Axiom audit of every cited declaration -/
def headlineNames : List Name := [
  `LcvxObstruction.gtpl_no_lossless_upright_6dof_mass,
  `LcvxObstruction.gtpl_no_lossless_freeTime_mass,
  `LcvxObstruction.no_lossless_relaxation_constrained_5dof,
  `LcvxObstruction.no_lossless_relaxation_constrained_upright_5dof,
  `LcvxObstruction.no_lossless_relaxation_constrained_6dof,
  `LcvxObstruction.no_lossless_relaxation_constrained_upright_6dof,
  `LcvxObstruction.no_lossless_relaxation_constrained_upright_6dof_mass,
  `LcvxObstruction.not_isLossless_of_not_convex]

def citedNames : List Name := headlineNames ++ [
  `LcvxObstruction.AccMass,
  `LcvxObstruction.Attitude6Admissible.toM1,
  `LcvxObstruction.Slice.CostRelaxation.aOpt,
  `LcvxObstruction.Slice.CostRelaxation.aOpt_finset,
  `LcvxObstruction.Slice.CostRelaxation.mixing,
  `LcvxObstruction.Slice.dent,
  `LcvxObstruction.Slice.instL_norm_ge,
  `LcvxObstruction.Slice.lemmaS,
  `LcvxObstruction.Slice.master_inequality,
  `LcvxObstruction.Slice.master_inequality_fixed,
  `LcvxObstruction.Slice.no_valueLossless_of_strict,
  `LcvxObstruction.Slice.periodic_wirtinger,
  `LcvxObstruction.Slice.theoremD_hard_landing,
  `LcvxObstruction.Slice.value_le_convexCombination,
  `LcvxObstruction.Slice.wirtinger_lipschitz,
  `LcvxObstruction.Slice.wirtinger_scalar,
  `LcvxObstruction.StateLinearRelaxation,
  `LcvxObstruction.StateLinearRelaxation.convexHull_subset,
  `LcvxObstruction.StateLinearRelaxation.lossy_of_gap,
  `LcvxObstruction.TVC.convex_tvcSet_iff,
  `LcvxObstruction.TVC.cop_identity_E3,
  `LcvxObstruction.TVC.cop_identity_roll,
  `LcvxObstruction.TVC.tvc1_main,
  `LcvxObstruction.TVC.tvc1_model,
  `LcvxObstruction.TVC.tvc1_skeleton,
  `LcvxObstruction.UniformConvexRelaxation,
  `LcvxObstruction.UniformConvexRelaxation.IsLossless,
  `LcvxObstruction.UniformConvexRelaxation.IsLossless.convex_affine_image,
  `LcvxObstruction.UniformConvexRelaxation.IsLosslessFor,
  `LcvxObstruction.UniformConvexRelaxation.IsLosslessFor.isLossless,
  `LcvxObstruction.VStar_not_mem_WSet,
  `LcvxObstruction.accMass_spec,
  `LcvxObstruction.constrainedLandingSet_mass_nonempty,
  `LcvxObstruction.constrainedLandingSet_nonempty,
  `LcvxObstruction.convex_reachSet_of_convex_landingSet,
  `LcvxObstruction.convex_superset_gap,
  `LcvxObstruction.exists_max_phiFace_mass,
  `LcvxObstruction.exists_switchTime,
  `LcvxObstruction.inner_triangle,
  `LcvxObstruction.inner_triangle_eq_lateral,
  `LcvxObstruction.landingSet_dist_ge,
  `LcvxObstruction.landingSet_dist_ge_mass,
  `LcvxObstruction.landingSet_nonempty,
  `LcvxObstruction.lateral_eq_of_inner_ge,
  `LcvxObstruction.lift_admissible,
  `LcvxObstruction.midpoint_not_mem_closure_landingSet,
  `LcvxObstruction.minError_lossy,
  `LcvxObstruction.no_losslessFor_relaxation_5dof,
  `LcvxObstruction.no_losslessFor_relaxation_constrained_5dof,
  `LcvxObstruction.no_losslessFor_relaxation_constrained_5dof_mass,
  `LcvxObstruction.no_lossless_relaxation_5dof,
  `LcvxObstruction.no_lossless_relaxation_5dof_box,
  `LcvxObstruction.no_lossless_relaxation_5dof_lower,
  `LcvxObstruction.no_lossless_relaxation_5dof_mass,
  `LcvxObstruction.no_lossless_relaxation_constrained_5dof_mass,
  `LcvxObstruction.no_lossless_relaxation_constrained_6dof_mass,
  `LcvxObstruction.no_lossless_relaxation_constrained_upright_5dof_mass,
  `LcvxObstruction.no_lossless_relaxation_freeTime_5dof,
  `LcvxObstruction.no_lossless_relaxation_freeTime_5dof_mass,
  `LcvxObstruction.not_convex_constrainedLandingSet,
  `LcvxObstruction.not_convex_constrainedLandingSet6,
  `LcvxObstruction.not_convex_constrainedLandingSet6Up,
  `LcvxObstruction.not_convex_constrainedLandingSetUp,
  `LcvxObstruction.not_convex_constrainedLandingSet_mass,
  `LcvxObstruction.not_convex_landingSet,
  `LcvxObstruction.not_convex_landingSet6,
  `LcvxObstruction.not_convex_reachSet,
  `LcvxObstruction.not_isLosslessFor_of_not_convex,
  `LcvxObstruction.not_lineSearch_lossless,
  `LcvxObstruction.not_lineSearch_lossless_of_symmetry,
  `LcvxObstruction.position_eq_integral_velocity,
  `LcvxObstruction.snd_image_landingSet,
  `LcvxObstruction.symmetric_supply,
  `LcvxObstruction.theoremA,
  `LcvxObstruction.witness_admissible_upright,
  `LcvxObstruction.witness_mem_glideSlope,
  `LcvxPositive.AumannInstance,
  `LcvxPositive.C3_headline,
  `LcvxPositive.PMPConclusion,
  `LcvxPositive.PMPConclusion.lossless_ae_of_ND,
  `LcvxPositive.PMPConclusion.lossless_ae_off_degenerate,
  `LcvxPositive.PMPConclusion.lossy_subset_degenerate_minThrottle,
  `LcvxPositive.PMPConclusion.min_throttle_of_antiRay,
  `LcvxPositive.cap_subset_closure_convexHull_sCap,
  `LcvxPositive.convex_feasData_M3b,
  `LcvxPositive.convex_origFeas,
  `LcvxPositive.convex_tvcSet,
  `LcvxPositive.discrete_lossless_nodewise,
  `LcvxPositive.extremePoints_cap,
  `LcvxPositive.gimbal_bound_iff_cot,
  `LcvxPositive.isMaxOn_cap_unique,
  `LcvxPositive.norm_eq_or_antiRay_of_isMaxOn_cap,
  `LcvxPositive.normal_of_max_of_norm_lt,
  `LcvxPositive.origFeas_eq_relFeas,
  `LcvxPositive.original_subset_relaxed,
  `LcvxPositive.purification_count,
  `LcvxPositive.purification_three,
  `LcvxPositive.relaxed_subset_original,
  `LcvxPositive.throttle_interval,
  `LcvxPositive.torque_balance_iff,
  `LcvxPositive.volume_degenerate_eq_zero_of_ND,
  `LcvxPositive.zoh_pairing,
  `LcvxSolver.axial_floor,
  `LcvxSolver.chord_bound,
  `LcvxSolver.dir_accel_bound_calculus,
  `LcvxSolver.euler_axisymmetric,
  `LcvxSolver.euler_axisymmetric_integral,
  `LcvxSolver.foh_gimbal_rate,
  `LcvxSolver.gimbal_box_angles,
  `LcvxSolver.gimbal_rate_pair,
  `LcvxSolver.gyro_vanish,
  `LcvxSolver.phi_rate_bound_standalone,
  `LcvxSolver.phi_rate_heuristic_false,
  `LcvxSolver.relaxation_lower_bound,
  `LcvxSolver.theta_rate_bound,
  `LcvxSolver.throttle_slew_foh,
  `LcvxSolver.value3_le_value6,
  `LcvxSolver.value3_le_value6_freeTime]

def standardAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

elab "#audit_cited" : command => do
  let env ← getEnv
  let mut bad := 0
  for n in citedNames do
    unless env.contains n do
      logError m!"missing declaration: {n}"
      bad := bad + 1
      continue
    let axs ← liftCoreM (collectAxioms n)
    let extra := axs.filter (fun a => !standardAxioms.contains a)
    unless extra.isEmpty do
      logError m!"{n} depends on non-standard axioms {extra}"
      bad := bad + 1
  if bad == 0 then
    logInfo m!"PASS: all {citedNames.length} cited declarations exist and depend only on propext, Classical.choice, Quot.sound."

#audit_cited
