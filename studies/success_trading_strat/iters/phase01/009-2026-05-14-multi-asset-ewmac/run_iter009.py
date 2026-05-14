"""Iteration 009 runner: multi-asset EWMAC trend forecast family.

This iteration pivots away from VXX carry into Carver-style fixed EWMAC trend
forecasts with small trial accounting `[systematic_trading, p.118-119]`, while
retaining MCPT/PBO/DSR as hard anti-overfit controls `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
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


ITERATION = "009-2026-05-14-multi-asset-ewmac"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "TLT", "IEF", "GLD", "SHV"]
DEFENSIVE = "SHV"
CUMULATIVE_TRIALS_AFTER = 24
CONFIGS: list[dict[str, Any]] = [
    {"name": "ewmac_16_64_risk3", "assets": ["SPY", "QQQ", "TLT"], "fast": 16, "slow": 64},
    {"name": "ewmac_32_128_risk3", "assets": ["SPY", "QQQ", "TLT"], "fast": 32, "slow": 128},
    {"name": "ewmac_16_64_div5", "assets": ["SPY", "QQQ", "TLT", "IEF", "GLD"], "fast": 16, "slow": 64},
    {"name": "ewmac_32_128_div5", "assets": ["SPY", "QQQ", "TLT", "IEF", "GLD"], "fast": 32, "slow": 128},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_prices() -> pd.DataFrame:
    frames: dict[str, pd.Series] = {}
    for ticker in REQUIRED:
        path = PRICE_DIR / f"{ticker}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"missing {path}")
        df = pd.read_parquet(path)
        if "date" in df.columns:
            df = df.set_index("date")
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        col = "adj_close" if "adj_close" in df.columns else "close"
        frames[ticker] = df[col].astype(float).sort_index().rename(ticker)
    prices = pd.concat(frames.values(), axis=1, join="inner").dropna()
    prices = prices.loc["2010-01-01":]
    if prices.empty or len(prices) < 252 * 8:
        raise ValueError("insufficient common ETF history")
    return prices


def max_drawdown(returns: pd.Series | np.ndarray) -> float:
    r = pd.Series(np.asarray(returns, dtype=float)).dropna()
    equity = (1.0 + r).cumprod()
    dd = equity / equity.cummax() - 1.0
    return float(dd.min())


def metrics(returns: pd.Series | np.ndarray) -> Metrics:
    r = pd.Series(np.asarray(returns, dtype=float)).dropna()
    years = len(r) / 252.0
    terminal = float((1.0 + r).prod())
    cagr = terminal ** (1.0 / years) - 1.0 if years > 0 else 0.0
    return Metrics(
        cagr=float(cagr),
        sharpe=float(sharpe_annualized(r.to_numpy())),
        mdd=max_drawdown(r),
        terminal_multiple=terminal,
    )


def ewmac_forecasts(prices: pd.DataFrame, assets: list[str], fast: int, slow: int) -> pd.DataFrame:
    px = prices[assets]
    fast_ema = px.ewm(span=fast, adjust=False, min_periods=fast).mean()
    slow_ema = px.ewm(span=slow, adjust=False, min_periods=slow).mean()
    vol_price = px.pct_change().rolling(25, min_periods=25).std() * px
    return (fast_ema - slow_ema) / vol_price.replace(0.0, np.nan)


def strategy_returns(prices: pd.DataFrame, *, assets: list[str], fast: int, slow: int) -> pd.Series:
    daily_returns = prices.pct_change().fillna(0.0)
    forecasts = ewmac_forecasts(prices, assets, fast, slow)
    ranked_forecasts = forecasts.fillna(-np.inf)
    winner = ranked_forecasts.idxmax(axis=1)
    best_score = ranked_forecasts.max(axis=1)
    selected = winner.where(best_score > 0.0, DEFENSIVE).shift(1).fillna(DEFENSIVE)
    out = pd.Series(index=prices.index, dtype=float)
    for asset in assets + [DEFENSIVE]:
        mask = selected == asset
        out.loc[mask] = daily_returns.loc[mask, asset]
    warmup = max(slow, 25) + 1
    return out.fillna(0.0).iloc[warmup:]


def strategy_returns_numpy(prices: pd.DataFrame, *, assets: list[str], fast: int, slow: int) -> pd.Series:
    values = prices[assets + [DEFENSIVE]].to_numpy(dtype=float)
    asset_count = len(assets)
    risk_values = values[:, :asset_count]
    all_returns = np.zeros_like(values)
    all_returns[1:] = values[1:] / values[:-1] - 1.0

    def ema(arr: np.ndarray, span: int) -> np.ndarray:
        alpha = 2.0 / (span + 1.0)
        out = np.full_like(arr, np.nan, dtype=float)
        out[span - 1] = np.mean(arr[:span])
        for i in range(span, len(arr)):
            out[i] = alpha * arr[i] + (1.0 - alpha) * out[i - 1]
        return out

    fast_ema = np.column_stack([ema(risk_values[:, i], fast) for i in range(asset_count)])
    slow_ema = np.column_stack([ema(risk_values[:, i], slow) for i in range(asset_count)])
    vol = np.full_like(risk_values, np.nan, dtype=float)
    risk_rets = all_returns[:, :asset_count]
    for i in range(25, len(risk_values)):
        vol[i] = np.std(risk_rets[i - 24: i + 1], axis=0, ddof=1) * risk_values[i]
    forecast = (fast_ema - slow_ema) / vol
    forecast[~np.isfinite(forecast)] = np.nan
    selected = np.full(len(values), asset_count, dtype=int)
    for i in range(len(values)):
        row = forecast[i]
        if np.all(np.isnan(row)):
            continue
        j = int(np.nanargmax(row))
        if row[j] > 0.0:
            selected[i] = j
    tradable = np.roll(selected, 1)
    tradable[0] = asset_count
    out = all_returns[np.arange(len(values)), tradable]
    warmup = max(slow, 25) + 1
    return pd.Series(out[warmup:], index=prices.index[warmup:])


def benchmark_returns(prices: pd.DataFrame, assets: list[str], index: pd.Index) -> tuple[pd.Series, pd.Series]:
    rets = prices.pct_change().fillna(0.0)
    equal_weight = rets[assets].mean(axis=1).loc[index]
    spy = rets["SPY"].loc[index]
    return equal_weight, spy


def returns_to_prices(first: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    rebuilt = (1.0 + returns).cumprod().mul(first, axis=1)
    first_row = first.to_frame().T
    first_row.index = [returns.index[0] - pd.Timedelta(days=1)]
    return pd.concat([first_row, rebuilt]).sort_index()


def permuted_prices(prices: pd.DataFrame, rng: np.random.Generator, start: int = 1) -> pd.DataFrame:
    rets = prices.pct_change().iloc[1:].copy()
    prefix = prices.iloc[:start].copy()
    tail = rets.iloc[start - 1:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    new_rets = pd.concat([rets.iloc[: start - 1], shuffled]).sort_index()
    rebuilt = returns_to_prices(prefix.iloc[0], new_rets)
    return rebuilt.loc[prices.index[0]:].reindex(prices.index).ffill()


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(prices, assets=config["assets"], fast=config["fast"], slow=config["slow"])).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng)
        stats.append(metrics(strategy_returns(perm, assets=config["assets"], fast=config["fast"], slow=config["slow"])).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    slow = int(config["slow"])
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - slow - 30: start + train + test]
        r = strategy_returns(test_prices, assets=config["assets"], fast=config["fast"], slow=config["slow"]).iloc[-test:]
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
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng, start=1008)
        perm_returns, _ = wf_returns_fixed(perm, config)
        stats.append(metrics(perm_returns).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=909)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        prices = load_prices()
    except (FileNotFoundError, ValueError) as exc:
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
            "kill_switches": ["required_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter009.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered ETF data unavailable: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(prices, assets=config["assets"], fast=config["fast"], slow=config["slow"])
        config_returns[config["name"]] = r
        m = metrics(r)
        rows.append({"config": config["name"], **config, **m.__dict__})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    equal_weight_bench, spy_bench = benchmark_returns(prices.loc[best_returns.index], best_config["assets"], best_returns.index)
    equal_weight_metrics = metrics(equal_weight_bench)
    spy_metrics = metrics(spy_bench)

    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=901)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=902)
    oos = best_returns.iloc[int(len(best_returns) * 0.8):]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)

    numpy_returns = strategy_returns_numpy(prices, assets=best_config["assets"], fast=best_config["fast"], slow=best_config["slow"]).loc[best_returns.index]
    numpy_metrics = metrics(numpy_returns)
    cagr_delta = abs(float(ranked[0]["cagr"]) - numpy_metrics.cagr)

    gates_bool = {
        "economic_sharpe_vs_equal_weight": bool(ranked[0]["sharpe"] > equal_weight_metrics.sharpe),
        "economic_positive_cagr": bool(ranked[0]["cagr"] > 0.0),
        "is_mcpt": bool(is_mcpt["p_value"] <= 0.01),
        "wf_mcpt": bool(wf_mcpt["p_value"] <= 0.05),
        "pbo": bool(float(pbo_res.pbo) < 0.5),
        "dsr": bool(float(dsr_res.p_value) < 0.05),
        "wf_windows": bool(len(wf_windows) >= 8 and sum(w["total_return"] > 0 for w in wf_windows) >= 6),
        "oos": bool((1.0 + oos).prod() - 1.0 > 0.0),
        "fwd_stress": bool((1.0 + fwd).prod() - 1.0 > 0.0),
        "bootstrap": bool(boot_low > 0.0),
        "cross_lib": bool(cagr_delta <= 0.03),
    }
    winner = all(gates_bool.values())
    status = "winner" if winner else "fail"

    write_results({
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": {
            "best": ranked[0],
            "all_configs": rows,
            "wf_total_return": float((1.0 + wf_returns).prod() - 1.0),
            "wf_positive_windows": int(sum(w["total_return"] > 0 for w in wf_windows)),
            "wf_n_windows": len(wf_windows),
            "oos_total_return": float((1.0 + oos).prod() - 1.0),
            "fwd_63d_total_return": float((1.0 + fwd).prod() - 1.0),
            "bootstrap_mean_daily_ci_0_001": boot_low,
            "cross_lib_cagr_delta": cagr_delta,
        },
        "benchmark": {
            "equal_weight_assets": best_config["assets"],
            "equal_weight": equal_weight_metrics.__dict__,
            "spy": spy_metrics.__dict__,
        },
        "gates": {
            **gates_bool,
            "pbo_value": float(pbo_res.pbo),
            "pbo_combinations": int(pbo_res.n_combinations),
            "dsr_p_value": float(dsr_res.p_value),
            "dsr_observed_sharpe_periodic": float(dsr_res.observed_sharpe),
            "dsr_benchmark_sharpe_periodic": float(dsr_res.benchmark_sharpe),
            "is_mcpt": {**is_mcpt, "pass": gates_bool["is_mcpt"]},
            "wf_mcpt": {**wf_mcpt, "pass": gates_bool["wf_mcpt"]},
            "wf_windows": {"pass": gates_bool["wf_windows"], "windows": wf_windows},
            "oos": {"pass": gates_bool["oos"], "total_return": float((1.0 + oos).prod() - 1.0)},
            "fwd_stress": {"pass": gates_bool["fwd_stress"], "total_return": float((1.0 + fwd).prod() - 1.0)},
            "bootstrap": {"pass": gates_bool["bootstrap"], "mean_daily_ci_0_001": boot_low},
            "cross_lib": {"pass": gates_bool["cross_lib"], "numpy_cagr": numpy_metrics.cagr, "delta": cagr_delta},
        },
        "kill_switches": [name for name, ok in gates_bool.items() if not ok],
        "artifacts": ["PRE_REG.md", "run_iter009.py", "RESULTS.json", "SUMMARY.md"],
        "notes": "Multi-asset EWMAC tested with one-bar execution lag; MCPT permutes joint daily return rows to preserve contemporaneous cross-asset structure.",
    })


if __name__ == "__main__":
    main()
