"""Comparative plots for spy_beater_hunt iters.

Different from studies.long_term_portfolio.plot_helper (which plots ONE
selected config vs benchmarks). This module overlays ALL configs in a
sweep so we can visually compare how SMA/EMA/threshold variants stack
against each other and against SPY.

Three plots per dataset:

  1. ``plot_overlay_{dataset}.png`` — top: equity curves (log scale) of
     every config in the sweep + SPY 1× buy-hold benchmark.
     bottom: drawdown curves with the 40.85% MDD bar marked.

  2. ``plot_cagr_mdd_scatter.png`` (single, all datasets aggregated) —
     scatter of mean(CAGR) × mean(MDD) per config, with WINNER zone
     shaded (CAGR ≥ 13.80% AND MDD ≤ 40.85%) and SPY benchmark plotted.

  3. ``plot_gate_heatmap.png`` (single, all datasets) — color-coded
     7-gate pass/fail matrix per (config × dataset).

Citations:
  - SPY benchmark numbers (CAGR 13.80%, MDD 40.85%) from
    studies.spy_beater_hunt.scoring.SPY_CAGR_MEAN / SPY_MDD_MEAN.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.ai_trade.backtest.data.testfolio_loader import load_testfolio_series
from studies.long_term_portfolio import datasets as datasets_mod
from studies.spy_beater_hunt.scoring import SPY_CAGR_MEAN, SPY_MDD_MEAN


def _spy_returns_for_dataset(dataset: str) -> pd.Series:
    """SPYSIM daily returns sliced to the dataset's window."""
    spy = load_testfolio_series("SPYSIM").pct_change().dropna()
    meta = datasets_mod.get_meta(dataset)
    return spy.loc[meta["start"]:meta["end"]].dropna()


def _drawdown_pct(returns: pd.Series) -> pd.Series:
    eq = (1.0 + returns).cumprod()
    return (eq / eq.cummax() - 1.0) * 100.0


def plot_overlay_per_dataset(
    iter_dir: Path,
    config_returns: dict[str, dict[str, pd.Series]],
    datasets_to_test: tuple[str, ...],
) -> list[Path]:
    """Generate one overlay PNG per dataset (equity + drawdown stacked)."""
    out_paths: list[Path] = []
    for ds in datasets_to_test:
        path = iter_dir / f"plot_overlay_{ds}.png"
        try:
            spy_ret = _spy_returns_for_dataset(ds)
        except Exception:
            spy_ret = None

        fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # Equity curves (log scale)
        for cfg, ds_returns in config_returns.items():
            r = ds_returns.get(ds)
            if r is None or len(r) < 2:
                continue
            eq = (1.0 + r).cumprod()
            axes[0].plot(eq.index, eq.values, label=cfg, linewidth=1.0, alpha=0.85)
        if spy_ret is not None and len(spy_ret) > 1:
            spy_eq = (1.0 + spy_ret).cumprod()
            axes[0].plot(
                spy_eq.index, spy_eq.values,
                label="SPY 1× buy-hold",
                linewidth=2.0, color="black", linestyle="--",
            )
        axes[0].set_yscale("log")
        axes[0].set_title(f"{ds} — equity curves (log scale)")
        axes[0].legend(loc="best", fontsize=9, ncol=2)
        axes[0].grid(True, alpha=0.3, which="both")
        axes[0].set_ylabel("Equity (start = 1)")

        # Drawdowns
        for cfg, ds_returns in config_returns.items():
            r = ds_returns.get(ds)
            if r is None or len(r) < 2:
                continue
            dd = _drawdown_pct(r)
            axes[1].plot(dd.index, dd.values, label=cfg, linewidth=1.0, alpha=0.85)
        if spy_ret is not None and len(spy_ret) > 1:
            spy_dd = _drawdown_pct(spy_ret)
            axes[1].plot(
                spy_dd.index, spy_dd.values,
                label="SPY 1× buy-hold",
                linewidth=2.0, color="black", linestyle="--",
            )
        axes[1].axhline(
            -SPY_MDD_MEAN * 100,
            color="red", linestyle="--", alpha=0.6,
            label=f"MDD bar ({SPY_MDD_MEAN*100:.2f}%)",
        )
        axes[1].set_title(f"{ds} — drawdown (%)")
        axes[1].legend(loc="lower left", fontsize=9, ncol=2)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylabel("Drawdown (%)")
        axes[1].set_xlabel("Date")

        fig.tight_layout()
        fig.savefig(path, dpi=120)
        plt.close(fig)
        out_paths.append(path)
    return out_paths


