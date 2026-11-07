"""Analytic lower bound of [proof] (BOARD 2026-11-06 23:30, "ball bound"):
for any admissible M1 trajectory and any tau with delta + omega*max(tau, tf-tau) <= pi/2,
    |Dv| >= <Dv, b(tau)> >= G(tau) := int_0^tf a1(s) cos(delta + omega|s - tau|) ds,
so dist(M, R) >= max_tau G(tau) - |M|.   Compared here with the multistart NLP distance (an upper bound
on the true distance since the discretization is an inner approximation)."""
import json, sys
import numpy as np
import models


def G(P, tf, tau, n=20001):
    s = np.linspace(0, tf, n)
    a1 = P["rho1"] / (P["m0"] - P["alpha"] * P["rho1"] * s)
    return np.trapezoid(a1 * np.cos(P["delta"] + P["omega"] * np.abs(s - tau)), s)


def ball_bound(P, tf, tent=False):
    ex = models.extreme_arcs_M1_cont(P, tf, tent=tent)
    Mn = abs(ex["Mz"])
    taus = np.linspace(0, tf, 401)
    ok = P["delta"] + P["omega"] * np.maximum(taus, tf - taus) <= np.pi / 2 + 1e-12
    if not ok.any():
        return np.nan
    return max(G(P, tf, t) for t in taus[ok]) - Mn


if __name__ == "__main__":
    D2R = np.pi / 180
    res = json.load(open("results/t1_base.json"))
    rows = []
    for name, sw in res["sweeps"].items():
        for i, r in enumerate(sw):
            kw = dict(omega=r["omega_deg"] * D2R, delta=r["delta_deg"] * D2R, rho1=r["ratio"] * 1000.0)
            if name == "alpha":
                kw["alpha"] = [0.0, 5.66e-4, 2e-3, 5e-3][i]
            P = models.gtpl(**kw)
            lb = ball_bound(P, r["tf"])
            rows.append((name, r["omega_deg"], r["tf"], r["delta_deg"], r["ratio"], lb, r["dist"]))
            print(f"{name:9s} w={r['omega_deg']:6.1f} tf={r['tf']:6.3f} delta={r['delta_deg']:5.1f} ratio={r['ratio']:.2f}  "
                  f"ball-bound LB={lb:8.4f}  NLP dist={r['dist']:8.4f}  ok={lb <= r['dist'] + 1e-6}")
    bad = [r for r in rows if r[5] > r[6] + 1e-6]
    print("violations (LB > NLP):", len(bad))
