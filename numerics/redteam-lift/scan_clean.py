"""redteam-lift: broad test of the well-posed C-SD2 (Slater holds): SDP lower bound vs genuine upper bound obtained by
rank-3 extraction + SLSQP polish (exact feasibility <=1e-10), plus eig4/eig1 of the SDP optimum.
Targets: random mixtures of rotated extreme arcs (+vertical offsets), theta_M, and pure random (r,v) targets."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sdp_clean import build
from certify_slsqp import polish

def sdp(wv, wr, N, tf, om, dl):
    G, cons, obj = build(wv, wr, N, tf, om, dl); p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL)
    Gv = G.value; nbi = N - 1
    B = np.vstack([[1, 0, 0], [Gv[3 + i, :3] for i in range(nbi)], [1, 0, 0]]); D = np.array([Gv[3 + nbi + k, :3] for k in range(N)])
    ev = np.sort(np.linalg.eigvalsh(Gv))[::-1]
    return p.value, p.status, B / np.linalg.norm(B, axis=1, keepdims=True), D / np.linalg.norm(D, axis=1, keepdims=True), ev[3] / ev[0]

if __name__ == "__main__":
    N = int(sys.argv[1]); tf = float(sys.argv[2]); om = np.deg2rad(float(sys.argv[3])); dl = np.deg2rad(float(sys.argv[4])); K = int(sys.argv[5]); a1 = 5.0
    h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
    cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
    rng = np.random.default_rng(123); rows = []
    tg = [("theta_M", np.array([Pv[0], 0, 0]), np.array([Pr[0], 0, 0]))]
    for j in range(K):
        if j % 2 == 0:
            lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 3)
            R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
            tg.append((f"mix{j}", lam * Pv + (1 - lam) * (R @ Pv) + [up, 0, 0], lam * Pr + (1 - lam) * (R @ Pr) + [up * tf / 2, 0, 0]))
        else:
            tg.append((f"rnd{j}", Pv[0] * np.array([rng.uniform(0.8, 1.4), *rng.uniform(-0.8, 0.8, 2)]), Pr[0] * np.array([rng.uniform(0.8, 1.4), *rng.uniform(-0.8, 0.8, 2)])))
    worst = 0
    for lab, wv, wr in tg:
        v, st, B, D, e4 = sdp(wv, wr, N, tf, om, dl)
        up, viol, msg = polish(B, D, wv, wr, N, tf, om, dl)
        rg = (up - v) / max(up, 1e-9); worst = max(worst, rg)
        print(f"N={N} tf={tf} {lab:8s} SDP={v:.7e}[{st}] genuine={up:.7e} viol={viol:.0e} relgap={rg:+.1e} eig4/eig1={e4:.0e}", flush=True)
    print(f"SUMMARY N={N} tf={tf} om={sys.argv[3]} dl={sys.argv[4]}: worst relgap={worst:.1e} over {len(tg)} targets")
