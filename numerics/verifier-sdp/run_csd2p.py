"""[verifier-sdp] Adversarial screen of CSD2' : Gram lift exact for (i) delta=0 (thrust along b) and
(ii) the convexified-lens gimbal model (||d_k||<=1, both cones).
Target families: near-dent mixtures of rotated extreme arcs (set B), non-coplanar (r,v) laterals,
rate-saturated far targets with opposite laterals, and random.  N up to 32, small omega*tf.
Only SDP solutions with eig4/eig1 > 1e-7 can hide a gap (rank-3 => genuine); those get heavy
multistart, plus a 10% spot-check of the rest.  Usage: python run_csd2p.py <N> [<N>...]"""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vgim import Gim

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def rot(a):
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


def targets(G, rng, n):
    Pv, Pr = G.extreme_readouts()
    S = G.gv.sum(); Sr = G.gr.sum(); tf = G.tf
    out = []
    for it in range(n):
        kind = it % 4
        if kind == 0:     # near-dent mixture (set B), small noise
            lam = rng.uniform(0.2, 0.8); ra = rng.uniform(0.3, np.pi)
            up = rng.uniform(-0.02, 0.05) * S
            v = lam * Pv + (1 - lam) * rot(ra) @ Pv + [0, 0, up] + rng.normal(0, 0.005, 3) * S
            r = lam * Pr + (1 - lam) * rot(ra) @ Pr + [0, 0, up * tf / 2] + rng.normal(0, 0.005, 3) * Sr
        elif kind == 1:   # non-coplanar laterals: r and v laterals at 30..150 deg
            s1, s2 = rng.uniform(0.2, 1.0, 2); a1 = rng.uniform(0, 2 * np.pi); a2 = a1 + rng.choice([-1, 1]) * rng.uniform(np.pi / 6, 5 * np.pi / 6)
            v = np.array([s1 * Pv[0] * np.cos(a1), s1 * Pv[0] * np.sin(a1), Pv[2] + rng.uniform(-0.05, 0.1) * S])
            r = np.array([s2 * Pr[0] * np.cos(a2), s2 * Pr[0] * np.sin(a2), Pr[2] + rng.uniform(-0.05, 0.1) * Sr])
        elif kind == 2:   # rate-saturated: far, opposite laterals
            K = rng.choice([2.0, 5.0, 20.0]); psi = rng.uniform(0, 2 * np.pi); u = np.array([np.cos(psi), np.sin(psi), 0])
            v = K * S * (u + rng.uniform(-0.5, 1) * np.array([0, 0, 1.0]))
            r = K * Sr * (-u + rng.uniform(-0.5, 1) * np.array([0, 0, 1.0]))
        else:             # random in a box around the reachable set
            v = np.array([rng.uniform(-1, 1) * S, rng.uniform(-1, 1) * S, rng.uniform(0, 1.1) * S])
            r = np.array([rng.uniform(-1, 1) * Sr, rng.uniform(-1, 1) * Sr, rng.uniform(0, 1.1) * Sr])
        out.append((kind, v, r))
    return out


if __name__ == "__main__":
    Ns = [int(a) for a in sys.argv[1:]]
    rng = np.random.default_rng(sum(Ns) * 7 + 3)
    fout = open(os.path.join(OUT, f"csd2p_{'_'.join(map(str, Ns))}.jsonl"), "w")
    for N in Ns:
        ntg = {3: 80, 4: 80, 6: 60, 8: 40, 16: 24, 24: 16, 32: 12}.get(N, 16)
        nst = 60 if N <= 6 else (30 if N <= 16 else 16)
        for model in ("d=b", "cvx15", "cvx40"):
            for wtf in (0.5, 1.0, 2.0944):
                delta = None if model == "d=b" else np.deg2rad(15 if model == "cvx15" else 40)
                G = Gim(N, 4.0, wtf / 4.0, delta, a=11.0, cvx=(delta is not None))
                S2 = G.gv.sum() ** 2 + G.gr.sum() ** 2
                ngap, nchk, worst = 0, 0, -1.0
                t0 = time.time()
                for kind, v, r in targets(G, rng, ntg):
                    s = G.sdp(v, r)
                    hi = s["e4"] > 1e-7
                    if not (hi or rng.uniform() < 0.1):
                        continue
                    nchk += 1
                    b, x, fs = G.best3(v, r, rng, nst, Zv=s["Z"])
                    rel = (b - s["val"]) / max(b, 1e-12); absn = (b - s["val"]) / S2
                    rec = dict(N=N, model=model, wtf=wtf, kind=int(kind), wv=list(v), wr=list(r), L=s["val"], st=s["status"],
                               e4=s["e4"], U=b, rel=rel, absn=absn, nhit=int(np.sum(fs < b + 1e-7 * max(1, b))), nfeas=int(len(fs)))
                    fout.write(json.dumps(rec) + "\n"); fout.flush()
                    if absn > 1e-8 and rel > 1e-4:
                        ngap += 1
                        print(f"  GAP? N={N} {model} wtf={wtf:.3f} kind={kind}: L={s['val']:.9g} [{s['status'][:4]}] U={b:.9g} "
                              f"rel={rel:.2e} absn={absn:.1e} e4={s['e4']:.1e} hits={rec['nhit']}/{rec['nfeas']}", flush=True)
                    if absn > 1e-9:
                        worst = max(worst, rel)
                print(f"csd2p N={N} {model} wtf={wtf:.3f}: checked {nchk}/{ntg}, gaps {ngap}, worst rel(absn>1e-9) {worst:.2e}, "
                      f"{time.time() - t0:.0f}s", flush=True)
