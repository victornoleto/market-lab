"""Iteration 009: Hirsch/Kaeppel seasonal leveraged SPY window.

Kaufman summarizes Hirsch's seasonal rule as buying the first trading day of
November and selling the last trading day of April `[trading_systems_methods,
p.480]`. This runner keeps that calendar rule fixed, maps the strong season to
SSO or UPRO and the weak season to CASHX, and applies returns only after the
calendar state is known. PBO/DSR follow AFML `[advances_fin_ml, p.208-211]`,
`[advances_fin_ml, p.222-223]`.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from market_lab.backtest.metrics.performance import cagr, max_drawdown, sharpe, sortino
from market_lab.backtest.validation.dsr import dsr
from market_lab.backtest.validation.pbo import pbo
from studies.letf_rotation_hunt.core.data_loader import load_testfolio_series


ITERATION = "009-2026-05-13-seasonal-hirsch-window"
OUT_DIR = Path(__file__).resolve().parent
REQUIRED_TICKERS = ["SPYSIM", "SSOSIM", "UPROSIM", "CASHX"]
STRONG_MONTHS = {11, 12, 1, 2, 3, 4}
CONFIGS = {
    "hirsch_nov_apr_sso_cash": {"risk_asset": "SSOSIM"},
    "hirsch_nov_apr_upro_cash": {"risk_asset": "UPROSIM"},
}
CUMULATIVE_N_TRIALS_AFTER = 18


def _equity_from_returns(returns: pd.Series) -> pd.Series:
    return (1.0 + returns).cumprod()


def _window_cagr(equity: pd.Series) -> float:
    if len(equity) < 2 or float(equity.iloc[0]) <= 0:
        return float("nan")
    return float((float(equity.iloc[-1]) / float(equity.iloc[0])) ** (252 / (len(equity) - 1)) - 1)


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


def _seasonal_signal(index: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(index.month.isin(STRONG_MONTHS), index=index, name="seasonal_on")


def _strategy_returns(prices: pd.DataFrame, config: dict[str, str]) -> pd.Series:
    risk_asset = config["risk_asset"]
    signal = _seasonal_signal(prices.index)
    asset_returns = prices[[risk_asset, "CASHX"]].pct_change()
    returns = asset_returns["CASHX"].where(~signal, asset_returns[risk_asset])
    return returns.dropna()


def _strategy_returns_loop(prices: pd.DataFrame, config: dict[str, str]) -> pd.Series:
    risk_asset = config["risk_asset"]
    asset_returns = prices[[risk_asset, "CASHX"]].pct_change()
    vals: list[float] = []
    idx: list[pd.Timestamp] = []
    for i in range(1, len(prices)):
        on = prices.index[i].month in STRONG_MONTHS
        value = float(asset_returns[risk_asset].iloc[i] if on else asset_returns["CASHX"].iloc[i])
        if np.isfinite(value):
            vals.append(value)
            idx.append(prices.index[i])
    return pd.Series(vals, index=pd.DatetimeIndex(idx))


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
        windows.append({"start": str(frame.index.min().date()), "end": str(frame.index.max().date()), "candidate_return": cand_ret, "spy_return": spy_ret, "excess_return": excess, "pass": passed})
    return {"pass_count": pass_count, "total": n_windows, "pass": pass_count >= 6, "windows": windows}


def _oos_gate(candidate: pd.Series, spy: pd.Series) -> dict[str, Any]:
    aligned = pd.concat([candidate.rename("candidate"), spy.rename("spy")], axis=1).dropna()
    tail = aligned.iloc[int(len(aligned) * 0.75) :]
    candidate_cagr = _window_cagr(_equity_from_returns(tail["candidate"]))
    spy_cagr = _window_cagr(_equity_from_returns(tail["spy"]))
    return {"start": str(tail.index.min().date()), "end": str(tail.index.max().date()), "candidate_cagr": candidate_cagr, "spy_cagr": spy_cagr, "excess_cagr": candidate_cagr - spy_cagr, "pass": candidate_cagr > spy_cagr}


def _fwd_gate(candidate: pd.Series, spy: pd.Series, years: int = 3) -> dict[str, Any]:
    aligned = pd.concat([candidate.rename("candidate"), spy.rename("spy")], axis=1).dropna().iloc[-years * 252 :]
    candidate_cagr = _window_cagr(_equity_from_returns(aligned["candidate"]))
    spy_cagr = _window_cagr(_equity_from_returns(aligned["spy"]))
    return {"start": str(aligned.index.min().date()), "end": str(aligned.index.max().date()), "candidate_cagr": candidate_cagr, "spy_cagr": spy_cagr, "excess_cagr": candidate_cagr - spy_cagr, "pass": candidate_cagr > spy_cagr}


def _bootstrap_excess_ci(excess_returns: pd.Series, n_resamples: int = 2000, seed: int = 49) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    values = excess_returns.dropna().to_numpy(dtype=float)
    samples = rng.choice(values, size=(n_resamples, len(values)), replace=True).mean(axis=1) * 252
    lo, hi = np.quantile(samples, [0.001, 0.999])
    return {"annualized_excess_mean": float(values.mean() * 252), "ci_low_99_9": float(lo), "ci_high_99_9": float(hi), "n_resamples": n_resamples, "pass": bool(lo > 0)}


def _write_json(name: str, data: dict[str, Any]) -> None:
    (OUT_DIR / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> None:
    blockers: list[str] = []
    loaded: dict[str, pd.Series] = {}
    for ticker in REQUIRED_TICKERS:
        try:
            loaded[ticker] = load_testfolio_series(ticker).dropna().sort_index()
        except Exception as exc:  # noqa: BLE001 - artifact should capture data blockers.
            blockers.append(f"{ticker}: {exc}")

    if blockers:
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
            "kill_switches": blockers,
            "artifacts": ["PRE_REG.md", "run_seasonal_hirsch_window.py", "RESULTS.json"],
            "notes": "Required pre-registered testfolio labels unavailable; no substitution performed.",
        }
        _write_json("RESULTS.json", results)
        return

    prices = pd.concat(loaded, axis=1).dropna()
    strategy_returns: dict[str, pd.Series] = {}
    loop_returns: dict[str, pd.Series] = {}
    for config_name, config in CONFIGS.items():
        strategy_returns[config_name] = _strategy_returns(prices, config).rename(config_name)
        loop_returns[config_name] = _strategy_returns_loop(prices, config).rename(config_name)

    matrix = pd.DataFrame(strategy_returns).dropna()
    spy_returns = prices["SPYSIM"].pct_change().reindex(matrix.index).dropna().rename("SPYSIM")
    matrix = matrix.reindex(spy_returns.index).dropna()
    spy_returns = spy_returns.reindex(matrix.index)
    spy_equity = _equity_from_returns(spy_returns)

    config_metrics = {name: _metrics(_equity_from_returns(ret.reindex(matrix.index)), ret.reindex(matrix.index), spy_equity) for name, ret in strategy_returns.items()}
    spy_benchmark = _metrics(spy_equity, spy_returns, spy_equity)
    best_name = max(config_metrics, key=lambda k: config_metrics[k]["cagr"])
    best_returns = matrix[best_name]
    best_equity = _equity_from_returns(best_returns)

    pbo_result = pbo(matrix.to_numpy(dtype=float), n_blocks=10)
    dsr_result = dsr(best_returns.to_numpy(dtype=float), n_trials=CUMULATIVE_N_TRIALS_AFTER)
    cross_lib = {}
    for name in CONFIGS:
        vec = _equity_from_returns(strategy_returns[name].reindex(matrix.index).dropna())
        loop = _equity_from_returns(loop_returns[name].reindex(matrix.index).dropna())
        cagr_delta = abs(cagr(vec) - cagr(loop))
        cross_lib[name] = {"vector_cagr": cagr(vec), "loop_cagr": cagr(loop), "abs_delta": cagr_delta, "pass": cagr_delta <= 0.03}

    beats_spy_cagr = bool(config_metrics[best_name]["cagr"] > spy_benchmark["cagr"])
    terminal_beats_spy = bool(config_metrics[best_name]["terminal_ratio_vs_spy"] > 1.0)
    gates = {
        "pbo": {"computed": True, "value": pbo_result.pbo, "n_blocks": pbo_result.n_blocks, "n_combinations": pbo_result.n_combinations, "pass": pbo_result.pbo < 0.5, "note": "Unstable with only two pre-registered configs."},
        "dsr": {"computed": True, "p_value": dsr_result.p_value, "dsr": dsr_result.dsr, "observed_sharpe_periodic": dsr_result.observed_sharpe, "benchmark_sharpe_periodic": dsr_result.benchmark_sharpe, "n_trials": dsr_result.n_trials, "pass": dsr_result.p_value < 0.05},
        "walk_forward": _wf_gate(best_returns, spy_returns),
        "oos": _oos_gate(best_returns, spy_returns),
        "fwd": _fwd_gate(best_returns, spy_returns),
        "bootstrap": _bootstrap_excess_ci(best_returns - spy_returns),
        "cross_lib": {"configs": cross_lib, "pass": all(v["pass"] for v in cross_lib.values())},
        "economic": {"beats_spy_cagr": beats_spy_cagr, "terminal_beats_spy": terminal_beats_spy, "pass": beats_spy_cagr and terminal_beats_spy},
    }
    winner = all(gate.get("pass", False) for gate in gates.values())
    kill_switches = [name for name, gate in gates.items() if not gate.get("pass", False)]
    status = "winner" if winner else "fail"

    diagnostics = {
        "iteration": ITERATION,
        "data_window": {"start": str(prices.index.min().date()), "end": str(prices.index.max().date()), "n_prices": int(len(prices))},
        "test_window": {"start": str(matrix.index.min().date()), "end": str(matrix.index.max().date()), "n_returns": int(len(matrix))},
        "configs": CONFIGS,
        "seasonal_rule": {"strong_months": sorted(STRONG_MONTHS), "weak_months": [5, 6, 7, 8, 9, 10]},
        "config_metrics": config_metrics,
        "best_equity_tail": {str(k.date()): float(v) for k, v in best_equity.tail(5).items()},
    }
    _write_json("diagnostics.json", diagnostics)

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
        "artifacts": ["PRE_REG.md", "run_seasonal_hirsch_window.py", "RESULTS.json", "diagnostics.json"],
        "notes": "Pre-fixed Hirsch November-April seasonal exposure mapped to SSO or UPRO with CASHX off-leg.",
    }
    _write_json("RESULTS.json", results)


if __name__ == "__main__":
    main()
