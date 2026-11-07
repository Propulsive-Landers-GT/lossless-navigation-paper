"""[proof-tvc] State-space (Riccati / dynamic-programming) certificate for Theorem TVC-1 at long horizons.
Same inequality chain as certificate2.py (math/06 §4), but the discrete matrix inequality on the cellwise-linear
space is checked by a BACKWARD RICCATI RECURSION on the state z=(x, x', m0, mw) with cell control u=(a,b)
(n = a + b (t-c_k) on cell k).  Cost O(N): allows N ~ 10^3 cells, so the Lemma 4.6' remainder floors become
negligible.  The multiplier lambda is generated from a coarse dense SDP (NOT part of the proof) and checked here.
Rigour: stage/transition matrices are exact integrals (Gauss-Legendre exact for the polynomial integrands with
sub-cell-frozen conservative coefficients); the recursion is re-run in Arb ball arithmetic (python-flint) on
rationalized, conservatively-rounded data (exact_riccati()).
"""
import os, sys, json
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
from fractions import Fraction
import certificate2 as C2
from witness_nl import gtpl, segments_bangbang, evaluate_segments
from localize import localize

GLx, GLw = np.polynomial.legendre.leggauss(6)

def fine_data(P, tf, ss, Nf, par, loc, rho, rhoc):
    """Per-cell stage matrices S_k (4x4 on v=(x_k,x'_k,a,b), without the -lambda term), moment rows,
    Mlate_k, Nb2_k, lam_ub_k, remainder floors lam_lb_k."""
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    zeta, xi, kap, lam_max = par['zeta'], par['xi'], par['kap'], par['lam_max']
    tau, taup, taur = par['tau'], par['taup'], par.get('taurho', 0.2)
    K1 = a1*np.sin(de)/eps; K2 = a2*np.sin(de)/eps
    vbar, phibar = loc
    h = tf/Nf; tk = np.arange(Nf+1)*h; kss = int(round(ss/h)); assert abs(kss*h-ss) < 1e-12
    def cellmax(fun, lo, hi):
        i0 = max(int(np.floor(lo/fun.ds))-1, 0); i1 = min(int(np.ceil(hi/fun.ds))+1, len(fun.cells))
        return float(np.max(fun.cells[i0:i1]))
    def theta_of(vb):
        er = 2*eps**2*(vb**4)/a2**2
        return 1e-3 if er <= 0 else float(np.clip(1/(1+par['r_theta']/er), 1e-3, 0.9))
    S = np.zeros((Nf, 4, 4)); Lk = np.zeros((Nf, 4, 4)); g0 = np.zeros((Nf, 4)); gw = np.zeros((Nf, 4))
    Mlate = np.zeros(Nf); cloc = np.zeros(Nf)
    nsub = par['nsub']
    for k in range(Nf):
        Sk = np.zeros((4, 4)); wsup = max(abs(tk[k]-ss), abs(tk[k+1]-ss)); cvmax = 0.0; cxmax = 0.0; cLmax = 0.0
        c2min = np.inf
        for j in range(nsub):
            lo = tk[k]+j*h/nsub; hi = lo+h/nsub
            ph = cellmax(phibar, lo, hi); vb = cellmax(vbar, lo, hi); early = hi <= ss+1e-15
            th = theta_of(vb)
            cL = 2*(1+1/kap)*vb**4
            if early:
                Ax = a1*np.cos(de)/(1+np.cos(ph)); Bv = eps/np.cos(ph)**2; fac = 1+tau; sgn = 1.0
            else:
                A2e = a2/2 - (1/th-1)*eps**2*2*vb**4/(2*a2)
                Ax = (1-zeta)*A2e; Bv = (1-zeta)*eps*np.cos(ph); fac = 1-taup; sgn = -1.0
                c2min = min(c2min, (1-zeta)*(lo-ss)*(1-th)*eps**2*np.cos(ph)**2/(2*a2))
            fr = (1+1/tau) if early else (1/taup-1)
            cvmax = max(cvmax, fr*Bv); cxmax = max(cxmax, fr*Ax); cLmax = max(cLmax, cL)
            for x, w in zip(GLx, GLw):
                s = (lo+hi)/2+(hi-lo)/2*x; ws = w*(hi-lo)/2; tt = s-tk[k]
                px = np.array([1, tt, tt**2/2, tt**3/6-h*tt**2/4]); pv = np.array([0, 1, tt, tt**2/2-h*tt/2])
                wabs = abs(s-ss)
                Sk += ws*(fac*sgn*wabs*(Ax*np.outer(px, px)+Bv*np.outer(pv, pv)))
                Lk[k] += ws*(1+tau)*cL*np.outer(px, px)       # multiplied by lambda_k in the check (exact, local)
                f0 = a1*np.cos(de) if s <= ss else a2
                g0[k] += ws*f0*px; gw[k] += ws*(s-ss)*f0*px
        S[k] = Sk
        Mlate[k] = max(c2min, 0.0) if k >= kss else 0.0
        cloc[k] = cvmax*wsup*(h/(2*np.pi))**2 + cxmax*wsup*h*h**3/(4*np.pi**2) \
                  + (1+1/tau)*lam_max*cLmax*h*h**3/(4*np.pi**2)
    rho0, rhow = rho
    cg = (1/taur-1)*(rho0*a2**2 + rhow*(a2*max(ss, tf-ss))**2)*h**4*tf/64
    lam_lb = np.maximum(cloc+cg-Mlate, 0.0)*1.02
    kappa_D = 2*K1*np.tan(de)/eps + (a2-a1*np.cos(de))*np.tan(de)**2/eps**2
    Nb2 = np.zeros(Nf); lam_ub = np.full(Nf, lam_max)
    e1 = par['eta1_time']
    for k in range(Nf):
        if tk[k+1] <= ss - e1 + 1e-12:
            Nb2[k] = (1+kap)*K1**2
            lam_ub[k] = min(lam_max, (1-xi)*(ss-tk[k+1])*np.cos(phibar(np.array([tk[k+1]]))[0])/((1+kap)*kappa_D))
        else:
            Nb2[k] = (1+kap)*K2**2
    return dict(S=S, Lk=Lk, g0=g0, gw=gw, Mlate=Mlate, lam_lb=lam_lb, lam_ub=lam_ub, Nb2=Nb2, h=h, tk=tk, Nf=Nf,
                terminal=np.diag([(1-taup)*rhoc, (1-taup)*rhoc, (1-taur)*rho0, (1-taur)*rhow]))

