"""Iteration 010: cross-asset Clenow-style adjusted-slope momentum.

The signal ranks assets by Clenow's annualized 90-day log-price regression slope
times R² `[stocks_on_the_move, p.75-77]`, only allows new risk exposure when SPY
is above its 200-day SMA `[stocks_on_the_move, p.66-67]`, and sizes one variant
by inverse volatility to allocate risk rather than cash `[stocks_on_the_move,
p.83-89]`. PBO/DSR follow AFML `[advances_fin_ml, p.208-211]`,
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


ITERATION = "010-2026-05-13-cross-asset-clenow-momentum"
OUT_DIR = Path(__file__).resolve().parent
ASSETS = ["SPYSIM", "ZROZSIM", "GLDSIM", "KMLMSIM"]
REQUIRED_TICKERS = [*ASSETS, "CASHX"]
LOOKBACK = 90
REGIME_SMA = 200
INVOL_LOOKBACK = 63
CONFIGS = {
    "clenow_xasset_top1_cash": {"top_k": 1, "weighting": "winner_take_all"},
    "clenow_xasset_top2_invvol_cash": {"top_k": 2, "weighting": "inverse_vol"},
}
CUMULATIVE_N_TRIALS_AFTER = 20


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


def _adjusted_slope(values: np.ndarray) -> float:
    if len(values) != LOOKBACK or np.any(values <= 0) or not np.all(np.isfinite(values)):
        return float("nan")
    y = np.log(values)
    x = np.arange(len(values), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    ss_res = float(np.sum((y - fitted) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 0.0 if ss_tot == 0 else max(0.0, 1.0 - ss_res / ss_tot)
    annualized = float(np.exp(slope * 250) - 1.0)
    return annualized * r2


def _rebalance_mask(index: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(index.weekday == 2, index=index)


def _target_weights(prices: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    scores = prices[ASSETS].rolling(LOOKBACK).apply(_adjusted_slope, raw=True)
    regime_on = prices["SPYSIM"] > prices["SPYSIM"].rolling(REGIME_SMA).mean()
    vol = prices[ASSETS].pct_change().rolling(INVOL_LOOKBACK).std() * np.sqrt(252)
    is_rebalance = _rebalance_mask(prices.index)
    weights = pd.DataFrame(0.0, index=prices.index, columns=REQUIRED_TICKERS)
    current = pd.Series(0.0, index=REQUIRED_TICKERS)

    for dt in prices.index:
        if bool(is_rebalance.loc[dt]):
            current[:] = 0.0
            row = scores.loc[dt].dropna().sort_values(ascending=False)
            if bool(regime_on.loc[dt]) and len(row) >= int(config["top_k"]):
                selected = list(row.index[: int(config["top_k"])])
                if config["weighting"] == "winner_take_all":
                    current[selected[0]] = 1.0
                else:
                    inv = 1.0 / vol.loc[dt, selected].replace(0.0, np.nan).dropna()
                    if len(inv) == len(selected) and float(inv.sum()) > 0:
                        current.loc[selected] = inv / float(inv.sum())
                    else:
                        current[selected] = 1.0 / len(selected)
            else:
                current["CASHX"] = 1.0
        weights.loc[dt] = current
    return weights


def _strategy_returns(prices: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    weights = _target_weights(prices, config).shift(1).fillna(0.0)
    asset_returns = prices[REQUIRED_TICKERS].pct_change().fillna(0.0)
    returns = (weights * asset_returns).sum(axis=1)
    return returns.iloc[REGIME_SMA + 1 :].dropna()


def _strategy_returns_loop(prices: pd.DataFrame, config: dict[str, Any]) -> pd.Series:
    weights = _target_weights(prices, config).shift(1).fillna(0.0)
    asset_returns = prices[REQUIRED_TICKERS].pct_change().fillna(0.0)
    vals: list[float] = []
    idx: list[pd.Timestamp] = []
    for i in range(REGIME_SMA + 1, len(prices)):
        value = float(sum(float(weights.iloc[i][ticker]) * float(asset_returns.iloc[i][ticker]) for ticker in REQUIRED_TICKERS))
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


def _bootstrap_excess_ci(excess_returns: pd.Series, n_resamples: int = 2000, seed: int = 50) -> dict[str, Any]:
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
            "artifacts": ["PRE_REG.md", "run_cross_asset_clenow_momentum.py", "RESULTS.json"],
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
        "assets": ASSETS,
        "configs": CONFIGS,
        "parameters": {"lookback": LOOKBACK, "regime_sma": REGIME_SMA, "inverse_vol_lookback": INVOL_LOOKBACK, "rebalance_weekday": "Wednesday"},
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
        "artifacts": ["PRE_REG.md", "run_cross_asset_clenow_momentum.py", "RESULTS.json", "diagnostics.json"],
        "notes": "Pre-fixed Clenow adjusted-slope cross-asset momentum with SPY SMA200 regime filter.",
    }
    _write_json("RESULTS.json", results)


if __name__ == "__main__":
    main()
