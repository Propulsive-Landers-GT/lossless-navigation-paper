"""Print the markdown tables for RESULTS-SCVX.md from results/{openloop_scvx,hop_map_scvx,mc_inair_scvx,mc_hop_scvx}.json."""
import json
import os

import numpy as np

R = os.path.join(os.path.dirname(__file__), '..', 'results')


def load(name):
    p = os.path.join(R, name)
    return json.load(open(p)) if os.path.exists(p) else None


def openloop():
    d = load('openloop_scvx.json')
    print('### Open loop, 8 scenarios x 2 final times (16 problems)\n')
    print('| scenario | t_f [s] | D best [kg] | B [kg] | S (3DOF start) [kg] | S (straight-line start) [kg] | B SOCPs / solver s | S-3DOF SOCPs / solver s | S-line SOCPs / solver s |')
    print('|---|---|---|---|---|---|---|---|---|')
    agg = {k: dict(gap=[], ns=[], st=[], cert=0, ff=[]) for k in ('B', 'S_3dof', 'S_linear')}
    for row in d:
        for tag in ('tfB', 'tfB+0.5'):
            x = row[tag]
            D = x['D']
            cells = []
            for k in ('B', 'S_3dof', 'S_linear'):
                y = x[k]
                agg[k]['gap'].append(100 * (y['fuel'] - D) / D)
                agg[k]['ns'].append(y['n_solves'])
                agg[k]['st'].append(y['solve_time'])
                agg[k]['cert'] += bool(y['cert'])
                agg[k]['ff'].append(y['first_feasible_iter'])
                cells.append(f"{y['fuel']:.4f} ({100 * (y['fuel'] - D) / D:+.3f} %){'' if y['cert'] else ' FAIL'}")
            work = [f"{x[k]['n_solves']} / {x[k]['solve_time']:.2f}" for k in ('B', 'S_3dof', 'S_linear')]
            print(f"| {row['name'].split()[0]}{' +0.5' if tag != 'tfB' else ''} | {x['tf']:.2f} | {D:.4f} | " + ' | '.join(cells + work) + ' |')
    print('\n**Aggregate (16 problems)**\n')
    print('| | certified | fuel vs IPOPT: mean / max | SOCPs: median / max | Clarabel time [s]: median / max |')
    print('|---|---|---|---|---|')
    for k, lab in (('B', 'B'), ('S_3dof', 'S, 3DOF start'), ('S_linear', 'S, straight-line start')):
        a = agg[k]
        print(f"| {lab} | {a['cert']}/16 | {np.mean(a['gap']):+.4f} % / {np.max(a['gap']):+.4f} % | "
              f"{int(np.median(a['ns']))} / {max(a['ns'])} | {np.median(a['st']):.2f} / {max(a['st']):.2f} |")
    return d


def hop():
    d = load('hop_map_scvx.json')
    if d is None:
        return
    print('\n### Pad-hop map (20 cells, t_f = 4 s)\n')
    print('| | agrees with IPOPT on feasibility | certified where feasible (9 cells) | SOCPs, feasible cells: median / max | SOCPs, infeasible cells: median / max | solver time, all cells: total [s] |')
    print('|---|---|---|---|---|---|')
    for k, lab in (('B', 'B'), ('S_3dof', 'S, 3DOF start'), ('S_linear', 'S, straight-line start')):
        agree = sum((r[k]['cert']) == r['D_feasible'] for r in d)
        feas = [r for r in d if r['D_feasible']]
        inf = [r for r in d if not r['D_feasible']]
        nsf = [r[k]['n_solves'] for r in feas]
        nsi = [r[k]['n_solves'] for r in inf]
        print(f"| {lab} | {agree}/20 | {sum(r[k]['cert'] for r in feas)}/{len(feas)} | {int(np.median(nsf))} / {max(nsf)} | "
              f"{int(np.median(nsi))} / {max(nsi)} | {sum(r[k]['solve_time'] for r in d):.1f} |")
    fb = [abs(r['B']['fuel'] - r['S_3dof']['fuel']) / r['D_fuel'] * 100 for r in d if r['D_feasible']]
    print(f"\nWhere feasible, B and S fuel differ by at most {max(fb):.3f} %.")


def mc(sc):
    d = load(f'mc_{sc}_scvx.json')
    if d is None:
        return
    print(f'\n### Closed loop, {sc} ({len(set(r["case"] for r in d))} cases)\n')
    print('| method | success | touchdown speed [m/s] median / p95 / max | lateral error [m] median / p95 / max | fuel at t_f [kg] mean | flown plans certified | replans needing continuation or t_f extension | solver time per replan [s] mean / max |')
    print('|---|---|---|---|---|---|---|---|')
    for m in ('B', 'S'):
        rs = [r for r in d if r['method'] == m and 'failed' not in r]
        nf = [r for r in d if r['method'] == m and 'failed' in r]
        n = len(rs) + len(nf)
        sp = np.array([r['speed'] for r in rs])
        pe = np.array([r['pos_err'] for r in rs])
        succ = sum(bool(r['success']) for r in rs)
        fuel = np.mean([r['fuel'] for r in rs])
        cert = np.mean([r['cert_rate'] for r in rs])
        nrep = sum(r['n_replans'] - 1 for r in rs)
        nfb = sum(r['n_fallback'] for r in rs)
        sm = np.mean([r['solve_mean'] for r in rs])
        sx = np.max([r['solve_max'] for r in rs])
        q = lambda a: f"{np.median(a):.2f} / {np.percentile(a, 95):.2f} / {a.max():.2f}"
        print(f"| {m} | {100 * succ / n:.0f} % ({succ}/{n}) | {q(sp)} | {q(pe)} | {fuel:.3f} | {100 * cert:.0f} % | "
              f"{nfb}/{nrep} ({100 * nfb / max(nrep, 1):.0f} %) | {sm:.2f} / {sx:.2f} |")
    by = {}
    for r in d:
        if 'failed' not in r:
            by.setdefault(r['case'], {})[r['method']] = r
    both = [v for v in by.values() if 'B' in v and 'S' in v]
    dfuel = [100 * (v['S']['fuel'] - v['B']['fuel']) / v['B']['fuel'] for v in both]
    print(f"\nPaired over {len(both)} cases: S fuel minus B fuel, mean {np.mean(dfuel):+.2f} % (range {min(dfuel):+.2f} to {max(dfuel):+.2f} %); "
          f"touchdown speed lower for S in {sum(v['S']['speed'] < v['B']['speed'] for v in both)}/{len(both)} cases.")


if __name__ == '__main__':
    openloop()
    hop()
    mc('inair')
    mc('hop')
