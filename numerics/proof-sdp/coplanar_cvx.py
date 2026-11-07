import sys, numpy as np
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from dimtest import sdp
from convex_d import nlp_cvx
cases, a1 = make_cases(); c = cases[12]; dl = np.deg2rad(15); N, tf, om = c["N"], c["tf"], c["om"]
wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
lat = wv[1:] / np.linalg.norm(wv[1:]); wr2 = np.r_[wr[0], np.linalg.norm(wr[1:]) * lat]
vc, st, evc, G = sdp(wv, wr2, N, tf, om, dl, a1, cvx=True)
w, U = np.linalg.eigh(G); idx = np.argsort(w)[::-1][:3]; X = U[:, idx] * np.sqrt(np.maximum(w[idx], 0))
Uq, S, Vt = np.linalg.svd(X[:3].T); Z = X @ (Uq @ Vt); nbi = N - 1
ng, Bs, Ds = nlp_cvx(wv, wr2, N, tf, om, dl, a1, [np.r_[Z[3:3+nbi].ravel(), Z[3+nbi:].ravel()]], starts=8)
nrm = np.r_[0, -lat[1], lat[0]]
print(f"coplanar case12' convexified: SDP_cvx={vc:.8e}[{st}] ev4/ev1={evc[3]/evc[0]:.1e} genuine_cvx={ng:.8e} |d|min={np.min(np.linalg.norm(Ds,axis=1)):.4f} out-of-plane={max(np.max(np.abs(Bs@nrm)),np.max(np.abs(Ds@nrm))):.1e}")
