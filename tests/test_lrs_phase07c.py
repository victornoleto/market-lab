from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from lrs.phases.phase04_validation_gates.run import BranchContext
from lrs.phases.phase07c_macro_gtt_gate.run import gtt_signal


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2000-01-03", periods=n)


def _context(n: int = 300, seed: int = 0) -> BranchContext:
    rng = np.random.default_rng(seed)
    idx = _days(n)
    returns = pd.DataFrame(
        {
            "SPYSIM": 0.01 * rng.standard_normal(n),
            "SSOSIM": 0.02 * rng.standard_normal(n),
            "UPROSIM": 0.03 * rng.standard_normal(n),
            "ZROZSIM": 0.01 * rng.standard_normal(n),
            "CASHX": np.full(n, 0.0001),
        },
        index=idx,
    )
    sma_signal = pd.Series(rng.random(n) > 0.5, index=idx)
    return BranchContext(
        branch={"branch": "SPY", "underlying": "SPYSIM", "lev2": "SSOSIM", "lev3": "UPROSIM"},
        returns=returns,
        sma_signal=sma_signal,
        underlying_taxed=pd.Series(dtype=float),
    )


_NO_VOL = {"name": "none", "window": 0, "threshold": None}


def test_forced_macro_risk_reproduces_base_signal() -> None:
    context = _context()
    macro = pd.Series(True, index=context.returns.index)

    for scope in ("trend_only", "trend_and_vol"):
        signal = gtt_signal(context, _NO_VOL, macro, scope)
        assert (signal == context.sma_signal).all()


def test_expansion_override_trend_and_vol_is_always_on() -> None:
    context = _context(seed=1)
    macro = pd.Series(False, index=context.returns.index)

    signal = gtt_signal(context, _NO_VOL, macro, "trend_and_vol")

    assert signal.all()


def test_expansion_override_trend_only_keeps_vol_gate() -> None:
    context = _context(seed=2)
    macro = pd.Series(False, index=context.returns.index)
    # A vol spec tight enough to be False on some days.
    vol_spec = {"name": "RV21 <= 1%", "window": 21, "threshold": 0.01}

    signal = gtt_signal(context, vol_spec, macro, "trend_only")

    # In expansion the trend gate is bypassed but the vol gate still binds:
    # signal must equal the vol gate itself, regardless of the SMA state.
    from lrs.phases.phase04_validation_gates.run import vol_gate

    expected = vol_gate(context, vol_spec).reindex(context.returns.index).fillna(False)
    assert (signal == expected).all()


def test_mixed_regime_switches_between_base_and_override() -> None:
    context = _context(seed=3)
    idx = context.returns.index
    macro = pd.Series([True, False] * (len(idx) // 2), index=idx)

    signal = gtt_signal(context, _NO_VOL, macro, "trend_and_vol")

    assert (signal[macro] == context.sma_signal[macro]).all()
    assert signal[~macro].all()


def test_unknown_scope_rejected() -> None:
    context = _context(seed=4)
    macro = pd.Series(True, index=context.returns.index)
    with pytest.raises(ValueError):
        gtt_signal(context, _NO_VOL, macro, "bogus")
