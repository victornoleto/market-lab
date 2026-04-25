"""Iter 026 — Pure-numpy reference for VRP-primary portfolio (G7 parity).

Replicates `vrp_primary.compute_vrp_primary_returns` using only numpy
+ math.erf (no pandas). Matches the pandas engine to floating-point
precision so iter 026 can satisfy G7 (cross-library ±3 pp CAGR) on
top of the iter 020 BS pricing inheritance.

Citations
---------
* `[volatility_trading, p.11]` — Black-Scholes pricing identity.
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

from math import erf, exp, log, sqrt

import numpy as np

SQRT_2 = sqrt(2.0)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / SQRT_2))


def _bs_put(S: float, K: float, T: float, sigma: float, r: float) -> float:
    """Black-Scholes European put price. Matches iter 020's primitive."""
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


def _compute_long_overlay_np(
    prices: np.ndarray,
    iv_raw: np.ndarray,
    *,
    k_long_pct: float,
    k_short_pct: float,
    dte_days: int,
    rf: float,
    iv_scale: float,
    cost_bps_per_roll: float,
) -> np.ndarray:
    """Pure-numpy replica of `compute_put_spread_daily_returns`.

    Same roll mechanics, same opening cost on day 0, same MtM logic.
    """
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

    n = len(prices)
    if n < 2:
        raise ValueError(f"need >= 2 aligned bars, got {n}")

    iv_arr = iv_raw * iv_scale / 100.0
    ret = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0

    S_entry = float(prices[0])
    K_long = k_long_pct * S_entry
    K_short = k_short_pct * S_entry
    entry_idx = 0
    expiry_idx = min(entry_idx + dte_days, n - 1)
    T_0 = dte_days / 252.0
    sigma_0 = max(float(iv_arr[0]), 1e-6)
    prev_value = _put_spread_value(S_entry, K_long, K_short, T_0, sigma_0, rf)
    ret[0] = -cost_frac

    for i in range(1, n):
        S_t = float(prices[i])
        sigma_t = max(float(iv_arr[i]), 1e-6)
        T_remaining = max(0, expiry_idx - i) / 252.0
        current_value = _put_spread_value(
            S_t, K_long, K_short, T_remaining, sigma_t, rf,
        )
        ret[i] = (current_value - prev_value) / S_entry
        if i >= expiry_idx and i < n - 1:
            ret[i] -= cost_frac
            S_entry = S_t
            K_long = k_long_pct * S_entry
            K_short = k_short_pct * S_entry
            entry_idx = i
            expiry_idx = min(entry_idx + dte_days, n - 1)
            prev_value = _put_spread_value(
                S_entry, K_long, K_short, T_0, sigma_t, rf,
            )
        else:
            prev_value = current_value

    return ret


def compute_vrp_primary_returns_np(
    prices: np.ndarray,
    iv_raw: np.ndarray,
    *,
    rf: float = 0.02,
    harvest_notional: float = 1.0,
    k_long_pct: float = 0.95,
    k_short_pct: float = 0.90,
    dte_days: int = 21,
    iv_scale: float = 1.0,
    cost_bps_per_roll: float = 5.0,
) -> np.ndarray:
    """Pure-numpy replica of `compute_vrp_primary_returns`.

    Returns a 1-D numpy array of daily strategy returns matching the
    pandas engine to float precision (modulo Series-vs-array boundary).
    """
    if harvest_notional < 0:
        raise ValueError(
            f"harvest_notional must be >= 0; got {harvest_notional}"
        )
    long_overlay = _compute_long_overlay_np(
        prices, iv_raw,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        rf=rf,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
    )
    rf_daily = (1.0 + rf) ** (1.0 / 252.0) - 1.0
    return rf_daily + harvest_notional * (-long_overlay)
