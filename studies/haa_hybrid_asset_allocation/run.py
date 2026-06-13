#!/usr/bin/env python3
"""Run the Hybrid Asset Allocation study.

The runner is deliberately storage-only for Tiingo. It audits the restored cache
instead of silently falling back to yfinance, because stock universes are highly
survivorship-sensitive [advances_fin_ml, p.208-211].
"""

from __future__ import annotations

import argparse
import json
import math
import sys
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
from studies._shared.tax_engine import AnnualDarfEngine  # noqa: E402
from studies.haa_hybrid_asset_allocation.haa import (  # noqa: E402
    HAA_BALANCED_G8_T4,
    HAA_BALANCED_G8_T4_NO_VNQ,
    HAA_BESTFOLIO_NO_QQQ_SEED,
    HAAConfig,
    TRADING_DAYS_PER_YEAR,
    equity_from_returns,
    load_testfolio_price_frame,
    load_tiingo_price_frame,
    load_yfinance_price_frame,
    manifest_tickers_by_asset_class,
    metrics_from_returns,
    simulate_haa_gross,
    simulate_haa_holdings_loop,
)


STUDY_DIR = Path(__file__).resolve().parent
RESULTS_DIR = STUDY_DIR / "results"
REPORT = STUDY_DIR / "REPORT.md"
DATA_AUDIT = STUDY_DIR / "DATA_AUDIT.md"
TIINGO_ROOT = REPO_ROOT / "data" / "tiingo"
TESTFOLIO_CACHE = REPO_ROOT / "data" / "testfolio" / "cache" / "history.parquet"

CANARY_AND_DEFENSIVE = ("TIP", "BIL", "IEF")
DEFAULT_STOCK_TOP_N = (4, 10, 20)


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


def audit_data() -> dict[str, object]:
    grouped = manifest_tickers_by_asset_class(TIINGO_ROOT)
    prices_dir = TIINGO_ROOT / "daily" / "prices"
    parquet_count = len(list(prices_dir.glob("*.parquet"))) if prices_dir.exists() else 0
    manifest_count = sum(len(values) for values in grouped.values())
    canonical_missing = []
    for ticker in HAA_BALANCED_G8_T4.required_assets:
        if not (prices_dir / f"{ticker}.parquet").exists():
            canonical_missing.append(ticker)
    return {
        "tiingo_manifest_exists": (TIINGO_ROOT / "manifest.json").exists(),
        "tiingo_prices_dir_exists": prices_dir.exists(),
        "tiingo_manifest_count": manifest_count,
        "tiingo_asset_classes": {key: len(values) for key, values in sorted(grouped.items())},
        "tiingo_parquet_count": parquet_count,
        "canonical_haa_tiingo_missing": canonical_missing,
        "testfolio_cache_exists": TESTFOLIO_CACHE.exists(),
    }


def write_data_audit(audit: dict[str, object]) -> None:
    rows = [{"Item": key, "Value": value} for key, value in audit.items()]
    DATA_AUDIT.write_text(
        "# HAA Data Audit\n\n"
        "Status: data-readiness audit for `studies/haa_hybrid_asset_allocation/`.\n\n"
        "The Tiingo cache is the preferred source for `only_stocks` and "
        "`stocks_plus_etfs`, because yfinance/current-universe stock tests carry "
        "survivorship bias [advances_fin_ml, p.208-211]. Testfol.io is the preferred "
        "source only for canonical long-history ETF reproduction.\n\n"
        + md_table(rows, ["Item", "Value"])
        + "\n## Interpretation\n\n"
        "If `tiingo_parquet_count` is `0`, restore `data/tiingo/daily/prices/*.parquet` "
        "from the subscription-era backup before running stock or ETF Tiingo variants. "
        "The committed manifest alone is not enough for a backtest.\n",
        encoding="utf-8",
    )


def choose_liquid_tickers(
    grouped: dict[str, list[str]],
    asset_class: str,
    limit: int,
    exclude: set[str] | None = None,
) -> list[str]:
    """Pick a deterministic manifest subset; liquidity filtering happens after prices load."""
    exclude = exclude or set()
    tickers = [ticker for ticker in grouped.get(asset_class, []) if ticker not in exclude]
    return tickers[:limit]


