import numpy as np
from a3_1d_mass import curves
for (lab, a) in (('GTPL', 5.66e-4), ('x5', 5.66e-4*5), ('x8 mf/m0=0.55', 5.66e-4*8), ('x9.5 mf/m0=0.46', 5.66e-4*9.5)):
    c = curves(80, 400., 1000., a, 8.0)
    res = []
    for name, sgn in (('max', 1), ('min', -1)):
        S, W = c[name]; o = np.argsort(S); S, W = S[o], W[o]
        worst = 0
        for i in range(0, len(S), 20):
            for j in range(i+40, len(S), 20):
                Sm, Wm = (S[i]+S[j])/2, (W[i]+W[j])/2
                Wc = np.interp(Sm, S, W)
                worst = max(worst, sgn*(Wm - Wc))   # >0 => chord outside set
        res.append((name, worst, (W.max()-W.min())))
    print(lab, [(n, f"{w:.3e}", f"rel {w/r:.2e}") for n, w, r in res])
