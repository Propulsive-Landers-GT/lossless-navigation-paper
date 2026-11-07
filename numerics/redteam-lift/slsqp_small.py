"""redteam-lift: same SDP->rank-3->SLSQP certificate on the small-N scan instances (scan_small.py targets)."""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from certify_slsqp import extract, polish
N = int(sys.argv[1]); js = [int(t) for t in sys.argv[2].split(",")]
tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
rng = np.random.default_rng(0)
for j in range(max(js) + 1):
    lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
    R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
    wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
    if j not in js: continue
    v, Bn, Dn = extract(wv, wr, N, tf, om, dl)
    u, viol, msg = polish(Bn, Dn, wv, wr, N, tf, om, dl)
    print(f"SLSQP N={N} j={j}: SDP lower={v:.8e} genuine upper={u:.8e} viol={viol:.1e} relgap={(u - v) / u:.1e} [{msg}]", flush=True)
