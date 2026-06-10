from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.phases.phase04_validation_gates.run import BranchContext
from lrs.phases.phase07f_composition.run import (
    composed_desired_targets,
    ladder_weight_frame,
)


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2000-01-03", periods=n)


def _context(n: int = 60) -> BranchContext:
    idx = _days(n)
    returns = pd.DataFrame(
        {
            "SPYSIM": np.full(n, 0.001),
            "SSOSIM": np.full(n, 0.002),
            "UPROSIM": np.full(n, 0.003),
            "ZROZSIM": np.full(n, 0.0005),
            "CASHX": np.full(n, 0.0001),
        },
        index=idx,
    )
    return BranchContext(
        branch={"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
        returns=returns,
        sma_signal=pd.Series(True, index=idx),
        underlying_taxed=pd.Series(dtype=float),
    )


def test_ladder_frame_rows_sum_to_one() -> None:
    context = _context()
    lev = pd.Series([0.0, 0.5, 1.0, 1.75, 2.0] * 12, index=context.returns.index)

    frame = ladder_weight_frame(context, lev, 2.0)

    assert np.allclose(frame.sum(axis=1).to_numpy(), 1.0)
    # L=0 days are pure cash; L=2 days are pure 2x ETF.
    assert frame.loc[lev == 0.0, "CASHX"].eq(1.0).all()
    assert frame.loc[lev == 2.0, "SSOSIM"].eq(1.0).all()


def test_composed_targets_blend_linearly() -> None:
    context = _context()
    idx = context.returns.index
    lev = pd.Series(2.0, index=idx)
    risk_off = {"ZROZSIM": 1.0}

    half = composed_desired_targets(context, pd.Series(0.5, index=idx), lev, 2.0, risk_off)

    assert np.allclose(half["SSOSIM"].to_numpy(), 0.5)
    assert np.allclose(half["ZROZSIM"].to_numpy(), 0.5)
    assert np.allclose(half.sum(axis=1).to_numpy(), 1.0)


def test_composed_targets_extremes() -> None:
    context = _context()
    idx = context.returns.index
    lev = pd.Series(1.75, index=idx)
    risk_off = {"ZROZSIM": 0.5, "CASHX": 0.5}

    full_on = composed_desired_targets(context, pd.Series(1.0, index=idx), lev, 2.0, risk_off)
    full_off = composed_desired_targets(context, pd.Series(0.0, index=idx), lev, 2.0, risk_off)

    # f=1: pure ladder (0.25 underlying / 0.75 2x at L=1.75).
    assert np.allclose(full_on["SPYSIM"].to_numpy(), 0.25)
    assert np.allclose(full_on["SSOSIM"].to_numpy(), 0.75)
    assert np.allclose(full_on["ZROZSIM"].to_numpy(), 0.0)
    # f=0: pure risk-off.
    assert np.allclose(full_off["ZROZSIM"].to_numpy(), 0.5)
    assert np.allclose(full_off["CASHX"].to_numpy(), 0.5)