def build_configs(args: argparse.Namespace) -> list[HAAConfig]:
    grouped = manifest_tickers_by_asset_class(TIINGO_ROOT)
    configs: list[HAAConfig] = []

    if args.variant in {"all", "only_etfs_canonical"}:
        configs.append(HAA_BALANCED_G8_T4)

    if args.variant in {"all", "only_etfs_no_vnq"}:
        configs.append(HAA_BALANCED_G8_T4_NO_VNQ)

    if args.variant in {"all", "only_etfs_bestfolio_seed"}:
        configs.append(HAA_BESTFOLIO_NO_QQQ_SEED)

    if args.variant in {"all", "only_etfs_tiingo"}:
        etfs = choose_liquid_tickers(grouped, "etf", args.max_assets, set(CANARY_AND_DEFENSIVE))
        for top_n in DEFAULT_STOCK_TOP_N:
            configs.append(
                HAAConfig(
                    name=f"haa_only_etfs_tiingo_top{top_n}",
                    offensive_assets=tuple(etfs),
                    top_n=top_n,
                    min_offensive_assets=top_n,
                )
            )

    if args.variant in {"all", "only_stocks"}:
        stocks = choose_liquid_tickers(
            grouped, "equity", args.max_assets, set(CANARY_AND_DEFENSIVE)
        )
        for top_n in DEFAULT_STOCK_TOP_N:
            configs.append(
                HAAConfig(
                    name=f"haa_only_stocks_tiingo_top{top_n}",
                    offensive_assets=tuple(stocks),
                    top_n=top_n,
                    min_offensive_assets=top_n,
                )
            )

    if args.variant in {"all", "stocks_plus_etfs"}:
        stocks = choose_liquid_tickers(
            grouped, "equity", args.max_assets // 2, set(CANARY_AND_DEFENSIVE)
        )
        etfs = choose_liquid_tickers(
            grouped, "etf", args.max_assets // 2, set(CANARY_AND_DEFENSIVE)
        )
        universe = tuple(stocks + etfs)
        for top_n in DEFAULT_STOCK_TOP_N:
            configs.append(
                HAAConfig(
                    name=f"haa_stocks_plus_etfs_tiingo_top{top_n}",
                    offensive_assets=universe,
                    top_n=top_n,
                    min_offensive_assets=top_n,
                )
            )

    return configs


def source_for_config(config: HAAConfig, requested: str) -> str:
    if requested != "auto":
        return requested
    if config.name in {
        HAA_BALANCED_G8_T4.name,
        HAA_BALANCED_G8_T4_NO_VNQ.name,
        HAA_BESTFOLIO_NO_QQQ_SEED.name,
    }:
        return "testfolio"
    return "tiingo"


def load_prices_for_config(config: HAAConfig, source: str, args: argparse.Namespace) -> pd.DataFrame:
    if source == "testfolio":
        return load_testfolio_price_frame(
            config.required_assets,
            path=TESTFOLIO_CACHE,
            start=args.start,
            end=args.end,
        )
    if source == "tiingo":
        return load_tiingo_price_frame(
            config.required_assets, root=TIINGO_ROOT, start=args.start, end=args.end
        )
    if source == "yfinance":
        if not args.allow_biased_yfinance:
            raise ValueError(
                "yfinance source requires --allow-biased-yfinance; it is a "
                "current-universe/survivorship-biased screen, not promotion evidence."
            )
        return load_yfinance_price_frame(
            config.required_assets, start=args.start, end=args.end, allow_missing=True
        )
    raise ValueError(f"unknown source {source!r}")


def adapt_config_to_available_prices(config: HAAConfig, prices: pd.DataFrame) -> HAAConfig:
    """Drop missing yfinance offensive tickers while preserving mandatory HAA legs."""
    missing = {str(ticker).upper() for ticker in prices.attrs.get("missing_tickers", [])}
    is_yfinance_frame = "missing_tickers" in prices.attrs
    base_name = config.name.replace("_tiingo", "_yf") if is_yfinance_frame else config.name
    if is_yfinance_frame and base_name == config.name:
        base_name = f"{config.name}_yf"
    if not missing and base_name == config.name:
        return config

    required_non_offensive = {config.canary_asset.upper()} | {
        asset.upper() for asset in config.defensive_assets
    }
    missing_required = sorted(missing & required_non_offensive)
    if missing_required:
        raise FileNotFoundError(f"missing required HAA canary/defensive assets: {missing_required}")

    available_offensive = tuple(
        asset for asset in config.offensive_assets if asset.upper() not in missing
    )
    if len(available_offensive) < config.top_n:
        raise FileNotFoundError(
            f"only {len(available_offensive)} offensive yfinance assets remain after missing "
            f"{sorted(missing)}; top_n={config.top_n}"
        )

    if len(available_offensive) == len(config.offensive_assets) and base_name == config.name:
        return config
    name = base_name
    if len(available_offensive) != len(config.offensive_assets):
        name = f"{base_name}_available{len(available_offensive)}"
    return HAAConfig(
        name=name,
        offensive_assets=available_offensive,
        canary_asset=config.canary_asset,
        defensive_assets=config.defensive_assets,
        top_n=config.top_n,
        lookback_months=config.lookback_months,
        min_offensive_assets=min(config.min_required_offensive_assets, len(available_offensive)),
    )


