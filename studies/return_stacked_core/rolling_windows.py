"""Rolling-window analytics for the long-term portfolio plots.

Used by `plot_helper.py` to render the rolling-window comparison panels:
strategy Sharpe vs each benchmark Sharpe at multiple window sizes
(3/5/10/15/20/30 years) plus the % of windows where the strategy beats
the benchmark.

Auto-skips windows that don't fit the dataset length (e.g. 30y window on
17y `vt_real` returns empty Series / zero count).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS_PER_YEAR = 252
DEFAULT_WINDOWS_YEARS: list[int] = [3, 5, 10, 15, 20, 30]


def _annualised_sharpe(returns: pd.Series) -> float:
    sd = returns.std(ddof=0)
    if sd <= 0 or len(returns) < 2:
        return float("nan")
    return float(returns.mean() / sd * np.sqrt(TRADING_DAYS_PER_YEAR))


def rolling_sharpe_at_windows(
    returns: pd.Series,
    windows_years: list[int] = DEFAULT_WINDOWS_YEARS,
) -> dict[int, pd.Series]:
    """Compute rolling annualised Sharpe at each window size in years.

    Args:
        returns: daily returns Series, indexed by date.
        windows_years: window sizes in years (default 3/5/10/15/20/30).

    Returns:
        dict[year_window] -> rolling Sharpe Series. If the dataset is shorter
        than the window, the corresponding Series is empty.
    """
    out: dict[int, pd.Series] = {}
    n = len(returns)
    for w in windows_years:
        win_days = w * TRADING_DAYS_PER_YEAR
        if n < win_days:
            out[w] = pd.Series([], dtype=float, name=f"sharpe_{w}y")
            continue
        mu = returns.rolling(win_days).mean()
        sd = returns.rolling(win_days).std(ddof=0)
        sharpe = (mu / sd * np.sqrt(TRADING_DAYS_PER_YEAR)).dropna()
        sharpe.name = f"sharpe_{w}y"
        out[w] = sharpe
    return out


def rolling_outperformance_pct(
    strat_returns: pd.Series,
    bench_returns: pd.Series,
    windows_years: list[int] = DEFAULT_WINDOWS_YEARS,
) -> dict[int, dict[str, float]]:
    """Pct of rolling windows where strategy Sharpe > benchmark Sharpe.

    Both series are aligned on their common index before measuring. Each
    payload contains:
      - pct_strat_wins: fraction in [0, 1]
      - n_windows: total windows evaluated (0 if dataset shorter than window)
      - mean_sharpe_diff: mean (strat_sharpe - bench_sharpe) over the windows.
    """
    common = strat_returns.index.intersection(bench_returns.index)
    s = strat_returns.loc[common]
    b = bench_returns.loc[common]
    out: dict[int, dict[str, float]] = {}
    n = len(common)
    for w in windows_years:
        win_days = w * TRADING_DAYS_PER_YEAR
        if n < win_days:
            out[w] = {"pct_strat_wins": float("nan"), "n_windows": 0, "mean_sharpe_diff": float("nan")}
            continue
        s_mu, s_sd = s.rolling(win_days).mean(), s.rolling(win_days).std(ddof=0)
        b_mu, b_sd = b.rolling(win_days).mean(), b.rolling(win_days).std(ddof=0)
        s_sharpe = (s_mu / s_sd * np.sqrt(TRADING_DAYS_PER_YEAR)).dropna()
        b_sharpe = (b_mu / b_sd * np.sqrt(TRADING_DAYS_PER_YEAR)).dropna()
        common_w = s_sharpe.index.intersection(b_sharpe.index)
        s_w = s_sharpe.loc[common_w]
        b_w = b_sharpe.loc[common_w]
        wins = (s_w > b_w).sum()
        total = len(common_w)
        diff = (s_w - b_w).mean() if total > 0 else float("nan")
        out[w] = {
            "pct_strat_wins": float(wins) / total if total > 0 else float("nan"),
            "n_windows": int(total),
            "mean_sharpe_diff": float(diff),
        }
    return out


def fits_in_history(returns: pd.Series, windows_years: list[int]) -> list[int]:
    """Subset of `windows_years` that actually fit in the data."""
    n = len(returns)
    return [w for w in windows_years if n >= w * TRADING_DAYS_PER_YEAR]
