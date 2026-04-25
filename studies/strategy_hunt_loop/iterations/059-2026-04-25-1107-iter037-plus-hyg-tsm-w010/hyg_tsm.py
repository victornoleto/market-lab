"""Iter 059 — HYG long-only with 90d boolean trend filter (credit-carry TSM).

Vendored verbatim from iter 058. Single-asset boolean trend filter
applied to HYG (iShares iBoxx HY Corporate). Mechanism:

    pos[t] = 1 if (price[t-1] / price[t-1-lookback] - 1) > 0 else 0
    r_hyg_tsm[t] = pos[t] * r_hyg[t] + (1 - pos[t]) * rf_d - cost[t]
    cost[t] = cost_bps * 1e-4 * |pos[t] - pos[t-1]|

Position at t depends only on prices ≤ t-1 (no lookahead, AFML p.162-164).
During the first `lookback` bars (warmup) `pos = 0` (cash earning rf_d).

The credit risk premium thesis (Asvanunt-Richardson 2017, JPM 43(2),
DOI 10.3905/jpm.2017.43.2.090) gives HYG a structurally positive
default-adjusted carry (~2-4% annualised), with the trend filter
removing the equity-correlated stress drawdowns of 2008/2020.

Citations
---------
* Asvanunt & Richardson 2017 JPM 43(2) DOI 10.3905/jpm.2017.43.2.090
  — credit risk premium quantification + trend filter for stress
  avoidance.
* `[systematic_trading]` (Carver) — generic TSM rule on a single asset.
* `[stocks_on_the_move, p.76-77]` (Clenow) — boolean trend on log price.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[risk_parity, ch.5]` — diversification thesis across asset classes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_hyg_tsm_returns(
    prices: pd.Series,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Daily net returns of single-asset HYG TSM.

    Parameters
    ----------
    prices : pd.Series
        Adjusted-close prices indexed by date (HYG daily prices).
    lookback : int, default 90
        Number of trading days for the trend signal. Must be > 0.
    rf : float, default 0.02
        Annual risk-free rate; converted to per-day with 252-day compounding.
    cost_bps : float, default 5.0
        Linear cost per unit of |Δposition|, in basis points (5 = 0.05%).

    Returns
    -------
    pd.Series
        Daily net returns indexed on prices.index[1:].

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
    rets = px.pct_change().dropna()
    trail = px / px.shift(lookback) - 1.0
    trail_lagged = trail.shift(1).reindex(rets.index)

    pos = np.where(trail_lagged.values > 0.0, 1.0, 0.0)
    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover
    net = pos * rets.values + (1.0 - pos) * rf_d - cost

    out = pd.Series(net, index=rets.index, name="r_hyg_tsm")
    return out
