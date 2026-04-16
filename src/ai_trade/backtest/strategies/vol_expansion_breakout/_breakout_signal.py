"""Donchian channel breakout signal [trading_systems_methods, p.353]."""
from __future__ import annotations

from enum import Enum

import pandas as pd


class BreakoutDirection(str, Enum):
    LONG = "long"
    SHORT = "short"


class DonchianBreakout:
    """Fires a breakout signal when the last close exceeds the n_entry-bar Donchian channel.

    Entry logic [trading_systems_methods, p.353]:
    - LONG  when close[-1] strictly > max(high[-n_entry-1:-1])
    - SHORT when close[-1] strictly < min(low[-n_entry-1:-1])
    - None  otherwise (including exact-boundary touches)
    """

    def __init__(self, n_entry: int) -> None:
        if n_entry < 2:
            raise ValueError("n_entry must be >= 2")
        self.n_entry = n_entry

    def fire(self, df: pd.DataFrame) -> BreakoutDirection | None:
        """Return breakout direction or None if no signal / insufficient data."""
        if len(df) < self.n_entry + 1:
            return None
        window = df.iloc[-(self.n_entry + 1):-1]
        last_close = float(df["close"].iloc[-1])
        if last_close > float(window["high"].max()):
            return BreakoutDirection.LONG
        if last_close < float(window["low"].min()):
            return BreakoutDirection.SHORT
        return None
