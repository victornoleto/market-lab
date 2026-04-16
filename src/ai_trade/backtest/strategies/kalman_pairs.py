"""Kalman-filter pair trading on 1h bars [algo_trading_chan, p.76-80, ch.3].

Adaptive variant of ``ChanBollingerPairsStrategy``: instead of a static OLS
hedge ratio ``β`` fit once on a training slice, the hedge parameters
``[α_t, β_t]`` evolve each bar via a Kalman filter.

State-space model (Chan p.77, eq. 3.10-3.13):

* State ``x_t = [α_t, β_t]ᵀ`` with transition ``x_t = x_{t-1} + w_t``,
  ``w_t ~ N(0, Q)``, ``Q = δ·I`` (process noise — small δ → slow drift).
* Observation ``y_t = H_t · x_t + ν_t`` where ``H_t = [1, x_obs_t]``,
  ``ν_t ~ N(0, R)``.

Each bar we trade the **standardized innovation** ``z_t = e_t / √S_t``
where ``e_t = y_t − H_t · x̂_{t|t-1}`` and ``S_t = H_t · P_{t|t-1} · H_tᵀ + R``
[p.78, eq. 3.14-3.15].

Entry/exit follow Chan's canonical rule [p.79]:
* ``z_t < −entry_z`` → long spread (buy long leg, short ``β_t·`` short leg).
* ``z_t >  +entry_z`` → short spread.
* ``|z_t| < exit_z`` → flatten.

Shares the CFD-specific adaptations with ``ChanBollingerPairsStrategy``:

* Session gate (``entry_hour_cutoff`` + Friday cut-offs) — Pepperstone
  overnight swap kills multi-day pair holds.
* Wall-clock ``max_hold_hours`` hard cap — short-hold gate.
* Spread blow-out stop at ``|z| ≥ spread_stop_z`` — capital preservation.

Initial state is seeded from an OLS fit on the first ``init_train_bars``
aligned bars; ``P_0`` is set to ``OLS_variance``. After seeding the filter
is fully recursive.
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
class KalmanPairsStrategy:
    """Adaptive Kalman pair trader on 1h bars [algo_trading_chan, p.76-80]."""

    data: dict[str, pd.DataFrame]
    long_symbol: str = "SPY"
    short_symbol: str = "IWM"

    # Grid knobs.
    delta: float = 1e-4
    entry_z: float = 1.0

    # Fixed constants (each one cited in docstring).
    exit_z: float = 0.0
    spread_stop_z: float = 3.0
    obs_noise_r: float = 1.0
    init_train_bars: int = 500
    risk_pct_of_equity: float = 0.95
    max_hold_hours: float = 48.0
    entry_hour_cutoff: int = 14
    friday_flat_hour: int = 15
    friday_no_entry_hour: int = 13

    _logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("ai_trade.strategy.kalman_pairs"),
        repr=False,
    )
    _indicators: pd.DataFrame = field(init=False, default_factory=pd.DataFrame)

    def __post_init__(self) -> None:
        if self.long_symbol not in self.data:
            raise KeyError(f"long_symbol {self.long_symbol!r} not in data")
        if self.short_symbol not in self.data:
            raise KeyError(f"short_symbol {self.short_symbol!r} not in data")
        if self.delta <= 0:
            raise ValueError(f"delta must be > 0, got {self.delta}")
        if self.entry_z <= 0:
            raise ValueError(f"entry_z must be > 0, got {self.entry_z}")
        if self.init_train_bars < 30:
            raise ValueError(
                f"init_train_bars must be ≥ 30, got {self.init_train_bars}"
            )

        self.data = {sym: adjust_ohlc(df) for sym, df in self.data.items()}
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        if not df_long.index.equals(df_short.index):
            raise ValueError(
                f"timestamps of {self.long_symbol} and {self.short_symbol} "
                f"must be aligned (len {len(df_long)} vs {len(df_short)})"
            )
        if self.init_train_bars >= len(df_long):
            raise RuntimeError(
                f"init_train_bars={self.init_train_bars} ≥ len(data)"
                f"={len(df_long)} — not enough history to seed Kalman"
            )
        self._precompute_indicators()

    def _seed_from_ols(self, y: np.ndarray, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Fit OLS y = α + β·x on the seed window → returns (state, P0)."""
        n = len(x)
        X = np.column_stack([np.ones(n), x])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        residuals = y - X @ coef
        dof = n - 2
        sigma2 = float((residuals @ residuals) / dof) if dof > 0 else 1.0
        xtx_inv = np.linalg.inv(X.T @ X)
        p0 = sigma2 * xtx_inv  # 2x2 covariance of (α, β)
        state = np.array([float(coef[0]), float(coef[1])])
        return state, p0

    def _precompute_indicators(self) -> None:
        """Run the Kalman filter forward once over the full series.

        Produces per-bar arrays: α, β, innovation e, innovation std √S,
        and standardised innovation z = e/√S. Only bars with index ≥
        ``init_train_bars`` have valid values.
        """
        df_long = self.data[self.long_symbol]
        df_short = self.data[self.short_symbol]
        y_all = df_long["close"].to_numpy(dtype=float)
        x_all = df_short["close"].to_numpy(dtype=float)
        n = len(y_all)

        # Seed state from OLS on the first init_train_bars
        y_train = y_all[: self.init_train_bars]
        x_train = x_all[: self.init_train_bars]
        state, P = self._seed_from_ols(y_train, x_train)

        Q = self.delta * np.eye(2)
        R = float(self.obs_noise_r)

        alpha_out = np.full(n, np.nan)
        beta_out = np.full(n, np.nan)
        innov_out = np.full(n, np.nan)
        innov_std_out = np.full(n, np.nan)
        z_out = np.full(n, np.nan)

        # Warm phase (indices < init_train_bars): still run filter updates
        # so the state is calibrated, but don't export signal values (NaN).
        for t in range(n):
            H = np.array([1.0, x_all[t]])
            # Predict
            P_pred = P + Q
            # Innovation + innovation variance
            y_pred = float(H @ state)
            e = float(y_all[t] - y_pred)
            S = float(H @ P_pred @ H) + R
            S = max(S, 1e-12)
            # Kalman gain (2,)
            K = P_pred @ H / S
            # Update
            state = state + K * e
            P = P_pred - np.outer(K, H) @ P_pred

            if t >= self.init_train_bars:
                alpha_out[t] = state[0]
                beta_out[t] = state[1]
                innov_out[t] = e
                innov_std_out[t] = float(np.sqrt(S))
                z_out[t] = e / float(np.sqrt(S))

        self._indicators = pd.DataFrame(
            {
                "alpha": alpha_out,
                "beta": beta_out,
                "innovation": innov_out,
                "innovation_std": innov_std_out,
                "zscore": z_out,
            },
            index=df_long.index,
        )

    STATE_KEY_PREFIX = "kalman_pairs_state"
    DIAG_KEY = "kalman_pairs_diagnostics"

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
        if ts.hour > self.entry_hour_cutoff:
            return True
        if ts.weekday() == 4 and ts.hour >= self.friday_no_entry_hour:
            return True
        return False

    def _compute_leg_volumes(
        self, equity: float, price_long: float, price_short: float, beta: float,
    ) -> tuple[float, float]:
        total_notional = equity * self.risk_pct_of_equity
        denom = price_long + abs(beta) * price_short
        if denom <= 0 or total_notional <= 0:
            return 0.0, 0.0
        long_leg = total_notional / denom
        short_leg = abs(beta) * long_leg
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
        pos_long = portfolio.positions.get(self.long_symbol)
        pos_short = portfolio.positions.get(self.short_symbol)
        if pos_long is None or pos_short is None:
            return []
        side = state.get("side", "long_spread")
        entry_ts: pd.Timestamp = state.get("entry_wall_clock_ts", ts)
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

        # 3. Wall-clock hard cap
        if wall_clock_h >= self.max_hold_hours:
            self._record_exit(context, "hard_cap", wall_clock_h)
            return close_orders()

        # 4. Mean-reversion exit [p.79, ch.3]
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
        if idx < self.init_train_bars + 1:
            return []

        zscore_now = float(self._indicators["zscore"].iloc[idx])
        zscore_prev = float(self._indicators["zscore"].iloc[idx - 1])
        beta_now = float(self._indicators["beta"].iloc[idx])
        if np.isnan(zscore_now) or np.isnan(zscore_prev) or np.isnan(beta_now):
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
                context[self._state_key()] = {}
            return exit_orders

        if self._should_skip_entry_session(ts):
            return []

        long_leg, short_leg = self._compute_leg_volumes(
            portfolio.equity, bar_long.close, bar_short.close, beta_now,
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
            state["beta_at_entry"] = beta_now
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
            state["beta_at_entry"] = beta_now
            return [
                Order(symbol=self.long_symbol, side="sell", volume=long_leg),
                Order(symbol=self.short_symbol, side="buy", volume=short_leg),
            ]

        return []
