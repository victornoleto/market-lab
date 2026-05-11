"""CLI orchestrator for the tax_comparison sub-study.

Usage:
    python -m studies.letf_rotation_hunt.analyses.tax_comparison.run_tax_comparison

Outputs (under studies/letf_rotation_hunt/reports/tax_comparison/):
  - top10_metrics_by_dataset.csv
  - master_summary.png
  - per_strategy_plots/<NN>_<name>_equity.png   (10 files)
  - per_strategy_plots/<NN>_<name>_ratio.png    (10 files)
  - TAX_COMPARISON_REPORT.md
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.letf_rotation_hunt.runners.run_iter_t1 import DATASET_WINDOWS
from studies.letf_rotation_hunt.analyses.tax_comparison.per_swing import simulate_per_swing
from studies.letf_rotation_hunt.analyses.tax_comparison.plot_tax_comparison import (
    plot_master_summary, plot_per_strategy_equity, plot_per_strategy_ratio,
)
from studies.letf_rotation_hunt.analyses.tax_comparison.reconstruct import reconstruct_strategy
from studies.letf_rotation_hunt.analyses.tax_comparison.select_top10 import select_top10
from studies.letf_rotation_hunt.core.tax_layer import apply_annual_darf

INITIAL_CAPITAL = 10_000.0
TAX_RATE = 0.15
TRADING_DAYS_PER_YEAR = 252


def _annualised_sharpe(returns: pd.Series) -> float:
    if returns.std() == 0 or len(returns) < 2:
        return float("nan")
    return float(returns.mean() / returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR))


def _cagr_from_equity(eq: pd.Series) -> float:
    if len(eq) < 2:
        return float("nan")
    n_years = (eq.index[-1] - eq.index[0]).days / 365.25
    if n_years <= 0:
        return float("nan")
    return float((eq.iloc[-1] / eq.iloc[0]) ** (1.0 / n_years) - 1.0)


def _max_drawdown(eq: pd.Series) -> float:
    rolling_max = eq.cummax()
    dd = eq / rolling_max - 1.0
    return float(dd.min())


def _pct_above_spy(eq: pd.Series, spy_eq: pd.Series) -> float:
    aligned = pd.concat({"s": eq, "b": spy_eq}, axis=1, join="inner").dropna()
    if len(aligned) == 0:
        return float("nan")
    s_norm = aligned["s"] / aligned["s"].iloc[0]
    b_norm = aligned["b"] / aligned["b"].iloc[0]
    return float((s_norm > b_norm).mean())


def _slice_to_dataset(eq: pd.Series, dataset: str) -> pd.Series:
    win = DATASET_WINDOWS.get(dataset)
    if win is None:
        return eq
    start, end = win
    return eq[(eq.index >= start) & (eq.index <= end)]


def _build_spy_equity(reference_index: pd.Index) -> pd.Series:
    """Bought-and-held SPY equity normalised to $10k at the strategy's start."""
    spy_full = load_testfolio_series("SPYSIM").dropna()
    spy_aligned = spy_full.reindex(reference_index).ffill().dropna()
    if len(spy_aligned) == 0:
        raise RuntimeError("SPYSIM has no overlap with strategy index")
    return INITIAL_CAPITAL * (spy_aligned / spy_aligned.iloc[0])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tax comparison sub-study")
    parser.add_argument(
        "--iterations-root", type=Path,
        default=Path("studies/letf_rotation_hunt/runs/original"),
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=Path("studies/letf_rotation_hunt/reports/tax_comparison"),
    )
    parser.add_argument(
        "--datasets", nargs="+",
        default=["lh_56y", "modern_1990", "spy_real", "ndx_real"],
    )
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = args.out_dir / "per_strategy_plots"
    plots_dir.mkdir(exist_ok=True)

    print(f"[tax_comparison] selecting top-10 from {args.iterations_root}")
    top = select_top10(args.iterations_root)
    if not top:
        print("ERROR: no eligible swing-rotation configs found", file=sys.stderr)
        return 1
    print(f"[tax_comparison] {len(top)} configs selected")
    for r in top:
        print(f"  {r['score']:6.2f}  {r['tier']:6s}  {r['config_name']}")

    csv_rows: list[dict] = []
    plot_payloads: list[dict] = []

    for rank, sel in enumerate(top, start=1):
        print(f"\n[tax_comparison] [{rank}/{len(top)}] reconstructing {sel['config_name']} ({sel['tier']})")
        rebuilt = reconstruct_strategy(sel, datasets=args.datasets)
        positions = rebuilt["positions"]
        asset_returns = rebuilt["asset_returns_aligned"]
        gross_eq = rebuilt["gross_equity"]
        gross_returns = rebuilt["strategy_returns"]

        # Model 1 — per-swing FIFO
        m1 = simulate_per_swing(
            positions, asset_returns,
            initial_capital=INITIAL_CAPITAL, tax_rate=TAX_RATE,
        )
        # Drop bar 0 of net_equity to align with dispatcher's gross_equity (which
        # has the first bar dropped by .shift(1).dropna() in the dispatcher).
        eq_per_swing = m1["net_equity"].reindex(gross_eq.index)

        # Model 2 — annual net (existing tax_layer)
        eq_annual_net = apply_annual_darf(
            gross_eq, gross_returns, mode="annual_realize", initial=INITIAL_CAPITAL,
        )

        # SPY benchmark from strategy's start
        eq_spy = _build_spy_equity(gross_eq.index)

        # Per-dataset metrics (4 datasets × 3 tax models = 12 rows per config)
        for ds in args.datasets:
            ds_gross = _slice_to_dataset(gross_eq, ds)
            ds_m1 = _slice_to_dataset(eq_per_swing, ds)
            ds_m2 = _slice_to_dataset(eq_annual_net, ds)
            ds_spy = _slice_to_dataset(eq_spy, ds)
            for label, eq in [("gross", ds_gross), ("per_swing", ds_m1), ("annual_net", ds_m2)]:
                if len(eq) < 2:
                    continue
                rets = eq.pct_change().dropna()
                csv_rows.append({
                    "config_name": sel["config_name"],
                    "tier": sel["tier"],
                    "iter_id": sel["iter_id"],
                    "dataset": ds,
                    "tax_model": label,
                    "cagr": _cagr_from_equity(eq),
                    "sharpe": _annualised_sharpe(rets),
                    "mdd": _max_drawdown(eq),
                    "final_equity": float(eq.iloc[-1]),
                    "final_ratio_vs_spy": float(eq.iloc[-1] / ds_spy.iloc[-1]) if len(ds_spy) > 0 else float("nan"),
                    "pct_time_above_spy": _pct_above_spy(eq, ds_spy),
                    "tax_paid_total": (m1["tax_paid_total"] if label == "per_swing" else float("nan")),
                    "n_taxable_swings": (m1["n_taxable_swings"] if label == "per_swing" else float("nan")),
                })

        # Per-strategy plots — lh_56y window
        gross_lh = _slice_to_dataset(gross_eq, "lh_56y")
        m1_lh    = _slice_to_dataset(eq_per_swing, "lh_56y")
        m2_lh    = _slice_to_dataset(eq_annual_net, "lh_56y")
        spy_lh   = _slice_to_dataset(eq_spy, "lh_56y")
        prefix = f"{rank:02d}_{sel['config_name']}"
        plot_per_strategy_equity(
            sel["config_name"], gross_lh, m1_lh, m2_lh, spy_lh,
            plots_dir / f"{prefix}_equity.png",
        )
        plot_per_strategy_ratio(
            sel["config_name"], gross_lh, m1_lh, m2_lh, spy_lh,
            plots_dir / f"{prefix}_ratio.png",
        )
        plot_payloads.append({
            "config_name": sel["config_name"],
            "eq_gross": gross_lh, "eq_per_swing": m1_lh,
            "eq_annual_net": m2_lh, "eq_spy": spy_lh,
        })

    # CSV
    csv_path = args.out_dir / "top10_metrics_by_dataset.csv"
    pd.DataFrame(csv_rows).to_csv(csv_path, index=False)
    print(f"\n[tax_comparison] CSV written: {csv_path}")

    # Master summary plot
    master_path = args.out_dir / "master_summary.png"
    plot_master_summary(plot_payloads, master_path)
    print(f"[tax_comparison] master plot written: {master_path}")

    # Markdown report
    report_path = args.out_dir / "TAX_COMPARISON_REPORT.md"
    report_path.write_text(_render_report(top, csv_rows))
    print(f"[tax_comparison] report written: {report_path}")
    return 0


