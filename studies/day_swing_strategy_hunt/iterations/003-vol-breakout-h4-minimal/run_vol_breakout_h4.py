"""Iteration 003: minimal H4 volatility breakout.

Research-only; no paper/live trading. PRE_REG.md was created before this test.

Citations:
- Donchian breakout, ATR filter and opposite-channel exits:
  [trading_systems_methods, ch.14].
- H4 transaction-cost stress: [systematic_trading, p.182-197].
- Random-entry and turnover controls: [evidence_based_ta, p.247-260].
- Bootstrap/OOS and PBO gates: [advances_fin_ml, p.31-34, p.208-211].
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import dukascopy_python as dk
import numpy as np
import pandas as pd


ITERATION = "003-vol-breakout-h4-minimal"
ROOT = Path(__file__).resolve().parent
ITER001_RESULTS = ROOT.parent / "001-tsmom-data-audit" / "RESULTS.json"
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
OOS_START = pd.Timestamp("2024-01-01", tz="UTC")
SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD", "XAUUSD", "BTCUSD", "ETHUSD"]
CHANNELS = [20, 55]
ATR_PERCENTILES = [50, 70]
PERIODS_PER_YEAR = 252 * 6
RNG_SEED = 20260503
N_BOOTSTRAP = 2000
N_RANDOM_RUNS = 200
CI_Q = 0.001

COST_BPS = {
    "FX": {"base": 2.0, "conservative": 5.0, "stress": 10.0},
    "XAU": {"base": 5.0, "conservative": 10.0, "stress": 20.0},
    "CRYPTO": {"base": 10.0, "conservative": 25.0, "stress": 50.0},
}

DUKAS_PAIR_MAP = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "USDCHF": "USD/CHF",
    "USDCAD": "USD/CAD",
    "AUDUSD": "AUD/USD",
    "NZDUSD": "NZD/USD",
    "XAUUSD": "XAU/USD",
    "BTCUSD": "BTC/USD",
    "ETHUSD": "ETH/USD",
}


@dataclass(frozen=True)
class SeriesResult:
    returns: pd.Series
    turnover: float
    entries: int
    avg_hold_bars: float | None


def asset_class(symbol: str) -> str:
    if symbol == "XAUUSD":
        return "XAU"
    if symbol in {"BTCUSD", "ETHUSD"}:
        return "CRYPTO"
    return "FX"


def scenario_cost(symbol: str, scenario: str) -> float:
    return COST_BPS[asset_class(symbol)][scenario] / 10_000.0


def fetch_dukascopy(symbol: str) -> pd.DataFrame:
    df = dk.fetch(DUKAS_PAIR_MAP[symbol], dk.INTERVAL_HOUR_4, dk.OFFER_SIDE_BID, START, END)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    values = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return values.max(axis=1)


def expanding_percentile_filter(series: pd.Series, threshold: int) -> pd.Series:
    values = series.to_numpy(dtype=float)
    passed = np.zeros(len(values), dtype=bool)
    history: list[float] = []
    for idx, value in enumerate(values):
        if history and np.isfinite(value):
            percentile = 100.0 * sum(prev <= value for prev in history) / len(history)
            passed[idx] = percentile > threshold
        if np.isfinite(value):
            history.append(float(value))
    return pd.Series(passed, index=series.index)


def breakout_position(df: pd.DataFrame, channel: int, atr_percentile: int) -> pd.Series:
    upper = df["high"].shift(1).rolling(channel).max()
    lower = df["low"].shift(1).rolling(channel).min()
    atr = true_range(df).rolling(channel).mean()
    atr_ok = expanding_percentile_filter(atr.shift(1), atr_percentile)
    pos = np.zeros(len(df), dtype=float)
    state = 0.0
    close = df["close"].to_numpy(dtype=float)
    upper_values = upper.to_numpy(dtype=float)
    lower_values = lower.to_numpy(dtype=float)
    atr_values = atr_ok.to_numpy(dtype=bool)
    for idx in range(len(df)):
        if not np.isfinite(upper_values[idx]) or not np.isfinite(lower_values[idx]):
            pos[idx] = state
            continue
        breaks_up = close[idx] > upper_values[idx]
        breaks_down = close[idx] < lower_values[idx]
        if breaks_up:
            state = 1.0 if atr_values[idx] else 0.0
        elif breaks_down:
            state = -1.0 if atr_values[idx] else 0.0
        pos[idx] = state
    return pd.Series(pos, index=df.index)


def summarize_returns(ret: pd.Series) -> dict[str, float | int | None]:
    ret = ret.dropna()
    if ret.empty:
        return {"bars": 0, "cagr": None, "sharpe": None, "max_drawdown": None, "total_return": None}
    equity = (1.0 + ret).cumprod()
    years = len(ret) / PERIODS_PER_YEAR
    vol = float(ret.std(ddof=1))
    sharpe_value = float(ret.mean() / vol * np.sqrt(PERIODS_PER_YEAR)) if vol > 0 else None
    dd = equity / equity.cummax() - 1.0
    return {
        "bars": int(len(ret)),
        "cagr": float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else None,
        "sharpe": sharpe_value,
        "max_drawdown": float(dd.min()),
        "total_return": float(equity.iloc[-1] - 1.0),
    }


def hold_stats(position: pd.Series) -> tuple[int, float | None]:
    pos = position.fillna(0.0).to_numpy(dtype=float)
    entries = 0
    lengths: list[int] = []
    current = 0
    in_trade = False
    prev = 0.0
    for value in pos:
        if value != 0.0:
            current = current + 1 if in_trade else 1
            if prev == 0.0:
                entries += 1
                in_trade = True
        elif in_trade:
            lengths.append(current)
            current = 0
            in_trade = False
        if value != 0.0 and prev != 0.0 and np.sign(value) != np.sign(prev):
            lengths.append(max(1, current - 1))
            entries += 1
            current = 1
        prev = value
    if in_trade:
        lengths.append(current)
    return entries, float(np.mean(lengths)) if lengths else None


def position_returns(close: pd.Series, position: pd.Series, cost: float) -> SeriesResult:
    raw = close.pct_change().fillna(0.0)
    pos = position.reindex(close.index).fillna(0.0).astype(float)
    pos_prev = pos.shift(1).fillna(0.0)
    turnover = (pos - pos_prev).abs()
    ret = pos_prev * raw - turnover * cost
    entries, avg_hold = hold_stats(pos)
    return SeriesResult(returns=ret, turnover=float(turnover.sum()), entries=entries, avg_hold_bars=avg_hold)


def random_position(index: pd.Index, entries: int, hold_bars: int, seed: int) -> pd.Series:
    values = np.zeros(len(index), dtype=float)
    if entries <= 0 or len(index) <= hold_bars:
        return pd.Series(values, index=index)
    rng = np.random.default_rng(seed)
    candidates = np.arange(0, max(1, len(index) - hold_bars))
    rng.shuffle(candidates)
    occupied = np.zeros(len(index), dtype=bool)
    starts = 0
    for candidate in candidates:
        end = min(candidate + hold_bars, len(index))
        if occupied[candidate:end].any():
            continue
        sign = 1.0 if rng.random() >= 0.5 else -1.0
        values[candidate:end] = sign
        occupied[candidate:end] = True
        starts += 1
        if starts >= entries:
            break
    return pd.Series(values, index=index)


def portfolio_average(series_by_symbol: dict[str, pd.Series]) -> pd.Series:
    frame = pd.concat(series_by_symbol, axis=1, sort=True).sort_index()
    return frame.mean(axis=1, skipna=True).dropna()


def bootstrap_annualized_mean_ci_low(ret: pd.Series, seed: int) -> dict[str, float | int | None]:
    values = ret.dropna().to_numpy(dtype=float)
    if len(values) == 0:
        return {"runs": N_BOOTSTRAP, "ci": 0.999, "annualized_mean": None, "ci_low": None}
    rng = np.random.default_rng(seed)
    means = np.empty(N_BOOTSTRAP)
    for idx in range(N_BOOTSTRAP):
        sample = rng.choice(values, size=len(values), replace=True)
        means[idx] = sample.mean() * PERIODS_PER_YEAR
    return {
        "runs": N_BOOTSTRAP,
        "ci": 0.999,
        "annualized_mean": float(values.mean() * PERIODS_PER_YEAR),
        "ci_low": float(np.quantile(means, CI_Q)),
    }


def sharpe(ret: pd.Series) -> float:
    ret = ret.dropna()
    vol = float(ret.std(ddof=1))
    if ret.empty or vol <= 0:
        return float("-inf")
    return float(ret.mean() / vol * np.sqrt(PERIODS_PER_YEAR))


def pbo_from_folds(portfolio_returns: dict[str, pd.Series]) -> dict[str, object]:
    combined = pd.concat(portfolio_returns, axis=1).dropna().sort_index()
    if len(combined) < 8:
        return {"pbo": None, "splits": 0, "reason": "insufficient_aligned_rows"}
    folds = np.array_split(np.arange(len(combined)), 8)
    details: list[dict[str, object]] = []
    below_median = 0
    total = 0
    configs = list(portfolio_returns)
    for train_fold_ids in combinations(range(8), 4):
        train_idx = np.concatenate([folds[i] for i in train_fold_ids])
        test_idx = np.concatenate([folds[i] for i in range(8) if i not in train_fold_ids])
        train_scores = {cfg: sharpe(combined.iloc[train_idx][cfg]) for cfg in configs}
        test_scores = {cfg: sharpe(combined.iloc[test_idx][cfg]) for cfg in configs}
        selected = max(configs, key=lambda cfg: train_scores[cfg])
        sorted_test = sorted(configs, key=lambda cfg: test_scores[cfg])
        rank_pct = (sorted_test.index(selected) + 1) / len(configs)
        if rank_pct <= 0.5:
            below_median += 1
        total += 1
        details.append({"selected_config": selected, "train_sharpe": train_scores[selected], "test_sharpe": test_scores[selected], "test_rank_pct": rank_pct})
    return {"pbo": below_median / total if total else None, "splits": total, "details": details}


def pass_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def load_iter001_h4_baselines() -> dict[str, object]:
    raw = json.loads(ITER001_RESULTS.read_text(encoding="utf-8"))
    return raw["baselines"]["H4"]


def class_superiority(asset_results: dict[str, object], baselines: dict[str, object], config: str) -> dict[str, object]:
    classes = {"FX": [], "XAU": [], "CRYPTO": []}
    for symbol in SYMBOLS:
        strat_sharpe = asset_results[symbol]["base"][config]["sharpe"]
        random_sharpe = baselines["assets"][symbol]["base"]["random_entry_matched_turnover_mean"]["sharpe"]
        classes[asset_class(symbol)].append(strat_sharpe is not None and random_sharpe is not None and strat_sharpe > random_sharpe)
    passed_classes = [name for name, values in classes.items() if any(values)]
    return {"passed_classes": passed_classes, "n_passed_classes": len(passed_classes), "required": 2}


def run() -> None:
    baselines = load_iter001_h4_baselines()
    frames: dict[str, pd.DataFrame] = {}
    audit_rows: list[dict[str, object]] = []
    for symbol in SYMBOLS:
        try:
            df = fetch_dukascopy(symbol)
        except Exception as exc:  # noqa: BLE001 - provider failures are iteration evidence.
            audit_rows.append({"symbol": symbol, "status": "error", "error": str(exc)})
            continue
        if df.empty or "close" not in df:
            audit_rows.append({"symbol": symbol, "status": "missing", "bars": 0})
            continue
        frames[symbol] = df.dropna(subset=["close"])
        audit_rows.append({"symbol": symbol, "status": "ok", "bars": int(len(df)), "start": str(df.index.min()), "end": str(df.index.max())})
    pd.DataFrame(audit_rows).to_csv(ROOT / "DATA_AUDIT_H4.csv", index=False)

    configs = [f"donchian{channel}_atrp{atrp}" for channel in CHANNELS for atrp in ATR_PERCENTILES]
    positions: dict[str, dict[str, pd.Series]] = {symbol: {} for symbol in frames}
    for symbol, df in frames.items():
        for channel in CHANNELS:
            for atrp in ATR_PERCENTILES:
                positions[symbol][f"donchian{channel}_atrp{atrp}"] = breakout_position(df, channel, atrp)

    asset_results: dict[str, object] = {symbol: {scenario: {} for scenario in ["base", "conservative", "stress"]} for symbol in frames}
    portfolio_returns: dict[str, dict[str, dict[str, pd.Series]]] = {scenario: {cfg: {} for cfg in configs} for scenario in ["base", "conservative", "stress"]}
    hold_by_config: dict[str, list[float]] = {cfg: [] for cfg in configs}

    for symbol, df in frames.items():
        close = df["close"].dropna()
        for cfg in configs:
            for scenario in ["base", "conservative", "stress"]:
                result = position_returns(close, positions[symbol][cfg], scenario_cost(symbol, scenario))
                asset_results[symbol][scenario][cfg] = summarize_returns(result.returns) | {
                    "turnover": result.turnover,
                    "entries": result.entries,
                    "avg_hold_bars": result.avg_hold_bars,
                }
                portfolio_returns[scenario][cfg][symbol] = result.returns
            avg_hold = asset_results[symbol]["base"][cfg]["avg_hold_bars"]
            if avg_hold is not None:
                hold_by_config[cfg].append(float(avg_hold))

    portfolio_results: dict[str, object] = {scenario: {} for scenario in ["base", "conservative", "stress"]}
    portfolio_series: dict[str, dict[str, pd.Series]] = {scenario: {} for scenario in ["base", "conservative", "stress"]}
    for scenario in ["base", "conservative", "stress"]:
        for cfg in configs:
            ret = portfolio_average(portfolio_returns[scenario][cfg])
            portfolio_series[scenario][cfg] = ret
            portfolio_results[scenario][cfg] = {
                "full": summarize_returns(ret),
                "in_sample_pre_2024": summarize_returns(ret[ret.index < OOS_START]),
                "oos_2024_plus": summarize_returns(ret[ret.index >= OOS_START]),
                "bootstrap_full": bootstrap_annualized_mean_ci_low(ret, RNG_SEED + len(cfg)),
                "bootstrap_oos": bootstrap_annualized_mean_ci_low(ret[ret.index >= OOS_START], RNG_SEED + 10_000 + len(cfg)),
            }

    best_config = max(configs, key=lambda cfg: portfolio_results["base"][cfg]["full"]["sharpe"] or float("-inf"))
    strategy_random_runs: list[pd.Series] = []
    for run_id in range(N_RANDOM_RUNS):
        run_series: dict[str, pd.Series] = {}
        for symbol, df in frames.items():
            entries = int(asset_results[symbol]["base"][best_config]["entries"])
            avg_hold = asset_results[symbol]["base"][best_config]["avg_hold_bars"] or 1.0
            rp = random_position(df.index, entries, max(1, int(round(float(avg_hold)))), RNG_SEED + run_id + len(symbol) * 1000)
            run_series[symbol] = position_returns(df["close"].dropna(), rp, scenario_cost(symbol, "base")).returns
        strategy_random_runs.append(portfolio_average(run_series))
    strategy_random_mean = pd.concat(strategy_random_runs, axis=1).mean(axis=1, skipna=True).dropna()

    pbo = pbo_from_folds(portfolio_series["base"])
    best_base = portfolio_results["base"][best_config]["full"]
    best_stress = portfolio_results["stress"][best_config]["full"]
    best_oos = portfolio_results["base"][best_config]["oos_2024_plus"]
    best_boot_full = portfolio_results["base"][best_config]["bootstrap_full"]
    best_boot_oos = portfolio_results["base"][best_config]["bootstrap_oos"]
    bh = baselines["portfolio"]["base"]["buy_and_hold_equal_weight"]
    rnd = baselines["portfolio"]["base"]["random_entry_matched_turnover_equal_weight_mean"]
    superiority = class_superiority(asset_results, baselines, best_config)
    single_asset_best = max(SYMBOLS, key=lambda symbol: asset_results[symbol]["base"][best_config]["sharpe"] or float("-inf"))

    gates = {
        "K1_data_available": pass_bool(len(frames) == len(SYMBOLS)),
        "cost_stress_positive": pass_bool((best_stress["cagr"] or 0.0) > 0 and (best_stress["sharpe"] or 0.0) > 0),
        "oos_single_block_positive": pass_bool((best_oos["cagr"] or 0.0) > 0 and (best_oos["sharpe"] or 0.0) > 0),
        "bootstrap_full_ci_low_gt_0": pass_bool((best_boot_full["ci_low"] or -1.0) > 0),
        "bootstrap_oos_ci_low_gt_0": pass_bool((best_boot_oos["ci_low"] or -1.0) > 0),
        "pbo_lt_0_5": pass_bool(pbo.get("pbo") is not None and float(pbo["pbo"]) < 0.5),
        "beats_buy_and_hold_ew_sharpe_base": pass_bool((best_base["sharpe"] or -999.0) > (bh["sharpe"] or -999.0)),
        "beats_iter001_random_entry_ew_sharpe_base": pass_bool((best_base["sharpe"] or -999.0) > (rnd["sharpe"] or -999.0)),
        "beats_strategy_matched_random_entry_sharpe_base": pass_bool((best_base["sharpe"] or -999.0) > (summarize_returns(strategy_random_mean)["sharpe"] or -999.0)),
        "beats_random_entry_in_at_least_2_asset_classes": pass_bool(superiority["n_passed_classes"] >= 2),
        "no_single_asset_winner_declared": "PASS",
        "dsr": "not_computed_minimal_scope_pbo_used_for_config_selection",
    }

    kill_switches = []
    if gates["K1_data_available"] == "FAIL":
        kill_switches.append("K1_PARTIAL_DATA")
    if gates["beats_iter001_random_entry_ew_sharpe_base"] == "FAIL" or gates["beats_strategy_matched_random_entry_sharpe_base"] == "FAIL":
        kill_switches.append("K2_RANDOM_ENTRY_PORTFOLIO_DOMINATES")
    if gates["pbo_lt_0_5"] == "FAIL":
        kill_switches.append("K3_PBO_GE_0_5")
    if gates["bootstrap_oos_ci_low_gt_0"] == "FAIL":
        kill_switches.append("K4_OOS_BOOTSTRAP_LOW_LE_0")
    if gates["cost_stress_positive"] == "FAIL":
        kill_switches.append("K5_COST_STRESS_ELIMINATES_EDGE")
    if gates["beats_random_entry_in_at_least_2_asset_classes"] == "FAIL":
        kill_switches.append("K6_MULTI_CLASS_CONFIRMATION_FAIL")

    status = "positive" if all(value == "PASS" for key, value in gates.items() if key != "dsr") else "negative"
    if any(kill in kill_switches for kill in ["K2_RANDOM_ENTRY_PORTFOLIO_DOMINATES", "K3_PBO_GE_0_5", "K4_OOS_BOOTSTRAP_LOW_LE_0", "K5_COST_STRESS_ELIMINATES_EDGE"]):
        status = "dead-end"
    if gates["K1_data_available"] == "FAIL":
        status = "inconclusive"

    results = {
        "iteration": ITERATION,
        "status": status,
        "hypothesis": "Volatility Breakout H4 Donchian 20/55 with ATR percentile 50/70",
        "pre_registered": True,
        "universe": SYMBOLS,
        "frequencies": ["H4"],
        "cost_scenarios": COST_BPS,
        "baselines": {"source": "../001-tsmom-data-audit/RESULTS.json baselines.H4", "portfolio_base": baselines["portfolio"]["base"]},
        "strategy_results": {
            "selected_config_by_base_portfolio_sharpe": best_config,
            "portfolio": portfolio_results,
            "assets": asset_results,
            "asset_class_random_entry_superiority": superiority,
            "single_asset_best_diagnostic": single_asset_best,
            "strategy_matched_random_entry_equal_weight_mean": summarize_returns(strategy_random_mean) | {"runs": N_RANDOM_RUNS},
            "avg_hold_bars_by_config": {cfg: float(np.mean(vals)) if vals else None for cfg, vals in hold_by_config.items()},
        },
        "gates": gates,
        "pbo": pbo,
        "kill_switches": kill_switches,
        "n_trials": len(configs),
        "artifacts": ["PRE_REG.md", "run_vol_breakout_h4.py", "DATA_AUDIT_H4.csv", "RESULTS.json", "SUMMARY.md"],
        "notes": "Research-only. No winner declared; single-asset results are diagnostic only. Specs backtest_phase2*.md referenced by CLAUDE.md were not present in this branch.",
    }
    (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    run()
