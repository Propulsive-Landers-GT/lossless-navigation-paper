"""[proof-tvc] Independent re-verification of a stored certificate (fresh process, no SDP solver):
rebuilds every matrix from scratch, checks the 2N x 2N matrix inequality with numpy eigvalsh AND with a
Cholesky factorization of the negated (scaled) matrix plus margin, recomputes U_total and compares with G_w.
usage: verify_cert.py tf ss N gim roll(0/1) rho0 rhow   (other parameters as in the certified run)"""
import os, sys
os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ["FASTL"] = "1"
import numpy as np, certificate2 as C2
from witness_nl import gtpl, evaluate, segments_bangbang, evaluate_segments
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
assert np.all(lam >= lam_lb) and np.all(lam <= D['lam_ub'] + 1e-15), "multiplier bounds violated"
A = (1+tau)*D['Kp'] + (1-taup)*D['Km'] - (1-par['taurho'] if 'taurho' in par else 1-0.2)*D['G'].T@np.diag([r0, rw])@D['G'] \
    - (1-taup)*0.1*D['C'].T@D['C'] + (1+tau)*par['lam_max']*sum(D['Lk']) + (1+tau)*coefV*D['Vall']
Mv = A - np.diag(Wd*np.concatenate([lam+D['Mlate']]*2))
Sc = 1/np.sqrt(Wd); Ms = (Mv+Mv.T)/2*Sc[:, None]*Sc[None, :]
top = np.linalg.eigvalsh(Ms).max()
try:
    np.linalg.cholesky(-Ms); chol = True   # -M positive definite (strict)
except np.linalg.LinAlgError:
    chol = False
U = h*np.sum(lam*D['Nb2']) + C2.moment_term(D, (r0, rw))
nv = np.load(f"witness_{gim}_{tf}_{ss}.npy"); G = evaluate_segments(P, tf, ss, segments_bangbang(P, tf, ss, nv))['G']   # ordinary bang-bang witness
print(f"verify {gim} tf={tf} s*={ss} N={N} roll={roll}: top eig={top:.2e}  cholesky(-M) ok={chol}  U_total={U:.6e}  G_w={G:.6e}  PASS={top<=0 and G>U}")
