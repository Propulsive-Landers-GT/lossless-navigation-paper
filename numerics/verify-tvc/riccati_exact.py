"""[verify-tvc] Independent rigorous re-check of TVC-2 (math/06 §5.7): tf=2, s*=1/2, no cap, Nf=600 Riccati certificate.
Independent of proof-tvc's code except for: the localization step tables (validated by loc_check2.py) and the
stored multipliers lambda.
 * per-cell stage matrices on v=(x_k, x'_k, a, b) by EXACT polynomial integration on the 3 sub-cells
   (fmpq polynomial part x Arb coefficients); moment rows g0, gw exact; transition with exact h = 1/300;
 * backward recursion H_k = S_k + lam_k L_k - (lam_k+Mlate_k) diag(0,0,h,h^3/12) + T_k^T P_{k+1} T_k in Arb (256 bit),
   -H_uu > 0 certified by (-H_11 > 0, det H_uu > 0); NO inflation/deflation fudge needed (all data are balls);
 * Lemma 4.6' floors with true sub-cell sups, absorption (i), lam <= lam_max, V_lambda -- all in Arb;
 * float cross-checks: (a) my stage data vs proof-tvc's fine_data; (b) DENSE 1200x1200 eigen test of the same form
   (independent of the Riccati logic).
"""
import sys, time, os
from fractions import Fraction as Fr
import numpy as np
from flint import arb, arb_mat, fmpq, fmpq_mat, ctx
ctx.prec = 256
TF = os.environ.get("TF", "2"); CAP = os.environ.get("CAP", "none")
th = np.load(f"theirs_riccati_{float(Fr(TF))}_{CAP}.npz")
t0 = time.time()
def A(q): q = Fr(q); return arb(q.numerator) / arb(q.denominator)
def Q(x): return Fr(float(x))
def me2q(a): mm, ee = a.man_exp(); return Fr(int(mm)) * (Fr(2) ** int(ee))
def lowq(x): return me2q(x.mid()) - me2q(x.rad())
# constants
m_q, rho1_q, rho2_q, Jt_q, L_q = Fr(7988, 100), Fr(400), Fr(1000), Fr(636, 10), Fr(589, 1000)
tf_q, ss_q = Fr(TF), Fr(1, 2); Nf = int(300 * tf_q)
zeta_q = xi_q = Fr(15, 100); kap_q = Fr(3, 100); lam_max_q = Fr(1, 100)
tau_q, taup_q, taurho_q, rhoc_q, rho0_q, rhow_q = Fr(3, 100), Fr(1, 100), Fr(1, 5), Fr(1, 10), Fr(1, 10), Fr(45)
eta1_q = Fr(os.environ['ETA1']) if 'ETA1' in os.environ else Fr(1, 15); nsub = 3; r_theta = 0.2
m, Jt, L = A(m_q), A(Jt_q), A(L_q); a1, a2 = A(rho1_q / m_q), A(rho2_q / m_q); eps = Jt / (m * L)
de = arb.pi() / 12; K1, K2 = a1 * de.sin() / eps, a2 * de.sin() / eps
zeta, xi, kap, lam_max, tau, taup, taurho, rhoc, rho0, rhow = map(A, (zeta_q, xi_q, kap_q, lam_max_q, tau_q, taup_q, taurho_q, rhoc_q, rho0_q, rhow_q))
h_q = tf_q / Nf; h = A(h_q); kss = int(ss_q / h_q); assert kss * h_q == ss_q
ss, tf = A(ss_q), A(tf_q)
kappa_D = 2 * K1 * de.tan() / eps + (a2 - a1 * de.cos()) * de.tan() ** 2 / eps ** 2
if CAP == 'none': assert K2 * (tf / 2) ** 2 / 2 < arb.pi() / 2 - arb('0.02')          # (A1) a priori
else: assert A(Fr(CAP)) < 90                                                            # (A1) from the class's tilt cap
pc, vc, dsf = th['phicells'], th['vcells'], float(th['ds'])
def cellmax(cells, lo, hi):
    i0 = max(int(np.floor(lo / dsf)) - 1, 0); i1 = min(int(np.ceil(hi / dsf)) + 1, len(cells)); return float(np.max(cells[i0:i1]))
def theta_of(vb):
    er = 2 * float(eps.mid()) ** 2 * vb ** 4 / float(a2.mid()) ** 2
    return 1e-3 if er <= 0 else float(np.clip(1 / (1 + r_theta / er), 1e-3, 0.9))
