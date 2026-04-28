"""Iter 016 — Static-ratio × Moreira-Muir vol-managed hybrid stack.

Combines iter 015's fixed 60:40 stacking ratio with iter 008's Moreira-
Muir portfolio-level variance-target scaling. The RATIO between legs is
locked (equity always 60% of total gross exposure, bond always 40%); the
TOTAL gross exposure rescales each bar by

    σ²_port[t-1] = w_eq²·σ²_eq[t-1] + w_bd²·σ²_bd[t-1]
                 + 2·w_eq·w_bd·cov_eq_bd[t-1]
    scale[t]     = clip(target_vol² / σ²_port[t-1], 0, max_leverage)
    pos_eq[t]    = w_eq · scale[t]   (default w_eq=0.6 → 0.9 at scale=1.5)
    pos_bd[t]    = w_bd · scale[t]   (default w_bd=0.4 → 0.6 at scale=1.5)

The crucial difference from iter 008's ``apply_blend_variance_target``
is that iter 008 dynamically reweights between legs using inverse
variance (w changes every bar), whereas iter 016 LOCKS the ratio
constant (w_eq=0.6, w_bd=0.4 forever) — inheriting iter 015's
cointegration-free structural property and layering only the overall
exposure scale from iter 008.

When ``max_leverage = eq_w + bd_w`` and ``target_vol = ∞``, scale is
always pinned to the cap, reproducing iter 015's constant 1.5× static
stack exactly.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity + fixed-weight stack.
* `[risk_parity, p.80-81, ch.4]` — negative SPY-bond correlation drives
  diversification benefit.
* `[systematic_trading, p.40, ch.2]` — volatility standardisation primitive.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 hard cap on leverage.
* Moreira & Muir (2017) JoF 72(4), 1611-1644 — variance-target scaling.
* `[advances_fin_ml, p.162-164]` — ``σ̂_{t-1}`` lag (no look-ahead).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_static_stack_vol_managed(
    r_eq: pd.Series,
    r_bd: pd.Series,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Two-leg fixed-ratio stack with Moreira-Muir variance-target scaling.

    Parameters
    ----------
    r_eq, r_bd : pd.Series
        Aligned daily simple-return streams for equity and bond legs.
        Must share the same DatetimeIndex.
    eq_weight, bd_weight : float
        FIXED normalised per-leg weights. Must be non-negative and sum
        to a positive number. Defaults (iter 016 pre-committed cfg):
        0.6 / 0.4. These are the FRACTIONS of the dynamic scale that
        each leg takes; e.g. when scale=1.5, pos_eq = 0.9, pos_bd = 0.6
        (reproducing iter 015 exactly).
    target_vol : float
        Target annualised portfolio volatility (e.g. 0.15 for 15%).
        Must be > 0.
    lookback : int
        Rolling-window length in bars for σ̂². Must be ≥ 2.
    max_leverage : float
        Upper bound on total gross exposure (scale[t]). Must be > 0.
        Keep ≤ 2.5 to respect IDM (Carver ch.11).
    periods_per_year : int
        Annualisation factor. Default 252.
    cost_bps_per_leg : float
        Linear cost per unit of per-leg ∆position. Default 2 bps.

    Returns
    -------
    (net_returns, pos_eq, pos_bd, scale)
        All indexed on the valid bars (first ``lookback`` dropped).
        ``net_returns`` : pd.Series of net daily returns (after cost).
        ``pos_eq``, ``pos_bd`` : pd.Series of per-leg gross positions.
        ``scale`` : pd.Series of total gross exposure (pos_eq + pos_bd).

    Raises
    ------
    ValueError
        If params are out of domain, legs are misaligned, or there are
        fewer than ``lookback + 1`` overlapping bars.
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
    if not r_eq.index.equals(r_bd.index):
        raise ValueError(
            "r_eq and r_bd must share the same index "
            f"(eq {len(r_eq)} bars {r_eq.index[0]}→{r_eq.index[-1]} vs "
            f"bd {len(r_bd)} bars {r_bd.index[0]}→{r_bd.index[-1]})"
        )

    a = r_eq.astype(float)
    b = r_bd.astype(float)
    mask = a.notna() & b.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    if len(a) <= lookback:
        raise ValueError(f"need > {lookback} overlapping bars, got {len(a)}")

    # Normalise weights so eq_weight + bd_weight = 1 internally.
    # (Callers pass already-normalised 0.6 / 0.4 by default; explicit
    # normalisation protects against callers passing the iter 015 raw
    # weights 0.9 / 0.6 by mistake — we divide by total in that case.)
    w_eq = eq_weight / total_w
    w_bd = bd_weight / total_w

    # Rolling annualised variance / covariance, shifted by 1 bar (σ̂²_{t-1}).
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

    # Portfolio annualised variance with FIXED normalised weights.
    ann_var_port = (
        w_eq ** 2 * ann_var_eq
        + w_bd ** 2 * ann_var_bd
        + 2.0 * w_eq * w_bd * ann_cov
    )
    # Guard against floating-point negatives from sample cov.
    ann_var_port = ann_var_port.clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=a.index, dtype=float)
    mask_valid = ann_var_port.notna()
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage  # σ²_port == 0 → full cap

    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()

    pos_eq = (scale * w_eq).astype(float)
    pos_bd = (scale * w_bd).astype(float)

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
    return net, pos_eq, pos_bd, scale
