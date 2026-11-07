"""[proof-tvc] Localization lemma (math/06 Lemma 4.0): explicit a-priori bounds on speed v=|bdot| and tilt for every
relaxed competitor with gain W_z - J0 >= 0 (variant R0: omega3 = 0). Returns piecewise-constant (per cell of a fine
grid) upper bounds vloc(s), philoc(s); each is min(crude, localized).
Steps (all inequalities in math/06 §4.0):
 E0  : Pen_E(1-c_abs) + int_L w Pi <= E0 := int_E |w| [A1 (1+k)(K1 s^2/2)^2 + B1 (1+k) K1^2 s^2]   (c_abs < 1 checked)
 late: int_L w|h|^2 <= 2E0/a2, int_L w v^2 <= E0/(eps c0), int_L w |q|^2 <= 2 a2 E0/c0^2  (c0 = cos phibar0 max)
       Agmon on [s0, tf]: sup g^2 <= int g^2/len + 2 sqrt(int g^2 int g'^2), weights w >= s0-s*, |v'| <= |q|/eps
 near s*: v(s) <= v(s*) + K2 (s-s*), |h|(s) <= sin phi(s*) + int v
 early: v(s) <= min(K2 s, K1 s + beta Ybar(s)), Ybar(s) = min(dpmax s, Pen_E^max/(cos0 (s*-s))), phi <= int v
"""
import numpy as np

