"""G7 cross-lib reference — hand-rolled numpy vol-target + Sharpe/CAGR.

The production implementation (``ai_trade.backtest.metrics.vol_target``) uses
pandas rolling windows. This module re-implements the same contract in pure
numpy (no pandas, no helper imports from the project) so the gate can verify
the two paths agree to ±3 pp CAGR on all 36 × 3 = 108 (cfg, dataset) pairs.

Citations
---------
* [advances_fin_ml, p.31-34] — cross-library parity as a correctness gate
* [systematic_trading, p.107-111] — canonical vol-target formula
"""

from __future__ import annotations

import numpy as np


def apply_vol_target_np(
    returns: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_roundtrip: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray]:
    """Pure-numpy vol-target: returns (net_returns, scale) after drop.

    The scale on bar ``t`` uses the rolling std over ``[t-lookback, t-1]``
    (no look-ahead). The first ``lookback`` bars have no valid scale and
    are dropped from the output. ``scale`` and ``net_returns`` share the
    same length (post-drop).

    Notes
    -----
    We compute ``std`` with ``ddof=0`` to match
    ``pd.Series.rolling(L).std(ddof=0)`` in the production path. The
    turnover cost on the first output bar uses ``|scale[0] - 0|`` to
    match the production path's ``diff().fillna(scale[0])`` behaviour.
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

    # Rolling annualised std on [t-L, t-1] for t ∈ [L+1, n-1].
    # Output valid bars: t = L+1 .. n-1 → count = n - L - 1.
    # Pandas `rolling(L, min_periods=L).std(ddof=0).shift(1)` gives σ̂_{t-1}
    # at bar t, which is defined for t ∈ [L, n-1] but NaN at t = L (first
    # valid rolling std lands at index L-1 in pandas; shift(1) → index L;
    # but value at index L uses window [0, L-1]; shift makes it land at
    # index L which is our bar t=L ... wait, the production code uses
    # `min_periods=lookback` so the first non-NaN rolling.std lands at
    # index L-1 (0-indexed).  shift(1) moves it to index L.  So σ̂_{t-1}
    # is valid for t ∈ [L, n-1] and the scaled series has length n - L.
    # However the production drops NaN at the end, so we match exactly.

    # Build σ̂_{t-1} (annualised) for t in [0, n-1]:
    ann_vol_prev = np.full(n, np.nan)
    for t in range(lookback, n):
        window = r[t - lookback : t]  # length L, indices [t-L, t-1]
        ann_vol_prev[t] = window.std(ddof=0) * np.sqrt(periods_per_year)

    # Compute scale:
    scale = np.full(n, np.nan)
    valid_pos = ann_vol_prev > 0
    valid_zero = ann_vol_prev == 0
    scale[valid_pos] = target_vol / ann_vol_prev[valid_pos]
    scale[valid_zero] = max_leverage
    scale = np.clip(scale, 0.0, max_leverage)

    # Drop the leading NaN bars.
    mask = ~np.isnan(scale)
    scale_valid = scale[mask]
    r_valid = r[mask]

    # Execution cost: |Δs| · cost_bps; first bar uses |scale[0] - 0|.
    dscale = np.empty_like(scale_valid)
    dscale[0] = abs(scale_valid[0])  # ramp from 0
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
    """Annualised Sharpe matching ``performance.sharpe`` (ddof=0, per-period rf)."""
    r = np.asarray(returns, dtype=float)
    if len(r) == 0:
        return 0.0
    std = r.std(ddof=0)
    if std <= 1e-12:
        return 0.0
    return float((r.mean() - risk_free) / std * np.sqrt(periods_per_year))


def cagr_np(returns: np.ndarray, *, periods_per_year: int = 252) -> float:
    """Annualised compound growth rate from returns → equity → CAGR."""
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    years = len(r) / periods_per_year
    if years <= 0 or eq[-1] <= 0:
        return 0.0
    return float(eq[-1] ** (1.0 / years) - 1.0)


def max_drawdown_np(returns: np.ndarray) -> float:
    """Max drawdown (positive magnitude) from returns → equity."""
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    return float(abs(dd.min()))
