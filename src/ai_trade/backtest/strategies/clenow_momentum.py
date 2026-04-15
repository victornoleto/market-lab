"""Clenow ``stocks_on_the_move`` momentum replication.

Every rule and constant is sourced from Clenow (2015). Citation tags match
the book summary at ``books/summaries/stocks_on_the_move.md``.

Core rules (verbatim from the book)
-----------------------------------
* **Ranking** — per-stock adjusted slope = (annualized 90-day exponential
  regression slope) × R². Higher is better. ``[p.70-72, p.76-77, p.82, p.98]``
* **Universe** — S&P 500, point-in-time membership. ``[p.98, p.107]``
* **Regime filter** — buy only if the index is above its 200-day MA.
  Existing positions are NOT sold because of the regime filter. ``[p.66-67,
  p.94-95, p.98-99]``
* **Per-stock trend filter** — stock must trade above its own 100-day MA to
  be buyable. Held stocks that fall below the 100-day MA are sold. ``[p.81-82,
  p.98]``
* **Gap filter** — disqualify (and exit) any stock with a single-day move of
  > 15% in the past 90 trading days. ``[p.82, p.98]``
* **Top 20% cutoff** — hold only stocks in the top 20% of the ranking
  (``rank ≤ 100`` on SPX 500). Stocks that slip below that cutoff are sold.
  ``[p.95, p.99, p.110]``
* **Position sizing** — ``shares = floor(equity × risk_factor / ATR20)``
  with ``risk_factor = 0.001`` (10 bps daily impact target). ``[p.88, p.98]``
* **Rebalance cadence** — weekly, arbitrary weekday (Clenow chooses
  Wednesday and notes the day is not magical). ``[p.98-99]``

Anti-patterns — never
---------------------
* Never rank by "% above 200d MA" alone — ignores volatility, rewards jumps.
  ``[p.68]``
* Never use trailing stops. ``[p.94, p.96]``
* Never sell because the index is in a bear regime — only stop buying.
  ``[p.94-95]``
* Never optimize the ranking constants; pick a concept, not a magical number.
  ``[p.219-220]``

Ranking score formula
---------------------
Given closes :math:`P_t` for :math:`t=0..N-1` (N = ``lookback_regression``):

    let :math:`m` = slope of the linear regression of :math:`\\ln P_t` vs :math:`t`
    let :math:`R^2` = coefficient of determination of that regression
    AnnualizedSlope = :math:`(e^m)^{250} - 1`   (250-trading-day year, Clenow p.72)
    AdjustedSlope   = AnnualizedSlope × :math:`R^2`

ATR20 uses the standard True Range (:math:`TR_t = \\max(H_t-L_t, |H_t-C_{t-1}|,
|L_t-C_{t-1}|)`, Clenow p.88) and a simple 20-bar mean. Clenow's book uses a
simple moving average of TR (not Wilder smoothing).
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.base import StrategyBase

log = logging.getLogger(__name__)

__all__ = ["ClenowMomentumStrategy", "adjusted_slope", "atr", "max_gap"]


# ---------------------------------------------------------------------------
# Math helpers (pure functions)
# ---------------------------------------------------------------------------


def adjusted_slope(
    prices: pd.Series, lookback: int = 90
) -> tuple[float, float]:
    """Return ``(annualized_slope, r_squared)`` over the last ``lookback`` prices.

    Regresses ``ln(prices)`` on a 0..N-1 time index. The slope is compounded
    over 250 trading days for annualization (Clenow p.72). Raises ``ValueError``
    when ``len(prices) < lookback``.
    """
    if len(prices) < lookback:
        raise ValueError(
            f"adjusted_slope needs lookback={lookback} bars, got {len(prices)}"
        )

    tail = prices.iloc[-lookback:]
    log_p = np.log(tail.to_numpy(dtype=float))
    t = np.arange(lookback, dtype=float)

    t_mean = t.mean()
    lp_mean = log_p.mean()
    var_t = ((t - t_mean) ** 2).sum()
    cov = ((t - t_mean) * (log_p - lp_mean)).sum()
    m = cov / var_t
    intercept = lp_mean - m * t_mean

    pred = m * t + intercept
    sse = ((log_p - pred) ** 2).sum()
    sst = ((log_p - lp_mean) ** 2).sum()
    r2 = 1.0 - sse / sst if sst > 0 else 0.0

    ann_slope = math.exp(m) ** 250 - 1.0
    return float(ann_slope), float(r2)


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    lookback: int = 20,
) -> float:
    """Simple-mean ATR over the last ``lookback`` bars.

    TR formula per Clenow p.88: ``max(H-L, |H-C_prev|, |L-C_prev|)``. The first
    bar's TR is just ``H-L`` (no prior close). Uses an arithmetic mean — not
    Wilder's smoothing — to match the book.
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1, skipna=True)
    tail = tr.iloc[-lookback:]
    if tail.empty:
        return float("nan")
    return float(tail.mean())


