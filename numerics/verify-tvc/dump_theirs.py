"""[verify-tvc] Run with proof-tvc's venv (needs cvxpy import). Rebuilds proof-tvc's float certificate matrix exactly as
verify_cert.py does and dumps it (plus their Mlate, lam_lb, moment term, U) for comparison with the independent Arb
assembly in exact_cert.py.  usage: dump_theirs.py tf ss N gim roll rho0 rhow"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ["FASTL"] = "1"
HERE = os.path.dirname(os.path.abspath(__file__)); PT = os.path.join(HERE, "..", "proof-tvc")
sys.path.insert(0, PT); os.chdir(PT)
import numpy as np, certificate2 as C2
from witness_nl import gtpl
from localize import localize
tf, ss, N, gim, roll, r0, rw = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), float(sys.argv[6]), float(sys.argv[7])
deg = 15.0 if gim == 'cone' else np.degrees(np.arccos(np.cos(np.deg2rad(15))**2))
P = gtpl(deg=deg)
par = dict(C2.PAR); par.update(tau=0.03, zeta=0.1, xi=0.1, lam_max=3e-3, roll=bool(roll), kapg=float(os.environ.get('KAPG', 10.0)))
vf, pf, info, _ = localize(P, tf, ss, roll=bool(roll))
D = C2.setup(P, tf, ss, N, par, loc=(vf, pf))
cE = np.cos(D['K2']*ss**2/2); D['Penmax'] = (par['xi']/(cE*(1-info['c_abs'])) + par['zeta']*info['lat_fac'])*info['E0']
z = np.load(f"cert2_{gim}_{tf}_{ss}_{N}_roll{roll}.npz"); lam = z['lam']
tau, taup = par['tau'], par['taup']; h = D['h']; Wd = D['Wdiag']
c_loc, cg = C2.remainder_constants(D, (r0, rw))
kg = par.get('kapg', 10.0); coefV = (1+1/kg)*(r0*D['Cg0'] + rw*D['Cgw'])
c_loc = c_loc + (1+1/tau)*coefV*D['cmax']*(h/(2*np.pi))**2
lam_lb = np.maximum(c_loc+cg-D['Mlate'], 0.0)
A = (1+tau)*D['Kp'] + (1-taup)*D['Km'] - (1-0.2)*D['G'].T@np.diag([r0, rw])@D['G'] \
    - (1-taup)*0.1*D['C'].T@D['C'] + (1+tau)*par['lam_max']*sum(D['Lk']) + (1+tau)*coefV*D['Vall']
Mv = A - np.diag(Wd*np.concatenate([lam+D['Mlate']]*2))
mt = C2.moment_term(D, (r0, rw))
out = os.path.join(HERE, f"theirs_{gim}_{N}_roll{roll}.npz")
np.savez(out, A=A, Mv=Mv, Kp=D['Kp'], Km=D['Km'], Lsum=sum(D['Lk']), G=D['G'], C=D['C'], Mlate=D['Mlate'], lam=lam,
         lam_lb=lam_lb, lam_ub=D['lam_ub'], c_loc=c_loc, cg=cg, Nb2=D['Nb2'], moment=mt, V=h*np.sum(lam*D['Nb2']),
         Penmax=D['Penmax'], Vall=D['Vall'], coefV=coefV, cmax=D['cmax'], Cg0=D['Cg0'], Cgw=D['Cgw'],
         phicells=pf.cells, vcells=vf.cells, ds=vf.ds, info=np.array([info['E0'], info['c_abs'], info['lat_fac']]))
print("dumped", out, "V=", h*np.sum(lam*D['Nb2']), "moment=", mt, "Penmax=", D['Penmax'])