def F2(c): return fmpq(c.numerator, c.denominator)
def polys(s0):     # px, pv as polynomials in sigma, tt = s0 + sigma ; rows = (x_k, x'_k, a, b)
    PX = [[Fr(1), 0, 0, 0], [s0, Fr(1), 0, 0], [s0 ** 2 / 2, s0, Fr(1, 2), 0],
          [s0 ** 3 / 6 - h_q * s0 ** 2 / 4, s0 ** 2 / 2 - h_q * s0 / 2, s0 / 2 - h_q / 4, Fr(1, 6)]]
    PV = [[0, 0, 0, 0], [Fr(1), 0, 0, 0], [s0, Fr(1), 0, 0], [s0 ** 2 / 2 - h_q * s0 / 2, s0 - h_q / 2, Fr(1, 2), 0]]
    return (fmpq_mat(4, 4, [F2(Fr(c)) for r in PX for c in r]), fmpq_mat(4, 4, [F2(Fr(c)) for r in PV for c in r]))
def hank(dq, w0, w1):
    mu = [dq ** (j + 1) / (j + 1) for j in range(9)]
    return fmpq_mat(4, 4, [F2(w0 * mu[a + b] + w1 * mu[a + b + 1]) for a in range(4) for b in range(4)])
dq = h_q / nsub
S, Lk, g0, gw, Ml, cloc, phc, Nb2, lamub = [], [], [], [], [], [], [], [], []
cg = (1 / taurho - 1) * (rho0 * a2 ** 2 + rhow * (a2 * A(max(ss_q, tf_q - ss_q))) ** 2) * h ** 4 * tf / 64
for k in range(Nf):
    tk = k * h_q
    Sk = arb_mat(4, 4); Lkk = arb_mat(4, 4); g0k = [arb(0)] * 4; gwk = [arb(0)] * 4
    c2min = None; cv = cx = cLm = arb(0); phmax = arb(0)
    for j in range(nsub):
        lo_q = tk + j * dq; hi_q = lo_q + dq
        ph = A(Q(cellmax(pc, float(lo_q), float(hi_q)))); vbf = cellmax(vc, float(lo_q), float(hi_q)); vb = A(Q(vbf))
        phmax = ph if float(ph.mid()) > float(phmax.mid()) else phmax
        cph = ph.cos(); early = hi_q <= ss_q
        PX, PV = polys(lo_q - tk); PXt, PVt = PX.transpose(), PV.transpose()
        w0, w1 = (ss_q - lo_q, Fr(-1)) if early else (lo_q - ss_q, Fr(1))
        Hw = hank(dq, w0, w1); H1 = hank(dq, Fr(1), Fr(0))
        Wx = arb_mat(PX * Hw * PXt); Wv = arb_mat(PV * Hw * PVt); Ux = arb_mat(PX * H1 * PXt)   # PX[i,a]: basis i, sigma^a
        cL = 2 * (1 + 1 / kap) * vb ** 4
        wsup = A(max(abs(lo_q - ss_q), abs(hi_q - ss_q)))
        if early:
            Ax = a1 * de.cos() / (1 + cph); Bv = eps / cph ** 2; fac = 1 + tau; fr = 1 + 1 / tau
            Sk += (Wx * Ax + Wv * Bv) * fac
        else:
            tq = Q(theta_of(vbf)); tt = A(tq)
            A2e = a2 / 2 - (1 / tt - 1) * eps ** 2 * 2 * vb ** 4 / (2 * a2)
            Ax = (1 - zeta) * A2e; Bv = (1 - zeta) * eps * cph; fac = 1 - taup; fr = 1 / taup - 1
            assert Ax > 0 and Bv > 0
            Sk -= (Wx * Ax + Wv * Bv) * fac
            c2 = lowq((1 - zeta) * A(lo_q - ss_q) * (1 - tt) * eps ** 2 * cph ** 2 / (2 * a2))
            c2min = c2 if c2min is None else min(c2min, c2)
        Lkk += Ux * ((1 + tau) * cL)
        for cand, store in ((fr * Bv * wsup, 'v'), (fr * Ax * wsup, 'x'), (cL, 'L')):
            if store == 'v' and float(cand.mid()) > float(cv.mid()): cv = cand
            if store == 'x' and float(cand.mid()) > float(cx.mid()): cx = cand
            if store == 'L' and float(cand.mid()) > float(cLm.mid()): cLm = cand
        f0 = a1 * de.cos() if early else a2
        mu = [A(dq ** (jj + 1) / (jj + 1)) for jj in range(6)]
        for i in range(4):
            cf = [A(Fr(int(PX[i, a].p), int(PX[i, a].q))) for a in range(4)]
            I0 = sum((cf[a] * mu[a] for a in range(4)), arb(0)); I1 = sum((cf[a] * mu[a + 1] for a in range(4)), arb(0))
            g0k[i] = g0k[i] + f0 * I0; gwk[i] = gwk[i] + f0 * (A(lo_q - ss_q) * I0 + I1)
    S.append(Sk); Lk.append(Lkk); g0.append(g0k); gw.append(gwk)
    Ml.append(c2min if c2min is not None else Fr(0))
    phc.append(phmax)
    cloc.append(cv * (h / (2 * arb.pi())) ** 2 + cx * h ** 4 / (4 * arb.pi() ** 2) + (1 + 1 / tau) * lam_max * cLm * h ** 4 / (4 * arb.pi() ** 2))
    if (k + 1) * h_q <= ss_q - eta1_q:
        Nb2.append((1 + kap) * K1 ** 2); lamub.append(True)
    else:
        Nb2.append((1 + kap) * K2 ** 2); lamub.append(False)
