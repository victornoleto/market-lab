"""Moreira-Muir variance-scaling position sizing.

Canonical form from Moreira & Muir (2017), *Journal of Finance* 72(4),
1611-1644. The scale on bar ``t`` is::

    s_t = clip(target_vol**2 / σ̂²_{t-1}, 0, max_leverage)

where ``σ̂²_{t-1}`` is the annualised rolling variance over ``[t-L, t-1]``.
Iter 004 used the first-order (vol-scaling) form ``target_vol / σ̂_{t-1}``;
iter 005 uses the squared-denominator canonical form.

The constant ``c = target_vol²`` is fixed so the average scale is ≈ 1 at
steady-state target volatility — the strategy remains benchmark-comparable.

Citations
---------
* Moreira, A., & Muir, T. (2017). *Journal of Finance* 72(4), 1611-1644.
  DOI 10.1111/jofi.12513.
* ``[systematic_trading, p.107-111]`` — vol standardisation family (iter 004
  was the first-order form).
* ``[advances_fin_ml, p.162-164]`` — ``σ̂_{t-1}`` lag for no look-ahead.

This module lives inside the iter 005 folder deliberately: the production
simulator namespace (``src/ai_trade/backtest/metrics/vol_target.py``)
stays unchanged for this iteration. If variance-scaling proves to be the
winner, a follow-up PR promotes this helper into the production layer
under a new name (``apply_variance_target``) with the same signature.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_variance_target(
    returns: pd.Series,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
) -> tuple[pd.Series, pd.Series]:
    """Scale ``returns`` by inverse realised variance (Moreira-Muir 2017).

    The scale on bar ``t`` uses the rolling std over ``[t-lookback, t-1]``
    — ``shift(1)`` on a rolling window with ``min_periods=lookback``,
    squared and annualised — so the sizing decision only sees the past.
    The first ``lookback`` bars have no valid scale and are dropped from
    the output.

    Parameters
    ----------
    returns : pd.Series
        Daily (or per-period) return stream.
    target_vol : float
        Target annualised vol as a fraction (e.g. ``0.15`` for 15%). Must
        be positive. Implies ``c = target_vol**2`` so that the mean scale
        is ≈ 1 when realised vol ≈ target.
    lookback : int
        Rolling-window length in bars. Must be ≥ 2.
    max_leverage : float
        Upper bound on the per-bar scale factor. Must be > 0. Zero realised
        variance is mapped to the cap (infinite demand clipped).
    periods_per_year : int
        Annualisation factor. Default 252.

    Returns
    -------
    (scaled_returns, scale_series)
        Both indexed on the valid bars (first ``lookback`` dropped).

    Raises
    ------
    ValueError
        If ``target_vol`` non-positive, ``lookback`` < 2, or
        ``max_leverage`` non-positive.
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")

    r = returns.dropna().astype(float)
    if len(r) <= lookback:
        raise ValueError(
            f"need > {lookback} bars to compute a scale, got {len(r)}"
        )

    ann_vol = r.rolling(lookback, min_periods=lookback).std(ddof=0) * np.sqrt(
        periods_per_year
    )
    ann_vol_prev = ann_vol.shift(1)
    ann_var_prev = ann_vol_prev ** 2

    target_var = target_vol ** 2

    raw_scale = pd.Series(index=r.index, dtype=float)
    mask_valid = ann_var_prev.notna()
    # σ² > 0 path.
    pos = mask_valid & (ann_var_prev > 0)
    raw_scale.loc[pos] = target_var / ann_var_prev.loc[pos]
    # σ² == 0 degenerate path → send to cap.
    zero = mask_valid & (ann_var_prev == 0)
    raw_scale.loc[zero] = max_leverage

    scale = raw_scale.clip(lower=0.0, upper=max_leverage).dropna()
    scaled = (scale * r.loc[scale.index]).astype(float)
    scaled.name = returns.name
    scale.name = "scale"
    return scaled, scale
