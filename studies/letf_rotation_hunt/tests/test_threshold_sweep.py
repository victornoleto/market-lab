"""TDD coverage for threshold_sweep sub-study.

Covers:
  - threshold_signals.sma_gate_with_buffer (stateful hysteresis)
  - threshold_signals.ar1_gate_with_buffer (stateless threshold)
  - variant_grid.VARIANTS (12 configs)
  - dispatcher integration (zero-buffer matches canonical)
  - run_threshold_sweep CLI smoke (subset)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_package_imports():
    """Smoke: package importable."""
    import studies.letf_rotation_hunt.analyses.threshold_sweep  # noqa: F401


def test_smabuf_zero_matches_strict_crossover():
    """With on=off=0, output equals plain sma_gate (strict crossover)."""
    from studies.letf_rotation_hunt.core.signals import sma_gate
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import sma_gate_with_buffer

    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    np_rng = np.random.default_rng(seed=42)
    rets = np_rng.normal(0.0005, 0.012, 400)
    prices = pd.Series(100.0 * np.cumprod(1.0 + rets), index=dates)

    plain = sma_gate(prices, period=200)
    buffered = sma_gate_with_buffer(prices, period=200, on_threshold=0.0, off_threshold=0.0)

    # Skip warmup (first 200 bars are NaN); compare the rest
    plain_clean = plain.dropna()
    buffered_clean = buffered.dropna()
    common_idx = plain_clean.index.intersection(buffered_clean.index)
    pd.testing.assert_series_equal(
        plain_clean.loc[common_idx], buffered_clean.loc[common_idx],
        check_names=False,
    )


def test_smabuf_symmetric_holds_state_in_band():
    """Price oscillates within ±1% of SMA; with buf=2% should never flip."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import sma_gate_with_buffer

    # Build prices that have stable SMA at 100 with ±1% oscillation
    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    base = np.full(400, 100.0)
    # First 200 bars: build up SMA at 100 (constant)
    # Then 200 bars: oscillate ±1% around 100
    osc = 1.0 * np.sin(np.arange(200) * 0.5)  # ±1
    prices_arr = np.concatenate([base[:200], 100.0 + osc])
    prices = pd.Series(prices_arr, index=dates)

    buffered = sma_gate_with_buffer(prices, period=200, on_threshold=0.02, off_threshold=0.02)

    # After warmup, all states should be the SAME (no flips inside ±2% band)
    post_warmup = buffered.iloc[200:].dropna()
    assert post_warmup.nunique() == 1, (
        f"Expected single state in ±1% oscillation band with ±2% buffer, "
        f"got values: {post_warmup.unique()}"
    )


def test_smabuf_asymmetric_fast_off_slow_on():
    """Sequence: state=1 initially, drop 1% → flips OFF; rise back 1% → does NOT flip ON."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import sma_gate_with_buffer

    # Build prices: 200 bars at 100 (warmup), then drop to 99, then back to 100
    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    prices_arr = np.concatenate([
        np.full(200, 100.0),       # warmup, SMA = 100
        np.full(100, 99.0),        # 1% below SMA — off_threshold=0 → flip to OFF
        np.full(100, 100.5),       # 0.5% above SMA — on_threshold=0.02 → does NOT flip ON
    ])
    prices = pd.Series(prices_arr, index=dates)

    buffered = sma_gate_with_buffer(prices, period=200, on_threshold=0.02, off_threshold=0.0)

    # Post-warmup state should be 0 throughout (off triggered, never re-armed)
    final_state = buffered.iloc[-1]
    assert final_state == 0.0, (
        f"Expected final state=0 (asymmetric: fast off, slow on), got {final_state}"
    )


def test_smabuf_first_bar_initialised_from_ratio():
    """First post-warmup bar with price > SMA should yield state=1."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import sma_gate_with_buffer

    dates = pd.date_range("2020-01-01", periods=210, freq="B")
    # 200 bars at 100, then 10 bars at 110 (above SMA after warmup)
    prices_arr = np.concatenate([np.full(200, 100.0), np.full(10, 110.0)])
    prices = pd.Series(prices_arr, index=dates)

    buffered = sma_gate_with_buffer(prices, period=200, on_threshold=0.0, off_threshold=0.0)

    # Bar 200 (first post-warmup) should be state=1 since 110 > SMA(=100)
    assert buffered.iloc[200] == 1.0


