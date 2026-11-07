"""Theorem P0-F witness (math/possibility-rho0.md): sign-change face with axis p_hat = (cos d, 0, -sin d)
(delta below horizontal), functional <p_hat, int (s - sigma) a d ds>.  M1, rho1=0, alpha=0, b(0)=e_z, b(tf) free.
Units: omega=1, a2=1 inside V; physical scaling in witness()."""
import os; os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

def V(bs, sig, T, dl, n=3000):
    bs = np.atleast_1d(np.asarray(bs, float))
    s1 = np.linspace(0, sig, n)[None, :]
    L = np.maximum(-s1, bs[:, None] - (sig - s1))
    E = np.trapezoid((sig - s1) * np.maximum(0, np.sin(np.minimum(2*dl - L, np.pi/2))), s1, axis=1)
    t = np.linspace(0, T - sig, n)[None, :]
    Lt = np.trapezoid(t * np.maximum(0, np.sin(bs[:, None] + t)), t, axis=1)
    return E + Lt

def AB(sig, T, dl, nb=2001):
    tau = T - sig
    A = V(-sig, sig, T, dl)[0]
    bs = np.linspace(-tau, sig, nb); v = V(bs, sig, T, dl)
    return A, v.max(), bs[np.argmax(v)]

def tie(T, dl):
    lo, hi = T/2, T
    fa = AB(lo, T, dl); fb = AB(hi, T, dl)
    assert fa[1] > fa[0] and fb[1] < fb[0], (fa, fb)
    for _ in range(45):
        m = 0.5*(lo+hi); A, B, _ = AB(m, T, dl)
        if B > A: lo = m
        else: hi = m
    sig = 0.5*(lo+hi); A, B, b2 = AB(sig, T, dl, nb=8001)
    return sig, -sig, b2, A, B

def controls(bs, sig, T, dl, s):
    be = np.where(s <= sig, np.maximum(-s, bs - (sig - s)), bs + (s - sig))
    early = s < sig
    ang = np.where(early, be - dl, be + dl)                     # signed tilt of d toward +x
    contrib = np.where(early, np.sin(np.minimum(2*dl - be, np.pi/2)), np.sin(be))
    a = (contrib > 1e-15).astype(float)
    return be, ang, a

def witness(T, dl, omega, a2, g, n=200001):
    """physical witness: returns dict with both trajectories (landing at r=v=0 at tf) and midpoint data."""
    sig, b1, b2, A, B = tie(T, dl)
    tf = T/omega; s_hat = np.linspace(0, T, n); s = s_hat/omega
    out = dict(T=T, delta=dl, omega=omega, tf=tf, sigma_hat=sig, sigma=sig/omega, beta1=b1, beta2=b2, A=A, B=B)
    for k, bs in (("1", b1), ("2", b2)):
        be, ang, a = controls(bs, sig, T, dl, s_hat)
        u = a2*a[:, None]*np.stack([np.sin(ang), 0*s, np.cos(ang)], 1)
        acc = u + np.array([0, 0, -g])
        # backward integration from r(tf)=v(tf)=0
        h = s[1]-s[0]
        v = np.zeros_like(acc); r = np.zeros_like(acc)
        cum = np.concatenate([[0*acc[0]], np.cumsum(0.5*(acc[1:]+acc[:-1])*h, 0)])
        v = cum - cum[-1]                       # v(t) = -int_t^tf acc
        cr = np.concatenate([[0*v[0]], np.cumsum(0.5*(v[1:]+v[:-1])*h, 0)])
        r = cr - cr[-1]
        I = np.trapezoid(u, s, axis=0); J = np.trapezoid((tf - s)[:, None]*u, s, axis=0)
        out["X"+k] = np.concatenate([I, J]); out["theta"+k] = np.concatenate([r[0], v[0]])
        out["rz_min"+k] = r[:, 2].min(); out["traj"+k] = (s, r, v, be, ang, a)
    out["theta_m"] = 0.5*(out["theta1"]+out["theta2"])
    phat = np.array([np.cos(dl), 0, -np.sin(dl)])
    out["pI1"], out["pI2"] = phat@out["X1"][:3], phat@out["X2"][:3]
    n = np.concatenate([(tf - sig/omega)*phat, -phat])
    out["face1"], out["face2"] = n@out["X1"], n@out["X2"]
    return out

if __name__ == "__main__":
    for (T, dd) in [(0.05, 15), (0.3, 15), (0.6, 15), (1.0, 15), (0.5, 0), (1.0, 0), (0.6, 30), (1.4, 5)]:
        dl = np.deg2rad(dd)
        sig, b1, b2, A, B = tie(T, dl)
        print(f"T=omega*tf={T} delta={dd}: sigma_c/tf={sig/T:.4f}  maximisers beta*/sigma = -1 and {b2/sig:+.4f}  A={A:.6g} B={B:.6g}")
