"""Small rotation helpers. Quaternions are scalar-first [w, x, y, z] and map body to world."""
import numpy as np


def hat(w):
    return np.array([[0.0, -w[2], w[1]], [w[2], 0.0, -w[0]], [-w[1], w[0], 0.0]])


def expm_so3(phi):
    """Rodrigues: rotation matrix exp([phi]x)."""
    th = np.linalg.norm(phi)
    K = hat(phi)
    if th < 1e-9:
        return np.eye(3) + K + 0.5 * K @ K
    return np.eye(3) + np.sin(th) / th * K + (1 - np.cos(th)) / th**2 * K @ K


def quat_to_R(q):
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
        [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
        [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
    ])


def R_to_quat(R):
    tr = np.trace(R)
    if tr > 0:
        s = 2.0 * np.sqrt(tr + 1.0)
        q = np.array([0.25 * s, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    else:
        i = int(np.argmax(np.diag(R)))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = 2.0 * np.sqrt(1.0 + R[i, i] - R[j, j] - R[k, k])
        q = np.zeros(4)
        q[0] = (R[k, j] - R[j, k]) / s
        q[1 + i] = 0.25 * s
        q[1 + j] = (R[j, i] + R[i, j]) / s
        q[1 + k] = (R[k, i] + R[i, k]) / s
    return q / np.linalg.norm(q) * (1 if q[0] >= 0 else -1)


def quat_mul(p, q):
    pw, pv = p[0], p[1:]
    qw, qv = q[0], q[1:]
    return np.concatenate([[pw * qw - pv @ qv], pw * qv + qw * pv + np.cross(pv, qv)])


def tilt_of_R(R):
    """Angle between body z axis and world vertical."""
    return float(np.arccos(np.clip(R[2, 2], -1.0, 1.0)))


def gimbal_angles(T_body):
    """Flight-code gimbal convention: d = (sin th cos ph, sin ph, cos th cos ph). Returns (th, ph)."""
    Tn = np.linalg.norm(T_body)
    ph = np.arcsin(np.clip(T_body[1] / Tn, -1, 1))
    th = np.arctan2(T_body[0], T_body[2])
    return th, ph


def gimbal_dir(th, ph):
    return np.array([np.sin(th) * np.cos(ph), np.sin(ph), np.cos(th) * np.cos(ph)])
