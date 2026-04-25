"""Pure-numpy reference for iter 049 gold TSM (G7 cross-lib parity check).

Identical logic to `gold_tsm.compute_gold_tsm_returns`, expressed in
plain numpy arrays. Used to verify the pandas implementation has no
hidden lookahead via index alignment.

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import numpy as np


def compute_gold_tsm_returns_np(
    prices: np.ndarray,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy reference for gold TSM net returns.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of adjusted-close prices, length n ≥ 2.
    lookback : int, default 90
    rf : float, default 0.02
    cost_bps : float, default 5.0

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

    # Trailing-lookback return at price index i: px[i] / px[i-lookback] - 1
    # We want this AT t-1 on the returns-index i (returns-index i ↔ price-index i+1
    # for the underlying date t; the position uses prices ≤ t-1 = price-index i).
    # So trail at price-index i, used by returns-index i (date t = price.index[i+1]).
    n_ret = n - 1
    pos = np.zeros(n_ret, dtype=float)
    # For returns-index i, look at price-index i (≡ date t-1) and check
    # px[i] / px[i - lookback] - 1 > 0 (requires i >= lookback).
    for i in range(lookback, n_ret):
        trail = px[i] / px[i - lookback] - 1.0
        pos[i] = 1.0 if trail > 0.0 else 0.0

    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover
    net = pos * rets + (1.0 - pos) * rf_d - cost
    return net
