import sys, numpy as np
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from c1_csd2_check import make_cases
from dimtest import sdp
cases, a1 = make_cases(); dl = np.deg2rad(15)
for ci in [int(x) for x in sys.argv[1:]]:
    c = cases[ci]; N, tf, om = c["N"], c["tf"], c["om"]
    wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
    v0, st0, ev0, _ = sdp(wv, wr, N, tf, om, dl, a1, cvx=False); v1, st1, ev1, G1 = sdp(wv, wr, N, tf, om, dl, a1, cvx=True)
    nbi = N - 1; dn = np.diag(G1)[3 + nbi:]
    print(f"case {ci}: SDP_unit={v0:.8f}[{st0}] rank-ev {np.round(ev0[:5],4)} | SDP_cvx={v1:.8f}[{st1}] rank-ev {np.round(ev1[:5],4)} |d|^2={np.round(dn,4)}", flush=True)
