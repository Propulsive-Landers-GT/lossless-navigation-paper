"""[verify-tvc] Independent, rigorous re-verification of the TVC-1 SDP certificate (math/06 §4.5-4.7, Lemma 4.6').

What is independent of proof-tvc's code: every matrix is re-assembled here by EXACT polynomial integration on each
sub-cell (fmpq rational matrices for the basis/weight part, Arb balls for the transcendental coefficients
cos/sin(delta), cos(phibar), ...), the cellwise remainder constants use the true sup over each sub-cell (endpoint of
the linear weight), Mlate is the exact minimum of the step-linear torque multiplier, and the final matrix inequality
-M >= 0 is decided by an EXACT integer Bareiss elimination (all leading principal minors > 0) of the rounded,
congruence-scaled midpoint matrix minus a rigorous bound on (ball radius + rounding) times I.

What is taken from proof-tvc (validated separately): the localized step functions phibar, vbar (checked against an
independent re-implementation in loc_check.py: theirs >= mine on all 20000 cells), the multipliers lambda (stored
.npz; any lambda that passes these checks is a valid certificate), and the free splitting parameters theta(s).
usage: exact_cert.py N gim roll rho0 rhow [kapg]
"""
import sys, time, math
from fractions import Fraction as Fr
import numpy as np
from flint import arb, fmpq, fmpq_mat, arb_mat, ctx

ctx.prec = 200
N, gim, roll = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
rho0_q, rhow_q = Fr(sys.argv[4]), Fr(sys.argv[5])
kapg_q = Fr(sys.argv[6]) if len(sys.argv) > 6 else Fr(10)
th = np.load(f"theirs_{gim}_{N}_roll{roll}.npz")
t0 = time.time()

def A(q):            # exact rational -> arb (exact if dyadic, else 200-bit ball)
    q = Fr(q); return arb(q.numerator) / arb(q.denominator)
def Q(x):            # float -> exact rational
    return Fr(float(x))
def me2q(a):         # exact arb (mid or rad) -> Fraction
    mm, ee = a.man_exp(); return Fr(int(mm)) * (Fr(2) ** int(ee))
def lowq(x): return me2q(x.mid()) - me2q(x.rad())
def highq(x): return me2q(x.mid()) + me2q(x.rad())
# ---- constants (exact) ----
m_q, rho1_q, rho2_q, Jt_q, L_q, Ja_q, taur_q = Fr(7988, 100), Fr(400), Fr(1000), Fr(636, 10), Fr(589, 1000), Fr(374, 100), Fr(3)
tf_q, ss_q = Fr(1), Fr(1, 4)
zeta_q = xi_q = Fr(1, 10); tau_q = Fr(3, 100); taup_q = Fr(1, 100); taurho_q = Fr(1, 5); kap_q = Fr(1, 100)
lam_max_q = Fr(3, 1000); rhoc_q = Fr(1, 10); eta1 = 2; nsub = 3; r_theta = 0.2; gg = Fr(1)
m, Jt, L, Ja = A(m_q), A(Jt_q), A(L_q), A(Ja_q)
a1, a2 = A(rho1_q / m_q), A(rho2_q / m_q)
eps = Jt / (m * L); rJ = Ja / Jt
d15 = arb.pi() / 12
de = d15 if gim == 'cone' else (d15.cos() ** 2).acos()
K1, K2 = a1 * de.sin() / eps, a2 * de.sin() / eps
zeta, xi, tau, taup, taurho, kap = map(A, (zeta_q, xi_q, tau_q, taup_q, taurho_q, kap_q))
lam_max, rhoc, rho0, rhow, kapg = A(lam_max_q), A(rhoc_q), A(rho0_q), A(rhow_q), A(kapg_q)
h_q = tf_q / N; h = A(h_q); kss = int(ss_q / h_q); assert kss * h_q == ss_q
ss, tf = A(ss_q), A(tf_q)
kappa_D = 2 * K1 * de.tan() / eps + (a2 - a1 * de.cos()) * de.tan() ** 2 / eps ** 2
twopi = 2 * arb.pi()
# crude (A1)/(A2) regime
assert (K2 * (tf / 2) ** 2 / 2) < arb.pi() / 2 - arb('0.05')
assert a1 * de.cos() - eps * (K2 * tf / 2) ** 2 > 0

