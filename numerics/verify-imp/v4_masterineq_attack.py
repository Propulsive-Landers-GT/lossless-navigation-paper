"""verify-imp: independent adversarial attack on Prop M (math/07): maximize gain - C_m*|pi_m|^2 over admissible
3D M1 trajectories (inner discretization: piecewise-constant tangential body rate |w_k|<=w, d constant per cell
inside the gimbal cone shrunk by w*h so it stays admissible on the whole cell, throttle in [rho1,rho2], alpha=0).
Must stay <= B. Single process, L-BFGS-B with numeric gradients, few starts."""
import numpy as np
from scipy.optimize import minimize
import importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location("v3", "v3_lemmaS_table.py")
with contextlib.redirect_stdout(io.StringIO()):
    v3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v3)

def run(dd, T, w, N=24, starts=6, seed=0):
    m0, rho1, rho2 = 100., 1200., 2500.
    dl = np.radians(dd); a10 = rho1 / m0; a2 = rho2 / m0
    Om = w * T; tb = dl + Om
    c0 = 1 / (1 + np.cos(dl)); Ap = c0 / a10
    k0 = np.cos(tb) / ((a2 - a10) * np.sin(tb) ** 2); Cm = Ap * k0 / (k0 - Ap)
    with contextlib.redirect_stdout(io.StringIO()):
        pass
    # B from v3
    import math
    from scipy.integrate import quad
    tau = lambda s: dl + w * s
    E4 = a10 * quad(lambda s: (1 / (1 + np.cos(tau(s))) - c0) * np.sin(tau(s)) ** 2, 0, T)[0]
    B = a10 * c0 * T * (Om / (2 * np.pi) + 2 * np.sin(dl / 2)) ** 2 + E4
    h = T / N; mu_max = max(dl - w * h, 0.0)
    sl = np.arange(N) * h; sr = sl + h
    G = np.array([[T, T ** 2 / 2], [T ** 2 / 2, T ** 3 / 3]]); Gi = np.linalg.inv(G)
    def unpack(x):
        wr = x[:2 * N].reshape(N, 2); md = x[2 * N:4 * N].reshape(N, 2); th = x[4 * N:]
        return wr, md, th
    def evaluate(x):
        wr, md, th = unpack(x)
        b = np.array([0, 0, 1.]); e1 = np.array([1., 0, 0])
        gain = 0.0; mom0 = np.zeros(2); mom1 = np.zeros(2)
        for k in range(N):
            # tangential rate: map R^2 -> disk radius w
            r = np.linalg.norm(wr[k]); om = wr[k] * (w * np.tanh(r) / (r + 1e-12))
            e1 = e1 - np.dot(e1, b) * b; e1 /= np.linalg.norm(e1); e2 = np.cross(b, e1)
            # gimbal offset within shrunk cone
            rm = np.linalg.norm(md[k]); mu = mu_max * np.tanh(rm); dirv = (md[k] / (rm + 1e-12))
            n = dirv[0] * e1 + dirv[1] * e2
            d = np.cos(mu) * b + np.sin(mu) * n
            a = a10 + (a2 - a10) / (1 + np.exp(-th[k]))
            gain += (a10 - a * d[2]) * h
            F = a * d[:2]
            mom0 += F * h; mom1 += F * (sr[k] ** 2 - sl[k] ** 2) / 2
            # rotate b (and frame) about axis k_ax = (om1 e1 + om2 e2) x b  ... rate vector Omega = om1*e2' ; simply:
            ang_vel = om[0] * e1 + om[1] * e2          # direction b moves
            sp = np.linalg.norm(ang_vel)
            if sp > 0:
                axis = np.cross(b, ang_vel / sp); ang = sp * h
                def R(v):
                    return v * np.cos(ang) + np.cross(axis, v) * np.sin(ang) + axis * np.dot(axis, v) * (1 - np.cos(ang))
                b = R(b); e1 = R(e1)
        m = np.stack([mom0, mom1])            # 2 x 2 (moment index x component)
        pin2 = sum(m[:, j] @ Gi @ m[:, j] for j in range(2))
        return gain - Cm * pin2
    rng = np.random.default_rng(seed)
    best = -np.inf
    for st in range(starts):
        x0 = rng.normal(scale=1.5, size=5 * N)
        if st == 0:   # planar S-turn-like start
            x0[:2 * N] = 0; x0[0:2 * N:2] = np.where(np.arange(N) < 0.3 * N, 3, -3)
            x0[2 * N:4 * N] = 0; x0[2 * N:4 * N:2] = np.where(np.arange(N) < 0.6 * N, 3, -3); x0[4 * N:] = -5
        if st == 1:   # coning start
            x0[:2 * N] = 0; x0[1:2 * N:2] = 3; x0[0:2 * N:2] = np.linspace(3, -3, N)
        r = minimize(lambda x: -evaluate(x), x0, method="L-BFGS-B", options=dict(maxiter=400))
        best = max(best, -r.fun)
    print(f"delta={dd} T={T} w={w}: sup found gain - Cm|pi|^2 = {best:.5f}  vs B = {B:.5f}  -> holds: {best <= B}")

run(0, 2, 0.2)
run(10, 2, 0.1)
