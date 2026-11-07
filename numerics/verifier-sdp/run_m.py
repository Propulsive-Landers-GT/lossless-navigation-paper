"""[verifier-sdp] Part 4: the SDP certifies that the Theorem-B midpoint M is unreachable, and the
state-linear relaxation (same lifted feasible set, cost = ||readout(first moments) - q||^2) does not.
Decomposes the SDP value at q = M into  ||Gamma x* - M||^2  (readout bias) + variance term."""
import os, json, warnings
warnings.filterwarnings("ignore")
import numpy as np
import cvxpy as cp
from vcore import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def state_linear_value(P, Q):
    built = build_sdp(P)
    prob, Z, Qp = built
    n = P.n
    X = Z[:n, n:]
    gF = P.gamma[P.free]
    yfix = sum(np.outer(P.gamma[k], EZ) for k in P.fixed)
    obj = 0
    for l in range(P.p):
        Y = gF[:, l] @ X + yfix[l]
        obj = obj + P.mu[l] * cp.sum_squares(Y - Q[l])
    pr = cp.Problem(cp.Minimize(obj), prob.constraints)
    pr.solve(solver="CLARABEL", tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9)
    return float(pr.value), pr.status


if __name__ == "__main__":
    rows = []
    rng = np.random.default_rng(5)
    for N in (8, 16, 32, 48):
        for wtf in (0.4, 1.2, 3.0, 5.5):
            for readout in ("r", "rv"):
                P = Prob(N, 1.0, wtf, readout=readout)
                M = P.midpoint_M()
                rc = solve_sdp(P, M)
                rs = solve_sdp(P, M, "SCS", tight=(N <= 16))
                d = sdp_diag(P, rc["Z"])
                X = d["X"]
                gF = P.gamma[P.free]
                yfix = sum(np.outer(P.gamma[k], EZ) for k in P.fixed)
                Yx = gF.T @ X + yfix
                bias = float(np.sum(P.mu[:, None] * (Yx - M) ** 2))
                var = rc["val"] - bias
                slv, slst = state_linear_value(P, M)
                nlp = GenuineNLP(P)
                g = genuine_best(P, nlp, M, rng, nstart=10 if N <= 16 else 6, Zv=rc["Z"])
                # planar extreme-arc distance (upper bound): distance from M to P_u
                Pu = P.readout_of(P.extreme_arc(0.0))
                row = dict(N=N, wtf=wtf, readout=readout, sdp=rc["val"], st=rc["status"], scs=rs["val"], st_scs=rs["status"],
                           genuine=g["f"], state_linear=slv, st_sl=slst, bias=bias, variance=var, rank=d["rank"],
                           dist2_M_Pu=float(np.sum(P.mu[:, None] * (Pu - M) ** 2)), scale2=P.scale2)
                rows.append(row)
                print(json.dumps(row), flush=True)
    json.dump(rows, open(os.path.join(OUT, "m_cert.json"), "w"), indent=1)