print(f"stage matrices assembled in {time.time()-t0:.0f}s", flush=True)

# ---- multipliers ----
lam = [A(Q(x)) for x in th['lam']]
Ml = [A(max(min(x, Q(t) - Fr(1, 10**15)) if t > 0 else Fr(0), Fr(0))) if k >= kss else arb(0) for k, (x, t) in enumerate(zip(Ml, th['Mlate']))]
# ---- float cross-check (a): my stage data vs theirs ----
f = lambda M_: np.array([[float(M_[i, j].mid()) for j in range(M_.ncols())] for i in range(M_.nrows())])
dS = max(np.abs(f(S[k]) - th['S'][k]).max() / max(np.abs(th['S'][k]).max(), 1e-300) for k in range(Nf))
dL = max(np.abs(f(Lk[k]) - th['Lk'][k]).max() / max(np.abs(th['Lk'][k]).max(), 1e-300) for k in range(Nf))
dg = max(max(abs(float(g0[k][i].mid()) - th['g0'][k][i]) for i in range(4)) for k in range(Nf))
dM = max(float(Ml[k].mid()) - th['Mlate'][k] for k in range(Nf))
print(f"vs proof-tvc fine_data: max rel diff S {dS:.2e}, L {dL:.2e}; max abs diff g0 {dg:.2e}; Mlate (min-ed) diff {dM:.1e}")
# ---- rigorous backward recursion ----
Tx = arb_mat([[1, h, 0, 0, h * h / 2, -h ** 3 / 12], [0, 1, 0, 0, h, 0]])
P = arb_mat(4, 4)
P[0, 0] = -(1 - taup) * rhoc; P[1, 1] = -(1 - taup) * rhoc; P[2, 2] = -(1 - taurho) * rho0; P[3, 3] = -(1 - taurho) * rhow
ok = True; worst = -1e300; kfail = None
idx = [0, 1, 4, 5]
for k in range(Nf - 1, -1, -1):
    Sv = S[k] + Lk[k] * lam[k]
    Sv[2, 2] -= (lam[k] + Ml[k]) * h; Sv[3, 3] -= (lam[k] + Ml[k]) * h ** 3 / 12
    H = arb_mat(6, 6)
    for a in range(4):
        for b in range(4): H[idx[a], idx[b]] = Sv[a, b]
    T = arb_mat(4, 6)
    for b in range(6): T[0, b] = Tx[0, b]; T[1, b] = Tx[1, b]
    T[2, 2] = 1; T[3, 3] = 1
    for a in range(4):
        T[2, idx[a]] += g0[k][a]; T[3, idx[a]] += gw[k][a]
    H = H + T.transpose() * P * T
    H11, H12, H21, H22 = H[4, 4], H[4, 5], H[5, 4], H[5, 5]
    det = H11 * H22 - H12 * H21
    if not ((-H11) > 0 and det > 0):
        ok = False; kfail = k; break
    # normalized pivot (for reporting): largest eigenvalue of scaled H_uu (float)
    sc = np.array([1 / np.sqrt(float(h.mid())), 1 / np.sqrt(float((h ** 3 / 12).mid()))])
    Hu = np.array([[float(H11.mid()), float(H12.mid())], [float(H21.mid()), float(H22.mid())]]) * np.outer(sc, sc)
    worst = max(worst, np.linalg.eigvalsh((Hu + Hu.T) / 2).max())
    inv = arb_mat([[H22 / det, -H12 / det], [-H21 / det, H11 / det]])
    Huz = arb_mat([[H[4, j] for j in range(4)], [H[5, j] for j in range(4)]])
    Hzz = arb_mat([[H[i, j] for j in range(4)] for i in range(4)])
    P = Hzz - Huz.transpose() * inv * Huz
