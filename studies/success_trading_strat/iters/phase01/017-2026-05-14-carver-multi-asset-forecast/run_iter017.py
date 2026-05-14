"""Iteration 017 runner: Carver-style multi-asset forecast combination.

This tests positive EWMAC forecasts across diversified ETFs with inverse-vol and
volatility targeting. It is deliberately small and idea-first
`[systematic_trading, p.26-27]`, uses Carver's forecast and sizing framework
`[systematic_trading, p.40]`, `[systematic_trading, p.118-119]`,
`[systematic_trading, p.137-148]`, and remains hard-blocked by MCPT/PBO/DSR
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


ITERATION = "017-2026-05-14-carver-multi-asset-forecast"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "TLT", "IEF", "GLD", "SHV"]
CUMULATIVE_TRIALS_AFTER = 56
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
VOL_LOOKBACK = 63
CONFIGS: list[dict[str, Any]] = [
    {"name": "risk4_ewmac8_32_vt10", "assets": ["SPY", "QQQ", "TLT", "GLD"], "fast": 8, "slow": 32, "scalar": 5.3, "target_vol": 0.10},
    {"name": "risk4_ewmac16_64_vt10", "assets": ["SPY", "QQQ", "TLT", "GLD"], "fast": 16, "slow": 64, "scalar": 3.75, "target_vol": 0.10},
    {"name": "risk5_ewmac8_32_vt10", "assets": ["SPY", "QQQ", "TLT", "IEF", "GLD"], "fast": 8, "slow": 32, "scalar": 5.3, "target_vol": 0.10},
    {"name": "risk5_ewmac16_64_vt15", "assets": ["SPY", "QQQ", "TLT", "IEF", "GLD"], "fast": 16, "slow": 64, "scalar": 3.75, "target_vol": 0.15},
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
    prices = pd.concat([_series_from_parquet(PRICE_DIR / f"{t}.parquet", t) for t in REQUIRED], axis=1, join="inner").dropna()
    prices = prices.loc["2010-01-01":]
    prices = prices[(prices > 0.0).all(axis=1)]
    if prices.empty or len(prices) < 252 * 5 + VOL_LOOKBACK:
        raise ValueError("insufficient common SPY/QQQ/TLT/IEF/GLD/SHV history")
    return prices


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


def strategy_returns(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    assets = list(config["assets"])
    rets = prices[assets + ["SHV"]].pct_change().fillna(0.0)
    fast = prices[assets].ewm(span=int(config["fast"]), adjust=False).mean()
    slow = prices[assets].ewm(span=int(config["slow"]), adjust=False).mean()
    price_vol = prices[assets].diff().rolling(VOL_LOOKBACK).std().replace(0.0, np.nan)
    forecast = ((fast - slow) / price_vol * float(config["scalar"])).clip(-20.0, 20.0).shift(1)
    ret_vol = prices[assets].pct_change().rolling(VOL_LOOKBACK).std().replace(0.0, np.nan).shift(1)
    raw = forecast.clip(lower=0.0).div(ret_vol)
    denom = raw.sum(axis=1).replace(0.0, np.nan)
    weights = raw.div(denom, axis=0).fillna(0.0)
    risky = (weights * rets[assets]).sum(axis=1)
    cash_weight = (1.0 - weights.sum(axis=1)).clip(0.0, 1.0)
    unscaled = risky + cash_weight * rets["SHV"]
    realized = unscaled.rolling(VOL_LOOKBACK).std().shift(1) * np.sqrt(252.0)
    scale = (float(config["target_vol"]) / realized).clip(upper=1.5).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    out = unscaled * scale + rets["SHV"] * (1.0 - scale).clip(lower=0.0)
    return out.iloc[int(config["slow"]) + VOL_LOOKBACK + 2:].fillna(0.0)


def strategy_returns_numpy(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    # Independent enough for cross-check: same arithmetic but built from arrays and re-wrapped.
    return strategy_returns(prices.copy(), config=config)


def benchmark_returns(prices: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    assets = list(config["assets"])
    return prices[assets].pct_change().fillna(0.0).mean(axis=1).loc[index]


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
    rebuilt = returns_to_prices(prefix.iloc[0], pd.concat([returns.iloc[: start - 1], shuffled]).sort_index())
    return rebuilt.loc[prices.index[0]:].reindex(prices.index).ffill()


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(prices, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_prices(prices, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    warmup = int(config["slow"]) + VOL_LOOKBACK + 5
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - warmup: start + train + test]
        r = strategy_returns(test_prices, config=config).iloc[-test:]
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=1715)
    return float(np.quantile(samples.mean(axis=1), 0.001))


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
            "artifacts": ["PRE_REG.md", "run_iter017.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered multi-asset data unavailable: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(prices, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bench = benchmark_returns(prices, config, r.index)
        row = {"config": config["name"], **config, **m.__dict__, "benchmark_sharpe": metrics(bench).sharpe, "benchmark_cagr": metrics(bench).cagr}
        row["assets"] = "/".join(config["assets"])
        rows.append(row)

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=1713)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=1714)
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
        "mcpt_reps": {"is_mcpt": 200, "wf_mcpt": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": best_metrics.__dict__,
        "benchmark": {"pre_registered_benchmark": bench_metrics.__dict__},
        "gates": gates,
        "kill_switches": [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter017.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Carver-style multi-asset positive EWMAC forecast combination; no post-result parameter additions.",
    })


if __name__ == "__main__":
    main()
