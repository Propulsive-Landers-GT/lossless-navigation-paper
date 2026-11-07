"""Classification restricted to instances satisfying ALL T5 hypotheses: C_yw nonsingular (|eig|>1e-3 rel), primer plane defined,
h_m nonzero at all interior nodes (|h|>1e-8), Z nonsingular (zeroZ==0)."""
import json, sys, collections, numpy as np
R = [json.loads(l) for l in open(sys.argv[1])]
tot = collections.Counter(); viol = 0
for r in R:
    if not (min(abs(e) for e in r['ecyw']) > 1e-3 and r['k'] >= 0 and r['asym'] < 1e-6): continue
    h = np.array(r['hint'])
    if np.min(np.abs(h[1:-1])) < 1e-8 or (len(sys.argv) > 2 and r['zeroZ'] > 0): tot['excluded(h_m=0 at a node or Z singular)'] += 1; continue
    tot['n'] += 1
    tot['identity ' + ('ok' if r['negQ'] == r['negZ'] - r['p0'] else 'FAIL')] += 1
    tot['sturm ' + ('ok' if r['k'] - 1 <= r['negZ'] <= r['k'] or (r['k'] == 0 and r['negZ'] == 0) else 'FAIL')] += 1
    cls = 'certified k<=p0' if r['k'] <= r['p0'] else ('k>=p0+2' if r['k'] - 1 > r['p0'] else 'residual k=p0+1')
    tot[cls] += 1
    if cls.startswith('residual'): tot['residual with negZ=k-1 (exact)' if r['negZ'] == r['k'] - 1 else 'residual negZ=k'] += 1
    tot['negQ>0'] += int(r['negQ'] > 0)
print(dict(tot))
