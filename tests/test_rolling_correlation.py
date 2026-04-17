"""Unit tests for ``backtest.metrics.rolling_correlation`` — Phase 3.5b Task 7e."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.metrics.rolling_correlation import (
    CANONICAL_HIGH_RHO_THRESHOLD,
    CANONICAL_WINDOWS,
    HighCorrelationRegime,
    PairwiseRollingStats,
    compute_rolling_correlation_report,
    find_high_correlation_regimes,
    pairwise_rolling_correlations,
    render_rolling_correlation_markdown,
    summarize_pair,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _bdate_index(n: int, start: str = "2010-01-04") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n, freq="B")


def _rand_series(n: int, seed: int, name: str) -> pd.Series:
    rng = np.random.default_rng(seed)
    return pd.Series(rng.normal(0.0, 0.01, size=n), index=_bdate_index(n), name=name)


# ---------------------------------------------------------------------------
# Canonical knobs
# ---------------------------------------------------------------------------


def test_canonical_windows_match_spec() -> None:
    assert CANONICAL_WINDOWS == (63, 252)
    assert CANONICAL_HIGH_RHO_THRESHOLD == 0.7


# ---------------------------------------------------------------------------
# pairwise_rolling_correlations
# ---------------------------------------------------------------------------


class TestPairwiseRolling:
    def test_shape_and_columns_use_series_names(self) -> None:
        a = _rand_series(300, 0, "LETF")
        b = _rand_series(300, 1, "QQQ")
        c = _rand_series(300, 2, "GLD")
        rolling = pairwise_rolling_correlations(a, b, c, window=63)
        assert list(rolling.columns) == ["LETF_vs_QQQ", "LETF_vs_GLD", "QQQ_vs_GLD"]
        assert len(rolling) == 300
        # First 62 rows must be NaN (min_periods=window=63).
        assert rolling.iloc[:62].isna().all().all()
        assert rolling.iloc[62:].notna().all().all()

    def test_perfectly_correlated_pair_gives_one(self) -> None:
        a = _rand_series(200, 3, "A")
        b = a.rename("B")
        c = _rand_series(200, 7, "C")
        rolling = pairwise_rolling_correlations(a, b, c, window=63)
        # A_vs_B must be 1.0 everywhere (post-warmup).
        assert np.isclose(rolling["A_vs_B"].dropna(), 1.0).all()

    def test_anti_correlated_pair_gives_minus_one(self) -> None:
        a = _rand_series(200, 9, "A")
        b = (-a).rename("B")
        c = _rand_series(200, 11, "C")
        rolling = pairwise_rolling_correlations(a, b, c, window=63)
        assert np.isclose(rolling["A_vs_B"].dropna(), -1.0).all()

    def test_rejects_short_window(self) -> None:
        a = _rand_series(100, 0, "A")
        b = _rand_series(100, 1, "B")
        c = _rand_series(100, 2, "C")
        with pytest.raises(ValueError, match=">= 2"):
            pairwise_rolling_correlations(a, b, c, window=1)

    def test_rejects_misaligned_indexes(self) -> None:
        a = _rand_series(100, 0, "A")
        b = _rand_series(100, 1, "B")
        # Shift c's index by 1 day so it no longer matches a/b.
        c_shifted = pd.Series(
            np.random.default_rng(2).normal(size=100),
            index=_bdate_index(100, start="2010-01-05"),
            name="C",
        )
        with pytest.raises(ValueError, match="identical indexes"):
            pairwise_rolling_correlations(a, b, c_shifted, window=10)


# ---------------------------------------------------------------------------
# summarize_pair
# ---------------------------------------------------------------------------


class TestSummarizePair:
    def test_all_above_threshold(self) -> None:
        idx = _bdate_index(100)
        s = pd.Series(np.full(100, 0.85), index=idx, name="X_vs_Y")
        stats = summarize_pair(s, window=63, threshold=0.7)
        assert stats.bars == 100
        assert stats.mean == pytest.approx(0.85)
        assert stats.frac_above_threshold == pytest.approx(1.0)
        assert stats.longest_streak_above == 100
        assert stats.std == pytest.approx(0.0, abs=1e-12)

    def test_all_below_threshold(self) -> None:
        idx = _bdate_index(50)
        s = pd.Series(np.full(50, 0.1), index=idx, name="X_vs_Y")
        stats = summarize_pair(s, window=63, threshold=0.7)
        assert stats.frac_above_threshold == 0.0
        assert stats.longest_streak_above == 0

    def test_alternating_streaks(self) -> None:
        idx = _bdate_index(10)
        vals = np.array([0.8, 0.8, 0.8, 0.1, 0.1, 0.9, 0.9, 0.9, 0.9, 0.2])
        s = pd.Series(vals, index=idx, name="X_vs_Y")
        stats = summarize_pair(s, window=5, threshold=0.7)
        assert stats.longest_streak_above == 4  # last four
        assert stats.frac_above_threshold == pytest.approx(7 / 10)

    def test_handles_empty_series(self) -> None:
        s = pd.Series([np.nan, np.nan], index=_bdate_index(2), name="X_vs_Y")
        stats = summarize_pair(s, window=63, threshold=0.7)
        assert stats.bars == 0
        assert stats.longest_streak_above == 0
        assert stats.frac_above_threshold == 0.0


# ---------------------------------------------------------------------------
# find_high_correlation_regimes
# ---------------------------------------------------------------------------


class TestFindRegimes:
    def test_detects_simultaneous_high_rho_streak(self) -> None:
        idx = _bdate_index(20)
        # All three pairs >= 0.7 on days 5-14 (10 bars).
        ab = np.array([0.1] * 5 + [0.8] * 10 + [0.1] * 5)
        ac = np.array([0.2] * 5 + [0.85] * 10 + [0.2] * 5)
        bc = np.array([0.0] * 5 + [0.9] * 10 + [0.0] * 5)
        rolling = pd.DataFrame(
            {"A_vs_B": ab, "A_vs_C": ac, "B_vs_C": bc}, index=idx
        )
        regimes = find_high_correlation_regimes(rolling, window=63, threshold=0.7, min_bars=5)
        assert len(regimes) == 1
        r = regimes[0]
        assert r.bars == 10
        assert r.start == idx[5]
        assert r.end == idx[14]
        assert r.mean_rho_letf_qqq == pytest.approx(0.8)
        assert r.mean_rho_letf_gld == pytest.approx(0.85)
        assert r.mean_rho_qqq_gld == pytest.approx(0.9)

    def test_ignores_streaks_below_min_bars(self) -> None:
        idx = _bdate_index(12)
        ab = np.array([0.1] * 5 + [0.8] * 3 + [0.1] * 4)
        ac = np.array([0.1] * 5 + [0.8] * 3 + [0.1] * 4)
        bc = np.array([0.1] * 5 + [0.8] * 3 + [0.1] * 4)
        rolling = pd.DataFrame(
            {"A_vs_B": ab, "A_vs_C": ac, "B_vs_C": bc}, index=idx
        )
        regimes = find_high_correlation_regimes(rolling, window=63, threshold=0.7, min_bars=5)
        assert regimes == []

    def test_requires_all_three_pairs_above_threshold(self) -> None:
        idx = _bdate_index(20)
        # Only 2 of 3 pairs exceed — no regime.
        ab = np.array([0.8] * 20)
        ac = np.array([0.8] * 20)
        bc = np.array([0.1] * 20)
        rolling = pd.DataFrame(
            {"A_vs_B": ab, "A_vs_C": ac, "B_vs_C": bc}, index=idx
        )
        regimes = find_high_correlation_regimes(rolling, window=63, threshold=0.7, min_bars=3)
        assert regimes == []

    def test_rejects_non_3col_input(self) -> None:
        idx = _bdate_index(10)
        bad = pd.DataFrame({"a": np.ones(10), "b": np.ones(10)}, index=idx)
        with pytest.raises(ValueError, match="3-column"):
            find_high_correlation_regimes(bad, window=63)


# ---------------------------------------------------------------------------
# compute_rolling_correlation_report (integration)
# ---------------------------------------------------------------------------


class TestComputeReport:
    def test_end_to_end_with_correlated_legs(self) -> None:
        # Build 3 legs where LETF ≈ QQQ (highly correlated) and GLD is independent.
        n = 400
        idx = _bdate_index(n)
        rng = np.random.default_rng(123)
        common = rng.normal(0, 0.01, size=n)
        letf = pd.Series(common + rng.normal(0, 0.002, size=n), index=idx, name="LETF_raw")
        qqq = pd.Series(common + rng.normal(0, 0.002, size=n), index=idx, name="QQQ_raw")
        gld = pd.Series(rng.normal(0, 0.008, size=n), index=idx, name="GLD_raw")

        report = compute_rolling_correlation_report(
            letf, qqq, gld, windows=(63, 252), threshold=0.7
        )
        assert report.bars == n
        assert len(report.pair_stats) == 6  # 3 pairs × 2 windows
        # The pair labels must use the canonical leg_names defaults (LETF, QQQ, GLD).
        expected_pairs = {
            "LETF_vs_QQQ",
            "LETF_vs_GLD",
            "QQQ_vs_GLD",
        }
        assert {s.pair for s in report.pair_stats} == expected_pairs

        # LETF vs QQQ mean ρ should be clearly high (> 0.8) — common-noise design.
        letf_qqq_stats = [s for s in report.pair_stats if s.pair == "LETF_vs_QQQ"]
        for s in letf_qqq_stats:
            assert s.mean > 0.8, f"window={s.window}: mean={s.mean}"

        # LETF vs GLD and QQQ vs GLD should have much lower mean ρ (|ρ| well under 0.3).
        for s in report.pair_stats:
            if s.pair in {"LETF_vs_GLD", "QQQ_vs_GLD"}:
                assert abs(s.mean) < 0.3, f"{s.pair} w={s.window}: mean={s.mean}"

        # Regime detection: shouldn't find ALL-three-above regimes because GLD is independent.
        assert report.regimes == ()
        # Series export should be keyed by window and shaped (bars, 3).
        assert set(report.series.keys()) == {63, 252}
        assert report.series[63].shape == (n, 3)

    def test_report_detects_regime_when_all_legs_move_together(self) -> None:
        # Construct a segment where all three legs are common-factor driven → all ρ ≈ 1.
        n = 500
        idx = _bdate_index(n)
        rng = np.random.default_rng(7)
        noise = rng.normal(0, 0.01, size=n)

        # First 300 bars: independent. Last 200: identical common factor.
        indep_a = noise + rng.normal(0, 0.005, size=n)
        indep_b = noise + rng.normal(0, 0.005, size=n)
        indep_c = rng.normal(0, 0.012, size=n)
        crisis = rng.normal(0, 0.01, size=n)
        letf_vals = np.concatenate([indep_a[:300], crisis[300:]])
        qqq_vals = np.concatenate([indep_b[:300], crisis[300:]])
        gld_vals = np.concatenate([indep_c[:300], crisis[300:]])

        letf = pd.Series(letf_vals, index=idx, name="LETF_raw")
        qqq = pd.Series(qqq_vals, index=idx, name="QQQ_raw")
        gld = pd.Series(gld_vals, index=idx, name="GLD_raw")

        report = compute_rolling_correlation_report(
            letf, qqq, gld, windows=(63,), threshold=0.7, min_regime_bars=20
        )
        # At least one regime found, covering part of the crisis tail.
        assert len(report.regimes) >= 1
        tail = report.regimes[-1]
        assert tail.end == idx[n - 1]
        assert tail.bars >= 20


# ---------------------------------------------------------------------------
# render_rolling_correlation_markdown
# ---------------------------------------------------------------------------


def test_render_markdown_contains_expected_sections() -> None:
    stats = PairwiseRollingStats(
        pair="LETF_vs_QQQ",
        window=63,
        bars=100,
        mean=0.6,
        median=0.61,
        std=0.1,
        min=0.2,
        max=0.9,
        p25=0.55,
        p75=0.7,
        last=0.65,
        frac_above_threshold=0.3,
        threshold=0.7,
        longest_streak_above=12,
    )
    regime = HighCorrelationRegime(
        window=63,
        threshold=0.7,
        start=pd.Timestamp("2020-03-01"),
        end=pd.Timestamp("2020-04-30"),
        bars=42,
        mean_rho_letf_qqq=0.87,
        mean_rho_letf_gld=0.81,
        mean_rho_qqq_gld=0.79,
    )
    from ai_trade.backtest.metrics.rolling_correlation import RollingCorrelationReport

    report = RollingCorrelationReport(
        leg_names=("LETF", "QQQ", "GLD"),
        common_start=pd.Timestamp("2010-01-04"),
        common_end=pd.Timestamp("2026-04-14"),
        bars=4000,
        threshold=0.7,
        windows=(63, 252),
        pair_stats=(stats,),
        regimes=(regime,),
        series={},
    )
    md = render_rolling_correlation_markdown(report)
    assert "Rolling correlation" in md
    assert "Pair-wise rolling ρ — summary statistics" in md
    assert "High-ρ regimes" in md
    assert "LETF_vs_QQQ" in md
    assert "2020-03-01" in md
    assert "2020-04-30" in md
    # Threshold should show up (either as a column value or in the header sentence).
    assert "0.70" in md
