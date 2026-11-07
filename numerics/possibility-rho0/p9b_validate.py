import numpy as np
from dp import solve
T, dl = 0.6, np.deg2rad(15); ph = np.array([np.cos(dl), -np.sin(dl)])
X = []; sg = np.linspace(0.6, 0.78, 61)*T
for s in sg: X.append(solve(-s*ph, ph, T, 1.0, dl, N=240, m=3)[2])
dX = np.linalg.norm(np.diff(np.array(X), axis=0), axis=1); k = np.argmax(dX)
print("theorem face: max jump", dX[k], "at sigma/T", sg[k]/T, "median", np.median(dX), "(face.py predicts sigma_c/T = 0.688)")
