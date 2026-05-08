"""HFEA-binary basket strategy — T2 shape per spec §2.3.

Two off-state modes:
  - "full_off": 100% off_asset (cash) when signal=0
  - "half_off": zero LETF, keep bond sleeve at full basket weight (HFEA philosophy)

Citation: [risk_parity, ch.5, p.10] (Carlson capital-efficient stacking).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_positions(
    signal: pd.Series,
    on_basket: dict[str, float],
    off_asset: str,
    off_mode: str = "full_off",
    bond_sleeve_assets: list[str] | None = None,
) -> pd.DataFrame:
    """Build daily weights for HFEA-binary strategy.

    Parameters
    ----------
    signal : pd.Series
        {0, 1, NaN} binary signal.
    on_basket : dict[str, float]
        Asset → weight mapping when signal=1. Must sum to 1.0.
    off_asset : str
        Asset held when signal=0 (full_off mode) or remaining cash (half_off).
    off_mode : str
        "full_off" (default) | "half_off".
    bond_sleeve_assets : list[str] | None
        For half_off mode: which on_basket assets to keep at full weight.
        Required if off_mode="half_off".

    Returns
    -------
    pd.DataFrame
        Daily weights. Columns = union of on_basket + off_asset + bond_sleeve_assets.
    """
    total = sum(on_basket.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"on_basket weights must sum to 1.0, got {total}")

    if off_mode == "half_off" and not bond_sleeve_assets:
        raise ValueError("half_off mode requires bond_sleeve_assets")

    all_assets = list(on_basket.keys())
    if off_asset not in all_assets:
        all_assets.append(off_asset)

    positions = pd.DataFrame(0.0, index=signal.index, columns=all_assets)
    on_weight = signal.fillna(0.0).clip(0.0, 1.0)

    for asset, w in on_basket.items():
        positions[asset] = on_weight * w

    if off_mode == "full_off":
        positions[off_asset] += (1 - on_weight)
    elif off_mode == "half_off":
        bond_total = sum(on_basket[a] for a in bond_sleeve_assets if a in on_basket)
        if bond_total <= 0:
            raise ValueError("bond_sleeve_assets must be in on_basket with non-zero weight")
        # When OFF: scale bond sleeve up to fill, zero LETF
        for a in bond_sleeve_assets:
            if a in on_basket:
                positions[a] = on_weight * on_basket[a] + (1 - on_weight) * (on_basket[a] / bond_total)
        # LETF assets (non-bond) zero when OFF
        for a in on_basket:
            if a not in bond_sleeve_assets:
                positions[a] = on_weight * on_basket[a]
    else:
        raise ValueError(f"Unknown off_mode: {off_mode}")

    return positions
