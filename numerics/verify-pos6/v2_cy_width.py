"""[verify-pos6] Spot check of Theorem C-Y (math/04 §10).

Planar M3b attitude ODE for a prescribed planar thrust history: phi'' = (|T|/k) sin(phi - psi), k = J/l.
Realizable initial rates eta: |phi - psi| <= delta on [0, tf], phi(0) = phi0.
Claim: the realizable set of eta has diameter <= 2 delta mu_c / sinh(mu_c tf), mu_c^2 = rho1 cos(delta)/k.
We scan eta on a fine grid (bisection on the edges) for several thrust histories and compare.
"""
import numpy as np
from scipy.integrate import solve_ivp

J, l = 63.6, 0.589
k = J / l
rho1, rho2 = 400.0, 1000.0
delta = np.radians(15)
mu_c = np.sqrt(rho1*np.cos(delta)/k)

def make_history(kind):
    if kind == "const-min":
        return (lambda t: rho1), (lambda t: 0.0)
    if kind == "const-max":
        return (lambda t: rho2), (lambda t: 0.0)
    if kind == "slew":       # thrust direction slews at 0.1 rad/s, throttle ramps
        return (lambda t: rho1 + 300*np.sin(t)**2), (lambda t: 0.1*t)
    if kind == "primer":     # gnomonic primer arc, |T| bang-bang
        return (lambda t: rho1 if t < 0.6 else rho2), (lambda t: np.arctan(0.8*(t-0.7)) - np.arctan(-0.56))
    raise ValueError

def ok(eta, Tn, psi, tf, phi0):
    viol = lambda t, x: delta - abs(x[0] - psi(t))
    viol.terminal = True
    f = lambda t, x: [x[1], Tn(t)/k*np.sin(x[0] - psi(t))]
    s = solve_ivp(f, (0, tf), [phi0, eta], rtol=1e-11, atol=1e-13, events=viol, max_step=0.01)
    return s.status == 0 and np.all(np.abs(s.y[0] - np.array([psi(t) for t in s.t])) <= delta + 1e-12)

def realizable_interval(Tn, psi, tf, phi0, lo=-2.0, hi=2.0, n=4001):
    etas = np.linspace(lo, hi, n)
    good = [e for e in etas if ok(e, Tn, psi, tf, phi0)]
    if not good:
        return None
    a, b = min(good), max(good)
    step = etas[1]-etas[0]
    # refine both edges by bisection
    def edge(inside, outside):
        for _ in range(50):
            mid = 0.5*(inside+outside)
            if ok(mid, Tn, psi, tf, phi0): inside = mid
            else: outside = mid
        return inside
    return edge(a, a-step), edge(b, b+step)

print(f"mu_c = {mu_c:.4f} 1/s (GTPL wet, rho1=400 N, delta=15 deg)")
for tf in (0.5, 1.0, 2.0):
    bound = 2*delta*mu_c/np.sinh(mu_c*tf)
    for kind in ("const-min", "const-max", "slew", "primer"):
        Tn, psi = make_history(kind)
        for phi0 in (psi(0.0), psi(0.0) + 0.5*delta):
            iv = realizable_interval(Tn, psi, tf, phi0, lo=-1.5, hi=1.5, n=1201)
            if iv is None:
                print(f"tf={tf:3.1f} {kind:9s} phi0-psi0={phi0-psi(0):+.3f}: empty set; bound {bound:.3e}")
                continue
            w = iv[1]-iv[0]
            print(f"tf={tf:3.1f} {kind:9s} phi0-psi0={phi0-psi(0):+.3f}: width {w:.4e}  bound {bound:.4e}  ratio {w/bound:.3f}"
                  + ("  VIOLATION" if w > bound*(1+1e-6) else ""))
print(f"GTPL tf=7 s bound: rho1=400 N -> {2*delta*mu_c/np.sinh(mu_c*7):.3e} rad/s;"
      f" rho1=300 N (flight-code value) -> {2*delta*np.sqrt(300*np.cos(delta)/k)/np.sinh(np.sqrt(300*np.cos(delta)/k)*7):.3e} rad/s")