def transition(h):
    # z' = T [x, x', m0, mw, a, b] ; moments added by caller
    return np.array([[1, h, 0, 0, h**2/2, -h**3/12], [0, 1, 0, 0, h, 0]], float)

def riccati_check(FD, lam, return_min=False):
    """Backward recursion; returns (ok, worst max-eigenvalue of H_uu normalized)."""
    Nf, h = FD['Nf'], FD['h']; Pz = -FD['terminal'].copy(); worst = -np.inf
    Tx = transition(h)
    for k in range(Nf-1, -1, -1):
        # w = (x, x', m0, mw, a, b); stage on (x, x', a, b)
        H = np.zeros((6, 6)); idx = [0, 1, 4, 5]
        Sk = FD['S'][k] + lam[k]*FD['Lk'][k] - np.diag([0, 0, h, h**3/12])*(lam[k]+FD['Mlate'][k])
        H[np.ix_(idx, idx)] += Sk
        T = np.zeros((4, 6)); T[0:2] = Tx; T[2, 2] = 1; T[3, 3] = 1
        T[2, [0, 1, 4, 5]] += FD['g0'][k]; T[3, [0, 1, 4, 5]] += FD['gw'][k]
        H += T.T@Pz@T
        Huu = H[4:, 4:]; Huz = H[4:, :4]; Hzz = H[:4, :4]
        sc = np.array([1/np.sqrt(h), 1/np.sqrt(h**3/12)])
        e = np.linalg.eigvalsh(Huu*np.outer(sc, sc)).max()
        worst = max(worst, e)
        if e >= 0: return (False, worst, k)
        Pz = Hzz - Huz.T@np.linalg.solve(Huu, Huz); Pz = (Pz+Pz.T)/2
    return (True, worst, -1)

