"""Kalman-filter dynamic hedge-ratio pair-trading with Engle-Granger gate.

V2-L5 (Phase 3.5a-V2) canonical implementation of the market-neutral
statistical-arbitrage family for equity ETF pairs. This module is
daily-frequency only and single-config (the V2 spec fixes the parameter
tuple — see ``KalmanPairConfig`` defaults). A fan-out sweep across six
pairs (GLD/SLV, QQQ/XLK, SPY/IWM, TLT/IEF, XLE/USO, XLF/HYG) is driven
by ``scripts/iter_v2_l5_run_pair.py``.

Design
------
1. **Cointegration gate (Engle-Granger two-step)** on the full series::

       y = a + b * x + residual
       ADF(residual) -> p-value < adf_alpha ?

   If ``p >= adf_alpha`` the pair is considered non-cointegrated and the
   rest of the pipeline returns a zero-return series (the downstream
   aggregator flags the pair as not investible). Reference:
   ``[algo_trading_chan, p.42-46]``.

2. **Kalman filter for dynamic [alpha, beta]** — state transition is a
   random walk with covariance ``Q = delta * I`` (small delta => beta
   moves slowly); observation equation ``y_t = alpha_t + beta_t * x_t +
   epsilon_t`` with ``V_e = observation_variance``. Hand-rolled two-
   dimensional Kalman filter so there is no optional dependency on
   ``pykalman``. Reference: ``[machine_trading_chan, ch.3]``.

3. **Innovation z-score** — the filter reports the innovation (``y_t -
   y_hat``) and its variance ``S_t``; ``z_t = innovation_t / sqrt(S_t)``
   is the standardised spread used for entry/exit. This is the canonical
   Kalman pair-trade signal ``[algo_trading_chan, p.47-50]``.

4. **Trading rules (market-neutral)** — signals act on bar ``t`` and
   positions apply to bar ``t+1`` returns (no look-ahead):

   * entry short-spread: ``z_t >= entry_z`` -> short y, long ``beta_t`` x
   * entry long-spread:  ``z_t <= -entry_z`` -> long y, short ``beta_t`` x
   * exit: ``|z_t| <= exit_z`` (default 0.0 -> mean reversion)
   * hard stop: ``|z_t| >= stop_z`` -> flat
   * time cap: flat after ``hold_cap_days`` calendar bars in position

5. **Costs** — the pair is a single round-trip against a broker that
   charges costs per leg. Pepperstone Razor retail tier (from Phase
   3.5a-V2 spec §3) is applied on BOTH legs: spread half 2 bps x 2 +
   commission RT 6.6 bps + slippage RT 3.0 bps = ~13.6 bps per round-
   trip per leg, times two legs for a market-neutral pair.

6. **Swap drag** — applied daily while a position is open. Long equity
   CFD swap ``~-0.005%/day`` (``[docs/investment-mandate.md §3]``); the
   short leg earns a tiny credit but Pepperstone retail deducts the
   broker margin so the net is close to the long rate. We model both
   legs with the long rate conservatively.

The net daily return series is the per-bar mark-to-market P&L of the
position in spread units, minus swap, minus transaction costs booked at
the entry/exit bar. The series is dollar-neutral by construction: the
signal is on the unitless innovation, and the pair position is sized to
unit notional on the ``y`` leg with ``beta_t`` units on the ``x`` leg.

Limits
------
* ``hold_cap_days`` caps the *calendar-bar* hold (not the absolute time
  between entry and exit); this keeps the retail cost model well-
  defined even when the spread refuses to revert.
* The ``delta`` and ``observation_variance`` defaults match the values
  used in Chan's textbook implementation. They are intentionally not
  swept in V2-L5 to preserve the single-config fan-out contract
  (spec ``specs/phase_3_5a_v2.md`` §2 V2-L5).

Citations
---------
* Engle-Granger cointegration with ADF on residuals: Engle & Granger
  (1987), and Chan, ``[algo_trading_chan, p.42-46]``.
* Kalman dynamic hedge ratio for pairs:
  ``[machine_trading_chan, ch.3]``; ``[algo_trading_chan, p.47-54]``.
* Pepperstone Razor retail cost model: Phase 3.5a-V2 spec §3.
* Hold economics (retail cost amortization; at least 3-day median
  hold): ``[systematic_trading, p.185-188]``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller


__all__ = [
    "KalmanPairConfig",
    "KalmanPairResult",
    "run_kalman_pair_pipeline",
]


@dataclass(frozen=True)
class KalmanPairConfig:
    """Canonical V2-L5 ``kalman_eg_2sigma_30d`` configuration.

    Defaults are the registry values — do not mutate at call sites; the
    fan-out spec (§2 V2-L5) fixes the tuple so the sweep is 1 config ×
    6 pairs.
    """

    # Cointegration gate (Engle-Granger two-step on full series)
    adf_alpha: float = 0.05
    """ADF rejection threshold on OLS residuals; pair must reject the
    unit-root null at 5% or tighter to be considered cointegrated."""

    # Kalman filter on [alpha, beta]
    delta: float = 1.0e-5
    """Process-noise scale for the state transition (Q = delta * I).
    Small delta ~ slowly varying hedge ratio; Chan's book default."""
    observation_variance: float = 1.0e-3
    """Observation-noise variance V_e in the filter."""

    # Trading rules
    entry_z: float = 2.0
    exit_z: float = 0.0
    stop_z: float = 4.0
    hold_cap_days: int = 30

    # Pepperstone Razor retail cost model (per leg)
    spread_half_bps: float = 2.0
    commission_round_trip_bps: float = 6.6
    slippage_bps_round_trip: float = 3.0
    """Round-trip transaction cost per leg (bps of notional)."""

    swap_daily_pct_long: float = -5.0e-5
    """Long equity CFD swap: -0.005%/day. Short leg assumed same drag
    conservatively (Pepperstone keeps the fed-funds spread)."""


