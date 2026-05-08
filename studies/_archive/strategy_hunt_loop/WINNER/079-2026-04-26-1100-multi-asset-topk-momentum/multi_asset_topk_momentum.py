"""Iter 079 — Multi-asset Top-K Relative+Absolute Momentum (5+1-asset GEM extension).

Mechanism
---------
At each monthly rebalance (last business day of month M):

1. Compute trailing N-month total return for each of the 5 selectable
   assets (SPY, QQQ, EFA, TLT, GLD).
2. Sort assets by trailing return descending; pick top-K (K∈{1,2,3}).
3. Per-leg absolute-momentum filter: each top-K leg's 1/K weight is
   either kept (lookback ≥ abs_threshold) or routed to AGG (defensive
   bond fallback) — Faber 2007 abs-mom applied PER LEG, not binary.
4. Allocation applied to month M+1's daily returns (T-1 lag,
   `[advances_fin_ml, p.162-164]`).

Cost: ``trans_cost_bps × |Δw|_1`` charged on the first business day of
the new month. The L1 norm is summed across all 6 sleeves
(SPY+QQQ+EFA+TLT+GLD+AGG).

Citations
---------
* **Antonacci, G.** (2014). *Dual Momentum Investing.* McGraw-Hill.
  ISBN 978-0071849449. — primary GEM source extended to 5+1 assets.
* **Antonacci, G.** (2017). "Risk Premia Harvesting Through Dual
  Momentum." *J. Portfolio Management* 16(1), 27-55.
  DOI 10.3905/joi.2017.16.1.027.
* **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." *J. Wealth Management* 9(4), 69-79.
  DOI 10.3905/jwm.2007.690606 — per-leg abs-mom variant adopted here.
* **Jegadeesh, N., Titman, S.** (1993). "Returns to Buying Winners
  and Selling Losers." *JoF* 48(1), 65-91.
* **Asness, C., Moskowitz, T., Pedersen, L.** (2013). "Value and
  Momentum Everywhere." *JoF* 68(3), 929-985.
* **Markowitz, H.** (1952). "Portfolio Selection." *JoF* 7(1), 77-91.
* `[stocks_on_the_move, p.21-30, p.81]` — Clenow's momentum framework.
* `[systematic_trading, p.42 (ch.2)]` — Carver's Law of Active Mgmt.
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]


# Selectable cross-asset universe (excludes AGG which is the defensive fallback)
SELECTABLE_ASSETS: list[str] = ["SPY", "QQQ", "EFA", "TLT", "GLD"]
ALL_SLEEVES: list[str] = SELECTABLE_ASSETS + ["AGG"]


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


def compute_monthly_rebalance_dates(daily_index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Last business day of each month present in ``daily_index``."""
    df = pd.DataFrame(index=daily_index)
    df["ym"] = df.index.to_period("M")
    last = df.groupby("ym").apply(lambda x: x.index.max())
    return pd.DatetimeIndex(last.values).sort_values()


def compute_lookback_returns_multi(
    monthly_prices: dict[str, pd.Series],
    lookback_months: int,
) -> pd.DataFrame:
    """N-month trailing total return per asset, indexed on common monthly dates.

    Only the 5 selectable assets appear in the output DataFrame —
    AGG is the defensive fallback and not eligible for top-K selection.
    """
    if lookback_months < 1:
        raise ValueError(f"lookback_months must be ≥ 1; got {lookback_months}")
    cols = {}
    common_idx: pd.DatetimeIndex | None = None
    for asset in SELECTABLE_ASSETS:
        if asset not in monthly_prices:
            raise KeyError(f"missing monthly_prices['{asset}']")
        p = monthly_prices[asset]
        lb = p / p.shift(lookback_months) - 1.0
        cols[asset] = lb
        common_idx = lb.index if common_idx is None else common_idx.intersection(lb.index)
    df = pd.DataFrame({a: cols[a].reindex(common_idx) for a in SELECTABLE_ASSETS})
    return df


