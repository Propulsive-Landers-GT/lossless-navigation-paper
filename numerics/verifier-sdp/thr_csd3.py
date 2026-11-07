"""[verifier-sdp] Variable throttle:
 (a) Is the 40% gap of the natural U-lift a discretization artifact?  Fixed physical problem
     (tf=1, omega=2 rad/s, a in [0.5,1], fixed (r,v) target), N = 4..16: U-lift SDP vs genuine.
     (Relaxed controls do not change this model: conv{a b_k : a in [a1,a2]} is already the segment.)
 (b) [proof-sdp] CSD3 separate-axis lift: Gram of (u_k, b_k, e) + scalars Gamma_k, S_k:
       ||b_k|| = 1, <b_k,b_k+1> >= c,  <u_k,b_k> >= Gamma_k cos(delta),  ||u_k||^2 <= S_k,
       S_k >= Gamma_k^2,  S_k <= (a1+a2) Gamma_k - a1 a2,  a1 <= Gamma_k <= a2.
     compared with  genuine-original (a1 <= ||u|| <= a2, angle(u,b) <= delta, unit b, rate)
     and genuine-CW (||u|| <= Gamma, <u,b> >= Gamma cos(delta), Gamma in [a1,a2]; the C-W relaxation at fixed b).
Writes results/thr_csd3.jsonl."""
import os, sys, json, time, warnings
warnings.filterwarnings("ignore")
import numpy as np
import cvxpy as cp
import casadi as ca
from vext import throttle, starts_throttle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
EZ = np.array([0, 0, 1.0])


def weights(N, tf):
    h = tf / N; t = np.arange(N) * h
    return h * (tf - t - h / 2), h * np.ones(N), h


def csd3_sdp(N, tf, om, wr, wv, a1, a2, delta):
    gr, gv, h = weights(N, tf)
    c = np.cos(min(om * h, np.pi)); cd = np.cos(delta)
    nb = N - 1
    n = N + nb
    Z = cp.Variable((n + 3, n + 3), symmetric=True)
    Gm = cp.Variable(N); S = cp.Variable(N)
    iu = lambda k: k
    ib = lambda k: N + k - 1
    ez = n + 2
    cons = [Z >> 0, Z[n:, n:] == np.eye(3)]
    bb = lambda j, k: (Z[ib(j), ib(k)] if (1 <= j <= nb and 1 <= k <= nb) else
                       Z[ib(j), ez] if 1 <= j <= nb else Z[ib(k), ez] if 1 <= k <= nb else 1.0)
    ub = lambda k: Z[iu(k), ib(k)] if 1 <= k <= nb else Z[iu(k), ez]
    for k in range(1, nb + 1):
        cons.append(Z[ib(k), ib(k)] == 1)
    for k in range(N):
        e = bb(k, k + 1)
        if not isinstance(e, float):
            cons.append(e >= c)
    for k in range(N):
        cons += [ub(k) >= Gm[k] * cd, Z[iu(k), iu(k)] <= S[k], cp.square(Gm[k]) <= S[k],
                 S[k] <= (a1 + a2) * Gm[k] - a1 * a2, Gm[k] >= a1, Gm[k] <= a2]
    G = Z[:N, :N]; X = Z[:N, n:]
    obj = 0
    for g, w in ((gr, wr), (gv, wv)):
        obj = obj + g @ G @ g - 2 * g @ X @ w + w @ w
    pr = cp.Problem(cp.Minimize(obj), cons)
    pr.solve(solver="CLARABEL", tol_gap_abs=1e-9, tol_gap_rel=1e-9, tol_feas=1e-9, max_iter=500)
    ev = np.linalg.eigvalsh(Z.value)[::-1]
    return float(pr.value), pr.status, float(ev[3] / ev[0])


