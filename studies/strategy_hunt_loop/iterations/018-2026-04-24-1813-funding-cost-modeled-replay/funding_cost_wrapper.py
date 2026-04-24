"""Iter 018 — Funding-cost wrapper around iter 016's static-stack VM primitive.

Applies a per-bar funding cost `(scale - 1) × r_Tbill` to iter 016's
synthetic stack's net returns. The extra-leverage fraction
`max(scale - 1, 0)` must be financed via short-term credit at the
prevailing T-bill rate. SHV (iShares Short Treasury Bond ETF, 1-3 mo
duration, inception 2007-01-11) is used as the `r_Tbill` proxy.

For the pre-SHV segment of the educational dataset (2006-01-03 →
2007-01-10, 251 bars), we pad with a constant
`r_Tbill_daily = 0.0475 / 252 ≈ 1.88e-4` matching the 2006 FRED DGS3MO
annual mean (Fed Funds target midpoint for the year).

Citations
---------
* `[risk_parity, p.80-84, ch.4]` — levered portfolio return decomposition
  `r_lev = L · r_asset − (L − 1) · r_f`.
* `[systematic_trading, p.170-171, ch.11]` — IDM as marginal cost of
  risk; leverage above 1.0× must earn excess over financing.
* `[advances_fin_ml, p.162-164]` — lag 1 bar on rate inputs (no
  look-ahead).
* NTSX prospectus — synthetic 90/60 stack structural funding cost.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"

sys.path.insert(0, str(ITER_016_DIR))
from static_stack_vm import apply_static_stack_vol_managed  # noqa: E402

TIINGO_DIR = ROOT / "data" / "tiingo" / "daily" / "prices"

# 2006 mean DGS3MO from FRED (pre-SHV pad rate). Chosen to match the
# 2006-Jan-Dec average Fed Funds target midpoint (4.25% → 5.25% window).
# This padding only affects the first ~251 bars of the educational
# dataset (2006-01-03 → 2007-01-10) — SHV inception is 2007-01-11.
PRE_SHV_PAD_ANNUAL = 0.0475
PRE_SHV_PAD_DAILY = PRE_SHV_PAD_ANNUAL / 252.0


def load_shv_daily_return(index: pd.DatetimeIndex) -> pd.Series:
    """Load SHV adj_close → simple daily return, aligned to `index`.

    For dates before SHV inception (2007-01-11), fill with the constant
    pad rate `PRE_SHV_PAD_DAILY` (matches 2006 FRED DGS3MO mean).

    The returned series is lagged 1 bar (as σ̂ is) to avoid look-ahead —
    funding cost on bar t uses yesterday's known T-bill rate.
    """
    shv = pd.read_parquet(TIINGO_DIR / "SHV.parquet")
    shv_ret = shv["adj_close"].pct_change()

    # Lag 1 bar (use r_{t-1} to finance bar t exposure set at open of t).
    shv_ret_lag = shv_ret.shift(1)

    # Reindex onto caller's index; dates before SHV start become NaN.
    aligned = shv_ret_lag.reindex(index)

    # Pad pre-SHV dates with constant rate.
    aligned = aligned.fillna(PRE_SHV_PAD_DAILY)
    aligned.name = "r_tbill"
    return aligned


def apply_funding_cost(
    net_gross: pd.Series,
    scale: pd.Series,
    r_tbill: pd.Series,
) -> tuple[pd.Series, pd.Series]:
    """Subtract per-bar levered financing cost from iter 016's `net`.

    Parameters
    ----------
    net_gross : pd.Series
        Iter 016's net returns (pre-funding-cost). Indexed on the
        valid bars after lookback warm-up.
    scale : pd.Series
        Iter 016's total gross exposure series. Same index as `net_gross`.
    r_tbill : pd.Series
        Daily simple T-bill return, lagged 1 bar, aligned to the full
        outer index (before lookback drop). Indexed on calendar days.

    Returns
    -------
    (net_post_cost, funding_cost) : (pd.Series, pd.Series)
        Both aligned on `net_gross`'s index. `funding_cost` is the
        per-bar subtraction amount (positive when scale > 1, zero
        otherwise).
    """
    if not net_gross.index.equals(scale.index):
        raise ValueError(
            "net_gross and scale must share the same index; "
            f"got {len(net_gross)} vs {len(scale)}"
        )
    # Align T-bill rate to the valid-bar index.
    r_tbill_valid = r_tbill.reindex(net_gross.index)
    if r_tbill_valid.isna().any():
        n_nan = int(r_tbill_valid.isna().sum())
        raise ValueError(
            f"r_tbill has {n_nan} NaN bars after reindexing to "
            f"net_gross.index — check SHV / pad coverage"
        )
    # Funding cost = max(scale - 1, 0) × r_tbill. The max(·, 0) clause
    # ensures we do not credit the portfolio when under-levered, which
    # matches real-world synthetic-ETF construction where the fee is
    # paid regardless of leverage direction.
    excess_lev = (scale - 1.0).clip(lower=0.0)
    funding_cost = excess_lev * r_tbill_valid
    funding_cost.name = "funding_cost"
    net_post = (net_gross - funding_cost).astype(float)
    net_post.name = "net_post_cost"
    return net_post, funding_cost


def apply_static_stack_vm_funded(
    r_eq: pd.Series,
    r_bd: pd.Series,
    r_tbill: pd.Series,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Iter 016 primitive + funding cost pass-through.

    Returns
    -------
    (net_post, net_gross, pos_eq, pos_bd, scale, funding_cost)
    """
    net_gross, pos_eq, pos_bd, scale = apply_static_stack_vol_managed(
        r_eq, r_bd,
        eq_weight=eq_weight, bd_weight=bd_weight,
        target_vol=target_vol, lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    net_post, funding_cost = apply_funding_cost(net_gross, scale, r_tbill)
    return net_post, net_gross, pos_eq, pos_bd, scale, funding_cost
