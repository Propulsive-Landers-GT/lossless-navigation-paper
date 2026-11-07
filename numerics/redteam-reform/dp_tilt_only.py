"""
[redteam-reform] Tilt-angle-only rate model (azimuth free, as in a 'tilt rate' LCvx constraint).
Exact DP over a Lipschitz grid for the support problem  max  int e(s).u(s) ds  over the model
   u = a d,  a in [a1,a2],  tilt(d) in [phi-delta, phi+delta] cap [0,pi],  azimuth(d) free,
   phi(0)=0, |phi'| <= omega (grid: phi_k = j*omega*h, j -> j-1, j, j+1).
Weight e(s) = ((s-s0) xhat, kappa)  (affine in s, so it is the weight of a linear functional of (v0,r0)).
Scan kappa: a jump of the maximizing endpoint with a tie => a non-singleton exposed face; if the
optimal-state set at the tie is disconnected (two branches), the face midpoint is not an endpoint of any
maximizer => F_tilt nonconvex (numerical evidence, discrete inner model).
"""
import numpy as np, json, sys

def solve(kappa, s0, P, ret_sets=False):
    a1, a2, om, de, tf, N = P["a1"], P["a2"], P["omega"], P["delta"], P["tf"], P["N"]
    h = tf / N
    s = (np.arange(N) + 0.5) * h
    J = int(np.floor(np.pi / (om * h)))          # phi grid up to pi
    phi = np.arange(J + 1) * om * h
    eh = s - s0; ez = kappa * np.ones(N)
    nrm = np.hypot(eh, ez); chi = np.arctan2(np.abs(eh), ez)  # folded tilt of e(s)
    # stage reward r[k, j] for interval k with phi = phi_j (phi held at node value; inner-ish)
    lo = np.clip(phi[None, :] - de, 0, np.pi); hi = np.clip(phi[None, :] + de, 0, np.pi)
    tau = np.clip(chi[:, None], lo, hi)
    c = np.cos(tau - chi[:, None])
    a = np.where(c > 0, a2, a1)
    r = h * nrm[:, None] * a * c
    NEG = -1e18
    V = np.full((N + 1, J + 1), NEG); V[0, 0] = 0.0
    for k in range(N):
        prev = V[k]
        best = prev.copy()
        best[1:] = np.maximum(best[1:], prev[:-1]); best[:-1] = np.maximum(best[:-1], prev[1:])
        V[k + 1] = best + r[k]           # phi at interval k = node k+1 value (reachable from node k)
    # backward
    W = np.full((N + 1, J + 1), NEG); W[N] = 0.0
    for k in range(N - 1, -1, -1):
        nxt = W[k + 1] + r[k]
        best = nxt.copy()
        best[1:] = np.maximum(best[1:], nxt[:-1]); best[:-1] = np.maximum(best[:-1], nxt[1:])
        W[k] = best
    Vstar = V[N].max()
    # recover one optimal path
    j = int(V[N].argmax()); path = [j]
    for k in range(N, 1, -1):
        cand = [jj for jj in (j - 1, j, j + 1) if 0 <= jj <= J and V[k - 1, jj] > NEG / 2]
        jj = max(cand, key=lambda q: V[k - 1, q]); path.append(jj); j = jj
    path = path[::-1]  # phi index on intervals 0..N-1
    ph = phi[np.array(path)]
    t = np.clip(chi, np.clip(ph - de, 0, np.pi), np.clip(ph + de, 0, np.pi))
    cc = np.cos(t - chi); aa = np.where(cc > 0, a2, a1)
    sgn = np.sign(eh); sgn[sgn == 0] = 1
    u = np.stack([aa * np.sin(t) * sgn, np.zeros(N), aa * np.cos(t)], 1)
    dv = (u * h).sum(0); dr = (u * h * (tf - s)[:, None]).sum(0)
    out = dict(V=Vstar, dv=dv, dr=dr, phi=ph)
    if ret_sets:
        tot = V[1:] + W[1:]   # total value through state (node k, j), k=1..N
        out["opt_states"] = [np.where(tot[k] >= Vstar - 1e-9 * abs(Vstar))[0] for k in range(N)]
        out["phigrid"] = phi
    return out

if __name__ == "__main__":
    P = dict(a1=5.0, a2=12.5, omega=0.4, delta=np.deg2rad(float(sys.argv[1]) if len(sys.argv) > 1 else 15.0),
             tf=7.0, N=1400)
    res = []
    for s0 in [3.0, 3.5, 4.0, 4.5, 5.0]:
        prev = None
        for kappa in np.linspace(0.05, 4.0, 80):
            o = solve(kappa, s0, P)
            mind = o["phi"][int(s0 / P["tf"] * P["N"])]
            if prev is not None:
                jump = np.linalg.norm(np.r_[o["dv"], o["dr"]] - np.r_[prev[1]["dv"], prev[1]["dr"]])
                res.append((s0, kappa, mind, jump))
            prev = (kappa, o)
    res = np.array(res)
    for s0 in np.unique(res[:, 0]):
        R = res[res[:, 0] == s0]
        i = R[:, 3].argmax()
        print(f"s0={s0}: max endpoint jump {R[i,3]:.3f} at kappa={R[i,1]:.3f}; phi(s0) over scan: "
              f"{np.round(np.rad2deg(R[::8,2]),1)}")
