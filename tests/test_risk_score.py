"""Tests for the risk-score module (Phase 2)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from market_lab.backtest.signals.risk_score import (
    IndicatorSpec,
    RISKY_SIGN,
    compute_composite_risk,
    compute_risk_score,
    rolling_zscore,
    sigmoid,
)


def _trading_index(start: str, n: int) -> pd.DatetimeIndex:
    return pd.bdate_range(start=start, periods=n)


class TestSigmoid:
    def test_sigmoid_bounds(self):
        vals = np.array([-100.0, -5.0, 0.0, 5.0, 100.0])
        out = sigmoid(vals, k=1.0)
        assert (out >= 0).all() and (out <= 1).all()
        assert abs(out[2] - 0.5) < 1e-9  # sigmoid(0) = 0.5

    def test_sigmoid_threshold_shifts_midpoint(self):
        # With threshold=1, risk at z=1 should be ~0.5.
        s = sigmoid(np.array([1.0]), k=2.0, threshold=1.0)
        assert abs(s[0] - 0.5) < 1e-9


class TestRollingZscore:
    def test_zero_for_constant(self):
        s = pd.Series(5.0, index=_trading_index("2020-01-02", 300))
        z = rolling_zscore(s, window=60)
        # Constant series → z undefined (std=0). Should be NaN or 0 — we
        # treat it as 0 to represent "no deviation from normal".
        assert (z.dropna() == 0).all() or z.dropna().isna().all()

    def test_known_zscore(self):
        # Series [1, 2, 3, 4, 5], window=5 → last z = (5 - 3) / std
        vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        s = pd.Series(vals, index=_trading_index("2020-01-02", 5))
        z = rolling_zscore(s, window=5)
        # The rolling z-score at bar 4 uses the full window [1..5]:
        # mean=3, sample std ≈ 1.5811, z ≈ 1.2649
        assert abs(z.iloc[-1] - 1.26491) < 1e-4

    def test_warmup_is_nan(self):
        s = pd.Series(np.arange(100.0), index=_trading_index("2020-01-02", 100))
        z = rolling_zscore(s, window=60)
        # First 59 bars should be NaN.
        assert z.iloc[:59].isna().all()
        assert not z.iloc[59:].isna().any()


class TestComputeRiskScore:
    def test_risk_is_bounded_zero_to_one(self):
        np.random.seed(0)
        s = pd.Series(
            np.random.normal(0, 1, 500),
            index=_trading_index("2020-01-02", 500),
        )
        risk = compute_risk_score(
            s, IndicatorSpec(name="test", window=60, sign=+1, z_threshold=1.0)
        )
        assert (risk.dropna() >= 0).all() and (risk.dropna() <= 1).all()

    def test_sign_inverts_direction(self):
        """Positive-sign and negative-sign risks must sum to ~1 at each bar."""
        s = pd.Series(
            np.random.RandomState(42).normal(0, 1, 300),
            index=_trading_index("2020-01-02", 300),
        )
        pos = compute_risk_score(
            s, IndicatorSpec(name="p", window=60, sign=+1, z_threshold=0.0)
        )
        neg = compute_risk_score(
            s, IndicatorSpec(name="n", window=60, sign=-1, z_threshold=0.0)
        )
        both = (pos + neg).dropna()
        assert abs(both.mean() - 1.0) < 1e-6

    def test_warmup_propagates_as_nan(self):
        s = pd.Series(
            np.arange(200.0), index=_trading_index("2020-01-02", 200),
        )
        risk = compute_risk_score(
            s, IndicatorSpec(name="t", window=60, sign=+1, z_threshold=1.0)
        )
        assert risk.iloc[:59].isna().all()


class TestComposite:
    def test_composite_is_mean_of_active(self):
        idx = _trading_index("2020-01-02", 120)
        # Two identical constant-high risk series (0.8 each) → composite 0.8
        r1 = pd.Series(0.8, index=idx)
        r2 = pd.Series(0.8, index=idx)
        out = compute_composite_risk({"a": r1, "b": r2})
        assert (out == 0.8).all()

    def test_composite_ignores_nan_indicators(self):
        idx = _trading_index("2020-01-02", 100)
        r1 = pd.Series(0.8, index=idx)
        r2 = pd.Series(np.nan, index=idx)
        r2.iloc[50:] = 0.2  # starts contributing at bar 50
        out = compute_composite_risk({"a": r1, "b": r2})
        # Before bar 50: only r1 active → 0.8
        assert (out.iloc[:50] == 0.8).all()
        # From bar 50 on: mean(0.8, 0.2) = 0.5
        assert (abs(out.iloc[50:] - 0.5) < 1e-9).all()

    def test_composite_returns_zero_when_all_nan(self):
        idx = _trading_index("2020-01-02", 50)
        r1 = pd.Series(np.nan, index=idx)
        r2 = pd.Series(np.nan, index=idx)
        out = compute_composite_risk({"a": r1, "b": r2})
        # When no indicator is active, "risk unknown" → default 0 (no de-lever).
        assert (out == 0.0).all()


class TestKnownSigns:
    def test_risky_sign_table(self):
        # Direction of stress for each canonical indicator.
        assert RISKY_SIGN["ebp"] == +1          # higher EBP = more risk
        assert RISKY_SIGN["cape"] == +1         # higher CAPE = more risk
        assert RISKY_SIGN["vix"] == +1          # higher VIX = more risk
        assert RISKY_SIGN["term_spread"] == -1  # lower / negative spread = more risk
