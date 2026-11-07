import sys, numpy as np, cvxpy as cp
sys.path.insert(0, "redteam-lift")
from sdp_clean import build
from c1_csd2_check import make_cases
cases, a = make_cases(); c = cases[12]; dl = np.deg2rad(15)
wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
print("case 12: N", c["N"], "tf", c["tf"], "omega deg", np.degrees(c["om"]), "target dv(mine x,y,z)", np.round(c["wv_m"], 4), "dr", np.round(c["wr_m"], 4))
for solver, kw in [(cp.CLARABEL, dict(tol_gap_abs=1e-10, tol_gap_rel=1e-10, tol_feas=1e-10)), (cp.SCS, dict(eps_abs=1e-10, eps_rel=1e-10, max_iters=500000))]:
    G, cons, obj = build(wv, wr, c["N"], c["tf"], c["om"], dl, a1=a)
    p = cp.Problem(cp.Minimize(obj), cons)
    try:
        p.solve(solver=solver, **kw)
    except Exception as e:
        print(solver, "failed", e); continue
    Gv = G.value; ev = np.linalg.eigvalsh(Gv)
    viol = max(float(np.max(np.abs(np.minimum(0, cc.expr.value)))) if hasattr(cc, "expr") else 0 for cc in cons) if False else None
    # constraint residuals
    res = []
    for cc in cons:
        v = cc.violation(); res.append(float(np.max(v)))
    print(solver, p.status, f"value={p.value:.8f}", "min eig", f"{ev.min():.2e}", "top eig", np.round(ev[::-1][:5], 5), "max constraint viol", f"{max(res):.1e}")
