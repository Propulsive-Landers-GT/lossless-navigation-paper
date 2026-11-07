"""[verifier-sdp] Part 2: fixed-thrust sweep.  Usage: python run_fixed.py <N> [<N> ...] > log
Writes results/fixed_N<N>.jsonl (one line per (config, target))."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vcore import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def accel_profile(kind, N):
    t = np.linspace(0, 1, N + 1)
    if kind == "const":
        return np.ones(N + 1)
    if kind == "ramp":          # mass depletion, 40% mass loss
        return 1.0 / (1.0 - 0.4 * t)
    if kind == "rand":          # adversarial: very non-uniform, deterministic per N
        r = np.random.default_rng(1000 + N)
        return r.uniform(0.2, 2.0, N + 1)
    raise ValueError(kind)


def targets(P, rng, nlp):
    """List of (label, Q) with Q of shape (p,3)."""
    T = []
    phi = np.minimum(P.tent_phi(), np.pi)
    S = np.sum(P.gamma, 0)                       # per-readout scale
    rho = P.gamma.T @ np.sin(phi)                # lateral radius of the bottom face
    zmin = P.gamma.T @ np.cos(phi)
    M = P.midpoint_M()
    T.append(("M", M))

    def face_pt(s, h, psis):
        Q = np.zeros((P.p, 3))
        for l in range(P.p):
            Q[l] = [s * rho[l] * np.cos(psis[l]), s * rho[l] * np.sin(psis[l]), zmin[l] + h * S[l]]
        return Q
    fl = [(0.5, 0.0), (0.9, 0.0), (0.5, 0.01), (0.2, 0.05), (0.97, 0.002), (0.5, -0.05)]
    if REDUCED:
        fl = [(0.5, 0.0), (0.9, 0.0), (0.97, 0.002), (0.5, -0.05)]
    for (s, h) in fl:
        psi = rng.uniform(0, 2 * np.pi)
        T.append((f"face s={s} h={h}", face_pt(s, h, [psi] * P.p)))
        if P.p == 2:   # misaligned lateral directions for r and v
            T.append((f"face s={s} h={h} perp", face_pt(s, h, [psi, psi + np.pi / 2])))
    # far targets and near-boundary points
    center = P.readout_of(P.extreme_arc(0.0) * 0 + EZ)      # straight-up readout
    for j in range(2):
        d = rng.normal(size=(P.p, 3)); d /= np.linalg.norm(d)
        Qfar = center + 1.5 * d * S[:, None]
        T.append(("far", Qfar))
        g = genuine_best(P, nlp, Qfar, rng, nstart=6)
        if g["B"] is not None:
            p = P.readout_of(g["B"])
            dirv = (Qfar - p) / max(np.linalg.norm(Qfar - p), 1e-12)
            T.append(("near-bdry out", p + 0.02 * dirv * S[:, None]))
            if not REDUCED:
                T.append(("near-bdry in", p - 0.02 * dirv * S[:, None]))
    for j in range(2 if REDUCED else 4):
        Q = np.zeros((P.p, 3))
        for l in range(P.p):
            Q[l] = [rng.uniform(-1, 1) * S[l], rng.uniform(-1, 1) * S[l], rng.uniform(zmin[l] - 0.2 * S[l], S[l])]
        T.append(("random", Q))
    return T


def run_config(N, wtf, terminal, readout, scheme, accel, rng, fout, nstart=8):
    P = Prob(N, 1.0, wtf, accel=accel_profile(accel, N), scheme=scheme, terminal=terminal, readout=readout)
    sl, slst = slater_margin(P)
    nlp = GenuineNLP(P)
    built = build_sdp(P)
    builtS = build_sdp(P)
    for it, (lab, Q) in enumerate(targets(P, rng, nlp)):
        t0 = time.time()
        rc = solve_sdp(P, Q, "CLARABEL", built=built)
        if (N <= 16 and not REDUCED) or it == 0:
            rs = solve_sdp(P, Q, "SCS", built=builtS, tight=(N <= 16))
        else:
            rs = dict(val=np.nan, status="skip")
        Zv = rc["Z"]
        diag = sdp_diag(P, Zv) if Zv is not None else None
        g = genuine_best(P, nlp, Q, rng, nstart=nstart, Zv=Zv)
        U, L = g["f"], rc["val"]
        absg = (U - L) / P.scale2
        relg = (U - L) / max(U, 1e-8 * P.scale2)
        rec = dict(N=N, wtf=wtf, terminal=terminal, readout=readout, scheme=scheme, accel=accel,
                   slater=sl, label=lab, Q=np.asarray(Q).tolist(),
                   sdp_clar=L, st_clar=rc["status"], sdp_scs=rs["val"], st_scs=rs["status"],
                   genuine=U, nfeas=g.get("nfeas", 0), nsame=int(np.sum(np.array(g.get("fs", [])) < U + 1e-9 * P.scale2)),
                   viol=g.get("viol", np.nan), absgap=absg, relgap=relg,
                   rank6=int(np.sum(diag["ev"] > 1e-6 * diag["ev"][0])) if diag else -1,
                   rank4=int(np.sum(diag["ev"] > 1e-4 * diag["ev"][0])) if diag else -1,
                   perp_sum=diag["perp_sum"] if diag else np.nan,
                   ev=diag["ev"][:7].tolist() if diag else [], scale2=P.scale2, secs=time.time() - t0)
        fout.write(json.dumps(rec) + "\n"); fout.flush()
        flag = "  <<<" if relg > 1e-5 and absg > 1e-8 else ""
        print(f"N={N} wtf={wtf} T={int(terminal)} {readout} {scheme} {accel:5s} {lab:24s} "
              f"L={L:.9g}[{rc['status'][:4]}] S={rs['val']:.9g}[{str(rs['status'])[:4]}] U={U:.9g} "
              f"rel={relg:.2e} abs={absg:.1e} rk={rec['rank6']}/{rec['rank4']} perp={rec['perp_sum']:.1e}{flag}",
              flush=True)


REDUCED = False


if __name__ == "__main__":
    if sys.argv[1] == "reduced":
        REDUCED = True
        Ns = [int(a) for a in sys.argv[2:]]
        for N in Ns:
            rng = np.random.default_rng(N)
            with open(os.path.join(OUT, f"fixed_red_N{N}.jsonl"), "w") as fout:
                for terminal, wtf in ((True, 0.4), (True, 2.0), (True, 3.6), (False, 1.2)):
                    for readout in ("r", "rv"):
                        for accel in ("const", "rand"):
                            run_config(N, wtf, terminal, readout, "zoh", accel, rng, fout, nstart=6)
        sys.exit(0)
    Ns = [int(a) for a in sys.argv[1:]]
    for N in Ns:
        rng = np.random.default_rng(N)
        with open(os.path.join(OUT, f"fixed_N{N}.jsonl"), "w") as fout:
            for terminal in (True, False):
                for wtf in (0.4, 1.2, 2.0, 3.6, 5.5):
                    if not terminal and wtf > 3.6:
                        continue
                    for readout in ("r", "rv"):
                        for accel in ("const", "ramp", "rand"):
                            if accel != "const" and readout == "rv" and N > 32:
                                continue
                            if accel == "ramp" and N > 32:
                                continue
                            run_config(N, wtf, terminal, readout, "zoh", accel, rng, fout, nstart=8 if N <= 16 else 6)
                    if wtf in (1.2, 3.6):
                        run_config(N, wtf, terminal, "rv", "trap", "const", rng, fout)
