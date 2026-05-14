"""Iteration 025 runner: current-constituent market breadth proxy.

Breadth is an advance/decline-style confirmation source distinct from the prior
price, volume, VIX, yield, seasonality and crypto families
`[trading_systems_methods, p.548-549]`. The current-constituent proxy has known
survivorship bias, so even a numeric pass cannot become a winner
`[trading_systems_methods, p.941]`.
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


ITERATION = "025-2026-05-14-market-breadth-proxy"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
CUMULATIVE_TRIALS_AFTER = 88
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
REQUIRED = ["SPY", "QQQ", "SHV"]
BREADTH_NAMES = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "AVGO", "TSLA", "COST", "NFLX",
    "AMD", "ADBE", "PEP", "CSCO", "TMUS", "INTU", "AMAT", "TXN", "QCOM", "AMGN",
    "HON", "ISRG", "BKNG", "VRTX", "LRCX", "MU", "ADI", "ADP", "PANW", "REGN",
]
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_breadth_sma63_gt55", "asset": "SPY", "lookback": 63, "threshold": 0.55},
    {"name": "qqq_breadth_sma63_gt55", "asset": "QQQ", "lookback": 63, "threshold": 0.55},
    {"name": "spy_breadth_sma126_gt55", "asset": "SPY", "lookback": 126, "threshold": 0.55},
    {"name": "qqq_breadth_sma126_gt55", "asset": "QQQ", "lookback": 126, "threshold": 0.55},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_close(ticker: str) -> pd.Series:
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
    if "adj_close" not in df.columns:
        raise ValueError(f"{ticker} missing adj_close")
    return df["adj_close"].astype(float).rename(ticker)


def load_data() -> tuple[pd.DataFrame, list[str]]:
    required = [load_close(ticker) for ticker in REQUIRED]
    available: list[pd.Series] = []
    names: list[str] = []
    for ticker in BREADTH_NAMES:
        try:
            s = load_close(ticker)
        except Exception:  # noqa: BLE001 - proxy may skip unavailable current members.
            continue
        available.append(s)
        names.append(ticker)
    if len(names) < 20:
        raise ValueError(f"only {len(names)} breadth names available; need >=20")
    data = pd.concat(required + available, axis=1, join="inner").dropna().loc["2010-01-01":]
    if data.empty or len(data) < 252 * 5 + 126:
        raise ValueError("insufficient common daily history")
    if not (data > 0.0).all().all():
        raise ValueError("non-positive adjusted close value")
    return data, names


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


def breadth_signal(data: pd.DataFrame, names: list[str], lookback: int, threshold: float) -> pd.Series:
    breadth = (data[names] > data[names].rolling(lookback).mean()).mean(axis=1)
    return (breadth >= threshold).shift(1).fillna(False).astype(bool)


def strategy_returns(data: pd.DataFrame, names: list[str], config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    risk_on = breadth_signal(data, names, int(config["lookback"]), float(config["threshold"]))
    asset_r = data[asset].pct_change().fillna(0.0)
    shv_r = data["SHV"].pct_change().fillna(0.0)
    return pd.Series(np.where(risk_on, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def strategy_returns_numpy(data: pd.DataFrame, names: list[str], config: dict[str, Any]) -> pd.Series:
    arr = data[[str(config["asset"]), "SHV", *names]].to_numpy(dtype=float)
    asset = arr[:, 0]
    shv = arr[:, 1]
    members = arr[:, 2:]
    lookback = int(config["lookback"])
    threshold = float(config["threshold"])
    sma = pd.DataFrame(members).rolling(lookback).mean().to_numpy(dtype=float)
    breadth = np.nanmean(members > sma, axis=1)
    risk_on = np.r_[False, (breadth >= threshold)[:-1]]
    asset_r = np.r_[0.0, asset[1:] / asset[:-1] - 1.0]
    shv_r = np.r_[0.0, shv[1:] / shv[:-1] - 1.0]
    return pd.Series(np.where(risk_on, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def benchmark_returns(data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return data[str(config["asset"])].pct_change().fillna(0.0).loc[index]


def permuted_data(data: pd.DataFrame, rng: np.random.Generator, start: int = 0) -> pd.DataFrame:
    returns = data.pct_change().fillna(0.0)
    tail_pos = np.arange(max(start, 1), len(data))
    shuffled_pos = tail_pos[rng.permutation(len(tail_pos))]
    prefix = data.iloc[:start].copy()
    base = data.iloc[[0]].copy() if prefix.empty else prefix.iloc[[-1]].copy()
    values = [base.iloc[0].to_numpy(dtype=float)]
    for row in returns.iloc[shuffled_pos].to_numpy(dtype=float):
        values.append(values[-1] * (1.0 + row))
    idx = data.index if prefix.empty else data.index[start - 1:]
    rebuilt = pd.DataFrame(values, index=idx, columns=data.columns)
    if prefix.empty:
        return rebuilt
    return pd.concat([data.iloc[: start - 1], rebuilt])


def mcpt_fixed_config(data: pd.DataFrame, names: list[str], config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(data, names, config)).sharpe
    stats = [metrics(strategy_returns(permuted_data(data, rng), names, config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(data: pd.DataFrame, names: list[str], config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(data):
        test_data = data.iloc[start + train: start + train + test]
        r = strategy_returns(test_data, names, config).iloc[-test + 1:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(data: pd.DataFrame, names: list[str], config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed_returns, windows = wf_returns_fixed(data, names, config)
    observed = metrics(observed_returns).sharpe
    stats = [metrics(wf_returns_fixed(permuted_data(data, rng, start=1008), names, config)[0]).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2505)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data, names = load_data()
    except Exception as exc:  # noqa: BLE001
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
            "kill_switches": ["breadth_proxy_data_unavailable"],
            "artifacts": ["PRE_REG.md", "run_iter025.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, names, config)
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
    is_mcpt = mcpt_fixed_config(data, names, best_config, n=200, seed=2503)
    wf_mcpt = wf_mcpt_fixed(data, names, best_config, n=100, seed=2504)
    wf_returns, wf_windows = wf_returns_fixed(data, names, best_config)
    bench_returns = benchmark_returns(data, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(data, names, best_config).loc[best_returns.index]).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    positive_wf = int(sum(1 for w in wf_windows if w["total_return"] > 0.0))
    wf_required = 6 if len(wf_windows) >= 8 else len(wf_windows)
    data_end = data.index.max()
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
        "survivorship_bias_caveat": {"pass": False, "reason": "current-constituent proxy list is not point-in-time"},
    }
    numeric_winner = bool(all(g["pass"] for k, g in gates.items() if k != "survivorship_bias_caveat"))
    status = "promising_not_validated" if numeric_winner else "fail"
    pd.DataFrame(rows).to_csv(OUT_DIR / "config_metrics.csv", index=False)
    pd.DataFrame(wf_windows).to_csv(OUT_DIR / "wf_windows.csv", index=False)
    (OUT_DIR / "breadth_names.json").write_text(json.dumps(names, indent=2) + "\n")
    write_results({
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "mcpt_reps": {"is": 200, "wf": 100},
        "best_config": best_name,
        "winner": False,
        "metrics": {**best_metrics.__dict__, "oos_return": oos_return, "fwd_63d_return": fwd_63d, "bootstrap_999_mean_daily_low": boot_low},
        "benchmark": bench_metrics.__dict__,
        "gates": gates,
        "kill_switches": [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter025.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv", "breadth_names.json"],
        "notes": "Current-constituent breadth proxy; survivorship caveat blocks winner even if numeric gates pass.",
    })


if __name__ == "__main__":
    main()
