"""Dual-broker cost models for the gold swing loop.

Two execution paths are modelled (per `INFRASTRUCTURE.md`):

* **Track A — Pepperstone XAUUSD CFD** (`apply_pepperstone_costs`)
  spread + per-night swap (long −, short +) + weekend 3× swap multiplier;
  zero swap on intraday-close strategies.

* **Track B — Banco Inter Internacional ETF** (`apply_inter_costs_with_darf`)
  FX round-trip + DARF 15% on positive monthly net profits;
  long-only and T+1 settlement enforced by caller (signed position must
  be ``≥ 0`` and bars are daily).

Inputs are normalized:

* ``gross_returns`` — bar-to-bar fractional returns of the underlying
  (close-to-close).
* ``position`` — signed exposure in **units of capital** at each bar's
  close. ``+1.0`` = full long, ``−1.0`` = full short, ``0`` = flat.
  Position is assumed held FOR the next bar (i.e., position[t] applies
  to ret[t+1]). Per-bar PnL = position.shift(1) × gross_returns.

Costs are deducted from the strategy's bar-PnL series and the function
returns ``(net_pnl, cost_breakdown)``.

References
----------
* Pepperstone Razor XAUUSD spec — `INFRASTRUCTURE.md` Track A
* DARF 15% rule — Brazilian fiscal rule; `INFRASTRUCTURE.md` Track B
* `[advances_fin_ml, p.31-34]` — cost realism in backtest validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Default rate cards (verify each iter; conservative — slightly worse than
# Pepperstone Razor mid-2026 published spec).
# ---------------------------------------------------------------------------

PEPPERSTONE_SPREAD_RT_BPS = 8.0       # round-trip; 4 bps per side
PEPPERSTONE_SWAP_LONG_BPS = -1.0      # per night per unit (negative = paid)
PEPPERSTONE_SWAP_SHORT_BPS = 0.3      # per night per unit (positive = received)
PEPPERSTONE_SLIPPAGE_BPS = 5.0        # per stop-out (caller adds via cost_breakdown)
PEPPERSTONE_WEEKEND_MULT = 3.0        # Friday-close hold incurs 3× swap

INTER_FX_RT_BPS = 100.0               # 100 bps round-trip; 50 bps per side
INTER_DARF_RATE = 0.15                # 15% on positive monthly net profits
INTER_GLD_EER_BPS_PER_YEAR = 40.0     # already netted from NAV; informational
INTER_IAU_EER_BPS_PER_YEAR = 25.0


@dataclass
class CostBreakdown:
    """Per-bar attribution of cost components."""

    gross_pnl: pd.Series
    spread_cost: pd.Series
    swap_cost: pd.Series
    fx_cost: pd.Series
    darf_cost: pd.Series  # zero except on track B (and only on +month bars)
    net_pnl: pd.Series
    total_turnover: float
    n_swap_nights: int
    n_weekend_holds: int
    track: str

    def summary(self) -> dict:
        return {
            "track": self.track,
            "gross_total_pnl": float(self.gross_pnl.sum()),
            "spread_total_pnl": float(-self.spread_cost.sum()),
            "swap_total_pnl": float(-self.swap_cost.sum()),
            "fx_total_pnl": float(-self.fx_cost.sum()),
            "darf_total_pnl": float(-self.darf_cost.sum()),
            "net_total_pnl": float(self.net_pnl.sum()),
            "total_turnover": float(self.total_turnover),
            "n_swap_nights": int(self.n_swap_nights),
            "n_weekend_holds": int(self.n_weekend_holds),
        }


def _bps(x: float) -> float:
    return x / 1e4


def _bar_pnl(position: pd.Series, gross_returns: pd.Series) -> pd.Series:
    """Realised bar PnL: position decided at bar t-1, return at bar t."""
    pos = position.shift(1).fillna(0.0)
    return (pos * gross_returns).fillna(0.0)


def _spread_cost_series(
    position: pd.Series,
    spread_rt_bps: float,
) -> pd.Series:
    """Per-bar spread cost from absolute position changes."""
    per_side = _bps(spread_rt_bps) / 2.0
    delta = position.diff().abs().fillna(position.iloc[0])
    return delta * per_side


def _swap_cost_series(
    position: pd.Series,
    swap_long_bps: float,
    swap_short_bps: float,
    weekend_mult: float,
) -> tuple[pd.Series, int, int]:
    """Per-bar swap cost; only on overnight holds (daily bars only).

    Convention: position carried from close[t-1] to close[t] earns swap on
    bar t. Friday → Monday accrues 3× the standard swap to cover the
    weekend (matches Pepperstone CFD convention).

    For 1h bars, swap is only charged at the daily-close bar (NY close
    ~21:00 UTC). The caller is responsible for either (a) using
    ``intraday_close=True`` if positions never carry overnight, or
    (b) collapsing intraday positions onto an end-of-day flag before
    calling this helper.
    """
    pos_overnight = position.shift(1).fillna(0.0)
    long_mask = pos_overnight > 0
    short_mask = pos_overnight < 0

    swap_long_per_night = _bps(swap_long_bps)   # negative number for longs
    swap_short_per_night = _bps(swap_short_bps)

    # Per-bar swap (price-of-holding); positive cost = drag.
    # Long position pays |swap_long_bps| per night; short receives.
    cost = pd.Series(0.0, index=position.index)
    cost[long_mask] = -pos_overnight[long_mask] * swap_long_per_night
    cost[short_mask] = -pos_overnight[short_mask] * swap_short_per_night
    # Note sign: long pays (positive cost), short receives (negative cost).

    # Weekend multiplier: bars where prior bar was Friday and this bar is
    # Monday (or first business day after weekend).
    if isinstance(position.index, pd.DatetimeIndex):
        is_monday_after_friday = (
            (position.index.dayofweek == 0)
            & (position.index.to_series().shift(1).dt.dayofweek == 4)
        ).fillna(False)
        cost[is_monday_after_friday] *= weekend_mult
        n_weekend = int(is_monday_after_friday.sum())
    else:
        n_weekend = 0

    n_nights = int((long_mask | short_mask).sum())
    return cost, n_nights, n_weekend


def apply_pepperstone_costs(
    gross_returns: pd.Series,
    position: pd.Series,
    *,
    spread_rt_bps: float = PEPPERSTONE_SPREAD_RT_BPS,
    swap_long_bps: float = PEPPERSTONE_SWAP_LONG_BPS,
    swap_short_bps: float = PEPPERSTONE_SWAP_SHORT_BPS,
    weekend_mult: float = PEPPERSTONE_WEEKEND_MULT,
    intraday_close: bool = False,
) -> CostBreakdown:
    """Apply Pepperstone XAUUSD CFD cost model to a strategy's bar-PnL.

    Parameters
    ----------
    gross_returns : pd.Series
        Bar-to-bar fractional returns of the underlying.
    position : pd.Series
        Signed position size at each bar's close (held into next bar).
        Same index as ``gross_returns``.
    spread_rt_bps : float
        Round-trip spread, applied as ``spread/2`` per side on
        ``abs(position.diff())``.
    swap_long_bps : float
        Per-night cost for a +1 long position (negative = pays).
    swap_short_bps : float
        Per-night cost for a −1 short position (positive = receives).
    weekend_mult : float
        Multiplier applied to swap on the bar that crosses the weekend.
    intraday_close : bool
        If True, swap is zeroed out (caller guarantees position closes
        before each daily session end). Recommended for sub-1d strategies.
    """
    if not gross_returns.index.equals(position.index):
        raise ValueError("gross_returns and position must share index")

    gross_pnl = _bar_pnl(position, gross_returns)
    spread = _spread_cost_series(position, spread_rt_bps)

    if intraday_close:
        swap = pd.Series(0.0, index=position.index)
        n_nights = 0
        n_weekend = 0
    else:
        swap, n_nights, n_weekend = _swap_cost_series(
            position, swap_long_bps, swap_short_bps, weekend_mult
        )

    fx = pd.Series(0.0, index=position.index)
    darf = pd.Series(0.0, index=position.index)
    net_pnl = gross_pnl - spread - swap - fx - darf
    turnover = float(position.diff().abs().fillna(position.iloc[0]).sum())

    return CostBreakdown(
        gross_pnl=gross_pnl,
        spread_cost=spread,
        swap_cost=swap,
        fx_cost=fx,
        darf_cost=darf,
        net_pnl=net_pnl,
        total_turnover=turnover,
        n_swap_nights=n_nights,
        n_weekend_holds=n_weekend,
        track="pepperstone_cfd",
    )


def apply_inter_costs_with_darf(
    gross_returns: pd.Series,
    position: pd.Series,
    *,
    fx_rt_bps: float = INTER_FX_RT_BPS,
    darf_rate: float = INTER_DARF_RATE,
) -> CostBreakdown:
    """Apply Inter ETF cost model (long-only, daily, with DARF tax).

    Long-only is enforced — the function raises if any bar has a
    negative position. T+1 settlement is enforced by the caller (no
    intraday round-trips).

    DARF is computed monthly: gross monthly net = sum of (gross − spread −
    fx) per month; tax = 15% of max(0, monthly_net). Tax is allocated
    back to the LAST bar of that month so the daily PnL series remains
    well-defined (a more elaborate per-trade tax allocation is unnecessary
    for backtest scoring; only the totals matter).

    Caller is responsible for using daily bars only and confirming the
    underlying is GLD/IAU (not XAUUSD spot — Inter routes via US ETFs).
    """
    if not gross_returns.index.equals(position.index):
        raise ValueError("gross_returns and position must share index")
    if (position < 0).any():
        raise ValueError("Inter track is LONG-ONLY; position must be ≥ 0")

    gross_pnl = _bar_pnl(position, gross_returns)

    # FX cost: 100 bps RT split into 50 bps per side, charged on
    # |position.diff()|. Captures the effective spread on USD↔BRL.
    fx_per_side = _bps(fx_rt_bps) / 2.0
    delta = position.diff().abs().fillna(position.iloc[0])
    fx = delta * fx_per_side

    spread = pd.Series(0.0, index=position.index)  # zero brokerage at Inter
    swap = pd.Series(0.0, index=position.index)  # ETF, no swap

    # Per-bar pre-tax net.
    pre_tax = gross_pnl - spread - swap - fx

    # Monthly DARF: 15% of positive monthly sum, allocated to last bar of
    # each month. Negative months → zero tax (carry-forward not modelled).
    if isinstance(position.index, pd.DatetimeIndex):
        monthly = pre_tax.groupby(pd.Grouper(freq="MS")).sum()
        darf_per_month = darf_rate * monthly.clip(lower=0.0)
        # allocate to last bar of each month
        last_bar_of_month = (
            pre_tax.index.to_series().groupby(pd.Grouper(freq="MS")).max()
        )
        darf = pd.Series(0.0, index=position.index)
        for month_start, last_dt in last_bar_of_month.items():
            if pd.notna(last_dt):
                tax_amt = float(darf_per_month.get(month_start, 0.0))
                if tax_amt > 0:
                    darf.loc[last_dt] += tax_amt
    else:
        darf = pd.Series(0.0, index=position.index)

    net_pnl = pre_tax - darf
    turnover = float(delta.sum())

    return CostBreakdown(
        gross_pnl=gross_pnl,
        spread_cost=spread,
        swap_cost=swap,
        fx_cost=fx,
        darf_cost=darf,
        net_pnl=net_pnl,
        total_turnover=turnover,
        n_swap_nights=0,
        n_weekend_holds=0,
        track="inter_etf",
    )


__all__ = [
    "PEPPERSTONE_SPREAD_RT_BPS",
    "PEPPERSTONE_SWAP_LONG_BPS",
    "PEPPERSTONE_SWAP_SHORT_BPS",
    "PEPPERSTONE_WEEKEND_MULT",
    "INTER_FX_RT_BPS",
    "INTER_DARF_RATE",
    "CostBreakdown",
    "apply_pepperstone_costs",
    "apply_inter_costs_with_darf",
]
