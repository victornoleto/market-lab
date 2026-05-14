"""Iteration 022 runner: KAMA/Efficiency Ratio regime timing.

KAMA uses Kaufman's Efficiency Ratio to adapt smoothing to directional vs noisy
price action; the rule remains a candidate only if it clears MCPT, PBO and DSR
`[trading_systems_methods, p.10-11]`, `[trading_systems_methods, p.780-782]`,
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


ITERATION = "022-2026-05-14-kama-efficiency-regime"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "SHV"]
CUMULATIVE_TRIALS_AFTER = 76
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_kama_slope", "asset": "SPY", "er_threshold": None},
    {"name": "qqq_kama_slope", "asset": "QQQ", "er_threshold": None},
    {"name": "spy_kama_er20", "asset": "SPY", "er_threshold": 0.20},
    {"name": "qqq_kama_er20", "asset": "QQQ", "er_threshold": 0.20},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_adjusted_close(ticker: str) -> pd.Series:
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
    if "adj_close" not in df.columns:
        raise ValueError(f"{ticker} missing adj_close")
    out = df["adj_close"].astype(float).sort_index().rename(ticker)
    return out[~out.index.duplicated(keep="last")]


def load_prices() -> pd.DataFrame:
    prices = pd.concat([load_adjusted_close(t) for t in REQUIRED], axis=1, join="inner").dropna()
    prices = prices.loc["2010-01-01":]
    if prices.empty or len(prices) < 252 * 5 + 60:
        raise ValueError("insufficient common adjusted-close history")
    if not (prices > 0.0).all().all():
        raise ValueError("non-positive adjusted close values")
    return prices


def efficiency_ratio(price: pd.Series, lookback: int = 10) -> pd.Series:
    change = (price - price.shift(lookback)).abs()
    volatility = price.diff().abs().rolling(lookback).sum()
    return (change / volatility.replace(0.0, np.nan)).fillna(0.0)


def kama(price: pd.Series, er_lookback: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    er = efficiency_ratio(price, er_lookback)
    fast_sc = 2.0 / (fast + 1.0)
    slow_sc = 2.0 / (slow + 1.0)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    values = np.empty(len(price), dtype=float)
    arr = price.to_numpy(dtype=float)
    values[0] = arr[0]
    for i in range(1, len(arr)):
        values[i] = values[i - 1] + sc.iloc[i] * (arr[i] - values[i - 1])
    return pd.Series(values, index=price.index, name=f"{price.name}_kama")


def signal_for_asset(prices: pd.DataFrame, asset: str, er_threshold: float | None) -> pd.Series:
    price = prices[asset]
    k = kama(price)
    slope_positive = k.diff() > 0.0
    signal = slope_positive
    if er_threshold is not None:
        signal = signal & (efficiency_ratio(price) >= er_threshold)
    return signal.shift(1).fillna(False).astype(bool)


def strategy_returns(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    asset_r = prices[asset].pct_change().fillna(0.0)
    shv_r = prices["SHV"].pct_change().fillna(0.0)
    risk_on = signal_for_asset(prices, asset, config["er_threshold"])
    return pd.Series(np.where(risk_on, asset_r, shv_r), index=prices.index, name=str(config["name"])).iloc[1:]


def strategy_returns_numpy(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    arr = prices[[str(config["asset"]), "SHV"]].to_numpy(dtype=float)
    asset = pd.Series(arr[:, 0], index=prices.index)
    shv = pd.Series(arr[:, 1], index=prices.index)
    k = kama(asset.rename(str(config["asset"])))
    sig = k.diff() > 0.0
    if config["er_threshold"] is not None:
        sig = sig & (efficiency_ratio(asset.rename(str(config["asset"]))) >= float(config["er_threshold"]))
    sig = sig.shift(1).fillna(False).to_numpy(dtype=bool)
    asset_r = np.r_[0.0, arr[1:, 0] / arr[:-1, 0] - 1.0]
    shv_r = np.r_[0.0, shv.to_numpy()[1:] / shv.to_numpy()[:-1] - 1.0]
    return pd.Series(np.where(sig, asset_r, shv_r), index=prices.index, name=str(config["name"])).iloc[1:]


def benchmark_returns(prices: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return prices[str(config["asset"])].pct_change().fillna(0.0).loc[index]


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


def permuted_prices(prices: pd.DataFrame, rng: np.random.Generator, start: int = 0) -> pd.DataFrame:
    returns = prices.pct_change().fillna(0.0)
    prefix = prices.iloc[:start].copy()
    tail_returns = returns.iloc[max(start, 1):].copy()
    shuffled = tail_returns.iloc[rng.permutation(len(tail_returns))]
    if prefix.empty:
        base = prices.iloc[[0]].copy()
    else:
        base = prefix.iloc[[-1]].copy()
    values = [base.iloc[0].to_numpy(dtype=float)]
    for row in shuffled.to_numpy(dtype=float):
        values.append(values[-1] * (1.0 + row))
    idx = prices.index if prefix.empty else prices.index[start - 1:]
    rebuilt_tail = pd.DataFrame(values, index=idx, columns=prices.columns)
    if prefix.empty:
        return rebuilt_tail
    return pd.concat([prices.iloc[: start - 1], rebuilt_tail])


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(prices, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_prices(prices, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train: start + train + test]
        r = strategy_returns(test_prices, config=config).iloc[-test + 1:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(prices: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed_returns, windows = wf_returns_fixed(prices, config)
    observed = metrics(observed_returns).sharpe
    stats = [metrics(wf_returns_fixed(permuted_prices(prices, rng, start=1008), config)[0]).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2205)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        prices = load_prices()
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
            "kill_switches": ["required_adjusted_close_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter022.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(prices, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bm = metrics(benchmark_returns(prices, config, r.index))
        rows.append({"config": config["name"], **config, **m.__dict__, "benchmark_sharpe": bm.sharpe, "benchmark_cagr": bm.cagr, "benchmark_mdd": bm.mdd})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]
    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=2203)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=2204)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    bench_returns = benchmark_returns(prices, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(prices, config=best_config).loc[best_returns.index]).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    data_end = prices.index.max()
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
        "artifacts": ["PRE_REG.md", "run_iter022.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "KAMA/ER adaptive-regime family with one-bar lag; no deployment authorization.",
    })


if __name__ == "__main__":
    main()
