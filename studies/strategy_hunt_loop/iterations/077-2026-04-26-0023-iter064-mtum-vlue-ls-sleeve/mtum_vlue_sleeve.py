"""Iter 077 — Long-short MTUM−VLUE factor sleeve + iter 064 ensemble.

Sleeve construction
-------------------
Dollar-neutral long-short on Carhart's UMD primitive (long momentum,
short value), proxied by liquid US-large-cap factor ETFs MTUM (iShares
MSCI USA Momentum, 2013-04-16) and VLUE (iShares MSCI USA Value,
2013-04-16):

    raw_t      = adj_close_MTUM[t]/adj_close_MTUM[t-1] - 1
    raw_t      − adj_close_VLUE[t]/adj_close_VLUE[t-1] - 1
    spread_t   = ret_MTUM_t - ret_VLUE_t      (gross long-short spread)
    vol_{t-1}  = std(spread[t-vol_lb : t]) · √252
    pos_{t-1}  = clip(target_vol / vol_{t-1}, 0, leg_cap)
    borrow_t   = pos_{t-1} · short_borrow_rate / 252       (short-side daily charge)
    cost_t     = trans_cost_bps · |pos_{t-1} - pos_{t-2}|  (turnover)
    r_sleeve_t = pos_{t-1} · spread_t - borrow_t - cost_t

Borrow rate default 1%/yr is the retail-margin securities-lending fee
on liquid US ETFs (Frazzini-Pedersen 2014 short-leg borrow primitive).
Transaction cost default 5 bps on |Δposition| matches iter 075 tc.

Ensemble
--------
Linear convex blend with iter 064's saved daily-return stream::

    r_077[t] = w_064 · r_064[t] + w_sleeve · r_sleeve[t]

Math identical to iter 074/075/076 outer-Markowitz convex combination
(Markowitz 1952 JoF 7(1)). Saved streams are pre-validated; the
combine is closed-form.

Citations
---------
* Carhart (1997) JoF 52(1) 57-82 — UMD long-short momentum factor.
* Asness-Moskowitz-Pedersen (2013) JoF 68(3) — value-momentum cross
  factor pair with documented Sharpe 0.7-1.1 on US equities.
* Jegadeesh-Titman (1993) JoF 48(1) — momentum primitive.
* Fama-French (1993) JFE 33(1) — value (HML) primitive.
* `[stocks_on_the_move, p.21-30]` — Clenow's momentum framework.
* `[volatility_trading, p.218]` — Sinclair (2013) inverse-vol sizing.
* Frazzini-Pedersen (2014) JFE 111(1) — short-leg borrow charge.
* `[risk_parity, ch.5]` — Asness-Frazzini-Pedersen (2012) risk parity.
* Markowitz (1952) JoF 7(1) — convex combination math (ensemble).
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
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


def compute_sleeve_returns(
    prices_mtum: pd.Series,
    prices_vlue: pd.Series,
    *,
    vol_lookback: int = 21,
    target_vol: float = 0.10,
    leg_cap: float = 1.0,
    short_borrow_rate: float = 0.01,
    trans_cost_bps: float = 5.0,
) -> pd.Series:
    """Compute the dollar-neutral long-MTUM short-VLUE sleeve returns.

    Parameters
    ----------
    prices_mtum, prices_vlue
        Daily price series for the two legs (datetime index).
    vol_lookback
        Lookback for the realized-vol estimator on the spread (default 21).
    target_vol
        Annualized target vol for the sleeve (default 0.10).
    leg_cap
        Hard cap on position size (default 1.0 — no leverage).
    short_borrow_rate
        Annualized borrow charge applied to the short leg notional
        (default 0.01 — 1%/yr retail-rate for liquid ETFs).
    trans_cost_bps
        Transaction cost in bps on |Δposition| (default 5).

    Returns
    -------
    pd.Series
        Daily net returns of the long-short sleeve, indexed on the
        intersection of the two input price series. Warmup bars (where
        vol estimator has no data) emit 0.0.
    """
    common = prices_mtum.index.intersection(prices_vlue.index)
    if len(common) < vol_lookback + 2:
        raise ValueError(
            f"insufficient overlap: {len(common)} bars, need "
            f"at least {vol_lookback + 2}"
        )
    if leg_cap < 0:
        raise ValueError(f"leg_cap must be >= 0; got {leg_cap}")
    if target_vol < 0:
        raise ValueError(f"target_vol must be >= 0; got {target_vol}")
    if short_borrow_rate < 0:
        raise ValueError(f"short_borrow_rate must be >= 0; got {short_borrow_rate}")
    if trans_cost_bps < 0:
        raise ValueError(f"trans_cost_bps must be >= 0; got {trans_cost_bps}")

    mtum = prices_mtum.loc[common].astype(float)
    vlue = prices_vlue.loc[common].astype(float)

    ret_mtum = mtum.pct_change().fillna(0.0)
    ret_vlue = vlue.pct_change().fillna(0.0)
    spread = ret_mtum - ret_vlue

    vol_daily = spread.rolling(window=vol_lookback, min_periods=vol_lookback).std()
    vol_ann = vol_daily * np.sqrt(ANNUALIZATION)
    vol_ann_lag = vol_ann.shift(1)

    with np.errstate(divide="ignore", invalid="ignore"):
        size_raw = np.where(
            (vol_ann_lag > 0) & np.isfinite(vol_ann_lag),
            target_vol / vol_ann_lag,
            0.0,
        )
    pos = pd.Series(np.minimum(np.maximum(size_raw, 0.0), leg_cap), index=common)
    pos = pos.fillna(0.0)

    daily_borrow = pos * (short_borrow_rate / ANNUALIZATION)
    pos_diff = pos.diff().abs().fillna(pos.iloc[0])
    cost = pos_diff * (trans_cost_bps / 10000.0)

    sleeve = (pos * spread - daily_borrow - cost).fillna(0.0)
    sleeve.name = "iter077_mtum_vlue_ls_sleeve"
    return sleeve


def combine_iter064_with_sleeve(
    r_064: pd.Series,
    r_sleeve: pd.Series,
    *,
    w_064: float,
    w_sleeve: float,
) -> pd.Series:
    """Linear convex blend of iter 064 stream with the iter 077 sleeve.

    Mirrors iter 075 API. Both weights must be ≥ 0; their sum > 0.

    Phase-in approach: when the sleeve has no data for a given date
    (e.g. pre-2013 because MTUM/VLUE inception is 2013-04-18), the
    iter 064 leg keeps its full 1.0 weight (we can't allocate to a
    non-existent sleeve, so we don't dilute the iter 064 anchor).
    Only on dates where the sleeve has data do we apply the convex
    blend ``w_064 · r_064 + w_sleeve · r_sleeve``.

    This represents the realistic "deployed-as-of-sleeve-inception"
    interpretation, avoiding artificial under-investment during the
    pre-sleeve era.
    """
    if w_064 < 0:
        raise ValueError(f"w_064 must be >= 0; got {w_064}")
    if w_sleeve < 0:
        raise ValueError(f"w_sleeve must be >= 0; got {w_sleeve}")
    if (w_064 + w_sleeve) <= 0:
        raise ValueError(
            f"w_064 + w_sleeve must be > 0; got {w_064 + w_sleeve}"
        )
    union = r_064.index.union(r_sleeve.index)
    if len(union) < 2:
        raise ValueError(
            f"r_064 and r_sleeve combined have <2 bars "
            f"(r_064={len(r_064)}, r_sleeve={len(r_sleeve)})"
        )
    a = r_064.reindex(union).fillna(0.0).astype(float)
    b = r_sleeve.reindex(union).fillna(0.0).astype(float)
    sleeve_present = r_sleeve.reindex(union).notna()
    # Default: full iter 064 weight (sleeve absent).
    eff_w_064 = pd.Series(1.0, index=union)
    eff_w_sleeve = pd.Series(0.0, index=union)
    # Where sleeve is present, apply the convex blend weights.
    eff_w_064[sleeve_present] = w_064
    eff_w_sleeve[sleeve_present] = w_sleeve
    combined = eff_w_064 * a + eff_w_sleeve * b
    combined.name = "iter077_combined"
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