@dataclass
class KalmanPairResult:
    """Pipeline output for a single pair."""

    pair_name: str
    daily_returns: pd.Series
    cointegration: dict
    """Engle-Granger ADF detail: residual ADF stat, p-value, whether
    the pair is cointegrated."""

    trade_ledger: list[dict] = field(default_factory=list)
    """One dict per closed round-trip, with entry/exit bar indexes and
    gross/net P&L in spread units."""

    median_hold_days: float = 0.0
    n_events_total: int = 0
    n_events_taken: int = 0
    cum_transaction_cost_pct: float = 0.0
    cum_swap_cost_pct: float = 0.0
    kalman_final_beta: float = 0.0


# ---------------------------------------------------------------------------
# Engle-Granger cointegration gate
# ---------------------------------------------------------------------------


def _engle_granger(y: pd.Series, x: pd.Series, alpha: float) -> dict:
    """OLS log(y) = a + b*log(x) + residuals; ADF on residuals; pass iff p < alpha.

    Working in log prices matches the Kalman filter step (also on log
    prices) and is the textbook choice for long-horizon ETF pairs
    (``[algo_trading_chan, p.42-46]``).
    """
    y_arr = np.log(np.asarray(y.values, dtype=float))
    x_arr = np.log(np.asarray(x.values, dtype=float))
    n = len(y_arr)
    if n < 30:
        return {
            "pass": False,
            "reason": f"n={n} < 30 bars",
            "ols_alpha": 0.0,
            "ols_beta": 0.0,
            "adf_stat": 0.0,
            "adf_p_value": 1.0,
        }
    # OLS with constant via numpy on log prices
    X = np.column_stack([np.ones(n), x_arr])
    coef, *_ = np.linalg.lstsq(X, y_arr, rcond=None)
    a_hat, b_hat = float(coef[0]), float(coef[1])
    residuals = y_arr - (a_hat + b_hat * x_arr)
    adf_stat, p_value, *_ = adfuller(residuals, autolag="AIC")
    return {
        "pass": bool(p_value < alpha),
        "reason": f"p={p_value:.4f}",
        "ols_alpha": a_hat,
        "ols_beta": b_hat,
        "adf_stat": float(adf_stat),
        "adf_p_value": float(p_value),
        "n_bars": n,
    }


# ---------------------------------------------------------------------------
# Kalman filter for dynamic [alpha, beta]
# ---------------------------------------------------------------------------


