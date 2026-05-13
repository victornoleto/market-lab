"""Iteration 002: pre-fixed static diversifier control.

The strategy family is a constant-long asset allocator, not a signal grid:
Carver recommends separating allocation from forecast mining and using sensible
handcrafted diversification when optimization is unstable `[systematic_trading,
p.72-85]`; the asset allocator's forecast is constant long exposure
`[systematic_trading, p.116]`. PBO/DSR gate discipline follows AFML
`[advances_fin_ml, p.208-211]`, `[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from market_lab.backtest.metrics.performance import cagr, max_drawdown, sharpe, sortino
from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series


ITERATION = "002-2026-05-13-static-diversifier-control"
OUT_DIR = Path(__file__).resolve().parent
TICKERS = ["SPYSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"]
CONFIGS: dict[str, dict[str, float]] = {
    "static_60_20_10_10": {"SPYSIM": 0.60, "ZROZSIM": 0.20, "GLDSIM": 0.10, "KMLMSIM": 0.10},
    "static_50_25_15_10": {"SPYSIM": 0.50, "ZROZSIM": 0.25, "GLDSIM": 0.15, "KMLMSIM": 0.10},
    "static_40_30_20_10": {"SPYSIM": 0.40, "ZROZSIM": 0.30, "GLDSIM": 0.20, "KMLMSIM": 0.10},
    "static_25_25_25_25": {"SPYSIM": 0.25, "ZROZSIM": 0.25, "GLDSIM": 0.25, "KMLMSIM": 0.25},
}


def _equity_from_returns(returns: pd.Series) -> pd.Series:
    return (1.0 + returns).cumprod()


def _daily_constant_weight_returns(asset_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    w = pd.Series(weights, dtype=float).reindex(asset_returns.columns).fillna(0.0)
    if not np.isclose(float(w.sum()), 1.0):
        raise ValueError(f"weights must sum to 1, got {w.sum()}")
    return asset_returns.mul(w, axis=1).sum(axis=1)


def _loop_constant_weight_returns(asset_returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    w = np.array([weights[c] for c in asset_returns.columns], dtype=float)
    vals: list[float] = []
    idx: list[pd.Timestamp] = []
    for dt, row in asset_returns.iterrows():
        vals.append(float(np.dot(row.to_numpy(dtype=float), w)))
        idx.append(dt)
    return pd.Series(vals, index=pd.DatetimeIndex(idx), name="loop_returns")


def _window_cagr(equity: pd.Series) -> float:
    if len(equity) < 2 or float(equity.iloc[0]) <= 0:
        return float("nan")
    return float((float(equity.iloc[-1]) / float(equity.iloc[0])) ** (252 / (len(equity) - 1)) - 1)


def _metrics(equity: pd.Series, returns: pd.Series, spy_equity: pd.Series) -> dict[str, Any]:
    aligned = pd.concat([equity.rename("candidate"), spy_equity.rename("spy")], axis=1).dropna()
    return {
        "start": str(aligned.index.min().date()),
        "end": str(aligned.index.max().date()),
        "n_returns": int(len(returns)),
        "cagr": cagr(equity),
        "mdd": max_drawdown(equity),
        "sharpe": sharpe(returns),
        "sortino": sortino(returns),
        "terminal_equity": float(equity.iloc[-1]),
        "terminal_ratio_vs_spy": float(aligned["candidate"].iloc[-1] / aligned["spy"].iloc[-1]),
        **_rolling_win_rates(equity, spy_equity),
    }


def _rolling_win_rates(equity: pd.Series, spy_equity: pd.Series) -> dict[str, float | None]:
    aligned = pd.concat([equity.rename("candidate"), spy_equity.rename("spy")], axis=1).dropna()
    out: dict[str, float | None] = {}
    for years in (3, 5, 10):
        window = years * 252
        if len(aligned) <= window:
            out[f"rolling_{years}y_cagr_win_rate_vs_spy"] = None
            continue
        cand = aligned["candidate"].rolling(window).apply(_window_cagr, raw=False).dropna()
        spy = aligned["spy"].rolling(window).apply(_window_cagr, raw=False).dropna()
        joined = pd.concat([cand.rename("candidate"), spy.rename("spy")], axis=1).dropna()
        out[f"rolling_{years}y_cagr_win_rate_vs_spy"] = float((joined["candidate"] > joined["spy"]).mean())
    return out


def _wf_gate(candidate: pd.Series, spy: pd.Series, n_windows: int = 8) -> dict[str, Any]:
    aligned = pd.concat([candidate.rename("candidate"), spy.rename("spy")], axis=1).dropna()
    chunks = np.array_split(aligned.index.to_numpy(), n_windows)
    windows = []
    pass_count = 0
    for chunk in chunks:
        frame = aligned.loc[pd.DatetimeIndex(chunk)]
        cand_ret = float((1.0 + frame["candidate"]).prod() - 1.0)
        spy_ret = float((1.0 + frame["spy"]).prod() - 1.0)
        excess = cand_ret - spy_ret
        passed = excess > 0
        pass_count += int(passed)
        windows.append(
            {
                "start": str(frame.index.min().date()),
                "end": str(frame.index.max().date()),
                "candidate_return": cand_ret,
                "spy_return": spy_ret,
                "excess_return": excess,
                "pass": passed,
            }
        )
    return {"pass_count": pass_count, "total": n_windows, "pass": pass_count >= 6, "windows": windows}


def _oos_gate(candidate: pd.Series, spy: pd.Series) -> dict[str, Any]:
    aligned = pd.concat([candidate.rename("candidate"), spy.rename("spy")], axis=1).dropna()
    start_i = int(len(aligned) * 0.75)
    tail = aligned.iloc[start_i:]
    candidate_cagr = _window_cagr(_equity_from_returns(tail["candidate"]))
    spy_cagr = _window_cagr(_equity_from_returns(tail["spy"]))
    return {"start": str(tail.index.min().date()), "end": str(tail.index.max().date()), "candidate_cagr": candidate_cagr, "spy_cagr": spy_cagr, "excess_cagr": candidate_cagr - spy_cagr, "pass": candidate_cagr > spy_cagr}


def _fwd_gate(candidate: pd.Series, spy: pd.Series, years: int = 3) -> dict[str, Any]:
    aligned = pd.concat([candidate.rename("candidate"), spy.rename("spy")], axis=1).dropna().iloc[-years * 252 :]
    candidate_cagr = _window_cagr(_equity_from_returns(aligned["candidate"]))
    spy_cagr = _window_cagr(_equity_from_returns(aligned["spy"]))
    return {"start": str(aligned.index.min().date()), "end": str(aligned.index.max().date()), "candidate_cagr": candidate_cagr, "spy_cagr": spy_cagr, "excess_cagr": candidate_cagr - spy_cagr, "pass": candidate_cagr > spy_cagr}


def _bootstrap_excess_ci(excess_returns: pd.Series, n_resamples: int = 2000, seed: int = 42) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    values = excess_returns.to_numpy(dtype=float)
    samples = rng.choice(values, size=(n_resamples, len(values)), replace=True).mean(axis=1) * 252
    lo, hi = np.quantile(samples, [0.001, 0.999])
    return {"annualized_excess_mean": float(values.mean() * 252), "ci_low_99_9": float(lo), "ci_high_99_9": float(hi), "n_resamples": n_resamples, "pass": bool(lo > 0)}


def main() -> None:
    data_blockers: list[str] = []
    try:
        prices = pd.concat({ticker: load_testfolio_series(ticker).dropna().sort_index() for ticker in TICKERS}, axis=1).dropna()
    except Exception as exc:  # noqa: BLE001 - artifact should capture data blockers.
        data_blockers.append(str(exc))
        prices = pd.DataFrame()

    if prices.empty:
        results = {
            "iteration": ITERATION,
            "status": "data_blocked",
            "pre_registered": True,
            "n_trials": 0,
            "best_config": None,
            "beats_spy_cagr": False,
            "winner": False,
            "metrics": {},
            "spy_benchmark": {},
            "gates": {},
            "kill_switches": data_blockers or ["common data window unavailable"],
            "artifacts": ["PRE_REG.md", "run_static_diversifier.py", "RESULTS.json"],
            "notes": "Required testfolio labels unavailable.",
        }
        (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        return

    asset_returns = prices.pct_change().dropna()
    spy_returns = asset_returns["SPYSIM"]
    spy_equity = _equity_from_returns(spy_returns)
    spy_benchmark = _metrics(spy_equity, spy_returns, spy_equity)
    config_returns: dict[str, pd.Series] = {}
    config_metrics: dict[str, dict[str, Any]] = {}
    cross_lib: dict[str, dict[str, Any]] = {}

    for name, weights in CONFIGS.items():
        vector_returns = _daily_constant_weight_returns(asset_returns, weights).rename(name)
        loop_returns = _loop_constant_weight_returns(asset_returns, weights)
        equity = _equity_from_returns(vector_returns)
        loop_equity = _equity_from_returns(loop_returns)
        config_returns[name] = vector_returns
        config_metrics[name] = _metrics(equity, vector_returns, spy_equity)
        cagr_delta = abs(cagr(equity) - cagr(loop_equity))
        cross_lib[name] = {"vector_cagr": cagr(equity), "loop_cagr": cagr(loop_equity), "abs_delta": cagr_delta, "pass": cagr_delta <= 0.03}

    best_name = max(config_metrics, key=lambda k: config_metrics[k]["cagr"])
    best_returns = config_returns[best_name]
    best_equity = _equity_from_returns(best_returns)
    matrix = pd.DataFrame(config_returns).reindex(best_returns.index).dropna()
    pbo_result = pbo(matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=4)
    wf = _wf_gate(best_returns, spy_returns)
    oos = _oos_gate(best_returns, spy_returns)
    fwd = _fwd_gate(best_returns, spy_returns)
    bootstrap = _bootstrap_excess_ci(best_returns - spy_returns)
    beats_spy_cagr = bool(config_metrics[best_name]["cagr"] > spy_benchmark["cagr"])
    terminal_beats_spy = bool(config_metrics[best_name]["terminal_ratio_vs_spy"] > 1.0)
    gates = {
        "pbo": {"computed": True, "value": pbo_result.pbo, "n_blocks": pbo_result.n_blocks, "n_combinations": pbo_result.n_combinations, "pass": pbo_result.pbo < 0.5},
        "dsr": {"computed": True, "p_value": dsr_result.p_value, "dsr": dsr_result.dsr, "observed_sharpe_periodic": dsr_result.observed_sharpe, "benchmark_sharpe_periodic": dsr_result.benchmark_sharpe, "n_trials": dsr_result.n_trials, "pass": dsr_result.p_value < 0.05},
        "walk_forward": wf,
        "oos": oos,
        "fwd": fwd,
        "bootstrap": bootstrap,
        "cross_lib": {"configs": cross_lib, "pass": all(v["pass"] for v in cross_lib.values())},
        "economic": {"beats_spy_cagr": beats_spy_cagr, "terminal_beats_spy": terminal_beats_spy, "pass": beats_spy_cagr and terminal_beats_spy},
    }
    winner = all(gate.get("pass", False) for gate in gates.values())
    status = "winner" if winner else "fail"
    kill_switches = [name for name, gate in gates.items() if not gate.get("pass", False)]

    diagnostics = {
        "iteration": ITERATION,
        "data_window": {"start": str(prices.index.min().date()), "end": str(prices.index.max().date()), "n_prices": int(len(prices))},
        "configs": CONFIGS,
        "config_metrics": config_metrics,
        "best_equity_tail": {str(k.date()): float(v) for k, v in best_equity.tail(5).items()},
    }
    (OUT_DIR / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n")

    results = {
        "iteration": ITERATION,
        "status": status,
        "pre_registered": True,
        "n_trials": len(CONFIGS),
        "best_config": best_name,
        "beats_spy_cagr": beats_spy_cagr,
        "winner": winner,
        "metrics": {"best": config_metrics[best_name], "all_configs": config_metrics},
        "spy_benchmark": spy_benchmark,
        "gates": gates,
        "kill_switches": kill_switches,
        "artifacts": ["PRE_REG.md", "run_static_diversifier.py", "RESULTS.json", "diagnostics.json"],
        "notes": "Static diversifier control with four pre-fixed configs; no technical signal or local optimization.",
    }
    (OUT_DIR / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
