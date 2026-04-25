"""Iter 040 — Vol-managed cross-asset VRP basket (Moreira-Muir 2017 σ⁻²-scaling).

Wraps iter 039's cross-asset VRP basket with the Moreira-Muir 2017
inverse-variance-target sizing discipline applied to the **basket
overlay** realized variance:

    overlay[t]    = - harvest_notional * sum_i ( weights[i] * overlay_i[t] )
    σ̂²_overlay[t] = annualised rolling-21d variance of overlay
    scale[t]      = clip( target_vol² / σ̂²_overlay[t-1], 0, max_lev )
    r_strategy[t] = rf_daily + scale[t] * overlay[t]

When realized basket-overlay vol is **low** (calm regime) the strategy
levers up to ``max_lev`` to harvest more short-vol premium per unit
of capital. When realized basket-overlay vol is **high** (stress)
``scale[t]`` shrinks below 1.0 — protecting capital against the spike
in short-side gamma.

Citations
---------
* `[volatility_trading, p.218]` — Sinclair (2013) cross-asset VRP harvest.
* Moreira & Muir (2017) JoF 72(4) 1611-1644 — vol-target scaling.
* `[volatility_trading, ch.3, p.41, p.217]` — VRP mechanics + capped tail.
* Bondarenko (2014) QJF 4(3) 1450015 — empirical SPX VRP magnitude.
* Carr-Wu (2009) RFS 22(3) 1311-1341 — variance risk premia structural.
* Bakshi-Madan (2006) JFE 81(2) 471-518 — cross-asset implied-vol premia.
* Driessen-Maenhout-Vilkov (2009) JoF 64(4) 1377-1406 — correlation risk.
* `[risk_parity, p.10-11, ch.1]` — fixed-weight stack primitive.
* `[systematic_trading, p.40, ch.2]` — vol standardisation primitive.
* `[systematic_trading, p.170-171, ch.11]` — IDM ≤ 2.5 leverage cap.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline (G7).
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag (no look-ahead).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
if str(ITER_020_DIR) not in sys.path:
    sys.path.append(str(ITER_020_DIR))

from put_spread_hedge import compute_put_spread_daily_returns  # noqa: E402


def compute_vrp_basket_vm_returns(
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
    target_vol: float = 0.05,
    lookback: int = 21,
    max_lev: float = 2.0,
    periods_per_year: int = 252,
) -> pd.Series:
    """Daily fractional returns of the vol-managed VRP basket portfolio.

    Parameters
    ----------
    prices : dict[str, pd.Series]
        Mapping ticker -> adj_close series (e.g. SPY/QQQ/IWM). Inner-
        join taken across all overlays.
    iv_series : pd.Series
        IV proxy in percentage units (e.g. VIX). Reused per leg with
        ``iv_scales[ticker]`` to approximate VXN (QQQ) and RVX (IWM).
    rf, harvest_notional, weights, iv_scales,
    k_long_pct, k_short_pct, dte_days, cost_bps_per_roll :
        Same semantics as iter 039's ``compute_vrp_basket_returns``.
    target_vol : float
        Target annualised overlay vol (e.g. 0.05 = 5%).
        ``scale[t] = clip(target_vol² / σ̂²_overlay[t-1], 0, max_lev)``.
        Must be > 0.
    lookback : int
        Rolling-window length in bars for σ̂²_overlay. Must be ≥ 2.
    max_lev : float
        Upper bound on ``scale[t]``. Must be > 0. Keep ≤ 2.5 to respect
        Carver IDM (`[systematic_trading, p.170]`).
    periods_per_year : int
        Annualisation factor for σ̂². Default 252.

    Returns
    -------
    pd.Series
        Daily strategy returns indexed on the inner-join of all
        overlays after the rolling-window warmup. The first
        ``lookback + 1`` bars are dropped (need σ̂²_{t-1}).

    Raises
    ------
    ValueError
        If params are out of domain or input dicts are misaligned.
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}. "
            "The sign flip to short-side is applied internally."
        )
    if not prices:
        raise ValueError("prices dict is empty")
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0; got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2; got {lookback}")
    if max_lev <= 0:
        raise ValueError(f"max_lev must be > 0; got {max_lev}")

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

    # Per-leg overlay (iter 020's `compute_put_spread_daily_returns`).
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
    weighted_long_overlay = sum(
        weights[t] * overlay_df[t] for t in tickers
    )
    # `overlay_t` is the SHORT-side return stream (sign-flipped) at
    # constant `harvest_notional`; this is what we want to scale.
    short_overlay = (-harvest_notional) * weighted_long_overlay
    short_overlay.name = "short_overlay"

    # Rolling annualised variance of the unscaled short_overlay.
    # ddof=0 matches numpy reference.
    ann_var = (
        short_overlay.rolling(lookback, min_periods=lookback).std(ddof=0) ** 2
        * periods_per_year
    ).shift(1)
    ann_var = ann_var.clip(lower=0.0)

    target_var = target_vol ** 2
    raw_scale = pd.Series(np.nan, index=short_overlay.index, dtype=float)
    mask_valid = ann_var.notna()
    pos_mask = mask_valid & (ann_var > 0)
    zero_mask = mask_valid & (ann_var == 0)
    raw_scale.loc[pos_mask] = target_var / ann_var.loc[pos_mask]
    raw_scale.loc[zero_mask] = max_lev  # σ̂²==0 → full cap
    scale = raw_scale.clip(lower=0.0, upper=max_lev).dropna()

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    short_aligned = short_overlay.loc[scale.index]
    strategy = rf_daily + scale * short_aligned
    strategy.name = "vrp_basket_vm_return"
    return strategy
