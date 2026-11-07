"""[verify-sdp2] T4 (hemisphere/Picone LP criterion), T5 (index identity + Sturm bounds), exactness, on FRESH instances:
non-constant thrust profiles a_k (mass-depletion-like and ramps), delta in {15,25,40}, odd N, case T and case F,
targets: random, dent mixtures of two support points, vertical-shortfall (Cor 4.3, discrete form), and lateral overshoot.
Adversarial T4 check: EVERY local KKT point found by multistart that passes the LP criterion must be globally optimal
(value = SDP).  Usage: python t45.py <tag> <seed> <ninst>"""
import sys, json, time
import numpy as np
from core import Model, EZ, E

tag, seed, ninst = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
rng = np.random.default_rng(seed)
out = open(f't45_{tag}.jsonl', 'w')


def profile(N, kind):
    t = (np.arange(N) + 0.5) / N
    if kind == 'const':
        return np.ones(N)
    if kind == 'mass':        # a = rho/m(t), m decreasing 30%
        return 1.0 / (1 - 0.3 * t)
    if kind == 'ramp':
        return 0.6 + 0.8 * t
    return 1.2 - 0.5 * t      # 'down'


def support_readout(M, rng):
    y = rng.normal(size=6)
    val, z, _ = M.best(obj=('lin', y[:3], y[3:]), rng=rng, nstart=3)
    if z is None:
        return None
    V, R = M.readout(z)
    return V[:3], R[:3]


def target(M, typ, rng):
    Uv = (M.cv.sum()) * EZ; Ur = (M.cr.sum()) * EZ
    Sv, Sr = M.cv.sum(), M.cr.sum()
    lat = lambda s: np.r_[rng.normal(size=2) * s, 0.0]
    if typ == 'rand':
        return Uv * rng.uniform(0.3, 1.1) + lat(0.4 * Sv), Ur * rng.uniform(0.3, 1.1) + lat(0.4 * Sr)
    if typ == 'mix':
        a = support_readout(M, rng); b = support_readout(M, rng)
        if a is None or b is None:
            return None
        lam = rng.uniform(0.3, 0.7)
        return lam * a[0] + (1 - lam) * b[0], lam * a[1] + (1 - lam) * b[1]
    if typ == 'short':
        # discrete Cor 4.3: w_vz + s w_rz >= sum(cv + s cr) for s in {h/2, tf-h/2}; inflate by (1+eps)
        f = 1 + rng.uniform(0.02, 0.4)
        return Uv * f + lat(0.6 * Sv), Ur * f + lat(0.6 * Sr)
    if typ == 'over':
        d = rng.normal(size=2); d /= np.linalg.norm(d)
        return Uv * rng.uniform(0.5, 0.9) + np.r_[d * Sv * rng.uniform(0.5, 1.2), 0], \
               Ur * rng.uniform(0.5, 0.9) + np.r_[(-d + 0.7 * rng.normal(size=2)) * Sr * rng.uniform(0.3, 1.0), 0]


