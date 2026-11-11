"""Figures for the AIAA student-conference version of the paper.

AIAA figure rules followed here: no background, borders or outlines; no caption inside the figure; axis labels in words
with units after a comma; all text at least 8 pt at the printed size (figures are saved at their printed size).

Usage (from this directory):  ../../solver/.venv/bin/python make_figures.py
Reads ../../solver/results/mc_{inair,hop}_flat.json and plans one example with the solver package.
"""
import json
import os
import sys
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SOLVER = os.path.join(HERE, '..', '..', 'solver')
sys.path.insert(0, SOLVER)
warnings.filterwarnings('ignore')

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['STIXGeneral', 'Times New Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 8.5, 'axes.labelsize': 8.5, 'xtick.labelsize': 8,
                     'ytick.labelsize': 8, 'legend.fontsize': 8, 'axes.linewidth': 0.6, 'savefig.transparent': True})
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#d9d8d2'
BLUE, AQUA = '#2a78d6', '#1baf7a'      # validated pair (dataviz palette slots 1 and 3); markers also differ


def clean(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2.5, width=0.6, colors=INK)
    ax.grid(True, color=GRID, lw=0.5, zorder=0)
    ax.set_axisbelow(True)


def fig_schematic():
    """Vehicle geometry: gimbal pivot, center of mass, center of percussion, thrust decomposition."""
    fig, ax = plt.subplots(figsize=(3.4, 3.2))
    th = np.radians(14.0)                                  # body tilt
    b = np.array([np.sin(th), np.cos(th)])
    n = np.array([np.cos(th), -np.sin(th)])
    cg = np.array([0.0, 0.0])
    L, eps, half_w, top = 0.59, 1.35, 0.17, 1.72
    piv, cop, nose = cg - L * b, cg + eps * b, cg + top * b
    body = Polygon([piv - half_w * n, piv + half_w * n, nose + half_w * n, nose - half_w * n], closed=True,
                   fc='#eeeeea', ec=INK, lw=0.8, zorder=1)
    ax.add_patch(body)
    ax.plot([piv[0], nose[0] + 0.4 * b[0]], [piv[1], nose[1] + 0.4 * b[1]], color=MUTED, lw=0.6, ls=(0, (4, 3)), zorder=2)
    # thrust at the pivot (force on the vehicle), split into its axial and lateral parts; gimbal angle exaggerated
    mu = np.radians(28.0)
    Ta, Tp = 0.30 * b, 0.30 * np.tan(mu) * n

    def arrow(p, d, col, lw=1.2):
        ax.add_patch(FancyArrowPatch(p, p + d, arrowstyle='-|>', mutation_scale=6, color=col, lw=lw, zorder=4,
                                     shrinkA=0, shrinkB=0))
    arrow(piv, Ta, BLUE)
    arrow(piv + Ta, Tp, BLUE)
    arrow(piv, Ta + Tp, INK, 1.5)
    ax.plot(*cg, 'o', color=INK, ms=4.5, zorder=5)
    ax.plot(*piv, 's', color=INK, ms=4, zorder=5)
    ax.plot(*cop, 'o', mfc='white', mec=INK, mew=1.1, ms=5.5, zorder=5)
    off = 0.40 * n
    for p, q, lab in ((piv, cg, r'$L$'), (cg, cop, r'$\varepsilon$')):
        ax.annotate('', xy=q - off, xytext=p - off, arrowprops=dict(arrowstyle='<->', color=MUTED, lw=0.6, shrinkA=0, shrinkB=0))
        m = 0.5 * (p + q) - off - 0.12 * n
        ax.text(m[0], m[1], lab, ha='center', va='center', fontsize=9.5, color=INK)
    T = dict(fontsize=8.5, color=INK)
    lx = 0.62                                              # common left edge of the right-hand labels
    for p, lab in ((cop, 'center of percussion, $y$'), (cg, 'center of mass, $r$'), (piv, 'gimbal pivot')):
        ax.plot([p[0] + 0.07, lx - 0.04], [p[1], p[1]], color=MUTED, lw=0.5, zorder=3)
        ax.text(lx, p[1], lab, va='center', **T)
    ax.text(*(nose + 0.46 * b + 0.07 * n), 'body axis, $b$', va='center', **T)
    ax.text(*(piv + 0.55 * Ta - 0.07 * n), '$T_a b$', ha='right', va='center', **T)
    ax.text(*(piv + Ta + 0.5 * Tp + 0.08 * b), r'$T_\perp$', ha='center', va='bottom', **T)
    ax.text(*(piv + Ta + Tp + 0.05 * n - 0.06 * b), '$T$', va='center', ha='left', **T)
    ax.set_aspect('equal')
    ax.set_xlim(-0.8, 2.25)
    ax.set_ylim(-0.75, 2.2)
    ax.axis('off')
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(os.path.join(HERE, 'figures', 'schematic.pdf'))
    plt.close(fig)


