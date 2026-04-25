"""Iter 029 — VIX-persistence VRP-primary (R-1): only skip open when VIX >= threshold for >= persistence_days consecutive bars.

Builds on iter 028's `vrp_filtered.py` with one structural change: the
open-gate condition checks the trailing window of length
``persistence_days`` rather than the single contemporaneous bar.

Mechanics
---------

Convention is identical to iter 020/026/028 — the internal ``overlay``
array records the **long-holder's** daily P&L (in fractions of
``S_entry``); costs are charged as negative entries (long pays). The
strategy is then ``rf_daily + harvest_notional * (-overlay)``. With
``persistence_days = 1`` this engine reproduces iter 028 exactly; with
``vix_threshold = 1e9`` it reproduces iter 026 exactly.

State machine (iter 029 specific):

  * ``OPEN`` — a position is currently held; daily MtM is computed; on
    the natural expiry/roll bar the position is closed (cost charged to
    long-holder) and a new one is opened **only if NOT
    ``is_persistent_high(vix, i, threshold, persistence_days)``**.
    Otherwise the strategy transitions to ``HOLD-CASH``.
  * ``HOLD-CASH`` — no position; daily ``overlay`` contribution is 0;
    re-evaluation occurs every ``dte_days`` bars (the same cadence as a
    natural roll). When the persistence gate clears, transition back to
    ``OPEN``.

Bar 0 special-case: ``is_persistent_high`` is False whenever
``i < persistence_days - 1`` (insufficient history), so the strategy
opens at bar 0.

Citations
---------
* `[volatility_trading, p.217]` — Sinclair (2013) ch. 8 §"Hedging short
  volatility positions": VIX < 35 entry filter for short index-vol
  (level component; refined by iter 028).
* `[volatility_trading, p.218]` — Sinclair §"VIX-VXV term structure":
  *sustained* high IV is the warning sign for short-vol writers, not
  single-day spikes (persistence component motivation).
* `[volatility_trading, ch.3, p.41]` — VRP mechanics + SPX excess
  kurtosis 21.3 (capped-tail rationale).
* `[volatility_trading, p.11]` — BSM pricing identity.
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Bondarenko (2014) QJF 4(3) 1450015 §3 — *persistent* high-IV regimes
  carry asymmetric tail risk; transient spikes rarely breach.
* Carr-Wu (2009) RFS 22(3) 1311-1341 — VRP level/persistence
  decomposition.
* Whaley (2009) JPM 35(3) 98-105 — VIX spike-and-revert vs. persistent
  regime characterization.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_020_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / \
    "020-2026-04-24-1850-put-spread-tail-hedge"
if str(ITER_020_DIR) not in sys.path:
    sys.path.append(str(ITER_020_DIR))

from put_spread_hedge import _price_put_spread  # noqa: E402


def is_persistent_high(
    vix: np.ndarray, i: int, threshold: float, persistence_days: int,
) -> bool:
    """True iff vix[i-k+1..i] are all >= threshold (k = persistence_days).

    False when ``i < persistence_days - 1`` (insufficient history).
    """
    if persistence_days < 1:
        raise ValueError(
            f"persistence_days must be >= 1; got {persistence_days}"
        )
    if i < persistence_days - 1:
        return False
    for j in range(i - persistence_days + 1, i + 1):
        if vix[j] < threshold:
            return False
    return True


def compute_vrp_persistence_returns(
    prices: pd.Series,
    iv_series: pd.Series,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    vix_threshold: float = 35.0,
    persistence_days: int = 3,
) -> pd.Series:
    """Daily fractional returns of the VIX-persistence-filtered VRP-primary portfolio.

    Identical to iter 028's `compute_vrp_filtered_returns` except the
    open-gate uses ``is_persistent_high(vix, i, threshold,
    persistence_days)`` rather than a single-bar comparison.

    Setting ``persistence_days = 1`` reproduces iter 028 exactly.
    Setting ``vix_threshold = 1e9`` reproduces iter 026 exactly.

    Parameters
    ----------
    prices, iv_series : pd.Series
        Equity adj_close + IV (% units). Aligned via inner-join.
    rf : float
        Annualised risk-free rate. Default 0.02.
    harvest_notional : float
        Non-negative scaling on the short-writer overlay.
    k_long_pct, k_short_pct, dte_days, iv_scale, cost_bps_per_roll :
        Inherited from iter 020/026/028.
    vix_threshold : float
        Open-gate level threshold in IV-series units. Must be >= 0.
        Default 35.0 (Sinclair p.217).
    persistence_days : int
        Number of trailing consecutive bars (inclusive of current bar)
        that must satisfy ``vix >= vix_threshold`` for the gate to
        skip the open. Must be >= 1. Default 3 (Bondarenko 2014 §3
        empirical persistence definition).

    Returns
    -------
    pd.Series of daily strategy returns aligned to the inner-join index.

    Raises
    ------
    ValueError if param bounds are violated.
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}."
        )
    if vix_threshold < 0:
        raise ValueError(
            f"vix_threshold must be >= 0; got {vix_threshold}."
        )
    if persistence_days < 1:
        raise ValueError(
            f"persistence_days must be >= 1; got {persistence_days}."
        )
    if k_short_pct >= k_long_pct:
        raise ValueError(
            f"k_short_pct must be < k_long_pct; "
            f"got k_short={k_short_pct}, k_long={k_long_pct}"
        )
    if not (0 < k_short_pct < 1 and 0 < k_long_pct < 1):
        raise ValueError("strike pcts must be in (0, 1)")
    if dte_days < 2:
        raise ValueError(f"dte_days must be >= 2; got {dte_days}")
    if cost_bps_per_roll < 0:
        raise ValueError(f"cost_bps must be >= 0; got {cost_bps_per_roll}")
    if iv_scale <= 0:
        raise ValueError(f"iv_scale must be > 0; got {iv_scale}")

    aligned = pd.concat(
        {"price": prices.astype(float), "iv_raw": iv_series.astype(float)},
        axis=1, join="inner",
    ).dropna()
    n = len(aligned)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    prices_arr = aligned["price"].to_numpy()
    iv_raw_arr = aligned["iv_raw"].to_numpy()       # gate input (raw VIX)
    iv_priced_arr = iv_raw_arr * iv_scale / 100.0   # BS pricer input
    dates = aligned.index

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    overlay = np.zeros(n)  # long-holder convention (see module docstring)
    cost_frac = cost_bps_per_roll / 10000.0
    T_0 = dte_days / 252.0

    # --- State machine: OPEN or HOLD-CASH ------------------------------
    position_open = False
    S_entry = 0.0
    K_long = 0.0
    K_short = 0.0
    expiry_idx = -1
    prev_value = 0.0

    # Bar 0 — open or skip
    if not is_persistent_high(iv_raw_arr, 0, vix_threshold, persistence_days):
        position_open = True
        S_entry = float(prices_arr[0])
        K_long = k_long_pct * S_entry
        K_short = k_short_pct * S_entry
        expiry_idx = min(0 + dte_days, n - 1)
        sigma_0 = max(float(iv_priced_arr[0]), 1e-6)
        prev_value = _price_put_spread(
            S_entry, K_long, K_short, T_0, sigma_0, rf,
        )
        overlay[0] = -cost_frac        # long pays opening commission
    else:
        # HOLD-CASH from start; next eval bar is dte_days bars away
        expiry_idx = min(0 + dte_days, n - 1)

    for i in range(1, n):
        S_t = float(prices_arr[i])
        sigma_t = max(float(iv_priced_arr[i]), 1e-6)

        if position_open:
            T_remaining = max(0, expiry_idx - i) / 252.0
            current_value = _price_put_spread(
                S_t, K_long, K_short, T_remaining, sigma_t, rf,
            )
            # Long-holder daily MtM (positive when spread value rises)
            overlay[i] = (current_value - prev_value) / S_entry

            if i >= expiry_idx and i < n - 1:
                # Roll bar — close (cost charged to long), then decide
                overlay[i] -= cost_frac
                if not is_persistent_high(
                    iv_raw_arr, i, vix_threshold, persistence_days,
                ):
                    # Open new position; cost above covers close+open
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                else:
                    # Skip new open; switch to HOLD-CASH
                    position_open = False
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = 0.0
            else:
                prev_value = current_value
        else:
            # HOLD-CASH: 0 overlay; re-evaluate every dte_days
            if i >= expiry_idx and i < n - 1:
                if not is_persistent_high(
                    iv_raw_arr, i, vix_threshold, persistence_days,
                ):
                    # Re-open
                    position_open = True
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                    overlay[i] = -cost_frac    # opening cost
                else:
                    # Stay in HOLD-CASH for another window
                    expiry_idx = min(i + dte_days, n - 1)
            # else: still inside the HOLD-CASH gap, overlay stays 0

    # Strategy = T-bill + short-writer (= -long-holder) overlay
    strategy = rf_daily + harvest_notional * (-overlay)
    return pd.Series(strategy, index=dates, name="vrp_persistence_return")
