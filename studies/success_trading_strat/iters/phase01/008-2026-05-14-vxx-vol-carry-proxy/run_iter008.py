"""Iteration 008 runner: volatility-carry proxy via VXX decay filter.

This is a pre-registered continuation of the blocked volatility-carry mechanism,
using confirmed-available `VXX` data rather than substituting inside iter 007.
Carry premia can be negative-skewed, so promotion remains blocked unless MCPT,
PBO and DSR pass `[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`,
`[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
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


ITERATION = "008-2026-05-14-vxx-vol-carry-proxy"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
ASSETS = ["SPY", "QQQ", "SHV", "VXX"]
DEFENSIVE = "SHV"
CUMULATIVE_TRIALS_AFTER = 20
CONFIGS = [
    {"name": "vxx_neg21_spy", "risk_asset": "SPY", "signal_asset": "VXX", "lookback": 21},
    {"name": "vxx_neg63_spy", "risk_asset": "SPY", "signal_asset": "VXX", "lookback": 63},
    {"name": "vxx_neg63_qqq", "risk_asset": "QQQ", "signal_asset": "VXX", "lookback": 63},
    {"name": "vxx_neg126_spy", "risk_asset": "SPY", "signal_asset": "VXX", "lookback": 126},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_prices() -> pd.DataFrame:
    frames: dict[str, pd.Series] = {}
    for ticker in ASSETS:
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
    prices = prices.loc["2012-01-01":]
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


def strategy_returns(prices: pd.DataFrame, *, risk_asset: str, signal_asset: str, lookback: int) -> pd.Series:
    daily_returns = prices.pct_change().fillna(0.0)
    trailing_signal_return = prices[signal_asset].pct_change(lookback)
    close_position = (trailing_signal_return < 0.0).astype(float)
    tradable_position = close_position.shift(1).fillna(0.0)
    out = tradable_position * daily_returns[risk_asset] + (1.0 - tradable_position) * daily_returns[DEFENSIVE]
    return out.loc[prices.index[lookback + 1:]]


def strategy_returns_numpy(prices: pd.DataFrame, *, risk_asset: str, signal_asset: str, lookback: int) -> pd.Series:
    values = prices[[risk_asset, signal_asset, DEFENSIVE]].to_numpy(dtype=float)
    risk = values[:, 0]
    signal = values[:, 1]
    defensive = values[:, 2]
    risk_ret = np.zeros_like(risk)
    def_ret = np.zeros_like(defensive)
    risk_ret[1:] = risk[1:] / risk[:-1] - 1.0
    def_ret[1:] = defensive[1:] / defensive[:-1] - 1.0
    pos = np.zeros_like(signal)
    signal_ret = signal[lookback:] / signal[:-lookback] - 1.0
    pos[lookback:] = (signal_ret < 0.0).astype(float)
    tradable = np.roll(pos, 1)
    tradable[0] = 0.0
    out = tradable * risk_ret + (1.0 - tradable) * def_ret
    return pd.Series(out[lookback + 1:], index=prices.index[lookback + 1:])


def benchmark_returns(prices: pd.DataFrame, risk_asset: str, index: pd.Index) -> tuple[pd.Series, pd.Series]:
    rets = prices.pct_change().fillna(0.0)
    same_asset = rets[risk_asset].loc[index]
    spy = rets["SPY"].loc[index]
    return same_asset, spy


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


def mcpt_fixed_config(prices: pd.DataFrame, config: dict[str, object], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(
        prices,
        risk_asset=str(config["risk_asset"]),
        signal_asset=str(config["signal_asset"]),
        lookback=int(config["lookback"]),
    )).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng)
        stats.append(metrics(strategy_returns(
            perm,
            risk_asset=str(config["risk_asset"]),
            signal_asset=str(config["signal_asset"]),
            lookback=int(config["lookback"]),
        )).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, object], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    lookback = int(config["lookback"])
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - lookback - 2: start + train + test]
        r = strategy_returns(
            test_prices,
            risk_asset=str(config["risk_asset"]),
            signal_asset=str(config["signal_asset"]),
            lookback=lookback,
        ).iloc[-test:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(prices: pd.DataFrame, config: dict[str, object], n: int, seed: int) -> dict[str, float | int]:
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=808)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def main() -> None:
    try:
        prices = load_prices()
    except (FileNotFoundError, ValueError) as exc:
        results = {
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
            "artifacts": ["PRE_REG.md", "run_iter008.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered VXX signal data unavailable: {exc}.",
        }
        (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        return

    config_returns: dict[str, pd.Series] = {}
    rows = []
    for config in CONFIGS:
        r = strategy_returns(
            prices,
            risk_asset=str(config["risk_asset"]),
            signal_asset=str(config["signal_asset"]),
            lookback=int(config["lookback"]),
        )
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
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    same_asset_bench, spy_bench = benchmark_returns(prices.loc[best_returns.index], str(best_config["risk_asset"]), best_returns.index)
    same_asset_metrics = metrics(same_asset_bench)
    spy_metrics = metrics(spy_bench)

    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=801)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=802)
    oos = best_returns.iloc[int(len(best_returns) * 0.8):]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)

    numpy_returns = strategy_returns_numpy(
        prices,
        risk_asset=str(best_config["risk_asset"]),
        signal_asset=str(best_config["signal_asset"]),
        lookback=int(best_config["lookback"]),
    ).loc[best_returns.index]
    numpy_metrics = metrics(numpy_returns)
    cagr_delta = abs(float(ranked[0]["cagr"]) - numpy_metrics.cagr)

    gates = {
        "economic_sharpe_vs_same_asset": bool(ranked[0]["sharpe"] > same_asset_metrics.sharpe),
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
            "same_asset": same_asset_metrics.__dict__,
            "spy": spy_metrics.__dict__,
        },
        "gates": {
            **gates,
            "pbo_value": float(pbo_res.pbo),
            "pbo_combinations": int(pbo_res.n_combinations),
            "dsr_p_value": float(dsr_res.p_value),
            "dsr_observed_sharpe_periodic": float(dsr_res.observed_sharpe),
            "dsr_benchmark_sharpe_periodic": float(dsr_res.benchmark_sharpe),
            "is_mcpt": {**is_mcpt, "pass": gates["is_mcpt"]},
            "wf_mcpt": {**wf_mcpt, "pass": gates["wf_mcpt"]},
            "wf_windows": {"pass": gates["wf_windows"], "windows": wf_windows},
            "oos": {"pass": gates["oos"], "total_return": float((1.0 + oos).prod() - 1.0)},
            "fwd_stress": {"pass": gates["fwd_stress"], "total_return": float((1.0 + fwd).prod() - 1.0)},
            "bootstrap": {"pass": gates["bootstrap"], "mean_daily_ci_0_001": boot_low},
            "cross_lib": {"pass": gates["cross_lib"], "numpy_cagr": numpy_metrics.cagr, "delta": cagr_delta},
        },
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_iter008.py", "RESULTS.json", "SUMMARY.md"],
        "notes": "VXX volatility-carry proxy tested with one-bar lag. Verdict cannot promote if any hard gate fails.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