def localize(P, tf, ss, kap=0.1, M=4001, roll=False, Ja=3.74, Jt=63.6, tau_r=3.0, theta_g=0.15):
    a1, a2, de, eps = P['a1'], P['a2'], P['de'], P['eps']
    K1 = a1*np.sin(de)/eps; K2 = a2*np.sin(de)/eps
    beta = np.tan(de)/eps; dpmax = a2-a1*np.cos(de)
    phib0 = lambda s: K2*np.minimum(s, tf-s)**2/2
    vb0 = lambda s: K2*np.minimum(s, tf-s)
    c0 = np.cos(phib0(tf/2))
    cE = np.cos(phib0(ss))                       # early cos lower bound
    A1 = a1*np.cos(de)/(1+cE); B1 = eps/cE**2
    # absorption constant of the Delta p contributions (speed and tilt) into Pen_E (coefficient cE)
    c_abs_v = B1*(1+1/kap)*beta**2*dpmax*ss**2/2/cE
    c_abs_t = A1*(1+1/kap)*beta**2*dpmax*ss**4/2/cE      # tilt: phi <= int v, (int beta Y)^2 <= s^2 beta^2 Y(s)^2-type bound
    c_abs = c_abs_v + c_abs_t
    assert c_abs < 0.9, c_abs
    s = np.linspace(0, ss, M)
    E0 = np.trapezoid((ss-s)*(A1*(1+kap)*(K1*s**2/2)**2 + B1*(1+kap)*K1**2*s**2), s)*1.001
    lat_fac = 1.0
    if roll:
        # (R1) gyro vertical term |w| eps (Ja/Jt) om3bar |h||hdot|: early part bounded a priori (|h|<=phibar0, |hdot|<=vbar0),
        # late part absorbed into theta_g*Pi via AM-GM: cg|h||hd| <= cg(gam|h|^2 + |hd|^2/gam)/2 <= theta_g((a2/2)|h|^2 + eps c0 |hd|^2)
        cgmax = eps*(Ja/Jt)*(tau_r/Ja)*tf
        gam = np.sqrt((eps*c0)/(a2/2))
        assert cgmax*gam/2 <= theta_g*a2/2 and cgmax/(2*gam) <= theta_g*eps*c0, "gyro absorption fails"
        E0 += np.trapezoid((ss-s)*eps*(Ja/Jt)*(tau_r/Ja)*s*np.sin(phib0(s))*vb0(s), s)*1.001
        lat_fac = 1/(1-theta_g)
    PenE = E0/(1-c_abs)
    LhW = 2*E0/a2*lat_fac; LvW = E0/(eps*c0)*lat_fac; LqW = 2*a2*E0/c0**2*lat_fac
    # early bounds
    etag = np.concatenate([[0], np.geomspace(1e-7, ss, 400)])
    def Ybar(x):
        x = np.atleast_1d(x)
        out = np.array([np.min(np.minimum(dpmax*xx, dpmax*np.minimum(etag, xx) + PenE/(cE*(ss-xx+etag+1e-300)))) for xx in x])
        return out
    vE = lambda x: np.minimum(K2*x, K1*x + beta*Ybar(x))
    sg = np.linspace(0, tf, 20001)
    v = np.zeros_like(sg); phi = np.zeros_like(sg)
    E = sg <= ss
    v[E] = vE(sg[E])
    # integrate tilt early (upper Riemann sum of v)
    dsg = sg[1]-sg[0]
    phiE = np.concatenate([[0], np.cumsum(np.maximum(v[E][:-1], v[E][1:])*dsg)])
    phi[E] = np.minimum(phiE, phib0(sg[E]))
    vss = v[E][-1]; phiss = phi[E][-1]
    # late: for each s0 > s*, Agmon on [s0, tf]
    L = ~E
    for i in np.where(L)[0]:
        s0 = sg[i]; sig = s0-ss
        # near-s* Lipschitz bounds
        v_lip = vss + K2*sig
        if sig > 1e-6:
            Iv = LvW/sig; Ivd = LqW/(eps**2*sig); ln = tf-s0
            v_ag = np.sqrt(Iv/max(ln, 1e-12) + 2*np.sqrt(Iv*Ivd)) if ln > 1e-9 else 0.0
        else:
            v_ag = np.inf
        v[i] = min(vb0(s0), v_lip, v_ag)
    # tilt late: |h| bound by Lipschitz from s* and by Agmon with int w|h|^2, int w|h'|^2 <= int w v^2
    vcum = np.concatenate([[0], np.cumsum(np.maximum(v[L][:-1], v[L][1:])*dsg)])
    hlate = np.zeros(L.sum())
    for jj, i in enumerate(np.where(L)[0]):
        s0 = sg[i]; sig = s0-ss
        h_lip = np.sin(min(phiss, np.pi/2)) + vcum[jj]
        if sig > 1e-6 and tf-s0 > 1e-9:
            Ih = LhW/sig; Ihd = LvW/sig
            h_ag = np.sqrt(Ih/(tf-s0) + 2*np.sqrt(Ih*Ihd))
        else:
            h_ag = np.inf
        hlate[jj] = min(np.sin(min(phib0(s0), np.pi/2)), h_lip, h_ag, 1.0)
    phi[L] = np.arcsin(np.minimum(hlate, 1.0))
    # rigorous step-function bounds: v is K2-Lipschitz and phi is (max v)-Lipschitz, so on the fine cell
    # [sg_i, sg_{i+1}] the true values are <= max(bound_i, bound_{i+1}) + Lip*ds.
    vcell = np.maximum(v[:-1], v[1:]) + K2*dsg
    pcell = np.maximum(phi[:-1], phi[1:]) + (v.max()+K2*dsg)*dsg
    def stepfun(cellvals):
        def f(x):
            x = np.asarray(x, dtype=float)
            i = np.clip(np.floor(x/dsg).astype(int), 0, len(cellvals)-1)
            j = np.clip(np.ceil(x/dsg).astype(int)-1, 0, len(cellvals)-1)   # at a breakpoint take both cells
            return np.maximum(cellvals[i], cellvals[j])
        return f
    vfun = stepfun(vcell); phifun = stepfun(pcell)
    vfun.cells = vcell; phifun.cells = pcell; vfun.ds = dsg; phifun.ds = dsg
    v = np.concatenate([vcell, vcell[-1:]]); phi = np.concatenate([pcell, pcell[-1:]])
    info = dict(lat_fac=lat_fac, E0=E0, PenE=PenE, c_abs=c_abs, vmax=v.max(), phimax=phi.max(), v_late_max=v[L].max(), phi_late_max=phi[L].max())
    return vfun, phifun, info, (sg, v, phi)

if __name__ == "__main__":
    from witness_nl import gtpl
    P = gtpl()
    for tf, ss in [(1.0, 0.25), (1.0, 0.35), (1.5, 0.4)]:
        vf, pf, info, _ = localize(P, tf, ss)
        print(tf, ss, {k: (round(v, 5) if isinstance(v, float) else v) for k, v in info.items()},
              "crude vmax", round(P['a2']*np.sin(P['de'])/P['eps']*tf/2, 3), "crude phimax", round(P['a2']*np.sin(P['de'])/P['eps']*tf**2/8, 3))
