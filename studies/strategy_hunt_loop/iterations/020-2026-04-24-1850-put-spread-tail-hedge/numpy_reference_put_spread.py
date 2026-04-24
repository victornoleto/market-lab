"""Iter 020 — Hand-rolled numpy reference for G7 cross-lib parity.

Independent re-implementation of:
  * black_scholes_put
  * compute_put_spread_daily_returns (monthly-rolled put spread MtM)
  * apply_put_spread_hedged_stack (full pipeline)

Must agree with the pandas/pd-based version in ``put_spread_hedge.py``
to ≤ 3 pp CAGR per `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import sys
from math import erf, log, sqrt
from pathlib import Path

import numpy as np

ITER_DIR = Path(__file__).resolve().parent
ROOT = ITER_DIR.parents[3]
ITER_016_DIR = ROOT / "studies" / "strategy_hunt_loop" / "iterations" / "016-2026-04-24-1729-static-stack-vm-hybrid"
if str(ITER_016_DIR) not in sys.path:
    sys.path.append(str(ITER_016_DIR))

from numpy_reference_stack_vm import apply_static_stack_vm_np  # noqa: E402


SQRT_2 = sqrt(2.0)


def _norm_cdf_np(x: float) -> float:
    return 0.5 * (1.0 + erf(x / SQRT_2))


def black_scholes_put_np(
    S: float, K: float, T: float, sigma: float, r: float = 0.0,
) -> float:
    """Numpy-pure BS put price (scalar)."""
    if S <= 0 or K <= 0:
        raise ValueError("S, K must be > 0")
    if T < 0 or sigma < 0:
        raise ValueError("T, sigma must be >= 0")
    if T <= 1e-10:
        return max(K - S, 0.0)
    if sigma <= 1e-10:
        return max(K * np.exp(-r * T) - S, 0.0)
    sigma_sqrt_T = sigma * sqrt(T)
    d1 = (log(S / K) + (r + 0.5 * sigma * sigma) * T) / sigma_sqrt_T
    d2 = d1 - sigma_sqrt_T
    return K * np.exp(-r * T) * _norm_cdf_np(-d2) - S * _norm_cdf_np(-d1)


def _price_spread_np(S, K_long, K_short, T, sigma, r):
    return (
        black_scholes_put_np(S, K_long, T, sigma, r)
        - black_scholes_put_np(S, K_short, T, sigma, r)
    )


def compute_put_spread_daily_returns_np(
    prices_arr: np.ndarray,
    iv_arr: np.ndarray,
    *,
    k_long_pct: float,
    k_short_pct: float,
    dte_days: int,
    rf: float,
    iv_scale: float,
    cost_bps_per_roll: float,
) -> np.ndarray:
    """Numpy-pure put-spread daily return series.

    Inputs are raw arrays (already aligned and masked). ``iv_arr`` is
    in percentage (e.g. VIX in %) — scaling + /100 handled internally.
    """
    n = len(prices_arr)
    if n < 2:
        raise ValueError("need >= 2 bars")
    if k_short_pct >= k_long_pct:
        raise ValueError("k_short_pct must be < k_long_pct")

    ret = np.zeros(n)
    cost_frac = cost_bps_per_roll / 10000.0
    iv_decimal = iv_arr * iv_scale / 100.0

    S_entry = float(prices_arr[0])
    K_long = k_long_pct * S_entry
    K_short = k_short_pct * S_entry
    entry_idx = 0
    expiry_idx = min(entry_idx + dte_days, n - 1)

    T_0 = dte_days / 252.0
    sigma_0 = max(float(iv_decimal[0]), 1e-6)
    prev_value = _price_spread_np(
        S_entry, K_long, K_short, T_0, sigma_0, rf,
    )
    ret[0] = -cost_frac

    for i in range(1, n):
        S_t = float(prices_arr[i])
        sigma_t = max(float(iv_decimal[i]), 1e-6)
        T_remaining = max(0, expiry_idx - i) / 252.0
        current_value = _price_spread_np(
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
            prev_value = _price_spread_np(
                S_entry, K_long, K_short, T_0, sigma_t, rf,
            )
        else:
            prev_value = current_value

    return ret


def apply_put_spread_hedged_stack_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    prices_eq: np.ndarray,
    iv_arr: np.ndarray,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    k_long_pct: float,
    k_short_pct: float,
    dte_days: int,
    rf: float,
    iv_scale: float,
    cost_bps_per_roll: float,
    hedge_notional_ratio: float = 1.0,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy-pure full pipeline: put-spread overlay + iter 016 stack.

    Assumes r_eq, r_bd, prices_eq, iv_arr all aligned to SAME grid and
    drop-na already applied. Returns (net, pos_eq, pos_bd, scale) like
    the pandas version but as numpy arrays on the valid-scale window.
    """
    if len(r_eq) != len(r_bd) or len(r_eq) != len(prices_eq) or len(r_eq) != len(iv_arr):
        raise ValueError("r_eq, r_bd, prices_eq, iv_arr must have same length")

    overlay = compute_put_spread_daily_returns_np(
        prices_eq, iv_arr,
        k_long_pct=k_long_pct,
        k_short_pct=k_short_pct,
        dte_days=dte_days,
        rf=rf,
        iv_scale=iv_scale,
        cost_bps_per_roll=cost_bps_per_roll,
    )

    r_eq_hedged = r_eq + hedge_notional_ratio * overlay

    net, pos_eq, pos_bd, scale = apply_static_stack_vm_np(
        r_eq_hedged, r_bd,
        eq_weight=eq_weight,
        bd_weight=bd_weight,
        target_vol=target_vol,
        lookback=lookback,
        max_leverage=max_leverage,
        periods_per_year=periods_per_year,
        cost_bps_per_leg=cost_bps_per_leg,
    )
    return net, pos_eq, pos_bd, scale
