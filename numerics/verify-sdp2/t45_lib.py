"""[verify-sdp2] analyze() shared with t45.py (copy)."""
import numpy as np
from core import EZ


def analyze(M, z, wv, wr, sdpval):
    K = M.kkt(z, wv, wr)
    Q, Zm = K['Q'], K['Z']
    sc = np.abs(Q).max(); tol = 1e-7 * sc
    eq, ez = np.linalg.eigvalsh(Q), np.linalg.eigvalsh(Zm)
    yv, yr = K['yv'], K['yr']
    m = np.cross(yv, yr); nm = np.linalg.norm(m)
    rec = dict(res=K['res'], licq=bool(K['licq']), negQ=int(np.sum(eq < -tol)), negZ=int(np.sum(ez < -tol)),
               zeroZ=int(np.sum(np.abs(ez) <= tol)), minQ=float(eq[0] / sc), minZ=float(ez[0] / sc))
    if M.kind != 'd0':
        mud = K['mu'][M.nb:]
        rec['mud_min'] = float(mud.min() / sc); rec['mud_npos'] = int(np.sum(mud > tol))
    t, c = M.criterion(z, yv, yr)
    rec['crit'] = t
    # C_yw, Yres
    Cyw = np.outer(yv[:2], wv[:2]) + np.outer(yr[:2], wr[:2])
    rec['asym'] = float(abs(Cyw[0, 1] - Cyw[1, 0]) / (np.abs(Cyw).max() + 1e-300))
    ec = np.linalg.eigvalsh(0.5 * (Cyw + Cyw.T)); ecn = ec / (np.abs(ec).max() + 1e-300)
    rec['ecyw'] = ecn.tolist()
    rec['p0'] = int(np.sum(ecn >= -1e-9))
    Yres = np.vstack([yv[:2], yr[:2]])
    rec['detYres'] = float(abs(np.linalg.det(Yres)) / (np.linalg.norm(yv[:2]) * np.linalg.norm(yr[:2]) + 1e-300))
    # primer-plane normal, h_m on nodes b_0..b_N, crossings
    if nm > 1e-10 * np.linalg.norm(yv) * np.linalg.norm(yr):
        m /= nm
        if m @ EZ < 0:
            m = -m
        B = M.nodes(z); h = B @ m
        rec['zeta0'] = float(m @ EZ)
        rec['hmin_int'] = float(np.min(np.abs(h[1:-1]))) if M.terminal else float(np.min(np.abs(h[1:])))
        hh = h.copy(); hh[0] = 1.0
        if M.terminal:
            hh[-1] = 1.0
        s = np.sign(hh)
        rec['k'] = int(np.sum(s[1:] != s[:-1]))
        rec['h'] = h.tolist()
    else:
        rec['k'] = -1
    # Schur chain S on b-slots
    nb = M.nb
    if M.kind != 'd0':
        D = np.diag(Zm)[nb:]
        rec['Dpos'] = bool(np.all(D > tol))
        if rec['Dpos']:
            S = Zm[:nb, :nb] - Zm[:nb, nb:] @ np.diag(1 / D) @ Zm[nb:, :nb]
        else:
            S = None
    else:
        rec['Dpos'] = True
        S = Zm.copy()
    if S is not None:
        off = np.array([S[i, i + 1] for i in range(nb - 1)])
        rec['S_offmax'] = float(off.max() / sc) if len(off) else -1.0
        rec['S_tridiag'] = bool(np.allclose(np.triu(S, 2), 0, atol=1e-12 * sc))
        rec['negS'] = int(np.sum(np.linalg.eigvalsh(S) < -tol))
    rec['gap'] = None
    return rec