# ---- localized step functions (validated by loc_check.py) ----
pcells, vcells, dsf = th['phicells'], th['vcells'], float(th['ds'])
def cellmax(cells, lo, hi):
    i0 = max(int(np.floor(lo / dsf)) - 1, 0); i1 = min(int(np.ceil(hi / dsf)) + 1, len(cells))
    return float(np.max(cells[i0:i1]))
def theta_of(vb):
    er = 2 * (float(eps.mid()) ** 2) * vb ** 4 / float(a2.mid()) ** 2
    return 1e-3 if er <= 0 else float(np.clip(1 / (1 + r_theta / er), 1e-3, 0.9))
om3bar = (lambda s_q: taur_q / Ja_q * s_q) if roll else (lambda s_q: Fr(0))

# ---- exact polynomial integration on sub-cells ----
n2 = 2 * N
def basis_polys(k, lo_q):
    """rows: 2N basis functions (N constants, N slopes) restricted to a sub-cell of cell k, as polynomials in
    sigma = s - lo (coefficients of 1, sigma, sigma^2, sigma^3), for x and xdot."""
    PX = [[Fr(0)] * 4 for _ in range(n2)]; PV = [[Fr(0)] * 4 for _ in range(n2)]
    for i in range(k):
        ci = h_q * (i + Fr(1, 2))
        PX[i] = [h_q * (lo_q - ci), h_q, Fr(0), Fr(0)]; PV[i] = [h_q, Fr(0), Fr(0), Fr(0)]
        PX[N + i] = [-h_q ** 3 / 12, Fr(0), Fr(0), Fr(0)]
    s0 = lo_q - k * h_q        # sig = s0 + sigma
    PX[k] = [s0 ** 2 / 2, s0, Fr(1, 2), Fr(0)]; PV[k] = [s0, Fr(1), Fr(0), Fr(0)]
    # X1 = sig^3/6 - h sig^2/4 ; Xd1 = sig^2/2 - h sig/2
    PX[N + k] = [s0 ** 3 / 6 - h_q * s0 ** 2 / 4, s0 ** 2 / 2 - h_q * s0 / 2, s0 / 2 - h_q / 4, Fr(1, 6)]
    PV[N + k] = [s0 ** 2 / 2 - h_q * s0 / 2, s0 - h_q / 2, Fr(1, 2), Fr(0)]
    return (fmpq_mat(n2, 4, [fmpq(c.numerator, c.denominator) for r in PX for c in r]),
            fmpq_mat(n2, 4, [fmpq(c.numerator, c.denominator) for r in PV for c in r]))
def hankel(dq, w0, w1, deg_extra=0):
    mu = [dq ** (j + 1) / (j + 1) for j in range(9)]
    return fmpq_mat(4, 4, [fmpq(*(lambda c: (c.numerator, c.denominator))(w0 * mu[a + b] + w1 * mu[a + b + 1]))
                           for a in range(4) for b in range(4)])
def F2q(c): return fmpq(c.numerator, c.denominator)