def _render_report(top: list[dict], csv_rows: list[dict]) -> str:
    """Generate TAX_COMPARISON_REPORT.md from selected configs + per-row metrics."""
    df = pd.DataFrame(csv_rows)
    lh = df[df["dataset"] == "lh_56y"].copy()

    lines = []
    lines.append("# LETF Tax Comparison — Top-10 Swing Strategies")
    lines.append("")
    lines.append(f"_Generated {datetime.now(timezone.utc).isoformat()}_")
    lines.append("")
    lines.append("Spec: pre-publication agent spec removed from the public tree.")
    lines.append("")
    lines.append("## Top-10 selection")
    lines.append("")
    lines.append("| Rank | Config | Tier | Iter | Score |")
    lines.append("|---:|---|---|---|---:|")
    for i, r in enumerate(top, start=1):
        lines.append(
            f"| {i} | `{r['config_name']}` | {r['tier']} | {r['iter_id']} | {r['score']:.1f} |"
        )
    lines.append("")

    lines.append("## Per-strategy net Sharpe (lh_56y)")
    lines.append("")
    lines.append("| Config | Gross | Model 1 (per-swing) | Model 2 (annual) | SPY edge gross | SPY edge M1 | SPY edge M2 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    spy_sharpe_lh = 0.682  # canonical from parent study
    for i, r in enumerate(top, start=1):
        sub = lh[lh["config_name"] == r["config_name"]]
        if sub.empty:
            continue
        gross_s = float(sub[sub["tax_model"] == "gross"]["sharpe"].iloc[0])
        m1_s    = float(sub[sub["tax_model"] == "per_swing"]["sharpe"].iloc[0])
        m2_s    = float(sub[sub["tax_model"] == "annual_net"]["sharpe"].iloc[0])
        lines.append(
            f"| `{r['config_name']}` | {gross_s:.3f} | {m1_s:.3f} | {m2_s:.3f} | "
            f"{gross_s - spy_sharpe_lh:+.3f} | {m1_s - spy_sharpe_lh:+.3f} | {m2_s - spy_sharpe_lh:+.3f} |"
        )
    lines.append("")
    lines.append(f"_SPY 1× buy-and-hold Sharpe lh_56y: {spy_sharpe_lh:.3f} (parent study anchor)._")
    lines.append("")

    lines.append("## Plots")
    lines.append("")
    lines.append("![Master summary](master_summary.png)")
    lines.append("")
    lines.append("Per-strategy plots in `per_strategy_plots/` — `<NN>_<name>_equity.png` and `<NN>_<name>_ratio.png`.")
    lines.append("")

    lines.append("## Citations")
    lines.append("")
    lines.append("- Lei 14.754/2023 (Brazil) — 15% flat, indefinite carry-forward.")
    lines.append("- `[advances_fin_ml, p.275]` — net-of-cost Sharpe evaluation.")
    lines.append("- Parent study protocol: `README.md`, `BASE_MEMORY.md` and `KILL_RULES.md`.")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
