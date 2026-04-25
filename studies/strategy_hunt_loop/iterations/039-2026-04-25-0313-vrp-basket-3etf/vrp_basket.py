"""Iter 039 — Cross-asset VRP basket portfolio (T-bill + 3 short put-credit-spreads).

Generalises iter 026's single-asset VRP-primary harvester to a 3-leg
basket: T-bills earn ``rf`` while the strategy SHORTS the same 5/10 %
OTM 21-DTE put credit spread on **SPY, QQQ and IWM** simultaneously,
each at ``weights[ticker]`` of total notional. With equal weights = 1/3
and ``harvest_notional = 1.0``, the total per-roll spread notional
shorted per unit capital is unchanged at 1.0, but distributed across
3 underlyings.

Daily P&L of one unit of capital:

    r_strategy[t] = rf_daily
                  + harvest_notional * sum_i ( weights[i] * (-overlay_i[t]) )

where ``overlay_i`` is iter 020's ``compute_put_spread_daily_returns``
applied to ticker ``i`` with the appropriate iv_scale (SPY=1.0,
QQQ≈1.10 to proxy VXN, IWM≈1.25 to proxy RVX).

Citations
---------
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest.
* `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics + capped tail.
* Bondarenko (2014) QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Carr-Wu (2009) RFS 22(3) 1311-1341 — variance risk premia structural.
* Driessen-Maenhout-Vilkov (2009) JoF 64(4) 1377-1406 — cross-sectional
  decomposition of index VRP into individual + correlation risk.
* Bakshi-Madan (2006) JFE 81(2) 471-518 — cross-asset implied-vol premia.
* Asness-Moskowitz-Pedersen (2013) JoF 68(3) 929-985 — diversification.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
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


def compute_vrp_basket_returns(
    prices: dict[str, pd.Series],
    iv_series: pd.Series,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    weights: dict[str, float] | None = None,
    iv_scales: dict[str, float] | None = None,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    cost_bps_per_roll: float = 5.0,
) -> pd.Series:
    """Daily fractional returns of the 3-leg VRP basket portfolio.

    Parameters
    ----------
    prices : dict[str, pd.Series]
        Mapping of ticker -> adj_close series (e.g. {"SPY": ..., "QQQ":
        ..., "IWM": ...}). All series must have a date index; an
        inner-join is taken across all overlays to produce a common
        return index.
    iv_series : pd.Series
        Implied-volatility proxy in percentage units (e.g. VIX). Reused
        as the IV input for every leg, with ``iv_scales[ticker]`` applied
        per leg to approximate VXN (QQQ) and RVX (IWM).
    rf : float
        Annualised risk-free rate (constant). Daily increment via
        ``(1 + rf) ** (1/252) - 1``.
    harvest_notional : float
        Non-negative scaling on the (sign-flipped) basket overlay. 1.0
        means the strategy shorts ``sum_i weights[i] = 1.0`` total
        spread notional per unit capital.
    weights : dict[str, float] | None
        Per-leg basket weights. If None, defaults to equal weights over
        the keys of ``prices``. Must be non-negative and sum to <= 1.0
        (sums to 1.0 + ``harvest_notional`` = nominal short notional).
    iv_scales : dict[str, float] | None
        Per-leg multiplier on ``iv_series / 100`` to approximate the
        ticker's index-vol regime. Defaults to {"SPY": 1.0, "QQQ":
        1.10, "IWM": 1.25} when None and tickers match those names.
        For unknown tickers, defaults to 1.0.
    k_long_pct, k_short_pct, dte_days, cost_bps_per_roll :
        Inherited from iter 020's ``compute_put_spread_daily_returns``;
        the same strike convention applies to every leg.

    Returns
    -------
    pd.Series
        Daily basket returns indexed on the inner-join of all overlays.

    Raises
    ------
    ValueError
        If ``harvest_notional < 0``, weights have a negative entry, or
        the per-ticker pricer raises (invalid strikes / DTE / etc).
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}. "
            "The sign flip to short-side is applied internally."
        )
    if not prices:
        raise ValueError("prices dict is empty")

    tickers = list(prices.keys())
    if weights is None:
        weights = {t: 1.0 / len(tickers) for t in tickers}
    if iv_scales is None:
        default_iv = {"SPY": 1.0, "QQQ": 1.10, "IWM": 1.25}
        iv_scales = {t: default_iv.get(t, 1.0) for t in tickers}

    missing_w = [t for t in tickers if t not in weights]
    missing_iv = [t for t in tickers if t not in iv_scales]
    if missing_w:
        raise ValueError(f"weights missing tickers: {missing_w}")
    if missing_iv:
        raise ValueError(f"iv_scales missing tickers: {missing_iv}")
    for t in tickers:
        if weights[t] < 0:
            raise ValueError(f"weights[{t}] must be >= 0; got {weights[t]}")

    overlays: dict[str, pd.Series] = {}
    for ticker in tickers:
        overlays[ticker] = compute_put_spread_daily_returns(
            prices[ticker], iv_series,
            k_long_pct=k_long_pct,
            k_short_pct=k_short_pct,
            dte_days=dte_days,
            rf=rf,
            iv_scale=iv_scales[ticker],
            cost_bps_per_roll=cost_bps_per_roll,
        )

    overlay_df = pd.concat(overlays, axis=1, join="inner").dropna()

    weighted_overlay = sum(
        weights[t] * overlay_df[t] for t in tickers
    )

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    strategy = rf_daily + harvest_notional * (-weighted_overlay)
    strategy.name = "vrp_basket_return"
    return strategy
