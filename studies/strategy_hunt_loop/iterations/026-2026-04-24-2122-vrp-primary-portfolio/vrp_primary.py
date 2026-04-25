"""Iter 026 — VRP-primary stand-alone portfolio.

Holds T-bills earning a constant ``rf`` and SHORTS a 5/10% OTM put
credit spread on the equity index each month at 21-DTE, rolling at
expiry. The strategy IS the harvest — no equity-leg, no bond-leg, no
vol-target wrapper sits underneath. Iter 020/021 built the option-
pricing primitive on top of an equity stack which absorbed the harvest
through ``σ²_port``; this iteration removes that absorption to ask
"does VRP-only deliver Sharpe edge vs SPY 1× post-GFC?".

Daily P&L of one unit of capital:

    r_strategy[t] = rf_daily + harvest_notional * (-overlay[t])

where ``overlay[t]`` is iter 020's `compute_put_spread_daily_returns`
(long-holder's daily fractional P&L per S_entry) and the ``-`` flips it
to short-writer's P&L. ``harvest_notional = 1.0`` means one full spread
sold per unit of capital (max single-roll loss = spread width minus net
credit, ≈ 4-4.5% per roll).

Citations
---------
* `[volatility_trading, ch.3]` — VRP mechanics (Sinclair 2013).
* `[volatility_trading, p.41]` — SPX kurtosis 21.3 → capped tail.
* `[volatility_trading, p.217]` — short index vol harvest rule.
* `[volatility_trading, p.11]` — BSM pricing identity (used in pricer).
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* Bondarenko (2014). "Why Are Put Options So Expensive?" QJF 4(3).
* Carr-Wu (2009). "Variance Risk Premiums." RFS 22(3).
* Coval-Shumway (2001). "Expected Option Returns." JoF 56(3).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
if str(ITER_020_DIR) not in sys.path:
    sys.path.append(str(ITER_020_DIR))

from put_spread_hedge import compute_put_spread_daily_returns  # noqa: E402


def compute_vrp_primary_returns(
    prices: pd.Series,
    iv_series: pd.Series,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
) -> pd.Series:
    """Daily fractional returns of the VRP-primary portfolio.

    Parameters
    ----------
    prices, iv_series : pd.Series
        Equity adj_close + IV (% units, e.g. VIX). Aligned via inner-join
        in the BS pricer.
    rf : float
        Annualized risk-free rate (constant). Daily rate computed via
        ``(1 + rf) ** (1/252) - 1``.
    harvest_notional : float
        Non-negative scaling on the short-writer overlay. 1.0 = one
        full spread per unit capital (max-loss ≈ 4-4.5% per roll).
    k_long_pct, k_short_pct, dte_days, iv_scale, cost_bps_per_roll :
        Inherited from iter 020's `compute_put_spread_daily_returns`.

    Returns
    -------
    pd.Series of daily strategy returns aligned to `prices.index`
    (after the inner-join inside the pricer).

    Raises
    ------
    ValueError
        If ``harvest_notional < 0`` (the sign flip to short-writer is
        applied internally; pass a positive magnitude only).
        Also propagates ValueErrors from
        `compute_put_spread_daily_returns` for invalid strikes/dte/etc.
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}. "
            "The sign flip to short-side is applied internally."
        )

    # Long-holder overlay (positive when SPY drops + IV rises; negative
    # most days due to theta decay).
    long_overlay = compute_put_spread_daily_returns(
        prices, iv_series,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        rf=rf,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
    )

    # Daily T-bill increment (constant).
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0

    # Strategy return: T-bill + short-writer harvest.
    strategy = rf_daily + harvest_notional * (-long_overlay)
    strategy.name = "vrp_primary_return"
    return strategy