def plot_cagr_mdd_scatter(
    iter_dir: Path,
    all_configs_metrics: dict[str, dict[str, dict[str, float]]],
    datasets_to_test: tuple[str, ...],
) -> Path:
    """Scatter of mean CAGR × mean MDD per config, with WINNER zone shaded."""
    path = iter_dir / "plot_cagr_mdd_scatter.png"
    fig, ax = plt.subplots(figsize=(11, 8))

    cagrs_x: list[float] = []
    mdds_x: list[float] = []
    for cfg, ds_metrics in all_configs_metrics.items():
        cagrs = [ds_metrics[ds]["cagr"] for ds in datasets_to_test]
        mdds = [ds_metrics[ds]["mdd"] for ds in datasets_to_test]
        mean_cagr = float(np.mean(cagrs))
        mean_mdd = float(np.mean(mdds))
        cagrs_x.append(mean_cagr)
        mdds_x.append(mean_mdd)
        ax.scatter(mean_mdd * 100, mean_cagr * 100, s=120, alpha=0.8, edgecolor="black")
        ax.annotate(
            cfg, (mean_mdd * 100, mean_cagr * 100),
            textcoords="offset points", xytext=(7, 4), fontsize=8,
        )

    # SPY benchmark point
    ax.scatter(
        SPY_MDD_MEAN * 100, SPY_CAGR_MEAN * 100,
        marker="*", s=350, color="black", label="SPY mean (3-dataset)",
        zorder=5,
    )
    # Strict bars
    ax.axhline(
        SPY_CAGR_MEAN * 100, color="green", linestyle="--", alpha=0.6,
        label=f"CAGR bar ({SPY_CAGR_MEAN*100:.2f}%)",
    )
    ax.axvline(
        SPY_MDD_MEAN * 100, color="red", linestyle="--", alpha=0.6,
        label=f"MDD ceiling ({SPY_MDD_MEAN*100:.2f}%)",
    )
    # WINNER zone shading
    ymax = max(40.0, max(cagrs_x) * 100 + 5.0)
    xmin = min(5.0, min(mdds_x) * 100 - 5.0) if mdds_x else 0.0
    ax.fill_between(
        [xmin, SPY_MDD_MEAN * 100],
        SPY_CAGR_MEAN * 100, ymax,
        alpha=0.15, color="green", label="WINNER zone (CAGR↑ + MDD↓ vs SPY)",
    )

    ax.set_xlabel("Mean MDD across 3 datasets (%)")
    ax.set_ylabel("Mean CAGR across 3 datasets (%)")
    ax.set_title("CAGR vs MDD per config — strict bars overlaid")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_gate_heatmap(
    iter_dir: Path,
    gate_details_per_dataset: dict[str, dict],
    config_results: dict[str, dict[str, dict[str, float]]],
    datasets_to_test: tuple[str, ...],
) -> Path:
    """Heatmap-like grid of gate pass/fail per dataset (selected config view).

    Caller passes ``gate_details_per_dataset[dataset][gate_key] = bool/numeric``.
    Cells coloured green=pass, red=fail; axis labels show the gate names.
    """
    path = iter_dir / "plot_gate_heatmap.png"
    gate_names = ["G1 PBO", "G2 DSR", "G3 WF", "G4 OOS70/30", "G5 FWD", "G6 Boot", "G7 CrossLib"]
    gate_keys = ["g1_pbo", "g2_dsr", "g3_wf", "g4_oos", "g5_fwd", "g6_bootstrap", "g7_crosslib"]

    grid = np.zeros((len(datasets_to_test), len(gate_keys)), dtype=int)
    for i, ds in enumerate(datasets_to_test):
        details = gate_details_per_dataset.get(ds, {})
        # gate_details has numeric values; we infer pass/fail by matching the
        # same logic as run_iter (PBO < 0.5, DSR p < 0.05, WF returns ≥ 6/8 >0
        # AND mdds ≤ 0.25, OOS Sharpe > 0, FWD Sharpe > 0, CI low > 0,
        # crosslib delta ≤ 3pp). For simplicity we read the boolean from the
        # gates dict if present in caller's payload.
        pbo = details.get("g1_pbo", float("nan"))
        dsr_p = details.get("g2_dsr_p", 1.0)
        wf_returns = details.get("g3_wf_returns", [])
        wf_mdds = details.get("g3_wf_mdds", [])
        oos_s = details.get("g4_oos_sharpe", 0.0)
        fwd_s = details.get("g5_fwd_sharpe", 0.0)
        ci_low = details.get("g6_ci_low", 0.0)
        crosslib = details.get("g7_crosslib_delta_pp", float("inf"))
        passed = [
            (not np.isnan(pbo) and pbo < 0.5) if isinstance(pbo, (int, float)) else False,
            dsr_p < 0.05,
            (
                len(wf_returns) >= 8
                and sum(x > 0 for x in wf_returns) >= 6
                and (max(wf_mdds) if wf_mdds else 1.0) <= 0.25
            ),
            oos_s > 0,
            fwd_s > 0,
            ci_low > 0,
            crosslib <= 3.0,
        ]
        for j, p in enumerate(passed):
            grid[i, j] = 1 if p else 0

    fig, ax = plt.subplots(figsize=(10, 1 + 0.7 * len(datasets_to_test)))
    cmap = plt.colormaps.get_cmap("RdYlGn").resampled(2)
    ax.imshow(grid, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(gate_names)))
    ax.set_xticklabels(gate_names, rotation=20, ha="right")
    ax.set_yticks(np.arange(len(datasets_to_test)))
    ax.set_yticklabels(datasets_to_test)
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            ax.text(
                j, i, "PASS" if grid[i, j] else "FAIL",
                ha="center", va="center",
                color="white", fontsize=9, fontweight="bold",
            )
    ax.set_title("Gate pass/fail per dataset (selected config)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
