"""Iter 012 — TDD specs for asymmetric T10Y3M overlay (equity-leg-only haircut).

Structural distinctions vs iter 009 (dead-end):

* ``smoothing_window = 5`` (not 21) — preserves 6-18 month lead-time.
* ``applied_to = "equity"`` — haircut on ``pos_spy`` only. ``pos_tlt``
  retains full weight (flight-to-quality preserved).

Citations
---------
* `[advances_fin_ml, p.31-34]` — cross-lib parity pattern.
* `[advances_fin_ml, p.162-164]` — σ̂_{t-1} lag + T10Y3M_{t-1} lag.
* `[regime_change, p.5-6, ch.2]` — regime-change principle.
* `[systematic_trading, p.144, ch.9]` — tier-2 half-exposure haircut.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ITER_DIR = (
    Path(__file__).resolve().parent.parent
    / "studies" / "strategy_hunt_loop" / "iterations"
    / "012-2026-04-24-1556-asymmetric-term-spread-overlay"
)
sys.path.insert(0, str(ITER_DIR))

from asymmetric_term_spread_overlay import (  # noqa: E402
    apply_blend_with_asymmetric_overlay,
    compute_gate_series,
    load_term_spread_daily,
)
from overlay_numpy_reference import (  # noqa: E402
    apply_blend_with_asymmetric_overlay_np,
    ema_np,
)


# ---------------------------------------------------------------------------
# Synthetic helpers
# ---------------------------------------------------------------------------


def _synth_returns(n: int, seed: int = 0) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-02", periods=n)
    r_spy = pd.Series(rng.normal(0.0004, 0.010, size=n), index=idx, name="SPY")
    r_tlt = pd.Series(rng.normal(0.0002, 0.006, size=n), index=idx, name="TLT")
    return r_spy, r_tlt


def _synth_term_spread(index: pd.DatetimeIndex, pattern: str = "bimodal") -> pd.Series:
    """Build a deterministic T10Y3M-like series.

    ``bimodal`` : positive in first half, negative in second half (so the
    gate fires on bars ≥ n//2).
    ``always_positive`` / ``always_negative`` : constant regime.
    """
    n = len(index)
    if pattern == "bimodal":
        vals = np.concatenate([np.full(n // 2, +1.0), np.full(n - n // 2, -0.5)])
    elif pattern == "always_positive":
        vals = np.full(n, +1.0)
    elif pattern == "always_negative":
        vals = np.full(n, -0.5)
    else:
        raise ValueError(pattern)
    return pd.Series(vals, index=index, name="term_spread")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGateSemantics:
    """Gate fires when lagged+smoothed signal ≤ threshold; stays 1.0 else."""

    def test_gate_always_one_when_signal_positive(self) -> None:
        idx = pd.bdate_range("2020-01-02", periods=60)
        ts_pos = pd.Series(np.full(60, +1.0), index=idx, name="ts_ema")
        gate = compute_gate_series(ts_pos, threshold=0.0, haircut=0.5)
        assert (gate == 1.0).all()

    def test_gate_equals_haircut_when_signal_negative(self) -> None:
        idx = pd.bdate_range("2020-01-02", periods=60)
        ts_neg = pd.Series(np.full(60, -0.5), index=idx, name="ts_ema")
        gate = compute_gate_series(ts_neg, threshold=0.0, haircut=0.5)
        assert (gate == 0.5).all()

    def test_gate_nan_defaults_to_one(self) -> None:
        idx = pd.bdate_range("2020-01-02", periods=10)
        vals = np.full(10, -0.5)
        vals[:3] = np.nan
        ts = pd.Series(vals, index=idx, name="ts_ema")
        gate = compute_gate_series(ts, threshold=0.0, haircut=0.5)
        assert (gate.iloc[:3] == 1.0).all()
        assert (gate.iloc[3:] == 0.5).all()


class TestAsymmetricApplication:
    """Haircut applied to equity leg ONLY; bond leg retains full weight."""

    def test_equity_leg_halved_bond_leg_unchanged_on_inversion(self) -> None:
        r_spy, r_tlt = _synth_returns(80, seed=1)
        ts_raw = _synth_term_spread(r_spy.index, pattern="always_negative")
        # Pre-compute lagged+smoothed signal
        ts_proc = ts_raw.shift(1).ewm(span=5, adjust=False).mean()

        net_a, pos_spy_a, pos_tlt_a, scale_a, gate_a = (
            apply_blend_with_asymmetric_overlay(
                r_spy, r_tlt,
                ts_ema_lagged=ts_proc,
                target_vol=0.15, lookback=21, max_leverage=2.0,
                haircut=0.5, threshold=0.0,
                cost_bps_per_leg=0.0002,
            )
        )
        # Run the identity case (haircut=1.0) for reference.
        _, pos_spy_id, pos_tlt_id, scale_id, gate_id = (
            apply_blend_with_asymmetric_overlay(
                r_spy, r_tlt,
                ts_ema_lagged=ts_proc,
                target_vol=0.15, lookback=21, max_leverage=2.0,
                haircut=1.0, threshold=0.0,
                cost_bps_per_leg=0.0002,
            )
        )

        # All bars are "inverted" in this fixture → gate = 0.5 throughout.
        assert (gate_a == 0.5).all()
        # SPY position should be halved vs identity case.
        np.testing.assert_allclose(
            pos_spy_a.to_numpy(), pos_spy_id.to_numpy() * 0.5,
            rtol=1e-12, atol=1e-14,
        )
        # TLT position should match identity case (NO haircut applied).
        np.testing.assert_allclose(
            pos_tlt_a.to_numpy(), pos_tlt_id.to_numpy(),
            rtol=1e-12, atol=1e-14,
        )

    def test_no_haircut_path_recovers_iter008_blend(self) -> None:
        """With haircut=1.0 (i.e., effectively disabled), the overlay path
        must reduce to the iter 008 base blend exactly (SPY and TLT both
        full-weight)."""
        from stock_bond_blend import apply_blend_variance_target  # iter 006

        r_spy, r_tlt = _synth_returns(80, seed=2)
        ts_proc = _synth_term_spread(r_spy.index, pattern="always_negative") \
            .shift(1).ewm(span=5, adjust=False).mean()

        net_base, pos_spy_base, pos_tlt_base, scale_base = (
            apply_blend_variance_target(
                r_spy, r_tlt,
                target_vol=0.15, lookback=21, max_leverage=2.0,
                cost_bps_per_leg=0.0002,
            )
        )
        net_a, pos_spy_a, pos_tlt_a, scale_a, gate_a = (
            apply_blend_with_asymmetric_overlay(
                r_spy, r_tlt,
                ts_ema_lagged=ts_proc,
                target_vol=0.15, lookback=21, max_leverage=2.0,
                haircut=1.0, threshold=0.0,
                cost_bps_per_leg=0.0002,
            )
        )
        np.testing.assert_allclose(
            net_a.to_numpy(), net_base.to_numpy(), rtol=1e-12, atol=1e-14,
        )


class TestNoLookahead:
    """Signal must be lagged ≥ 1 bar before smoothing so bar-t gate
    doesn't peek at bar-t's T10Y3M observation."""

    def test_gate_at_bar_t_ignores_raw_signal_at_t(self) -> None:
        idx = pd.bdate_range("2020-01-02", periods=60)
        # Construct raw ts that is positive on first 59 bars and negative
        # only on the LAST bar. A no-lookahead lagged+ema signal at bar
        # 59 must still be positive (hasn't "seen" the flip yet).
        raw = np.full(60, +1.0)
        raw[-1] = -10.0  # strong flip only on last bar
        ts_raw = pd.Series(raw, index=idx, name="term_spread")
        ts_proc = ts_raw.shift(1).ewm(span=5, adjust=False).mean()
        gate = compute_gate_series(ts_proc, threshold=0.0, haircut=0.5)
        # Even with the extreme flip on the last raw bar, the lagged+5d-EMA
        # view at the last bar must remain positive (hasn't absorbed it).
        assert gate.iloc[-1] == 1.0


class TestLoader:
    """Loader must reindex onto equity calendar, forward-fill, lag, then smooth."""

    def test_load_produces_lagged_ema(self, tmp_path: Path) -> None:
        idx_full = pd.bdate_range("2020-01-02", periods=100, name="observation_date")
        raw_vals = np.concatenate([np.full(50, +1.0), np.full(50, -0.5)])
        df = pd.DataFrame({"term_spread": raw_vals}, index=idx_full)
        p = tmp_path / "t10y3m_daily.parquet"
        df.to_parquet(p)

        eq_idx = pd.bdate_range("2020-01-02", periods=100)
        out = load_term_spread_daily(p, eq_idx, smoothing_window=5, lag_bars=1)
        # At bar 50 the raw flipped negative but lag-1 + 5d-EMA should
        # still be positive (smoothed and shifted).
        assert out.iloc[50] > 0.0
        # Well past the flip (say bar 80) the 5d-EMA of lagged value has
        # absorbed the negative regime.
        assert out.iloc[80] < 0.0


class TestCrossLibParity:
    """numpy reference returns within 1e-9 of pandas implementation."""

    def test_numpy_reference_matches_pandas(self) -> None:
        r_spy, r_tlt = _synth_returns(200, seed=11)
        ts_raw = pd.Series(
            np.sin(np.linspace(0, 6.28, 200)) * 0.5,  # oscillates ±0.5
            index=r_spy.index, name="term_spread",
        )
        ts_proc = ts_raw.shift(1).ewm(span=5, adjust=False).mean()

        net_p, pos_spy_p, pos_tlt_p, scale_p, gate_p = (
            apply_blend_with_asymmetric_overlay(
                r_spy, r_tlt,
                ts_ema_lagged=ts_proc,
                target_vol=0.15, lookback=21, max_leverage=2.0,
                haircut=0.5, threshold=0.0,
                cost_bps_per_leg=0.0002,
            )
        )
        net_n, pos_spy_n, pos_tlt_n, scale_n, gate_n = (
            apply_blend_with_asymmetric_overlay_np(
                r_spy.to_numpy(), r_tlt.to_numpy(),
                ts_raw.to_numpy(),
                target_vol=0.15, lookback=21, max_leverage=2.0,
                smoothing_window=5, threshold=0.0, haircut=0.5,
                lag_bars=1, cost_bps_per_leg=0.0002,
            )
        )
        np.testing.assert_allclose(net_p.to_numpy(), net_n, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(pos_spy_p.to_numpy(), pos_spy_n, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(pos_tlt_p.to_numpy(), pos_tlt_n, rtol=1e-9, atol=1e-12)
        np.testing.assert_allclose(gate_p.to_numpy(), gate_n, rtol=1e-9, atol=1e-12)


class TestEmaNp:
    """numpy EMA helper matches pandas ewm(adjust=False)."""

    def test_matches_pandas_on_clean_input(self) -> None:
        rng = np.random.default_rng(42)
        vals = rng.normal(size=100)
        pd_out = pd.Series(vals).ewm(span=5, adjust=False).mean().to_numpy()
        np_out = ema_np(vals, span=5)
        np.testing.assert_allclose(np_out, pd_out, rtol=1e-12, atol=1e-14)
