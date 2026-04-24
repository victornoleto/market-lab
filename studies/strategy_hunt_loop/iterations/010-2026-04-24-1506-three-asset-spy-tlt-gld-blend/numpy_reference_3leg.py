"""G7 cross-lib reference — pure-numpy 3-leg blend + CAGR.

Independent re-implementation of
``three_leg_blend.apply_blend_variance_target_3leg`` using only numpy
loops. Used by the G7 gate to check pandas-engine CAGR agrees to
±3 pp per ``[advances_fin_ml, p.31-34]``.

Citations
---------
* `[risk_parity, p.10-11, ch.1]` — naïve risk parity N-asset form.
* Moreira & Muir (2017), *JoF* 72(4) — variance-scaling canonical form.
* `[advances_fin_ml, p.31-34]` — cross-lib parity as correctness gate.
"""

from __future__ import annotations

import numpy as np


def apply_blend_variance_target_3leg_np(
    r_spy: np.ndarray,
    r_tlt: np.ndarray,
    r_gld: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    periods_per_year: int = 252,
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pure-numpy re-implementation of the iter 010 3-leg blend.

    Returns ``(net_returns, positions_Nx3, scale)`` with first
    ``lookback`` bars of the aligned input dropped.
    """
    if target_vol <= 0:
        raise ValueError(f"target_vol must be > 0, got {target_vol}")
    if lookback < 2:
        raise ValueError(f"lookback must be >= 2, got {lookback}")
    if max_leverage <= 0:
        raise ValueError(f"max_leverage must be > 0, got {max_leverage}")

    a = np.asarray(r_spy, dtype=float)
    b = np.asarray(r_tlt, dtype=float)
    c = np.asarray(r_gld, dtype=float)
    if not (a.shape == b.shape == c.shape):
        raise ValueError(
            f"shape mismatch: spy {a.shape}, tlt {b.shape}, gld {c.shape}"
        )
    mask = ~(np.isnan(a) | np.isnan(b) | np.isnan(c))
    a = a[mask]; b = b[mask]; c = c[mask]
    n = len(a)
    if n <= lookback:
        raise ValueError(f"need > {lookback} aligned bars, got {n}")

    ann_var = np.full((n, 3), np.nan)
    cov_ab = np.full(n, np.nan)
    cov_ac = np.full(n, np.nan)
    cov_bc = np.full(n, np.nan)
    for t in range(lookback, n):
        wa_ = a[t - lookback : t]
        wb_ = b[t - lookback : t]
        wc_ = c[t - lookback : t]
        ann_var[t, 0] = wa_.var(ddof=0) * periods_per_year
        ann_var[t, 1] = wb_.var(ddof=0) * periods_per_year
        ann_var[t, 2] = wc_.var(ddof=0) * periods_per_year
        cov_ab[t] = np.cov(wa_, wb_, ddof=0)[0, 1] * periods_per_year
        cov_ac[t] = np.cov(wa_, wc_, ddof=0)[0, 1] * periods_per_year
        cov_bc[t] = np.cov(wb_, wc_, ddof=0)[0, 1] * periods_per_year

    target_var = target_vol ** 2
    scale = np.full(n, np.nan)
    weights = np.full((n, 3), np.nan)
    for t in range(lookback, n):
        va = ann_var[t, 0]; vb = ann_var[t, 1]; vc = ann_var[t, 2]
        # Build weights.
        zero_a = (va == 0); zero_b = (vb == 0); zero_c = (vc == 0)
        n_zero = int(zero_a) + int(zero_b) + int(zero_c)
        if n_zero == 0:
            ia = 1.0 / va; ib = 1.0 / vb; ic = 1.0 / vc
            s = ia + ib + ic
            wa = ia / s; wb = ib / s; wc = ic / s
        elif n_zero == 1:
            wa = 1.0 if zero_a else 0.0
            wb = 1.0 if zero_b else 0.0
            wc = 1.0 if zero_c else 0.0
        elif n_zero == 2:
            # Two zeros → split 1/2 across the zero legs.
            wa = 0.5 if zero_a else 0.0
            wb = 0.5 if zero_b else 0.0
            wc = 0.5 if zero_c else 0.0
        else:
            wa = wb = wc = 1.0 / 3.0
        weights[t] = (wa, wb, wc)

        # Portfolio variance: wᵀ Σ w
        port_var = (
            wa * wa * va + wb * wb * vb + wc * wc * vc
            + 2.0 * wa * wb * cov_ab[t]
            + 2.0 * wa * wc * cov_ac[t]
            + 2.0 * wb * wc * cov_bc[t]
        )
        port_var = max(port_var, 0.0)
        if port_var > 0:
            raw = target_var / port_var
        else:
            raw = max_leverage
        scale[t] = min(max(raw, 0.0), max_leverage)

    valid = ~np.isnan(scale)
    scale_v = scale[valid]
    w_v = weights[valid]
    a_v = a[valid]; b_v = b[valid]; c_v = c[valid]
    pos = scale_v[:, None] * w_v
    gross = pos[:, 0] * a_v + pos[:, 1] * b_v + pos[:, 2] * c_v

    dpos = np.empty_like(pos)
    dpos[0] = np.abs(pos[0])
    dpos[1:] = np.abs(np.diff(pos, axis=0))
    cost = dpos.sum(axis=1) * cost_bps_per_leg
    net = gross - cost
    return net, pos, scale_v


def cagr_np(returns: np.ndarray, *, periods_per_year: int = 252) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    years = len(r) / periods_per_year
    if years <= 0 or eq[-1] <= 0:
        return 0.0
    return float(eq[-1] ** (1.0 / years) - 1.0)


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


def max_drawdown_np(returns: np.ndarray) -> float:
    r = np.asarray(returns, dtype=float)
    if len(r) < 2:
        return 0.0
    eq = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    return float(abs(dd.min()))
