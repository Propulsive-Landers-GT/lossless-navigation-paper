"""Print the tables of RESULTS-FLAT.md from results/*_flat.json and results/audit_single_convex.json."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(__file__)
R = lambda name: json.load(open(os.path.join(HERE, '..', 'results', name)))
NAMES = {'B': 'B', 'S': 'S (SCvx)', 'Sh': 'S + hover arrival', 'F0': 'F without hover arrival', 'F': 'F',
         'Blat': 'B', 'Slat': 'S (SCvx)', 'Shlat': 'S + hover arrival', 'F10hard': 'F without hover arrival, 10 Hz',
         'F10': 'F, 10 Hz', 'F10own': 'F, 10 Hz, own t_f (+0.5 s)', 'F10own25': 'F, 10 Hz, own t_f (+0.25 s)',
         'Slat4': 'S (SCvx)', 'F5x4': 'F, 5 Hz'}
GROUPS = (('Repo protocol: 1 Hz replans, plans applied instantly, same t_f', ['B', 'S', 'Sh', 'F0', 'F']),
          ('Realistic compute: plans applied after their solver time, each planner at its sustainable rate',
           ['Blat', 'Slat', 'Shlat', 'F10hard', 'F10', 'F10own', 'F10own25']),
          ('Four times slower computer: every solver time multiplied by 4', ['Slat4', 'F5x4']))
PAIRS = (('F', 'S'), ('F', 'Sh'), ('F10', 'Slat'), ('F10', 'Shlat'), ('F10', 'S'), ('F10own25', 'Slat'), ('F5x4', 'Slat4'))
LAT = ('Blat', 'Slat', 'Shlat', 'Slat4')


def q(a, f='{:.2f}'):
    a = np.asarray(a, float)
    return ' / '.join(f.format(x) for x in (np.median(a), np.percentile(a, 95), a.max()))


def openloop():
    d = R('openloop_flat.json')
    print('\n### Open loop at tfB + 0.5 s\n')
    print('| scenario | t_f [s] | lower bound [kg] | B [kg] | S [kg] | F, one SOCP [kg] | F vs best of B, S | SOCPs B / S / F | solver time B / S / F [s] |')
    print('|---|---|---|---|---|---|---|---|---|')
    gaps, tB, tS, tF = [], [], [], []
    for r in d:
        a = r['tfB+0.5']
        best = min(a['B']['fuel'], a['S']['fuel'])
        gap = 100 * (a['F1']['fuel'] / best - 1)
        gaps.append(gap); tB.append(a['B']['solve_time']); tS.append(a['S']['solve_time']); tF.append(a['F1']['solve_time'])
        print(f"| {r['name'][:2]} | {a['B']['tf']:.2f} | {a['LB']['fuel']:.4f} | {a['B']['fuel']:.4f} | {a['S']['fuel']:.4f} | "
              f"{a['F1']['fuel']:.4f} | {gap:+.2f} % | {a['B']['n_solves']} / {a['S']['n_solves']} / 1 | "
              f"{a['B']['solve_time']:.2f} / {a['S']['solve_time']:.2f} / {a['F1']['solve_time']:.3f} |")
    print(f"\nF (one SOCP) vs best of B and S: mean {np.mean(gaps):+.2f} %, max {np.max(gaps):+.2f} %. "
          f"Median solver time: B {np.median(tB):.2f} s, S {np.median(tS):.2f} s, F {np.median(tF):.3f} s "
          f"(B/F = {np.median(tB)/np.median(tF):.0f}x, S/F = {np.median(tS)/np.median(tF):.0f}x).")
    g2 = [100 * (r['tfB+0.5']['F']['fuel'] / min(r['tfB+0.5']['B']['fuel'], r['tfB+0.5']['S']['fuel']) - 1) for r in d]
    print(f"F with 2 refinement passes: mean {np.mean(g2):+.2f} %, max {np.max(g2):+.2f} %, "
          f"SOCPs {[r['tfB+0.5']['F']['n_solves'] for r in d]}.")
    print(f"All certificates passed: B {all(r['tfB+0.5']['B']['cert'] for r in d)}, S {all(r['tfB+0.5']['S']['cert'] for r in d)}, "
          f"F {all(r['tfB+0.5']['F1']['cert'] for r in d)}.")
    print('\n### Minimum final time and fuel there\n')
    print('| scenario | min t_f: B [s] | min t_f: F [s] | difference [s] | fuel B at its min [kg] | fuel F at its min [kg] | F vs B |')
    print('|---|---|---|---|---|---|---|')
    for r in d:
        a = r['own_min']
        print(f"| {r['name'][:2]} | {r['tfB']:.2f} | {r['tfF']:.2f} | {r['tfF'] - r['tfB']:+.2f} | {a['B']['fuel']:.4f} | "
              f"{a['F']['fuel']:.4f} | {100 * (a['F']['fuel'] / a['B']['fuel'] - 1):+.2f} % |")
    print('\n### Open-loop replay: landing position error [m] under three plant models (plan at tfB + 0.5 s)\n')
    print('| scenario | B: own model (frozen J, L) | S: own model | F: own model (CoP) | B: plant table | S: plant table | F: plant table |')
    print('|---|---|---|---|---|---|---|')
    for r in d:
        a = r['tfB+0.5']
        print(f"| {r['name'][:2]} | {a['B']['replay_frozen']['dr']:.1e} | {a['S']['replay_frozen']['dr']:.1e} | {a['F1']['replay_cop_dr']:.1e} | "
              f"{a['B']['replay_table']['dr']:.3f} | {a['S']['replay_table']['dr']:.3f} | {a['F1']['replay_table_dr']:.3f} |")
    own = [r['tfB+0.5']['F1']['replay_cop_dr'] for r in d]
    print(f"\nF own-model replay: median {np.median(own):.1e} m, max {np.max(own):.1e} m; velocity max "
          f"{max(r['tfB+0.5']['F1']['replay_cop_dv'] for r in d):.1e} m/s.")
    tb = lambda k, kk: np.median([r['tfB+0.5'][k][kk]['dr'] if k != 'F1' else r['tfB+0.5']['F1']['replay_table_dr'] for r in d])
    print(f"Median plant-table replay error: B {tb('B', 'replay_table'):.3f} m, S {tb('S', 'replay_table'):.3f} m, F {tb('F1', None):.3f} m.")
    pk = lambda k: max(r['tfB+0.5']['F1'][k] for r in d)
    print(f"F plan peaks over the 8 scenarios: gimbal cone {pk('gimbal_cone_max_deg'):.1f} deg, gimbal rate {pk('gimbal_rate_max_dps'):.0f} deg/s, "
          f"throttle rate {pk('thrust_rate_max'):.0f} N/s, tilt {pk('tilt_max_deg'):.1f} deg, T in "
          f"[{min(r['tfB+0.5']['F1']['T_min'] for r in d):.0f}, {pk('T_max'):.0f}] N.")


def hop():
    d = R('hop_map_flat.json')
    print('\n### Pad-hop map (t_f = 4 s)\n')
    vs, ds = sorted({r['v0z'] for r in d}), sorted({r['d'] for r in d})
    print('| v0z [m/s] | ' + ' | '.join(f'd = {x:.0f} m' for x in ds) + ' |')
    print('|---|' + '---|' * len(ds))
    for v in vs:
        cells = []
        for x in ds:
            r = next(z for z in d if z['v0z'] == v and z['d'] == x)
            if r['F_feasible']:
                cells.append(f"flyable; F ✓ ({100 * (r['F_fuel'] / r['D_fuel'] - 1):+.2f} % fuel)")
            elif r['D_feasible']:
                cells.append(f"flyable; F needs t_f {r['F_min_tf']:.2f} s")
            else:
                cells.append(f"none found; F refuses (lands with t_f {r['F_min_tf']:.2f} s)")
        print(f'| {v} | ' + ' | '.join(cells) + ' |')
    print(f"\nF feasible where IPOPT found no flyable plan: {sum(r['F_feasible'] and not r['D_feasible'] for r in d)} of "
          f"{sum(not r['D_feasible'] for r in d)}. Flyable cells kept at t_f = 4 s: {sum(r['F_feasible'] and r['D_feasible'] for r in d)} of "
          f"{sum(r['D_feasible'] for r in d)}; the rest need {min(r['F_min_tf'] - 4 for r in d if r['D_feasible'] and not r['F_feasible']):.2f} to "
          f"{max(r['F_min_tf'] - 4 for r in d if r['D_feasible'] and not r['F_feasible']):.2f} s more.")


def mc(scen, title):
    d = R(f'mc_{scen}_flat.json')
    cases = sorted({r['case'] for r in d})
    print(f'\n### Closed loop: {title} ({len(cases)} cases)\n')
    for group, meths in GROUPS:
        if not any(x['method'] in meths for x in d):
            continue
        print(f'**{group}**\n')
        print('| planner | success | lateral error [cm] median / p95 / max | touchdown speed [m/s] median / p95 / max | tilt [deg] median / p95 / max | fuel at t_f [kg] mean | solver time per replan [ms] mean / max | SOCPs per replan mean / max | replans kept previous plan | t_f extended (runs) |')
        print('|---|---|---|---|---|---|---|---|---|---|')
        for m in meths:
            rr = [r for r in d if r['method'] == m]
            ok = [r for r in rr if 'failed' not in r]
            if not ok:
                continue
            ns = sum(r['success'] for r in ok)
            rep = [r for r in ok if r.get('solve_replan_mean') is not None]
            nrep = sum(r['n_replans'] - 1 for r in ok)
            print(f"| {NAMES[m]} | {ns}/{len(rr)} | {q([100 * r['pos_err'] for r in ok], '{:.1f}')} | {q([r['speed'] for r in ok])} | "
                  f"{q([r['tilt_deg'] for r in ok])} | {np.mean([r['fuel_tf'] for r in ok]):.3f} | "
                  f"{1e3 * np.average([r['solve_replan_mean'] for r in rep], weights=[r['n_replans'] - 1 for r in rep]):.0f} / {1e3 * max(r['solve_replan_max'] for r in rep):.0f} | "
                  f"{(sum(r['n_socp'] for r in ok) - 0) / sum(r['n_replans'] for r in ok):.1f} / {max(r['n_socp_replan_max'] for r in ok)} | "
                  f"{sum(r['n_kept_previous'] for r in ok)}/{nrep} | {sum(r['tf_ext'] > 0 for r in ok)} |")
        print()
    print('**Actuator use and first plan**\n')
    print('| planner | gimbal travel [deg] mean | gimbal RMS [deg] mean | throttle travel [N] mean | throttle saturated (time) | gimbal saturated (time) | first plan: solver time [s] mean / max | time-of-flight search [s] mean |')
    print('|---|---|---|---|---|---|---|---|')
    for m in [x for _, g in GROUPS for x in g]:
        ok = [r for r in d if r['method'] == m and 'failed' not in r]
        if not ok:
            continue
        ts = np.mean([(r['t_tfF'] if m.startswith('F10own') else r['t_tfB']) or np.nan for r in ok])
        lab = NAMES[m] + (' (latency)' if m in LAT else '') + (' (4x slower computer)' if m in ('Slat4', 'F5x4') else '')
        print(f"| {lab} | {np.mean([r['gimbal_travel_deg'] for r in ok]):.0f} | {np.mean([r['gimbal_rms_deg'] for r in ok]):.2f} | "
              f"{np.mean([r['thrust_travel'] for r in ok]):.0f} | {100 * np.mean([r['thrust_sat_frac'] for r in ok]):.1f} % | "
              f"{100 * np.mean([r['gimbal_sat_frac'] for r in ok]):.1f} % | {np.mean([r['solve_first'] for r in ok]):.2f} / {max(r['solve_first'] for r in ok):.2f} | {ts:.1f} |")
    # paired comparisons
    by = {(r['case'], r['method']): r for r in d if 'failed' not in r}
    for a, b in PAIRS:
        pairs = [(by[(c, a)], by[(c, b)]) for c in cases if (c, a) in by and (c, b) in by]
        if not pairs:
            continue
        w_e = sum(x['pos_err'] < y['pos_err'] for x, y in pairs)
        w_v = sum(x['speed'] < y['speed'] for x, y in pairs)
        df = np.mean([100 * (x['fuel_tf'] / y['fuel_tf'] - 1) for x, y in pairs])
        print(f"\nPaired, {NAMES[a]} vs {NAMES[b]}{' (latency)' if b in LAT else ''}: smaller lateral error in {w_e}/{len(pairs)} cases, "
              f"lower touchdown speed in {w_v}/{len(pairs)}, fuel {df:+.2f} % on average.")
    fails = [(r['case'], r['method'], round(r.get('speed', -1), 2), round(r.get('pos_err', -1), 2), round(r.get('tilt_deg', -1), 1), r.get('failed'))
             for r in d if not r.get('success')]
    print('\nFailures (case, method, speed, lateral, tilt, note):', fails)
    pk = [r['plan_peaks'] for r in d if r['method'].startswith('F') and r.get('plan_peaks')]
    if pk:
        print(f"F plan peaks over all replans: gimbal cone {max(p['gimbal_cone_max_deg'] for p in pk):.1f} deg, gimbal rate "
              f"{max(p['gimbal_rate_max_dps'] for p in pk):.0f} deg/s, throttle rate {max(p['thrust_rate_max'] for p in pk):.0f} N/s, "
              f"T in [{min(p['T_min'] for p in pk):.0f}, {max(p['T_max'] for p in pk):.0f}] N.")
    cr = [r['cert_rate'] for r in d if r['method'].startswith('F') and 'failed' not in r]
    if cr:
        print(f"F: share of replans that returned a plan and passed the dense-grid limit check: {100 * np.mean(cr):.1f} %.")


def audit():
    d = R('audit_single_convex.json')
    print('\n### Relaxation-based single convex program (rate-limited LCvx with attitude boundary conditions), first plans\n')
    print('| scenario | cases | program feasible | of those, relaxation tight | infeasible cases: extra flight time needed [s] median / max | fuel vs planner F where both feasible | planner F feasible |')
    print('|---|---|---|---|---|---|---|')
    for scen in ('inair', 'hop'):
        rr = [r for r in d if r['scenario'] == scen]
        ok = [r for r in rr if 'fuel' in r]
        bad = [r['min_tf'] - r['tf'] for r in rr if 'fuel' not in r and r.get('min_tf')]
        both = [100 * (r['fuel'] / r['F_fuel'] - 1) for r in ok if r.get('F_fuel')]
        print(f"| {scen} | {len(rr)} | {len(ok)} | {sum(r['n_lossy'] == 0 for r in ok)} | "
              f"{(f'{np.median(bad):.2f} / {np.max(bad):.2f}' if bad else '-')} | "
              f"{(f'{np.mean(both):+.2f} %' if both else '-')} | {sum(r['F_status'] != 'infeasible' for r in rr)} |")
    ok = [r for r in d if 'fuel' in r]
    if ok:
        print(f"\nWhere feasible: gimbal angle a gimballed vehicle needs to follow the planned thrust direction, median / max "
              f"{np.median([r['gimbal_needed_max_deg'] for r in ok]):.1f} / {max(r['gimbal_needed_max_deg'] for r in ok):.1f} deg; "
              f"largest mid-flight offset between the planned path and the CG, median / max "
              f"{np.median([r['cg_offset_midflight_max'] for r in ok]):.2f} / {max(r['cg_offset_midflight_max'] for r in ok):.2f} m; "
              f"landing-point shift from the unplanned initial body rate, median / max "
              f"{np.median([r['cg_drift_from_initial_rate'] for r in ok]):.2f} / {max(r['cg_drift_from_initial_rate'] for r in ok):.2f} m.")
    for f in ('mc_inair.json', 'mc_hop.json'):
        try:
            rr = [x for x in R(f) if x['method'] == 'C' and 'tight_min' in x]
            print(f"Earlier closed-loop runs of the same construction without the boundary conditions ({f}): "
                  f"{sum(x['tight_min'] < 0.999 for x in rr)}/{len(rr)} runs produced at least one replan whose relaxation was not tight "
                  f"(smallest ||T||/Gamma = {min(x['tight_min'] for x in rr):.2f}).")
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    which = sys.argv[1:] or ['openloop', 'hop', 'inair', 'hopmc', 'audit']
    for w in which:
        try:
            {'openloop': openloop, 'hop': hop, 'inair': lambda: mc('inair', 'in-air descents'),
             'hopmc': lambda: mc('hop', 'pad hops'), 'audit': audit}[w]()
        except FileNotFoundError as e:
            print(f'[{w}: {e.filename} not found]')
