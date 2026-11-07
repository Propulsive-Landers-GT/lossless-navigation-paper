import numpy as np, time
from models import *
P=gtpl()
for planar in [True, False]:
  for tf in [2.0,4.0]:
    t=time.time()
    R=ReachM3(P,tf,30,planar=planar,omega_max=0.5)
    rng=np.random.default_rng(0)
    best,allr=R.multistart(8,rng,mode='lin',c=[0,0,1])
    zs=sorted([r['f'] for r in allr])
    print('M3',planar,tf,'zmin',best['z'].round(3),'n',len(allr),'t %.1f'%(time.time()-t),np.round(zs[:5],3),flush=True)
    zst=best['z']; M=np.array([0,0,zst[2]])
    b2,a2=R.multistart(8,rng,mode='dist',target=M)
    print('   dist to (0,0,z*)', np.sqrt(b2['f']), b2['z'].round(3),flush=True)
R=ReachM1A(P,4.0,40,eps=1.0,omega=0.5)
rng=np.random.default_rng(0)
best,allr=R.multistart(10,rng,mode='lin',c=[0,0,1]); print('M1A zmin',best['z'],len(allr))
b2,_=R.multistart(10,rng,mode='dist',target=[0,0,best['z'][2]]); print(' dist',np.sqrt(b2['f']),b2['z'])
