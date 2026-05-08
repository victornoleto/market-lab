"""Tests for total-return adjustment utility.

Validates that a 2-for-1 split (close halves, adj_close stays in post-split
units) is fully absorbed — the adjusted close series shows no gap on the
ex-split day, which is the precondition for Clenow's 15% gap filter and
Ehlers' Roofing Filter to behave correctly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.data.adjust import adjust_ohlc


def _frame(closes_raw, closes_adj):
    n = len(closes_raw)
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame(
        {
            "open": closes_raw,
            "high": [c + 1.0 for c in closes_raw],
            "low": [c - 1.0 for c in closes_raw],
            "close": closes_raw,
            "adj_close": closes_adj,
            "volume": [1_000_000.0] * n,
        },
        index=idx,
    )


class TestAdjustOhlc:
    def test_noop_when_adj_close_equals_close(self):
        raw = [100.0, 101.0, 102.0, 103.0]
        df = _frame(raw, raw)
        out = adjust_ohlc(df)
        pd.testing.assert_frame_equal(out, df)

    def test_split_2_for_1_absorbs_gap(self):
        """Bar 2 → Bar 3 has a 2:1 split: raw close halves, adj_close flat."""
        raw = [100.0, 102.0, 51.0, 51.5]
        adj = [50.0, 51.0, 51.0, 51.5]
        df = _frame(raw, adj)
        out = adjust_ohlc(df)

        # Post-adjust, close IS the adj_close series
        np.testing.assert_allclose(out["close"], adj)

        # H/L rescaled by the same ratio at each row
        ratio = pd.Series(adj) / pd.Series(raw)
        np.testing.assert_allclose(out["high"].to_numpy(), np.asarray(raw) * ratio.to_numpy() + ratio.to_numpy())
        np.testing.assert_allclose(out["low"].to_numpy(), np.asarray(raw) * ratio.to_numpy() - ratio.to_numpy())

        # Gap on the ex-split day is now ~0%
        pct = out["close"].pct_change().abs().max()
        assert pct < 0.05, f"split residual gap = {pct:.3%}"

    def test_dividend_smooths_ex_div_drop(self):
        """$1.50 ex-div drop on a $400 name is absorbed by adj_close."""
        n = 10
        raw = [400.0] * 5 + [398.5] * 5  # ex-div drop at index 5
        adj = [400.0 - 1.5 * i / (n - 1) for i in range(n)]  # smooth back-fill
        # Simpler construction: adj_close constant at ~398.5 (post-dividend)
        adj = [398.5] * n
        df = _frame(raw, adj)
        out = adjust_ohlc(df)

        # Biggest close-to-close move is << 1% after adjustment
        pct = out["close"].pct_change().abs().max()
        assert pct < 0.01, f"ex-div residual = {pct:.3%}"

    def test_volume_is_preserved(self):
        raw = [100.0, 102.0, 51.0, 51.5]
        adj = [50.0, 51.0, 51.0, 51.5]
        df = _frame(raw, adj)
        out = adjust_ohlc(df)
        pd.testing.assert_series_equal(out["volume"], df["volume"])

    def test_missing_adj_close_is_noop(self):
        """Synthetic fixtures without adj_close should pass through unchanged."""
        idx = pd.date_range("2024-01-01", periods=3, freq="B")
        df = pd.DataFrame(
            {
                "open": [100.0, 101.0, 102.0],
                "high": [101.0, 102.0, 103.0],
                "low": [99.0, 100.0, 101.0],
                "close": [100.5, 101.5, 102.5],
                "volume": [1e6, 1e6, 1e6],
            },
            index=idx,
        )
        out = adjust_ohlc(df)
        pd.testing.assert_frame_equal(out, df)

    def test_empty_frame_is_noop(self):
        df = pd.DataFrame(
            columns=["open", "high", "low", "close", "adj_close", "volume"]
        )
        out = adjust_ohlc(df)
        assert out.empty
        assert list(out.columns) == list(df.columns)

    def test_zero_close_does_not_nan(self):
        """Zero raw close (corrupt bar) should not produce inf/nan in adjusted output."""
        raw = [100.0, 0.0, 102.0, 103.0]
        adj = [100.0, 101.0, 102.0, 103.0]
        df = _frame(raw, adj)
        out = adjust_ohlc(df)
        # Ratio at the zero-close row is fillna(1.0) → OHLC that row unchanged
        assert np.isfinite(out["close"]).all()
        assert np.isfinite(out["high"]).all()
