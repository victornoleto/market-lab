"""Tests for the rolling-windows helper used by plot_helper.py."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _synthetic_returns(n_years: float, seed: int = 42, mu: float = 0.10, sigma: float = 0.15) -> pd.Series:
    rng = np.random.default_rng(seed)
    n = int(n_years * 252)
    daily = rng.normal(mu / 252, sigma / np.sqrt(252), size=n)
    idx = pd.date_range("1970-01-02", periods=n, freq="B")
    return pd.Series(daily, index=idx)


def test_rolling_sharpe_at_windows_returns_dict_keyed_by_years() -> None:
    from studies.return_stacked_core.rolling_windows import rolling_sharpe_at_windows

    s = _synthetic_returns(40)
    out = rolling_sharpe_at_windows(s, [3, 5, 10, 30])
    assert set(out.keys()) == {3, 5, 10, 30}
    for w, series in out.items():
        assert isinstance(series, pd.Series)
        assert series.index.is_monotonic_increasing


def test_rolling_sharpe_skips_windows_too_long_for_data() -> None:
    """A 30y window on 17y of data → empty Series, not an error."""
    from studies.return_stacked_core.rolling_windows import rolling_sharpe_at_windows

    s = _synthetic_returns(17)
    out = rolling_sharpe_at_windows(s, [3, 5, 10, 15, 20, 30])
    # 3, 5, 10, 15 should fit; 20 and 30 should be empty
    assert len(out[3]) > 0
    assert len(out[5]) > 0
    assert len(out[10]) > 0
    assert len(out[15]) > 0
    assert len(out[20]) == 0
    assert len(out[30]) == 0


def test_rolling_sharpe_values_match_manual_computation() -> None:
    """Spot-check: 5y rolling Sharpe at the end of 10y of data."""
    from studies.return_stacked_core.rolling_windows import rolling_sharpe_at_windows

    s = _synthetic_returns(10, seed=1)
    out = rolling_sharpe_at_windows(s, [5])
    last_window = s.iloc[-5 * 252:]
    expected = float(last_window.mean() / last_window.std(ddof=0) * np.sqrt(252))
    assert abs(out[5].iloc[-1] - expected) < 1e-6


def test_rolling_outperformance_pct_returns_fraction_and_count() -> None:
    """Returns a dict[window_years] -> {'pct_strat_wins': float, 'n_windows': int}."""
    from studies.return_stacked_core.rolling_windows import rolling_outperformance_pct

    strat = _synthetic_returns(20, seed=1, mu=0.12)
    bench = _synthetic_returns(20, seed=1, mu=0.08)  # same noise, different mean
    out = rolling_outperformance_pct(strat, bench, [3, 5, 10])
    for w, payload in out.items():
        assert "pct_strat_wins" in payload
        assert "n_windows" in payload
        assert 0.0 <= payload["pct_strat_wins"] <= 1.0
    # Higher-mean strategy should beat bench more than half the time
    assert out[5]["pct_strat_wins"] > 0.5


def test_rolling_outperformance_handles_window_too_long() -> None:
    from studies.return_stacked_core.rolling_windows import rolling_outperformance_pct

    strat = _synthetic_returns(8)
    bench = _synthetic_returns(8, seed=99)
    out = rolling_outperformance_pct(strat, bench, [3, 5, 10, 30])
    assert out[10]["n_windows"] == 0
    assert out[30]["n_windows"] == 0
    assert out[3]["n_windows"] > 0


def test_default_window_menu_is_3_5_10_15_20_30() -> None:
    from studies.return_stacked_core.rolling_windows import DEFAULT_WINDOWS_YEARS

    assert DEFAULT_WINDOWS_YEARS == [3, 5, 10, 15, 20, 30]
