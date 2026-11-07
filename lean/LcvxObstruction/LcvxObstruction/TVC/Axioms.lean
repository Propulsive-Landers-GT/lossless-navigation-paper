import LcvxObstruction.TVC.CentreOfPercussion
import LcvxObstruction.TVC.Certificate
import LcvxObstruction.TVC.Pointwise

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
