"""Figure for RESULTS-FLAT.md: touchdown lateral error vs touchdown speed, per planner, with computation time counted.

Usage: .venv/bin/python scripts/plot_flat.py  -> results/mc_flat_touchdown.png
"""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(__file__)
INK, INK2, MUTED, GRID, AXIS, SURF = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#fcfcfb'
SERIES = [('Slat', 'SCvx', '#2a78d6', 'o'), ('Blat', 'Planner B', '#eb6834', 's'), ('F10plainown', 'Landing algorithm (F), 10 Hz', '#1baf7a', '^')]


def main():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), sharey=True, facecolor=SURF)
    for ax, (scen, title) in zip(axes, (('inair', 'In-air descents (40 cases)'), ('hop', 'Pad hops (30 cases)'))):
        d = json.load(open(os.path.join(HERE, '..', 'results', f'mc_{scen}_flat.json')))
        ax.set_facecolor(SURF)
        for key, name, col, mk in SERIES:
            rr = [r for r in d if r['method'] == key and 'failed' not in r]
            x = np.maximum([100 * r['pos_err'] for r in rr], 0.02)
            y = [r['speed'] for r in rr]
            ax.scatter(x, y, s=34, marker=mk, color=col, edgecolor=SURF, linewidth=0.8, zorder=3,
                       label=f'{name}: median {np.median(x):.1f} cm, {np.median(y):.2f} m/s')
            ax.plot([np.median(x)] * 2, [0, 1.0], color=col, lw=1.2, alpha=0.55, zorder=2)
        ax.axhline(1.0, color=AXIS, lw=1, ls=(0, (4, 3)), zorder=1)
        ax.text(55, 1.03, 'success limit 1 m/s', fontsize=8, color=MUTED, va='bottom', ha='right')
        ax.legend(loc='upper left', frameon=False, fontsize=8.5, labelcolor=INK2, handletextpad=0.3, borderaxespad=0.2)
        ax.set_xscale('log')
        ax.set_xlim(0.018, 60)
        ax.set_ylim(0, 2.0)
        ax.set_xticks([0.1, 1, 10])
        ax.set_xticklabels(['0.1', '1', '10'])
        ax.set_xlabel('lateral error at touchdown [cm]', color=INK2, fontsize=9.5)
        ax.set_title(title, color=INK, fontsize=10.5, loc='left', pad=8)
        ax.grid(True, which='major', color=GRID, lw=0.8, zorder=0)
        ax.tick_params(colors=MUTED, labelsize=9, length=0)
        for s in ('top', 'right', 'left'):
            ax.spines[s].set_visible(False)
        ax.spines['bottom'].set_color(AXIS)
    axes[0].set_ylabel('touchdown speed [m/s]', color=INK2, fontsize=9.5)
    fig.suptitle('Touchdown accuracy with each plan applied after its solver time (vertical lines: median lateral error)',
                 x=0.012, ha='left', fontsize=11.5, color=INK, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = os.path.join(HERE, '..', 'results', 'mc_flat_touchdown.png')
    fig.savefig(out, dpi=170, facecolor=SURF)
    print(out)


if __name__ == '__main__':
    main()
