"""G7 cross-lib reference — pure-numpy SPY+TLT blend + CAGR/Sharpe.

Independent re-implementation of ``stock_bond_blend.apply_blend_variance_target``
using only numpy loops. Used by the G7 gate to check that the pandas-
based path and this numpy path agree to ±3 pp CAGR on all 12 × 3 = 36
(cfg, dataset) pairs per ``[advances_fin_ml, p.31-34]``.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity inverse-variance
  weighting is exact ERC for two-asset portfolios.
* Moreira & Muir (2017), *JoF* 72(4), 1611-1644 — variance-scaling
  canonical form.
* `[advances_fin_ml, p.31-34]` — cross-lib parity as correctness gate.
"""

from __future__ import annotations

import numpy as np


def apply_blend_variance_target_np(
    r_spy: np.ndarray,
    r_tlt: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy re-implementation of the iter 006 blend sizing.

    Returns ``(net_returns, pos_spy, pos_tlt, scale)`` all with the same
    length (first ``lookback`` bars dropped from the original input).
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be ≥ 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")

    a = np.asarray(r_spy, dtype=float)
    b = np.asarray(r_tlt, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"r_spy and r_tlt shape mismatch: {a.shape} vs {b.shape}")
    mask = ~(np.isnan(a) | np.isnan(b))
    a = a[mask]
    b = b[mask]
    n = len(a)
    if n <= lookback:
        raise ValueError(f"need > {lookback} aligned bars, got {n}")

    ann_var_spy = np.full(n, np.nan)
    ann_var_tlt = np.full(n, np.nan)
    cov_ab = np.full(n, np.nan)
    for t in range(lookback, n):
        wa = a[t - lookback : t]
        wb = b[t - lookback : t]
        ann_var_spy[t] = wa.var(ddof=0) * periods_per_year
        ann_var_tlt[t] = wb.var(ddof=0) * periods_per_year
        cov_ab[t] = np.cov(wa, wb, ddof=0)[0, 1] * periods_per_year

    target_var = target_vol ** 2
    scale = np.full(n, np.nan)
    w_spy = np.full(n, np.nan)
    for t in range(lookback, n):
        s2a = ann_var_spy[t]
        s2b = ann_var_tlt[t]
        cab = cov_ab[t]
        # Weights.
        if s2a > 0 and s2b > 0:
            ia = 1.0 / s2a
            ib = 1.0 / s2b
            w_spy[t] = ia / (ia + ib)
        elif s2a == 0 and s2b > 0:
            w_spy[t] = 1.0
        elif s2a > 0 and s2b == 0:
            w_spy[t] = 0.0
        else:
            w_spy[t] = 0.5  # both zero
        w_t = w_spy[t]
        # Portfolio variance (clamped non-negative).
        port_var = (
            w_t * w_t * s2a
            + (1.0 - w_t) * (1.0 - w_t) * s2b
            + 2.0 * w_t * (1.0 - w_t) * cab
        )
        port_var = max(port_var, 0.0)
        if port_var > 0:
            raw = target_var / port_var
        else:
            raw = max_leverage
        scale[t] = min(max(raw, 0.0), max_leverage)

    valid = ~np.isnan(scale)
    scale_v = scale[valid]
    w_spy_v = w_spy[valid]
    a_v = a[valid]
    b_v = b[valid]
    w_tlt_v = 1.0 - w_spy_v
    pos_spy = scale_v * w_spy_v
    pos_tlt = scale_v * w_tlt_v
    gross = pos_spy * a_v + pos_tlt * b_v

    dpos_spy = np.empty_like(pos_spy)
    dpos_tlt = np.empty_like(pos_tlt)
    dpos_spy[0] = abs(pos_spy[0])
    dpos_tlt[0] = abs(pos_tlt[0])
    dpos_spy[1:] = np.abs(np.diff(pos_spy))
    dpos_tlt[1:] = np.abs(np.diff(pos_tlt))
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = gross - cost
    return net, pos_spy, pos_tlt, scale_v


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
