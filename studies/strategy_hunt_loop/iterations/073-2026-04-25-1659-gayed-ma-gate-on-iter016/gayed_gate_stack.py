"""Iter 073 — Gayed (2016) 200-day MA regime gate on iter 016 vol-managed stack.

Architecture
------------

Layer 1 (iter 016): Static-ratio (eq_w / bd_w) × Moreira-Muir
portfolio variance-target scaling on SPY+IEF.

Layer 2 (iter 073): Binary regime gate from Gayed (2016) 200-day SMA
on the equity symbol. Gate-on → run iter 016 stack with full sizing.
Gate-off → 100% IEF allocation (NOT cash — captures duration safe-
haven during recession rate-cut rallies).

::

    SMA[t]      = mean(close_eq[t-MA_period .. t-1])     (no peek; uses [t-MA, t-1])
    gate_on[t]  = close_eq[t-1] > SMA[t-1]               (strict; aligned at t-1)
    σ²_port[t-1] inherits iter 016's lagged formula.
    scale[t]    = clip(target_vol² / σ²_port[t-1], 0, max_leverage)
    pos_eq[t]   = w_eq · scale[t] · 1{gate_on[t]}
    pos_bd[t]   = w_bd · scale[t] · 1{gate_on[t]} + 1.0 · 1{not gate_on[t]}
    cost[t]     = (|Δpos_eq| + |Δpos_bd|) · cost_bps_per_leg
    r_073[t]    = pos_eq[t]·r_eq[t] + pos_bd[t]·r_bd[t] - cost[t]

Citations
---------
* Gayed (2016) — `[leverage_for_the_long_run, p.13, p.16, p.21]`.
* `[risk_parity, p.10-11, ch.1]` — fixed-weight risk-parity primitive.
* `[risk_parity, p.80-81, ch.4]` — SPY-bond anti-corr → IEF off-market.
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
* `[systematic_trading, p.170-171, ch.11]` — Carver IDM ≤ 2.5.
* Moreira & Muir (2017). "Volatility-Managed Portfolios."
* `[advances_fin_ml, p.162-164]` — strict shift(1) on signal (no peek).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_gayed_gate_stack(
    r_eq: pd.Series,
    r_bd: pd.Series,
    px_eq: pd.Series,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    ma_period: int = 200,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Apply the iter 073 Gayed-gate × vol-managed stack.

    Parameters
    ----------
    r_eq, r_bd : pd.Series
        Aligned daily simple-return streams for the equity (SPY/QQQ) and
        bond (IEF) legs. Must share the same DatetimeIndex.
    px_eq : pd.Series
        Equity-leg adjusted close prices, indexed by the same dates as
        ``r_eq``. Used for the 200-day SMA gate signal.
    eq_weight, bd_weight : float
        Fixed normalised per-leg weights for the on-market state.
        Defaults aligned with iter 016: 0.6 / 0.4.
    target_vol : float
        Target annualised portfolio volatility for the on-market state.
    lookback : int
        σ̂² rolling-window length in bars. Must be ≥ 2.
    max_leverage : float
        Upper bound on total gross exposure (scale[t]). Must be > 0.
        Should respect IDM ≤ 2.5 (Carver).
    ma_period : int
        Gayed canonical 200; alternatives 10/20/50/100. Must be ≥ 2.
    periods_per_year : int
        Annualisation factor. Default 252.
    cost_bps_per_leg : float
        Linear cost per unit of per-leg ∆position. Default 2 bps.

    Returns
    -------
    (net, pos_eq, pos_bd, scale, gate_on)
        All indexed on the valid bars (warm-up dropped).
        ``net`` is daily net returns (after cost).
        ``pos_eq``, ``pos_bd`` are per-leg gross positions.
        ``scale`` is the on-market gross exposure (NaN dropped).
        ``gate_on`` is the boolean regime indicator (lagged 1 bar).
    """
    if eq_weight < 0 or bd_weight < 0:
        raise ValueError(
            f"weights must be non-negative; got eq={eq_weight} bd={bd_weight}"
        )
    total_w = eq_weight + bd_weight
    if total_w <= 0:
        raise ValueError(
            f"eq_weight + bd_weight must be > 0; got {total_w}"
        )
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if ma_period < 2:
        raise ValueError(f"ma_period must be ≥ 2, got {ma_period}")
    if not r_eq.index.equals(r_bd.index):
        raise ValueError("r_eq and r_bd must share the same index")
    if not r_eq.index.equals(px_eq.index):
        raise ValueError("px_eq must share the same index as r_eq")

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    p = px_eq.astype(float)
    mask = a.notna() & b.notna() & p.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    p = p.loc[mask]
    warmup = max(lookback, ma_period) + 1
    if len(a) <= warmup:
        raise ValueError(
            f"need > {warmup} overlapping bars, got {len(a)}"
        )

    w_eq = eq_weight / total_w
    w_bd = bd_weight / total_w

    # Layer 1: vol-managed scaling (inherits iter 016 logic exactly).
    ann_var_eq = (
        a.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_var_bd = (
        b.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_cov = (
        a.rolling(lookback, min_periods=lookback).cov(b, ddof=0)
        * periods_per_year
    ).shift(1)

    ann_var_port = (
        w_eq ** 2 * ann_var_eq
        + w_bd ** 2 * ann_var_bd
        + 2.0 * w_eq * w_bd * ann_cov
    ).clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=a.index, dtype=float)
    mask_valid = ann_var_port.notna()
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage
    scale = raw_scale.clip(lower=0.0, upper=max_leverage)

    # Layer 2: Gayed (2016) 200-day SMA regime gate.
    # SMA computed on prior MA_period closes; both SMA and px_eq are
    # shifted by 1 bar to enforce no-peek (signal at t uses info ≤ t-1).
    sma = p.rolling(ma_period, min_periods=ma_period).mean()
    px_lag = p.shift(1)
    sma_lag = sma.shift(1)
    gate_on_raw = (px_lag > sma_lag).astype(float)
    # Where we cannot evaluate the gate (warm-up), force NaN so the
    # alignment-drop step removes those bars cleanly.
    gate_on_raw = gate_on_raw.where(sma_lag.notna() & px_lag.notna())

    # Combine warm-ups: drop bars where ANY of (scale, gate_on) is NaN.
    keep_mask = scale.notna() & gate_on_raw.notna()
    scale = scale.loc[keep_mask]
    gate_on = gate_on_raw.loc[keep_mask].astype(bool)

    # On-market positions (iter 016 vol-managed sizing × gate indicator).
    on_eq = (scale * w_eq).where(gate_on, other=0.0)
    on_bd = (scale * w_bd).where(gate_on, other=0.0)
    # Off-market: 100% IEF allocation.
    off_bd = pd.Series(0.0, index=scale.index, dtype=float)
    off_bd.loc[~gate_on] = 1.0
    pos_eq = on_eq.astype(float)
    pos_bd = (on_bd + off_bd).astype(float)

    a_v = a.loc[scale.index]
    b_v = b.loc[scale.index]
    gross = pos_eq * a_v + pos_bd * b_v

    dpos_eq = pos_eq.diff().abs().fillna(pos_eq.iloc[0])
    dpos_bd = pos_bd.diff().abs().fillna(pos_bd.iloc[0])
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    net.name = "net"
    pos_eq.name = "pos_eq"
    pos_bd.name = "pos_bd"
    scale.name = "scale"
    gate_on.name = "gate_on"
    return net, pos_eq, pos_bd, scale, gate_on
