"""[verify-sdp2] Sharp adversarial test of T4 / Cor 4.3 (discrete form): in the vertical-shortfall class with omega*tf < pi
(case T) / < pi/2 (case F), c = e_z satisfies the LP criterion at EVERY feasible point, so T4 asserts that EVERY KKT point
is a global minimizer (all local minima have the same value = SDP value).  We hunt for distinct local minima with many
starts, large opposed lateral demands, omega*tf near the limit, delta up to 40 deg, non-constant thrust profiles."""
import sys, json
import numpy as np
from core import Model, EZ

rng = np.random.default_rng(int(sys.argv[1]))
nins = int(sys.argv[2])
out = open(f't4_short_{sys.argv[1]}.jsonl', 'w')
worst = 0.0
for it in range(nins):
    term = bool(rng.random() < 0.6)
    kind = str(rng.choice(['cvx', 'cvx', 'd0']))
    dd = int(rng.choice([15, 25, 40])) if kind == 'cvx' else 0
    N = int(rng.choice([6, 8, 10]))
    lim = np.pi if term else np.pi / 2
    wtf = float(rng.uniform(0.6, 0.98) * lim)
    t = (np.arange(N) + 0.5) / N
    a = [np.ones(N), 1 / (1 - 0.35 * t), 0.5 + t][int(rng.integers(3))]
    M = Model(N, 4.0, wtf / 4.0, dd, kind, terminal=term, a=a)
    Sv, Sr = M.cv.sum(), M.cr.sum()
    f = 1 + rng.uniform(0.0, 0.3)
    d1 = rng.normal(size=2); d1 /= np.linalg.norm(d1)
    d2 = -d1 + 0.5 * rng.normal(size=2)
    wv = np.r_[d1 * Sv * rng.uniform(0.3, 1.5), f * Sv]
    wr = np.r_[d2 * Sr * rng.uniform(0.3, 1.5), f * Sr]
    s = M.sdp(wv, wr)
    best, z, cands = M.best(wv, wr, rng=rng, nstart=30, extra=[M.factor(s['G'], dim=3)])
    if z is None:
        continue
    vals = []
    for (v, zz) in cands:
        K = M.kkt(zz, wv, wr)
        if K['res'] < 1e-6:
            tcrit, _ = M.criterion(zz, K['yv'], K['yr'])
            vals.append((v, tcrit, int(np.sum(np.linalg.eigvalsh(K['Q']) < -1e-7 * np.abs(K['Q']).max()))))
    spread = (max(v for v, _, _ in vals) - min(v for v, _, _ in vals)) / max(best, 1e-9) if vals else -1
    worst = max(worst, spread)
    rec = dict(kind=kind, delta=dd, term=term, N=N, wtf=wtf, sdp=s['val'], best=best, relgap=(best - s['val']) / max(best, 1e-9),
               nkkt=len(vals), spread=spread, mincrit=min(c for _, c, _ in vals) if vals else None,
               maxnegQ=max(q for _, _, q in vals) if vals else None)
    out.write(json.dumps(rec) + '\n'); out.flush()
    print(rec, flush=True)
print('WORST relative spread of local-KKT values:', worst)