def max_gap(close: pd.Series, lookback: int = 90) -> float:
    """Largest absolute close-to-close return in the last ``lookback`` bars.

    Clenow's "single-day move" filter at p.82. Returns 0.0 on a flat series;
    NaN-safe over the tail.
    """
    returns = close.pct_change().abs()
    tail = returns.iloc[-lookback:]
    if tail.empty:
        return 0.0
    value = tail.max(skipna=True)
    return 0.0 if pd.isna(value) else float(value)


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@dataclass
class ClenowMomentumStrategy(StrategyBase):
    """Weekly Wednesday rebalance on a point-in-time SPX universe.

    Construction
    ------------
    ``data``
        OHLCV frames per symbol (indexed by tz-naive ``DatetimeIndex``, columns
        ``open/high/low/close/volume``). Must include ``index_symbol``.
    ``constituents_provider``
        Callable ``(date) -> set[str]`` returning the tradable universe on
        that date. Production: ``WikipediaSPX.constituents_on``. Tests:
        a lambda returning a fixed set.
    ``index_symbol``
        Market-index ticker (default ``"^GSPC"``). Drives the regime filter.

    Parameters (Clenow defaults, explicitly NOT optimized — p.219-220)
    ------------------------------------------------------------------
    ``rebalance_weekday``  default 2 (Wednesday). Arbitrary per p.98-99.
    ``lookback_regression``  90 trading days (p.73, p.98).
    ``lookback_trend``       100 trading days for per-stock MA (p.81, p.98).
    ``lookback_index_trend`` 200 trading days for index MA (p.66, p.98).
    ``lookback_atr``         20 trading days (p.88).
    ``lookback_gap``         90 trading days (p.82).
    ``gap_threshold``        0.15 (p.82, p.98).
    ``top_pct``              0.20 (p.95, p.99, p.110).
    ``risk_factor``          0.001 = 10 bps (p.88, p.98).
    """

    data: dict[str, pd.DataFrame]
    constituents_provider: Callable[[date], set[str]]
    index_symbol: str = "^GSPC"
    rebalance_weekday: int = 2
    lookback_regression: int = 90
    lookback_trend: int = 100
    lookback_index_trend: int = 200
    lookback_atr: int = 20
    lookback_gap: int = 90
    gap_threshold: float = 0.15
    top_pct: float = 0.20
    risk_factor: float = 0.001
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.clenow"),
        repr=False,
    )

    def __post_init__(self) -> None:
        """Rescale OHLC to the total-return (adj_close) base once at construction.

        Splits and dividends would otherwise fire spurious "gap > 15%"
        disqualifications (p.82, p.98) and distort the 90-day slope
        regression. ``adjust_ohlc`` is a no-op when adj_close is absent
        or equal to close, so synthetic fixtures keep working unchanged.
        """
        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}

    # -- rebalance dispatch --------------------------------------------------

    def should_rebalance(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> bool:
        return ts.weekday() == self.rebalance_weekday

    def on_rebalance(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        universe = set(self.constituents_provider(ts.date()))

        ranking, qualified = self._compute_ranking(ts, universe)
        rank_of = {sym: i for i, (sym, _) in enumerate(ranking)}
        max_rank = max(1, int(self.top_pct * len(universe))) if universe else 0

        orders: list[Order] = []
        orders.extend(
            self._sell_orders(ts, bars, portfolio, universe, rank_of, max_rank)
        )

        if self._regime_on(ts):
            orders.extend(
                self._buy_orders(
                    ts, bars, portfolio, ranking, qualified, max_rank, orders
                )
            )
        return orders

    # -- internals -----------------------------------------------------------

    def _history(self, symbol: str, ts: pd.Timestamp) -> pd.DataFrame | None:
        df = self.data.get(symbol)
        if df is None:
            return None
        hist = df.loc[:ts]
        return hist if not hist.empty else None

    def _compute_ranking(
        self, ts: pd.Timestamp, universe: set[str]
    ) -> tuple[list[tuple[str, float]], dict[str, bool]]:
        """Return (ranking sorted by adjusted_slope desc, qualified-for-buy map)."""
        min_required = max(
            self.lookback_regression,
            self.lookback_trend,
            self.lookback_gap,
        )
        ranking: list[tuple[str, float]] = []
        qualified: dict[str, bool] = {}

        for sym in universe:
            hist = self._history(sym, ts)
            if hist is None or len(hist) < min_required:
                continue
            try:
                ann_slope, r2 = adjusted_slope(
                    hist["close"], self.lookback_regression
                )
            except (ValueError, FloatingPointError):
                continue
            if not math.isfinite(ann_slope) or not math.isfinite(r2):
                continue

            score = ann_slope * r2
            ranking.append((sym, score))

            current_close = float(hist["close"].iloc[-1])
            ma_trend = float(
                hist["close"].iloc[-self.lookback_trend:].mean()
            )
            gap = max_gap(hist["close"], self.lookback_gap)
            qualified[sym] = (
                current_close > ma_trend and gap <= self.gap_threshold
            )

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking, qualified

    def _regime_on(self, ts: pd.Timestamp) -> bool:
        """SPX close > SPX 200-day MA at ``ts``. True when history is too short."""
        hist = self._history(self.index_symbol, ts)
        if hist is None or len(hist) < self.lookback_index_trend:
            return True
        ma = float(hist["close"].iloc[-self.lookback_index_trend:].mean())
        current = float(hist["close"].iloc[-1])
        return current > ma

    def _sell_orders(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        universe: set[str],
        rank_of: dict[str, int],
        max_rank: int,
    ) -> list[Order]:
        orders: list[Order] = []
        for symbol, pos in list(portfolio.positions.items()):
            if pos.side != "long":
                continue  # Clenow is long-only
            if symbol not in bars:
                # Symbol has no bar today — delisted or data gap. Can't submit
                # a market order without a fill price; skip and retry next
                # rebalance. Permanently-delisted positions will stay open
                # at their last mark until data returns (Clenow universe is
                # point-in-time, so re-entry into SPX revives the bars).
                continue
            if self._should_sell(ts, symbol, universe, rank_of, max_rank):
                orders.append(Order(symbol=symbol, side="sell", volume=pos.volume))
        return orders

    def _should_sell(
        self,
        ts: pd.Timestamp,
        symbol: str,
        universe: set[str],
        rank_of: dict[str, int],
        max_rank: int,
    ) -> bool:
        if symbol not in universe:
            return True  # left the index — sell ([p.99])
        hist = self._history(symbol, ts)
        if hist is None or len(hist) < self.lookback_trend:
            return True  # no data to evaluate — exit defensively
        if symbol not in rank_of:
            return True
        if rank_of[symbol] >= max_rank:
            return True  # dropped out of top 20% ([p.99, p.110])
        current_close = float(hist["close"].iloc[-1])
        ma_trend = float(hist["close"].iloc[-self.lookback_trend:].mean())
        if current_close < ma_trend:
            return True  # below 100d MA ([p.99])
        if max_gap(hist["close"], self.lookback_gap) > self.gap_threshold:
            return True  # had a >15% single-day move ([p.99])
        return False

    def _buy_orders(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        ranking: list[tuple[str, float]],
        qualified: dict[str, bool],
        max_rank: int,
        already_issued: list[Order],
    ) -> list[Order]:
        equity = portfolio.equity
        available_cash = portfolio.cash
        to_be_sold: set[str] = set()

        # Runner applies orders in the list order, so cash from sells will be
        # credited before buys execute. Pre-compute sell proceeds optimistically
        # at bar.close (ignores spread/slippage — close enough for a break
        # decision, Clenow "until cash runs out" at p.99).
        for order in already_issued:
            if order.side == "sell" and order.symbol in bars:
                available_cash += order.volume * bars[order.symbol].close
                to_be_sold.add(order.symbol)

        already_long = {
            sym for sym, pos in portfolio.positions.items()
            if pos.side == "long" and sym not in to_be_sold
        }

        orders: list[Order] = []
        for symbol, _score in ranking[:max_rank]:
            if symbol in already_long:
                continue
            if not qualified.get(symbol, False):
                continue
            if symbol not in bars:
                continue

            hist = self._history(symbol, ts)
            if hist is None or len(hist) < self.lookback_atr + 1:
                continue
            atr_value = atr(
                hist["high"], hist["low"], hist["close"], self.lookback_atr
            )
            if not math.isfinite(atr_value) or atr_value <= 0:
                continue

            shares = int((equity * self.risk_factor) / atr_value)
            if shares <= 0:
                continue

            current_close = bars[symbol].close
            estimated_cost = shares * current_close
            if estimated_cost > available_cash:
                break  # Clenow: stop when cash runs out ([p.99])

            orders.append(Order(symbol=symbol, side="buy", volume=shares))
            available_cash -= estimated_cost

        return orders
