"""Iter 076 — LEVERED GLD/TLT trend sleeve + iter 064 ensemble.

Extends iter 075's sleeve construction to allow per-leg leverage (when
``target_vol / realized_vol > 1``) with honest borrow-drag modeling per
the Frazzini-Pedersen (2014) JFE 111(1) primitive used in iter 060/056.

Sleeve construction (per leg)
-----------------------------
* SMA-200 long-only trend filter (Faber 2007 SSRN 962461): position
  enabled (=1) when ``price[t-1] > SMA200[t-1]`` else 0.
* 21d trailing realized vol; size leg to hit ``target_vol`` annualized
  (Sinclair 2013 `[volatility_trading, p.218]`); cap at ``leg_cap``
  (default 3.0 ⇒ allow up to 3× leverage on a single leg).
* **Borrow drag** (NEW vs iter 075): when ``pos[t-1] > 1``, deduct
  ``(pos[t-1] - 1) × daily_borrow`` from the day's leg return, where
  ``daily_borrow = (1 + borrow_rate_annual) ** (1 / 252) - 1``. Same
  primitive as iter 060/056 `[leverage_for_the_long_run, ch.5]`,
  applied at the leg level rather than post-stream.
* Daily return = ``pos_{t-1} · raw_t - max(pos_{t-1} - 1, 0) · daily_borrow``
  (T-1 lag, no look-ahead per `[advances_fin_ml, p.162-164]`).

Sleeve return = ``0.5 · r_GLD_leg + 0.5 · r_TLT_leg`` (equal-weight
risk parity per `[risk_parity, ch.5]`).

Ensemble
--------
Linear convex blend with iter 064's saved daily-return stream
(identical math to iter 075 / iter 074 — Markowitz 1952 JoF 7(1))::

    r_076[t] = w_064 · r_064[t] + w_sleeve · r_sleeve[t]

Identity properties
-------------------
* When ``target_vol = 0.10, leg_cap = 1.0, borrow_rate_annual = 0.0``,
  output is bit-identical to iter 075 (no leg ever leveraged → no drag).
* When ``borrow_rate_annual = 0.0``, output is identical to a pure
  vol-target sleeve at the given ``target_vol`` regardless of leg_cap.

Citations
---------
* Faber (2007) SSRN 962461 — SMA-200 long-only trend filter.
* `[stocks_on_the_move, p.81]` — trend lookback rationale.
* `[risk_parity, ch.5]` — equal-weight risk parity rationale.
* Erb-Harvey (2006) FAJ 62(2) DOI 10.2469/faj.v62.i2.4084 — gold's
  strategic non-equity role.
* Markowitz (1952) JoF 7(1) DOI 10.1111/j.1540-6261.1952.tb01525.x —
  convex combination math (ensemble).
* `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing.
* `[leverage_for_the_long_run, ch.5]` — Hsiao-Williams 2017 borrow
  cost modeling primitive (now applied at the leg level).
* Frazzini-Pedersen (2014), JFE 111(1) 1-25, DOI 10.1016/j.jfineco.2013.10.005
  — borrow frictions on levered low-vol strategies.
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead) discipline.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]

ITER_064_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "064-2026-04-25-1315-iter058-qqq-trend-substitution"
ITER_064_CFG_ID = "iter046_plus_qqq_trend_w010_lookback200"

ANNUALIZATION = 252


def daily_borrow_from_annual(borrow_rate_annual: float) -> float:
    """Convert annual borrow rate to daily compounded equivalent.

    Identical primitive to iter 060's ``daily_borrow_from_annual``
    `[leverage_for_the_long_run, ch.5]`. ``(1 + r) ** (1/252) - 1``.
    For 4.5% annual this is ≈ 1.745e-4 per bar.
    """
    if borrow_rate_annual < 0:
        raise ValueError(
            f"borrow_rate_annual must be >= 0; got {borrow_rate_annual}"
        )
    return (1.0 + borrow_rate_annual) ** (1.0 / ANNUALIZATION) - 1.0


def _single_leg_returns(
    prices: pd.Series,
    *,
    sma_lookback: int,
    vol_lookback: int,
    target_vol: float,
    leg_cap: float,
    borrow_rate_annual: float,
) -> pd.Series:
    """Compute trend-filtered, vol-targeted, borrow-charged single-asset returns.

    Returns a series aligned to ``prices.index`` with NaN-safe zeros for
    the warmup period (first ``max(sma_lookback, vol_lookback) + 1``
    bars).

    Borrow drag applies only when leg position exceeds 1.0 (the levered
    portion). The first 1.0 of position is treated as unlevered cash
    deployment (no drag); excess uses borrowed funding at
    ``daily_borrow_from_annual(borrow_rate_annual)``.
    """
    raw = prices.pct_change().fillna(0.0)
    sma = prices.rolling(window=sma_lookback, min_periods=sma_lookback).mean()
    # Trend signal computed from price/SMA at T-1 (no look-ahead):
    trend = (prices > sma).astype(float).shift(1).fillna(0.0)
    # Annualized realized vol from raw daily returns at T-1:
    vol_daily = raw.rolling(window=vol_lookback, min_periods=vol_lookback).std()
    vol_ann = vol_daily * np.sqrt(ANNUALIZATION)
    vol_ann_lag = vol_ann.shift(1)
    # Position size: target_vol / vol_ann_lag, capped at leg_cap, gated
    # by trend filter:
    with np.errstate(divide="ignore", invalid="ignore"):
        size_raw = np.where(
            (vol_ann_lag > 0) & np.isfinite(vol_ann_lag),
            target_vol / vol_ann_lag,
            0.0,
        )
    size = np.minimum(size_raw, leg_cap)
    pos = pd.Series(size, index=prices.index) * trend
    pos = pos.fillna(0.0)
    # Leg gross return:
    gross = (pos * raw).fillna(0.0)
    # Borrow drag: charge (pos - 1)+ × daily_borrow per bar (no charge
    # when pos ≤ 1.0; floored at 0.0). Drag is leverage-on-T-1 × daily_borrow.
    daily_borrow = daily_borrow_from_annual(borrow_rate_annual)
    excess_pos = (pos - 1.0).clip(lower=0.0)
    drag = excess_pos * daily_borrow
    leg_returns = (gross - drag).fillna(0.0)
    return leg_returns


def compute_sleeve_returns(
    prices_gld: pd.Series,
    prices_tlt: pd.Series,
    *,
    sma_lookback: int = 200,
    vol_lookback: int = 21,
    target_vol: float = 0.10,
    leg_cap: float = 3.0,
    borrow_rate_annual: float = 0.045,
) -> pd.Series:
    """Compute the equal-weight GLD+TLT trend sleeve daily net returns.

    Parameters
    ----------
    prices_gld, prices_tlt
        Daily price series for the two legs (datetime index).
    sma_lookback
        Lookback for the SMA trend filter (default 200, Faber 2007).
    vol_lookback
        Lookback for the realized-vol estimator (default 21, ~1 month).
    target_vol
        Annualized portfolio-vol target per leg. Iter 076 sweeps this
        across {0.10, 0.15, 0.20, 0.25, 0.30}.
    leg_cap
        Hard cap on per-leg position size (default 3.0 in iter 076,
        vs 1.0 in iter 075).
    borrow_rate_annual
        Annualized borrow rate charged on (pos - 1)+ per leg per bar.
        Default 0.045 (industry-standard retail portfolio-margin SOFR
        + 0.5-1.0% spread).

    Returns
    -------
    pd.Series
        Daily net returns of the equal-weight sleeve, indexed on the
        intersection of the two input price series. Warmup bars (where
        SMA or vol estimators have no data) emit 0.0.
    """
    common = prices_gld.index.intersection(prices_tlt.index)
    if len(common) < max(sma_lookback, vol_lookback) + 2:
        raise ValueError(
            f"insufficient overlap: {len(common)} bars, need "
            f"at least {max(sma_lookback, vol_lookback) + 2}"
        )
    gld = prices_gld.loc[common].astype(float)
    tlt = prices_tlt.loc[common].astype(float)
    r_gld = _single_leg_returns(
        gld, sma_lookback=sma_lookback, vol_lookback=vol_lookback,
        target_vol=target_vol, leg_cap=leg_cap,
        borrow_rate_annual=borrow_rate_annual,
    )
    r_tlt = _single_leg_returns(
        tlt, sma_lookback=sma_lookback, vol_lookback=vol_lookback,
        target_vol=target_vol, leg_cap=leg_cap,
        borrow_rate_annual=borrow_rate_annual,
    )
    sleeve = 0.5 * r_gld + 0.5 * r_tlt
    sleeve.name = "iter076_gld_tlt_levered_trend_sleeve"
    return sleeve


def combine_iter064_with_sleeve(
    r_064: pd.Series,
    r_sleeve: pd.Series,
    *,
    w_064: float,
    w_sleeve: float,
) -> pd.Series:
    """Linear convex blend of iter 064 stream with iter 076 sleeve.

    Mirrors iter 075's combine_iter064_with_sleeve API. Both weights
    must be ≥ 0; their sum must be > 0; inner-join must have ≥ 2 bars.
    """
    if w_064 < 0:
        raise ValueError(f"w_064 must be >= 0; got {w_064}")
    if w_sleeve < 0:
        raise ValueError(f"w_sleeve must be >= 0; got {w_sleeve}")
    if (w_064 + w_sleeve) <= 0:
        raise ValueError(
            f"w_064 + w_sleeve must be > 0; got {w_064 + w_sleeve}"
        )
    common = r_064.index.intersection(r_sleeve.index)
    if len(common) < 2:
        raise ValueError(
            f"r_064 and r_sleeve have <2 overlap bars "
            f"(r_064={len(r_064)}, r_sleeve={len(r_sleeve)})"
        )
    a = r_064.loc[common].astype(float)
    b = r_sleeve.loc[common].astype(float)
    combined = w_064 * a + w_sleeve * b
    combined.name = "iter076_combined"
    return combined


def load_iter064_stream(dataset: str) -> pd.Series:
    """Load iter 064's saved daily-return stream for the given dataset."""
    p = ITER_064_DIR / "results.json"
    with p.open("r", encoding="utf-8") as f:
        results = json.load(f)
    series_dict = results["returns_series"][dataset][ITER_064_CFG_ID]
    idx = pd.to_datetime(series_dict["index"])
    vals = np.asarray(series_dict["net_returns"], dtype=float)
    return pd.Series(vals, index=idx, name=ITER_064_CFG_ID)


def load_price(symbol: str) -> pd.Series:
    """Load adjusted close price for a Tiingo-cached symbol."""
    p = ROOT / "data" / "tiingo" / "daily" / "prices" / f"{symbol}.parquet"
    df = pd.read_parquet(p)
    if "adj_close" in df.columns:
        return df["adj_close"]
    if "close" in df.columns:
        return df["close"]
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            return df[col]
    raise ValueError(f"no numeric price column in {p}")
