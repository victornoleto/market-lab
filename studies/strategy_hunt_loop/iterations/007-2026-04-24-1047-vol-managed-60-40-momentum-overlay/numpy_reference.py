"""Iter 007 — Numpy-only reference for blend × momentum overlay (G7 cross-lib).

Reimplements the compound mechanism of ``apply_blend_with_momentum_overlay``
(from ``momentum_overlay.py``) and the iter 006 reference blend in pure
numpy, so the G7 cross-library parity gate can verify ±3 pp CAGR on an
implementation with zero shared code-path.

Reference for CAGR calculation: ``[advances_fin_ml, p.31-34]`` (bar-level
return accumulation).
"""

from __future__ import annotations

import numpy as np


def _rolling_var_np(arr: np.ndarray, lookback: int) -> np.ndarray:
    """Rolling variance over ``lookback`` bars, ddof=0, shifted by 1.

    Out[t] = population variance of arr[t-lookback:t] (no-look-ahead).
    First ``lookback`` entries are NaN.
    """
    n = len(arr)
    out = np.full(n, np.nan, dtype=float)
    if n <= lookback:
        return out
    for t in range(lookback, n):
        window = arr[t - lookback:t]
        mu = window.mean()
        out[t] = ((window - mu) ** 2).mean()
    return out


def _rolling_cov_np(a: np.ndarray, b: np.ndarray, lookback: int) -> np.ndarray:
    """Rolling covariance ddof=0, shifted by 1."""
    n = len(a)
    out = np.full(n, np.nan, dtype=float)
    if n <= lookback:
        return out
    for t in range(lookback, n):
        wa = a[t - lookback:t]
        wb = b[t - lookback:t]
        mu_a, mu_b = wa.mean(), wb.mean()
        out[t] = ((wa - mu_a) * (wb - mu_b)).mean()
    return out


