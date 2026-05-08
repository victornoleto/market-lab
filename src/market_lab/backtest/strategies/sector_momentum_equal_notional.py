"""Cross-sectional momentum on SPDR sectors with equal-notional sizing.

Signal rule (identical to :mod:`sector_momentum_clenow`):

* Adjusted slope ranking = (annualized 90d exponential regression slope) × R²
  `[stocks_on_the_move, p.70-77, 82]`
* Per-asset disqualifiers: close < 100d SMA `[p.81]`, |daily move| > 15% in
  last 90d `[p.82]`
* Regime filter: buy only while regime_symbol close > 200d SMA
  `[p.66-67, 98-99]`
* Rebalance: weekly (arbitrary weekday — Clenow picks Wednesday `[p.98-99]`)
* Exit: rank falls outside top-K or disqualified — no stop-loss `[p.94-96]`

Sizing rule (differs from Clenow canonical):

* **Equal-notional**: each held sector receives ``equity × buy_leverage /
  top_k`` of exposure. shares = ``floor(target_notional / close)``.
* **Rationale** `[advances_fin_ml, p.298-299]`: with ``N ∈ {3..11}`` assets,
  the 1/N portfolio is a robust Bayesian prior against Markowitz's curse —
  covariance estimation error dominates in small-N. Equal-notional is also
  the **academic baseline** of cross-sectional momentum (Jegadeesh-Titman
  1993 used equal-weight deciles — referenced at `[stocks_on_the_move,
  p.60]`); Clenow's ATR-risk-parity is a refinement for S&P 500 universes
  with ATR ~1-3% of price.
* **Why not ATR risk-parity**: iter 002 showed the canonical 10 bps ATR
  sizing on 11 SPDR sectors (ATR ~0.3-1% of price) under-deploys by ~3×,
  leaving 60-80% of capital in cash regardless of signal edge. Equal-
  notional fully deploys capital and isolates the signal-edge question
  from the sizing-calibration issue.

Iteration 003 contract: tests of this module live in
``tests/test_sector_momentum_equal_notional.py``; the G7 numpy cross-lib
reference lives in the same test file.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

import pandas as pd

from market_lab.backtest.engine.execution import Bar, Order
from market_lab.backtest.engine.portfolio import Portfolio
from market_lab.backtest.strategies.base import StrategyBase
from market_lab.backtest.strategies.sector_momentum_clenow import (
    adjusted_slope,
    disqualify_gap,
    disqualify_trend,
    regime_allows_new_buys,
    top_k_ranks,
)

__all__ = [
    "SectorMomentumEqualNotional",
    "position_size_shares_equal_notional",
]


# ---------------------------------------------------------------------------
# Pure primitive (unit-tested)
# ---------------------------------------------------------------------------


def position_size_shares_equal_notional(
    equity: float,
    price: float,
    k_total: int,
    leverage: float = 1.0,
) -> int:
    """Equal-notional share count for one of ``k_total`` held positions.

    Target notional per position = ``equity × leverage / k_total``. Shares
    = ``floor(target_notional / price)``.

    Returns 0 for degenerate inputs (non-positive price, k_total, equity).

    Citation: `[advances_fin_ml, p.298-299]` for the 1/N prior motivation;
    Jegadeesh-Titman (1993) for equal-weight cross-sectional momentum as
    the academic baseline (via `[stocks_on_the_move, p.60]`).
    """
    if equity <= 0 or price <= 0 or k_total <= 0 or leverage <= 0:
        return 0
    if not (math.isfinite(equity) and math.isfinite(price) and math.isfinite(leverage)):
        return 0
    target_notional = equity * leverage / k_total
    shares = math.floor(target_notional / price)
    return int(max(0, shares))


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@dataclass
class SectorMomentumEqualNotional(StrategyBase):
    """Top-K sector momentum with equal-notional sizing + regime gate.

    Parameters
    ----------
    universe
        Tradable symbols (e.g. SPDR sectors). The regime_symbol (e.g. "SPY")
        MUST be present in the Runner's data dict but is not traded.
    regime_symbol
        Index ticker for the 200d regime filter.
    top_k
        Number of sectors to hold at any time.
    buy_leverage
        Notional gearing on entries. 1.0 = unlevered. Each position gets
        ``equity × buy_leverage / top_k`` of exposure.
    lookback_slope, lookback_trend, lookback_regime
        Canonical Clenow defaults — not tuned by grid (sweep is on ``top_k``
        and ``lookback_slope`` as per hypothesis spec).
    gap_threshold
        Max |daily return| in last ``lookback_slope`` bars `[p.82]`.
    rebalance_weekday
        0=Mon..4=Fri. Wednesday (=2) per `[p.98-99]` ("arbitrary").
    position_rebalance_every_n
        Resize existing positions every N portfolio rebalances (Clenow = 2).
    """

    universe: list[str] = field(default_factory=list)
    regime_symbol: str = "SPY"
    top_k: int = 5
    buy_leverage: float = 1.0
    lookback_slope: int = 90
    lookback_trend: int = 100
    lookback_regime: int = 200
    gap_threshold: float = 0.15
    rebalance_weekday: int = 2
    position_rebalance_every_n: int = 2

    _close_buf: dict[str, "deque[float]"] = field(default_factory=dict, init=False)
    _last_rebalance_date: pd.Timestamp | None = field(default=None, init=False)
    _rebalance_counter: int = field(default=0, init=False)
    _max_lookback: int = field(default=0, init=False)

    # ------------------------------------------------------------------
    # StrategyBase interface
    # ------------------------------------------------------------------

    def should_rebalance(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> bool:
        self._append_history(bars)
        if ts.weekday() != self.rebalance_weekday:
            return False
        if self._last_rebalance_date is not None:
            if (ts - self._last_rebalance_date).days < 5:
                return False
        regime_buf = self._close_buf.get(self.regime_symbol)
        if regime_buf is None or len(regime_buf) < self._max_lookback:
            return False
        return True

    def on_rebalance(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        self._last_rebalance_date = ts
        self._rebalance_counter += 1

        scores: dict[str, float] = {}
        disq: set[str] = set()
        for sym in self.universe:
            close_buf = self._close_buf.get(sym)
            if close_buf is None or len(close_buf) < max(
                self.lookback_slope, self.lookback_trend
            ):
                disq.add(sym)
                continue
            close = pd.Series(list(close_buf))
            try:
                slope, r2 = adjusted_slope(close, lookback=self.lookback_slope)
            except ValueError:
                disq.add(sym)
                continue
            if disqualify_trend(close, lookback=self.lookback_trend):
                disq.add(sym)
            if disqualify_gap(
                close, lookback=self.lookback_slope, threshold=self.gap_threshold
            ):
                disq.add(sym)
            scores[sym] = slope * r2

        top = top_k_ranks(scores, k=self.top_k, disqualified=disq)
        regime_close = pd.Series(list(self._close_buf[self.regime_symbol]))
        regime_on = regime_allows_new_buys(regime_close, lookback=self.lookback_regime)

        orders: list[Order] = []

        # Sell leg — anything held that drops out of top-K or gets disqualified.
        # Clenow `[p.94-95]`: do not force exit just because regime went off.
        held = list(portfolio.positions.keys())
        sell_syms: set[str] = set()
        for sym in held:
            if sym not in self.universe:
                continue
            pos = portfolio.positions[sym]
            should_exit = (
                sym not in top
                or sym in disq
                or sym not in bars
            )
            if should_exit and sym in bars:
                orders.append(Order(symbol=sym, side="sell", volume=pos.volume))
                sell_syms.add(sym)

        # Buy leg — only if regime ON. Equal-notional sizing per top-K slot.
        if regime_on:
            equity = portfolio.equity
            for sym in top:
                if sym in portfolio.positions and sym not in sell_syms:
                    continue  # already held, not exiting
                if sym not in bars:
                    continue
                price = bars[sym].close
                shares = position_size_shares_equal_notional(
                    equity=equity,
                    price=price,
                    k_total=self.top_k,
                    leverage=self.buy_leverage,
                )
                if shares > 0:
                    orders.append(Order(symbol=sym, side="buy", volume=float(shares)))

        # Periodic position rebalance `[p.99, p.108]`: every N-th rebalance,
        # resize existing survivors to current equal-notional target.
        if self._rebalance_counter % self.position_rebalance_every_n == 0:
            survivors = [
                s for s in portfolio.positions
                if s in top and s not in disq and s in bars and s not in sell_syms
            ]
            for sym in survivors:
                price = bars[sym].close
                target = position_size_shares_equal_notional(
                    equity=portfolio.equity,
                    price=price,
                    k_total=self.top_k,
                    leverage=self.buy_leverage,
                )
                current = int(portfolio.positions[sym].volume)
                diff = target - current
                if diff > 0:
                    orders.append(Order(symbol=sym, side="buy", volume=float(diff)))
                elif diff < 0:
                    orders.append(Order(symbol=sym, side="sell", volume=float(-diff)))

        return orders

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _append_history(self, bars: dict[str, Bar]) -> None:
        if self._max_lookback == 0:
            self._max_lookback = max(
                self.lookback_slope, self.lookback_trend, self.lookback_regime
            )
        cap = self._max_lookback
        for sym, bar in bars.items():
            if sym not in self._close_buf:
                self._close_buf[sym] = deque(maxlen=cap)
            self._close_buf[sym].append(bar.close)