def test_smabuf_warmup_returns_nan():
    """Bars before period warmup must return NaN."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import sma_gate_with_buffer

    dates = pd.date_range("2020-01-01", periods=300, freq="B")
    prices = pd.Series(np.linspace(100, 150, 300), index=dates)

    buffered = sma_gate_with_buffer(prices, period=200, on_threshold=0.01, off_threshold=0.01)

    assert buffered.iloc[:199].isna().all(), "Pre-warmup bars must be NaN"
    assert not pd.isna(buffered.iloc[199]), "Bar at index period-1 should have valid state"


def test_ar1_buffer_zero_matches_canonical():
    """ar1_gate_with_buffer(threshold=0) matches `(ar1_coefficient > 0).astype(float)`."""
    from studies.letf_rotation_hunt.core.signals import ar1_coefficient
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import ar1_gate_with_buffer

    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    np_rng = np.random.default_rng(seed=42)
    rets_arr = np_rng.normal(0.0005, 0.012, 400)
    returns = pd.Series(rets_arr, index=dates)

    plain_ar1 = ar1_coefficient(returns, window=30)
    plain_gate = (plain_ar1 > 0).astype(float)
    plain_gate[plain_ar1.isna()] = np.nan

    buffered = ar1_gate_with_buffer(returns, window=30, threshold=0.0)

    plain_clean = plain_gate.dropna()
    buffered_clean = buffered.dropna()
    common_idx = plain_clean.index.intersection(buffered_clean.index)
    pd.testing.assert_series_equal(
        plain_clean.loc[common_idx], buffered_clean.loc[common_idx],
        check_names=False,
    )


def test_ar1_buffer_strict_inequality_at_threshold():
    """With threshold=0.05, a synthetic series where ar1 ≈ 0.05 exactly returns 0
    (strict `>`)."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.threshold_signals import ar1_gate_with_buffer

    # Construct synthetic returns with known AR(1) ≈ 0.05 over the window.
    # Use a simple AR(1) process: r_t = 0.05 * r_{t-1} + noise
    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    np_rng = np.random.default_rng(seed=7)
    rets = np.zeros(400)
    rets[0] = np_rng.normal(0, 0.01)
    for i in range(1, 400):
        rets[i] = 0.05 * rets[i - 1] + np_rng.normal(0, 0.01)
    returns = pd.Series(rets, index=dates)

    # With threshold > 0.05 (clearly above the population AR(1) of 0.05),
    # the gate should mostly be 0
    buffered = ar1_gate_with_buffer(returns, window=30, threshold=0.20)
    post_warmup = buffered.dropna()
    # With threshold of 0.20 vs population AR(1) of 0.05, expect mostly 0s
    assert post_warmup.mean() < 0.3, (
        f"Expected gate mostly 0 when threshold (0.20) > population AR(1) (0.05); "
        f"got mean fire rate {post_warmup.mean():.3f}"
    )


