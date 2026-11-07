import sys, numpy as np
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from stress import stress
from dimtest import nlp, sdp, weights
cases, a1 = make_cases(); c = cases[12]; dl = np.deg2rad(15); N, tf, om = c["N"], c["tf"], c["om"]
wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
o = np.load("case12_out.npz")
ev, U, res, lam, mu, act = stress(o["conf3_B"], o["conf3_D"], wv, wr, N, tf, om, dl, a1)
print("case12 unit-d 3D optimum: stationarity residual", f"{res:.1e}", "lowest Q eigs", np.round(ev[:4], 5), "#active", len(act))
# coplanar demo: rotate wr's lateral onto wv's lateral direction
lat = wv[1:] / np.linalg.norm(wv[1:]); wr2 = np.r_[wr[0], np.linalg.norm(wr[1:]) * lat]
for lab, W2 in [("coplanar case12'", wr2)]:
    v, st, e, _ = sdp(wv, W2, N, tf, om, dl, a1)
    n3, (Bs, Ds) = nlp(wv, W2, N, tf, om, dl, 3, 12, a1=a1)
    nrm = np.r_[0, -lat[1], lat[0]]   # normal of the data plane
    planar = max(np.max(np.abs(Bs @ nrm)), np.max(np.abs(Ds @ nrm)))
    ev2, *_ , act2 = stress(Bs, Ds, wv, W2, N, tf, om, dl, a1)
    print(f"{lab}: SDP={v:.8e}[{st}] NLP3={n3:.8e} max|out-of-plane|={planar:.1e} lowest Q eigs {np.round(ev2[:3],5)}")
