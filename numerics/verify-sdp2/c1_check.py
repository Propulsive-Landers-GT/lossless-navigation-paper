"""[verify-sdp2] Re-check of math/09 §8 'T5 certifies 16/17 [numerics] c1 cases': for each c1 case (cvx15), compute the
genuine optimum with the independent core, SDP value, stress Q, and WHICH certificate applies:
T4 LP criterion, T5 hypotheses (Z nonsingular, chain connected, D>0, h_m != 0, Yres invertible) and class, or only the
direct stress test Q >= 0 (math/08 Thm 2.1)."""
import sys, os, json
import numpy as np
_here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(_here, '..')); sys.path.insert(0, os.path.join(_here, '../redteam-lift'))
from c1_csd2_check import make_cases
from core import Model
from t45_lib import analyze
cases, a1 = make_cases()
rng = np.random.default_rng(11)
for ci, c in enumerate(cases):
    if c['N'] > 24 or ci in (14, 17):
        continue
    wv, wr = np.array(c['wv_m'], float), np.array(c['wr_m'], float)
    # c1 vectors are (x, y, z) with z vertical? check: vertical component is the one ~ G0*tf
    M = Model(c['N'], c['tf'], c['om'], 15, 'cvx', terminal=True, a=np.full(c['N'], a1))
    s = M.sdp(wv, wr)
    best, z, _ = M.best(wv, wr, rng=rng, nstart=6, extra=[M.factor(s['G'], dim=3)])
    r = analyze(M, z, wv, wr, s['val'])
    hyp = r['zeroZ'] == 0 and r.get('Dpos') and r.get('S_offmax', 0) < -1e-9 and r.get('hmin_int', 0) > 1e-6 and r['detYres'] > 1e-3
    print(f"case {ci} set {c['set']} N={c['N']}: SDP={s['val']:.7g} gen={best:.7g} relgap={(best-s['val'])/max(best,1e-9):+.1e} res={r['res']:.0e} "
          f"negQ={r['negQ']} minQ={r['minQ']:+.1e} crit={r['crit']:+.2f} k={r['k']} negZ={r['negZ']} zeroZ={r['zeroZ']} p0={r['p0']} "
          f"Dpos={r.get('Dpos')} Soff={r.get('S_offmax',0):+.1e} T5hyps={hyp}", flush=True)
