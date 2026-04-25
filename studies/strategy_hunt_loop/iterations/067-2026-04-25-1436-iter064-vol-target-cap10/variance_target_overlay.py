"""Iter 067 — Moreira-Muir σ⁻² variance-target overlay (pandas) with cap ≤ 1.0.

Apply a one-sided variance-target wrapper on a saved daily return stream
(e.g. iter 064's `iter046_plus_qqq_trend_w010_lookback200`). The overlay
de-risks when realised σ̂ exceeds σ_target and is hard-capped at 1.0 to
forbid leverage. This makes the mechanism asymmetric (de-risk only).

Citations
---------
* Moreira & Muir (2017), JoF 72(4), 1611-1644. DOI 10.1111/jofi.12513.
  σ⁻² scaling primitive (with leverage); we use the cap = 1.0 variant.
* `[volatility_trading, p.218]` — Sinclair, σ⁻² sizing.
* `[advances_fin_ml, p.162-164]` — strict shift(1) to avoid look-ahead.
* `[systematic_trading, p.40, ch.2]` — Carver vol standardisation.
* `[risk_parity, ch.5]` — fixed-weight + variance dynamic-sizing layering.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def apply_variance_target_overlay(
    r: pd.Series,
    *,
    sigma_target: Optional[float],
    lookback: int,
    cap: float,
    cost_bps: float,
    periods_per_year: int = 252,
) -> tuple[pd.Series, pd.Series]:
    """One-sided σ⁻² variance-target overlay on a daily return stream.

    Parameters
    ----------
    r : pd.Series
        Daily simple-return stream (already net of underlying-strategy costs).
        DatetimeIndex required.
    sigma_target : float | None
        Target annualised σ. If None, defaults to ``r.std(ddof=0) * √252``
        — the full-window annualised σ of the input stream.
    lookback : int
        Rolling window length (bars) for σ̂². Must be ≥ 2.
    cap : float
        Upper bound on scale[t]. Must be > 0. Use 1.0 to forbid leverage.
    cost_bps : float
        Linear cost in bps per unit of |scale[t] - scale[t-1]|. Cost
        applies to the overlay only — `r` is already net of underlying costs.
    periods_per_year : int
        Annualisation factor (default 252).

    Returns
    -------
    (net_returns, scale)
        Both indexed on the valid bars (first ``lookback`` dropped due to
        rolling+shift warmup). ``net_returns`` is `scale * r - cost`,
        where cost = ``cost_bps * 1e-4 * |Δscale|``.

    Raises
    ------
    ValueError
        On invalid sigma_target, lookback, cap, cost_bps, or insufficient bars.
    """
    if sigma_target is not None and sigma_target < 0:
        raise ValueError(f"sigma_target must be ≥ 0, got {sigma_target}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if cap <= 0:
        raise ValueError(f"cap must be > 0, got {cap}")
    if cost_bps < 0:
        raise ValueError(f"cost_bps must be ≥ 0, got {cost_bps}")
    if len(r) <= lookback:
        raise ValueError(f"need > {lookback} bars, got {len(r)}")

    r = r.astype(float)

    if sigma_target is None:
        sigma_target = float(r.std(ddof=0)) * float(np.sqrt(periods_per_year))

    target_var = sigma_target * sigma_target  # σ_target² annualised

    # Rolling annualised σ̂², shifted by 1 bar (no look-ahead per AFML p.162-164).
    ann_var_hat = (
        r.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * float(periods_per_year)
    ).shift(1)

    raw_scale = pd.Series(np.nan, index=r.index, dtype=float)
    mask_valid = ann_var_hat.notna()
    pos_mask = mask_valid & (ann_var_hat > 0)
    zero_mask = mask_valid & (ann_var_hat == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var_hat.loc[pos_mask]
    raw_scale.loc[zero_mask] = cap  # σ̂² == 0 ⇒ saturate at cap

    scale = raw_scale.clip(lower=0.0, upper=cap).dropna()

    r_aligned = r.loc[scale.index]
    gross = scale * r_aligned

    # Friction: cost on |Δscale|. First bar has Δscale = scale[0] (assume
    # we built up to scale[0] from 0).
    delta_scale = scale.diff().abs()
    delta_scale.iloc[0] = scale.iloc[0]
    cost = delta_scale * (cost_bps * 1e-4)

    net = (gross - cost).astype(float)
    net.name = "net"
    scale.name = "scale"
    return net, scale
