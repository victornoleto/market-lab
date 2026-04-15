"""Chan Bollinger Pairs — canonical mean-reversion pair trading on 1h bars.

Implements the canonical formulation from [algo_trading_chan, p.71-73, ch.3]:
static OLS hedge ratio β fit on a training slice, OU regression to derive
half-life [p.47-48, ch.2], lookback = multiplier × half-life, Bollinger
z-score entry at ±entry_z, exit at 0.

Deviates from the pure-Chan canon in three CFD-specific adaptations (see
docstring of [_should_skip_entry_session] and [_maybe_exit]):

* Session gate (entry_hour_cutoff + Friday cut-offs) — protects against
  overnight swap and weekend 3x swap on Pepperstone CFD.
* Wall-clock 48h hard cap — [tiingo_service spec §1.4] short-hold gate.
* Spread-blow-out stop at |z| >= 3.0 — [p.293-294, ch.8] capital
  preservation against regime shift.

See `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio


@dataclass
class ChanBollingerPairsStrategy:
    """Canonical Chan Bollinger-z pair trader on 1h bars."""

    data: dict[str, pd.DataFrame]
    long_symbol: str = "GLD"
    short_symbol: str = "SLV"

    # Grid knobs.
    lookback_multiplier: int = 2
    entry_z: float = 1.0

    # Fixed constants (each one cited in the docstring / spec §3).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    train_bars: int = 1250
    half_life_min: int = 4
    half_life_max: int = 60
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13

    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.chan_pairs"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        return []  # scaffold — real logic in subsequent tasks
