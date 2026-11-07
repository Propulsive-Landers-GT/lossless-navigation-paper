"""[proof-tvc] Fresh-process re-check of a stored Riccati certificate (no SDP solver):
rebuild all per-cell data, check lambda bounds, run the float and the Arb-ball backward recursions,
recompute V_lambda, the moment term and the witness gain (ordinary bang-bang), and print the verdict.
usage: verify_riccati.py tf ss Nf cap|none rho0:rhow   (env ZETA, KAP, LAMMAX as in the certified run; Nc for eta1)"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ["FASTL"] = "1"
import numpy as np, certificate2 as C2, riccati_cert as R
from witness_nl import gtpl, segments_bangbang, evaluate_segments
from localize import localize
tf, ss, Nf = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]); capS = sys.argv[4]
cap = None if capS == 'none' else np.deg2rad(float(capS)); rho = tuple(float(y) for y in sys.argv[5].split(':'))
Nc = int(os.environ.get("NC", "60"))
P = gtpl(); par = dict(C2.PAR)
par.update(tau=0.03, zeta=float(os.environ["ZETA"]), xi=float(os.environ["ZETA"]), lam_max=float(os.environ["LAMMAX"]), kap=float(os.environ["KAP"]), cap=cap)
par['eta1_time'] = float(os.environ.get("ETA1", par['eta1_cells']*tf/Nc))
vf, pf, info, _ = localize(P, tf, ss, cap=cap)
FD = R.fine_data(P, tf, ss, Nf, par, (vf, pf), rho, 0.1)
z = np.load(f"riccati_{tf}_{ss}_{capS}_{Nf}.npz"); lam = z['lam']
assert np.all(lam >= FD['lam_lb']) and np.all(lam <= FD['lam_ub']*(1+1e-12)), "lambda bounds"
ok, worst, k = R.riccati_check(FD, lam)
okx, kx = R.exact_riccati(FD, lam)
D = C2.setup(P, tf, ss, int(round(4*tf/ss)), par, loc=(vf, pf))   # small grid; only the moment-term functions are used
cE = np.cos(min(D['K2']*ss**2/2, cap if cap else np.pi))
D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0']
mt = C2.moment_term(D, rho); V = FD['h']*np.sum(lam*FD['Nb2'])
ev = evaluate_segments(P, tf, ss, segments_bangbang(P, tf, ss, np.load(f"witness_cone_{tf}_{ss}.npy")))
print(f"verify tf={tf} s*={ss} cap={capS} Nf={Nf}: float recursion ok={ok} (worst {worst:.2e}); Arb recursion ok={okx}; "
      f"V={V:.6e} moment={mt:.3e} U={V+mt:.6e}; G_w={ev['G']:.6e} end={ev['end']} max v_z={ev['maxvz']:.2e}; "
      f"PASS={ok and okx and ev['G']>V+mt and abs(ev['end'][0])<1e-12 and abs(ev['end'][1])<1e-12 and ev['maxvz']<0}")
lo, hi = 0.0, 1.0
for _ in range(50):
    dm = (lo+hi)/2
    if ev['G'] - dm*np.sqrt(1+ss**2) > V + C2.moment_term(D, rho, dm): lo = dm
    else: hi = dm
print(f"quantitative: dist(theta_m, F) >= {lo:.3e} m")