def top_k_signal(
    lookback_df: pd.DataFrame,
    top_k: int,
    abs_threshold: float = 0.0,
) -> pd.DataFrame:
    """Build top-K equal-weight signal with per-leg AGG routing.

    Each row is processed independently:
      - Rank the 5 selectable assets by trailing return descending
        (deterministic tie-break by alphabetical asset name).
      - Pick the top ``top_k`` assets; each gets a 1/K share.
      - Each picked asset whose lookback ≥ ``abs_threshold`` keeps its
        share; each whose lookback < ``abs_threshold`` routes its 1/K
        share to AGG (defensive fallback).

    NaN rows (warmup) yield all-zero weights (caller treats as flat).
    Output sums to 1.0 per row when there is any valid signal.

    Parameters
    ----------
    lookback_df
        DataFrame with rows = monthly rebalance dates, cols =
        SELECTABLE_ASSETS. Each cell is the trailing N-month return.
    top_k
        Integer in {1, 2, 3, 4, 5}. Number of top-ranked assets to hold.
    abs_threshold
        Per-leg absolute-momentum threshold. A picked asset whose
        lookback < threshold routes its share to AGG.

    Returns
    -------
    DataFrame with rows = lookback_df.index, cols = ALL_SLEEVES (6),
    each cell = weight ∈ [0, 1]. Each row sums to 1.0 (or 0.0 for NaN
    warmup rows).
    """
    if top_k < 1 or top_k > len(SELECTABLE_ASSETS):
        raise ValueError(
            f"top_k must be in [1, {len(SELECTABLE_ASSETS)}]; got {top_k}"
        )
    if not list(lookback_df.columns) == SELECTABLE_ASSETS:
        raise ValueError(
            f"lookback_df.columns must equal SELECTABLE_ASSETS={SELECTABLE_ASSETS}; "
            f"got {list(lookback_df.columns)}"
        )

    out = pd.DataFrame(0.0, index=lookback_df.index, columns=ALL_SLEEVES)
    weight_per_leg = 1.0 / top_k

    for ts, row in lookback_df.iterrows():
        if row.isna().any():
            continue  # warmup: stay flat (all zeros)
        # Sort descending; alphabetical tie-break — stable sort + name ordering.
        # We want highest first; then alphabetical for ties.
        sorted_assets = sorted(
            row.index, key=lambda a: (-row[a], a)
        )
        picks = sorted_assets[:top_k]
        for asset in picks:
            if row[asset] >= abs_threshold:
                out.at[ts, asset] = weight_per_leg
            else:
                out.at[ts, "AGG"] += weight_per_leg
    return out


def compute_topk_returns(
    daily_returns: dict[str, pd.Series],
    signal_df: pd.DataFrame,
    *,
    trans_cost_bps: float = 5.0,
) -> pd.Series:
    """Apply monthly top-K signal to daily returns with T-1 lag + cost.

    Parameters
    ----------
    daily_returns
        Dict with keys = ALL_SLEEVES (6 assets); values = pd.Series of
        daily returns sharing the same daily index.
    signal_df
        DataFrame indexed on monthly rebalance dates with cols =
        ALL_SLEEVES. Each row is a weight vector summing to 0 or 1.
    trans_cost_bps
        Cost in bps applied to the L1 turnover on rebalance days.

    Returns
    -------
    Daily net returns aligned to ``daily_returns["SPY"].index``.
    """
    if trans_cost_bps < 0:
        raise ValueError(f"trans_cost_bps must be ≥ 0; got {trans_cost_bps}")
    for asset in ALL_SLEEVES:
        if asset not in daily_returns:
            raise KeyError(f"missing daily_returns['{asset}']")
    spy = daily_returns["SPY"]
    daily_idx = spy.index
    if not isinstance(daily_idx, pd.DatetimeIndex):
        daily_idx = pd.DatetimeIndex(daily_idx)
    for asset in ALL_SLEEVES[1:]:
        if not daily_returns[asset].index.equals(spy.index):
            raise ValueError(f"daily_returns['{asset}'] index mismatch with SPY")

    # Reorder signal columns to match ALL_SLEEVES.
    sig = signal_df.reindex(columns=ALL_SLEEVES, fill_value=0.0)
    rebal_dates = sig.index
    if not isinstance(rebal_dates, pd.DatetimeIndex):
        rebal_dates = pd.DatetimeIndex(rebal_dates)
    rebal_dates = rebal_dates.sort_values()
    sig_sorted = sig.loc[rebal_dates]

    n_days = len(daily_idx)
    n_sleeves = len(ALL_SLEEVES)
    w_mat = np.zeros((n_days, n_sleeves), dtype=float)

    if len(rebal_dates) > 0:
        rebal_arr = rebal_dates.values
        days_arr = daily_idx.values
        # For each day d, find latest rebalance index ridx where rebal[ridx] < d.
        ins = np.searchsorted(rebal_arr, days_arr, side="left")
        rebal_idx = ins - 1
        sig_arr = sig_sorted.values  # shape (n_rebal, n_sleeves)
        valid = rebal_idx >= 0
        # Vectorized: for valid days, w_mat[i] = sig_arr[rebal_idx[i]]
        w_mat[valid] = sig_arr[rebal_idx[valid]]

    w_prev = np.vstack([np.zeros((1, n_sleeves)), w_mat[:-1]])
    turnover = np.abs(w_mat - w_prev).sum(axis=1)
    cost = turnover * (trans_cost_bps / 10000.0)

    # Stack daily returns in the same column order.
    ret_mat = np.column_stack([daily_returns[a].values for a in ALL_SLEEVES])
    gross = (w_mat * ret_mat).sum(axis=1)
    net = gross - cost
    return pd.Series(net, index=daily_idx, name="iter079_topk")
