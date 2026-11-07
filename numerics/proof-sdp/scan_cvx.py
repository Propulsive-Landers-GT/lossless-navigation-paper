"""proof-sdp: CSD2' test. Convexified-lens discretization (||d_k||<=1): SDP_cvx vs genuine convexified 3D NLP
(warm start from E-projection of the SDP factor + random starts). Also reports SDP_unit for comparison.
Targets: [numerics] c1 cases (all), vertical = coord 0."""
import sys, numpy as np
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from dimtest import sdp
from convex_d import nlp_cvx
cases, a1 = make_cases(); dl = np.deg2rad(15)
ids = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(len(cases))
for ci in ids:
    c = cases[ci]; N, tf, om = c["N"], c["tf"], c["om"]
    if N > 24: continue
    wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
    vu, _, evu, _ = sdp(wv, wr, N, tf, om, dl, a1)
    vc, st, evc, G = sdp(wv, wr, N, tf, om, dl, a1, cvx=True)
    w, U = np.linalg.eigh(G); idx = np.argsort(w)[::-1][:3]; X = U[:, idx] * np.sqrt(np.maximum(w[idx], 0))
    Uq, S, Vt = np.linalg.svd(X[:3].T); T = Uq @ Vt; Z = X @ T   # rotate constants to identity
    nbi = N - 1; x0 = np.r_[Z[3:3 + nbi].ravel(), Z[3 + nbi:].ravel()]
    ng, Bs, Ds = nlp_cvx(wv, wr, N, tf, om, dl, a1, [x0], starts=int(sys.argv[1]))
    print(f"case {ci} N={N}: SDP_unit={vu:.7e} SDP_cvx={vc:.7e}[{st}] genuine_cvx={ng:.7e} relgap_cvx={(ng-vc)/max(ng,1e-12):+.1e} ev4/ev1(cvx)={evc[3]/evc[0]:.1e} min|d|={(np.min(np.linalg.norm(Ds,axis=1)) if Ds is not None else -1):.4f}", flush=True)
