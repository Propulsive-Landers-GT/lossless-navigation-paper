"""[proof-tvc] Certificate v2 for Theorem TVC-1 (math/06-pure-tvc.md §4): piecewise-LINEAR cell basis.
Same inequality chain as certificate.py, with three changes:
 * discrete space = cellwise polynomials of degree 1 (2N dof); remainder n'' is orthogonal to {1,t} on each cell,
   so xdot'' and x'' are cell-local and  |xdot''|^2_cell <= (h/2pi)^2 |n''|^2_cell,  |x''|^2_inf <= h^3/(4pi^2)|n''|^2_cell,
   |int g n''| <= sup|g''| h^2/8 sqrt(tf) |n''|  (Lemma 4.6');
 * node-wise splitting parameter theta(s) for the late torque cost (Sec. 4.3), chosen so that the homogeneous
   remainder removes at most a fraction r_theta of A2;
 * defaults tau = tau' = 0.01, zeta = xi = 0.05.
"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, cvxpy as cp
from witness_nl import gtpl, J0, optimize, evaluate, segments_bangbang, evaluate_segments
import certificate as C1

GL_x, GL_w = np.polynomial.legendre.leggauss(6)     # exact for degree <= 11 (cubic x times cubic x times linear w)
PAR = dict(roll=False, Ja=3.74, Jt=63.6, tau_roll=3.0, gyro_gamma=1.0, zeta=0.05, xi=0.05, r_theta=0.2,
           kap=0.01, eta1_cells=2, tau=0.01, taup=0.01, lam_max=1e-2, nsub=3)

def setup(P, tf, ss, N, par=PAR, loc=None):
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    zeta, xi, kap, lam_max = par['zeta'], par['xi'], par['kap'], par['lam_max']
    K1 = a1*np.sin(de)/eps; K2 = a2*np.sin(de)/eps
    h = tf/N; kss = int(round(ss/h)); assert abs(kss*h-ss) < 1e-12 and ss <= tf/2
    tk = np.arange(N+1)*h; ck = (tk[:-1]+tk[1:])/2
    capv = par.get('cap') or np.pi
    phib0 = lambda s: np.minimum(K2*np.minimum(s, tf-s)**2/2, capv)
    vb0 = lambda s: K2*np.minimum(s, tf-s)
    if loc is None:
        phibar, vbar = phib0, vb0
    else:   # localized bounds (Lemma 4.0), valid for competitors with gain >= 0
        vbar, phibar = loc
    om3 = (lambda s: par['tau_roll']/par['Ja']*s) if par['roll'] else (lambda s: 0.0*s)
    rJ = par['Ja']/par['Jt']
    assert phib0(tf/2) < np.pi/2 - 0.02, "(A1) fails"
    # (A2) f>=0 is no longer needed: Pi >= b_z |a2-f| for either sign of f (math/06 §4.2)
    def cellmax(fun, lo, hi):
        if hasattr(fun, 'cells'):   # rigorous: max over all fine cells meeting [lo, hi]
            i0 = max(int(np.floor(lo/fun.ds))-1, 0); i1 = min(int(np.ceil(hi/fun.ds))+1, len(fun.cells))
            return float(np.max(fun.cells[i0:i1]))
        return max(fun(lo), fun(hi), fun(min(max(tf/2, lo), hi)))   # crude bounds are unimodal with max at tf/2
    def theta_of(vb, cq3):
        er = 2*eps**2*(vb**4)/a2**2          # remainder per unit (1/theta-1), relative to A2=a2/2
        if er <= 0: return 1e-3
        return float(np.clip(1/(1+par['r_theta']/er), 1e-3, 0.9))
    rows = []
    for k in range(N):
        for j in range(par['nsub']):
            lo = tk[k]+j*h/par['nsub']; hi = lo+h/par['nsub']
            ph = cellmax(phibar, lo, hi); vb = cellmax(vbar, lo, hi); o3 = float(om3(hi))
            cg3 = eps*rJ*o3; cq3 = rJ*o3/np.cos(ph); gg = par['gyro_gamma']
            early = hi <= ss+1e-15
            th = theta_of(vb, cq3)
            for x, w in zip(GL_x, GL_w):
                s = (lo+hi)/2+(hi-lo)/2*x; ws = w*(hi-lo)/2
                cL = 2*(1+1/kap)*vb**4; cLd = 2*(1+1/kap)*cq3**2
                if early:
                    cA = (ss-s)*(a1*np.cos(de)/(1+np.cos(ph)) + cg3*gg/2); cB = (ss-s)*(eps/np.cos(ph)**2 + cg3/(2*gg)); sd = 1
                    c2 = 0.0
                else:
                    A2e = a2/2 - (1/th-1)*eps**2*2*vb**4/(2*a2)
                    B2e = eps*np.cos(ph) - (1/th-1)*eps**2*2*cq3**2/(2*a2)
                    if par.get('ideal_theta'):   # DIAGNOSTIC ONLY (not rigorous): drop the curvature remainder
                        th = 1e-3; A2e = a2/2; B2e = eps*np.cos(ph)
                    cA = -(s-ss)*((1-zeta)*A2e - cg3*gg/2); cB = -(s-ss)*((1-zeta)*B2e - cg3/(2*gg)); sd = -1
                    c2 = (1-zeta)*(s-ss)*(1-th)*eps**2*np.cos(ph)**2/(2*a2)   # torque-cost multiplier of n^2
                rows.append((k, s, ws, cA, cB, cL, cLd, sd, c2))
    R = np.array(rows); cell = R[:, 0].astype(int); s = R[:, 1]; wq = R[:, 2]
    cA, cB, cL, cLd, side, c2 = R[:, 3], R[:, 4], R[:, 5], R[:, 6], R[:, 7], R[:, 8]
    # basis: for cell k, phi_{k,0} = 1, phi_{k,1} = (t-c_k)  (on the cell). Exact x, xdot at nodes.
    S = s[:, None]; T0 = tk[:-1][None, :]; T1 = tk[1:][None, :]
    sig = np.clip(S-T0, 0, h); inside = (S > T0) & (S <= T1); after = S > T1
    Xd0 = sig; X0 = np.where(S <= T0, 0, np.where(inside, sig**2/2, h*(S-(T0+T1)/2)))
    Xd1 = np.where(inside, sig**2/2 - (h/2)*sig, 0.0)
    X1 = np.where(inside, sig**3/6 - (h/2)*sig**2/2, np.where(after, -h**3/12, 0.0))
    X = np.hstack([X0, X1]); Xd = np.hstack([Xd0, Xd1])          # columns: N constants, then N slopes
    pos = side > 0
    form = lambda m, cx, cv: (X[m].T*(wq*cx)[m])@X[m] + (Xd[m].T*(wq*cv)[m])@Xd[m]
    Kp = form(pos, cA, cB); Km = form(~pos, cA, cB)
    Lk = [form(cell == k, cL, cLd) for k in range(N)]
    # gyro lateral-force weight c(s) >= eps (Ja/Jt) om3bar / cos(phibar); Cauchy-Schwarz with weight c:
    # (int c|h'|)^2 <= (int c) (int c |h'|^2)
    cnode = np.array([eps*rJ*float(om3(x))/np.cos(cellmax(phibar, x-1e-12, x+1e-12)) for x in s])
    Vall = (Xd.T*(wq*cnode))@Xd                           # int c xdot^2
    sgf = np.linspace(0, tf, 20001); dsf = sgf[1]-sgf[0]
    cgy = eps*rJ*np.maximum(om3(sgf[1:]), 0)/np.cos(np.array([cellmax(phibar, a, b) for a, b in zip(sgf[:-1], sgf[1:])]))
    wcell = np.maximum(np.abs(sgf[:-1]-ss), np.abs(sgf[1:]-ss))
    Cg0 = float(np.sum(cgy)*dsf); Cgw = float(np.sum(wcell**2*cgy)*dsf)   # int c, int w^2 c  (weights for m0, m_w)
    # mass matrix of int n^2 on cell k: h for constant, h^3/12 for slope
    Wdiag = np.concatenate([np.full(N, h), np.full(N, h**3/12)])
    # late torque multiplier: cellwise min of c2 (a lower bound, piecewise constant)
    Mlate = np.array([c2[cell == k].min() if k >= kss else 0.0 for k in range(N)])
    Mlate = np.maximum(Mlate - 0.0, 0.0)
    # (endpoint check: c2 is increasing in s on each late cell near s*; nodes don't include the left end, use t_k)
    for k in range(kss, N):
        thk = theta_of(cellmax(vbar, tk[k], tk[k+1]), 0.0)
        Mlate[k] = min(Mlate[k], (1-zeta)*(tk[k]-ss)*(1-thk)*eps**2*np.cos(cellmax(phibar, tk[k], tk[k+1]))**2/(2*a2)) if tk[k] > ss else 0.0
    f0 = np.where(s <= ss, a1*np.cos(de), a2)
    G = np.vstack([(wq*f0)@X, (wq*(s-ss)*f0)@X])     # m0 = int f0 x ;  m_w = int (s-s*) f0 x  (Lambda_h part)
    Cc = np.vstack([np.concatenate([h*np.ones(N), np.zeros(N)]),
                    np.concatenate([h*(tf-ck), -np.full(N, h**3/12)])])   # xdot(tf), x(tf) = int (tf-t) n
    Nb2 = np.zeros(N); lam_ub = np.full(N, lam_max)
    kappa_D = 2*K1*np.tan(de)/eps + (a2-a1*np.cos(de))*np.tan(de)**2/eps**2
    for k in range(N):
        if k < kss-par['eta1_cells']:
            Nb2[k] = (1+kap)*K1**2
            lam_ub[k] = min(lam_max, (1-xi)*(ss-tk[k+1])*np.cos(phibar(tk[k+1]))/((1+kap)*kappa_D))
        else:
            Nb2[k] = (1+kap)*K2**2
    return dict(cmax=float(cnode.max()) if len(cnode) else 0.0, Vall=Vall, Cg0=Cg0, Cgw=Cgw, P=P, tf=tf, ss=ss, N=N, h=h, kss=kss, tk=tk, Kp=Kp, Km=Km, Lk=Lk, G=G, C=Cc, Mlate=Mlate,
                Wdiag=Wdiag, Nb2=Nb2, lam_ub=lam_ub, K1=K1, K2=K2, par=par, phibar=phibar, vbar=vbar,
                s=s, wq=wq, cA=cA, cB=cB, cL=cL, cLd=cLd, side=side, cell=cell, om3=om3, rJ=rJ)

def remainder_constants(D, rho):
    h, tf, N = D['h'], D['tf'], D['N']; par = D['par']
    tau, taup, lam_max = par['tau'], par['taup'], par['lam_max']
    cA, cB, cL, cLd, side, cell = D['cA'], D['cB'], D['cL'], D['cLd'], D['side'], D['cell']
    fac = np.where(side > 0, 1+1/tau, 1/taup-1)
    c_loc = np.zeros(N)
    for k in range(N):
        m = cell == k
        cv = np.max(fac[m]*np.abs(cB[m])) + (1+1/tau)*lam_max*np.max(cLd[m])
        cx = np.max(fac[m]*np.abs(cA[m])) + (1+1/tau)*lam_max*np.max(cL[m])
        c_loc[k] = cv*(h/(2*np.pi))**2 + cx*h*h**3/(4*np.pi**2)
    a2 = D['P']['a2']
    taur = par.get('taurho', 0.2)
    rho0, rhow = rho
    # sup|g''|: g0'' = f0 <= a2 ; gw''(t) = (t-s*) f0(t) <= a2*max(s*, tf-s*)
    cg = (1/taur-1)*(rho0*a2**2 + rhow*(a2*max(D['ss'], tf-D['ss']))**2)*h**4*tf/64   # clamps: g linear => 0
    return c_loc, cg

def solve_cert(D, rho, rhoc):
    rho0, rhow = (rho, rho) if np.isscalar(rho) else rho
    N, h, par = D['N'], D['h'], D['par']; tau, taup = par['tau'], par['taup']
    c_loc, cg = remainder_constants(D, (rho0, rhow))
    c_loc = c_loc + (1+1/tau)*(1+1/par.get('kapg', 10.0))*(rho0*D['Cg0'] + rhow*D['Cgw'])*D['cmax']*(h/(2*np.pi))**2
    lam_lb = np.maximum(c_loc+cg-D['Mlate'], 0.0)*1.02
    if np.any(lam_lb > D['lam_ub']): return None
    Rm = np.diag([rho0, rhow])
    kg = par.get('kapg', 10.0)
    coefV = (1+1/kg)*(rho0*D['Cg0'] + rhow*D['Cgw'])     # (int c|h'|)^2 <= int c^2 * int |h'|^2  (gyro lateral force)
    A = (1+tau)*D['Kp'] + (1-taup)*D['Km'] - (1-par.get('taurho', 0.2))*D['G'].T@Rm@D['G'] - (1-taup)*rhoc*D['C'].T@D['C']
    A = A + (1+tau)*coefV*D['Vall']
    A = (A+A.T)/2
    Wd = D['Wdiag']
    lam = cp.Variable(N)
    lam2 = cp.hstack([lam, lam]); M2 = np.concatenate([D['Mlate'], D['Mlate']])
    if os.environ.get("FASTL", "0") == "1":
        # lam_k <= lam_max on every cell, and L_k is PSD: replace sum lam_k L_k by the fixed PSD bound lam_max * sum L_k
        A = A + (1+tau)*par['lam_max']*sum(D['Lk'])
        LK = 0
    else:
        LK = sum(lam[k]*((1+tau)*D['Lk'][k]) for k in range(N))
    Sc = 1/np.sqrt(Wd)                      # well-conditioned (lambda-unit) scaling of the LMI
    As = (A*Sc[:, None]*Sc[None, :]); As = (As+As.T)/2
    if not isinstance(LK, int): LK = cp.multiply(LK, np.outer(Sc, Sc))
    Mx = As + LK - cp.diag(lam2 + M2)
    prob = cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam, D['Nb2']))),
                      [lam >= lam_lb, lam <= D['lam_ub'], (Mx+Mx.T)/2 << 0])
    solver = os.environ.get("SOLVER", "CLARABEL")
    try:
        if solver == "SCS": prob.solve(solver='SCS', eps=float(os.environ.get("SCSEPS","1e-7")), max_iters=200000, verbose=os.environ.get("VERB","0")=="1")
        else: prob.solve(solver=solver, verbose=os.environ.get("VERB","0")=="1")
    except Exception as e:
        print("solver error", e); return None
    if lam.value is None: return None
    lv = np.clip(lam.value, lam_lb, D['lam_ub'])
    print(f"    solver objective {prob.value:.5e}", flush=True)
    def top(lv):
        LKv = 0 if os.environ.get("FASTL", "0") == "1" else (1+tau)*sum(lv[k]*D['Lk'][k] for k in range(N))
        Mv = A + LKv - np.diag(Wd*np.concatenate([lv+D['Mlate']]*2))
        # scale-invariant check: symmetric diagonal scaling by Wd^{-1/2}
        Sc = 1/np.sqrt(Wd); Mv = (Mv+Mv.T)/2*Sc[:, None]*Sc[None, :]
        return np.linalg.eigvalsh(Mv).max()
    t = top(lv); it = 0
    while t > 0 and it < 30:
        lv = lv + 1.2*t; it += 1
        if np.any(lv > D['lam_ub']): return None
        t = top(lv)
    if t > 0: return None
    return dict(val=h*np.sum(lv*D['Nb2']), lam=lv, topeig=t, lam_lb=lam_lb,
                lbpart=h*np.sum(lam_lb*D['Nb2']))

def moment_term(D, rho, d=0.0, M=40001):
    """Lemma 4.7'' : rho0*(d+Mv0+mu0(Pen))^2 + rhow*(d(1+s*)+Mvw+cw*Pen)^2 - Pen, maximized over 0<=Pen<=Penmax.
    mu0: bathtub bound for the unweighted shift; the weighted shift int (s-s*) Df h is <= cw*Pen (linear),
    cw = sup sin(phibar)/omega. Penmax = (xi/(cE(1-c_abs)) + zeta) E0 from Lemma 4.0."""
    rho0, rhow = rho
    P = D['P']; a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    tf, ss = D['tf'], D['ss']; zeta, xi = D['par']['zeta'], D['par']['xi']
    sg = np.linspace(0, tf, M); ds = sg[1]-sg[0]
    sph = np.maximum(np.sin(D['phibar'](sg[:-1])), np.sin(D['phibar'](sg[1:])))
    vb = np.maximum(D['vbar'](sg[:-1]), D['vbar'](sg[1:]))
    E = sg[1:] <= ss
    wmax = np.maximum(np.abs(sg[:-1]-ss), np.abs(sg[1:]-ss)); wmin = np.minimum(np.abs(sg[:-1]-ss), np.abs(sg[1:]-ss))
    gyro = 0.0*vb          # gyro lateral force is handled inside the SDP (coefV term)
    kgf = 1+D['par'].get('kapg', 10.0) if D['par']['roll'] else 1.0
    Mv0 = np.sum(np.where(E, sph*eps*vb**2, 0))*ds + np.sum(gyro)*ds
    Mvw = np.sum(np.where(E, wmax*sph*eps*vb**2, 0))*ds + np.sum(wmax*gyro)*ds
    Dmax = a2 - a1*np.cos(de) + eps*vb.max()**2
    om = np.where(E, xi, zeta)*np.cos(D['phibar'](sg[1:]))    # late: zeta*Pi >= zeta*b_z|a2-f|
    cw = np.max(sph/om)
    cost = om*wmin*Dmax*ds; gain = sph*Dmax*ds
    order = np.argsort(-(gain/np.maximum(cost, 1e-300)))
    cumP = np.concatenate([[0], np.cumsum(cost[order])]); cumG = np.concatenate([[0], np.cumsum(gain[order])])
    mu0 = lambda Pen: cumG[min(np.searchsorted(cumP, Pen, side='left'), len(cumG)-1)]
    Penmax = D['Penmax']
    grid = np.linspace(0, Penmax, 20001)
    val = lambda Pa, Pb: kgf*(rho0*(d+Mv0+mu0(Pb))**2 + rhow*(d*(1+ss)+Mvw+cw*Pb)**2) - Pa
    best = max(val(grid[i], grid[i+1]) for i in range(len(grid)-1))
    return best

if __name__ == "__main__":
    tf = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    ss = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    gim = sys.argv[4] if len(sys.argv) > 4 else 'cone'
    deg = 15.0 if gim == 'cone' else np.degrees(np.arccos(np.cos(np.deg2rad(15))**2))
    P = gtpl(deg=deg)
    wfile = f"witness_{gim}_{tf}_{ss}.npy"
    if os.path.exists(wfile): nv = np.load(wfile)
    else:
        nv = optimize(P, tf, ss, N=int(os.environ.get("WN", 100)), starts=6, cap=np.deg2rad(float(os.environ["TILTCAP"])) if "TILTCAP" in os.environ else None)[1]; np.save(wfile, nv)
    ev = evaluate(P, tf, ss, nv)
    evo = evaluate_segments(P, tf, ss, segments_bangbang(P, tf, ss, nv))   # ordinary-control realization (exact bang-bang early)
    assert abs(evo['end'][0]) < 1e-12 and abs(evo['end'][1]) < 1e-12
    ev['G'] = evo['G']; ev['maxvz'] = max(ev['maxvz'], evo['maxvz'])
    par = dict(PAR); par['tau'] = float(os.environ.get("TAU", par['tau'])); par['zeta'] = par['xi'] = float(os.environ.get("ZETA", par['zeta'])); par['kapg'] = float(os.environ.get("KAPG", 10.0)); par['cap'] = np.deg2rad(float(os.environ["TILTCAP"])) if "TILTCAP" in os.environ else None; par['roll'] = os.environ.get("ROLL", "0") == "1"; par['lam_max'] = float(os.environ.get("LAMMAX", par['lam_max']))
    print(f"[{gim} delta={deg:.2f}] tf={tf} s*={ss} N={N} roll-competitors={par['roll']}: witness G_w={ev['G']:.6e}, "
          f"max tilt {np.degrees(ev['maxtilt']):.3f} deg, max v_z(t<tf)={ev['maxvz']:.3e}, min r_z/|r_h|={ev['rzrel']:.3e}, "
          f"r0={ev['r0']}, v0={ev['v0']}", flush=True)
    loc = None
    if os.environ.get("LOC", "1") == "1":
        from localize import localize
        vf, pf, info, _ = localize(P, tf, ss, roll=par['roll'], cap=par.get('cap'))
        print("  localization (Lemma 4.0):", {k: float(v) for k, v in info.items()}, flush=True)
        loc = (vf, pf)
    D = setup(P, tf, ss, N, par, loc=loc)
    cE = np.cos(D['K2']*ss**2/2)
    D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0'] if loc is not None else 1e2
    print(f"  Penmax={D['Penmax']:.3e}", flush=True)
    best = None
    for rho in [tuple(float(y) for y in x.split(":")) for x in os.environ.get("RHOS", "1:100").split(",")]:
        for rhoc in [float(x) for x in os.environ.get("RHOCS", "1e-1").split(",")]:
            c = solve_cert(D, rho, rhoc)
            if c is None:
                print(f"  rho={rho} rhoc={rhoc:g}: no certificate", flush=True); continue
            mt = moment_term(D, rho); U = c['val']+mt
            print(f"  rho={rho} rhoc={rhoc:g}: SDP={c['val']:.5e} (remainder floor {c['lbpart']:.2e}) topeig={c['topeig']:.1e} "
                  f"moment={mt:.3e} U_total={U:.5e}  G_w/U={ev['G']/U:.4f}", flush=True)
            if best is None or U < best[0]: best = (U, rho, rhoc, c)
    if best:
        U, rho, rhoc, c = best
        ok = ev['G'] > U
        dlo, dhi = 0.0, 1.0
        for _ in range(50):
            dm = (dlo+dhi)/2
            if ev['G']-dm*np.sqrt(1+ss**2) > c['val']+moment_term(D, rho, dm): dlo = dm
            else: dhi = dm
        print(f"RESULT tf={tf} s*={ss} N={N} {gim} roll={par['roll']}: G_w={ev['G']:.5e}  U_total={U:.5e}  margin={(ev['G']-U):.3e} "
              f"({(ev['G']-U)/ev['G']*100:.1f}%)  dist(theta_m,F) >= {dlo:.3e}  certificate={'PASS' if ok else 'FAIL'}", flush=True)
        np.savez(f"cert2_{gim}_{tf}_{ss}_{N}_roll{int(par['roll'])}.npz", lam=c['lam'], U=U, Gw=ev['G'], rho=rho, rhoc=rhoc, dist=dlo)

