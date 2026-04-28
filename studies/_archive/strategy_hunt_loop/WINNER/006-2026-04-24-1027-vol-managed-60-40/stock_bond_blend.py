"""Iter 006 — Vol-managed 60/40 SPY+TLT with inverse-variance weighting.

Two-asset blend sized by naïve risk parity (inverse variance per leg)
with a Moreira-Muir portfolio-level variance-scaling cap on top.

Formulation (at each bar ``t``, using returns from ``[t-L, t-1]``):

    σ²_spy   = var(r_spy[t-L:t]) · 252
    σ²_tlt   = var(r_tlt[t-L:t]) · 252

    # Naïve risk parity weights [risk_parity, p.10-11, ch.1]:
    w_spy_t  = (1/σ²_spy) / (1/σ²_spy + 1/σ²_tlt)
    w_tlt_t  = 1 − w_spy_t

    # Portfolio realised variance (weighted blend over the window):
    r_port[t-L:t] = w_spy_t · r_spy[t-L:t] + w_tlt_t · r_tlt[t-L:t]
    σ²_port      = var(r_port) · 252

    # Moreira-Muir total leverage scale:
    s_t      = clip(target_vol² / σ²_port, 0, max_leverage)

    # Final leg positions (sum = s_t):
    pos_spy_t = s_t · w_spy_t
    pos_tlt_t = s_t · w_tlt_t

    # Return stream:
    gross_t  = pos_spy_t · r_spy[t] + pos_tlt_t · r_tlt[t]
    cost_t   = (|ΔPos_spy| + |ΔPos_tlt|) · cost_bps_per_leg
    net_t    = gross_t − cost_t

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity is exact ERC for
  two-asset portfolios.
* `[risk_parity, p.80-81, ch.4]` — negative SPY-TLT correlation is the
  diversification axis this sizing exploits.
* `[systematic_trading, p.40, ch.2]` — volatility standardisation is
  the core primitive.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 hard cap on
  total gross exposure.
* Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — variance-scaling form.
* `[advances_fin_ml, p.162-164]` — ``σ̂_{t-1}`` lag (no look-ahead).

This module stays inside the iter 006 folder. If the mechanism proves
to be the winner a follow-up PR promotes a cleaned version into
``src/ai_trade/backtest/metrics/``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_blend_variance_target(
    r_spy: pd.Series,
    r_tlt: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Two-leg inverse-variance-weighted + Moreira-Muir portfolio scaling.

    Parameters
    ----------
    r_spy, r_tlt : pd.Series
        Aligned daily return streams for the two legs. Must share the
        same index.
    target_vol : float
        Target annualised portfolio volatility (e.g. 0.15 for 15%). Must
        be positive. Implies ``c = target_vol²``.
    lookback : int
        Rolling-window length in bars. Must be ≥ 2.
    max_leverage : float
        Upper bound on total gross exposure (``s_t``). Must be > 0. Since
        leg weights sum to 1, this also bounds the sum of leg positions.
        Keep ≤ 2.5 to respect IDM (Carver ch.11).
    periods_per_year : int
        Annualisation factor. Default 252.
    cost_bps_per_leg : float
        Cost per unit of per-leg position change. Default 0.0002 (2 bps).

    Returns
    -------
    (net_returns, pos_spy, pos_tlt, scale)
        All indexed on the valid bars (first ``lookback`` dropped).

    Raises
    ------
    ValueError
        If params are out of domain, the two legs are mis-aligned, or
        there are fewer than ``lookback + 1`` overlapping bars.
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")
    if not r_spy.index.equals(r_tlt.index):
        raise ValueError(
            "r_spy and r_tlt must share the same index "
            f"(spy {len(r_spy)} bars {r_spy.index[0]}→{r_spy.index[-1]} vs "
            f"tlt {len(r_tlt)} bars {r_tlt.index[0]}→{r_tlt.index[-1]})"
        )

    a = r_spy.astype(float)
    b = r_tlt.astype(float)
    mask = a.notna() & b.notna()
    a = a.loc[mask]
    b = b.loc[mask]
    if len(a) <= lookback:
        raise ValueError(f"need > {lookback} overlapping bars, got {len(a)}")

    # Rolling annualised variance per leg, shifted by 1 bar (σ̂²_{t-1}).
    ann_var_spy = (
        a.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_var_tlt = (
        b.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)

    # Naïve risk parity weights. Handle σ²==0 gracefully:
    # - both zero → split 50/50 (degenerate).
    # - one zero → that leg takes 100% weight (the finite-vol one gets 0).
    #   (Inverse variance of zero is +∞ → normalises to 1.)
    w_spy = pd.Series(np.nan, index=a.index, dtype=float)
    both_pos = (ann_var_spy > 0) & (ann_var_tlt > 0)
    only_spy_zero = (ann_var_spy == 0) & (ann_var_tlt > 0)
    only_tlt_zero = (ann_var_spy > 0) & (ann_var_tlt == 0)
    both_zero = (ann_var_spy == 0) & (ann_var_tlt == 0)

    inv_a = 1.0 / ann_var_spy.where(both_pos)
    inv_b = 1.0 / ann_var_tlt.where(both_pos)
    w_spy.loc[both_pos] = inv_a.loc[both_pos] / (inv_a.loc[both_pos] + inv_b.loc[both_pos])
    w_spy.loc[only_spy_zero] = 1.0  # infinite inverse-var on spy → 100%
    w_spy.loc[only_tlt_zero] = 0.0  # infinite inverse-var on tlt → 0%
    w_spy.loc[both_zero] = 0.5       # symmetric degenerate

    w_tlt = 1.0 - w_spy

    # Portfolio realised variance (weighted blend over the window, weights
    # constant within the window == values of w_spy_t at the output bar).
    # Implementation: compute variance of the historical weighted blend
    # using the formula σ²_port = w_spy²·σ²_spy + w_tlt²·σ²_tlt + 2·w_spy·w_tlt·cov.
    # Cov needs a separate rolling step; since both legs already have their
    # rolling σ², adding a rolling covariance finishes it.
    cov_ab = (
        a.rolling(lookback, min_periods=lookback).cov(b, ddof=0)
        * periods_per_year
    ).shift(1)

    ann_var_port = (
        w_spy ** 2 * ann_var_spy
        + w_tlt ** 2 * ann_var_tlt
        + 2.0 * w_spy * w_tlt * cov_ab
    )

    # Guard against floating-point negatives from cov estimator (should
    # be ≥ 0 analytically but finite samples can drift slightly below).
    ann_var_port = ann_var_port.clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=a.index, dtype=float)
    mask_valid = ann_var_port.notna()
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_port.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_leverage  # σ²_port == 0 → full cap

    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()
    w_spy_v = w_spy.loc[scale.index]
    w_tlt_v = w_tlt.loc[scale.index]
    pos_spy = (scale * w_spy_v).astype(float)
    pos_tlt = (scale * w_tlt_v).astype(float)

    a_v = a.loc[scale.index]
    b_v = b.loc[scale.index]
    gross = pos_spy * a_v + pos_tlt * b_v

    dpos_spy = pos_spy.diff().abs().fillna(pos_spy.iloc[0])
    dpos_tlt = pos_tlt.diff().abs().fillna(pos_tlt.iloc[0])
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = (gross - cost).astype(float)

    net.name = "net"
    pos_spy.name = "pos_spy"
    pos_tlt.name = "pos_tlt"
    scale.name = "scale"
    return net, pos_spy, pos_tlt, scale
