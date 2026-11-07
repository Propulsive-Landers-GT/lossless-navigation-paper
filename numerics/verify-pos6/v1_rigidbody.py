"""[verify-pos6] Pointwise checks of the rigid-body identities used by Thm D/D*/E0 and the FLAT row.

Full rigid body, body inertia J = diag(Jt, Jt, Ja), engine pivot at -L e3 (body), thrust T d_b (body),
roll torque tau3 e3 (body) and optional extra transverse torque tau_perp (body).
World: b = R e3, bdot = R (w x e3), bddot = R (w x (w x e3) + wdot x e3), wdot from Euler.

Checks (random states, ANY roll rate w3):
 (1) Lemma 0:  Jt d/dt |w_perp|^2 / 2 = <w_perp, tau_perp>   (gyroscopic term does no work)
 (2) Lemma 1:  Jt (Pi_b bddot) = -L T g + Ja w3 (b x bdot)   (g = transverse gimbal vector, pure TVC)
 (3) centre of percussion: y = r + eps b, eps = Jt/(m L):
       yddot = (T cos mu / m - eps |w_perp|^2) b - g e3 + (Ja/(m L)) w3 (b x bdot)
     i.e. exact for w3 = 0, with the roll correction otherwise.
 (4) box-gimbal corner angle for the GTPL Cardan parametrisation vs a tangent parametrisation.
"""
import numpy as np
rng = np.random.default_rng(0)

def hat(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])

def rand_rot():
    q = rng.normal(size=4); q /= np.linalg.norm(q)
    a, b, c, d = q
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
                     [2*(b*c+a*d), a*a-b*b+c*c-d*d, 2*(c*d-a*b)],
                     [2*(b*d-a*c), 2*(c*d+a*b), a*a-b*b-c*c+d*d]])

e3 = np.array([0., 0., 1.])
worst = dict(L0=0, L1=0, cop=0, cop_noroll=0)
for _ in range(2000):
    m = rng.uniform(50, 90); L = rng.uniform(.3, .8); Jt = rng.uniform(30, 70); Ja = rng.uniform(2, 6)
    T = rng.uniform(300, 1200); g0 = 9.81
    J = np.diag([Jt, Jt, Ja])
    R = rand_rot()
    w = rng.normal(size=3) * np.array([1, 1, 0]) * 1.5
    w3 = rng.normal() * 2.0
    w[2] = w3
    mu = rng.uniform(0, .4); az = rng.uniform(0, 2*np.pi)
    db = np.array([np.sin(mu)*np.cos(az), np.sin(mu)*np.sin(az), np.cos(mu)])  # body thrust direction
    tau_rcs = np.array([0., 0., rng.normal()*3])
    tau_extra = np.array([rng.normal(), rng.normal(), 0.]) * 20  # independent transverse torque (Thm D model)
    for case in ("tvc", "decoupled"):
        tau = np.cross(-L*e3, T*db) + tau_rcs + (tau_extra if case == "decoupled" else 0)
        wdot = np.linalg.solve(J, tau - np.cross(w, J @ w))
        # (1) Lemma 0 in body coordinates
        wp = w*np.array([1, 1, 0]); taup = tau*np.array([1, 1, 0])
        lhs = Jt*np.dot(wp, wdot*np.array([1, 1, 0]))
        worst['L0'] = max(worst['L0'], abs(lhs - np.dot(wp, taup)) / (1 + abs(lhs)))
        if case == "decoupled":
            continue
        b = R @ e3; bdot = R @ np.cross(w, e3); bddot = R @ (np.cross(w, np.cross(w, e3)) + np.cross(wdot, e3))
        d = R @ db; gvec = d - np.dot(d, b)*b
        Pb = np.eye(3) - np.outer(b, b)
        res1 = Jt*(Pb @ bddot) - (-L*T*gvec + Ja*w3*np.cross(b, bdot))
        worst['L1'] = max(worst['L1'], np.abs(res1).max())
        eps = Jt/(m*L)
        rddot = T*d/m - g0*e3
        yddot = rddot + eps*bddot
        wperp2 = w[0]**2 + w[1]**2
        flat = (T*np.cos(mu)/m - eps*wperp2)*b - g0*e3
        corr = (Ja/(m*L))*w3*np.cross(b, bdot)
        worst['cop'] = max(worst['cop'], np.abs(yddot - flat - corr).max())
        worst['cop_noroll'] = max(worst['cop_noroll'], np.abs(yddot - flat).max())
print("max residuals over 2000 random states (any roll rate):")
for k, v in worst.items():
    print(f"  {k:11s} {v:.2e}")
print("  (cop_noroll is the size of the roll correction that the w3=0 identity omits)")
# also: b x bdot equals the world transverse angular velocity
R = rand_rot(); w = np.array([.3, -.7, 1.1])
print("  |b x bdot - R w_perp| =", np.abs(np.cross(R@e3, R@np.cross(w, e3)) - R@(w*np.array([1, 1, 0]))).max())

# (4) corner angle of a +-15 deg per-axis box
d15 = np.radians(15)
th1 = th2 = d15
cardan = np.array([np.sin(th2)*np.cos(th1), -np.sin(th1), np.cos(th1)*np.cos(th2)])  # GTPL MPC parametrisation
tang = np.array([np.tan(d15), np.tan(d15), 1.0]); tang /= np.linalg.norm(tang)
print(f"corner angle, Cardan (GTPL: tx=sin th cos ph, ty=sin ph, tz=cos th cos ph): {np.degrees(np.arccos(cardan[2])):.3f} deg"
      f" = arccos(cos^2 15deg) = {np.degrees(np.arccos(np.cos(d15)**2)):.3f}")
print(f"corner angle, tangent parametrisation: {np.degrees(np.arccos(tang[2])):.3f} deg")
# inscribed cone of the Cardan box: min over boundary of angle from e3
best = 90
for t in np.linspace(-d15, d15, 401):
    for (a, c) in ((d15, t), (t, d15)):
        v = np.array([np.sin(c)*np.cos(a), -np.sin(a), np.cos(a)*np.cos(c)])
        best = min(best, np.degrees(np.arccos(v[2])))
print(f"inscribed cone of the Cardan box: {best:.3f} deg")
