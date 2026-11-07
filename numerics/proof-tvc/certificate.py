"""[proof-tvc] Computer-assisted certificate for Theorem TVC-1 (math/06-pure-tvc.md, Section 4).

Checks   G_w  >  U_total, where
  G_w     = exact gain of the explicit planar witness (witness_nl.evaluate);
  U_total = rigorous upper bound on W_z(q) - J0 over ALL relaxed pure-TVC trajectories q (upright at rest at
            both ends) with zero lateral data (r0h = v0h = 0).
Inequality chain (numbers refer to math/06 Section 4):
  (4.3) W_z - J0 <= Q(h) - Pen,
        Q(h) = int_E (s*-s)[A1|h|^2+B1|h'|^2] - (1-zeta) int_L (s-s*)[A2e|h|^2 + B2|h'|^2 + C2|h''|^2]
  (4.4) |h''|^2 <= (1+kap) Nb^2 + (1+1/kap) vbar^4 |h|^2  (+ Delta p terms early), via h'' = -q_h/eps - v^2 h
  (4.5) S-procedure + Finsler certificate (lam, rho) on scalar functions; vector case = sum of components
  (4.6) cell-average splitting n = nbar + n' with explicit O(h^2) remainder constants
  (4.7) moment-shift term  max_Pen [rho sum_j (Mv_j + U_j(Pen) + d)^2 - Pen]
All coefficient functions are replaced by cellwise-conservative constants. Double precision; the discrete
matrix inequality is re-verified by an independent eigenvalue computation and repaired by a uniform shift.
"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np, cvxpy as cp
from witness_nl import gtpl, J0, optimize, evaluate

GL_x, GL_w = np.polynomial.legendre.leggauss(5)   # exact for polynomial degree <= 9
PAR = dict(roll=False, Ja=3.74, Jt=63.6, tau_roll=3.0, gyro_gamma=1.0, zeta=0.15, xi=0.5, theta=0.5, kap=0.01, eta1_cells=2, tau=0.1, taup=0.5, lam_max=1e-2, nsub=4)

def setup(P, tf, ss, N, par=PAR):
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    zeta, xi, theta, kap, lam_max = par['zeta'], par['xi'], par['theta'], par['kap'], par['lam_max']
    K1 = a1*np.sin(de)/eps; K2 = a2*np.sin(de)/eps
    h = tf/N; kss = int(round(ss/h)); assert abs(kss*h-ss) < 1e-12 and ss <= tf/2
    tk = np.arange(N+1)*h
    phibar = lambda s: K2*np.minimum(s, tf-s)**2/2          # Lemma 4.1
    vbar = lambda s: K2*np.minimum(s, tf-s)
    # roll: |omega3(s)| <= (tau_roll/Ja) s  (omega(0)=0, axisymmetric J); cg3 = eps*(Ja/Jt)*om3bar, cq3 = (Ja/Jt)*om3bar
    om3 = (lambda s: par['tau_roll']/par['Ja']*s) if par['roll'] else (lambda s: 0.0*s)
    rJ = par['Ja']/par['Jt']
    assert phibar(tf/2) < np.pi/2 - 0.05, "(A1) a priori tilt bound too large"
    fmin = a1*np.cos(de) - eps*vbar(tf/2)**2
    assert fmin > 0, "(A2) f>=0 not guaranteed a priori"
    def cellmax(fun, lo, hi):
        return max(fun(lo), fun(hi), fun(min(max(tf/2, lo), hi)))   # functions are unimodal (max at tf/2)
    nodes = []; wts = []; cA = []; cB = []; cL = []; cLd = []; side = []; cell = []
    for k in range(N):
        for j in range(par['nsub']):
            lo = tk[k]+j*h/par['nsub']; hi = lo+h/par['nsub']
            ph = cellmax(phibar, lo, hi); vb = cellmax(vbar, lo, hi)
            o3 = float(om3(hi)); cg3 = eps*rJ*o3; cq3 = rJ*o3/np.cos(ph); gg = par['gyro_gamma']
            early = hi <= ss + 1e-15
            for x, w in zip(GL_x, GL_w):
                s = (lo+hi)/2 + (hi-lo)/2*x; ws = w*(hi-lo)/2
                nodes.append(s); wts.append(ws); cell.append(k)
                # lam(s)-multiplied gain terms: |h''| <= Nb + vb^2|h| + cq3|h'|  =>  |h''|^2 <= (1+kap)Nb^2 + 2(1+1/kap)(vb^4|h|^2 + cq3^2|h'|^2)
                cL.append(2*(1+1/kap)*vb**4); cLd.append(2*(1+1/kap)*cq3**2)
                if early:
                    # gyro vertical term w*eps*(Ja/Jt)*om3*(h x h')_z <= |w| cg3 (gg|h|^2 + |h'|^2/gg)/2
                    cA.append((ss-s)*(a1*np.cos(de)/(1+np.cos(ph)) + cg3*gg/2)); cB.append((ss-s)*(eps/np.cos(ph)**2 + cg3/(2*gg))); side.append(1)
                else:
                    A2e = a2/2 - (1/theta-1)*eps**2*2*vb**4/(2*a2)
                    B2e = eps*np.cos(ph) - (1/theta-1)*eps**2*2*cq3**2/(2*a2)
                    # (1-zeta) only multiplies the Pi-derived costs; the gyro term enters with full weight
                    cA.append(-(s-ss)*((1-zeta)*A2e - cg3*gg/2)); cB.append(-(s-ss)*((1-zeta)*B2e - cg3/(2*gg))); side.append(-1)
    s = np.array(nodes); wq = np.array(wts); cA = np.array(cA); cB = np.array(cB); cL = np.array(cL); cLd = np.array(cLd)
    side = np.array(side); cell = np.array(cell)
    T0 = tk[:-1][None, :]; T1 = tk[1:][None, :]; S = s[:, None]
    Xd = np.clip(S-T0, 0, h)
    X = np.where(S <= T0, 0.0, np.where(S <= T1, (S-T0)**2/2, h*(S-(T0+T1)/2)))
    pos = side > 0
    Kp = (X[pos].T*(wq*cA)[pos])@X[pos] + (Xd[pos].T*(wq*cB)[pos])@Xd[pos]
    Km = (X[~pos].T*(wq*cA)[~pos])@X[~pos] + (Xd[~pos].T*(wq*cB)[~pos])@Xd[~pos]
    # lam-dependent gain term  sum_k lam_k * L_k,  L_k = int_{cell k} cL x^2
    Lk = [(X[cell == k].T*(wq*cL)[cell == k])@X[cell == k] + (Xd[cell == k].T*(wq*cLd)[cell == k])@Xd[cell == k] for k in range(N)]
    f0 = np.where(s <= ss, a1*np.cos(de), a2)
    G = np.vstack([(wq*f0)@X, (wq*s*f0)@X])
    C = np.vstack([h*np.ones(N), h*(tf-(tk[:-1]+tk[1:])/2)])
    C2 = lambda x: (1-theta)*eps**2*np.cos(phibar(x))**2/(2*a2)
    Mlate = np.zeros(N)
    for k in range(kss, N):
        xs = np.linspace(tk[k], tk[k+1], 17)
        c2min = min(C2(tk[k]), C2(tk[k+1]), C2(min(max(tf/2, tk[k]), tk[k+1])))
        Mlate[k] = (1-zeta)*(tk[k]-ss)*c2min
    Nb2 = np.zeros(N); lam_ub = np.full(N, lam_max)
    kappa_D = 2*K1*np.tan(de)/eps + (a2-a1*np.cos(de))*np.tan(de)**2/eps**2
    for k in range(N):
        if k < kss - par['eta1_cells']:
            Nb2[k] = (1+kap)*K1**2
            lam_ub[k] = min(lam_max, (1-xi)*(ss-tk[k+1])*np.cos(phibar(tk[k+1]))/((1+kap)*kappa_D))
        else:
            Nb2[k] = (1+kap)*K2**2
    return dict(P=P, tf=tf, ss=ss, N=N, h=h, kss=kss, tk=tk, Kp=Kp, Km=Km, Lk=Lk, G=G, C=C, Mlate=Mlate,
                Nb2=Nb2, lam_ub=lam_ub, K1=K1, K2=K2, par=par, phibar=phibar, vbar=vbar,
                s=s, wq=wq, cA=cA, cB=cB, cL=cL, cLd=cLd, side=side, cell=cell, om3=om3, rJ=rJ)

def nprime_constants(D, rho, rhoc):
    """Lemma 4.6 remainder: (1+1/tau)<Kp_tot n',n'> + (1/taup-1)<S n',n'> <= sum_k c_loc[k]|n'|_k^2 + c_glob|n'|^2.
    |xdot'(s)|^2 <= h |n'|_k^2 (s in cell k);  |x'(s)| <= h sqrt(tf/12)|n'| + h^{3/2}/sqrt(3) |n'|_k;
    |int g n'| <= sup|g'| h sqrt(tf/12) |n'|."""
    h, tf, N, tk = D['h'], D['tf'], D['N'], D['tk']
    s, wq, cA, cB, cL, side, cell = D['s'], D['wq'], D['cA'], D['cB'], D['cL'], D['side'], D['cell']
    tau, taup, lam_max = D['par']['tau'], D['par']['taup'], D['par']['lam_max']
    fac = np.where(side > 0, 1+1/tau, 1/taup-1)
    oxA = np.abs(cA); oxL = lam_max*cL*(1+1/tau); oxLd = lam_max*D['cLd']*(1+1/tau)   # lam-terms: gain side (PSD)
    c_loc = np.zeros(N)
    for k in range(N):
        m = cell == k
        c_loc[k] = (np.max(fac[m]*np.abs(cB[m])) + np.max(oxLd[m]))*h**2/2 + (np.max(fac[m]*oxA[m]) + np.max(oxL[m]))*2*(h**3/3)*h
    cg = np.sum(wq*(fac*oxA + oxL))*2*h**2*tf/12
    a2 = D['P']['a2']
    gp = [a2*tf, a2*tf**2/2]
    cg += (1/taup-1)*rho*(gp[0]**2+gp[1]**2)*h**2*tf/12
    cg += (1/taup-1)*rhoc*1.0*h**2*tf/12
    return c_loc, cg

