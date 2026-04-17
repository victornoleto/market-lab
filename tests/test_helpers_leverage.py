"""Tests for leverage helpers (Phase 3 Lead A1).

Covers:
- Kelly fraction from synthetic trade P&L.
- Intra-bar ruin scan reconstructs position timeline correctly.
- Stationary block bootstrap prob-of-ruin behaves monotonically in L.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.engine.portfolio import Trade
from ai_trade.backtest.helpers.leverage import (
    bootstrap_prob_of_ruin,
    intra_bar_ruin_scan,
    kelly_fraction_from_trades,
)


# ---------------------------------------------------------------------------
# Kelly
# ---------------------------------------------------------------------------


def test_kelly_empty_returns_zero() -> None:
    assert kelly_fraction_from_trades([]) == 0.0


def test_kelly_all_wins_or_all_losses_returns_zero() -> None:
    # All wins — undefined Kelly (no loss sample).
    assert kelly_fraction_from_trades([1.0, 2.0, 3.0]) == 0.0
    # All losses.
    assert kelly_fraction_from_trades([-1.0, -2.0, -0.5]) == 0.0


def test_kelly_fair_coin_zero_edge_is_zero() -> None:
    # 50% win rate, equal win/loss magnitudes → Kelly = 0.
    pnls = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
    assert abs(kelly_fraction_from_trades(pnls)) < 1e-9


def test_kelly_positive_edge_gives_positive_fraction() -> None:
    # 60% win @ +1, 40% loss @ -1 → f = 0.6/1 - 0.4/1 = 0.2.
    pnls = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0, -1.0, -1.0, -1.0]
    f = kelly_fraction_from_trades(pnls)
    assert 0.18 < f < 0.22


def test_kelly_clamped_to_unit_interval() -> None:
    # Huge edge — binomial formula could go > 1, helper clamps.
    pnls = [10.0] * 90 + [-0.1] * 10
    f = kelly_fraction_from_trades(pnls)
    assert 0.0 <= f <= 1.0


def test_kelly_capital_at_entry_normalization() -> None:
    # Same edge but dollar scale changes with account.
    pnls = [100.0, 100.0, 100.0, -100.0, -100.0]
    cap_constant = [10_000] * 5
    f_const = kelly_fraction_from_trades(pnls, capital_at_entry=cap_constant)
    assert f_const > 0.0


def test_kelly_capital_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        kelly_fraction_from_trades([1.0, -1.0], capital_at_entry=[10_000])


# ---------------------------------------------------------------------------
# Intra-bar ruin scan
# ---------------------------------------------------------------------------


def _ohlcv(index, lows, highs, closes) -> pd.DataFrame:
    n = len(index)
    return pd.DataFrame(
        {
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1e6] * n,
        },
        index=index,
    )


def test_ruin_scan_no_trades_returns_initial() -> None:
    idx = pd.date_range("2021-01-01", periods=5, freq="h")
    df = _ohlcv(idx, [100.0] * 5, [100.0] * 5, [100.0] * 5)
    res = intra_bar_ruin_scan([], df, initial_cash=1_000.0)
    assert res.ruined is False
    assert res.worst_equity == 1_000.0


def test_ruin_scan_long_not_ruined_when_low_above_break_even() -> None:
    idx = pd.date_range("2021-01-01", periods=3, freq="h")
    df = _ohlcv(idx, [99.0, 98.0, 100.0], [101.0, 101.0, 101.0], [100.0, 100.0, 100.0])
    # Long 10x: vol=100, entry=100. Cash after entry = 1000 - 10000 = -9000.
    # Worst bar 1: low=98 → position value = 100*98 = 9800. Eq = -9000 + 9800 = 800.
    tr = Trade(
        symbol="X",
        side="long",
        volume=100.0,
        entry_price=100.0,
        exit_price=100.0,
        entry_time=idx[0],
        exit_time=idx[2],
        pnl=0.0,
    )
    res = intra_bar_ruin_scan([tr], df, initial_cash=1_000.0)
    assert res.ruined is False
    assert 790 < res.worst_equity < 810


def test_ruin_scan_long_ruined_when_low_blows_through() -> None:
    idx = pd.date_range("2021-01-01", periods=3, freq="h")
    df = _ohlcv(
        idx,
        lows=[99.0, 85.0, 100.0],  # bar 1 low=85 → catastrophic
        highs=[101.0, 101.0, 101.0],
        closes=[100.0, 90.0, 100.0],
    )
    tr = Trade(
        symbol="X",
        side="long",
        volume=100.0,
        entry_price=100.0,
        exit_price=100.0,
        entry_time=idx[0],
        exit_time=idx[2],
        pnl=0.0,
    )
    res = intra_bar_ruin_scan([tr], df, initial_cash=1_000.0, ruin_threshold=0.0)
    assert res.ruined is True
    assert res.ruin_time == idx[1]
    # Worst equity = -9000 + 100*85 = -500.
    assert res.worst_equity < 0.0


def test_ruin_scan_short_uses_high_for_worst() -> None:
    idx = pd.date_range("2021-01-01", periods=3, freq="h")
    df = _ohlcv(
        idx,
        lows=[99.0, 99.0, 99.0],
        highs=[101.0, 115.0, 101.0],  # spike up on bar 1
        closes=[100.0, 110.0, 100.0],
    )
    # Short 10x: vol=100, entry=100. Cash = 1000 + 10000 = 11000.
    # Worst bar 1: high=115 → pos value = -100*115 = -11500. Eq = 11000 -11500 = -500.
    tr = Trade(
        symbol="X",
        side="short",
        volume=100.0,
        entry_price=100.0,
        exit_price=100.0,
        entry_time=idx[0],
        exit_time=idx[2],
        pnl=0.0,
    )
    res = intra_bar_ruin_scan([tr], df, initial_cash=1_000.0, ruin_threshold=0.0)
    assert res.ruined is True
    assert res.worst_equity < 0.0


# ---------------------------------------------------------------------------
# Bootstrap prob-of-ruin
# ---------------------------------------------------------------------------


def test_bootstrap_por_zero_paths_for_trivial_positive_edge_low_lev() -> None:
    # All small positive returns — no path can ruin at 1x.
    rets = np.array([0.01] * 100)
    p = bootstrap_prob_of_ruin(rets, leverage=1.0, n_paths=500, block_size=5)
    assert p == 0.0


def test_bootstrap_por_monotone_in_leverage() -> None:
    rng = np.random.default_rng(0)
    # Mix of small wins and a few 20% losses to trigger ruin at high L.
    rets = np.concatenate([rng.normal(0.01, 0.02, 80), np.full(20, -0.20)])
    p_low = bootstrap_prob_of_ruin(
        rets, leverage=1.0, n_paths=500, block_size=5, horizon=50, seed=1,
    )
    p_high = bootstrap_prob_of_ruin(
        rets, leverage=5.0, n_paths=500, block_size=5, horizon=50, seed=1,
    )
    assert p_high >= p_low


def test_bootstrap_por_empty_returns_zero() -> None:
    assert bootstrap_prob_of_ruin([], leverage=2.0, n_paths=100) == 0.0


def test_bootstrap_por_handles_block_size_one() -> None:
    rets = np.array([0.01, -0.02, 0.03])
    p = bootstrap_prob_of_ruin(rets, leverage=1.0, n_paths=200, block_size=1, seed=0)
    assert 0.0 <= p <= 1.0
