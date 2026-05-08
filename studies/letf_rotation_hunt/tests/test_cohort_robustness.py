"""TDD coverage for cohort_robustness sub-study.

Covers:
  - cohort_dates.py — 8 cohort entry dates within data range
  - regime_classifier.py — K-count via canonical T3d signals
  - slice_equity.py — forward window, recovery time, beat-SPY time
  - plot_*.py — smoke tests that PNGs are emitted
  - run_cohort_robustness.py — CLI smoke

Reuses existing fixtures and reconstruct.py from tax_comparison/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_package_imports():
    """Smoke: package importable."""
    import studies.letf_rotation_hunt.cohort_robustness  # noqa: F401


def test_cohort_dates_within_data_range():
    """All 8 cohort dates must fall within lh_56y data range (1986-2026)."""
    from studies.letf_rotation_hunt.cohort_robustness.cohort_dates import COHORT_DATES

    assert len(COHORT_DATES) == 8
    earliest = pd.Timestamp("1986-01-01")
    latest = pd.Timestamp("2026-04-30")
    for c in COHORT_DATES:
        d = pd.Timestamp(c["date"])
        assert earliest <= d <= latest, f"{c['date']} outside data range"
        assert c["tier"] in ("worst", "control")
        assert c["event"]  # non-empty


def test_cohort_dates_have_unique_ids():
    from studies.letf_rotation_hunt.cohort_robustness.cohort_dates import COHORT_DATES
    ids = [c["cohort_id"] for c in COHORT_DATES]
    assert len(set(ids)) == 8
    assert ids == sorted(ids)  # 01..08 monotonic


def test_classify_regimes_returns_one_label_per_month():
    """For a 24-month synthetic dataset, classifier returns 1 row per month-end."""
    from studies.letf_rotation_hunt.cohort_robustness.regime_classifier import classify_regimes

    # Synthetic: 600 daily bars (~24 months business days)
    dates = pd.date_range("2020-01-01", periods=600, freq="B")
    np_rng = np.random.default_rng(seed=42)
    rets = np_rng.normal(0.0005, 0.012, 600)
    prices = pd.Series(100.0 * np.cumprod(1.0 + rets), index=dates)

    df = classify_regimes(prices)

    assert "k_count" in df.columns
    assert "regime" in df.columns
    assert df["k_count"].between(0, 4).all()
    # All-on / Mostly-on / Borderline / Risk-off only
    assert set(df["regime"].unique()) <= {"All-on", "Mostly-on", "Borderline", "Risk-off"}


def test_classify_regimes_strong_uptrend_is_all_on():
    """Pure exponential uptrend with low vol → K=4 (All-on) at the end."""
    from studies.letf_rotation_hunt.cohort_robustness.regime_classifier import classify_regimes

    # 400 bars of steady +0.05%/day, near-zero vol
    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    prices = pd.Series(100.0 * (1.0005 ** np.arange(400)), index=dates)

    df = classify_regimes(prices)

    # The last available month-end should be All-on (above SMA200, SMA50, low vol, positive AR1)
    last = df.dropna(subset=["k_count"]).iloc[-1]
    assert last["k_count"] == 4
    assert last["regime"] == "All-on"


def test_classify_regimes_strong_drawdown_is_risk_off():
    """Pure exponential drawdown with high vol → K∈{0,1} (Risk-off)."""
    from studies.letf_rotation_hunt.cohort_robustness.regime_classifier import classify_regimes

    dates = pd.date_range("2020-01-01", periods=400, freq="B")
    # Steep decline: -0.3%/day with 3% daily vol
    np_rng = np.random.default_rng(seed=7)
    rets = np_rng.normal(-0.003, 0.03, 400)
    prices = pd.Series(100.0 * np.cumprod(1.0 + rets), index=dates)

    df = classify_regimes(prices)

    last = df.dropna(subset=["k_count"]).iloc[-1]
    assert last["k_count"] <= 1
    assert last["regime"] == "Risk-off"


def test_slice_forward_window_basic():
    """Slicing 5y forward from a known date returns ~252×5 = 1260 rows."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import slice_forward_window

    dates = pd.date_range("1990-01-01", "2010-12-31", freq="B")
    eq = pd.Series(np.linspace(1, 2, len(dates)), index=dates)

    sliced = slice_forward_window(eq, entry_date="2000-01-03", years=5)

    # ~5 business years ≈ 1305 bars (5×261 ≈ 1305 with weekday business days)
    assert 1200 <= len(sliced) <= 1400
    assert sliced.index[0] >= pd.Timestamp("2000-01-03")
    assert sliced.index[-1] <= pd.Timestamp("2005-01-03") + pd.Timedelta(days=7)


