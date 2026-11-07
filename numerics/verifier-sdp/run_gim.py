"""[verifier-sdp] Gimbal / no-gimbal screen with [numerics]-style 'set B' targets (mixtures of rotated
tent extreme arcs + noise), small to moderate N, to locate SDP gaps and find SMALL-N gaps
(candidates for an order-2 Lasserre certificate).  Also [proof-sdp] request (i): case 12 with the
r-lateral rotated parallel to the v-lateral.  Writes results/gim.jsonl."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vgim import Gim

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def rot(a):
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


if __name__ == "__main__":
    rng = np.random.default_rng(31)
    fout = open(os.path.join(OUT, "gim.jsonl"), "w")
    # (i) case 12, parallel laterals
    G = Gim(16, 4.0, np.deg2rad(30), np.deg2rad(15), a=11.0)
    wv = np.array([5.0939, 21.9914, 32.1819]); wr = np.array([8.2825, 44.1701, 64.908])
    ang = np.arctan2(wv[1], wv[0]) - np.arctan2(wr[1], wr[0])
    print(f"case12 lateral angle wv vs wr: {np.degrees(ang):.3f} deg")
    for lab, (v, r) in (("case12", (wv, wr)), ("case12-parallel", (wv, rot(ang) @ wr))):
        s = G.sdp(v, r)
        b, x, fs = G.best3(v, r, rng, 200, Zv=s["Z"])
        # planarity of the best 3-D solution: smallest singular value of the stacked vectors
        V = x.reshape(-1, 3); sv = np.linalg.svd(V, compute_uv=False)
        rec = dict(part="c12", label=lab, L=s["val"], st=s["status"], e4=s["e4"], U=b, rel=(b - s["val"]) / b,
                   nhit=int(np.sum(fs < b + 1e-7)), nfeas=int(len(fs)), planarity=float(sv[-1] / sv[0]))
        fout.write(json.dumps(rec) + "\n"); fout.flush()
        print(rec, flush=True)
    # screen
    for N in (3, 4, 5, 6, 8, 16):
        for deg in (None, 15.0, 40.0):
            for wtf in (1.0, 2.0944, 3.0):
                if deg == 40.0 and N > 8:
                    continue
                tf = 4.0; om = wtf / tf
                G = Gim(N, tf, om, None if deg is None else np.deg2rad(deg), a=11.0)
                Pv, Pr = G.extreme_readouts()
                S = G.gv.sum()
                ntg = 60 if N <= 6 else 20
                ngap = 0; worst = -1.0
                for it in range(ntg):
                    lam = rng.uniform(0.2, 0.8); ra = rng.uniform(0.5, np.pi)
                    up = rng.uniform(0, 1.5) * S / 44.0 * (1 if it % 3 else 0)
                    v = lam * Pv + (1 - lam) * rot(ra) @ Pv + np.array([0, 0, up]) + rng.normal(0, 0.3, 3) * S / 44.0
                    r = lam * Pr + (1 - lam) * rot(ra) @ Pr + np.array([0, 0, up * tf / 2]) + rng.normal(0, 0.6, 3) * S / 44.0
                    s = G.sdp(v, r)
                    nong = s["perp"] > 1e-5
                    if nong or rng.uniform() < 0.15:
                        b, x, fs = G.best3(v, r, rng, 60 if N <= 6 else 40, Zv=s["Z"])
                        rel = (b - s["val"]) / max(b, 1e-12)
                        absn = (b - s["val"]) / (2 * S ** 2 * tf ** 2)
                        rec = dict(part="screen", N=N, deg=deg, wtf=wtf, wv=v.tolist(), wr=r.tolist(), L=s["val"],
                                   st=s["status"], e4=s["e4"], perp=s["perp"], U=b, rel=rel, absn=absn,
                                   nhit=int(np.sum(fs < b + 1e-7 * max(1, b))), nfeas=int(len(fs)))
                        fout.write(json.dumps(rec) + "\n"); fout.flush()
                        if rel > 1e-5 and absn > 1e-9:
                            ngap += 1
                            print(f"  GAP N={N} deg={deg} wtf={wtf:.3f}: L={s['val']:.9g} U={b:.9g} rel={rel:.2e} "
                                  f"e4/e1={s['e4']:.1e} hits={rec['nhit']}/{rec['nfeas']}", flush=True)
                        worst = max(worst, rel)
                print(f"screen N={N} deg={deg} wtf={wtf:.3f}: gaps {ngap}/{ntg}, worst rel {worst:.2e}", flush=True)
