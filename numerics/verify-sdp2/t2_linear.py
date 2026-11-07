"""[verify-sdp2] T2 (math/09 §2.2): linear objectives <yv,V>+<yr,R> are exact in every model.
(a) constructive: take the SDP optimum factor (rank up to n+3), apply the primer-plane fold
    F x = P_Pi x + ||P_{Pi^perp} x|| m, check feasibility in R^3 and objective preservation;
(b) independent: SDP value vs 3D multistart NLP;
(c) fold applied to lifted rank>3 optima of the QUADRATIC problem at unit-d gap instances (feasibility + linear part kept).
"""
import sys, json, time
import numpy as np
from core import Model, EZ

rng = np.random.default_rng(20261107)


def fold(z, yv, yr):
    """z: n x dim (first 3 coords E). Pi = span(yv,yr) in E."""
    dim = z.shape[1]
    Ub = np.linalg.svd(np.vstack([yv, yr]).T, full_matrices=False)[0]   # 3x2 orthonormal basis of Pi
    m = np.cross(Ub[:, 0], Ub[:, 1]); m /= np.linalg.norm(m)
    if m @ EZ < 0:
        m = -m
    out = np.zeros((z.shape[0], 3))
    for i, x in enumerate(z):
        xE = x[:3]
        pPi = Ub @ (Ub.T @ xE)
        perp2 = np.sum(x ** 2) - pPi @ pPi
        out[i] = pPi + np.sqrt(max(perp2, 0.0)) * m
    return out, m


def lin_obj(M, z, yv, yr):
    V, R = M.readout(z)
    return float(yv @ V[:3] + yr @ R[:3])


def run():
    log = open('t2_linear.txt', 'w')
    def P(s):
        print(s, flush=True); log.write(s + '\n'); log.flush()
    P('# T2 linear-objective test. cols: model N wtf term | SDP rank(ev>1e-6) | fold viol, |obj_fold-SDP| | NLP3 best | rel gap SDP-NLP3')
    worst_fold = 0.0; worst_gap = 0.0; nt = 0
    for kind, dd in (('unit', 15), ('unit', 40), ('cvx', 15), ('cvx', 40), ('d0', 0)):
        for term in (True, False):
            for N in (4, 7):
                for wtf in (1.0, 2.5, 5.0):
                    M = Model(N, 4.0, wtf / 4.0, dd, kind, terminal=term, a=np.linspace(1.0, 1.4, N))
                    for trial in range(3):
                        # generic direction: laterals far from parallel, random vertical
                        yv = rng.normal(size=3); yr = rng.normal(size=3)
                        s = M.sdp(obj=('lin', yv, yr))
                        Zl = M.factor(s['G'])
                        zf, m = fold(Zl, yv, yr)
                        vf = M.violation(zf); of = lin_obj(M, zf, yv, yr)
                        val, z3, _ = M.best(obj=('lin', yv, yr), rng=rng, nstart=6, extra=[zf])
                        rk = int(np.sum(s['ev'] > 1e-6 * s['ev'][0]))
                        gap = (s['val'] - val) / max(abs(s['val']), 1e-9)
                        worst_fold = max(worst_fold, vf, abs(of - s['val']) / max(abs(s['val']), 1))
                        worst_gap = max(worst_gap, gap); nt += 1
                        P(f"{kind}{dd} N={N} wtf={wtf} term={int(term)} | rank={rk} | fold viol={vf:.1e} dobj={of - s['val']:+.1e} | NLP3={val:.8g} SDP={s['val']:.8g} gap={gap:+.1e}")
    P(f'# SUMMARY generic: {nt} instances, worst fold (viol or rel dobj) = {worst_fold:.2e}, worst rel gap SDP-NLP3 = {worst_gap:.2e}')

    # (c) adversarial: case 12 (unit-d gap instance) -- linear objective along its genuine residual direction,
    #     and fold of the rank-4 QUADRATIC SDP optimum.
    deg = 15
    M = Model(16, 4.0, np.deg2rad(30), deg, 'unit', terminal=True, a=np.full(16, 11.0))
    wv = np.array([5.0939, 21.9914, 32.1819]); wr = np.array([8.2825, 44.1701, 64.9080])
    sq = M.sdp(wv, wr)
    Zl = M.factor(sq['G'])
    V, R = M.readout(Zl)
    yv, yr = V[:3] - wv, R[:3] - wr
    P(f'# case12 unit-d quadratic SDP={sq["val"]:.7g} ev={np.round(sq["ev"][:5],4)}')
    zf, m = fold(Zl, yv, yr)
    P(f'  fold of lifted quad optimum: viol={M.violation(zf):.1e}, <y,Y> lifted={yv@V[:3]+yr@R[:3]:.8g} folded={lin_obj(M, zf, yv, yr):.8g}, '
      f'quad cost folded={M.cost(zf, wv, wr):.7g} (>= SDP, Brouwer remark)')
    for (yy, lab) in (((yv, yr), 'residual dir'), ((-yv, -yr), '-residual dir'), ((rng.normal(size=3), rng.normal(size=3)), 'random')):
        s = M.sdp(obj=('lin', yy[0], yy[1]))
        Zl2 = M.factor(s['G']); zf2, _ = fold(Zl2, *yy)
        val, z3, _ = M.best(obj=('lin',) + yy, rng=rng, nstart=4, extra=[zf2])
        P(f'  case12 linear {lab}: SDP={s["val"]:.9g} fold viol={M.violation(zf2):.1e} obj_fold={lin_obj(M, zf2, *yy):.9g} NLP3={val:.9g}')
    # N=3 Lasserre-recipe style instance (math/08 §6.4) with delta=40, unit-d: gaps known for quadratic cost
    for dd in (15, 40):
        M = Model(3, 1.0, 1.0, dd, 'unit', terminal=True)
        for t in range(4):
            yv = rng.normal(size=3); yr = rng.normal(size=3)
            s = M.sdp(obj=('lin', yv, yr)); zf2, _ = fold(M.factor(s['G']), yv, yr)
            val, _, _ = M.best(obj=('lin', yv, yr), rng=rng, nstart=10, extra=[zf2])
            P(f'  N=3 unit{dd} linear: SDP={s["val"]:.9g} fold viol={M.violation(zf2):.1e} obj_fold={lin_obj(M, zf2, yv, yr):.9g} NLP3={val:.9g}')


if __name__ == '__main__':
    run()
