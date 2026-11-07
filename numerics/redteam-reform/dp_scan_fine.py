import numpy as np, sys
sys.path.insert(0, "redteam-reform")
from dp_tilt_only import solve
P = dict(a1=5.0, a2=12.5, omega=0.4, delta=np.deg2rad(15.0), tf=7.0, N=int(sys.argv[1]) if len(sys.argv)>1 else 1400)
s0 = 4.0
ks = np.linspace(0.0, 0.3, 61)
prev=None
for k in ks:
    o = solve(k, s0, P)
    ph = np.rad2deg(o["phi"]); i0=int(s0/P["tf"]*P["N"])
    x = np.r_[o["dv"], o["dr"]]
    j = 0 if prev is None else np.linalg.norm(x-prev)
    print(f"kappa={k:.3f} V={o['V']:.5f} minphi_near_s0={ph[i0-50:i0+50].min():6.2f} maxphi={ph.max():6.2f} dv=({o['dv'][0]:.3f},{o['dv'][2]:.3f}) jump={j:.3f}")
    prev=x