def fig_example():
    """One plan from one convex program: throttle, tilt and gimbal angle, with the planning limits."""
    from gtpl_guidance.landing import LandingGuidance
    target = np.array([0.0, 0.0, 1.5])
    x0 = np.array([10.0, 20.0, 50.0, 0.0, 0.0, -3.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 79.0])
    g = LandingGuidance(target)
    g.update(0.0, x0)
    tr = g.plan.traj
    t = np.linspace(0.0, tr.tf, 600)
    e = tr.eval(t)
    tilt = np.degrees(np.arccos(np.clip(e['b'][:, 2], -1, 1)))
    gim = np.degrees(np.arctan(e['gim_tan']))
    cfg = g.cfg
    fig, axes = plt.subplots(2, 2, figsize=(6.5, 3.5))
    axes = axes.ravel()
    # a) side view in the vertical plane through the start and the target, with the body axis drawn every 0.5 s
    hdir = -e['r'][0, :2] / np.linalg.norm(e['r'][0, :2])
    dist = (e['r'][:, :2] - e['r'][0, :2]) @ hdir - np.linalg.norm(e['r'][0, :2])        # horizontal distance to target
    alt = e['r'][:, 2] - target[2]
    ax = axes[0]
    clean(ax)
    ax.plot(dist, alt, color=BLUE, lw=1.3, zorder=3)
    ax.set_xlim(-30, 14)
    ax.set_ylim(-3, 53)
    ax.set_xlabel('Horizontal distance to target, m')
    ax.set_ylabel('Altitude above target, m')
    fig.tight_layout(pad=0.4, w_pad=1.6, h_pad=0.9)
    fig.canvas.draw()
    box = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())          # panel size in inches
    sx, sy = 44.0 / box.width, 56.0 / box.height                                       # data units per inch
    for ti in np.arange(0.0, tr.tf + 1e-9, 0.5):                                       # body axis, true angle on the page
        k = int(np.argmin(np.abs(t - ti)))
        bh, bz = e['b'][k, :2] @ hdir, e['b'][k, 2]
        dx, dy = 0.075 * bh * sx, 0.075 * bz * sy
        ax.plot([dist[k] - dx, dist[k] + dx], [alt[k] - dy, alt[k] + dy], color=INK, lw=0.9, zorder=4)
    for ax, yv, lab, lims in ((axes[1], e['T'], 'Thrust, N', (cfg.T_min_plan, cfg.T_max_plan)),
                              (axes[2], tilt, 'Tilt from vertical, deg', (np.degrees(cfg.tilt_max),)),
                              (axes[3], gim, 'Gimbal angle, deg', (np.degrees(cfg.gimbal_plan),))):
        clean(ax)
        for lim in lims:
            ax.axhline(lim, color=MUTED, lw=0.7, ls=(0, (4, 3)), zorder=2)
        ax.plot(t, yv, color=BLUE, lw=1.3, zorder=3)
        ax.set_xlabel('Time, s')
        ax.set_ylabel(lab)
        ax.set_xlim(0, tr.tf)
    axes[1].set_ylim(380, 980)
    axes[2].set_ylim(0, 22)
    axes[3].set_ylim(0, 11)
    for ax, tag in zip(axes, ('a)', 'b)', 'c)', 'd)')):
        ax.text(-0.14, -0.24, tag, transform=ax.transAxes, fontsize=8.5, color=INK, va='top', ha='right')
    fig.tight_layout(pad=0.4, w_pad=1.6, h_pad=0.9)
    fig.savefig(os.path.join(HERE, 'figures', 'example_plan.pdf'))
    plt.close(fig)
    return dict(tf=float(tr.tf), fuel=float(g.plan.fuel), solve_ms=float(1e3 * g.plan.solve_time),
                tilt_max=float(tilt.max()), gimbal_max=float(gim.max()), T_min=float(e['T'].min()), T_max=float(e['T'].max()))


def fig_touchdown():
    """Closed-loop touchdown accuracy with computation time counted: successive convexification vs this work."""
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.45), sharey=True)
    series = (('Slat', 'Successive convexification', BLUE, 'o'), ('F10plainown', 'Single convex program (this work)', AQUA, '^'))
    for ax, scen, tag in zip(axes, ('inair', 'hop'), ('a)', 'b)')):
        d = json.load(open(os.path.join(SOLVER, 'results', f'mc_{scen}_flat.json')))
        clean(ax)
        for key, name, col, mk in series:
            rr = [r for r in d if r['method'] == key and 'failed' not in r]
            x = np.maximum([100 * r['pos_err'] for r in rr], 0.02)
            ax.scatter(x, [r['speed'] for r in rr], s=20, marker=mk, color=col, edgecolor='white', linewidth=0.5,
                       label=name, zorder=3)
        ax.set_xscale('log')
        ax.set_xlim(0.02, 40)
        ax.set_ylim(0, 1.0)
        ax.set_xticks([0.1, 1, 10])
        ax.set_xticklabels(['0.1', '1', '10'])
        ax.set_xlabel('Lateral error at touchdown, cm')
        ax.text(-0.02, -0.2, tag, transform=ax.transAxes, fontsize=8.5, color=INK, va='top', ha='right')
    axes[0].set_ylabel('Touchdown speed, m/s')
    axes[0].legend(loc='upper left', frameon=False, handletextpad=0.2, borderaxespad=0.1)
    fig.tight_layout(pad=0.4, w_pad=1.0)
    fig.savefig(os.path.join(HERE, 'figures', 'touchdown.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    fig_schematic()
    info = fig_example()
    fig_touchdown()
    print(json.dumps(info, indent=1))