def solve_cert(D, rho, rhoc):
    N, h, par = D['N'], D['h'], D['par']
    tau, taup = par['tau'], par['taup']
    c_loc, cg = nprime_constants(D, rho, rhoc)
    lam_lb = np.maximum(c_loc + cg - D['Mlate'], 0.0)*1.02
    if np.any(lam_lb > D['lam_ub']): return None
    A = (1+tau)*D['Kp'] + (1-taup)*D['Km'] - (1-taup)*rho*D['G'].T@D['G'] - (1-taup)*rhoc*D['C'].T@D['C']
    A = (A+A.T)/2
    Lsum = lambda lv: sum(lv[k]*D['Lk'][k] for k in range(N))
    lam = cp.Variable(N)
    LK = sum(lam[k]*((1+tau)*D['Lk'][k]) for k in range(N))
    Mx = A + LK - cp.diag(h*(lam + D['Mlate']))
    prob = cp.Problem(cp.Minimize(h*cp.sum(cp.multiply(lam, D['Nb2']))),
                      [lam >= lam_lb, lam <= D['lam_ub'], (Mx+Mx.T)/2 << 0])
    try: prob.solve(solver='CLARABEL')
    except Exception: return None
    if lam.value is None: return None
    lv = np.clip(lam.value, lam_lb, D['lam_ub'])
    def top(lv):
        Mv = A + (1+tau)*Lsum(lv) - np.diag(h*(lv + D['Mlate']))
        return np.linalg.eigvalsh((Mv+Mv.T)/2).max()
    t = top(lv); it = 0
    while t > 0 and it < 20:          # uniform shift repair (the L_k term grows with lam, so iterate)
        lv = lv + 1.1*t/h; it += 1
        if np.any(lv > D['lam_ub']): return None
        t = top(lv)
    if t > 0: return None
    return dict(val=h*np.sum(lv*D['Nb2']), lam=lv, topeig=t, lam_lb=lam_lb)

