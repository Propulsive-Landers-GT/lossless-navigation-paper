"""[verify-tvc] Run with proof-tvc's venv: dump proof-tvc's fine_data (TVC-2) + stored lambda + localization tables."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PT = os.path.join(HERE, "..", "proof-tvc")
sys.path.insert(0, PT); os.chdir(PT); os.environ["FASTL"] = "1"
import numpy as np, certificate2 as C2, riccati_cert as R
from witness_nl import gtpl
from localize import localize
tf, Nf = float(sys.argv[1]), int(sys.argv[2]); capS = sys.argv[3]; ss, rho = 0.5, (0.1, 45.0)
cap = None if capS == 'none' else np.deg2rad(float(capS))
P = gtpl(); par = dict(C2.PAR); par.update(tau=0.03, zeta=0.15, xi=0.15, lam_max=0.01, kap=0.03, cap=cap)
par['eta1_time'] = float(os.environ.get('ETA1', par['eta1_cells']*tf/60))
vf, pf, info, _ = localize(P, tf, ss, cap=cap)
FD = R.fine_data(P, tf, ss, Nf, par, (vf, pf), rho, 0.1)
D = C2.setup(P, tf, ss, int(round(10*tf)), par, loc=(vf, pf))
cE = np.cos(min(D['K2']*ss**2/2, cap if cap else np.pi)); D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0']
mt = C2.moment_term(D, rho)
z = np.load(f"riccati_{tf}_{ss}_{capS}_{Nf}.npz")
np.savez(os.path.join(HERE, f"theirs_riccati_{tf}_{capS}.npz"), lam=z['lam'], S=FD['S'], Lk=FD['Lk'], g0=FD['g0'], gw=FD['gw'], Mlate=FD['Mlate'],
         lam_lb=FD['lam_lb'], lam_ub=FD['lam_ub'], Nb2=FD['Nb2'], terminal=FD['terminal'], phicells=pf.cells, vcells=vf.cells,
         ds=vf.ds, info=np.array([info['E0'], info['c_abs'], info['lat_fac']]), moment=mt, Penmax=D['Penmax'], par=str(par))
print("dumped; moment", mt, "Penmax", D['Penmax'], "nsub", par['nsub'], "eta1_time", par['eta1_time'], "r_theta", par['r_theta'])
