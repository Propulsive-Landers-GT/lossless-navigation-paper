"""[verify-tvc] Independent check of the TVC-1 witness (math/06 §4.8).

1. Finds that the stored witness is NOT bang-bang on E (|n| < K1 on every early cell; cell 9 at 0.865 K1), so with
   T = rho1 and p = a1 cos(delta) it is a RELAXED (chattering) control, contrary to math/06 §3 Remark / §4.8.
2. Repair: an explicit ORDINARY control. On each early cell (split into M sub-intervals) the gimbal is bang-bang at
   +-delta (T = rho1, so p = a1 cos delta and n = +-K1 exactly) with a symmetric 3-segment pattern whose mean is the
   cell value nbar; symmetric => first moment also matches, so psi, psidot agree with the piecewise-constant profile
   at every node.  The terminal conditions psi(tf) = psidot(tf) = 0 are enforced EXACTLY by a rational correction of
   the last two (late, interior) cells.  Late: T = rho2, sin(mu) = -eps*n/a2, |mu| < delta.
3. Rigorous gain G_w of this ordinary control in the centre-of-percussion model (Lemma 2.1/2.3 exact identities):
   W_z = int (s-s*) (p - eps psidot^2) cos(psi) ds, by Arb ball integration (python-flint acb.integral) on every
   smooth segment; G_w = W_z - J0.
4. Independent full rigid-body simulation (quaternion, Euler equations, engine at -L e3, own RK4, no CoP reduction):
   terminal attitude/rate, theta_w = (r0, v0), ell = r0z + s* v0z, G_w(6DOF) = ell - kappa - J0, altitude and glide
   slope along the trajectory, gimbal/thrust limits.
usage: witness_check.py [cone|box] [M_sub]
"""
import sys
from fractions import Fraction as Fr
import numpy as np
import flint
from flint import arb, acb, ctx

ctx.prec = 128
gim = sys.argv[1] if len(sys.argv) > 1 else 'cone'
MSUB = int(sys.argv[2]) if len(sys.argv) > 2 else 8

# ---------------- exact constants ----------------
m_q, rho1_q, rho2_q, Jt_q, L_q = Fr(7988, 100), Fr(400), Fr(1000), Fr(636, 10), Fr(589, 1000)
tf_q, ss_q = Fr(1), Fr(1, 4)
g0 = arb('9.80665')
A = lambda q: arb(q.numerator) / arb(q.denominator)
m, Jt, L = A(m_q), A(Jt_q), A(L_q)
a1, a2 = A(rho1_q / m_q), A(rho2_q / m_q)
eps = Jt / (m * L)
d15 = arb.pi() / 12
de = d15 if gim == 'cone' else (d15.cos() ** 2).acos()
K1 = a1 * de.sin() / eps
tf, ss = A(tf_q), A(ss_q)
J0 = -a1 * de.cos() * ss ** 2 / 2 + a2 * (tf - ss) ** 2 / 2
kappa = g0 * tf * (ss - tf / 2)

nf = np.load(f"../proof-tvc/witness_{gim}_1.0_0.25.npy")
N = len(nf); h_q = tf_q / N; kss = int(ss_q / h_q)
K1f = float(K1.mid())
print(f"[{gim}] delta={float(de.mid())*180/np.pi:.4f} deg  K1={K1f:.10f}  early |n|/K1 min={np.min(np.abs(nf[:kss]))/K1f:.4f} "
      f"max={np.max(np.abs(nf[:kss]))/K1f:.6f}  (bang-bang requires 1)")

# exact rational cell values; fix last two cells so that sum h n = 0 and sum h n (tf-c) = 0 exactly
nq = [Fr(float(x)) for x in nf]
c = [h_q * (k + Fr(1, 2)) for k in range(N)]
S0 = sum(h_q * nq[k] for k in range(N)); S1 = sum(h_q * nq[k] * (tf_q - c[k]) for k in range(N))
i, j = N - 2, N - 1   # solve  h(dn_i + dn_j) = -S0,  h(dn_i (tf-c_i) + dn_j (tf-c_j)) = -S1
det = h_q * h_q * ((tf_q - c[j]) - (tf_q - c[i]))
dni = (-S0 * h_q * (tf_q - c[j]) + S1 * h_q) / det
dnj = (S0 * h_q * (tf_q - c[i]) - S1 * h_q) / det
nq[i] += dni; nq[j] += dnj
assert sum(h_q * nq[k] for k in range(N)) == 0 and sum(h_q * nq[k] * (tf_q - c[k]) for k in range(N)) == 0
print(f"  terminal correction: dn = ({float(dni):.2e}, {float(dnj):.2e}) on the last two cells (exact psi(tf)=psidot(tf)=0)")
K2f = float((a2 * de.sin() / eps).mid())
assert max(abs(float(x)) for x in nq[kss:]) < 0.999 * K2f
assert all(abs(float(x)) < K1f * (1 - 1e-9) for x in nq[:kss])

