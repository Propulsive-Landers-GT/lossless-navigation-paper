"""Turn results/*.json into markdown tables (stdout) and plots (results/*.png)."""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, '..', 'results')
COL = {'B': '#2a78d6', 'A': '#eb6834', 'C': '#1baf7a', 'D': '#eda100', 'LB': '#8a8985'}
NAME = {'A': 'A: flight 3DOF LCvx', 'B': 'B: attitude-aware (recommended)', 'C': 'C: 3DOF + rate limits'}
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True,
                     'grid.color': '#e4e3df', 'grid.linewidth': 0.6, 'axes.edgecolor': '#8a8985',
                     'axes.labelcolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e'})


def load(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else None


def pct(a, b):
    return 100 * (a - b) / b


def openloop():
    ol = load('openloop.json')
    if not ol:
        return
    print('\n### Open loop (same t_f = B\'s minimum feasible t_f)\n')
    print('| scenario | t_f [s] | LB (3DOF relax.) | B fuel [kg] | D best [kg] | B − D | B − LB | B iters / conic solves / solver s | B cert | C at t_f | C own t_f / fuel | A t_f / fuel | A min delivered thrust [N] | A dir. accel / available |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    gapsD, gapsLB = [], []
    for r in ol:
        x = r['tfB']
        B, D = x['B'], x['D']
        gD = pct(B['fuel'], D['best']) if D['best'] else np.nan
        gL = pct(B['fuel'], x['LB'])
        gapsD.append(gD)
        gapsLB.append(gL)
        C = x['C']
        cs = 'infeasible' if not np.isfinite(C['fuel']) else f"{C['fuel']:.3f}"
        A = r['A']
        print(f"| {r['name']} | {x['tf']:.2f} | {x['LB']:.4f} | {B['fuel']:.4f} | {D['best']:.4f} | {gD:+.3f}% | {gL:+.2f}% | "
              f"{B['iters']} / {B['n_solves']} / {B['solve_time']:.2f} | {'PASS' if B['cert'] else 'FAIL'} | {cs} | "
              f"{r['C_own']['tf']:.2f} / {r['C_own']['fuel']:.3f} ({pct(r['C_own']['fuel'], B['fuel']):+.1f}%) | "
              f"{A['tf']:.1f} / {A['fuel']:.3f} | {A['T_delivered_min']:.0f} | {A['dir_acc_max'] / A['alpha_available']:.1f}× |")
    print(f"\nB − D: max {np.nanmax(gapsD):+.3f}%, mean {np.nanmean(gapsD):+.3f}%;  B − LB: max {np.max(gapsLB):.2f}%, mean {np.mean(gapsLB):.2f}%")
    print('\n### Open loop at t_f + 0.5 s\n')
    print('| scenario | LB | B | D | B − D | B − LB | B0 (warm start + 1 inner, no iterations) | C |')
    print('|---|---|---|---|---|---|---|---|')
    for r in ol:
        x = r['tfB+0.5']
        B, D, B0, C = x['B'], x['D'], x['B0'], x['C']
        b0 = f"{B0['fuel']:.4f} ({'cert' if B0['status'] == 'certified-inner' else 'not feasible: dv=%.2f m/s' % B0['defect']['v']})"
        cs = 'infeasible' if not np.isfinite(C['fuel']) else f"{C['fuel']:.4f}"
        print(f"| {r['name']} | {x['LB']:.4f} | {B['fuel']:.4f} | {D['best']:.4f} | {pct(B['fuel'], D['best']):+.3f}% | "
              f"{pct(B['fuel'], x['LB']):+.2f}% | {b0} | {cs} |")
    # D starts
    print('\nD multistart (t_f = B min): converged starts / best start per scenario: ' + '; '.join(
        f"{r['name'].split()[0]}: {sum(q['ok'] for q in r['tfB']['D']['runs'])}/{len(r['tfB']['D']['runs'])} ({r['tfB']['D']['best_start']})"
        for r in ol))
    # plot
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    names = [r['name'].split()[0] for r in ol]
    xs = np.arange(len(ol))
    w = 0.2
    series = [('LB', [r['tfB']['LB'] for r in ol], '3DOF lower bound'),
              ('B', [r['tfB']['B']['fuel'] for r in ol], 'B (certified)'),
              ('D', [r['tfB']['D']['best'] for r in ol], 'D (IPOPT best)'),
              ('C', [r['C_own']['fuel'] for r in ol], 'C (own min t_f)')]
    for j, (k, vals, lab) in enumerate(series):
        ax.bar(xs + (j - 1.5) * w, vals, w * 0.9, color=COL[k], label=lab)
    ax.set_xticks(xs, names)
    ax.set_ylabel('propellant used [kg]')
    ax.set_ylim(2.5, None)
    ax.legend(ncol=4, frameon=False, loc='upper left', bbox_to_anchor=(0, 1.15))
    ax.set_title('Open-loop fuel, in-air descents (A omitted: its plans are not flyable)', loc='left', pad=22)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'openloop_fuel.png'), dpi=150)


