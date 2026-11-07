"""proof-sdp: small-N search for CSD2 gaps near the dent (targets = mixtures of rotated extreme tent arcs + noise)."""
import numpy as np, sys, json
from dimtest import sdp, nlp, weights
N = int(sys.argv[1]); K = int(sys.argv[2]); seed = int(sys.argv[3])
tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h, cv, cr = weights(N, tf, a1)
s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
def P(rot):
    u = np.array([0, np.cos(rot), np.sin(rot)]); D = np.outer(np.cos(psi), [1, 0, 0]) + np.outer(np.sin(psi), u)
    return cv @ D, cr @ D
rng = np.random.default_rng(seed); out = []
for j in range(K):
    lam = rng.uniform(0.2, 0.8); r1 = rng.uniform(0, 2*np.pi); r2 = r1 + rng.uniform(0.5, np.pi)
    v1, q1 = P(r1); v2, q2 = P(r2); sc = rng.uniform(0, 0.05)
    wv = lam*v1 + (1-lam)*v2 + sc*rng.normal(size=3); wr = lam*q1 + (1-lam)*q2 + sc*tf/2*rng.normal(size=3)
    v, st, ev, _ = sdp(wv, wr, N, tf, om, dl, a1)
    n3, _ = nlp(wv, wr, N, tf, om, dl, 3, 60, seed=j); n4, _ = nlp(wv, wr, N, tf, om, dl, 4, 30, seed=j)
    rg = (n3 - v) / max(abs(n3), 1e-12)
    print(f"N={N} j={j} SDP={v:.8e}[{st}] NLP3={n3:.8e} NLP4={n4:.8e} relgap={rg:+.2e} ev={np.round(ev[:5]/ev[0],5)}", flush=True)
    out.append(dict(j=j, wv=wv.tolist(), wr=wr.tolist(), sdp=v, n3=n3, n4=n4, ev=ev[:6].tolist()))
json.dump(out, open(f"search_N{N}_s{seed}.json", "w"))
