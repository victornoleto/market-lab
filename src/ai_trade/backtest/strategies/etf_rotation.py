"""Monthly ETF Rotation Strategy — cross-sectional momentum on small universe.

Ranks a fixed ETF universe by Clenow's adjusted momentum score each month,
allocates 100% equity to the top-ranked ETF. Regime filter: flat when the
index proxy (SPY) is below its 200-day SMA.

Rules (all pre-specified from literature, no tuning):
* Ranking signal: (annualized 90-day exp-regression slope) × R²
  [stocks_on_the_move, p.81, ch.4]
* Regime filter: only invest when index_symbol > SMA(200)
  [stocks_on_the_move, p.66-67, ch.5]; go flat (cash) otherwise
* Rebalancing cadence: first bar of each calendar month
  [stocks_on_the_move, p.98-99, ch.6]
* Top-N ETFs: equal allocation (100%/N each)
  [stocks_on_the_move, p.95, ch.6]
* Per-stock trend filter: ETF must be above its own 100-day SMA
  [stocks_on_the_move, p.81-82, ch.6]

Canonical parameters:
  lookback=90, sma_index=200, sma_stock=100 [stocks_on_the_move, p.81/66/81]

Path B [SWING BROKER]: long-only, no swap, 15% BR capital-gains tax to be
applied to net Sharpe gate at reporting time.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ai_trade.backtest.data.adjust import adjust_ohlc
from ai_trade.backtest.engine.execution import Bar, Order
from ai_trade.backtest.engine.portfolio import Portfolio
from ai_trade.backtest.strategies.base import StrategyBase
from ai_trade.backtest.helpers.momentum import adjusted_slope

log = logging.getLogger(__name__)

__all__ = ["ETFRotationStrategy"]


@dataclass
class ETFRotationStrategy(StrategyBase):
    """Monthly ETF rotation by momentum score.

    Parameters
    ----------
    data:
        Full OHLCV history for all symbols (including warmup). Must contain
        'close' and optionally 'adj_close'. Pre-adjusted via adjust_ohlc.
    symbols:
        ETF universe to rotate through (e.g. ['SPY','QQQ','IWM','GLD','TLT']).
    index_symbol:
        Symbol used for regime filter (must be in data). Typically 'SPY'.
    lookback:
        Regression window for adjusted_slope. [stocks_on_the_move, p.81]
    sma_index_period:
        SMA period for regime filter on index_symbol. [stocks_on_the_move, p.66-67]
    sma_stock_period:
        SMA period for per-ETF trend filter. [stocks_on_the_move, p.81-82]
    """

    data: dict[str, pd.DataFrame]
    symbols: list[str]
    index_symbol: str = "SPY"
    lookback: int = 90
    sma_index_period: int = 200
    sma_stock_period: int = 100
    top_n: int = 1  # [stocks_on_the_move, p.95, ch.6]
    # Vol-sizing: scale position to target_vol/realized_vol [machine_trading, p.126-127]
    vol_sizing: bool = False
    target_vol: float = 0.15  # 15% annual target
    vol_window: int = 20  # trailing days for realized vol estimate

    _adj_data: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _prev_month: int = field(init=False, default=-1)

    def __post_init__(self) -> None:
        missing = [s for s in self.symbols if s not in self.data]
        if missing:
            raise KeyError(f"symbols not in data: {missing}")
        if self.index_symbol not in self.data:
            raise KeyError(f"index_symbol {self.index_symbol!r} not in data")
        self._adj_data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._prev_month = -1

    def should_rebalance(self, ts: pd.Timestamp, bars: dict[str, Bar]) -> bool:
        """Rebalance on the first bar of each calendar month."""
        if ts.month != self._prev_month:
            self._prev_month = ts.month
            return True
        return False

    def on_rebalance(
        self,
        ts: pd.Timestamp,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        orders: list[Order] = []

        # --- Regime filter: flat if index below SMA ---
        idx_close = self._close_up_to(self.index_symbol, ts)
        if idx_close is None or len(idx_close) < self.sma_index_period:
            return []  # not enough history yet
        in_regime = float(idx_close.iloc[-1]) > float(
            idx_close.iloc[-self.sma_index_period :].mean()
        )

        if not in_regime:
            orders.extend(self._exit_all(portfolio))
            return orders

        # --- Score each ETF ---
        scores: dict[str, float] = {}
        for sym in self.symbols:
            if sym not in bars:
                continue
            closes = self._close_up_to(sym, ts)
            if closes is None or len(closes) < max(self.lookback, self.sma_stock_period):
                continue
            # Per-stock trend filter: must be above own SMA
            sma_val = float(closes.iloc[-self.sma_stock_period :].mean())
            if float(closes.iloc[-1]) < sma_val:
                continue
            slope, r2 = adjusted_slope(closes, self.lookback)
            if math.isnan(slope) or math.isnan(r2):
                continue
            scores[sym] = slope * r2

        if not scores:
            orders.extend(self._exit_all(portfolio))
            return orders

        # Pick top-N by score; equal-weight allocation [stocks_on_the_move, p.95]
        targets = sorted(scores, key=scores.__getitem__, reverse=True)[: self.top_n]
        alloc_per = 1.0 / len(targets)

        # --- Exit positions not in target set ---
        for sym in list(portfolio.positions):
            if sym not in targets:
                pos = portfolio.positions[sym]
                orders.append(Order(
                    symbol=sym,
                    side="sell" if pos.side == "long" else "buy",
                    volume=pos.volume,
                ))

        # --- Enter/rebalance each target ---
        for target in targets:
            if target not in portfolio.positions:
                bar = bars[target]
                if bar.close > 0 and portfolio.equity > 0:
                    scale = self._vol_scale(target, ts) if self.vol_sizing else 1.0
                    volume = portfolio.equity * alloc_per * scale / bar.close
                    if volume > 0:
                        orders.append(Order(symbol=target, side="buy", volume=volume))

        return orders

    def _vol_scale(self, sym: str, ts: pd.Timestamp) -> float:
        """Return position scale factor: target_vol / realized_vol, capped at 1.0."""
        closes = self._close_up_to(sym, ts)
        if closes is None or len(closes) < self.vol_window + 1:
            return 1.0
        rets = closes.iloc[-(self.vol_window + 1):].pct_change().dropna()
        vol_annual = float(rets.std(ddof=1) * np.sqrt(252))
        if vol_annual <= 0:
            return 1.0
        return min(1.0, self.target_vol / vol_annual)

    def _close_up_to(self, sym: str, ts: pd.Timestamp) -> pd.Series | None:
        df = self._adj_data.get(sym)
        if df is None or "close" not in df.columns:
            return None
        closes = df["close"].loc[:ts]
        return closes if not closes.empty else None

    def _exit_all(self, portfolio: Portfolio) -> list[Order]:
        orders = []
        for sym, pos in list(portfolio.positions.items()):
            orders.append(Order(
                symbol=sym,
                side="sell" if pos.side == "long" else "buy",
                volume=pos.volume,
            ))
        return orders
