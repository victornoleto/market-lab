"""Phase 3.7 — H1.c: Maróy 2024 Ladder exit on Zarattini 2024 noise boundary.

Intraday SPY (and cross-asset QQQ) breakout strategy combining:

* **Entry** — Zarattini-Aziz-Barbon 2024 noise boundary [paper.zarattini_2024_intraday_spy]
  ``upper_t = open_of_day_t × (1 + MA(|intraday_return|, 14d))``
  ``lower_t = open_of_day_t × (1 − MA(|intraday_return|, 14d))``
  Long if ``close_t > upper_t``, short if ``close_t < lower_t``.

* **Exit — Maróy 2024 Ladder (SSRN 5095349)** [paper.maroy_2024_intraday_improvements]
  3-level TP scale-out at ``0.5 × ATR20_entry``, ``1.0 × ATR20_entry``,
  ``2.0 × ATR20_entry`` + trailing runner after TP2.
  * At entry: full position 1.0.
  * At TP1 (+0.5×ATR): close 1/3 → position 2/3.
  * At TP2 (+1.0×ATR): close 1/3 → position 1/3; activate trailing stop.
  * At TP3 (+2.0×ATR): close 1/3 → position 0 (fully flat).
  * After TP2, runner is trailed at ``high_since_entry − 1 × ATR20_running``.
  * Flat at close (mandate §3 intraday zero-swap).

Short is the symmetric mirror.

All cost accounting is done on the **weight_change path**: each TP hit
generates a 1/3-notional partial exit that pays spread. Maróy Ladder has
up to 4 flips per trade (entry + TP1 + TP2 + TP3 or trailing), vs
1-2 for single-trail variants — cost drag is materially higher and MUST
be honestly captured in the cost model.

Citations
---------
* Noise-boundary signal: ``[paper.zarattini_2024_intraday_spy, §3]``.
* Ladder exit: ``[paper.maroy_2024_intraday_improvements, §Ladder]``.
* F2-alignment (prev_weight × ret, shift(1).fillna(0)):
  ``[advances_fin_ml, p.31-34]``; reference implementation
  ``src/ai_trade/backtest/strategies/phase3_6_k_universal_trend.py:556-568``.
* Pepperstone SPX500 CFD cost model (0.4 pts ≈ 0.67 bps per side, zero
  commission, zero swap intraday): ``docs/investment-mandate.md §2.4``.
* PBO/DSR framework: ``[advances_fin_ml, p.208-211, p.275]``.

Known limitation
----------------
Cross-library validation: the Ladder's variable-fraction, path-dependent
exit is not naturally expressible as a single vectorbt portfolio because
vbt.from_signals takes a single exit signal per bar per asset. A faithful
vbt replication would require manual per-trade iteration that mirrors
this pandas reference. The runner script (`run_h1_maroy_ladder.py`)
attempts a **simplified single-TP 1×ATR** vbt comparison purely as a
±3pp Δ-CAGR cross-lib check on the noise-boundary signal itself.
If the simplified version's Δ vs a pandas-single-TP control exceeds 3pp,
gate 9 FAILS (documented as `KNOWN LIMITATION`).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

__all__ = [
    "MaroyLadderConfig",
    "MaroyLadderResult",
    "compute_atr_wilder_intraday",
    "simulate_h1_maroy_ladder",
]

# Regular US equity session has 390 1-minute bars per day.
BARS_PER_SESSION = 390
TRADING_DAYS_PER_YEAR = 252
BARS_PER_YEAR = BARS_PER_SESSION * TRADING_DAYS_PER_YEAR


@dataclass(frozen=True)
class MaroyLadderConfig:
    """Immutable config for one Maróy-Ladder backtest cell.

    Parameters
    ----------
    noise_lookback_days : int
        Number of prior days used in the rolling-mean ``|intraday_return|``.
        Zarattini 2024 uses 14d. [paper.zarattini_2024_intraday_spy]
    atr_period : int
        ATR period for exit-distance calibration. Maróy 2024 uses 20-bar.
        [paper.maroy_2024_intraday_improvements]
    tp1_mult, tp2_mult, tp3_mult : float
        Multipliers on ``ATR_entry`` for the three take-profit rungs.
        Defaults 0.5 / 1.0 / 2.0 per Maróy 2024 best config.
    trailing_atr_mult : float
        Multiplier on running ATR for the trailing stop activated after TP2.
        Default 1.0.
    allow_short : bool
        Symmetric short side? Default True.
    flat_at_close : bool
        Force flat at session end (mandate §3 intraday).
    spread_one_way : float
        One-way spread fraction (bps/10_000). 0.4 SPX500 pts on a $500
        SPY ≈ 0.67 bps; we set 0.000067 per side (6.7e-5 as a fraction).
        Applied PER weight-change on the post-cost path — capturing the
        extra partial-exit cost that is the Ladder's defining drag.
    commission_round_trip : float
        0.0 for Pepperstone Razor SPX500 CFD (spread-only).
    swap_daily : float
        0.0 — positions flat at close; no overnight swap.
    tax_rate : float
        0.0 — CFD on Pepperstone per mandate §4.8 no-DARF decision.
    """

    noise_lookback_days: int = 14
    atr_period: int = 20
    tp1_mult: float = 0.5
    tp2_mult: float = 1.0
    tp3_mult: float = 2.0
    trailing_atr_mult: float = 1.0
    allow_short: bool = True
    flat_at_close: bool = True
    spread_one_way: float = 6.7e-5
    commission_round_trip: float = 0.0
    swap_daily: float = 0.0
    tax_rate: float = 0.0

    def __post_init__(self) -> None:
        if self.noise_lookback_days < 2:
            raise ValueError("noise_lookback_days must be >= 2")
        if self.atr_period < 2:
            raise ValueError("atr_period must be >= 2")
        for name, v in (
            ("tp1_mult", self.tp1_mult),
            ("tp2_mult", self.tp2_mult),
            ("tp3_mult", self.tp3_mult),
        ):
            if v <= 0:
                raise ValueError(f"{name} must be > 0")
        if not (self.tp1_mult < self.tp2_mult < self.tp3_mult):
            raise ValueError("TP multipliers must be strictly ascending")
        if self.trailing_atr_mult <= 0:
            raise ValueError("trailing_atr_mult must be > 0")
        if self.spread_one_way < 0:
            raise ValueError("spread_one_way must be >= 0")


@dataclass
class MaroyLadderResult:
    """Output of a Maróy Ladder simulation."""

    bar_returns: pd.Series  # per-bar net returns aligned with close index
    gross_returns: pd.Series
    weights: pd.Series  # bar-level weight in {-1,-2/3,-1/3,0,+1/3,+2/3,+1}
    entries: pd.Series  # True on bar where weight jumps 0 → ±1
    exits: pd.Series  # True on bar where weight returns to 0 from nonzero
    trade_pnl: list[float]  # per full-trade net return (entry → fully flat)
    hold_lengths_bars: list[int]  # bars held per trade
    tp1_hits: int = 0
    tp2_hits: int = 0
    tp3_hits: int = 0
    trailing_exits: int = 0
    eod_exits: int = 0
    cum_spread_pct: float = 0.0
    n_entries: int = 0

    @property
    def n_trades(self) -> int:
        return self.n_entries

    def sharpe(self, periods_per_year: int = BARS_PER_YEAR) -> float:
        r = self.bar_returns.dropna()
        if r.empty:
            return 0.0
        sd = float(r.std(ddof=1))
        return float(r.mean() / sd * np.sqrt(periods_per_year)) if sd > 0 else 0.0

    def cagr(self, periods_per_year: int = BARS_PER_YEAR) -> float:
        r = self.bar_returns.dropna()
        if len(r) < 2:
            return 0.0
        n = len(r)
        eq = float((1.0 + r).prod())
        if eq <= 0:
            return -1.0
        return eq ** (periods_per_year / n) - 1.0

    def max_drawdown(self) -> float:
        r = self.bar_returns.dropna()
        if r.empty:
            return 0.0
        eq = (1.0 + r).cumprod()
        peak = eq.cummax()
        return float((eq / peak - 1.0).min())

    def median_hold_minutes(self) -> float:
        if not self.hold_lengths_bars:
            return float("nan")
        return float(np.median(self.hold_lengths_bars))

    def daily_returns(self) -> pd.Series:
        """Aggregate bar-level net returns into daily returns via compounding."""
        r = self.bar_returns.dropna()
        if r.empty:
            return pd.Series(dtype=float)
        idx = r.index
        day = pd.Index(pd.to_datetime(idx).date, name="date")
        daily = (1.0 + r).groupby(day).prod() - 1.0
        daily.index = pd.to_datetime(daily.index)
        return daily


def compute_atr_wilder_intraday(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20
) -> pd.Series:
    """Wilder ATR on 1-min intraday bars (no session boundary handling).

    Note: Wilder smoothing runs across session gaps by design — the spec
    uses the standard TR with ``prev_close`` from the previous bar
    (could be yesterday's close for the first bar of a day). This matches
    Maróy 2024's described ATR20 on a continuous minute stream.
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()
    return atr


def _compute_noise_boundary(
    df: pd.DataFrame, lookback_days: int = 14
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Return (day_open, upper, lower) for every bar.

    ``boundary = MA(|intraday_ret|, lookback_days)`` where the mean is
    taken over the **prior** ``lookback_days`` daily mean-absolute
    intraday returns (not peeking at today's bars).

    intraday_ret per bar k = close_k / open_of_day − 1.
    day-level |intraday_ret| summary = mean |close_k/open − 1| over all bars of the day.
    """
    idx = df.index
    day_id = pd.Index(pd.to_datetime(idx).normalize(), name="day")

    # Per-bar |intraday return| relative to day open — bar-level.
    day_open = df.groupby(day_id)["open"].transform("first")
    intraday_abs = (df["close"] / day_open - 1.0).abs()
    # Daily mean absolute intraday return.
    daily_mean_abs = intraday_abs.groupby(day_id).mean()
    # Rolling mean over prior N days (shift 1 so today uses up to yesterday only).
    rolling = daily_mean_abs.shift(1).rolling(lookback_days, min_periods=lookback_days).mean()
    # Broadcast back to per-bar index.
    rolling_series = pd.Series(rolling, index=daily_mean_abs.index)
    boundary_per_bar = day_id.to_series().map(rolling_series).to_numpy()

    upper = day_open * (1.0 + boundary_per_bar)
    lower = day_open * (1.0 - boundary_per_bar)
    return day_open, upper, lower


def simulate_h1_maroy_ladder(
    data: pd.DataFrame, config: MaroyLadderConfig
) -> MaroyLadderResult:
    """Run Maróy-Ladder intraday backtest on a single-asset 1-min OHLC panel.

    Parameters
    ----------
    data : pd.DataFrame
        Columns ``open, high, low, close`` indexed by tz-aware minute
        timestamps (UTC). One asset only — multi-asset aggregation is
        done in the runner by calling this per asset and combining
        returns.
    config : MaroyLadderConfig
    """
    if data.empty:
        raise ValueError("input data is empty")
    req = {"open", "high", "low", "close"}
    if not req.issubset(data.columns):
        raise ValueError(f"data must contain columns {req}")

    df = data.sort_index()
    idx = df.index
    n = len(df)

    # --- Compute signals (noise boundary) ---
    day_open, upper, lower = _compute_noise_boundary(df, config.noise_lookback_days)

    # --- Compute ATR20 intraday ---
    atr = compute_atr_wilder_intraday(
        df["high"], df["low"], df["close"], period=config.atr_period
    ).to_numpy()

    close_arr = df["close"].to_numpy()
    high_arr = df["high"].to_numpy()
    low_arr = df["low"].to_numpy()
    upper_arr = upper.to_numpy()
    lower_arr = lower.to_numpy()

    # Session boundaries: last-bar-of-day mask for forced EOD flat.
    day_id_arr = pd.to_datetime(idx).normalize().to_numpy()
    # last-bar-of-day mask: True where next row starts a new day (or is last).
    next_day = np.empty(n, dtype=object)
    next_day[:-1] = day_id_arr[1:]
    next_day[-1] = None
    eod_mask = (day_id_arr != next_day)

    # --- State machine ---
    weight = np.zeros(n, dtype=float)
    entry = np.zeros(n, dtype=bool)
    exit_ = np.zeros(n, dtype=bool)

    in_pos = False
    side = 0  # +1 long, -1 short, 0 flat
    entry_price = np.nan
    atr_entry = np.nan
    tp1_hit = tp2_hit = tp3_hit = False
    trailing_active = False
    peak_since_entry = -np.inf  # for long: running high; for short: running low (stored as -price so we can always "max")
    running_extreme = np.nan
    current_pos = 0.0  # in {0, 1/3, 2/3, 1}, signed by `side`
    bars_in_trade = 0

    tp1_hits = tp2_hits = tp3_hits = trailing_exits = eod_exits = 0
    n_entries = 0
    hold_lengths: list[int] = []
    trade_pnl: list[float] = []
    trade_entry_price = np.nan
    trade_weighted_pnl = 0.0  # sum of fractional exits' realised return contributions

    THIRD = 1.0 / 3.0

    for t in range(n):
        c = close_arr[t]
        h = high_arr[t]
        low = low_arr[t]
        u = upper_arr[t]
        lo = lower_arr[t]
        a = atr[t]

        if in_pos:
            bars_in_trade += 1
            # Update running extreme (uses current bar's high/low — intra-bar
            # triggers are evaluated first so no peek).
            # --- Partial-exit ladder (evaluated using high/low of this bar) ---
            # We assume a long TP hits if bar high >= TP level; short TP hits
            # if bar low <= TP level. Intra-bar ordering: TP1 before TP2 before
            # TP3 when all three trigger in one bar (conservative favorable
            # order). Trailing stop checked AFTER TPs.
            if side > 0:
                # long
                tp1_level = entry_price + config.tp1_mult * atr_entry
                tp2_level = entry_price + config.tp2_mult * atr_entry
                tp3_level = entry_price + config.tp3_mult * atr_entry
                # TP1
                if (not tp1_hit) and h >= tp1_level:
                    tp1_hit = True
                    tp1_hits += 1
                    # realised +0.5 ATR return fraction on 1/3 of position
                    r = (tp1_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos -= THIRD
                # TP2
                if (not tp2_hit) and h >= tp2_level:
                    tp2_hit = True
                    tp2_hits += 1
                    r = (tp2_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos -= THIRD
                    trailing_active = True
                    running_extreme = max(running_extreme, h)
                # TP3
                if (not tp3_hit) and h >= tp3_level:
                    tp3_hit = True
                    tp3_hits += 1
                    r = (tp3_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos -= THIRD
                    # Full exit — close trade.
                    exit_[t] = True
                    hold_lengths.append(bars_in_trade)
                    trade_pnl.append(trade_weighted_pnl)
                    in_pos = False
                    side = 0
                    current_pos = 0.0
                    tp1_hit = tp2_hit = tp3_hit = False
                    trailing_active = False
                    weight[t] = 0.0
                    continue
                # Trailing stop (after TP2 activated, runner only)
                if trailing_active and not tp3_hit:
                    running_extreme = max(running_extreme, h)
                    stop_level = running_extreme - config.trailing_atr_mult * a
                    if np.isfinite(stop_level) and low <= stop_level:
                        # Close remaining runner at stop level.
                        r = (stop_level - entry_price) / entry_price
                        trade_weighted_pnl += r * current_pos * side  # current_pos is 1/3
                        current_pos = 0.0
                        trailing_exits += 1
                        exit_[t] = True
                        hold_lengths.append(bars_in_trade)
                        trade_pnl.append(trade_weighted_pnl)
                        in_pos = False
                        side = 0
                        tp1_hit = tp2_hit = tp3_hit = False
                        trailing_active = False
                        weight[t] = 0.0
                        continue
            else:  # short
                tp1_level = entry_price - config.tp1_mult * atr_entry
                tp2_level = entry_price - config.tp2_mult * atr_entry
                tp3_level = entry_price - config.tp3_mult * atr_entry
                if (not tp1_hit) and low <= tp1_level:
                    tp1_hit = True
                    tp1_hits += 1
                    r = (tp1_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos += THIRD  # current_pos is negative, becomes less negative
                if (not tp2_hit) and low <= tp2_level:
                    tp2_hit = True
                    tp2_hits += 1
                    r = (tp2_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos += THIRD
                    trailing_active = True
                    running_extreme = min(running_extreme, low)
                if (not tp3_hit) and low <= tp3_level:
                    tp3_hit = True
                    tp3_hits += 1
                    r = (tp3_level - entry_price) / entry_price
                    trade_weighted_pnl += r * THIRD * side
                    current_pos += THIRD
                    exit_[t] = True
                    hold_lengths.append(bars_in_trade)
                    trade_pnl.append(trade_weighted_pnl)
                    in_pos = False
                    side = 0
                    current_pos = 0.0
                    tp1_hit = tp2_hit = tp3_hit = False
                    trailing_active = False
                    weight[t] = 0.0
                    continue
                if trailing_active and not tp3_hit:
                    running_extreme = min(running_extreme, low)
                    stop_level = running_extreme + config.trailing_atr_mult * a
                    if np.isfinite(stop_level) and h >= stop_level:
                        r = (stop_level - entry_price) / entry_price
                        trade_weighted_pnl += r * abs(current_pos) * side
                        current_pos = 0.0
                        trailing_exits += 1
                        exit_[t] = True
                        hold_lengths.append(bars_in_trade)
                        trade_pnl.append(trade_weighted_pnl)
                        in_pos = False
                        side = 0
                        tp1_hit = tp2_hit = tp3_hit = False
                        trailing_active = False
                        weight[t] = 0.0
                        continue

            # EOD forced flat — close at current close.
            if config.flat_at_close and eod_mask[t] and in_pos:
                # Close remaining position at close price.
                r = (c - entry_price) / entry_price
                trade_weighted_pnl += r * abs(current_pos) * side
                current_pos = 0.0
                eod_exits += 1
                exit_[t] = True
                hold_lengths.append(bars_in_trade)
                trade_pnl.append(trade_weighted_pnl)
                in_pos = False
                side = 0
                tp1_hit = tp2_hit = tp3_hit = False
                trailing_active = False
                weight[t] = 0.0
                continue

            # Still in position — record current signed fractional weight.
            weight[t] = current_pos if side > 0 else current_pos  # already signed
            continue

        # --- Flat — evaluate entry ---
        if eod_mask[t]:
            # No new entries on session's final bar (would be forced flat immediately).
            weight[t] = 0.0
            continue
        if not np.isfinite(u) or not np.isfinite(lo) or not np.isfinite(a) or a <= 0:
            weight[t] = 0.0
            continue
        if c > u:  # long entry
            in_pos = True
            side = 1
            entry_price = c
            atr_entry = a
            current_pos = 1.0
            weight[t] = 1.0
            entry[t] = True
            n_entries += 1
            bars_in_trade = 1
            tp1_hit = tp2_hit = tp3_hit = False
            trailing_active = False
            running_extreme = c
            trade_weighted_pnl = 0.0
            trade_entry_price = c
        elif config.allow_short and c < lo:
            in_pos = True
            side = -1
            entry_price = c
            atr_entry = a
            current_pos = -1.0
            weight[t] = -1.0
            entry[t] = True
            n_entries += 1
            bars_in_trade = 1
            tp1_hit = tp2_hit = tp3_hit = False
            trailing_active = False
            running_extreme = c
            trade_weighted_pnl = 0.0
            trade_entry_price = c
        else:
            weight[t] = 0.0

    # --- F2-patched PnL path: prev_weight × ret ---
    weight_series = pd.Series(weight, index=idx, name="weight")
    prev_weight = weight_series.shift(1).fillna(0.0)
    ret_series = df["close"].pct_change().fillna(0.0)
    gross_bar = prev_weight * ret_series

    # Spread cost — pay on EACH weight change (captures TP-ladder's extra flips).
    weight_change = (weight_series - weight_series.shift(1).fillna(0.0)).abs()
    spread_drag = weight_change * config.spread_one_way
    commission_drag = weight_change * config.commission_round_trip
    # swap_daily = 0 intraday, but keep term for completeness
    swap_drag = pd.Series(0.0, index=idx)

    net_bar = gross_bar - spread_drag - commission_drag - swap_drag

    entries_series = pd.Series(entry, index=idx, name="entries")
    exits_series = pd.Series(exit_, index=idx, name="exits")

    # If still in pos at end of panel, close it conceptually for hold stats.
    if in_pos:
        hold_lengths.append(bars_in_trade)

    return MaroyLadderResult(
        bar_returns=net_bar,
        gross_returns=gross_bar,
        weights=weight_series,
        entries=entries_series,
        exits=exits_series,
        trade_pnl=trade_pnl,
        hold_lengths_bars=hold_lengths,
        tp1_hits=tp1_hits,
        tp2_hits=tp2_hits,
        tp3_hits=tp3_hits,
        trailing_exits=trailing_exits,
        eod_exits=eod_exits,
        cum_spread_pct=float(spread_drag.sum()),
        n_entries=n_entries,
    )
