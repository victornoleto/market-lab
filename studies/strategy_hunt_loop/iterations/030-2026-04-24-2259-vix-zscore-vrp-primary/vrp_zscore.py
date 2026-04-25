"""Iter 030 — VIX z-score VRP-primary (R-2): only skip the open when the
*standardized* VIX deviation over a 60-day rolling window exceeds 2.0σ.

Builds on iter 029's `vrp_persistence.py` with one structural change: the
open-gate consumes a precomputed z-score series rather than a level
threshold or persistence window.

Mechanics
---------

Convention is identical to iter 020/026/028/029 — the internal ``overlay``
array records the **long-holder's** daily P&L (in fractions of
``S_entry``); costs are charged as negative entries (long pays). The
strategy is then ``rf_daily + harvest_notional * (-overlay)``.

The z-score series is computed externally (see :func:`rolling_zscore`)
from a buffered VIX history so the warmup window is already populated
when the aligned price series begins. The first ``window - 1`` aligned
bars may still have NaN z (if the buffer is exhausted); the engine
treats NaN as "do NOT skip" — defaulting to OPEN, the same convention
as iter 029's persistence helper for ``i < persistence_days - 1``.

State machine (iter 030 specific):

  * ``OPEN`` — a position is held; daily MtM is computed; on the natural
    expiry/roll bar the position closes (cost charged) and a new one
    opens **only if NOT z[i] >= z_threshold** (or NaN z, which means
    "no signal yet → open"). Otherwise transition to ``HOLD-CASH``.
  * ``HOLD-CASH`` — no position; daily ``overlay`` contribution is 0;
    re-evaluation occurs every ``dte_days`` bars.

With ``z_threshold = 1e9`` this engine reproduces iter 026 exactly.

Citations
---------
* `[volatility_trading, p.218]` — Sinclair (2013) ch. 8 §"VIX-VXV term
  structure": *sustained* high IV is the warning sign for short-vol
  writers, not single-bar level. Iter 030 implements the relative-
  shock interpretation of "sustained": shocks defined relative to the
  prevailing 60d regime baseline.
* `[volatility_trading, p.39]` — VIX has annualized daily vol-of-vol
  0.96, weekly 0.84, monthly 0.59 (1990-2011). Regime-dependent
  dispersion motivates standardizing absolute moves by rolling scale.
* `[volatility_trading, p.58-59]` — volatility cone with realized-vol
  percentiles across 20/40/60/120/240 days. The 60d window is the
  canonical middle horizon.
* `[volatility_trading, p.214]` — variance premium (unchanged).
* `[volatility_trading, ch.3, p.41]` — VRP mechanics (unchanged).
* `[volatility_trading, p.11]` — BSM identity (unchanged).
* `[advances_fin_ml, p.31-34]` — cross-library parity (G7).
* Whaley (2009) JPM 35(3) — VIX innovation analysis using
  standardized deviations.
* Bondarenko (2014) QJF 4(3) §3 — persistent regimes.
* Carr-Wu (2009) RFS 22(3) — VRP level/persistence/innovation
  decomposition.
"""

from __future__ import annotations

import math
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


def rolling_zscore(
    vix: pd.Series,
    window: int = 60,
) -> pd.Series:
    """Rolling z-score (x - mean) / std on a pandas Series.

    Uses sample std (ddof=1) and the bar's own value in the rolling
    window (closed='right'). The first ``window - 1`` indices are NaN.

    Parameters
    ----------
    vix : pd.Series
        Raw VIX series (must already include any pre-window buffer the
        caller wants in the warmup).
    window : int
        Rolling window length. Must be >= 2. Default 60 (Sinclair p.58
        cone middle horizon; ~3 calendar months).

    Returns
    -------
    pd.Series with same index as ``vix``; first ``window - 1`` indices
    are NaN; remainder are (vix[t] - rolling_mean) / rolling_std.

    Raises
    ------
    ValueError if ``window < 2``.
    """
    if window < 2:
        raise ValueError(f"window must be >= 2; got {window}")
    mu = vix.rolling(window=window, min_periods=window).mean()
    sigma = vix.rolling(window=window, min_periods=window).std(ddof=1)
    return (vix - mu) / sigma


