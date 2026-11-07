"""Check the explicit inequality of Theorem P0-F (math/possibility-rho0.md):
   f(h) = sin 2h - h cos 2h + sin h - 2h > 0  for 0 < h <= pi/4   (h = omega*tf/2)."""
import numpy as np
h = np.linspace(1e-6, np.pi/4, 2_000_001)
f = np.sin(2*h) - h*np.cos(2*h) + np.sin(h) - 2*h
print("min f/h^3 on (0, pi/4]:", (f/h**3).min(), " at h =", h[np.argmin(f/h**3)], "; f(pi/4) =", f[-1])
# rigorous: f(h) >= h^3 (1/2 - 2h^2/3) > 0 for h < sqrt(3)/2 (Taylor bounds); f''' below is only informative
f3 = 4*np.cos(2*h) - 8*h*np.sin(2*h) - np.cos(h)   # correct f''' (not used for rigour; changes sign)
print("min f''' on [0,pi/4]:", f3.min())
