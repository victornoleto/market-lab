"""ExitManager — three exit conditions, first-fires.

Exit priority order:
1. Opposite Donchian channel [trading_systems_methods, p.353]
2. 48 h hard time cap [tiingo-service spec §1.4]
3. Disaster stop 4σ [systematic_trading, p.212, ch.13]
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

import pandas as pd

from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
)


class ExitReason(str, Enum):
    OPPOSITE_CHANNEL = "opposite_channel"
    TIME_STOP = "time_stop"
    DISASTER_STOP = "disaster_stop"


@dataclass(frozen=True)
class PositionState:
    """Immutable snapshot of an open position captured at entry."""

    direction: BreakoutDirection
    entry_price: float
    entry_timestamp: datetime
    sigma_yz_at_entry_annual: float
    bars_per_year_at_entry: int


class ExitManager:
    """Evaluates three exit conditions in priority order and returns the first that fires.

    Parameters
    ----------
    n_exit:            Donchian channel lookback for the opposite-side exit [trading_systems_methods, p.353].
    max_hold_hours:    Hard time cap in wall-clock hours [tiingo-service spec §1.4].
    disaster_n_sigma:  Number of reference-period sigmas for the disaster stop [systematic_trading, p.212].
    ref_hold_bars:     Reference holding period in bars used to scale per-bar volatility [systematic_trading, ch.13].
    """

    def __init__(
        self,
        n_exit: int,
        max_hold_hours: float,
        disaster_n_sigma: float,
        ref_hold_bars: int,
    ) -> None:
        self.n_exit = n_exit
        self.max_hold_hours = max_hold_hours
        self.disaster_n_sigma = disaster_n_sigma
        self.ref_hold_bars = ref_hold_bars

    def disaster_threshold(self, position: PositionState) -> float:
        """Compute the price-distance threshold that triggers the disaster stop.

        Method [systematic_trading, p.212, ch.13]:
            sigma_pp_per_bar = entry_price * sigma_yz_annual / sqrt(bars_per_year)
            sigma_pp_ref     = sigma_pp_per_bar * sqrt(ref_hold_bars)
            threshold        = disaster_n_sigma * sigma_pp_ref
        """
        sigma_pp_per_bar = (
            position.entry_price
            * position.sigma_yz_at_entry_annual
            / math.sqrt(position.bars_per_year_at_entry)
        )
        sigma_pp_ref = sigma_pp_per_bar * math.sqrt(self.ref_hold_bars)
        return self.disaster_n_sigma * sigma_pp_ref

    def should_exit(
        self,
        df: pd.DataFrame,
        position: PositionState,
        now: datetime,
    ) -> ExitReason | None:
        """Return the first exit reason that fires, or None if no exit condition is met.

        Requires at least n_exit + 1 rows in df; returns None if buffer too small.
        """
        if len(df) < self.n_exit + 1:
            return None

        last_close = float(df["close"].iloc[-1])
        window = df.iloc[-(self.n_exit + 1):-1]

        # 1. Opposite Donchian channel [trading_systems_methods, p.353]
        if position.direction == BreakoutDirection.LONG:
            if last_close < float(window["low"].min()):
                return ExitReason.OPPOSITE_CHANNEL
        else:
            if last_close > float(window["high"].max()):
                return ExitReason.OPPOSITE_CHANNEL

        # 2. Time stop — hard cap [tiingo-service spec §1.4]
        if (now - position.entry_timestamp) >= timedelta(hours=self.max_hold_hours):
            return ExitReason.TIME_STOP

        # 3. Disaster stop [systematic_trading, p.212, ch.13]
        threshold = self.disaster_threshold(position)
        if position.direction == BreakoutDirection.LONG:
            if (position.entry_price - last_close) >= threshold:
                return ExitReason.DISASTER_STOP
        else:
            if (last_close - position.entry_price) >= threshold:
                return ExitReason.DISASTER_STOP

        return None
