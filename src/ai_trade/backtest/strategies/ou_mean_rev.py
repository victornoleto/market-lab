"""Ornstein-Uhlenbeck Mean-Reversion strategy (intraday / short-hold).

Trades the z-score of log prices toward their rolling mean. Genuinely
different from Bollinger MR: uses log-price z-scores instead of raw
close vs. MA ± k·σ bands, and includes a mean-reversion confirmation
gate via the ADF regression coefficient λ.

**Citations:**

- OU process and half-life: ``[algo_trading_chan, p.47-48, ch.2]`` —
  half-life = −log(2)/λ where λ is the ADF regression coefficient.
  Sets the natural time scale for mean-reversion.
- Lookback rule: ``[algo_trading_chan, p.269, ch.2]`` — "Set the
  lookback for moving average and standard deviation to a small
  multiple of the half-life."
- AR model foundation: ``[machine_trading, p.60-65, ch.3]`` —
  AR(1) model; stationary iff |φ| < 1.
- Z-score entry for mean-reversion: ``[quant_trading_chan, p.140-142]``
  — estimate θ via regression of Δz on (z − z̄).
- Hard time-stop: ``[machine_trading, p.126, ch.4]``.

Pipeline (per bar)
------------------

1. Pre-compute rolling z-score on log(close) with ``lookback`` window.
2. Pre-compute rolling λ from ADF regression (Δlog(p) on log(p_{t-1})).
3. **Entry (long):** z-score < −z_entry AND λ < 0 (mean-reversion confirmed).
4. **Exit:** z-score ≥ z_exit (mean reached), OR stop-loss, OR time-stop.
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
class OUMeanRevStrategy:
    """Single-instrument OU z-score mean-reversion (short-hold).

    Parameters
    ----------
    lookback : int
        Window for rolling z-score and ADF regression. Should approximate
        the half-life of mean reversion ``[algo_trading_chan, p.47-48, ch.2]``.
    z_entry : float
        Z-score threshold for entry (negative). Buy when z < −z_entry.
    z_exit : float
        Z-score threshold for exit. Sell when z ≥ z_exit (default 0 = mean).
    stop_pct : float
        Stop-loss as fraction of entry price.
    max_hold : int
        Hard time-stop in bars ``[machine_trading, p.126, ch.4]``.
    """

    data: dict[str, pd.DataFrame]
    symbol: str = "SPY"
    lookback: int = 60
    z_entry: float = 2.0
    z_exit: float = 0.0
    stop_pct: float = 0.02
    max_hold: int = 24
    risk_pct_of_equity: float = 0.95

    _indicators: dict[str, pd.DataFrame] = field(init=False, default_factory=dict)
    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.ou_mean_rev"),
        repr=False,
    )

    def __post_init__(self) -> None:
        if self.lookback < 10:
            raise ValueError(f"lookback must be >= 10, got {self.lookback}")
        if self.z_entry <= 0:
            raise ValueError(f"z_entry must be > 0, got {self.z_entry}")
        if not (0 < self.stop_pct < 1):
            raise ValueError(f"stop_pct must be in (0, 1), got {self.stop_pct}")
        if self.max_hold < 1:
            raise ValueError(f"max_hold must be >= 1, got {self.max_hold}")
        if self.symbol not in self.data:
            raise KeyError(f"symbol {self.symbol!r} not in data")

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        self._precompute_indicators(self.symbol)

    def _precompute_indicators(self, symbol: str) -> None:
        """Compute rolling z-score on log(close) and ADF λ coefficient."""
        close = self.data[symbol]["close"].astype(float)
        log_close = np.log(close)

        # Rolling mean and std of log(close).
        roll_mean = log_close.rolling(
            window=self.lookback, min_periods=self.lookback,
        ).mean()
        roll_std = log_close.rolling(
            window=self.lookback, min_periods=self.lookback,
        ).std(ddof=1)

        # Z-score: (log(p) − μ) / σ [quant_trading_chan, p.140-142].
        z_score = (log_close - roll_mean) / roll_std

        # Rolling ADF λ: regress Δlog(p) on log(p_{t-1}).
        # λ = cov(Δlog(p), log(p_{t-1})) / var(log(p_{t-1}))
        # [algo_trading_chan, p.42-43, ch.2].
        delta_log = log_close.diff()
        lag_log = log_close.shift(1)

        roll_cov = delta_log.rolling(
            window=self.lookback, min_periods=self.lookback,
        ).cov(lag_log)
        roll_var = lag_log.rolling(
            window=self.lookback, min_periods=self.lookback,
        ).var(ddof=1)

        # λ < 0 means mean-reverting [algo_trading_chan, p.42, ch.2].
        adf_lambda = roll_cov / roll_var

        self._indicators[symbol] = pd.DataFrame({
            "z_score": z_score,
            "adf_lambda": adf_lambda,
            "log_close": log_close,
        }, index=close.index)

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

        if idx < self.lookback:
            return []

        z_now = float(ind["z_score"].iloc[idx])
        lam_now = float(ind["adf_lambda"].iloc[idx])

        if np.isnan(z_now) or np.isnan(lam_now):
            return []

        pos = portfolio.positions.get(self.symbol)
        state = context.setdefault(f"ou_state_{self.symbol}", {})

        if pos is not None:
            exit_order = self._maybe_exit(pos, bar, idx, state, z_now)
            if exit_order is not None:
                state.clear()
                return [exit_order]
            return []

        return self._maybe_enter(bar, idx, state, portfolio, z_now, lam_now)

    def _maybe_exit(
        self,
        pos,
        bar: Bar,
        idx: int,
        state: dict,
        z_now: float,
    ) -> Order | None:
        entry_price = pos.avg_entry_price
        entry_idx = state.get("entry_idx", idx)
        bars_held = idx - entry_idx

        # 1. Stop-loss [machine_trading, p.126, ch.4].
        if bar.close <= entry_price * (1 - self.stop_pct):
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        # 2. Z-score mean-reversion target: z crosses above z_exit.
        if z_now >= self.z_exit:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        # 3. Hard time-stop.
        if bars_held >= self.max_hold:
            return Order(symbol=self.symbol, side="sell", volume=pos.volume)

        return None

    def _maybe_enter(
        self,
        bar: Bar,
        idx: int,
        state: dict,
        portfolio: Portfolio,
        z_now: float,
        lam_now: float,
    ) -> list[Order]:
        # Mean-reversion confirmation: λ must be negative.
        # [algo_trading_chan, p.42, ch.2] — only trade when ADF confirms
        # the series is mean-reverting.
        if lam_now >= 0:
            return []

        # Z-score entry: buy when z < −z_entry [quant_trading_chan, p.140-142].
        if z_now >= -self.z_entry:
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

        state["entry_idx"] = idx
        return [Order(symbol=self.symbol, side="buy", volume=volume)]
