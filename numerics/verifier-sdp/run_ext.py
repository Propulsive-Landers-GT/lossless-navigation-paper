"""[verifier-sdp] Part 3: extensions.  Usage: python run_ext.py {throttle|gimbal|altitude|fuel}
Writes results/ext_<block>.jsonl."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
import cvxpy as cp
from vcore import Prob, EZ
from vext import *
from vqcqp import lin, prod, qadd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def dump(fout, **kw):
    fout.write(json.dumps(kw, default=float) + "\n"); fout.flush()


def gapstr(L, U):
    return (U - L), (U - L) / max(abs(U), 1e-12)


# ------------------------------------------------------------------------------------- throttle
def block_throttle(fout, rng):
    for N in (4, 6, 8, 12):
        for wtf in (0.5, 1.5, 3.0, 1e3):
            for (a1, a2) in ((0.5, 1.0), (0.8, 1.0)):
                for readout in ("rv", "r"):
                    if N == 16 and readout == "r":
                        continue
                    Pm = Prob(N, 1.0, wtf, readout=readout, accel=np.full(N + 1, a1))
                    M = Pm.midpoint_M()
                    Qs = [("M_a1", M), ("0.8M", 0.8 * M), ("1.1M", 1.1 * M)]
                    S = Prob(N, 1.0, wtf, readout=readout, accel=np.full(N + 1, a2)).gamma.sum(0)
                    for j in range(3):
                        Qs.append(("rand", rng.normal(size=M.shape) * 0.5 * S[:, None]))
                    for lab, Q in Qs:
                        T = throttle(N, 1.0, wtf, Q, a1, a2, readout=readout)
                        t0 = time.time()
                        s = T.sdp()
                        b = T.best_of(starts_throttle(T, rng, 40 if N <= 8 else 24, min(wtf, 50)))
                        dg, rg = gapstr(s["val"], b["f"])
                        dump(fout, block="throttle", N=N, wtf=wtf, a1=a1, a2=a2, readout=readout, label=lab,
                             Q=np.asarray(Q).tolist(), L=s["val"], st=s["status"], rank=s["rank"], U=b["f"],
                             nsame=int(np.sum(np.array(b["fs"]) < b["f"] + 1e-8)), absgap=dg, relgap=rg,
                             a_sdp=s["z"][:N].tolist(), a_gen=b["z"][:N].tolist() if b["z"] is not None else None,
                             secs=time.time() - t0)
                        print(f"throttle N={N} wtf={wtf} a=[{a1},{a2}] {readout} {lab:5s} L={s['val']:.8g}[{s['status'][:4]}] "
                              f"U={b['f']:.8g} rel={rg:.2e} rank={s['rank']}", flush=True)


# ------------------------------------------------------------------------------------- gimbal
def block_gimbal(fout, rng):
    for N in (6, 12, 16):
        for wtf in (0.5, 1.5, 3.0):
            for deg in (5, 15, 40):
                delta = np.radians(deg)
                for readout in ("rv", "r"):
                    P0 = Prob(N, 1.0, wtf, readout=readout)
                    # extreme arcs tilt phi + delta (thrust leans further by delta)
                    k = np.arange(N + 1)
                    phi = np.minimum(np.minimum(k, N - k) * wtf / N + delta, np.pi)
                    th = lambda u: np.sin(phi)[:, None] * u + np.cos(phi)[:, None] * EZ
                    Pu = P0.readout_of(th(np.array([1, 0, 0]))); Pmu = P0.readout_of(th(np.array([-1, 0, 0])))
                    M = 0.5 * (Pu + Pmu)
                    rho = P0.gamma.T @ np.sin(phi); zmin = P0.gamma.T @ np.cos(phi); S = P0.gamma.sum(0)
                    Qs = [("M", M)]
                    for (s_, h) in ((0.5, 0.0), (0.9, 0.01), (0.5, -0.05)):
                        for perp in ((False, True) if readout == "rv" else (False,)):
                            Q = np.zeros((P0.p, 3))
                            for l in range(P0.p):
                                ps = np.pi / 2 * l if perp else 0.0
                                Q[l] = [s_ * rho[l] * np.cos(ps), s_ * rho[l] * np.sin(ps), zmin[l] + h * S[l]]
                            Qs.append((f"face s={s_} h={h}{' perp' if perp else ''}", Q))
                    for j in range(3):
                        Qs.append(("rand", rng.normal(size=M.shape) * 0.6 * S[:, None]))
                    for lab, Q in Qs:
                        F = fixed_thrust(N, 1.0, wtf, Q, readout=readout, delta=delta)
                        t0 = time.time()
                        s = F.sdp()
                        b = F.best_of(starts_fixed(F, N, rng, 30 if N <= 6 else 16, delta=delta, omega=wtf))
                        dg, rg = gapstr(s["val"], b["f"])
                        dump(fout, block="gimbal", N=N, wtf=wtf, deg=deg, readout=readout, label=lab, Q=np.asarray(Q).tolist(),
                             L=s["val"], st=s["status"], rank=s["rank"], ev=s["ev"][:6].tolist(), U=b["f"],
                             absgap=dg, relgap=rg, secs=time.time() - t0)
                        print(f"gimbal N={N} wtf={wtf} d={deg} {readout} {lab:22s} L={s['val']:.9g}[{s['status'][:4]}] "
                              f"U={b['f']:.9g} rel={rg:.2e} rank={s['rank']}", flush=True)


# ------------------------------------------------------------------------------------- altitude / glide slope
def altitude_path(r0, v0, g, a, variant, tang=None, nodes=None):
    """returns path(m, th, b, dt) for fixed_thrust; altitude r_z(t_j) >= 0 at nodes j=1..N-1."""
    def path(m, th, b, dt):
        N = len(th)
        alts, lats = [], []
        for j in range(1, N):
            tj = j * dt
            Rz = lin(m, np.zeros(m), r0[2] + v0[2] * tj - 0.5 * g * tj ** 2)
            Rx = lin(m, np.zeros(m), r0[0] + v0[0] * tj)
            Ry = lin(m, np.zeros(m), r0[1] + v0[1] * tj)
            for k in range(j):
                w = a * dt * (tj - k * dt - dt / 2)
                Rz = qadd(Rz, th[k].comp(2), w=[1, w])
                Rx = qadd(Rx, th[k].comp(0), w=[1, w])
                Ry = qadd(Ry, th[k].comp(1), w=[1, w])
            alts.append(Rz); lats.append((Rx, Ry))
        cons = []
        convex = []
        if variant in ("A", "B"):
            cons += [(*f, ">=") for f in alts]
        if variant == "B":
            for i in range(len(alts)):
                for j in range(i, len(alts)):
                    cons.append((*prod(alts[i], alts[j]), ">="))
        if variant in ("G", "G2"):
            cons += [(*f, ">=") for f in alts]
            if variant == "G2":   # lifted  tan^2 r_z^2 - |r_xy|^2 >= 0
                for f, (fx, fy) in zip(alts, lats):
                    q = qadd(prod(f, f), prod(fx, fx), prod(fy, fy), w=[tang ** 2, -1, -1])
                    cons.append((*q, ">="))

            def convex_z(z):
                out = []
                for f, (fx, fy) in zip(alts, lats):
                    ex = lambda tr: 2 * (tr[1] @ z) + tr[2]
                    out.append(cp.norm(cp.hstack([ex(fx), ex(fy)])) <= tang * ex(f))
                return out
            return cons, convex_z
        return cons, None
    return path


def block_altitude(fout, rng):
    g, a = 1.0, 1.5
    found = 0
    tries = 0
    while found < 14 and tries < 300:
        tries += 1
        N = int(rng.choice([8, 12, 16])); tf = float(rng.choice([2.0, 4.0])); omega = float(rng.choice([0.3, 0.8]))
        r0 = np.array([rng.uniform(-3, 3), rng.uniform(-1, 1), rng.uniform(0.3, 3.0)])
        v0 = np.array([rng.uniform(-1.5, 1.5), rng.uniform(-0.5, 0.5), rng.uniform(-2.5, 0.0)])
        accel = np.full(N + 1, a)
        # readout target: thrust part must equal -(r0 + v0 tf - g tf^2/2 ez), -(v0 - g tf ez)
        Q = np.array([-(r0 + v0 * tf - 0.5 * g * tf ** 2 * EZ), -(v0 - g * tf * EZ)])
        F0 = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel)
        b0 = F0.best_of(starts_fixed(F0, N, rng, 12, omega=omega))
        if b0["z"] is None:
            continue
        # altitude of the unconstrained genuine optimum
        Fa = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel, path=altitude_path(r0, v0, g, a, "A"))
        Fa.nlp()
        alts = []
        # evaluate altitude constraints (the last N-1 rows of g beyond base constraints)
        gv = np.array(Fa._gfun(b0["z"])).ravel()[-(N - 1):]
        if gv.min() > -0.02:
            continue
        if Fa.sdp()["status"] != "optimal":
            continue
        if Fa.best_of(starts_fixed(Fa, N, rng, 12, omega=omega))["z"] is None:
            continue
        found += 1
        tang = np.tan(np.radians(75))     # glide-slope cone half-angle 75 deg from vertical
        FG2 = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel, path=altitude_path(r0, v0, g, a, "G2", tang=tang))
        bG = FG2.best_of(starts_fixed(FG2, N, rng, 24, omega=omega, extra=[b0["z"]]))
        for variant in ("A", "B", "G", "G2"):
            Fv = fixed_thrust(N, tf, omega, Q, readout="rv", accel=accel,
                              path=altitude_path(r0, v0, g, a, variant, tang=tang))
            t0 = time.time()
            s = Fv.sdp()
            if variant in ("A", "B"):
                b = Fv.best_of(starts_fixed(Fv, N, rng, 24, omega=omega, extra=[b0["z"]]))
            else:
                b = bG      # genuine glide-slope problem (exact quadratic cone constraint + altitude)
            dg, rg = gapstr(s["val"], b["f"])
            dump(fout, block="altitude", N=N, tf=tf, omega=omega, r0=r0.tolist(), v0=v0.tolist(), variant=variant,
                 unconstrained=b0["f"], minalt_uncon=float(gv.min()), L=s["val"], st=s["status"], rank=s["rank"],
                 ev=s["ev"][:6].tolist(), U=b["f"], absgap=dg, relgap=rg, secs=time.time() - t0)
            print(f"altitude #{found} N={N} tf={tf} w={omega} var={variant}: uncon={b0['f']:.6g} (minalt {gv.min():.3f}) "
                  f"L={s['val']:.8g}[{str(s['status'])[:4]}] U={b['f']:.8g} rel={rg:.2e} rank={s['rank']}", flush=True)


# ------------------------------------------------------------------------------------- min fuel
def block_fuel(fout, rng):
    a1, a2 = 0.5, 1.0
    for N in (6, 8, 12):
        for wtf in (0.5, 1.5, 3.0):
            Pm = Prob(N, 1.0, wtf, readout="rv", accel=np.full(N + 1, a1))
            M = Pm.midpoint_M()
            Qs = [("M_a1 (unreachable)", M)]
            # reachable targets: random genuine trajectories with random throttle
            T0 = throttle(N, 1.0, wtf, M, a1, a2, readout="rv")
            for z in starts_throttle(T0, rng, 6, wtf):
                # make it exactly feasible by polishing toward itself, then read out
                a = z[:N]; Uv = np.vstack([[0, 0, a[0]]] + [z[N + 3 * (k - 1):N + 3 * k] for k in range(1, N)])
                dt = 1.0 / N; t = np.arange(N) * dt
                Y = np.array([(dt * (1 - t - dt / 2)) @ Uv, dt * Uv.sum(0)])
                Qs.append(("reach", Y))
            # dent points: near M but slightly lifted (may or may not be reachable)
            Qs.append(("M+up", M + np.array([[0, 0, 0.02], [0, 0, 0.02]])))
            for lab, Q in Qs:
                for landing in ("linear", "lifted"):
                    eps = 1e-8
                    T = throttle(N, 1.0, wtf, Q, a1, a2, readout="rv", objective="fuel", landing=landing, eps=eps)
                    t0 = time.time()
                    s = T.sdp()
                    starts = starts_throttle(T, rng, 40, wtf)
                    if lab == "reach":
                        pass
                    b = T.best_of(starts, feas_tol=1e-7)
                    # second-moment landing error of the SDP solution
                    errL = T.eval_lifted(T.info["err"], s["M"]) if s["M"] is not None else np.nan
                    U = b["f"]
                    dump(fout, block="fuel", N=N, wtf=wtf, label=lab, landing=landing, Q=np.asarray(Q).tolist(),
                         L=s["val"], st=s["status"], rank=s["rank"], U=U, lifted_err=errL,
                         a_sdp=None if s["z"] is None else s["z"][:N].tolist(), secs=time.time() - t0)
                    print(f"fuel N={N} wtf={wtf} {lab:20s} {landing:6s} L={s['val']:.8g}[{str(s['status'])[:6]}] U={U:.8g} "
                          f"rank={s['rank']} liftedErr={errL:.2e}", flush=True)


if __name__ == "__main__":
    blk = sys.argv[1]
    rng = np.random.default_rng({"throttle": 11, "gimbal": 12, "altitude": 13, "fuel": 14}[blk])
    with open(os.path.join(OUT, f"ext_{blk}.jsonl"), "w") as fout:
        globals()["block_" + blk](fout, rng)