def mc(scn):
    d = load(f'mc_{scn}.json')
    if not d:
        return
    cases = sorted({r['case'] for r in d})
    print(f'\n### Closed-loop Monte Carlo: {scn} ({len(cases)} cases)\n')
    print('| method | success | touched | speed at TD [m/s] med / p95 / max | lateral err [m] med / p95 / max | tilt at TD [deg] p95 | max tilt [deg] p95 | fuel to TD [kg] mean | fuel at t_f mean | thrust-sat time | gimbal-sat time | plans certified | replan solver time mean / max [s] | replan wall (Python) mean [s] |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for m in ['A', 'B', 'C']:
        rs = [r for r in d if r['method'] == m and 'speed' in r]
        nf = len([r for r in d if r['method'] == m and 'failed' in r])
        if not rs:
            continue
        g = lambda k: np.array([r[k] for r in rs], float)
        sp, pe, ti, mt = g('speed'), g('pos_err'), g('tilt_deg'), g('max_tilt_deg')
        print(f"| {m} | {np.mean(g('success')) * 100:.0f}% ({int(g('success').sum())}/{len(rs) + nf}) | {np.mean(g('touched')) * 100:.0f}% | "
              f"{np.median(sp):.2f} / {np.percentile(sp, 95):.2f} / {sp.max():.2f} | {np.median(pe):.2f} / {np.percentile(pe, 95):.2f} / {pe.max():.2f} | "
              f"{np.percentile(ti, 95):.1f} | {np.percentile(mt, 95):.1f} | {g('fuel').mean():.3f} | {g('fuel_tf').mean():.3f} | "
              f"{g('thrust_sat_frac').mean() * 100:.1f}% | {g('gimbal_sat_frac').mean() * 100:.1f}% | {g('cert_rate').mean() * 100:.0f}% | "
              f"{np.nanmean(g('solve_mean')):.3f} / {np.nanmax(g('solve_max')):.3f} | {g('wall_mean').mean():.2f} |")
        if nf:
            print(f'|  | ({nf} runs without a feasible t_f) |')
    if 'B' in {r['method'] for r in d}:
        rb = [r for r in d if r['method'] == 'B' and 'speed' in r]
        print(f"\nB: t_f extensions used in {sum(r['tf_ext'] > 0 for r in rb)}/{len(rb)} runs (mean {np.mean([r['tf_ext'] for r in rb]):.2f} s); "
              f"first plan certified in {sum(r['cert_first'] for r in rb)}/{len(rb)}; min altitude margin {min(r['min_alt_margin'] for r in rb):.3f} m; "
              f"replans needing a fallback (continuation or t_f extension): {sum(r.get('n_fallback', 0) for r in rb)}/{sum(r['n_replans'] - 1 for r in rb)}; "
              f"mean fuel overrun at t_f vs first plan {np.mean([100 * (r['fuel_tf'] / r['plan_fuel0'] - 1) for r in rb]):+.1f}%")
    fig, ax = plt.subplots(figsize=(5.5, 3.6))
    for m in ['A', 'C', 'B']:
        rs = [r for r in d if r['method'] == m and 'speed' in r]
        if rs:
            ax.scatter([r['pos_err'] for r in rs], [r['speed'] for r in rs], s=22, color=COL[m], label=NAME[m],
                       edgecolor='white', linewidth=0.8, zorder=3)
    ax.axhline(1.0, color='#8a8985', lw=0.8, ls='--')
    ax.axvline(1.0, color='#8a8985', lw=0.8, ls='--')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('lateral touchdown error [m]')
    ax.set_ylabel('touchdown speed [m/s]')
    ax.set_title(f'Closed-loop touchdowns ({scn}); dashed = 1 m, 1 m/s', loc='left')
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, f'mc_{scn}_touchdown.png'), dpi=150)


