"""Iteration 016 runner: credit-risk appetite filter.

The rule uses `HYG/IEF` as a cross-asset risk-appetite proxy for equity exposure,
then requires lagged own-asset momentum before holding SPY or QQQ. The design is
idea-first and deliberately small `[systematic_trading, p.26-27]`, uses
diversification across markets `[systematic_trading, p.42]`, and remains subject
to MCPT/PBO/DSR hard controls `[testing_tuning, p.318-320]`,
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


ITERATION = "016-2026-05-14-credit-risk-appetite-filter"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = {"SPY": "SPY", "QQQ": "QQQ", "HYG": "HYG", "IEF": "IEF", "SHV": "SHV"}
CUMULATIVE_TRIALS_AFTER = 52
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
MOM_LOOKBACK = 63
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_hygief63_m63", "asset": "SPY", "credit_lookback": 63},
    {"name": "spy_hygief126_m63", "asset": "SPY", "credit_lookback": 126},
    {"name": "qqq_hygief63_m63", "asset": "QQQ", "credit_lookback": 63},
    {"name": "qqq_hygief126_m63", "asset": "QQQ", "credit_lookback": 126},
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
    frames = [_series_from_parquet(PRICE_DIR / f"{filename}.parquet", ticker) for ticker, filename in REQUIRED.items()]
    prices = pd.concat(frames, axis=1, join="inner").dropna()
    prices = prices.loc["2010-01-01":]
    prices = prices[(prices > 0.0).all(axis=1)]
    if prices.empty or len(prices) < 252 * 5 + max(MOM_LOOKBACK, 126):
        raise ValueError("insufficient common SPY/QQQ/HYG/IEF/SHV history")
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
    return Metrics(cagr=float(cagr), sharpe=float(sharpe_annualized(r.to_numpy())), mdd=max_drawdown(r), terminal_multiple=terminal)


def strategy_returns(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    credit_lookback = int(config["credit_lookback"])
    rets = prices[[asset, "SHV"]].pct_change().fillna(0.0)
    credit_ratio = prices["HYG"] / prices["IEF"]
    credit_momentum = credit_ratio.pct_change(credit_lookback).shift(1)
    asset_momentum = prices[asset].pct_change(MOM_LOOKBACK).shift(1)
    risk_on = (credit_momentum > 0.0) & (asset_momentum > 0.0)
    out = rets[asset].where(risk_on, rets["SHV"])
    warmup = max(MOM_LOOKBACK, credit_lookback) + 2
    return out.iloc[warmup:].fillna(0.0)


def strategy_returns_numpy(prices: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    asset_idx = 0 if asset == "SPY" else 1
    credit_lookback = int(config["credit_lookback"])
    values = prices[["SPY", "QQQ", "HYG", "IEF", "SHV"]].to_numpy(dtype=float)
    rets = np.zeros_like(values)
    rets[1:] = values[1:] / values[:-1] - 1.0
    warmup = max(MOM_LOOKBACK, credit_lookback) + 2
    out = np.zeros(len(values), dtype=float)
    for i in range(len(values)):
        if i < warmup:
            out[i] = rets[i, 4]
            continue
        credit_now = values[i - 1, 2] / values[i - 1, 3]
        credit_then = values[i - credit_lookback - 1, 2] / values[i - credit_lookback - 1, 3]
        credit_mom = credit_now / credit_then - 1.0
        asset_mom = values[i - 1, asset_idx] / values[i - MOM_LOOKBACK - 1, asset_idx] - 1.0
        out[i] = rets[i, asset_idx] if credit_mom > 0.0 and asset_mom > 0.0 else rets[i, 4]
    return pd.Series(out[warmup:], index=prices.index[warmup:])


def benchmark_returns(prices: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return prices[str(config["asset"])].pct_change().fillna(0.0).loc[index]


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
    observed = metrics(strategy_returns(prices, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_prices(prices, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    warmup = max(MOM_LOOKBACK, int(config["credit_lookback"])) + 5
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
    stats = []
    for _ in range(n):
        perm_returns, _ = wf_returns_fixed(permuted_prices(prices, rng, start=1008), config)
        stats.append(metrics(perm_returns).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=1615)
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
            "artifacts": ["PRE_REG.md", "run_iter016.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered SPY/QQQ/HYG/IEF/SHV data unavailable: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(prices, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bench = benchmark_returns(prices, config, r.index)
        rows.append({
            "config": config["name"],
            **config,
            **m.__dict__,
            "benchmark_sharpe": metrics(bench).sharpe,
            "benchmark_cagr": metrics(bench).cagr,
        })

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=1613)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=1614)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    bench_returns = benchmark_returns(prices, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_start = int(len(best_returns) * 0.8)
    oos_return = float((1.0 + best_returns.iloc[oos_start:]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_returns = strategy_returns_numpy(prices, config=best_config).loc[best_returns.index]
    numpy_cagr = metrics(numpy_returns).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    data_end = prices.index.max()
    data_stale = bool(data_end < STALE_BLOCK_DATE)
    positive_wf = int(sum(1 for w in wf_windows if w["total_return"] > 0.0))
    wf_required = 6 if len(wf_windows) >= 8 else len(wf_windows)

    gates = {
        "data_not_stale": {"pass": not data_stale, "data_end": str(data_end.date()), "threshold": str(STALE_BLOCK_DATE.date())},
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
    status = "winner" if winner else "fail"
    kill_switches = [name for name, gate in gates.items() if not gate["pass"]]

    pd.DataFrame(rows).to_csv(OUT_DIR / "config_metrics.csv", index=False)
    pd.DataFrame(wf_windows).to_csv(OUT_DIR / "wf_windows.csv", index=False)
    write_results({
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is_mcpt": 200, "wf_mcpt": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": best_metrics.__dict__,
        "benchmark": {"pre_registered_benchmark": bench_metrics.__dict__},
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_iter016.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Credit-risk appetite filter tested with lagged HYG/IEF ratio momentum plus own-asset momentum; no post-result parameter additions.",
    })


if __name__ == "__main__":
    main()
