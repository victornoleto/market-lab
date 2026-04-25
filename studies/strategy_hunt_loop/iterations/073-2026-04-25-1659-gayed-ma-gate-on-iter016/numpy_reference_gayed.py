"""Iter 073 — Hand-rolled numpy reference for cross-library parity (G7).

Pure-numpy re-implementation of ``apply_gayed_gate_stack``. Required
by gate G7: the two implementations must agree to ≤ 3 pp CAGR
(typically ≤ 1e-10 absolute on returns).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np


def _rolling_var_np(x: np.ndarray, window: int) -> np.ndarray:
    """Rolling population (ddof=0) variance. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        w = x[i - window + 1 : i + 1]
        out[i] = float(np.var(w, ddof=0))
    return out


def _rolling_cov_np(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    """Rolling population (ddof=0) covariance. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        xw = x[i - window + 1 : i + 1]
        yw = y[i - window + 1 : i + 1]
        out[i] = float(
            np.mean((xw - xw.mean()) * (yw - yw.mean()))
        )
    return out


def _rolling_mean_np(x: np.ndarray, window: int) -> np.ndarray:
    """Rolling mean. NaN for bars < window."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    if n < window:
        return out
    for i in range(window - 1, n):
        out[i] = float(np.mean(x[i - window + 1 : i + 1]))
    return out


def apply_gayed_gate_stack_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    px_eq: np.ndarray,
    *,
    eq_weight: float,
    bd_weight: float,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    ma_period: int = 200,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Numpy-pure re-implementation of ``apply_gayed_gate_stack``.

    Returns ``(net, pos_eq, pos_bd, scale, gate_on)`` truncated to bars
    where both the σ²_{t-1} window and the SMA_{t-1} window are valid.
    Same shape convention as the pandas version's ``.dropna()`` output.
    """
    if eq_weight < 0 or bd_weight < 0:
        raise ValueError("weights must be non-negative")
    total_w = eq_weight + bd_weight
    if total_w <= 0:
        raise ValueError("eq+bd weights must sum to > 0")
    if target_vol <= 0:
        raise ValueError("target_vol must be > 0")
    if lookback < 2:
        raise ValueError("lookback must be ≥ 2")
    if max_leverage <= 0:
        raise ValueError("max_leverage must be > 0")
    if ma_period < 2:
        raise ValueError("ma_period must be ≥ 2")

    n = len(r_eq)
    if len(r_bd) != n or len(px_eq) != n:
        raise ValueError("r_eq, r_bd, px_eq must all have the same length")

    w_eq = eq_weight / total_w
    w_bd = bd_weight / total_w

    var_eq = _rolling_var_np(r_eq, lookback) * periods_per_year
    var_bd = _rolling_var_np(r_bd, lookback) * periods_per_year
    cov = _rolling_cov_np(r_eq, r_bd, lookback) * periods_per_year

    shifted_var_eq = np.full(n, np.nan, dtype=float)
    shifted_var_bd = np.full(n, np.nan, dtype=float)
    shifted_cov = np.full(n, np.nan, dtype=float)
    shifted_var_eq[1:] = var_eq[:-1]
    shifted_var_bd[1:] = var_bd[:-1]
    shifted_cov[1:] = cov[:-1]

    ann_var_port = (
        w_eq ** 2 * shifted_var_eq
        + w_bd ** 2 * shifted_var_bd
        + 2.0 * w_eq * w_bd * shifted_cov
    )
    ann_var_port = np.where(ann_var_port < 0, 0.0, ann_var_port)

    target_var = target_vol ** 2
    scale_full = np.full(n, np.nan, dtype=float)
    mask_valid = ~np.isnan(ann_var_port)
    pos_mask = mask_valid & (ann_var_port > 0)
    zero_mask = mask_valid & (ann_var_port == 0)
    scale_full[pos_mask] = target_var / ann_var_port[pos_mask]
    scale_full[zero_mask] = max_leverage
    scale_full = np.clip(scale_full, 0.0, max_leverage)

    # Gayed gate via SMA on equity price.
    sma = _rolling_mean_np(px_eq, ma_period)
    px_lag = np.full(n, np.nan, dtype=float)
    sma_lag = np.full(n, np.nan, dtype=float)
    px_lag[1:] = px_eq[:-1]
    sma_lag[1:] = sma[:-1]
    gate_on_full = np.where(
        np.isnan(px_lag) | np.isnan(sma_lag),
        np.nan,
        (px_lag > sma_lag).astype(float),
    )

    # Combine warm-ups.
    keep = ~np.isnan(scale_full) & ~np.isnan(gate_on_full)
    idx_keep = np.where(keep)[0]
    scale = scale_full[idx_keep]
    gate_on = gate_on_full[idx_keep].astype(bool)

    # Positions.
    on_eq = w_eq * scale
    on_bd = w_bd * scale
    pos_eq = np.where(gate_on, on_eq, 0.0)
    pos_bd = np.where(gate_on, on_bd, 1.0)

    r_eq_v = r_eq[idx_keep]
    r_bd_v = r_bd[idx_keep]
    gross = pos_eq * r_eq_v + pos_bd * r_bd_v

    dpos_eq = np.empty_like(pos_eq)
    dpos_bd = np.empty_like(pos_bd)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    dpos_eq[1:] = np.abs(np.diff(pos_eq))
    dpos_bd[1:] = np.abs(np.diff(pos_bd))
    cost = (dpos_eq + dpos_bd) * cost_bps_per_leg

    net = gross - cost
    return net, pos_eq, pos_bd, scale, gate_on
