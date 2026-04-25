"""Iter 025 — pure-numpy reference implementation for G7 cross-lib parity.

Mirrors ``slow_ewmac_multi_asset.apply_slow_ewmac_strategy`` using only
numpy arrays (no pandas). The CAGR difference between this and the
pandas engine must be ≤ 3 pp per `[advances_fin_ml, p.31-34]`.
"""

from __future__ import annotations

import numpy as np


def _ewmac_forecast_np(
    prices: np.ndarray, Lfast: int, Lslow: int, scalar: float,
    *, sigma_span: int, cap: float = 20.0,
) -> np.ndarray:
    """Capped forecast for one asset, one speed pair (1-D float array)."""
    n = len(prices)
    afast = 2.0 / (Lfast + 1)
    aslow = 2.0 / (Lslow + 1)
    efast = np.empty(n)
    eslow = np.empty(n)
    efast[0] = prices[0]
    eslow[0] = prices[0]
    for t in range(1, n):
        efast[t] = afast * prices[t] + (1.0 - afast) * efast[t - 1]
        eslow[t] = aslow * prices[t] + (1.0 - aslow) * eslow[t - 1]
    crossover = efast - eslow

    # σ_pp: EWMA std of |Δprice| with bias=False matching pandas.
    dp = np.empty(n)
    dp[0] = np.nan
    dp[1:] = prices[1:] - prices[:-1]
    sigma_pp = _ewm_std_np(dp, span=sigma_span, min_periods=sigma_span)

    raw = np.full(n, np.nan)
    valid = ~np.isnan(sigma_pp) & (sigma_pp != 0)
    raw[valid] = scalar * crossover[valid] / sigma_pp[valid]
    capped = np.where(np.isnan(raw), np.nan, np.clip(raw, -cap, cap))
    return capped


def _ewm_std_np(
    series: np.ndarray, span: int, min_periods: int,
) -> np.ndarray:
    """EWM std with bias=False, matching pandas semantics for a 1-D array.

    Reproduces the pandas convention where, for a sample of size n, the
    weighted-population std is multiplied by `√(s1² / (s1² − s2))` (the
    bias-correction factor), and the first ``min_periods − 1`` outputs
    are NaN.
    """
    n = len(series)
    alpha = 2.0 / (span + 1.0)
    out = np.full(n, np.nan)
    if n == 0:
        return out

    weighted_mean = np.nan
    s1 = 0.0  # sum of weights
    s2 = 0.0  # sum of squared weights
    weighted_var_num = 0.0  # sum w · (x - mean)²
    valid_count = 0

    for t in range(n):
        x = series[t]
        if np.isnan(x):
            # Rescale running stats by (1 - alpha)? pandas treats NaN as
            # "missing" and SKIPS the update — we mirror that.
            if valid_count >= min_periods and not np.isnan(weighted_mean):
                # carry forward
                pass
            continue
        # Update sums (pandas: each new bar enters with weight 1; previous
        # weights decay by factor (1 - alpha)).
        s1 = s1 * (1.0 - alpha) + 1.0
        s2 = s2 * (1.0 - alpha) ** 2 + 1.0
        if np.isnan(weighted_mean):
            weighted_mean = x
            weighted_var_num = 0.0
        else:
            delta = x - weighted_mean
            weighted_mean = weighted_mean + (alpha * delta)
            # Approximate weighted variance update using EWM definition:
            # var_{t} = (1-alpha) · (var_{t-1} + alpha · delta²)
            # We track the weighted_var_num accumulator equivalently.
            weighted_var_num = (
                (1.0 - alpha) * weighted_var_num
                + (1.0 - alpha) * alpha * delta * delta
            )
        valid_count += 1
        if valid_count >= min_periods:
            denom = s1 * s1 - s2
            if denom > 0:
                # Bias-corrected EWM variance.
                bias_factor = (s1 * s1) / denom
                ewm_var = weighted_var_num * bias_factor
                if ewm_var > 0:
                    out[t] = float(np.sqrt(ewm_var))
                else:
                    out[t] = 0.0
    return out


def _combine_forecasts_np(
    forecasts: list[np.ndarray], weights: list[float], fdm: float, cap: float = 20.0,
) -> np.ndarray:
    """Stack and weighted-sum N forecast arrays, apply FDM, then cap."""
    stack = np.vstack(forecasts)  # shape (N_speeds, n_bars)
    w = np.asarray(weights).reshape(-1, 1)
    weighted = (stack * w).sum(axis=0)
    combined = weighted * fdm
    return np.clip(combined, -cap, cap)


