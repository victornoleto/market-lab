"""Iter 049 — Gold time-series momentum (TSM) on GLD.

Single-asset boolean trend filter:

    pos[t] = 1 if (price[t-1] / price[t-1-lookback] - 1) > 0 else 0
    r_gold_tsm[t] = pos[t] * r_gld[t] + (1 - pos[t]) * rf_d - cost[t]
    cost[t] = cost_bps * 1e-4 * |pos[t] - pos[t-1]|

Position at t depends only on prices ≤ t-1 (no lookahead, AFML p.162-164).
During the first `lookback` bars (warmup) `pos = 0` (cash earning rf_d).

Citations
---------
* `[systematic_trading]` (Carver) — generic TSM rule on a single asset.
* `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log price.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[risk_parity, p.27-29, ch.2]` — gold's price return dominates roll yield;
  TSM filter avoids persistent drawdowns (1996-2001, 2013-2018).
* MYP 2012 (TSM across asset classes) — TSM has positive Sharpe on gold
  (DOI 10.1016/j.jfineco.2011.11.003).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_gold_tsm_returns(
    prices: pd.Series,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Daily net returns of single-asset gold TSM.

    Parameters
    ----------
    prices : pd.Series
        Adjusted-close prices indexed by date (e.g. GLD daily prices).
    lookback : int, default 90
        Number of trading days for the trend signal. Must be > 0.
    rf : float, default 0.02
        Annual risk-free rate; converted to per-day with 252-day compounding.
    cost_bps : float, default 5.0
        Linear cost per unit of |Δposition|, in basis points (5 = 0.05%).
        Charged when the position transitions long ↔ cash.

    Returns
    -------
    pd.Series
        Daily net returns indexed on prices.index[1:] (one bar lost to
        pct_change). During the warmup (first `lookback` bars) the
        position is 0 (cash) and returns equal rf_d. After warmup, on
        each bar the position is `1` if the trailing-`lookback` return
        ending at t-1 was positive, else `0`.

    Raises
    ------
    ValueError
        If `lookback <= 0` or `prices` has < 2 valid points.
    """
    if lookback <= 0:
        raise ValueError(f"lookback must be > 0; got {lookback}")
    if len(prices) < 2:
        raise ValueError(f"prices must have ≥ 2 points; got {len(prices)}")

    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    px = prices.astype(float)
    rets = px.pct_change().dropna()  # length n-1
    # Position at t (index i in returns) is computed from
    # px[i-lookback] vs px[i-1+1=i] in the original price index;
    # in returns-index terms (which starts at 1), position[i] uses
    # the trailing return over the window ending at returns-index i-1.
    # Simpler: compute trailing-lookback return on the PRICE series
    # ending at t-1, then shift by 1 to align with returns-index.
    # Trailing-lookback price ratio:
    #   trail[t] = price[t] / price[t - lookback] - 1
    # Position at returns-index i corresponds to date t = returns.index[i];
    # we use trail[t-1] (1-day lag). On the price index, that means
    # we compute trail on prices, then look up trail at price[t-1].
    trail = px / px.shift(lookback) - 1.0  # indexed on prices
    # Align to returns index (each ret at date t uses trail at date t-1).
    # trail.shift(1) brings yesterday's trail into today's index, then we
    # restrict to dates that are also in `rets.index`.
    trail_lagged = trail.shift(1).reindex(rets.index)

    # Position: 1 if trailing return is strictly positive, else 0.
    # NaN (warmup) → 0.
    pos = np.where(trail_lagged.values > 0.0, 1.0, 0.0)

    # Position transitions for cost. pos[-1] before history is 0 (cash).
    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover  # daily cost contribution

    # Net return: long-side gets r_gld, cash-side gets rf_d, minus cost.
    net = pos * rets.values + (1.0 - pos) * rf_d - cost

    out = pd.Series(net, index=rets.index, name="r_gold_tsm")
    return out
