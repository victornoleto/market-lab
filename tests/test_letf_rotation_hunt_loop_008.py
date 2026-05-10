"""Tests for iter 008 (compound-4axis-cscv-diversity) backtest module.

Iter 008 introduces NO new module — it re-uses iter 005's basket_sizer,
iter 006's rate_vol_gate, and iter 007's compound assembly + turnover
helpers via importlib. These tests therefore verify only the iter 008
config grid structure and that the iter delegates correctly to iter
007 helpers (load-bearing for KILL_LOOP #3 / #4 replica-sanity checks).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ITER_DIR = (
    Path(__file__).resolve().parents[1]
    / "studies/letf_rotation_hunt/loop_iterations/008-2026-05-09-compound-4axis-cscv-diversity"
)


def _load_iter008_backtest():
    spec = importlib.util.spec_from_file_location(
        "iter008_backtest", ITER_DIR / "backtest.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BT = _load_iter008_backtest()


def test_config_grid_has_six_configs():
    """6-config 5-mechanic-axis grid as pre-registered in hypothesis.md."""
    assert len(BT.CONFIG_SPECS) == 6


def test_config_grid_spans_five_mechanic_axes():
    """Verify the 5 mechanic-axis variants vs winner replica.

    Each non-baseline non-winner-replica config differs from the winner
    replica (config 2) on exactly one mechanic axis: ON-basket on/off,
    OFF-mechanic on/off, threshold, window, alt-OFF asset.
    """
    by_kind = {s["kind"]: s for s in BT.CONFIG_SPECS}
    expected_kinds = {
        "baseline", "winner_replica", "basket3_only",
        "threshold_p80", "window_120d", "alt_off_ief",
    }
    assert set(by_kind) == expected_kinds

    winner = by_kind["winner_replica"]
    # winner replica = iter 007 best config: basket3 invvol60 × ratevol-p70-60d-CASHX
    assert winner["on_basket"] == ["QLDSIM", "UPROSIM", "UGLSIM"]
    assert winner["on_sizing"] == "invvol"
    assert winner["on_vol_window"] == 60
    assert winner["use_off_override"] is True
    assert winner["off_pct"] == 0.70
    assert winner["off_vol_window"] == 60
    assert winner["alt_off"] == "CASHX"

    # threshold_p80 differs only in off_pct
    assert by_kind["threshold_p80"]["off_pct"] == 0.80
    assert by_kind["threshold_p80"]["off_vol_window"] == 60

    # window_120d differs only in off_vol_window
    assert by_kind["window_120d"]["off_pct"] == 0.70
    assert by_kind["window_120d"]["off_vol_window"] == 120

    # alt_off_ief differs only in alt_off
    assert by_kind["alt_off_ief"]["alt_off"] == "IEFSIM"
    assert by_kind["alt_off_ief"]["off_pct"] == 0.70
    assert by_kind["alt_off_ief"]["off_vol_window"] == 60


def test_iter008_delegates_to_iter007_helpers():
    """Compound assembly + turnover are imported from iter 007 unchanged.

    This is load-bearing for KILL_LOOP #4 (cross-iter winner replica
    must reproduce iter 007's Sortino 1.4637 to within ±0.06).
    """
    assert BT.build_compound_strategy_returns is BT.ITER007.build_compound_strategy_returns
    assert BT.compound_turnover is BT.ITER007.compound_turnover
    assert BT.windowed_returns is BT.ITER007.windowed_returns
    assert BT.compute_per_dataset is BT.ITER007.compute_per_dataset


def test_winner_benchmark_constants_frozen():
    """LOOP_PROTOCOL §"Beats-winner test" requires frozen benchmark."""
    assert BT.WINNER_BENCHMARK_SORTINO == 1.3246
    assert BT.BEATS_THRESHOLD_SORTINO == 1.3746
    assert BT.BEATS_PCT_ABOVE == 0.95
    assert BT.WINNER_BENCHMARK_ITER == "022-2026-05-06-T3d-extended-grid"


def test_trial_accounting_starts_at_iter007_close():
    """cumulative_n_trials_global = 468 (iter 007 close) + 6 = 474."""
    assert BT.PRE_ITER_CUMULATIVE == 468
    assert BT.PRE_ITER_LOOP == 42
    assert BT.LOCAL_N_CONFIGS == 6
    assert BT.PRE_ITER_CUMULATIVE + BT.LOCAL_N_CONFIGS == 474


def test_dataset_windows_match_loop_canonical():
    """Same 4 datasets as iters 005/006/007 for cross-iter comparability."""
    assert set(BT.DATASET_WINDOWS) == {"lh_56y", "modern_1990", "spy_real", "ndx_real"}
    assert BT.DATASET_WINDOWS["lh_56y"] == ("1970-01-01", "2026-04-30")
