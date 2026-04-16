"""Yang-Zhang volatility estimator + cone percentile filter.

Sinclair [volatility_trading, p.22-23, Eq.2.17a] for YZ; [p.58-60] for cone.
Output API consumed by sizer (§3.3) and disaster stop (§3.4) of the spec.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class RegimeReading:
    """Single observation of regime state at one bar."""

    is_quiet: bool
    sigma_yz_annual: float
    sigma_yz_percentile: float
    bars_in_history: int


class YangZhangCone:
    """Stub — implementation in subsequent tasks."""

    def __init__(self, yz_window: int, cone_lookback: int, k_filter: float, bars_per_year: int) -> None:
        self.yz_window = yz_window
        self.cone_lookback = cone_lookback
        self.k_filter = k_filter
        self.bars_per_year = bars_per_year
