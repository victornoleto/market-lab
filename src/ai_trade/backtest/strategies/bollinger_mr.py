"""Bollinger Band Mean-Reversion strategy (intraday / short-hold).

Simple mean-reversion: buy when price dips below the lower Bollinger
band, exit when it reverts to the moving average. Designed for 1h bars
on liquid ETFs (SPY, QQQ). Targets median hold ≤ 24 bars (1 day on 1h).

**Citations:**

- Entry rule (buy below lower band, exit at MA): ``[algo_trading_chan,
  p.28-30, ch.2]`` — "a stock that has deviated more than X standard
  deviations from its mean will revert". Long-only variant for ETFs.
- Bollinger band construction (MA ± k·σ): ``[machine_trading, p.204-205,
  ch.7]`` — standard 20-bar MA with 1.5–2.0σ bands for short-term
  scalping.
- Hard time-stop to cap holding period: ``[machine_trading, p.126, ch.4]``
  — "exit after N bars if not profitable" for intraday risk control.
- Optional SMA regime filter: ``[stocks_on_the_move, p.110]`` — only
  enter when close > SMA(regime_sma) to avoid bear-market entries.

Pipeline (per bar)
------------------

1. Pre-compute MA(window) and rolling σ(window) on adjusted close.
2. Lower band = MA - mult × σ.
3. **Entry (long only):** close crosses below lower band.
4. **Exit:** close crosses above MA, OR hard time-stop (max_hold bars),
   OR stop-loss (fixed %).
5. No short entries — mean-reversion on equity indices is asymmetric
   (oversold bounces are more reliable than overbought shorts)
   ``[algo_trading_chan, p.30, ch.2]``.

Position sizing
---------------

Fraction of current equity at entry: ``notional = equity · risk_pct``,
``volume = notional / entry_price``.
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
class BollingerMRStrategy:
    """Single-instrument Bollinger mean-reversion (long-only, short-hold)."""

    data: dict[str, pd.DataFrame]
    symbol: str = "SPY"
    window: int = 20
    std_mult: float = 2.0
    stop_pct: float = 0.02
    max_hold: int = 24
    risk_pct_of_equity: float = 0.95
    regime_sma: int = 0  # 0 = disabled; >0 = SMA(N) regime filter [stocks_on_the_move, p.110]

    _indicators: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.bollinger_mr"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if not (0 < self.stop_pct < 1):
            raise ValueError(f"stop_pct must be in (0, 1), got {self.stop_pct}")
        if self.window < 2:
            raise ValueError(f"window must be >= 2, got {self.window}")
        if self.std_mult <= 0:
            raise ValueError(f"std_mult must be > 0, got {self.std_mult}")
        if self.max_hold < 1:
            raise ValueError(f"max_hold must be >= 1, got {self.max_hold}")
        if self.regime_sma < 0:
            raise ValueError(f"regime_sma must be >= 0, got {self.regime_sma}")
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._precompute_indicators(self.symbol)

    def _precompute_indicators(self, symbol: str) -> None:
        close = self.data[symbol]["close"].astype(float)
        ma = close.rolling(window=self.window, min_periods=self.window).mean()
        std = close.rolling(window=self.window, min_periods=self.window).std(ddof=1)
        lower_band = ma - self.std_mult * std

        cols = {"ma": ma, "std": std, "lower_band": lower_band}
        if self.regime_sma > 0:
            cols["regime_ma"] = close.rolling(
                window=self.regime_sma, min_periods=self.regime_sma,
            ).mean()

        self._indicators[symbol] = pd.DataFrame(cols, index=close.index)

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if self.symbol not in bars:
            return []

        bar = bars[self.symbol]
        ts = bar.timestamp
        ind = self._indicators[self.symbol]
        try:
            idx = ind.index.get_loc(ts)
        except KeyError:
            return []

        if idx < self.window:
            return []

        ma_now = float(ind["ma"].iloc[idx])
        lower_now = float(ind["lower_band"].iloc[idx])

        if np.isnan(ma_now) or np.isnan(lower_now):
            return []

        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"bollinger_state_{self.symbol}", {})

        if pos is not None:
            exit_order = self._maybe_exit(pos, bar, idx, state, ma_now)
            if exit_order is not None:
                state.clear()
                return [exit_order]
            return []

        return self._maybe_enter(bar, idx, state, portfolio, lower_now)

    def _maybe_exit(
        self,
        pos,
        bar: Bar,
        idx: int,
        state: dict,
        ma_now: float,
    ) -> Order | None:
        entry_price = pos.avg_entry_price
        entry_idx = state.get("entry_idx", idx)
        bars_held = idx - entry_idx

        # 1. Stop-loss — capital preservation (always first).
        if bar.close <= entry_price * (1 - self.stop_pct):
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        # 2. Mean-reversion target: close crosses above MA.
        if bar.close >= ma_now:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        # 3. Hard time-stop: exit after max_hold bars regardless.
        if bars_held >= self.max_hold:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        return None

    def _maybe_enter(
        self,
        bar: Bar,
        idx: int,
        state: dict,
        portfolio: Portfolio,
        lower_now: float,
    ) -> list[Order]:
        # Regime filter: skip entry if close is below SMA regime filter.
        # [stocks_on_the_move, p.110] — go flat in bear markets.
        if self.regime_sma > 0:
            regime_ma = self._indicators[self.symbol]["regime_ma"].iloc[idx]
            if np.isnan(regime_ma) or bar.close < regime_ma:
                return []

        equity = portfolio.equity
        if equity <= 0:
            return []
        notional = equity * self.risk_pct_of_equity
        if bar.close <= 0:
            return []
        volume = notional / bar.close
        if volume <= 0:
            return []

        # Long entry: close dips below lower Bollinger band.
        if bar.close < lower_now:
            state["entry_idx"] = idx
            return [Order(symbol=self.symbol, side="buy", volume=volume)]

        return []
