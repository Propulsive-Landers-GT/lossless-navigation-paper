"""Theorem-D check: lateral landing-position set L for a FIXED realistic initial state (r0, v0) and fixed tf,
with soft landing v(tf)=0, r_z(tf)=0 and altitude path constraint r_z(t) >= 0.

    L = { r_lat(tf) } = r0_lat + v0_lat tf + { Dr_lat : (Dv, Dr_z) fixed by the boundary data, admissible }.

L is a 2D slice of F_tf (translate: landing at a target from r0 <=> starting from r0 - p), so if L is
nonconvex then F_tf intersected with physical boundary data is nonconvex.

Method: support function h(theta) of L at 24-36 angles (conv L), then a grid of points inside conv L,
each tested by min-distance NLP (multistart).  dent = max over grid of dist(q, L) [m].

Usage: .venv/bin/python d1_landing_set.py <model> <scenario> [quick]
  model    : M1 | M1tent | MT | M3 | M3w   (M3w: M3 with |w| <= 0.5 rad/s)
  scenario : S1 (r0=(0,0,50), v0=(0,0,-5), tf=7) | S2 (v0=(4,0,-5)) | S3 (r0=(0,0,30), v0=(3,0,-8), tf=6)
"""
import sys, json, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import models
from runner import run_batch, run_many

SCEN = {"S1": dict(r0=[0, 0, 50.0], v0=[0, 0, -5.0], tf=7.0),
        "S2": dict(r0=[0, 0, 50.0], v0=[4.0, 0, -5.0], tf=7.0),
        "S3": dict(r0=[0, 0, 30.0], v0=[3.0, 0, -8.0], tf=6.0),
        "S4": dict(r0=[0, 0, 50.0], v0=[0, 0, -5.0], tf=9.0)}


def make_spec(model, P, tf, quick):
    eq = (0, 1, 2, 5)
    if model in ("M1", "M1tent"):
        N = 24 if quick else 40
        return ("M1", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True, eq_idx=eq, tent=(model == "M1tent")))
    if model in ("MT", "MTtent"):
        N = 24 if quick else 40
        return ("MT", P, dict(tf=tf, N=N, use_r=True, alt=True, eq_idx=eq, tent=(model == "MTtent")))
    if model in ("M3", "M3w"):
        N = 20 if quick else 32
        return ("M3", P, dict(tf=tf, N=N, planar=False, use_r=True, alt=True, eq_idx=eq,
                               omega_max=(0.5 if model == "M3w" else None)))
    raise ValueError(model)


def main():
    model, scen = sys.argv[1], sys.argv[2]
    quick = "quick" in sys.argv
    S = SCEN[scen]; tf = S["tf"]; r0 = np.array(S["r0"]); v0 = np.array(S["v0"])
    P = models.gtpl(omega=0.4)
    g = P["g"]
    dv = np.array([-v0[0], -v0[1], g * tf - v0[2]])
    drz = dv[2] * tf - g * tf ** 2 / 2 - r0[2]
    eqv = [dv[0], dv[1], dv[2], drz]
    spec = make_spec(model, P, tf, quick)
    base = r0[:2] + v0[:2] * tf
    t0 = time.time()
    nang = 16 if quick else 32
    th = np.linspace(0, 2 * np.pi, nang, endpoint=False)
    sup = run_batch([(spec, dict(mode="lin", c=[0, 0, 0, -np.cos(t), -np.sin(t), 0], eq_val=eqv)) for t in th],
                    8 if quick else 16, chunk=8)
    h = np.array([-s["f"] for s in sup])
    if not np.all(np.isfinite(h)):
        print("infeasible directions:", np.sum(~np.isfinite(h)))
    S_pts = np.array([s["z"][3:5] if s["z"] is not None else [np.nan, np.nan] for s in sup])
    print(model, scen, "support done", round(time.time() - t0, 1), "h range", np.nanmin(h), np.nanmax(h), flush=True)
    C = np.stack([np.cos(th), np.sin(th)], 1)
    lo = np.nanmin(S_pts, 0); hi = np.nanmax(S_pts, 0)
    ng = 13 if quick else (17 if model.startswith("M3") else 25)
    gx = np.linspace(lo[0], hi[0], ng); gy = np.linspace(lo[1], hi[1], ng)
    GX, GY = np.meshgrid(gx, gy, indexing="ij")
    Q = np.stack([GX.ravel(), GY.ravel()], 1)
    inside = np.all(Q @ C.T <= h[None, :] - 1e-6, axis=1)
    Qi = Q[inside]
    W = [0, 0, 0, 1, 1, 0]
    res = run_batch([(spec, dict(mode="dist", target=[0, 0, 0, q[0], q[1], 0], W=W, eq_val=eqv)) for q in Qi],
                    4 if quick else 8, chunk=4 if quick else 8)
    dist = np.sqrt(np.array([r["f"] for r in res]))
    # confirm the worst points with heavy multistart
    order = np.argsort(-dist)[:5]
    conf = run_batch([(spec, dict(mode="dist", target=[0, 0, 0, Qi[i][0], Qi[i][1], 0], W=W, eq_val=eqv)) for i in order],
                     16 if quick else 48, chunk=8)
    for k, i in enumerate(order):
        dist[i] = min(dist[i], np.sqrt(conf[k]["f"]))
    dent = float(np.max(dist)) if dist.size else np.nan
    qmax = Qi[int(np.argmax(dist))] if dist.size else None
    width = float(np.max(h + np.roll(h, nang // 2)))  # max width of conv L
    print(model, scen, f"dent={dent:.4f} m at {None if qmax is None else (qmax + base).round(3)}; conv(L) width {width:.2f} m; "
          f"#grid inside {len(Qi)}, #dist>1e-3: {(dist > 1e-3).sum()}, time {time.time() - t0:.0f}s", flush=True)
    out = dict(model=model, scen=scen, S=S, omega=P["omega"], h=h.tolist(), theta=th.tolist(), support=S_pts.tolist(),
               Q=Qi.tolist(), dist=dist.tolist(), dent=dent, width=width, base=base.tolist())
    tag = f"{model}_{scen}" + ("_quick" if quick else "")
    json.dump(out, open(f"results/d1_{tag}.json", "w"), indent=1)
    fig, ax = plt.subplots(figsize=(6, 5.5))
    sc = ax.scatter(Qi[:, 0] + base[0], Qi[:, 1] + base[1], c=dist, s=30, cmap="viridis",
                    vmin=0, vmax=max(dent, 1e-3))
    plt.colorbar(sc, label="dist(q, L) [m]")
    hullpts = S_pts + base
    ax.plot(np.append(hullpts[:, 0], hullpts[0, 0]), np.append(hullpts[:, 1], hullpts[0, 1]), "r-", lw=1.5,
            label="support points of L (conv L boundary)")
    ax.set_aspect("equal"); ax.set_xlabel("landing x [m]"); ax.set_ylabel("landing y [m]")
    ax.set_title(f"{model}, {scen}: r0={S['r0']}, v0={S['v0']}, tf={tf}\nmax dist(conv L, L) = {dent:.3f} m", fontsize=9)
    ax.legend(fontsize=7)
    plt.tight_layout(); plt.savefig(f"results/d1_{tag}.png", dpi=130); plt.close()


if __name__ == "__main__":
    main()
