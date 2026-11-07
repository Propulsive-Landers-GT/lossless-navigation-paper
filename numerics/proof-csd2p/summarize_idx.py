import json, sys, collections
R = [json.loads(l) for l in open(sys.argv[1])]
c = collections.Counter(); tot = collections.Counter()
for r in R:
    nd = min(abs(e) for e in r['ecyw']) > 1e-3 and r['k'] >= 0 and r['asym'] < 1e-6
    ok = r['negQ'] == r['negZ'] - r['p0']
    cls = 'proved(k<=p0)' if r['k'] <= r['p0'] else ('obstructed(k>=p0+2)' if r['k'] - 1 > r['p0'] else 'open(k=p0+1)')
    c[(nd, ok, cls, r['k'], r['negZ'], r['p0'], r['negQ'], r['rel'] > 1e-4)] += 1
    if nd: tot[cls] += 1; tot['identity_ok' if ok else 'identity_fail'] += 1; tot['n'] += 1
for k, v in sorted(c.items()): print('nondeg,identity,class,k,negZ,p0,negQ,gap', k, v)
print(len(R), dict(tot))