Kp = arb_mat(n2, n2); Km = arb_mat(n2, n2); Lsum = arb_mat(n2, n2); Vall = arb_mat(n2, n2)
G0 = [arb(0)] * n2; Gw = [arb(0)] * n2
Mlate = [None] * N
csubs = []           # per sub-cell data for remainder constants
dq = h_q / nsub
for k in range(N):
    for j in range(nsub):
        lo_q = k * h_q + j * dq; hi_q = lo_q + dq
        lo, hi = float(lo_q), float(hi_q)
        ph = A(Q(cellmax(pcells, lo, hi))); vbf = cellmax(vcells, lo, hi); vb = A(Q(vbf))
        cph = ph.cos()
        o3 = A(om3bar(hi_q)); cg3 = eps * rJ * o3; cq3 = rJ * o3 / cph
        early = hi_q <= ss_q
        PX, PV = basis_polys(k, lo_q)
        PXt, PVt = PX.transpose(), PV.transpose()
        sgn = Fr(1) if early else Fr(-1)                       # |s - s*| = sgn*(s* - s) ... as linear in sigma
        w0, w1 = (ss_q - lo_q, Fr(-1)) if early else (lo_q - ss_q, Fr(1))
        Hw = hankel(dq, w0, w1); H1 = hankel(dq, Fr(1), Fr(0))
        Wx = arb_mat(PX * Hw * PXt); Wv = arb_mat(PV * Hw * PVt); Ux = arb_mat(PX * H1 * PXt); Uv = arb_mat(PV * H1 * PVt)
        cL = 2 * (1 + 1 / kap) * vb ** 4; cLd = 2 * (1 + 1 / kap) * cq3 ** 2
        Lsum += Ux * cL + Uv * cLd
        wmax_sub = A(max(abs(lo_q - ss_q), abs(hi_q - ss_q)))
        if early:
            cA = a1 * de.cos() / (1 + cph) + cg3 * A(gg) / 2
            cB = eps / cph ** 2 + cg3 / (2 * A(gg))
            Kp += Wx * cA + Wv * cB
            fac = 1 + 1 / tau
        else:
            thq = Q(theta_of(vbf)); tht = A(thq)
            A2e = a2 / 2 - (1 / tht - 1) * eps ** 2 * 2 * vb ** 4 / (2 * a2)
            B2e = eps * cph - (1 / tht - 1) * eps ** 2 * 2 * cq3 ** 2 / (2 * a2)
            cA = (1 - zeta) * A2e - cg3 * A(gg) / 2; cB = (1 - zeta) * B2e - cg3 / (2 * A(gg))
            assert cA > 0 and cB > 0, "late form not NSD"
            Km -= Wx * cA + Wv * cB
            fac = 1 / taup - 1
            c2min = (1 - zeta) * A(lo_q - ss_q) * (1 - tht) * eps ** 2 * cph ** 2 / (2 * a2)
            c2lo = lowq(c2min)                                   # exact rational lower bound of the multiplier
            Mlate[k] = c2lo if Mlate[k] is None else min(Mlate[k], c2lo)
        if roll:     # gyro lateral force: c_hat = eps rJ om3bar / cos(phibar) (sup on sub-cell), int c_hat xdot^2
            chat = eps * rJ * o3 / cph
            Vall += Uv * chat
        else:
            chat = arb(0)
        # linear functionals m0 = int f0 x, m_w = int (s-s*) f0 x : exact moments of polynomials
        f0 = a1 * de.cos() if early else a2
        mu = [A(dq ** (jj + 1) / (jj + 1)) for jj in range(6)]
        PXl = PX.entries()
        for i in range(n2):
            cfs = [A(Fr(int(PXl[4 * i + a].p), int(PXl[4 * i + a].q))) for a in range(4)]
            if all(c == 0 for c in cfs): continue
            I0 = sum((cfs[a] * mu[a] for a in range(4)), arb(0)); I1 = sum((cfs[a] * mu[a + 1] for a in range(4)), arb(0))
            G0[i] = G0[i] + f0 * I0
            Gw[i] = Gw[i] + f0 * (A(lo_q - ss_q) * I0 + I1)
        csubs.append(dict(k=k, early=early, fac=fac, cA=cA * wmax_sub, cB=cB * wmax_sub, cL=cL, cLd=cLd, chat=chat, ph=ph))
for k in range(kss):
    Mlate[k] = Fr(0)
# use min(mine, theirs): both are valid lower bounds of the torque multiplier, so this checks THEIR inequality (or a
# stronger one) -- never a weaker one
Mlate = [A(max(min(x, Q(t) - Fr(1, 10 ** 15) if t > 0 else Fr(0)), Fr(0))) for x, t in zip(Mlate, th['Mlate'])]
print(f"assembled in {time.time()-t0:.1f}s", flush=True)

