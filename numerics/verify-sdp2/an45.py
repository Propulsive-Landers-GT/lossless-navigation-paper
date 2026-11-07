"""[verify-sdp2] analysis of t45_*.jsonl (T4 criterion, T5 identity/Sturm, exactness)."""
import sys, json, collections
import numpy as np

R = []
for f in sys.argv[1:]:
    R += [json.loads(l) for l in open(f)]
c = collections.Counter()
flags = []
for i, r in enumerate(R):
    good = r['res'] < 1e-5
    c['total'] += 1
    if not good:
        c['bad KKT residual (NLP not converged) - skipped'] += 1
        continue
    c['good'] += 1
    gap = r['relgap']
    c['exact (|gap|<=1e-5)' if gap <= 1e-5 else 'GAP>1e-5'] += 1
    if gap > 1e-5:
        flags.append(('gap', i, r['kind'], r['delta'], r['term'], r['N'], r['typ'], r['wtf'], gap, r['negQ'], r['crit']))
    # T4
    if r['crit'] > 1e-6:
        c['T4 crit true'] += 1
        ok = (r['negQ'] == 0) and gap <= 1e-5
        c['T4 crit true & (Q psd & exact)' if ok else 'T4 VIOLATION?'] += 1
        if not ok:
            flags.append(('T4', i, r['kind'], r['delta'], r['term'], r['typ'], gap, r['negQ'], r['minQ'], r['crit']))
    if r['typ'] == 'short':
        c['short-class'] += 1
        c['short-class crit true' if r['crit'] > 1e-6 else 'short-class crit FALSE'] += 1
    for o in r['others']:
        if o['res'] < 1e-5:
            c['other local KKT pts'] += 1
            if o['crit'] > 1e-6:
                c['OTHER (non-global) KKT pt passing T4 crit  <-- would break T4'] += 1
                flags.append(('T4other', i, r['typ'], o))
            if r['typ'] == 'short':
                c['short-class non-global local KKT pt'] += 1
    # T5 identity
    hyp51 = r['zeroZ'] == 0 and r['detYres'] > 1e-3 and r['k'] >= 0 and r['asym'] < 1e-5
    if r['k'] >= 0 and r['detYres'] > 1e-3 and r['asym'] < 1e-5:
        c['identity tested (any Z)'] += 1
        c['identity holds (any Z)' if r['negQ'] == r['negZ'] - r['p0'] else 'identity fails (any Z)'] += 1
    if hyp51:
        c['T5.1 hyps hold'] += 1
        okid = r['negQ'] == r['negZ'] - r['p0']
        c['T5.1 identity OK' if okid else 'T5.1 IDENTITY FAIL'] += 1
        if not okid:
            flags.append(('T5.1', i, r['negQ'], r['negZ'], r['p0'], r['ecyw']))
    hyp52 = hyp51 and r.get('Dpos') and r.get('S_offmax', 0) < -1e-9 and r.get('hmin_int', 0) > 1e-6 and r.get('S_tridiag', False) \
        and r.get('zeta0', 0) > 1e-8
    if hyp52:
        key = 'T' if r['term'] else 'F'
        c[f'T5.2 hyps hold case {key}'] += 1
        k, nz = r['k'], r['negZ']
        if key == 'T':
            c['  case T: k-1<=negZ<=k ' + ('OK' if k - 1 <= nz <= k else 'FAIL')] += 1
            if not (k - 1 <= nz <= k):
                flags.append(('Sturm T', i, k, nz, r['negS']))
        else:
            c['  case F: k-1<=negZ<=k ' + ('OK' if k - 1 <= nz <= k else 'FAIL')] += 1
            c['  case F: negZ == k ' + ('OK' if nz == k else 'FAIL')] += 1
        cls = 'certified k<=p0' if k <= r['p0'] else ('k>=p0+2' if k >= r['p0'] + 2 else 'residual k=p0+1')
        c[f'  class {key}: ' + cls] += 1
        if cls.startswith('residual'):
            c[f'  residual {key}: negZ=' + ('k-1 (exact)' if nz == k - 1 else 'k')] += 1
        c[f'  (k,negZ,p0,negQ) {key} {(k, nz, r["p0"], r["negQ"])}'] += 1
    else:
        why = []
        if r['zeroZ'] > 0: why.append('Z singular')
        if not r.get('Dpos', True): why.append('mu_d=0 somewhere')
        if r.get('S_offmax', -1) >= -1e-9: why.append('chain disconnected')
        if r['detYres'] <= 1e-3: why.append('Yres singular')
        if r.get('hmin_int', 1) <= 1e-6: why.append('h_m=0 at a node')
        c['T5 hyps fail: ' + ','.join(why)] += 1
for k in sorted(c):
    print(f'{k:70s} {c[k]}')
print('\nFLAGS:')
for f in flags:
    print(f)
