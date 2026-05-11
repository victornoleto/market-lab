"""Single LETF Gayed binary rotation — T1 shape per spec §2.2.

Binary on/off: signal=1 → 100% on_asset (LETF); signal=0 → 100% off_asset (BIL/IEF/...).
NaN signal (warmup) → defensive 100% off_asset.

Citation: [leverage_for_the_long_run, p.13] (canonical LRS).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def build_positions(
    signal: pd.Series,
    on_asset: str,
    off_asset: str,
) -> pd.DataFrame:
    """Build daily weights DataFrame from binary signal.

    Parameters
    ----------
    signal : pd.Series
        {0, 1, NaN} signal values.
    on_asset : str
        Ticker held when signal=1 (e.g. "UPRO").
    off_asset : str
        Ticker held when signal=0 or NaN (e.g. "BIL").

    Returns
    -------
    pd.DataFrame
        Columns = [on_asset, off_asset]; rows = signal.index. Each row sums to 1.0.
    """
    on_weight = signal.fillna(0.0).clip(0.0, 1.0)  # 1 when ON; 0 when OFF or NaN
    off_weight = 1.0 - on_weight
    return pd.DataFrame({on_asset: on_weight, off_asset: off_weight}, index=signal.index)
