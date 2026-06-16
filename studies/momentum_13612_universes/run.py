#!/usr/bin/env python3
"""Run pure 13612 universe momentum screens.

This runner is research-only. It can fetch current US stock/ETF screens through
yfinance, read restored Tiingo parquets, and consume the user's BR 1-minute
Postgres quotes as daily last-bar closes. Current-universe/yfinance and unaudited
Postgres rows are marked non-promotable because survivorship, PIT membership and
corporate-action quality must be resolved before any mandate interpretation
`[advances_fin_ml, p.208-211]`.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from market_lab.backtest.metrics.performance import max_drawdown, sharpe  # noqa: E402
from market_lab.backtest.validation.dsr import dsr, psr  # noqa: E402
from market_lab.backtest.validation.pbo import pbo  # noqa: E402
from market_lab.backtest.validation.walk_forward import walk_forward_splits  # noqa: E402
from market_lab.config import get_settings  # noqa: E402
from studies.momentum_13612_universes.core import (  # noqa: E402
    Momentum13612Config,
    TRADING_DAYS_PER_YEAR,
    equity_from_returns,
    metrics_from_returns,
    simulate_momentum_gross,
    simulate_momentum_holdings_loop,
)
from studies.momentum_13612_universes.universes import (  # noqa: E402
    PostgresDailyCloseConfig,
    br_etf_tickers,
    br_stock_tickers,
    env_or_default,
    load_postgres_daily_close_frame,
    load_tiingo_price_frame,
    load_yfinance_price_frame,
    manifest_tickers_by_asset_class,
    masked_database_url,
    us_etf_tickers,
    us_stock_tickers,
)


STUDY_DIR = Path(__file__).resolve().parent
RESULTS_DIR = STUDY_DIR / "results"
PLOTS_DIR = STUDY_DIR / "plots"
REPORT = STUDY_DIR / "REPORT.md"
DATA_AUDIT = STUDY_DIR / "DATA_AUDIT.md"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"

DEFAULT_TOP_N = (4, 10, 20)
VARIANTS = ("us_stocks", "us_etfs", "us_mixed", "br_stocks", "br_etfs", "br_mixed")


def fmt_pct(value: float, digits: int = 2) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{100.0 * float(value):.{digits}f}%"


def fmt_num(value: float, digits: int = 3) -> str:
    if not math.isfinite(float(value)):
        return "n/a"
    return f"{float(value):.{digits}f}"


def md_value(value: object) -> str:
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return "n/a"
    return str(value)


def md_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._\n"
    header = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join("---" for _ in columns) + "|"
    body = [
        "| " + " | ".join(md_value(row.get(col, "")) for col in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body]) + "\n"


def json_safe(value: object) -> object:
    """Convert non-finite numeric values to strict JSON-compatible nulls."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def safe_filename(value: str) -> str:
    """Return a conservative filename stem for generated plot artifacts."""
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)


def selected_variants(raw: str) -> tuple[str, ...]:
    if raw == "all":
        return VARIANTS
    if raw == "us_all":
        return ("us_stocks", "us_etfs", "us_mixed")
    if raw == "br_all":
        return ("br_stocks", "br_etfs", "br_mixed")
    return (raw,)