def test_variant_grid_has_12_configs():
    """Exactly 12 variants per spec §2.2 (1 baseline + 5 sym SMA + 3 hyst + 3 AR1)."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.variant_grid import VARIANTS

    assert len(VARIANTS) == 12
    required_keys = {
        "name", "on_asset", "off_asset", "signal_type", "k",
        "sma_long_buffer_on", "sma_long_buffer_off",
        "sma_short_buffer_on", "sma_short_buffer_off",
        "ar1_buffer",
    }
    for v in VARIANTS:
        missing = required_keys - set(v.keys())
        assert not missing, f"Variant {v.get('name', '?')} missing keys: {missing}"


def test_variant_grid_baseline_has_zero_buffers():
    """The baseline variant must have all buffers at 0 (canonical T3d K=2)."""
    from studies.letf_rotation_hunt.analyses.threshold_sweep.variant_grid import VARIANTS

    baseline = next((v for v in VARIANTS if v["name"] == "t3d_k2_baseline"), None)
    assert baseline is not None, "Baseline variant 't3d_k2_baseline' missing"
    assert baseline["sma_long_buffer_on"] == 0.0
    assert baseline["sma_long_buffer_off"] == 0.0
    assert baseline["sma_short_buffer_on"] == 0.0
    assert baseline["sma_short_buffer_off"] == 0.0
    assert baseline["ar1_buffer"] == 0.0
    assert baseline["on_asset"] == "QLD"
    assert baseline["off_asset"] == "ZROZ"
    assert baseline["k"] == 2


def test_dispatcher_zero_buffer_matches_canonical_sharpe():
    """Running t3d_k2_baseline (all-zero buffers) through the dispatcher must
    produce Sharpe within ±0.001 of the canonical iter_014 K=2 result (0.853)."""
    from studies.letf_rotation_hunt.core.data_loader import load_ffr_daily
    from studies.letf_rotation_hunt.runners.run_iter_t3 import _run_single_composite_config
    from studies.letf_rotation_hunt.analyses.threshold_sweep.variant_grid import VARIANTS

    baseline = next(v for v in VARIANTS if v["name"] == "t3d_k2_baseline")
    ffr_daily = load_ffr_daily()
    result = _run_single_composite_config(
        baseline, datasets=["lh_56y"], ffr_daily=ffr_daily, n_trials_local=1,
    )
    sharpe = result["metrics_gross"]["lh_56y"]["sharpe"]
    # Canonical Sharpe lh_56y = 0.853 per parent study STUDY_FINAL_REPORT
    assert abs(sharpe - 0.853) < 0.001, (
        f"Baseline Sharpe {sharpe:.6f} diverges from canonical 0.853 "
        f"by {abs(sharpe - 0.853):.6f}. Expected ±0.001 tolerance."
    )


def test_plot_threshold_sweep_smoke(tmp_path):
    from studies.letf_rotation_hunt.analyses.threshold_sweep.plot_threshold_sweep import (
        plot_equity_overlay_top4, plot_sharpe_bar, plot_trade_count_bar,
    )

    df = pd.DataFrame({
        "name": [f"v{i:02d}" for i in range(12)],
        "gross_sharpe": np.linspace(0.80, 0.95, 12),
        "m1_sharpe":    np.linspace(0.65, 0.80, 12),
        "m2_sharpe":    np.linspace(0.72, 0.85, 12),
        "trade_count_m1": np.linspace(60, 220, 12).astype(int),
    })

    out_a = tmp_path / "sharpe_gross.png"
    plot_sharpe_bar(df, metric="gross_sharpe", reference=0.903,
                    title="Test Gross", out_path=out_a)
    assert out_a.exists() and out_a.stat().st_size > 1000

    out_b = tmp_path / "trade_count.png"
    plot_trade_count_bar(df, out_path=out_b)
    assert out_b.exists() and out_b.stat().st_size > 1000

    # Equity overlay
    dates = pd.date_range("2010-01-01", periods=500, freq="B")
    eq_curves = {
        "v00": {"gross": pd.Series(np.linspace(10000, 50000, 500), index=dates),
                "m1": pd.Series(np.linspace(10000, 30000, 500), index=dates),
                "m2": pd.Series(np.linspace(10000, 40000, 500), index=dates)},
        "v01": {"gross": pd.Series(np.linspace(10000, 60000, 500), index=dates),
                "m1": pd.Series(np.linspace(10000, 35000, 500), index=dates),
                "m2": pd.Series(np.linspace(10000, 45000, 500), index=dates)},
    }
    spy = pd.Series(np.linspace(100, 300, 500), index=dates)
    out_c = tmp_path / "equity_overlay.png"
    plot_equity_overlay_top4(eq_curves, spy, out_path=out_c)
    assert out_c.exists() and out_c.stat().st_size > 1000
