import LcvxObstruction.Slice.AOpt
import LcvxObstruction.Slice.LemmaS

/-! Axiom audit for the slice files (expected: `propext`, `Classical.choice`, `Quot.sound`). -/

open LcvxObstruction LcvxObstruction.Slice

#print axioms Slice.CostRelaxation.aOpt
#print axioms Slice.CostRelaxation.aOpt_finset
#print axioms Slice.value_le_convexCombination
#print axioms Slice.no_valueLossless_of_strict
#print axioms StateLinearRelaxation.lossy_of_gap
#print axioms periodic_wirtinger
#print axioms wirtinger_scalar
#print axioms wirtinger_lipschitz
#print axioms master_inequality
#print axioms master_inequality_fixed
#print axioms dent
#print axioms dent_fixed
#print axioms instL_norm_ge
#print axioms lemmaS
#print axioms theoremD_hard_landing