def apply_blend_variance_target_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy reference for iter 006 blend (no overlay)."""
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    if len(a) != len(b):
        raise ValueError("r_eq, r_bd length mismatch")
    n = len(a)

    var_a = _rolling_var_np(a, lookback) * periods_per_year
    var_b = _rolling_var_np(b, lookback) * periods_per_year
    cov_ab = _rolling_cov_np(a, b, lookback) * periods_per_year

    w_a = np.full(n, np.nan, dtype=float)
    mask_valid = ~np.isnan(var_a) & ~np.isnan(var_b)
    both_pos = mask_valid & (var_a > 0) & (var_b > 0)
    only_a_zero = mask_valid & (var_a == 0) & (var_b > 0)
    only_b_zero = mask_valid & (var_a > 0) & (var_b == 0)
    both_zero = mask_valid & (var_a == 0) & (var_b == 0)

    inv_a = np.where(both_pos, 1.0 / var_a, 0.0)
    inv_b = np.where(both_pos, 1.0 / var_b, 0.0)
    w_a[both_pos] = inv_a[both_pos] / (inv_a[both_pos] + inv_b[both_pos])
    w_a[only_a_zero] = 1.0
    w_a[only_b_zero] = 0.0
    w_a[both_zero] = 0.5
    w_b = 1.0 - w_a

    var_port = (
        w_a ** 2 * var_a
        + w_b ** 2 * var_b
        + 2.0 * w_a * w_b * cov_ab
    )
    var_port = np.where(np.isnan(var_port), np.nan,
                        np.maximum(var_port, 0.0))

    raw_scale = np.full(n, np.nan, dtype=float)
    target_var = target_vol ** 2
    pos_mask = mask_valid & (var_port > 0) & ~np.isnan(var_port)
    zero_mask = mask_valid & (var_port == 0) & ~np.isnan(var_port)
    raw_scale[pos_mask] = target_var / var_port[pos_mask]
    raw_scale[zero_mask] = max_leverage

    scale = np.clip(raw_scale, 0.0, max_leverage)

    pos_eq = scale * w_a
    pos_bd = scale * w_b

    # Keep lag structure: shift scale/positions by +1 so at bar t we use
    # σ̂_{t-1}. Actually in `stock_bond_blend.py` this is done via the
    # `.shift(1)` on the variance series before computing weights. Here
    # we applied the shift implicitly by rolling over `arr[t-lookback:t]`
    # (excluding bar t). That already gives the σ̂_{t-1} form per ddof
    # convention of the pandas implementation. Cross-check OK.

    # Compute returns only on bars where positions are defined.
    valid = ~np.isnan(scale)
    gross = np.zeros(n, dtype=float)
    gross[valid] = (pos_eq[valid] * a[valid]) + (pos_bd[valid] * b[valid])

    # Costs: |Δpos| per leg, initial bar = |pos[0]|.
    dpos_eq = np.zeros(n, dtype=float)
    dpos_bd = np.zeros(n, dtype=float)
    first_valid = np.argmax(valid) if valid.any() else n
    if first_valid < n:
        dpos_eq[first_valid] = abs(pos_eq[first_valid])
        dpos_bd[first_valid] = abs(pos_bd[first_valid])
        for t in range(first_valid + 1, n):
            if valid[t]:
                dpos_eq[t] = abs(pos_eq[t] - pos_eq[t - 1])
                dpos_bd[t] = abs(pos_bd[t] - pos_bd[t - 1])
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = gross - cost
    # Replace invalid bars with NaN so downstream agg can skip.
    net = np.where(valid, net, np.nan)
    return net, pos_eq, pos_bd, scale


def time_series_momentum_gate_np(
    prices: np.ndarray, *, lookback: int, skip: int,
) -> np.ndarray:
    """{0, 1} gate on a price array. Warmup bars are NaN."""
    n = len(prices)
    warmup = lookback + skip
    gate = np.full(n, np.nan, dtype=float)
    if n <= warmup:
        return gate
    for t in range(warmup, n):
        p_num = prices[t - skip]
        p_den = prices[t - skip - lookback]
        mom = p_num / p_den - 1.0
        gate[t] = 1.0 if mom > 0 else 0.0
    return gate


def apply_blend_with_momentum_overlay_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    price_signal: np.ndarray,
    *,
    blend_cfg: dict,
    overlay_cfg: dict,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy reference for overlay compound (G7 cross-lib for iter 007)."""
    r_eq = np.asarray(r_eq, dtype=float)
    r_bd = np.asarray(r_bd, dtype=float)
    prices = np.asarray(price_signal, dtype=float)

    # Base blend without cost.
    net_base, pos_eq_base, pos_bd_base, scale_base = apply_blend_variance_target_np(
        r_eq, r_bd,
        target_vol=blend_cfg["target_vol"],
        lookback=blend_cfg["lookback"],
        max_leverage=blend_cfg["max_leverage"],
        periods_per_year=periods_per_year,
        cost_bps_per_leg=0.0,
    )

    gate = time_series_momentum_gate_np(
        prices,
        lookback=overlay_cfg["lookback"],
        skip=overlay_cfg["skip"],
    )
    # Lag gate by one additional bar (strict causality).
    gate_eff = np.concatenate([[np.nan], gate[:-1]])

    n = len(r_eq)
    # Intersection: both base blend valid AND gate_eff defined.
    valid = (~np.isnan(scale_base)) & (~np.isnan(gate_eff))

    scale_ov = np.where(valid, scale_base * gate_eff, np.nan)
    pos_eq = np.where(valid, pos_eq_base * gate_eff, np.nan)
    pos_bd = np.where(valid, pos_bd_base * gate_eff, np.nan)

    gross = np.zeros(n, dtype=float)
    gross[valid] = pos_eq[valid] * r_eq[valid] + pos_bd[valid] * r_bd[valid]

    dpos_eq = np.zeros(n, dtype=float)
    dpos_bd = np.zeros(n, dtype=float)
    first_valid = np.argmax(valid) if valid.any() else n
    if first_valid < n:
        dpos_eq[first_valid] = abs(pos_eq[first_valid]) if not np.isnan(pos_eq[first_valid]) else 0.0
        dpos_bd[first_valid] = abs(pos_bd[first_valid]) if not np.isnan(pos_bd[first_valid]) else 0.0
        for t in range(first_valid + 1, n):
            if valid[t] and valid[t - 1]:
                dpos_eq[t] = abs(pos_eq[t] - pos_eq[t - 1])
                dpos_bd[t] = abs(pos_bd[t] - pos_bd[t - 1])
            elif valid[t]:
                dpos_eq[t] = abs(pos_eq[t])
                dpos_bd[t] = abs(pos_bd[t])
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = np.where(valid, gross - cost, np.nan)
    return net, pos_eq, pos_bd, scale_ov, gate_eff


def cagr_np(net_returns: np.ndarray, periods_per_year: int = 252) -> float:
    """CAGR from a daily net-return series (skipping NaN)."""
    r = np.asarray(net_returns, dtype=float)
    valid = ~np.isnan(r)
    r = r[valid]
    if len(r) == 0:
        return 0.0
    eq = np.cumprod(1.0 + r)
    years = len(r) / periods_per_year
    if years <= 0 or eq[-1] <= 0:
        return 0.0
    return float(eq[-1] ** (1.0 / years) - 1.0)
