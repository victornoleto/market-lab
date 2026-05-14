"""Iteration 024 runner: accumulation/distribution volume timing.

This runner tests close-location volume pressure rather than OBV close-to-close
signed volume. Accumulation/Distribution and Intraday Intensity use the close's
position inside the daily range, a distinct volume-confirmation source
`[trading_systems_methods, p.540-541]`, while MCPT/PBO/DSR remain hard controls
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades
from market_lab.backtest.validation.dsr import dsr, sharpe_annualized
from market_lab.backtest.validation.pbo import pbo


ITERATION = "024-2026-05-14-accumulation-distribution-volume"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "SHV"]
CUMULATIVE_TRIALS_AFTER = 84
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_ad21", "asset": "SPY", "indicator": "ad", "lookback": 21},
    {"name": "qqq_ad21", "asset": "QQQ", "indicator": "ad", "lookback": 21},
    {"name": "spy_ii21", "asset": "SPY", "indicator": "ii", "lookback": 21},
    {"name": "qqq_ii21", "asset": "QQQ", "indicator": "ii", "lookback": 21},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def _adjusted_ohlc(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if "adj_close" not in df.columns:
        raise ValueError(f"{ticker} missing adj_close")
    if {"adj_open", "adj_high", "adj_low", "adj_close", "volume"}.issubset(df.columns):
        cols = ["adj_open", "adj_high", "adj_low", "adj_close", "volume"]
        out = df[cols].rename(columns={
            "adj_open": "open",
            "adj_high": "high",
            "adj_low": "low",
            "adj_close": "close",
        })
    elif {"open", "high", "low", "close", "adj_close", "volume"}.issubset(df.columns):
        factor = (df["adj_close"] / df["close"]).replace([np.inf, -np.inf], np.nan)
        out = pd.DataFrame({
            "open": df["open"] * factor,
            "high": df["high"] * factor,
            "low": df["low"] * factor,
            "close": df["adj_close"],
            "volume": df["volume"],
        }, index=df.index)
    else:
        raise ValueError(f"{ticker} missing adjusted/raw OHLCV columns")
    return out.astype(float).rename(columns={col: f"{ticker}_{col}" for col in out.columns})


def load_ticker(ticker: str) -> pd.DataFrame:
    path = PRICE_DIR / f"{ticker}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if "date" in df.columns:
        df = df.set_index("date")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    if ticker == "SHV":
        if "adj_close" not in df.columns:
            raise ValueError("SHV missing adj_close")
        return df[["adj_close"]].astype(float).rename(columns={"adj_close": "SHV_close"})
    return _adjusted_ohlc(df, ticker)


def load_data() -> pd.DataFrame:
    data = pd.concat([load_ticker(t) for t in REQUIRED], axis=1, join="inner").dropna()
    data = data.loc["2010-01-01":]
    price_cols = [col for col in data.columns if col.endswith(("_open", "_high", "_low", "_close"))]
    if data.empty or len(data) < 252 * 5 + 21:
        raise ValueError("insufficient common daily history")
    if not (data[price_cols] > 0.0).all().all():
        raise ValueError("non-positive adjusted OHLC values")
    if not (data[["SPY_volume", "QQQ_volume"]] >= 0.0).all().all():
        raise ValueError("negative risk-asset volume values")
    return data


def close(data: pd.DataFrame, ticker: str) -> pd.Series:
    return data[f"{ticker}_close"].rename(ticker)


def accumulation_distribution(data: pd.DataFrame, ticker: str) -> pd.Series:
    high = data[f"{ticker}_high"]
    low = data[f"{ticker}_low"]
    open_ = data[f"{ticker}_open"]
    close_ = data[f"{ticker}_close"]
    volume = data[f"{ticker}_volume"]
    spread = (high - low).replace(0.0, np.nan)
    pressure = ((close_ - open_) / spread).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return (pressure * volume).cumsum().rename(f"{ticker}_ad")


def intraday_intensity(data: pd.DataFrame, ticker: str) -> pd.Series:
    high = data[f"{ticker}_high"]
    low = data[f"{ticker}_low"]
    close_ = data[f"{ticker}_close"]
    volume = data[f"{ticker}_volume"]
    spread = (high - low).replace(0.0, np.nan)
    pressure = (((close_ - low) - (high - close_)) / spread).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return (pressure * volume).cumsum().rename(f"{ticker}_ii")


def indicator_series(data: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    if config["indicator"] == "ad":
        return accumulation_distribution(data, asset)
    if config["indicator"] == "ii":
        return intraday_intensity(data, asset)
    raise ValueError(f"unknown indicator {config['indicator']}")


def signal_for_asset(data: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    lookback = int(config["lookback"])
    signal = indicator_series(data, config).diff(lookback) > 0.0
    return signal.shift(1).fillna(False).astype(bool)


def strategy_returns(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    asset_r = close(data, asset).pct_change().fillna(0.0)
    shv_r = close(data, "SHV").pct_change().fillna(0.0)
    risk_on = signal_for_asset(data, config)
    return pd.Series(np.where(risk_on, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def strategy_returns_numpy(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    arr = data[[f"{asset}_open", f"{asset}_high", f"{asset}_low", f"{asset}_close", f"{asset}_volume", "SHV_close"]].to_numpy(dtype=float)
    open_, high, low, price, volume, shv = arr.T
    spread = high - low
    safe_spread = np.where(spread == 0.0, np.nan, spread)
    if config["indicator"] == "ad":
        pressure = np.nan_to_num((price - open_) / safe_spread, nan=0.0, posinf=0.0, neginf=0.0)
    else:
        pressure = np.nan_to_num(((price - low) - (high - price)) / safe_spread, nan=0.0, posinf=0.0, neginf=0.0)
    cumul = np.cumsum(pressure * volume)
    lookback = int(config["lookback"])
    delta = np.full(len(cumul), np.nan, dtype=float)
    delta[lookback:] = cumul[lookback:] - cumul[:-lookback]
    signal = np.r_[False, (delta > 0.0)[:-1]]
    asset_r = np.r_[0.0, price[1:] / price[:-1] - 1.0]
    shv_r = np.r_[0.0, shv[1:] / shv[:-1] - 1.0]
    return pd.Series(np.where(signal, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def benchmark_returns(data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return close(data, str(config["asset"])).pct_change().fillna(0.0).loc[index]


def max_drawdown(returns: pd.Series | np.ndarray) -> float:
    r = pd.Series(np.asarray(returns, dtype=float)).dropna()
    equity = (1.0 + r).cumprod()
    return float((equity / equity.cummax() - 1.0).min())


def metrics(returns: pd.Series | np.ndarray) -> Metrics:
    r = pd.Series(np.asarray(returns, dtype=float)).dropna()
    years = len(r) / 252.0
    terminal = float((1.0 + r).prod())
    cagr = terminal ** (1.0 / years) - 1.0 if years > 0 and terminal > 0 else -1.0
    return Metrics(cagr=float(cagr), sharpe=float(sharpe_annualized(r.to_numpy())), mdd=max_drawdown(r), terminal_multiple=terminal)


def permuted_data(data: pd.DataFrame, rng: np.random.Generator, start: int = 0) -> pd.DataFrame:
    returns = data[["SPY_open", "SPY_high", "SPY_low", "SPY_close", "QQQ_open", "QQQ_high", "QQQ_low", "QQQ_close", "SHV_close"]].pct_change().fillna(0.0)
    volumes = data[["SPY_volume", "QQQ_volume"]]
    tail_pos = np.arange(max(start, 1), len(data))
    shuffled_pos = tail_pos[rng.permutation(len(tail_pos))]
    prefix = data.iloc[:start].copy()
    base = data.iloc[[0]].copy() if prefix.empty else prefix.iloc[[-1]].copy()
    ohlc_cols = returns.columns.tolist()
    price_values = [base[ohlc_cols].iloc[0].to_numpy(dtype=float)]
    for row in returns.iloc[shuffled_pos].to_numpy(dtype=float):
        price_values.append(price_values[-1] * (1.0 + row))
    idx = data.index if prefix.empty else data.index[start - 1:]
    rebuilt = pd.DataFrame(price_values, index=idx, columns=ohlc_cols)
    volume_pos = np.r_[start - 1 if start else 0, shuffled_pos]
    rebuilt[["SPY_volume", "QQQ_volume"]] = volumes.iloc[volume_pos].to_numpy(dtype=float)
    if prefix.empty:
        return rebuilt[data.columns]
    return pd.concat([data.iloc[: start - 1], rebuilt[data.columns]])


def mcpt_fixed_config(data: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(data, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_data(data, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(data: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(data):
        test_data = data.iloc[start + train: start + train + test]
        r = strategy_returns(test_data, config=config).iloc[-test + 1:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(data: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed_returns, windows = wf_returns_fixed(data, config)
    observed = metrics(observed_returns).sharpe
    stats = [metrics(wf_returns_fixed(permuted_data(data, rng, start=1008), config)[0]).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2405)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_data()
    except Exception as exc:  # noqa: BLE001 - artifact must record honest data blockers.
        write_results({
            "iteration": ITERATION,
            "status": "data_blocked",
            "pre_registered": True,
            "n_trials": 0,
            "mcpt_reps": {},
            "best_config": None,
            "winner": False,
            "metrics": {},
            "benchmark": {},
            "gates": {},
            "kill_switches": ["required_ohlcv_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter024.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bm = metrics(benchmark_returns(data, config, r.index))
        rows.append({"config": config["name"], **config, **m.__dict__, "benchmark_sharpe": bm.sharpe, "benchmark_cagr": bm.cagr, "benchmark_mdd": bm.mdd})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]
    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(data, best_config, n=200, seed=2403)
    wf_mcpt = wf_mcpt_fixed(data, best_config, n=100, seed=2404)
    wf_returns, wf_windows = wf_returns_fixed(data, best_config)
    bench_returns = benchmark_returns(data, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(data, config=best_config).loc[best_returns.index]).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    data_end = data.index.max()
    positive_wf = int(sum(1 for w in wf_windows if w["total_return"] > 0.0))
    wf_required = 6 if len(wf_windows) >= 8 else len(wf_windows)
    gates = {
        "data_not_stale": {"pass": bool(data_end >= STALE_BLOCK_DATE), "data_end": str(data_end.date()), "threshold": str(STALE_BLOCK_DATE.date())},
        "economic_sharpe_vs_benchmark": {"pass": best_metrics.sharpe > bench_metrics.sharpe, "strategy": best_metrics.sharpe, "benchmark": bench_metrics.sharpe},
        "is_mcpt": {"pass": is_mcpt["p_value"] <= 0.01, **is_mcpt},
        "wf_mcpt": {"pass": wf_mcpt["p_value"] <= 0.05, **wf_mcpt},
        "pbo": {"pass": float(pbo_res.pbo) < 0.5, "value": float(pbo_res.pbo)},
        "dsr": {"pass": float(dsr_res.p_value) < 0.05, "p_value": float(dsr_res.p_value), "n_trials": CUMULATIVE_TRIALS_AFTER},
        "walk_forward": {"pass": positive_wf >= wf_required, "positive_windows": positive_wf, "n_windows": len(wf_windows), "required_positive": wf_required},
        "oos": {"pass": oos_return > 0.0, "return": oos_return},
        "fwd_63d": {"pass": fwd_63d > 0.0, "return": fwd_63d},
        "bootstrap_999_mean_daily_low": {"pass": boot_low > 0.0, "value": boot_low},
        "cross_lib_cagr": {"pass": cagr_delta_pp <= 3.0, "numpy_cagr": numpy_cagr, "delta_pp": cagr_delta_pp},
    }
    winner = bool(all(g["pass"] for g in gates.values()))
    pd.DataFrame(rows).to_csv(OUT_DIR / "config_metrics.csv", index=False)
    pd.DataFrame(wf_windows).to_csv(OUT_DIR / "wf_windows.csv", index=False)
    write_results({
        "iteration": ITERATION,
        "status": "winner" if winner else "fail",
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": best_name,
        "winner": winner,
        "metrics": {**best_metrics.__dict__, "oos_return": oos_return, "fwd_63d_return": fwd_63d, "bootstrap_999_mean_daily_low": boot_low},
        "benchmark": bench_metrics.__dict__,
        "gates": gates,
        "kill_switches": [] if winner else [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter024.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Accumulation/distribution close-location volume family with one-bar lag; no deployment authorization.",
    })


if __name__ == "__main__":
    main()
