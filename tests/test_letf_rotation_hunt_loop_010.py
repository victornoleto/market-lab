"""Tests for iter 010 (graded-master-bridge) helper module.

Iter 010 introduces ONE new helper:
`loop_iterations/010-2026-05-09-graded-master-bridge/graded_master_strategy.py`
with `build_graded_master_strategy_returns` + `graded_master_turnover`.

Critical equivalence properties (load-bearing for KILL_LOOP #4 / #5
replica-sanity checks vs iter 007 offleg and iter 009 master_pure):
- gamma=0  ≡  iter 007 `build_compound_strategy_returns(use_off_override=True)`
- gamma=1  ≡  iter 009 `build_master_scope_strategy_returns`

Other properties verified:
- gamma in (0, 1) interpolates linearly in the (ratevol fired, on_signal=ON) cell only
- gamma validation raises ValueError outside [0, 1]
- Signal lag is 1 day (consistent with iters 005/006/007/009)
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/loop_iterations/010-2026-05-09-graded-master-bridge"
)
ITER007_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/loop_iterations/007-2026-05-09-compound-ratevol-off-x-invvol-on-basket"
)
ITER009_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/loop_iterations/009-2026-05-09-master-scope-off-override"
)


def _load(file_path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GMSCOPE = _load(ITER_DIR / "graded_master_strategy.py", "iter010_graded_master")
ITER007_BT = _load(ITER007_DIR / "backtest.py", "iter010_iter007_backtest")
ITER009_MSCOPE = _load(
    ITER009_DIR / "master_scope_strategy.py", "iter010_iter009_master_scope",
)


def _make_synth() -> dict[str, pd.Series]:
    """Synthetic 200-day return + signal series exercising all 4 regime cells."""
    rng = np.random.default_rng(42)
    idx = pd.date_range("2020-01-01", periods=200, freq="B")
    on_basket = pd.Series(rng.normal(0.001, 0.02, 200), index=idx)
    off_zroz = pd.Series(rng.normal(0.0003, 0.012, 200), index=idx)
    alt_off = pd.Series(rng.normal(0.00005, 0.001, 200), index=idx)

    on_signal = pd.Series(0.0, index=idx)
    on_signal.iloc[: 100] = 1.0  # first half ON
    on_signal.iloc[100:] = 0.0   # second half OFF

    ratevol = pd.Series(0.0, index=idx)
    ratevol.iloc[50:75] = 1.0   # ratevol fires during ON regime
    ratevol.iloc[150:175] = 1.0  # ratevol fires during OFF regime

    return {
        "on_signal": on_signal,
        "on_basket": on_basket,
        "off_zroz": off_zroz,
        "alt_off": alt_off,
        "ratevol": ratevol,
    }


def test_gamma_zero_matches_iter007_offleg():
    """gamma=0 must be bit-exactly equivalent to iter 007 offleg-only override.

    Load-bearing for cross-iter KILL_LOOP #4 (offleg replica sanity).
    """
    s = _make_synth()
    r_graded = GMSCOPE.build_graded_master_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
        gamma=0.0,
    )
    r_offleg = ITER007_BT.build_compound_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
        use_off_override=True,
    )
    pd.testing.assert_series_equal(r_graded, r_offleg, check_names=False)


def test_gamma_one_matches_iter009_master():
    """gamma=1 must be bit-exactly equivalent to iter 009 master_scope.

    Load-bearing for cross-iter KILL_LOOP #5 (master replica sanity, when
    iter 010 chooses to add it; otherwise verifies the topology endpoint).
    """
    s = _make_synth()
    r_graded = GMSCOPE.build_graded_master_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
        gamma=1.0,
    )
    r_master = ITER009_MSCOPE.build_master_scope_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
    )
    pd.testing.assert_series_equal(r_graded, r_master, check_names=False)


def test_gamma_half_interpolates_only_in_ratevol_on_cell():
    """For gamma=0.5, only the (ratevol fired, on_signal=ON) cell blends.

    All other cells must equal both iter 007 offleg AND iter 009 master.
    """
    s = _make_synth()
    r_graded = GMSCOPE.build_graded_master_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
        gamma=0.5,
    )
    r_offleg = ITER007_BT.build_compound_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
        use_off_override=True,
    )
    r_master = ITER009_MSCOPE.build_master_scope_strategy_returns(
        on_signal=s["on_signal"],
        on_basket_returns=s["on_basket"],
        off_returns=s["off_zroz"],
        alt_off_returns=s["alt_off"],
        ratevol_gate=s["ratevol"],
    )

    on_lag = s["on_signal"].shift(1)
    rv_lag = s["ratevol"].shift(1).fillna(0.0)
    blend_idx = r_graded.index[
        (on_lag.reindex(r_graded.index) == 1)
        & (rv_lag.reindex(r_graded.index) == 1)
    ]
    non_blend_idx = r_graded.index.difference(blend_idx)

    assert len(blend_idx) > 0, "synthetic series must include ratevol+ON cells"
    assert len(non_blend_idx) > 0, "synthetic series must include non-blend cells"

    pd.testing.assert_series_equal(
        r_graded.loc[non_blend_idx], r_offleg.loc[non_blend_idx], check_names=False,
    )
    pd.testing.assert_series_equal(
        r_graded.loc[non_blend_idx], r_master.loc[non_blend_idx], check_names=False,
    )

    expected_blend = (
        0.5 * r_master.loc[blend_idx]
        + 0.5 * r_offleg.loc[blend_idx]
    )
    pd.testing.assert_series_equal(
        r_graded.loc[blend_idx], expected_blend, check_names=False,
    )


def test_gamma_validation_raises():
    """gamma must be in [0, 1]; out-of-range values raise ValueError."""
    s = _make_synth()
    for bad in (-0.01, 1.01, -1.0, 2.0):
        with pytest.raises(ValueError, match="gamma must be in"):
            GMSCOPE.build_graded_master_strategy_returns(
                on_signal=s["on_signal"],
                on_basket_returns=s["on_basket"],
                off_returns=s["off_zroz"],
                alt_off_returns=s["alt_off"],
                ratevol_gate=s["ratevol"],
                gamma=bad,
            )
        with pytest.raises(ValueError, match="gamma must be in"):
            GMSCOPE.graded_master_turnover(
                weights=None,
                on_signal=s["on_signal"],
                ratevol_gate=s["ratevol"],
                gamma=bad,
            )


def test_signal_lag_is_one_day():
    """Strategy uses lagged signals (close-of-t-1 → applied at t) per
    iters 005/006/007/009 convention. Verified by checking that an ON
    signal that flips ON at t produces basket return at t+1, not t.
    """
    idx = pd.date_range("2020-01-01", periods=10, freq="B")
    on_basket = pd.Series([0.10] * 10, index=idx)
    off_zroz = pd.Series([0.01] * 10, index=idx)
    alt_off = pd.Series([0.001] * 10, index=idx)
    ratevol = pd.Series([0.0] * 10, index=idx)

    on_signal = pd.Series([0.0] * 10, index=idx)
    on_signal.iloc[5:] = 1.0  # flips ON at index 5

    r = GMSCOPE.build_graded_master_strategy_returns(
        on_signal=on_signal,
        on_basket_returns=on_basket,
        off_returns=off_zroz,
        alt_off_returns=alt_off,
        ratevol_gate=ratevol,
        gamma=0.5,
    )

    assert r.loc[idx[5]] == pytest.approx(0.01), (
        "at flip day t=5, on_signal_lag(t=5) = on_signal(t=4) = 0 → off_zroz return"
    )
    assert r.loc[idx[6]] == pytest.approx(0.10), (
        "at t=6, on_signal_lag(t=6) = on_signal(t=5) = 1 → on_basket return"
    )


def test_turnover_low_when_signals_constant():
    """Constant signals → at most 1 turnover unit per year (boundary NaN
    in `exposure.shift(1)` comparison, matching iter 007/009 convention).
    """
    idx = pd.date_range("2020-01-01", periods=252, freq="B")
    on_signal = pd.Series([1.0] * 252, index=idx)
    ratevol = pd.Series([0.0] * 252, index=idx)

    turnover = GMSCOPE.graded_master_turnover(
        weights=None,
        on_signal=on_signal,
        ratevol_gate=ratevol,
        gamma=0.5,
    )
    assert turnover < 1.5


def test_turnover_positive_when_state_oscillates():
    """Many state changes ⇒ positive turnover."""
    idx = pd.date_range("2020-01-01", periods=252, freq="B")
    on_signal = pd.Series([float(i % 2) for i in range(252)], index=idx)
    ratevol = pd.Series([0.0] * 252, index=idx)

    turnover = GMSCOPE.graded_master_turnover(
        weights=None,
        on_signal=on_signal,
        ratevol_gate=ratevol,
        gamma=0.5,
    )
    assert turnover > 100.0
