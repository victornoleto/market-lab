"""Carver vol-targeted continuous strategy — T5 shape per spec §2.6.

Per-asset position size = vol_scalar × forecast / 10, capped by IDM.
Long-only (negative forecasts → 0 position; net cash residual).

Citation: [systematic_trading, ch.7-12 p.98-202] (Carver framework).
  - Forecast capped ±20 [p.133]
  - Half-Kelly: σ_target = SR_realistic / 2 [p.144]
  - IDM ≤ 2.5 [p.170-171]
  - Position inertia 10% threshold [p.174]
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def build_positions(
    forecasts: pd.DataFrame,
    vol_per_asset: pd.DataFrame,
    sigma_target: float,
    idm: float,
    position_inertia: float,
    off_asset: str,
    external_weights: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Carver vol-targeted positions (long-only).

    When ``external_weights`` is provided, it replaces the ``idm`` uniform
    multiplier per asset. Each asset's allocation is multiplied by
    ``external_weights[asset, t]`` instead of ``idm``. Weights must sum
    to 1 across the pool (will be normalized). See spec §3.3.

    Parameters
    ----------
    forecasts : pd.DataFrame
        Per-asset forecast ∈ [-20, +20] (e.g. EWMAC). Cols=assets.
    vol_per_asset : pd.DataFrame
        Per-asset daily realized vol (decimal, e.g. 0.01).
    sigma_target : float
        Annual portfolio vol target (default 0.25 = Half-Kelly cap).
    idm : float
        Instrument Diversification Multiplier (≤ 2.5 per Carver [p.170-171]).
    position_inertia : float
        Don't rebalance if delta < this fraction (e.g. 0.10 = 10%) [p.174].
    off_asset : str
        Cash residual ticker.
    external_weights : pd.DataFrame | None, optional
        Per-asset portfolio weights (HRP/ERC). When provided, replaces the
        ``idm`` multiplier: each asset uses ``w * N_assets`` as multiplier.
        Configs should set ``idm=1.0`` when using this path (spec §3.3).

    Returns
    -------
    pd.DataFrame
        Daily weights. Long-only (forecasts < 0 → 0).
    """
    if external_weights is None and idm > 2.5:
        raise ValueError(f"idm must be ≤ 2.5 per Carver [p.170-171], got {idm}")

    assets = list(forecasts.columns)
    if off_asset not in assets:
        assets.append(off_asset)

    daily_vol_target = sigma_target / np.sqrt(TRADING_DAYS_PER_YEAR)
    positions = pd.DataFrame(0.0, index=forecasts.index, columns=assets)
    prev_positions = pd.Series(0.0, index=assets)

    for date in forecasts.index:
        target_row = pd.Series(0.0, index=assets)
        for a in forecasts.columns:
            f = forecasts.loc[date, a]
            v = vol_per_asset.loc[date, a]
            if pd.isna(f) or pd.isna(v) or v <= 0 or f <= 0:
                target_row[a] = 0.0
                continue
            # Carver: vol_scalar = daily_vol_target / instrument_vol [p.133]
            vol_scalar = daily_vol_target / v
            if external_weights is not None:
                w = external_weights.loc[date, a] if date in external_weights.index else 0.0
                if pd.isna(w):
                    w = 0.0
                # Per-asset allocation: vol_scalar * f/10 * weight * N_assets
                # The N_assets factor maintains parity with IDM=N case under equal weights
                multiplier = w * len(forecasts.columns)
            else:
                multiplier = idm
            # subsystem_position = vol_scalar × forecast / 10 × multiplier
            target_row[a] = vol_scalar * f / 10.0 * multiplier

        # Cap total long allocation at 1.0 (long-only, no leverage beyond targets)
        long_total = target_row.sum()
        if long_total > 1.0:
            target_row *= 1.0 / long_total
        target_row[off_asset] = max(0.0, 1.0 - target_row.sum())

        # Position inertia: don't rebalance if delta < threshold [p.174]
        for a in assets:
            if abs(target_row[a] - prev_positions[a]) < position_inertia * abs(target_row[a]):
                target_row[a] = prev_positions[a]

        # Renormalize after inertia adjustments
        s = target_row.sum()
        if s > 0:
            target_row /= s

        positions.loc[date] = target_row
        prev_positions = target_row.copy()

    return positions
