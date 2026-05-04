"""Iteration 001 data audit and minimal baselines.

Research-only. No strategy signal is tested here.

Citations:
- Trend-following candidate family deferred to later iterations:
  [systematic_trading, ch.10].
- D1/H4 horizons reduce short-horizon cost dominance:
  [systematic_trading, p.182-197].
- Random-entry controls test whether apparent results are just chance or turnover:
  [evidence_based_ta, p.247-260].
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import dukascopy_python as dk
import numpy as np
import pandas as pd


ITERATION = "001-tsmom-data-audit"
ROOT = Path(__file__).resolve().parent
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
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
FREQUENCIES = ["D1", "H4"]
RNG_SEED = 20260503
N_RANDOM_RUNS = 200
HOLD_BARS = 20

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


def fetch_dukascopy(symbol: str, freq: str) -> pd.DataFrame:
    interval = {"D1": dk.INTERVAL_DAY_1, "H4": dk.INTERVAL_HOUR_4}[freq]
    df = dk.fetch(DUKAS_PAIR_MAP[symbol], interval, dk.OFFER_SIDE_BID, START, END)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.index.name = "timestamp"
    return df


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


def summarize_returns(ret: pd.Series, periods_per_year: int) -> dict[str, float | int | None]:
    ret = ret.dropna()
    if ret.empty:
        return {"bars": 0, "cagr": None, "sharpe": None, "max_drawdown": None, "total_return": None}
    equity = (1.0 + ret).cumprod()
    years = len(ret) / periods_per_year
    total = float(equity.iloc[-1] - 1.0)
    cagr = float(equity.iloc[-1] ** (1.0 / years) - 1.0) if years > 0 else None
    vol = float(ret.std(ddof=1))
    sharpe = float(ret.mean() / vol * np.sqrt(periods_per_year)) if vol > 0 else None
    dd = equity / equity.cummax() - 1.0
    return {
        "bars": int(len(ret)),
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": float(dd.min()),
        "total_return": total,
    }


def position_returns(close: pd.Series, position: pd.Series, cost: float) -> SeriesResult:
    raw = close.pct_change().fillna(0.0)
    pos = position.reindex(close.index).fillna(0.0).astype(float)
    pos_prev = pos.shift(1).fillna(0.0)
    turnover = (pos - pos_prev).abs()
    ret = pos_prev * raw - turnover * cost
    entries = int(((pos > 0) & (pos_prev == 0)).sum())
    return SeriesResult(returns=ret, turnover=float(turnover.sum()), entries=entries)


def uniform_position(index: pd.Index) -> pd.Series:
    values = np.zeros(len(index), dtype=float)
    cycle = HOLD_BARS * 2
    for start in range(0, len(index), cycle):
        values[start : start + HOLD_BARS] = 1.0
    return pd.Series(values, index=index)


def random_position(index: pd.Index, entries: int, seed: int) -> pd.Series:
    values = np.zeros(len(index), dtype=float)
    if entries <= 0 or len(index) <= HOLD_BARS:
        return pd.Series(values, index=index)
    rng = np.random.default_rng(seed)
    candidates = np.arange(0, max(1, len(index) - HOLD_BARS))
    rng.shuffle(candidates)
    starts: list[int] = []
    occupied = np.zeros(len(index), dtype=bool)
    for candidate in candidates:
        end = min(candidate + HOLD_BARS, len(index))
        if occupied[candidate:end].any():
            continue
        starts.append(int(candidate))
        occupied[candidate:end] = True
        if len(starts) >= entries:
            break
    for start in starts:
        values[start : start + HOLD_BARS] = 1.0
    return pd.Series(values, index=index)


def audit_frame(symbol: str, freq: str, df: pd.DataFrame) -> dict[str, object]:
    if df.empty:
        return {
            "symbol": symbol,
            "frequency": freq,
            "source": "Dukascopy BID via dukascopy-python",
            "status": "missing",
            "bars": 0,
            "start": None,
            "end": None,
            "timezone": "UTC requested; timestamp index from provider",
            "columns": [],
            "duplicate_timestamps": 0,
            "missing_close": None,
            "max_gap_hours": None,
            "caveats": "No bars returned in fixed audit window.",
        }
    gaps = df.index.to_series().diff().dropna().dt.total_seconds() / 3600.0
    return {
        "symbol": symbol,
        "frequency": freq,
        "source": "Dukascopy BID via dukascopy-python",
        "status": "ok",
        "bars": int(len(df)),
        "start": str(df.index.min()),
        "end": str(df.index.max()),
        "timezone": "UTC requested; timestamp index from provider",
        "columns": list(df.columns),
        "duplicate_timestamps": int(df.index.duplicated().sum()),
        "missing_close": int(df["close"].isna().sum()),
        "max_gap_hours": float(gaps.max()) if not gaps.empty else 0.0,
        "caveats": "BID-only OHLC; no broker-specific swap/commission history; weekend/holiday gaps expected.",
    }


def portfolio_average(series_by_symbol: dict[str, pd.Series]) -> pd.Series:
    if not series_by_symbol:
        return pd.Series(dtype=float)
    frame = pd.concat(series_by_symbol, axis=1).sort_index()
    return frame.mean(axis=1, skipna=True).dropna()


def run() -> None:
    audit_rows: list[dict[str, object]] = []
    results: dict[str, object] = {
        "iteration": ITERATION,
        "status": "positive",
        "hypothesis": "TSMOM D1/H4 data audit plus minimal baselines",
        "pre_registered": True,
        "universe": SYMBOLS,
        "frequencies": FREQUENCIES,
        "cost_scenarios": COST_BPS,
        "baselines": {},
        "strategy_results": {},
        "gates": {},
        "kill_switches": [],
        "n_trials": 0,
        "artifacts": ["DATA_AUDIT.csv", "RESULTS.json", "SUMMARY.md"],
        "notes": "Research-only baselines; no strategy signal and no winner declaration.",
    }

    for freq in FREQUENCIES:
        periods = 252 if freq == "D1" else 252 * 6
        freq_results: dict[str, object] = {"assets": {}, "portfolio": {}}
        scenario_portfolios: dict[str, dict[str, pd.Series]] = {
            scenario: {"buy_and_hold": {}, "uniform_frequency": {}, "always_flat": {}}
            for scenario in ["base", "conservative", "stress"]
        }
        random_portfolios: dict[str, list[pd.Series]] = {scenario: [] for scenario in ["base", "conservative", "stress"]}

        for symbol in SYMBOLS:
            try:
                df = fetch_dukascopy(symbol, freq)
            except Exception as exc:  # noqa: BLE001 - audit should capture provider failures.
                audit_rows.append(
                    {
                        "symbol": symbol,
                        "frequency": freq,
                        "source": "Dukascopy BID via dukascopy-python",
                        "status": "error",
                        "bars": 0,
                        "start": None,
                        "end": None,
                        "timezone": "UTC requested",
                        "columns": [],
                        "duplicate_timestamps": None,
                        "missing_close": None,
                        "max_gap_hours": None,
                        "caveats": str(exc),
                    }
                )
                continue

            audit_rows.append(audit_frame(symbol, freq, df))
            if df.empty or "close" not in df:
                continue

            close = df["close"].dropna()
            if len(close) < HOLD_BARS * 4:
                continue

            asset_metrics: dict[str, object] = {}
            flat = pd.Series(0.0, index=close.index)
            uniform = uniform_position(close.index)
            uniform_entries = int(((uniform > 0) & (uniform.shift(1).fillna(0.0) == 0)).sum())

            for scenario in ["base", "conservative", "stress"]:
                cost = scenario_cost(symbol, scenario)
                bh = position_returns(close, pd.Series(1.0, index=close.index), cost)
                uf = position_returns(close, uniform, cost)
                fl = position_returns(close, flat, cost)
                random_runs = []
                for run_id in range(N_RANDOM_RUNS):
                    rp = random_position(close.index, uniform_entries, RNG_SEED + run_id + len(symbol) * 1000)
                    random_runs.append(position_returns(close, rp, cost).returns)
                random_summary = pd.DataFrame(random_runs).T.mean(axis=1)

                asset_metrics[scenario] = {
                    "buy_and_hold": summarize_returns(bh.returns, periods) | {"turnover": bh.turnover, "entries": bh.entries},
                    "always_flat": summarize_returns(fl.returns, periods) | {"turnover": fl.turnover, "entries": fl.entries},
                    "uniform_frequency": summarize_returns(uf.returns, periods) | {"turnover": uf.turnover, "entries": uf.entries},
                    "random_entry_matched_turnover_mean": summarize_returns(random_summary, periods)
                    | {"runs": N_RANDOM_RUNS, "matched_entries": uniform_entries},
                }

                scenario_portfolios[scenario]["buy_and_hold"][symbol] = bh.returns
                scenario_portfolios[scenario]["uniform_frequency"][symbol] = uf.returns
                scenario_portfolios[scenario]["always_flat"][symbol] = fl.returns
                random_portfolios[scenario].append(random_summary.rename(symbol))

            freq_results["assets"][symbol] = asset_metrics

        for scenario in ["base", "conservative", "stress"]:
            random_frame = pd.concat(random_portfolios[scenario], axis=1).sort_index() if random_portfolios[scenario] else pd.DataFrame()
            freq_results["portfolio"][scenario] = {
                "buy_and_hold_equal_weight": summarize_returns(
                    portfolio_average(scenario_portfolios[scenario]["buy_and_hold"]), periods
                ),
                "always_flat_equal_weight": summarize_returns(
                    portfolio_average(scenario_portfolios[scenario]["always_flat"]), periods
                ),
                "uniform_frequency_equal_weight": summarize_returns(
                    portfolio_average(scenario_portfolios[scenario]["uniform_frequency"]), periods
                ),
                "random_entry_matched_turnover_equal_weight_mean": summarize_returns(
                    random_frame.mean(axis=1, skipna=True).dropna(), periods
                )
                if not random_frame.empty
                else {},
            }
        results["baselines"][freq] = freq_results

    audit = pd.DataFrame(audit_rows)
    audit.to_csv(ROOT / "DATA_AUDIT.csv", index=False)

    ok_rows = audit[audit["status"] == "ok"]
    expected_ok = len(SYMBOLS) * len(FREQUENCIES)
    if len(ok_rows) < expected_ok:
        results["status"] = "inconclusive"
        results["kill_switches"].append("K1_PARTIAL_DATA_PROVIDER_FAILURE")
    if ok_rows.empty:
        results["status"] = "dead-end"
        results["kill_switches"].append("K1_NO_DATA")

    results["gates"] = {
        "K1_data_available": "PASS" if len(ok_rows) == expected_ok else "FAIL",
        "no_strategy_tested": "PASS",
        "no_winner_declared": "PASS",
        "dsr_pbo_wf_oos_bootstrap": "not_applicable_no_strategy_or_selector",
    }

    (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    run()
