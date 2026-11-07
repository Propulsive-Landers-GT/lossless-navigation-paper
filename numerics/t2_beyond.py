"""Task 2: beyond the proven regime of Theorem B.

Parts (select with argv, default all):
  long   : long tf (delta + omega tf > pi/2), generalized midpoint M* = (0,0,z*), z* = min Dv_z, M1 3D, with tilt caps
  tent   : tent profile b(0) = b(tf) = e_z
  freetf : the 6D hole point (Dv, Dr) of fixed tf0 tested against all tf' (free final time union)
  slice  : planar slices of F_tf in (v0_x, r0_x) with v0_z fixed, r0_z free
  rho0   : rho1 = 0: generic nonconvexity index (random convex combinations of support points)
  m1a    : planar acceleration-limited kinematic axis (gimbal decoupled)
  m3     : torque-coupled TVC rigid body with GTPL parameters (planar + 3D): M*, gap, index, section
Outputs: results/t2_*.json, results/t2_*.png
"""
import sys, json, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import models
from runner import run_many, run_batch

D2R = np.pi / 180
OUT = "results/"
PARTS = sys.argv[1:] or ["long", "tent", "face", "freetf", "slice", "rho0", "m1a", "m3"]
QUICK = "quick" in PARTS
RES = {}


def save(name):
    json.dump(RES, open(OUT + f"t2_{name}.json", "w"), indent=1, default=float)


def gen_midpoint(spec, nstart, nstart_d=None, Wd=None):
    """z* = min Dv_z over R; lateral of minimizer; dist((0,0,z*), R)."""
    r = run_many(spec, dict(mode="lin", c=[0, 0, 1]), nstart)
    z = r["z"]; zs = z[2]; lat = float(np.hypot(z[0], z[1]))
    d = run_many(spec, dict(mode="dist", target=[0, 0, zs]), nstart_d or nstart)
    return dict(zstar=float(zs), lat=lat, dist=float(np.sqrt(d["f"])), znear=d["z"].tolist(),
                n_zmin_at_best=int(np.sum(np.array(r["fs"]) < r["fs"][0] + 1e-6)), n_ok=r["nok"])


def sphere_dirs(n, rng):
    v = rng.normal(size=(n, 3)); return v / np.linalg.norm(v, axis=1, keepdims=True)


def nonconvexity_index(spec, ndir, ncomb, nstart_sup, nstart_dist, rng, planar=False):
    """Lower bound on Hausdorff distance d_H(conv R, R): support points s(c) for random c, random
    convex combinations q of 2-3 support points, dist(q, R) by multistart NLP."""
    if planar:
        ang = rng.uniform(0, 2 * np.pi, ndir); C = np.stack([np.sin(ang), 0 * ang, np.cos(ang)], 1)
    else:
        C = sphere_dirs(ndir, rng)
    sup = run_batch([(spec, dict(mode="lin", c=-c)) for c in C], nstart_sup)
    S = np.array([s["z"] for s in sup])
    Q = []
    for _ in range(ncomb):
        k = rng.choice([2, 3]) if not planar else 2
        idx = rng.choice(len(S), k, replace=False)
        w = rng.dirichlet(np.ones(k)) if rng.random() < 0.5 else np.ones(k) / k
        Q.append(w @ S[idx])
    Q = np.array(Q)
    ds = run_batch([(spec, dict(mode="dist", target=q)) for q in Q], nstart_dist)
    dist = np.sqrt(np.array([d["f"] for d in ds]))
    return dict(support=S.tolist(), Q=Q.tolist(), dist=dist.tolist(), max=float(dist.max()),
                q_at_max=Q[int(np.argmax(dist))].tolist(), median=float(np.median(dist)),
                frac_pos=float(np.mean(dist > 1e-3)))


