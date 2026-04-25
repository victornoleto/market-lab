"""Pure-numpy reference for iter 064 QQQ-trend (G7 cross-lib parity check).

Identical logic to `qqq_trend.compute_qqq_trend_returns`, expressed in
plain numpy arrays. Used to verify the pandas implementation has no
hidden lookahead via index alignment.

Citations
---------
* `[advances_fin_ml, p.31-34]` — G7 cross-library parity.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
"""

from __future__ import annotations

import numpy as np


def compute_qqq_trend_returns_np(
    prices: np.ndarray,
    *,
    lookback: int = 200,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> np.ndarray:
    """Pure-numpy reference for QQQ trend net returns.

    Parameters
    ----------
    prices : np.ndarray
        1-D array of adjusted-close prices, length n ≥ 2.
    lookback : int, default 200
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
    rets = (px[1:] / px[:-1]) - 1.0
    n_ret = n - 1
    pos = np.zeros(n_ret, dtype=float)
    # Compute SMA via rolling mean, then signal at i requires SMA[i-1] vs px[i-1].
    # In return index terms: ret[i] corresponds to px[i+1]/px[i]-1, so we want
    # signal applied at ret[i] = (price[i] > SMA_{lookback}(price)[i]).
    # The rets array index i corresponds to price index i+1; px[1:][i] = px[i+1].
    # Match the pandas: signal_raw = (px > sma).shift(1) so for ret index i
    # (price index i+1), signal uses price index i, i.e. px[i] vs SMA[i].
    # SMA[i] requires bars [i-lookback+1 .. i] inclusive (lookback bars).
    for i in range(n_ret):
        # Need price index i, SMA over [i-lookback+1 .. i] i.e. last `lookback` bars
        if i < lookback - 1:
            pos[i] = 0.0
            continue
        sma_i = float(np.mean(px[i - lookback + 1: i + 1]))
        pos[i] = 1.0 if px[i] > sma_i else 0.0

    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover
    net = pos * rets + (1.0 - pos) * rf_d - cost
    return net
