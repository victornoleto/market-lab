"""Baseline report for SPY/SSO/UPRO leveraged rotation.

Signals are lagged by one trading day before execution to avoid same-close
lookahead. Canonical LRS uses SPY > SMA200 `[leverage_for_the_long_run, p.13]`;
the T3d-style vote combines trend, realized-volatility and AR(1) components
motivated by LETF volatility decay and regime persistence
`[leverage_for_the_long_run, p.5-7]`.
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

from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series
from studies.technical_signal_vote_hunt.core import build_t3d_k2_signal, daily_returns, sma
from studies.technical_signal_vote_hunt.runners.run_stage1_close_only_fast import _metrics_row_np, _simulate_on_off_np


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = REPO_ROOT / "studies/spy_leveraged_rotation_hunt/reports/baseline"
TRADING_DAYS_PER_YEAR = 252


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate SPY leveraged rotation baseline report")
    p.add_argument("--off-leg", choices=["CASHX", "ZROZSIM"], default="CASHX")
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    tables_dir = args.out_dir / "tables"
    plots_dir = args.out_dir / "plots"
    tables_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    prices = _load_prices(args.off_leg)
    returns = {k: daily_returns(v) for k, v in prices.items()}
    strategy_returns = _build_strategy_returns(prices, returns)
    aligned = pd.concat(strategy_returns, axis=1, sort=False).dropna()

    metrics = _metrics_table(aligned)
    rolling = _rolling_table(aligned)
    rel = (1.0 + aligned).cumprod().div((1.0 + aligned["SPY buy_hold"]).cumprod(), axis=0)

    aligned.to_csv(tables_dir / "baseline_returns.csv")
    metrics.to_csv(tables_dir / "baseline_metrics.csv")
    rolling.to_csv(tables_dir / "baseline_rolling_windows.csv", index=False)
    rel.to_csv(tables_dir / "baseline_relative_to_spy.csv")

    _plot_equity(aligned, plots_dir / "baseline_equity.png")
    _plot_drawdown(aligned, plots_dir / "baseline_drawdown.png")
    _plot_relative(rel, plots_dir / "baseline_relative_to_spy.png")
    _write_report(args.out_dir, metrics, rolling, args.off_leg, aligned.index)
    _write_manifest(args.out_dir, args, aligned.index, len(strategy_returns))
    print(f"wrote {args.out_dir / 'REPORT.md'}", flush=True)
    return 0


def _load_prices(off_leg: str) -> dict[str, pd.Series]:
    return {
        "SPY": load_testfolio_series("SPYSIM"),
        "SSO": load_testfolio_series("SSOSIM"),
        "UPRO": load_testfolio_series("UPROSIM"),
        "OFF": load_testfolio_series(off_leg),
    }


def _build_strategy_returns(prices: dict[str, pd.Series], returns: dict[str, pd.Series]) -> dict[str, pd.Series]:
    spy_lrs = _sma200_signal(prices["SPY"])
    spy_t3d = build_t3d_k2_signal(prices["SPY"])
    sso_t3d = build_t3d_k2_signal(prices["SSO"])
    return {
        "SPY buy_hold": returns["SPY"],
        "SSO buy_hold": returns["SSO"],
        "UPRO buy_hold": returns["UPRO"],
        "LRS SPY->SSO": _on_off(spy_lrs, returns["SSO"], returns["OFF"]),
        "LRS SPY->UPRO": _on_off(spy_lrs, returns["UPRO"], returns["OFF"]),
        "T3d SPY->SSO": _on_off(spy_t3d, returns["SSO"], returns["OFF"]),
        "T3d SPY->UPRO": _on_off(spy_t3d, returns["UPRO"], returns["OFF"]),
        "T3d SSO->SSO": _on_off(sso_t3d, returns["SSO"], returns["OFF"]),
        "T3d SSO->UPRO": _on_off(sso_t3d, returns["UPRO"], returns["OFF"]),
    }


def _sma200_signal(prices: pd.Series) -> pd.Series:
    ma = sma(prices.astype(float), 200)
    out = (prices > ma).astype(float)
    out[ma.isna()] = np.nan
    return out


def _on_off(signal: pd.Series, on_returns: pd.Series, off_returns: pd.Series) -> pd.Series:
    aligned = pd.concat({"sig": signal, "on": on_returns, "off": off_returns}, axis=1, sort=False).dropna(subset=["on", "off"])
    sig = aligned["sig"].fillna(0.0).to_numpy(float) >= 1.0
    daily = _simulate_on_off_np(sig, aligned["on"].to_numpy(float), aligned["off"].to_numpy(float))
    return pd.Series(daily, index=aligned.index)


def _metrics_table(returns: pd.DataFrame) -> pd.DataFrame:
    bench = returns["SPY buy_hold"].to_numpy(float)
    dates = pd.DatetimeIndex(returns.index)
    rows = []
    for label in returns.columns:
        rows.append(_metrics_row_np(returns[label].to_numpy(float), bench, dates, label, "SPY", "baseline", 0, 0, "baseline"))
    return pd.DataFrame(rows).set_index("label").sort_values(["sortino", "cagr", "calmar"], ascending=[False, False, False])


def _rolling_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in returns.columns:
        r = returns[label].dropna()
        for years in (3, 5, 10, 15):
            vals = (1.0 + r).rolling(years * TRADING_DAYS_PER_YEAR).apply(np.prod, raw=True).dropna()
            cagr = vals ** (1.0 / years) - 1.0
            rows.append(
                {
                    "label": label,
                    "years": years,
                    "min_cagr": float(cagr.min()) if len(cagr) else np.nan,
                    "median_cagr": float(cagr.median()) if len(cagr) else np.nan,
                    "pct_positive": float((cagr > 0.0).mean()) if len(cagr) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def _drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1.0


def _plot_equity(returns: pd.DataFrame, path: Path) -> None:
    equity = (1.0 + returns).cumprod()
    ax = equity.plot(figsize=(12, 7), logy=True, linewidth=1.2)
    ax.set_title("SPY Leveraged Rotation Baselines")
    ax.set_ylabel("Growth of $1, log scale")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _plot_drawdown(returns: pd.DataFrame, path: Path) -> None:
    dd = (1.0 + returns).cumprod().apply(_drawdown)
    ax = dd.plot(figsize=(12, 7), linewidth=1.0)
    ax.set_title("Drawdowns")
    ax.set_ylabel("Drawdown")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _plot_relative(relative: pd.DataFrame, path: Path) -> None:
    ax = relative.plot(figsize=(12, 7), logy=True, linewidth=1.0)
    ax.set_title("Relative Equity vs SPY Buy-Hold")
    ax.set_ylabel("Strategy / SPY, log scale")
    ax.grid(True, alpha=0.3)
    ax.figure.tight_layout()
    ax.figure.savefig(path, dpi=140)
    plt.close(ax.figure)


def _write_report(out_dir: Path, metrics: pd.DataFrame, rolling: pd.DataFrame, off_leg: str, index: pd.DatetimeIndex) -> None:
    spy = metrics.loc["SPY buy_hold"]
    beaters = metrics[(metrics["cagr"] > spy["cagr"]) & (metrics["sharpe"] > spy["sharpe"]) & (metrics["sortino"] > spy["sortino"]) & (metrics["mdd"] > spy["mdd"])]
    roll_pivot = rolling.pivot(index="label", columns="years", values="min_cagr")
    roll_pivot = roll_pivot.rename(columns={3: "3y_min", 5: "5y_min", 10: "10y_min", 15: "15y_min"})
    lines = [
        "# SPY Leveraged Rotation Baseline Report",
        "",
        f"Window: `{index.min().date()}..{index.max().date()}`",
        f"Risk-off leg: `{off_leg}`",
        "",
        "## Initial Screen",
        "",
        f"Strategies beating `SPY buy_hold` on CAGR, Sharpe, Sortino and MaxDD: `{len(beaters)}`.",
        "",
        beaters[["cagr", "sharpe", "sortino", "mdd", "calmar", "end_mult"]].to_markdown(floatfmt=".4f") if len(beaters) else "No baseline strategy clears the full economic screen versus SPY.",
        "",
        "## Headline Metrics",
        "",
        metrics[["cagr", "sharpe", "sortino", "mdd", "calmar", "end_mult", "end_rel_to_benchmark", "pct_above_benchmark"]].to_markdown(floatfmt=".4f"),
        "",
        "## Minimum Rolling CAGR",
        "",
        roll_pivot.to_markdown(floatfmt=".4f"),
        "",
        "## Method Notes",
        "",
        "All switching signals are executed with a one-day lag. LRS uses `SPY > SMA200` per Gayed `[leverage_for_the_long_run, p.13]`. T3d-style votes use price/SMA, realized-volatility and AR(1) components; volatility gates reflect LETF decay risk `[leverage_for_the_long_run, p.5-7]`.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(out_dir: Path, args: argparse.Namespace, index: pd.DatetimeIndex, n_strategies: int) -> None:
    data = {
        "off_leg": args.off_leg,
        "start": str(index.min().date()),
        "end": str(index.max().date()),
        "n_strategies": int(n_strategies),
        "report": str(out_dir / "REPORT.md"),
    }
    (out_dir / "manifest.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
