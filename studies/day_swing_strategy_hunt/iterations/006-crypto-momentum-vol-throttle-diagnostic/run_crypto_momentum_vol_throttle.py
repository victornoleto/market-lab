"""Iteration 006: crypto momentum with volatility throttle diagnostic.

Research-only; no paper/live trading. PRE_REG.md was created before this script.

Citations:
- Crypto momentum with volatility throttle: [volatility_trading, ch.2].
- D1 horizon and transaction-cost stress: [systematic_trading, p.182-197].
- Random-entry and turnover controls: [evidence_based_ta, p.247-260].
- OOS/bootstrap gates and PBO rule: [advances_fin_ml, p.31-34, p.208-211].
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import dukascopy_python as dk
import numpy as np
import pandas as pd


ITERATION = "006-crypto-momentum-vol-throttle-diagnostic"
ROOT = Path(__file__).resolve().parent
ITER001_RESULTS = ROOT.parent / "001-tsmom-data-audit" / "RESULTS.json"
START = datetime(2018, 1, 1, tzinfo=timezone.utc)
END = datetime(2026, 5, 1, tzinfo=timezone.utc)
OOS_START = pd.Timestamp("2024-01-01", tz="UTC")
SYMBOLS = ["BTCUSD", "ETHUSD"]
DUKAS_PAIR_MAP = {"BTCUSD": "BTC/USD", "ETHUSD": "ETH/USD"}
PERIODS_PER_YEAR = 252
RNG_SEED = 20260503
N_BOOTSTRAP = 2000
N_RANDOM_RUNS = 200
CI_Q = 0.001
COST_BPS = {"CRYPTO": {"base": 10.0, "conservative": 25.0, "stress": 50.0}}


@dataclass(frozen=True)
class SeriesResult:
    returns: pd.Series
    turnover: float
    entries: int
    avg_exposure: float


def scenario_cost(_symbol: str, scenario: str) -> float:
    return COST_BPS["CRYPTO"][scenario] / 10_000.0


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
    return SeriesResult(
        returns=ret,
        turnover=float(turnover.sum()),
        entries=entries,
        avg_exposure=float(pos.abs().mean()),
    )


def throttle_position(close: pd.Series) -> pd.Series:
    momentum = close.pct_change(60)
    returns = close.pct_change()
    realized_vol = returns.rolling(20).std(ddof=1) * np.sqrt(PERIODS_PER_YEAR)
    vol_pct = realized_vol.rolling(252).rank(pct=True)
    exposure = pd.Series(0.0, index=close.index)
    exposure[(momentum > 0.0) & (vol_pct <= 0.80)] = 1.0
    exposure[(momentum > 0.0) & (vol_pct > 0.80) & (vol_pct <= 0.95)] = 0.5
    exposure[(momentum > 0.0) & (vol_pct > 0.95)] = 0.0
    return exposure.fillna(0.0)


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


def random_position(index: pd.Index, entries: int, avg_hold_bars: int, exposure_scale: float, seed: int) -> pd.Series:
    values = np.zeros(len(index), dtype=float)
    if entries <= 0 or len(index) <= avg_hold_bars:
        return pd.Series(values, index=index)
    rng = np.random.default_rng(seed)
    candidates = np.arange(0, max(1, len(index) - avg_hold_bars))
    rng.shuffle(candidates)
    occupied = np.zeros(len(index), dtype=bool)
    starts: list[int] = []
    for candidate in candidates:
        end = min(candidate + avg_hold_bars, len(index))
        if occupied[candidate:end].any():
            continue
        starts.append(int(candidate))
        occupied[candidate:end] = True
        if len(starts) >= entries:
            break
    for start in starts:
        values[start : min(start + avg_hold_bars, len(index))] = exposure_scale
    return pd.Series(values, index=index)


def pass_bool(value: bool) -> str:
    return "PASS" if value else "FAIL"


def load_iter001_crypto_baselines() -> dict[str, object]:
    raw = json.loads(ITER001_RESULTS.read_text(encoding="utf-8"))
    d1 = raw["baselines"]["D1"]
    assets = {symbol: d1["assets"][symbol] for symbol in SYMBOLS}
    portfolio: dict[str, dict[str, object]] = {}
    for scenario in ["base", "conservative", "stress"]:
        portfolio[scenario] = {}
        for baseline in ["buy_and_hold", "always_flat", "uniform_frequency", "random_entry_matched_turnover_mean"]:
            rows = [assets[symbol][scenario][baseline] for symbol in SYMBOLS]
            portfolio[scenario][baseline + "_crypto_mean_metrics"] = {
                key: mean_metric([row[key] for row in rows if row.get(key) is not None])
                for key in ["cagr", "sharpe", "max_drawdown", "total_return"]
            }
    return {"source": "../001-tsmom-data-audit/RESULTS.json baselines.D1 crypto subset", "assets": assets, "portfolio": portfolio}


def mean_metric(values: list[float]) -> float | None:
    if not values:
        return None
    return float(np.mean(values))


def run() -> None:
    baselines = load_iter001_crypto_baselines()
    close_by_symbol: dict[str, pd.Series] = {}
    audit_rows: list[dict[str, object]] = []
    for symbol in SYMBOLS:
        try:
            df = fetch_dukascopy(symbol)
        except Exception as exc:  # noqa: BLE001
            audit_rows.append({"symbol": symbol, "status": "error", "error": str(exc)})
            continue
        close = df["close"].dropna() if "close" in df else pd.Series(dtype=float)
        status = "ok" if len(close) >= 1000 and close.index.duplicated().sum() == 0 else "fail"
        if status == "ok":
            close_by_symbol[symbol] = close
        audit_rows.append(
            {
                "symbol": symbol,
                "status": status,
                "bars": int(len(close)),
                "start": str(close.index.min()) if not close.empty else None,
                "end": str(close.index.max()) if not close.empty else None,
                "duplicate_timestamps": int(close.index.duplicated().sum()) if not close.empty else None,
                "missing_close": int(df["close"].isna().sum()) if "close" in df else None,
                "caveats": "Dukascopy BID-only; no broker-specific swap/overnight history.",
            }
        )

    pd.DataFrame(audit_rows).to_csv(ROOT / "DATA_AUDIT_D1.csv", index=False)

    strategy_by_scenario: dict[str, dict[str, pd.Series]] = {scenario: {} for scenario in ["base", "conservative", "stress"]}
    asset_results: dict[str, object] = {}
    base_positions: dict[str, pd.Series] = {}
    matched_random_runs: list[pd.Series] = []

    for symbol, close in close_by_symbol.items():
        position = throttle_position(close)
        base_positions[symbol] = position
        asset_results[symbol] = {}
        for scenario in ["base", "conservative", "stress"]:
            result = position_returns(close, position, scenario_cost(symbol, scenario))
            asset_results[symbol][scenario] = summarize_returns(result.returns) | {
                "turnover": result.turnover,
                "entries": result.entries,
                "avg_exposure": result.avg_exposure,
            }
            strategy_by_scenario[scenario][symbol] = result.returns

    if close_by_symbol:
        for run_id in range(N_RANDOM_RUNS):
            run_series = {}
            for symbol, close in close_by_symbol.items():
                position = base_positions[symbol]
                entries = int(((position > 0) & (position.shift(1).fillna(0.0) == 0)).sum())
                nonzero = int((position > 0).sum())
                avg_hold = max(1, int(round(nonzero / entries))) if entries else 1
                exposure_scale = float(position[position > 0].mean()) if (position > 0).any() else 0.0
                rp = random_position(close.index, entries, avg_hold, exposure_scale, RNG_SEED + run_id + len(symbol) * 1000)
                run_series[symbol] = position_returns(close, rp, scenario_cost(symbol, "base")).returns
            matched_random_runs.append(portfolio_average(run_series))

    portfolio_results: dict[str, object] = {}
    portfolio_series: dict[str, pd.Series] = {}
    for scenario in ["base", "conservative", "stress"]:
        ret = portfolio_average(strategy_by_scenario[scenario]) if strategy_by_scenario[scenario] else pd.Series(dtype=float)
        portfolio_series[scenario] = ret
        portfolio_results[scenario] = {
            "full": summarize_returns(ret),
            "in_sample_pre_2024": summarize_returns(ret[ret.index < OOS_START]),
            "oos_2024_plus": summarize_returns(ret[ret.index >= OOS_START]),
            "bootstrap_full": bootstrap_annualized_mean_ci_low(ret, RNG_SEED),
            "bootstrap_oos": bootstrap_annualized_mean_ci_low(ret[ret.index >= OOS_START], RNG_SEED + 10_000),
        }

    matched_random = pd.concat(matched_random_runs, axis=1).mean(axis=1, skipna=True).dropna() if matched_random_runs else pd.Series(dtype=float)
    base_full = portfolio_results.get("base", {}).get("full", {})
    stress_full = portfolio_results.get("stress", {}).get("full", {})
    oos = portfolio_results.get("base", {}).get("oos_2024_plus", {})
    boot_full = portfolio_results.get("base", {}).get("bootstrap_full", {})
    boot_oos = portfolio_results.get("base", {}).get("bootstrap_oos", {})
    bh = baselines["portfolio"]["base"]["buy_and_hold_crypto_mean_metrics"]
    uniform = baselines["portfolio"]["base"]["uniform_frequency_crypto_mean_metrics"]
    rnd001 = baselines["portfolio"]["base"]["random_entry_matched_turnover_mean_crypto_mean_metrics"]
    rnd_matched = summarize_returns(matched_random) | {"runs": N_RANDOM_RUNS}

    gates = {
        "K1_data_reliability": pass_bool(len(close_by_symbol) == len(SYMBOLS)),
        "cost_stress_positive": pass_bool((stress_full.get("cagr") or 0.0) > 0 and (stress_full.get("sharpe") or 0.0) > 0),
        "oos_single_block_positive": pass_bool((oos.get("cagr") or 0.0) > 0 and (oos.get("sharpe") or 0.0) > 0),
        "bootstrap_full_ci_low_gt_0": pass_bool((boot_full.get("ci_low") or -1.0) > 0),
        "bootstrap_oos_ci_low_gt_0": pass_bool((boot_oos.get("ci_low") or -1.0) > 0),
        "pbo": "NOT_APPLICABLE_SINGLE_CONFIG",
        "beats_buy_and_hold_crypto_sharpe_base": pass_bool((base_full.get("sharpe") or -999.0) > (bh.get("sharpe") or -999.0)),
        "beats_uniform_frequency_crypto_sharpe_base": pass_bool((base_full.get("sharpe") or -999.0) > (uniform.get("sharpe") or -999.0)),
        "beats_iter001_random_entry_crypto_sharpe_base": pass_bool((base_full.get("sharpe") or -999.0) > (rnd001.get("sharpe") or -999.0)),
        "beats_strategy_matched_random_entry_sharpe_base": pass_bool((base_full.get("sharpe") or -999.0) > (rnd_matched.get("sharpe") or -999.0)),
        "no_crypto_only_winner_declared": "PASS",
    }

    kill_switches: list[str] = ["K6_CRYPTO_ONLY_DIAGNOSTIC_NO_WINNER"]
    if gates["K1_data_reliability"] == "FAIL":
        kill_switches.append("K1_CRYPTO_D1_DATA_UNRELIABLE")
    if gates["beats_strategy_matched_random_entry_sharpe_base"] == "FAIL":
        kill_switches.append("K2_RANDOM_ENTRY_MATCHED_TURNOVER_DOMINATES")
    if gates["bootstrap_oos_ci_low_gt_0"] == "FAIL":
        kill_switches.append("K4_OOS_BOOTSTRAP_LOW_LE_0")
    if gates["cost_stress_positive"] == "FAIL":
        kill_switches.append("K5_COST_STRESS_ELIMINATES_EDGE")
    if gates["beats_buy_and_hold_crypto_sharpe_base"] == "FAIL":
        kill_switches.append("K9_LONG_BETA_CRYPTO_NOT_BEATEN")

    status = "positive"
    if gates["K1_data_reliability"] == "FAIL":
        status = "inconclusive"
    elif any(gates[name] == "FAIL" for name in ["cost_stress_positive", "bootstrap_oos_ci_low_gt_0", "beats_strategy_matched_random_entry_sharpe_base"]):
        status = "dead-end"
    elif any(value == "FAIL" for value in gates.values()):
        status = "negative"

    results = {
        "iteration": ITERATION,
        "status": status,
        "hypothesis": "Crypto momentum D1 with realized-volatility percentile throttle",
        "pre_registered": True,
        "universe": SYMBOLS,
        "frequencies": ["D1"],
        "cost_scenarios": COST_BPS,
        "baselines": baselines | {"strategy_matched_random_entry_mean": rnd_matched},
        "strategy_results": {"portfolio": portfolio_results, "assets": asset_results},
        "gates": gates,
        "kill_switches": kill_switches,
        "n_trials": 1,
        "artifacts": ["PRE_REG.md", "run_crypto_momentum_vol_throttle.py", "DATA_AUDIT_D1.csv", "RESULTS.json", "SUMMARY.md"],
        "notes": "Research-only diagnostic. BTCUSD/ETHUSD-only cannot be a winner; no paper/live.",
    }
    (ROOT / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    run()
