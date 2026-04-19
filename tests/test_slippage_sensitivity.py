"""Unit tests for ``backtest.metrics.slippage_sensitivity`` — Phase 3.5b Task 7c."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ai_trade.backtest.metrics.slippage_sensitivity import (
    CANONICAL_SLIPPAGE_LEVELS_BPS,
    SlippageRow,
    make_cost_varied_config,
    render_multi_strategy_slippage_markdown,
    render_strategy_slippage_markdown,
    summarize_equity,
)
from ai_trade.backtest.strategies.letf_rotation import LETFRotationConfig
from ai_trade.backtest.strategies.tsmom import TSMOMConfig


def _geom_equity(n: int, daily: float, start: float = 1.0) -> pd.Series:
    idx = pd.bdate_range("2020-01-02", periods=n, freq="B")
    vals = start * (1.0 + daily) ** np.arange(n, dtype=float)
    return pd.Series(vals, index=idx, name="equity")


# ---------------------------------------------------------------------------
# Canonical set
# ---------------------------------------------------------------------------


def test_canonical_levels_match_spec():
    assert CANONICAL_SLIPPAGE_LEVELS_BPS == (0.0, 1.0, 5.0, 10.0)


# ---------------------------------------------------------------------------
# summarize_equity
# ---------------------------------------------------------------------------


def test_summarize_equity_constant_growth_sharpe_inf():
    eq = _geom_equity(252, 0.0005)  # ~13% CAGR, zero vol
    row = summarize_equity(eq, level_bps=5.0, n_switches=3, cum_cost_pct=0.01)
    assert row.level_bps == 5.0
    assert row.bars == 252
    assert row.n_switches == 3
    assert row.cum_cost_pct == pytest.approx(0.01)
    assert row.volatility_ann_pct == pytest.approx(0.0, abs=1e-12)
    # Constant-daily-return curve has zero std → Sharpe convention returns 0.
    assert row.sharpe == 0.0
    assert row.max_drawdown_pct == pytest.approx(0.0, abs=1e-12)
    # CAGR ≈ (1.0005)**252 - 1 ≈ 13.3%
    assert 0.12 < row.cagr_pct < 0.15


def test_summarize_equity_empty_returns_zero_row():
    eq = pd.Series(dtype=float)
    row = summarize_equity(eq, level_bps=10.0, n_switches=0, cum_cost_pct=0.0)
    assert row.bars == 0
    assert row.sharpe == 0.0
    assert row.cagr_pct == 0.0
    assert row.max_drawdown_pct == 0.0


def test_summarize_equity_with_drawdown():
    idx = pd.bdate_range("2021-01-04", periods=10, freq="B")
    vals = [1.0, 1.1, 1.2, 1.15, 1.05, 0.95, 1.00, 1.08, 1.12, 1.18]
    eq = pd.Series(vals, index=idx, name="equity")
    row = summarize_equity(eq, level_bps=1.0, n_switches=4, cum_cost_pct=0.004)
    # Peak at 1.20, trough at 0.95 → max DD magnitude = (1.20-0.95)/1.20 = 20.83%
    # (performance.max_drawdown returns a positive magnitude.)
    assert row.max_drawdown_pct == pytest.approx(0.2083, abs=1e-3)
    assert row.total_return_pct == pytest.approx(0.18, abs=1e-9)


# ---------------------------------------------------------------------------
# make_cost_varied_config
# ---------------------------------------------------------------------------


def test_make_cost_varied_config_letf():
    base = LETFRotationConfig(filter="EMA", lookback=100, leverage=2.0, gold_weight=0.0)
    varied = make_cost_varied_config(base, level_bps=7.0)
    assert varied.commission_bps == 0.0
    assert varied.spread_bps == 7.0
    # Other fields preserved.
    assert varied.filter == "EMA"
    assert varied.lookback == 100
    assert varied.leverage == 2.0
    assert varied.tax_rate == base.tax_rate
    assert varied.annual_fee == base.annual_fee
    assert varied.switch_cost_pct == pytest.approx(7.0 / 10_000.0)


def test_make_cost_varied_config_tsmom():
    base = TSMOMConfig(entry_lookback=20, exit_lookback=10)
    varied = make_cost_varied_config(base, level_bps=0.0)
    assert varied.commission_bps == 0.0
    assert varied.spread_bps == 0.0
    assert varied.entry_lookback == 20
    assert varied.exit_lookback == 10
    assert varied.tax_rate == base.tax_rate
    assert varied.switch_cost_pct == 0.0


def test_make_cost_varied_config_rejects_negative():
    base = TSMOMConfig()
    with pytest.raises(ValueError):
        make_cost_varied_config(base, level_bps=-1.0)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _row(level: float, sharpe: float = 1.5, cagr: float = 0.25) -> SlippageRow:
    return SlippageRow(
        level_bps=level,
        bars=1000,
        n_switches=40,
        cum_cost_pct=level * 40.0 / 10_000.0,
        total_return_pct=1.0,
        cagr_pct=cagr,
        volatility_ann_pct=0.18,
        sharpe=sharpe,
        max_drawdown_pct=-0.12,
    )


def test_render_strategy_table_has_header_and_rows():
    rows = [_row(l) for l in CANONICAL_SLIPPAGE_LEVELS_BPS]
    md = render_strategy_slippage_markdown("Strategy X", rows)
    assert md.startswith("### Strategy X")
    assert "| slippage_bps |" in md
    for level in CANONICAL_SLIPPAGE_LEVELS_BPS:
        assert f"| {int(level)} |" in md


def test_render_multi_strategy_wraps_all_sections():
    rows_a = [_row(l, sharpe=1.0) for l in CANONICAL_SLIPPAGE_LEVELS_BPS]
    rows_b = [_row(l, sharpe=2.0, cagr=0.30) for l in CANONICAL_SLIPPAGE_LEVELS_BPS]
    md = render_multi_strategy_slippage_markdown(
        [("LETF", rows_a), ("Portfolio", rows_b)],
        title="Phase 3.5b Task 7c — Slippage sensitivity",
    )
    assert md.startswith("# Phase 3.5b Task 7c — Slippage sensitivity")
    assert "### LETF" in md
    assert "### Portfolio" in md
    assert "commission_bps=0" in md  # explanation block present
    assert "Swept levels (bps): 0, 1, 5, 10" in md