def test_slice_forward_window_truncates_at_end_of_data():
    """If entry_date + years exceeds data, returns whatever is available."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import slice_forward_window

    dates = pd.date_range("2020-01-01", "2026-01-01", freq="B")
    eq = pd.Series(np.linspace(1, 2, len(dates)), index=dates)

    sliced = slice_forward_window(eq, entry_date="2024-06-01", years=10)

    # Only ~1.5 years of data after 2024-06-01
    assert sliced.index[0] >= pd.Timestamp("2024-06-01")
    assert sliced.index[-1] <= pd.Timestamp("2026-01-01")


def test_time_to_recovery_basic():
    """Equity dips 50% then climbs back to 100 — recovery is when it crosses 100 again."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import time_to_recovery

    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    eq = pd.Series([100, 80, 60, 50, 60, 80, 95, 100, 110, 105], index=dates)

    days = time_to_recovery(eq)

    # Crosses 100 again at index 7 (day 8) → 7 days from start
    assert days == 7


def test_time_to_recovery_returns_nan_when_never():
    """Equity drops and never recovers."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import time_to_recovery

    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    eq = pd.Series([100, 80, 60, 50, 40], index=dates)

    days = time_to_recovery(eq)

    assert pd.isna(days)


def test_time_to_beat_spy_strategy_above_throughout():
    """Strategy always above SPY — beats from day 1 (returns 0)."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import time_to_beat_spy

    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    strat = pd.Series([100, 110, 120, 130, 140], index=dates)
    spy = pd.Series([100, 105, 110, 115, 120], index=dates)

    days = time_to_beat_spy(strat, spy)

    assert days == 0


def test_time_to_beat_spy_strategy_loses_first_then_wins():
    """Strategy drops below SPY then crosses back above on day 5."""
    from studies.letf_rotation_hunt.cohort_robustness.slice_equity import time_to_beat_spy

    dates = pd.date_range("2020-01-01", periods=6, freq="D")
    strat = pd.Series([100, 90, 80, 90, 95, 110], index=dates)
    spy = pd.Series([100, 105, 110, 105, 100, 95], index=dates)

    days = time_to_beat_spy(strat, spy)

    # Day 5 (index 5) is the first day strat > spy → 5 days from start
    assert days == 5


def test_plot_cohort_smoke(tmp_path):
    from studies.letf_rotation_hunt.cohort_robustness.plot_cohort import plot_cohort

    dates = pd.date_range("2000-01-01", periods=2520, freq="B")  # ~10y
    np_rng = np.random.default_rng(seed=0)
    eq_canonical = pd.Series(
        10_000 * np.cumprod(1 + np_rng.normal(0.0005, 0.015, 2520)), index=dates,
    )
    eq_sma250 = pd.Series(
        10_000 * np.cumprod(1 + np_rng.normal(0.0006, 0.014, 2520)), index=dates,
    )
    eq_tqqq = pd.Series(
        10_000 * np.cumprod(1 + np_rng.normal(0.0007, 0.020, 2520)), index=dates,
    )
    eq_spy = pd.Series(
        10_000 * np.cumprod(1 + np_rng.normal(0.0003, 0.012, 2520)), index=dates,
    )

    out = tmp_path / "cohort_test.png"
    plot_cohort(
        cohort={"cohort_id": "01", "date": "2000-03-24",
                "event": "NDX dotcom peak", "tier": "worst"},
        eq_per_config={
            "qld_vote_k2_off_zroz": eq_canonical,
            "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz": eq_sma250,
            "tqqq_voteK2_off_zroz": eq_tqqq,
        },
        eq_spy=eq_spy,
        out_path=out,
    )

    assert out.exists()
    assert out.stat().st_size > 1000  # non-empty PNG


def test_plot_regime_violin_smoke(tmp_path):
    from studies.letf_rotation_hunt.cohort_robustness.plot_regime import plot_regime_violin

    np_rng = np.random.default_rng(seed=0)
    rows = []
    regimes = ["All-on", "Mostly-on", "Borderline", "Risk-off"]
    configs = ["qld_vote_k2_off_zroz",
               "qld_voteK2_sma250_100_vol21_40_ar30_off_zroz",
               "tqqq_voteK2_off_zroz"]
    for r in regimes:
        for c in configs:
            for _ in range(40):
                rows.append({
                    "regime": r,
                    "config_name": c,
                    "forward_5y_sharpe": float(np_rng.normal(0.7, 0.2)),
                })
    df = pd.DataFrame(rows)

    out = tmp_path / "regime_violin.png"
    plot_regime_violin(df, out_path=out)

    assert out.exists()
    assert out.stat().st_size > 1000


def test_plot_heatmap_smoke(tmp_path):
    from studies.letf_rotation_hunt.cohort_robustness.plot_heatmap import plot_forward_heatmap

    # Synthetic parquet-like df
    rng = pd.date_range("2000-01-31", "2020-12-31", freq="BME")
    rows = []
    for d in rng:
        for ws in [3, 5, 10, 15, 20]:
            rows.append({
                "config": "qld_vote_k2_off_zroz",
                "window_size_y": ws,
                "start_date": d,
                "sharpe": 0.7 + 0.1 * (ws / 20.0),
            })
    df = pd.DataFrame(rows)

    out = tmp_path / "heatmap.png"
    plot_forward_heatmap(
        df=df, config_name="qld_vote_k2_off_zroz", out_path=out,
        spy_anchor=0.682,
    )

    assert out.exists()
    assert out.stat().st_size > 1000