def _kalman_alpha_beta(
    y: np.ndarray,
    x: np.ndarray,
    delta: float,
    observation_variance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Hand-rolled 2-D Kalman filter for pair-trade hedge ratio.

    Returns (alpha[n], beta[n], innovation[n], innovation_variance[n]).
    The state at index 0 is the posterior after observing the first
    bar, so the filter does not peek ahead.
    """
    n = len(y)
    alpha = np.zeros(n)
    beta = np.zeros(n)
    innovation = np.zeros(n)
    innov_var = np.zeros(n)

    theta = np.zeros(2)
    P = np.eye(2) * 1.0
    Q = np.eye(2) * delta
    for t in range(n):
        # Predict
        theta_pred = theta
        P_pred = P + Q
        # Observe
        H = np.array([1.0, x[t]])
        y_hat = float(H @ theta_pred)
        S = float(H @ P_pred @ H + observation_variance)
        K = P_pred @ H / S  # Kalman gain (2,)
        innov = float(y[t] - y_hat)
        theta = theta_pred + K * innov
        P = P_pred - np.outer(K, H) @ P_pred

        alpha[t] = theta[0]
        beta[t] = theta[1]
        innovation[t] = innov
        innov_var[t] = S
    return alpha, beta, innovation, innov_var


# ---------------------------------------------------------------------------
# Trading simulation
# ---------------------------------------------------------------------------


def _simulate(
    y_close: pd.Series,
    x_close: pd.Series,
    alpha_t: np.ndarray,
    beta_t: np.ndarray,
    z_score: np.ndarray,
    cfg: KalmanPairConfig,
) -> tuple[pd.Series, list[dict], dict]:
    """Market-neutral pair-trade simulation with Pepperstone cost model.

    Alignment convention (no look-ahead):
      * ``z_score[t]`` is observed at close of bar ``t``.
      * Position change (entry or exit) is executed at open of bar ``t+1``.
      * ``position_bar[t] = +1`` -> long spread held during bar ``t``;
        its P&L is booked against bar ``t``'s close-to-close return.
      * Round-trip cost is split half at entry, half at exit; swap drag
        is applied daily while the position is open.

    Spread sign convention:
      * long spread  (+1) = long y, short ``beta_entry`` x
      * short spread (-1) = short y, long ``beta_entry`` x
    """
    n = len(y_close)
    y_ret = y_close.pct_change().fillna(0.0).to_numpy(dtype=float)
    x_ret = x_close.pct_change().fillna(0.0).to_numpy(dtype=float)

    pnl = np.zeros(n, dtype=float)
    transact_cost = np.zeros(n, dtype=float)
    swap_cost = np.zeros(n, dtype=float)

    trades: list[dict] = []
    position = 0  # position currently held (applies to the *next* bar onward)
    current_beta = 0.0
    current_entry = -1  # bar index where position started
    n_events_total = 0
    n_events_taken = 0

    # Half round-trip transaction cost per leg (bps -> fraction),
    # doubled for two legs (long one, short the other).
    half_rt_per_leg = (
        cfg.spread_half_bps  # one side only here
        + 0.5 * cfg.commission_round_trip_bps
        + 0.5 * cfg.slippage_bps_round_trip
    ) * 1e-4
    cost_one_side = 2.0 * half_rt_per_leg  # enter or exit, both legs
    # Daily swap drag (both legs priced at long rate conservatively)
    swap_daily = -2.0 * cfg.swap_daily_pct_long  # positive = fraction

    for t in range(1, n):
        # (1) Book PnL on bar t for the position carried into bar t
        if position != 0:
            spread_ret = (
                y_ret[t] - current_beta * x_ret[t]
                if position == +1
                else -y_ret[t] + current_beta * x_ret[t]
            )
            spread_ret -= swap_daily
            pnl[t] += spread_ret
            swap_cost[t] += swap_daily

        # (2) Observe signal at close of bar t -> decide exit or entry for bar t+1
        z = z_score[t]
        if position != 0:
            days_in = t - current_entry + 1  # inclusive bars held
            exit_reason: str | None = None
            if abs(z) >= cfg.stop_z:
                exit_reason = "stop"
            elif days_in >= cfg.hold_cap_days:
                exit_reason = "time"
            elif (position == +1 and z >= -cfg.exit_z) or (
                position == -1 and z <= cfg.exit_z
            ):
                exit_reason = "mean_reversion"
            if exit_reason is not None:
                # Exit cost hits bar t+1 when the order fills
                exit_bar = t + 1 if t + 1 < n else n - 1
                pnl[exit_bar] -= cost_one_side
                transact_cost[exit_bar] += cost_one_side
                trades.append(
                    {
                        "entry_bar": int(current_entry),
                        "exit_bar": int(exit_bar),
                        "hold_bars": int(days_in),
                        "direction": int(position),
                        "entry_beta": float(current_beta),
                        "exit_z": float(z),
                        "exit_reason": exit_reason,
                    }
                )
                position = 0
                current_beta = 0.0
                current_entry = -1
        if position == 0:
            if z >= cfg.entry_z:
                n_events_total += 1
                n_events_taken += 1
                position = -1
                current_beta = float(beta_t[t])
                current_entry = t + 1
                # Entry cost hits bar t+1 when the order fills
                if t + 1 < n:
                    pnl[t + 1] -= cost_one_side
                    transact_cost[t + 1] += cost_one_side
            elif z <= -cfg.entry_z:
                n_events_total += 1
                n_events_taken += 1
                position = +1
                current_beta = float(beta_t[t])
                current_entry = t + 1
                if t + 1 < n:
                    pnl[t + 1] -= cost_one_side
                    transact_cost[t + 1] += cost_one_side

    # Open position at end-of-data: force-close without extra cost
    if position != 0:
        days_in = (n - 1) - current_entry + 1
        trades.append(
            {
                "entry_bar": int(current_entry),
                "exit_bar": int(n - 1),
                "hold_bars": int(max(days_in, 1)),
                "direction": int(position),
                "entry_beta": float(current_beta),
                "exit_z": float(z_score[n - 1]),
                "exit_reason": "end_of_data",
            }
        )

    daily_returns = pd.Series(pnl, index=y_close.index, name="daily_returns")

    aggregates = {
        "n_events_total": n_events_total,
        "n_events_taken": n_events_taken,
        "cum_transaction_cost_pct": float(np.sum(transact_cost)),
        "cum_swap_cost_pct": float(np.sum(swap_cost)),
    }
    return daily_returns, trades, aggregates


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def run_kalman_pair_pipeline(
    y_close: pd.Series,
    x_close: pd.Series,
    pair_name: str,
    cfg: KalmanPairConfig | None = None,
) -> KalmanPairResult:
    """Run the full V2-L5 Kalman pair-trade pipeline on one pair.

    Parameters
    ----------
    y_close, x_close
        Aligned daily close-price series for the two legs of the pair.
        Index must be a DatetimeIndex; ``y`` is the dependent leg
        (signal is on ``y - beta * x``). Non-overlapping dates are
        dropped by inner-joining the two series.
    pair_name
        Human-readable pair label (e.g. ``"GLD_SLV"``).
    cfg
        Configuration; defaults to the V2-L5 canonical tuple.

    Returns
    -------
    KalmanPairResult
        ``.daily_returns`` is the net P&L series in fractional units
        (multiplicative equity curve via ``(1+r).cumprod()``).
    """
    if cfg is None:
        cfg = KalmanPairConfig()

    common = pd.concat(
        [y_close.rename("y"), x_close.rename("x")], axis=1, sort=True
    ).dropna()
    y_close = common["y"]
    x_close = common["x"]

    cointeg = _engle_granger(y_close, x_close, alpha=cfg.adf_alpha)

    # Kalman filter on log prices for numerical stability and to align
    # with the textbook formulation (log-returns -> sharpe).
    y_log = np.log(y_close.to_numpy(dtype=float))
    x_log = np.log(x_close.to_numpy(dtype=float))
    alpha_t, beta_t, innov, innov_var = _kalman_alpha_beta(
        y_log, x_log, delta=cfg.delta, observation_variance=cfg.observation_variance
    )
    z_score = innov / np.sqrt(np.where(innov_var > 0, innov_var, 1.0))

    if not cointeg["pass"]:
        # Non-cointegrated pair: return a zero-return series so the
        # aggregator records an explicit "not investible" verdict.
        zeros = pd.Series(
            np.zeros(len(y_close)), index=y_close.index, name="daily_returns"
        )
        return KalmanPairResult(
            pair_name=pair_name,
            daily_returns=zeros,
            cointegration=cointeg,
            trade_ledger=[],
            median_hold_days=0.0,
            n_events_total=0,
            n_events_taken=0,
            cum_transaction_cost_pct=0.0,
            cum_swap_cost_pct=0.0,
            kalman_final_beta=float(beta_t[-1]) if len(beta_t) else 0.0,
        )

    daily_returns, trades, agg = _simulate(
        y_close=y_close,
        x_close=x_close,
        alpha_t=alpha_t,
        beta_t=beta_t,
        z_score=z_score,
        cfg=cfg,
    )

    holds = [int(tr["hold_bars"]) for tr in trades]
    median_hold = float(np.median(holds)) if holds else 0.0

    return KalmanPairResult(
        pair_name=pair_name,
        daily_returns=daily_returns,
        cointegration=cointeg,
        trade_ledger=trades,
        median_hold_days=median_hold,
        n_events_total=int(agg["n_events_total"]),
        n_events_taken=int(agg["n_events_taken"]),
        cum_transaction_cost_pct=float(agg["cum_transaction_cost_pct"]),
        cum_swap_cost_pct=float(agg["cum_swap_cost_pct"]),
        kalman_final_beta=float(beta_t[-1]) if len(beta_t) else 0.0,
    )
