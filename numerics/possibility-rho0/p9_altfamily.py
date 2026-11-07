"""Search for ties on faces whose primer ends upward (both witnesses end in a braking burn).
p(s) = (1 - s/tf) q + mu (s/tf) e_z,  q = (-cos g, -sin g) (left, g below horizontal) -> p_x <= 0: z-axis fold exact.
Scan mu; a jump of the optimal moments in mu = non-singleton face."""
import numpy as np, sys
from dp import solve
T = float(sys.argv[1]); dd = float(sys.argv[2]); dl = np.deg2rad(dd)
for gdeg in [dd + 2, dd + 5, dd + 10, dd + 20, dd + 35]:
    g = np.deg2rad(gdeg); q = np.array([-np.cos(g), -np.sin(g)])
    mus = np.geomspace(0.02, 20, 120); X = []
    for mu in mus:
        A = q; B = (mu*np.array([0, 1.0]) - q)/T
        X.append(solve(A, B, T, 1.0, dl, N=240, m=3, side=-1)[2])
    X = np.array(X); dX = np.linalg.norm(np.diff(X, axis=0), axis=1)
    k = np.argmax(dX)
    print(f"T={T} delta={dd} gamma={gdeg}: max moment jump {dX[k]:.4f} at mu in [{mus[k]:.3f},{mus[k+1]:.3f}] (median step {np.median(dX):.4f})", flush=True)
