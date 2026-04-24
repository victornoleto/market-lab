"""Iter 024 — Bond-curve carry-driven duration timing on a 0.9 SPY + 0.6 bond stack.

Mechanism (carry as ALLOCATION signal, not haircut):

    sig_smoothed[t]  = T10Y3M_daily[t-21..t-1].mean()        (21-day SMA)
    sig_lagged[t]    = sig_smoothed[t-1]                      (1-bar lag, no look-ahead)
    alloc_TLT[t]     = clip(sig_lagged[t] / ramp_max_bps, 0, 1)
    alloc_SHV[t]     = 1 - alloc_TLT[t]

    pos_SPY[t]       = eq_w                                   (constant 0.9)
    pos_TLT[t]       = bd_w · alloc_TLT[t]                    (≤ 0.6)
    pos_SHV[t]       = bd_w · alloc_SHV[t]                    (≤ 0.6)
    pos_SPY + pos_TLT + pos_SHV ≡ eq_w + bd_w == 1.5          (constant total leverage)

    gross[t] = pos_SPY · r_SPY[t] + pos_TLT · r_TLT[t] + pos_SHV · r_SHV[t]
    cost[t]  = (|∆pos_SPY| + |∆pos_TLT| + |∆pos_SHV|) · cost_bps_per_leg
    net[t]   = gross[t] - cost[t]

Rebalance cadence is monthly (rebalance_bars=21): allocations are
recomputed only on rebalance bars and held constant in between, to
suppress turnover. The signal lag is enforced regardless of rebalance.

Citations
---------
* `[ilmanen_expected_returns, ch.6-7]` — term premium and roll-down carry.
* `[risk_parity, p.10-11, ch.1]` — fixed-weight risk parity (basis ratio).
* Koijen, Moskowitz, Pedersen & Vrugt (2018). "Carry." JFE 127(2), 197-225.
* Cochrane & Piazzesi (2005). "Bond Risk Premia." AER 95(1), 138-160.
* Estrella & Mishkin (1998). "Predicting U.S. Recessions." Restat 80(1), 45-61.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — no-lookahead lag rule.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_carry_allocation(
    signal: pd.Series,
    *,
    smoothing_days: int,
    lag_bars: int,
    ramp_max_bps: float,
) -> pd.Series:
    """Translate raw daily T10Y3M (in percentage units, e.g. 1.50 for 150 bps)
    into a dynamic ``alloc_TLT`` series in [0, 1].

    The signal is converted from percent to bps by ×100, smoothed by a
    rolling mean of ``smoothing_days``, lagged by ``lag_bars``, then
    linearly mapped to [0, 1] via ``clip(./ramp_max_bps, 0, 1)``.

    Parameters
    ----------
    signal : pd.Series
        Raw T10Y3M in percent units, indexed by trading date.
    smoothing_days : int
        Rolling SMA window (must be ≥ 1).
    lag_bars : int
        Number of bars to shift forward (≥ 0). 1 prevents look-ahead.
    ramp_max_bps : float
        Threshold (in bps) at which alloc_TLT saturates at 1.0.
        Below 0 bps it floors at 0.

    Returns
    -------
    pd.Series of alloc_TLT in [0, 1] with NaN for the warm-up region.
    """
    if smoothing_days < 1:
        raise ValueError(f"smoothing_days must be ≥ 1, got {smoothing_days}")
    if lag_bars < 0:
        raise ValueError(f"lag_bars must be ≥ 0, got {lag_bars}")
    if ramp_max_bps <= 0:
        raise ValueError(f"ramp_max_bps must be > 0, got {ramp_max_bps}")

    bps = signal.astype(float) * 100.0  # percent → bps
    smoothed = bps.rolling(smoothing_days, min_periods=smoothing_days).mean()
    lagged = smoothed.shift(lag_bars)
    alloc = (lagged / ramp_max_bps).clip(lower=0.0, upper=1.0)
    alloc.name = "alloc_TLT"
    return alloc


def apply_bond_carry_duration_timing(
    r_eq: pd.Series,
    r_tlt: pd.Series,
    r_shv: pd.Series,
    signal_t10y3m: pd.Series,
    *,
    eq_w: float = 0.9,
    bd_w: float = 0.6,
    smoothing_days: int = 21,
    lag_bars: int = 1,
    ramp_max_bps: float = 100.0,
    rebalance_bars: int = 21,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.DataFrame, pd.Series, pd.Series]:
    """Three-leg static-equity / dynamic-bond stack with carry-driven duration.

    Parameters
    ----------
    r_eq, r_tlt, r_shv : pd.Series
        Daily simple-return streams. Must share an inner-joinable index.
    signal_t10y3m : pd.Series
        Raw daily T10Y3M term-spread in percent units (FRED convention).
    eq_w : float
        Static equity-leg weight (default 0.9, NTSX prospectus).
    bd_w : float
        Static bond-leg weight (default 0.6); split between TLT and SHV
        according to the carry signal.
    smoothing_days : int
        SMA window applied to the T10Y3M signal (default 21).
    lag_bars : int
        Bars of lag enforced on the smoothed signal (default 1).
    ramp_max_bps : float
        T10Y3M threshold (in bps) at which alloc_TLT saturates at 1.0.
    rebalance_bars : int
        Re-compute allocations every ``rebalance_bars`` bars; in between,
        hold allocations constant. Default 21 (≈ monthly).
    cost_bps_per_leg : float
        Linear cost per unit of per-leg ∆position. Default 2 bps.

    Returns
    -------
    (net_returns, positions_df, scale, alloc_tlt)
        ``net_returns`` : pd.Series of net daily returns after cost.
        ``positions_df`` : pd.DataFrame columns ["EQ", "TLT", "SHV"].
        ``scale`` : pd.Series equal to eq_w + bd_w (constant).
        ``alloc_tlt`` : pd.Series of the bond-leg's TLT fraction in [0, 1].
    """
    if eq_w < 0 or bd_w < 0:
        raise ValueError(f"weights must be non-negative; got eq={eq_w} bd={bd_w}")
    if rebalance_bars < 1:
        raise ValueError(f"rebalance_bars must be ≥ 1, got {rebalance_bars}")

    # Align all 4 streams on intersection of indices.
    df = pd.concat(
        {"eq": r_eq, "tlt": r_tlt, "shv": r_shv, "sig": signal_t10y3m},
        axis=1, join="inner",
    ).dropna(subset=["eq", "tlt", "shv"])  # signal NaN handled by allocation

    if len(df) == 0:
        raise ValueError("no overlapping bars across r_eq, r_tlt, r_shv, signal")

    # Compute alloc_TLT from the (still possibly partial) signal column.
    alloc_full = compute_carry_allocation(
        df["sig"],
        smoothing_days=smoothing_days,
        lag_bars=lag_bars,
        ramp_max_bps=ramp_max_bps,
    )

    # Drop bars with NaN alloc (warm-up of smoothing+lag) — keep the rest.
    keep = alloc_full.notna()
    df = df.loc[keep]
    alloc = alloc_full.loc[keep]

    # Apply monthly rebalance: hold alloc constant between rebalance bars.
    n = len(df)
    rebal_idx = np.arange(0, n, rebalance_bars)
    held = pd.Series(np.nan, index=df.index, dtype=float)
    for i, k in enumerate(rebal_idx):
        end = rebal_idx[i + 1] if i + 1 < len(rebal_idx) else n
        held.iloc[k:end] = float(alloc.iloc[k])
    alloc_held = held

    # Per-leg positions.
    pos_eq = pd.Series(eq_w, index=df.index, dtype=float)
    pos_tlt = (bd_w * alloc_held).astype(float)
    pos_shv = (bd_w * (1.0 - alloc_held)).astype(float)

    # Gross + cost + net.
    gross = pos_eq * df["eq"] + pos_tlt * df["tlt"] + pos_shv * df["shv"]

    # Cost: |∆pos| × cost_bps. Initial bar charged against zero.
    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    dpos_shv = pos_shv.diff().abs().fillna(pos_shv.iloc[0])
    cost = (dpos_eq + dpos_tlt + dpos_shv) * cost_bps_per_leg

    net = (gross - cost).astype(float)
    net.name = "net"

    positions = pd.DataFrame(
        {"EQ": pos_eq, "TLT": pos_tlt, "SHV": pos_shv}, index=df.index,
    )
    scale = pos_eq + pos_tlt + pos_shv
    scale.name = "scale"
    return net, positions, scale, alloc_held.rename("alloc_TLT")
