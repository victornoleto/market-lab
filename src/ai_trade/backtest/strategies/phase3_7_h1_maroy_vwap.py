"""Phase 3.7 H1.b — Maróy 2024 VWAP-exit intraday noise-boundary.

Intraday momentum entry per Zarattini-Aziz-Barbon 2024 (SSRN 4824172)
with the **Maróy 2024 (SSRN 5095349) VWAP-cross exit variant** replacing
the original ATR-distance trailing stop.

Signal (entry, literal from Zarattini 2024)
-------------------------------------------

For each trading day ``d`` with session open at bar ``t_0``::

    upper_d = open_d × (1 + MA_14(|intraday_return_k|))
    lower_d = open_d × (1 − MA_14(|intraday_return_k|))

where ``MA_14(|intraday_return_k|)`` is the 14-trading-day rolling mean
of the absolute close-to-close intraday return (|return_{bar}|).
Zarattini 2024 uses the rolling mean of the *absolute intraday return
over the whole session*; we follow the literal formulation by averaging
|ret_t| over the 14 prior sessions (all intraday bars) to get a single
MA applied to both upper and lower boundaries.
``[zarattini_aziz_barbon_2024]``

**Entry** on bar ``t`` (after the opening minute, so ``t > t_0``):
  * long if ``close_t > upper_d`` and flat;
  * short if ``close_t < lower_d`` and flat;
  * otherwise hold prior position.

Exit rule (Maróy 2024 VWAP-cross variant)
-----------------------------------------

Anchored VWAP from day-open::

    VWAP_t = Σ_{k=t_0..t} (close_k × volume_k) / Σ_{k=t_0..t} volume_k

The Tiingo IEX 1-min parquets (``data/phase3_7/intraday/*.parquet``)
carry open/high/low/close only — no volume. We substitute a **typical-
VWAP (TVWAP) close-only approximation**::

    TVWAP_t = mean(close_{t_0..t})

This is a known approximation of the price-weighted by-minute TWAP; it
under-weights minutes with outsized volume (e.g. open/close bursts) but
tracks the same directional signal Maróy uses. Documented explicitly as
a data limitation in AGGREGATE.md §Limitations.
``[maroy_2024]``

**Exit** (long):
  * ``close_{t-1} ≥ TVWAP_{t-1}`` AND ``close_t < TVWAP_t``.
  * symmetric for short: ``close_{t-1} ≤ TVWAP_{t-1}`` AND ``close_t > TVWAP_t``.

**Flat at close (mandate §3 intraday, no swap)** — any position open at
the last session bar is force-closed on that bar's close. No overnight
carry, no swap accrual.

Cost model (Pepperstone Razor SPX500 CFD intraday)
--------------------------------------------------

Per `docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md`:

* **Spread one-way**: 0.4 pts on SPX500 ≈ **0.0067% ≈ 0.67 bps per side**
  (6.7e-5). Applied on every position flip (entry and exit).
* **Commission**: 0 on index CFDs (Razor applies to FX/metals only).
* **Swap**: 0 — positions are closed intraday by construction.

Cost-×2 (gate 13): 0.8 pts spread (1.34e-4 per side).

Sizing (base case, unleveraged)
-------------------------------

Fixed notional of 1.0 (full equity) when in position. Leverage sweep is
a meta-layer (H4 in the hunt prompt) and NOT part of H1.b.

Alignment (AFML p.31-34)
------------------------

All intraday returns are computed with the **F2-patched prev_weight ×
ret alignment**: ``prev_weight = weight_bar.shift(1).fillna(0.0)``. This
guarantees zero lookahead (today's weight cannot earn today's return).
For aggregation to daily returns (for validation framework
compatibility), we compound within-day net returns per trading session,
yielding one daily pct-return per trading day.

Citations
---------
* `[zarattini_aziz_barbon_2024]` — noise-boundary entry formula.
* `[maroy_2024]` — VWAP-cross exit variant.
* `[advances_fin_ml, p.31-34]` — prev_weight × ret alignment.
* `[docs/investment-mandate.md §2.4]` — 13-gate framework.
* `[docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md]` — cost
  model source (SPX500 CFD 0.4-pt spread, 0 commission, 0 swap intraday).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "MaroyVwapConfig",
    "MaroyVwapResult",
    "simulate_h1_maroy_vwap",
]

TRADING_DAYS_PER_YEAR = 252
REGULAR_SESSION_BARS = 390  # 9:30-16:00 ET, 1-min bars


@dataclass(frozen=True)
class MaroyVwapConfig:
    """Immutable configuration for H1.b backtest cell.

    Parameters
    ----------
    ma_lookback_days : int
        Trading-day lookback for the MA of |intraday_return|. Zarattini
        2024 uses 14. ``[zarattini_aziz_barbon_2024]``
    noise_band_scale : float
        Multiplier on the MA-of-|ret| for boundary width. 1.0 = literal
        Zarattini; retained as config knob so we do not peek OOS.
    allow_short : bool
        Enable short entries. Default True (symmetric signal). Mandate
        §3.1 permits shorts on CFD for Strategy A.
    flat_at_close : bool
        Force-close all positions at the last session bar. Default True
        per mandate §3 intraday, no swap.
    spread_one_way : float
        Per-side spread fraction on SPX500 CFD. 6.7e-5 = 0.67 bps (0.4
        points on SPX 6000). Applied per flip. Source:
        ``docs/strategies/plano_a_pepperstone_index_cfd_rate_card.md``.
    commission_per_flip : float
        Commission per flip. 0 for Pepperstone index CFD.
    min_bar_idx_for_entry : int
        Minimum bar index (within day) for new entries. Entries only
        after this bar so the ``open_d`` reference and boundary
        estimate aren't immediately triggered on the very first tick
        (Zarattini 2024 uses post-opening tick); default 1.
    """

    ma_lookback_days: int = 14
    noise_band_scale: float = 1.0
    allow_short: bool = True
    flat_at_close: bool = True
    spread_one_way: float = 6.7e-5
    commission_per_flip: float = 0.0
    min_bar_idx_for_entry: int = 1

    def __post_init__(self) -> None:
        if self.ma_lookback_days < 2:
            raise ValueError(
                f"ma_lookback_days must be ≥ 2, got {self.ma_lookback_days}"
            )
        if self.noise_band_scale <= 0:
            raise ValueError(
                f"noise_band_scale must be > 0, got {self.noise_band_scale}"
            )
        if self.spread_one_way < 0:
            raise ValueError(
                f"spread_one_way must be ≥ 0, got {self.spread_one_way}"
            )


@dataclass
class MaroyVwapResult:
    """Output of one H1.b simulation."""

    daily_returns: pd.Series  # pct-return per calendar trading day
    per_bar_returns: pd.Series  # net per-bar returns (intraday granularity)
    positions: pd.Series  # signed weight per bar (-1/0/+1)
    hold_lengths_bars: list[int] = field(default_factory=list)
    n_trades: int = 0
    cum_spread_pct: float = 0.0
    cum_commission_pct: float = 0.0

    def sharpe(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return (
            float(r.mean() / sd * np.sqrt(periods_per_year))
            if sd > 0
            else 0.0
        )

    def cagr(self, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
        r = self.daily_returns.dropna()
        if len(r) < 2:
            return 0.0
        n = len(r)
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        return eq ** (periods_per_year / n) - 1.0

    def max_drawdown(self) -> float:
        r = self.daily_returns.dropna()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_bars(self) -> float:
        if not self.hold_lengths_bars:
            return float("nan")
        return float(np.median(self.hold_lengths_bars))

    def median_hold_minutes(self) -> float:
        return self.median_hold_bars()  # 1-min bars


def simulate_h1_maroy_vwap(
    df: pd.DataFrame,
    config: MaroyVwapConfig,
) -> MaroyVwapResult:
    """Run one H1.b Maróy-VWAP intraday simulation on a single asset.

    Parameters
    ----------
    df : pd.DataFrame
        1-min OHLC bars with tz-aware DatetimeIndex. Columns must
        include ``open, high, low, close``. Index should be in UTC or
        a market-local tz; we convert to ``America/New_York`` internally
        for session grouping.
    config : MaroyVwapConfig
        Strategy cell.

    Returns
    -------
    MaroyVwapResult
    """
    required = {"open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("index must be a DatetimeIndex")
    if df.index.tz is None:
        raise ValueError("index must be tz-aware")

    # --- Prep: sort + session grouping in ET ---
    d = df[["open", "high", "low", "close"]].astype(float).sort_index().copy()
    d.index.name = "ts_utc"
    idx_et = d.index.tz_convert("America/New_York")
    d["date_et"] = pd.Index(idx_et.date)

    # --- Compute per-day series: open, per-bar intraday_return, close ---
    # Group by session day. First bar = session open, last bar = close.
    groups = d.groupby("date_et", sort=True)

    # Per-day open price (first close is NOT the open — use 'open' of first bar).
    # Zarattini 2024 uses the actual day open price as reference.
    day_open = groups["open"].first()

    # Per-day |intraday_return| average over whole session. intraday_return
    # for bar t = close_t / close_{t-1} - 1 (within same day, so no overnight).
    # We'll compute per-bar intraday returns and average their absolute value
    # per day.
    # close-to-close per-bar ret; first bar of day = open-to-close of that bar
    # (since there's no close_{t-1} in the same session). Zarattini mean of
    # absolute intraday returns across all bars of a session.
    d["close_prev"] = d.groupby("date_et")["close"].shift(1)
    # For first bar of day (NaN close_prev), use close/open - 1 so the bar
    # contributes its own move.
    first_bar_mask = d["close_prev"].isna()
    d.loc[first_bar_mask, "close_prev"] = d.loc[first_bar_mask, "open"]
    d["bar_ret"] = d["close"] / d["close_prev"] - 1.0
    d["abs_bar_ret"] = d["bar_ret"].abs()

    day_mean_abs = groups["abs_bar_ret"].mean()

    # Rolling-14 trailing MA of day_mean_abs — shift(1) so today's boundary
    # uses only data through yesterday (no lookahead).
    ma_14 = (
        day_mean_abs.rolling(config.ma_lookback_days, min_periods=config.ma_lookback_days)
        .mean()
        .shift(1)
    )

    # --- Build per-bar boundary + TVWAP in one pass ---
    # Attach per-day open + ma to every bar.
    d["day_open"] = d["date_et"].map(day_open)
    d["ma_14"] = d["date_et"].map(ma_14)
    d["boundary_width"] = d["day_open"] * d["ma_14"] * config.noise_band_scale
    d["upper"] = d["day_open"] + d["boundary_width"]
    d["lower"] = d["day_open"] - d["boundary_width"]

    # Anchored TVWAP (close-only mean since day-open).
    # cumulative mean within day.
    d["bar_idx"] = groups.cumcount()
    d["cum_close"] = groups["close"].cumsum()
    d["tvwap"] = d["cum_close"] / (d["bar_idx"] + 1)

    # Prior-bar tvwap and close for the cross detection.
    d["tvwap_prev"] = d.groupby("date_et")["tvwap"].shift(1)
    d["close_prev_sameday"] = d.groupby("date_et")["close"].shift(1)

    # --- State machine per bar (numpy fast) ---
    n = len(d)
    close_v = d["close"].to_numpy()
    upper_v = d["upper"].to_numpy()
    lower_v = d["lower"].to_numpy()
    ma_v = d["ma_14"].to_numpy()
    bar_idx_v = d["bar_idx"].to_numpy()
    tvwap_v = d["tvwap"].to_numpy()
    tvwap_prev_v = d["tvwap_prev"].to_numpy()
    close_prev_sd_v = d["close_prev_sameday"].to_numpy()
    bar_ret_v = d["bar_ret"].to_numpy()

    # Last-bar-of-day mask: True if next bar has a different date.
    date_v = d["date_et"].to_numpy()
    last_bar_mask = np.concatenate([
        date_v[1:] != date_v[:-1], [True]
    ])

    pos = np.zeros(n, dtype=np.int8)  # -1/0/+1 CURRENT bar
    entry_flag = np.zeros(n, dtype=bool)
    exit_flag = np.zeros(n, dtype=bool)

    cur_pos = 0
    seg_len = 0
    hold_lengths: list[int] = []
    n_trades = 0

    for i in range(n):
        if not np.isfinite(ma_v[i]):
            # Before warmup → flat.
            pos[i] = 0
            if cur_pos != 0:
                # flush any open (shouldn't happen, but safety).
                exit_flag[i] = True
                hold_lengths.append(seg_len)
                cur_pos = 0
                seg_len = 0
            continue

        # --- Exit check FIRST (if in pos) ---
        if cur_pos != 0:
            # Flat-at-close rule.
            if config.flat_at_close and last_bar_mask[i]:
                pos[i] = cur_pos
                exit_flag[i] = True
                seg_len += 1
                hold_lengths.append(seg_len)
                cur_pos = 0
                seg_len = 0
                continue
            # VWAP cross exit (needs prior bar values same-day).
            cp = close_prev_sd_v[i]
            cc = close_v[i]
            vp = tvwap_prev_v[i]
            vc = tvwap_v[i]
            if (
                np.isfinite(cp)
                and np.isfinite(vp)
                and np.isfinite(vc)
            ):
                if cur_pos == 1:
                    if (cp >= vp) and (cc < vc):
                        # Long VWAP-cross down: exit.
                        exit_flag[i] = True
                        seg_len += 1
                        hold_lengths.append(seg_len)
                        cur_pos = 0
                        seg_len = 0
                        pos[i] = 0
                        continue
                elif cur_pos == -1:
                    if (cp <= vp) and (cc > vc):
                        # Short VWAP-cross up: exit.
                        exit_flag[i] = True
                        seg_len += 1
                        hold_lengths.append(seg_len)
                        cur_pos = 0
                        seg_len = 0
                        pos[i] = 0
                        continue
            # Held — keep position.
            pos[i] = cur_pos
            seg_len += 1
            continue

        # --- Flat: entry check ---
        # Don't open a brand-new position on the very last bar (we'd
        # just be paying cost to close it).
        if config.flat_at_close and last_bar_mask[i]:
            pos[i] = 0
            continue
        if bar_idx_v[i] < config.min_bar_idx_for_entry:
            pos[i] = 0
            continue
        c = close_v[i]
        u = upper_v[i]
        l_ = lower_v[i]
        if not (np.isfinite(u) and np.isfinite(l_) and np.isfinite(c)):
            pos[i] = 0
            continue
        if c > u:
            # Long entry.
            cur_pos = 1
            seg_len = 1
            pos[i] = 1
            entry_flag[i] = True
            n_trades += 1
        elif c < l_ and config.allow_short:
            cur_pos = -1
            seg_len = 1
            pos[i] = -1
            entry_flag[i] = True
            n_trades += 1
        else:
            pos[i] = 0

    # --- Returns (prev_weight × ret alignment — AFML p.31-34) ---
    # Weight at bar t is `pos[t]`. prev_weight = pos.shift(1).
    # per_bar_gross_ret[t] = prev_weight[t] * bar_ret[t].
    prev_weight = np.concatenate([[0], pos[:-1]]).astype(float)
    # Zero out cross-day prev_weight: first bar of a new day has no
    # "previous-bar position within same day" → prev_weight forced to 0.
    # (In practice we already force-close at last bar, so prev_weight at
    # day-boundary is already 0. Defensive re-zero for safety.)
    same_day_mask = np.concatenate([[False], date_v[1:] == date_v[:-1]])
    prev_weight = np.where(same_day_mask, prev_weight, 0.0)

    bar_ret_safe = np.nan_to_num(bar_ret_v, nan=0.0)
    gross_bar = prev_weight * bar_ret_safe

    # Cost: spread per flip (entry OR exit flag). Commission similarly.
    flips = entry_flag.astype(float) + exit_flag.astype(float)
    cost_bar = flips * (config.spread_one_way + config.commission_per_flip)
    net_bar = gross_bar - cost_bar

    per_bar_series = pd.Series(
        net_bar, index=d.index, name="net_ret"
    )

    # Compound per-day: (1 + r_bar).prod() - 1 gives daily return.
    daily_factor = (1.0 + per_bar_series).groupby(d["date_et"].values).prod()
    daily_returns = daily_factor - 1.0
    daily_returns.index = pd.DatetimeIndex(
        pd.to_datetime(list(daily_returns.index))
    )
    daily_returns.name = "daily_ret"

    positions_series = pd.Series(pos.astype(float), index=d.index, name="position")

    return MaroyVwapResult(
        daily_returns=daily_returns,
        per_bar_returns=per_bar_series,
        positions=positions_series,
        hold_lengths_bars=hold_lengths,
        n_trades=int(n_trades),
        cum_spread_pct=float(flips.sum() * config.spread_one_way),
        cum_commission_pct=float(flips.sum() * config.commission_per_flip),
    )
