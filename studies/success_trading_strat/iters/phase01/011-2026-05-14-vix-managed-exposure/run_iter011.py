"""Iteration 011 runner: VIX-managed equity exposure.

This iteration pivots away from local price-only ETF rules. It scales SPY/QQQ
exposure inversely to previous-month VIX, following the VIX-managed portfolio
mechanism `[paper.bozovic_2024_vix_managed, §methodology]`. Signals are shifted
one bar to avoid same-close lookahead `[advances_fin_ml, p.196-202]`; MCPT, PBO
and DSR remain hard anti-overfit controls `[testing_tuning, p.318-320]`,
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


ITERATION = "011-2026-05-14-vix-managed-exposure"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
VIX_PATH = ROOT / "data/phase3_7/vix/VIXCLS.parquet"
REQUIRED = ["SPY", "QQQ", "SHV"]
CUMULATIVE_TRIALS_AFTER = 32
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_vix15_w21", "asset": "SPY", "vix_window": 21, "vix_anchor": 15.0, "cap": 1.0},
    {"name": "spy_vix20_w21", "asset": "SPY", "vix_window": 21, "vix_anchor": 20.0, "cap": 1.0},
    {"name": "qqq_vix15_w21", "asset": "QQQ", "vix_window": 21, "vix_anchor": 15.0, "cap": 1.0},
    {"name": "qqq_vix20_w21", "asset": "QQQ", "vix_window": 21, "vix_anchor": 20.0, "cap": 1.0},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def _series_from_parquet(path: Path, ticker: str | None = None) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if isinstance(df, pd.Series):
        s = df
    else:
        if "date" in df.columns:
            df = df.set_index("date")
        if ticker and ticker in df.columns:
            col = ticker
        elif "adj_close" in df.columns:
            col = "adj_close"
        elif "close" in df.columns:
            col = "close"
        elif "value" in df.columns:
            col = "value"
        else:
            numeric = list(df.select_dtypes(include=["number"]).columns)
            if not numeric:
                raise ValueError(f"no numeric price/value column in {path}")
            col = str(numeric[0])
        s = df[col]
    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.to_datetime(s.index)
    return s.astype(float).sort_index()


def load_data() -> pd.DataFrame:
    frames: dict[str, pd.Series] = {}
    for ticker in REQUIRED:
        frames[ticker] = _series_from_parquet(PRICE_DIR / f"{ticker}.parquet", ticker).rename(ticker)
    frames["VIX"] = _series_from_parquet(VIX_PATH, "VIXCLS").rename("VIX")
    data = pd.concat(frames.values(), axis=1, join="inner").dropna()
    data = data.loc["2010-01-01":]
    data = data[data["VIX"] > 0.0]
    if data.empty or len(data) < 252 * 8:
        raise ValueError("insufficient common ETF/VIX history")
    return data


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


def vix_weight(data: pd.DataFrame, *, vix_window: int, vix_anchor: float, cap: float) -> pd.Series:
    vix_mean = data["VIX"].rolling(vix_window, min_periods=vix_window).mean()
    raw = (vix_anchor / vix_mean).clip(lower=0.0, upper=cap)
    return raw.shift(1).fillna(0.0)


def strategy_returns(data: pd.DataFrame, *, asset: str, vix_window: int, vix_anchor: float, cap: float) -> pd.Series:
    rets = data[[asset, "SHV"]].pct_change().fillna(0.0)
    weight = vix_weight(data, vix_window=vix_window, vix_anchor=vix_anchor, cap=cap)
    out = weight * rets[asset] + (1.0 - weight) * rets["SHV"]
    return out.iloc[vix_window + 1:]


def strategy_returns_numpy(data: pd.DataFrame, *, asset: str, vix_window: int, vix_anchor: float, cap: float) -> pd.Series:
    arr = data[[asset, "SHV", "VIX"]].to_numpy(dtype=float)
    weights = np.zeros(len(arr), dtype=float)
    for i in range(vix_window, len(arr)):
        mean_vix = float(np.mean(arr[i - vix_window:i, 2]))
        if mean_vix > 0.0:
            weights[i] = min(max(vix_anchor / mean_vix, 0.0), cap)
    rets = np.zeros((len(arr), 2), dtype=float)
    rets[1:] = arr[1:, :2] / arr[:-1, :2] - 1.0
    out = weights * rets[:, 0] + (1.0 - weights) * rets[:, 1]
    return pd.Series(out[vix_window + 1:], index=data.index[vix_window + 1:])


def returns_to_prices(first: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    rebuilt = (1.0 + returns).cumprod().mul(first, axis=1)
    first_row = first.to_frame().T
    first_row.index = [returns.index[0] - pd.Timedelta(days=1)]
    return pd.concat([first_row, rebuilt]).sort_index()


def permuted_data(data: pd.DataFrame, rng: np.random.Generator, start: int = 1) -> pd.DataFrame:
    returns = data[["SPY", "QQQ", "SHV", "VIX"]].pct_change().iloc[1:].copy()
    prefix = data.iloc[:start].copy()
    tail = returns.iloc[start - 1:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    new_returns = pd.concat([returns.iloc[: start - 1], shuffled]).sort_index()
    rebuilt = returns_to_prices(prefix.iloc[0], new_returns)
    return rebuilt.loc[data.index[0]:].reindex(data.index).ffill()


def mcpt_fixed_config(data: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(data, asset=config["asset"], vix_window=config["vix_window"], vix_anchor=config["vix_anchor"], cap=config["cap"])).sharpe
    stats = []
    for _ in range(n):
        perm = permuted_data(data, rng)
        stats.append(metrics(strategy_returns(perm, asset=config["asset"], vix_window=config["vix_window"], vix_anchor=config["vix_anchor"], cap=config["cap"])).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(data: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    vix_window = int(config["vix_window"])
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(data):
        test_data = data.iloc[start + train - vix_window - 5: start + train + test]
        r = strategy_returns(test_data, asset=config["asset"], vix_window=vix_window, vix_anchor=config["vix_anchor"], cap=config["cap"]).iloc[-test:]
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
    stats = []
    for _ in range(n):
        perm = permuted_data(data, rng, start=1008)
        perm_returns, _ = wf_returns_fixed(perm, config)
        stats.append(metrics(perm_returns).sharpe)
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=1011)
    means = samples.mean(axis=1)
    return float(np.quantile(means, 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_data()
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
            "artifacts": ["PRE_REG.md", "run_iter011.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered VIX/ETF data unavailable: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, asset=config["asset"], vix_window=config["vix_window"], vix_anchor=config["vix_anchor"], cap=config["cap"])
        config_returns[config["name"]] = r
        m = metrics(r)
        avg_exposure = float(vix_weight(data, vix_window=config["vix_window"], vix_anchor=config["vix_anchor"], cap=config["cap"]).loc[r.index].mean())
        rows.append({"config": config["name"], **config, **m.__dict__, "avg_exposure": avg_exposure})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]

    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)

    bench_rets = data[["SPY", "QQQ", "SHV"]].pct_change().fillna(0.0).loc[best_returns.index]
    asset_bench = bench_rets[best_config["asset"]]
    asset_metrics = metrics(asset_bench)
    shv_metrics = metrics(bench_rets["SHV"])

    is_mcpt = mcpt_fixed_config(data, best_config, n=200, seed=1101)
    wf_returns, wf_windows = wf_returns_fixed(data, best_config)
    wf_mcpt = wf_mcpt_fixed(data, best_config, n=100, seed=1102)
    oos = best_returns.iloc[int(len(best_returns) * 0.8):]
    fwd = best_returns.iloc[-63:]
    boot_low = bootstrap_ci_low(best_returns)

    numpy_returns = strategy_returns_numpy(data, asset=best_config["asset"], vix_window=best_config["vix_window"], vix_anchor=best_config["vix_anchor"], cap=best_config["cap"]).loc[best_returns.index]
    numpy_metrics = metrics(numpy_returns)
    cagr_delta = abs(float(ranked[0]["cagr"]) - numpy_metrics.cagr)

    gates_bool = {
        "economic_sharpe_vs_same_asset": bool(ranked[0]["sharpe"] > asset_metrics.sharpe),
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
            "data_start": str(data.index.min().date()),
            "data_end": str(data.index.max().date()),
            "n_observations": int(len(data)),
            "wf_total_return": float((1.0 + wf_returns).prod() - 1.0),
            "wf_positive_windows": int(sum(w["total_return"] > 0 for w in wf_windows)),
            "wf_n_windows": len(wf_windows),
            "oos_total_return": float((1.0 + oos).prod() - 1.0),
            "fwd_63d_total_return": float((1.0 + fwd).prod() - 1.0),
            "bootstrap_mean_daily_ci_0_001": boot_low,
            "cross_lib_cagr_delta": cagr_delta,
        },
        "benchmark": {
            "same_asset_buy_hold": {"asset": best_config["asset"], **asset_metrics.__dict__},
            "shv": shv_metrics.__dict__,
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
        "artifacts": ["PRE_REG.md", "run_iter011.py", "RESULTS.json", "SUMMARY.md"],
        "notes": "VIX-managed exposure tested with one-bar-lagged previous-month VIX mean; MCPT permutes joint daily rows for ETF and VIX changes.",
    })


if __name__ == "__main__":
    main()
