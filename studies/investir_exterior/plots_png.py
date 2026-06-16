"""Renderers matplotlib → arquivos PNG (para o relatório markdown).

Legendas SEMPRE fora da área de plot (nunca cobrindo dados) e escala log nas
curvas de crescimento (``chart.log_y``). dpi=140, backend Agg.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

from . import chartdata as C  # noqa: E402
from .util import brl_short  # noqa: E402

plt.rcParams.update({
    "figure.dpi": 140,
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

_LEGEND_RIGHT = dict(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=8, frameon=False)


def _save(fig, plots_dir: Path, key: str) -> str:
    plots_dir.mkdir(parents=True, exist_ok=True)
    rel = f"plots/{key}.png"
    fig.savefig(plots_dir / f"{key}.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return rel


def _money_axis(ax) -> None:
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _p: brl_short(x)))


def render(chart, plots_dir: Path) -> str:
    if isinstance(chart, C.LineChart):
        return _line(chart, plots_dir)
    if isinstance(chart, C.WaterfallChart):
        return _waterfall(chart, plots_dir)
    if isinstance(chart, C.BreakevenChart):
        return _breakeven(chart, plots_dir)
    if isinstance(chart, C.SensitivityChart):
        return _sensitivity(chart, plots_dir)
    if isinstance(chart, C.ValidationChart):
        return _validation(chart, plots_dir)
    raise TypeError(f"tipo de chart desconhecido: {type(chart)}")


def _line(c: C.LineChart, plots_dir: Path) -> str:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for ln in c.lines:
        ax.plot(ln.x, ln.y, label=ln.label, color=ln.color,
                linestyle=":" if ln.dash else "-", linewidth=1.1 if ln.dash else 1.6,
                alpha=0.8 if ln.dash else 1.0)
    if c.log_y:
        ax.set_yscale("log")
    if c.money:
        _money_axis(ax)
    ax.set_title(c.title)
    ax.set_ylabel(c.ylabel)
    ax.legend(**_LEGEND_RIGHT)
    return _save(fig, plots_dir, c.key)


def _waterfall(c: C.WaterfallChart, plots_dir: Path) -> str:
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    x = range(len(c.categories))
    bottoms = [0.0] * len(c.categories)
    for label, cor, vals in c.components:
        ax.bar(x, vals, bottom=bottoms, label=label, color=cor, width=0.6)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    for i, t in enumerate(c.totals):
        ax.text(i, t, f" {brl_short(t)}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(c.categories, fontsize=9)
    ax.set_title(c.title)
    ax.set_ylabel(c.ylabel)
    _money_axis(ax)
    ax.legend(**_LEGEND_RIGHT)
    return _save(fig, plots_dir, c.key)


def _breakeven(c: C.BreakevenChart, plots_dir: Path) -> str:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.5, 6.2), sharex=True, height_ratios=[2, 1])
    ax1.plot(c.br.x, c.br.y, label=c.br.label, color=c.br.color, linewidth=1.6)
    ax1.plot(c.us.x, c.us.y, label=c.us.label, color=c.us.color, linewidth=1.6)
    ax1.set_yscale("log")
    _money_axis(ax1)
    ax1.set_title(c.title)
    ax1.set_ylabel(c.ylabel)
    ax1.legend(**_LEGEND_RIGHT)

    import numpy as np
    diff = np.asarray(c.diff_y, dtype=float)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.fill_between(c.diff_x, diff, 0, where=(diff >= 0), color=c.us_color, alpha=0.3)
    ax2.fill_between(c.diff_x, diff, 0, where=(diff < 0), color=C.COR_BR, alpha=0.3)
    ax2.plot(c.diff_x, diff, color="black", linewidth=1.0)
    ax2.set_ylabel("Vantagem US−BR\n(% do aporte)")
    return _save(fig, plots_dir, c.key)


def _sensitivity(c: C.SensitivityChart, plots_dir: Path) -> str:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for ln in c.lines:
        ax.plot(ln.x, ln.y, marker="o", label=ln.label, color=ln.color, linewidth=1.6)
    ax.set_xticks(list(range(len(c.xticklabels))))
    ax.set_xticklabels(c.xticklabels)
    ax.set_title(c.title)
    ax.set_ylabel(c.ylabel)
    ax.set_xlabel(c.xlabel)
    ax.legend(**_LEGEND_RIGHT)
    return _save(fig, plots_dir, c.key)


def _validation(c: C.ValidationChart, plots_dir: Path) -> str:
    n = max(1, len(c.panels))
    fig, axes = plt.subplots(1, n, figsize=(4.3 * n, 4.0))
    if n == 1:
        axes = [axes]
    for ax, (nome, x, syn, real) in zip(axes, c.panels):
        ax.plot(x, syn, label="sintético", color="#3949ab", linewidth=1.3)
        ax.plot(x, real, label="real (B3)", color="#d32f2f", linewidth=1.0, alpha=0.85)
        ax.set_yscale("log")
        ax.set_title(nome, fontsize=9)
        ax.legend(fontsize=7, frameon=False)
    fig.suptitle(c.title, fontsize=10)
    fig.tight_layout()
    return _save(fig, plots_dir, c.key)