def moment_term(D, rho, d=0.0):
    """Lemma 4.7: max_{Pen>=0} [ rho * sum_j (d + Mv_j + U_j(Pen))^2 - Pen ]."""
    P = D['P']; a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    tf, ss = D['tf'], D['ss']; zeta, xi = D['par']['zeta'], D['par']['xi']
    sg = np.linspace(0, tf, 40001); ds = sg[1]-sg[0]
    sph = np.sin(D['phibar'](sg)); vb = D['vbar'](sg)
    E = sg <= ss
    rs = lambda arr: np.sum(np.maximum(arr[:-1], arr[1:]))*ds        # upper Riemann sum (monotone pieces)
    Mv = [rs(np.where(E, sg**j*sph*eps*vb**2, 0)) + rs(sg**j*eps*D['rJ']*D['om3'](sg)*vb) for j in (0, 1)]
    Dmax = a2 - a1*np.cos(de) + eps*vb.max()**2
    om = np.where(E, xi*np.cos(D['phibar'](sg)), zeta)
    w = np.abs(sg-ss)
    etas = np.geomspace(1e-6, tf, 500)
    I = [np.array([rs(np.where(w < e+ds, sg**j*sph, 0)) for e in etas]) for j in (0, 1)]
    Z = [np.array([np.max((sg**j*sph/om)[w >= e-ds]) for e in etas]) for j in (0, 1)]
    Utriv = [rs(sg**j*sph*Dmax) for j in (0, 1)]
    grid = np.concatenate([[0], np.geomspace(1e-16, 1e3, 8000)])
    Us = np.array([[min(Utriv[j], np.min(Dmax*I[j] + P_*Z[j]/etas)) for j in (0, 1)] for P_ in grid])
    val = lambda U: rho*sum((d+Mv[j]+U[j])**2 for j in (0, 1))
    best = val(Us[0])
    for i in range(len(grid)-1):
        best = max(best, val(Us[i+1]) - grid[i])
    best = max(best, val(Utriv) - 1e3)
    return best