def analyze(M, z, wv, wr, sdpval):
    K = M.kkt(z, wv, wr)
    Q, Zm = K['Q'], K['Z']
    sc = np.abs(Q).max(); tol = 1e-7 * sc
    eq, ez = np.linalg.eigvalsh(Q), np.linalg.eigvalsh(Zm)
    yv, yr = K['yv'], K['yr']
    m = np.cross(yv, yr); nm = np.linalg.norm(m)
    rec = dict(res=K['res'], licq=bool(K['licq']), negQ=int(np.sum(eq < -tol)), negZ=int(np.sum(ez < -tol)),
               zeroZ=int(np.sum(np.abs(ez) <= tol)), minQ=float(eq[0] / sc), minZ=float(ez[0] / sc))
    if M.kind != 'd0':
        mud = K['mu'][M.nb:]
        rec['mud_min'] = float(mud.min() / sc); rec['mud_npos'] = int(np.sum(mud > tol))
    t, c = M.criterion(z, yv, yr)
    rec['crit'] = t
    # C_yw, Yres
    Cyw = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2])
    rec['asym'] = float(abs(Cyw[0, 1] - Cyw[1, 0]) / (np.abs(Cyw).max() + 1e-300))
    ec = np.linalg.eigvalsh(0.5 * (Cyw + Cyw.T)); ecn = ec / (np.abs(ec).max() + 1e-300)
    rec['ecyw'] = ecn.tolist()
    rec['p0'] = int(np.sum(ecn >= -1e-9))
    Yres = np.vstack([yv[:2], yr[:2]])
    rec['detYres'] = float(abs(np.linalg.det(Yres)) / (np.linalg.norm(yv[:2]) * np.linalg.norm(yr[:2]) + 1e-300))
    # primer-plane normal, h_m on nodes b_0..b_N, crossings
    if nm > 1e-10 * np.linalg.norm(yv) * np.linalg.norm(yr):
        m /= nm
        if m @ EZ < 0:
            m = -m
        B = M.nodes(z); h = B @ m
        rec['zeta0'] = float(m @ EZ)
        rec['hmin_int'] = float(np.min(np.abs(h[1:-1]))) if M.terminal else float(np.min(np.abs(h[1:])))
        hh = h.copy(); hh[0] = 1.0
        if M.terminal:
            hh[-1] = 1.0
        s = np.sign(hh)
        rec['k'] = int(np.sum(s[1:] != s[:-1]))
        rec['h'] = h.tolist()
    else:
        rec['k'] = -1
    # Schur chain S on b-slots
    nb = M.nb
    if M.kind != 'd0':
        D = np.diag(Zm)[nb:]
        rec['Dpos'] = bool(np.all(D > tol))
        if rec['Dpos']:
            S = Zm[:nb, :nb] - Zm[:nb, nb:] @ np.diag(1 / D) @ Zm[nb:, :nb]
        else:
            S = None
    else:
        rec['Dpos'] = True
        S = Zm.copy()
    if S is not None:
        off = np.array([S[i, i + 1] for i in range(nb - 1)])
        rec['S_offmax'] = float(off.max() / sc) if len(off) else -1.0
        rec['S_tridiag'] = bool(np.allclose(np.triu(S, 2), 0, atol=1e-12 * sc))
        rec['negS'] = int(np.sum(np.linalg.eigvalsh(S) < -tol))
    rec['gap'] = None
    return rec


def main():
    t0 = time.time(); cnt = 0
    while cnt < ninst:
        kind = rng.choice(['cvx', 'cvx', 'cvx', 'd0'])
        dd = int(rng.choice([15, 25, 40])) if kind == 'cvx' else 0
        term = bool(rng.random() < 0.7)
        N = int(rng.choice([5, 7, 9]))
        prof = str(rng.choice(['const', 'mass', 'ramp', 'down']))
        typ = str(rng.choice(['rand', 'mix', 'short', 'over', 'short']))
        if typ == 'short':
            wtf = float(rng.uniform(0.5, 0.95 * (np.pi if term else np.pi / 2)))
        else:
            wtf = float(rng.choice([1.0, 2.0, 3.5, 5.0]))
        M = Model(N, 4.0, wtf / 4.0, dd, kind, terminal=term, a=profile(N, prof))
        tw = target(M, typ, rng)
        if tw is None:
            continue
        wv, wr = tw
        try:
            s = M.sdp(wv, wr)
        except Exception as e:
            continue
        zs = M.factor(s['G'], dim=3)
        best, z, cands = M.best(wv, wr, rng=rng, nstart=10, extra=[zs])
        if z is None:
            continue
        rec = dict(kind=kind, delta=dd, term=term, N=N, prof=prof, typ=typ, wtf=wtf, wv=wv.tolist(), wr=wr.tolist(),
                   sdp=s['val'], nlp=best, rank=int(np.sum(s['ev'] > 1e-6 * s['ev'][0])))
        rec['relgap'] = (best - s['val']) / max(abs(best), 1e-9)
        rec.update(analyze(M, z, wv, wr, s['val']))
        # adversarial T4: other local KKT points passing the criterion must be global
        others = []
        seen = [best]
        for (v, zz) in cands[1:]:
            if v - best < 1e-6 * max(1, abs(best)) or any(abs(v - u) < 1e-7 * max(1, abs(u)) for u in seen):
                continue
            seen.append(v)
            a = analyze(M, zz, wv, wr, s['val'])
            others.append(dict(val=v, res=a['res'], crit=a['crit'], negQ=a['negQ'], k=a.get('k'), p0=a['p0'], negZ=a['negZ']))
        rec['others'] = others
        out.write(json.dumps(rec) + '\n'); out.flush(); cnt += 1
        print(f"[{cnt}] {kind}{dd} T={int(term)} N={N} {prof} {typ} wtf={wtf:.2f} gap={rec['relgap']:+.1e} res={rec['res']:.0e} "
              f"crit={rec['crit']:+.2f} negQ={rec['negQ']} negZ={rec['negZ']}(0:{rec['zeroZ']}) p0={rec['p0']} k={rec['k']} "
              f"others={[(round(o['val'],4), round(o['crit'],2), o['negQ']) for o in others]} t={time.time()-t0:.0f}s", flush=True)


main()
