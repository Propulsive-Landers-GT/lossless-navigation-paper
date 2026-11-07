import numpy as np, cvxpy as cp
from vcore import *
P = Prob(16, 4.0, 0.4, readout="r"); M = P.midpoint_M()
prob,Z,Qp = build_sdp(P); Qp.value=M
for tol in [1e-7,1e-8,1e-9,1e-10]:
    prob.solve(solver="CLARABEL", tol_gap_abs=tol, tol_gap_rel=tol, tol_feas=tol, max_iter=500)
    print(tol, prob.status, repr(prob.value), prob.solver_stats.num_iters)
for st in [True, False]:
  try:
    prob.solve(solver="CLARABEL", tol_gap_abs=1e-10, tol_gap_rel=1e-10, tol_feas=1e-10, max_iter=500, static_regularization_constant=1e-9 if st else 1e-8, equilibrate_enable=st)
    print(st, prob.status, repr(prob.value))
  except Exception as e: print(e)
