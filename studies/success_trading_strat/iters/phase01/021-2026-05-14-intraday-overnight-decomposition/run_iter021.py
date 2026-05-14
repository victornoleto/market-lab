"""Iteration 021 runner: intraday/overnight return decomposition.

This daily-OHLC proxy tests whether the close-to-open or open-to-close return
component is a distinct source of edge in liquid ETFs. It is motivated by
intraday momentum evidence, but remains suspect unless it clears MCPT, PBO and
DSR `[paper.zarattini_2024_intraday_spy, §methodology]`,
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


ITERATION = "021-2026-05-14-intraday-overnight-decomposition"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "QQQ", "SHV"]
CUMULATIVE_TRIALS_AFTER = 72
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_close_to_open", "asset": "SPY", "leg": "close_to_open"},
    {"name": "qqq_close_to_open", "asset": "QQQ", "leg": "close_to_open"},
    {"name": "spy_open_to_close", "asset": "SPY", "leg": "open_to_close"},
    {"name": "qqq_open_to_close", "asset": "QQQ", "leg": "open_to_close"},
]


@dataclass(frozen=True)
class Metrics:
    cagr: float
    sharpe: float
    mdd: float
    terminal_multiple: float


def _adjusted_ohlc(path: Path, ticker: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing {path}")
    df = pd.read_parquet(path)
    if "date" in df.columns:
        df = df.set_index("date")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    required_cols = {"open", "close", "adj_close"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(f"{ticker} missing required OHLC columns: {sorted(missing)}")
    ratio = df["adj_close"].astype(float) / df["close"].astype(float)
    out = pd.DataFrame({
        (ticker, "open"): df["open"].astype(float) * ratio,
        (ticker, "close"): df["adj_close"].astype(float),
    }, index=df.index).sort_index()
    return out


def load_inputs() -> pd.DataFrame:
    data = pd.concat([_adjusted_ohlc(PRICE_DIR / f"{t}.parquet", t) for t in REQUIRED], axis=1, join="inner").dropna()
    data = data.loc["2010-01-01":]
    if data.empty or len(data) < 252 * 5 + 60:
        raise ValueError("insufficient common OHLC history")
    if not (data > 0.0).all().all():
        raise ValueError("non-positive adjusted OHLC values")
    return data


def component_returns(data: pd.DataFrame) -> pd.DataFrame:
    out: dict[str, pd.Series] = {}
    for ticker in REQUIRED:
        open_ = data[(ticker, "open")]
        close = data[(ticker, "close")]
        out[f"{ticker}_close_to_open"] = open_ / close.shift(1) - 1.0
        out[f"{ticker}_open_to_close"] = close / open_ - 1.0
        out[f"{ticker}_close_to_close"] = close.pct_change()
    return pd.DataFrame(out, index=data.index).iloc[1:].dropna()


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


def strategy_returns(components: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    asset = str(config["asset"])
    leg = str(config["leg"])
    if leg == "close_to_open":
        return components[f"{asset}_close_to_open"].fillna(0.0)
    if leg == "open_to_close":
        # Daily proxy: risky capital is exposed intraday; otherwise it earns the
        # defensive SHV close-to-close leg. This avoids adding any fitted filter.
        return (components[f"{asset}_open_to_close"] + components["SHV_close_to_close"]).fillna(0.0)
    raise ValueError(f"unknown leg: {leg}")


def strategy_returns_numpy(components: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    arr = components.to_numpy(dtype=float)
    cols = list(components.columns)
    asset = str(config["asset"])
    if config["leg"] == "close_to_open":
        out = arr[:, cols.index(f"{asset}_close_to_open")]
    else:
        out = arr[:, cols.index(f"{asset}_open_to_close")] + arr[:, cols.index("SHV_close_to_close")]
    return pd.Series(out, index=components.index)


def benchmark_returns(components: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    return components[f"{config['asset']}_close_to_close"].loc[index].fillna(0.0)


def permuted_components(components: pd.DataFrame, rng: np.random.Generator, start: int = 0) -> pd.DataFrame:
    out = components.copy()
    tail = out.iloc[start:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    out.iloc[start:] = shuffled
    return out


def mcpt_fixed_config(components: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed = metrics(strategy_returns(components, config=config)).sharpe
    stats = [metrics(strategy_returns(permuted_components(components, rng), config=config)).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n}


def wf_returns_fixed(components: pd.DataFrame, config: dict[str, Any], train: int = 1008, test: int = 252, step: int = 252) -> tuple[pd.Series, list[dict[str, float]]]:
    parts: list[pd.Series] = []
    windows: list[dict[str, float]] = []
    start = 0
    while start + train + test <= len(components):
        test_components = components.iloc[start + train: start + train + test]
        r = strategy_returns(test_components, config=config).iloc[-test:]
        parts.append(r)
        windows.append({"total_return": float((1.0 + r).prod() - 1.0), "mdd": max_drawdown(r)})
        start += step
    if not parts:
        raise ValueError("not enough observations for walk-forward")
    return pd.concat(parts), windows


def wf_mcpt_fixed(components: pd.DataFrame, config: dict[str, Any], n: int, seed: int) -> dict[str, float | int]:
    rng = np.random.default_rng(seed)
    observed_returns, windows = wf_returns_fixed(components, config)
    observed = metrics(observed_returns).sharpe
    stats = [metrics(wf_returns_fixed(permuted_components(components, rng, start=1008), config)[0]).sharpe for _ in range(n)]
    arr = np.asarray(stats, dtype=float)
    return {"observed": observed, "p_value": float(np.mean(arr >= observed)), "n_permutations": n, "n_windows": len(windows)}


def bootstrap_ci_low(returns: pd.Series) -> float:
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=2115)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_inputs()
        components = component_returns(data)
    except Exception as exc:  # noqa: BLE001 - data-blocked artifact must record loader failures.
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
            "kill_switches": ["required_ohlc_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter021.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered OHLC inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(components, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bench = benchmark_returns(components, config, r.index)
        bm = metrics(bench)
        rows.append({"config": config["name"], **config, **m.__dict__, "benchmark_sharpe": bm.sharpe, "benchmark_cagr": bm.cagr, "benchmark_mdd": bm.mdd})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]
    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(components, best_config, n=200, seed=2113)
    wf_mcpt = wf_mcpt_fixed(components, best_config, n=100, seed=2114)
    wf_returns, wf_windows = wf_returns_fixed(components, best_config)
    bench_returns = benchmark_returns(components, best_config, best_returns.index)
    best_metrics = metrics(best_returns)
    bench_metrics = metrics(bench_returns)
    oos_return = float((1.0 + best_returns.iloc[int(len(best_returns) * 0.8):]).prod() - 1.0)
    fwd_63d = float((1.0 + best_returns.iloc[-63:]).prod() - 1.0)
    boot_low = bootstrap_ci_low(best_returns)
    numpy_cagr = metrics(strategy_returns_numpy(components, config=best_config).loc[best_returns.index]).cagr
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
        "mcpt_reps": {"is_mcpt": 200, "wf_mcpt": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": best_metrics.__dict__,
        "benchmark": {"pre_registered_benchmark": bench_metrics.__dict__},
        "gates": gates,
        "kill_switches": [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter021.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Daily adjusted-OHLC intraday/overnight decomposition; no post-result filters or session retuning.",
    })


if __name__ == "__main__":
    main()
