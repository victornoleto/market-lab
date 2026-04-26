"""Iter 078 — Antonacci Dual Momentum (GEM) standalone-base strategy.

Mechanism
---------
At each monthly rebalance (last business day of month M), compute the
trailing N-month total return of US equity (SPY) and developed-
international equity (EFA). Pick the asset with the higher trailing
return — RELATIVE momentum (Jegadeesh-Titman 1993). If the winner's
trailing return is also above the absolute-momentum threshold (0% or
T-bill proxy via IEF trailing return) — ABSOLUTE momentum (Faber 2007)
— allocate 100% to the winner; otherwise allocate 100% to AGG (US
aggregate bond — defensive sleeve).

The chosen allocation is applied to month M+1's daily returns
(T-1 lag, no look-ahead per `[advances_fin_ml, p.162-164]`).

Costs: ``trans_cost_bps × |Δposition|`` charged on the first business
day of the new month, where ``|Δposition|`` is the L1 norm of the
allocation vector change (e.g., switching SPY→EFA = 1.0 + 1.0 = 2.0
turnover units).

Citations
---------
* **Antonacci, G.** (2014). *Dual Momentum Investing.* McGraw-Hill.
  ISBN 978-0071849449. — primary GEM source.
* **Antonacci, G.** (2017). "Risk Premia Harvesting Through Dual
  Momentum." *J. Portfolio Management* 16(1), 27-55.
  DOI 10.3905/joi.2017.16.1.027.
* **Faber, M.** (2007). "A Quantitative Approach to Tactical Asset
  Allocation." *J. Wealth Management* 9(4), 69-79.
  DOI 10.3905/jwm.2007.690606 — absolute momentum (timing filter).
* **Jegadeesh, N., Titman, S.** (1993). "Returns to Buying Winners
  and Selling Losers." *JoF* 48(1), 65-91.
  DOI 10.1111/j.1540-6261.1993.tb04702.x — relative momentum primitive.
* **Asness, C., Moskowitz, T., Pedersen, L.** (2013). "Value and
  Momentum Everywhere." *JoF* 68(3), 929-985.
  DOI 10.1111/jofi.12021.
* **Moskowitz, T., Ooi, Y. H., Pedersen, L.** (2012). "Time Series
  Momentum." *JFE* 104(2), 228-250.
* `[stocks_on_the_move, p.21-30]` — Clenow's momentum framework
  (cross-sectional ranking discipline).
* `[systematic_trading, p.42 (ch.2)]` — Carver's Law of Active
  Management (multi-asset diversification rationale).
* `[advances_fin_ml, p.162-164]` — T-1 lag (no look-ahead).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]


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
    """Last business day of each month present in ``daily_index``.

    Uses the actual observed trading days (groupby year-month, take max),
    so holidays and partial months are handled correctly.
    """
    df = pd.DataFrame(index=daily_index)
    df["ym"] = df.index.to_period("M")
    last = df.groupby("ym").apply(lambda x: x.index.max())
    return pd.DatetimeIndex(last.values).sort_values()


def compute_lookback_return(
    monthly_prices: pd.Series, lookback_months: int,
) -> pd.Series:
    """N-month trailing total return at each monthly observation.

    ``out[t] = price[t] / price[t - lookback_months] - 1``.
    First ``lookback_months`` entries are NaN.
    """
    if lookback_months < 1:
        raise ValueError(f"lookback_months must be ≥ 1; got {lookback_months}")
    return monthly_prices / monthly_prices.shift(lookback_months) - 1.0


def gem_signal(
    spy_lb: pd.Series,
    efa_lb: pd.Series,
    threshold: pd.Series,
) -> pd.Series:
    """GEM allocation signal per month.

    Truth table per month:
      - winner = "SPY" if spy_lb >= efa_lb else "EFA" (relative momentum)
      - if winner_lb > threshold[t] → allocate winner (absolute momentum filter clears)
      - else → allocate "AGG" (defensive)

    Inputs are aligned to monthly rebalance dates. NaN inputs (warmup
    bars) yield NaN signal which the caller treats as "stay flat".
    """
    if not (spy_lb.index.equals(efa_lb.index) and spy_lb.index.equals(threshold.index)):
        raise ValueError("spy_lb, efa_lb, threshold must share index")
    signal = pd.Series(index=spy_lb.index, dtype=object)
    valid = spy_lb.notna() & efa_lb.notna() & threshold.notna()
    spy_v = spy_lb.where(valid)
    efa_v = efa_lb.where(valid)
    th_v = threshold.where(valid)
    winner = np.where(spy_v >= efa_v, "SPY", "EFA")
    winner_lb = np.where(spy_v >= efa_v, spy_v.values, efa_v.values)
    chosen = np.where(winner_lb > th_v.values, winner, "AGG")
    signal.loc[valid] = chosen[valid.values]
    return signal


def compute_gem_returns(
    daily_returns: dict[str, pd.Series],
    signal: pd.Series,
    *,
    trans_cost_bps: float = 5.0,
) -> pd.Series:
    """Apply the GEM monthly signal to daily returns with T-1 lag + cost.

    Parameters
    ----------
    daily_returns
        Dict with keys ``{"SPY", "EFA", "AGG"}``; each value is a
        pd.Series of daily returns sharing the same daily index.
    signal
        Monthly signal indexed on rebalance dates (last bday of each
        month). Values must be ``"SPY"``, ``"EFA"``, ``"AGG"``, or NaN
        (warmup → flat).
    trans_cost_bps
        Cost in bps on the L1 turnover when allocation changes,
        charged on the first day of the new month.

    Returns
    -------
    pd.Series indexed on the daily date range, with daily net returns.
    """
    if trans_cost_bps < 0:
        raise ValueError(f"trans_cost_bps must be ≥ 0; got {trans_cost_bps}")
    spy = daily_returns["SPY"]
    efa = daily_returns["EFA"]
    agg = daily_returns["AGG"]
    if not (spy.index.equals(efa.index) and spy.index.equals(agg.index)):
        raise ValueError("daily returns must share index across SPY/EFA/AGG")
    daily_idx = spy.index
    if not isinstance(daily_idx, pd.DatetimeIndex):
        daily_idx = pd.DatetimeIndex(daily_idx)

    rebal_dates = signal.index
    if not isinstance(rebal_dates, pd.DatetimeIndex):
        rebal_dates = pd.DatetimeIndex(rebal_dates)

    # Build per-day allocation vector (w_spy, w_efa, w_agg) ∈ {0, 1} per day.
    # Allocation at day d is determined by the signal at the LAST rebalance
    # date < d (T-1 lag — signal computed on close of M, applied next session).
    w_spy = np.zeros(len(daily_idx), dtype=float)
    w_efa = np.zeros(len(daily_idx), dtype=float)
    w_agg = np.zeros(len(daily_idx), dtype=float)

    if len(rebal_dates) > 0:
        rebal_arr = rebal_dates.values
        days_arr = daily_idx.values
        # For each day, find the most-recent rebalance date strictly less than it.
        # searchsorted with side='left' on sorted rebal returns insertion idx;
        # subtracting 1 gives last rebal index < day.
        ins = np.searchsorted(rebal_arr, days_arr, side="left")
        rebal_idx = ins - 1
        for i, ridx in enumerate(rebal_idx):
            if ridx < 0:
                continue
            sig_v = signal.iloc[ridx]
            if pd.isna(sig_v):
                continue
            if sig_v == "SPY":
                w_spy[i] = 1.0
            elif sig_v == "EFA":
                w_efa[i] = 1.0
            elif sig_v == "AGG":
                w_agg[i] = 1.0

    # Daily turnover: |w_t - w_{t-1}| summed across legs (L1 norm).
    w_mat = np.stack([w_spy, w_efa, w_agg], axis=1)  # (T, 3)
    w_prev = np.vstack([np.zeros((1, 3)), w_mat[:-1]])  # day-0 prior = flat
    turnover = np.abs(w_mat - w_prev).sum(axis=1)
    cost = turnover * (trans_cost_bps / 10000.0)

    gross = (
        w_spy * spy.values
        + w_efa * efa.values
        + w_agg * agg.values
    )
    net = gross - cost
    return pd.Series(net, index=daily_idx, name="iter078_gem")
