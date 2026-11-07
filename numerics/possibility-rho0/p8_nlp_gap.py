"""3D NLP check of Theorem P0-F: distance from the midpoint theta_m to F_tf (M1, rho1=0, alpha=0), multistart ipopt.
Inner discretisation: b nodes on S^2, <b_k,b_{k+1}> >= cos(omega h); per-interval constant u_k with |u_k| <= a2 and
<u_k, b_k>, <u_k, b_{k+1}> >= |u_k| cos(delta)  (caps geodesically convex => admissible in continuous time).
NLP value = upper bound on dist(theta_m, F) (any NLP point is admissible).  Also checks witnesses are (near) feasible."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, casadi as ca, sys, json
from face import witness
T = float(sys.argv[1]); dd = float(sys.argv[2]); N = int(sys.argv[3]); nstart = int(sys.argv[4])
om, a2, g = 0.4, 12.5, 9.80665; dl = np.deg2rad(dd)
W = witness(T, dl, om, a2, g, n=100001); tf = W["tf"]; h = tf/N
th1, th2, thm = W["theta1"], W["theta2"], W["theta_m"]
def X_to_theta(I, J):
    v0 = ca.vertcat(0, 0, g*tf) - I
    r0 = -v0*tf + ca.vertcat(0, 0, g*tf**2/2) - J
    return ca.vertcat(r0, v0)
b = ca.SX.sym("b", 3, N+1); u = ca.SX.sym("u", 3, N)
cons, lb, ub = [], [], []
for k in range(N+1):
    cons.append(ca.sumsqr(b[:, k])); lb.append(1); ub.append(1)
cons.append(b[:, 0] - ca.DM([0, 0, 1])); lb += [0]*3; ub += [0]*3
for k in range(N):
    cons.append(ca.dot(b[:, k], b[:, k+1])); lb.append(np.cos(om*h)); ub.append(1)
    nu = ca.sqrt(ca.sumsqr(u[:, k]) + 1e-10)
    cons.append(ca.sumsqr(u[:, k])); lb.append(0); ub.append(a2**2)
    for kk in (k, k+1):
        cons.append(ca.dot(u[:, k], b[:, kk]) - np.cos(dl)*nu); lb.append(0); ub.append(ca.inf)
w = np.array([(tf - k*h)**2/2 - (tf - (k+1)*h)**2/2 for k in range(N)])
I = h*ca.sum2(u); J = ca.mtimes(u, ca.DM(w))
th = X_to_theta(I, J)
obj = ca.sumsqr(th - ca.DM(thm))
x = ca.vertcat(ca.vec(b), ca.vec(u))
S = ca.nlpsol("S", "ipopt", {"x": x, "f": obj, "g": ca.vertcat(*cons)},
              {"ipopt.print_level": 0, "print_time": 0, "ipopt.max_iter": 3000, "ipopt.tol": 1e-10})
rng = np.random.default_rng(1)
def init_from(beta_fn, uscale):
    s = np.linspace(0, tf, N+1); be = beta_fn(s)
    az = rng.uniform(-np.pi, np.pi)*0
    B = np.stack([np.sin(be), 0*s, np.cos(be)]); U = uscale*a2*(B[:, :-1] + B[:, 1:])/2
    return np.concatenate([B.T.ravel(), U.T.ravel()])
def rand_init():
    s = np.linspace(0, tf, N+1); kn = rng.normal(size=(3, 4))
    tilt = np.cumsum(rng.uniform(-1, 1, N+1))*om*h*0.9; tilt -= tilt[0]
    az = np.cumsum(rng.normal(0, 0.3, N+1))
    B = np.stack([np.sin(tilt)*np.cos(az), np.sin(tilt)*np.sin(az), np.cos(tilt)])
    U = rng.uniform(0, 1, N)*a2*(B[:, :-1] + B[:, 1:])/2
    return np.concatenate([B.T.ravel(), U.T.ravel()])
best = (np.inf, None)
inits = [rand_init() for _ in range(nstart)]
for be in [W["beta1"], W["beta2"]]:
    sig = W["sigma_hat"]
    f = lambda s, be=be: np.where(om*s <= sig, np.maximum(-om*s, be - (sig - om*s)), be + (om*s - sig))
    for sc in (0.3, 0.5, 0.8): inits.append(init_from(f, sc))
for x0 in inits:
    r = S(x0=x0, lbg=ca.vertcat(*[ca.DM(l) if not isinstance(l, ca.DM) else l for l in lb]) if False else ca.vertcat(*[ca.DM(np.atleast_1d(l)) for l in lb]),
          ubg=ca.vertcat(*[ca.DM(np.atleast_1d(v)) for v in ub]))
    st = S.stats()["return_status"]
    if st in ("Solve_Succeeded", "Solved_To_Acceptable_Level"):
        d = float(np.sqrt(float(r["f"])))
        if d < best[0]: best = (d, np.array(r["x"]).ravel())
print(json.dumps(dict(T=T, delta_deg=dd, N=N, tf=tf, sigma=W["sigma"], beta1=W["beta1"], beta2=W["beta2"],
    theta1=W["theta1"].tolist(), theta2=W["theta2"].tolist(), theta_m=thm.tolist(),
    sep=float(np.linalg.norm(th1-th2)), rz_min=[W["rz_min1"], W["rz_min2"]], pI=[W["pI1"], W["pI2"]],
    face=[W["face1"], W["face2"]], nlp_min_dist=best[0], nstarts=len(inits)), indent=1))
