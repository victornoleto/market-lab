"""Strategy D — Swing BR ranking mensal (base + leads D1 + D4).

Three classes:

* :class:`MonthlyRankingStrategy` — abstract base. Handles the monthly
  rebalance trigger, dynamic universe filter (via
  :func:`~ai_trade.backtest.data.br_tickers.get_universe_on`), sector cap
  enforcement, position inertia, and order emission. Subclasses plug in
  their scoring function via :meth:`compute_scores`.

* :class:`D1ClenowBR` — Lead D1. Adjusted Slope (annualized regression
  slope × R²) over a lookback window, with SMA₁₀₀ trend filter and gap
  filter. Mirrors :class:`ETFRotationStrategy` from the US side of the
  project but adapted to a dynamic BR universe with sector caps.

* :class:`D4LowvolMomBR` — Lead D4. Two-stage ranker: take top-K by
  adjusted slope 180d, then re-rank by ascending realized volatility and
  keep top-N. Hypothesis: carries the Clenow signal while avoiding
  single-name concentration in the most volatile names (Petrobras, Vale,
  small-caps), which is a known failure mode of pure momentum on a
  heavily-concentrated index like IBrX-100.

Citations
---------
* Adjusted Slope, SMA₁₀₀ filter, gap filter, 20-30 basket size, ATR
  sizing 10 bps/day: ``[stocks_on_the_move, p.76-77, 81-82, 88,
  153, 229-230]``.
* Position inertia 10%: ``[systematic_trading, p.174]``.
* Equal-weight > conviction weights (Kahneman via Chan):
  ``[quant_trading_chan, ch.1, p.7]``.
* Mandate anchor: ``docs/investment-mandate.md §4b``.
"""

from __future__ import annotations

import logging
import math
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from ai_trade.backtest.data.br_tickers import (
    UniverseConfig,
    get_universe_on,
    sector_of,
)
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.helpers.momentum import adjusted_slope, atr, max_gap
from ai_trade.backtest.strategies.base import StrategyBase

log = logging.getLogger(__name__)

