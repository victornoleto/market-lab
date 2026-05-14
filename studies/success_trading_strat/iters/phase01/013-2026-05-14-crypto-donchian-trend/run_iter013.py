"""Iteration 013 runner: BTC/ETH Donchian trend breakout.

This is a pivot away from local VIX-managed tuning into a crypto trend-following
mechanism. Donchian breakout trend logic is motivated by the crypto trend paper,
while the validation stack keeps MCPT/PBO/DSR as hard anti-overfit controls
`[paper.zarattini_2025_crypto_trends, §methodology]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
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


ITERATION = "013-2026-05-14-crypto-donchian-trend"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = {"BTCUSD": "btcusd", "ETHUSD": "ethusd", "SHV": "SHV"}
CUMULATIVE_TRIALS_AFTER = 40
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "btc_don20", "asset": "BTCUSD", "lookback": 20},
    {"name": "btc_don55", "asset": "BTCUSD", "lookback": 55},
    {"name": "eth_don20", "asset": "ETHUSD", "lookback": 20},
    {"name": "eth_don55", "asset": "ETHUSD", "lookback": 55},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def _series_from_parquet(path: Path, ticker: str) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if "date" in df.columns:
        df = df.set_index("date")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    col = "adj_close" if "adj_close" in df.columns else "close"
    return df[col].astype(float).sort_index().rename(ticker)


def load_prices() -> pd.DataFrame:
    frames = []
    for ticker, filename in REQUIRED.items():
        frames.append(_series_from_parquet(PRICE_DIR / f"{filename}.parquet", ticker))
    prices = pd.concat(frames, axis=1, join="inner").dropna()
    prices = prices.loc["2016-01-01":]
    prices = prices[(prices > 0.0).all(axis=1)]
    if prices.empty or len(prices) < 252 * 5:
        raise ValueError("insufficient common BTC/ETH/SHV history")
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
    cagr = terminal ** (1.0 / years) - 1.0 if years > 0 and terminal > 0 else -1.0
    return Metrics(
        cagr=float(cagr),
        sharpe=float(sharpe_annualized(r.to_numpy())),
        mdd=max_drawdown(r),
        terminal_multiple=terminal,
    )


def strategy_returns(prices: pd.DataFrame, *, asset: str, lookback: int) -> pd.Series:
    asset_returns = prices[asset].pct_change().fillna(0.0)
    cash_returns = prices["SHV"].pct_change().fillna(0.0)
    previous_breakout_high = prices[asset].shift(2).rolling(lookback, min_periods=lookback).max()
    signal = prices[asset].shift(1) > previous_breakout_high
    out = asset_returns.where(signal, cash_returns)
    return out.iloc[lookback + 2:].fillna(0.0)


def strategy_returns_numpy(prices: pd.DataFrame, *, asset: str, lookback: int) -> pd.Series:
    values = prices[[asset, "SHV"]].to_numpy(dtype=float)
    rets = np.zeros_like(values)
    rets[1:] = values[1:] / values[:-1] - 1.0
    out = np.zeros(len(values), dtype=float)
    for i in range(len(values)):
        if i >= lookback + 2:
            prior_close = values[i - 1, 0]
            prior_high = float(np.max(values[i - lookback - 1: i - 1, 0]))
            out[i] = rets[i, 0] if prior_close > prior_high else rets[i, 1]
        else:
            out[i] = rets[i, 1]
    return pd.Series(out[lookback + 2:], index=prices.index[lookback + 2:])


def benchmark_returns(prices: pd.DataFrame, asset: str, index: pd.Index) -> tuple[pd.Series, pd.Series]:
    rets = prices.pct_change().fillna(0.0)
    same_asset = rets[asset].loc[index]
    crypto_equal_weight = rets[["BTCUSD", "ETHUSD"]].mean(axis=1).loc[index]
    return same_asset, crypto_equal_weight


def returns_to_prices(first: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    rebuilt = (1.0 + returns).cumprod().mul(first, axis=1)
    first_row = first.to_frame().T
    first_row.index = [returns.index[0] - pd.Timedelta(days=1)]
    return pd.concat([first_row, rebuilt]).sort_index()


def permuted_prices(prices: pd.DataFrame, rng: np.random.Generator, start: int = 1) -> pd.DataFrame:
    returns = prices.pct_change().iloc[1:].copy()
    prefix = prices.iloc[:start].copy()
    tail = returns.iloc[start - 1:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    new_returns = pd.concat([returns.iloc[: start - 1], shuffled]).sort_index()
    rebuilt = returns_to_prices(prefix.iloc[0], new_returns)
    return rebuilt.loc[prices.index[0]:].reindex(prices.index).ffill()


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(prices, asset=config["asset"], lookback=config["lookback"])).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng)
        stats.append(metrics(strategy_returns(perm, asset=config["asset"], lookback=config["lookback"])).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    lookback = int(config["lookback"])
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - lookback - 5: start + train + test]
        r = strategy_returns(test_prices, asset=config["asset"], lookback=lookback).iloc[-test:]
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=1013)
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
            "kill_switches": ["required_data_missing_or_insufficient"],
            "artifacts": ["PRE_REG.md", "run_iter013.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered crypto data unavailable: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(prices, asset=config["asset"], lookback=config["lookback"])
        config_returns[config["name"]] = r
        m = metrics(r)
        same_asset, equal_weight = benchmark_returns(prices, str(config["asset"]), r.index)
        rows.append({
            "config": config["name"],
            **config,
            **m.__dict__,
            "same_asset_bh_sharpe": metrics(same_asset).sharpe,
            "same_asset_bh_cagr": metrics(same_asset).cagr,
            "crypto_ew_bh_sharpe": metrics(equal_weight).sharpe,
        })

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=1313)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=1314)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    same_asset_bh, crypto_ew_bh = benchmark_returns(prices, str(best_config["asset"]), best_returns.index)
    best_metrics = metrics(best_returns)
    same_asset_metrics = metrics(same_asset_bh)
    ew_metrics = metrics(crypto_ew_bh)
    oos_start = int(len(best_returns) * 0.8)
    oos_return = float((1.0 + best_returns.iloc[oos_start:]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_returns = strategy_returns_numpy(prices, asset=str(best_config["asset"]), lookback=int(best_config["lookback"])).loc[best_returns.index]
    numpy_cagr = metrics(numpy_returns).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    data_end = prices.index.max()
    data_stale = bool(data_end < STALE_BLOCK_DATE)
    positive_wf = int(sum(1 for w in wf_windows if w["total_return"] > 0.0))
    wf_required = 6 if len(wf_windows) >= 8 else len(wf_windows)

    gates = {
        "data_not_stale": {"pass": not data_stale, "data_end": str(data_end.date()), "threshold": str(STALE_BLOCK_DATE.date())},
        "economic_sharpe_vs_same_asset_bh": {"pass": best_metrics.sharpe > same_asset_metrics.sharpe, "strategy": best_metrics.sharpe, "benchmark": same_asset_metrics.sharpe},
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
    status = "winner" if winner else "fail"
    kill_switches = [name for name, gate in gates.items() if not gate["pass"]]

    rows_path = OUT_DIR / "config_metrics.csv"
    pd.DataFrame(rows).to_csv(rows_path, index=False)
    wf_path = OUT_DIR / "wf_windows.csv"
    pd.DataFrame(wf_windows).to_csv(wf_path, index=False)

    write_results({
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is_mcpt": 200, "wf_mcpt": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": best_metrics.__dict__,
        "benchmark": {
            "same_asset_buy_hold": same_asset_metrics.__dict__,
            "crypto_equal_weight_buy_hold": ew_metrics.__dict__,
        },
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_iter013.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "BTC/ETH Donchian trend tested on local Tiingo weekday/common cache; crypto cache freshness is an explicit promotion gate.",
    })


if __name__ == "__main__":
    main()