def top_n_values(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values or any(value <= 0 for value in values):
        raise ValueError("--top-n must contain positive integers")
    return values


def tickers_for_variant(variant: str, args: argparse.Namespace) -> tuple[str, ...]:
    if variant == "us_stocks":
        return tuple(
            us_stock_tickers(
                TIINGO_ROOT, limit=args.max_us_stocks, universe=args.us_stock_universe
            )
        )
    if variant == "us_etfs":
        return tuple(
            us_etf_tickers(TIINGO_ROOT, limit=args.max_us_etfs, universe=args.us_etf_universe)
        )
    if variant == "us_mixed":
        stocks = us_stock_tickers(
            TIINGO_ROOT, limit=args.max_us_stocks, universe=args.us_stock_universe
        )
        etfs = us_etf_tickers(TIINGO_ROOT, limit=args.max_us_etfs, universe=args.us_etf_universe)
        return tuple(sorted(set(stocks) | set(etfs)))
    if variant == "br_stocks":
        return tuple(br_stock_tickers(limit=args.max_br_stocks))
    if variant == "br_etfs":
        return tuple(br_etf_tickers(limit=args.max_br_etfs))
    if variant == "br_mixed":
        stocks = br_stock_tickers(limit=args.max_br_stocks)
        etfs = br_etf_tickers(limit=args.max_br_etfs)
        return tuple(sorted(set(stocks) | set(etfs)))
    raise ValueError(f"unknown variant {variant!r}")


def build_configs(args: argparse.Namespace) -> list[tuple[str, Momentum13612Config]]:
    configs: list[tuple[str, Momentum13612Config]] = []
    for variant in selected_variants(args.variant):
        tickers = tickers_for_variant(variant, args)
        for top_n in top_n_values(args.top_n):
            configs.append(
                (
                    variant,
                    Momentum13612Config(
                        name=f"mom13612_{variant}_top{top_n}",
                        assets=tickers,
                        top_n=top_n,
                        min_assets=top_n,
                    ),
                )
            )
    return configs


def resolve_us_source(args: argparse.Namespace) -> str:
    if args.us_source != "auto":
        return args.us_source
    prices_dir = TIINGO_ROOT / "daily" / "prices"
    return "tiingo" if prices_dir.exists() else "yfinance"


def postgres_config(args: argparse.Namespace) -> PostgresDailyCloseConfig:
    return PostgresDailyCloseConfig(
        database_url=args.database_url,
        table=args.br_postgres_table,
        ticker_column=args.br_postgres_ticker_col,
        timestamp_column=args.br_postgres_ts_col,
        close_column=args.br_postgres_close_col,
        strip_sa_suffix=not args.br_postgres_keep_sa,
    )


def load_prices_for_variant(
    variant: str, tickers: tuple[str, ...], args: argparse.Namespace
) -> tuple[pd.DataFrame, str]:
    if variant.startswith("us_"):
        source = resolve_us_source(args)
        if source == "tiingo":
            return load_tiingo_price_frame(tickers, TIINGO_ROOT, args.start, args.end), "tiingo"
        if source == "yfinance":
            require_yfinance_allowed(args)
            return load_yfinance_price_frame(tickers, args.start, args.end), "yfinance"
        raise ValueError(f"unknown US source {source!r}")

    if variant == "br_stocks":
        if args.br_stock_source == "postgres":
            frame = load_postgres_daily_close_frame(
                tickers, postgres_config(args), start=args.start, end=args.end
            )
            return frame, "postgres_1m"
        require_yfinance_allowed(args)
        return load_yfinance_price_frame(tickers, args.start, args.end), "yfinance"

    if variant == "br_etfs":
        require_yfinance_allowed(args)
        return load_yfinance_price_frame(tickers, args.start, args.end), "yfinance"

    if variant == "br_mixed":
        full_br_etfs = set(br_etf_tickers())
        stock_tickers = tuple(ticker for ticker in tickers if ticker not in full_br_etfs)
        etf_tickers = tuple(ticker for ticker in tickers if ticker in full_br_etfs)
        frames: list[pd.DataFrame] = []
        sources: list[str] = []
        if stock_tickers:
            if args.br_stock_source == "postgres":
                frames.append(
                    load_postgres_daily_close_frame(
                        stock_tickers, postgres_config(args), start=args.start, end=args.end
                    )
                )
                sources.append("postgres_1m")
            else:
                require_yfinance_allowed(args)
                frames.append(load_yfinance_price_frame(stock_tickers, args.start, args.end))
                sources.append("yfinance")
        if etf_tickers:
            require_yfinance_allowed(args)
            frames.append(load_yfinance_price_frame(etf_tickers, args.start, args.end))
            sources.append("yfinance")
        if not frames:
            raise FileNotFoundError("no BR mixed price frames loaded")
        return merge_price_frames(frames), "+".join(sorted(set(sources)))

    raise ValueError(f"unknown variant {variant!r}")


def load_benchmark_prices(args: argparse.Namespace) -> pd.DataFrame:
    """Load the benchmark price series used for plots/comparison.

    SPY adjusted close is the practical S&P 500 proxy in this repo. It is a
    benchmark, not a selected universe member, but reports still disclose the
    yfinance source when Tiingo is unavailable `[advances_fin_ml, p.208-211]`.
    """
    if args.benchmark_source == "tiingo":
        return load_tiingo_price_frame((args.benchmark,), TIINGO_ROOT, args.start, args.end)
    return load_yfinance_price_frame((args.benchmark,), args.start, args.end, allow_missing=False)


def require_yfinance_allowed(args: argparse.Namespace) -> None:
    if not args.allow_biased_yfinance:
        raise ValueError(
            "yfinance source requires --allow-biased-yfinance; it is a "
            "current-universe/survivorship-biased screen, not promotion evidence."
        )


def merge_price_frames(frames: list[pd.DataFrame]) -> pd.DataFrame:
    out = pd.concat(frames, axis=1, sort=True).sort_index()
    out = out.loc[:, ~out.columns.duplicated(keep="first")]
    missing: list[str] = []
    for frame in frames:
        missing.extend(str(ticker) for ticker in frame.attrs.get("missing_tickers", []))
    if missing:
        out.attrs["missing_tickers"] = sorted(set(missing))
    return out


def adapt_config_to_available_prices(
    config: Momentum13612Config, prices: pd.DataFrame
) -> Momentum13612Config:
    available_columns = {str(col).upper() for col in prices.columns}
    available_assets = tuple(asset for asset in config.assets if asset.upper() in available_columns)
    if len(available_assets) < config.top_n:
        missing = sorted(set(config.assets) - set(available_assets))
        raise FileNotFoundError(
            f"only {len(available_assets)} assets remain after missing data; "
            f"top_n={config.top_n}; missing_sample={missing[:25]}"
        )
    if len(available_assets) == len(config.assets):
        return config
    return Momentum13612Config(
        name=f"{config.name}_available{len(available_assets)}",
        assets=available_assets,
        top_n=config.top_n,
        lookback_months=config.lookback_months,
        min_assets=min(config.min_required_assets, len(available_assets)),
    )


def promotion_eligible(source: str) -> bool:
    """Only restored Tiingo screens are eligible for deeper validation claims."""
    return source == "tiingo"


def data_caveat(source: str) -> str:
    if "yfinance" in source:
        return "yfinance current-universe/survivorship-biased screen only"
    if "postgres_1m" in source:
        return "Postgres 1m daily-last-bar screen; PIT/corporate-action audit pending"
    return "none"


def align_benchmark_returns(
    strategy_returns: pd.Series,
    benchmark_prices: pd.DataFrame | None,
    benchmark_symbol: str,
) -> tuple[pd.Series, pd.Series]:
    """Align strategy returns with benchmark buy-and-hold returns."""
    clean_strategy = strategy_returns.dropna().astype(float)
    if benchmark_prices is None or clean_strategy.empty:
        return clean_strategy.iloc[0:0], clean_strategy.iloc[0:0].rename(benchmark_symbol)

    benchmark_columns = {str(col).upper(): col for col in benchmark_prices.columns}
    source_col = benchmark_columns.get(benchmark_symbol.upper(), benchmark_prices.columns[0])
    bench_prices = benchmark_prices[source_col].astype(float).sort_index()
    bench_prices.index = pd.DatetimeIndex(bench_prices.index).tz_localize(None)
    bench_prices = bench_prices.reindex(clean_strategy.index, method="ffill").dropna()
    aligned_strategy = clean_strategy.reindex(bench_prices.index).dropna()
    bench_prices = bench_prices.reindex(aligned_strategy.index).dropna()
    aligned_strategy = aligned_strategy.reindex(bench_prices.index).dropna()
    if aligned_strategy.empty or bench_prices.empty:
        return aligned_strategy.iloc[0:0], aligned_strategy.iloc[0:0].rename(benchmark_symbol)
    bench_returns = bench_prices.pct_change(fill_method=None).fillna(0.0)
    bench_returns.name = benchmark_symbol.upper()
    return aligned_strategy, bench_returns


def benchmark_comparison(
    strategy_returns: pd.Series,
    benchmark_prices: pd.DataFrame | None,
    benchmark_symbol: str,
) -> dict[str, object]:
    """Return benchmark and excess metrics on the common date range."""
    aligned_strategy, benchmark_returns = align_benchmark_returns(
        strategy_returns, benchmark_prices, benchmark_symbol
    )
    if aligned_strategy.empty or benchmark_returns.empty:
        return {
            "symbol": benchmark_symbol.upper(),
            "metrics": metrics_from_returns(pd.Series(dtype=float)),
            "strategy_common_metrics": metrics_from_returns(pd.Series(dtype=float)),
            "excess_cagr": float("nan"),
            "excess_sharpe": float("nan"),
        }
    strategy_metrics = metrics_from_returns(aligned_strategy)
    benchmark_metrics = metrics_from_returns(benchmark_returns)
    return {
        "symbol": benchmark_symbol.upper(),
        "metrics": benchmark_metrics,
        "strategy_common_metrics": strategy_metrics,
        "excess_cagr": float(strategy_metrics["cagr"]) - float(benchmark_metrics["cagr"]),
        "excess_sharpe": float(strategy_metrics["sharpe"]) - float(benchmark_metrics["sharpe"]),
    }


def drawdown_from_equity(equity: pd.Series) -> pd.Series:
    """Drawdown series from an equity curve."""
    if equity.empty:
        return equity
    return equity / equity.cummax() - 1.0


def plot_strategy_vs_benchmark(
    strategy_returns: pd.Series,
    benchmark_prices: pd.DataFrame | None,
    benchmark_symbol: str,
    config_name: str,
) -> str | None:
    """Write a 3-panel strategy-vs-benchmark plot and return report path."""
    aligned_strategy, benchmark_returns = align_benchmark_returns(
        strategy_returns, benchmark_prices, benchmark_symbol
    )
    if aligned_strategy.empty or benchmark_returns.empty:
        return None

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    strategy_equity = equity_from_returns(aligned_strategy, start_value=1.0)
    benchmark_equity = equity_from_returns(benchmark_returns, start_value=1.0)
    aligned_equity = pd.concat(
        {"Strategy": strategy_equity, benchmark_symbol.upper(): benchmark_equity}, axis=1
    ).dropna()
    if aligned_equity.empty:
        return None
    ratio = aligned_equity["Strategy"] / aligned_equity[benchmark_symbol.upper()]

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    aligned_equity.plot(ax=axes[0], linewidth=1.4)
    axes[0].set_title(f"{config_name}: equity vs {benchmark_symbol.upper()}")
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(True, alpha=0.3)

    drawdowns = pd.concat(
        {
            "Strategy": drawdown_from_equity(aligned_equity["Strategy"]),
            benchmark_symbol.upper(): drawdown_from_equity(aligned_equity[benchmark_symbol.upper()]),
        },
        axis=1,
    )
    drawdowns.plot(ax=axes[1], linewidth=1.2)
    axes[1].set_title("Drawdown")
    axes[1].set_ylabel("Drawdown")
    axes[1].grid(True, alpha=0.3)

    ratio.plot(ax=axes[2], color="black", linewidth=1.2)
    axes[2].axhline(1.0, color="gray", linewidth=1.0, linestyle="--")
    axes[2].set_title(f"Strategy / {benchmark_symbol.upper()} relative equity")
    axes[2].set_ylabel("Ratio")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    path = PLOTS_DIR / f"{safe_filename(config_name)}_vs_{benchmark_symbol.upper()}.png"
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return str(path.relative_to(STUDY_DIR))


def walk_forward_diagnostic(returns: pd.Series) -> dict[str, object]:
    n = len(returns)
    window = n // 9
    if window < 63:
        return {
            "n_windows": 0,
            "positive_windows": 0,
            "max_oos_mdd": float("nan"),
            "pass_gate": False,
        }
    oos_returns: list[float] = []
    oos_mdds: list[float] = []
    for _, test_range in walk_forward_splits(n, window, window, window):
        idx = list(test_range)
        r = returns.iloc[idx]
        eq = equity_from_returns(r, start_value=1.0)
        oos_returns.append(float((1.0 + r).prod() - 1.0))
        oos_mdds.append(float(max_drawdown(eq)))
        if len(oos_returns) >= 8:
            break
    n_windows = len(oos_returns)
    positive = sum(value > 0.0 for value in oos_returns)
    max_mdd = max(oos_mdds) if oos_mdds else float("nan")
    return {
        "n_windows": int(n_windows),
        "positive_windows": int(positive),
        "max_oos_mdd": float(max_mdd),
        "oos_returns": oos_returns,
        "oos_mdds": oos_mdds,
        "pass_gate": bool(n_windows >= 8 and positive >= 6),
    }


def bootstrap_sharpe_ci_low(
    returns: pd.Series, n_resamples: int = 1000, block: int = 21
) -> float:
    arr = returns.to_numpy(dtype=float)
    if len(arr) < TRADING_DAYS_PER_YEAR:
        return float("nan")
    rng = np.random.default_rng(42)
    n_blocks = len(arr) // block
    values: list[float] = []
    for _ in range(n_resamples):
        starts = rng.integers(0, len(arr) - block + 1, size=n_blocks)
        sample = np.concatenate([arr[start : start + block] for start in starts])[: len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            values.append(float(sample.mean() / sigma * np.sqrt(TRADING_DAYS_PER_YEAR)))
    return float(np.percentile(values, 0.1)) if values else float("nan")


def evaluate_config(
    config: Momentum13612Config, variant: str, source: str, prices: pd.DataFrame, n_trials: int
) -> dict[str, object]:
    gross, weights = simulate_momentum_gross(prices, config)
    loop = simulate_momentum_holdings_loop(prices, config).reindex(gross.index).dropna()
    aligned = pd.concat({"vectorized": gross, "loop": loop}, axis=1).dropna()
    xlib_delta_pp = 0.0
    if not aligned.empty:
        vec_metrics = metrics_from_returns(aligned["vectorized"])
        loop_metrics = metrics_from_returns(aligned["loop"])
        xlib_delta_pp = abs(float(vec_metrics["cagr"]) - float(loop_metrics["cagr"])) * 100.0

    p_value = 1.0
    if len(gross) >= 3:
        arr = gross.to_numpy(dtype=float)
        if n_trials >= 2:
            p_value = float(dsr(arr, n_trials=n_trials).p_value)
        else:
            p_value = 1.0 - float(psr(arr, benchmark=0.0))

    wf = walk_forward_diagnostic(gross)
    oos = gross.iloc[int(len(gross) * 0.70) :]
    fwd = gross[gross.index >= "2020-01-01"]
    boot_low = bootstrap_sharpe_ci_low(gross)
    gates = {
        "dsr_p_lt_0_05": bool(p_value < 0.05),
        "wf_6_of_8_positive": bool(wf["pass_gate"]),
        "oos_sharpe_positive": bool(
            len(oos) >= 63 and sharpe(oos, TRADING_DAYS_PER_YEAR) > 0.0
        ),
        "fwd_sharpe_positive": bool(
            len(fwd) >= 63 and sharpe(fwd, TRADING_DAYS_PER_YEAR) > 0.0
        ),
        "bootstrap_999_low_gt_0": bool(math.isfinite(boot_low) and boot_low > 0.0),
        "xlib_delta_lte_3pp": bool(xlib_delta_pp <= 3.0),
    }
    gates["n_passed_ex_pbo"] = sum(bool(value) for value in gates.values())

    return {
        "variant": variant,
        "config": asdict(config),
        "source": source,
        "promotion_eligible": promotion_eligible(source),
        "data_caveat": data_caveat(source),
        "gross_metrics": metrics_from_returns(gross),
        "gate_details": {
            "n_trials": n_trials,
            "dsr_p_value": p_value,
            "walk_forward": wf,
            "oos_sharpe": float(sharpe(oos, TRADING_DAYS_PER_YEAR)) if len(oos) else 0.0,
            "fwd_sharpe": float(sharpe(fwd, TRADING_DAYS_PER_YEAR)) if len(fwd) else 0.0,
            "bootstrap_999_ci_low_sharpe": boot_low,
            "xlib_cagr_delta_pp": xlib_delta_pp,
        },
        "gates": gates,
    }


def pbo_for_returns(returns_by_name: dict[str, pd.Series]) -> dict[str, object]:
    if len(returns_by_name) < 2:
        return {"pbo": float("nan"), "n_combinations": 0, "pass_gate": True, "note": "single config"}
    aligned = pd.concat(returns_by_name, axis=1).dropna()
    if aligned.shape[1] < 2 or len(aligned) < 252:
        return {
            "pbo": float("nan"),
            "n_combinations": 0,
            "pass_gate": False,
            "note": "insufficient aligned data",
        }
    result = pbo(aligned.to_numpy(dtype=float), n_blocks=10)
    return {
        "pbo": float(result.pbo),
        "n_combinations": int(result.n_combinations),
        "pass_gate": bool(result.pbo < 0.5),
    }


def audit_data(args: argparse.Namespace) -> dict[str, object]:
    grouped = manifest_tickers_by_asset_class(TIINGO_ROOT)
    prices_dir = TIINGO_ROOT / "daily" / "prices"
    parquet_count = len(list(prices_dir.glob("*.parquet"))) if prices_dir.exists() else 0
    return {
        "tiingo_manifest_exists": (TIINGO_ROOT / "manifest.json").exists(),
        "tiingo_asset_classes": {key: len(values) for key, values in sorted(grouped.items())},
        "tiingo_prices_dir_exists": prices_dir.exists(),
        "tiingo_parquet_count": parquet_count,
        "us_source_effective": resolve_us_source(args),
        "benchmark": args.benchmark,
        "benchmark_source": args.benchmark_source,
        "plots_enabled": not args.no_plots,
        "us_stock_universe": args.us_stock_universe,
        "us_etf_universe": args.us_etf_universe,
        "br_stock_source": args.br_stock_source,
        "br_postgres_url": masked_database_url(args.database_url),
        "br_postgres_table": args.br_postgres_table,
        "br_postgres_columns": {
            "ticker": args.br_postgres_ticker_col,
            "timestamp": args.br_postgres_ts_col,
            "close": args.br_postgres_close_col,
        },
        "br_postgres_strip_sa_suffix": not args.br_postgres_keep_sa,
        "br_curated_etf_count": len(br_etf_tickers()),
    }


def write_data_audit(audit: dict[str, object]) -> None:
    rows = [{"Item": key, "Value": value} for key, value in audit.items()]
    DATA_AUDIT.write_text(
        "# Momentum 13612 Universe Data Audit\n\n"
        "Status: data-readiness audit for `studies/momentum_13612_universes/`.\n\n"
        "Tiingo parquets are preferred for US stock/ETF historical screens when restored. "
        "yfinance is explicit screen-only. BR stocks can use the local Postgres 1m quote "
        "database, collapsed to daily last-bar closes; corporate-action/PIT quality remains "
        "a separate audit before promotion `[advances_fin_ml, p.208-211]`.\n\n"
        + md_table(rows, ["Item", "Value"]),
        encoding="utf-8",
    )


def write_report(
    results: list[dict[str, object]], pbo_result: dict[str, object], errors: list[str]
) -> None:
    rows: list[dict[str, object]] = []
    for result in results:
        metrics = result["gross_metrics"]
        gates = result["gates"]
        rows.append(
            {
                "Config": result["config"]["name"],
                "Variant": result["variant"],
                "Source": result["source"],
                "Assets": len(result["config"]["assets"]),
                "Window": f"{metrics['start']}..{metrics['end']}",
                "CAGR": fmt_pct(float(metrics["cagr"])),
                "SPY CAGR": fmt_pct(
                    float(result.get("benchmark", {}).get("metrics", {}).get("cagr", float("nan")))
                ),
                "Excess CAGR": fmt_pct(
                    float(result.get("benchmark", {}).get("excess_cagr", float("nan")))
                ),
                "MDD": fmt_pct(float(metrics["mdd"])),
                "SPY MDD": fmt_pct(
                    float(result.get("benchmark", {}).get("metrics", {}).get("mdd", float("nan")))
                ),
                "Sharpe": fmt_num(float(metrics["sharpe"])),
                "SPY Sharpe": fmt_num(
                    float(result.get("benchmark", {}).get("metrics", {}).get("sharpe", float("nan")))
                ),
                "Calmar": fmt_num(float(metrics["calmar"])),
                "Gates ex-PBO": f"{gates['n_passed_ex_pbo']}/6",
                "Promotion eligible": result["promotion_eligible"],
                "Plot": (
                    f"[{Path(str(result['plot_path'])).name}]({result['plot_path']})"
                    if result.get("plot_path")
                    else "n/a"
                ),
            }
        )

    error_text = "\n".join(f"- {error}" for error in errors) if errors else "_No run errors._"
    any_promotion_eligible = any(bool(result.get("promotion_eligible")) for result in results)
    pbo_pass = bool(pbo_result.get("pass_gate"))
    if not results:
        verdict = "No successful result rows; current run is data-blocked."
    elif not any_promotion_eligible:
        verdict = (
            "Screen-only FAIL: no result row is promotion-eligible. yfinance/current-list "
            "and unaudited Postgres 1m rows cannot support a winner without PIT/delisted "
            "and corporate-action validation `[advances_fin_ml, p.208-211]`."
        )
    elif not pbo_pass:
        verdict = "FAIL: PBO gate did not pass `[advances_fin_ml, p.208-211]`."
    else:
        verdict = "Diagnostic pass only; mandate promotion still requires all hard gates."

    REPORT.write_text(
        "# Momentum 13612 Universe Study Report\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Method\n\n"
        "Pure monthly 13612U cross-sectional rotation: rank each universe by the "
        "equal-weighted mean of 1/3/6/12-month returns, hold top-N equal weight, "
        "and apply month-end weights only to subsequent daily returns. Momentum and "
        "monthly cadence are anchored in `[stocks_on_the_move, p.60]` and "
        "`[stocks_on_the_move, p.98-99]`; validation diagnostics follow "
        "`[advances_fin_ml, p.208-211]` and `[advances_fin_ml, p.273-275]`.\n\n"
        "## Results\n\n"
        + md_table(
            rows,
            [
                "Config",
                "Variant",
                "Source",
                "Assets",
                "Window",
                "CAGR",
                "SPY CAGR",
                "Excess CAGR",
                "MDD",
                "SPY MDD",
                "Sharpe",
                "SPY Sharpe",
                "Calmar",
                "Gates ex-PBO",
                "Promotion eligible",
                "Plot",
            ],
        )
        + "\n## PBO\n\n"
        + md_table(
            [{"Item": key, "Value": value} for key, value in pbo_result.items()],
            ["Item", "Value"],
        )
        + "\n## Errors / Data Blocks\n\n"
        + error_text
        + "\n\n## Caveats\n\n"
        "- Results are gross of transaction costs and taxes in this first scaffold.\n"
        "- Benchmark comparison uses SPY adjusted close as the S&P 500 proxy.\n"
        "- yfinance rows require `--allow-biased-yfinance` and are current-universe/"
        "survivorship-biased screens only.\n"
        "- BR Postgres 1m rows use the last intraday bar as daily close; adjusted-price, "
        "split/dividend and PIT membership audits remain required.\n"
        "- CAGR/MDD are warning tiers under the mandate, not standalone promotion gates.\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pure 13612 universe momentum screens")
    parser.add_argument(
        "--variant",
        choices=["all", "us_all", "br_all", *VARIANTS],
        default="all",
    )
    parser.add_argument("--top-n", default=",".join(str(value) for value in DEFAULT_TOP_N))
    parser.add_argument("--us-source", choices=["auto", "tiingo", "yfinance"], default="auto")
    parser.add_argument("--benchmark", default="SPY")
    parser.add_argument("--benchmark-source", choices=["yfinance", "tiingo"], default="yfinance")
    parser.add_argument("--no-plots", action="store_true")
    parser.add_argument(
        "--us-stock-universe",
        choices=["sp500", "tiingo_manifest"],
        default="sp500",
    )
    parser.add_argument(
        "--us-etf-universe",
        choices=["curated", "tiingo_manifest"],
        default="curated",
    )
    parser.add_argument("--br-stock-source", choices=["postgres", "yfinance"], default="postgres")
    parser.add_argument(
        "--allow-biased-yfinance",
        action="store_true",
        help="explicitly allow yfinance current-universe/survivorship-biased screens",
    )
    parser.add_argument("--max-us-stocks", type=int, default=120)
    parser.add_argument("--max-us-etfs", type=int, default=60)
    parser.add_argument("--max-br-stocks", type=int, default=100)
    parser.add_argument("--max-br-etfs", type=int, default=40)
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--audit-only", action="store_true")

    settings = get_settings()
    parser.add_argument("--database-url", default=settings.database_url)
    parser.add_argument(
        "--br-postgres-table",
        default=env_or_default("MARKET_LAB_BR_1M_TABLE", "quotes_1m"),
    )
    parser.add_argument(
        "--br-postgres-ticker-col",
        default=env_or_default("MARKET_LAB_BR_1M_TICKER_COL", "ticker"),
    )
    parser.add_argument(
        "--br-postgres-ts-col",
        default=env_or_default("MARKET_LAB_BR_1M_TS_COL", "ts"),
    )
    parser.add_argument(
        "--br-postgres-close-col",
        default=env_or_default("MARKET_LAB_BR_1M_CLOSE_COL", "close"),
    )
    parser.add_argument(
        "--br-postgres-keep-sa",
        action="store_true",
        help="query BR DB symbols with .SA suffix instead of stripping it",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not args.no_plots:
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    audit = audit_data(args)
    write_data_audit(audit)
    if args.audit_only:
        print(f"wrote {DATA_AUDIT.relative_to(REPO_ROOT)}")
        return 0

    configs = build_configs(args)
    if not configs:
        raise RuntimeError(f"no configs built for variant={args.variant}")

    grouped_configs: dict[str, list[Momentum13612Config]] = defaultdict(list)
    for variant, config in configs:
        grouped_configs[variant].append(config)

    results: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    errors: list[str] = []
    n_trials = len(configs)
    benchmark_prices: pd.DataFrame | None = None
    try:
        benchmark_prices = load_benchmark_prices(args)
    except Exception as exc:
        errors.append(f"benchmark {args.benchmark} ({args.benchmark_source}): {exc}")

    for variant, variant_configs in grouped_configs.items():
        tickers = tickers_for_variant(variant, args)
        try:
            prices, source = load_prices_for_variant(variant, tickers, args)
        except Exception as exc:
            for config in variant_configs:
                errors.append(f"{config.name}: {exc}")
            continue

        for config in variant_configs:
            try:
                eval_config = adapt_config_to_available_prices(config, prices)
                result = evaluate_config(eval_config, variant, source, prices, n_trials=n_trials)
                gross, _weights = simulate_momentum_gross(prices, eval_config)
                result["benchmark"] = benchmark_comparison(
                    gross, benchmark_prices, args.benchmark
                )
                if not args.no_plots:
                    result["plot_path"] = plot_strategy_vs_benchmark(
                        gross, benchmark_prices, args.benchmark, eval_config.name
                    )
                results.append(result)
                returns_by_name[eval_config.name] = gross
            except Exception as exc:
                errors.append(f"{config.name} ({source}): {exc}")

    pbo_result = (
        pbo_for_returns(returns_by_name)
        if results
        else {"pbo": float("nan"), "pass_gate": False, "note": "no successful configs"}
    )
    payload = json_safe({"results": results, "pbo": pbo_result, "errors": errors})
    (RESULTS_DIR / "results.json").write_text(
        json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8"
    )
    write_report(results, pbo_result, errors)
    print(f"wrote {REPORT.relative_to(REPO_ROOT)}")
    print(f"wrote {(RESULTS_DIR / 'results.json').relative_to(REPO_ROOT)}")
    if errors:
        print("data/errors:")
        for error in errors:
            print(f"- {error}")
    return 0 if results else 2


if __name__ == "__main__":
    raise SystemExit(main())
