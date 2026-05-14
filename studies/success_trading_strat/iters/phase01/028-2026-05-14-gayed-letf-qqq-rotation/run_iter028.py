"""Iteration 028 runner: Gayed-style QQQ LETF rotation.

The family uses QQQ as a lagged volatility/regime signal for QLD/TQQQ exposure,
with SHV as the off-leg. The 200-day MA and sparse volatility-control variant are
pre-registered from the leverage-regime thesis, not optimized after validation
`[leverage_for_the_long_run, p.13]`, `[leverage_for_the_long_run, p.16-17]`,
`[trading_systems_methods, p.1085-1091]`. Promotion remains hard-gated by MCPT,
PBO and DSR `[testing_tuning, p.318-320]`, `[advances_fin_ml, p.208-211]`.
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


ITERATION = "028-2026-05-14-gayed-letf-qqq-rotation"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
CUMULATIVE_TRIALS_AFTER = 96
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
START_DATE = "2010-02-12"
REQUIRED = ["QQQ", "QLD", "TQQQ", "SHV"]
CONFIGS: list[dict[str, Any]] = [
    {"name": "qld_qqq_sma200", "risk_asset": "QLD", "ma": 200, "rv_filter": False},
    {"name": "tqqq_qqq_sma200", "risk_asset": "TQQQ", "ma": 200, "rv_filter": False},
    {"name": "qld_qqq_sma200_rv70", "risk_asset": "QLD", "ma": 200, "rv_filter": True},
    {"name": "tqqq_qqq_sma200_rv70", "risk_asset": "TQQQ", "ma": 200, "rv_filter": True},
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


def load_data() -> pd.DataFrame:
    data = pd.concat([load_close(ticker) for ticker in REQUIRED], axis=1, join="inner").dropna().loc[START_DATE:]
    if data.empty or len(data) < 252 * 5 + 252:
        raise ValueError("insufficient common daily history")
    if not (data > 0.0).all().all():
        raise ValueError("non-positive adjusted close value")
    return data


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


def risk_on_signal(data: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    qqq = data["QQQ"]
    trend = qqq > qqq.rolling(int(config["ma"])).mean()
    if bool(config["rv_filter"]):
        rv21 = qqq.pct_change().rolling(21).std() * np.sqrt(252.0)
        rv_cap = rv21.rolling(252).quantile(0.70)
        trend = trend & (rv21 < rv_cap)
    return trend.shift(1).fillna(False).astype(bool)


def strategy_returns(data: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    risk_on = risk_on_signal(data, config)
    risk_r = data[str(config["risk_asset"])].pct_change().fillna(0.0)
    shv_r = data["SHV"].pct_change().fillna(0.0)
    return pd.Series(np.where(risk_on, risk_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def strategy_returns_numpy(data: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    arr = data[["QQQ", str(config["risk_asset"]), "SHV"]].to_numpy(dtype=float)
    qqq, risk_asset, shv = arr[:, 0], arr[:, 1], arr[:, 2]
    ma = int(config["ma"])
    sma = pd.Series(qqq).rolling(ma).mean().to_numpy(dtype=float)
    trend = qqq > sma
    if bool(config["rv_filter"]):
        qqq_r = pd.Series(qqq).pct_change()
        rv21 = qqq_r.rolling(21).std() * np.sqrt(252.0)
        rv_cap = rv21.rolling(252).quantile(0.70)
        trend = trend & (rv21.to_numpy(dtype=float) < rv_cap.to_numpy(dtype=float))
    risk_on = np.r_[False, trend[:-1]]
    risk_r = np.r_[0.0, risk_asset[1:] / risk_asset[:-1] - 1.0]
    shv_r = np.r_[0.0, shv[1:] / shv[:-1] - 1.0]
    return pd.Series(np.where(risk_on, risk_r, shv_r), index=data.index, name=str(config["name"])).iloc[1:]


def benchmark_returns(data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return data[str(config["risk_asset"])].pct_change().fillna(0.0).loc[index]


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


def mcpt_fixed_config(data: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(data, config)).sharpe
    stats = [metrics(strategy_returns(permuted_data(data, rng), config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(data: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(data):
        window_data = data.iloc[start: start + train + test]
        r = strategy_returns(window_data, config).iloc[-test + 1:]
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2805)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_data()
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
            "kill_switches": ["letf_rotation_data_unavailable"],
            "artifacts": ["PRE_REG.md", "run_iter028.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, config)
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
    is_mcpt = mcpt_fixed_config(data, best_config, n=200, seed=2803)
    wf_mcpt = wf_mcpt_fixed(data, best_config, n=100, seed=2804)
    wf_returns, wf_windows = wf_returns_fixed(data, best_config)
    bench_returns = benchmark_returns(data, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(data, best_config).loc[best_returns.index]).cagr
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
        "kill_switches": [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter028.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Gayed-style QQQ LETF rotation; no local tuning after validation.",
    })


if __name__ == "__main__":
    main()
