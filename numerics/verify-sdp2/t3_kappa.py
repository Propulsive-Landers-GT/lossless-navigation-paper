"""[verify-sdp2] T3 pointwise algebra: at a gimbal-active unit-thrust point, (S_u) mu_u u - (lam/2) b = P gives
lam = 2|P| sin(th-d)/sin d, mu_u = |P| sin th/sin d, and q + nu|bdot|^2 = (lam/2)<u,b> - lam^2/(4 mu_u) = kappa = |P| sin(th-d) cot th.
Also: kappa = -(d^2/de^2) sigma(b_e, P), b_e = cos e b + sin e n (out-of-plane), sigma(b,P) = max_{u in K(b)} <P,u>."""
import numpy as np
rng = np.random.default_rng(3)
worst = [0, 0, 0]
for _ in range(2000):
    d = rng.uniform(0.05, 1.4); th = rng.uniform(d + 1e-3, np.pi - 0.05); Pn = rng.uniform(0.1, 5)
    b = np.array([0, 0, 1.0]); e = np.array([1.0, 0, 0]); n = np.array([0, 1.0, 0])
    P = Pn * (np.cos(th) * b + np.sin(th) * e)
    u = np.cos(d) * b + np.sin(d) * e
    # solve mu u - (lam/2) b = P in the (b,e) plane
    A = np.array([[u @ b, -0.5], [u @ e, 0.0]]); mu, lam = np.linalg.solve(A, [P @ b, P @ e])
    kap = Pn * np.sin(th - d) / np.tan(th)
    q = 0.5 * lam * (u @ b) - lam ** 2 / (4 * mu)
    sig = lambda bb: Pn * np.cos(max(np.arccos(np.clip(bb @ P / Pn, -1, 1)) - d, 0))
    h = 1e-4
    d2 = (sig(np.cos(h) * b + np.sin(h) * n) - 2 * sig(b) + sig(np.cos(-h) * b + np.sin(-h) * n)) / h ** 2
    worst[0] = max(worst[0], abs(lam - 2 * Pn * np.sin(th - d) / np.sin(d)) / Pn)
    worst[1] = max(worst[1], abs(q - kap) / Pn)
    worst[2] = max(worst[2], abs(-d2 - kap) / Pn)
print('max rel err lam formula %.1e, q=kappa %.1e, kappa=-sigma_ee %.1e' % tuple(worst))
