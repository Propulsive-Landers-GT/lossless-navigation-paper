import LcvxObstruction.TVC.CentreOfPercussion
import LcvxObstruction.TVC.Certificate
import LcvxObstruction.TVC.Pointwise
import LcvxObstruction.TVC.Model
import LcvxObstruction.FreeTimeBStar

/-! `#print axioms` for the main theorems of the `TVC/` files (expected: only
`[propext, Classical.choice, Quot.sound]`). Not imported from the root; run with
`lake env lean LcvxObstruction/TVC/Axioms.lean`. -/

#print axioms LcvxObstruction.TVC.cop_identity
#print axioms LcvxObstruction.TVC.cop_identity_E3
#print axioms LcvxObstruction.TVC.cop_identity_roll
#print axioms LcvxObstruction.TVC.euler_roll_const
#print axioms LcvxObstruction.TVC.convex_tvcSet_iff
#print axioms LcvxObstruction.TVC.sprocedure_finsler
#print axioms LcvxObstruction.TVC.sprocedure_finsler_sum
#print axioms LcvxObstruction.TVC.gain_le_of_certificate
#print axioms LcvxObstruction.TVC.tvc1_skeleton
#print axioms LcvxObstruction.TVC.rotPi2_fixed_iff
#print axioms LcvxObstruction.TVC.tvc1_main
#print axioms LcvxObstruction.TVC.late_majorant
#print axioms LcvxObstruction.TVC.late_pi_ge
#print axioms LcvxObstruction.TVC.speed_sq_le
#print axioms LcvxObstruction.TVC.sq_add_le_split
#print axioms LcvxObstruction.TVC.sq_sub_pos_ge_split
#print axioms LcvxObstruction.TVC.relaxed_contains_ordinary

-- B* with mass depletion (`DiveBrakeMass.lean`, `DiveBrakeMassModel.lean`)
#print axioms LcvxObstruction.PhiMax_not_mem_WSet
#print axioms LcvxObstruction.not_convex_constrainedLandingSet_of_max
#print axioms LcvxObstruction.dive_identity
#print axioms LcvxObstruction.exists_sigma_compare
#print axioms LcvxObstruction.exists_max_phiFace_mass
#print axioms LcvxObstruction.not_convex_constrainedLandingSet_mass
#print axioms LcvxObstruction.no_lossless_relaxation_constrained_5dof_mass
#print axioms LcvxObstruction.no_losslessFor_relaxation_constrained_5dof_mass
#print axioms LcvxObstruction.no_lossless_relaxation_constrained_upright_5dof_mass
#print axioms LcvxObstruction.no_lossless_relaxation_constrained_6dof_mass
#print axioms LcvxObstruction.no_lossless_relaxation_constrained_upright_6dof_mass

-- B*, free final time on a compact window (`FreeTimeBStar.lean`)
#print axioms LcvxObstruction.not_convex_iUnion_of_max
#print axioms LcvxObstruction.not_convex_iUnion_constrainedLandingSet_box
#print axioms LcvxObstruction.not_convex_iUnion_constrainedLandingSet_mass
#print axioms LcvxObstruction.no_lossless_relaxation_freeTime_5dof
#print axioms LcvxObstruction.no_lossless_relaxation_freeTime_5dof_mass

-- concrete pure-TVC model (`TVC/Model.lean`)
#print axioms LcvxObstruction.TVC.ordinarySet_subset_relaxedSet
#print axioms LcvxObstruction.TVC.tvcLandingSet_rot
#print axioms LcvxObstruction.TVC.rotPiE2_fixed_iff
#print axioms LcvxObstruction.TVC.tvc_lambda_identity
#print axioms LcvxObstruction.TVC.tvc1_model
#print axioms LcvxObstruction.TVC.ellE_eq_Wz
#print axioms LcvxObstruction.TVC.tvc1_model_ctrl
#print axioms LcvxObstruction.constrainedLandingSet_mass_nonempty
