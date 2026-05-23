"""Reproduce Stage 4 base vote on testfolio long-history data.

The Stage 4 base vote is close-only, so it can be reproduced on `QQQSIM` with
`QLDSIM`/`TQQQSIM` risk-on legs. This is not identical to Tiingo execution because
testfolio uses synthetic long-history series, but it answers whether the same rule
survives older cycles such as 1987, 2000-2002 and 2008 `[advances_fin_ml,
p.208-211]`.
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
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_testfolio_reproduction"
T3D_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/original/022-2026-05-06-T3d-extended-grid/qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
ITER030_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120_strategy_returns.csv"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reproduce Stage 4 base vote on testfolio")
    p.add_argument("--off-leg", choices=["CASHX", "ZROZSIM"], default="CASHX")
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS)
    p.add_argument("--base-k", type=int, default=3)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    tables_dir = args.out_dir / "tables"
    plots_dir = args.out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    returns = _build_returns(args)
    returns = returns.loc[returns.notna().all(axis=1)]
    equity = (1.0 + returns).cumprod()
    rel_spy = equity.div(equity["SPYSIM buy_hold"], axis=0)
    rel_ndx = equity.div(equity["QQQSIM/NDX buy_hold"], axis=0)
    metrics = _metrics_table(returns)
    rel_summary = _relative_summary(equity)
    rolling = _rolling_table(returns)

    metrics.to_csv(tables_dir / "metrics.csv")
    rel_summary.to_csv(tables_dir / "relative_summary.csv")
    rolling.to_csv(tables_dir / "rolling_windows.csv", index=False)
    equity.to_csv(tables_dir / "equity_curves.csv")
    rel_spy.to_csv(tables_dir / "relative_to_spy.csv")
    rel_ndx.to_csv(tables_dir / "relative_to_ndx_qqq.csv")
    _plot(equity, "Testfolio Equity Curves", "Growth of $1", plots_dir / "equity_curves.png")
    _plot(rel_spy, "Relative Equity vs SPYSIM", "Strategy / SPYSIM", plots_dir / "relative_to_spy.png")
    _plot(rel_ndx, "Relative Equity vs QQQSIM/NDX", "Strategy / QQQSIM", plots_dir / "relative_to_ndx_qqq.png")
    _write_report(metrics, rel_summary, rolling, args, returns.index)
    _write_manifest(args, returns.index)
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
    return 0


def _build_returns(args: argparse.Namespace) -> pd.DataFrame:
    qqq = load_testfolio_series("QQQSIM")
    signals = build_close_only_signals(qqq)
    names = [name for name in args.base_signals.split("|") if name]
    sig_df = pd.concat([signals[name] for name in names], axis=1)
    valid = ~sig_df.isna().any(axis=1)
    vote = ((sig_df.sum(axis=1) >= args.base_k) & valid).to_numpy(dtype=bool)

    dates = sig_df.index
    off = daily_returns(load_testfolio_series(args.off_leg)).reindex(dates)
    qld = daily_returns(load_testfolio_series("QLDSIM")).reindex(dates)
    tqqq = daily_returns(load_testfolio_series("TQQQSIM")).reindex(dates)
    spy = daily_returns(load_testfolio_series("SPYSIM")).reindex(dates)
    qqq_ret = daily_returns(qqq).reindex(dates)
    stage4_qld = pd.Series(_simulate_on_off_np(vote, qld.to_numpy(float), off.to_numpy(float)), index=dates)
    stage4_tqqq = pd.Series(_simulate_on_off_np(vote, tqqq.to_numpy(float), off.to_numpy(float)), index=dates)
    t3d = _read_returns(T3D_CANONICAL).reindex(dates)
    iter030 = _read_returns(ITER030_CANONICAL).reindex(dates)

    return pd.concat(
        {
            f"Stage4 QLD base vote / {args.off_leg}": stage4_qld,
            f"Stage4 TQQQ base vote / {args.off_leg}": stage4_tqqq,
            "SPYSIM buy_hold": spy,
            "QQQSIM/NDX buy_hold": qqq_ret,
            "T3d-K2 canonical QLD/ZROZ": t3d,
            "iter030 canonical QLD/ZROZ LRS1.20": iter030,
        },
        axis=1,
        sort=False,
    )


def _read_returns(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date")["return"].astype(float)


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    dates = pd.DatetimeIndex(returns.index)
    benchmark = returns["SPYSIM buy_hold"].to_numpy(float)
    rows = []
    for name in returns.columns:
        rows.append(_metrics_row_np(returns[name].to_numpy(float), benchmark, dates, name, "QQQ", "mixed", 0, 0, "comparison"))
    return pd.DataFrame(rows).set_index("label")


def _relative_summary(equity: pd.DataFrame) -> pd.DataFrame:
    spy = equity["SPYSIM buy_hold"]
    ndx = equity["QQQSIM/NDX buy_hold"]
    return pd.DataFrame({
        "end_equity": equity.iloc[-1],
        "end_vs_spy": equity.iloc[-1] / spy.iloc[-1],
        "end_vs_ndx_qqq": equity.iloc[-1] / ndx.iloc[-1],
        "pct_days_above_spy": equity.gt(spy, axis=0).mean(),
        "pct_days_above_ndx_qqq": equity.gt(ndx, axis=0).mean(),
    })


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in returns.columns:
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            window = years * 252
            vals = []
            if len(r) >= window:
                for end in range(window, len(r) + 1, 21):
                    sub = r.iloc[end - window:end].to_numpy(float)
                    eq = np.cumprod(1.0 + sub)
                    total = float(eq[-1] / eq[0])
                    vals.append(total ** (1.0 / years) - 1.0 if total > 0 else np.nan)
            arr = np.asarray(vals, dtype=float)
            rows.append({
                "label": label,
                "window_years": years,
                "n_windows": int(np.isfinite(arr).sum()),
                "min_cagr": float(np.nanmin(arr)) if len(arr) else np.nan,
                "median_cagr": float(np.nanmedian(arr)) if len(arr) else np.nan,
                "pct_positive_cagr": float(np.nanmean(arr > 0.0)) if len(arr) else np.nan,
            })
    return pd.DataFrame(rows)


def _plot(df: pd.DataFrame, title: str, ylabel: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    df.plot(ax=ax, logy=True, linewidth=1.6)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame, rel: pd.DataFrame, rolling: pd.DataFrame, args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    lines = [
        "# Stage 4 Testfolio Reproduction",
        "",
        "Status: long-history reproduction of the Stage 4 close-only base vote.",
        "",
        f"Window: `{index.min().date()}` to `{index.max().date()}` ({len(index):,} bars)",
        f"Off leg: `{args.off_leg}`",
        f"Base rule: `{args.base_signals}`, `k={args.base_k}`",
        "",
        "## Metrics",
        "",
        metrics[["sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "end_rel_to_benchmark", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## Relative Summary",
        "",
        rel.to_markdown(floatfmt=".4f"),
        "",
        "## Rolling Windows",
        "",
        rolling.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Plots",
        "",
        "![Equity curves](plots/equity_curves.png)",
        "",
        "![Relative to SPY](plots/relative_to_spy.png)",
        "",
        "![Relative to QQQ/NDX](plots/relative_to_ndx_qqq.png)",
        "",
        "## Interpretation",
        "",
        "The Stage 4 base vote is reproducible on testfolio because it uses only close-derived signals. This test is stricter than the Tiingo 2010+ view because it includes older crash and whipsaw regimes.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, index: pd.DatetimeIndex) -> None:
    manifest = {
        "stage": "stage4_testfolio_reproduction",
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "off_leg": args.off_leg,
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "primary_citation": "[advances_fin_ml, p.208-211]",
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