maxrad = max(float(P[i, j].rad()) for i in range(4) for j in range(4))
print(f"Arb Riccati recursion: all -H_uu > 0 certified: {ok}" + (f" (failed at cell {kfail})" if not ok else "") +
      f";  worst scaled pivot eigenvalue {worst:.3e};  final ball radius {maxrad:.1e}  [{time.time()-t0:.0f}s]", flush=True)
# ---- Lemma 4.6' floors, absorption, bounds, V ----
ok_lb = all(lam[k] + Ml[k] - cloc[k] - cg > 0 for k in range(Nf))
worst_lb = min(float((lam[k] + Ml[k] - cloc[k] - cg).mid()) for k in range(Nf))
ok_ub = all(lam[k] >= 0 and lam[k] <= lam_max for k in range(Nf))
ok_abs = all((not lamub[k]) or (lam[k] * (1 + kap) * kappa_D <= (1 - xi) * (ss - h * (k + 1)) * phc[k].cos()) for k in range(Nf))
V = h * sum((lam[k] * Nb2[k] for k in range(Nf)), arb(0))
print(f"floors lam+Mlate >= c_loc+c_g: {ok_lb} (worst slack {worst_lb:.2e});  0<=lam<=lam_max: {ok_ub};  absorption (i): {ok_abs}")
print(f"V_lambda in {V.str(10, radius=True)}")
np.save(f"riccati_exact_{float(tf_q)}_{CAP}.npy", np.array([float(V.upper().mid()) + float(V.rad()), float(ok), float(ok_lb), float(ok_ub and ok_abs)]))
# ---- float cross-check (b): dense eigen test of the same form, independent of the Riccati logic ----
n2 = 2 * Nf
Z = np.zeros((4, n2)); Fm = np.zeros((n2, n2))
Txf = np.array([[1, 1/300, 0, 0, (1/300)**2/2, -(1/300)**3/12], [0, 1, 0, 0, 1/300, 0]]); assert h_q == Fr(1, 300)
for k in range(Nf):
    Sv = f(S[k]) + float(lam[k].mid()) * f(Lk[k]); Sv[2, 2] -= float((lam[k] + Ml[k]).mid()) / 300; Sv[3, 3] -= float((lam[k] + Ml[k]).mid()) / 300**3 / 12
    E = np.zeros((2, n2)); E[0, k] = 1; E[1, Nf + k] = 1
    Vk = np.vstack([Z[0:2], E])                        # (x_k, x'_k, a, b) as linear maps of u
    Fm += Vk.T @ Sv @ Vk
    g0f = np.array([float(x.mid()) for x in g0[k]]); gwf = np.array([float(x.mid()) for x in gw[k]])
    Znew = np.zeros_like(Z)
    Znew[0:2] = Txf[:, [0, 1]] @ Z[0:2] + Txf[:, [4, 5]] @ E
    Znew[2] = Z[2] + g0f @ Vk; Znew[3] = Z[3] + gwf @ Vk
    Z = Znew
Pt = np.diag([-(0.99) * 0.1, -(0.99) * 0.1, -(0.8) * 0.1, -(0.8) * 45])
Fm += Z.T @ Pt @ Z
Wd = np.r_[np.full(Nf, 1/300), np.full(Nf, (1/300)**3/12)]; Sc = 1 / np.sqrt(Wd)
ev = np.linalg.eigvalsh((Fm + Fm.T) / 2 * Sc[:, None] * Sc[None, :])
print(f"dense 1200x1200 float test of the same form: top eigenvalue = {ev.max():.4e} (must be < 0)")
if len(sys.argv) > 1 and sys.argv[1] == 'diag':
    rels = [(np.abs(f(Lk[k]) - th['Lk'][k]).max() / np.abs(th['Lk'][k]).max(), k) for k in range(Nf)]
    r, kk = max(rels); print("worst L cell", kk, r); print(f(Lk[kk])); print(th['Lk'][kk])
    rels = [(np.abs(f(S[k]) - th['S'][k]).max() / np.abs(th['S'][k]).max(), k) for k in range(Nf)]
    r, kk = max(rels); print("worst S cell", kk, r); print(f(S[kk])); print(th['S'][kk])
