import numpy as np
from models import *
P=gtpl()
for planar in [True,False]:
    R=ReachM1(P,2.0,30 if not planar else 40,planar=planar,eq_idx=(0,) if planar else (0,1))
    rng=np.random.default_rng(0)
    for i in range(200):
        x0=R.random_x0(rng)
        if not np.all(np.isfinite(x0)): print('nan x0',planar,i); break
        f=R.Gf(np.clip(x0,R.lbx,R.ubx))
        if not np.all(np.isfinite(np.array(f))): print('nan g',planar,i); break
print('ok')
