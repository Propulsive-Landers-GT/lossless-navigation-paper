"""redteam-lift: scan small-N instances for a degree-2 (C-SD2) gap: SDP vs multistart NLP (velocity+position)."""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from csd2_deep import sdp_rv, nlp
N = int(sys.argv[1]); tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
for j in range(int(sys.argv[3]) if len(sys.argv) > 3 else 15):
    lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
    R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
    wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
    v, Bx, Dx, ev = sdp_rv(wv, wr, N, tf, om, dl)
    m = nlp(wv, wr, N, tf, om, dl, starts=40, warm=(Bx, Dx))
    print(f"N={N} j={j} SDP={v:.6e} NLP={m:.6e} relgap={(m - v) / max(m, 1e-12):.2e} eig4={ev[3]:.1e}", flush=True)
