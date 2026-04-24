"""Iter 013 — Numpy-only reference for G7 cross-lib CAGR parity check.

Mirrors meta_labeling.apply_blend_with_meta using numpy arrays end-to-
end (no pandas rolling). Same scikit-learn LogisticRegression (trusted
dependency). Tolerance per G7 spec: ≤ 3 pp CAGR delta.

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-library parity discipline.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression


def _rolling_std(x: np.ndarray, window: int) -> np.ndarray:
    """Pandas-compatible rolling population std (ddof=0), window-anchored."""
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    for i in range(window - 1, n):
        w = x[i - window + 1:i + 1]
        if np.isnan(w).any():
            continue
        out[i] = np.std(w, ddof=0)
    return out


def _rolling_mean(x: np.ndarray, window: int) -> np.ndarray:
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    for i in range(window - 1, n):
        w = x[i - window + 1:i + 1]
        if np.isnan(w).any():
            continue
        out[i] = np.mean(w)
    return out


def _rolling_cov(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    for i in range(window - 1, n):
        w_x = x[i - window + 1:i + 1]
        w_y = y[i - window + 1:i + 1]
        if np.isnan(w_x).any() or np.isnan(w_y).any():
            continue
        mean_x = np.mean(w_x)
        mean_y = np.mean(w_y)
        out[i] = np.mean((w_x - mean_x) * (w_y - mean_y))  # ddof=0
    return out


def _rolling_corr(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
    n = len(x)
    out = np.full(n, np.nan, dtype=float)
    for i in range(window - 1, n):
        w_x = x[i - window + 1:i + 1]
        w_y = y[i - window + 1:i + 1]
        if np.isnan(w_x).any() or np.isnan(w_y).any():
            continue
        sx = np.std(w_x, ddof=0)
        sy = np.std(w_y, ddof=0)
        if sx <= 1e-18 or sy <= 1e-18:
            out[i] = 0.0
            continue
        mx = np.mean(w_x)
        my = np.mean(w_y)
        out[i] = float(np.mean((w_x - mx) * (w_y - my)) / (sx * sy))
    return out


def _shift1(x: np.ndarray) -> np.ndarray:
    """Right-shift array by 1; first element becomes NaN."""
    out = np.empty_like(x, dtype=float)
    out[0] = np.nan
    out[1:] = x[:-1]
    return out


def _compute_blend_np(
    r_spy: np.ndarray, r_tlt: np.ndarray,
    target_vol: float, lookback: int, max_leverage: float,
    cost_bps_per_leg: float, periods_per_year: int = 252,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    """Reimplementation of apply_blend_variance_target (pure numpy).

    Returns (net_blend, pos_spy, pos_tlt, scale, first_valid_idx).
    """
    n = len(r_spy)
    # Rolling annualised variance per leg, shifted by 1.
    std_spy = _rolling_std(r_spy, lookback)
    std_tlt = _rolling_std(r_tlt, lookback)
    var_spy = (std_spy ** 2) * periods_per_year
    var_tlt = (std_tlt ** 2) * periods_per_year
    var_spy = _shift1(var_spy)
    var_tlt = _shift1(var_tlt)
    cov_ab = _rolling_cov(r_spy, r_tlt, lookback) * periods_per_year
    cov_ab = _shift1(cov_ab)

    w_spy = np.full(n, np.nan, dtype=float)
    both_pos = (var_spy > 0) & (var_tlt > 0)
    only_spy_zero = (var_spy == 0) & (var_tlt > 0)
    only_tlt_zero = (var_spy > 0) & (var_tlt == 0)
    both_zero = (var_spy == 0) & (var_tlt == 0)

    with np.errstate(divide="ignore", invalid="ignore"):
        inv_s = np.where(both_pos, 1.0 / var_spy, np.nan)
        inv_t = np.where(both_pos, 1.0 / var_tlt, np.nan)
    w_spy[both_pos] = inv_s[both_pos] / (inv_s[both_pos] + inv_t[both_pos])
    w_spy[only_spy_zero] = 1.0
    w_spy[only_tlt_zero] = 0.0
    w_spy[both_zero] = 0.5
    w_tlt = 1.0 - w_spy

    var_port = (
        w_spy ** 2 * var_spy
        + w_tlt ** 2 * var_tlt
        + 2.0 * w_spy * w_tlt * cov_ab
    )
    var_port = np.where(var_port < 0, 0.0, var_port)

    target_var = target_vol ** 2
    raw_scale = np.full(n, np.nan, dtype=float)
    pos_mask = (~np.isnan(var_port)) & (var_port > 0)
    zero_mask = (~np.isnan(var_port)) & (var_port == 0)
    raw_scale[pos_mask] = target_var / var_port[pos_mask]
    raw_scale[zero_mask] = max_leverage
    scale = np.clip(raw_scale, 0.0, max_leverage)

    pos_spy = scale * w_spy
    pos_tlt = scale * w_tlt

    # gross/cost/net — in this routine we compute UN-GATED; the meta
    # wrapper handles the gate + cost reassessment.
    gross = pos_spy * r_spy + pos_tlt * r_tlt
    first_valid = int(np.argmax(~np.isnan(scale)))
    # For parity: fill initial NaN positions/scale with 0 for the net
    # stream before the first valid bar (they get sliced away anyway).
    net = gross.copy()
    return net, pos_spy, pos_tlt, scale, first_valid


def apply_blend_with_meta_np(
    r_spy: np.ndarray,
    r_tlt: np.ndarray,
    vix: np.ndarray,
    *,
    target_vol: float,
    lookback: int,
    max_leverage: float,
    cost_bps_per_leg: float,
    train_window: int,
    retrain_cadence: int,
    warmup_bars: int,
    decision_threshold: float,
    random_state: int,
    rho_window: int = 60,
    vix_z_window: int = 252,
    periods_per_year: int = 252,
) -> np.ndarray:
    """Numpy-only reference of the meta-labeled pipeline.

    Returns net-return array aligned on the blend's valid index (same
    length as the pandas engine's ``net`` output).
    """
    _net_b, pos_spy, pos_tlt, scale, first_valid = _compute_blend_np(
        r_spy, r_tlt, target_vol, lookback, max_leverage, cost_bps_per_leg,
        periods_per_year,
    )
    # Slice to valid region (first_valid onward).
    r_spy_v = r_spy[first_valid:]
    r_tlt_v = r_tlt[first_valid:]
    vix_v = vix[first_valid:]
    pos_spy_v = pos_spy[first_valid:]
    pos_tlt_v = pos_tlt[first_valid:]

    # Features (lagged).
    rho_raw = _rolling_corr(r_spy, r_tlt, rho_window)
    rho_lagged = _shift1(rho_raw)[first_valid:]
    vix_mean = _rolling_mean(vix, vix_z_window)
    vix_std = _rolling_std(vix, vix_z_window)
    with np.errstate(invalid="ignore", divide="ignore"):
        vix_z = np.where(vix_std > 0, (vix - vix_mean) / vix_std, np.nan)
    vix_z_lagged = _shift1(vix_z)[first_valid:]
    X_all = np.column_stack([rho_lagged, vix_z_lagged])

    # Un-gated blend net for label generation (gross returns per bar).
    net_blend = pos_spy_v * r_spy_v + pos_tlt_v * r_tlt_v  # un-costed labels
    y_all = (net_blend > 0).astype(int)

    n = len(scale) - first_valid
    p_act = np.ones(n, dtype=float)

    boundaries = list(range(warmup_bars, n, retrain_cadence))
    if not boundaries or boundaries[-1] < n - 1:
        boundaries.append(
            min(n, boundaries[-1] + retrain_cadence) if boundaries else warmup_bars
        )

    current_model: LogisticRegression | None = None
    for b in boundaries:
        train_start = max(0, b - train_window)
        X_train = X_all[train_start:b]
        y_train = y_all[train_start:b]
        mask = ~np.isnan(X_train).any(axis=1)
        X_train_clean = X_train[mask]
        y_train_clean = y_train[mask]
        if len(y_train_clean) >= 50 and len(np.unique(y_train_clean)) >= 2:
            model = LogisticRegression(
                C=1.0, penalty="l2", solver="lbfgs",
                max_iter=1000, random_state=random_state,
            )
            model.fit(X_train_clean, y_train_clean)
            current_model = model
        pred_start = b
        pred_end = min(b + retrain_cadence, n)
        if current_model is None:
            p_act[pred_start:pred_end] = 1.0
        else:
            X_pred = X_all[pred_start:pred_end]
            pred_mask = ~np.isnan(X_pred).any(axis=1)
            probs = np.ones(pred_end - pred_start, dtype=float)
            if pred_mask.any():
                probs[pred_mask] = current_model.predict_proba(X_pred[pred_mask])[:, 1]
            p_act[pred_start:pred_end] = probs

    gate = np.where(p_act > decision_threshold, 1.0, 0.0)
    pos_spy_g = pos_spy_v * gate
    pos_tlt_g = pos_tlt_v * gate

    gross = pos_spy_g * r_spy_v + pos_tlt_g * r_tlt_v
    dpos_spy = np.empty(n, dtype=float)
    dpos_tlt = np.empty(n, dtype=float)
    dpos_spy[0] = abs(pos_spy_g[0])
    dpos_tlt[0] = abs(pos_tlt_g[0])
    dpos_spy[1:] = np.abs(np.diff(pos_spy_g))
    dpos_tlt[1:] = np.abs(np.diff(pos_tlt_g))
    cost = (dpos_spy + dpos_tlt) * cost_bps_per_leg
    net = gross - cost
    return net
