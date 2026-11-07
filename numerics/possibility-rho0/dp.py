"""Planar exact-structure DP for support functions of K (M1, rho1=0, alpha=0).
Primer p(s) = A + B s in the x-z plane; beta = signed tilt of b (rad), |beta'| <= omega, beta(0)=0.
Pointwise best thrust: contribution |p| c(|phi - beta|), c = 1 (<=delta), cos(.-delta), 0 beyond delta+pi/2.
Returns optimal value, beta path, and moments (I_x, I_z, J_x, J_z) of the optimal control (a2 = 1 unless given).
side=-1 restricts beta <= 0 (exact for primers with p_x <= 0 by the z-axis fold, see math/possibility-rho0.md)."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

def wrap(x): return (x + np.pi) % (2*np.pi) - np.pi

def solve(A, B, tf, omega, dl, N=300, m=3, a2=1.0, side=0, final0=False):
    h = tf / N; db = omega*h/m
    nb = int(np.ceil(omega*tf/db)) ; grid = np.arange(-nb, nb+1)*db
    if side < 0: grid = grid[grid <= 1e-12]
    if side > 0: grid = grid[grid >= -1e-12]
    sm = (np.arange(N)+0.5)*h
    P = A[None, :] + sm[:, None]*B[None, :]                          # (N,2) primer at midpoints
    mag = np.linalg.norm(P, axis=1); phi = np.arctan2(P[:, 0], P[:, 1])   # angle from e_z toward +x
    ang = np.abs(wrap(phi[:, None] - grid[None, :]))                 # (N, nb)
    c = np.where(ang <= dl, 1.0, np.maximum(0, np.cos(np.minimum(ang - dl, np.pi))))
    R = h*mag[:, None]*c                                              # stage reward (beta held over step ~ midpoint)
    # reachability: |beta_k| <= omega*k*h
    Vn = np.zeros(len(grid))
    if final0: Vn = np.where(np.abs(grid) < 1e-12, 0.0, -np.inf)   # tent variant b(tf)=e_z
    choice = np.zeros((N, len(grid)), int)
    idx = np.arange(len(grid))
    for k in range(N-1, -1, -1):
        # from state j at node k, move to j+dj (|dj|<=m) at node k+1; reward evaluated at node-k beta (approx)
        best = np.full(len(grid), -np.inf); arg = np.zeros(len(grid), int)
        for dj in range(-m, m+1):
            j2 = idx + dj; ok = (j2 >= 0) & (j2 < len(grid))
            val = np.full(len(grid), -np.inf); val[ok] = Vn[j2[ok]]
            upd = val > best + 1e-15; best[upd] = val[upd]; arg[upd] = j2[upd]
        Vn = R[k] + best; choice[k] = arg
        Vn[np.abs(grid) > omega*k*h + 1e-9] = -np.inf
    j = int(np.argmin(np.abs(grid))); val = Vn[j]; path = [j]
    for k in range(N): j = choice[k, j]; path.append(j)
    beta = grid[np.array(path[:-1])]
    # moments with the pointwise-optimal thrust direction
    dlt = wrap(phi - beta); off = np.clip(dlt, -dl, dl); dang = beta + off
    a = a2*(c[np.arange(N), np.array(path[:-1])] > 1e-12)
    u = a[:, None]*np.stack([np.sin(dang), np.cos(dang)], 1)
    I = h*u.sum(0); J = h*((tf - sm)[:, None]*u).sum(0)
    return val*a2, beta, np.concatenate([I, J]), a, dang
