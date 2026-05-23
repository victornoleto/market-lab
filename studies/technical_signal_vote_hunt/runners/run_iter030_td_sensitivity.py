"""Local T/D sensitivity around the iter030 parameter-GA candidate.

This is a deliberately small, pre-specified grid over post-crash rearm geometry:
`T in {20,35,45}` and `D in {60,90,120}`. It is meant to explain why the
parameter GA liked `D120`, not to continue open-ended optimization. Final claims
remain blocked by PBO/DSR validation `[advances_fin_ml, p.196-202]`,
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.data.testfolio_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_close_only_signals, daily_returns
from studies.technical_signal_vote_hunt.runners.run_iter030_param_ga import (
    Gene,
    _baseline_gene,
    _evaluate,
    _label,
    _load_module,
    _prepare_context,
    _returns_for_gene,
    ITER030_BACKTEST,
)
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np
from studies.technical_signal_vote_hunt.runners.run_stage4_inside_iter030 import _build_returns as _inside_iter030_returns
from studies.technical_signal_vote_hunt.runners.run_stage4_inside_iter030 import _load_module as _load_stage4_module
from studies.technical_signal_vote_hunt.runners.run_stage4_inside_iter030 import ITER030_BACKTEST as STAGE4_ITER030_BACKTEST
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/iter030_td_sensitivity"
T3D_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/original/022-2026-05-06-T3d-extended-grid/qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
ITER030_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120_strategy_returns.csv"

STAGE3_SHARED_SIGNALS = "px_gt_sma10|px_gt_ema200|px_gt_sma250|px_gt_ema250|roc20_gt_0|roc60_gt_0|roc120_gt_0|rsi14_gt_50"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run local T/D sensitivity around iter030")
    p.add_argument("--t-values", default="20,35,45")
    p.add_argument("--d-values", default="60,90,120")
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    tables_dir = args.out_dir / "tables"
    plots_dir = args.out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    ctx = _prepare_context(_load_module(ITER030_BACKTEST, "iter030_td_sensitivity"))
    t_values = [int(x) for x in args.t_values.split(",")]
    d_values = [int(x) for x in args.d_values.split(",")]

    td_returns, td_metrics = _td_grid(ctx, t_values, d_values)
    comparison_returns = _comparison_returns(ctx)
    comparison_returns = comparison_returns.loc[comparison_returns.notna().all(axis=1)]
    comparison_metrics = _metrics_table(comparison_returns)
    rolling = _rolling_table(comparison_returns)
    relative = (1.0 + comparison_returns).cumprod().div((1.0 + comparison_returns["iter030 canonical"]).cumprod(), axis=0)

    td_metrics.to_csv(tables_dir / "td_grid_metrics.csv", index=False)
    td_returns.to_csv(tables_dir / "td_grid_returns.csv")
    comparison_returns.to_csv(tables_dir / "comparison_returns.csv")
    comparison_metrics.to_csv(tables_dir / "comparison_metrics.csv")
    rolling.to_csv(tables_dir / "comparison_rolling_windows.csv", index=False)
    relative.to_csv(tables_dir / "comparison_relative_to_iter030.csv")

    comparison_equity = (1.0 + comparison_returns).cumprod()
    _plot_equity(comparison_equity, plots_dir / "comparison_equity.png")
    _plot_relative(relative, plots_dir / "comparison_relative_to_iter030.png")
    _plot_rolling_10y(comparison_returns, plots_dir / "comparison_rolling_10y.png")
    _plot_heatmap(td_metrics, "cagr", plots_dir / "td_heatmap_cagr.png")
    _plot_heatmap(td_metrics, "sortino", plots_dir / "td_heatmap_sortino.png")
    _plot_heatmap(td_metrics, "mdd", plots_dir / "td_heatmap_mdd.png")

    _write_report(td_metrics, comparison_metrics, rolling, args, comparison_returns.index)
    _write_manifest(args, comparison_returns.index)
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
    return 0


def _td_grid(ctx, t_values: list[int], d_values: list[int]) -> tuple[pd.DataFrame, pd.DataFrame]:
    returns = {}
    rows = []
    base = _baseline_gene()
    for t_crash in t_values:
        for d_arm in d_values:
            gene = Gene(
                base.sma_long,
                base.sma_short,
                base.vol_window,
                base.vol_threshold,
                base.ar_window,
                base.entry_k,
                base.upgrade_mode,
                t_crash,
                d_arm,
                base.tqqq_weight,
                base.lrs_factor,
                base.gamma,
                base.ratevol_window,
                base.ratevol_threshold,
            )
            label = f"T{t_crash}D{d_arm}"
            returns[label] = _returns_for_gene(ctx, gene)
            row = _evaluate(ctx, gene, _label(gene))
            row.update({"td_label": label, "is_ga_winner": t_crash == 20 and d_arm == 120})
            rows.append(row)
    return pd.concat(returns, axis=1, sort=False), pd.DataFrame(rows).sort_values(["sortino", "cagr"], ascending=[False, False])


def _comparison_returns(ctx) -> pd.DataFrame:
    qqq = load_testfolio_series("QQQSIM")
    spy_ret = load_testfolio_series("SPYSIM").pct_change().dropna()
    qqq_ret = qqq.pct_change().dropna()
    zroz_ret = load_testfolio_series("ZROZSIM").pct_change().dropna()
    qld_ret = load_testfolio_series("QLDSIM").pct_change().dropna()
    tqqq_ret = load_testfolio_series("TQQQSIM").pct_change().dropna()

    new_winner = _returns_for_gene(ctx, _gene_with_td(20, 120))
    iter030 = _read_returns(ITER030_CANONICAL)
    t3d = _read_returns(T3D_CANONICAL)
    stage4_qld, stage4_tqqq = _stage4_base_votes(qqq, qld_ret, tqqq_ret, zroz_ret)
    stage3_qld, stage3_tqqq = _stage3_shared_votes(qqq, qld_ret, tqqq_ret, zroz_ret)
    inside = _stage4_inside_iter030()["inside_rearm_or_stage4"]

    return pd.concat(
        {
            "iter030 T20D120 candidate": new_winner,
            "iter030 canonical": iter030,
            "T3d-K2 canonical": t3d,
            "Stage4-inside iter030 turbo": inside,
            "Stage4 QLD base vote": stage4_qld,
            "Stage4 TQQQ base vote": stage4_tqqq,
            "Stage3 shared QLD": stage3_qld,
            "Stage3 shared TQQQ": stage3_tqqq,
            "QQQ buy_hold": qqq_ret,
            "SPY buy_hold": spy_ret,
        },
        axis=1,
        sort=False,
    )


def _gene_with_td(t_crash: int, d_arm: int) -> Gene:
    base = _baseline_gene()
    return Gene(
        base.sma_long,
        base.sma_short,
        base.vol_window,
        base.vol_threshold,
        base.ar_window,
        base.entry_k,
        base.upgrade_mode,
        t_crash,
        d_arm,
        base.tqqq_weight,
        base.lrs_factor,
        base.gamma,
        base.ratevol_window,
        base.ratevol_threshold,
    )


def _stage4_base_votes(qqq: pd.Series, qld_ret: pd.Series, tqqq_ret: pd.Series, off_ret: pd.Series) -> tuple[pd.Series, pd.Series]:
    signal = _vote(qqq, DEFAULT_BASE_SIGNALS, 3)
    dates = signal.index
    qld = qld_ret.reindex(dates)
    tqqq = tqqq_ret.reindex(dates)
    off = off_ret.reindex(dates)
    vote = signal.to_numpy(dtype=bool)
    return (
        pd.Series(_simulate_on_off_np(vote, qld.to_numpy(float), off.to_numpy(float)), index=dates),
        pd.Series(_simulate_on_off_np(vote, tqqq.to_numpy(float), off.to_numpy(float)), index=dates),
    )


def _stage3_shared_votes(qqq: pd.Series, qld_ret: pd.Series, tqqq_ret: pd.Series, off_ret: pd.Series) -> tuple[pd.Series, pd.Series]:
    signal = _vote(qqq, STAGE3_SHARED_SIGNALS, 6)
    dates = signal.index
    qld = qld_ret.reindex(dates)
    tqqq = tqqq_ret.reindex(dates)
    off = off_ret.reindex(dates)
    vote = signal.to_numpy(dtype=bool)
    return (
        pd.Series(_simulate_on_off_np(vote, qld.to_numpy(float), off.to_numpy(float)), index=dates),
        pd.Series(_simulate_on_off_np(vote, tqqq.to_numpy(float), off.to_numpy(float)), index=dates),
    )


def _vote(qqq: pd.Series, signal_names: str, k: int) -> pd.Series:
    signals = build_close_only_signals(qqq)
    names = [name for name in signal_names.split("|") if name]
    df = pd.concat([signals[name] for name in names], axis=1)
    return ((df.sum(axis=1) >= k) & (~df.isna().any(axis=1)))


def _stage4_inside_iter030() -> pd.DataFrame:
    iter030 = _load_stage4_module(STAGE4_ITER030_BACKTEST, "iter030_stage4_td_sensitivity")
    args = argparse.Namespace(base_signals=DEFAULT_BASE_SIGNALS, base_k=3)
    returns, _stats = _inside_iter030_returns(iter030, args)
    return returns


def _read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date")["return"].astype(float)


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    dates = pd.DatetimeIndex(returns.index)
    bench = returns["SPY buy_hold"].to_numpy(float)
    for label in returns.columns:
        rows.append(_metrics_row_np(returns[label].to_numpy(float), bench, dates, label, "QQQ", "td_sensitivity", 0, 0, "comparison"))
    return pd.DataFrame(rows).set_index("label").sort_values(["sortino", "cagr"], ascending=[False, False])


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in returns.columns:
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            vals = (1.0 + r).rolling(years * 252).apply(np.prod, raw=True).dropna()
            cagr = vals ** (1.0 / years) - 1.0
            rows.append(
                {
                    "label": label,
                    "window_years": years,
                    "n_windows": int(cagr.count()),
                    "min_cagr": float(cagr.min()),
                    "median_cagr": float(cagr.median()),
                    "pct_positive_cagr": float((cagr > 0.0).mean()),
                }
            )
    return pd.DataFrame(rows)


def _plot_equity(equity: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    equity.plot(ax=ax, logy=True, linewidth=1.5)
    ax.set_title("Study Strategy Comparison: Equity")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_relative(relative: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    relative.drop(columns=["iter030 canonical"]).plot(ax=ax, logy=True, linewidth=1.5)
    ax.axhline(1.0, color="black", linewidth=0.9, alpha=0.6)
    ax.set_title("Study Strategy Comparison: Relative to iter030")
    ax.set_ylabel("Strategy / iter030")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_rolling_10y(returns: pd.DataFrame, path: Path) -> None:
    equity = (1.0 + returns).cumprod()
    rolling = (equity / equity.shift(10 * 252)) ** 0.1 - 1.0
    fig, ax = plt.subplots(figsize=(13, 7))
    rolling.plot(ax=ax, linewidth=1.1)
    ax.axhline(0.0, color="black", linewidth=0.9, alpha=0.6)
    ax.set_title("Study Strategy Comparison: 10-Year Rolling CAGR")
    ax.set_ylabel("CAGR")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_heatmap(metrics: pd.DataFrame, value: str, path: Path) -> None:
    pivot = metrics.pivot(index="t_crash", columns="d_arm", values=value).sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    im = ax.imshow(pivot.to_numpy(float), aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(pivot.columns)), labels=[str(c) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), labels=[str(i) for i in pivot.index])
    ax.set_xlabel("D arm")
    ax.set_ylabel("T crash")
    ax.set_title(f"T/D Sensitivity: {value}")
    for i, t in enumerate(pivot.index):
        for j, d in enumerate(pivot.columns):
            ax.text(j, i, f"{pivot.loc[t, d]:.3f}", ha="center", va="center", color="white", fontsize=9)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(
    td_metrics: pd.DataFrame,
    comparison_metrics: pd.DataFrame,
    rolling: pd.DataFrame,
    args: argparse.Namespace,
    index: pd.DatetimeIndex,
) -> None:
    compact_td = td_metrics[["td_label", "sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "t_crash", "d_arm", "is_ga_winner"]]
    compact_comparison = comparison_metrics[["sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "pct_above_benchmark"]]
    rolling_pivot = rolling.pivot(index="label", columns="window_years", values="min_cagr").reset_index()
    rolling_pivot.columns = ["label"] + [f"min_{int(c)}y_cagr" for c in rolling_pivot.columns[1:]]
    lines = [
        "# Iter030 T/D Sensitivity and Study Comparison",
        "",
        "Status: final constrained sensitivity after the iter030 parameter GA. This is explanatory, not a new optimization branch.",
        "",
        f"Window: `{index.min().date()}` to `{index.max().date()}` ({len(index):,} bars)",
        f"T values: `{args.t_values}`",
        f"D values: `{args.d_values}`",
        "",
        "## Verdict",
        "",
        "`T20D120` remains the best CAGR/terminal-equity variant in this local T/D grid, but `T20D90` is the best balanced variant by Sortino with nearly identical CAGR and the same full-period MDD. Neither is a validated winner: prior formal validation of the GA strict-Pareto set still failed DSR and PBO. Treat `T20D120` as the performance-first sensitivity and `T20D90` as a local explanatory challenger, not as deployable replacements `[advances_fin_ml, p.196-202]`, `[advances_fin_ml, p.208-211]`.",
        "",
        "## T/D Grid",
        "",
        compact_td.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Strategy Comparison",
        "",
        compact_comparison.to_markdown(floatfmt=".4f"),
        "",
        "## Rolling Minimum CAGR",
        "",
        rolling_pivot.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plots",
        "",
        "![Comparison equity](plots/comparison_equity.png)",
        "",
        "![Relative to iter030](plots/comparison_relative_to_iter030.png)",
        "",
        "![10-year rolling CAGR](plots/comparison_rolling_10y.png)",
        "",
        "![T/D CAGR heatmap](plots/td_heatmap_cagr.png)",
        "",
        "![T/D Sortino heatmap](plots/td_heatmap_sortino.png)",
        "",
        "![T/D MDD heatmap](plots/td_heatmap_mdd.png)",
        "",
        "## Interpretation",
        "",
        "The local grid shows that longer rearm persistence (`D90`/`D120`) is the main source of the GA improvement, especially when paired with the faster `T20` crash trigger. That is a plausible economic mechanism, but it is also a small parametric move selected on the same long history. Since the honest validation of the strict Pareto candidates closed 0/7 PASS, the correct conclusion is to stop this optimization branch and keep iter030 as the core anchor.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    manifest = {
        "stage": "iter030_td_sensitivity",
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "t_values": args.t_values,
        "d_values": args.d_values,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
