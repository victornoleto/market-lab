"""Composite-signal strategy — T3 shape per spec §2.4.

Accepts a CONTINUOUS weight ∈ [0, 1] (vs binary in T1/T2). Useful for
VIX scaling (T3b), Vote-of-K, or any signal that produces a continuous
allocation between basket and cash.

Citation: [paper.bozovic_2024_vix_managed] (continuous scaling).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_positions(
    weight: pd.Series,
    on_basket: dict[str, float],
    off_asset: str,
) -> pd.DataFrame:
    """Build daily weights from continuous signal weight.

    Parameters
    ----------
    weight : pd.Series
        Continuous ∈ [0, 1]. NaN treated as 0 (defensive OFF).
    on_basket : dict[str, float]
        Asset → fraction of basket. Must sum to 1.0.
    off_asset : str
        Cash equivalent.

    Returns
    -------
    pd.DataFrame
        Daily weights. Each row sums to 1.0.
    """
    total = sum(on_basket.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"on_basket weights must sum to 1.0, got {total}")

    all_assets = list(on_basket.keys())
    if off_asset not in all_assets:
        all_assets.append(off_asset)

    w = weight.fillna(0.0).clip(0.0, 1.0)
    positions = pd.DataFrame(0.0, index=weight.index, columns=all_assets)

    for asset, basket_w in on_basket.items():
        positions[asset] = w * basket_w
    positions[off_asset] += (1 - w)

    return positions
