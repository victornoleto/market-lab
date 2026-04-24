"""Numpy-pure reference for iter 022 TOM overlay (G7 parity check).

Recomputes the TOM-modulated static-stack vol-managed net return stream
using only numpy arithmetic — no pandas rolling, no cov, no groupby.
Used to cross-verify the primary pandas implementation via ``G7
cross-lib ±3 pp CAGR``.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library validation gate.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def _tom_flag_numpy(index: pd.DatetimeIndex, last_n: int, first_n: int) -> np.ndarray:
    """Compute TOM flag using calendar-absolute business-day rank.

    Mirrors the pandas primitive's semantic: for each bar, compute its
    position within its CALENDAR month's business-day sequence (using
    pd.bdate_range for that month), then flag if in first_n or last_n.
    This is robust to index subsetting.
    """
    n = len(index)
    flag = np.zeros(n, dtype=bool)
    idx = pd.DatetimeIndex(index)
    # Cache ym → (first_set, last_set).
    yms = set(zip(idx.year.tolist(), idx.month.tolist()))
    month_windows: dict[tuple[int, int], tuple[set, set]] = {}
    for y, m in yms:
        start = pd.Timestamp(year=y, month=m, day=1)
        end = start + pd.offsets.MonthEnd(1)
        bdays = pd.bdate_range(start, end)
        first_set = set(bdays[:first_n]) if first_n > 0 else set()
        last_set = set(bdays[-last_n:]) if last_n > 0 else set()
        month_windows[(y, m)] = (first_set, last_set)
    for i, ts in enumerate(idx):
        f_s, l_s = month_windows[(ts.year, ts.month)]
        if ts in f_s or ts in l_s:
            flag[i] = True
    return flag


def tom_static_stack_vm_numpy(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    *,
    index: pd.DatetimeIndex,
    eq_weight_tom: float,
    eq_weight_mid: float,
    bd_weight_tom: float,
    bd_weight_mid: float,
    tom_last_n: int,
    tom_first_n: int,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> np.ndarray:
    """Return the net return stream using only numpy (no pandas ops)."""
    r_eq = np.asarray(r_eq, dtype=float)
    r_bd = np.asarray(r_bd, dtype=float)
    n = len(r_eq)
    if len(r_bd) != n:
        raise ValueError("r_eq and r_bd must have same length")
    if n <= lookback:
        raise ValueError(f"need > {lookback} bars, got {n}")

    # Drop NaN rows (per-element, both legs required).
    mask = ~(np.isnan(r_eq) | np.isnan(r_bd))
    r_eq_m = r_eq[mask]
    r_bd_m = r_bd[mask]
    idx_m = index[mask]
    n_m = len(r_eq_m)
    if n_m <= lookback:
        raise ValueError(f"need > {lookback} overlapping bars after NaN mask, got {n_m}")

    # TOM flag per bar.
    tom = _tom_flag_numpy(idx_m, last_n=tom_last_n, first_n=tom_first_n)

    # Normalise weight pairs.
    sum_tom = eq_weight_tom + bd_weight_tom
    sum_mid = eq_weight_mid + bd_weight_mid
    w_eq_tom = eq_weight_tom / sum_tom
    w_bd_tom = bd_weight_tom / sum_tom
    w_eq_mid = eq_weight_mid / sum_mid
    w_bd_mid = bd_weight_mid / sum_mid
    w_eq = np.where(tom, w_eq_tom, w_eq_mid)
    w_bd = np.where(tom, w_bd_tom, w_bd_mid)

    # Rolling σ̂² with lookback, shifted by 1 bar (σ̂_{t-1}).
    var_eq = np.full(n_m, np.nan)
    var_bd = np.full(n_m, np.nan)
    cov_eb = np.full(n_m, np.nan)
    for t in range(lookback, n_m):
        win_eq = r_eq_m[t - lookback:t]
        win_bd = r_bd_m[t - lookback:t]
        var_eq[t] = float(np.var(win_eq, ddof=0)) * periods_per_year
        var_bd[t] = float(np.var(win_bd, ddof=0)) * periods_per_year
        # Covariance matching pandas cov(ddof=0) — population cov.
        m_eq = win_eq.mean()
        m_bd = win_bd.mean()
        cov_eb[t] = float(((win_eq - m_eq) * (win_bd - m_bd)).mean()) * periods_per_year

    # σ²_port[t] with today's projected weights + yesterday's per-leg σ̂².
    var_port = (
        w_eq ** 2 * var_eq
        + w_bd ** 2 * var_bd
        + 2.0 * w_eq * w_bd * cov_eb
    )
    var_port = np.clip(var_port, 0.0, None)

    target_var = target_vol ** 2
    scale = np.full(n_m, np.nan)
    valid = ~np.isnan(var_port)
    scale[valid & (var_port > 0)] = target_var / var_port[valid & (var_port > 0)]
    scale[valid & (var_port == 0)] = max_leverage
    # Clip to [0, max_leverage].
    scale = np.where(np.isnan(scale), np.nan, np.clip(scale, 0.0, max_leverage))

    # Build gross/cost on rows where scale is defined.
    valid_idx = ~np.isnan(scale)
    pos_eq = np.where(valid_idx, scale * w_eq, np.nan)
    pos_bd = np.where(valid_idx, scale * w_bd, np.nan)
    gross = pos_eq * r_eq_m + pos_bd * r_bd_m

    # Turnover cost: ∆pos.
    dpos_eq = np.full(n_m, np.nan)
    dpos_bd = np.full(n_m, np.nan)
    prev_eq = np.nan
    prev_bd = np.nan
    for t in range(n_m):
        if valid_idx[t]:
            if np.isnan(prev_eq):
                dpos_eq[t] = pos_eq[t]
                dpos_bd[t] = pos_bd[t]
            else:
                dpos_eq[t] = abs(pos_eq[t] - prev_eq)
                dpos_bd[t] = abs(pos_bd[t] - prev_bd)
            prev_eq = pos_eq[t]
            prev_bd = pos_bd[t]
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg
    net = gross - cost
    # Drop rows where scale not yet defined.
    net = net[valid_idx]
    return net
