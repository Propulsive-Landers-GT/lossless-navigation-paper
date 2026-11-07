"""redteam-lift: exact-feasibility repair of the rank-3 extraction by geodesic contraction toward e_z
(p -> exp_{e_z}((1-eps) log_{e_z} p) is 1-Lipschitz on the open upper hemisphere, fixes e_z, so it
preserves every angle constraint up to the contraction).  Gives a rigorous genuine upper bound to compare
with the SDP lower bound (up to SDP solver tolerance)."""
import sys, numpy as np, cvxpy as cp
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from rankred import build as sdpbuild
from csd2_deep import targets

def contract(P, eps):
    z = np.clip(P[:, 0], -1, 1); th = np.arccos(z); lat = P[:, 1:]
    nl = np.linalg.norm(lat, axis=1, keepdims=True); u = np.where(nl > 1e-15, lat / np.maximum(nl, 1e-300), 0)
    th2 = (1 - eps) * th
    return np.c_[np.cos(th2), np.sin(th2)[:, None] * u]

def check(Bn, Dn, N, tf, om, dl):
    h = tf / N
    ang = lambda a, b: np.arccos(np.clip(a @ b, -1, 1))
    vb = max(ang(Bn[k], Bn[k + 1]) - om * h for k in range(N))
    vd = max(max(ang(Dn[k], Bn[k]), ang(Dn[k], Bn[k + 1])) - dl for k in range(N))
    return max(vb, vd, np.abs(Bn[0] - [1, 0, 0]).max(), np.abs(Bn[N] - [1, 0, 0]).max())

def certify(wv, wr, N, tf, om, dl, a1=5.0):
    G, cons, obj = sdpbuild(wv, wr, N, tf, om, dl)
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); v = p.value; Gv = G.value
    for it in range(8):
        ev, V = np.linalg.eigh(Gv); W = V[:, :-3] @ V[:, :-3].T
        q = cp.Problem(cp.Minimize(cp.trace(W @ G)), cons + [obj <= v + 1e-8 * max(abs(v), 1e-3)]); q.solve(solver=cp.CLARABEL); Gv = G.value
        if np.sort(np.linalg.eigvalsh(Gv))[::-1][3] < 1e-9: break
    nb = N + 1; h = tf / N
    Bn = np.array([Gv[3 + k, :3] for k in range(nb)]); Dn = np.array([Gv[3 + nb + k, :3] for k in range(N)])
    Bn /= np.linalg.norm(Bn, axis=1, keepdims=True); Dn /= np.linalg.norm(Dn, axis=1, keepdims=True)
    Bn[0] = Bn[N] = [1, 0, 0]
    cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
    cost = lambda D: np.sum((cv @ D - wv) ** 2) + np.sum((cr @ D - wr) ** 2)
    for eps in [0, 1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2]:
        B2, D2 = contract(Bn, eps), contract(Dn, eps)
        if check(B2, D2, N, tf, om, dl) <= 1e-12:
            return v, cost(D2), eps
    return v, np.nan, None

if __name__ == "__main__":
    jobs = [(0, "rand0"), (0, "rand2"), (1, "rand0"), (1, "rand1"), (1, "rand2")]
    for ci, lab in jobs:
        for l, (N, tf, om, dl), wv, wr in targets(ci):
            if l == lab:
                v, up, eps = certify(wv, wr, N, tf, om, dl)
                print(f"CERT2 cfg{ci} {lab} N={N}: SDP lower={v:.8e}  genuine feasible upper={up:.8e} (contraction eps={eps})  relgap={(up - v) / up:.1e}", flush=True)
