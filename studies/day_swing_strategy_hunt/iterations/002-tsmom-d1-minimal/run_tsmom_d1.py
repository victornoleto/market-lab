"""Iteration 002: minimal D1 time-series momentum.

Research-only; no paper/live trading. The pre-registration in PRE_REG.md was
created before running this script.

Citations:
- Time-series momentum/trend following rule: [systematic_trading, ch.10].
- D1 horizon and transaction-cost stress: [systematic_trading, p.182-197].
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


ITERATION = "002-tsmom-d1-minimal"
ROOT = Path(__file__).resolve().parent
ITER001_RESULTS = ROOT.parent / "001-tsmom-data-audit" / "RESULTS.json"
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
OOS_START = pd.Timestamp("2024-01-01", tz="UTC")
SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "USDCHF",
    "USDCAD",
    "AUDUSD",
    "NZDUSD",
    "XAUUSD",
    "BTCUSD",
    "ETHUSD",
]
LOOKBACKS = [20, 60, 120]
PERIODS_PER_YEAR = 252
RNG_SEED = 20260503
N_BOOTSTRAP = 2000
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


def asset_class(symbol: str) -> str:
    if symbol == "XAUUSD":
        return "XAU"
    if symbol in {"BTCUSD", "ETHUSD"}:
        return "CRYPTO"
    return "FX"


def scenario_cost(symbol: str, scenario: str) -> float:
    return COST_BPS[asset_class(symbol)][scenario] / 10_000.0


def fetch_dukascopy(symbol: str) -> pd.DataFrame:
    df = dk.fetch(DUKAS_PAIR_MAP[symbol], dk.INTERVAL_DAY_1, dk.OFFER_SIDE_BID, START, END)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


def summarize_returns(ret: pd.Series) -> dict[str, float | int | None]:
    ret = ret.dropna()
    if ret.empty:
        return {"bars": 0, "cagr": None, "sharpe": None, "max_drawdown": None, "total_return": None}
    equity = (1.0 + ret).cumprod()
    years = len(ret) / PERIODS_PER_YEAR
    vol = float(ret.std(ddof=1))
    sharpe = float(ret.mean() / vol * np.sqrt(PERIODS_PER_YEAR)) if vol > 0 else None
    dd = equity / equity.cummax() - 1.0
    return {
        "bars": int(len(ret)),
        "cagr": float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else None,
        "sharpe": sharpe,
        "max_drawdown": float(dd.min()),
        "total_return": float(equity.iloc[-1] - 1.0),
    }


def position_returns(close: pd.Series, position: pd.Series, cost: float) -> SeriesResult:
    raw = close.pct_change().fillna(0.0)
    pos = position.reindex(close.index).fillna(0.0).astype(float)
    pos_prev = pos.shift(1).fillna(0.0)
    turnover = (pos - pos_prev).abs()
    ret = pos_prev * raw - turnover * cost
    entries = int(((pos > 0) & (pos_prev == 0)).sum())
    return SeriesResult(returns=ret, turnover=float(turnover.sum()), entries=entries)


def tsmom_position(close: pd.Series, lookback: int) -> pd.Series:
    signal = close.pct_change(lookback) > 0.0
    return signal.astype(float).fillna(0.0)


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


def pbo_from_folds(portfolio_returns: dict[int, pd.Series]) -> dict[str, float | int | list[dict[str, float | int]] | None]:
    combined = pd.concat(portfolio_returns, axis=1).dropna().sort_index()
    if len(combined) < 8:
        return {"pbo": None, "splits": 0, "reason": "insufficient_aligned_rows"}
    folds = np.array_split(np.arange(len(combined)), 8)
    split_rows: list[dict[str, float | int]] = []
    below_median = 0
    total = 0
    for train_fold_ids in combinations(range(8), 4):
        train_idx = np.concatenate([folds[i] for i in train_fold_ids])
        test_idx = np.concatenate([folds[i] for i in range(8) if i not in train_fold_ids])
        train_scores = {lb: sharpe(combined.iloc[train_idx][lb]) for lb in LOOKBACKS}
        test_scores = {lb: sharpe(combined.iloc[test_idx][lb]) for lb in LOOKBACKS}
        selected = max(LOOKBACKS, key=lambda lb: train_scores[lb])
        sorted_test = sorted(LOOKBACKS, key=lambda lb: test_scores[lb])
        rank = sorted_test.index(selected) + 1
        rank_pct = rank / len(LOOKBACKS)
        if rank_pct <= 0.5:
            below_median += 1
        total += 1
        split_rows.append(
            {
                "selected_lookback": selected,
                "train_sharpe": train_scores[selected],
                "test_sharpe": test_scores[selected],
                "test_rank_pct": rank_pct,
            }
        )
    return {"pbo": below_median / total if total else None, "splits": total, "details": split_rows}


def sharpe(ret: pd.Series) -> float:
    ret = ret.dropna()
    vol = float(ret.std(ddof=1))
    if ret.empty or vol <= 0:
        return float("-inf")
    return float(ret.mean() / vol * np.sqrt(PERIODS_PER_YEAR))


def pass_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def load_iter001_d1_baselines() -> dict[str, object]:
    raw = json.loads(ITER001_RESULTS.read_text(encoding="utf-8"))
    return raw["baselines"]["D1"]


def class_superiority(asset_results: dict[str, object], baselines: dict[str, object], lookback: int) -> dict[str, object]:
    classes = {"FX": [], "XAU": [], "CRYPTO": []}
    for symbol in SYMBOLS:
        strat_sharpe = asset_results[symbol]["base"][str(lookback)]["sharpe"]
        random_sharpe = baselines["assets"][symbol]["base"]["random_entry_matched_turnover_mean"]["sharpe"]
        classes[asset_class(symbol)].append(strat_sharpe is not None and random_sharpe is not None and strat_sharpe > random_sharpe)
    passed_classes = [name for name, values in classes.items() if any(values)]
    return {"passed_classes": passed_classes, "n_passed_classes": len(passed_classes), "required": 2}


def run() -> None:
    baselines = load_iter001_d1_baselines()
    close_by_symbol: dict[str, pd.Series] = {}
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
        close = df["close"].dropna()
        close_by_symbol[symbol] = close
        audit_rows.append(
            {
                "symbol": symbol,
                "status": "ok",
                "bars": int(len(close)),
                "start": str(close.index.min()),
                "end": str(close.index.max()),
            }
        )

    pd.DataFrame(audit_rows).to_csv(ROOT / "DATA_AUDIT_D1.csv", index=False)

    asset_results: dict[str, object] = {symbol: {scenario: {} for scenario in COST_BPS[asset_class(symbol)]} for symbol in close_by_symbol}
    portfolio_returns: dict[str, dict[int, dict[str, pd.Series]]] = {
        scenario: {lb: {} for lb in LOOKBACKS} for scenario in ["base", "conservative", "stress"]
    }

    for symbol, close in close_by_symbol.items():
        for lookback in LOOKBACKS:
            position = tsmom_position(close, lookback)
            for scenario in ["base", "conservative", "stress"]:
                result = position_returns(close, position, scenario_cost(symbol, scenario))
                asset_results[symbol][scenario][str(lookback)] = summarize_returns(result.returns) | {
                    "turnover": result.turnover,
                    "entries": result.entries,
                }
                portfolio_returns[scenario][lookback][symbol] = result.returns

    portfolio_results: dict[str, object] = {scenario: {} for scenario in ["base", "conservative", "stress"]}
    portfolio_series: dict[str, dict[int, pd.Series]] = {scenario: {} for scenario in ["base", "conservative", "stress"]}
    for scenario in ["base", "conservative", "stress"]:
        for lookback in LOOKBACKS:
            ret = portfolio_average(portfolio_returns[scenario][lookback])
            portfolio_series[scenario][lookback] = ret
            full = summarize_returns(ret)
            ins = summarize_returns(ret[ret.index < OOS_START])
            oos = summarize_returns(ret[ret.index >= OOS_START])
            portfolio_results[scenario][str(lookback)] = {
                "full": full,
                "in_sample_pre_2024": ins,
                "oos_2024_plus": oos,
                "bootstrap_full": bootstrap_annualized_mean_ci_low(ret, RNG_SEED + lookback),
                "bootstrap_oos": bootstrap_annualized_mean_ci_low(ret[ret.index >= OOS_START], RNG_SEED + 10_000 + lookback),
            }

    best_lookback = max(LOOKBACKS, key=lambda lb: portfolio_results["base"][str(lb)]["full"]["sharpe"] or float("-inf"))
    best_base = portfolio_results["base"][str(best_lookback)]["full"]
    best_stress = portfolio_results["stress"][str(best_lookback)]["full"]
    best_oos = portfolio_results["base"][str(best_lookback)]["oos_2024_plus"]
    best_boot_full = portfolio_results["base"][str(best_lookback)]["bootstrap_full"]
    best_boot_oos = portfolio_results["base"][str(best_lookback)]["bootstrap_oos"]
    bh = baselines["portfolio"]["base"]["buy_and_hold_equal_weight"]
    rnd = baselines["portfolio"]["base"]["random_entry_matched_turnover_equal_weight_mean"]
    superiority = class_superiority(asset_results, baselines, best_lookback)
    pbo = pbo_from_folds({lb: portfolio_series["base"][lb] for lb in LOOKBACKS})

    gates = {
        "K1_data_available": pass_bool(len(close_by_symbol) == len(SYMBOLS)),
        "cost_stress_positive": pass_bool((best_stress["cagr"] or 0.0) > 0 and (best_stress["sharpe"] or 0.0) > 0),
        "oos_single_block_positive": pass_bool((best_oos["cagr"] or 0.0) > 0 and (best_oos["sharpe"] or 0.0) > 0),
        "bootstrap_full_ci_low_gt_0": pass_bool((best_boot_full["ci_low"] or -1.0) > 0),
        "bootstrap_oos_ci_low_gt_0": pass_bool((best_boot_oos["ci_low"] or -1.0) > 0),
        "pbo_lt_0_5": pass_bool(pbo.get("pbo") is not None and float(pbo["pbo"]) < 0.5),
        "beats_buy_and_hold_ew_sharpe_base": pass_bool((best_base["sharpe"] or -999.0) > (bh["sharpe"] or -999.0)),
        "beats_random_entry_ew_sharpe_base": pass_bool((best_base["sharpe"] or -999.0) > (rnd["sharpe"] or -999.0)),
        "beats_random_entry_in_at_least_2_asset_classes": pass_bool(superiority["n_passed_classes"] >= 2),
        "no_single_asset_winner_declared": "PASS",
    }

    kill_switches = []
    if gates["K1_data_available"] == "FAIL":
        kill_switches.append("K1_PARTIAL_DATA")
    if gates["beats_random_entry_ew_sharpe_base"] == "FAIL":
        kill_switches.append("K2_RANDOM_ENTRY_PORTFOLIO_DOMINATES")
    if gates["pbo_lt_0_5"] == "FAIL":
        kill_switches.append("K3_PBO_GE_0_5")
    if gates["bootstrap_oos_ci_low_gt_0"] == "FAIL":
        kill_switches.append("K4_OOS_BOOTSTRAP_LOW_LE_0")
    if gates["cost_stress_positive"] == "FAIL":
        kill_switches.append("K5_COST_STRESS_ELIMINATES_EDGE")
    if gates["beats_random_entry_in_at_least_2_asset_classes"] == "FAIL":
        kill_switches.append("K6_MULTI_CLASS_CONFIRMATION_FAIL")

    status = "positive" if all(value == "PASS" for value in gates.values()) else "negative"
    if "K3_PBO_GE_0_5" in kill_switches or "K2_RANDOM_ENTRY_PORTFOLIO_DOMINATES" in kill_switches:
        status = "dead-end"
    if gates["K1_data_available"] == "FAIL":
        status = "inconclusive"

    results = {
        "iteration": ITERATION,
        "status": status,
        "hypothesis": "TSMOM D1 long/flat lookbacks 20/60/120",
        "pre_registered": True,
        "universe": SYMBOLS,
        "frequencies": ["D1"],
        "cost_scenarios": COST_BPS,
        "baselines": {
            "source": "../001-tsmom-data-audit/RESULTS.json baselines.D1",
            "portfolio_base": baselines["portfolio"]["base"],
        },
        "strategy_results": {
            "selected_lookback_by_base_portfolio_sharpe": best_lookback,
            "portfolio": portfolio_results,
            "assets": asset_results,
            "asset_class_random_entry_superiority": superiority,
        },
        "gates": gates,
        "pbo": pbo,
        "kill_switches": kill_switches,
        "n_trials": len(LOOKBACKS),
        "artifacts": ["PRE_REG.md", "run_tsmom_d1.py", "DATA_AUDIT_D1.csv", "RESULTS.json", "SUMMARY.md"],
        "notes": "Research-only. No winner declared; single-asset results are diagnostic only.",
    }
    (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    run()
