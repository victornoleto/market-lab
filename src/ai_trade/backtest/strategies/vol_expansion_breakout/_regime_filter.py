"""Yang-Zhang volatility estimator + cone percentile filter.

Sinclair [volatility_trading, p.22-23, Eq.2.17a] for YZ; [p.58-60] for cone.
Output API consumed by sizer (§3.3) and disaster stop (§3.4) of the spec.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RegimeReading:
    """Single observation of regime state at one bar."""

    is_quiet: bool
    sigma_yz_annual: float
    sigma_yz_percentile: float
    bars_in_history: int


class YangZhangCone:
    """Yang-Zhang volatility cone with k_filter percentile regime gate.

    Reference:
        σ²_yz = σ²_o + k·σ²_c + (1-k)·σ²_rs  [volatility_trading, p.22-23, Eq.2.17a]
        Cone percentile gate                    [volatility_trading, p.58-60]
    """

    def __init__(
        self,
        yz_window: int,
        cone_lookback: int,
        k_filter: float,
        bars_per_year: int,
    ) -> None:
        if yz_window < 2:
            raise ValueError("yz_window must be >= 2")
        if cone_lookback < yz_window:
            raise ValueError("cone_lookback must be >= yz_window")
        if not 0.0 < k_filter < 100.0:
            raise ValueError("k_filter must be in (0, 100)")
        if bars_per_year <= 0:
            raise ValueError("bars_per_year must be positive")
        self.yz_window = yz_window
        self.cone_lookback = cone_lookback
        self.k_filter = k_filter
        self.bars_per_year = bars_per_year

    # ------------------------------------------------------------------
    # Task 3: Yang-Zhang per-bar estimator
    # ------------------------------------------------------------------

    def _k(self) -> float:
        """Weighting factor k [volatility_trading, p.22-23, Eq.2.17a]."""
        n = self.yz_window
        return 0.34 / (1.34 + (n + 1) / (n - 1))

    def _yz_per_bar(self, df: pd.DataFrame) -> float:
        """Yang-Zhang per-bar sigma over the most recent yz_window bars.

        Requires len(df) >= yz_window + 1 (needs prior close for overnight).
        Returns 0.0 if data is degenerate.

        σ²_yz = σ²_o + k·σ²_c + (1-k)·σ²_rs  [volatility_trading, p.22-23, Eq.2.17a]
        """
        if len(df) < self.yz_window + 1:
            return 0.0
        window = df.iloc[-(self.yz_window + 1):]
        opens = window["open"].to_numpy()
        highs = window["high"].to_numpy()
        lows = window["low"].to_numpy()
        closes = window["close"].to_numpy()

        # Overnight: close-to-open log returns [volatility_trading, p.22]
        log_oc = np.log(opens[1:] / closes[:-1])
        var_o = float(np.var(log_oc, ddof=0))

        # Daytime: open-to-close log returns [volatility_trading, p.22]
        log_co = np.log(closes[1:] / opens[1:])
        var_c = float(np.var(log_co, ddof=0))

        # Rogers-Satchell-Yoon intraday component [volatility_trading, p.22, Eq.2.16]
        h, l, o, c = highs[1:], lows[1:], opens[1:], closes[1:]
        rs_terms = np.log(h / c) * np.log(h / o) + np.log(l / c) * np.log(l / o)
        var_rs = float(np.mean(rs_terms))

        k = self._k()
        var_yz = var_o + k * var_c + (1.0 - k) * var_rs
        if not np.isfinite(var_yz) or var_yz <= 0:
            return 0.0
        return math.sqrt(var_yz)

    def _annualize(self, sigma_per_bar: float) -> float:
        """Annualize per-bar sigma: σ_annual = σ_per_bar × sqrt(bars_per_year)."""
        return sigma_per_bar * math.sqrt(self.bars_per_year)

    # ------------------------------------------------------------------
    # Task 4: cone percentile read() — public API
    # ------------------------------------------------------------------

    def read(self, df: pd.DataFrame) -> RegimeReading:
        """Compute current sigma_yz and its percentile in the cone history.

        Returns is_quiet=True when current YZ is in the bottom k_filter
        percentile of the cone_lookback history [volatility_trading, p.58-60].
        """
        n = len(df)
        min_required = self.yz_window + 1
        if n < min_required:
            return RegimeReading(
                is_quiet=False,
                sigma_yz_annual=0.0,
                sigma_yz_percentile=float("nan"),
                bars_in_history=0,
            )

        history: list[float] = []
        for end in range(min_required, n + 1):
            sigma = self._yz_per_bar(df.iloc[:end])
            history.append(sigma)

        sigma_now_per_bar = history[-1]
        sigma_now_annual = self._annualize(sigma_now_per_bar)
        bars_in_history = len(history)

        if bars_in_history > self.cone_lookback:
            history = history[-self.cone_lookback:]

        if bars_in_history < self.cone_lookback:
            return RegimeReading(
                is_quiet=False,
                sigma_yz_annual=sigma_now_annual,
                sigma_yz_percentile=float("nan"),
                bars_in_history=bars_in_history,
            )

        arr = np.asarray(history, dtype=float)
        pct = float((arr <= sigma_now_per_bar).sum()) / len(arr) * 100.0
        is_quiet = pct <= self.k_filter

        return RegimeReading(
            is_quiet=is_quiet,
            sigma_yz_annual=sigma_now_annual,
            sigma_yz_percentile=pct,
            bars_in_history=bars_in_history,
        )
