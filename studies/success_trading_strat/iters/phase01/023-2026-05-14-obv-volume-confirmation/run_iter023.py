"""Iteration 023 runner: OBV volume-confirmation timing.

OBV is a signed-volume accumulation indicator; this runner tests whether lagged
accumulation/distribution pressure adds timing information beyond price-only
smoothers while preserving MCPT/PBO/DSR hard controls
`[trading_systems_methods, p.537]`, `[testing_tuning, p.318-320]`,
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


ITERATION = "023-2026-05-14-obv-volume-confirmation"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "SHV"]
CUMULATIVE_TRIALS_AFTER = 80
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_obv21", "asset": "SPY", "obv_lookback": 21, "price_filter": False},
    {"name": "qqq_obv21", "asset": "QQQ", "obv_lookback": 21, "price_filter": False},
    {"name": "spy_obv63_price63", "asset": "SPY", "obv_lookback": 63, "price_filter": True},
    {"name": "qqq_obv63_price63", "asset": "QQQ", "obv_lookback": 63, "price_filter": True},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def load_ticker(ticker: str) -> pd.DataFrame:
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
    required_cols = ["adj_close"] if ticker == "SHV" else ["adj_close", "volume"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"{ticker} missing columns: {missing}")
    out = df[required_cols].astype(float).sort_index()
    out = out[~out.index.duplicated(keep="last")]
    return out.rename(columns={col: f"{ticker}_{col}" for col in out.columns})


def load_data() -> pd.DataFrame:
    data = pd.concat([load_ticker(t) for t in REQUIRED], axis=1, join="inner").dropna()
    data = data.loc["2010-01-01":]
    price_cols = [col for col in data.columns if col.endswith("adj_close")]
    if data.empty or len(data) < 252 * 5 + 63:
        raise ValueError("insufficient common daily history")
    if not (data[price_cols] > 0.0).all().all():
        raise ValueError("non-positive adjusted close values")
    if not (data[["SPY_volume", "QQQ_volume"]] >= 0.0).all().all():
        raise ValueError("negative risk-asset volume values")
    return data


def adjusted_close(data: pd.DataFrame, ticker: str) -> pd.Series:
    return data[f"{ticker}_adj_close"].rename(ticker)


def on_balance_volume(data: pd.DataFrame, ticker: str) -> pd.Series:
    price = adjusted_close(data, ticker)
    volume = data[f"{ticker}_volume"]
    signed_volume = np.sign(price.diff().fillna(0.0)) * volume
    return signed_volume.cumsum().rename(f"{ticker}_obv")


def signal_for_asset(data: pd.DataFrame, asset: str, obv_lookback: int, price_filter: bool) -> pd.Series:
    price = adjusted_close(data, asset)
    obv_delta = on_balance_volume(data, asset).diff(obv_lookback)
    signal = obv_delta > 0.0
    if price_filter:
        signal = signal & (price.pct_change(63) > 0.0)
    return signal.shift(1).fillna(False).astype(bool)


def strategy_returns(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    asset_r = adjusted_close(data, asset).pct_change().fillna(0.0)
    shv_r = adjusted_close(data, "SHV").pct_change().fillna(0.0)
    risk_on = signal_for_asset(data, asset, int(config["obv_lookback"]), bool(config["price_filter"]))
    return pd.Series(np.where(risk_on, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def strategy_returns_numpy(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    arr = data[[f"{asset}_adj_close", f"{asset}_volume", "SHV_adj_close"]].to_numpy(dtype=float)
    price = arr[:, 0]
    volume = arr[:, 1]
    shv = arr[:, 2]
    signed_volume = np.sign(np.r_[0.0, np.diff(price)]) * volume
    obv = np.cumsum(signed_volume)
    lookback = int(config["obv_lookback"])
    obv_delta = np.full(len(obv), np.nan, dtype=float)
    obv_delta[lookback:] = obv[lookback:] - obv[:-lookback]
    signal = obv_delta > 0.0
    if bool(config["price_filter"]):
        price_mom = np.full(len(price), np.nan, dtype=float)
        price_mom[63:] = price[63:] / price[:-63] - 1.0
        signal = signal & (price_mom > 0.0)
    signal = np.r_[False, signal[:-1]]
    asset_r = np.r_[0.0, price[1:] / price[:-1] - 1.0]
    shv_r = np.r_[0.0, shv[1:] / shv[:-1] - 1.0]
    return pd.Series(np.where(signal, asset_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def benchmark_returns(data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return adjusted_close(data, str(config["asset"])).pct_change().fillna(0.0).loc[index]


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


def permuted_data(data: pd.DataFrame, rng: np.random.Generator, start: int = 0) -> pd.DataFrame:
    returns = data[["SPY_adj_close", "QQQ_adj_close", "SHV_adj_close"]].pct_change().fillna(0.0)
    volume = data[["SPY_volume", "QQQ_volume"]]
    tail_pos = np.arange(max(start, 1), len(data))
    shuffled_pos = tail_pos[rng.permutation(len(tail_pos))]
    prefix = data.iloc[:start].copy()
    base = data.iloc[[0]].copy() if prefix.empty else prefix.iloc[[-1]].copy()
    price_values = [base[["SPY_adj_close", "QQQ_adj_close", "SHV_adj_close"]].iloc[0].to_numpy(dtype=float)]
    for row in returns.iloc[shuffled_pos].to_numpy(dtype=float):
        price_values.append(price_values[-1] * (1.0 + row))
    idx = data.index if prefix.empty else data.index[start - 1:]
    rebuilt = pd.DataFrame(price_values, index=idx, columns=["SPY_adj_close", "QQQ_adj_close", "SHV_adj_close"])
    volume_pos = np.r_[start - 1 if start else 0, shuffled_pos]
    rebuilt[["SPY_volume", "QQQ_volume"]] = volume.iloc[volume_pos].to_numpy(dtype=float)
    if prefix.empty:
        return rebuilt[data.columns]
    return pd.concat([data.iloc[: start - 1], rebuilt[data.columns]])


def mcpt_fixed_config(data: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(data, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_data(data, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(data: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(data):
        test_data = data.iloc[start + train: start + train + test]
        r = strategy_returns(test_data, config=config).iloc[-test + 1:]
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
    stats = [metrics(wf_returns_fixed(permuted_data(data, rng, start=1008), config)[0]).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2305)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_data()
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
            "kill_switches": ["required_obv_volume_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter023.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, config=config)
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
    is_mcpt = mcpt_fixed_config(data, best_config, n=200, seed=2303)
    wf_mcpt = wf_mcpt_fixed(data, best_config, n=100, seed=2304)
    wf_returns, wf_windows = wf_returns_fixed(data, best_config)
    bench_returns = benchmark_returns(data, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(data, config=best_config).loc[best_returns.index]).cagr
    cagr_delta_pp = abs(numpy_cagr - best_metrics.cagr) * 100.0
    data_end = data.index.max()
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
        "artifacts": ["PRE_REG.md", "run_iter023.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "OBV volume-confirmation family with one-bar lag; no deployment authorization.",
    })


if __name__ == "__main__":
    main()