def is_z_high(z: np.ndarray, i: int, threshold: float) -> bool:
    """True iff z[i] is finite AND z[i] >= threshold.

    NaN z (warmup) → False (do not skip → default to open).
    """
    val = z[i]
    if val != val:   # NaN check (NaN != NaN)
        return False
    return val >= threshold


def compute_vrp_zscore_returns(
    prices: pd.Series,
    iv_series: pd.Series,
    vix_zscore: pd.Series,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    z_threshold: float = 2.0,
) -> pd.Series:
    """Daily fractional returns of the VIX-z-score-filtered VRP-primary portfolio.

    Identical to iter 029's `compute_vrp_persistence_returns` except the
    open-gate consumes ``vix_zscore`` (precomputed externally) rather
    than checking a level + persistence window. Setting
    ``z_threshold = 1e9`` reproduces iter 026 exactly.

    Parameters
    ----------
    prices, iv_series : pd.Series
        Equity adj_close + IV (% units). Aligned via inner-join on
        their union index, dropna.
    vix_zscore : pd.Series
        Precomputed z-score series. Must share dates with the prices /
        iv_series inner-join post-alignment. NaN values (warmup) are
        treated as "no signal → open".
    rf : float
        Annualised risk-free rate. Default 0.02.
    harvest_notional : float
        Non-negative scaling on the short-writer overlay.
    k_long_pct, k_short_pct, dte_days, iv_scale, cost_bps_per_roll :
        Inherited from iter 020/026/028/029.
    z_threshold : float
        Z-score level above which the gate fires (skip open). Must be
        >= 0. Default 2.0 (~97.7th percentile under normality).

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
    if z_threshold < 0:
        raise ValueError(
            f"z_threshold must be >= 0; got {z_threshold}."
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
        {
            "price": prices.astype(float),
            "iv_raw": iv_series.astype(float),
            "vix_z": vix_zscore.astype(float),
        },
        axis=1,
        join="inner",
    )
    # Drop rows where price or iv_raw is NaN (preserve NaN z as warmup).
    aligned = aligned.dropna(subset=["price", "iv_raw"])
    n = len(aligned)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    prices_arr = aligned["price"].to_numpy()
    iv_raw_arr = aligned["iv_raw"].to_numpy()
    iv_priced_arr = iv_raw_arr * iv_scale / 100.0
    z_arr = aligned["vix_z"].to_numpy()
    dates = aligned.index

    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    overlay = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0
    T_0 = dte_days / 252.0

    position_open = False
    S_entry = 0.0
    K_long = 0.0
    K_short = 0.0
    expiry_idx = -1
    prev_value = 0.0

    # Bar 0
    if not is_z_high(z_arr, 0, z_threshold):
        position_open = True
        S_entry = float(prices_arr[0])
        K_long = k_long_pct * S_entry
        K_short = k_short_pct * S_entry
        expiry_idx = min(0 + dte_days, n - 1)
        sigma_0 = max(float(iv_priced_arr[0]), 1e-6)
        prev_value = _price_put_spread(
            S_entry, K_long, K_short, T_0, sigma_0, rf,
        )
        overlay[0] = -cost_frac
    else:
        expiry_idx = min(0 + dte_days, n - 1)

    for i in range(1, n):
        S_t = float(prices_arr[i])
        sigma_t = max(float(iv_priced_arr[i]), 1e-6)

        if position_open:
            T_remaining = max(0, expiry_idx - i) / 252.0
            current_value = _price_put_spread(
                S_t, K_long, K_short, T_remaining, sigma_t, rf,
            )
            overlay[i] = (current_value - prev_value) / S_entry

            if i >= expiry_idx and i < n - 1:
                overlay[i] -= cost_frac
                if not is_z_high(z_arr, i, z_threshold):
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                else:
                    position_open = False
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = 0.0
            else:
                prev_value = current_value
        else:
            if i >= expiry_idx and i < n - 1:
                if not is_z_high(z_arr, i, z_threshold):
                    position_open = True
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _price_put_spread(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                    overlay[i] = -cost_frac
                else:
                    expiry_idx = min(i + dte_days, n - 1)

    strategy = rf_daily + harvest_notional * (-overlay)
    return pd.Series(strategy, index=dates, name="vrp_zscore_return")
