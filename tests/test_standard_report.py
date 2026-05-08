"""Unit tests for ``backtest.metrics.standard_report`` — Phase 3.5b Task 1.

The spec (``specs/phase_3_5b_winners_validation.md`` §Task 1) requires:

1. A synthetic 2-trade scenario (one winner, one loser) where the IR is
   applied **only** on the winning trade.
2. A synthetic SPY series to verify the benchmark and excess-return math.

We also cover the smaller pieces (Trade invariants, drawdown periods, SPY
loader, markdown rendering) so regressions here are localized.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from market_lab.backtest.metrics.standard_report import (
    DEFAULT_SPY_PARQUET,
    SpyBenchmark,
    StandardReport,
    Trade,
    build_spy_benchmark,
    build_standard_report,
    compare_vs_spy,
    drawdown_periods,
    load_spy_series,
    render_markdown,
    render_trade_log,
)


# ---------------------------------------------------------------------------
# Trade
# ---------------------------------------------------------------------------


def test_trade_long_profit_pct_and_brl():
    t = Trade(
        asset="ABC",
        entry_date=pd.Timestamp("2024-01-01"),
        exit_date=pd.Timestamp("2024-01-11"),
        entry_price=100.0,
        exit_price=110.0,
        notional=1_000.0,
        direction="long",
    )
    assert t.gross_pnl_pct == pytest.approx(0.10)
    assert t.gross_pnl_brl == pytest.approx(100.0)
    assert t.tax_brl(0.15) == pytest.approx(15.0)
    assert t.net_pnl_brl(0.15) == pytest.approx(85.0)
    assert t.hold_days == 10


def test_trade_long_loss_no_tax():
    t = Trade(
        asset="XYZ",
        entry_date=pd.Timestamp("2024-01-01"),
        exit_date=pd.Timestamp("2024-01-06"),
        entry_price=100.0,
        exit_price=90.0,
        notional=2_000.0,
    )
    assert t.gross_pnl_pct == pytest.approx(-0.10)
    assert t.gross_pnl_brl == pytest.approx(-200.0)
    assert t.tax_brl() == 0.0
    assert t.net_pnl_brl() == pytest.approx(-200.0)


def test_trade_short_profit_inverts_sign():
    t = Trade(
        asset="SHORT",
        entry_date=pd.Timestamp("2024-01-01"),
        exit_date=pd.Timestamp("2024-01-10"),
        entry_price=100.0,
        exit_price=90.0,  # price dropped → short wins
        notional=1_000.0,
        direction="short",
    )
    assert t.gross_pnl_pct == pytest.approx(0.10)
    assert t.gross_pnl_brl == pytest.approx(100.0)
    assert t.tax_brl() == pytest.approx(15.0)


def test_trade_invalid_raises():
    with pytest.raises(ValueError):
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2024-01-10"),
            exit_date=pd.Timestamp("2024-01-01"),
            entry_price=100.0,
            exit_price=110.0,
        )
    with pytest.raises(ValueError):
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2024-01-01"),
            exit_date=pd.Timestamp("2024-01-10"),
            entry_price=-1.0,
            exit_price=110.0,
        )
    with pytest.raises(ValueError):
        Trade(
            asset="X",
            entry_date=pd.Timestamp("2024-01-01"),
            exit_date=pd.Timestamp("2024-01-10"),
            entry_price=100.0,
            exit_price=110.0,
            direction="neutral",  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Drawdown periods
# ---------------------------------------------------------------------------


def test_drawdown_periods_simple_recovery():
    # peak at t=0, dip at t=2, recover at t=4
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    eq = pd.Series([100, 100, 90, 95, 100], index=idx, dtype=float)
    periods = drawdown_periods(eq)
    assert len(periods) == 1
    start, end, days = periods[0]
    assert start == pd.Timestamp("2024-01-02")  # last peak before dip
    assert end == pd.Timestamp("2024-01-05")    # recovery
    assert days == 3


def test_drawdown_periods_unrecovered_tail():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    eq = pd.Series([100, 110, 105, 95], index=idx, dtype=float)
    periods = drawdown_periods(eq)
    assert len(periods) == 1
    start, end, _ = periods[0]
    assert start == pd.Timestamp("2024-01-02")
    assert end == pd.Timestamp("2024-01-04")  # series end, no recovery


def test_drawdown_periods_no_drawdown():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    eq = pd.Series([100, 101, 102, 103], index=idx, dtype=float)
    assert drawdown_periods(eq) == []


# ---------------------------------------------------------------------------
# Standard report — synthetic 2-trade scenario
# ---------------------------------------------------------------------------


def _synthetic_equity() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=21, freq="D")
    # Equity starts at 10k, grows steadily, dips mid-window, recovers, ends up.
    values = np.linspace(10_000, 10_500, 10).tolist() + np.linspace(10_500, 11_000, 11).tolist()
    return pd.Series(values, index=idx)


def test_build_standard_report_basic_fields():
    eq = _synthetic_equity()
    trades = [
        Trade(
            asset="A",
            entry_date=eq.index[0],
            exit_date=eq.index[10],
            entry_price=100.0,
            exit_price=110.0,
            notional=10_000.0,
        ),
        Trade(
            asset="A",
            entry_date=eq.index[11],
            exit_date=eq.index[20],
            entry_price=110.0,
            exit_price=104.5,  # −5 %
            notional=10_000.0,
        ),
    ]
    rpt = build_standard_report(
        equity=eq, trades=trades, strategy_name="Synth", params="L=2"
    )
    assert isinstance(rpt, StandardReport)
    assert rpt.strategy_name == "Synth"
    assert rpt.params == "L=2"
    assert rpt.start == eq.index[0]
    assert rpt.end == eq.index[-1]
    assert rpt.duration_days == 20
    assert rpt.equity_start == pytest.approx(10_000.0)
    assert rpt.equity_final == pytest.approx(11_000.0)
    assert rpt.return_pct == pytest.approx(0.10)
    assert rpt.n_trades == 2
    assert rpt.win_rate_pct == pytest.approx(0.5)
    assert rpt.best_trade_pct == pytest.approx(0.10)
    assert rpt.worst_trade_pct == pytest.approx(-0.05)
    # Profit factor = 0.10 / 0.05 = 2.0
    assert rpt.profit_factor == pytest.approx(2.0)
    # Expectancy = mean(0.10, -0.05) = 0.025
    assert rpt.expectancy_pct == pytest.approx(0.025)
    # SQN = sqrt(2) * 0.025 / std([0.10,-0.05])  with std ddof=0 = 0.075
    assert rpt.sqn == pytest.approx(math.sqrt(2) * 0.025 / 0.075, rel=1e-6)
    # Kelly = 0.5 − (1−0.5) / (0.10 / 0.05) = 0.25
    assert rpt.kelly == pytest.approx(0.25)


def test_build_standard_report_exposure_time():
    eq = _synthetic_equity()
    trade = Trade(
        asset="A",
        entry_date=eq.index[0],
        exit_date=eq.index[10],
        entry_price=100.0,
        exit_price=110.0,
        notional=10_000.0,
    )
    rpt = build_standard_report(
        equity=eq, trades=[trade], strategy_name="X"
    )
    # 11 bars in position out of 21 total ≈ 0.524.
    assert rpt.exposure_time_pct == pytest.approx(11 / 21, abs=0.001)


def test_build_standard_report_empty_trades_ok():
    eq = _synthetic_equity()
    rpt = build_standard_report(equity=eq, trades=[], strategy_name="Buy&Hold")
    assert rpt.n_trades == 0
    assert rpt.win_rate_pct == 0.0
    assert rpt.sqn == 0.0
    assert rpt.kelly == 0.0
    assert rpt.exposure_time_pct == 0.0


def test_build_standard_report_rejects_single_point():
    idx = pd.date_range("2024-01-01", periods=1, freq="D")
    eq = pd.Series([10_000.0], index=idx)
    with pytest.raises(ValueError):
        build_standard_report(equity=eq, trades=[], strategy_name="X")


# ---------------------------------------------------------------------------
# SPY benchmark + comparison — synthetic series
# ---------------------------------------------------------------------------


def _synthetic_spy() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=21, freq="D")
    # Starts at 400, ends at 404 — modest 1% move, small wobble mid-window.
    values = [400.0]
    for i in range(1, 21):
        values.append(values[-1] * (1.0 + (0.0005 if i % 2 == 0 else -0.0001)))
    return pd.Series(values, index=idx, name="SPY")


def test_build_spy_benchmark_applies_initial_capital():
    spy = _synthetic_spy()
    bench = build_spy_benchmark(spy, initial_capital=10_000.0)
    assert isinstance(bench, SpyBenchmark)
    assert bench.equity_curve.iloc[0] == pytest.approx(10_000.0)
    expected_ret = float(spy.iloc[-1] / spy.iloc[0] - 1.0)
    assert bench.return_pct == pytest.approx(expected_ret)


def test_build_spy_benchmark_window_truncation():
    spy = _synthetic_spy()
    window_start = spy.index[5]
    window_end = spy.index[15]
    bench = build_spy_benchmark(
        spy, initial_capital=1_000.0, window_start=window_start, window_end=window_end
    )
    assert bench.equity_curve.index[0] == window_start
    assert bench.equity_curve.index[-1] == window_end
    assert bench.equity_curve.iloc[0] == pytest.approx(1_000.0)


def test_build_spy_benchmark_rejects_negative_capital():
    spy = _synthetic_spy()
    with pytest.raises(ValueError):
        build_spy_benchmark(spy, initial_capital=-1.0)


def test_compare_vs_spy_excess_and_beta_with_known_series():
    idx = pd.date_range("2024-01-01", periods=30, freq="D")
    # Strategy = SPY * 2 (levered) so beta ≈ 2, correlation ≈ 1.
    spy_rets = np.random.default_rng(42).normal(0.0005, 0.01, size=29)
    spy_equity = pd.Series(
        100.0 * np.cumprod(np.concatenate([[1.0], 1.0 + spy_rets])), index=idx
    )
    strat_equity = pd.Series(
        100.0 * np.cumprod(np.concatenate([[1.0], 1.0 + 2.0 * spy_rets])), index=idx
    )
    cmp_ = compare_vs_spy(strat_equity, spy_equity)
    assert cmp_.correlation == pytest.approx(1.0, abs=1e-6)
    assert cmp_.beta == pytest.approx(2.0, abs=1e-6)
    # Strategy return > SPY return for this positive-drift series.
    assert cmp_.excess_return_pct > 0


def test_compare_vs_spy_requires_overlap():
    idx1 = pd.date_range("2024-01-01", periods=5, freq="D")
    idx2 = pd.date_range("2025-01-01", periods=5, freq="D")
    s1 = pd.Series([100.0, 101, 102, 103, 104], index=idx1)
    s2 = pd.Series([200.0, 201, 202, 203, 204], index=idx2)
    with pytest.raises(ValueError):
        compare_vs_spy(s1, s2)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def test_render_markdown_contains_all_spec_sections():
    eq = _synthetic_equity()
    trades = [
        Trade(
            asset="A",
            entry_date=eq.index[0],
            exit_date=eq.index[10],
            entry_price=100.0,
            exit_price=110.0,
            notional=10_000.0,
        ),
    ]
    rpt = build_standard_report(equity=eq, trades=trades, strategy_name="Synth")
    spy = _synthetic_spy()
    bench = build_spy_benchmark(spy, initial_capital=10_000.0)
    cmp_ = compare_vs_spy(eq, bench.equity_curve)

    md = render_markdown(rpt, bench, cmp_)
    for needle in (
        "# Synth",
        "## Metrics",
        "Start",
        "End",
        "Duration",
        "Exposure Time [%]",
        "Equity Final [$]",
        "Equity Peak [$]",
        "Return [%]",
        "Return (Ann.) [%]",
        "Volatility (Ann.) [%]",
        "CAGR [%]",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Calmar Ratio",
        "Max. Drawdown [%]",
        "Avg. Drawdown [%]",
        "Max. Drawdown Duration",
        "Avg. Drawdown Duration",
        "# Trades",
        "Win Rate [%]",
        "Best Trade [%]",
        "Worst Trade [%]",
        "Avg. Trade [%]",
        "Max. Trade Duration",
        "Avg. Trade Duration",
        "Profit Factor",
        "Expectancy [%]",
        "SQN",
        "Kelly Criterion",
        "_strategy",
        "## SPY Buy & Hold Benchmark",
        "SPY Return [%]",
        "SPY CAGR [%]",
        "SPY Max. Drawdown [%]",
        "SPY Sharpe Ratio",
        "## Strategy vs SPY",
        "Excess Return [%]",
        "Information Ratio",
        "Correlation (daily)",
        "Beta vs SPY",
    ):
        assert needle in md, f"missing row: {needle!r}"


def test_render_markdown_without_benchmark_omits_spy_blocks():
    eq = _synthetic_equity()
    rpt = build_standard_report(equity=eq, trades=[], strategy_name="NoBench")
    md = render_markdown(rpt)
    assert "## SPY" not in md
    assert "## Strategy vs SPY" not in md
    assert "## Metrics" in md


# ---------------------------------------------------------------------------
# Trade log rendering — IR applied per winning trade
# ---------------------------------------------------------------------------


def test_render_trade_log_applies_tax_only_on_winners():
    idx = pd.date_range("2024-01-01", periods=30, freq="D")
    winner = Trade(
        asset="A",
        entry_date=idx[0],
        exit_date=idx[10],
        entry_price=100.0,
        exit_price=110.0,
        notional=1_000.0,
    )
    loser = Trade(
        asset="A",
        entry_date=idx[11],
        exit_date=idx[20],
        entry_price=110.0,
        exit_price=99.0,  # −10 %
        notional=1_000.0,
    )
    csv_text, md_text = render_trade_log([winner, loser], initial_capital=10_000.0)

    # CSV parseable + contains both trades.
    df = pd.read_csv(pd.io.common.StringIO(csv_text))
    assert len(df) == 2

    # Winner pays tax; loser pays nothing.
    win_row = df.iloc[0]
    loss_row = df.iloc[1]
    assert win_row["gross_pnl_brl"] == pytest.approx(100.0)
    assert win_row["tax_brl"] == pytest.approx(15.0)
    assert win_row["net_pnl_brl"] == pytest.approx(85.0)
    # loser pct = (99 - 110) / 110 = −10 % of notional 1000 = −100 BRL.
    assert loss_row["gross_pnl_brl"] == pytest.approx(-100.0)
    assert loss_row["tax_brl"] == 0.0
    assert loss_row["net_pnl_brl"] == pytest.approx(-100.0)

    # Cumulative equity: 10_000 + 85 − 100 = 9_985.
    assert loss_row["cumulative_equity_brl"] == pytest.approx(9_985.0)

    # Markdown contains at least both asset entries + header row.
    assert "asset" in md_text
    assert md_text.count("\n") >= 3


def test_render_trade_log_empty():
    csv_text, md_text = render_trade_log([], initial_capital=10_000.0)
    assert "entry_date" in csv_text
    assert "No trades" in md_text


def test_render_trade_log_rejects_bad_capital():
    with pytest.raises(ValueError):
        render_trade_log([], initial_capital=0.0)


# ---------------------------------------------------------------------------
# Real-data smoke test — only if SPY parquet is present
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not Path(DEFAULT_SPY_PARQUET).exists(),
    reason="Tiingo SPY parquet cache not present in this environment",
)
def test_load_spy_series_real_cache_smoke():
    s = load_spy_series()
    assert len(s) > 1_000  # Tiingo cache covers 2001-05 → present
    assert s.is_monotonic_increasing or s.index.is_monotonic_increasing
    # Values are adjusted close — must be positive floats.
    assert (s > 0).all()
    # Verify first/last make sense (SPY is unlikely ever to be below $10).
    assert float(s.iloc[0]) > 10.0
    assert float(s.iloc[-1]) > 10.0
