"""proof-sdp: structure of [numerics] case 12 (BOARD 03:20). Vertical = coord 0 (mine)."""
import sys, numpy as np
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from dimtest import sdp, nlp, weights
cases, a1 = make_cases(); c = cases[12]; dl = np.deg2rad(15); N, tf, om = c["N"], c["tf"], c["om"]
wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
print("a1", a1, "N", N, "tf", tf, "om", np.degrees(om), "wv", wv, "wr", wr)
print("lateral angle wv,wr (deg):", np.degrees(np.arctan2(wv[2], wv[1])), np.degrees(np.arctan2(wr[2], wr[1])))
v, st, ev, G = sdp(wv, wr, N, tf, om, dl, a1)
print("SDP", v, st, "eig", np.round(ev[:6], 5))
# factor: G = X X^T with first 3 rows = identity block
w, U = np.linalg.eigh(G); idx = np.argsort(w)[::-1][:4]; X = U[:, idx] * np.sqrt(np.maximum(w[idx], 0))
# rotate so that rows 0..2 become e_0,e_1,e_2 in first 3 coords
Q, _ = np.linalg.qr(np.vstack([X[:3], np.eye(4)])[:4].T); Xr = X @ Q
A = Xr[:3, :3]; M = np.eye(4); M[:3, :3] = np.linalg.inv(A)  # Xr[:3] ~ [A 0]
Y = Xr @ np.linalg.inv(np.block([[A, np.zeros((3, 1))], [np.zeros((1, 3)), np.ones((1, 1))]]).T) if False else None
# simpler: least-squares map T (4x4 orthogonal) with X[:3] T = [I 0]
Uq, S, Vt = np.linalg.svd(X[:3].T @ np.eye(4)[:3]); T = Uq @ Vt
Z = X @ T
print("constant rows after rotation:\n", np.round(Z[:3], 4))
nbi = N - 1; B = Z[3:3 + nbi]; D = Z[3 + nbi:]
print("E-perp (4th) comps of b_1..b_N-1:", np.round(B[:, 3], 4))
print("E-perp (4th) comps of d_0..d_N-1:", np.round(D[:, 3], 4))
h, cv, cr = weights(N, tf, a1)
print("E-perp moments: sum cv d4 =", cv @ D[:, 3], " sum cr d4 =", cr @ D[:, 3])
# 4D polish from SDP factor and 3D best from many starts incl. projected SDP
x0_4 = np.vstack([B, D]).ravel()
n4, conf4 = nlp(wv, wr, N, tf, om, dl, 4, 0, a1=a1, x0s=[x0_4])
P3 = np.vstack([B, D])[:, :3]; x0_3 = (P3 / np.linalg.norm(P3, axis=1, keepdims=True)).ravel()
print("NLP4 polish from SDP factor:", n4)
n3, conf3 = nlp(wv, wr, N, tf, om, dl, 3, int(sys.argv[1]) if len(sys.argv) > 1 else 20, a1=a1, x0s=[x0_3])
print("NLP3 best:", n3, " gap (n3-sdp)/n3 =", (n3 - v) / n3)
np.savez("case12_out.npz", B=B, D=D, conf3_B=conf3[0], conf3_D=conf3[1], conf4_B=conf4[0], conf4_D=conf4[1], sdp=v, n3=n3, n4=n4)
