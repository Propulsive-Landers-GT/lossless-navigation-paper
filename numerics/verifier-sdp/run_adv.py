"""[verifier-sdp] Adversarial fixed-thrust search.
 (1) rank screen: many random/adversarial targets at small N; only non-genuine SDP solutions
     (perp_sum > tol) can carry a gap -> those get a heavy multistart; 10% of genuine ones are spot-checked.
 (2) [proof-sdp] regimes: (a) full (r,v), lateral r ⟂ lateral v, vertical BELOW the floor (x0.3-0.8);
     (b) far targets (x10, x100) with opposite r/v laterals, small omega.
Writes results/adv.jsonl."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
from vcore import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def rec_line(fout, **kw):
    fout.write(json.dumps(kw) + "\n"); fout.flush()


def check(P, nlp, built, Q, rng, nstart, Zv=None):
    rc = solve_sdp(P, Q, "CLARABEL", built=built)
    d = sdp_diag(P, rc["Z"])
    g = genuine_best(P, nlp, Q, rng, nstart=nstart, Zv=rc["Z"])
    U, L = g["f"], rc["val"]
    return dict(L=L, st=rc["status"], U=U, absgap=(U - L) / P.scale2, relgap=(U - L) / max(U, 1e-8 * P.scale2),
                perp=d["perp_sum"], rank=d["rank"], ev=d["ev"][:6].tolist(),
                e4e1=float(d["ev"][3] / d["ev"][0]) if len(d["ev"]) > 3 else 0.0)


def screen(fout, rng):
    for N in (3, 4, 5, 6, 8):
        for wtf in (0.5, 1.5, 3.0):
            for terminal in (True, False):
                for readout in ("rv", "r"):
                    P = Prob(N, 1.0, wtf, terminal=terminal, readout=readout)
                    nlp = GenuineNLP(P); built = build_sdp(P)
                    phi = np.minimum(P.tent_phi(), np.pi)
                    S = P.gamma.sum(0); rho = P.gamma.T @ np.sin(phi); zmin = P.gamma.T @ np.cos(phi)
                    nng = 0; worst = -1
                    for it in range(150):
                        kind = it % 5
                        Q = np.zeros((P.p, 3))
                        psi0 = rng.uniform(0, 2 * np.pi)
                        for l in range(P.p):
                            psi = psi0 + (np.pi / 2 * l if kind in (1, 2) else rng.uniform(0, 2 * np.pi) if kind == 4 else 0)
                            if kind == 0:     # box
                                Q[l] = [rng.uniform(-1, 1) * S[l], rng.uniform(-1, 1) * S[l], rng.uniform(zmin[l] - .3 * S[l], S[l])]
                            elif kind == 1:   # face, perpendicular laterals, slightly above/below
                                s = rng.uniform(0, 1.1)
                                Q[l] = [s * rho[l] * np.cos(psi), s * rho[l] * np.sin(psi), zmin[l] + rng.uniform(-.05, .05) * S[l]]
                            elif kind == 2:   # well below the floor, perpendicular laterals
                                s = rng.uniform(0, 1.2)
                                Q[l] = [s * rho[l] * np.cos(psi), s * rho[l] * np.sin(psi), rng.uniform(0.3, 0.8) * zmin[l]]
                            elif kind == 3:   # far, opposite laterals
                                K = rng.choice([3, 10, 100])
                                sgn = 1 if l == 0 else -1
                                Q[l] = K * S[l] * np.array([sgn * np.cos(psi0), sgn * np.sin(psi0), rng.uniform(-1, 1)])
                            else:             # face with independent azimuths
                                s = rng.uniform(0.3, 1.0)
                                Q[l] = [s * rho[l] * np.cos(psi), s * rho[l] * np.sin(psi), zmin[l] + rng.uniform(0, .1) * S[l]]
                        rc = solve_sdp(P, Q, "CLARABEL", built=built)
                        d = sdp_diag(P, rc["Z"])
                        nongen = d["perp_sum"] > 1e-5
                        if nongen or rng.uniform() < 0.1:
                            g = genuine_best(P, nlp, Q, rng, nstart=40, Zv=rc["Z"])
                            U, L = g["f"], rc["val"]
                            absg = (U - L) / P.scale2; relg = (U - L) / max(U, 1e-8 * P.scale2)
                            nng += nongen; worst = max(worst, absg)
                            rec_line(fout, part="screen", N=N, wtf=wtf, terminal=terminal, readout=readout, kind=kind,
                                     Q=Q.tolist(), L=L, st=rc["status"], U=U, absgap=absg, relgap=relg,
                                     perp=d["perp_sum"], rank=d["rank"], ev=d["ev"][:6].tolist())
                            if absg > 1e-7 and relg > 1e-5:
                                print("  GAP?", N, wtf, terminal, readout, kind, L, U, relg, d["rank"], flush=True)
                    print(f"screen N={N} wtf={wtf} T={int(terminal)} {readout}: nongenuine={nng}/150 worst absgap={worst:.2e}", flush=True)


def proof_sdp(fout, rng):
    for N in (2, 3, 4, 5, 6, 8, 16):
        for wtf in (0.2, 0.5, 1.5, 3.0):
            for terminal in (True, False):
                P = Prob(N, 1.0, wtf, terminal=terminal, readout="rv")
                nlp = GenuineNLP(P); built = build_sdp(P)
                phi = np.minimum(P.tent_phi(), np.pi)
                S = P.gamma.sum(0); rho = P.gamma.T @ np.sin(phi); zmin = P.gamma.T @ np.cos(phi)
                ns = 60 if N <= 8 else 30
                for f in (0.3, 0.5, 0.8):
                    for s in (0.0, 0.5, 1.0):
                        Q = np.array([[0, s * rho[0], f * zmin[0]], [s * rho[1], 0, f * zmin[1]]])
                        r = check(P, nlp, built, Q, rng, ns)
                        rec_line(fout, part="a", N=N, wtf=wtf, terminal=terminal, f=f, s=s, Q=Q.tolist(), **r)
                        print(f"(a) N={N} wtf={wtf} T={int(terminal)} f={f} s={s}: L={r['L']:.10g} U={r['U']:.10g} "
                              f"rel={r['relgap']:.1e} rank={r['rank']} e4/e1={r['e4e1']:.1e}", flush=True)
                for K in (10, 100):
                    for zr in (-1, 0, 1):
                        psi = rng.uniform(0, 2 * np.pi); u = np.array([np.cos(psi), np.sin(psi), 0])
                        Q = np.array([K * S[0] * (u + zr * 0.5 * EZ), K * S[1] * (-u + 0.3 * EZ)])
                        r = check(P, nlp, built, Q, rng, ns)
                        rec_line(fout, part="b", N=N, wtf=wtf, terminal=terminal, K=K, zr=zr, Q=Q.tolist(), **r)
                        print(f"(b) N={N} wtf={wtf} T={int(terminal)} K={K} zr={zr}: L={r['L']:.10g} U={r['U']:.10g} "
                              f"rel={r['relgap']:.1e} rank={r['rank']} e4/e1={r['e4e1']:.1e}", flush=True)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    which = sys.argv[1]
    with open(os.path.join(OUT, f"adv_{which}.jsonl"), "w") as fout:
        if which == "screen":
            screen(fout, rng)
        else:
            proof_sdp(fout, rng)
