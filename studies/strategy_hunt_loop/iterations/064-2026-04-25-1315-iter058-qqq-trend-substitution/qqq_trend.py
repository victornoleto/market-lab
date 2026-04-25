"""Iter 064 — QQQ-200d-trend (Faber 2007 TAA single-asset trend filter).

Single-asset boolean trend filter applied to QQQ (Invesco QQQ Nasdaq-100):

    pos[t] = 1 if price[t-1] > SMA_{lookback}(price)[t-1] else 0
    r_qqq_trend[t] = pos[t] * r_qqq[t] + (1 - pos[t]) * rf_d - cost[t]
    cost[t] = cost_bps * 1e-4 * |pos[t] - pos[t-1]|

Position at t depends only on prices ≤ t-1 (no lookahead, AFML p.162-164).
During the first `lookback` bars (warmup) `pos = 0` (cash earning rf_d).

The Faber 2007 thesis (SSRN 962461 — *A Quantitative Approach to Tactical
Asset Allocation*, J. Wealth Mgmt) applies a single-asset 200-day SMA
filter to broad equity indices, demonstrating Sharpe ~0.7-0.85 with MDD
reduction from ~50% to ~25% on US equities over 1972-2005. Replicated
in subsequent literature (Clenow [stocks_on_the_move, p.21-30] uses
the 200d filter as a regime gate inside a wider momentum portfolio).

Iter 064 swaps iter 058's HYG_TSM (S~0.99, CAGR~4.85%, Sharpe-additive
but CAGR-dilutive) with QQQ_TREND (S~0.80, CAGR~12-14%, Sharpe-trade-off
but CAGR-additive) to break iter 058's binding 0/3 CAGR floor.

Citations
---------
* Faber (2007) SSRN 962461 — single-asset 200-day SMA TAA primitive.
* `[stocks_on_the_move, p.21-30]` (Clenow) — 200d SMA as regime gate.
* `[systematic_trading]` (Carver) — generic boolean TSM rule.
* Moskowitz-Ooi-Pedersen (2012) JFE 104(2) DOI 10.1016/j.jfineco.2011.11.003
  — TSM with 12-month formation generalising single-asset trend.
* `[advances_fin_ml, p.162-164]` — no-lookahead 1-day shift rule.
* `[risk_parity, ch.5]` — diversification thesis across asset classes.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def compute_qqq_trend_returns(
    prices: pd.Series,
    *,
    lookback: int = 200,
    rf: float = 0.02,
    cost_bps: float = 5.0,
) -> pd.Series:
    """Daily net returns of single-asset QQQ trend filter (Faber 2007).

    Parameters
    ----------
    prices : pd.Series
        Adjusted-close prices indexed by date (QQQ daily prices).
    lookback : int, default 200
        SMA window length in trading days. Faber 2007 uses 200 (~10 months).
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
        each bar the position is `1` if price[t-1] > SMA_{lookback}[t-1],
        else `0`.

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
    sma = px.rolling(lookback).mean()
    # Signal at t-1: prior-day close > prior-day SMA. Shift by 1 to apply at t.
    signal_raw = (px > sma).astype(float)
    signal_lagged = signal_raw.shift(1).reindex(rets.index)
    # Warmup: first `lookback` bars have NaN SMA; treat as cash (pos=0).
    pos = signal_lagged.fillna(0.0).values

    pos_prev = np.concatenate([[0.0], pos[:-1]])
    turnover = np.abs(pos - pos_prev)
    cost = (cost_bps * 1e-4) * turnover
    net = pos * rets.values + (1.0 - pos) * rf_d - cost

    out = pd.Series(net, index=rets.index, name="r_qqq_trend")
    return out
