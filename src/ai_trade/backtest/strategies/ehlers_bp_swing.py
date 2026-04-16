"""Ehlers Band-Pass Swing Trader.

Long-on-oversold / short-on-overbought swing strategy built on Ehlers's
DSP primitives. Every rule below is cited verbatim from [cycle_analytics,
ch.17, p.220-226].

Pipeline (per bar)
------------------

1. **Preprocessing** — ``close → roofing_filter(hp_period, lp_period)``
   yields a zero-mean, Spectral-Dilation-corrected stream ``roofed``.
   Mandatory per [p.88-89, ch.7] — without it, conventional oscillators
   misfire during trending markets.

2. **Dominant Cycle Period** — ``dcp = dominant_cycle_period(roofed)``
   (Homodyne Discriminator [rocket_science, ch.8, p.82-83]), clamped to
   ``[6, 50]`` bars per [cycle_analytics, p.82-83, ch.7].

3. **Band-pass** — ``bp = band_pass(roofed, dcp, pct_of_dcp)``. Tuned to
   ``pct · DCP`` (default 0.90) for ~60° of phase lead
   [p.152-153, ch.11].

4. **AGC-normalize** to ``osc ∈ [-1, +1]``. Decay factor 0.991 per
   [p.54-55, ch.5].

5. **Entry (anticipatory)** — [p.220-221, ch.17]:

   * Long when ``osc`` crosses **below** ``lower_threshold`` (−0.7).
   * Short when ``osc`` crosses **above** ``upper_threshold`` (+0.7).

   Buys into oversold / sells into overbought. Recovers ~4 bars of lag
   vs. the confirmation rule (cross back out).

6. **Exit — safety valve** [p.224-225, ch.17]:

   * Trend break: ``close < SuperSmoother(close, lp_period)`` (long) or
     ``close > SuperSmoother(close, lp_period)`` (short).
   * Time-stop: if held ≥ ``0.5 · DCP_at_entry`` bars and P&L ≤ 0, exit.

7. **Stop-loss** [p.225-226, ch.17]: fixed ``stop_pct`` (default 5%) as
   a guard against extreme losses. Not part of the signal — just capital
   preservation. Takes precedence over the safety valve.

Position sizing
---------------

Fraction of current equity at entry: ``notional = equity · risk_pct``,
``volume = notional / entry_price``. A float volume is allowed (the
engine supports fractional shares / CFD micro-lots).

State
-----

Indicators are pre-computed once on the full history in
``__post_init__`` — this is a single-instrument strategy, so
``O(len(data))`` work once, then ``O(1)`` lookups per bar. Per-trade
state (entry index, DCP at entry) lives in the Runner's ``context`` dict
under ``f"ehlers_state_{symbol}"``.
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
from ai_trade.backtest.indicators.ehlers_bp import band_pass
from ai_trade.backtest.indicators.ehlers_dcp import dominant_cycle_period
from ai_trade.backtest.indicators.ehlers_roofing import roofing_filter
from ai_trade.backtest.indicators.ehlers_ss import super_smoother


def _agc_normalize(series: pd.Series, decay: float = 0.991) -> pd.Series:
    """Automatic Gain Control: fast-attack / slow-decay peak normaliser.

    Produces output bounded in ``[-1, +1]``. Decay ``K = 0.991`` yields
    ~1.5 dB gain slope across the 10–48 bar trading band
    [cycle_analytics, p.54-55, ch.5].
    """
    values = series.to_numpy(dtype=float, copy=True)
    n = len(values)
    peak = np.zeros(n)
    for t in range(1, n):
        peak[t] = max(abs(values[t]), decay * peak[t - 1])
    safe = np.where(peak > 1e-9, peak, 1.0)
    return pd.Series(values / safe, index=series.index, name=series.name)


@dataclass
class EhlersBPSwingStrategy:
    """Single-instrument Ehlers Band-Pass Swing Trader."""

    data: dict[str, pd.DataFrame]
    symbol: str = "^GSPC"
    hp_period: int = 48
    lp_period: int = 10
    pct_of_dcp: float = 0.90
    stop_pct: float = 0.05
    upper_threshold: float = 0.70
    lower_threshold: float = -0.70
    agc_decay: float = 0.991
    risk_pct_of_equity: float = 0.95  # near-full deployment (swing trader)
    period_min: int = 6
    period_max: int = 50
    # Regime filter: 0 = disabled. When > 0, only enter long above SMA(N),
    # only enter short below SMA(N). [algo_trading_chan, p.28, ch.2]
    regime_sma_period: int = 0
    # Hard time-stop: exit after N bars if still in position (0 = disabled).
    # 5 bars on daily = 1 trading week. [algo_trading_chan, p.28, ch.2]
    max_hold_bars: int = 0

    _indicators: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.ehlers_bp_swing"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if not (0 < self.stop_pct < 1):
            raise ValueError(f"stop_pct must be in (0, 1), got {self.stop_pct}")
        if self.lower_threshold >= self.upper_threshold:
            raise ValueError(
                f"lower_threshold ({self.lower_threshold}) must be strictly "
                f"less than upper_threshold ({self.upper_threshold})"
            )
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")

        # Rescale OHLC to the total-return (adj_close) base before
        # precomputing the roofing filter / DCP / band-pass. Splits and
        # dividends otherwise inject discontinuities the Roofing Filter
        # cannot fully absorb. No-op when adj_close is absent (synthetic
        # fixtures) or identical to close.
        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}

        self._precompute_indicators(self.symbol)

    def _precompute_indicators(self, symbol: str) -> None:
        close = self.data[symbol]["close"]
        roofed = roofing_filter(close, self.hp_period, self.lp_period)
        dcp = dominant_cycle_period(
            roofed, period_min=self.period_min, period_max=self.period_max
        )
        bp = band_pass(roofed, dcp, pct_of_dcp=self.pct_of_dcp)
        osc = _agc_normalize(bp, decay=self.agc_decay)
        trend = super_smoother(close, self.lp_period)

        ind: dict[str, pd.Series] = {
            "smooth": roofed,
            "dcp": dcp,
            "bp": bp,
            "osc": osc,
            "trend": trend,
        }

        if self.regime_sma_period > 0:
            ind["regime_sma"] = close.rolling(self.regime_sma_period).mean()

        self._indicators[symbol] = pd.DataFrame(ind)

    # -- main dispatch -------------------------------------------------------

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

        if idx < 1:
            return []  # need previous bar to detect a threshold crossing

        osc_now = float(ind["osc"].iloc[idx])
        osc_prev = float(ind["osc"].iloc[idx - 1])
        trend_now = float(ind["trend"].iloc[idx])
        dcp_now = float(ind["dcp"].iloc[idx])

        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"ehlers_state_{self.symbol}", {})

        if pos is not None:
            exit_order = self._maybe_exit(
                pos, bar, idx, state, trend_now
            )
            if exit_order is not None:
                state.clear()
                return [exit_order]
            return []

        return self._maybe_enter(bar, idx, state, portfolio, osc_now, osc_prev, dcp_now)

    # -- exit ---------------------------------------------------------------

    def _maybe_exit(
        self,
        pos,
        bar: Bar,
        idx: int,
        state: dict,
        trend_now: float,
    ) -> Order | None:
        side = pos.side
        entry_price = pos.avg_entry_price
        entry_idx = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        dcp_at_entry = state.get("dcp_at_entry", self.period_min)
        half_dcp = max(1, int(0.5 * dcp_at_entry))
        pnl_per_unit = (
            bar.close - entry_price if side == "long" else entry_price - bar.close
        )

        # 1. Stop-loss (always first — capital preservation).
        if side == "long" and bar.close <= entry_price * (1 - self.stop_pct):
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)
        if side == "short" and bar.close >= entry_price * (1 + self.stop_pct):
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)

        # 2. Safety-valve trend break.
        if side == "long" and bar.close < trend_now:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)
        if side == "short" and bar.close > trend_now:
            return Order(symbol=self.symbol, side="buy", volume=pos.volume)

        # 3. Hard time-stop: exit after max_hold_bars (0 = disabled).
        if self.max_hold_bars > 0 and bars_held >= self.max_hold_bars:
            close_side = "sell" if side == "long" else "buy"
            return Order(symbol=self.symbol, side=close_side, volume=pos.volume)

        # 4. Time-stop: non-profitable past half the dominant cycle.
        if bars_held >= half_dcp and pnl_per_unit <= 0:
            close_side = "sell" if side == "long" else "buy"
            return Order(symbol=self.symbol, side=close_side, volume=pos.volume)

        return None

    # -- entry --------------------------------------------------------------

    def _maybe_enter(
        self,
        bar: Bar,
        idx: int,
        state: dict,
        portfolio: Portfolio,
        osc_now: float,
        osc_prev: float,
        dcp_now: float,
    ) -> list[Order]:
        if math.isnan(osc_now) or math.isnan(osc_prev):
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

        # Regime filter [algo_trading_chan, p.28, ch.2]: above SMA = long-only,
        # below SMA = short-only. NaN (warmup period) = allow both sides.
        regime_allows_long = True
        regime_allows_short = True
        if self.regime_sma_period > 0 and "regime_sma" in self._indicators[self.symbol].columns:
            sma_val = float(self._indicators[self.symbol]["regime_sma"].iloc[idx])
            if not math.isnan(sma_val):
                regime_allows_long = bar.close > sma_val
                regime_allows_short = bar.close < sma_val

        # Long entry: cross below lower_threshold (anticipatory).
        if regime_allows_long and osc_prev > self.lower_threshold and osc_now <= self.lower_threshold:
            state["entry_idx"] = idx
            state["dcp_at_entry"] = dcp_now
            return [Order(symbol=self.symbol, side="buy", volume=volume)]

        # Short entry: cross above upper_threshold.
        if regime_allows_short and osc_prev < self.upper_threshold and osc_now >= self.upper_threshold:
            state["entry_idx"] = idx
            state["dcp_at_entry"] = dcp_now
            return [Order(symbol=self.symbol, side="sell", volume=volume)]

        return []
