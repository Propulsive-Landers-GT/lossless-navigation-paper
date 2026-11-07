import os; os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np
from lateral import V
def scan(tf, dl, ns=600, nb=3001):
    prev = None; best = 0.0
    for sig in np.linspace(0.01, 0.99, ns) * tf:
        bs = np.linspace(-sig, sig, nb); arg = bs[np.argmax(V(bs, sig, tf, dl))] / sig
        if prev is not None: best = max(best, abs(arg - prev))
        prev = arg
    return best
# sanity vs quadrature version
from scipy.integrate import quad
def Vq(b, sig, tf, dl):
    L = lambda s: max(-s, b - (sig - s))
    return quad(lambda s: (sig-s)*max(0, np.sin(dl-L(s))), 0, sig, points=[(sig-b)/2], limit=200)[0] + \
           quad(lambda s: (s-sig)*max(0, np.sin(dl+b+s-sig)), sig, tf, limit=200)[0]
print("closed-form check:", max(abs(V(b, .7, 1.2, .26) - Vq(b, .7, 1.2, .26)) for b in np.linspace(-.7, .7, 15)))
degs = [0, 2, 5, 10, 15, 25, 40, 60]
print("rows omega*tf, cols delta(deg)", degs, " entry = max jump of argmax(beta*)/sigma in sigma (0 => continuous)")
for wtf in [0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.55]:
    row = []
    for d in degs:
        dl = np.deg2rad(d)
        row.append("   -- " if dl + wtf > np.pi/2 else f"{scan(wtf, dl):6.3f}")
    print(f"{wtf:5.2f} " + " ".join(row), flush=True)