def hop():
    d = load('hop_map.json')
    if not d:
        return
    print('\n### Pad hop feasibility map (t_f = 4 s, launch from the pad with upward speed v0z, land d metres away)\n')
    print('| v0z [m/s] | d [m] | A (flight LCvx) | 3DOF relaxation | B | D (IPOPT, 2 starts) | B fuel | D fuel |')
    print('|---|---|---|---|---|---|---|---|')
    for r in d:
        a = r['A_status'] + ('' if r['A_Tdel_min'] is None else f" (min T {r['A_Tdel_min']:.0f} N)")
        bd = r['B'] if r['B'] == 'certified-inner' else f"no plan (dv {r['B_defect']['v']:.2f} m/s, tilt {np.degrees(r['B_defect']['tilt']):.1f}°)"
        print(f"| {r['v0z']} | {r['d']} | {a} | {r['relax3']} | {bd} | {'feasible' if r['D_feasible'] else 'no solution'} | "
              f"{r['B_fuel']:.3f} | {'-' if r['D_fuel'] is None else '%.3f' % r['D_fuel']} |")


def example():
    """Plan profiles for scenario S2: thrust direction demanded by A versus B's flyable attitude."""
    sys.path.insert(0, os.path.join(HERE, '..'))
    import warnings
    warnings.filterwarnings('ignore')
    from gtpl_guidance.params import default_vehicle, default_config
    from gtpl_guidance.lcvx3dof import tf_search_A
    from gtpl_guidance.aacg import AACG
    from gtpl_guidance.rotations import gimbal_angles
    veh, cfg = default_vehicle(), default_config()
    r0, v0, tgt = np.array([10, 20, 50.]), np.zeros(3), np.array([0, 0, 1.5])
    pA = tf_search_A(r0, v0, 80.0, tgt, veh)
    pB = AACG(veh, cfg).plan(r0, v0, 80.0, np.eye(3), np.zeros(3), tgt, 8.40)
    fig, axs = plt.subplots(3, 1, figsize=(7, 6.2), sharex=True)
    tA = pA.t[:-1]
    TA = pA.T
    tiltA = np.degrees(np.arccos(TA[:, 2] / np.linalg.norm(TA, axis=1)))
    tB = pB.grid.ts
    tiltB = np.degrees(np.arccos(np.clip(pB.att['b'][:, 2], -1, 1)))
    axs[0].step(tA, tiltA, where='post', color=COL['A'], lw=1.6, label='A: thrust-direction tilt (no body model)')
    axs[0].plot(tB, tiltB, color=COL['B'], lw=2, label='B: body tilt')
    axs[0].set_ylabel('tilt [deg]')
    axs[0].legend(frameon=False, fontsize=8)
    axs[1].step(tA, np.linalg.norm(TA, axis=1), where='post', color=COL['A'], lw=1.6, label='A: delivered |T|')
    axs[1].plot(tB, np.linalg.norm(pB.T_body, axis=1), color=COL['B'], lw=2, label='B: |T|')
    axs[1].axhline(veh.T_min, color='#8a8985', ls='--', lw=0.8)
    axs[1].axhline(veh.T_max, color='#8a8985', ls='--', lw=0.8)
    axs[1].set_ylabel('thrust [N]')
    axs[1].legend(frameon=False, fontsize=8)
    ang = np.degrees(np.array([gimbal_angles(t) for t in pB.T_body]))
    axs[2].plot(tB, ang[:, 0], color=COL['B'], lw=2, label='B: gimbal θ')
    axs[2].plot(tB, ang[:, 1], color=COL['C'], lw=2, label='B: gimbal φ')
    axs[2].axhline(15, color='#8a8985', ls='--', lw=0.8)
    axs[2].axhline(-15, color='#8a8985', ls='--', lw=0.8)
    axs[2].set_ylabel('gimbal [deg]')
    axs[2].set_xlabel('time [s]')
    axs[2].legend(frameon=False, fontsize=8)
    axs[0].set_title('S2, start (10, 20, 50) m: plan profiles of A and B', loc='left')
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'example_S2_profiles.png'), dpi=150)


if __name__ == '__main__':
    openloop()
    hop()
    for s in ('inair', 'hop'):
        mc(s)
    if '--example' in sys.argv:
        example()