def apply_annual_darf(
    returns: pd.Series, weights: pd.DataFrame
) -> tuple[pd.Series, dict[str, object]]:
    """Apply the shared annual DARF model to a gross return stream."""
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    prev_value = engine.port_value
    prev_weights = {col: 0.0 for col in weights.columns}
    net_returns: list[float] = []
    last_year: int | None = None

    for date, daily_return in returns.items():
        current_weights = weights.loc[date].to_dict() if date in weights.index else prev_weights
        if any(
            abs(current_weights.get(key, 0.0) - prev_weights.get(key, 0.0)) > 1e-9
            for key in set(current_weights) | set(prev_weights)
        ):
            engine.record_trade(date, prev_weights, current_weights)
            prev_weights = current_weights

        if last_year is not None and date.year != last_year:
            engine.year_end_settlement(last_year)
        last_year = int(date.year)

        engine.apply_return(float(daily_return))
        new_value = engine.port_value
        net_returns.append(new_value / prev_value - 1.0)
        prev_value = new_value

    if last_year is not None:
        pre_settle = prev_value
        engine.year_end_settlement(last_year, force=True)
        if net_returns and pre_settle > 0:
            net_returns[-1] = (1.0 + net_returns[-1]) * (engine.port_value / pre_settle) - 1.0

    return pd.Series(
        net_returns, index=returns.index, name=f"{returns.name}_after_tax"
    ), engine.summary() | {"events": engine.events}


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
        sample = np.concatenate([arr[start:start + block] for start in starts])[: len(arr)]
        sigma = sample.std(ddof=0)
        if sigma > 1e-12:
            values.append(float(sample.mean() / sigma * np.sqrt(TRADING_DAYS_PER_YEAR)))
    return float(np.percentile(values, 0.1)) if values else float("nan")


def evaluate_config(
    config: HAAConfig, source: str, prices: pd.DataFrame, n_trials: int
) -> dict[str, object]:
    gross, weights = simulate_haa_gross(prices, config)
    net, tax_summary = apply_annual_darf(gross, weights)
    loop = simulate_haa_holdings_loop(prices, config).reindex(gross.index).dropna()
    aligned = pd.concat({"vectorized": gross, "loop": loop}, axis=1).dropna()
    xlib_delta_pp = 0.0
    if not aligned.empty:
        vec_metrics = metrics_from_returns(aligned["vectorized"])
        loop_metrics = metrics_from_returns(aligned["loop"])
        xlib_delta_pp = abs(float(vec_metrics["cagr"]) - float(loop_metrics["cagr"])) * 100.0

    p_value = 1.0
    if len(net) >= 3:
        arr = net.to_numpy(dtype=float)
        if n_trials >= 2:
            p_value = float(dsr(arr, n_trials=n_trials).p_value)
        else:
            p_value = 1.0 - float(psr(arr, benchmark=0.0))

    wf = walk_forward_diagnostic(net)
    oos = net.iloc[int(len(net) * 0.70):]
    fwd = net[net.index >= "2020-01-01"]
    boot_low = bootstrap_sharpe_ci_low(net)

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
        "config": asdict(config),
        "source": source,
        "promotion_eligible": source != "yfinance",
        "data_caveat": (
            "yfinance current-universe/survivorship-biased screen only"
            if source == "yfinance"
            else "none"
        ),
        "gross_metrics": metrics_from_returns(gross),
        "after_tax_metrics": metrics_from_returns(net),
        "tax_summary": tax_summary,
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


def pbo_for_results(
    results: list[dict[str, object]], returns_by_name: dict[str, pd.Series]
) -> dict[str, object]:
    if len(returns_by_name) < 2:
        return {
            "pbo": float("nan"),
            "n_combinations": 0,
            "pass_gate": True,
            "note": "single config",
        }
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