def _position_size_np(
    fcast: np.ndarray, returns: np.ndarray,
    *, target_vol_per_asset: float, asset_vol_span: int, lag_bars: int,
    max_per_asset_leverage: float, long_only: bool,
) -> np.ndarray:
    """Position size for one asset using the EWM-vol estimator."""
    n = len(fcast)
    asset_sigma = _ewm_std_np(returns, span=asset_vol_span, min_periods=asset_vol_span)
    asset_vol_ann = asset_sigma * np.sqrt(252.0)
    fcast_norm = fcast / 10.0
    fcast_lag = np.full(n, np.nan)
    fcast_lag[lag_bars:] = fcast_norm[:-lag_bars] if lag_bars > 0 else fcast_norm
    vol_lag = np.full(n, np.nan)
    if lag_bars > 0:
        vol_lag[lag_bars:] = asset_vol_ann[:-lag_bars]
    else:
        vol_lag = asset_vol_ann

    raw = fcast_lag * target_vol_per_asset / vol_lag
    capped = np.clip(raw, -max_per_asset_leverage, max_per_asset_leverage)
    if long_only:
        capped = np.where(np.isnan(capped), np.nan, np.maximum(capped, 0.0))
    return capped


def _no_trade_buffer_np(target: np.ndarray, threshold_pct: float) -> np.ndarray:
    """Hold position unless |Δ| > threshold_pct × max(|target|, |current|)."""
    n = len(target)
    held = np.empty(n)
    current = 0.0
    for t in range(n):
        tgt = target[t]
        if np.isnan(tgt):
            held[t] = current
            continue
        deviation = abs(tgt - current)
        scale = max(abs(tgt), abs(current), 1e-9)
        if deviation > threshold_pct * scale:
            current = tgt
        held[t] = current
    return held


def apply_slow_ewmac_strategy_np(
    prices_2d: np.ndarray,
    *,
    speeds: list[tuple[int, int]],
    speed_scalars: list[float],
    speed_weights: list[float],
    fdm: float = 1.10,
    target_vol_per_asset: float = 0.04,
    asset_vol_span: int = 36,
    lag_bars: int = 1,
    no_trade_buffer_pct: float = 0.10,
    max_per_asset_leverage: float = 0.6,
    long_only: bool = True,
    cost_bps_per_leg: float = 0.0002,
    sigma_span: int = 36,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """numpy reference of apply_slow_ewmac_strategy.

    ``prices_2d`` shape: (n_bars, n_assets), columns aligned with
    ``speeds``-independent asset axis.

    Returns
    -------
    (net, valid_mask, held) — net is shape (n_valid,) of net daily
    returns; valid_mask is bool (n_bars,) marking bars that passed
    the warmup; held is (n_valid, n_assets) of held weights.
    """
    n_bars, n_assets = prices_2d.shape

    # Per-asset combined forecast.
    fcasts_per_asset = np.full((n_bars, n_assets), np.nan)
    for j in range(n_assets):
        per_speed = []
        for (Lf, Ls), sc in zip(speeds, speed_scalars):
            f = _ewmac_forecast_np(
                prices_2d[:, j], Lf, Ls, sc, sigma_span=sigma_span,
            )
            per_speed.append(f)
        fcasts_per_asset[:, j] = _combine_forecasts_np(per_speed, speed_weights, fdm)

    # Per-asset target weight.
    returns_2d = np.full((n_bars, n_assets), np.nan)
    returns_2d[1:] = prices_2d[1:] / prices_2d[:-1] - 1.0

    target_2d = np.full((n_bars, n_assets), np.nan)
    for j in range(n_assets):
        target_2d[:, j] = _position_size_np(
            fcasts_per_asset[:, j], returns_2d[:, j],
            target_vol_per_asset=target_vol_per_asset,
            asset_vol_span=asset_vol_span,
            lag_bars=lag_bars,
            max_per_asset_leverage=max_per_asset_leverage,
            long_only=long_only,
        )

    valid = np.all(~np.isnan(target_2d), axis=1)
    target_valid = target_2d[valid]
    returns_valid = returns_2d[valid]

    # Apply no-trade buffer per asset.
    held_valid = np.empty_like(target_valid)
    for j in range(n_assets):
        held_valid[:, j] = _no_trade_buffer_np(
            target_valid[:, j], threshold_pct=no_trade_buffer_pct,
        )

    # Compute net.
    gross = np.sum(held_valid * returns_valid, axis=1)

    # cost = Σ |Δw_i| · cost_bps; first row uses |w_0| (charged from zero).
    dpos = np.empty_like(held_valid)
    dpos[0] = np.abs(held_valid[0])
    dpos[1:] = np.abs(held_valid[1:] - held_valid[:-1])
    cost = np.sum(dpos, axis=1) * cost_bps_per_leg

    net = gross - cost
    return net, valid, held_valid
