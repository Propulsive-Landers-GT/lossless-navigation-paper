import sys, numpy as np, cvxpy as cp
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from dimtest import weights
from convex_d import nlp_cvx
cases, a1 = make_cases(); c = cases[12]; dl = np.deg2rad(15); N, tf, om = c["N"], c["tf"], c["om"]
wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
o = np.load("case12_out.npz"); B4, D4 = o["conf4_B"], o["conf4_D"]
val, Bs, Ds = nlp_cvx(wv, wr, N, tf, om, dl, a1, [np.r_[B4[1:N, :3].ravel(), D4[:, :3].ravel()]], 0)
h, cv, cr = weights(N, tf, a1)
print("NLP cvx value", val, "recomputed", np.sum((cv @ Ds - wv)**2) + np.sum((cr @ Ds - wr)**2))
print("min slacks: rate", np.min(np.einsum('ij,ij->i', Bs[:-1], Bs[1:]) - np.cos(om*h)), "gim", min(np.min(np.einsum('ij,ij->i', Ds, Bs[:-1]) - np.cos(dl)), np.min(np.einsum('ij,ij->i', Ds, Bs[1:]) - np.cos(dl))), "norm", np.min(1-np.einsum('ij,ij->i', Ds, Ds)), "|b|-1", np.max(np.abs(np.linalg.norm(Bs,axis=1)-1)))
# build SDP and evaluate at Gram of NLP config; then solve with tight tolerances
nbi = N - 1; n = 3 + nbi + N
X = np.vstack([np.eye(3), Bs[1:N], Ds]); G0 = X @ X.T
G = cp.Variable((n, n), PSD=True)
Bi = lambda k: 0 if k in (0, N) else 3 + (k - 1); Di = lambda k: 3 + nbi + k
cons = [G[i, j] == float(i == j) for i in range(3) for j in range(i, 3)] + [G[3+i, 3+i] == 1 for i in range(nbi)] + [G[Di(k), Di(k)] <= 1 for k in range(N)]
for k in range(N): cons += [G[Bi(k), Bi(k+1)] >= np.cos(om*h), G[Di(k), Bi(k)] >= np.cos(dl), G[Di(k), Bi(k+1)] >= np.cos(dl)]
di = [Di(k) for k in range(N)]
def sq(cc, w):
    m = [cp.sum(cp.multiply(cc, cp.hstack([G[Di(k), i] for k in range(N)]))) for i in range(3)]
    return cp.sum(cp.multiply(np.outer(cc, cc), G[np.ix_(di, di)])) - 2*sum(w[i]*m[i] for i in range(3)) + float(w @ w)
obj = sq(cv, wv) + sq(cr, wr); p = cp.Problem(cp.Minimize(obj), cons)
G.value = G0; print("SDP objective at NLP Gram:", obj.value, " max viol:", max(float(np.max(cc.violation())) for cc in cons))
for solver, kw in [(cp.CLARABEL, dict(tol_gap_abs=1e-12, tol_gap_rel=1e-12, tol_feas=1e-12, max_iter=500)), (cp.SCS, dict(eps_abs=1e-10, eps_rel=1e-10, max_iters=400000))]:
    p.solve(solver=solver, **kw); ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]
    print(solver, p.status, p.value, np.round(ev[:5], 6))
