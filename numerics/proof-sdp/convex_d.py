"""proof-sdp: is the case-12 gap a discrete-chattering artifact? Genuine model with CONVEXIFIED thrust direction
d_k in conv(lens) = {||d||<=1, <d,b_k>>=cos dl, <d,b_{k+1}> >= cos dl} (discrete analogue of continuous-time relaxed
controls, which equal genuine ones by Lyapunov when alpha=0), compared with the SDP value."""
import sys, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, ".."); sys.path.insert(0, "../redteam-lift")
from dimtest import weights, sdp

def nlp_cvx(wv, wr, N, tf, om, dl, a1, x0s, starts=0, seed=0):
    h, cv, cr = weights(N, tf, a1); nbi = N - 1; n = 3; e0 = np.array([1., 0, 0])
    def unpack(x):
        Bm = x[:3 * nbi].reshape(nbi, 3); Bm = Bm / np.linalg.norm(Bm, axis=1, keepdims=True)
        return np.vstack([e0, Bm, e0]), x[3 * nbi:].reshape(N, 3)
    def f(x):
        Bs, Ds = unpack(x); V = cv @ Ds - wv; R = cr @ Ds - wr; return V @ V + R @ R
    def g(x):
        Bs, Ds = unpack(x)
        return np.concatenate([np.einsum('ij,ij->i', Bs[:-1], Bs[1:]) - np.cos(om * h), np.einsum('ij,ij->i', Ds, Bs[:-1]) - np.cos(dl),
                               np.einsum('ij,ij->i', Ds, Bs[1:]) - np.cos(dl), 1 - np.einsum('ij,ij->i', Ds, Ds)])
    rng = np.random.default_rng(seed); inits = list(x0s)
    for s in range(starts):
        inits.append(np.r_[(np.tile(e0, (nbi, 1)) + rng.normal(scale=rng.uniform(.05, .6), size=(nbi, 3))).ravel(), (np.tile(e0, (N, 1)) + rng.normal(scale=.3, size=(N, 3))).ravel()])
    best = (np.inf, None)
    for x0 in inits:
        r = minimize(f, x0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': g}], options={'maxiter': 3000, 'ftol': 1e-15})
        if np.min(g(r.x)) > -1e-9 and r.fun < best[0]: best = (r.fun, r.x)
    if best[1] is None: return np.inf, None, None
    Bs, Ds = unpack(best[1]); return best[0], Bs, Ds

if __name__ == "__main__":
    from c1_csd2_check import make_cases
    cases, a1 = make_cases(); c = cases[12]; dl = np.deg2rad(15); N, tf, om = c["N"], c["tf"], c["om"]
    wv = np.array([c["wv_m"][2], c["wv_m"][0], c["wv_m"][1]]); wr = np.array([c["wr_m"][2], c["wr_m"][0], c["wr_m"][1]])
    o = np.load("case12_out.npz"); B4, D4 = o["conf4_B"], o["conf4_D"]
    x_proj = np.r_[B4[1:N, :3].ravel(), D4[:, :3].ravel()]      # E-projection of the 4D optimum
    x_g3 = np.r_[o["conf3_B"][1:N].ravel(), o["conf3_D"].ravel()]  # best unit-d 3D optimum
    val, Bs, Ds = nlp_cvx(wv, wr, N, tf, om, dl, a1, [x_proj, x_g3], starts=int(sys.argv[1]) if len(sys.argv) > 1 else 6)
    print("SDP (unit d) =", float(o["sdp"]), " genuine unit-d 3D =", float(o["n3"]), " genuine CONVEXIFIED-d 3D =", val)
    print("|d_k| at convexified optimum:", np.round(np.linalg.norm(Ds, axis=1), 4))
