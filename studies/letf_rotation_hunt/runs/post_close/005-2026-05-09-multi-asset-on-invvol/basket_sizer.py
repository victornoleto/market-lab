"""Inverse-volatility basket sizing for iter 005.

Helpers live INSIDE the iter dir (per LOOP_PROTOCOL §"Scope limits"). Not
imported by other iters or by the closed-study modules.

Citations
---------
- [stocks_on_the_move, p.98]: Clenow vol-parity sizing — w_i ∝ 1/σ_i so
  each position contributes equal volatility.
- [systematic_trading, ch.10]: Carver instrument volatility scalar
  IVS_i = vol_target / σ_i; equivalent up to a normalising constant.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd


def realised_vol(returns: pd.Series, window: int) -> pd.Series:
    """Annualised rolling realised volatility (σ × √252).

    Min_periods = window (no short-window blow-up). NaN during warmup.
    """
    return returns.rolling(window=window, min_periods=window).std() * np.sqrt(252.0)


def inverse_vol_weights(
    returns_by_asset: dict[str, pd.Series],
    window: int,
) -> pd.DataFrame:
    """Daily inverse-volatility weights for a basket of assets.

    For each timestamp t: w_i(t) = (1/σ_i(t-1)) / Σ_j (1/σ_j(t-1)).
    The 1-day lag is applied here so callers can pre-compute weights at
    close of t-1 and apply them at open of t (same convention as winner
    gates).

    NaNs during warmup (first `window` bars) are propagated as NaN rows;
    callers should reindex to the strategy returns index and forward-fill
    or treat warmup as ON-state-undefined.

    Parameters
    ----------
    returns_by_asset:
        Dict ticker → daily-return Series (same DatetimeIndex semantics
        across all assets; the function reindexes to the union and aligns).
    window:
        Lookback in trading days (e.g., 60 or 120).

    Returns
    -------
    pd.DataFrame
        Columns = asset tickers, index = aligned dates, values = weights
        in [0, 1]. Rows sum to 1.0 except during warmup (NaN).
    """
    assets = list(returns_by_asset.keys())
    if len(assets) < 1:
        raise ValueError("inverse_vol_weights needs at least 1 asset")
    aligned = pd.DataFrame({a: returns_by_asset[a] for a in assets})
    sigmas = pd.DataFrame(
        {a: realised_vol(aligned[a], window) for a in assets}
    ).shift(1)
    inv = 1.0 / sigmas
    inv = inv.where(inv.notna() & np.isfinite(inv) & (inv > 0))
    row_sum = inv.sum(axis=1)
    weights = inv.div(row_sum, axis=0)
    weights = weights.where(row_sum.notna() & (row_sum > 0))
    return weights


def equal_weights(assets: Sequence[str], index: pd.Index) -> pd.DataFrame:
    """Static equal-weight basket: 1/N per asset across all dates."""
    n = len(assets)
    if n < 1:
        raise ValueError("equal_weights needs at least 1 asset")
    w = 1.0 / n
    return pd.DataFrame({a: pd.Series(w, index=index) for a in assets})


def basket_returns_from_weights(
    weights: pd.DataFrame,
    returns_by_asset: dict[str, pd.Series],
) -> pd.Series:
    """Daily basket return = Σ_i w_i(t) × r_i(t).

    Weights are aligned on the asset axis with `returns_by_asset` keys;
    missing assets in weights are treated as 0 (e.g. warmup rows).
    """
    assets = list(weights.columns)
    aligned_r = pd.DataFrame(
        {a: returns_by_asset[a] for a in assets}
    ).reindex(weights.index)
    w = weights.fillna(0.0)
    out = (w.values * aligned_r.values).sum(axis=1)
    s = pd.Series(out, index=weights.index)
    s[w.sum(axis=1) <= 0.0] = np.nan
    return s
