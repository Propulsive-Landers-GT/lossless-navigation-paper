"""verify-imp: stress test of Thm B* Step 7 (math/02 §10.3) inequalities on near-face admissible trajectories.
alpha = 0 (so V* is explicit). Discretized; b rotated exactly by bounded-rate rotations (angle per step <= w*h),
d placed inside the gimbal cone of b. Checks, per trajectory:
 (iv)  |X_h| >= gamma_X - c1*eta_dive
 (v)   |B_h| <= sqrt(2 W_b eta_brake)
 (vi)  |Lambda - Lambda_m| = sqrt(|W_h|^2 + eta^2) >= eta0
Single process."""
import numpy as np
from scipy.optimize import brentq
rng = np.random.default_rng(1)
rho1, rho2, m0, g0 = 400., 1000., 80., 9.81
dl, w, tf = np.radians(15), 0.4, 7.0
s_st = dl / w
a10, amax = rho1 / m0, rho2 / m0
N = 3000
s = (np.arange(N) + 0.5) * tf / N; h = tf / N
th = a10 * np.sin(dl) / (4 * amax); gX = 5 / 32 * a10 * np.sin(dl) * s_st ** 2
Wb = amax * (tf - s_st) ** 2 / 2; c1 = 1 / (w * th * s_st)
eta0 = brentq(lambda e: (1 + c1) * e + np.sqrt(2 * Wb * e) - gX, 0, gX)
dive = s < s_st
wgt = s - s_st
Vstar = np.sum(-(s_st - s[dive]) * a10 * np.cos(dl + w * s[dive])) * h + np.sum(wgt[~dive] * amax) * h
ez = np.array([0, 0, 1.])

def rot(v, k, ang):
    k = k / np.linalg.norm(k)
    return v * np.cos(ang) + np.cross(k, v) * np.sin(ang) + k * np.dot(k, v) * (1 - np.cos(ang))

def traj(kind, eps):
    """near-face trajectory families"""
    u = np.array([1., 0, 0])
    b = np.zeros((N, 3)); d = np.zeros((N, 3)); a = np.where(dive, a10, amax).astype(float)
    cur = ez.copy()
    for i in range(N):
        t = s[i]
        if t < s_st:
            if kind == 'cone':     # azimuth precession during the dive (coning)
                az = eps * t / s_st
                uu = np.array([np.cos(az), np.sin(az), 0])
            else:
                uu = u
            tilt = w * t * (1 - (eps if kind == 'slow' else 0))
            b[i] = np.cos(tilt) * ez + np.sin(tilt) * uu
            dt = dl * (1 - (eps if kind == 'inner' else 0))
            d[i] = np.cos(tilt + dt) * ez + np.sin(tilt + dt) * uu
        else:
            b[i] = b[i - 1]
            if kind == 'brake':    # tilt d toward +u in brake to cancel the weighted lateral moment
                d[i] = np.cos(eps) * ez + np.sin(eps) * u
            else:
                d[i] = ez
        if kind == 'throttle' and t < s_st:
            a[i] = a10 * (1 + eps)
    # admissibility checks (gimbal + rate)
    gim = np.min(np.sum(d * b, 1)) >= np.cos(dl) - 1e-9
    ang = np.arccos(np.clip(np.sum(b[1:] * b[:-1], 1), -1, 1))
    rate = np.max(ang) <= w * h * (1 + 1e-6) + 1e-12
    return a, d, b, gim and rate

def check(a, d, b):
    X = np.sum(((s_st - s) * a * dive)[:, None] * d, 0) * h
    B = np.sum(((s - s_st) * a * (~dive))[:, None] * d, 0) * h
    Z0 = np.sum((s_st - s[dive]) * a[dive] * np.cos(dl + w * s[dive])) * h
    B0 = np.sum((s - s_st)[~dive] * a[~dive]) * h
    eta_d = X[2] - Z0; eta_b = B0 - B[2]
    W = -X + B
    eta = Vstar - W[2]
    iv = np.linalg.norm(X[:2]) >= gX - c1 * eta_d - 1e-9
    v = np.linalg.norm(B[:2]) <= np.sqrt(2 * Wb * max(eta_b, 0)) + 1e-9
    dist = np.sqrt(np.linalg.norm(W[:2]) ** 2 + eta ** 2)
    return iv, v, dist, eta, np.linalg.norm(W[:2])

print(f"gamma_X={gX:.5f} c1={c1:.2f} Wb={Wb:.2f} eta0={eta0:.3e} V*={Vstar:.5f}")
worst = (np.inf, None)
for kind in ['brake', 'cone', 'inner', 'slow', 'throttle']:
    for eps in np.concatenate([np.linspace(0, 0.02, 41), np.linspace(0.02, 0.5, 25)]):
        a, d, b, ok = traj(kind, eps)
        if not ok:
            continue
        iv, v, dist, eta, Wh = check(a, d, b)
        if not (iv and v):
            print("VIOLATION", kind, eps, iv, v)
        if dist < worst[0]:
            worst = (dist, (kind, eps, eta, Wh))
print("min |dLambda| over families:", worst, " >= eta0?", worst[0] >= eta0)
# the exact canceller of the brake family: sin eps = |X_h|/B0
a, d, b, _ = traj('brake', 0.0)
X = np.sum(((s_st - s) * a * dive)[:, None] * d, 0) * h
B0 = np.sum((s - s_st)[~dive] * a[~dive]) * h
eps = np.arcsin(np.linalg.norm(X[:2]) / B0)
a, d, b, ok = traj('brake', eps)
iv, v, dist, eta, Wh = check(a, d, b)
print(f"exact brake canceller: eps={eps:.3e} rad, eta={eta:.3e} m, |W_h|={Wh:.2e}, ratio eta/eta0={eta/eta0:.1f}, ok={ok}")
