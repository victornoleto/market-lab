"""Pure-numpy companion to :mod:`stop_loss_and_risk_signals`.

Provides :func:`simulate_with_stop_and_risk_numpy` — a completely
hand-rolled implementation of the combined stop-loss + risk-signal
simulator that does **not** use pandas ``rolling`` / ``ewm`` / DataFrame
operations. Its only pandas contact is wrapping the final equity array
into a :class:`pd.Series` for downstream convenience.

Purpose
-------

Cross-library parity guard (gate G7 in the mandate). Two independent
implementations of the same algorithm must agree on CAGR within
±3 pp (``[advances_fin_ml, p.31-34]``). Without this, a subtle
look-ahead / alignment bug can silently flatter the vectorised path.

Scope
-----

This is a superset — it reproduces every legal overlay combination:

* ``stop_cfg.stop_loss_pct is None`` and ``lambda_de_lever == 0`` →
  matches the base :func:`simulate_regime_threshold_with_legs`.
* ``stop_cfg`` active, ``lambda_de_lever == 0`` → matches
  :func:`simulate_with_stop_loss`.
* ``stop_cfg.stop_loss_pct is None``, ``lambda_de_lever > 0`` → matches
  :func:`simulate_with_risk_signal`.
* Both overlays → matches :func:`simulate_with_stop_and_risk`.

Returns
-------

Only the equity curve (``pd.Series``) — trades / stop events / position
trace are intentionally not reproduced here. G7 tests CAGR only.

Citations
---------
* Honest alignment: ``[advances_fin_ml, p.31-34]``.
* Gayed synth formula ``r = L · r − fee/252``:
  ``[leverage_for_the_long_run, p.16, footnote 22]``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    TRADING_DAYS_PER_YEAR,
)
from market_lab.backtest.strategies.stop_loss_and_risk_signals import (
    RiskSignalConfig,
    StopLossConfig,
)


def _compute_ma_numpy(prices: np.ndarray, filter_kind: str, lookback: int) -> np.ndarray:
    """Hand-rolled SMA / EMA in pure numpy — no pandas rolling/ewm."""
    n = len(prices)
    ma = np.full(n, np.nan, dtype=float)
    if filter_kind == "SMA":
        # Rolling window mean via cumulative sums.
        if n < lookback:
            return ma
        cs = np.concatenate(([0.0], np.cumsum(prices)))
        windows = (cs[lookback:] - cs[:-lookback]) / lookback
        ma[lookback - 1 :] = windows
    else:  # EMA iterative
        if n < lookback:
            return ma
        alpha = 2.0 / (lookback + 1.0)
        seed = float(prices[:lookback].mean())
        ma[lookback - 1] = seed
        ema = seed
        for i in range(lookback, n):
            ema = alpha * prices[i] + (1.0 - alpha) * ema
            ma[i] = ema
    return ma


def _compute_regime_numpy(
    prices: np.ndarray, ma: np.ndarray, threshold: float
) -> np.ndarray:
    n = len(prices)
    out = np.full(n, np.nan, dtype=float)
    prev: int | None = None
    for i in range(n):
        m = ma[i]
        if np.isnan(m):
            continue
        up = m * (1.0 + threshold)
        lo = m * (1.0 - threshold)
        p = prices[i]
        if p > up:
            prev = 1
        elif p < lo:
            prev = -1
        out[i] = prev if prev is not None else -1
    return out


def simulate_with_stop_and_risk_numpy(
    signal_prices: pd.Series,
    buy_leg_returns: pd.Series,
    sell_leg_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
    stop_cfg: StopLossConfig,
    risk_series: pd.Series,
    risk_cfg: RiskSignalConfig,
) -> pd.Series:
    """Pure-numpy combined overlay simulator. Returns equity curve only.

    Re-implements :func:`simulate_with_stop_and_risk` from scratch using
    only numpy arrays for the inner loop. Drift from the vectorised
    reference must stay within ±3 pp CAGR (tests in
    ``tests/test_stop_and_risk_numpy_parity.py``).
    """
    idx = buy_leg_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("buy_leg_returns index must be monotonic increasing")

    # Reindex inputs onto the common calendar.
    px = signal_prices.reindex(idx).values.astype(float)
    long_vals = buy_leg_returns.values.astype(float)
    short_vals = sell_leg_returns.reindex(idx).values.astype(float)
    risk_vals = risk_series.reindex(idx).values.astype(float)

    ma = _compute_ma_numpy(px, cfg.filter, cfg.lookback)
    regime = _compute_regime_numpy(px, ma, cfg.threshold_pct)

    lam = float(risk_cfg.lambda_de_lever)
    stop_pct = stop_cfg.stop_loss_pct
    stop_enabled = stop_pct is not None
    stop_pct_f = float(stop_pct) if stop_enabled else 0.0
    mode = stop_cfg.reentry_mode
    reentry_param = stop_cfg.reentry_param
    switch_cost = cfg.switch_cost_pct
    tax_rate = cfg.tax_rate

    n = len(idx)
    equity_arr = np.empty(n, dtype=float)
    equity = 1.0
    running_peak = 1.0
    prev_regime: int | None = None
    prev_pos = 0.0
    entry_equity = 1.0

    # Stop state
    stop_active = False
    stop_bar = -1
    bottom_price = np.nan
    saw_non_bull_since_stop = False

    for i in range(n):
        cur_base = regime[i]
        if np.isnan(cur_base):
            equity_arr[i] = equity
            continue
        cur_signal = int(cur_base)

        # Step 1: earn return at yesterday's effective position.
        if prev_regime is not None:
            if prev_regime == 1:
                bl = long_vals[i]
                cl = short_vals[i]
                bl = 0.0 if np.isnan(bl) else bl
                cl = 0.0 if np.isnan(cl) else cl
                r = prev_pos * bl + (1.0 - prev_pos) * cl
            else:
                r = short_vals[i]
                r = 0.0 if np.isnan(r) else r
            equity *= 1.0 + r

        # Step 2: peak / bottom tracking.
        if not stop_active:
            if equity > running_peak:
                running_peak = equity
        else:
            p_now = px[i]
            if not np.isnan(p_now):
                if np.isnan(bottom_price) or p_now < bottom_price:
                    bottom_price = p_now

        # Step 3: stop trigger / re-entry.
        if stop_enabled:
            if not stop_active:
                if running_peak > 0:
                    dd = equity / running_peak - 1.0
                    if dd <= -stop_pct_f:
                        stop_active = True
                        stop_bar = i
                        p_now = px[i]
                        bottom_price = p_now if not np.isnan(p_now) else np.nan
                        saw_non_bull_since_stop = False
            else:
                if mode == "next_signal":
                    if cur_signal != 1:
                        saw_non_bull_since_stop = True
                    should_exit = saw_non_bull_since_stop and cur_signal == 1
                elif mode == "time_cooldown":
                    should_exit = (i - stop_bar) >= int(reentry_param)
                else:  # recovery_trigger
                    p_now = px[i]
                    should_exit = False
                    if (
                        not np.isnan(bottom_price)
                        and bottom_price > 0
                        and not np.isnan(p_now)
                    ):
                        should_exit = (p_now / bottom_price - 1.0) >= float(reentry_param)

                if should_exit:
                    stop_active = False
                    running_peak = equity
                    saw_non_bull_since_stop = False

        # Step 4: effective regime + position.
        if stop_active:
            effective_regime = -1
            cur_pos = 0.0
        elif cur_signal == 1:
            effective_regime = 1
            r_raw = risk_vals[i]
            r_t = 0.0 if np.isnan(r_raw) else r_raw
            cur_pos = max(0.0, 1.0 - lam * r_t)
        else:
            effective_regime = -1
            cur_pos = 0.0

        # Step 5: switch cost + tax on regime change.
        if prev_regime is not None and effective_regime != prev_regime:
            if tax_rate > 0.0 and equity > entry_equity:
                gain = equity - entry_equity
                equity -= gain * tax_rate
            equity -= switch_cost * equity
            entry_equity = equity
        elif prev_regime is None:
            entry_equity = equity

        equity_arr[i] = equity
        prev_regime = effective_regime
        prev_pos = cur_pos

    return pd.Series(equity_arr, index=idx, name="equity_numpy")