def exact_riccati(FD, lam, prec=int(os.environ.get("ARBPREC", "512"))):
    """Arb-ball re-run of the recursion on rationalized data (conservative rounding: the stage matrix is rounded
    UP in the PSD direction by adding a tiny multiple of the identity (eps_r * diag scale), the multiplier term
    rounded DOWN). Returns True iff every H_uu is certified negative definite (via Arb Cholesky of -H_uu)."""
    import flint
    flint.ctx.prec = prec
    arb, arb_mat = flint.arb, flint.arb_mat
    Nf, h = FD['Nf'], FD['h']
    hq = Fraction(h).limit_denominator(10**12); assert abs(float(hq)-h) < 1e-15
    def A(x): return arb(Fraction(float(x)).numerator)/arb(Fraction(float(x)).denominator)
    def M(m): return arb_mat([[A(v) for v in row] for row in m])
    epsr = 1e-10
    P = M(-FD['terminal'])
    for k in range(Nf-1, -1, -1):
        Sk = FD['S'][k] + lam[k]*FD['Lk'][k]; scale = np.abs(Sk).max()
        Sk_up = Sk + epsr*scale*np.eye(4)                       # conservative: makes the form larger
        lamterm = (lam[k]+FD['Mlate'][k])*(1-1e-12)              # conservative: smaller multiplier
        H6 = np.zeros((6, 6)); idx = [0, 1, 4, 5]
        H6[np.ix_(idx, idx)] = Sk_up
        Hs = M(H6)
        hA = A(h)
        Hs[4, 4] -= A(lamterm)*hA; Hs[5, 5] -= A(lamterm)*hA*hA*hA/12
        T = np.zeros((4, 6)); T[0, :] = [1, h, 0, 0, h**2/2, -h**3/12]; T[1, :] = [0, 1, 0, 0, h, 0]; T[2, 2] = 1; T[3, 3] = 1
        T[2, [0, 1, 4, 5]] += FD['g0'][k]; T[3, [0, 1, 4, 5]] += FD['gw'][k]
        TA = M(T)
        H = Hs + TA.transpose()*P*TA
        Huu = arb_mat([[H[4, 4], H[4, 5]], [H[5, 4], H[5, 5]]])
        # -Huu positive definite  <=>  -Huu[0,0] > 0 and det(-Huu) > 0
        if not ((-Huu[0, 0]) > 0 and (Huu[0, 0]*Huu[1, 1]-Huu[0, 1]*Huu[1, 0]) > 0):
            return False, k
        Huz = arb_mat([[H[4, j] for j in range(4)], [H[5, j] for j in range(4)]])
        Hzz = arb_mat([[H[i, j] for j in range(4)] for i in range(4)])
        det = Huu[0, 0]*Huu[1, 1]-Huu[0, 1]*Huu[1, 0]
        inv = arb_mat([[Huu[1, 1]/det, -Huu[0, 1]/det], [-Huu[1, 0]/det, Huu[0, 0]/det]])
        P = Hzz - Huz.transpose()*inv*Huz
    return True, -1

