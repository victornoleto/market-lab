"""Donchian Channel Breakout strategy (intraday / short-hold).

Bar-level breakout strategy for Phase 3.5a Lead T2 (Path A short-hold
CFD). Designed to test trend-follow edge on FX, metals and equity-index
proxies on 1-hour bars, where BollingerMR mean-reversion failed
(`2026-04-18-0130-phase3.5a-T1-bollinger-mr-fx-metals-DEAD.md`).

Trades through the same ``Runner``/``ExecutionSimulator`` pipeline as
``BollingerMRStrategy``, so per-bar Pepperstone costs (spread,
commission, swap) and bar-level fills are honored.

Citations
---------

- Donchian channel (N-day high/low breakout) and Turtles 20/40 entry,
  10/20 exit: ``[trading_systems_methods, p.353]`` — "Buy when high >
  max high N days; exit long when low < min low M days, M < N".
- Time-series momentum as a distinct family: ``[algo_trading_chan,
  p.133, ch.6]`` — "past returns of a single instrument are positively
  correlated with future returns".
- ATR-based hard stop and time-stop (intraday risk control):
  ``[machine_trading, p.126, ch.4]`` — "exit after N bars if not
  profitable" + ATR multiple stop.
- Volatility-targeted notional via ATR (optional): ``[volatility_trading]``
  — risk-by-vol scaling so equal $-risk per trade.

Pipeline (per bar)
------------------

1. Pre-compute rolling ``max(high, entry_lookback)``, ``min(low,
   entry_lookback)`` (entry channel) and ``min(low, exit_lookback)``,
   ``max(high, exit_lookback)`` (exit channel). The channels exclude
   the current bar (shifted by 1) so the signal is leakage-free.
2. **Long entry:** close > prior entry high.
3. **Long exit:** close < prior exit low (M-bar low) OR ATR-based stop
   OR time-stop (max_hold bars).
4. **Short entry (optional):** close < prior entry low.
5. **Short exit:** close > prior exit high OR ATR-stop OR time-stop.

One position at a time, fixed risk-pct sizing.
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

Direction = Literal["long", "short", "both"]


@dataclass
class DonchianBreakoutStrategy:
    """Single-instrument Donchian channel breakout (short-hold)."""

    data: dict[str, pd.DataFrame]
    symbol: str = "SPY"
    entry_lookback: int = 20
    exit_lookback: int = 10
    atr_lookback: int = 14
    atr_stop_mult: float = 2.0  # 0.0 to disable ATR stop
    max_hold: int = 120  # ~5 days on FX 1h (24h * 5)
    risk_pct_of_equity: float = 0.95
    direction: Direction = "long"

    _indicators: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.donchian"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.entry_lookback < 2:
            raise ValueError(f"entry_lookback must be >= 2, got {self.entry_lookback}")
        if self.exit_lookback < 1:
            raise ValueError(f"exit_lookback must be >= 1, got {self.exit_lookback}")
        if self.exit_lookback >= self.entry_lookback:
            raise ValueError(
                f"exit_lookback ({self.exit_lookback}) must be < entry_lookback "
                f"({self.entry_lookback}) per Turtles canonical."
            )
        if self.atr_lookback < 2:
            raise ValueError(f"atr_lookback must be >= 2, got {self.atr_lookback}")
        if self.atr_stop_mult < 0:
            raise ValueError(f"atr_stop_mult must be >= 0, got {self.atr_stop_mult}")
        if self.max_hold < 1:
            raise ValueError(f"max_hold must be >= 1, got {self.max_hold}")
        if self.direction not in ("long", "short", "both"):
            raise ValueError(
                f"direction must be 'long', 'short', or 'both', got {self.direction!r}"
            )
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._precompute_indicators(self.symbol)

    def _precompute_indicators(self, symbol: str) -> None:
        df = self.data[symbol]
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        close = df["close"].astype(float)

        # Channels EXCLUDE current bar (shift 1) — leakage-free.
        entry_high = high.shift(1).rolling(self.entry_lookback,
                                           min_periods=self.entry_lookback).max()
        entry_low = low.shift(1).rolling(self.entry_lookback,
                                         min_periods=self.entry_lookback).min()
        exit_low = low.shift(1).rolling(self.exit_lookback,
                                        min_periods=self.exit_lookback).min()
        exit_high = high.shift(1).rolling(self.exit_lookback,
                                          min_periods=self.exit_lookback).max()

        # ATR (Wilder's classic) for stop sizing.
        prev_close = close.shift(1)
        tr = pd.concat(
            [(high - low),
             (high - prev_close).abs(),
             (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        atr = tr.ewm(alpha=1.0 / self.atr_lookback,
                     adjust=False, min_periods=self.atr_lookback).mean()

        self._indicators[symbol] = pd.DataFrame(
            {
                "entry_high": entry_high,
                "entry_low": entry_low,
                "exit_low": exit_low,
                "exit_high": exit_high,
                "atr": atr,
            },
            index=df.index,
        )

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if self.symbol not in bars:
            return []

        bar = bars[self.symbol]
        ts = bar.timestamp
        ind = self._indicators[self.symbol]
        try:
            idx = ind.index.get_loc(ts)
        except KeyError:
            return []

        if idx < max(self.entry_lookback, self.atr_lookback):
            return []

        row = ind.iloc[idx]
        if row.isna().any():
            return []

        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"donchian_state_{self.symbol}", {})

        if pos is not None:
            order = self._maybe_exit(pos, bar, idx, state, row)
            if order is not None:
                state.clear()
                return [order]
            return []

        return self._maybe_enter(bar, idx, state, portfolio, row)

    def _maybe_exit(
        self, pos, bar: Bar, idx: int, state: dict, row: pd.Series,
    ) -> Order | None:
        entry_idx = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        atr_at_entry = state.get("atr_at_entry", 0.0)

        if pos.side == "long":
            # 1. ATR stop (price drops by N×ATR from entry).
            if self.atr_stop_mult > 0 and atr_at_entry > 0:
                stop_px = pos.avg_entry_price - self.atr_stop_mult * atr_at_entry
                if bar.close <= stop_px:
                    return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            # 2. Donchian exit channel breakdown.
            if bar.close < float(row["exit_low"]):
                return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            # 3. Time-stop.
            if bars_held >= self.max_hold:
                return Order(symbol=self.symbol, side="sell", volume=pos.volume)
            return None

        # short
        if self.atr_stop_mult > 0 and atr_at_entry > 0:
            stop_px = pos.avg_entry_price + self.atr_stop_mult * atr_at_entry
            if bar.close >= stop_px:
                return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        if bar.close > float(row["exit_high"]):
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        if bars_held >= self.max_hold:
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)
        return None

    def _maybe_enter(
        self,
        bar: Bar,
        idx: int,
        state: dict,
        portfolio: Portfolio,
        row: pd.Series,
    ) -> list[Order]:
        equity = portfolio.equity
        if equity <= 0 or bar.close <= 0:
            return []
        notional = equity * self.risk_pct_of_equity
        volume = notional / bar.close
        if volume <= 0:
            return []

        if self.direction in ("long", "both") and bar.close > float(row["entry_high"]):
            state["entry_idx"] = idx
            state["atr_at_entry"] = float(row["atr"])
            return [Order(symbol=self.symbol, side="buy", volume=volume)]

        if self.direction in ("short", "both") and bar.close < float(row["entry_low"]):
            state["entry_idx"] = idx
            state["atr_at_entry"] = float(row["atr"])
            return [Order(symbol=self.symbol, side="sell", volume=volume)]

        return []
