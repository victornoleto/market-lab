from __future__ import annotations

import numpy as np
import pandas as pd

from lrs.phases.phase06c_wf_forensics.run import (
    classify_trend,
    classify_vol,
    failure_concentration,
    headline_answer,
    realized_vol_series,
    segment_mdd,
    total_return,
    window_rows,
)


def _days(n: int, start: str = "1990-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def test_classify_trend_sign_convention() -> None:
    assert classify_trend(0.10) == "bull"
    assert classify_trend(-0.10) == "bear"
    # Zero return is not a beat-able bull window; labeled bear by convention.
    assert classify_trend(0.0) == "bear"


def test_classify_vol_preregistered_cuts() -> None:
    assert classify_vol(0.10) == "low"
    assert classify_vol(0.1499) == "low"
    assert classify_vol(0.15) == "mid"
    assert classify_vol(0.2499) == "mid"
    assert classify_vol(0.25) == "high"
    assert classify_vol(0.60) == "high"


def test_total_return_and_segment_mdd() -> None:
    s = pd.Series([0.10, -0.50, 0.0], index=_days(3))
    assert abs(total_return(s) - (1.10 * 0.50 - 1.0)) < 1e-12
    # Peak 1.10, trough 0.55 -> 50% drawdown, positive magnitude.
    assert abs(segment_mdd(s) - 0.50) < 1e-12


def test_realized_vol_series_is_annualized_contemporaneous() -> None:
    rng = np.random.default_rng(0)
    s = pd.Series(0.01 * rng.standard_normal(300), index=_days(300))
    rv = realized_vol_series(s, window=21)
    expected = s.rolling(21).std(ddof=0) * np.sqrt(252.0)
    pd.testing.assert_series_equal(rv, expected)


def test_window_rows_one_per_split_non_overlapping() -> None:
    n = 1200
    rng = np.random.default_rng(1)
    idx = _days(n)
    under = pd.Series(0.0004 + 0.01 * rng.standard_normal(n), index=idx)
    strat = under + 0.0005
    signal = pd.Series(True, index=idx)
    rv = realized_vol_series(under)

    rows = window_rows(
        {"branch": "SPY", "base_name": "toy"},
        strat,
        under,
        signal,
        rv,
        is_size=240,
        oos_size=120,
        step=120,
    )

    assert len(rows) == (n - 240) // 120
    # Strategy beats underlying every day -> every window beats.
    assert all(r["beat"] for r in rows)
    # OOS windows are contiguous and non-overlapping.
    for prev, cur in zip(rows, rows[1:]):
        assert prev["oos_end"] < cur["oos_start"]
    # Regime cell is consistent with its parts.
    for r in rows:
        assert r["regime_cell"] == f"{r['regime_trend']}_{r['regime_vol']}"


def test_failure_concentration_and_headline() -> None:
    frame = pd.DataFrame(
        [
            {"branch": "SPY", "regime_cell": "bull_low", "regime_trend": "bull", "beat": False, "rel_ret": -0.05},
            {"branch": "SPY", "regime_cell": "bull_low", "regime_trend": "bull", "beat": False, "rel_ret": -0.02},
            {"branch": "SPY", "regime_cell": "bear_high", "regime_trend": "bear", "beat": False, "rel_ret": -0.01},
            {"branch": "QQQ", "regime_cell": "bear_high", "regime_trend": "bear", "beat": True, "rel_ret": 0.30},
        ]
    )

    conc = failure_concentration(frame)
    pooled_bull_low = conc[(conc["scope"] == "ALL") & (conc["regime_cell"] == "bull_low")].iloc[0]
    assert pooled_bull_low["n_windows"] == 2
    assert pooled_bull_low["beat_rate"] == 0.0

    headline = headline_answer(frame)
    assert headline["n_fail"] == 3
    assert headline["n_fail_bull_low"] == 2
    # 2/3 share meets the >=2/3 pre-registered threshold.
    assert headline["headline_yes"] is True
