"""Pure-numpy reference for iter 057 commodity TSM basket (G7 parity).

Replicates ``commodity_tsm.compute_commodity_basket_tsm_returns`` using
plain numpy arrays. Used to verify the pandas implementation has no
hidden lookahead via index alignment.

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import numpy as np


def compute_single_asset_tsm_np(
    prices: np.ndarray,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy single-asset boolean TSM.

    Returns
    -------
    np.ndarray
        Length n-1 array of daily net returns.
    """
    if lookback <= 0:
        raise ValueError(f"lookback must be > 0; got {lookback}")
    px = np.asarray(prices, dtype=float)
    n = len(px)
    if n < 2:
        raise ValueError(f"prices must have ≥ 2 points; got {n}")

    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    rets = (px[1:] / px[:-1]) - 1.0  # length n-1

    n_ret = n - 1
    pos = np.zeros(n_ret, dtype=float)
    # Position at returns-index i uses px[i] (which is t-1 in date terms,
    # since returns at i correspond to date prices.index[i+1]).
    for i in range(lookback, n_ret):
        trail = px[i] / px[i - lookback] - 1.0
        pos[i] = 1.0 if trail > 0.0 else 0.0

    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover
    net = pos * rets + (1.0 - pos) * rf_d - cost
    return net


def compute_commodity_basket_np(
    aligned_prices: np.ndarray,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Equal-weight commodity TSM basket on aligned price matrix.

    Parameters
    ----------
    aligned_prices : np.ndarray
        Shape (n_bars, n_assets) — rows are aligned dates (inner-join
        already performed by caller), columns are assets.

    Returns
    -------
    np.ndarray
        Length n_bars - 1 array of daily basket net returns.
    """
    if aligned_prices.ndim != 2:
        raise ValueError(
            f"aligned_prices must be 2-D (rows=bars, cols=assets); "
            f"got shape {aligned_prices.shape}"
        )
    n_bars, n_assets = aligned_prices.shape
    if n_assets < 1:
        raise ValueError("must have ≥ 1 asset")

    per_asset_nets = np.zeros((n_bars - 1, n_assets), dtype=float)
    for j in range(n_assets):
        per_asset_nets[:, j] = compute_single_asset_tsm_np(
            aligned_prices[:, j],
            lookback=lookback,
            rf=rf,
            cost_bps=cost_bps,
        )
    return per_asset_nets.mean(axis=1)