def main():
    tf = float(sys.argv[1]); ss = float(sys.argv[2]); Nc = int(sys.argv[3]); Nf = int(sys.argv[4])
    cap = None if sys.argv[5] == 'none' else np.deg2rad(float(sys.argv[5]))
    rho = tuple(float(y) for y in sys.argv[6].split(':')); rhoc = 0.1
    P = gtpl()
    par = dict(C2.PAR); par.update(tau=0.03, zeta=float(os.environ.get("ZETA","0.1")), xi=float(os.environ.get("ZETA","0.1")), lam_max=float(os.environ.get("LAMMAX", "0.01")), kap=float(os.environ.get("KAP", "0.1")), cap=cap)
    vf, pf, info, _ = localize(P, tf, ss, cap=cap)
    print("localization:", {k: round(float(v), 5) for k, v in info.items()}, flush=True)
    os.environ["FASTL"] = "1"; os.environ["NOFLOOR"] = "1"
    D = C2.setup(P, tf, ss, Nc, par, loc=(vf, pf))
    if os.environ.get("GEN") == "kelley":
        cE = np.cos(min(D['K2']*ss**2/2, cap if cap else np.pi))
        D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0']
        mt = C2.moment_term(D, rho); print(f"moment term {mt:.4e}", flush=True)
        par['eta1_time'] = float(os.environ.get("ETA1", par['eta1_cells']*tf/Nc))
        FD = fine_data(P, tf, ss, Nf, par, (vf, pf), rho, rhoc)
        G = evaluate_segments(P, tf, ss, segments_bangbang(P, tf, ss, np.load(f"witness_cone_{tf}_{ss}.npy")))['G']
        lam, its = kelley(FD, iters=int(os.environ.get("KITERS", "4000")))
        if lam is None: print("RESULT: kelley did not converge"); return
        for safety in [1.02, 1.05, 1.1]:
            l2 = np.minimum((lam-FD['lam_lb'])*safety + FD['lam_lb'], np.maximum(FD['lam_ub'], FD['lam_lb']))
            ok, w, k = riccati_check(FD, l2)
            if not ok: continue
            okx, kx = exact_riccati(FD, l2); U = FD['h']*np.sum(l2*FD['Nb2']) + mt
            print(f"RESULT tf={tf} s*={ss} cap={sys.argv[5]} Nf={Nf} rho={rho} (kelley {its} it, safety {safety}): U_total={U:.6e}  G_w={G:.6e}  margin={(G-U)/G*100:.2f}%  exact Arb recursion={'PASS' if okx else 'FAIL'}  certificate={'PASS' if (okx and G>U) else 'FAIL'}", flush=True)
            np.savez(f"riccati_{tf}_{ss}_{sys.argv[5]}_{Nf}.npz", lam=l2, U=U, G=G, rho=rho)
            if okx: return
        print("RESULT: safety scaling failed"); return
    cE = np.cos(min(D['K2']*ss**2/2, cap if cap else np.pi))
    D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0']
    if os.environ.get("GENFILE"):
        c = dict(lam=np.zeros(Nc), val=float('nan'))       # generator comes from file (see below)
    elif os.environ.get("GEN", "") == "deg0":
        # generator: the rigorous coarse LMI restricted to cell-constant n (Finsler rho, caps), Clarabel; NOT the proof
        import cvxpy as cp
        hc = D['h']; idx = np.arange(Nc); tau_, taup_ = par['tau'], par['taup']
        Rm = np.diag(rho)
        A = (1+tau_)*D['Kp'] + (1-taup_)*D['Km'] - 0.8*D['G'].T@Rm@D['G'] - (1-taup_)*rhoc*D['C'].T@D['C'] + (1+tau_)*par['lam_max']*sum(D['Lk'])
        A = A[np.ix_(idx, idx)]; A = (A+A.T)/2/hc
        lamv = cp.Variable(Nc)
        sdiag = 1/np.sqrt(1 + np.abs(np.diag(A))/1e-3)        # diagonal congruence preconditioning
        As_ = A*np.outer(sdiag, sdiag)
        pr = cp.Problem(cp.Minimize(hc*cp.sum(cp.multiply(lamv, D['Nb2']))),
                        [lamv >= 0, lamv <= D['lam_ub'], (As_ - cp.diag(cp.multiply(sdiag**2, lamv+D['Mlate']))) << 0])
        try: pr.solve(solver='CLARABEL')
        except Exception:
            pr.solve(solver='SCS', eps=1e-9, max_iters=200000)
        c = None if lamv.value is None else dict(lam=np.maximum(lamv.value, 0), val=pr.value)
    elif os.environ.get("GEN", "") == "ideal":
        # generator from the idealized exact-weighted-moment SDP (deg 0, Clarabel); NOT part of the proof
        import cvxpy as cp
        pari = dict(par); pari.update(zeta=1e-9, xi=1e-9, kap=1e-9, ideal_theta=1, eta1_cells=0, lam_max=1.0)
        Di = C2.setup(P, tf, ss, Nc, pari, loc=(vf, pf)); hc = Di['h']; idx = np.arange(Nc)
        A = (Di['Kp']+Di['Km'])[np.ix_(idx, idx)]; G0 = Di['G'][0][idx]; Gw = Di['G'][1][idx]; Cc = Di['C'][:, idx]
        cons = np.vstack([Gw, Cc]); u_, s_, vt = np.linalg.svd(cons); Z = vt[np.sum(s_ > 1e-12*s_[0]):].T
        Sc = 1/np.sqrt(np.full(Nc, hc)); Zy = Z/Sc[:, None]; As = (A-rho[0]*np.outer(G0, G0))*Sc[:, None]*Sc[None, :]
        lamv = cp.Variable(Nc); Mx = Zy.T@As@Zy - Zy.T@cp.diag(lamv+Di['Mlate'])@Zy
        pr = cp.Problem(cp.Minimize(hc*cp.sum(cp.multiply(lamv, Di['Nb2']))), [lamv >= 0, (Mx+Mx.T)/2 << 0]); pr.solve(solver='CLARABEL')
        c = dict(lam=np.maximum(lamv.value, 0), val=pr.value)
    else:
        c = C2.solve_cert(D, rho, rhoc)
    if c is None:
        print("coarse SDP (Clarabel) failed; retry with SCS (generator only)", flush=True)
        os.environ["SOLVER"] = "SCS"; c = C2.solve_cert(D, rho, rhoc)
    if c is None: print("coarse SDP failed"); return
    lam_c = c['lam']; print(f"coarse (no-floor) SDP value {c['val']:.5e}", flush=True)
    mt = C2.moment_term(D, rho); print(f"moment term {mt:.4e}", flush=True)
    par['eta1_time'] = float(os.environ.get("ETA1", par['eta1_cells']*tf/Nc))
    FD = fine_data(P, tf, ss, Nf, par, (vf, pf), rho, rhoc)
    ratio = Nf//Nc; assert Nf % Nc == 0
    if os.environ.get("GENFILE"):
        # generator: a stored fine multiplier on the same fine step h (e.g. the tf=2 certificate), padded with zeros
        lf = np.load(os.environ["GENFILE"])['lam']; lam_c = None
        basef = np.zeros(Nf); basef[:min(Nf, len(lf))] = lf[:min(Nf, len(lf))]
    sm = int(os.environ.get("SMOOTH", "0"))
    if sm > 0 and not os.environ.get("GENFILE"):   # max-filter the coarse generator over +-sm coarse cells (generator heuristic only)
        lam_c = np.array([lam_c[max(0, i-sm):i+sm+1].max() for i in range(len(lam_c))])
    if os.environ.get("GENFILE"):
        base = basef
    else:
        print("  coarse lambda near s*:", np.round(lam_c[max(0, int(round(ss/(tf/Nc)))-6):int(round(ss/(tf/Nc)))+3], 5), flush=True)
        base = np.repeat(lam_c, ratio)
    G = evaluate_segments(P, tf, ss, segments_bangbang(P, tf, ss, np.load(f"witness_cone_{tf}_{ss}.npy")))['G']
    best = None
    def trial(f):
        lam = np.maximum(base*f, 0) + FD['lam_lb']
        lam = np.minimum(lam, FD['lam_ub'])
        if np.any(lam < FD['lam_lb']): return None
        ok, worst, kfail = riccati_check(FD, lam)
        return (ok, lam, FD['h']*np.sum(lam*FD['Nb2']))
    if os.environ.get("REPAIR") == "1":
        # failure-guided local increase of the generator (multiplier search only; the final lambda is re-checked)
        lamr = np.maximum(base, 0) + FD['lam_lb']; wid = int(os.environ.get("RWID", "15"))
        for itr in range(3000):
            ok, worst, kf = riccati_check(FD, lamr)
            if ok: break
            a_, b_ = max(0, kf-wid), min(Nf, kf+wid+1)
            lamr[a_:b_] = np.minimum(lamr[a_:b_]*1.01 + 1e-7, np.maximum(FD['lam_ub'][a_:b_], FD['lam_lb'][a_:b_]))
        print(f"  repair: {itr} steps, feasible={ok}, V+moment={FD['h']*np.sum(lamr*FD['Nb2'])+mt:.5e}", flush=True)
        if ok:
            base = lamr - FD['lam_lb']
    lo, hi = 0.5, float(os.environ.get("FMAX", "1.6"))
    r = trial(hi)
    if r is None or not r[0]:
        lamt = np.minimum(np.maximum(base*hi, 0) + FD['lam_lb'], FD['lam_ub'])
        okt, wt, kt = riccati_check(FD, lamt)
        print(f"  even factor {hi} fails (fail cell {kt} of {Nf}, t={kt*FD['h']:.3f}; clipped cells {int(np.sum(base*hi+FD['lam_lb'] > FD['lam_ub']))})"); return
    best = (hi, r[1], r[2]+mt)
    for _ in range(14):           # bisection on the uniform factor (lambda feasible set is convex in this direction)
        mid = (lo+hi)/2; r = trial(mid)
        if r is not None and r[0]: hi = mid; best = (mid, r[1], r[2]+mt)
        else: lo = mid
    print(f"  smallest feasible factor {best[0]:.4f}: V+moment = {best[2]:.5e}  G_w = {G:.5e}", flush=True)
    nb = int(os.environ.get("BLOCKS", "0"))
    if nb > 0:   # block-coordinate reduction of lambda with the fine Riccati check (multiplier search only)
        import time; t0 = time.time()
        lam = best[1].copy(); fl = FD['lam_lb']; edges = np.linspace(0, Nf, nb+1).astype(int)
        for sweep in range(int(os.environ.get("SWEEPS", "3"))):
            for bi in np.argsort(-np.array([np.sum((lam[edges[i]:edges[i+1]]-fl[edges[i]:edges[i+1]])*FD['Nb2'][edges[i]:edges[i+1]]) for i in range(nb)])):
                a_, b_ = edges[bi], edges[bi+1]
                lo_, hi_ = 0.0, 1.0; keep = lam[a_:b_].copy()
                for _ in range(8):
                    mu = (lo_+hi_)/2; trialv = lam.copy(); trialv[a_:b_] = fl[a_:b_] + mu*(keep-fl[a_:b_])
                    if riccati_check(FD, trialv)[0]: hi_ = mu
                    else: lo_ = mu
                lam[a_:b_] = fl[a_:b_] + hi_*(keep-fl[a_:b_])
            Vb = FD['h']*np.sum(lam*FD['Nb2'])
            print(f"  sweep {sweep}: V+moment = {Vb+mt:.5e}  ({time.time()-t0:.0f}s)", flush=True)
        best = (1.0, lam, FD['h']*np.sum(lam*FD['Nb2'])+mt)
        base = (lam - FD['lam_lb'])        # safety scaling below acts on the reduced multiplier
        def trial(f):
            l = np.minimum(np.maximum(base*f, 0) + FD['lam_lb'], FD['lam_ub'])
            ok, worst, kfail = riccati_check(FD, l)
            return (ok, l, FD['h']*np.sum(l*FD['Nb2']))
    for safety in [1.002, 1.005, 1.01, 1.02, 1.05, 1.1, 1.2]:          # strict margin so that the conservative Arb re-run passes
        r = trial(best[0]*safety)
        if r is not None and r[0]:
            okx, kx = exact_riccati(FD, r[1])
            print(f"  safety {safety}: float ok, Arb {'PASS' if okx else 'FAIL at '+str(kx)}, U={r[2]+mt:.5e}", flush=True)
            if okx: best = (best[0]*safety, r[1], r[2]+mt); break
    if best is None: print("RESULT: no certificate"); return
    sc, lam, U = best
    okx, kx = exact_riccati(FD, lam)
    print(f"RESULT tf={tf} s*={ss} cap={sys.argv[5]} Nf={Nf} rho={rho}: U_total={U:.6e}  G_w={G:.6e}  margin={(G-U)/G*100:.2f}%  exact Arb recursion={'PASS' if okx else 'FAIL at '+str(kx)}  certificate={'PASS' if (okx and G>U) else 'FAIL'}", flush=True)
    np.savez(f"riccati_{tf}_{ss}_{sys.argv[5]}_{Nf}.npz", lam=lam, U=U, G=G, rho=rho)


