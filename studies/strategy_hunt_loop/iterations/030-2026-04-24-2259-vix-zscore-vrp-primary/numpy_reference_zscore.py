"""Iter 030 — Pure-numpy reference for VIX-z-score VRP-primary (G7 parity).

Replicates `vrp_zscore.compute_vrp_zscore_returns` using only numpy +
math.erf (no pandas). Matches the pandas engine to floating-point
precision.

Citations
---------
* `[volatility_trading, p.218]` — sustained vs transient (relative-shock).
* `[volatility_trading, p.39, p.58-59]` — VIX vol-of-vol + cone.
* `[volatility_trading, p.11]` — Black-Scholes pricing identity.
* `[advances_fin_ml, p.31-34]` — cross-library parity.
"""

from __future__ import annotations

from math import erf, exp, log, sqrt

import numpy as np

SQRT_2 = sqrt(2.0)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / SQRT_2))


def _bs_put(S: float, K: float, T: float, sigma: float, r: float) -> float:
    if S <= 0 or K <= 0:
        raise ValueError(f"S,K must be > 0; got S={S} K={K}")
    if T < 0:
        raise ValueError(f"T must be >= 0; got T={T}")
    if sigma < 0:
        raise ValueError(f"sigma must be >= 0; got sigma={sigma}")
    if T <= 1e-10:
        return max(K - S, 0.0)
    if sigma <= 1e-10:
        return max(K * exp(-r * T) - S, 0.0)
    sigma_sqrt_T = sigma * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    return K * exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def _put_spread_value(
    S: float, K_long: float, K_short: float,
    T: float, sigma: float, r: float,
) -> float:
    return _bs_put(S, K_long, T, sigma, r) - _bs_put(S, K_short, T, sigma, r)


def _is_z_high_np(z: np.ndarray, i: int, threshold: float) -> bool:
    val = z[i]
    if val != val:   # NaN
        return False
    return val >= threshold


def compute_vrp_zscore_returns_np(
    prices: np.ndarray,
    iv_raw: np.ndarray,
    vix_zscore: np.ndarray,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
    z_threshold: float = 2.0,
) -> np.ndarray:
    """Pure-numpy replica of `compute_vrp_zscore_returns`.

    Same parameter semantics. Returns 1-D numpy array of daily strategy
    returns matching the pandas engine to float precision.
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
    if len(prices) != len(iv_raw) or len(prices) != len(vix_zscore):
        raise ValueError(
            "prices, iv_raw, vix_zscore must share length; "
            f"got {len(prices)}, {len(iv_raw)}, {len(vix_zscore)}"
        )

    n = len(prices)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    iv_priced = iv_raw * iv_scale / 100.0
    overlay = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0
    T_0 = dte_days / 252.0
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0

    position_open = False
    S_entry = 0.0
    K_long = 0.0
    K_short = 0.0
    expiry_idx = -1
    prev_value = 0.0

    if not _is_z_high_np(vix_zscore, 0, z_threshold):
        position_open = True
        S_entry = float(prices[0])
        K_long = k_long_pct * S_entry
        K_short = k_short_pct * S_entry
        expiry_idx = min(0 + dte_days, n - 1)
        sigma_0 = max(float(iv_priced[0]), 1e-6)
        prev_value = _put_spread_value(
            S_entry, K_long, K_short, T_0, sigma_0, rf,
        )
        overlay[0] = -cost_frac
    else:
        expiry_idx = min(0 + dte_days, n - 1)

    for i in range(1, n):
        S_t = float(prices[i])
        sigma_t = max(float(iv_priced[i]), 1e-6)

        if position_open:
            T_remaining = max(0, expiry_idx - i) / 252.0
            current_value = _put_spread_value(
                S_t, K_long, K_short, T_remaining, sigma_t, rf,
            )
            overlay[i] = (current_value - prev_value) / S_entry

            if i >= expiry_idx and i < n - 1:
                overlay[i] -= cost_frac
                if not _is_z_high_np(vix_zscore, i, z_threshold):
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _put_spread_value(
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
                if not _is_z_high_np(vix_zscore, i, z_threshold):
                    position_open = True
                    S_entry = S_t
                    K_long = k_long_pct * S_entry
                    K_short = k_short_pct * S_entry
                    expiry_idx = min(i + dte_days, n - 1)
                    prev_value = _put_spread_value(
                        S_entry, K_long, K_short, T_0, sigma_t, rf,
                    )
                    overlay[i] = -cost_frac
                else:
                    expiry_idx = min(i + dte_days, n - 1)

    return rf_daily + harvest_notional * (-overlay)