class ThrNLP:
    """genuine models: mode 'orig' (a1<=|u|<=a2, <u,b> >= |u| cos delta) or 'cw' (|u|<=G, <u,b> >= G cos delta)."""
    def __init__(self, N, tf, om, a1, a2, delta, mode):
        gr, gv, h = weights(N, tf)
        c = np.cos(min(om * h, np.pi)); cd = np.cos(delta)
        nb = N - 1
        x = ca.SX.sym("x", 3 * nb + 3 * N + N)
        p = ca.SX.sym("p", 6)
        Bf = ca.reshape(x[:3 * nb], 3, nb)
        U = ca.reshape(x[3 * nb:3 * nb + 3 * N], 3, N)
        Gm = x[3 * nb + 3 * N:]
        ez = ca.DM(EZ)
        B = ca.horzcat(ez, Bf, ez)
        f = ca.sumsqr(ca.mtimes(U, ca.DM(gr)) - p[0:3]) + ca.sumsqr(ca.mtimes(U, ca.DM(gv)) - p[3:6])
        g, lb, ub = [], [], []
        for k in range(1, N):
            g.append(ca.sumsqr(B[:, k])); lb.append(1); ub.append(1)
        for k in range(N):
            g.append(ca.dot(B[:, k], B[:, k + 1])); lb.append(c); ub.append(ca.inf)
            if mode == "orig":
                g.append(ca.sumsqr(U[:, k])); lb.append(a1 ** 2); ub.append(a2 ** 2)
                g.append(ca.dot(U[:, k], B[:, k]) - cd * ca.sqrt(ca.sumsqr(U[:, k]) + 1e-16)); lb.append(0); ub.append(ca.inf)
                g.append(Gm[k]); lb.append(0); ub.append(0)
            else:
                g.append(Gm[k] ** 2 - ca.sumsqr(U[:, k])); lb.append(0); ub.append(ca.inf)
                g.append(ca.dot(U[:, k], B[:, k]) - cd * Gm[k]); lb.append(0); ub.append(ca.inf)
                g.append(Gm[k]); lb.append(a1); ub.append(a2)
        opts = {"ipopt.print_level": 0, "print_time": 0, "ipopt.tol": 1e-11, "ipopt.sb": "yes",
                "ipopt.constr_viol_tol": 1e-10, "ipopt.max_iter": 3000}
        self.S = ca.nlpsol("S", "ipopt", {"x": x, "p": p, "f": f, "g": ca.vertcat(*g)}, opts)
        self.gf = ca.Function("g", [x], [ca.vertcat(*g)])
        self.lb, self.ub = np.array(lb, float), np.array(ub, float)
        self.N, self.nb, self.om, self.h, self.a1, self.a2 = N, nb, om, h, a1, a2

    def best(self, wr, wv, rng, k):
        best = np.inf
        N = self.N
        for j in range(k):
            s = rng.uniform(0.1, 1); psi0 = rng.uniform(0, 2 * np.pi); sw = rng.uniform(-3, 3) * (j % 2)
            kk = np.arange(N + 1); phi = np.minimum(s * np.minimum(kk, N - kk) * self.om * self.h, np.pi)
            psi = psi0 + sw * np.linspace(0, np.pi, N + 1)
            B = np.stack([np.sin(phi) * np.cos(psi), np.sin(phi) * np.sin(psi), np.cos(phi)], 1)
            a = rng.uniform(self.a1, self.a2, N)
            U = a[:, None] * B[:N]
            x0 = np.r_[B[1:N].ravel(), U.ravel(), a]
            r = self.S(x0=x0, p=np.r_[wr, wv], lbg=self.lb, ubg=self.ub)
            x = np.array(r["x"]).ravel()
            gv = np.array(self.gf(x)).ravel()
            viol = max(0, np.max(self.lb - gv), np.max(gv - self.ub))
            if viol < 1e-7:
                f = float(r["f"])
                best = min(best, f)
        return best


if __name__ == "__main__":
    rng = np.random.default_rng(21)
    fout = open(os.path.join(OUT, "thr_csd3.jsonl"), "w")
    a1, a2 = 0.5, 1.0
    Q = np.array([[0.1727921, 0.41080907, 0.16521854], [-0.65157862, 0.45267793, 0.22318729]])
    # (a) refinement of the natural U-lift gap
    for N in (4, 6, 8, 12, 16):
        T = throttle(N, 1.0, 2.0, Q, a1, a2, readout="rv", rlt=(N <= 12))
        s = T.sdp()
        b = T.best_of(starts_throttle(T, rng, 60 if N <= 8 else 30, 2.0))
        rec = dict(part="refine", N=N, L=s["val"], st=s["status"], rank=s["rank"], U=b["f"], rel=(b["f"] - s["val"]) / b["f"])
        fout.write(json.dumps(rec) + "\n"); fout.flush()
        print(rec, flush=True)
    # (b) CSD3
    for N in (4, 6, 8, 12):
        for deg in (0.0, 15.0):
            for wtf in (1.0, 2.0, 6.0):
                for j in range(4):
                    Qj = Q if j == 0 else rng.normal(size=(2, 3)) * 0.5
                    wr, wv = Qj[0], Qj[1]
                    L, st, e4 = csd3_sdp(N, 1.0, wtf, wr, wv, a1, a2, np.deg2rad(deg))
                    Uo = ThrNLP(N, 1.0, wtf, a1, a2, np.deg2rad(deg), "orig").best(wr, wv, rng, 40)
                    Uc = ThrNLP(N, 1.0, wtf, a1, a2, np.deg2rad(deg), "cw").best(wr, wv, rng, 40)
                    rec = dict(part="csd3", N=N, deg=deg, wtf=wtf, j=j, Q=Qj.tolist(), L=L, st=st, e4=e4, U_orig=Uo, U_cw=Uc,
                               rel_orig=(Uo - L) / max(Uo, 1e-12), rel_cw=(Uc - L) / max(Uc, 1e-12))
                    fout.write(json.dumps(rec) + "\n"); fout.flush()
                    print(f"CSD3 N={N} deg={deg} wtf={wtf} j={j}: SDP {L:.7g} [{st[:4]}] e4={e4:.1e} | genuine-orig {Uo:.7g} "
                          f"(rel {rec['rel_orig']:.1e}) | genuine-CW {Uc:.7g} (rel {rec['rel_cw']:.1e})", flush=True)