def oracle(FD, lam):
    """Backward recursion; if infeasible, return a violating global control (as per-cell v-vectors) and its cut
    coefficients: F(n;lam) = F0 + sum_j lam_j * (L_j - W_j) > 0."""
    Nf, h = FD['Nf'], FD['h']; Pz = -FD['terminal'].copy()
    Tx = transition(h); gains = [None]*Nf; Ts = [None]*Nf
    for k in range(Nf-1, -1, -1):
        H = np.zeros((6, 6)); idx = [0, 1, 4, 5]
        Sk = FD['S'][k] + lam[k]*FD['Lk'][k] - np.diag([0, 0, h, h**3/12])*(lam[k]+FD['Mlate'][k])
        H[np.ix_(idx, idx)] += Sk
        T = np.zeros((4, 6)); T[0:2] = Tx; T[2, 2] = 1; T[3, 3] = 1
        T[2, [0, 1, 4, 5]] += FD['g0'][k]; T[3, [0, 1, 4, 5]] += FD['gw'][k]; Ts[k] = T
        H += T.T@Pz@T
        Huu = H[4:, 4:]; Huz = H[4:, :4]; Hzz = H[:4, :4]
        sc = np.array([1/np.sqrt(h), 1/np.sqrt(h**3/12)])
        ev, evec = np.linalg.eigh(Huu*np.outer(sc, sc))
        if ev[-1] >= -1e-14:
            # violating direction: zero control before k, u_k = top eigvec, optimal feedback after k
            uk = evec[:, -1]*sc
            z = np.zeros(4); F0 = 0.0; LmW = np.zeros(Nf)
            for j in range(k, Nf):
                u = uk if j == k else -gains[j]@z
                v = np.array([z[0], z[1], u[0], u[1]])
                F0 += v@FD['S'][j]@v - FD['Mlate'][j]*(h*u[0]**2 + h**3/12*u[1]**2)
                LmW[j] = v@FD['Lk'][j]@v - (h*u[0]**2 + h**3/12*u[1]**2)
                w = np.array([z[0], z[1], z[2], z[3], u[0], u[1]]); z = Ts[j]@w
            F0 += -z@FD['terminal']@z
            nrm = abs(F0) + np.abs(LmW).sum() + 1e-300
            return False, (F0/nrm, LmW/nrm)
        gains[k] = np.linalg.solve(Huu, Huz)
        Pz = Hzz - Huz.T@gains[k]; Pz = (Pz+Pz.T)/2
    return True, None

