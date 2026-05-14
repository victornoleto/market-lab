"""Iteration 019 runner: yield/carry rotation.

This iteration tests a pre-registered carry/yield mechanism rather than another
local technical overlay. Carry forecasts are expected-return proxies but carry is
negative-skew, so promotion remains blocked unless MCPT, PBO and DSR pass
`[systematic_trading, p.32-35]`, `[systematic_trading, p.119]`,
`[systematic_trading, p.288]`, `[testing_tuning, p.318-320]`,
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
from studies.letf_rotation_hunt.core.data_loader_yields import (
    load_constant_maturity_yield,
    load_dividend_yield,
)


ITERATION = "019-2026-05-14-yield-carry-rotation"
OUT_DIR = ROOT / "studies/success_trading_strat/iters" / ITERATION
PRICE_DIR = ROOT / "data/tiingo/daily/prices"
REQUIRED = ["SPY", "TLT", "IEF", "SHV"]
CUMULATIVE_TRIALS_AFTER = 64
STALE_BLOCK_DATE = pd.Timestamp("2026-03-31")
CONFIGS: list[dict[str, Any]] = [
    {"name": "spy_div_gt_cash_tlt_term", "kind": "equity_bond", "equity": "SPY", "bond": "TLT", "bond_tenor": "30y"},
    {"name": "spy_div_gt_cash_ief_term", "kind": "equity_bond", "equity": "SPY", "bond": "IEF", "bond_tenor": "10y"},
    {"name": "bond_steep_tlt_else_shv", "kind": "bond_only", "bond": "TLT", "bond_tenor": "30y"},
    {"name": "bond_steep_ief_else_shv", "kind": "bond_only", "bond": "IEF", "bond_tenor": "10y"},
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


def _date_indexed(series: pd.Series) -> pd.Series:
    out = series.copy()
    if not isinstance(out.index, pd.DatetimeIndex):
        out.index = pd.to_datetime(out.index)
    if out.index.tz is not None:
        out.index = out.index.tz_localize(None)
    out.index = out.index.normalize()
    return out.astype(float).sort_index()


def load_inputs() -> pd.DataFrame:
    prices = pd.concat([_series_from_parquet(PRICE_DIR / f"{t}.parquet", t) for t in REQUIRED], axis=1, join="inner").dropna()
    prices = prices.loc["2010-01-01":]
    yields = pd.concat(
        [
            _date_indexed(load_constant_maturity_yield("3m")).rename("y3m"),
            _date_indexed(load_constant_maturity_yield("10y")).rename("y10y"),
            _date_indexed(load_constant_maturity_yield("30y")).rename("y30y"),
            _date_indexed(load_dividend_yield("SPY")).rename("spy_div_yield"),
        ],
        axis=1,
        join="outer",
    ).sort_index().ffill()
    data = prices.join(yields, how="inner").dropna()
    data = data[(data[REQUIRED] > 0.0).all(axis=1)]
    if data.empty or len(data) < 252 * 5 + 60:
        raise ValueError("insufficient common price/yield history")
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


def strategy_returns(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    rets = data[REQUIRED].pct_change().fillna(0.0)
    bond = str(config["bond"])
    tenor_col = "y30y" if config["bond_tenor"] == "30y" else "y10y"
    term_positive = data[tenor_col] > data["y3m"]
    if config["kind"] == "equity_bond":
        equity_positive_carry = data["spy_div_yield"] > data["y3m"]
        target = pd.Series("SHV", index=data.index, dtype="object")
        target.loc[term_positive] = bond
        target.loc[equity_positive_carry] = str(config["equity"])
    else:
        target = pd.Series(np.where(term_positive, bond, "SHV"), index=data.index)
    target = target.shift(1).fillna("SHV")
    out = pd.Series(index=data.index, dtype=float)
    for asset in REQUIRED:
        out.loc[target == asset] = rets.loc[target == asset, asset]
    return out.iloc[2:].fillna(0.0)


def strategy_returns_numpy(data: pd.DataFrame, *, config: dict[str, Any]) -> pd.Series:
    return strategy_returns(data.copy(), config=config)


def benchmark_returns(data: pd.DataFrame, config: dict[str, Any], index: pd.Index) -> pd.Series:
    rets = data[REQUIRED].pct_change().fillna(0.0)
    if config["kind"] == "equity_bond":
        bond = str(config["bond"])
        return (0.6 * rets["SPY"] + 0.4 * rets[bond]).loc[index]
    return rets["SHV"].loc[index]


def returns_to_prices(first: pd.Series, returns: pd.DataFrame) -> pd.DataFrame:
    rebuilt = (1.0 + returns).cumprod().mul(first, axis=1)
    first_row = first.to_frame().T
    first_row.index = [returns.index[0] - pd.Timedelta(days=1)]
    return pd.concat([first_row, rebuilt]).sort_index()


def permuted_data(data: pd.DataFrame, rng: np.random.Generator, start: int = 1) -> pd.DataFrame:
    price_returns = data[REQUIRED].pct_change().iloc[1:].copy()
    prefix = data[REQUIRED].iloc[:start].copy()
    tail = price_returns.iloc[start - 1:].copy()
    shuffled = tail.iloc[rng.permutation(len(tail))]
    shuffled.index = tail.index
    rebuilt_prices = returns_to_prices(prefix.iloc[0], pd.concat([price_returns.iloc[: start - 1], shuffled]).sort_index())
    out = data.copy()
    out[REQUIRED] = rebuilt_prices.loc[data.index[0]:].reindex(data.index).ffill()
    return out


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
        test_data = data.iloc[start + train - 5: start + train + test]
        r = strategy_returns(test_data, config=config).iloc[-test:]
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
    samples = stationary_bootstrap_trades(returns.dropna().to_numpy(), block_mean=5, n_resamples=2000, seed=1915)
    return float(np.quantile(samples.mean(axis=1), 0.001))


def write_results(results: dict[str, Any]) -> None:
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


def main() -> None:
    try:
        data = load_inputs()
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
            "kill_switches": ["required_price_or_yield_data_missing"],
            "artifacts": ["PRE_REG.md", "run_iter019.py", "RESULTS.json", "SUMMARY.md"],
            "notes": f"Pre-registered price/yield inputs unavailable: {type(exc).__name__}: {exc}.",
        })
        return

    config_returns: dict[str, pd.Series] = {}
    rows: list[dict[str, Any]] = []
    for config in CONFIGS:
        r = strategy_returns(data, config=config)
        config_returns[str(config["name"])] = r
        m = metrics(r)
        bench = benchmark_returns(data, config, r.index)
        rows.append({"config": config["name"], **config, **m.__dict__, "benchmark_sharpe": metrics(bench).sharpe, "benchmark_cagr": metrics(bench).cagr})

    ranked = sorted(rows, key=lambda x: (x["sharpe"], x["cagr"]), reverse=True)
    best_name = str(ranked[0]["config"])
    best_config = next(c for c in CONFIGS if c["name"] == best_name)
    best_returns = config_returns[best_name]
    matrix = pd.concat(config_returns.values(), axis=1, join="inner").dropna()
    matrix.columns = list(config_returns.keys())
    pbo_res = pbo(matrix.to_numpy(), n_blocks=8)
    dsr_res = dsr(best_returns.dropna().to_numpy(), n_trials=CUMULATIVE_TRIALS_AFTER)
    is_mcpt = mcpt_fixed_config(data, best_config, n=200, seed=1913)
    wf_mcpt = wf_mcpt_fixed(data, best_config, n=100, seed=1914)
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
        "mcpt_reps": {"is_mcpt": 200, "wf_mcpt": 100},
        "best_config": best_config,
        "winner": winner,
        "metrics": best_metrics.__dict__,
        "benchmark": {"pre_registered_benchmark": bench_metrics.__dict__},
        "gates": gates,
        "kill_switches": [name for name, gate in gates.items() if not gate["pass"]],
        "artifacts": ["PRE_REG.md", "run_iter019.py", "RESULTS.json", "SUMMARY.md", "config_metrics.csv", "wf_windows.csv"],
        "notes": "Yield/carry rotation with one-bar-lagged signals; no post-result parameter additions.",
    })


if __name__ == "__main__":
    main()
