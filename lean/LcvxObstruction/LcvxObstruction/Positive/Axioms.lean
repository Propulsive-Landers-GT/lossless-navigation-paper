import LcvxObstruction.Positive.Cap
import LcvxObstruction.Positive.Primer
import LcvxObstruction.Positive.PMP
import LcvxObstruction.Positive.Discrete
import LcvxObstruction.Positive.Bilinear
import LcvxObstruction.Positive.TVC
import LcvxObstruction.Positive.Convexity

/-!
# Axiom audit for the positive-side formalization

Every main theorem should depend only on `propext`, `Classical.choice`, `Quot.sound`.
PMP and Aumann enter only as explicit hypotheses (`PMPConclusion`, `AumannInstance`).
-/

open LcvxPositive

-- Tier 1 (pointwise, C-G / H / C-3 / U / S / J / L8 / X)
#print axioms normal_of_max_of_norm_lt
#print axioms eq_neg_smul_of_normal_halfspace
#print axioms norm_eq_or_antiRay_of_isMaxOn_cap
#print axioms isMaxOn_cap_unique
#print axioms isMaxOn_cap_of_antiRay
#print axioms isMaxOn_cap_of_antiRay_boundary
#print axioms isMaxOn_slice_of_isMaxOn_joint
#print axioms original_feasible_of_lossless
#print axioms extremePoints_cap
#print axioms C3_headline
-- Tier 2 (primer geometry, C-D1, ND)
#print axioms primer_zero_subsingleton
#print axioms degenerate_subset_of_dependent
#print axioms degenerate_subset_of_independent
#print axioms volume_degenerate_eq_zero_of_ND
#print axioms x_div_one_add_sq_sq_le
-- Tier 3 (C-S / C-D2 under PMPConclusion)
#print axioms PMPConclusion.neg_lamV_eq
#print axioms PMPConclusion.lossless_ae_off_degenerate
#print axioms PMPConclusion.lossless_ae_of_null_degenerate
#print axioms PMPConclusion.lossless_ae_of_ND
#print axioms PMPConclusion.min_throttle_of_primer_zero
#print axioms PMPConclusion.lossy_subset_degenerate_minThrottle
-- Discrete (C-K1, C-K2, C-E(a))
#print axioms discrete_lossless_nodewise
#print axioms zoh_r_eq
#print axioms zoh_pairing
#print axioms exchange_min_throttle
#print axioms purification_count
#print axioms purification_three
-- P22
#print axioms bilinear_restriction
#print axioms convex_ccpSet
-- TVC (Lemma 8.1, C-6)
#print axioms torque_balance_iff
#print axioms throttle_interval
#print axioms convex_tvcSet
#print axioms convex_feasData_M3b
-- C-W(1) / C-F under AumannInstance
#print axioms relaxed_subset_original
#print axioms convex_origFeas
