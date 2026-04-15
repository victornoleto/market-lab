"""Chan Bollinger Pairs — canonical mean-reversion pair trading on 1h bars.

Implements the canonical formulation from [algo_trading_chan, p.71-73, ch.3]:
static OLS hedge ratio β fit on a training slice, OU regression to derive
half-life [p.47-48, ch.2], lookback = multiplier × half-life, Bollinger
z-score entry at ±entry_z, exit at 0.

Deviates from the pure-Chan canon in three CFD-specific adaptations (see
docstring of [_should_skip_entry_session] and [_maybe_exit]):

* Session gate (entry_hour_cutoff + Friday cut-offs) — protects against
  overnight swap and weekend 3x swap on Pepperstone CFD.
* Wall-clock 48h hard cap — [tiingo_service spec §1.4] short-hold gate.
* Spread-blow-out stop at |z| >= 3.0 — [p.293-294, ch.8] capital
  preservation against regime shift.

See `docs/superpowers/specs/2026-04-15-chan-pairs-1h-design.md`.
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
class ChanBollingerPairsStrategy:
    """Canonical Chan Bollinger-z pair trader on 1h bars."""

    data: dict[str, pd.DataFrame]
    long_symbol: str = "GLD"
    short_symbol: str = "SLV"

    # Grid knobs.
    lookback_multiplier: int = 2
    entry_z: float = 1.0

    # Fixed constants (each one cited in the docstring / spec §3).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    train_bars: int = 1250
    half_life_min: int = 4
    half_life_max: int = 60
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13

    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.chan_pairs"),
        repr=False,
    )
    _beta: float = field(init=False, default=float("nan"))
    _half_life_bars: int = field(init=False, default=0)
    _t_stat_ou: float = field(init=False, default=float("nan"))
    _hedge_ordering: str = field(init=False, default="")
    _indicators: pd.DataFrame = field(init=False, default_factory=pd.DataFrame)
    _lookback_bars: int = field(init=False, default=0)
    _time_stop_bars: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        # Rescale OHLC to the adjusted-close base — regression guard for
        # bug commit 5ca9410 (raw close triggered false z-crossings on ex-div bars).
        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )
        self._fit_hedge_and_half_life()
        self._precompute_indicators()

    def _precompute_indicators(self) -> None:
        """Compute spread, rolling mean/std, z-score on the full data index."""
        self._lookback_bars = self.lookback_multiplier * self._half_life_bars
        self._time_stop_bars = min(3 * self._half_life_bars, 24)

        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        spread = df_long["close"] - self._beta * df_short["close"]
        spread_ma = spread.rolling(self._lookback_bars, min_periods=self._lookback_bars).mean()
        spread_std = spread.rolling(self._lookback_bars, min_periods=self._lookback_bars).std()
        zscore = (spread - spread_ma) / spread_std
        self._indicators = pd.DataFrame(
            {
                "spread": spread,
                "spread_ma": spread_ma,
                "spread_std": spread_std,
                "zscore": zscore,
            },
            index=df_long.index,
        )

    def _fit_beta_single(
        self, y: np.ndarray, x: np.ndarray
    ) -> tuple[float, float]:
        """OLS of y on x with constant; return (β, t_stat_β)."""
        n = len(x)
        X = np.column_stack([np.ones(n), x])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        residuals = y - X @ coef
        dof = n - 2
        if dof <= 0:
            return coef[1], float("nan")
        sigma2 = (residuals @ residuals) / dof
        xtx_inv = np.linalg.inv(X.T @ X)
        se_beta = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
        t_stat = float(coef[1] / se_beta) if se_beta > 0 else float("nan")
        return float(coef[1]), t_stat

    def _fit_ou_half_life(
        self, spread: np.ndarray
    ) -> tuple[int, float]:
        """OU regression: Δs_t ~ λ · s_{t-1} + α. Returns (half_life, t_stat_λ)."""
        s_lag = spread[:-1]
        s_delta = np.diff(spread)
        n = len(s_lag)
        X = np.column_stack([np.ones(n), s_lag])
        coef, *_ = np.linalg.lstsq(X, s_delta, rcond=None)
        residuals = s_delta - X @ coef
        dof = n - 2
        sigma2 = (residuals @ residuals) / dof if dof > 0 else float("nan")
        xtx_inv = np.linalg.inv(X.T @ X)
        se_lam = float(np.sqrt(sigma2 * xtx_inv[1, 1]))
        lam = float(coef[1])
        t_stat = float(lam / se_lam) if se_lam > 0 else float("nan")
        if lam >= 0 or not np.isfinite(lam):
            return 0, t_stat
        half_life = int(round(-np.log(2) / lam))
        return half_life, t_stat

    def _fit_hedge_and_half_life(self) -> None:
        """Fit β (both orderings, pick best OU t-stat) + half-life. Raises if not cointegrated."""
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if self.train_bars >= len(df_long):
            raise RuntimeError(
                f"train_bars={self.train_bars} >= len(data)={len(df_long)} "
                f"— not enough history to fit"
            )
        train_long = df_long["close"].to_numpy()[: self.train_bars]
        train_short = df_short["close"].to_numpy()[: self.train_bars]

        # Ordering A: price_long = α + β·price_short
        beta_a, t_beta_a = self._fit_beta_single(train_long, train_short)
        spread_a = train_long - beta_a * train_short
        hl_a, t_ou_a = self._fit_ou_half_life(spread_a)

        # Ordering B: price_short = α + β·price_long → convert to β_long-per-short
        beta_b_raw, t_beta_b = self._fit_beta_single(train_short, train_long)
        beta_b = 1.0 / beta_b_raw if abs(beta_b_raw) > 1e-9 else float("nan")
        spread_b = train_long - beta_b * train_short
        hl_b, t_ou_b = self._fit_ou_half_life(spread_b)

        # Chan [p.54]: pick the ordering with the most negative OU t-stat.
        if t_ou_a <= t_ou_b:
            self._beta = beta_a
            self._half_life_bars = hl_a
            self._t_stat_ou = t_ou_a
            self._hedge_ordering = f"{self.long_symbol}~{self.short_symbol}"
        else:
            self._beta = beta_b
            self._half_life_bars = hl_b
            self._t_stat_ou = t_ou_b
            self._hedge_ordering = f"{self.short_symbol}~{self.long_symbol}"

        self._logger.info(
            "hedge fit: ordering=%s β=%.4f t_stat_OU=%.3f half_life=%d",
            self._hedge_ordering, self._beta, self._t_stat_ou, self._half_life_bars,
        )

        # CADF 5% critical value ≈ -3.34 for bivariate cointegration
        # [algo_trading_chan, p.43-45]. Using -3.4 for a small margin.
        if not np.isfinite(self._t_stat_ou) or self._t_stat_ou > -3.4:
            raise RuntimeError(
                f"pair not cointegrated on training slice: "
                f"t_stat_OU={self._t_stat_ou:.3f} > -3.4 "
                f"(half_life would be {self._half_life_bars})"
            )
        if not (self.half_life_min <= self._half_life_bars <= self.half_life_max):
            raise RuntimeError(
                f"half_life={self._half_life_bars} outside clamp "
                f"[{self.half_life_min}, {self.half_life_max}] — pair not suitable "
                f"for 1h mean-reversion"
            )

    STATE_KEY_PREFIX = "chan_pairs_state"
    DIAG_KEY = "chan_pairs_diagnostics"

    def _state_key(self) -> str:
        return f"{self.STATE_KEY_PREFIX}_{self.long_symbol}_{self.short_symbol}"

    def _record_exit(
        self, context: dict, reason: str, hold_hours: float,
    ) -> None:
        diag = context.setdefault(self.DIAG_KEY, {
            "exit_reasons": [], "hold_hours": [],
        })
        diag["exit_reasons"].append(reason)
        diag["hold_hours"].append(float(hold_hours))

    def _should_skip_entry_session(self, ts: pd.Timestamp) -> bool:
        """Session gate — blocks entry near close or late on Friday."""
        if ts.hour > self.entry_hour_cutoff:
            return True
        if ts.weekday() == 4 and ts.hour >= self.friday_no_entry_hour:
            return True
        return False

    def _compute_leg_volumes(
        self, equity: float, price_long: float, price_short: float
    ) -> tuple[float, float]:
        """Return (long_leg_shares, short_leg_shares) given current prices."""
        total_notional = equity * self.risk_pct_of_equity
        denom = price_long + self._beta * price_short
        if denom <= 0 or total_notional <= 0:
            return 0.0, 0.0
        long_leg = total_notional / denom
        short_leg = self._beta * long_leg
        return long_leg, short_leg

    def _maybe_exit(
        self,
        ts: pd.Timestamp,
        idx: int,
        zscore_now: float,
        portfolio: Portfolio,
        state: dict,
        context: dict,
    ) -> list[Order]:
        """Return a pair of closing orders if any exit rule fires; else []."""
        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        if pos_long is None or pos_short is None:
            return []
        side = state.get("side", "long_spread")
        entry_ts: pd.Timestamp = state.get("entry_wall_clock_ts", ts)
        entry_idx: int = state.get("entry_idx", idx)
        bars_held = idx - entry_idx
        wall_clock_h = (ts - entry_ts).total_seconds() / 3600.0

        def close_orders() -> list[Order]:
            close_long_side = "sell" if pos_long.side == "long" else "buy"
            close_short_side = "sell" if pos_short.side == "long" else "buy"
            return [
                Order(self.long_symbol, close_long_side, pos_long.volume),
                Order(self.short_symbol, close_short_side, pos_short.volume),
            ]

        # 1. Spread blow-out stop [p.293-294, ch.8]
        if (
            (side == "long_spread" and zscore_now <= -self.spread_stop_z)
            or (side == "short_spread" and zscore_now >= self.spread_stop_z)
        ):
            self._record_exit(context, "spread_stop", wall_clock_h)
            return close_orders()

        # 2. Friday weekend-flat (CFD adaptation)
        if ts.weekday() == 4 and ts.hour >= self.friday_flat_hour:
            self._record_exit(context, "friday_flat", wall_clock_h)
            return close_orders()

        # 3. Wall-clock 48h hard cap [spec §1.4]
        if wall_clock_h >= self.max_hold_hours:
            self._record_exit(context, "hard_cap", wall_clock_h)
            return close_orders()

        # 4. Time-stop in trading bars [p.47, ch.2]
        if bars_held >= self._time_stop_bars:
            self._record_exit(context, "time_stop", wall_clock_h)
            return close_orders()

        # 5. Mean-reversion exit [p.71-72, ch.3]
        if (
            (side == "long_spread" and zscore_now >= self.exit_z)
            or (side == "short_spread" and zscore_now <= -self.exit_z)
        ):
            self._record_exit(context, "mean_revert", wall_clock_h)
            return close_orders()

        return []

    def on_bar(
        self,
        bars: dict[str, Bar],
        portfolio: Portfolio,
        context: dict,
    ) -> list[Order]:
        if self.long_symbol not in bars or self.short_symbol not in bars:
            return []
        bar_long = bars[self.long_symbol]
        bar_short = bars[self.short_symbol]
        ts = bar_long.timestamp
        try:
            idx = self._indicators.index.get_loc(ts)
        except KeyError:
            return []
        if idx < 1:
            return []
        zscore_now = float(self._indicators["zscore"].iloc[idx])
        zscore_prev = float(self._indicators["zscore"].iloc[idx - 1])
        if np.isnan(zscore_now) or np.isnan(zscore_prev):
            return []

        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        in_position = pos_long is not None and pos_short is not None

        if in_position:
            state = context.setdefault(self._state_key(), {})
            exit_orders = self._maybe_exit(
                ts=ts, idx=idx, zscore_now=zscore_now,
                portfolio=portfolio, state=state, context=context,
            )
            if exit_orders:
                context[self._state_key()] = {}  # clear state after exit
            return exit_orders
        if self._should_skip_entry_session(ts):
            return []

        long_leg, short_leg = self._compute_leg_volumes(
            portfolio.equity, bar_long.close, bar_short.close
        )
        if long_leg <= 0:
            return []

        state = context.setdefault(self._state_key(), {})

        # Long spread entry: z crosses DOWN through -entry_z
        if zscore_prev > -self.entry_z and zscore_now <= -self.entry_z:
            state["entry_idx"] = idx
            state["entry_z"] = zscore_now
            state["entry_wall_clock_ts"] = ts
            state["side"] = "long_spread"
            state["beta_at_entry"] = self._beta
            return [
                Order(symbol=self.long_symbol, side="buy", volume=long_leg),
                Order(symbol=self.short_symbol, side="sell", volume=short_leg),
            ]

        # Short spread entry: z crosses UP through +entry_z
        if zscore_prev < self.entry_z and zscore_now >= self.entry_z:
            state["entry_idx"] = idx
            state["entry_z"] = zscore_now
            state["entry_wall_clock_ts"] = ts
            state["side"] = "short_spread"
            state["beta_at_entry"] = self._beta
            return [
                Order(symbol=self.long_symbol, side="sell", volume=long_leg),
                Order(symbol=self.short_symbol, side="buy", volume=short_leg),
            ]

        return []
