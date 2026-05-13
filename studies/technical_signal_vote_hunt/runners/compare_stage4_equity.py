"""Compare Stage 4 base-vote equity against SPY, QQQ/NDX and LETF anchors.

The comparison is economic-first and uses the same Tiingo 2010+ operational
timing as Stage 4: `CASH_USD` off-leg and `extra_lag_days=1`. QQQ is used as the
tradable NDX proxy. T3d-K2 and iter030 are Tiingo proxies on QQQ->QLD/CASH_USD,
not the canonical long-history testfolio files `[leverage_for_the_long_run,
p.13]`, `[advances_fin_ml, p.31-34]`.
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

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from studies.technical_signal_vote_hunt.core import build_rearm_gate, build_t3d_k2_signal, daily_returns
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np
from studies.technical_signal_vote_hunt.runners.run_stage2_tiingo_ohlc import (
    BRANCHES,
    _prepare,
    _simulate_on_off_lag_np,
    _window_prepared,
)
from studies.technical_signal_vote_hunt.runners.run_stage4_regime_bridge import DEFAULT_BASE_SIGNALS, _base_vote

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/technical_signal_vote_hunt/reports/stage4_equity_benchmark_comparison"
T3D_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/original/022-2026-05-06-T3d-extended-grid/qld_voteK2_sma250_100_vol21_40_ar30_off_zroz_strategy_returns.csv"
ITER030_CANONICAL = REPO_ROOT / "studies/letf_rotation_hunt/runs/post_close/030-2026-05-10-tcrash-scan-lrs120-rearmonly/qld_voteK2_sma250_100_vol21_40_ar30_unclrs_single_rearmonly_g25_rvp70_cashx_T35D60_unclrs120_strategy_returns.csv"
TRADING_DAYS_PER_YEAR = 252


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare Stage 4 equity curves against benchmarks")
    p.add_argument("--start-date", default="2010-02-12")
    p.add_argument("--end-date", default=None)
    p.add_argument("--off-leg", choices=["CASH_USD", "BIL", "ZROZ"], default="CASH_USD")
    p.add_argument("--extra-lag-days", type=int, default=1)
    p.add_argument("--base-signals", default=DEFAULT_BASE_SIGNALS)
    p.add_argument("--base-k", type=int, default=3)
    p.add_argument("--storage-root", type=Path, default=REPO_ROOT / "data/tiingo")
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir
    tables_dir = out_dir / "tables"
    plots_dir = out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    storage = TiingoStorage(args.storage_root)
    returns = _build_returns(storage, args)
    returns = returns.loc[returns.notna().all(axis=1)]
    equity = (1.0 + returns).cumprod()
    rel_spy = equity.div(equity["SPY buy_hold"], axis=0)
    rel_ndx = equity.div(equity["NDX/QQQ buy_hold"], axis=0)

    metrics = _metrics_table(returns)
    rel_summary = _relative_summary(equity)
    metrics.to_csv(tables_dir / "metrics.csv")
    rel_summary.to_csv(tables_dir / "relative_summary.csv")
    equity.to_csv(tables_dir / "equity_curves.csv")
    rel_spy.to_csv(tables_dir / "relative_to_spy.csv")
    rel_ndx.to_csv(tables_dir / "relative_to_ndx_qqq.csv")

    _plot_equity(equity, plots_dir / "equity_curves.png")
    _plot_relative(rel_spy, "Relative Equity vs SPY", plots_dir / "relative_to_spy.png")
    _plot_relative(rel_ndx, "Relative Equity vs NDX/QQQ", plots_dir / "relative_to_ndx_qqq.png")
    _write_report(metrics, rel_summary, args, returns.index, out_dir)
    _write_manifest(args, returns.index, out_dir)
    print(f"wrote {out_dir / 'REPORT.md'}", flush=True)
    return 0


def _build_returns(storage: TiingoStorage, args: argparse.Namespace) -> pd.DataFrame:
    qld = _strategy_returns(storage, "QLD_2x", args)
    tqqq = _strategy_returns(storage, "TQQQ_3x", args)
    spy = daily_returns(_close(storage, "SPY"))
    qqq = daily_returns(_close(storage, "QQQ"))
    t3d, iter030 = _anchor_returns(storage, args)
    t3d_canonical = _read_return_csv(T3D_CANONICAL)
    iter030_canonical = _read_return_csv(ITER030_CANONICAL)
    return pd.concat(
        {
            "Stage4 QLD base vote": qld,
            "Stage4 TQQQ base vote": tqqq,
            "SPY buy_hold": spy,
            "NDX/QQQ buy_hold": qqq,
            "T3d-K2 proxy QLD/CASH": t3d,
            "iter030-like proxy QLD/CASH": iter030,
            "T3d-K2 canonical sliced": t3d_canonical,
            "iter030 canonical sliced": iter030_canonical,
        },
        axis=1,
        sort=False,
    ).loc[args.start_date:args.end_date]


def _strategy_returns(storage: TiingoStorage, risk_on: str, args: argparse.Namespace) -> pd.Series:
    prepared = _window_prepared(_prepare(BRANCHES[("QQQ", risk_on)], args.off_leg, storage), args.start_date, args.end_date)
    signal = _base_vote(prepared, args.base_signals, args.base_k)
    returns = _simulate_on_off_lag_np(signal, prepared.on_returns, prepared.off_returns, args.extra_lag_days)
    return pd.Series(returns, index=prepared.dates)


def _anchor_returns(storage: TiingoStorage, args: argparse.Namespace) -> tuple[pd.Series, pd.Series]:
    qqq_close = _close(storage, "QQQ")
    qld_returns = daily_returns(_close(storage, "QLD"))
    if args.off_leg == "CASH_USD":
        off_returns = pd.Series(0.0, index=qld_returns.index)
    else:
        off_returns = daily_returns(_close(storage, args.off_leg))
    t3d_signal = build_t3d_k2_signal(qqq_close)
    aligned = pd.concat({"sig": t3d_signal, "on": qld_returns, "off": off_returns}, axis=1, sort=False).loc[args.start_date:args.end_date].dropna(subset=["on", "off"])
    sig = aligned["sig"].fillna(0.0).to_numpy(dtype=float) >= 1.0
    t3d = pd.Series(_simulate_on_off_lag_np(sig, aligned["on"].to_numpy(float), aligned["off"].to_numpy(float), args.extra_lag_days), index=aligned.index)

    rearm = build_rearm_gate(aligned["sig"]).fillna(0.0).to_numpy(dtype=float) >= 1.0
    iter030 = pd.Series(
        _simulate_iter030_like_lag_np(
            sig,
            rearm,
            aligned["on"].to_numpy(float),
            aligned["off"].to_numpy(float),
            args.extra_lag_days,
        ),
        index=aligned.index,
    )
    return t3d, iter030


def _simulate_iter030_like_lag_np(
    signal: np.ndarray,
    rearm: np.ndarray,
    on_returns: np.ndarray,
    off_returns: np.ndarray,
    extra_lag_days: int,
    lrs_factor: float = 1.20,
) -> np.ndarray:
    lag = 1 + extra_lag_days
    sig_lag = np.zeros_like(signal, dtype=bool)
    rearm_lag = np.zeros_like(rearm, dtype=bool)
    if lag < len(signal):
        sig_lag[lag:] = signal[:-lag]
        rearm_lag[lag:] = rearm[:-lag]
    on_leg = np.where(rearm_lag, on_returns * lrs_factor, on_returns)
    return np.where(sig_lag, on_leg, off_returns)


def _close(storage: TiingoStorage, ticker: str) -> pd.Series:
    return storage.read(ticker, frequency="daily")["adj_close"].astype(float)


def _read_return_csv(path: Path) -> pd.Series:
    df = pd.read_csv(path, parse_dates=["date"])
    return df.set_index("date")["return"].astype(float)


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    dates = pd.DatetimeIndex(returns.index)
    benchmark = returns["SPY buy_hold"].to_numpy(float)
    for name in returns.columns:
        row = _metrics_row_np(
            returns=returns[name].to_numpy(float),
            benchmark_returns=benchmark,
            dates=dates,
            label=name,
            branch="QQQ",
            risk_on="mixed",
            n=0,
            k=0,
            signals="comparison",
        )
        rows.append(row)
    return pd.DataFrame(rows).set_index("label")


def _relative_summary(equity: pd.DataFrame) -> pd.DataFrame:
    spy = equity["SPY buy_hold"]
    ndx = equity["NDX/QQQ buy_hold"]
    return pd.DataFrame(
        {
            "end_equity": equity.iloc[-1],
            "end_vs_spy": equity.iloc[-1] / spy.iloc[-1],
            "end_vs_ndx_qqq": equity.iloc[-1] / ndx.iloc[-1],
            "pct_days_above_spy": equity.gt(spy, axis=0).mean(),
            "pct_days_above_ndx_qqq": equity.gt(ndx, axis=0).mean(),
        }
    )


def _plot_equity(equity: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    equity.plot(ax=ax, logy=True, linewidth=1.8)
    ax.set_title("Equity Curves, Log Scale")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _plot_relative(relative: pd.DataFrame, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    relative.plot(ax=ax, logy=True, linewidth=1.8)
    ax.axhline(1.0, color="black", linewidth=1.0, alpha=0.5)
    ax.set_title(title)
    ax.set_ylabel("Strategy equity / benchmark equity")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _write_report(metrics: pd.DataFrame, rel: pd.DataFrame, args: argparse.Namespace, index: pd.DatetimeIndex, out_dir: Path) -> None:
    lines = [
        "# Stage 4 Equity vs Benchmarks",
        "",
        "Status: economic-first comparison. QQQ is used as tradable NDX proxy. The table includes both Tiingo QQQ->QLD/CASH proxies and canonical testfolio anchor returns sliced to the same window.",
        "",
        f"Window: `{index.min().date()}` to `{index.max().date()}` ({len(index):,} bars)",
        f"Off leg: `{args.off_leg}`",
        f"Extra lag days: `{args.extra_lag_days}`",
        f"Stage 4 base rule: `{args.base_signals}`, `k={args.base_k}`",
        "",
        "## Metrics",
        "",
        metrics[["sortino", "cagr", "sharpe", "mdd", "calmar", "end_mult", "end_rel_to_benchmark", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## Relative Summary",
        "",
        rel.to_markdown(floatfmt=".4f"),
        "",
        "## Plots",
        "",
        "![Equity curves](plots/equity_curves.png)",
        "",
        "![Relative to SPY](plots/relative_to_spy.png)",
        "",
        "![Relative to NDX/QQQ](plots/relative_to_ndx_qqq.png)",
        "",
        "## Method Notes",
        "",
        "- Stage 4 strategies use the same `CASH_USD + extra_lag_days=1` timing from the regime bridge.",
        "- T3d-K2 proxy uses the QQQ T3d-K2 vote into QLD/CASH with the same extra lag.",
        "- iter030-like proxy adds the documented T35D60 rearm and LRS1.20 multiplier to the T3d-K2 proxy `[leverage_for_the_long_run, p.5-7]`.",
        "- Canonical sliced rows come directly from the preserved `letf_rotation_hunt` return CSVs and are included to avoid conflating proxies with original anchors.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(args: argparse.Namespace, index: pd.DatetimeIndex, out_dir: Path) -> None:
    manifest = {
        "stage": "stage4_equity_benchmark_comparison",
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "off_leg": args.off_leg,
        "extra_lag_days": args.extra_lag_days,
        "base_signals": args.base_signals,
        "base_k": args.base_k,
        "ndx_proxy": "QQQ",
        "primary_citation": "[leverage_for_the_long_run, p.13]",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
