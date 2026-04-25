"""Iter 057 — Multi-commodity TSM basket on USO+UNG+SLV.

Per-asset boolean trend filter (same rule as iter 049 gold TSM,
generalised to a basket via 1/N equal-weight aggregation):

    pos_i[t] = 1 if (price_i[t-1] / price_i[t-1-lookback] - 1) > 0 else 0
    r_i_tsm[t] = pos_i[t] * r_i[t] + (1 - pos_i[t]) * rf_d - cost_i[t]
    cost_i[t] = cost_bps * 1e-4 * |pos_i[t] - pos_i[t-1]|
    r_basket[t] = (1/N) * sum_i r_i_tsm[t]      # equal-weight basket

Position at t depends only on prices ≤ t-1 (no lookahead, AFML p.162-164).
During the warmup (first `lookback` bars per asset) `pos_i = 0`
(cash earning rf_d). The basket aggregation uses the inner-join of all
asset return indexes — assets with shorter histories dominate the
basket start date.

Citations
---------
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen 2012 risk-parity stack.
* `[systematic_trading]` — Carver generic TSM rule.
* `[stocks_on_the_move, p.76-77]` — Clenow boolean trend on log price.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift.
* Moskowitz-Ooi-Pedersen (2012), JFE 104(2) 228-250
  (DOI 10.1016/j.jfineco.2011.11.003) — TSM positive Sharpe across
  commodities/equities/bonds/FX; cross-asset diversification of
  trend-filtered streams compounds.
* Asness-Moskowitz-Pedersen (2013), JoF 68(3) 929-985 — value/momentum
  everywhere; commodity TSM has lower correlation to equities than
  expected.
* Erb-Harvey (2006), FAJ 62(2) — commodity premia; trend-filter avoids
  persistent commodity drawdowns.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd


def compute_single_asset_tsm_returns(
    prices: pd.Series,
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Daily net returns of single-asset boolean TSM.

    Identical logic to ``gold_tsm.compute_gold_tsm_returns`` (iter 049)
    but kept self-contained here so iter 057 doesn't import iter 049.

    Parameters
    ----------
    prices : pd.Series
        Adjusted-close prices indexed by date (e.g. USO daily prices).
    lookback : int, default 90
        Number of trading days for the trend signal. Must be > 0.
    rf : float, default 0.02
        Annual risk-free rate; converted to per-day with 252-day compounding.
    cost_bps : float, default 5.0
        Linear cost per unit of |Δposition|, in basis points.

    Returns
    -------
    pd.Series
        Daily net returns indexed on prices.index[1:].

    Raises
    ------
    ValueError
        If ``lookback <= 0`` or prices has < 2 valid points.
    """
    if lookback <= 0:
        raise ValueError(f"lookback must be > 0; got {lookback}")
    if len(prices) < 2:
        raise ValueError(f"prices must have ≥ 2 points; got {len(prices)}")

    rf_d = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    px = prices.astype(float)
    rets = px.pct_change().dropna()  # length n-1

    trail = px / px.shift(lookback) - 1.0  # indexed on prices
    trail_lagged = trail.shift(1).reindex(rets.index)

    pos = np.where(trail_lagged.values > 0.0, 1.0, 0.0)
    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover

    net = pos * rets.values + (1.0 - pos) * rf_d - cost
    return pd.Series(net, index=rets.index, name=f"r_{prices.name or 'tsm'}")


def compute_commodity_basket_tsm_returns(
    prices: Mapping[str, pd.Series],
    *,
    lookback: int = 90,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Equal-weight TSM basket across multiple commodity ETFs.

    Per-asset boolean TSM (long iff trailing-lookback return at t-1 > 0,
    else cash earning rf_d) — identical rule per asset — then equal-weight
    aggregation across the inner-join of asset return indexes.

    Parameters
    ----------
    prices : Mapping[str, pd.Series]
        Map of ticker → adjusted-close prices. Each Series indexed by date.
        At least 1 ticker required. Each ticker must have ≥ ``lookback + 2``
        bars (else its first ``lookback`` bars are treated as cash).
    lookback, rf, cost_bps : same as single-asset TSM.

    Returns
    -------
    pd.Series
        Daily net returns of the equal-weight basket, indexed on the
        inner-join of all per-asset return indexes.

    Raises
    ------
    ValueError
        If ``prices`` is empty or any ticker has < 2 prices.
    """
    if not prices:
        raise ValueError("prices must contain ≥ 1 ticker")

    per_asset: dict[str, pd.Series] = {}
    for tk, p in prices.items():
        per_asset[tk] = compute_single_asset_tsm_returns(
            p.rename(tk), lookback=lookback, rf=rf, cost_bps=cost_bps,
        )

    # Inner-join indexes
    common = None
    for tk, s in per_asset.items():
        common = s.index if common is None else common.intersection(s.index)
    if common is None or len(common) < 2:
        raise ValueError(
            f"basket inner-join has < 2 bars (assets: "
            f"{[(tk, len(s)) for tk, s in per_asset.items()]})"
        )

    n = len(per_asset)
    aligned = pd.concat(
        {tk: s.loc[common] for tk, s in per_asset.items()}, axis=1,
    )
    basket = aligned.mean(axis=1)
    basket.name = "r_commodity_tsm_basket"
    return basket
