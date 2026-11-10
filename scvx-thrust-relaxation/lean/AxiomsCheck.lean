import LCvx

/-!
Run `lake env lean AxiomsCheck.lean` after `lake build`. Every line should report only
`[propext, Classical.choice, Quot.sound]`, Lean's standard axioms. A proof that used `sorry`
would list `sorryAx`.
-/

-- Core and general theorems
#print axioms LCvx.not_isLocalMinOn_of_surjective
#print axioms LCvx.Problem.slack_eq_lower_at
#print axioms LCvx.Problem.slack_eq_lower_of_surjective
#print axioms LCvx.Problem.not_surjective_of_free_param
#print axioms LCvx.Problem.not_surjective_of_nondegenerate
#print axioms LCvx.Problem.card_lossy_lt
#print axioms LCvx.Problem.isLocalMinOn_original
#print axioms LCvx.Problem.isMinOn_original
-- Converged SCvx iterates
#print axioms LCvx.isMinOn_of_isMinOn_add
#print axioms LCvx.Problem.isMinOn_of_fixed_point
-- 6-DOF
#print axioms LCvx.SixDOF.sixDOF_free_time
#print axioms LCvx.SixDOF.sixDOF_fixed_time
#print axioms LCvx.SixDOF.sixDOF_ptr_free_time
#print axioms LCvx.SixDOF.sixDOF_ptr_fixed_time
#print axioms LCvx.SixDOF.Data.cost_sub_linProblem_cost
#print axioms LCvx.SixDOF.traj_eq_of_agree
#print axioms LCvx.SixDOF.fderiv_traj_eq_zero
#print axioms LCvx.SixDOF.sixDOF_tail
#print axioms LCvx.SixDOF.sixDOF_ptr_tail
#print axioms LCvx.SixDOF.fold_core
#print axioms LCvx.SixDOF.sixDOF_fold
#print axioms LCvx.SixDOF.sixDOF_ptr_fold
-- Examples: hypotheses satisfiable, and each of steering and slack is necessary
#print axioms LCvx.Example.toy_slack_eq_lower
#print axioms LCvx.Example.toy_original_empty
#print axioms LCvx.Example.toy2_sharp
#print axioms LCvx.Example.toy3_sharp
