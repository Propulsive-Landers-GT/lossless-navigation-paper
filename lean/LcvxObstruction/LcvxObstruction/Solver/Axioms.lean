import LcvxObstruction.Solver.Gimbal
import LcvxObstruction.Solver.Vectors
import LcvxObstruction.Solver.Gyro
import LcvxObstruction.Solver.Relaxation

/-! `#print axioms` for every solver-claim theorem (N1–N7). Expected for each:
`[propext, Classical.choice, Quot.sound]`. -/

-- N1
#print axioms LcvxSolver.gimbal_box_angles
#print axioms LcvxSolver.axial_floor
-- N2
#print axioms LcvxSolver.hasDerivAt_theta
#print axioms LcvxSolver.theta_rate_bound
#print axioms LcvxSolver.hasDerivAt_phi
#print axioms LcvxSolver.phi_rate_heuristic_false
#print axioms LcvxSolver.phi_rate_bound_standalone
#print axioms LcvxSolver.phi_rate_bound_pair
#print axioms LcvxSolver.gimbal_rate_pair
#print axioms LcvxSolver.foh_gimbal_rate
-- N3
#print axioms LcvxSolver.hasDerivAt_norm_of_ne
#print axioms LcvxSolver.throttle_rate_le
#print axioms LcvxSolver.norm_le_sum_abs
#print axioms LcvxSolver.throttle_slew_foh
#print axioms LcvxSolver.throttle_slew_increment
-- N4
#print axioms LcvxSolver.chord_bound
-- N5
#print axioms LcvxSolver.dir_accel_bound
#print axioms LcvxSolver.dir_accel_bound_calculus
-- N6
#print axioms LcvxSolver.gyro_roll_component
#print axioms LcvxSolver.gyro_vanish
#print axioms LcvxSolver.euler_axisymmetric
#print axioms LcvxSolver.euler_axisymmetric_integral
-- N7
#print axioms LcvxSolver.relaxation_lower_bound
#print axioms LcvxSolver.relaxation_lower_bound_real
#print axioms LcvxSolver.freeTime_lower_bound
#print axioms LcvxSolver.value3_le_value6
#print axioms LcvxSolver.value3_le_value6_freeTime
#print axioms LcvxSolver.constrainedLandingSet6_subset_landingSet3
