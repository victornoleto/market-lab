#!/usr/bin/env python3
"""Validate frozen weekly momentum deploy candidates.

This runner compares two fixed strategies with two dynamic walk-forward
strategies. Fixed candidates test whether one pre-specified parameter set is
stable. Dynamic candidates test whether the frozen walk-forward selection process
works when parameters are chosen only from prior train windows
`[advances_fin_ml, p.208-211]`.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from market_lab.backtest.data.tiingo_storage import TiingoStorage
from market_lab.backtest.metrics.standard_report import load_spy_series
from market_lab.backtest.validation.dsr import dsr as compute_dsr
from market_lab.backtest.validation.pbo import pbo as compute_pbo
from studies._shared.tax_engine import AnnualDarfEngine
from studies.weekly_momentum.core import WeeklyMomentumConfig, simulate_weekly_momentum
from studies.weekly_momentum.data import load_variation_prices, sp500_pit_universe_provider
from studies.weekly_momentum.reporting import (
    build_spy_benchmark,
    compute_report_metrics,
    config_slug,
    write_run_outputs,
)
from studies.weekly_momentum.scripts.sweep import SUBPERIODS, rolling_edge_metrics
from studies.weekly_momentum.scripts.walk_forward import (
    _build_configs,
    _parse_ints,
    _parse_market_filters,
    _run_walk_forward,
    _walk_forward_windows,
)


@dataclass(frozen=True)
class Candidate:
    name: str
    kind: str
    variation: str
    only_sp500: bool
    config: WeeklyMomentumConfig | None = None


FIXED_CANDIDATES = [
    Candidate(
        name="fixed_aggressive_sp500",
        kind="fixed",
        variation="stocks",
        only_sp500=True,
        config=WeeklyMomentumConfig(
            lookback_days=60,
            top_k=3,
            allow_negative_momentum=False,
            market_filter_type="sma",
            market_filter_days=200,
        ),
    ),
    Candidate(
        name="fixed_balanced_sp500",
        kind="fixed",
        variation="stocks",
        only_sp500=True,
        config=WeeklyMomentumConfig(
            lookback_days=60,
            top_k=10,
            allow_negative_momentum=False,
            market_filter_type="sma",
            market_filter_days=100,
        ),
    ),
    Candidate(
        name="phase2_fixed_lb80_k5_sma200",
        kind="fixed_phase2",
        variation="stocks",
        only_sp500=True,
        config=WeeklyMomentumConfig(
            lookback_days=80,
            top_k=5,
            allow_negative_momentum=False,
            market_filter_type="sma",
            market_filter_days=200,
        ),
    ),
    Candidate(
        name="phase2_fixed_lb80_k4_sma200",
        kind="fixed_phase2",
        variation="stocks",
        only_sp500=True,
        config=WeeklyMomentumConfig(
            lookback_days=80,
            top_k=4,
            allow_negative_momentum=False,
            market_filter_type="sma",
            market_filter_days=200,
        ),
    ),
    Candidate(
        name="phase2_fixed_lb80_k5_sma250",
        kind="fixed_phase2",
        variation="stocks",
        only_sp500=True,
        config=WeeklyMomentumConfig(
            lookback_days=80,
            top_k=5,
            allow_negative_momentum=False,
            market_filter_type="sma",
            market_filter_days=250,
        ),
    ),
]

DYNAMIC_CANDIDATES = [
    Candidate(name="dynamic_wf_sp500", kind="dynamic_wf", variation="stocks", only_sp500=True),
    Candidate(name="dynamic_wf_all_stocks", kind="dynamic_wf", variation="stocks", only_sp500=False),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate weekly momentum deploy candidates")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--storage-root", default="data/tiingo")
    parser.add_argument("--spy-path", default="data/tiingo/daily/prices/SPY.parquet")
    parser.add_argument("--output-dir", default="studies/weekly_momentum/deploy_candidates")
    parser.add_argument("--lookbacks", default="4,20,60,90,126")
    parser.add_argument("--top-ks", default="3,5,10,20")
    parser.add_argument("--market-filters", default="none,sma100,sma200,ema100,ema200")
    parser.add_argument("--allow-negative-momentum", default="0,1")
    parser.add_argument("--train-years", type=int, default=3)
    parser.add_argument("--test-years", type=int, default=1)
    parser.add_argument("--cost-bps", default="0,10,25,50", help="One-way transaction cost stress in bps.")
    parser.add_argument("--tax-cost-bps", type=float, default=10.0, help="Cost bps used before annual DARF tax stress.")
    parser.add_argument("--liquidity-aum", type=float, default=100_000.0, help="Reference AUM for ADV usage diagnostics.")
    parser.add_argument("--min-age-bars", type=int, default=0, help="Drop symbols with fewer non-NaN price bars.")
    parser.add_argument("--min-median-adv20", type=float, default=0.0, help="Drop symbols below median 20d dollar volume threshold.")
    parser.add_argument("--pit-min-age-bars", type=int, default=0, help="Point-in-time minimum observed bars before a symbol can enter the ranking universe.")
    parser.add_argument("--pit-min-adv20", type=float, default=0.0, help="Point-in-time minimum 20d average dollar volume before a symbol can enter the ranking universe.")
    parser.add_argument("--pit-min-price", type=float, default=0.0, help="Point-in-time minimum adjusted price before a symbol can enter the ranking universe.")
    parser.add_argument("--progress-every", type=int, default=25, help="Print progress every N configs for dynamic candidates.")
    parser.add_argument("--sp500-pit", action="store_true", help="Use approximate Wikipedia point-in-time S&P 500 membership at signal time.")
    parser.add_argument(
        "--pit-load-all-stocks",
        action="store_true",
        help="When --sp500-pit is enabled, load all cached equities before PIT filtering so removed/delisted names can participate.",
    )
    parser.add_argument(
        "--candidates",
        default="fixed_aggressive_sp500,fixed_balanced_sp500,dynamic_wf_sp500,dynamic_wf_all_stocks",
        help="Comma-separated candidate names to run.",
    )
    parser.add_argument("--plots-only", action="store_true", help="Regenerate plots/report from existing CSV outputs.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    start = date.fromisoformat(args.start) if args.start else None
    end = date.fromisoformat(args.end) if args.end else None
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.plots_only:
        summary = pd.read_csv(out_dir / "candidate_comparison.csv")
        subperiods = pd.read_csv(out_dir / "candidate_subperiods.csv")
        windows = pd.read_csv(out_dir / "candidate_windows.csv")
        _write_combined_plots(out_dir, summary)
        _write_report(out_dir / "CANDIDATE_VALIDATION_REPORT.md", summary, subperiods, windows, args)
        print("plots_only=1")
        print(f"outputs={out_dir}")
        return 0

    spy = load_spy_series(args.spy_path)
    summary_rows: list[dict[str, object]] = []
    subperiod_rows: list[dict[str, object]] = []
    window_rows: list[dict[str, object]] = []

    candidate_names = {name.strip() for name in args.candidates.split(",") if name.strip()}
    for candidate in FIXED_CANDIDATES:
        if candidate.name not in candidate_names:
            continue
        row, sub_rows, win_rows = _run_fixed_candidate(candidate, args, start, end, spy, out_dir)
        summary_rows.append(row)
        subperiod_rows.extend(sub_rows)
        window_rows.extend(win_rows)

    for candidate in DYNAMIC_CANDIDATES:
        if candidate.name not in candidate_names:
            continue
        row, sub_rows, win_rows = _run_dynamic_candidate(candidate, args, start, end, spy, out_dir)
        summary_rows.append(row)
        subperiod_rows.extend(sub_rows)
        window_rows.extend(win_rows)

    if not summary_rows:
        raise SystemExit("No candidates selected")

    summary = pd.DataFrame(summary_rows).sort_values("candidate")
    subperiods = pd.DataFrame(subperiod_rows).sort_values(["candidate", "subperiod"])
    windows = pd.DataFrame(window_rows).sort_values(["candidate", "test_start"])
    summary = _apply_oos_and_family_gate_context(summary, windows)

    summary.to_csv(out_dir / "candidate_comparison.csv", index=False)
    subperiods.to_csv(out_dir / "candidate_subperiods.csv", index=False)
    windows.to_csv(out_dir / "candidate_windows.csv", index=False)
    _write_combined_plots(out_dir, summary)
    _write_report(out_dir / "CANDIDATE_VALIDATION_REPORT.md", summary, subperiods, windows, args)

    print(f"candidates={len(summary)}")
    print(f"outputs={out_dir}")
    print(summary[["candidate", "kind", "universe", "cagr", "mdd", "sharpe", "spy_cagr", "spy_mdd", "spy_sharpe"]].to_string(index=False))
    return 0


def _run_fixed_candidate(
    candidate: Candidate,
    args: argparse.Namespace,
    start: date | None,
    end: date | None,
    spy: pd.Series,
    out_dir: Path,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    assert candidate.config is not None
    prices = load_variation_prices(
        candidate.variation,
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=candidate.config.lookback_days + 2,
        only_sp500=_load_only_sp500(candidate, args),
    )
    prices = _filter_prices_for_phase2(prices, args)
    universe_provider = _universe_provider_for(candidate, args, prices)
    result = simulate_weekly_momentum(
        prices,
        candidate.config,
        market_filter_prices=spy if candidate.config.market_filter_type != "none" else None,
        universe_by_date=universe_provider,
    )
    candidate_dir = out_dir / candidate.name
    payload = write_run_outputs(
        out_dir=candidate_dir,
        variation=candidate.variation,
        config=candidate.config,
        result=result,
        n_assets=prices.shape[1],
        universe_label=_universe_label(candidate, args),
        spy_path=args.spy_path,
    )
    spy_equity, spy_returns = build_spy_benchmark(result.equity, candidate.config.initial_cash, args.spy_path)
    aligned = _align(result.equity, result.returns, spy_equity, spy_returns)
    _write_candidate_series_and_plots(candidate_dir, candidate.name, aligned)
    windows = _walk_forward_windows(aligned.index, args.train_years, args.test_years)
    return (
        _summary_row(
            candidate,
            payload["metrics"]["strategy"],
            payload["metrics"]["spy"],
            aligned["strategy_return"],
            result.weights,
            aligned["strategy_equity"],
            aligned["spy_equity"],
            prices.shape[1],
            candidate_dir,
            args,
        ),
        _subperiod_rows(candidate, aligned["strategy_return"], aligned["spy_return"]),
        _fixed_window_rows(candidate, aligned["strategy_return"], aligned["spy_return"], windows),
    )


def _run_dynamic_candidate(
    candidate: Candidate,
    args: argparse.Namespace,
    start: date | None,
    end: date | None,
    spy: pd.Series,
    out_dir: Path,
) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    lookbacks = _parse_ints(args.lookbacks)
    top_ks = _parse_ints(args.top_ks)
    market_filters = _parse_market_filters(None, args.market_filters)
    allow_negative_values = [bool(v) for v in _parse_ints(args.allow_negative_momentum)]
    prices = load_variation_prices(
        candidate.variation,
        storage_root=args.storage_root,
        start=start,
        end=end,
        min_bars=max(lookbacks) + 2,
        only_sp500=_load_only_sp500(candidate, args),
    )
    prices = _filter_prices_for_phase2(prices, args)
    configs = _build_configs(lookbacks, top_ks, market_filters, allow_negative_values)
    returns_by_config: dict[str, pd.Series] = {}
    weights_by_config: dict[str, pd.DataFrame] = {}
    config_payload = {}
    aligned_spy = spy.reindex(prices.index).ffill()
    universe_provider = _universe_provider_for(candidate, args, prices)
    for cfg in configs:
        slug = config_slug(cfg)
        idx = len(returns_by_config) + 1
        if args.progress_every > 0 and (idx == 1 or idx % args.progress_every == 0 or idx == len(configs)):
            print(f"dynamic_candidate={candidate.name} config={idx}/{len(configs)} slug={slug}", flush=True)
        result = simulate_weekly_momentum(
            prices,
            cfg,
            market_filter_prices=aligned_spy if cfg.market_filter_type != "none" else None,
            universe_by_date=universe_provider,
        )
        returns_by_config[slug] = result.returns
        weights_by_config[slug] = result.weights
        config_payload[slug] = asdict(cfg)

    windows = _walk_forward_windows(prices.index, args.train_years, args.test_years)
    selections, wf_returns = _run_walk_forward(returns_by_config, windows)
    wf_equity = (1.0 + wf_returns).cumprod() * 10_000.0
    spy_returns = aligned_spy.pct_change(fill_method=None).fillna(0.0).reindex(wf_returns.index).fillna(0.0)
    spy_equity = (1.0 + spy_returns).cumprod() * 10_000.0
    metrics = compute_report_metrics(wf_equity, wf_returns)
    spy_metrics = compute_report_metrics(spy_equity, spy_returns)
    weights = _splice_weights(weights_by_config, selections)
    candidate_dir = out_dir / candidate.name
    candidate_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(selections).to_csv(candidate_dir / "selections.csv", index=False)
    pd.DataFrame({"strategy_return": wf_returns, "strategy_equity": wf_equity, "spy_return": spy_returns, "spy_equity": spy_equity}).to_csv(candidate_dir / "equity.csv")
    weights.to_csv(candidate_dir / "weights.csv")
    (candidate_dir / "config_grid.json").write_text(json.dumps(config_payload, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame({"strategy": metrics, "spy": spy_metrics}).to_csv(candidate_dir / "metrics.csv")
    aligned = _align(wf_equity, wf_returns, spy_equity, spy_returns)
    _write_candidate_series_and_plots(candidate_dir, candidate.name, aligned)
    row = _summary_row(candidate, metrics, spy_metrics, wf_returns, weights, wf_equity, spy_equity, prices.shape[1], candidate_dir, args)
    row.update(_pbo_family_metrics(returns_by_config))
    return (
        row,
        _subperiod_rows(candidate, wf_returns, spy_returns),
        _dynamic_window_rows(candidate, selections, spy_returns),
    )


def _summary_row(
    candidate: Candidate,
    metrics: dict[str, float],
    spy_metrics: dict[str, float],
    returns: pd.Series,
    weights: pd.DataFrame,
    strategy_equity: pd.Series,
    spy_equity: pd.Series,
    n_assets: int,
    output_dir: Path,
    args: argparse.Namespace,
) -> dict[str, object]:
    exposure = weights.sum(axis=1).clip(0.0, 1.0) if not weights.empty else pd.Series(dtype=float)
    active = weights.gt(0.0).sum(axis=1) if not weights.empty else pd.Series(dtype=float)
    turnover = _annualized_turnover(weights)
    roll = rolling_edge_metrics(strategy_equity, spy_equity)
    cost_metrics = _cost_stress_metrics(returns, weights, _parse_float_list(args.cost_bps))
    tax_metrics = _tax_stress_metrics(returns, weights, args.tax_cost_bps)
    liquidity = _liquidity_summary(weights, args.storage_root, args.liquidity_aum)
    anti_overfit = _candidate_anti_overfit_metrics(returns, _dynamic_grid_n_trials(args))
    row = {
        "candidate": candidate.name,
        "kind": candidate.kind,
        "universe": _universe_label(candidate, args),
        "n_assets": n_assets,
        "avg_exposure": float(exposure.mean()) if len(exposure) else float("nan"),
        "avg_positions_when_invested": float(active[active > 0].mean()) if (active > 0).any() else 0.0,
        "annualized_turnover_proxy": turnover,
        "output_dir": output_dir.as_posix(),
        "pbo_family": float("nan"),
        "pbo_family_pass": "not_run_fixed_context_pending",
        "pbo_family_n_combinations": 0,
    }
    row.update({key: float(value) for key, value in metrics.items()})
    row.update({f"spy_{key}": float(value) for key, value in spy_metrics.items()})
    row.update({key: value for key, value in roll.items() if key not in row})
    row.update(cost_metrics)
    row.update(tax_metrics)
    row.update(liquidity)
    row.update(anti_overfit)
    return row


def _cost_stress_metrics(
    gross_returns: pd.Series,
    weights: pd.DataFrame,
    cost_bps_values: list[float],
) -> dict[str, float]:
    out: dict[str, float] = {}
    turnover = _daily_turnover(weights).reindex(gross_returns.index).fillna(0.0)
    for bps in cost_bps_values:
        net_returns = _apply_transaction_costs(gross_returns, turnover, bps)
        net_equity = (1.0 + net_returns).cumprod() * 10_000.0
        metrics = compute_report_metrics(net_equity, net_returns)
        suffix = _bps_suffix(bps)
        out[f"cost{suffix}_cagr"] = metrics["cagr"]
        out[f"cost{suffix}_mdd"] = metrics["mdd"]
        out[f"cost{suffix}_sharpe"] = metrics["sharpe"]
    return out


def _tax_stress_metrics(
    gross_returns: pd.Series,
    weights: pd.DataFrame,
    cost_bps: float,
) -> dict[str, float]:
    turnover = _daily_turnover(weights).reindex(gross_returns.index).fillna(0.0)
    costed_returns = _apply_transaction_costs(gross_returns, turnover, cost_bps)
    net_returns, tax_paid = _apply_annual_darf_tax(costed_returns, weights)
    net_equity = (1.0 + net_returns).cumprod() * 10_000.0
    metrics = compute_report_metrics(net_equity, net_returns)
    suffix = _bps_suffix(cost_bps)
    return {
        f"cost{suffix}_tax_cagr": metrics["cagr"],
        f"cost{suffix}_tax_mdd": metrics["mdd"],
        f"cost{suffix}_tax_sharpe": metrics["sharpe"],
        f"cost{suffix}_tax_paid_pct_initial": tax_paid / 10_000.0,
    }


def _apply_transaction_costs(gross_returns: pd.Series, turnover: pd.Series, cost_bps: float) -> pd.Series:
    cost_rate = cost_bps / 10_000.0
    aligned_turnover = turnover.reindex(gross_returns.index).fillna(0.0)
    # One-way turnover × bps drag. This is a stress proxy before execution-grade fills.
    return ((1.0 + gross_returns) * (1.0 - aligned_turnover * cost_rate) - 1.0).rename(gross_returns.name)


def _apply_annual_darf_tax(returns: pd.Series, weights: pd.DataFrame) -> tuple[pd.Series, float]:
    engine = AnnualDarfEngine(initial_investment=10_000.0)
    weights = weights.reindex(returns.index).fillna(0.0)
    prev_weights: dict[str, float] = {}
    out = []
    for idx, ts in enumerate(returns.index):
        before = engine.port_value
        current_weights = _weights_dict(weights.loc[ts])
        if current_weights != prev_weights:
            engine.record_trade(ts, prev_weights, current_weights)
        engine.apply_return(float(returns.loc[ts]))
        next_ts = returns.index[idx + 1] if idx + 1 < len(returns.index) else None
        if next_ts is None or pd.Timestamp(next_ts).year != pd.Timestamp(ts).year:
            engine.year_end_settlement(pd.Timestamp(ts).year, force=next_ts is None)
        out.append(engine.port_value / before - 1.0 if before > 0 else 0.0)
        prev_weights = current_weights
    return pd.Series(out, index=returns.index, name=returns.name), engine.total_darf_paid


def _liquidity_summary(weights: pd.DataFrame, storage_root: str, reference_aum: float) -> dict[str, float]:
    held_symbols = sorted(weights.columns[weights.gt(0.0).any(axis=0)]) if not weights.empty else []
    if not held_symbols:
        return _empty_liquidity_summary()
    dollar_volume = _load_dollar_volume(held_symbols, storage_root).reindex(weights.index)
    if dollar_volume.empty:
        return _empty_liquidity_summary(unique_held_symbols=len(held_symbols))
    adv20 = dollar_volume.rolling(20, min_periods=5).mean()
    bars_available = dollar_volume.notna().cumsum()
    held_mask = weights[adv20.columns].gt(0.0)
    held_adv = adv20.where(held_mask).stack()
    held_age = bars_available.where(held_mask).stack()
    position_adv_usage = (weights[adv20.columns] * reference_aum / adv20).where(held_mask).stack()
    return {
        "unique_held_symbols": float(len(held_symbols)),
        "median_held_adv20": float(held_adv.median()) if len(held_adv) else float("nan"),
        "min_held_adv20": float(held_adv.min()) if len(held_adv) else float("nan"),
        "pct_held_obs_adv20_lt_1m": float((held_adv < 1_000_000.0).mean()) if len(held_adv) else float("nan"),
        "pct_held_obs_adv20_lt_5m": float((held_adv < 5_000_000.0).mean()) if len(held_adv) else float("nan"),
        "pct_held_obs_age_lt_252d": float((held_age < 252.0).mean()) if len(held_age) else float("nan"),
        "max_position_adv20_usage_100k": float(position_adv_usage.max()) if len(position_adv_usage) else float("nan"),
    }


def _load_dollar_volume(symbols: list[str], storage_root: str) -> pd.DataFrame:
    storage = TiingoStorage(root=Path(storage_root))
    series = []
    for symbol in symbols:
        try:
            df = storage.read(symbol, frequency="daily")
        except (FileNotFoundError, KeyError):
            continue
        if "close" not in df.columns or "volume" not in df.columns:
            continue
        close = pd.to_numeric(df["close"], errors="coerce")
        volume = pd.to_numeric(df["volume"], errors="coerce")
        series.append((close * volume).rename(symbol))
    if not series:
        return pd.DataFrame()
    return pd.concat(series, axis=1, sort=True).sort_index()


def _filter_prices_for_phase2(prices: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    keep = pd.Series(True, index=prices.columns)
    if args.min_age_bars > 0:
        keep &= prices.notna().sum(axis=0) >= args.min_age_bars
    if args.min_median_adv20 > 0:
        dollar_volume = _load_dollar_volume(list(prices.columns), args.storage_root).reindex(prices.index)
        adv20 = dollar_volume.rolling(20, min_periods=5).mean().median(axis=0)
        keep &= adv20.reindex(prices.columns).fillna(0.0) >= args.min_median_adv20
    filtered = prices.loc[:, keep[keep].index]
    if filtered.empty:
        raise SystemExit("All symbols were removed by phase2 filters")
    return filtered


def _empty_liquidity_summary(unique_held_symbols: int = 0) -> dict[str, float]:
    return {
        "unique_held_symbols": float(unique_held_symbols),
        "median_held_adv20": float("nan"),
        "min_held_adv20": float("nan"),
        "pct_held_obs_adv20_lt_1m": float("nan"),
        "pct_held_obs_adv20_lt_5m": float("nan"),
        "pct_held_obs_age_lt_252d": float("nan"),
        "max_position_adv20_usage_100k": float("nan"),
    }


def _candidate_anti_overfit_metrics(returns: pd.Series, n_trials: int) -> dict[str, object]:
    clean = returns.dropna()
    if len(clean) < 252:
        return {
            "dsr_p_value": float("nan"),
            "dsr_pass": False,
            "bootstrap_cagr_ci_low_0p1pct": float("nan"),
            "bootstrap_sharpe_ci_low_0p1pct": float("nan"),
            "bootstrap_pass": False,
        }
    dsr_res = compute_dsr(clean.to_numpy(dtype=float), n_trials=n_trials)
    boot = _block_bootstrap_ci(clean)
    return {
        "dsr_p_value": float(dsr_res.p_value),
        "dsr_pass": bool(dsr_res.p_value < 0.05),
        "bootstrap_cagr_ci_low_0p1pct": boot["cagr_low"],
        "bootstrap_sharpe_ci_low_0p1pct": boot["sharpe_low"],
        "bootstrap_pass": bool(boot["cagr_low"] > 0.0),
    }


def _pbo_family_metrics(returns_by_config: dict[str, pd.Series]) -> dict[str, object]:
    aligned = pd.concat(returns_by_config, axis=1, sort=True).dropna()
    if aligned.shape[0] < 252 or aligned.shape[1] < 4:
        return {
            "pbo_family": float("nan"),
            "pbo_family_pass": "not_run_insufficient_grid",
            "pbo_family_n_combinations": 0,
        }
    result = compute_pbo(aligned.to_numpy(dtype=float), n_blocks=10)
    return {
        "pbo_family": float(result.pbo),
        "pbo_family_pass": bool(result.pbo < 0.5),
        "pbo_family_n_combinations": int(result.n_combinations),
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


def _dynamic_grid_n_trials(args: argparse.Namespace) -> int:
    return (
        len(_parse_ints(args.lookbacks))
        * len(_parse_ints(args.top_ks))
        * len(_parse_market_filters(None, args.market_filters))
        * len(_parse_ints(args.allow_negative_momentum))
    )


def _apply_oos_and_family_gate_context(summary: pd.DataFrame, windows: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    oos_rows = []
    for candidate, group in windows.groupby("candidate"):
        total = int(len(group))
        positive = int((group["cagr"] > 0).sum())
        beat_spy = int((group["cagr"] > group["spy_cagr"]).sum())
        oos_rows.append({
            "candidate": candidate,
            "oos_windows": total,
            "oos_positive_windows": positive,
            "oos_positive_ratio": positive / total if total else float("nan"),
            "oos_beat_spy_windows": beat_spy,
            "oos_beat_spy_ratio": beat_spy / total if total else float("nan"),
            "oos_pass": bool(total >= 8 and positive >= 6),
        })
    summary = summary.merge(pd.DataFrame(oos_rows), on="candidate", how="left")
    sp500_pbo = summary.loc[summary["candidate"] == "dynamic_wf_sp500", ["pbo_family", "pbo_family_pass", "pbo_family_n_combinations"]]
    if not sp500_pbo.empty:
        values = sp500_pbo.iloc[0].to_dict()
        fixed_mask = summary["candidate"].isin(["fixed_aggressive_sp500", "fixed_balanced_sp500"])
        for key, value in values.items():
            summary.loc[fixed_mask, key] = value
    return summary


def _write_candidate_series_and_plots(out_dir: Path, candidate_name: str, aligned: pd.DataFrame) -> None:
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(out_dir / "aligned_strategy_spy.csv")
    _plot_performance(aligned, plots_dir / "performance_vs_spy.png", candidate_name)
    _plot_rolling_windows(aligned, plots_dir / "rolling_windows_1_3_5_10y.png", candidate_name)


def _write_combined_plots(out_dir: Path, summary: pd.DataFrame) -> None:
    combined = _load_combined_candidate_series(summary)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    _plot_combined_performance(combined, plots_dir / "combined_performance_vs_spy.png")
    _plot_combined_relative(combined, plots_dir / "combined_equity_over_spy.png")
    _plot_combined_rolling_windows(combined, plots_dir / "combined_rolling_windows_1_3_5_10y.png")


def _load_combined_candidate_series(summary: pd.DataFrame) -> pd.DataFrame:
    frames = []
    spy_parts = []
    for row in summary.itertuples(index=False):
        path = Path(row.output_dir) / "aligned_strategy_spy.csv"
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        frames.append((df["strategy_equity"] / float(df["strategy_equity"].iloc[0])).rename(row.candidate))
        spy_parts.append(df["spy_equity"].rename(row.candidate))
    spy = pd.concat(spy_parts, axis=1, sort=True).mean(axis=1).dropna()
    frames.append((spy / float(spy.iloc[0])).rename("SPY"))
    return pd.concat(frames, axis=1, sort=True)


def _plot_combined_performance(combined: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    for column in combined.columns:
        style = {"color": "black", "linestyle": "--", "linewidth": 1.5} if column == "SPY" else {"linewidth": 1.35}
        ax.plot(combined.index, combined[column], label=column, **style)
    ax.set_yscale("log")
    ax.set_title("Deploy candidates performance vs SPY")
    ax.set_ylabel("Normalized equity, log scale")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_combined_relative(combined: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    spy = combined["SPY"]
    for column in [c for c in combined.columns if c != "SPY"]:
        ratio = combined[column] / spy
        ax.plot(ratio.index, ratio, label=f"{column} / SPY", linewidth=1.35)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.0)
    ax.set_yscale("log")
    ax.set_title("Deploy candidates relative equity vs SPY")
    ax.set_ylabel("Candidate equity / SPY equity")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_combined_rolling_windows(combined: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=False)
    for ax, years in zip(axes.ravel(), (1, 3, 5, 10), strict=True):
        window = years * 252
        plotted = False
        for column in combined.columns:
            series = combined[column].dropna()
            if len(series) <= window:
                continue
            rolling = (series / series.shift(window)) ** (1.0 / years) - 1.0
            style = {"color": "black", "linestyle": "--", "linewidth": 1.4} if column == "SPY" else {"linewidth": 1.15}
            ax.plot(rolling.index, rolling * 100.0, label=column, **style)
            plotted = True
        if not plotted:
            ax.text(0.5, 0.5, f"Insufficient history for {years}y rolling window", ha="center", va="center")
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.45)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.3)
        if plotted:
            ax.legend(fontsize=7)
    fig.suptitle("Deploy candidates rolling CAGR vs SPY", y=0.995)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_performance(aligned: pd.DataFrame, out_path: Path, candidate_name: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.plot(aligned.index, aligned["strategy_equity"], label="Candidate", linewidth=1.5)
    ax.plot(aligned.index, aligned["spy_equity"], label="SPY buy & hold", color="black", linestyle="--", linewidth=1.4)
    ax.set_yscale("log")
    ax.set_title(f"Performance vs SPY - {candidate_name}")
    ax.set_ylabel("Equity ($, log scale)")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _plot_rolling_windows(aligned: pd.DataFrame, out_path: Path, candidate_name: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=False)
    for ax, years in zip(axes.ravel(), (1, 3, 5, 10), strict=True):
        window = years * 252
        if len(aligned) <= window:
            ax.text(0.5, 0.5, f"Insufficient data for {years}y", ha="center", va="center")
            ax.set_title(f"{years}y rolling CAGR")
            ax.grid(True, alpha=0.25)
            continue
        strat = (aligned["strategy_equity"] / aligned["strategy_equity"].shift(window)) ** (1.0 / years) - 1.0
        spy = (aligned["spy_equity"] / aligned["spy_equity"].shift(window)) ** (1.0 / years) - 1.0
        edge = strat - spy
        ax.plot(strat.index, strat * 100.0, label="Candidate", linewidth=1.2)
        ax.plot(spy.index, spy * 100.0, label="SPY", color="black", linestyle="--", linewidth=1.2)
        ax.fill_between(edge.index, 0, edge * 100.0, where=edge >= 0, color="#16a34a", alpha=0.18)
        ax.fill_between(edge.index, 0, edge * 100.0, where=edge < 0, color="#d62728", alpha=0.16)
        ax.axhline(0.0, color="black", linewidth=0.7, alpha=0.5)
        ax.set_title(f"{years}y rolling CAGR")
        ax.set_ylabel("CAGR (%)")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle(f"Rolling window CAGR vs SPY - {candidate_name}", y=0.995)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _subperiod_rows(
    candidate: Candidate,
    strategy_returns: pd.Series,
    spy_returns: pd.Series,
) -> list[dict[str, object]]:
    rows = []
    for name, (lo, hi) in SUBPERIODS.items():
        strat = strategy_returns.loc[lo:hi]
        bench = spy_returns.loc[strat.index]
        if len(strat) < 20:
            continue
        strat_eq = (1.0 + strat).cumprod() * 10_000.0
        spy_eq = (1.0 + bench).cumprod() * 10_000.0
        sm = compute_report_metrics(strat_eq, strat)
        bm = compute_report_metrics(spy_eq, bench)
        rows.append({
            "candidate": candidate.name,
            "subperiod": name,
            "cagr": sm["cagr"],
            "mdd": sm["mdd"],
            "sharpe": sm["sharpe"],
            "spy_cagr": bm["cagr"],
            "spy_mdd": bm["mdd"],
            "spy_sharpe": bm["sharpe"],
        })
    return rows


def _fixed_window_rows(
    candidate: Candidate,
    strategy_returns: pd.Series,
    spy_returns: pd.Series,
    windows: list[dict[str, pd.Timestamp]],
) -> list[dict[str, object]]:
    rows = []
    for window in windows:
        test = strategy_returns.loc[window["test_start"]:window["test_end"]]
        bench = spy_returns.loc[test.index]
        rows.append(_window_row(candidate, window, test, bench, selected_config=config_slug(candidate.config)))
    return rows


def _dynamic_window_rows(
    candidate: Candidate,
    selections: list[dict],
    spy_returns: pd.Series,
) -> list[dict[str, object]]:
    rows = []
    for selection in selections:
        window = {key: pd.Timestamp(selection[key]) for key in ("train_start", "train_end", "test_start", "test_end")}
        bench = spy_returns.loc[window["test_start"]:window["test_end"]]
        bench_metrics = _period_metrics(bench)
        rows.append({
            "candidate": candidate.name,
            "train_start": selection["train_start"],
            "train_end": selection["train_end"],
            "test_start": selection["test_start"],
            "test_end": selection["test_end"],
            "selected_config": selection["selected_config"],
            "cagr": selection["test_cagr"],
            "mdd": selection["test_mdd"],
            "sharpe": selection["test_sharpe"],
            "spy_cagr": bench_metrics["cagr"],
            "spy_mdd": bench_metrics["mdd"],
            "spy_sharpe": bench_metrics["sharpe"],
        })
    return rows


def _window_row(
    candidate: Candidate,
    window: dict[str, pd.Timestamp],
    strategy_returns: pd.Series,
    spy_returns: pd.Series,
    selected_config: str,
) -> dict[str, object]:
    sm = _period_metrics(strategy_returns)
    bm = _period_metrics(spy_returns)
    return {
        "candidate": candidate.name,
        "train_start": str(window["train_start"].date()),
        "train_end": str(window["train_end"].date()),
        "test_start": str(window["test_start"].date()),
        "test_end": str(window["test_end"].date()),
        "selected_config": selected_config,
        "cagr": sm["cagr"],
        "mdd": sm["mdd"],
        "sharpe": sm["sharpe"],
        "spy_cagr": bm["cagr"],
        "spy_mdd": bm["mdd"],
        "spy_sharpe": bm["sharpe"],
    }


def _period_metrics(returns: pd.Series) -> dict[str, float]:
    returns = returns.dropna()
    if len(returns) < 20:
        return {"cagr": float("nan"), "mdd": float("nan"), "sharpe": float("nan")}
    equity = (1.0 + returns).cumprod() * 10_000.0
    metrics = compute_report_metrics(equity, returns)
    return {"cagr": metrics["cagr"], "mdd": metrics["mdd"], "sharpe": metrics["sharpe"]}


def _splice_weights(weights_by_config: dict[str, pd.DataFrame], selections: list[dict]) -> pd.DataFrame:
    parts = []
    for selection in selections:
        selected = selection["selected_config"]
        weights = weights_by_config[selected].loc[selection["test_start"]:selection["test_end"]]
        parts.append(weights)
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts).sort_index()
    return out[~out.index.duplicated(keep="first")]


def _annualized_turnover(weights: pd.DataFrame) -> float:
    if weights.empty or len(weights) < 2:
        return float("nan")
    turnover = _daily_turnover(weights)
    return float(turnover.mean() * 252.0)


def _daily_turnover(weights: pd.DataFrame) -> pd.Series:
    if weights.empty:
        return pd.Series(dtype=float)
    return (weights.diff().abs().sum(axis=1) / 2.0).fillna(weights.iloc[0].abs().sum())


def _weights_dict(row: pd.Series) -> dict[str, float]:
    active = row[row.abs() > 1e-12]
    return {str(key): float(value) for key, value in active.items()}


def _parse_float_list(raw: str) -> list[float]:
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def _bps_suffix(value: float) -> str:
    return f"{int(value)}bps" if float(value).is_integer() else f"{value:g}bps".replace(".", "p")


def _align(
    strategy_equity: pd.Series,
    strategy_returns: pd.Series,
    spy_equity: pd.Series,
    spy_returns: pd.Series,
) -> pd.DataFrame:
    return pd.concat(
        {
            "strategy_equity": strategy_equity,
            "strategy_return": strategy_returns,
            "spy_equity": spy_equity,
            "spy_return": spy_returns,
        },
        axis=1,
        sort=True,
    ).dropna()


def _load_only_sp500(candidate: Candidate, args: argparse.Namespace) -> bool:
    if (
        args.sp500_pit
        and args.pit_load_all_stocks
        and candidate.variation == "stocks"
        and candidate.only_sp500
    ):
        return False
    return candidate.only_sp500


def _universe_label(candidate: Candidate, args: argparse.Namespace | None = None) -> str:
    if candidate.variation != "stocks":
        return "all_etfs"
    if args is not None and args.sp500_pit and args.pit_load_all_stocks and candidate.only_sp500:
        return "sp500_pit_expanded_cache"
    return "sp500" if candidate.only_sp500 else "all_stocks"


def _universe_provider_for(
    candidate: Candidate,
    args: argparse.Namespace,
    prices: pd.DataFrame,
) -> Callable[[pd.Timestamp], set[str]] | None:
    providers: list[Callable[[pd.Timestamp], set[str]]] = []
    if args.sp500_pit and candidate.variation == "stocks" and candidate.only_sp500:
        providers.append(sp500_pit_universe_provider())
    tradability = _tradability_provider(prices, args)
    if tradability is not None:
        providers.append(tradability)
    if not providers:
        return None

    def provider(ts: pd.Timestamp) -> set[str]:
        allowed = providers[0](ts)
        for item in providers[1:]:
            allowed = allowed & item(ts)
        return allowed

    return provider


def _tradability_provider(
    prices: pd.DataFrame,
    args: argparse.Namespace,
) -> Callable[[pd.Timestamp], set[str]] | None:
    """Point-in-time liquidity/age/price ranking universe filter.

    This avoids the look-ahead risk of filtering symbols by full-sample median
    liquidity before a walk-forward run. ADV20 uses only data up to the signal
    date, and age is cumulative observed bars `[stocks_on_the_move, p.81]`.
    """
    if args.pit_min_age_bars <= 0 and args.pit_min_adv20 <= 0 and args.pit_min_price <= 0:
        return None
    age = prices.notna().cumsum()
    adv20 = None
    if args.pit_min_adv20 > 0:
        dollar_volume = _load_dollar_volume(list(prices.columns), args.storage_root).reindex(prices.index)
        adv20 = dollar_volume.rolling(20, min_periods=5).mean()

    def provider(ts: pd.Timestamp) -> set[str]:
        day = pd.Timestamp(ts)
        if day not in prices.index:
            loc = prices.index.searchsorted(day, side="right") - 1
            if loc < 0:
                return set()
            day = pd.Timestamp(prices.index[loc])
        mask = prices.loc[day].notna()
        if args.pit_min_age_bars > 0:
            mask &= age.loc[day] >= args.pit_min_age_bars
        if args.pit_min_price > 0:
            mask &= prices.loc[day] >= args.pit_min_price
        if adv20 is not None:
            mask &= adv20.loc[day].fillna(0.0) >= args.pit_min_adv20
        return {str(symbol) for symbol in prices.columns[mask.to_numpy()]}

    return provider


def _write_report(
    out_path: Path,
    summary: pd.DataFrame,
    subperiods: pd.DataFrame,
    windows: pd.DataFrame,
    args: argparse.Namespace,
) -> None:
    show_cols = [
        "candidate", "kind", "universe", "cagr", "mdd", "sharpe", "sortino",
        "avg_exposure", "avg_positions_when_invested", "annualized_turnover_proxy",
        "cost10bps_cagr", "cost25bps_cagr", "cost50bps_cagr", "cost10bps_tax_cagr",
        "unique_held_symbols", "median_held_adv20", "pct_held_obs_adv20_lt_5m",
        "pbo_family", "pbo_family_pass", "dsr_p_value", "dsr_pass",
        "oos_positive_windows", "oos_windows", "oos_pass",
        "bootstrap_cagr_ci_low_0p1pct", "bootstrap_pass",
        "roll_1y_pct_beat_spy", "roll_3y_pct_beat_spy", "roll_5y_pct_beat_spy",
        "roll_10y_pct_beat_spy", "spy_cagr", "spy_mdd", "spy_sharpe",
    ]
    lines = [
        "# Weekly Momentum Candidate Validation Report",
        "",
        "## Setup",
        "",
        f"- Candidates: `{args.candidates}`.",
        f"- sp500_pit: `{args.sp500_pit}`; pit_load_all_stocks: `{args.pit_load_all_stocks}`.",
        f"- Dynamic grid: lookbacks `{args.lookbacks}`, top_k `{args.top_ks}`, market filters `{args.market_filters}`, allow_negative `{args.allow_negative_momentum}`.",
        f"- Cost stress: one-way turnover cost bps `{args.cost_bps}`; annual DARF tax stress after `{args.tax_cost_bps:g}` bps costs.",
        f"- Liquidity diagnostics use held-name 20d average dollar volume and reference AUM `${args.liquidity_aum:,.0f}` `[stocks_on_the_move, p.81]`.",
        f"- Point-in-time tradability filters: min_age_bars `{args.pit_min_age_bars}`, min_adv20 `${args.pit_min_adv20:,.0f}`, min_price `${args.pit_min_price:g}`.",
        f"- Walk-forward windows: `{args.train_years}`y train -> `{args.test_years}`y test `[advances_fin_ml, p.208-211]`.",
        "- Momentum premise: cross-sectional ranking `[stocks_on_the_move, p.60]`; SPY trend-risk filter `[stocks_on_the_move, p.66-67, p.81]`.",
        "",
        "## Candidate Comparison",
        "",
        summary[show_cols].to_markdown(index=False),
        "",
        "## Plots",
        "",
        "### Combined Candidates",
        "",
        "![Combined performance vs SPY](plots/combined_performance_vs_spy.png)",
        "",
        "![Combined equity over SPY](plots/combined_equity_over_spy.png)",
        "",
        "![Combined rolling windows 1/3/5/10y](plots/combined_rolling_windows_1_3_5_10y.png)",
        "",
        "Note: the dynamic walk-forward candidates start only after the initial train window and end at the last complete OOS block, so the combined 10y rolling panel can be unavailable until the common history is long enough.",
        "",
    ]
    for row in summary.sort_values("candidate").itertuples(index=False):
        rel_dir = Path(row.output_dir).name
        lines.extend([
            f"### `{row.candidate}`",
            "",
            f"![Performance vs SPY]({rel_dir}/plots/performance_vs_spy.png)",
            "",
            f"![Rolling Windows 1/3/5/10y]({rel_dir}/plots/rolling_windows_1_3_5_10y.png)",
            "",
        ])

    lines.extend([
        "## Subperiods",
        "",
        subperiods.to_markdown(index=False),
        "",
        "## Walk-Forward / OOS Windows",
        "",
        windows.to_markdown(index=False),
        "",
        "## Caveats",
        "",
        "- These candidates are frozen for validation, not approved for deploy.",
        "- Current S&P 500 and full-cache universes are not point-in-time.",
        "- Dynamic candidates splice returns from selected configs and are a research proxy until transition costs/state are modeled explicitly.",
        "- Costs/slippage and DARF are stress proxies, not broker-grade execution or tax accounting.",
        "- PBO is a family/grid gate; fixed candidates inherit the S&P 500 family PBO context rather than having a standalone PBO.",
        "- Point-in-time universe, delisting handling and deeper bootstrap variants remain pending `[advances_fin_ml, p.196-202]`.",
        "",
    ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