# clamp functionals xdot(tf) = int n, x(tf) = int (tf - t) n
Cm = arb_mat(2, n2)
for k in range(N):
    Cm[0, k] = h; Cm[1, k] = h * (tf - h * (k + arb(1) / 2)); Cm[1, N + k] = -h ** 3 / 12
G0m = arb_mat(1, n2, G0); Gwm = arb_mat(1, n2, Gw)
Wd = [h] * N + [h ** 3 / 12] * N

# ---- multipliers from the stored certificate (exact rationals) ----
lam = [A(Q(x)) for x in th['lam']]
# ---- gyro lateral-force weights (R1): Cg0 = int c_hat, Cgw = int w^2 c_hat (exact for the step c_hat on sub-cells) ----
Cg0 = sum((d['chat'] * A(dq) for d in csubs), arb(0))
Cgw = arb(0)
for idx, d in enumerate(csubs):
    l_q = (idx // nsub) * h_q + (idx % nsub) * dq; u_q = l_q + dq
    Cgw += d['chat'] * A(((u_q - ss_q) ** 3 - (l_q - ss_q) ** 3) / 3)
coefV = (1 + 1 / kapg) * (rho0 * Cg0 + rhow * Cgw) if roll else arb(0)

# ---- the matrix ----
Amat = Kp * (1 + tau) + Km * (1 - taup) - (G0m.transpose() * G0m * rho0 + Gwm.transpose() * Gwm * rhow) * (1 - taurho) \
       - Cm.transpose() * Cm * ((1 - taup) * rhoc) + Lsum * ((1 + tau) * lam_max) + Vall * ((1 + tau) * coefV)
Mmat = Amat
for i in range(n2):
    k = i % N
    Mmat[i, i] = Mmat[i, i] - Wd[i] * (lam[k] + Mlate[k])
# compare with proof-tvc's float matrix
Mf = np.array([[float(Mmat[i, j].mid()) for j in range(n2)] for i in range(n2)])
Sc = 1 / np.sqrt(np.array([float(w.mid()) for w in Wd]))
diff = np.abs((Mf - th['Mv']) * Sc[:, None] * Sc[None, :]).max()
Mlf = np.array([float(x.mid()) for x in Mlate])
print(f"max |M_mine - M_theirs| (scaled) = {diff:.3e};  Mlate mine - theirs: min {np.min(Mlf - th['Mlate']):.3e} max {np.max(Mlf - th['Mlate']):.3e}")
evs = np.linalg.eigvalsh((Mf + Mf.T) / 2 * Sc[:, None] * Sc[None, :])
print(f"float top eigenvalue of scaled M_mine = {evs.max():.4e}")

# ---- exact decision of -M > 0 ----
Sq = [Fr(1 / np.sqrt(float(w.mid()))).limit_denominator(10 ** 6) for w in Wd]   # rational congruence scaling
SqA = [A(s) for s in Sq]
E = 64
rad2 = arb(0); Bint = [[0] * n2 for _ in range(n2)]
for i in range(n2):
    for j in range(n2):
        e = -(Mmat[i, j] * SqA[i] * SqA[j])
        mq = me2q(e.mid())
        bi = round(mq * 2 ** E)
        Bint[i][j] = bi
        err = abs(mq - Fr(bi, 2 ** E)) + me2q(e.rad())
        rad2 += A(err) ** 2
for i in range(n2):          # symmetrize exactly (both halves are rigorous enclosures of the same symmetric matrix)
    for j in range(i + 1, n2):
        a_, b_ = Bint[i][j], Bint[j][i]
        Bint[i][j] = Bint[j][i] = (a_ + b_) // 2
radF = rad2.sqrt() + A(Fr(n2, 2 ** E))          # Frobenius bound on radius + rounding + symmetrization
def bareiss_pd(Bm):
    n = len(Bm); Mx = [row[:] for row in Bm]; prev = 1; mins = []
    for k in range(n):
        piv = Mx[k][k]
        if piv <= 0: return False, k, mins
        mins.append(piv)
        rk = Mx[k]
        for i in range(k + 1, n):
            ri = Mx[i]; a_ik = ri[k]
            for j in range(k + 1, n):
                ri[j] = (piv * ri[j] - a_ik * rk[j]) // prev
        prev = piv
    return True, n, mins
def certify(shift_q):
    """exact check of  -M  >=  (radF + shift) I  in the scaled basis"""
    sh = highq(radF + A(shift_q))
    s_int = math.ceil(sh * 2 ** E)
    Bm = [[Bint[i][j] - (s_int if i == j else 0) for j in range(n2)] for i in range(n2)]
    ok, k, _ = bareiss_pd(Bm)
    return ok, k
print(f"rigorous radius (Frobenius, incl. rounding) = {float(radF.upper()):.3e}", flush=True)
t1 = time.time(); ok, kfail = certify(Fr(0)); print(f"EXACT Bareiss: -M - radF*I > 0 : {ok} (failed at {kfail})  [{time.time()-t1:.0f}s]", flush=True)
margin_shift = Fr(0)
if ok:
    for sh in [Fr(1, 10 ** 9), Fr(1, 10 ** 8), Fr(2, 10 ** 8), Fr(1, 10 ** 7)]:
        okk, _ = certify(sh)
        if okk: margin_shift = sh
        else: break
    print(f"certified eigen-margin (scaled units): >= {float(margin_shift):.1e}")

# ---- remainder constants and multiplier bounds (Lemma 4.6', Def 4.5 (i),(ii)) ----
cg = (1 / taurho - 1) * (rho0 * a2 ** 2 + rhow * (a2 * A(max(ss_q, tf_q - ss_q))) ** 2) * h ** 4 * tf / 64
ok_lb = ok_ub = True; worst_lb = None
for k in range(N):
    subs = [d for d in csubs if d['k'] == k]
    cv = max((d['fac'] * abs(d['cB']) + (1 + 1 / tau) * lam_max * d['cLd'] for d in subs), key=lambda x: float(highq(x)))
    cx = max((d['fac'] * abs(d['cA']) + (1 + 1 / tau) * lam_max * d['cL'] for d in subs), key=lambda x: float(highq(x)))
    cloc = cv * (h / twopi) ** 2 + cx * h * h ** 3 / (4 * arb.pi() ** 2)
    if roll:
        cloc += (1 + 1 / tau) * coefV * max((d['chat'] for d in subs), key=lambda x: float(highq(x))) * (h / twopi) ** 2
    slack = lam[k] + Mlate[k] - cloc - cg
    if not slack > 0: ok_lb = False
    worst_lb = slack if worst_lb is None or float(slack.mid()) < float(worst_lb.mid()) else worst_lb
    if not (lam[k] >= 0 and lam[k] <= lam_max): ok_ub = False
    if k < kss - eta1:
        phc = max((d['ph'] for d in subs), key=lambda x: float(highq(x)))
        if not (lam[k] * (1 + kap) * kappa_D <= (1 - xi) * (ss - h * (k + 1)) * phc.cos()): ok_ub = False
print(f"remainder condition lam_k + Mlate_k >= c_loc,k + c_g on all cells: {ok_lb} (worst slack {worst_lb.str(4, radius=False)})")
print(f"absorption (i) and lam <= lam_max (ii): {ok_ub}")

# ---- value ----
Nb2 = [(1 + kap) * (K1 ** 2 if k < kss - eta1 else K2 ** 2) for k in range(N)]
V = h * sum((lam[k] * Nb2[k] for k in range(N)), arb(0))
print(f"V_lambda in {V.str(10, radius=True)}   (theirs {float(th['V']):.10e})")
np.save(f"exact_{gim}_{N}_roll{roll}.npy", np.array([float(V.upper()), float(margin_shift), float(ok), float(ok_lb), float(ok_ub)]))
print(f"total time {time.time()-t0:.0f}s")
