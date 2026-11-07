import json, sys, numpy as np
R = [json.loads(l) for l in open(sys.argv[1])]
for r in R:
    nd = min(abs(e) for e in r['ecyw']) > 1e-3 and r['k'] >= 0 and r['asym'] < 1e-6
    if not nd: continue
    if (r['k'] == 0 and r['negZ'] > 0) or (r['k'] - 1 > r['negZ']) or r['negZ'] > r['k']:
        h = np.array(r['hint']) if r['hint'] else None
        print(r['N'], r['model'], round(r['wtf'], 2), 'k', r['k'], 'negZ', r['negZ'], 'zeroZ', r['zeroZ'], 'p0', r['p0'],
              'h0=%.2e' % h[0], 'hmin_int=%.2e' % h[1:-1].min(), 'h_int_neg=%d' % np.sum(h[1:-1] < 0), 'mud_min=%.1e' % r['mud_min'], 'res=%.0e' % r['res'])
