"""Iteration 004 runner: cross-sectional ETF momentum.

The tested family uses relative-strength momentum normalized by realized
volatility, with monthly rebalancing and next-day execution to avoid same-close
lookahead `[stocks_on_the_move, p.76-77]`, `[systematic_trading, p.185-188]`,
`[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from market_lab.backtest.validation.bootstrap import stationary_bootstrap_trades
from market_lab.backtest.validation.dsr import dsr, sharpe_annualized
from market_lab.backtest.validation.pbo import pbo


ITERATION = "004-2026-05-14-cross-sectional-etf-momentum"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
RISK_ASSETS = ["SPY", "QQQ", "IWM", "TLT", "GLD"]
DEFENSIVE = "SHV"
CONFIGS = [
    {"name": "mom63_top1", "lookback": 63, "top_k": 1},
    {"name": "mom63_top2", "lookback": 63, "top_k": 2},
    {"name": "mom126_top1", "lookback": 126, "top_k": 1},
    {"name": "mom126_top2", "lookback": 126, "top_k": 2},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_prices() -> pd.DataFrame:
    frames: dict[str, pd.Series] = {}
    for ticker in [*RISK_ASSETS, DEFENSIVE]:
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
    prices = prices.loc["2008-01-01":]
    if prices.empty or len(prices) < 252 * 5:
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


def strategy_returns(prices: pd.DataFrame, *, lookback: int, top_k: int) -> pd.Series:
    risk_prices = prices[RISK_ASSETS]
    risk_rets = risk_prices.pct_change()
    realized_vol = risk_rets.rolling(lookback).std() * np.sqrt(252.0)
    scores = risk_prices.pct_change(lookback) / realized_vol
    rebalance_dates = scores.dropna().resample("ME").last().index
    rebalance_weights = pd.DataFrame(0.0, index=rebalance_dates, columns=prices.columns)
    for dt in rebalance_dates:
        if dt not in scores.index:
            continue
        score = scores.loc[dt].dropna()
        if score.empty:
            continue
        if float(score.mean()) <= 0.0:
            rebalance_weights.loc[dt, DEFENSIVE] = 1.0
            continue
        selected = list(score.sort_values(ascending=False).head(top_k).index)
        for ticker in selected:
            rebalance_weights.loc[dt, ticker] = 1.0 / len(selected)
    weights = rebalance_weights.reindex(prices.index).ffill().fillna(0.0)
    daily_returns = prices.pct_change().fillna(0.0)
    # One-bar lag ensures the month-end signal is tradable only on the next bar.
    out = (weights.shift(1).fillna(0.0) * daily_returns).sum(axis=1)
    return out.loc[scores.dropna().index[0]:]


def benchmark_returns(prices: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    rets = prices.pct_change().fillna(0.0)
    equal_weight = rets[RISK_ASSETS].mean(axis=1)
    return equal_weight, rets["SPY"]


def returns_to_prices(first: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    prices = (1.0 + returns).cumprod().mul(first, axis=1)
    first_row = first.to_frame().T
    first_row.index = [returns.index[0] - pd.Timedelta(days=1)]
    return pd.concat([first_row, prices]).sort_index()


def permuted_prices(prices: pd.DataFrame, rng: np.random.Generator, start: int = 1) -> pd.DataFrame:
    rets = prices.pct_change().iloc[1:].copy()
    prefix = prices.iloc[:start].copy()
    tail = rets.iloc[start - 1:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    new_rets = pd.concat([rets.iloc[: start - 1], shuffled]).sort_index()
    rebuilt = returns_to_prices(prefix.iloc[0], new_rets)
    return rebuilt.loc[prices.index[0]:].reindex(prices.index).ffill()


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, int | str], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(prices, lookback=int(config["lookback"]), top_k=int(config["top_k"]))).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng)
        stats.append(metrics(strategy_returns(perm, lookback=int(config["lookback"]), top_k=int(config["top_k"]))).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, int | str], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - int(config["lookback"]): start + train + test]
        r = strategy_returns(test_prices, lookback=int(config["lookback"]), top_k=int(config["top_k"]))
        r = r.iloc[-test:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(prices: pd.DataFrame, config: dict[str, int | str], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed_returns, windows = wf_returns_fixed(prices, config)
    observed = metrics(observed_returns).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng, start=1008)
        perm_returns, _ = wf_returns_fixed(perm, config)
        stats.append(metrics(perm_returns).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {
        "observed": observed,
        "p_value": float(np.mean(arr >= observed)),
        "n_permutations": n,
        "n_windows": len(windows),
    }


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=404)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def main() -> None:
    prices = load_prices()
    config_returns: dict[str, pd.Series] = {}
    rows = []
    for config in CONFIGS:
        r = strategy_returns(prices, lookback=int(config["lookback"]), top_k=int(config["top_k"]))
        config_returns[str(config["name"])] = r
        m = metrics(r)
        rows.append({"config": config["name"], **config, **m.__dict__})
    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=8)
    ew_bench, spy_bench = benchmark_returns(prices.loc[best_returns.index])
    bench_metrics = metrics(ew_bench.loc[best_returns.index])
    spy_metrics = metrics(spy_bench.loc[best_returns.index])

    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=401)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=402)
    oos = best_returns.iloc[int(len(best_returns) * 0.8):]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)

    gates = {
        "economic_sharpe_vs_equal_weight": bool(ranked[0]["sharpe"] > bench_metrics.sharpe),
        "economic_mdd_vs_equal_weight": bool(ranked[0]["mdd"] >= bench_metrics.mdd),
        "is_mcpt": bool(is_mcpt["p_value"] <= 0.01),
        "wf_mcpt": bool(wf_mcpt["p_value"] <= 0.05),
        "pbo": bool(float(pbo_res.pbo) < 0.5),
        "dsr": bool(float(dsr_res.p_value) < 0.05),
        "wf_windows": bool(len(wf_windows) >= 8 and sum(w["total_return"] > 0 for w in wf_windows) >= 6),
        "oos": bool((1.0 + oos).prod() - 1.0 > 0.0),
        "fwd_stress": bool((1.0 + fwd).prod() - 1.0 > 0.0),
        "bootstrap": bool(boot_low > 0.0),
        "cross_lib": False,
    }
    winner = all(gates.values())
    status = "winner" if winner else "fail"
    kill_switches = [name for name, ok in gates.items() if not ok]

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": {
            "configs": rows,
            "best": ranked[0],
            "pbo": float(pbo_res.pbo),
            "pbo_combinations": int(pbo_res.n_combinations),
            "dsr_p_value": float(dsr_res.p_value),
            "dsr_observed_sharpe_periodic": float(dsr_res.observed_sharpe),
            "is_mcpt": is_mcpt,
            "wf_mcpt": wf_mcpt,
            "wf_positive_windows": int(sum(w["total_return"] > 0 for w in wf_windows)),
            "wf_total_windows": int(len(wf_windows)),
            "oos_total_return": float((1.0 + oos).prod() - 1.0),
            "fwd_63d_total_return": float((1.0 + fwd).prod() - 1.0),
            "bootstrap_mean_ci_0_1pct_low": boot_low,
            "date_start": str(best_returns.index.min().date()),
            "date_end": str(best_returns.index.max().date()),
        },
        "benchmark": {"equal_weight": bench_metrics.__dict__, "spy": spy_metrics.__dict__},
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_iter004.py", "RESULTS.json", "SUMMARY.md"],
        "notes": "Monthly cross-sectional ETF momentum failed required gates; cross-lib was not computed by design, so winner promotion was impossible.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    pd.DataFrame(rows).to_csv(OUT_DIR / "config_metrics.csv", index=False)
    pd.DataFrame(wf_windows).to_csv(OUT_DIR / "wf_windows.csv", index=False)


if __name__ == "__main__":
    main()