def kelley(FD, lam0=None, iters=3000, tol_rel=0.0, verbose=True):
    from scipy.optimize import linprog
    Nf = FD['Nf']; c = FD['h']*FD['Nb2']
    lb, ub = FD['lam_lb'], np.maximum(FD['lam_ub'], FD['lam_lb'])
    A = []; b = []; lam = lb.copy() if lam0 is None else lam0.copy()
    best_feas = None
    for it in range(iters):
        ok, cut = oracle(FD, lam)
        if ok:
            if best_feas is None or c@lam < c@best_feas: best_feas = lam.copy()
            if verbose: print(f"  kelley it {it}: feasible, V={c@lam:.5e}", flush=True)
            return lam, it
        F0, LmW = cut
        A.append(-LmW); b.append(F0)           # F0 + sum lam_j LmW_j <= 0  <=>  -LmW . lam >= F0  ->  LmW.lam <= -F0
        A[-1] = LmW; b[-1] = -F0
        res = linprog(c, A_ub=np.array(A), b_ub=np.array(b), bounds=list(zip(lb, ub)), method='highs')
        if res.status != 0:
            print("  LP infeasible/failed:", res.message); return None, it
        lam = res.x
        if verbose and it % 50 == 0: print(f"  kelley it {it}: LP V={c@lam:.5e} cuts={len(A)}", flush=True)
    return None, iters

if __name__ == "__main__":
    main()
