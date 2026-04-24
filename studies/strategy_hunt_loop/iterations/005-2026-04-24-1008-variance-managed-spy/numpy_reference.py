"""G7 cross-lib reference — pure-numpy variance-target + CAGR/Sharpe.

Mirrors iter 004's ``numpy_reference.py`` but with the ``σ^{-2}`` form.
Used by the G7 gate to check that the pandas-based ``variance_target``
path and this independent numpy re-implementation agree to ±3 pp CAGR
on all 12 × 3 = 36 ``(cfg, dataset)`` pairs.

Citations
---------
* Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — variance-scaling canonical.
* ``[advances_fin_ml, p.31-34]`` — cross-library parity as correctness gate.
"""

from __future__ import annotations

import numpy as np


def apply_variance_target_np(
    returns: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_roundtrip: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy variance-target: returns (net_returns, scale) after drop.

    The scale on bar ``t`` uses the rolling std over ``[t-lookback, t-1]``
    squared and annualised (no look-ahead). The first ``lookback`` bars
    have no valid scale and are dropped from the output.
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")

    r = np.asarray(returns, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n <= lookback:
        raise ValueError(f"need > {lookback} bars, got {n}")

    ann_var_prev = np.full(n, np.nan)
    for t in range(lookback, n):
        window = r[t - lookback : t]
        ann_vol = window.std(ddof=0) * np.sqrt(periods_per_year)
        ann_var_prev[t] = ann_vol ** 2

    target_var = target_vol ** 2
    scale = np.full(n, np.nan)
    valid_pos = ann_var_prev > 0
    valid_zero = ann_var_prev == 0
    scale[valid_pos] = target_var / ann_var_prev[valid_pos]
    scale[valid_zero] = max_leverage
    scale = np.clip(scale, 0.0, max_leverage)

    mask = ~np.isnan(scale)
    scale_valid = scale[mask]
    r_valid = r[mask]

    dscale = np.empty_like(scale_valid)
    dscale[0] = abs(scale_valid[0])
    dscale[1:] = np.abs(np.diff(scale_valid))
    cost = dscale * cost_bps_roundtrip

    gross = scale_valid * r_valid
    net = gross - cost
    return net, scale_valid


def sharpe_np(
    returns: np.ndarray,
    *,
    periods_per_year: int = 252,
    risk_free: float = 0.0,
) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) == 0:
        return 0.0
    std = r.std(ddof=0)
    if std <= 1e-12:
        return 0.0
    return float((r.mean() - risk_free) / std * np.sqrt(periods_per_year))


def cagr_np(returns: np.ndarray, *, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    years = len(r) / periods_per_year
    if years <= 0 or eq[-1] <= 0:
        return 0.0
    return float(eq[-1] ** (1.0 / years) - 1.0)


def max_drawdown_np(returns: np.ndarray) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    return float(abs(dd.min()))
