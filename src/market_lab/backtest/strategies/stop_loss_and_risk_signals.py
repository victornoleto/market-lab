"""Stop-loss and crash-predictor overlays on the EMA/SMA threshold strategy.

Phases 1-2 of the crash-protection evolution (see
``studies/SPEC_crash_protection_evolution.md``).

* :func:`simulate_with_stop_loss` — Phase 1 overlay (drawdown stop + re-entry).
* :func:`simulate_with_risk_signal` — Phase 2 overlay (continuous
  de-leveraging driven by an external risk score in [0, 1]).

LPPLS wrappers and the combined stop+signal simulator live in companion
modules added in later phases.

Design
------

We expose a thin wrapper around
:func:`simulate_regime_threshold_with_legs` that overlays two extra rules
on the base signal:

1. **Stop-loss by drawdown-from-peak.** Whenever equity drops more than
   ``stop_loss_pct`` from its running peak, the effective regime is
   forced to ``-1`` (flat / cash), irrespective of the MA signal.
2. **Re-entry** is mode-dependent:

   * ``next_signal`` — wait until the underlying signal prints a fresh
     ``+1`` (a cross-up) after having printed something other than ``+1``
     first. Matches the user's intent of "wait for the next bull
     signal".
   * ``time_cooldown`` — wait ``reentry_param`` bars after the stop bar,
     then let the signal drive normally.
   * ``recovery_trigger`` — wait until the signal-asset price recovers by
     ``reentry_param`` (fractional) from the local bottom observed after
     the stop.

When the stop mode exits, the running peak is reset to the current equity
so small drawdowns do not immediately retrigger the stop.

Citations
---------

* Drawdown-from-peak stop rule is a textbook risk-management overlay;
  the exact mechanics (magnitude, re-entry) are the subject of the sweep
  in ``SPEC_crash_protection_evolution.md``.
* Close-of-day execution (no intraday stops) reflects
  ``SPEC_crash_protection_evolution.md §8.4``.
* Honest alignment (no look-ahead) follows ``[advances_fin_ml, p.31-34]``;
  we reuse the base simulator's bar ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd

from ai_trade.backtest.strategies.ema_sma_threshold_educational import (
    EMASMAThresholdConfig,
    Trade,
    compute_threshold_regime,
)

ReentryMode = Literal["next_signal", "time_cooldown", "recovery_trigger"]

VALID_INDICATORS: tuple[str, ...] = ("ebp", "term_spread", "cape", "vix", "composite")

__all__ = [
    "StopLossConfig",
    "StopEvent",
    "StopLossResult",
    "simulate_with_stop_loss",
    "RiskSignalConfig",
    "RiskSignalResult",
    "simulate_with_risk_signal",
    "StopAndRiskResult",
    "simulate_with_stop_and_risk",
    "VALID_INDICATORS",
]


@dataclass(frozen=True)
class StopLossConfig:
    """Immutable stop-loss + re-entry configuration.

    Parameters
    ----------
    stop_loss_pct : float | None
        Drawdown-from-peak threshold as a positive fraction in ``(0, 1)``.
        ``None`` disables the overlay (the function becomes an honest
        no-op wrapper that matches
        :func:`simulate_regime_threshold_with_legs`).
    reentry_mode : {"next_signal", "time_cooldown", "recovery_trigger"}
        How we leave the stopped state.
    reentry_param : float | int | None
        Mode-dependent parameter:

        * ``next_signal`` — unused (must be ``None``; the sweep driver
          passes ``None``).
        * ``time_cooldown`` — positive number of bars to wait.
        * ``recovery_trigger`` — positive fractional price recovery from
          the local bottom observed after the stop.
    """

    stop_loss_pct: float | None = None
    reentry_mode: ReentryMode = "next_signal"
    reentry_param: float | int | None = None

    def __post_init__(self) -> None:
        if self.stop_loss_pct is not None:
            if not (0.0 < float(self.stop_loss_pct) < 1.0):
                raise ValueError(
                    f"stop_loss_pct must be in (0, 1) or None, got {self.stop_loss_pct}"
                )
        if self.reentry_mode not in ("next_signal", "time_cooldown", "recovery_trigger"):
            raise ValueError(
                f"reentry_mode must be one of next_signal/time_cooldown/"
                f"recovery_trigger, got {self.reentry_mode!r}"
            )
        if self.reentry_mode == "time_cooldown":
            p = self.reentry_param
            if p is None or not isinstance(p, (int, float)) or float(p) <= 0:
                raise ValueError(
                    f"reentry_param must be a positive number for time_cooldown, got {p!r}"
                )
        elif self.reentry_mode == "recovery_trigger":
            p = self.reentry_param
            if p is None or not isinstance(p, (int, float)) or float(p) <= 0:
                raise ValueError(
                    f"reentry_param must be a positive fraction for recovery_trigger, got {p!r}"
                )


@dataclass
class StopEvent:
    """One stop-trigger → re-entry episode."""

    stop_bar: int
    stop_date: pd.Timestamp
    equity_at_stop: float
    peak_before_stop: float
    drawdown_at_stop: float  # negative: e.g. -0.25
    reentry_bar: int | None = None
    reentry_date: pd.Timestamp | None = None
    reentry_bar_offset: int | None = None  # reentry_bar - stop_bar
    bottom_equity_during_stop: float | None = None
    bottom_price_during_stop: float | None = None


@dataclass
class StopLossResult:
    """Simulation output — superset of ``ThresholdResult`` with stop stats."""

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series  # *effective* regime (after stop overlay)
    n_switches: int
    cum_cost_pct: float
    cum_tax_pct: float = 0.0
    trades: list[Trade] = field(default_factory=list)
    n_stops_triggered: int = 0
    stop_events: list[StopEvent] = field(default_factory=list)


def simulate_with_stop_loss(
    signal_prices: pd.Series,
    buy_leg_returns: pd.Series,
    sell_leg_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
    stop_cfg: StopLossConfig,
) -> StopLossResult:
    """Run one sweep cell with stop-loss overlay.

    Signature mirrors :func:`simulate_regime_threshold_with_legs`; when
    ``stop_cfg.stop_loss_pct is None`` the result is equivalent to the
    base function (verified by regression tests).

    Parameters
    ----------
    signal_prices : pd.Series
        Daily close of the signal asset. Drives the base MA regime and
        the ``recovery_trigger`` re-entry test.
    buy_leg_returns, sell_leg_returns : pd.Series
        Per-bar returns of each leg (real ETFs or synth LETF series).
    cfg : EMASMAThresholdConfig
        Base strategy config (MA + threshold + switch cost + tax).
    stop_cfg : StopLossConfig
        Stop-loss overlay config.

    Returns
    -------
    StopLossResult
    """
    idx = buy_leg_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("buy_leg_returns index must be monotonic increasing")

    sell_leg = sell_leg_returns.reindex(idx)
    prices_on_ret_idx = signal_prices.reindex(idx)
    base_regime = compute_threshold_regime(prices_on_ret_idx, cfg)

    long_vals = buy_leg_returns.values
    short_vals = sell_leg.values
    base_regime_vals = base_regime.values
    price_vals = prices_on_ret_idx.values
    idx_values = idx

    switch_cost = cfg.switch_cost_pct
    tax_rate = cfg.tax_rate

    stop_pct = stop_cfg.stop_loss_pct
    stop_enabled = stop_pct is not None
    mode = stop_cfg.reentry_mode
    reentry_param = stop_cfg.reentry_param

    # Sim state
    equity = 1.0
    running_peak = 1.0
    equity_curve: list[float] = []
    daily_net: list[float] = []
    effective_regime_seq: list[float] = []
    n_switches = 0
    cum_cost = 0.0
    cum_tax = 0.0
    prev_regime: int | None = None  # effective regime actually held

    trades: list[Trade] = []
    entry_equity = 1.0
    entry_idx: int | None = None

    # Stop state
    stop_active = False
    active_event: StopEvent | None = None
    saw_non_bull_since_stop = False  # for next_signal mode
    stop_events: list[StopEvent] = []
    n_stops_triggered = 0

    for i in range(len(idx)):
        cur_base = base_regime_vals[i]
        if np.isnan(cur_base):
            equity_curve.append(equity)
            daily_net.append(0.0)
            effective_regime_seq.append(np.nan)
            continue

        cur_signal_int = int(cur_base)
        prev_eq = equity

        # Step 1: earn today's return at yesterday's effective regime.
        if prev_regime is not None:
            r = long_vals[i] if prev_regime == 1 else short_vals[i]
            r = 0.0 if np.isnan(r) else float(r)
            equity *= 1.0 + r

        # Step 2: peak / bottom tracking.
        if not stop_active:
            if equity > running_peak:
                running_peak = equity
        else:
            # Track local bottom while stopped (for recovery_trigger and stats).
            if active_event is not None:
                if (
                    active_event.bottom_equity_during_stop is None
                    or equity < active_event.bottom_equity_during_stop
                ):
                    active_event.bottom_equity_during_stop = equity
                p_now = price_vals[i]
                if not np.isnan(p_now):
                    if (
                        active_event.bottom_price_during_stop is None
                        or float(p_now) < active_event.bottom_price_during_stop
                    ):
                        active_event.bottom_price_during_stop = float(p_now)

        # Step 3: stop / re-entry logic.
        if stop_enabled:
            if not stop_active:
                # Check for stop trigger.
                if running_peak > 0:
                    dd = equity / running_peak - 1.0
                    if dd <= -float(stop_pct):  # type: ignore[arg-type]
                        stop_active = True
                        n_stops_triggered += 1
                        saw_non_bull_since_stop = False
                        p_now_raw = price_vals[i]
                        p_now = float(p_now_raw) if not np.isnan(p_now_raw) else float("nan")
                        active_event = StopEvent(
                            stop_bar=i,
                            stop_date=pd.Timestamp(idx_values[i]),
                            equity_at_stop=equity,
                            peak_before_stop=running_peak,
                            drawdown_at_stop=dd,
                            bottom_equity_during_stop=equity,
                            bottom_price_during_stop=p_now,
                        )
                        stop_events.append(active_event)
            else:
                # Stopped: check re-entry condition.
                if mode == "next_signal":
                    if cur_signal_int != 1:
                        saw_non_bull_since_stop = True
                    should_exit = saw_non_bull_since_stop and cur_signal_int == 1
                elif mode == "time_cooldown":
                    assert active_event is not None
                    should_exit = (i - active_event.stop_bar) >= int(reentry_param)  # type: ignore[arg-type]
                else:  # recovery_trigger
                    assert active_event is not None
                    p_now_raw = price_vals[i]
                    should_exit = False
                    if (
                        active_event.bottom_price_during_stop is not None
                        and not np.isnan(p_now_raw)
                        and active_event.bottom_price_during_stop > 0
                    ):
                        recovery = float(p_now_raw) / active_event.bottom_price_during_stop - 1.0
                        should_exit = recovery >= float(reentry_param)  # type: ignore[arg-type]

                if should_exit:
                    stop_active = False
                    running_peak = equity  # reset peak on re-entry
                    assert active_event is not None
                    active_event.reentry_bar = i
                    active_event.reentry_date = pd.Timestamp(idx_values[i])
                    active_event.reentry_bar_offset = i - active_event.stop_bar
                    active_event = None
                    saw_non_bull_since_stop = False

        # Step 4: effective regime.
        effective_regime = -1 if stop_active else cur_signal_int
        effective_regime_seq.append(float(effective_regime))

        # Step 5: switch cost + tax on effective regime change.
        if prev_regime is not None and effective_regime != prev_regime:
            tax = 0.0
            if tax_rate > 0.0 and entry_idx is not None and equity > entry_equity:
                gain = equity - entry_equity
                tax = gain * tax_rate
                equity -= tax
                cum_tax += tax
            cost = switch_cost * equity
            equity -= cost
            cum_cost += cost
            n_switches += 1

            if entry_idx is not None:
                exit_ts = pd.Timestamp(idx_values[i])
                entry_ts = pd.Timestamp(idx_values[entry_idx])
                trades.append(
                    Trade(
                        regime=prev_regime,
                        entry_date=entry_ts,
                        exit_date=exit_ts,
                        entry_equity=entry_equity,
                        exit_equity=equity,
                        gross_return=(equity + tax + cost) / entry_equity - 1.0,
                        tax_paid=tax,
                        bars_held=i - entry_idx,
                    )
                )
            entry_equity = equity
            entry_idx = i
        elif prev_regime is None:
            entry_equity = equity
            entry_idx = i

        equity_curve.append(equity)
        daily_net.append(equity / prev_eq - 1.0 if prev_eq > 0 else 0.0)
        prev_regime = effective_regime

    # Close any still-open trade at the final bar.
    if entry_idx is not None and prev_regime is not None:
        last_i = len(idx) - 1
        if entry_idx < last_i:
            exit_ts = pd.Timestamp(idx_values[last_i])
            entry_ts = pd.Timestamp(idx_values[entry_idx])
            trades.append(
                Trade(
                    regime=prev_regime,
                    entry_date=entry_ts,
                    exit_date=exit_ts,
                    entry_equity=entry_equity,
                    exit_equity=equity,
                    gross_return=equity / entry_equity - 1.0,
                    tax_paid=0.0,
                    bars_held=last_i - entry_idx,
                )
            )

    equity_series = pd.Series(equity_curve, index=idx, name="equity")
    returns_series = pd.Series(daily_net, index=idx, name="returns")
    eff_regime_series = pd.Series(effective_regime_seq, index=idx, name="regime")

    return StopLossResult(
        equity=equity_series,
        daily_returns=returns_series,
        regime=eff_regime_series,
        n_switches=n_switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
        trades=trades,
        n_stops_triggered=n_stops_triggered,
        stop_events=stop_events,
    )


# ---------------------------------------------------------------------------
# Phase 2 — risk-signal de-leveraging overlay
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskSignalConfig:
    """Continuous de-leveraging based on an external risk score.

    At every bar ``t`` where the base regime is ``+1`` (long), the
    effective position is::

        pos(t) = max(0, 1 − lambda_de_lever · risk(t))

    * ``risk(t) = 0`` (or NaN during warmup) → full position (1.0).
    * ``risk(t) = 1`` + ``lambda_de_lever = 1`` → zero position (all cash).
    * Intermediate values scale linearly.

    When the base regime is ``-1`` the signal is honored literally —
    same as the baseline (no stop, no de-levering applied to the
    sell leg).

    Parameters
    ----------
    indicator_type : str
        One of ``{"ebp", "term_spread", "cape", "vix", "composite"}``.
        This is metadata only; the risk series itself is supplied to
        :func:`simulate_with_risk_signal`.
    lambda_de_lever : float
        In ``[0, 1]``. ``0`` disables the overlay (equivalent to the
        baseline simulator).
    """

    indicator_type: str = "composite"
    lambda_de_lever: float = 0.0

    def __post_init__(self) -> None:
        if self.indicator_type not in VALID_INDICATORS:
            raise ValueError(
                f"indicator_type must be one of {VALID_INDICATORS}, "
                f"got {self.indicator_type!r}"
            )
        if not (0.0 <= float(self.lambda_de_lever) <= 1.0):
            raise ValueError(
                f"lambda_de_lever must be in [0, 1], got {self.lambda_de_lever}"
            )


@dataclass
class RiskSignalResult:
    """Output of :func:`simulate_with_risk_signal`."""

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    effective_position: pd.Series  # [0, 1], NaN during warmup
    n_switches: int
    cum_cost_pct: float
    cum_tax_pct: float = 0.0
    trades: list[Trade] = field(default_factory=list)


def simulate_with_risk_signal(
    signal_prices: pd.Series,
    buy_leg_returns: pd.Series,
    sell_leg_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
    risk_series: pd.Series,
    risk_cfg: RiskSignalConfig,
) -> RiskSignalResult:
    """Simulate with continuous risk-signal de-leveraging.

    Long-leg exposure is scaled by ``pos(t) = max(0, 1 − λ · risk(t))``.
    The sell-leg side is **unchanged** from the baseline — this overlay
    affects only the bull regime.

    Switch costs are charged on regime changes only. Gradual intra-regime
    position changes (due to varying risk) do **not** incur a switch
    cost in this simple model — Phase 3's combined simulator may revisit
    this if rebalancing costs become material.

    Parameters
    ----------
    signal_prices : pd.Series
        Daily close of the signal asset (drives MA/threshold regime).
    buy_leg_returns, sell_leg_returns : pd.Series
        Per-bar leg returns.
    cfg : EMASMAThresholdConfig
        Base strategy config.
    risk_series : pd.Series
        Daily risk score in ``[0, 1]``; NaN during warmup is treated as
        0 (no de-lever).
    risk_cfg : RiskSignalConfig
        Overlay parameters.

    Returns
    -------
    RiskSignalResult
    """
    idx = buy_leg_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("buy_leg_returns index must be monotonic increasing")

    sell_leg = sell_leg_returns.reindex(idx)
    prices_on_ret_idx = signal_prices.reindex(idx)
    risk_aligned = risk_series.reindex(idx)
    base_regime = compute_threshold_regime(prices_on_ret_idx, cfg)

    long_vals = buy_leg_returns.values
    short_vals = sell_leg.values
    risk_vals = risk_aligned.values
    base_regime_vals = base_regime.values
    idx_values = idx

    switch_cost = cfg.switch_cost_pct
    tax_rate = cfg.tax_rate
    lam = float(risk_cfg.lambda_de_lever)

    equity = 1.0
    equity_curve: list[float] = []
    daily_net: list[float] = []
    pos_trace: list[float] = []
    n_switches = 0
    cum_cost = 0.0
    cum_tax = 0.0
    prev_regime: int | None = None
    prev_pos: float = 0.0  # effective position held "yesterday"

    trades: list[Trade] = []
    entry_equity = 1.0
    entry_idx: int | None = None

    for i in range(len(idx)):
        cur_base = base_regime_vals[i]
        if np.isnan(cur_base):
            equity_curve.append(equity)
            daily_net.append(0.0)
            pos_trace.append(np.nan)
            continue
        cur_signal = int(cur_base)

        # Step 1: earn return using yesterday's position.
        prev_eq = equity
        if prev_regime is not None:
            if prev_regime == 1:
                buy_r = long_vals[i]
                cash_r = short_vals[i]
                buy_r = 0.0 if np.isnan(buy_r) else float(buy_r)
                cash_r = 0.0 if np.isnan(cash_r) else float(cash_r)
                r = prev_pos * buy_r + (1.0 - prev_pos) * cash_r
            else:
                r = short_vals[i]
                r = 0.0 if np.isnan(r) else float(r)
            equity *= 1.0 + r

        # Step 2: determine today's effective position from risk.
        if cur_signal == 1:
            r_raw = risk_vals[i]
            r_t = 0.0 if np.isnan(r_raw) else float(r_raw)
            cur_pos = max(0.0, 1.0 - lam * r_t)
        else:
            cur_pos = 0.0  # sell regime → position in cash/short leg only

        # Step 3: switch cost + tax on regime change (base signal level).
        if prev_regime is not None and cur_signal != prev_regime:
            tax = 0.0
            if tax_rate > 0.0 and entry_idx is not None and equity > entry_equity:
                gain = equity - entry_equity
                tax = gain * tax_rate
                equity -= tax
                cum_tax += tax
            cost = switch_cost * equity
            equity -= cost
            cum_cost += cost
            n_switches += 1

            if entry_idx is not None:
                exit_ts = pd.Timestamp(idx_values[i])
                entry_ts = pd.Timestamp(idx_values[entry_idx])
                trades.append(
                    Trade(
                        regime=prev_regime,
                        entry_date=entry_ts,
                        exit_date=exit_ts,
                        entry_equity=entry_equity,
                        exit_equity=equity,
                        gross_return=(equity + tax + cost) / entry_equity - 1.0,
                        tax_paid=tax,
                        bars_held=i - entry_idx,
                    )
                )
            entry_equity = equity
            entry_idx = i
        elif prev_regime is None:
            entry_equity = equity
            entry_idx = i

        equity_curve.append(equity)
        daily_net.append(equity / prev_eq - 1.0 if prev_eq > 0 else 0.0)
        pos_trace.append(cur_pos)
        prev_regime = cur_signal
        prev_pos = cur_pos

    # Close any still-open trade at the final bar.
    if entry_idx is not None and prev_regime is not None:
        last_i = len(idx) - 1
        if entry_idx < last_i:
            exit_ts = pd.Timestamp(idx_values[last_i])
            entry_ts = pd.Timestamp(idx_values[entry_idx])
            trades.append(
                Trade(
                    regime=prev_regime,
                    entry_date=entry_ts,
                    exit_date=exit_ts,
                    entry_equity=entry_equity,
                    exit_equity=equity,
                    gross_return=equity / entry_equity - 1.0,
                    tax_paid=0.0,
                    bars_held=last_i - entry_idx,
                )
            )

    return RiskSignalResult(
        equity=pd.Series(equity_curve, index=idx, name="equity"),
        daily_returns=pd.Series(daily_net, index=idx, name="returns"),
        regime=base_regime,
        effective_position=pd.Series(pos_trace, index=idx, name="eff_pos"),
        n_switches=n_switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
        trades=trades,
    )


# ---------------------------------------------------------------------------
# Phase 3 — combined stop-loss + risk-signal overlay
# ---------------------------------------------------------------------------


@dataclass
class StopAndRiskResult:
    """Output of :func:`simulate_with_stop_and_risk`."""

    equity: pd.Series
    daily_returns: pd.Series
    regime: pd.Series
    effective_position: pd.Series  # 0 when stopped; else max(0, 1−λ·risk) in bull
    n_switches: int
    cum_cost_pct: float
    cum_tax_pct: float = 0.0
    trades: list[Trade] = field(default_factory=list)
    n_stops_triggered: int = 0
    stop_events: list[StopEvent] = field(default_factory=list)


def simulate_with_stop_and_risk(
    signal_prices: pd.Series,
    buy_leg_returns: pd.Series,
    sell_leg_returns: pd.Series,
    cfg: EMASMAThresholdConfig,
    stop_cfg: StopLossConfig,
    risk_series: pd.Series,
    risk_cfg: RiskSignalConfig,
) -> StopAndRiskResult:
    """Combined stop-loss + risk-signal overlay.

    Precedence: stop-loss dominates. When the stop is active the
    effective position is forced to 0 regardless of the risk signal.
    When the stop is inactive and the base regime is ``+1``, the
    effective position is ``max(0, 1 − λ · risk(t))``. When the base
    regime is ``-1`` the effective position is 0 (sell leg drives).

    Re-entry from the stop resets the running peak (to the current
    equity) so gradual signal-driven de-leveraging does not
    immediately re-trigger the stop.

    Parameters match :func:`simulate_with_stop_loss` and
    :func:`simulate_with_risk_signal` combined. Degenerate settings
    reduce to each component exactly (validated by the tests in
    ``tests/test_stop_and_risk_combined.py``).
    """
    idx = buy_leg_returns.index
    if not idx.is_monotonic_increasing:
        raise ValueError("buy_leg_returns index must be monotonic increasing")

    sell_leg = sell_leg_returns.reindex(idx)
    prices_on_ret_idx = signal_prices.reindex(idx)
    risk_aligned = risk_series.reindex(idx)
    base_regime = compute_threshold_regime(prices_on_ret_idx, cfg)

    long_vals = buy_leg_returns.values
    short_vals = sell_leg.values
    risk_vals = risk_aligned.values
    base_regime_vals = base_regime.values
    price_vals = prices_on_ret_idx.values
    idx_values = idx

    switch_cost = cfg.switch_cost_pct
    tax_rate = cfg.tax_rate
    lam = float(risk_cfg.lambda_de_lever)

    stop_pct = stop_cfg.stop_loss_pct
    stop_enabled = stop_pct is not None
    mode = stop_cfg.reentry_mode
    reentry_param = stop_cfg.reentry_param

    # Sim state
    equity = 1.0
    running_peak = 1.0
    equity_curve: list[float] = []
    daily_net: list[float] = []
    pos_trace: list[float] = []
    n_switches = 0
    cum_cost = 0.0
    cum_tax = 0.0
    prev_regime: int | None = None  # effective regime: +1 if any exposure, -1 if flat
    prev_pos: float = 0.0

    trades: list[Trade] = []
    entry_equity = 1.0
    entry_idx: int | None = None

    # Stop state
    stop_active = False
    active_event: StopEvent | None = None
    saw_non_bull_since_stop = False
    stop_events: list[StopEvent] = []
    n_stops_triggered = 0

    for i in range(len(idx)):
        cur_base = base_regime_vals[i]
        if np.isnan(cur_base):
            equity_curve.append(equity)
            daily_net.append(0.0)
            pos_trace.append(np.nan)
            continue
        cur_signal = int(cur_base)

        prev_eq = equity

        # Step 1: earn return at yesterday's effective position.
        if prev_regime is not None:
            if prev_regime == 1:
                buy_r = long_vals[i]
                cash_r = short_vals[i]
                buy_r = 0.0 if np.isnan(buy_r) else float(buy_r)
                cash_r = 0.0 if np.isnan(cash_r) else float(cash_r)
                r = prev_pos * buy_r + (1.0 - prev_pos) * cash_r
            else:
                r = short_vals[i]
                r = 0.0 if np.isnan(r) else float(r)
            equity *= 1.0 + r

        # Step 2: update peak / stop-bottom tracking.
        if not stop_active:
            if equity > running_peak:
                running_peak = equity
        else:
            if active_event is not None:
                if (
                    active_event.bottom_equity_during_stop is None
                    or equity < active_event.bottom_equity_during_stop
                ):
                    active_event.bottom_equity_during_stop = equity
                p_now = price_vals[i]
                if not np.isnan(p_now):
                    if (
                        active_event.bottom_price_during_stop is None
                        or float(p_now) < active_event.bottom_price_during_stop
                    ):
                        active_event.bottom_price_during_stop = float(p_now)

        # Step 3: stop-loss trigger / re-entry logic.
        if stop_enabled:
            if not stop_active:
                if running_peak > 0:
                    dd = equity / running_peak - 1.0
                    if dd <= -float(stop_pct):  # type: ignore[arg-type]
                        stop_active = True
                        n_stops_triggered += 1
                        saw_non_bull_since_stop = False
                        p_now_raw = price_vals[i]
                        p_now = float(p_now_raw) if not np.isnan(p_now_raw) else float("nan")
                        active_event = StopEvent(
                            stop_bar=i,
                            stop_date=pd.Timestamp(idx_values[i]),
                            equity_at_stop=equity,
                            peak_before_stop=running_peak,
                            drawdown_at_stop=dd,
                            bottom_equity_during_stop=equity,
                            bottom_price_during_stop=p_now,
                        )
                        stop_events.append(active_event)
            else:
                if mode == "next_signal":
                    if cur_signal != 1:
                        saw_non_bull_since_stop = True
                    should_exit = saw_non_bull_since_stop and cur_signal == 1
                elif mode == "time_cooldown":
                    assert active_event is not None
                    should_exit = (i - active_event.stop_bar) >= int(reentry_param)  # type: ignore[arg-type]
                else:  # recovery_trigger
                    assert active_event is not None
                    p_now_raw = price_vals[i]
                    should_exit = False
                    if (
                        active_event.bottom_price_during_stop is not None
                        and not np.isnan(p_now_raw)
                        and active_event.bottom_price_during_stop > 0
                    ):
                        recovery = float(p_now_raw) / active_event.bottom_price_during_stop - 1.0
                        should_exit = recovery >= float(reentry_param)  # type: ignore[arg-type]

                if should_exit:
                    stop_active = False
                    running_peak = equity
                    assert active_event is not None
                    active_event.reentry_bar = i
                    active_event.reentry_date = pd.Timestamp(idx_values[i])
                    active_event.reentry_bar_offset = i - active_event.stop_bar
                    active_event = None
                    saw_non_bull_since_stop = False

        # Step 4: effective regime + position.
        if stop_active:
            effective_regime = -1  # forced cash
            cur_pos = 0.0
        elif cur_signal == 1:
            effective_regime = 1
            r_raw = risk_vals[i]
            r_t = 0.0 if np.isnan(r_raw) else float(r_raw)
            cur_pos = max(0.0, 1.0 - lam * r_t)
        else:
            effective_regime = -1
            cur_pos = 0.0

        # Step 5: switch cost + tax on regime change.
        if prev_regime is not None and effective_regime != prev_regime:
            tax = 0.0
            if tax_rate > 0.0 and entry_idx is not None and equity > entry_equity:
                gain = equity - entry_equity
                tax = gain * tax_rate
                equity -= tax
                cum_tax += tax
            cost = switch_cost * equity
            equity -= cost
            cum_cost += cost
            n_switches += 1

            if entry_idx is not None:
                exit_ts = pd.Timestamp(idx_values[i])
                entry_ts = pd.Timestamp(idx_values[entry_idx])
                trades.append(
                    Trade(
                        regime=prev_regime,
                        entry_date=entry_ts,
                        exit_date=exit_ts,
                        entry_equity=entry_equity,
                        exit_equity=equity,
                        gross_return=(equity + tax + cost) / entry_equity - 1.0,
                        tax_paid=tax,
                        bars_held=i - entry_idx,
                    )
                )
            entry_equity = equity
            entry_idx = i
        elif prev_regime is None:
            entry_equity = equity
            entry_idx = i

        equity_curve.append(equity)
        daily_net.append(equity / prev_eq - 1.0 if prev_eq > 0 else 0.0)
        pos_trace.append(cur_pos)
        prev_regime = effective_regime
        prev_pos = cur_pos

    # Close any still-open trade.
    if entry_idx is not None and prev_regime is not None:
        last_i = len(idx) - 1
        if entry_idx < last_i:
            exit_ts = pd.Timestamp(idx_values[last_i])
            entry_ts = pd.Timestamp(idx_values[entry_idx])
            trades.append(
                Trade(
                    regime=prev_regime,
                    entry_date=entry_ts,
                    exit_date=exit_ts,
                    entry_equity=entry_equity,
                    exit_equity=equity,
                    gross_return=equity / entry_equity - 1.0,
                    tax_paid=0.0,
                    bars_held=last_i - entry_idx,
                )
            )

    return StopAndRiskResult(
        equity=pd.Series(equity_curve, index=idx, name="equity"),
        daily_returns=pd.Series(daily_net, index=idx, name="returns"),
        regime=base_regime,
        effective_position=pd.Series(pos_trace, index=idx, name="eff_pos"),
        n_switches=n_switches,
        cum_cost_pct=cum_cost,
        cum_tax_pct=cum_tax,
        trades=trades,
        n_stops_triggered=n_stops_triggered,
        stop_events=stop_events,
    )