# ---------------- segment list (ordinary control) ----------------
# each segment: (t_start [arb], length [arb], n [arb], p [arb], T [float], sin_mu [float])
segs = []
hA = A(h_q)
for k in range(N):
    tk = A(k * h_q)
    nb = A(nq[k])
    if k < kss:
        sg = 1 if nq[k] > 0 else -1
        hs = hA / MSUB
        al = hs * (1 + abs(nb) / K1) / 4          # outer pieces 2*al at sg*K1, middle hs-2al at -sg*K1
        for jj in range(MSUB):
            t0 = tk + jj * hs
            for (st, ln, nn) in [(t0, al, sg * K1), (t0 + al, hs - 2 * al, -sg * K1), (t0 + hs - al, al, sg * K1)]:
                segs.append((st, ln, nn, a1 * de.cos(), float(rho1_q), -float(nn.mid()) * float(eps.mid()) / float(a1.mid())))
    else:
        segs.append((tk, hA, nb, (a2 ** 2 - eps ** 2 * nb ** 2).sqrt(), float(rho2_q), -float(nq[k]) * float(eps.mid()) / float(a2.mid())))

# ---------------- rigorous W_z in the CoP model ----------------
psi, om = arb(0), arb(0)
W = arb(0)
for (st, ln, nn, p, T, smu) in segs:
    def F(x, analytic, st=st, ln=ln, nn=nn, p=p, psi=psi, om=om):
        sig = x * acb(ln)
        s = acb(st) + sig
        ps = acb(psi) + acb(om) * sig + acb(nn) * sig * sig / 2
        od = acb(om) + acb(nn) * sig
        return (s - acb(ss)) * (acb(p) - acb(eps) * od * od) * ps.cos() * acb(ln)
    W += acb.integral(F, 0, 1, rel_tol=arb(2) ** -80).real
    psi = psi + om * ln + nn * ln * ln / 2
    om = om + nn * ln
G = W - J0
print(f"  end state (ball): psi(tf) in {psi.str(5, radius=True)}, psidot(tf) in {om.str(5, radius=True)}  (exactly 0 by construction)")
print(f"  RIGOROUS G_w (ordinary bang-bang, MSUB={MSUB}) in {G.str(10, radius=True)}")

# relaxed value of the original profile, for comparison (float, high resolution)
def relaxed_G(nv, M=200000):
    a1f, a2f, epsf, def_ = float(a1.mid()), float(a2.mid()), float(eps.mid()), float(de.mid())
    t = (np.arange(M) + 0.5) / M; dt = 1 / M
    k = np.minimum((t * N).astype(int), N - 1); nn = np.array([float(x) for x in nv])[k]
    om = np.concatenate([[0], np.cumsum(nn * dt)])
    psi = np.concatenate([[0], np.cumsum(om[:-1] * dt + nn * dt ** 2 / 2)])
    pm = psi[:-1] + om[:-1] * dt / 2 + nn * dt ** 2 / 8; omm = om[:-1] + nn * dt / 2
    p = np.where(t < 0.25, a1f * np.cos(def_), np.sqrt(a2f ** 2 - epsf ** 2 * nn ** 2))
    return np.sum(dt * (t - 0.25) * (p - epsf * omm ** 2) * np.cos(pm)) - float(J0.mid())
print(f"  relaxed G_w of stored profile (float, chattering p=a1 cos delta)   = {relaxed_G(nq):.6e}")
p_ord = lambda: None
# ordinary evaluation WITHOUT chattering (gimbal angle mu<delta, p = sqrt(a1^2-eps^2 n^2)): what 'no chattering' really gives
def ordinary_nochatter_G(nv, M=200000):
    a1f, a2f, epsf = float(a1.mid()), float(a2.mid()), float(eps.mid())
    t = (np.arange(M) + 0.5) / M; dt = 1 / M
    k = np.minimum((t * N).astype(int), N - 1); nn = np.array([float(x) for x in nv])[k]
    om = np.concatenate([[0], np.cumsum(nn * dt)])
    psi = np.concatenate([[0], np.cumsum(om[:-1] * dt + nn * dt ** 2 / 2)])
    pm = psi[:-1] + om[:-1] * dt / 2 + nn * dt ** 2 / 8; omm = om[:-1] + nn * dt / 2
    p = np.where(t < 0.25, np.sqrt(a1f ** 2 - epsf ** 2 * nn ** 2), np.sqrt(a2f ** 2 - epsf ** 2 * nn ** 2))
    return np.sum(dt * (t - 0.25) * (p - epsf * omm ** 2) * np.cos(pm)) - float(J0.mid())
print(f"  same profile flown literally (T=rho1, |mu|<delta, no chattering)    = {ordinary_nochatter_G(nq):.6e}")

