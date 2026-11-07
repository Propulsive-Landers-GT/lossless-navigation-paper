import numpy as np, time
from models import *
P=gtpl()
tf=2.0
for planar in [True, False]:
    for N in [20,40]:
        t=time.time()
        R=ReachM1(P,tf,N,planar=planar)
        tb=time.time()-t
        ex=extreme_arcs_M1(P,tf,N); exc=extreme_arcs_M1_cont(P,tf)
        M=np.array([0,0,ex['Mz']])
        rng=np.random.default_rng(0)
        t=time.time()
        best,allr=R.multistart(20,rng,mode='dist',target=M)
        fs=np.sqrt(sorted([r['f'] for r in allr]))
        print(planar,N,'build',round(tb,2),'Px %.4f Mz %.4f'%(ex['Px'],ex['Mz']),'cont',exc,'dist %.5f'%np.sqrt(best['f']),'z',best['z'].round(4),'nok',len(allr),'t %.1f'%(time.time()-t), fs[:4].round(5), flush=True)
        # check extreme arc reachable: min z
        best2,_=R.multistart(10,rng,mode='lin',c=[0,0,1])
        print('   minz',best2['z'].round(5),'vs Mz',round(ex['Mz'],5),flush=True)
