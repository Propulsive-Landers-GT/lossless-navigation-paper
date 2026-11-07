"""[proof-csd2p] CSD2' screen at LARGE omega*tf (pi .. 3pi), where the Wirtinger margin of the E-perp
second variation (math/09 Sec. 4) is gone, so non-planar rate-saturated optima are the natural place for gaps.
Targets: (0) near-dent mixtures of rotated extreme arcs; (1) mixtures of two genuine support points
(NLP with far target in a random direction y in R^6); (2) mixtures of three; (3) random box.
Models: d=b (delta=0), cvx15, cvx40 (convexified lens), terminal b(tf)=e_z or free.
Usage: python screen_big.py <tag> <model,...> <terminal:1|0> <N> """
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../verifier-sdp"))
import numpy as np
from vgim import Gim

def rot(a):
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])

def support_point(G, rng, y, nst=6):
    S = G.gv.sum(); Sr = G.gr.sum()
    far = 1e3 * np.r_[S * y[:3], Sr * y[3:]]
    best, xb = np.inf, None
    for _ in range(nst):
        x, f, v = G.solve(G.random_start(rng), far[:3], far[3:])
        if v < 1e-8 and f < best:
            best, xb = f, x
    if xb is None:
        return None
    return readout(G, xb)

def readout(G, x):
    N, nb = G.N, G.nb
    if G.gim:
        T = x[3 * nb:].reshape(N, 3)
    else:
        B = np.vstack([[0, 0, 1.0], x[:3 * nb].reshape(nb, 3)] + ([[0, 0, 1.0]] if G.terminal else []))
        T = B[:N]
    return G.gv @ T, G.gr @ T

def targets(G, rng, n):
    Pv, Pr = G.extreme_readouts(); S = G.gv.sum(); Sr = G.gr.sum()
    out = []
    for it in range(n):
        kind = it % 4
        if kind == 0:
            lam = rng.uniform(0.2, 0.8); ra = rng.uniform(0.3, np.pi); up = rng.uniform(-0.02, 0.05) * S
            v = lam * Pv + (1 - lam) * rot(ra) @ Pv + [0, 0, up] + rng.normal(0, 0.005, 3) * S
            r = lam * Pr + (1 - lam) * rot(ra) @ Pr + [0, 0, up * G.tf / 2] + rng.normal(0, 0.005, 3) * Sr
        elif kind in (1, 2):
            m = 2 if kind == 1 else 3
            pts = []
            for _ in range(m):
                y = rng.normal(size=6); y /= np.linalg.norm(y)
                p = support_point(G, rng, y)
                if p is not None: pts.append(p)
            if len(pts) < 2:
                continue
            lam = rng.dirichlet(np.ones(len(pts)))
            v = sum(l * p[0] for l, p in zip(lam, pts)) + rng.normal(0, 0.003, 3) * S
            r = sum(l * p[1] for l, p in zip(lam, pts)) + rng.normal(0, 0.003, 3) * Sr
        else:
            v = np.array([rng.uniform(-.7, .7) * S, rng.uniform(-.7, .7) * S, rng.uniform(0, 1.0) * S])
            r = np.array([rng.uniform(-.7, .7) * Sr, rng.uniform(-.7, .7) * Sr, rng.uniform(0, 1.0) * Sr])
        out.append((kind, v, r))
    return out

if __name__ == "__main__":
    tag, models, term, N = sys.argv[1], sys.argv[2].split(","), sys.argv[3] == "1", int(sys.argv[4])
    rng = np.random.default_rng(abs(hash(tag)) % 2**32)
    fout = open(f"results_{tag}.jsonl", "a")
    for model in models:
        for wtf in (np.pi, 1.5 * np.pi, 2 * np.pi, 3 * np.pi):
            delta = None if model == "d=b" else np.deg2rad(int(model[3:]))
            G = Gim(N, 4.0, wtf / 4.0, delta, a=11.0, cvx=(delta is not None), terminal=term)
            S2 = G.gv.sum() ** 2 + G.gr.sum() ** 2
            ngap = nchk = 0; worst = -1; t0 = time.time()
            for kind, v, r in targets(G, rng, 24):
                s = G.sdp(v, r)
                b, x, fs = G.best3(v, r, rng, 14, Zv=s["Z"])
                nchk += 1
                rel = (b - s["val"]) / max(b, 1e-12); absn = (b - s["val"]) / S2
                rec = dict(N=N, model=model, term=term, wtf=wtf, kind=kind, wv=list(v), wr=list(r), L=s["val"], st=s["status"],
                           e4=s["e4"], U=b, rel=rel, absn=absn, nfeas=int(len(fs)))
                fout.write(json.dumps(rec) + "\n"); fout.flush()
                if absn > 1e-8 and rel > 1e-4:
                    ngap += 1
                    print(f"  GAP? N={N} {model} term={term} wtf={wtf:.3f} kind={kind}: L={s['val']:.9g} [{s['status'][:4]}] U={b:.9g} rel={rel:.2e} e4={s['e4']:.1e}", flush=True)
                if absn > 1e-9: worst = max(worst, rel)
            print(f"{tag} N={N} {model} term={term} wtf={wtf:.3f}: {nchk} checked, gaps {ngap}, worst rel {worst:.2e}, {time.time()-t0:.0f}s", flush=True)
