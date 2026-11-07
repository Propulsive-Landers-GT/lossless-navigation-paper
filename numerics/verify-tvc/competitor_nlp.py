"""[verify-tvc] Sanity check (lower bound on the competitor supremum): best ZERO-LATERAL relaxed competitor found by
multistart NLP, planar (psi) and spatial (h = (h1,h2), exact unit-sphere dynamics), R0, constant mass.
Relaxed control u in C(b): p = <u,b> in [a1 cos d, a2], q perp b, |q| <= p tan d, p^2+|q|^2 <= a2^2.
Torque: eps * nabla bdot = -q.  y-identity: W_z = int (s-s*) (p - eps v^2) b_z.  Lateral: int f h = 0, int s f h = 0.
If any competitor exceeded U_tot the certificate would be wrong.  usage: competitor_nlp.py [cone|box] [planar|spatial] starts
"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, casadi as ca
gim = sys.argv[1] if len(sys.argv) > 1 else 'cone'; mode = sys.argv[2] if len(sys.argv) > 2 else 'planar'
starts = int(sys.argv[3]) if len(sys.argv) > 3 else 8
m, rho1, rho2, Jt, L = 79.88, 400., 1000., 63.6, 0.589
de = np.pi/12 if gim == 'cone' else np.arccos(np.cos(np.pi/12)**2)
a1, a2, eps = rho1/m, rho2/m, Jt/(m*L); tf, ss = 1.0, 0.25
J0 = -a1*np.cos(de)*ss**2/2 + a2*(tf-ss)**2/2
N = 80; h = tf/N; sub = 4
best = None; rng = np.random.default_rng(1)
for st in range(starts):
    o = ca.Opti()
    p = o.variable(N); dim = 1 if mode == 'planar' else 2
    qv = o.variable(dim, N)
    # state: b (3), bdot (3) for spatial; psi, psid for planar
    if mode == 'planar':
        psi, om = 0, 0
    else:
        b = ca.DM([0, 0, 1]); bd = ca.DM([0, 0, 0])
    W = 0; lat0 = 0; lat1 = 0
    for k in range(N):
        o.subject_to(p[k] >= a1*np.cos(de)); o.subject_to(p[k]**2 + ca.sumsqr(qv[:, k]) <= a2**2)
        o.subject_to(ca.sumsqr(qv[:, k]) <= (p[k]*np.tan(de))**2)
        for j in range(sub):
            dt = h/sub; s = k*h + (j+.5)*dt
            if mode == 'planar':
                n = -qv[0, k]/eps
                pm = psi + om*dt/2 + n*dt**2/8; omm = om + n*dt/2
                f = p[k] - eps*omm**2
                W += dt*(s-ss)*f*ca.cos(pm); lat0 += dt*f*ca.sin(pm); lat1 += dt*s*f*ca.sin(pm)
                psi = psi + om*dt + n*dt**2/2; om = om + n*dt
            else:
                # tangent basis at b: e1 = normalize(ex - (ex.b)b), e2 = b x e1 ; q = q1 e1 + q2 e2
                def acc(b, bd):
                    ex = ca.DM([1, 0, 0]); e1 = ex - ca.dot(ex, b)*b; e1 = e1/ca.norm_2(e1); e2 = ca.cross(b, e1)
                    q = qv[0, k]*e1 + qv[1, k]*e2
                    return -q/eps - ca.sumsqr(bd)*b
                k1b, k1v = bd, acc(b, bd)
                k2b, k2v = bd + dt/2*k1v, acc(b + dt/2*k1b, bd + dt/2*k1v)
                k3b, k3v = bd + dt/2*k2v, acc(b + dt/2*k2b, bd + dt/2*k2v)
                k4b, k4v = bd + dt*k3v, acc(b + dt*k3b, bd + dt*k3v)
                bm = b + dt/2*k1b; bdm = bd + dt/2*k1v
                f = p[k] - eps*ca.sumsqr(bdm)
                W += dt*(s-ss)*f*bm[2]; lat0 += dt*f*bm[0:2]; lat1 += dt*s*f*bm[0:2]
                b = b + dt/6*(k1b + 2*k2b + 2*k3b + k4b); bd = bd + dt/6*(k1v + 2*k2v + 2*k3v + k4v)
                b = b/ca.norm_2(b)
    if mode == 'planar':
        o.subject_to(psi == 0); o.subject_to(om == 0)
    else:
        o.subject_to(b[0:2] == 0); o.subject_to(bd == 0)
    o.subject_to(lat0 == 0); o.subject_to(lat1 == 0)
    o.minimize(-(W - J0)*1e4)
    o.set_initial(p, a1*np.cos(de) + rng.uniform(0, 1, N)*(a2 - a1))
    o.set_initial(qv, rng.uniform(-1, 1, (dim, N))*a1*np.sin(de)*0.8)
    o.solver('ipopt', {'ipopt.print_level': 0, 'print_time': 0, 'ipopt.sb': 'yes', 'ipopt.max_iter': 3000, 'ipopt.tol': 1e-10})
    try:
        sol = o.solve(); val = float(sol.value(W - J0))
    except RuntimeError:
        try: val = float(o.debug.value(W - J0)); stat = 'fail'
        except Exception: continue
        print(f"  start {st}: not converged ({val:.3e})", flush=True); continue
    print(f"  start {st}: zero-lateral gain = {val:.4e}", flush=True)
    if best is None or val > best: best = val
print(f"[{gim} {mode}] best zero-lateral relaxed competitor gain found = {best:.4e}  (certified U_tot cone N=120: 6.27e-5; box N=60: 1.33e-4)")
