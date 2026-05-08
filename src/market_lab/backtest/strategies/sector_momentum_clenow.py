"""Clenow cross-sectional momentum applied to US SPDR sector ETFs.

Book canonical spec `[stocks_on_the_move]`:

* Adjusted slope ranking = (annualized 90d exponential regression slope) × R²
  `[p.76, 82]`
* Disqualifiers: close < 100d SMA `[p.81]`, |gap| > 15% in last 90d `[p.82]`
* Regime filter: buy only while regime_symbol close > 200d SMA `[p.66-67, 98-99]`
* Sizing: shares = floor(equity × risk_factor / ATR20), risk_factor = 10 bps
  `[p.88-89]`
* Rebalance: weekly (any weekday — Clenow picks Wednesday explicitly because
  the day doesn't matter `[p.98-99]`)
* Exit: rank falls outside top-K or trend/gap fail — **no stop-loss** `[p.94-96]`

Transport adaptation (iter 002):

* Universe is 11 SPDR sectors instead of ~500 S&P 500 stocks. Top-K parameter
  must respect the much smaller universe (top-20% on 500 stocks = 100 names;
  top-20% on 11 sectors = 2-3 — tested as a user-facing parameter, not as a
  sweep).
* `buy_leverage` allows unlevered (1.0) or gearing (e.g. 2.0). Clenow's
  original is 1.0 ("cash is positive — don't use leverage" implicit).
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.base import StrategyBase

__all__ = [
    "SectorMomentumClenow",
    "adjusted_slope",
    "atr",
    "disqualify_gap",
    "disqualify_trend",
    "position_size_shares",
    "regime_allows_new_buys",
    "top_k_ranks",
]


# ---------------------------------------------------------------------------
# Pure primitives (unit-tested; used inside the strategy and in G7 ref impl)
# ---------------------------------------------------------------------------


def adjusted_slope(prices: pd.Series, lookback: int = 90) -> tuple[float, float]:
    """Annualized exponential regression slope × R² over last ``lookback`` bars.

    Returns ``(annualized_slope, r_squared)``. Caller multiplies to get the
    Clenow ranking score.

    Formula `[stocks_on_the_move, p.70-77]`:

    * ``m = linear_regression_slope(ln(price), t=0..N-1)``
    * ``annualized = (e^m)^250 - 1``
    * ``r² = RSQ(ln(price), t)``
    """
    if len(prices) < lookback:
        raise ValueError(
            f"need at least {lookback} bars for adjusted_slope, got {len(prices)}"
        )
    y = np.log(prices.iloc[-lookback:].to_numpy())
    x = np.arange(lookback, dtype=float)
    x_mean = x.mean()
    y_mean = y.mean()
    cov = float(((x - x_mean) * (y - y_mean)).sum())
    var_x = float(((x - x_mean) ** 2).sum())
    var_y = float(((y - y_mean) ** 2).sum())
    slope_m = cov / var_x if var_x != 0.0 else 0.0
    annualized = math.exp(slope_m) ** 250 - 1
    r2 = (cov**2) / (var_x * var_y) if (var_x > 0 and var_y > 0) else 0.0
    return annualized, r2


def atr(ohlc: pd.DataFrame, lookback: int = 20) -> float:
    """Average True Range over last ``lookback`` bars `[stocks_on_the_move, p.88]`.

    ``TR_t = max(H_t - L_t, |H_t - C_{t-1}|, |L_t - C_{t-1}|)``.
    Requires columns ``high, low, close`` in ``ohlc``. Returns NaN when the
    window can't be filled (caller is expected to guard).
    """
    if len(ohlc) < lookback + 1:
        return float("nan")
    window = ohlc.iloc[-(lookback + 1) :]
    high = window["high"].to_numpy()
    low = window["low"].to_numpy()
    close = window["close"].to_numpy()
    prev_close = close[:-1]
    tr = np.maximum.reduce([
        high[1:] - low[1:],
        np.abs(high[1:] - prev_close),
        np.abs(low[1:] - prev_close),
    ])
    return float(tr.mean())


def position_size_shares(
    equity: float, atr20: float, risk_factor: float = 0.001
) -> int:
    """Risk-parity sizing `[stocks_on_the_move, p.88-89]`.

    ``shares = floor(equity × risk_factor / ATR20)``.

    Returns 0 if ``atr20`` is 0 or NaN (degenerate, no movement).
    """
    if atr20 is None or not math.isfinite(atr20) or atr20 <= 0.0:
        return 0
    target = equity * risk_factor / atr20
    if not math.isfinite(target) or target <= 0.0:
        return 0
    return int(math.floor(target))


def disqualify_gap(
    prices: pd.Series, lookback: int = 90, threshold: float = 0.15
) -> bool:
    """True iff any |daily return| > threshold in last ``lookback`` bars
    `[stocks_on_the_move, p.82]`."""
    if len(prices) < 2:
        return False
    recent = prices.iloc[-lookback:]
    rets = recent.pct_change().dropna().abs()
    if rets.empty:
        return False
    return bool(rets.max() > threshold)


def disqualify_trend(prices: pd.Series, lookback: int = 100) -> bool:
    """True iff last close < SMA(lookback) `[stocks_on_the_move, p.81]`."""
    if len(prices) < lookback:
        return True  # not enough history → conservative reject
    sma = float(prices.iloc[-lookback:].mean())
    return float(prices.iloc[-1]) < sma


def regime_allows_new_buys(prices: pd.Series, lookback: int = 200) -> bool:
    """True iff index close > SMA(lookback) — i.e., regime ON
    `[stocks_on_the_move, p.66-67, 98-99]`."""
    if len(prices) < lookback:
        return False
    sma = float(prices.iloc[-lookback:].mean())
    return float(prices.iloc[-1]) > sma


def top_k_ranks(
    scores: dict[str, float],
    k: int,
    disqualified: set[str] | None = None,
) -> list[str]:
    """Return the top-K symbols by score, descending, skipping NaN and
    disqualified. Ties broken alphabetically for determinism."""
    disq = disqualified or set()
    eligible = [
        (sym, sc)
        for sym, sc in scores.items()
        if sym not in disq and isinstance(sc, float) and math.isfinite(sc)
    ]
    eligible.sort(key=lambda x: (-x[1], x[0]))
    return [sym for sym, _ in eligible[:k]]


# ---------------------------------------------------------------------------
# Strategy
# ---------------------------------------------------------------------------


@dataclass
class SectorMomentumClenow(StrategyBase):
    """Top-K sector momentum portfolio with weekly rebalance + regime gate.

    Parameters
    ----------
    universe
        Tradable symbols (e.g. SPDR sectors). The regime_symbol (e.g. "SPY")
        MUST be provided in the Runner's data dict but is NOT traded.
    regime_symbol
        Index ticker for the 200d regime filter.
    top_k
        Number of sectors to hold at any time (e.g. 3 or 5 of 11).
    buy_leverage
        Notional gearing on entries. 1.0 = unlevered (Clenow canonical).
    lookback_slope, lookback_trend, lookback_regime, lookback_atr
        Canonical Clenow defaults — NOT tuned by grid.
    gap_threshold
        Max |daily return| in last 90d to accept as non-disqualified `[p.82]`.
    risk_factor
        Per-position daily impact budget `[p.88-89]`. 10 bps canonical.
    rebalance_weekday
        0=Mon..4=Fri. Wednesday (=2) in Clenow; explicitly arbitrary `[p.98-99]`.
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
    lookback_atr: int = 20
    gap_threshold: float = 0.15
    risk_factor: float = 0.001
    rebalance_weekday: int = 2  # Wednesday
    position_rebalance_every_n: int = 2

    # Runtime state — populated during run. Rolling OHLC buffers (deques) per
    # symbol; capped at max(lookback_*) to keep memory bounded and O(1) append.
    _open_buf: dict[str, "deque[float]"] = field(default_factory=dict, init=False)
    _high_buf: dict[str, "deque[float]"] = field(default_factory=dict, init=False)
    _low_buf: dict[str, "deque[float]"] = field(default_factory=dict, init=False)
    _close_buf: dict[str, "deque[float]"] = field(default_factory=dict, init=False)
    _last_rebalance_date: pd.Timestamp | None = field(default=None, init=False)
    _rebalance_counter: int = field(default=0, init=False)
    _max_lookback: int = field(default=0, init=False)

    # ------------------------------------------------------------------
    # StrategyBase interface
    # ------------------------------------------------------------------

    def should_rebalance(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> bool:
        # Always update price history so that when the rebalance fires we
        # have fresh windows (includes today's close).
        self._append_history(ts, bars)
        if ts.weekday() != self.rebalance_weekday:
            return False
        # Only rebalance once per week (avoid re-firing on Wednesday holidays
        # that shift to Thursday, etc — conservative).
        if self._last_rebalance_date is not None:
            if (ts - self._last_rebalance_date).days < 5:
                return False
        # Need enough history for ranking on at least some symbols.
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

        # 1) Compute adjusted-slope scores + disqualifications.
        scores: dict[str, float] = {}
        disq: set[str] = set()
        atrs: dict[str, float] = {}
        for sym in self.universe:
            close_buf = self._close_buf.get(sym)
            if close_buf is None or len(close_buf) < max(self.lookback_slope, self.lookback_trend):
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
            if disqualify_gap(close, lookback=self.lookback_slope, threshold=self.gap_threshold):
                disq.add(sym)
            scores[sym] = slope * r2
            atrs[sym] = self._atr_from_bufs(sym, lookback=self.lookback_atr)

        top = top_k_ranks(scores, k=self.top_k, disqualified=disq)
        regime_close = pd.Series(list(self._close_buf[self.regime_symbol]))
        regime_on = regime_allows_new_buys(regime_close, lookback=self.lookback_regime)

        orders: list[Order] = []

        # 2) Sell leg — anything held that drops out of top-K or gets
        # disqualified. Clenow: "Do not sell just because the index fell
        # below 200d MA" `[p.94-95]` — so regime off does NOT force exits.
        held = list(portfolio.positions.keys())
        for sym in held:
            if sym not in self.universe:
                continue  # don't touch non-strategy positions
            pos = portfolio.positions[sym]
            should_exit = (
                sym not in top
                or sym in disq
                or sym not in bars  # no fresh price this bar
            )
            if should_exit and sym in bars:
                orders.append(Order(symbol=sym, side="sell", volume=pos.volume))

        # 3) Buy leg — only if regime ON. Top-K not yet held → enter.
        if regime_on:
            # Use equity net of pending sells for sizing. Runner executes sells
            # before buys within the same rebalance call because sells come
            # first in the orders list.
            equity_for_sizing = portfolio.equity * self.buy_leverage
            for sym in top:
                if sym in portfolio.positions and sym not in [
                    o.symbol for o in orders if o.side == "sell"
                ]:
                    continue  # already held, not exiting
                if sym not in bars:
                    continue
                atr20 = atrs.get(sym, float("nan"))
                shares = position_size_shares(
                    equity=equity_for_sizing,
                    atr20=atr20,
                    risk_factor=self.risk_factor,
                )
                if shares > 0:
                    orders.append(Order(symbol=sym, side="buy", volume=float(shares)))

        # 4) Periodic position rebalance `[p.99, p.108]`: every N-th rebalance,
        # resize existing positions to the current ATR target. Only applies to
        # positions that will survive the sell leg.
        if self._rebalance_counter % self.position_rebalance_every_n == 0:
            survivors = [
                s for s in portfolio.positions
                if s in top and s not in disq and s in bars
            ]
            for sym in survivors:
                atr20 = atrs.get(sym, float("nan"))
                target = position_size_shares(
                    equity=portfolio.equity * self.buy_leverage,
                    atr20=atr20,
                    risk_factor=self.risk_factor,
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

    def _append_history(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> None:
        """Append today's OHLC to the per-symbol rolling deque (O(1))."""
        if self._max_lookback == 0:
            self._max_lookback = max(
                self.lookback_slope,
                self.lookback_trend,
                self.lookback_atr + 1,
                self.lookback_regime,
            )
        cap = self._max_lookback
        for sym, bar in bars.items():
            if sym not in self._close_buf:
                self._open_buf[sym] = deque(maxlen=cap)
                self._high_buf[sym] = deque(maxlen=cap)
                self._low_buf[sym] = deque(maxlen=cap)
                self._close_buf[sym] = deque(maxlen=cap)
            self._open_buf[sym].append(bar.open)
            self._high_buf[sym].append(bar.high)
            self._low_buf[sym].append(bar.low)
            self._close_buf[sym].append(bar.close)

    def _atr_from_bufs(self, sym: str, lookback: int) -> float:
        """Compute ATR from the symbol's rolling deques (no DataFrame alloc)."""
        high = np.asarray(self._high_buf[sym], dtype=float)
        low = np.asarray(self._low_buf[sym], dtype=float)
        close = np.asarray(self._close_buf[sym], dtype=float)
        if len(close) < lookback + 1:
            return float("nan")
        hi = high[-lookback:]
        lo = low[-lookback:]
        cl = close[-lookback:]
        prev_cl = close[-(lookback + 1) : -1]
        tr = np.maximum.reduce([
            hi - lo,
            np.abs(hi - prev_cl),
            np.abs(lo - prev_cl),
        ])
        return float(tr.mean())
