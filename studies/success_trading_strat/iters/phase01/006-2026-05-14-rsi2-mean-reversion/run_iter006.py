"""Iteration 006 runner: RSI(2) ETF mean reversion.

This family tests a short-horizon mean-reversion trigger rather than momentum or
volatility targeting. RSI thresholds are applied with a one-bar execution lag to
avoid look-ahead bias `[quant_trading_chan, p.51]`; the family remains subject to
MCPT, PBO and DSR promotion blocks `[testing_tuning, p.318-320]`,
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
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


ITERATION = "006-2026-05-14-rsi2-mean-reversion"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
ASSETS = ["SPY", "QQQ", "SHV"]
DEFENSIVE = "SHV"
RSI_PERIOD = 2
EXIT_RSI = 70.0
CUMULATIVE_TRIALS_AFTER = 16
CONFIGS = [
    {"name": "spy_rsi2_e5_x70", "asset": "SPY", "entry_rsi": 5.0, "exit_rsi": EXIT_RSI},
    {"name": "spy_rsi2_e10_x70", "asset": "SPY", "entry_rsi": 10.0, "exit_rsi": EXIT_RSI},
    {"name": "qqq_rsi2_e5_x70", "asset": "QQQ", "entry_rsi": 5.0, "exit_rsi": EXIT_RSI},
    {"name": "qqq_rsi2_e10_x70", "asset": "QQQ", "entry_rsi": 10.0, "exit_rsi": EXIT_RSI},
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


def rsi_wilder(close: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - (100.0 / (1.0 + rs))
    return out.fillna(50.0)


def strategy_returns(prices: pd.DataFrame, *, asset: str, entry_rsi: float, exit_rsi: float) -> pd.Series:
    rsi = rsi_wilder(prices[asset])
    close_position = pd.Series(0.0, index=prices.index)
    invested = False
    for dt, value in rsi.items():
        if invested and float(value) >= exit_rsi:
            invested = False
        elif not invested and float(value) <= entry_rsi:
            invested = True
        close_position.loc[dt] = 1.0 if invested else 0.0
    tradable_position = close_position.shift(1).fillna(0.0)
    daily_returns = prices.pct_change().fillna(0.0)
    out = tradable_position * daily_returns[asset] + (1.0 - tradable_position) * daily_returns[DEFENSIVE]
    return out.loc[prices.index[RSI_PERIOD + 1]:]


def benchmark_returns(prices: pd.DataFrame, best_asset: str, start_index: pd.Index) -> tuple[pd.Series, pd.Series]:
    rets = prices.pct_change().fillna(0.0)
    same_asset = rets[best_asset].loc[start_index]
    spy = rets["SPY"].loc[start_index]
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
        asset=str(config["asset"]),
        entry_rsi=float(config["entry_rsi"]),
        exit_rsi=float(config["exit_rsi"]),
    )).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_prices(prices, rng)
        stats.append(metrics(strategy_returns(
            perm,
            asset=str(config["asset"]),
            entry_rsi=float(config["entry_rsi"]),
            exit_rsi=float(config["exit_rsi"]),
        )).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(prices: pd.DataFrame, config: dict[str, object], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(prices):
        test_prices = prices.iloc[start + train - (RSI_PERIOD + 5): start + train + test]
        r = strategy_returns(
            test_prices,
            asset=str(config["asset"]),
            entry_rsi=float(config["entry_rsi"]),
            exit_rsi=float(config["exit_rsi"]),
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=606)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def main() -> None:
    prices = load_prices()
    config_returns: dict[str, pd.Series] = {}
    rows = []
    for config in CONFIGS:
        r = strategy_returns(
            prices,
            asset=str(config["asset"]),
            entry_rsi=float(config["entry_rsi"]),
            exit_rsi=float(config["exit_rsi"]),
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
    same_asset_bench, spy_bench = benchmark_returns(prices.loc[best_returns.index], str(best_config["asset"]), best_returns.index)
    same_asset_metrics = metrics(same_asset_bench)
    spy_metrics = metrics(spy_bench)

    is_mcpt = mcpt_fixed_config(prices, best_config, n=200, seed=601)
    wf_returns, wf_windows = wf_returns_fixed(prices, best_config)
    wf_mcpt = wf_mcpt_fixed(prices, best_config, n=100, seed=602)
    oos = best_returns.iloc[int(len(best_returns) * 0.8):]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)

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
        "benchmark": {"same_asset_buy_hold": same_asset_metrics.__dict__, "spy": spy_metrics.__dict__},
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_iter006.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "RSI(2) mean reversion tested as a mechanism pivot. Cross-lib was not computed by design, so winner promotion was impossible.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    pd.DataFrame(rows).to_csv(OUT_DIR / "config_metrics.csv", index=False)
    pd.DataFrame(wf_windows).to_csv(OUT_DIR / "wf_windows.csv", index=False)


if __name__ == "__main__":
    main()
