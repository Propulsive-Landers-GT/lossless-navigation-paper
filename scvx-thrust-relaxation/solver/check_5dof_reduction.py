"""Check that the roll-free 5-DOF model reproduces the 6-DOF one.

Continuous time: integrate sixdof_lcvx.Model and the 5-DOF field side by side with the same RK4
stages, feeding the 5-DOF model the inertial thrust T_I = R(q) T_B, and compare (m, r, v, R e_1,
R w) with the 5-DOF state. Discrete time: map the 6-DOF IPOPT optimum of sdp_relaxation.py into
the variables of sdp_relaxation_5dof.py and evaluate the 5-DOF constraints there.
"""
import numpy as np

from sdp_relaxation import Lander, evaluate, solve_nlp
from sdp_relaxation_5dof import Lander5
from sixdof_lcvx import IQ, IW, Model, Params, quat_to_dcm


def f5(p, y, T, G):
    m, v, b, W = y[0], y[4:7], y[7:10], y[10:13]
    return np.concatenate([[-p.alpha * G], v, T / m + p.g, np.cross(W, b),
                           p.rT[0] / p.J[1] * np.cross(b, T)])


def project(x):
    R = np.array(quat_to_dcm(x[IQ]))
    return np.concatenate([x[:7], R[:, 0], R @ x[IW]])


def max_difference(model, x0, U, G, s):
    p, M = model.p, model.p.substeps
    h = s / (p.N * M)
    f = lambda z, u, g: np.concatenate([model.f(z[:14], u, g),
                                        f5(p, z[14:], np.array(quat_to_dcm(z[IQ])) @ u, g)])
    z, err = np.concatenate([x0, project(x0)]), 0.0
    for k in range(p.N):
        for _ in range(M):
            k1 = f(z, U[k], G[k])
            k2 = f(z + h / 2 * k1, U[k], G[k])
            k3 = f(z + h / 2 * k2, U[k], G[k])
            k4 = f(z + h * k3, U[k], G[k])
            z = z + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            err = max(err, np.abs(project(z[:14]) - z[14:]).max())
    same = np.abs(model.propagate(x0, U, G, s)[-1] - z[:14]).max()
    return err, same


def discrete_check(p, N, tf):
    L6, L5 = Lander(p, N, tf), Lander5(p, N, tf)
    x6, m6, st = solve_nlp(L6, L6.straight_line(p))
    val = lambda Ps: np.array([evaluate(q, x6) for q in Ps])
    ix = lambda Ps: [next(iter(q))[0] for q in Ps]
    x5 = np.zeros(L5.n)
    for k in range(N + 1):
        X6, X5 = L6.X[k], L5.X[k]
        R = val(X6["R"]).reshape(3, 3)
        x5[ix([X5["m"]])], x5[ix(X5["b"])], x5[ix(X5["W"])] = val([X6["m"]]), R[:, 0], R @ val(X6["w"])
        x5[ix(L5.r[k])], x5[ix(L5.v[k])] = val(L6.r[k]), val(L6.v[k])
        if k < N:
            T = R @ val(X6["T"])
            x5[ix(X5["a"])], x5[ix(X5["T"])], x5[ix([X5["G"]])] = val(X6["a"]), T, val([X6["G"]])
            x5[ix([X5["s"]])], x5[ix(X5["tau"])] = val(X6["T"])[0], np.cross(R[:, 0], T)
    eqv, _ = L5.violation(x5)
    eqr = max(abs(evaluate(P, x5)) for P in L5.eq_r)
    return st, m6, evaluate(L5.objective, x5), eqv, eqr


if __name__ == "__main__":
    d = np.load("results/baseline.npz")
    for M in (8, 64):
        model = Model(Params(substeps=M))
        for roll in (0.0, 1.0):
            x0 = d["X"][0].copy()
            x0[IQ] = [np.cos(roll / 2), np.sin(roll / 2), 0, 0]
            err, same = max_difference(model, x0, d["U"], d["G"], float(d["s"]))
            print(f"RK4 substeps {M}, initial roll {roll} rad: max |5-DOF - 6-DOF| = {err:.1e} "
                  f"(6-DOF part vs Model.propagate: {same:.1e})")
    st, m6, m5, eqv, eqr = discrete_check(Params(), 10, 7.5)
    print(f"\n6-DOF IPOPT optimum at N = 10, t_f = 7.5 ({st}, m_N = {m6:.6f}) mapped to 5-DOF: "
          f"m_N = {m5:.6f}, max equality error {eqv:.1e}, max redundant-equality error {eqr:.1e}")
