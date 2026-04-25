"""Iter 044 — Pure-numpy reference for multi-feature regime gate.

Independent re-implementation of `apply_multifeature_regime_3leg` for
G7 cross-library parity (`[advances_fin_ml, p.31-34]`). Must NOT call
the pandas engine — different code path detects engine bugs.

The numpy reference also re-implements the rolling causal z-score and
the composite regime construction so that the FULL pipeline (raw VIX,
T10Y3M arrays → net returns) is duplicated in pure numpy.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np


def rolling_zscore_np(x: np.ndarray, window: int) -> np.ndarray:
    """Causal rolling z-score with expanding warm-up (pure numpy).

    Mirrors `multifeature_regime_gate.rolling_zscore`:
    * window must be >= 2;
    * for `t < 1` returns 0 (no two-bar history);
    * for `1 <= t < window-1` uses bars `[0, t]` (expanding);
    * for `t >= window-1` uses the last `window` bars.
    Population std (ddof=0). Bars where std is 0 → 0.0.
    """
    x = np.asarray(x, dtype=float)
    n = x.shape[0]
    if window < 2:
        raise ValueError(f"window must be >= 2; got {window}")
    z = np.zeros(n, dtype=float)
    for t in range(n):
        if t == 0:
            z[t] = 0.0
            continue
        start = max(0, t - window + 1)
        win = x[start: t + 1]
        if win.size < 2:
            z[t] = 0.0
            continue
        mu = win.mean()
        sd = win.std(ddof=0)
        if sd <= 0:
            z[t] = 0.0
        else:
            z[t] = (x[t] - mu) / sd
    return z


def build_composite_regime_np(
    vix: np.ndarray,
    term_spread: np.ndarray,
    *,
    z_window: int = 252,
    feature_weights: Mapping[str, float] = None,
    stress_threshold: float = 0.0,
    lag_days: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Build (regime, composite_score) in pure numpy."""
    if feature_weights is None:
        feature_weights = {"vix": 0.5, "neg_t10y3m": 0.5}
    vix = np.asarray(vix, dtype=float)
    ts = np.asarray(term_spread, dtype=float)
    if vix.shape != ts.shape:
        raise ValueError(
            f"shape mismatch: vix={vix.shape}, term_spread={ts.shape}"
        )
    z_vix = rolling_zscore_np(vix, z_window)
    z_neg_t = rolling_zscore_np(-ts, z_window)
    s = (
        feature_weights["vix"] * z_vix
        + feature_weights["neg_t10y3m"] * z_neg_t
    )
    n = s.shape[0]
    if lag_days > 0:
        s_lag = np.empty(n, dtype=float)
        s_lag[lag_days:] = s[:-lag_days] if lag_days > 0 else s
        for i in range(min(lag_days, n)):
            s_lag[i] = s[0]
    else:
        s_lag = s.copy()
    regime = (s_lag < stress_threshold).astype(int)
    return regime, s


def apply_multifeature_regime_3leg_np(
    r_eq: np.ndarray,
    r_bd: np.ndarray,
    r_gld: np.ndarray,
    regime: np.ndarray,
    *,
    calm_weights: Mapping[str, float],
    stress_weights: Mapping[str, float],
    cost_bps_per_leg: float = 0.0002,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Three-leg regime-weighted stack — pure numpy.

    Same signature as iter 041's numpy reference (regime mask passed
    in from `build_composite_regime_np`). Detects engine bugs in
    weight assignment / cost accounting.
    """
    a = np.asarray(r_eq, dtype=float)
    b = np.asarray(r_bd, dtype=float)
    c = np.asarray(r_gld, dtype=float)
    reg = np.asarray(regime, dtype=int)
    if not (a.shape == b.shape == c.shape == reg.shape):
        raise ValueError(
            f"shape mismatch: eq={a.shape}, bd={b.shape}, gld={c.shape}, "
            f"regime={reg.shape}"
        )
    n = a.shape[0]
    if n == 0:
        raise ValueError("empty input arrays")

    cw = (calm_weights["eq_w"], calm_weights["bd_w"], calm_weights["gld_w"])
    sw = (stress_weights["eq_w"], stress_weights["bd_w"], stress_weights["gld_w"])
    for w in (*cw, *sw):
        if w < 0:
            raise ValueError(f"weights must be non-negative; got {w}")

    pos_eq = np.where(reg == 1, cw[0], sw[0]).astype(float)
    pos_bd = np.where(reg == 1, cw[1], sw[1]).astype(float)
    pos_gld = np.where(reg == 1, cw[2], sw[2]).astype(float)
    scale = pos_eq + pos_bd + pos_gld

    gross = pos_eq * a + pos_bd * b + pos_gld * c

    dpos_eq = np.empty(n, dtype=float)
    dpos_bd = np.empty(n, dtype=float)
    dpos_gld = np.empty(n, dtype=float)
    dpos_eq[0] = pos_eq[0]
    dpos_bd[0] = pos_bd[0]
    dpos_gld[0] = pos_gld[0]
    if n > 1:
        dpos_eq[1:] = np.abs(np.diff(pos_eq))
        dpos_bd[1:] = np.abs(np.diff(pos_bd))
        dpos_gld[1:] = np.abs(np.diff(pos_gld))
    cost = (dpos_eq + dpos_bd + dpos_gld) * cost_bps_per_leg

    net = gross - cost
    positions = np.column_stack([pos_eq, pos_bd, pos_gld])
    return net, positions, scale


def cagr_np(net: np.ndarray, periods_per_year: int = 252) -> float:
    eq = np.cumprod(1.0 + np.asarray(net, dtype=float))
    n = len(eq)
    if n == 0:
        return 0.0
    final = float(eq[-1])
    if final <= 0:
        return -1.0
    return final ** (periods_per_year / n) - 1.0