# ---------------- independent full rigid-body simulation ----------------
mf, Jtf, Ja, Lf, g0f = float(m_q), float(Jt_q), 3.74, float(L_q), 9.80665
Jd = np.array([Jtf, Jtf, Ja])
def qmul(p, q):
    return np.array([p[0]*q[0]-p[1]*q[1]-p[2]*q[2]-p[3]*q[3], p[0]*q[1]+p[1]*q[0]+p[2]*q[3]-p[3]*q[2],
                     p[0]*q[2]-p[1]*q[3]+p[2]*q[0]+p[3]*q[1], p[0]*q[3]+p[1]*q[2]-p[2]*q[1]+p[3]*q[0]])
def rot(q, v):
    return qmul(qmul(q, np.r_[0, v]), q * np.array([1, -1, -1, -1]))[1:]
def fdyn(x, T, db):
    r, v, q, w = x[0:3], x[3:6], x[6:10], x[10:13]
    tau = np.cross(np.array([0, 0, -Lf]), T * db)          # engine pivot at -L e3 (body)
    wd = (tau - np.cross(w, Jd * w)) / Jd
    return np.r_[v, T / mf * rot(q, db) - np.array([0, 0, g0f]), 0.5 * qmul(q, np.r_[0, w]), wd]
x = np.zeros(13); x[6] = 1.0
traj_t, traj_x = [0.0], [x.copy()]
t = 0.0; maxmu = 0.0; maxcard = [0.0]
PHIC = np.arctan2(1.0, np.cos(np.pi/12)) if gim == 'box' else 0.0   # box: motion in the corner-azimuth vertical plane
for (st, ln, nn, p, T, smu) in segs:
    lnf = float(ln.mid()); maxmu = max(maxmu, abs(np.arcsin(smu)))
    db = np.array([smu * np.cos(PHIC), smu * np.sin(PHIC), np.sqrt(1 - smu ** 2)])
    if gim == 'box':   # Cardan angles in the m3tvc convention d = (cos b sin a, sin b, cos a cos b)
        cb_ = np.arcsin(db[1]); ca_ = np.arctan2(db[0], db[2]); maxcard[0] = max(maxcard[0], abs(ca_), abs(cb_))
    ns = max(4, int(np.ceil(lnf / 2e-5))); dt = lnf / ns
    for _ in range(ns):
        k1 = fdyn(x, T, db); k2 = fdyn(x + dt/2*k1, T, db); k3 = fdyn(x + dt/2*k2, T, db); k4 = fdyn(x + dt*k3, T, db)
        x = x + dt/6*(k1 + 2*k2 + 2*k3 + k4); x[6:10] /= np.linalg.norm(x[6:10]); t += dt
        traj_t.append(t); traj_x.append(x.copy())
traj_t = np.array(traj_t); traj_x = np.array(traj_x)
bT = rot(x[6:10], np.array([0, 0, 1.0])); wT = x[10:13]
v0 = -x[3:6]; r0 = -x[0:3] - t * v0                      # landing data: r(tf)=0, v(tf)=0
ell = r0[2] + 0.25 * v0[2]
G6 = ell - float(kappa.mid()) - float(J0.mid())
print(f"  6DOF sim: tf={t:.12f}  |b(tf)-e_z|={np.linalg.norm(bT-[0,0,1]):.2e}  |w(tf)|={np.linalg.norm(wT):.2e}  max gimbal {np.degrees(maxmu):.4f} deg (limit {float(de.mid())*180/np.pi:.4f})")
if gim == 'box': print(f"  box: max Cardan angle along the witness = {np.degrees(maxcard[0]):.10f} deg (limit 15)")
print(f"  6DOF sim: r0={r0}  v0={v0}  ell={ell:.10f}  G_w(6DOF)={G6:.6e}")
rphys = traj_x[:, 0:3] + r0[None, :] + traj_t[:, None] * v0[None, :]
inner = traj_t < t - 1e-9
rz, rh = rphys[inner, 2], np.hypot(rphys[inner, 0], rphys[inner, 1])
bz = 1 - 2 * (traj_x[:, 7] ** 2 + traj_x[:, 8] ** 2)
print(f"  altitude: min r_z(t<tf)={rz.min():.3e} (at t={traj_t[inner][np.argmin(rz)]:.6f}), "
      f"min r_z/|r_h| = {np.min(rz/np.maximum(rh,1e-300)):.3f}, max tilt {np.degrees(np.arccos(bz.min())):.4f} deg, max |v_h| {np.abs(traj_x[:,3:5]+v0[None,:2]).max():.3e}")
# last 10 ms detail
late = (traj_t > t - 0.01) & inner
print(f"  last 10 ms: min r_z/|r_h| = {np.min(rz[late[inner]]/np.maximum(rh[late[inner]],1e-300)):.3f}; vz<0 on [0,tf): {bool(np.all((traj_x[inner,5]+v0[2])<0))}")
np.savez(f"witness_ordinary_{gim}_M{MSUB}.npz", r0=r0, v0=v0, G6=G6, Glo=float(G.lower()), Ghi=float(G.upper()))
