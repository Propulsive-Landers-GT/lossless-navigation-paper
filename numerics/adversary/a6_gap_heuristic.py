"""A6: heuristic size of the B* nonconvexity gap under altitude constraints (GTPL, alpha~0 for simplicity).
Competitor to the axial midpoint: keep the optimal dive, cancel the weighted lateral moment X_h by small brake tilts.
Minimal cost (Cauchy-Schwarz, tight) = |X_h|^2 / (2 B0), B0 = int_{s*}^{tf} (s-s*) a2 ds.  This is an UPPER estimate of the
l-deficit any lateral-zero competitor needs, hence ~ the true gap scale at this face. Also checks (S2)."""
import numpy as np
m0, rho1, rho2, g0, delta, om = 80., 400., 1000., 9.81, np.deg2rad(15), 0.4
a1, a2 = rho1/m0, rho2/m0; Ab = a2 - g0
for tf in (7., 8., 12.):
    for ss in (delta/om, 1.0, 1.5, 0.215*tf):
        s = np.linspace(0, ss, 2001)
        Xh = np.trapezoid((ss - s)*a1*np.sin(delta + om*s), s)          # dive weighted lateral moment (rigid ramp)
        # envelope version: after s*, tilt descends from om*s* to delta at rate om with d tilted (phi-delta) outward
        q = ss + max(om*ss - delta, 0)/om; t = np.linspace(ss, q, 2001)
        Bh_tail = np.trapezoid((t - ss)*a2*np.sin(np.maximum(om*ss - om*(t - ss) - delta, 0)), t)
        B0 = a2*(tf - ss)**2/2
        print(f"tf={tf:4.1f} s*={ss:5.3f} (om s*={np.degrees(om*ss):5.1f}deg) S2:{g0*ss < Ab*(tf-ss)}  |X_h|={Xh:.3f} m  "
              f"tail={Bh_tail:.3f}  gap~|X_h-tail|^2/(2B0)={(Xh-Bh_tail)**2/(2*B0):.2e} m (weighted moment W_h=-X_h+B_h; sign fixed per [proof])")
