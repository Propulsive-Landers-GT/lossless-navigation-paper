import time, numpy as np
from vcore import *
P = Prob(16, 4.0, 0.4, readout="r")
M = P.midpoint_M()
print("M", M, "Slater", slater_margin(P))
t=time.time(); r = solve_sdp(P, M); print(r["status"], r["val"], time.time()-t)
d = sdp_diag(P, r["Z"]); print("rank", d["rank"], d["ev"][:6], "perp", d["perp_max"])
r2 = solve_sdp(P, M, solver="SCS"); print("SCS", r2["status"], r2["val"])
nlp = GenuineNLP(P); rng=np.random.default_rng(0)
t=time.time(); g = genuine_best(P, nlp, M, rng, nstart=12, Zv=r["Z"]); print("genuine", g["f"], g["fs"][:5], time.time()-t)