__all__ = [
    "D1ClenowBR",
    "D4LowvolMomBR",
    "MonthlyRankingStrategy",
]


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------
@dataclass
class MonthlyRankingStrategy(StrategyBase):
    """Monthly cross-sectional ranking on a dynamic BR universe.

    Parameters
    ----------
    data
        Full OHLCV history for **all** candidate tickers (pre-adjusted).
        The strategy selects the active universe each month by liquidity.
    n_top
        Basket size — how many tickers to hold. Grid ∈ {15, 20, 25, 30}
        per ``[stocks_on_the_move, p.153, 229-230]``.
    sector_cap_pct
        Maximum portion of equity in any single sector (e.g. 0.25 = 25%).
        ``None`` disables the cap.
    position_inertia_pct
        Hysteresis: hold a ticker that has fallen to rank
        ``n_top × (1 + inertia)`` rather than swap it for one at the
        boundary. Default 10% per ``[systematic_trading, p.174]``.
    universe_config
        Parameters for :func:`get_universe_on` — liquidity floor, lookback.
    sizing
        ``"equal"`` for equal notional per basket slot, or ``"atr"`` for
        Clenow's ATR-based risk parity at 10 bps/day
        ``[stocks_on_the_move, p.88]``. ATR sizing typically scales the
        equal-weight target, so the basket still roughly sums to 100%.
    atr_risk_per_day
        Per-position daily risk fraction used when ``sizing="atr"``.
    atr_lookback
        ATR window (Clenow uses 20 days).
    """

    data: dict[str, pd.DataFrame]
    n_top: int = 20
    sector_cap_pct: float | None = 0.25
    position_inertia_pct: float = 0.10
    universe_config: UniverseConfig = field(default_factory=UniverseConfig)
    sizing: str = "equal"
    atr_risk_per_day: float = 0.001
    atr_lookback: int = 20

    _prev_month: int = field(init=False, default=-1)
    _last_targets: list[str] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        if self.n_top <= 0:
            raise ValueError(f"n_top must be > 0, got {self.n_top}")
        if self.sector_cap_pct is not None and not (
            0.0 < self.sector_cap_pct <= 1.0
        ):
            raise ValueError(
                f"sector_cap_pct must be in (0, 1], got {self.sector_cap_pct}"
            )
        if self.position_inertia_pct < 0:
            raise ValueError(
                f"position_inertia_pct must be ≥ 0, got {self.position_inertia_pct}"
            )
        if self.sizing not in ("equal", "atr"):
            raise ValueError(f"sizing must be 'equal' or 'atr', got {self.sizing!r}")
        self._prev_month = -1
        self._last_targets = []

    # -- Rebalance trigger ---------------------------------------------------
    def should_rebalance(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> bool:
        """Trigger on the first bar of each new calendar month.

        Same pattern as :class:`ETFRotationStrategy`.
        """
        if ts.month != self._prev_month:
            self._prev_month = ts.month
            return True
        return False

    # -- Abstract scoring ---------------------------------------------------
    @abstractmethod
    def compute_scores(
        self,
        universe: list[str],
        ts: pd.Timestamp,
        bars: dict[str, Bar],
    ) -> dict[str, float]:
        """Return ``{ticker: score}`` (higher is better) for each eligible ticker.

        Tickers missing from the returned dict are implicitly dropped from
        ranking — use this to express "filtered out" (failed trend filter,
        insufficient history, etc.).
        """

    # -- Rebalance engine ----------------------------------------------------
    def on_rebalance(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        universe = get_universe_on(
            ts.date() if hasattr(ts, "date") else ts,
            self.data,
            self.universe_config,
        )
        if not universe:
            return self._exit_all(portfolio)

        scores = self.compute_scores(universe, ts, bars)
        if not scores:
            return self._exit_all(portfolio)

        targets = self._pick_targets(scores)
        if not targets:
            return self._exit_all(portfolio)

        # Capture for subsequent sessions' inertia decisions.
        self._last_targets = list(targets)

        return self._emit_orders(targets, scores, ts, bars, portfolio)

    # -- Ranking with inertia + sector cap ----------------------------------
    def _pick_targets(self, scores: dict[str, float]) -> list[str]:
        """Select the final basket, applying inertia then sector cap.

        Inertia: include previously-held tickers still in the top
        ``n_top × (1 + inertia_pct)``, ahead of fresh boundary names.
        Sector cap: stop adding tickers from a sector once it would
        exceed ``sector_cap_pct`` of the basket by count.
        """
        ranked = sorted(scores, key=scores.__getitem__, reverse=True)
        inertia_cutoff = int(math.ceil(self.n_top * (1.0 + self.position_inertia_pct)))
        inertia_pool = set(ranked[:inertia_cutoff])

        # Priority 1: previously-held tickers still within inertia pool.
        held_first = [t for t in self._last_targets if t in inertia_pool]
        # Priority 2: new top-ranked not already in held_first.
        fresh = [t for t in ranked if t not in held_first]

        ordered = held_first + fresh

        selected: list[str] = []
        sector_counts: dict[str, int] = {}
        max_per_sector = (
            int(math.floor(self.n_top * self.sector_cap_pct))
            if self.sector_cap_pct is not None
            else self.n_top  # no cap
        )
        # Ensure at least 1 per sector is allowed even if cap would round to 0.
        max_per_sector = max(1, max_per_sector)

        for ticker in ordered:
            if len(selected) >= self.n_top:
                break
            sec = sector_of(ticker)
            if sector_counts.get(sec, 0) >= max_per_sector:
                continue
            selected.append(ticker)
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

        return selected

    # -- Order emission ------------------------------------------------------
    def _emit_orders(
        self,
        targets: list[str],
        scores: dict[str, float],
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
    ) -> list[Order]:
        orders: list[Order] = []
        target_set = set(targets)

        # Close positions not in target set.
        for sym in list(portfolio.positions):
            if sym not in target_set:
                pos = portfolio.positions[sym]
                orders.append(
                    Order(
                        symbol=sym,
                        side="sell" if pos.side == "long" else "buy",
                        volume=pos.volume,
                    )
                )

        if not targets:
            return orders

        base_alloc = 1.0 / len(targets)
        equity = portfolio.equity

        for target in targets:
            if target in portfolio.positions:
                continue  # inertia kept it; skip re-entry (engine doesn't need to top-up)
            bar = bars.get(target)
            if bar is None or bar.close <= 0 or equity <= 0:
                continue
            scale = self._sizing_scale(target, ts, bar) if self.sizing == "atr" else 1.0
            volume_brl = equity * base_alloc * scale
            volume_shares = volume_brl / bar.close
            if volume_shares > 0:
                orders.append(Order(symbol=target, side="buy", volume=volume_shares))

        return orders

    def _sizing_scale(
        self, ticker: str, ts: pd.Timestamp, bar: Bar
    ) -> float:
        """ATR-based scale: position takes ``atr_risk_per_day`` × equity per day.

        From Clenow ``[stocks_on_the_move, p.88]``: ``shares = (capital × 0.001)
        / ATR(20)``. Converted to a scale relative to equal-weight so the
        basket retains its notional target (the scale caps at 1 to avoid
        concentrated positions just because a stock is low-vol).
        """
        df = self.data.get(ticker)
        if df is None:
            return 1.0
        tail = df.loc[:ts]
        if len(tail) < self.atr_lookback + 1:
            return 1.0
        atr_value = atr(tail["high"], tail["low"], tail["close"], self.atr_lookback)
        if not math.isfinite(atr_value) or atr_value <= 0:
            return 1.0
        # Equal-weight target per slot: 1/n_top × equity; scale down if too much risk.
        # Clenow direct sizing: risk-per-day = atr / price; normalize so equal-weight ≈ 1.
        risk_per_currency = atr_value / bar.close  # fraction of price per day
        if risk_per_currency <= 0:
            return 1.0
        # Scale so that position × risk_per_currency ≈ atr_risk_per_day × (1/n_top).
        target_risk_per_slot = self.atr_risk_per_day * self.n_top
        scale = target_risk_per_slot / risk_per_currency
        return float(min(1.0, max(0.0, scale)))

    def _exit_all(self, portfolio: Portfolio) -> list[Order]:
        orders: list[Order] = []
        for sym, pos in list(portfolio.positions.items()):
            orders.append(
                Order(
                    symbol=sym,
                    side="sell" if pos.side == "long" else "buy",
                    volume=pos.volume,
                )
            )
        self._last_targets = []
        return orders

    # -- Helpers reusable by subclasses -------------------------------------
    def _close_up_to(self, ticker: str, ts: pd.Timestamp) -> pd.Series | None:
        df = self.data.get(ticker)
        if df is None or "close" not in df.columns:
            return None
        closes = df["close"].loc[:ts]
        return closes if not closes.empty else None


# ---------------------------------------------------------------------------
# Lead D1 — Clenow momentum
# ---------------------------------------------------------------------------
@dataclass
class D1ClenowBR(MonthlyRankingStrategy):
    """Lead D1: cross-sectional Clenow momentum on IBrX-100.

    Score per ticker = annualized regression slope × R² over
    ``lookback`` days. Filters:

    * ``close > SMA(sma_stock_period)`` (trend filter)
      ``[stocks_on_the_move, p.81-82]``.
    * ``max |close-to-close return| over lookback ≤ max_gap_pct``
      ``[stocks_on_the_move, p.82]``.

    Parameters (on top of base)
    ---------------------------
    lookback
        Regression window in trading days. Grid ∈ {90, 180}
        ``[stocks_on_the_move, p.76]``.
    sma_stock_period
        Per-stock trend filter SMA. Canonical 100
        ``[stocks_on_the_move, p.81-82]``.
    max_gap_pct
        Single-day-move filter. Canonical 15%
        ``[stocks_on_the_move, p.82]``.
    """

    lookback: int = 90
    sma_stock_period: int = 100
    max_gap_pct: float = 0.15

    def compute_scores(
        self,
        universe: list[str],
        ts: pd.Timestamp,
        bars: dict[str, Bar],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}
        min_hist = max(self.lookback, self.sma_stock_period)
        for sym in universe:
            if sym not in bars:
                continue
            closes = self._close_up_to(sym, ts)
            if closes is None or len(closes) < min_hist:
                continue
            # Trend filter
            sma_val = float(closes.iloc[-self.sma_stock_period :].mean())
            if float(closes.iloc[-1]) < sma_val:
                continue
            # Gap filter
            gap = max_gap(closes, self.lookback)
            if gap > self.max_gap_pct:
                continue
            # Score
            try:
                slope, r2 = adjusted_slope(closes, self.lookback)
            except ValueError:
                continue
            if math.isnan(slope) or math.isnan(r2):
                continue
            scores[sym] = slope * r2
        return scores


# ---------------------------------------------------------------------------
# Lead D4 — Low-vol + Momentum hybrid
# ---------------------------------------------------------------------------
@dataclass
class D4LowvolMomBR(MonthlyRankingStrategy):
    """Lead D4: 2-stage rank — top-K by momentum, re-rank by low vol.

    Stage 1: adjusted slope over ``slope_lookback`` (180d default) — take
    top ``pre_n`` (30/40/50). Stage 2: re-rank the survivors by ascending
    realized volatility over ``vol_lookback`` (60/90d) — keep top ``n_top``.

    Hypothesis: Clenow's raw momentum tends to concentrate the basket in
    the highest-volatility single names (e.g. commodity giants during
    super-cycles, small-caps in rally phases). Adding a low-vol re-rank
    preserves the momentum signal while pushing the basket toward more
    risk-balanced allocations. No single book citation — composite of
    Clenow (momentum) ``[stocks_on_the_move, p.76-77]`` + low-vol
    anomaly literature (Frazzini-Pedersen "Betting Against Beta"; within
    the ai-trade knowledge base this is motivated by the Kahneman-via-Chan
    rationale for equal-weight rank combinations
    ``[quant_trading_chan, ch.1, p.7]``).

    Parameters (on top of base)
    ---------------------------
    slope_lookback
        Momentum regression window. Default 180d.
    pre_n
        First-stage cut — how many survive the momentum filter before
        vol re-ranking. Grid ∈ {30, 40, 50}.
    vol_lookback
        Realized vol window. Grid ∈ {60, 90}.
    """

    slope_lookback: int = 180
    pre_n: int = 40
    vol_lookback: int = 90

    def compute_scores(
        self,
        universe: list[str],
        ts: pd.Timestamp,
        bars: dict[str, Bar],
    ) -> dict[str, float]:
        # Stage 1: momentum score (same shape as D1, but no trend/gap filters —
        # the re-rank will prune anyway).
        momentum: dict[str, float] = {}
        for sym in universe:
            if sym not in bars:
                continue
            closes = self._close_up_to(sym, ts)
            if closes is None or len(closes) < max(self.slope_lookback, self.vol_lookback + 1):
                continue
            try:
                slope, r2 = adjusted_slope(closes, self.slope_lookback)
            except ValueError:
                continue
            if math.isnan(slope) or math.isnan(r2):
                continue
            momentum[sym] = slope * r2

        if not momentum:
            return {}

        top_k = sorted(momentum, key=momentum.__getitem__, reverse=True)[: self.pre_n]

        # Stage 2: score = -realized_vol(vol_lookback) (ascending vol = better).
        scores: dict[str, float] = {}
        for sym in top_k:
            closes = self._close_up_to(sym, ts)
            if closes is None:
                continue
            rets = closes.iloc[-(self.vol_lookback + 1) :].pct_change().dropna()
            if len(rets) < self.vol_lookback // 2:
                continue
            vol_ann = float(rets.std(ddof=1) * np.sqrt(252))
            if not math.isfinite(vol_ann) or vol_ann <= 0:
                continue
            scores[sym] = -vol_ann
        return scores
