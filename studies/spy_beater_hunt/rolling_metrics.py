"""Rolling-window CAGR and MDD computation for spy_beater_hunt.

Different from studies.long_term_portfolio.rolling_windows (which only
covers rolling Sharpe). This module computes per-window CAGR (compound
annual growth) and MDD (max drawdown) over W-year windows, used in:

  - scoring criterion 6 (multi-horizon robustness):
    pass-rate of W-year windows where strategy CAGR ≥ SPY benchmark CAGR.
  - plot_helper.plot_rolling_cagr_mdd: per-dataset visualisation.

Window sizes default to {5, 10, 15, 20} years per user request 2026-04-29.
Step size 252 trading days = 1y forward shift between windows (overlapping).
Windows that don't fit the dataset length are auto-skipped.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252
DEFAULT_WINDOWS_YEARS: list[int] = [5, 10, 15, 20]


def _window_cagr_mdd(returns: pd.Series) -> tuple[float, float]:
    """Compute CAGR and MDD on a daily-returns Series."""
    eq = (1.0 + returns).cumprod() * 10_000.0
    if len(eq) < 2:
        return float("nan"), float("nan")
    n = len(returns)
    cagr_val = float((eq.iloc[-1] / eq.iloc[0]) ** (TRADING_DAYS_PER_YEAR / n) - 1.0)
    running_max = eq.cummax()
    mdd_val = float((1.0 - eq / running_max).max())
    return cagr_val, mdd_val


def rolling_cagr_mdd_at_windows(
    returns: pd.Series,
    windows_years: list[int] = DEFAULT_WINDOWS_YEARS,
    step_days: int = TRADING_DAYS_PER_YEAR,
) -> dict[int, list[dict]]:
    """Per-window CAGR and MDD, indexed by window-size in years.

    Returns:
        ``{w_years: [{"start": Timestamp, "end": Timestamp,
                       "cagr": float, "mdd": float}, ...]}``
        For window sizes that don't fit the dataset, value is an empty list.
    """
    out: dict[int, list[dict]] = {}
    n = len(returns)
    for w in windows_years:
        win_days = w * TRADING_DAYS_PER_YEAR
        if n < win_days:
            out[w] = []
            continue
        rows: list[dict] = []
        for start in range(0, n - win_days + 1, step_days):
            sample = returns.iloc[start:start + win_days]
            cagr_val, mdd_val = _window_cagr_mdd(sample)
            rows.append({
                "start": sample.index[0],
                "end": sample.index[-1],
                "cagr": cagr_val,
                "mdd": mdd_val,
            })
        out[w] = rows
    return out


def cagr_pass_rate_vs_benchmark(
    strat_rolling: list[dict],
    bench_rolling: list[dict],
) -> tuple[float, int]:
    """Pct of windows where strat CAGR ≥ bench CAGR.

    Both lists must be aligned by window index (same start/end pairs);
    missing alignment is silently skipped.
    """
    if not strat_rolling or not bench_rolling:
        return float("nan"), 0
    bench_map = {(r["start"], r["end"]): r["cagr"] for r in bench_rolling}
    n_eval = 0
    n_pass = 0
    for r in strat_rolling:
        key = (r["start"], r["end"])
        if key not in bench_map:
            continue
        n_eval += 1
        if r["cagr"] >= bench_map[key]:
            n_pass += 1
    pct = float(n_pass / n_eval) if n_eval > 0 else float("nan")
    return pct, n_eval


def worst_window_mdd(strat_rolling: list[dict]) -> float:
    """Max MDD across all windows (worst peak-to-trough)."""
    if not strat_rolling:
        return float("nan")
    return float(max(r["mdd"] for r in strat_rolling))


def worst_window_cagr(strat_rolling: list[dict]) -> float:
    """Min CAGR across all windows (worst growth period)."""
    if not strat_rolling:
        return float("nan")
    return float(min(r["cagr"] for r in strat_rolling))
