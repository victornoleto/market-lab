"""End-to-end integration test for the Clenow replication pipeline.

Zero network: all OHLCV frames are generated synthetically with a fixed RNG
seed. The test exercises the full stack — data → strategy → runner →
engine → report — and verifies that:

* the equity curve is non-empty and finite;
* at least one round-trip trade is executed;
* performance metrics are finite;
* the Markdown report + PNG chart are written to disk;
* the survivorship disclaimer is emitted because we tag the source as
  ``yfinance``.

Validation (CPCV/PBO/DSR/walk-forward) is intentionally omitted — those
layers are unit-tested in ``test_validation.py`` and require a multi-trial
matrix. A single replication run doesn't generate one.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def _ohlcv_from_close(
    close: list[float], start: pd.Timestamp
) -> pd.DataFrame:
    """Build an OHLCV frame from a close series. High/low ±0.5%, open = close."""
    idx = pd.bdate_range(start=start, periods=len(close), name="date")
    return pd.DataFrame(
        {
            "open": close,
            "high": [c * 1.005 for c in close],
            "low": [c * 0.995 for c in close],
            "close": close,
            "adj_close": close,
            "volume": [1_000_000] * len(close),
        },
        index=idx,
    )


def _trending_close(
    start_price: float, daily_drift: float, noise_sigma: float, n: int, seed: int
) -> list[float]:
    """Exponential trend with lognormal noise — deterministic per ``seed``."""
    rng = np.random.default_rng(seed)
    shocks = rng.normal(0, noise_sigma, n)
    log_path = np.cumsum(shocks) + daily_drift * np.arange(n)
    return [start_price * math.exp(lp) for lp in log_path]


@pytest.fixture
def synthetic_market():
    """Return (data dict, universe) for a 400-bar 10-stock synthetic market."""
    start = pd.Timestamp("2023-01-02")
    n_bars = 400

    # Index: mild upward drift, gentle noise (keeps the regime filter ON for
    # most of the run while still having some variance).
    idx_close = _trending_close(1000.0, 0.0005, 0.005, n_bars, seed=1)

    constituent_specs = [
        ("A", 0.0015, 0.015, 10),  # strong trend
        ("B", 0.0013, 0.015, 11),
        ("C", 0.0011, 0.015, 12),
        ("D", 0.0009, 0.015, 13),
        ("E", 0.0007, 0.015, 14),
        ("F", 0.0005, 0.020, 15),
        ("G", 0.0003, 0.020, 16),
        ("H", 0.0001, 0.020, 17),
        ("I", -0.0002, 0.025, 18),  # weak / negative
        ("J", -0.0005, 0.025, 19),
    ]

    data: dict[str, pd.DataFrame] = {
        "INDEX": _ohlcv_from_close(idx_close, start),
    }
    for sym, drift, noise, seed in constituent_specs:
        closes = _trending_close(100.0, drift, noise, n_bars, seed=seed)
        data[sym] = _ohlcv_from_close(closes, start)

    universe = {s for s, _, _, _ in constituent_specs}
    return data, universe


def test_clenow_pipeline_runs_end_to_end(synthetic_market, tmp_path: Path):
    """Full pipeline: data → strategy → runner → report, checked for sanity."""
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.metrics.performance import (
        max_drawdown,
        returns_from_equity,
        sharpe,
    )
    from ai_trade.backtest.metrics.report import generate_report
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    data, universe = synthetic_market

    strategy = ClenowMomentumStrategy(
        data=data,
        constituents_provider=lambda d: universe,
        index_symbol="INDEX",
        top_pct=0.50,       # hold up to 5 of 10 stocks
        risk_factor=0.002,  # slightly oversized so we exercise cash constraints
    )

    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data, initial_cash=100_000.0)

    # --- Sanity on result --------------------------------------------------
    assert not result.equity_curve.empty
    assert math.isfinite(result.final_equity)
    assert result.final_equity > 0

    # Strategy must have acted at some point during the run.
    assert len(result.fills) > 0
    # And at least one sell must have closed a round-trip trade (weekly
    # rebalance churns stocks in/out of the ranking).
    assert len(result.trades) > 0

    # --- Metrics must be finite -------------------------------------------
    rets = returns_from_equity(result.equity_curve)
    sr = sharpe(rets, 252)
    dd = max_drawdown(result.equity_curve)
    assert math.isfinite(sr)
    assert 0.0 <= dd <= 1.0

    # --- Report generation -------------------------------------------------
    report_path = generate_report(
        result=result,
        validation={},  # single trial — no PBO/DSR/CPCV
        strategy_name="clenow_integration",
        output_dir=tmp_path,
        data_source="yfinance",  # must trigger survivorship disclaimer
    )

    assert report_path.exists()
    text = report_path.read_text()
    assert "clenow_integration" in text
    assert "Survivorship bias" in text  # disclaimer must be present
    # PNG companion generated?
    assets = list((tmp_path / "assets").glob("*.png"))
    assert len(assets) == 1
    assert assets[0].stat().st_size > 0


def test_strategy_respects_regime_filter_during_index_drawdown(
    synthetic_market,
):
    """Inject an index crash mid-run; verify that no new buys occur while the
    index is below its 200-day MA."""
    from ai_trade.backtest.engine import (
        ExecutionConfig,
        ExecutionSimulator,
        Runner,
    )
    from ai_trade.backtest.strategies.clenow_momentum import (
        ClenowMomentumStrategy,
    )

    data, universe = synthetic_market
    # Force the index into a deep drawdown over the final 100 bars so the
    # 200-day MA sits above the current close by the end of the run.
    crash = _trending_close(1000.0, -0.01, 0.005, 100, seed=99)
    crashed_close = list(data["INDEX"]["close"].iloc[:300]) + crash
    data["INDEX"] = _ohlcv_from_close(
        crashed_close, pd.Timestamp("2023-01-02")
    )

    strategy = ClenowMomentumStrategy(
        data=data,
        constituents_provider=lambda d: universe,
        index_symbol="INDEX",
        top_pct=0.50,
        risk_factor=0.002,
    )
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    result = runner.run(strategy=strategy, data=data, initial_cash=100_000.0)

    # Check: on the LAST rebalance Wednesday, regime is OFF, so no buy fills
    # happen on that date. (At least one sell may still fire.)
    last_wed = max(
        ts for ts in data["INDEX"].index if ts.weekday() == 2
    )
    last_day_fills = [f for f in result.fills if f.fill_time == last_wed]
    last_day_buys = [f for f in last_day_fills if f.order.side == "buy"]
    assert last_day_buys == []
