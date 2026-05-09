#!/usr/bin/env python3
"""Quick QLD/Nasdaq-100 46-week high-watermark gate study.

Rule under test: hold QQQSIM?L=2 when QQQSIM closes above 85% of its trailing
46-week high-watermark; otherwise hold cash/T-bills. The rule is a fixed
trend/risk gate in the leverage-rotation family: leveraged equity when risk-on,
cash/T-bills when risk-off `[leverage_for_the_long_run, p.13, p.21]`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from market_lab.backtest.data.testfolio_loader import load_testfolio_frame, load_testfolio_meta
from market_lab.backtest.metrics.performance import sortino


TRADING_DAYS_PER_YEAR = 252
STUDY_ROOT = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = STUDY_ROOT / "results" / "default"


@dataclass(frozen=True)
class Config:
    signal_ticker: str = "QQQSIM"
    risk_on_ticker: str = "QQQSIM?L=2"
    risk_off_ticker: str = "CASHX"
    comparison_ticker: str = "QQQSIM?L=3"
    threshold_pct: float = 0.85
    lookback_weeks: int = 46
    initial_cash: float = 10_000.0
    signal_freq: str = "W-FRI"
    out_dir: str = str(DEFAULT_OUT_DIR)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QLD Nasdaq ATH gate study")
    parser.add_argument("--signal-ticker", default="QQQSIM")
    parser.add_argument("--risk-on-ticker", default="QQQSIM?L=2")
    parser.add_argument("--risk-off-ticker", default="CASHX")
    parser.add_argument("--comparison-ticker", default="QQQSIM?L=3")
    parser.add_argument("--threshold-pct", type=float, default=0.85)
    parser.add_argument("--lookback-weeks", type=int, default=46)
    parser.add_argument("--initial-cash", type=float, default=10_000.0)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = Config(
        signal_ticker=args.signal_ticker,
        risk_on_ticker=args.risk_on_ticker,
        risk_off_ticker=args.risk_off_ticker,
        comparison_ticker=args.comparison_ticker,
        threshold_pct=args.threshold_pct,
        lookback_weeks=args.lookback_weeks,
        initial_cash=args.initial_cash,
        out_dir=args.out_dir,
    )
    bundle = run_study(config)
    write_outputs(config, bundle)
    metrics = bundle["metrics"]
    print(f"outputs={config.out_dir}")
    print(f"date_start={bundle['date_start']}")
    print(f"date_end={bundle['date_end']}")
    print(f"strategy_cagr={metrics['strategy']['cagr']:.6f}")
    print(f"strategy_mdd={metrics['strategy']['mdd']:.6f}")
    print(f"strategy_sharpe={metrics['strategy']['sharpe']:.6f}")
    print(f"signal_cagr={metrics['signal']['cagr']:.6f}")
    print(f"risk_on_cagr={metrics['risk_on']['cagr']:.6f}")
    print(f"comparison_cagr={metrics['comparison']['cagr']:.6f}")
    return 0


def run_study(config: Config) -> dict[str, Any]:
    signal_prices = load_testfolio_series_with_alias(config.signal_ticker)
    risk_on_prices = load_testfolio_series_with_alias(config.risk_on_ticker)
    risk_off_prices = load_testfolio_series_with_alias(config.risk_off_ticker)
    comparison_prices = load_testfolio_series_with_alias(config.comparison_ticker)

    prices = pd.concat(
        {
            "signal": signal_prices,
            "risk_on": risk_on_prices,
            "risk_off": risk_off_prices,
            "comparison": comparison_prices,
        },
        axis=1,
        sort=True,
    ).dropna()
    if prices.empty:
        raise ValueError("No overlapping testfol.io history")

    signal = build_signal(prices["signal"], config)
    signal_daily = signal.reindex(prices.index).ffill().dropna()
    prices = prices.loc[signal_daily.index]
    exposure = signal_daily["risk_on"].astype(float).shift(1).fillna(0.0).rename("risk_on_weight")

    risk_on_returns = prices["risk_on"].pct_change(fill_method=None).fillna(0.0)
    signal_returns = prices["signal"].pct_change(fill_method=None).fillna(0.0)
    risk_off_returns = prices["risk_off"].pct_change(fill_method=None).fillna(0.0)
    comparison_returns = prices["comparison"].pct_change(fill_method=None).fillna(0.0)
    strategy_returns = (exposure * risk_on_returns + (1.0 - exposure) * risk_off_returns).rename("strategy")

    equity = pd.DataFrame(
        {
            "strategy": equity_from_returns(strategy_returns, config.initial_cash),
            "signal": equity_from_returns(signal_returns, config.initial_cash),
            "risk_on": equity_from_returns(risk_on_returns, config.initial_cash),
            "comparison": equity_from_returns(comparison_returns, config.initial_cash),
            "risk_off": equity_from_returns(risk_off_returns, config.initial_cash),
        }
    )
    returns = pd.DataFrame(
        {
            "strategy": strategy_returns,
            "signal": signal_returns,
            "risk_on": risk_on_returns,
            "comparison": comparison_returns,
            "risk_off": risk_off_returns,
        }
    )
    signal_daily = signal_daily.assign(risk_on_weight=exposure)
    trades = build_trade_log(exposure, config)
    metrics = {col: compute_metrics(equity[col], returns[col]) for col in equity.columns}
    rolling_summary = compute_rolling_summary(equity)

    return {
        "config": asdict(config),
        "date_start": str(equity.index.min().date()),
        "date_end": str(equity.index.max().date()),
        "equity": equity,
        "returns": returns,
        "signal": signal_daily,
        "trades": trades,
        "metrics": metrics,
        "rolling_summary": rolling_summary,
    }


def load_testfolio_series_with_alias(ticker: str) -> pd.Series:
    """Load testfol.io series, resolving exported ``?L`` aliases when needed.

    The cache stores common leveraged exports under readable names such as
    ``QLDSIM`` and keeps the original ``QQQSIM?L=2`` mapping in metadata. The
    ``?L`` syntax keeps the study aligned with testfol.io leverage notation while
    using the compact local parquet cache `[leverage_for_the_long_run, p.21]`.
    """
    df = load_testfolio_frame()
    key = ticker.upper()
    if key not in df.columns:
        rename_map = {k.upper(): v for k, v in load_testfolio_meta().get("label_rename_map", {}).items()}
        key = rename_map.get(key, key)
    if key not in df.columns:
        raise KeyError(f"ticker {ticker!r} not in testfol.io cache — available: {list(df.columns)}")
    series = df[key].astype(float)
    series.name = ticker.upper()
    return series.sort_index()


def build_signal(signal_prices: pd.Series, config: Config) -> pd.DataFrame:
    """Weekly close above 85% of 46-week high watermark.

    The line is intentionally simple and not optimized. It is a high-watermark
    trend gate, conceptually adjacent to breakout/high-channel filters described
    in Kaufman `[trading_systems_methods, p.353]`.
    """
    weekly = signal_prices.resample(config.signal_freq).last().dropna().rename("signal_weekly_close")
    high = weekly.rolling(config.lookback_weeks, min_periods=config.lookback_weeks).max().rename("trailing_high")
    line = (high * config.threshold_pct).rename("signal_line")
    risk_on = (weekly > line).rename("risk_on")
    out = pd.concat([weekly, high, line, risk_on], axis=1).dropna()
    return out


def equity_from_returns(returns: pd.Series, initial_cash: float) -> pd.Series:
    equity = (1.0 + returns.fillna(0.0)).cumprod() * initial_cash
    return equity.astype(float)


def build_trade_log(exposure: pd.Series, config: Config) -> pd.DataFrame:
    changed = exposure.ne(exposure.shift(1)).fillna(False)
    rows = []
    for ts, value in exposure.loc[changed].items():
        target = config.risk_on_ticker if value >= 0.5 else config.risk_off_ticker
        rows.append({"date": ts, "target": target, "risk_on_weight": float(value)})
    return pd.DataFrame(rows, columns=["date", "target", "risk_on_weight"])


def compute_metrics(equity: pd.Series, returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    equity = equity.dropna()
    years = len(returns) / TRADING_DAYS_PER_YEAR
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    cagr = float((equity.iloc[-1] / equity.iloc[0]) ** (1.0 / years) - 1.0) if years > 0 else np.nan
    drawdown = equity / equity.cummax() - 1.0
    std = float(returns.std(ddof=1))
    sharpe = float(returns.mean() / std * np.sqrt(TRADING_DAYS_PER_YEAR)) if std > 0 else 0.0
    return {
        "total_return": total_return,
        "cagr": cagr,
        "mdd": float(drawdown.min()),
        "sharpe": sharpe,
        "sortino": float(sortino(returns, periods_per_year=TRADING_DAYS_PER_YEAR)),
        "calmar": float(cagr / abs(drawdown.min())) if drawdown.min() < 0 else float("inf"),
        "vol_annual": float(std * np.sqrt(TRADING_DAYS_PER_YEAR)),
        "best_day": float(returns.max()),
        "worst_day": float(returns.min()),
    }


def compute_rolling_summary(equity: pd.DataFrame, windows_years: tuple[int, ...] = (1, 3, 5, 10)) -> pd.DataFrame:
    rows = []
    for years in windows_years:
        window = years * TRADING_DAYS_PER_YEAR
        if len(equity) <= window:
            rows.append({"window_years": years, "n_obs": 0})
            continue
        rolling = (equity / equity.shift(window)) ** (1.0 / years) - 1.0
        edge_signal = rolling["strategy"] - rolling["signal"]
        edge_risk_on = rolling["strategy"] - rolling["risk_on"]
        edge_comparison = rolling["strategy"] - rolling["comparison"]
        rows.append(
            {
                "window_years": years,
                "n_obs": int(edge_signal.dropna().shape[0]),
                "strategy_median_cagr": float(rolling["strategy"].median()),
                "signal_median_cagr": float(rolling["signal"].median()),
                "risk_on_median_cagr": float(rolling["risk_on"].median()),
                "comparison_median_cagr": float(rolling["comparison"].median()),
                "win_rate_vs_signal": float((edge_signal.dropna() > 0).mean()),
                "win_rate_vs_risk_on": float((edge_risk_on.dropna() > 0).mean()),
                "win_rate_vs_comparison": float((edge_comparison.dropna() > 0).mean()),
                "median_edge_vs_signal": float(edge_signal.median()),
                "median_edge_vs_risk_on": float(edge_risk_on.median()),
                "median_edge_vs_comparison": float(edge_comparison.median()),
                "worst_edge_vs_signal": float(edge_signal.min()),
                "worst_edge_vs_risk_on": float(edge_risk_on.min()),
                "worst_edge_vs_comparison": float(edge_comparison.min()),
            }
        )
    return pd.DataFrame(rows)


def write_outputs(config: Config, bundle: dict[str, Any]) -> None:
    out_dir = Path(config.out_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    bundle["equity"].to_csv(out_dir / "equity.csv")
    bundle["returns"].to_csv(out_dir / "returns.csv")
    bundle["signal"].to_csv(out_dir / "signal.csv")
    bundle["trades"].to_csv(out_dir / "trades.csv", index=False)
    bundle["rolling_summary"].to_csv(out_dir / "rolling_summary.csv", index=False)
    (out_dir / "config.json").write_text(json.dumps(bundle["config"], indent=2) + "\n", encoding="utf-8")

    metrics_payload = {
        "date_start": bundle["date_start"],
        "date_end": bundle["date_end"],
        "config": bundle["config"],
        "metrics": jsonify(bundle["metrics"]),
        "rolling_summary": bundle["rolling_summary"].to_dict(orient="records"),
        "n_trades": int(len(bundle["trades"])),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics_payload, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(bundle["metrics"]).to_csv(out_dir / "metrics.csv")

    plot_equity(bundle["equity"], config, plots_dir / "equity.png")
    plot_drawdown(bundle["equity"], config, plots_dir / "drawdown.png")
    plot_signal(bundle["signal"], config, plots_dir / "signal_line.png")
    plot_rolling_sharpe(bundle["returns"], config, plots_dir / "rolling_sharpe_1y.png")
    plot_rolling_windows(bundle["equity"], config, plots_dir / "rolling_windows_1_3_5_10y.png")
    write_report(out_dir / "report.md", config, bundle)


def series_labels(config: Config) -> dict[str, str]:
    return {
        "strategy": "Strategy",
        "signal": config.signal_ticker,
        "risk_on": config.risk_on_ticker,
        "comparison": config.comparison_ticker,
        "risk_off": config.risk_off_ticker,
    }


def plot_equity(equity: pd.DataFrame, config: Config, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    labels = series_labels(config)
    styles = {"strategy": "-", "signal": "--", "risk_on": ":", "comparison": (0, (3, 1, 1, 1)), "risk_off": "-."}
    for col, style in styles.items():
        ax.plot(equity.index, equity[col], label=labels[col], linewidth=1.4, linestyle=style)
    ax.set_yscale("log")
    ax.set_title("Nasdaq ATH gate: strategy vs testfol.io benchmarks")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_drawdown(equity: pd.DataFrame, config: Config, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    labels = series_labels(config)
    styles = {"strategy": "-", "signal": "--", "risk_on": ":", "comparison": (0, (3, 1, 1, 1)), "risk_off": "-."}
    for col, style in styles.items():
        dd = equity[col] / equity[col].cummax() - 1.0
        ax.plot(dd.index, dd * 100.0, label=labels[col], linewidth=1.3, linestyle=style)
    ax.set_title("Drawdown")
    ax.set_ylabel("Drawdown (%)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_signal(signal: pd.DataFrame, config: Config, out_path: Path) -> None:
    weekly = signal[["signal_weekly_close", "signal_line", "risk_on"]].resample(config.signal_freq).last().dropna().copy()
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(weekly.index, weekly["signal_weekly_close"], label=f"{config.signal_ticker} weekly close", linewidth=1.3)
    ax.plot(weekly.index, weekly["signal_line"], label=f"{config.threshold_pct:.0%} of trailing {config.lookback_weeks}-week high", linewidth=1.3)
    off = weekly[~weekly["risk_on"].astype(bool)]
    if not off.empty:
        ax.scatter(off.index, off["signal_weekly_close"], s=9, color="#d62728", label="Risk-off weekly close", alpha=0.7)
    ax.set_yscale("log")
    ax.set_title(f"{config.signal_ticker} signal line")
    ax.set_ylabel(f"{config.signal_ticker} value (log scale)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_rolling_sharpe(returns: pd.DataFrame, config: Config, out_path: Path, window_days: int = 252) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    labels = series_labels(config)
    for col, style in [("strategy", "-"), ("signal", "--"), ("risk_on", ":"), ("comparison", "-.")]:
        rolling = returns[col].rolling(window_days).mean() / returns[col].rolling(window_days).std(ddof=1)
        rolling = rolling * np.sqrt(TRADING_DAYS_PER_YEAR)
        ax.plot(rolling.index, rolling, label=labels[col], linewidth=1.2, linestyle=style)
    ax.axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    ax.set_title("Rolling 1-year Sharpe")
    ax.set_ylabel("Sharpe")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_rolling_windows(equity: pd.DataFrame, config: Config, out_path: Path, windows_years: tuple[int, ...] = (1, 3, 5, 10)) -> None:
    """Plot rolling CAGRs for regime stability `[trading_systems_methods, ch.21]`."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, years in zip(axes.ravel(), windows_years, strict=True):
        window = years * TRADING_DAYS_PER_YEAR
        if len(equity) <= window:
            ax.text(0.5, 0.5, f"Insufficient data for {years}y", ha="center", va="center")
            ax.set_title(f"{years}y rolling CAGR")
            continue
        rolling = (equity / equity.shift(window)) ** (1.0 / years) - 1.0
        ax.plot(rolling.index, rolling["strategy"] * 100.0, label="Strategy", linewidth=1.2)
        ax.plot(rolling.index, rolling["signal"] * 100.0, label=config.signal_ticker, linewidth=1.1, linestyle="--", color="black")
        ax.plot(rolling.index, rolling["risk_on"] * 100.0, label=config.risk_on_ticker, linewidth=1.1, linestyle=":", color="#ff7f0e")
        edge = rolling["strategy"] - rolling["signal"]
        ax.fill_between(edge.index, 0, edge.values * 100.0, where=edge.values >= 0, color="#16a34a", alpha=0.15)
        ax.fill_between(edge.index, 0, edge.values * 100.0, where=edge.values < 0, color="#d62728", alpha=0.14)
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.5)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Rolling windows: strategy vs signal/risk-on benchmarks", y=0.995)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def write_report(out_path: Path, config: Config, bundle: dict[str, Any]) -> None:
    metrics = bundle["metrics"]
    rolling = bundle["rolling_summary"]
    trades = bundle["trades"]
    labels = series_labels(config)
    latest_trades = trades.tail(12).copy()
    if not latest_trades.empty:
        latest_trades["date"] = latest_trades["date"].astype(str)

    lines = [
        "# QLD Nasdaq ATH Gate Report",
        "",
        "## Strategy",
        "",
        f"- Rule: hold `{config.risk_on_ticker}` when `{config.signal_ticker}` is above `{config.threshold_pct:.0%}` of its trailing `{config.lookback_weeks}` weekly closes high-watermark; otherwise hold `{config.risk_off_ticker}`.",
        f"- Signal proxy: `{config.signal_ticker}` long-history Nasdaq-100 proxy from testfol.io; risk-on asset: `{config.risk_on_ticker}`; comparison leverage: `{config.comparison_ticker}`; risk-off asset: `{config.risk_off_ticker}`.",
        "- Timing: weekly signal is forward-filled and shifted one trading day before allocation to avoid same-close look-ahead.",
        "- Source rationale: leveraged equity above a risk gate and cash/T-bills below follows the LRS family `[leverage_for_the_long_run, p.13, p.21]`.",
        "- High-watermark/breakout-style filters are a classic trend-following family `[trading_systems_methods, p.353]`.",
        "",
        "## Result Summary",
        "",
        f"- Date range: `{bundle['date_start']}` to `{bundle['date_end']}`.",
        f"- Trade events: `{len(trades)}`.",
        f"- Strategy CAGR: `{fmt_pct(metrics['strategy']['cagr'])}` vs {config.signal_ticker} `{fmt_pct(metrics['signal']['cagr'])}` vs {config.risk_on_ticker} `{fmt_pct(metrics['risk_on']['cagr'])}` vs {config.comparison_ticker} `{fmt_pct(metrics['comparison']['cagr'])}`.",
        f"- Strategy MDD: `{fmt_pct(metrics['strategy']['mdd'])}` vs {config.signal_ticker} `{fmt_pct(metrics['signal']['mdd'])}` vs {config.risk_on_ticker} `{fmt_pct(metrics['risk_on']['mdd'])}` vs {config.comparison_ticker} `{fmt_pct(metrics['comparison']['mdd'])}`.",
        f"- Strategy Sharpe: `{metrics['strategy']['sharpe']:.3f}` vs {config.signal_ticker} `{metrics['signal']['sharpe']:.3f}` vs {config.risk_on_ticker} `{metrics['risk_on']['sharpe']:.3f}` vs {config.comparison_ticker} `{metrics['comparison']['sharpe']:.3f}`.",
        f"- Terminal wealth vs {config.signal_ticker}: `{bundle['equity']['strategy'].iloc[-1] / bundle['equity']['signal'].iloc[-1]:.2f}x`; vs {config.risk_on_ticker}: `{bundle['equity']['strategy'].iloc[-1] / bundle['equity']['risk_on'].iloc[-1]:.2f}x`; vs {config.comparison_ticker}: `{bundle['equity']['strategy'].iloc[-1] / bundle['equity']['comparison'].iloc[-1]:.2f}x`.",
        "",
        "## Metrics",
        "",
        f"| metric | {labels['strategy']} | {labels['signal']} | {labels['risk_on']} | {labels['comparison']} | {labels['risk_off']} |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in ["total_return", "cagr", "mdd", "sharpe", "sortino", "calmar", "vol_annual", "best_day", "worst_day"]:
        lines.append(
            f"| {metric} | {fmt_metric(metric, metrics['strategy'][metric])} | {fmt_metric(metric, metrics['signal'][metric])} | {fmt_metric(metric, metrics['risk_on'][metric])} | {fmt_metric(metric, metrics['comparison'][metric])} | {fmt_metric(metric, metrics['risk_off'][metric])} |"
        )

    lines.extend([
        "",
        "## Rolling Windows",
        "",
        "Rolling windows test whether the full-period result survives different start/end regimes `[trading_systems_methods, ch.21]`.",
        "",
    ])
    lines.append(rolling.to_markdown(index=False, floatfmt=".4f"))

    lines.extend([
        "",
        "## Plots",
        "",
        "![Equity](plots/equity.png)",
        "",
        "![Drawdown](plots/drawdown.png)",
        "",
        "![Signal Line](plots/signal_line.png)",
        "",
        "![Rolling Sharpe](plots/rolling_sharpe_1y.png)",
        "",
        "![Rolling Windows](plots/rolling_windows_1_3_5_10y.png)",
        "",
        "## Recent Trades",
        "",
    ])
    lines.append(latest_trades.to_markdown(index=False) if not latest_trades.empty else "No trade events.")
    lines.extend([
        "",
        "## Caveats",
        "",
        "- This is a fast diagnostic, not a deployable strategy verdict.",
        "- testfol.io `QQQSIM` extends Nasdaq-100 proxy history before live QQQ/QLD/TQQQ inception; pre-inception bars are modelled approximations, not directly tradeable history.",
        "- Leveraged specs such as `QQQSIM?L=2` and `QQQSIM?L=3` are resolved to local cache aliases (`QLDSIM`, `TQQQSIM`) when available.",
        "- Costs, taxes, slippage, market impact and operational execution are not modeled.",
        "- No PBO, DSR, walk-forward, bootstrap or cross-library gate is run here, so mandate promotion is not implied.",
        f"- {config.risk_off_ticker} is a testfol.io cash/T-bill proxy and not a broker-specific cash sweep implementation.",
        "",
    ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


def jsonify(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: jsonify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [jsonify(v) for v in value]
    if isinstance(value, float):
        if np.isposinf(value):
            return "Infinity"
        if np.isneginf(value):
            return "-Infinity"
        if np.isnan(value):
            return "NaN"
        return value
    return value


def fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%" if np.isfinite(value) else str(value)


def fmt_metric(metric: str, value: float) -> str:
    if metric in {"total_return", "cagr", "mdd", "vol_annual", "best_day", "worst_day"}:
        return fmt_pct(value)
    if np.isposinf(value):
        return "+inf"
    if np.isneginf(value):
        return "-inf"
    return f"{value:.3f}" if np.isfinite(value) else "nan"


if __name__ == "__main__":
    raise SystemExit(main())
