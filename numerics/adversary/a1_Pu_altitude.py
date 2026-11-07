"""A1: Is the Thm-B witness arc P_u physically admissible under an altitude constraint r_z >= 0?
GTPL central parameters (context/vehicle.md). Landing at r=0,v=0 at tf; integrate backwards."""
import numpy as np
m0, rho1, rho2, alpha, g = 80.0, 400.0, 1000.0, 5.66e-4, 9.81
delta, om = np.deg2rad(15), 0.4
for tent in (False, True):
    tf = (np.pi/2 - delta)/om * (2 if tent else 1) * 0.999
    s = np.linspace(0, tf, 20001); h = s[1]-s[0]
    phi = np.minimum(om*s, om*(tf-s)) if tent else om*s
    a1 = rho1/(m0 - alpha*rho1*s)
    fz = a1*np.cos(delta+phi) - g          # net vertical accel
    fx = a1*np.sin(delta+phi)
    # v(s) = -int_s^tf f ; r(s) = -int_s^tf v
    vz = -np.flip(np.concatenate([[0], np.cumsum(np.flip(fz)[:-1]*h)]))
    rz = -np.flip(np.concatenate([[0], np.cumsum(np.flip(vz)[:-1]*h)]))
    vx = -np.flip(np.concatenate([[0], np.cumsum(np.flip(fx)[:-1]*h)]))
    rx = -np.flip(np.concatenate([[0], np.cumsum(np.flip(vx)[:-1]*h)]))
    print(f"tent={tent} tf={tf:.3f}s  a1/g={a1[0]/g:.3f}  r0z={rz[0]:.3f} m  max r_z on [0,tf)={rz[:-1].max():.3f} m  v0z={vz[0]:.3f}  r0x={rx[0]:.3f} v0x={vx[0]:.3f}")
