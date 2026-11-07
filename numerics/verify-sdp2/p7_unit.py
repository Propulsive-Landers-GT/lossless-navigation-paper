"""[verify-sdp2] P7 on fresh unit-d gap instances: at the genuine D^unit optimum, sign of the norm multipliers mu_d,
lambda_min(Q); then the convexified version at the same target (mu_d >= 0, Q psd, SDP_cvx = genuine_cvx?).
Also checks the rigorous part: >= 3 negative mu_d  =>  Q not psd (rank-2 C)."""
import sys, json
import numpy as np
from core import Model, EZ

rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
nwant = int(sys.argv[2]) if len(sys.argv) > 2 else 15
out = open('p7_unit.jsonl', 'w')
found = 0; tried = 0
while found < nwant and tried < 400:
    tried += 1
    N = int(rng.choice([3, 4, 5])); dd = int(rng.choice([15, 40])); wtf = float(rng.choice([0.6, 1.0, 1.5]))
    Mu = Model(N, 1.0 * N / 4 * 4, wtf / (N), dd, 'unit', terminal=True)
    Mu = Model(N, 4.0, wtf / 4.0, dd, 'unit', terminal=True)
    S = Mu.cv.sum(); Sr = Mu.cr.sum()
    wv = np.r_[rng.normal(size=2) * 0.3 * S, rng.uniform(0.5, 1.0) * S]
    wr = np.r_[rng.normal(size=2) * 0.3 * Sr, rng.uniform(0.5, 1.0) * Sr]
    s = Mu.sdp(wv, wr)
    best, z, _ = Mu.best(wv, wr, rng=rng, nstart=25, extra=[Mu.factor(s['G'], dim=3)])
    if z is None:
        continue
    gap = (best - s['val']) / max(best, 1e-9)
    if gap < 1e-3:
        continue
    K = Mu.kkt(z, wv, wr)
    if K['res'] > 1e-5:
        continue
    sc = np.abs(K['Q']).max()
    mud = K['mu'][Mu.nb:] / sc
    lq = np.linalg.eigvalsh(K['Q'])[0] / sc
    Mc = Model(N, 4.0, wtf / 4.0, dd, 'cvx', terminal=True)
    sc_ = Mc.sdp(wv, wr)
    bc, zc, _ = Mc.best(wv, wr, rng=rng, nstart=25, extra=[Mc.factor(sc_['G'], dim=3), z])
    Kc = Mc.kkt(zc, wv, wr)
    scc = np.abs(Kc['Q']).max()
    rec = dict(N=N, delta=dd, wtf=wtf, gap_unit=gap, n_mud_neg=int(np.sum(mud < -1e-9)), mud_min=float(mud.min()),
               lminQ_unit=float(lq), licq=bool(K['licq']), sdp_cvx=sc_['val'], gen_cvx=bc,
               gap_cvx=(bc - sc_['val']) / max(bc, 1e-9), mud_cvx_min=float(Kc['mu'][Mc.nb:].min() / scc),
               lminQ_cvx=float(np.linalg.eigvalsh(Kc['Q'])[0] / scc), res_cvx=Kc['res'])
    out.write(json.dumps(rec) + '\n'); out.flush(); found += 1
    print(rec, flush=True)
print('tried', tried, 'found', found)
