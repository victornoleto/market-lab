"""G7 cross-lib reference — pure-numpy weekly 3-leg blend.

Re-implements the weekly wrapper using only numpy loops (including a
hand-coded W-FRI resample from daily timestamps). Used by G7 to verify
pandas-engine CAGR agrees to ≤ 3 pp per `[advances_fin_ml, p.31-34]`.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling canonical form
  on monthly data; weekly is closer to this regime than daily.
* `[advances_fin_ml, p.31-34]` — cross-lib parity as correctness gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ITER_10_DIR = ITER_DIR.parent / "010-2026-04-24-1506-three-asset-spy-tlt-gld-blend"
sys.path.insert(0, str(ITER_10_DIR))

from numpy_reference_3leg import (  # noqa: E402
    apply_blend_variance_target_3leg_np,
    cagr_np,
    sharpe_np,
    max_drawdown_np,
)


def _weekly_resample_np(
    dates: np.ndarray, returns_3col: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Hand-coded W-FRI compound resample using numpy + pandas date arithmetic.

    Returns (weekly_friday_dates, weekly_returns_3col) with the same
    semantics as ``resample_returns_weekly`` in the pandas wrapper.
    """
    ts = pd.DatetimeIndex(dates)
    # Compute the Friday of each week for every daily timestamp.
    # dayofweek: Mon=0, ..., Fri=4, Sat=5, Sun=6.
    dow = ts.dayofweek.to_numpy()
    # Days to add to reach Friday of this week: (4 - dow) % 7 gives 0 if dow<=4,
    # but we want to snap forward to Friday only if dow<=4, or else next week.
    # Simpler: use pandas-equivalent "W-FRI" which is the label of the week
    # the timestamp belongs to (week ends on Friday).
    # Pandas convention for W-FRI resample labels week by its Friday end-date.
    # We replicate: for each timestamp, compute the Friday >= ts.date.
    # If dow <= 4: add (4 - dow) days; else (wrap to next week): add (4 + 7 - dow).
    offset = np.where(dow <= 4, 4 - dow, 11 - dow)
    week_labels = (ts + pd.to_timedelta(offset, unit="D")).to_numpy()

    unique_weeks, inverse_idx = np.unique(week_labels, return_inverse=True)
    n_weeks = len(unique_weeks)
    n_legs = returns_3col.shape[1]
    weekly = np.zeros((n_weeks, n_legs), dtype=float)
    counts = np.zeros(n_weeks, dtype=np.int64)
    # Compound within each week: weekly_return = prod(1 + daily) - 1.
    # Compute prod of (1 + r) grouped by inverse_idx, then -1.
    log1p = np.log1p(returns_3col)
    for k in range(n_weeks):
        mask = inverse_idx == k
        counts[k] = int(mask.sum())
        block = log1p[mask]
        if block.size == 0:
            weekly[k] = 0.0
        else:
            weekly[k] = np.expm1(block.sum(axis=0))
    # Drop weeks with zero observations.
    keep = counts > 0
    return unique_weeks[keep], weekly[keep]


def apply_weekly_blend_np(
    daily_dates: np.ndarray,
    r_spy_daily: np.ndarray,
    r_tlt_daily: np.ndarray,
    r_gld_daily: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy pipeline: resample daily → weekly, then apply iter 010
    numpy 3-leg blend with ``periods_per_year=52``.

    Returns ``(weekly_friday_dates, net_returns, positions, scale)``.
    """
    ret_stack = np.column_stack([r_spy_daily, r_tlt_daily, r_gld_daily])
    mask = ~np.any(np.isnan(ret_stack), axis=1)
    ret_stack = ret_stack[mask]
    dates_masked = np.asarray(daily_dates)[mask]

    weekly_fri, weekly_ret = _weekly_resample_np(dates_masked, ret_stack)
    net, pos, scale = apply_blend_variance_target_3leg_np(
        weekly_ret[:, 0],
        weekly_ret[:, 1],
        weekly_ret[:, 2],
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=52,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    # net is valid-bars-only (iter 010 numpy reference drops pre-lookback);
    # the corresponding weekly dates are the trailing len(net) entries.
    valid_weekly_fri = weekly_fri[-len(net):] if len(net) > 0 else weekly_fri[:0]
    return valid_weekly_fri, net, pos, scale


def cagr_weekly_np(returns: np.ndarray) -> float:
    """CAGR on weekly returns (52/yr)."""
    return cagr_np(returns, periods_per_year=52)


def sharpe_weekly_np(returns: np.ndarray, risk_free: float = 0.0) -> float:
    """Sharpe on weekly returns (√52 annualisation)."""
    return sharpe_np(returns, periods_per_year=52, risk_free=risk_free)
