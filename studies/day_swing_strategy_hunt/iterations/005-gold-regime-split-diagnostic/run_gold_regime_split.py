"""Iteration 005: XAUUSD-only Gold Regime Trend/MR Split diagnostic.

Research-only; no paper/live trading. PRE_REG.md was created before this test.

Citations:
- Regime split by trend and volatility: [trading_systems_methods, p.13-14].
- D1 horizon and transaction-cost stress: [systematic_trading, p.182-197].
- Random-entry and turnover controls: [evidence_based_ta, p.247-260].
- Bootstrap/OOS anti-overfit gates: [advances_fin_ml, p.31-34, p.196-211].
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import dukascopy_python as dk
import numpy as np
import pandas as pd


ITERATION = "005-gold-regime-split-diagnostic"
ROOT = Path(__file__).resolve().parent
ITER001_RESULTS = ROOT.parent / "001-tsmom-data-audit" / "RESULTS.json"
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
OOS_START = pd.Timestamp("2024-01-01", tz="UTC")
SYMBOL = "XAUUSD"
PERIODS_PER_YEAR = 252
RNG_SEED = 20260503
N_BOOTSTRAP = 2000
N_RANDOM_RUNS = 200
CI_Q = 0.001

COST_BPS = {"XAU": {"base": 5.0, "conservative": 10.0, "stress": 20.0}}


@dataclass(frozen=True)
class SeriesResult:
    returns: pd.Series
    turnover: float
    entries: int
    avg_hold_bars: float | None


def fetch_xauusd_d1() -> pd.DataFrame:
    df = dk.fetch("XAU/USD", dk.INTERVAL_DAY_1, dk.OFFER_SIDE_BID, START, END)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def scenario_cost(scenario: str) -> float:
    return COST_BPS["XAU"][scenario] / 10_000.0


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


def rolling_percentile(series: pd.Series, window: int) -> pd.Series:
    def pct_rank(values: np.ndarray) -> float:
        current = values[-1]
        history = values[:-1]
        history = history[np.isfinite(history)]
        if not np.isfinite(current) or len(history) == 0:
            return np.nan
        return float(100.0 * np.sum(history <= current) / len(history))

    return series.rolling(window + 1, min_periods=window + 1).apply(pct_rank, raw=True)


def gold_regime_position(df: pd.DataFrame) -> pd.Series:
    close = df["close"]
    sma100 = close.rolling(100).mean()
    ret100 = close.pct_change(100)
    atr14 = true_range(df).rolling(14).mean()
    atr_pct = rolling_percentile(atr14 / close, 252)
    sma20 = close.rolling(20).mean()

    trend_up = (close > sma100) & (ret100 > 0.0)
    trend_down = (close < sma100) & (ret100 < 0.0)
    trend_capable = atr_pct >= 60.0
    range_regime = atr_pct <= 40.0

    lower_band = sma20 - atr14
    upper_band = sma20 + atr14

    pos = pd.Series(0.0, index=df.index)
    pos.loc[trend_capable & trend_up] = 1.0
    pos.loc[trend_capable & trend_down] = -1.0
    pos.loc[range_regime & (close < lower_band)] = 1.0
    pos.loc[range_regime & (close > upper_band)] = -1.0
    return pos.fillna(0.0)


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
        values[candidate:end] = 1.0 if rng.random() >= 0.5 else -1.0
        occupied[candidate:end] = True
        starts += 1
        if starts >= entries:
            break
    return pd.Series(values, index=index)


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


def pass_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def load_iter001_xau_d1_baselines() -> dict[str, object]:
    raw = json.loads(ITER001_RESULTS.read_text(encoding="utf-8"))
    return raw["baselines"]["D1"]["assets"][SYMBOL]


def audit_frame(df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {"symbol": SYMBOL, "frequency": "D1", "status": "missing", "bars": 0, "start": None, "end": None}
    gaps = df.index.to_series().diff().dropna().dt.total_seconds() / 3600.0
    return {
        "symbol": SYMBOL,
        "frequency": "D1",
        "source": "Dukascopy BID via dukascopy-python",
        "status": "ok",
        "bars": int(len(df)),
        "start": str(df.index.min()),
        "end": str(df.index.max()),
        "duplicate_timestamps": int(df.index.duplicated().sum()),
        "missing_close": int(df["close"].isna().sum()) if "close" in df else None,
        "max_gap_hours": float(gaps.max()) if not gaps.empty else 0.0,
        "caveats": "BID-only OHLC; no broker-specific swap/commission history; weekend/holiday gaps expected.",
    }


def run() -> None:
    baselines = load_iter001_xau_d1_baselines()
    try:
        df = fetch_xauusd_d1()
        audit = audit_frame(df)
    except Exception as exc:  # noqa: BLE001 - provider failures are iteration evidence.
        df = pd.DataFrame()
        audit = {"symbol": SYMBOL, "frequency": "D1", "status": "error", "error": str(exc)}

    pd.DataFrame([audit]).to_csv(ROOT / "DATA_AUDIT_D1.csv", index=False)

    if df.empty or "close" not in df or len(df.dropna(subset=["close"])) < 400:
        results = {
            "iteration": ITERATION,
            "status": "inconclusive",
            "hypothesis": "XAUUSD D1 Gold Regime Trend/MR Split diagnostic",
            "pre_registered": True,
            "universe": [SYMBOL],
            "frequencies": ["D1"],
            "cost_scenarios": COST_BPS,
            "baselines": {"source": "../001-tsmom-data-audit/RESULTS.json baselines.D1.assets.XAUUSD", "xauusd": baselines},
            "strategy_results": {},
            "gates": {"K1_data_available": "FAIL"},
            "kill_switches": ["K1_XAUUSD_D1_UNAVAILABLE"],
            "n_trials": 1,
            "artifacts": ["PRE_REG.md", "run_gold_regime_split.py", "DATA_AUDIT_D1.csv", "RESULTS.json", "SUMMARY.md"],
            "notes": "Research-only. No winner declared; XAUUSD-only is diagnostic only.",
        }
        (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
        return

    df = df.dropna(subset=["close"]).copy()
    close = df["close"]
    position = gold_regime_position(df)

    strategy_results: dict[str, object] = {}
    returns_by_scenario: dict[str, pd.Series] = {}
    result_by_scenario: dict[str, SeriesResult] = {}
    for scenario in ["base", "conservative", "stress"]:
        result = position_returns(close, position, scenario_cost(scenario))
        result_by_scenario[scenario] = result
        returns_by_scenario[scenario] = result.returns
        strategy_results[scenario] = {
            "full": summarize_returns(result.returns),
            "in_sample_pre_2024": summarize_returns(result.returns[result.returns.index < OOS_START]),
            "oos_2024_plus": summarize_returns(result.returns[result.returns.index >= OOS_START]),
            "bootstrap_full": bootstrap_annualized_mean_ci_low(result.returns, RNG_SEED),
            "bootstrap_oos": bootstrap_annualized_mean_ci_low(result.returns[result.returns.index >= OOS_START], RNG_SEED + 10_000),
            "turnover": result.turnover,
            "entries": result.entries,
            "avg_hold_bars": result.avg_hold_bars,
        }

    base_result = result_by_scenario["base"]
    random_runs = []
    hold_bars = max(1, int(round(base_result.avg_hold_bars or 1.0)))
    for run_id in range(N_RANDOM_RUNS):
        rp = random_position(close.index, base_result.entries, hold_bars, RNG_SEED + run_id)
        random_runs.append(position_returns(close, rp, scenario_cost("base")).returns)
    random_mean = pd.concat(random_runs, axis=1).mean(axis=1, skipna=True).dropna()

    base_full = strategy_results["base"]["full"]
    stress_full = strategy_results["stress"]["full"]
    base_oos = strategy_results["base"]["oos_2024_plus"]
    boot_full = strategy_results["base"]["bootstrap_full"]
    boot_oos = strategy_results["base"]["bootstrap_oos"]
    bh = baselines["base"]["buy_and_hold"]
    uniform = baselines["base"]["uniform_frequency"]
    random_iter001 = baselines["base"]["random_entry_matched_turnover_mean"]
    random_matched = summarize_returns(random_mean) | {"runs": N_RANDOM_RUNS, "matched_entries": base_result.entries, "matched_hold_bars": hold_bars}

    gates = {
        "K1_data_available": pass_bool(audit.get("status") == "ok" and int(audit.get("bars", 0)) >= 400),
        "cost_stress_positive": pass_bool((stress_full["cagr"] or 0.0) > 0 and (stress_full["sharpe"] or 0.0) > 0),
        "oos_single_block_positive": pass_bool((base_oos["cagr"] or 0.0) > 0 and (base_oos["sharpe"] or 0.0) > 0),
        "bootstrap_full_ci_low_gt_0": pass_bool((boot_full["ci_low"] or -1.0) > 0),
        "bootstrap_oos_ci_low_gt_0": pass_bool((boot_oos["ci_low"] or -1.0) > 0),
        "pbo": "not_applicable_single_pre_registered_config",
        "beats_always_flat_xau_cagr_base": pass_bool((base_full["cagr"] or -999.0) > 0.0),
        "beats_buy_and_hold_xau_sharpe_base": pass_bool((base_full["sharpe"] or -999.0) > (bh["sharpe"] or -999.0)),
        "beats_iter001_uniform_frequency_xau_sharpe_base": pass_bool((base_full["sharpe"] or -999.0) > (uniform["sharpe"] or -999.0)),
        "beats_iter001_random_entry_xau_sharpe_base": pass_bool((base_full["sharpe"] or -999.0) > (random_iter001["sharpe"] or -999.0)),
        "beats_strategy_matched_random_entry_sharpe_base": pass_bool((base_full["sharpe"] or -999.0) > (random_matched["sharpe"] or -999.0)),
        "no_single_asset_winner_declared": "PASS",
    }

    kill_switches = ["K6_XAUUSD_ONLY_DIAGNOSTIC_NO_WINNER"]
    if gates["K1_data_available"] == "FAIL":
        kill_switches.append("K1_XAUUSD_D1_UNAVAILABLE")
    if gates["beats_strategy_matched_random_entry_sharpe_base"] == "FAIL":
        kill_switches.append("K2_RANDOM_ENTRY_MATCHED_TURNOVER_DOMINATES")
    if gates["bootstrap_oos_ci_low_gt_0"] == "FAIL":
        kill_switches.append("K4_OOS_BOOTSTRAP_LOW_LE_0")
    if gates["cost_stress_positive"] == "FAIL":
        kill_switches.append("K5_COST_STRESS_ELIMINATES_EDGE")

    pass_values = [value for key, value in gates.items() if key != "pbo"]
    status = "positive" if all(value == "PASS" for value in pass_values) else "negative"
    if any(kill in kill_switches for kill in ["K2_RANDOM_ENTRY_MATCHED_TURNOVER_DOMINATES", "K4_OOS_BOOTSTRAP_LOW_LE_0", "K5_COST_STRESS_ELIMINATES_EDGE"]):
        status = "dead-end"
    if gates["K1_data_available"] == "FAIL":
        status = "inconclusive"

    results = {
        "iteration": ITERATION,
        "status": status,
        "hypothesis": "XAUUSD D1 Gold Regime Trend/MR Split diagnostic",
        "pre_registered": True,
        "universe": [SYMBOL],
        "frequencies": ["D1"],
        "cost_scenarios": COST_BPS,
        "baselines": {
            "source": "../001-tsmom-data-audit/RESULTS.json baselines.D1.assets.XAUUSD",
            "xauusd": baselines,
            "strategy_matched_random_entry_mean": random_matched,
        },
        "strategy_results": {
            "single_config": "sma100_ret100_atr14_atr_pct252_60_40_sma20_1atr_bands",
            "by_cost_scenario": strategy_results,
            "position_diagnostics": {
                "long_bars": int((position > 0).sum()),
                "short_bars": int((position < 0).sum()),
                "flat_bars": int((position == 0).sum()),
                "entries_base": base_result.entries,
                "turnover_base": base_result.turnover,
                "avg_hold_bars_base": base_result.avg_hold_bars,
            },
        },
        "gates": gates,
        "pbo": {"status": "not_applicable", "reason": "single pre-registered configuration; no config selection"},
        "kill_switches": kill_switches,
        "n_trials": 1,
        "artifacts": ["PRE_REG.md", "run_gold_regime_split.py", "DATA_AUDIT_D1.csv", "RESULTS.json", "SUMMARY.md"],
        "notes": "Research-only. No winner declared; XAUUSD-only is diagnostic only and cannot justify paper/live.",
    }
    (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    run()
