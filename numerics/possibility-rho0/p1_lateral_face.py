"""Lateral sign-change face of the two-moment set K (M1, rho1=0, alpha=0, omega=1 units, a2=1).
Primer p(s) = (s - sigma) e_x  <=> functional  <e_x, int (s-sigma) a d>  = r0x + sigma v0x (up to sign/const).
Reduced value V(beta*) where beta* = signed lateral tilt at s = sigma (exact reduction, see math/possibility-rho0.md).
"""
import numpy as np
from scipy.integrate import quad

def V(bs, sig, tf, dl):
    L = lambda s: max(-s, bs - (sig - s))
    E = quad(lambda s: (sig - s) * max(0.0, np.sin(dl - L(s))), 0, sig, limit=200, points=[(sig-bs)/2])[0]
    Lt = quad(lambda s: (s - sig) * max(0.0, np.sin(min(dl + bs + (s - sig), np.pi/2))), sig, tf, limit=200)[0]
    return E + Lt

if __name__ == "__main__":
    for tf, dl in [(1.2, 0.0), (1.2, np.deg2rad(15)), (0.3, 0.0), (0.3, np.deg2rad(15)), (1.3, np.deg2rad(15))]:
        print(f"tf={tf} delta={dl:.3f}")
        for sig in np.linspace(0.05, 0.95, 19) * tf:
            bs = np.linspace(-sig, sig, 401)
            v = np.array([V(b, sig, tf, dl) for b in bs])
            i = np.argmax(v)
            # local maxima
            loc = [j for j in range(len(v)) if (j == 0 or v[j] >= v[j-1]) and (j == len(v)-1 or v[j] >= v[j+1])]
            print(f"  sig={sig:.3f} argmax b*={bs[i]:+.3f}  V(-s)={v[0]:.5f} V(+s)={v[-1]:.5f} max={v[i]:.5f} locmax={[round(bs[j],3) for j in loc]}")
