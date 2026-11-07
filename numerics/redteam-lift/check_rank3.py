"""redteam-lift: inspect C-SD2 optimum at small-N gap instances: eigenvalues, feasibility of the projected 3D trajectory, its cost."""
import sys, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import factor
N = int(sys.argv[1]); J = int(sys.argv[2]); tf, om, dl, a1 = 4.0, np.deg2rad(30), np.deg2rad(15), 5.0
h = tf / N; s = np.arange(N + 1) * h; phi = om * np.minimum(s, tf - s); psi = dl + np.minimum(phi[:-1], phi[1:])
cr = h * a1 * (tf - (np.arange(N) + 0.5) * h)
Pv = np.array([np.sum(h * a1 * np.cos(psi)), np.sum(h * a1 * np.sin(psi)), 0]); Pr = np.array([np.sum(cr * np.cos(psi)), np.sum(cr * np.sin(psi)), 0])
rng = np.random.default_rng(0)
for j in range(J + 1):
    lam = rng.uniform(0, 1); rot = rng.uniform(0, 2 * np.pi); up = rng.uniform(0, 1.5)
    R = np.array([[1, 0, 0], [0, np.cos(rot), -np.sin(rot)], [0, np.sin(rot), np.cos(rot)]])
    wv = lam * Pv + (1 - lam) * (R @ Pv) + np.array([up, 0, 0]); wr = lam * Pr + (1 - lam) * (R @ Pr) + np.array([up * tf / 2, 0, 0])
val, G, cv, crr = factor.solve_G(wv, wr, N, tf, om, dl)
ev = np.sort(np.linalg.eigvalsh(G))[::-1]
nb = N + 1
Bx = np.array([G[3 + k, :3] for k in range(nb)]); Dx = np.array([G[3 + nb + k, :3] for k in range(N)])
print("SDP", val, "eig", np.round(ev[:6], 8))
print("|b| proj", np.round(np.linalg.norm(Bx, axis=1), 6), "|d| proj", np.round(np.linalg.norm(Dx, axis=1), 6))
Sv = cv @ Dx; Sr = crr @ Dx
print("cost of projected (unnormalized) traj", np.sum((Sv - wv) ** 2) + np.sum((Sr - wr) ** 2))
print("b·b' ", [round(Bx[k] @ Bx[k + 1], 6) for k in range(N)], "need >=", round(np.cos(om * h), 6))
print("d·b  ", [round(Dx[k] @ Bx[k], 6) for k in range(N)], [round(Dx[k] @ Bx[k + 1], 6) for k in range(N)], "need >=", round(np.cos(dl), 6))
