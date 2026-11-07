"""proof-sdp: delta=0 fixed-thrust sphere chain. Thrust on segment k along b_k (k=0..N-1), b_0=b_N=e_z,
<b_k,b_{k+1}> >= cos(omega h). AXIS (r,v) targets with excess vertical thrust force lateral cancellation of BOTH
moments (sum c_k b_k,lat = 0, sum c_k (tf-s_k) b_k,lat = 0). Question: does R^4 (3D lateral) beat R^3 (2D lateral)?
NLP3 vs NLP4 vs SDP."""
import sys, numpy as np, cvxpy as cp
from scipy.optimize import minimize

def setup(N, tf, a1):
    h = tf / N; cv = h * a1 * np.ones(N); cr = h * a1 * (tf - (np.arange(N) + 0.5) * h); return h, cv, cr

def nlp(wv, wr, N, tf, om, a1, n, starts, seed=0, x0s=()):
    h, cv, cr = setup(N, tf, a1); e0 = np.zeros(n); e0[0] = 1; W = np.zeros((2, n)); W[0, :3] = wv; W[1, :3] = wr
    def unpack(x):
        Z = x.reshape(N - 1, n); Z = Z / np.linalg.norm(Z, axis=1, keepdims=True); return np.vstack([e0, Z, e0])
    def f(x):
        Bs = unpack(x)[:N]; V = cv @ Bs - W[0]; R = cr @ Bs - W[1]; return V @ V + R @ R
    def g(x):
        Bs = unpack(x); return np.einsum('ij,ij->i', Bs[:-1], Bs[1:]) - np.cos(om * h)
    rng = np.random.default_rng(seed); inits = list(x0s); t = np.arange(1, N) * h
    for s in range(starts):
        if s % 2 == 0:   # coning guess: tilt profile + azimuth rotation (random rate / axis in R^n)
            phi = rng.uniform(0.3, 1.0) * np.minimum(om * np.minimum(t, tf - t), rng.uniform(0.3, 1.2))
            P = np.linalg.qr(rng.normal(size=(n - 1, 2)))[0]; Q3 = np.linalg.qr(rng.normal(size=(n - 1, n - 1)))[0]
            k = rng.integers(1, 4); psi = 2 * np.pi * k * t / tf * rng.uniform(0.7, 1.3)
            lat = np.outer(np.cos(psi), P[:, 0]) + np.outer(np.sin(psi), P[:, 1])
            if n > 3 and rng.uniform() < 0.5:   # 3D lateral "seam" curve
                lat = lat + 0.6 * np.outer(np.sin(2 * psi + rng.uniform(0, 6)), Q3[:, -1])
                lat /= np.linalg.norm(lat, axis=1, keepdims=True)
            Z = np.hstack([np.cos(phi)[:, None], np.sin(phi)[:, None] * lat])
        else:
            Z = np.tile(e0, (N - 1, 1)) + rng.normal(scale=rng.uniform(0.1, 0.8), size=(N - 1, n))
        inits.append(Z.ravel())
    best = (np.inf, None)
    for x0 in inits:
        r = minimize(f, x0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': g}], options={'maxiter': 4000, 'ftol': 1e-15})
        if np.min(g(r.x)) > -1e-9 and r.fun < best[0]: best = (r.fun, r.x)
    return best[0], unpack(best[1])

def sdp(wv, wr, N, tf, om, a1):
    h, cv, cr = setup(N, tf, a1); n = 3 + N - 1; G = cp.Variable((n, n), PSD=True)
    Bi = lambda k: 0 if k in (0, N) else 3 + k - 1
    cons = [G[i, j] == float(i == j) for i in range(3) for j in range(i, 3)] + [G[3 + i, 3 + i] == 1 for i in range(N - 1)]
    cons += [G[Bi(k), Bi(k + 1)] >= np.cos(om * h) for k in range(N)]
    def lin(c, i): return cp.sum(cp.hstack([c[k] * G[Bi(k), i] for k in range(N)]))
    def quad(c): return cp.sum(cp.hstack([c[j] * c[k] * G[Bi(j), Bi(k)] for j in range(N) for k in range(N)]))
    obj = sum(quad(c) - 2 * sum(w[i] * lin(c, i) for i in range(3)) + float(w @ w) for c, w in ((cv, wv), (cr, wr)))
    p = cp.Problem(cp.Minimize(obj), cons); p.solve(solver=cp.CLARABEL); ev = np.sort(np.linalg.eigvalsh(G.value))[::-1]
    return p.value, p.status, ev

if __name__ == "__main__":
    N, tf, omd, starts = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]); a1 = 5.0; om = np.deg2rad(omd)
    h, cv, cr = setup(N, tf, a1)
    for frac in [float(x) for x in sys.argv[5:]]:
        wv = np.array([frac * cv.sum(), 0, 0]); wr = np.array([frac * cr.sum(), 0, 0])
        vs, st, ev = sdp(wv, wr, N, tf, om, a1)
        n3, B3 = nlp(wv, wr, N, tf, om, a1, 3, starts, 1); n4, B4 = nlp(wv, wr, N, tf, om, a1, 4, starts, 2)
        print(f"delta0 axis N={N} tf={tf} om={omd} frac={frac}: SDP={vs:.7e}[{st}] NLP3={n3:.7e} NLP4={n4:.7e} (n3-sdp)/n3={(n3-vs)/max(n3,1e-12):+.2e} ev={np.round(ev[:6]/ev[0],4)}", flush=True)
