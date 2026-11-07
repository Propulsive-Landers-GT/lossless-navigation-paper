"""Tent variant (b(tf) = e_z): scan sign-change faces (axis angle phi0, sigma) with the planar DP for moment jumps."""
import os; os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np, sys
from dp import solve
T = float(sys.argv[1]); dd = float(sys.argv[2]); dl = np.deg2rad(dd)
for phi0d in [90 - dd, 90, 90 + dd, 60, 120]:
    ph = np.deg2rad(phi0d); p = np.array([np.sin(ph), np.cos(ph)])
    sg = np.linspace(0.05, 0.95, 91)*T
    X = [solve(-s*p, p, T, 1.0, dl, N=200, m=3, final0=True)[2] for s in sg]
    dX = np.linalg.norm(np.diff(np.array(X), axis=0), axis=1); k = np.argmax(dX)
    print(f"tent T={T} delta={dd} phi0={phi0d}: max jump {dX[k]:.4f} (x{dX[k]/np.median(dX):.0f} median) at sigma/T={sg[k]/T:.3f}", flush=True)