def write_report(
    results: list[dict[str, object]], pbo_result: dict[str, object], errors: list[str]
) -> None:
    rows: list[dict[str, object]] = []
    for result in results:
        metrics = result["after_tax_metrics"]
        gates = result["gates"]
        rows.append(
            {
                "Config": result["config"]["name"],
                "Source": result["source"],
                "Window": f"{metrics['start']}..{metrics['end']}",
                "CAGR": fmt_pct(float(metrics["cagr"])),
                "MDD": fmt_pct(float(metrics["mdd"])),
                "Sharpe": fmt_num(float(metrics["sharpe"])),
                "Calmar": fmt_num(float(metrics["calmar"])),
                "Gates ex-PBO": f"{gates['n_passed_ex_pbo']}/6",
                "Promotion eligible": result["promotion_eligible"],
            }
        )

    error_text = "\n".join(f"- {error}" for error in errors) if errors else "_No run errors._"
    any_promotion_eligible = any(bool(result.get("promotion_eligible")) for result in results)
    all_yfinance = bool(results) and all(result.get("source") == "yfinance" for result in results)
    pbo_pass = bool(pbo_result.get("pass_gate"))
    if not results:
        verdict = "No successful result rows; current run is data-blocked."
    elif all_yfinance:
        verdict = (
            "Screen-only FAIL: all result rows use yfinance, so `promotion_eligible=false`; "
            "current-universe yfinance data cannot support a winner without PIT/delisted "
            "validation [advances_fin_ml, p.208-211]."
        )
    elif not any_promotion_eligible:
        verdict = "Screen-only FAIL: no result row is promotion-eligible."
    elif not pbo_pass:
        verdict = "FAIL: PBO gate did not pass [advances_fin_ml, p.208-211]."
    else:
        verdict = "Diagnostic pass only; mandate promotion still requires all hard gates."

    REPORT.write_text(
        "# HAA Hybrid Asset Allocation Study Report\n\n"
        "Status: research-only. No deployment, paper-trade label or mandate change.\n\n"
        "## Verdict\n\n"
        f"{verdict}\n\n"
        "## Method\n\n"
        "HAA ranks offensive assets by equal-weighted 1/3/6/12-month momentum, "
        "uses TIP as a canary, and replaces risk-off slots with the stronger "
        "defensive asset between BIL and IEF. Momentum and monthly cadence are "
        "anchored in `[stocks_on_the_move, p.60]` and `[stocks_on_the_move, "
        "p.98-99]`; validation gates follow `[advances_fin_ml, p.208-211]` and "
        "`[advances_fin_ml, p.273-275]`.\n\n"
        "## Results\n\n"
        + md_table(
            rows,
            [
                "Config",
                "Source",
                "Window",
                "CAGR",
                "MDD",
                "Sharpe",
                "Calmar",
                "Gates ex-PBO",
                "Promotion eligible",
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
        "- Testfol.io ETF histories are synthetic/modelled before ETF inception.\n"
        "- `haa_balanced_g8_t4_no_vnq_proxy` is not canonical; it exists only because "
        "VNQSIM is unavailable in the current Testfol.io cache/API sample.\n"
        "- Tiingo stock/ETF tests require restored `data/tiingo/daily/prices/*.parquet`; "
        "the manifest alone is not enough.\n"
        "- yfinance runs require `--allow-biased-yfinance` and are current-universe/"
        "survivorship-biased screens only; `promotion_eligible=false` for those rows.\n"
        "- Stock universes still need survivorship-free/delisted validation before any "
        "promotion claim.\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HAA study variants")
    parser.add_argument(
        "--variant",
        choices=[
            "all",
            "only_etfs_canonical",
            "only_etfs_no_vnq",
            "only_etfs_bestfolio_seed",
            "only_etfs_tiingo",
            "only_stocks",
            "stocks_plus_etfs",
        ],
        default="all",
    )
    parser.add_argument(
        "--source", choices=["auto", "tiingo", "testfolio", "yfinance"], default="auto"
    )
    parser.add_argument(
        "--allow-biased-yfinance",
        action="store_true",
        help="explicitly allow yfinance current-universe/survivorship-biased screen rows",
    )
    parser.add_argument(
        "--max-assets", type=int, default=120, help="manifest subset size for broad variants"
    )
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--audit-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    audit = audit_data()
    write_data_audit(audit)
    if args.audit_only:
        print(f"wrote {DATA_AUDIT.relative_to(REPO_ROOT)}")
        return 0

    configs = build_configs(args)
    if not configs:
        raise RuntimeError(f"no configs built for variant={args.variant}")

    results: list[dict[str, object]] = []
    returns_by_name: dict[str, pd.Series] = {}
    errors: list[str] = []
    n_trials = len(configs)
    for config in configs:
        source = source_for_config(config, args.source)
        try:
            prices = load_prices_for_config(config, source, args)
            eval_config = adapt_config_to_available_prices(config, prices)
            result = evaluate_config(eval_config, source, prices, n_trials=n_trials)
            results.append(result)
            gross, weights = simulate_haa_gross(prices, eval_config)
            net, _tax = apply_annual_darf(gross, weights)
            returns_by_name[eval_config.name] = net
        except Exception as exc:  # data-blocked variants should not hide successful ones
            error_name = config.name.replace("_tiingo", "_yf") if source == "yfinance" else config.name
            errors.append(f"{error_name} ({source}): {exc}")

    pbo_result = pbo_for_results(results, returns_by_name) if results else {"pbo": float("nan"), "pass_gate": False, "note": "no successful configs"}
    payload = json_safe({"results": results, "pbo": pbo_result, "errors": errors})
    (RESULTS_DIR / "results.json").write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
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
