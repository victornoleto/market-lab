"""Iter 011 — Weekly-rebalance 3-leg vol-managed blend.

Thin wrapper on iter 010's ``apply_blend_variance_target_3leg`` that
first resamples daily returns to weekly (W-FRI last-close) and then
applies the identical inverse-variance + Moreira-Muir variance-scaling
mechanism with ``periods_per_year=52``.

The resample preserves the compound-return identity:

    weekly_ret_t = prod_{d in week t}(1 + daily_ret_d) - 1

This is achieved by compounding daily returns inside each W-FRI block
(equivalent to last-close-to-last-close on daily prices). No
look-ahead: the weekly bar for week ending Friday ``F`` uses exactly
the daily returns Mon-Fri of that week.

Citations
---------
* `[systematic_trading, p.144, ch.9]` — target_vol is cadence-
  independent.
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity applies at any
  sampling frequency.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling was derived
  on *monthly* returns; weekly (52 obs/yr) is closer to their native
  regime than daily (252 obs/yr).
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag on whichever cadence.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER_10_DIR = ITER_DIR.parent / "010-2026-04-24-1506-three-asset-spy-tlt-gld-blend"
sys.path.insert(0, str(ITER_10_DIR))

from three_leg_blend import apply_blend_variance_target_3leg  # noqa: E402


def resample_returns_weekly(daily_returns: pd.DataFrame) -> pd.DataFrame:
    """Compound daily returns into W-FRI weekly returns.

    Uses a closed-form compounding per W-FRI block: within each week
    ending on Friday F, ``weekly_ret = prod(1 + daily_ret) - 1``. If
    a given Friday is a holiday, the weekly bar is labelled with the
    calendar Friday and reflects the compound of remaining bars in
    that week (i.e. Mon-Thu).

    Parameters
    ----------
    daily_returns : pd.DataFrame
        DatetimeIndex of daily return streams, one column per leg.

    Returns
    -------
    pd.DataFrame
        Same columns; index is W-FRI DatetimeIndex. Any all-NaN weekly
        rows (no daily data that week) are dropped.
    """
    if not isinstance(daily_returns.index, pd.DatetimeIndex):
        raise TypeError(
            f"daily_returns index must be DatetimeIndex, got {type(daily_returns.index)}"
        )
    if daily_returns.empty:
        return daily_returns.copy()
    # Compound: prod(1+r) - 1 per W-FRI block.
    weekly = (1.0 + daily_returns).resample("W-FRI").prod() - 1.0
    # Any weekly bar that had NO daily observations should be dropped
    # (pandas fills empty resamples with NaN or 0; be robust).
    # A safer approach: use a mask of "any daily bar present in week"
    # and drop false rows.
    count = daily_returns.resample("W-FRI").count().sum(axis=1)
    weekly = weekly.loc[count > 0]
    return weekly


def apply_weekly_blend(
    r_spy_daily: pd.Series,
    r_tlt_daily: pd.Series,
    r_gld_daily: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series]:
    """Run the iter 010 3-leg blend on weekly-resampled returns.

    Parameters are identical in meaning to iter 010's
    ``apply_blend_variance_target_3leg`` except ``lookback`` is
    interpreted in **weekly bars** and annualisation uses
    ``periods_per_year=52``.
    """
    daily = pd.concat(
        {"SPY": r_spy_daily, "TLT": r_tlt_daily, "GLD": r_gld_daily},
        axis=1, join="inner",
    ).dropna()
    weekly = resample_returns_weekly(daily)
    weekly.columns = ["SPY", "TLT", "GLD"]
    return apply_blend_variance_target_3leg(
        weekly["SPY"], weekly["TLT"], weekly["GLD"],
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=52,
        cost_bps_per_leg=cost_bps_per_leg,
    )
