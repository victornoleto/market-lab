#!/usr/bin/env python3
"""ETF-focused evolution for weekly_momentum.

This runner is intentionally separate from the closed stock study. It tests an
ETF-specific hypothesis: ETF universes are smaller and more correlated than
single-stock universes, so the search should emphasize broader top-K sleeves,
explicit defensive ETFs, and optional exclusion of leveraged/inverse products
instead of only transplanting the stock parameters. Cross-sectional momentum and
trend-risk filters follow Clenow's momentum/risk-filter framing
``[stocks_on_the_move, p.60]`` and ``[stocks_on_the_move, p.66-67, p.81]``;
walk-forward selection pays the train/test separation cost discussed by Lopez de
Prado ``[advances_fin_ml, p.208-211]``.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from market_lab.backtest.metrics.standard_report import load_spy_series
from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.validation.pbo import pbo as compute_pbo
from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices
from studies.weekly_momentum.reporting import compute_report_metrics, config_slug
from studies.weekly_momentum.scripts.sweep import rolling_edge_metrics
from studies.weekly_momentum.scripts.walk_forward import _parse_ints, _parse_market_filters


LEVERAGED_OR_INVERSE = {
    "QLD", "SOXL", "SSO", "TMF", "TQQQ", "UGL", "UPRO", "UVXY", "VIXM", "VIXY", "VXX",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ETF-focused weekly momentum evolution")
    parser.add_argument("--lookbacks", default="60,80,100,126,168,252")
    parser.add_argument("--top-ks", default="5,10,15,20")
    parser.add_argument("--market-filters", default="sma100,sma150,sma200,sma250")
    parser.add_argument("--defensive-assets", default="cash,BIL,SHV,IEF,ZROZ")
    parser.add_argument("--allow-negative-momentum", default="0")
    parser.add_argument("--train-years", type=int, default=3)
    parser.add_argument("--test-years", type=int, default=1)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    parser.add_argument("--output-dir", default="studies/weekly_momentum/evidence/etf_focus_evolution")
    parser.add_argument("--exclude-leveraged", type=int, choices=[0, 1], default=0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lookbacks = _parse_ints(args.lookbacks)
    top_ks = _parse_ints(args.top_ks)
    market_filters = _parse_market_filters(None, args.market_filters)
    allow_negative_values = [bool(v) for v in _parse_ints(args.allow_negative_momentum)]
    defensive_assets = [item.strip().upper() if item.strip().lower() != "cash" else None for item in args.defensive_assets.split(",") if item.strip()]

    prices = load_variation_prices(
        "etfs",
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=max(lookbacks) + 2,
        only_sp500=False,
    )
    if args.exclude_leveraged:
        prices = prices.drop(columns=[c for c in prices.columns if c in LEVERAGED_OR_INVERSE], errors="ignore")
    if prices.empty:
        raise SystemExit("No ETF prices loaded")

    spy = load_spy_series(args.spy_path).reindex(prices.index).ffill()
    spy_returns = spy.pct_change(fill_method=None).fillna(0.0)
    spy_equity = (1.0 + spy_returns).cumprod() * 10_000.0

    configs = _build_configs(lookbacks, top_ks, market_filters, allow_negative_values, defensive_assets, set(prices.columns))
    returns_by_config: dict[str, pd.Series] = {}
    configs_by_slug: dict[str, WeeklyMomentumConfig] = {}
    full_rows = []
    rolling_rows = []
    for cfg in configs:
        slug = config_slug(cfg)
        result = simulate_weekly_momentum(prices, cfg, market_filter_prices=spy)
        returns_by_config[slug] = result.returns
        configs_by_slug[slug] = cfg
        equity = result.equity.reindex(spy.index).dropna()
        returns = result.returns.reindex(equity.index).fillna(0.0)
        metrics = compute_report_metrics(equity, returns)
        roll = rolling_edge_metrics(equity, spy_equity.reindex(equity.index).dropna())
        full_rows.append({"config": slug, **asdict(cfg), **metrics, **roll, "score": _score(metrics, roll)})
        for years in (1, 3, 5, 10):
            rolling_rows.append({"config": slug, "window_years": years, **rolling_edge_metrics(equity, spy_equity.reindex(equity.index).dropna(), (years,))})

    windows = _walk_forward_windows(prices.index, args.train_years, args.test_years)
    selections, wf_returns = _run_walk_forward(returns_by_config, windows)
    wf_equity = (1.0 + wf_returns).cumprod() * 10_000.0
    wf_spy_returns = spy_returns.reindex(wf_returns.index).fillna(0.0)
    wf_spy_equity = (1.0 + wf_spy_returns).cumprod() * 10_000.0
    wf_metrics = compute_report_metrics(wf_equity, wf_returns)
    wf_spy_metrics = compute_report_metrics(wf_spy_equity, wf_spy_returns)
    gate_metrics = _gate_metrics(returns_by_config, wf_returns, n_trials=len(configs))

    full = pd.DataFrame(full_rows).sort_values("score", ascending=False)
    rolling = pd.DataFrame(rolling_rows)
    selections_df = pd.DataFrame(selections)
    full.to_csv(out_dir / "full_period_metrics.csv", index=False)
    rolling.to_csv(out_dir / "rolling_window_metrics.csv", index=False)
    selections_df.to_csv(out_dir / "walk_forward_selections.csv", index=False)
    pd.DataFrame({"wf_return": wf_returns, "wf_equity": wf_equity}).to_csv(out_dir / "walk_forward_equity.csv")
    pd.DataFrame({"walk_forward": wf_metrics, "spy": wf_spy_metrics}).to_csv(out_dir / "walk_forward_metrics.csv")
    pd.DataFrame([gate_metrics]).to_csv(out_dir / "gate_metrics.csv", index=False)
    (out_dir / "config_grid.json").write_text(json.dumps({k: asdict(v) for k, v in configs_by_slug.items()}, indent=2) + "\n", encoding="utf-8")
    _plot_equity(wf_equity, wf_spy_equity, out_dir / "walk_forward_vs_spy.png")
    _write_report(out_dir / "REPORT.md", args, prices, configs, full, selections_df, wf_metrics, wf_spy_metrics, gate_metrics)

    print(f"configs={len(configs)}")
    print(f"assets={prices.shape[1]}")
    print(f"windows={len(selections)}")
    print(f"wf_cagr={wf_metrics['cagr']:.6f}")
    print(f"wf_mdd={wf_metrics['mdd']:.6f}")
    print(f"wf_sharpe={wf_metrics['sharpe']:.6f}")
    print(f"spy_cagr={wf_spy_metrics['cagr']:.6f}")
    print(f"spy_sharpe={wf_spy_metrics['sharpe']:.6f}")
    print(f"pbo_family={gate_metrics['pbo_family']:.6f}")
    print(f"dsr_p_value={gate_metrics['dsr_p_value']:.6f}")
    print(f"bootstrap_cagr_low_0p1pct={gate_metrics['bootstrap_cagr_ci_low_0p1pct']:.6f}")
    print(f"outputs={out_dir}")
    print(full.head(10)[["config", "score", "cagr", "mdd", "sharpe", "roll_3y_pct_beat_spy"]].to_string(index=False))
    return 0


def _build_configs(
    lookbacks: list[int],
    top_ks: list[int],
    market_filters: list[tuple[str, int | None]],
    allow_negative_values: list[bool],
    defensive_assets: list[str | None],
    available_symbols: set[str],
) -> list[WeeklyMomentumConfig]:
    configs = []
    for lookback in lookbacks:
        for top_k in top_ks:
            for filter_type, filter_days in market_filters:
                for allow_negative in allow_negative_values:
                    for defensive_asset in defensive_assets:
                        if defensive_asset is not None and defensive_asset not in available_symbols:
                            continue
                        configs.append(
                            WeeklyMomentumConfig(
                                lookback_days=lookback,
                                top_k=top_k,
                                allow_negative_momentum=allow_negative,
                                defensive_asset=defensive_asset,
                                market_filter_type=filter_type,
                                market_filter_days=filter_days,
                            )
                        )
    return configs


def _walk_forward_windows(index: pd.DatetimeIndex, train_years: int, test_years: int) -> list[dict[str, pd.Timestamp]]:
    first = pd.Timestamp(index.min()).normalize()
    last = pd.Timestamp(index.max()).normalize()
    train_start = first
    windows = []
    while True:
        train_end = train_start + pd.DateOffset(years=train_years) - pd.Timedelta(days=1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.DateOffset(years=test_years) - pd.Timedelta(days=1)
        if test_end > last:
            break
        windows.append({"train_start": train_start, "train_end": train_end, "test_start": test_start, "test_end": test_end})
        train_start = train_start + pd.DateOffset(years=test_years)
    return windows


def _run_walk_forward(
    returns_by_config: dict[str, pd.Series],
    windows: list[dict[str, pd.Timestamp]],
) -> tuple[list[dict[str, object]], pd.Series]:
    selections = []
    wf_parts = []
    for window in windows:
        train_scores = []
        for slug, returns in returns_by_config.items():
            train = returns.loc[window["train_start"]:window["train_end"]]
            train_stats = _period_stats(train)
            train_scores.append((slug, _selection_score(train_stats), train_stats))
        train_scores.sort(key=lambda row: (-row[1], row[0]))
        selected, score, train_stats = train_scores[0]
        test = returns_by_config[selected].loc[window["test_start"]:window["test_end"]]
        test_stats = _period_stats(test)
        wf_parts.append(test)
        selections.append({
            **{k: str(v.date()) for k, v in window.items()},
            "selected_config": selected,
            "selection_score": score,
            "train_cagr": train_stats["cagr"],
            "train_mdd": train_stats["mdd"],
            "train_sharpe": train_stats["sharpe"],
            "test_cagr": test_stats["cagr"],
            "test_mdd": test_stats["mdd"],
            "test_sharpe": test_stats["sharpe"],
        })
    wf_returns = pd.concat(wf_parts).sort_index() if wf_parts else pd.Series(dtype=float)
    return selections, wf_returns[~wf_returns.index.duplicated(keep="first")].rename("wf_return")


def _period_stats(returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    if len(returns) < 20:
        return {"cagr": float("nan"), "mdd": float("nan"), "sharpe": float("-inf"), "sortino": float("nan")}
    equity = (1.0 + returns).cumprod() * 10_000.0
    return compute_report_metrics(equity, returns)


def _gate_metrics(
    returns_by_config: dict[str, pd.Series],
    wf_returns: pd.Series,
    n_trials: int,
) -> dict[str, object]:
    """Compute diagnostic anti-overfit gates for the focused ETF grid.

    These are still diagnostics because the ETF cache is not a point-in-time
    survivorship-free ETF universe. PBO and DSR follow AFML's multiple-testing
    controls ``[advances_fin_ml, p.208-211]`` and ``[advances_fin_ml, p.273-275]``.
    """
    aligned = pd.concat(returns_by_config, axis=1, sort=True).dropna()
    pbo_res = compute_pbo(aligned.to_numpy(dtype=float), n_blocks=10)
    clean = wf_returns.dropna()
    dsr_res = compute_dsr(clean.to_numpy(dtype=float), n_trials=n_trials)
    boot = _block_bootstrap_ci(clean)
    return {
        "pbo_family": float(pbo_res.pbo),
        "pbo_family_pass": bool(pbo_res.pbo < 0.5),
        "pbo_family_n_combinations": int(pbo_res.n_combinations),
        "dsr_p_value": float(dsr_res.p_value),
        "dsr_pass": bool(dsr_res.p_value < 0.05),
        "bootstrap_cagr_ci_low_0p1pct": boot["cagr_low"],
        "bootstrap_sharpe_ci_low_0p1pct": boot["sharpe_low"],
        "bootstrap_pass": bool(boot["cagr_low"] > 0.0),
    }


def _block_bootstrap_ci(returns: pd.Series, n_resamples: int = 2000, block: int = 21) -> dict[str, float]:
    arr = returns.to_numpy(dtype=float)
    rng = np.random.default_rng(42)
    n_blocks = int(np.ceil(len(arr) / block))
    cagrs = []
    sharpes = []
    for _ in range(n_resamples):
        starts = rng.integers(0, len(arr) - block + 1, size=n_blocks)
        sample = np.concatenate([arr[s:s + block] for s in starts])[:len(arr)]
        years = len(sample) / 252.0
        terminal = float(np.prod(1.0 + sample))
        cagrs.append(terminal ** (1.0 / years) - 1.0 if terminal > 0 and years > 0 else -1.0)
        sigma = float(sample.std(ddof=1))
        sharpes.append(float(sample.mean() / sigma * np.sqrt(252.0)) if sigma > 0 else 0.0)
    return {
        "cagr_low": float(np.percentile(cagrs, 0.1)),
        "sharpe_low": float(np.percentile(sharpes, 0.1)),
    }


def _selection_score(stats: dict[str, float]) -> float:
    if not np.isfinite(stats.get("sharpe", np.nan)):
        return float("-inf")
    return float(stats["sharpe"] + stats["cagr"] - abs(stats["mdd"]) + 0.25 * stats.get("sortino", 0.0))


def _score(metrics: dict[str, float], roll: dict[str, float]) -> float:
    return float(
        metrics.get("sharpe", 0.0)
        + metrics.get("cagr", 0.0)
        - abs(metrics.get("mdd", 0.0))
        + 0.25 * metrics.get("sortino", 0.0)
        + 0.75 * _safe(roll.get("roll_3y_pct_beat_spy"))
        + 0.50 * _safe(roll.get("roll_5y_pct_beat_spy"))
        + 0.50 * _safe(roll.get("roll_3y_median_edge"))
    )


def _plot_equity(wf_equity: pd.Series, spy_equity: pd.Series, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.plot(wf_equity.index, wf_equity.values, label="ETF-focused WF", linewidth=1.6)
    ax.plot(spy_equity.index, spy_equity.values, label="SPY buy & hold", color="black", linestyle="--", linewidth=1.4)
    ax.set_yscale("log")
    ax.set_title("ETF-focused weekly momentum walk-forward vs SPY")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_report(
    path: Path,
    args: argparse.Namespace,
    prices: pd.DataFrame,
    configs: list[WeeklyMomentumConfig],
    full: pd.DataFrame,
    selections: pd.DataFrame,
    wf: dict[str, float],
    spy: dict[str, float],
    gates: dict[str, object],
) -> None:
    top = full.head(25).copy()
    show_cols = [
        "config", "score", "cagr", "mdd", "sharpe", "sortino", "calmar",
        "roll_1y_pct_beat_spy", "roll_3y_pct_beat_spy", "roll_5y_pct_beat_spy",
        "roll_3y_worst_edge", "roll_5y_worst_edge",
    ]
    lines = [
        "# ETF-Focused Weekly Momentum Evolution",
        "",
        "## Hypothesis",
        "",
        "ETF momentum should be tested as a cross-asset/factor rotation problem, not only as a direct stock-momentum transplant. This run emphasizes broader top-K sleeves, explicit defensive ETFs, and optional leveraged/inverse exclusion because ETF universes are smaller and more correlated than single-stock universes `[stocks_on_the_move, p.60]`, `[stocks_on_the_move, p.66-67, p.81]`.",
        "",
        "## Setup",
        "",
        f"- Assets loaded: `{prices.shape[1]}`.",
        f"- Exclude leveraged/inverse: `{bool(args.exclude_leveraged)}`.",
        f"- Grid size: `{len(configs)}`.",
        f"- Lookbacks: `{args.lookbacks}`.",
        f"- Top-K: `{args.top_ks}`.",
        f"- Market filters: `{args.market_filters}`.",
        f"- Defensive assets: `{args.defensive_assets}`.",
        f"- Walk-forward: `{args.train_years}`y train -> `{args.test_years}`y test; train-only selection to reduce overfit `[advances_fin_ml, p.208-211]`.",
        "",
        "## Walk-Forward Result",
        "",
        "| metric | ETF-focused WF | SPY |",
        "|---|---:|---:|",
        f"| CAGR | {_pct(wf['cagr'])} | {_pct(spy['cagr'])} |",
        f"| MDD | {_pct(wf['mdd'])} | {_pct(spy['mdd'])} |",
        f"| Sharpe | {wf['sharpe']:.3f} | {spy['sharpe']:.3f} |",
        f"| Sortino | {wf['sortino']:.3f} | {spy['sortino']:.3f} |",
        "",
        "## Diagnostic Gates",
        "",
        "| gate | value | pass? |",
        "|---|---:|---|",
        f"| PBO family | {float(gates['pbo_family']):.3f} | `{gates['pbo_family_pass']}` |",
        f"| DSR p-value | {float(gates['dsr_p_value']):.3f} | `{gates['dsr_pass']}` |",
        f"| bootstrap 0.1% CAGR low | {_pct(float(gates['bootstrap_cagr_ci_low_0p1pct']))} | `{gates['bootstrap_pass']}` |",
        "",
        "These gates are diagnostic because the ETF cache is not point-in-time or survivorship-free; they do not authorize deployment `[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.273-275]`.",
        "",
        "![Walk-forward vs SPY](walk_forward_vs_spy.png)",
        "",
        "## Top Full-Period Configs",
        "",
        top[show_cols].to_markdown(index=False),
        "",
        "## Walk-Forward Selections",
        "",
        selections.to_markdown(index=False) if not selections.empty else "No windows generated.",
        "",
        "## Caveats",
        "",
        "- This remains exploratory: no PBO/DSR/bootstrap/cost/tax gate has been run on this expanded ETF grid yet.",
        "- ETF cache coverage is not a point-in-time investable universe; delisted/closed ETF history may be missing `[advances_fin_ml, p.208-211]`.",
        "- Full-period ranks are for diagnosis only; the walk-forward result is the primary anti-overfit readout.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%" if np.isfinite(value) else "nan"


def _safe(value: object) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return 0.0
    return f if np.isfinite(f) else 0.0


if __name__ == "__main__":
    raise SystemExit(main())
