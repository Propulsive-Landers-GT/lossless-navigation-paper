"""[proof-tvc] Probe for long horizons with a tilt cap: witness gain + localization constants."""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS","1")
import numpy as np
from witness_nl import gtpl, optimize, evaluate
from localize import localize
P=gtpl(); cap=np.deg2rad(float(sys.argv[1]))
for tf,ss in [tuple(float(y) for y in x.split(":")) for x in sys.argv[2:]]:
    try:
        vf,pf,info,_=localize(P,tf,ss,cap=cap)
        li={k:round(float(v),5) for k,v in info.items()}
    except AssertionError as e:
        li=f"localize fails: {e}"
    b=optimize(P,tf,ss,N=int(round(tf*50)),starts=4,cap=cap); ev=evaluate(P,tf,ss,b[1])
    np.save(f"witness_cone_{tf}_{ss}_cap{sys.argv[1]}.npy",b[1])
    print(f"cap={sys.argv[1]} tf={tf} s*={ss}: G_w={ev['G']:.4e} maxtilt={np.degrees(ev['maxtilt']):.2f}deg maxvz={ev['maxvz']:.2e} rz/|rh|={ev['rzrel']:.1f} r0z={ev['r0'][1]:.2f}  loc={li}",flush=True)
