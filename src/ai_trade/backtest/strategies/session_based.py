"""Session-based intraday FX strategy (Phase 3.5a Lead T4).

Single strategy class that implements three distinct session-timed
variants via a ``mode`` flag — all of them short-hold (median hold
≤ 24h), designed to be tested on 1-hour FX majors under the
Pepperstone cost model (``docs/investment-mandate.md §3``):

* ``orb`` — **opening-range breakout**. Build a reference range over
  ``range_hours_utc`` (e.g., Asian session 00–07 UTC). During
  ``signal_hours_utc`` (e.g., London 07–21 UTC), enter on a close
  beyond the range. ATR stop + time-stop + optional forced exit.
* ``mr``  — **mean-reversion fade over a rolling bar window**. Build
  a rolling ``range_window_bars`` high/low (e.g., last 24 bars at the
  NY close). At the signal hour, if close is ``entry_band_pct`` past
  the range → fade.
* ``fade`` — **time-windowed range fade**. Same as ``orb`` for the
  range construction (day-block), but fades breaks instead of riding
  them. Typical: fade NY-session extremes during the Asian session.

Citations
---------

- Session / ORB mechanics (buy when close > N-bar high of prior
  window): ``[trading_systems_methods, p.353]`` — Donchian /
  Turtles breakout foundations; generalised here to a calendar-hour
  window instead of bar-count.
- Range-fade / false-breakout mechanics (sell when price extends
  beyond yesterday's range): ``[trading_systems_methods, p.326-329]``.
- FX intraday parsimony (≤ 5 params per strategy; avoid over-tuning
  on hour-of-day cuts): ``[quant_trading_chan, p.43-53, ch.2-3]``.
- ATR-based hard stop + time-stop (intraday risk control):
  ``[machine_trading, p.126, ch.4]``.
- ATR / volatility filter for entry-size discipline:
  ``[volatility_trading]``.
- Hold-time discipline (≤ 5d, aiming for ≤ 24h on this lead to
  avoid swap): ``[systematic_trading, p.185-188]``.

Pipeline (per bar)
------------------

1. Pre-compute per-bar ``range_high`` / ``range_low`` per the
   ``range_spec`` (time window or bar window), plus Wilder ATR for
   stop sizing.
2. If flat and current bar lies in the signal window and range
   values are finite → evaluate the mode-specific entry condition.
3. If in position → check ATR hard stop, mode-specific exit band,
   optional forced-exit hour, then the time-stop. Exit on the first
   hit.

One position at a time; fixed risk-pct sizing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio

Mode = Literal["orb", "mr", "fade"]
Direction = Literal["long", "short", "both"]
RangeType = Literal["hours", "bars"]


@dataclass
class SessionStrategy:
    """Session-timed intraday strategy (ORB / session-MR / session-fade).

    Range source
    ------------
    ``range_type == "hours"``:
        ``range_hours_utc = (hs, he)`` (``0 <= hs < he <= 24``). The
        reference range for timestamp ``ts`` is the ``(max(high),
        min(low))`` of the most recent completed day-block whose
        ``he``-hour boundary has passed at or before ``ts``.

    ``range_type == "bars"``:
        ``range_window_bars = N``. Rolling ``N``-bar (``max`` /
        ``min``) shifted by one bar so the current bar does not leak
        into its own range.

    Signal & exit windows
    ---------------------
    * ``signal_hours_utc = (ss, se)`` (``0 <= ss < se <= 24``) —
      entries are only considered when ``ss <= ts.hour < se``.
    * ``exit_hours_utc = (xs, xe)`` — optional forced exit hours. If
      in position and ``xs <= ts.hour < xe``, close immediately
      regardless of P&L.

    Entry logic
    -----------
    * ``orb``: ``close > range_high`` → long; ``close < range_low`` →
      short. No band (``entry_band_pct`` must be 0 for orb).
    * ``mr``: ``close > range_high + band × range_width`` → **short**
      (fade); ``close < range_low − band × range_width`` → **long**
      (fade). ``entry_band_pct`` is expressed as a fraction of the
      range width, not a fraction of the price — this keeps the band
      meaningful across FX (pip-level moves) and equities (%-level
      moves) without symbol-specific calibration.
    * ``fade``: same as ``mr`` but paired with ``range_type="hours"``;
      the range is the previous session block.

    Exits
    -----
    1. ATR hard stop: long exits if ``close ≤ entry_px − atr_stop_mult
       × atr_at_entry``; short symmetric above entry.
    2. Optional forced-exit hour window (``exit_hours_utc``) — closes
       outright on the first bar inside the window.
    3. Time-stop: close after ``max_hold`` bars since entry.

    No Donchian band exit; the session / time-stop IS the exit band —
    that's what distinguishes this from T2.
    """

    data: dict[str, pd.DataFrame]
    symbol: str
    mode: Mode
    range_type: RangeType
    range_hours_utc: tuple[int, int] | None = None
    range_window_bars: int | None = None
    signal_hours_utc: tuple[int, int] = (0, 24)
    exit_hours_utc: tuple[int, int] | None = None
    direction: Direction = "both"
    entry_band_pct: float = 0.0
    atr_stop_mult: float = 2.0
    atr_window: int = 14
    max_hold: int = 24
    risk_pct_of_equity: float = 0.95

    _indicators: pd.DataFrame = field(init=False, repr=False)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.session"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")
        if self.mode not in ("orb", "mr", "fade"):
            raise ValueError(f"mode must be orb/mr/fade, got {self.mode!r}")
        if self.direction not in ("long", "short", "both"):
            raise ValueError(f"direction invalid: {self.direction!r}")
        if self.range_type not in ("hours", "bars"):
            raise ValueError(f"range_type invalid: {self.range_type!r}")

        if self.range_type == "hours":
            if self.range_hours_utc is None:
                raise ValueError("range_type='hours' requires range_hours_utc")
            hs, he = self.range_hours_utc
            if not (0 <= hs < he <= 24):
                raise ValueError(f"range_hours_utc must satisfy 0<=hs<he<=24, got {self.range_hours_utc}")
        else:
            if not self.range_window_bars or self.range_window_bars < 2:
                raise ValueError("range_type='bars' requires range_window_bars >= 2")

        ss, se = self.signal_hours_utc
        if not (0 <= ss < se <= 24):
            raise ValueError(f"signal_hours_utc invalid: {self.signal_hours_utc}")
        if self.exit_hours_utc is not None:
            xs, xe = self.exit_hours_utc
            if not (0 <= xs < xe <= 24):
                raise ValueError(f"exit_hours_utc invalid: {self.exit_hours_utc}")

        if self.entry_band_pct < 0:
            raise ValueError("entry_band_pct must be >= 0")
        if self.mode == "orb" and self.entry_band_pct > 0:
            raise ValueError("entry_band_pct must be 0 for mode='orb'")
        if self.atr_stop_mult < 0:
            raise ValueError("atr_stop_mult must be >= 0")
        if self.atr_window < 2:
            raise ValueError("atr_window must be >= 2")
        if self.max_hold < 1:
            raise ValueError("max_hold must be >= 1")
        if not (0 < self.risk_pct_of_equity <= 1.0):
            raise ValueError("risk_pct_of_equity must be in (0, 1]")

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._indicators = self._precompute(self.data[self.symbol])

    # ------------------------------------------------------------------
    # Precompute helpers

    def _precompute(self, df: pd.DataFrame) -> pd.DataFrame:
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)

        if self.range_type == "hours":
            range_high, range_low = self._time_window_range(df)
        else:
            range_high = high.rolling(
                int(self.range_window_bars), min_periods=int(self.range_window_bars)
            ).max().shift(1)
            range_low = low.rolling(
                int(self.range_window_bars), min_periods=int(self.range_window_bars)
            ).min().shift(1)

        prev_close = close.shift(1)
        tr = pd.concat(
            [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(
            alpha=1.0 / self.atr_window, adjust=False, min_periods=self.atr_window
        ).mean()

        return pd.DataFrame(
            {"range_high": range_high, "range_low": range_low, "atr": atr},
            index=df.index,
        )

    def _time_window_range(
        self, df: pd.DataFrame
    ) -> tuple[pd.Series, pd.Series]:
        """Day-block high/low keyed to the block's `he`-hour boundary.

        Leakage-free: a bar at ``ts`` sees the range of the most
        recent complete block whose closing boundary (``he`` hour on
        some prior date) is ``<= ts``.
        """
        assert self.range_hours_utc is not None  # validated in __post_init__
        hs, he = self.range_hours_utc
        hours = df.index.hour
        in_window = (hours >= hs) & (hours < he)
        in_bars = df[in_window]
        if in_bars.empty:
            # Pathological — no in-window bars. Return all-NaN series.
            nan = pd.Series(np.nan, index=df.index)
            return nan.copy(), nan.copy()

        daily = in_bars.groupby(in_bars.index.normalize()).agg(
            range_high=("high", "max"), range_low=("low", "min")
        )
        # Key each daily row to the block's closing boundary so it only
        # becomes visible on bars at or after that boundary.
        if he == 24:
            # Block closes at 00:00 of the *next* calendar day.
            boundary = daily.index + pd.Timedelta(days=1)
        else:
            boundary = daily.index + pd.Timedelta(hours=he)
        daily_at_boundary = daily.set_axis(boundary).sort_index()
        ref = daily_at_boundary.reindex(df.index, method="ffill")
        return ref["range_high"].astype(float), ref["range_low"].astype(float)

    # ------------------------------------------------------------------
    # Runtime

    def on_bar(
        self, bars: dict[str, Bar], portfolio: Portfolio, context: dict
    ) -> list[Order]:
        if self.symbol not in bars:
            return []
        bar = bars[self.symbol]
        ts = bar.timestamp
        try:
            idx = self._indicators.index.get_loc(ts)
        except KeyError:
            return []

        row = self._indicators.iloc[idx]
        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"session_state_{self.symbol}", {})

        if pos is not None:
            exit_order = self._maybe_exit(pos, bar, idx, row, state)
            if exit_order is not None:
                state.clear()
                return [exit_order]
            return []

        if row.isna().any():
            return []

        return self._maybe_enter(bar, idx, row, portfolio, state)

    def _in_window(self, hour: int, window: tuple[int, int]) -> bool:
        ws, we = window
        return ws <= hour < we

    def _maybe_enter(
        self,
        bar: Bar,
        idx: int,
        row: pd.Series,
        portfolio: Portfolio,
        state: dict,
    ) -> list[Order]:
        hour = int(bar.timestamp.hour)
        if not self._in_window(hour, self.signal_hours_utc):
            return []
        equity = portfolio.equity
        if equity <= 0 or bar.close <= 0:
            return []
        notional = equity * self.risk_pct_of_equity
        volume = notional / bar.close
        if volume <= 0:
            return []

        rh = float(row["range_high"])
        rl = float(row["range_low"])

        band = self.entry_band_pct
        if self.mode == "orb":
            long_trigger = bar.close > rh
            short_trigger = bar.close < rl
        else:  # mr / fade: symmetrical fade of range-extension
            width = max(rh - rl, 0.0)
            long_trigger = bar.close < rl - band * width
            short_trigger = bar.close > rh + band * width

        if self.direction in ("long", "both") and long_trigger:
            state["entry_idx"] = idx
            state["atr_at_entry"] = float(row["atr"])
            return [Order(symbol=self.symbol, side="buy", volume=volume)]
        if self.direction in ("short", "both") and short_trigger:
            state["entry_idx"] = idx
            state["atr_at_entry"] = float(row["atr"])
            return [Order(symbol=self.symbol, side="sell", volume=volume)]
        return []

    def _maybe_exit(
        self, pos, bar: Bar, idx: int, row: pd.Series, state: dict
    ) -> Order | None:
        entry_idx = int(state.get("entry_idx", idx))
        bars_held = idx - entry_idx
        atr_at_entry = float(state.get("atr_at_entry", 0.0))
        hour = int(bar.timestamp.hour)

        if pos.side == "long":
            if self.atr_stop_mult > 0 and atr_at_entry > 0:
                stop_px = pos.avg_entry_price - self.atr_stop_mult * atr_at_entry
                if bar.close <= stop_px:
                    return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            if self.exit_hours_utc is not None and self._in_window(hour, self.exit_hours_utc):
                return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            if bars_held >= self.max_hold:
                return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            return None

        # short
        if self.atr_stop_mult > 0 and atr_at_entry > 0:
            stop_px = pos.avg_entry_price + self.atr_stop_mult * atr_at_entry
            if bar.close >= stop_px:
                return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        if self.exit_hours_utc is not None and self._in_window(hour, self.exit_hours_utc):
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        if bars_held >= self.max_hold:
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        return None