def part_long():
    P = models.gtpl()
    tfs = [1, 2, 3, 4, 6, 8, 10] if not QUICK else [2, 4, 8]
    out = {}
    for cap_name, cap in [("none", None), ("90deg", 90 * D2R), ("30deg", 30 * D2R)]:
        rows = []
        for tf in tfs:
            N = max(20, int(round(8 * tf))) if not QUICK else 20
            N = min(N, 60)
            spec = ("M1", P, dict(tf=float(tf), N=N, planar=False, tilt_max=cap))
            g = gen_midpoint(spec, 60 if not QUICK else 20)
            g.update(tf=tf, N=N, regime=bool(P["delta"] + P["omega"] * tf <= np.pi / 2),
                     Mz_thm=models.extreme_arcs_M1_cont(P, tf)["Mz"])
            rows.append(g)
            print("long", cap_name, tf, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items() if k != "znear"}, flush=True)
        out[cap_name] = rows
    RES["long"] = out; save("long")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for k, rows in out.items():
        ax[0].plot([r["tf"] for r in rows], [r["dist"] for r in rows], "o-", label=f"tilt cap {k}")
        ax[1].plot([r["tf"] for r in rows], [r["lat"] for r in rows], "o-", label=f"tilt cap {k}")
    tcrit = (np.pi / 2 - P["delta"]) / P["omega"]
    for a in ax:
        a.axvline(tcrit, color="k", ls=":", label="delta+omega tf = pi/2"); a.set_xlabel("tf [s]"); a.legend(fontsize=8)
    ax[0].set_ylabel("dist((0,0,z*), R) [m/s]"); ax[0].set_title("M1 GTPL w=30deg/s: gap of generalized midpoint")
    ax[1].set_ylabel("|lateral Dv| of min-Dv_z solution [m/s]")
    plt.tight_layout(); plt.savefig(OUT + "t2_long_tf.png", dpi=130); plt.close()


def part_face():
    """'Dive-then-brake' joint (Dv, Dr) face (cf. [adversary] B*): minimize c.(Dv,Dr) with
    c = ((tf - s*) e_z, -e_z), i.e. time weight w_z(s) = (s - s*) on a d_z: thrust up (max) before s*,
    tilt down (min throttle) after.  If the minimizer has lateral != 0, its rotations form a circle on a
    face of conv(Q), the face's centre is in conv(Q) and (if dist > 0) not in Q => F_tf nonconvex.
    Run for long tf with a tilt cap, where the pure-velocity face test of part 'long' becomes convex."""
    P = models.gtpl()
    rows = []
    for cap_name, cap in [("30deg", 30 * D2R), ("none", None)]:
        for tf in ([4, 8, 12] if not QUICK else [8]):
            for lead in [1.0, 2.0]:   # tf - s*
                N = 40 if not QUICK else 24
                spec = ("M1", P, dict(tf=float(tf), N=N, planar=False, tilt_max=cap, use_r=True))
                c = np.array([0, 0, lead, 0, 0, -1.0])
                r = run_many(spec, dict(mode="lin", c=c), 40 if not QUICK else 16)
                z = r["z"]; lat_v = float(np.hypot(z[0], z[1])); lat_r = float(np.hypot(z[3], z[4]))
                tgt = np.array([0, 0, z[2], 0, 0, z[5]])
                W = np.array([1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2])
                d = run_many(spec, dict(mode="dist", target=tgt, W=W), 40 if not QUICK else 16)
                n_at = int(np.sum(np.array(r["fs"]) < r["fs"][0] + 1e-6 * max(1, abs(r["fs"][0]))))
                row = dict(cap=cap_name, tf=tf, lead=lead, N=N, lat_v=lat_v, lat_r=lat_r, val=float(r["f"]),
                           dist_w=float(np.sqrt(d["f"])), znear=d["z"].tolist(), zface=z.tolist(), n_at_best=n_at)
                rows.append(row)
                print("face", cap_name, tf, lead, "lat_v %.3f lat_r %.3f dist_w %.4f" % (lat_v, lat_r, row["dist_w"]), flush=True)
    RES["face"] = rows; save("face")


def part_tent():
    P = models.gtpl()
    rows = []
    for tf in ([2, 4, 5, 6, 8, 10] if not QUICK else [2, 5]):
        N = min(60, max(20, 8 * tf))
        spec = ("M1", P, dict(tf=float(tf), N=N, planar=False, tent=True))
        ex = models.extreme_arcs_M1_cont(P, tf, tent=True)
        d = run_many(spec, dict(mode="dist", target=[0, 0, ex["Mz"]]), 60 if not QUICK else 20)
        g = gen_midpoint(spec, 60 if not QUICK else 20)
        g.update(tf=tf, N=N, Mz_thm=ex["Mz"], Px_thm=ex["Px"], dist_thm=float(np.sqrt(d["f"])),
                 regime=bool(P["delta"] + P["omega"] * tf / 2 <= np.pi / 2))
        rows.append(g); print("tent", tf, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in g.items() if k != "znear"}, flush=True)
    RES["tent"] = rows; save("tent")


