"""Iter 025 — Slow-EWMAC trend on 6-asset broad-asset-class basket.

Mechanism (Carver 2015 systematic-trading framework, slow-speeds only):

    For each asset i, for each speed pair (Lfast, Lslow):
        Afast = 2 / (Lfast + 1)
        Aslow = 2 / (Lslow + 1)
        Efast[t] = Afast · P[t] + (1 - Afast) · Efast[t-1]
        Eslow[t] = Aslow · P[t] + (1 - Aslow) · Eslow[t-1]
        crossover[t] = Efast[t] - Eslow[t]
        sigma_pp[t] = EWMA std of |P[t] - P[t-1]|, span=sigma_span
        forecast_raw[t] = scalar · crossover[t] / sigma_pp[t]
        forecast[t] = clip(forecast_raw[t], -20, +20)

    combined[t] = (Σ_k speed_weights[k] · forecast_k[t]) · FDM
    combined_capped[t] = clip(combined[t], -20, +20)
    fcast_norm[t] = combined_capped[t] / 10           (E[|.|] ≈ 1)

    asset_vol_i[t] = EWMA std of return_i, span=asset_vol_span,
                     annualized × √252
    weight_target_i[t] = fcast_norm_i[t-lag_bars] · target_vol_per_asset
                         / asset_vol_i[t-lag_bars]
    weight_target_i = clip(weight_target_i, -cap, +cap)
    if long_only: weight_target_i = max(0, weight_target_i)

    No-trade buffer: weight_held_i[t] is updated to weight_target_i[t]
    only if |weight_target - weight_held| > buffer · |weight_target|;
    otherwise weight_held_i[t] = weight_held_i[t-1].

    gross[t] = Σ_i weight_held_i[t] · r_i[t]
    cost[t]  = Σ_i |Δweight_held_i[t]| · cost_bps_per_leg
    net[t]   = gross[t] - cost[t]

Citations
---------
* `[systematic_trading, p.118-119, ch.7]` — EWMAC rule, six speed pairs.
* `[systematic_trading, p.131-133, ch.8]` — FDM for combined forecast.
* `[systematic_trading, p.244-258, ch.15]` — No-trade buffer / position
  trade-band primitive.
* `[systematic_trading, p.282-285, app.B]` — EWMAC computation + scalars.
* `[risk_parity, p.10-11, ch.1]` — Multi-asset diversification basis.
* `[advances_fin_ml, p.31-34]` — Cross-library parity discipline.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} no-look-ahead lag.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def compute_ewmac_forecast(
    prices: pd.Series,
    Lfast: int,
    Lslow: int,
    scalar: float,
    *,
    sigma_span: int = 36,
    cap: float = 20.0,
) -> pd.Series:
    """Compute one-asset, one-speed EWMAC capped forecast.

    Parameters
    ----------
    prices : pd.Series
        Daily adjusted-close prices (positive, monotone-time index).
    Lfast, Lslow : int
        Fast and slow EWMA lookbacks (e.g. 32 and 128). Must satisfy
        Lslow > Lfast > 0.
    scalar : float
        Forecast scalar from Carver Table 49 (32:128 → 2.65, 64:256 → 1.87).
    sigma_span : int
        EWMA span for the price-points volatility estimator (~7w halflife
        at default 36 ≈ Carver's 25-day window with typical span/halflife
        ≈ span ≈ 1.5 × halflife).
    cap : float
        Forecast cap (Carver default ±20).

    Returns
    -------
    pd.Series of capped forecast, NaN where σ_pp is not yet defined.
    """
    if Lslow <= Lfast or Lfast <= 0:
        raise ValueError(f"need Lslow > Lfast > 0, got Lfast={Lfast}, Lslow={Lslow}")
    if scalar <= 0:
        raise ValueError(f"scalar must be > 0, got {scalar}")

    afast = 2.0 / (Lfast + 1)
    aslow = 2.0 / (Lslow + 1)
    n = len(prices)
    p = prices.to_numpy(dtype=float)
    efast = np.empty(n)
    eslow = np.empty(n)
    efast[0] = p[0]
    eslow[0] = p[0]
    for t in range(1, n):
        efast[t] = afast * p[t] + (1.0 - afast) * efast[t - 1]
        eslow[t] = aslow * p[t] + (1.0 - aslow) * eslow[t - 1]
    crossover = pd.Series(efast - eslow, index=prices.index)

    # σ_price_points: EWMA std of daily price changes (NOT pct returns)
    dp = prices.diff()
    sigma_pp = dp.ewm(span=sigma_span, min_periods=sigma_span).std(bias=False)

    raw = (crossover / sigma_pp) * scalar
    capped = raw.clip(lower=-cap, upper=cap)
    capped.name = f"ewmac_{Lfast}_{Lslow}"
    return capped


def combine_forecasts(
    forecasts: Sequence[pd.Series],
    weights: Sequence[float],
    fdm: float = 1.10,
    *,
    cap: float = 20.0,
) -> pd.Series:
    """Weighted-average + FDM scaling of N speed forecasts.

    All forecasts must share the same index.

    Returns capped combined forecast.
    """
    if len(forecasts) != len(weights):
        raise ValueError("forecasts and weights must have same length")
    if abs(sum(weights) - 1.0) > 1e-9:
        raise ValueError(f"weights must sum to 1, got {sum(weights)}")
    if fdm <= 0:
        raise ValueError(f"fdm must be > 0, got {fdm}")

    df = pd.concat(forecasts, axis=1, join="inner")
    weighted = df.multiply(np.asarray(weights), axis=1).sum(axis=1)
    combined = (weighted * fdm).clip(lower=-cap, upper=cap)
    combined.name = "combined_forecast"
    return combined


def position_size(
    forecast_capped: pd.Series,
    asset_returns: pd.Series,
    *,
    target_vol_per_asset: float,
    asset_vol_span: int,
    lag_bars: int,
    max_per_asset_leverage: float,
    long_only: bool,
) -> pd.Series:
    """Translate capped forecast → target weight per asset.

    weight = (forecast_capped[t-lag] / 10) × target_vol / asset_vol[t-lag]

    Then capped to ±max_per_asset_leverage and long-only-flatted.
    """
    fcast_norm = forecast_capped / 10.0  # E[|.|] ≈ 1
    # σ̂_{t-lag}: EWMA std of returns, annualized.
    asset_vol = (
        asset_returns.ewm(span=asset_vol_span, min_periods=asset_vol_span)
        .std(bias=False)
        * np.sqrt(252.0)
    )
    fcast_lag = fcast_norm.shift(lag_bars)
    vol_lag = asset_vol.shift(lag_bars)

    raw = fcast_lag * target_vol_per_asset / vol_lag
    capped = raw.clip(lower=-max_per_asset_leverage, upper=max_per_asset_leverage)
    if long_only:
        capped = capped.clip(lower=0.0)
    return capped


def apply_no_trade_buffer(
    target_weights: pd.Series,
    *,
    threshold_pct: float,
) -> pd.Series:
    """Hold position unless |Δw| > threshold_pct × |target|.

    Standard Carver "no-trade buffer" — position is updated only on bars
    where the new target deviates materially from the held position.
    Reduces turnover without sacrificing edge (Carver p.252-258).
    """
    if threshold_pct < 0:
        raise ValueError("threshold_pct must be ≥ 0")
    arr = target_weights.to_numpy(dtype=float)
    held = np.empty_like(arr)
    n = len(arr)
    if n == 0:
        return target_weights.copy()
    # Initialize held to 0 until first valid target.
    current = 0.0
    for t in range(n):
        target = arr[t]
        if np.isnan(target):
            held[t] = current
            continue
        deviation = abs(target - current)
        # Threshold uses the larger of |target| or |current| as scale.
        scale = max(abs(target), abs(current), 1e-9)
        if deviation > threshold_pct * scale:
            current = target
        held[t] = current
    return pd.Series(held, index=target_weights.index)


def apply_slow_ewmac_strategy(
    prices_df: pd.DataFrame,
    *,
    speeds: Sequence[tuple[int, int]],
    speed_scalars: Sequence[float],
    speed_weights: Sequence[float],
    fdm: float = 1.10,
    target_vol_per_asset: float = 0.04,
    asset_vol_span: int = 36,
    lag_bars: int = 1,
    no_trade_buffer_pct: float = 0.10,
    max_per_asset_leverage: float = 0.6,
    long_only: bool = True,
    cost_bps_per_leg: float = 0.0002,
    sigma_span: int = 36,
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute the slow-EWMAC strategy on a multi-asset price DataFrame.

    Parameters
    ----------
    prices_df : pd.DataFrame
        Each column is one asset's adjusted-close series; rows aligned by
        date (inner-joined).
    speeds : sequence of (Lfast, Lslow)
        Speed pairs to use, e.g. [(32, 128), (64, 256)].
    speed_scalars : sequence of float
        Carver Table 49 forecast scalars matching speeds.
    speed_weights : sequence of float
        Combination weights for speeds, must sum to 1.
    fdm : float
        Forecast diversification multiplier (Carver Table 18).
    target_vol_per_asset : float
        Per-asset annualized vol contribution target. With N=6 assets at
        moderate (~0.3) cross-correlation, total portfolio vol ≈
        target_vol × √(N · (1 + (N−1)·ρ)) ≈ 0.04 × √15 ≈ 15.5%.
    asset_vol_span : int
        EWMA span for the per-asset realized vol estimator.
    lag_bars : int
        Bars of lag enforced on the forecast and vol (≥ 1; default 1).
    no_trade_buffer_pct : float
        Position-trade-band threshold (Carver p.252-258).
    max_per_asset_leverage : float
        Per-asset cap (default 0.6× equity).
    long_only : bool
        If True, negative weights clipped to 0.
    cost_bps_per_leg : float
        Linear cost per |Δweight| per asset (default 2 bps).
    sigma_span : int
        EWMA span for the EWMAC σ_pp estimator.

    Returns
    -------
    (net_returns, positions, target_positions, combined_forecasts)
        ``net_returns`` : pd.Series of net daily returns.
        ``positions`` : pd.DataFrame of held weights per asset (post-buffer).
        ``target_positions`` : pd.DataFrame of target weights per asset
                              (pre-buffer; for diagnostics).
        ``combined_forecasts`` : pd.DataFrame of combined forecasts per asset.
    """
    if len(speeds) != len(speed_scalars) or len(speeds) != len(speed_weights):
        raise ValueError("speeds, speed_scalars, speed_weights must align")
    if prices_df.shape[1] < 2:
        raise ValueError(f"need ≥ 2 asset columns, got {prices_df.shape[1]}")
    if prices_df.isna().any().any():
        prices_df = prices_df.dropna()
    if len(prices_df) < max(L for _, L in speeds) + asset_vol_span + lag_bars:
        raise ValueError("not enough bars for warmup of speeds + asset_vol")

    asset_names = list(prices_df.columns)
    returns_df = prices_df.pct_change()

    # Per-asset combined forecast.
    fcast_combined: dict[str, pd.Series] = {}
    for asset in asset_names:
        prices_asset = prices_df[asset]
        per_speed: list[pd.Series] = []
        for (Lf, Ls), sc in zip(speeds, speed_scalars):
            f = compute_ewmac_forecast(
                prices_asset, Lf, Ls, sc,
                sigma_span=sigma_span,
            )
            per_speed.append(f)
        combined = combine_forecasts(per_speed, list(speed_weights), fdm=fdm)
        fcast_combined[asset] = combined
    fcast_df = pd.DataFrame(fcast_combined)

    # Per-asset target weights.
    target_w: dict[str, pd.Series] = {}
    for asset in asset_names:
        target_w[asset] = position_size(
            fcast_df[asset], returns_df[asset],
            target_vol_per_asset=target_vol_per_asset,
            asset_vol_span=asset_vol_span,
            lag_bars=lag_bars,
            max_per_asset_leverage=max_per_asset_leverage,
            long_only=long_only,
        )
    target_df = pd.DataFrame(target_w)

    # Drop bars where ANY asset has NaN target (i.e. warmup region).
    valid = target_df.notna().all(axis=1)
    target_df = target_df.loc[valid]
    fcast_df = fcast_df.loc[valid]
    returns_aligned = returns_df.loc[target_df.index]

    # Apply no-trade buffer per asset.
    held_w: dict[str, pd.Series] = {}
    for asset in asset_names:
        held_w[asset] = apply_no_trade_buffer(
            target_df[asset], threshold_pct=no_trade_buffer_pct,
        )
    held_df = pd.DataFrame(held_w)

    # Returns + cost.
    gross = (held_df * returns_aligned).sum(axis=1)
    dpos = held_df.diff().abs().fillna(held_df.iloc[0].abs())
    cost = dpos.sum(axis=1) * cost_bps_per_leg
    net = gross - cost
    net.name = "net"

    return net, held_df, target_df, fcast_df
