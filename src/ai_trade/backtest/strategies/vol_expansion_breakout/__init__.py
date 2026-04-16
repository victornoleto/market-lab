"""Vol-Expansion Breakout strategy package.

See docs/superpowers/specs/2026-04-15-vol-expansion-breakout-1h-design.md.
"""

from __future__ import annotations

from ai_trade.backtest.strategies.vol_expansion_breakout._breakout_signal import (
    BreakoutDirection,
    DonchianBreakout,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._exit_manager import (
    ExitManager,
    ExitReason,
    PositionState,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._regime_filter import (
    RegimeReading,
    YangZhangCone,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._strategy import (
    VolExpansionBreakoutStrategy,
)
from ai_trade.backtest.strategies.vol_expansion_breakout._vol_target_sizer import (
    VolTargetSizer,
)

__all__ = [
    "BreakoutDirection",
    "DonchianBreakout",
    "ExitManager",
    "ExitReason",
    "PositionState",
    "RegimeReading",
    "VolExpansionBreakoutStrategy",
    "VolTargetSizer",
    "YangZhangCone",
]
