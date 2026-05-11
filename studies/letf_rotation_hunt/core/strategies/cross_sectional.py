"""Cross-sectional rotation — T4 shape per spec §2.5.

Pool of N LETFs ranked by score (Clenow slope×R² or EWMAC). Hold top-K
equally-weighted; rest = 0%. Master gate (SPY > SMA200) holds cash when off.

Citation: [stocks_on_the_move, p.98-99] (Clenow ranking + master regime filter).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_positions(
    scores: pd.DataFrame,
    master_gate: pd.Series,
    top_k: int,
    off_asset: str,
) -> pd.DataFrame:
    """Build daily weights from cross-sectional ranking.

    Parameters
    ----------
    scores : pd.DataFrame
        Daily ranking scores per asset (cols=assets, rows=dates). NaN allowed.
    master_gate : pd.Series
        {0, 1, NaN} master regime filter (e.g. SPY > SMA200).
    top_k : int
        Number of top-ranked assets to hold (e.g. 2).
    off_asset : str
        Cash held when master_gate=0 OR ranking has fewer than top_k valid scores.

    Returns
    -------
    pd.DataFrame
        Columns = scores.columns + off_asset. Each row sums to 1.0.
    """
    assets = list(scores.columns)
    if off_asset not in assets:
        assets.append(off_asset)

    positions = pd.DataFrame(0.0, index=scores.index, columns=assets)

    for date in scores.index:
        mg = master_gate.get(date, np.nan)
        if pd.isna(mg) or mg == 0:
            positions.loc[date, off_asset] = 1.0
            continue

        row = scores.loc[date].dropna()
        if len(row) < top_k:
            positions.loc[date, off_asset] = 1.0
            continue

        # Pick top-K by score (descending)
        top_assets = row.nlargest(top_k).index.tolist()
        weight = 1.0 / top_k
        for a in top_assets:
            positions.loc[date, a] = weight

    return positions