def part_freetf():
    """Hole point of fixed tf0 (midpoint of extreme arcs in (Dv,Dr), i.e. midpoint of two landing
    boundary conditions (r0,v0) in F_tf0) tested for all tf' in a grid (free final time)."""
    out = {}
    for pname, P, tf0, tgrid in [("GTPL", models.gtpl(), 2.0, np.linspace(1.0, 6.0, 26 if not QUICK else 6)),
                                 ("Mars", models.mars(), 5.0, np.linspace(2.0, 15.0, 27 if not QUICK else 6))]:
        g = P["g"]; ez = np.array([0, 0, 1.0])
        exd = models.extreme_arcs_M1(P, tf0, 400)
        dv_s = np.array([0, 0, exd["Mz"]]); dr_s = np.array([0, 0, exd["Rz"]])
        v0 = g * tf0 * ez - dv_s; r0 = -v0 * tf0 + 0.5 * g * tf0 ** 2 * ez - dr_s
        jobs6, jobs3 = [], []
        for tfp in tgrid:
            N = int(min(50, max(20, 10 * tfp)))
            dvp = dv_s + g * (tfp - tf0) * ez
            drp = -v0 * tfp + 0.5 * g * tfp ** 2 * ez - r0
            W = np.array([1, 1, 1, 1 / tfp ** 2, 1 / tfp ** 2, 1 / tfp ** 2])
            jobs6.append((("M1", P, dict(tf=float(tfp), N=N, planar=False, use_r=True)),
                          dict(mode="dist", target=np.concatenate([dvp, drp]), W=W)))
            jobs3.append((("M1", P, dict(tf=float(tfp), N=N, planar=False)), dict(mode="dist", target=dvp)))
        ns = 40 if not QUICK else 10
        r6 = run_batch(jobs6, ns, chunk=ns // 2); r3 = run_batch(jobs3, ns, chunk=ns // 2)
        d6 = np.sqrt([r["f"] for r in r6]); d3 = np.sqrt([r["f"] for r in r3])
        out[pname] = dict(tf0=tf0, r0=r0.tolist(), v0=v0.tolist(), tgrid=tgrid.tolist(), dist_rv=d6.tolist(), dist_v_only=d3.tolist())
        print("freetf", pname, "r0", r0.round(3), "v0", v0.round(3), "\n  d6", d6.round(4), "\n  d3", d3.round(4), flush=True)
    RES["freetf"] = out; save("freetf")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for a, (k, o) in zip(ax, out.items()):
        a.semilogy(o["tgrid"], np.maximum(o["dist_rv"], 1e-6), "o-", label="(r0,v0) joint: weighted dist")
        a.semilogy(o["tgrid"], np.maximum(o["dist_v_only"], 1e-6), "s-", label="v0 only (r0 free)")
        a.axvline(o["tf0"], color="k", ls=":"); a.set_xlabel("tf' [s]"); a.set_ylabel("distance to R_tf' (floor 1e-6)")
        a.set_title(f"{k}: hole point of tf0={o['tf0']} vs free final time"); a.legend(fontsize=8)
    plt.tight_layout(); plt.savefig(OUT + "t2_free_tf.png", dpi=130); plt.close()


def part_slice():
    """Planar slices of F_tf: v0_z fixed (Dv_z = Mz + kappa), r0_z free; region in (v0_x, r0_x)."""
    P = models.gtpl(); tf = 2.0; N = 30
    ex = models.extreme_arcs_M1(P, tf, N)
    out = {}
    ng = 25 if not QUICK else 11
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    for a, kap in zip(ax, [0.1, 0.5, 1.5]):
        spec = ("M1", P, dict(tf=tf, N=N, planar=True, use_r=True, eq_idx=(2,)))
        # first find the extent: support in x for dv and dr
        xv = np.linspace(-1.15, 1.15, ng) * ex["Px"]; xr = np.linspace(-1.15, 1.15, ng) * ex["Rx"]
        jobs = []
        for a_ in xv:
            for b_ in xr:
                jobs.append((spec, dict(mode="dist", target=[a_, 0, 0, b_, 0, 0], W=[1, 0, 0, 1 / tf ** 2, 0, 0],
                                        eq_val=[ex["Mz"] + kap])))
        rr = run_batch(jobs, 6)
        D = np.sqrt(np.array([r["f"] for r in rr])).reshape(ng, ng)
        feas = D < 1e-4
        # map to boundary data: v0_x = -Dv_x, r0_x = Dv_x tf - Dr_x
        VX, RX = np.meshgrid(xv, xr, indexing="ij")
        v0x = -VX; r0x = VX * tf - RX
        a.scatter(v0x[feas], r0x[feas], s=12, c="tab:blue", label="feasible")
        a.scatter(v0x[~feas], r0x[~feas], s=4, c="0.85")
        a.set_xlabel("v0_x [m/s]"); a.set_ylabel("r0_x [m]")
        a.set_title(f"F_tf slice, tf=2s, v0_z fixed (Dv_z = M_z + {kap}), r0_z free")
        out[str(kap)] = dict(xv=xv.tolist(), xr=xr.tolist(), D=D.tolist())
        # midpoint test along the segment between the two islands
        print("slice", kap, "feasible frac", feas.mean(), flush=True)
    plt.tight_layout(); plt.savefig(OUT + "t2_F_slices.png", dpi=130); plt.close()
    RES["slice"] = out; save("slice")


def part_rho0():
    rng = np.random.default_rng(7)
    out = {}
    nd, nc = (16, 40) if not QUICK else (6, 10)
    cases = [("rho1=0, tf=2", models.gtpl(rho1=0.0), 2.0, None),
             ("rho1=0.4, tf=2", models.gtpl(), 2.0, None),
             ("rho1=0, tf=6", models.gtpl(rho1=0.0), 6.0, None),
             ("rho1=0, tf=6, tilt<=30", models.gtpl(rho1=0.0), 6.0, 30 * D2R),
             ("rho1=0.4, tf=6, tilt<=30", models.gtpl(), 6.0, 30 * D2R)]
    for name, P, tf, cap in cases:
        N = 30 if tf <= 2 else 40
        spec = ("M1", P, dict(tf=tf, N=N, planar=False, tilt_max=cap))
        ni = nonconvexity_index(spec, nd, nc, 10, 20, rng)
        g = gen_midpoint(spec, 30)
        ni["gen_midpoint"] = g
        out[name] = ni
        print("index", name, "max", round(ni["max"], 4), "median", round(ni["median"], 5), "frac>1e-3", ni["frac_pos"],
              "q*", np.round(ni["q_at_max"], 3), "| M*:", round(g["zstar"], 3), round(g["lat"], 3), round(g["dist"], 4), flush=True)
    RES["rho0"] = out; save("rho0")


def part_m1a():
    P = models.gtpl(omega=0.5)
    rows = []
    for eps in [0.5, 1.0, 2.4]:
        for tf in ([1, 2, 4, 6] if not QUICK else [2, 4]):
            spec = ("M1A", P, dict(tf=float(tf), N=40, eps=eps, omega=0.5))
            g = gen_midpoint(spec, 40); g.update(eps=eps, tf=tf)
            rows.append(g); print("m1a", eps, tf, round(g["zstar"], 4), round(g["lat"], 4), round(g["dist"], 4), flush=True)
    RES["m1a"] = rows; save("m1a")


def part_m3():
    out = {}
    rng = np.random.default_rng(11)
    P = models.gtpl()
    rows = []
    for planar in [True, False]:
        for om in [None, 0.5]:
            for tf in ([1, 2, 4, 6, 8] if not QUICK else [2, 4]):
                N = 30 if tf <= 4 else 40
                spec = ("M3", P, dict(tf=float(tf), N=N, planar=planar, omega_max=om))
                ns = 30 if planar else 20
                g = gen_midpoint(spec, ns)
                g.update(planar=planar, omega_max=om, tf=tf, N=N)
                rows.append(g)
                print("m3", "planar" if planar else "3d", om, tf, round(g["zstar"], 4), round(g["lat"], 4), round(g["dist"], 4), flush=True)
    out["midpoint"] = rows; RES["m3"] = out; save("m3")
    # tent version (upright at tf, rest)
    rows = []
    for tf in ([2, 4, 6, 8] if not QUICK else [4]):
        spec = ("M3", P, dict(tf=float(tf), N=40, planar=True, omega_max=0.5, tent=True, rest_final=True))
        g = gen_midpoint(spec, 30); g.update(tf=tf); rows.append(g)
        print("m3 tent planar", tf, round(g["zstar"], 4), round(g["lat"], 4), round(g["dist"], 4), flush=True)
    out["tent_planar"] = rows; save("m3")
    # nonconvexity index 3D, tf=4
    spec = ("M3", P, dict(tf=4.0, N=30, planar=False, omega_max=0.5))
    ni = nonconvexity_index(spec, 12 if not QUICK else 4, 24 if not QUICK else 6, 6, 10, rng)
    out["index_3d_tf4"] = ni
    print("m3 index", ni["max"], ni["median"], ni["frac_pos"], flush=True); save("m3")
    # section plot planar, tf=2 and 4
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for a, tf in zip(ax, [2.0, 4.0]):
        spec0 = ("M3", P, dict(tf=tf, N=30, planar=True, omega_max=0.5))
        r = run_many(spec0, dict(mode="lin", c=[0, 0, 1]), 30); zs = r["z"]
        sx = run_many(spec0, dict(mode="lin", c=[-1, 0, 0]), 30)["z"][0]
        xs = np.linspace(-sx, sx, 31 if not QUICK else 11)
        spec1 = ("M3", P, dict(tf=tf, N=30, planar=True, omega_max=0.5, eq_idx=(0,)))
        lo = run_batch([(spec1, dict(mode="lin", c=[0, 0, 1], eq_val=[x])) for x in xs], 12)
        hi = run_batch([(spec1, dict(mode="lin", c=[0, 0, -1], eq_val=[x])) for x in xs], 8)
        zlo = np.array([q["f"] for q in lo]); zhi = -np.array([q["f"] for q in hi])
        zlo[~np.isfinite(zlo)] = np.nan; zhi[~np.isfinite(zhi)] = np.nan
        a.plot(xs, zlo, "r-", lw=2, label="lower boundary z_min(x)")
        a.plot(xs, zhi, "r--", label="upper boundary")
        a.plot([-abs(zs[0]), abs(zs[0])], [zs[2], zs[2]], "k:o", label="chord between min-Dv_z points")
        a.plot(0, zs[2], "k*", ms=12, label="M* (in conv R)")
        a.set_xlabel("Dv_x [m/s]"); a.set_ylabel("Dv_z [m/s]"); a.legend(fontsize=8)
        a.set_title(f"M3 torque-coupled TVC, GTPL, tf={tf}s, |w|<=0.5 rad/s (planar)")
        out[f"section_tf{tf}"] = dict(xs=xs.tolist(), zlo=zlo.tolist(), zhi=zhi.tolist(), zstar=zs.tolist())
    plt.tight_layout(); plt.savefig(OUT + "t2_M3_section.png", dpi=130); plt.close()
    save("m3")


if __name__ == "__main__":
    t0 = time.time()
    for p in PARTS:
        if p == "quick":
            continue
        print("=== part", p, flush=True)
        globals()["part_" + p]()
        print("=== done", p, round(time.time() - t0, 1), flush=True)


def part_rho0b():
    """Candidate possibility regime (rho1 = 0, alpha = 0, delta + omega tf <= pi/2): LOCAL nonconvexity
    index in the joint (Dv, Dr) space Q (=> F_tf).  Support points for pairs/triples of NEARBY random
    directions in R^6 (angle 5-40 deg), whose convex combinations lie near the boundary of conv Q, where
    a dent would be.  Compared with rho1 = 0.4 (same tf) as a positive control."""
    rng = np.random.default_rng(21)
    out = {}
    for name, P in [("rho1=0,alpha=0", models.gtpl(rho1=0.0, alpha=0.0)), ("rho1=0.4,alpha=0", models.gtpl(alpha=0.0))]:
        for tf in [2.0]:
            spec = ("M1", P, dict(tf=tf, N=30, planar=False, use_r=True))
            W = np.array([1, 1, 1, 1 / tf ** 2, 1 / tf ** 2, 1 / tf ** 2])
            npairs = 60 if not QUICK else 10
            C1 = rng.normal(size=(npairs, 6)); C1 /= np.linalg.norm(C1, axis=1, keepdims=True)
            C2 = []
            for c in C1:
                ang = rng.uniform(5, 40) * D2R
                p = rng.normal(size=6); p -= p.dot(c) * c; p /= np.linalg.norm(p)
                C2.append(np.cos(ang) * c + np.sin(ang) * p)
            C2 = np.array(C2)
            Cw = np.vstack([C1, C2])
            sup = run_batch([(spec, dict(mode="lin", c=-c)) for c in Cw], 10)
            S = np.array([s["z"] for s in sup])
            Q = 0.5 * (S[:npairs] + S[npairs:])
            ds = run_batch([(spec, dict(mode="dist", target=q, W=W)) for q in Q], 24, chunk=8)
            dist = np.sqrt([d["f"] for d in ds])
            out[f"{name},tf={tf}"] = dict(max=float(dist.max()), median=float(np.median(dist)), dist=dist.tolist(),
                                          frac_pos=float(np.mean(dist > 1e-3)))
            print("rho0b", name, tf, "max %.4f median %.5f frac>1e-3 %.3f" % (dist.max(), np.median(dist), np.mean(dist > 1e-3)), flush=True)
    RES["rho0b"] = out; save("rho0b")
