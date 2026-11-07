"""[verify-sdp2] Re-solve the two non-axis idx_full records with asym>1e-6 and recompute C_yw at the genuine optimum."""
import json, numpy as np
from core import Model
R = [json.loads(l) for l in open('../verifier-sdp/results/idx_full.jsonl')]
rng = np.random.default_rng(0)
for r in R:
    if r['asym'] > 1e-6 and np.linalg.norm(np.r_[r['wv'][:2], r['wr'][:2]]) > 1e-6:
        wv, wr = np.array(r['wv']), np.array(r['wr'])
        M = Model(r['N'], 4.0, r['wtf'] / 4.0, int(r['model'][3:]), 'cvx', terminal=r.get('term', True), a=np.full(r['N'], 11.0))
        s = M.sdp(wv, wr)
        best, z, _ = M.best(wv, wr, rng=rng, nstart=4, extra=[M.factor(s['G'], dim=3)])
        K = M.kkt(z, wv, wr); yv, yr = K['yv'], K['yr']
        C = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2])
        print('N', r['N'], 'SDP %.8g gen %.8g res %.1e' % (s['val'], best, K['res']), 'C_yw=', np.round(C, 6),
              'asym abs %.1e, |y_h| %.2e %.2e, angle(yv_h,yr_h)=%.2e' % (abs(C[0, 1] - C[1, 0]), np.linalg.norm(yv[:2]), np.linalg.norm(yr[:2]),
              abs(yv[0]*yr[1]-yv[1]*yr[0]) / (np.linalg.norm(yv[:2]) * np.linalg.norm(yr[:2]) + 1e-300)))
