"""Figures for the AIAA student-conference paper on the impossibility result.

AIAA figure rules followed here: no background, borders or outlines; no caption inside the figure; axis labels in words
with units after a comma; all text at least 8 pt at the printed size (figures are saved at their printed size).

Usage (from this directory):  ../../../solver/.venv/bin/python make_figures.py
Fig. 1 is computed here from the closed-form dive-then-brake witness. Fig. 2 reads
../../../solver/results/audit_hop_ring.json (written by solver/scripts/audit_hop_ring.py).
"""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, '..', '..', '..', 'solver', 'results')
FIG = os.path.join(HERE, 'figures')

plt.rcParams.update({'font.family': 'serif', 'font.serif': ['STIXGeneral', 'Times New Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 8.5, 'axes.labelsize': 8.5, 'xtick.labelsize': 8,
                     'ytick.labelsize': 8, 'legend.fontsize': 8, 'axes.linewidth': 0.6, 'savefig.transparent': True})
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#d9d8d2'
BLUE, AQUA = '#2a78d6', '#1baf7a'


def clean(ax):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2.5, width=0.6, colors=INK)


def witness(delta, omega, sstar, amin, amax, tf, g0=9.81, sign=1.0, n=40001):
    """Dive-then-brake witness of Theorem 2 at constant mass: state history that lands at rest at the origin."""
    t = np.linspace(0.0, tf, n)
    dive = t < sstar
    ang = np.where(dive, delta + omega * t, 0.0)          # thrust direction from vertical
    a = np.where(dive, amin, amax)
    acc = np.stack([sign * a * np.sin(ang), a * np.cos(ang) - g0], axis=1)
    dt = np.diff(t)[:, None]
    # integrate backward from rest at the origin
    v = np.zeros_like(acc)
    v[:-1] = -np.cumsum((0.5 * (acc[1:] + acc[:-1]) * dt)[::-1], axis=0)[::-1]
    r = np.zeros_like(acc)
    r[:-1] = -np.cumsum((0.5 * (v[1:] + v[:-1]) * dt)[::-1], axis=0)[::-1]
    tilt = omega * np.minimum(t, sstar)
    return t, r, v, tilt, ang


def fig_witness():
    delta, omega = np.radians(15.0), 0.4
    sstar, amin, amax, tf = delta / omega, 5.0, 12.5, 4.0
    t, rp, vp, tilt, ang = witness(delta, omega, sstar, amin, amax, tf, sign=+1)
    _, rm, vm, _, _ = witness(delta, omega, sstar, amin, amax, tf, sign=-1)
    print('witness data: r0 = (%.4f, %.4f) m, v0 = (%.4f, %.4f) m/s' % (rp[0, 0], rp[0, 1], vp[0, 0], vp[0, 1]))
    print('min altitude %.2e m, min glide margin (30 deg) %.2e m' %
          (rp[:, 1].min(), (rp[:, 1] - np.tan(np.radians(30)) * np.abs(rp[:, 0])).min()))
    k = np.searchsorted(t, sstar)
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.55), gridspec_kw={'width_ratios': [1.0, 1.15]})
    a0 = ax[0]
    for r, col, lab in ((rp, BLUE, 'Witness'), (rm, AQUA, 'Mirror image')):
        a0.plot(r[k:, 0], r[k:, 1], color=col, lw=1.0)
        a0.plot(r[:k + 1, 0], r[:k + 1, 1], color=col, lw=2.4, solid_capstyle='butt', label=lab)
        a0.plot(r[0, 0], r[0, 1], 'o', color=col, ms=4.5)
    a0.plot(0, rp[0, 1], 'x', color=INK, ms=6, mew=1.4, label='Midpoint of the two\ninitial states')
    a0.plot(0, 0, 's', color=INK, ms=4)
    a0.set_xlabel('Lateral position, m')
    a0.set_ylabel('Altitude, m')
    a0.set_xlim(-0.75, 0.75)
    a0.set_ylim(0, 21.5)
    a0.legend(frameon=False, loc='lower left', bbox_to_anchor=(0.0, 0.02), handlelength=1.6, borderaxespad=0.2)
    clean(a0)
    a1 = ax[1]
    a1.axvspan(0, sstar, color=GRID, lw=0, alpha=0.6)
    a1.plot(t, np.degrees(ang), color=BLUE, lw=1.4, label='Thrust direction')
    a1.plot(t, np.degrees(tilt), color=INK, lw=1.2, ls=(0, (4, 2)), label='Body axis')
    a1.set_xlabel('Time, s')
    a1.set_ylabel('Angle from vertical, deg')
    a1.set_xlim(0, tf)
    a1.set_ylim(-1, 34)
    a1.legend(frameon=False, loc='upper right')
    clean(a1)
    for a, s in zip(ax, 'ab'):
        a.text(0.5, -0.25, s + ')', transform=a.transAxes, ha='center', va='top', fontsize=8.5)
    fig.subplots_adjust(left=0.075, right=0.99, top=0.97, bottom=0.29, wspace=0.26)
    fig.savefig(os.path.join(FIG, 'witness.pdf'))
    plt.close(fig)


def fig_hopring():
    d = json.load(open(os.path.join(RESULTS, 'audit_hop_ring.json')))
    fig, ax = plt.subplots(figsize=(3.4, 2.3))
    yes = [(e['v0z'], e['d']) for e in d if e['D_feasible']]
    no = [(e['v0z'], e['d']) for e in d if not e['D_feasible']]
    ax.plot(*zip(*yes), 'o', color=BLUE, ms=6, label='Landing found')
    ax.plot(*zip(*no), 'x', color=INK, ms=6, mew=1.4, label='No landing found')
    ax.set_xlabel('Launch speed, m/s')
    ax.set_ylabel('Distance from launch point\nto landing point, m')
    ax.set_xticks([6.0, 6.1, 6.2, 6.3, 6.4])
    ax.set_yticks([0, 1, 2, 3])
    ax.set_xlim(5.93, 6.47)
    ax.set_ylim(-0.45, 3.45)
    ax.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.22), ncol=2, columnspacing=1.2, handletextpad=0.3)
    clean(ax)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.87, bottom=0.19)
    fig.savefig(os.path.join(FIG, 'hopring.pdf'))
    plt.close(fig)


if __name__ == '__main__':
    os.makedirs(FIG, exist_ok=True)
    fig_witness()
    fig_hopring()