if __name__ == "__main__":
    tf = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
    ss = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
    N = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    gim = sys.argv[4] if len(sys.argv) > 4 else 'cone'
    deg = 15.0 if gim == 'cone' else np.degrees(np.arccos(np.cos(np.deg2rad(15))**2))
    P = gtpl(deg=deg)
    wfile = f"witness_{gim}_{tf}_{ss}.npy"
    if os.path.exists(wfile): nv = np.load(wfile)
    else:
        nv = optimize(P, tf, ss, N=100, starts=6)[1]; np.save(wfile, nv)
    ev = evaluate(P, tf, ss, nv)
    print(f"[{gim} delta={deg:.2f}] tf={tf} s*={ss}: witness G_w={ev['G']:.6e}, max tilt {np.degrees(ev['maxtilt']):.3f} deg, "
          f"max v_z(t<tf)={ev['maxvz']:.3e} (<0 => r_z>0 on [0,tf)), min r_z/|r_h|={ev['rzrel']:.3e}, r0={ev['r0']}, v0={ev['v0']}", flush=True)
    par = dict(PAR); par['roll'] = os.environ.get("ROLL", "0") == "1"
    print(f"  roll-rate competitors allowed: {par['roll']}", flush=True)
    D = setup(P, tf, ss, N, par)
    best = None
    for rho in [float(x) for x in os.environ.get("RHOS", "1e-3,3e-3,1e-2").split(",")]:
        for rhoc in [float(x) for x in os.environ.get("RHOCS", "1e-2,1e-1").split(",")]:
            c = solve_cert(D, rho, rhoc)
            if c is None:
                print(f"  rho={rho:g} rhoc={rhoc:g}: no certificate", flush=True); continue
            mt = moment_term(D, rho)
            U = c['val'] + mt
            print(f"  rho={rho:g} rhoc={rhoc:g}: SDP={c['val']:.5e} topeig={c['topeig']:.1e} moment={mt:.3e} U_total={U:.5e}  G_w/U={ev['G']/U:.4f}", flush=True)
            if best is None or U < best[0]: best = (U, rho, rhoc, c)
    if best:
        U, rho, rhoc, c = best
        ok = ev['G'] > U
        # quantitative: smallest d with  G_w - d*sqrt(1+s*^2) <= c.val + moment_term(d)
        dlo, dhi = 0.0, 1.0
        for _ in range(60):
            dm = (dlo+dhi)/2
            if ev['G'] - dm*np.sqrt(1+ss**2) > c['val'] + moment_term(D, rho, dm): dlo = dm
            else: dhi = dm
        print(f"RESULT tf={tf} s*={ss} N={N} {gim}: G_w={ev['G']:.5e}  U_total={U:.5e}  margin={(ev['G']-U):.3e} "
              f"({(ev['G']-U)/ev['G']*100:.1f}%)  dist(theta_m, F) >= {dlo:.3e}  certificate={'PASS' if ok else 'FAIL'}", flush=True)
        np.savez(f"cert_{gim}_{tf}_{ss}_{N}.npz", lam=c['lam'], U=U, Gw=ev['G'], rho=rho, rhoc=rhoc, dist=dlo)
