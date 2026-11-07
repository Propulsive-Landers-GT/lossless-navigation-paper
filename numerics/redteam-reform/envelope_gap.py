"""[redteam-reform] Tilt-only model: is the tilt-ENVELOPE cone relaxation  u_z >= |u| cos(delta+omega s)
exact for the full (v0,r0) feasible set?  Compare support values for affine weights e(s)=((s-s0)x, kappa):
envelope (pointwise optimum, any tilt <= delta+omega s) vs exact tilt-only DP.  Gap>0 => the envelope
relaxation accepts boundary data outside F_tilt (lossy)."""
import numpy as np, sys
sys.path.insert(0, "redteam-reform")
from dp_tilt_only import solve
P = dict(a1=5.0, a2=12.5, omega=0.4, delta=np.deg2rad(15.0), tf=7.0, N=1400)
h = P["tf"]/P["N"]; s = (np.arange(P["N"])+0.5)*h
for s0 in [3.0, 4.0, 5.0]:
    for kappa in [0.05, 0.2, 0.5, 1.0]:
        eh = s-s0; nrm = np.hypot(eh, kappa); chi = np.arctan2(np.abs(eh), kappa)
        tau = np.minimum(chi, P["delta"]+P["omega"]*s)
        c = np.cos(tau-chi); a = np.where(c>0, P["a2"], P["a1"])
        Venv = (h*nrm*a*c).sum()
        Vdp = solve(kappa, s0, P)["V"]
        print(f"s0={s0} kappa={kappa}: envelope support {Venv:.3f}  exact tilt-only {Vdp:.3f}  rel gap {(Venv-Vdp)/abs(Vdp):.3%}")
