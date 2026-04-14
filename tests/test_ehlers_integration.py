"""End-to-end integration tests for the Ehlers Band-Pass Swing replication.

Exercises the full pipeline — strategy → Runner → Portfolio →
metrics/report — on synthetic OHLCV (no network). Keeps the suite fast
while catching wiring breakage between the Ehlers strategy and the
existing engine/report infrastructure.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_cyclic_ohlcv() -> dict[str, pd.DataFrame]:
    """1500 bars of 20-bar-period sinusoid on ^GSPC, tight spread."""
    n = 1500
    period = 20
    amplitude = 5.0
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    t = np.arange(n)
    close = pd.Series(100.0 + amplitude * np.sin(2 * np.pi * t / period), index=idx)
    half_spread = close * 1.0 * 1e-4
    ohlcv = pd.DataFrame(
        {
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + half_spread,
            "low": close - half_spread,
            "close": close,
            "volume": 1_000_000.0,
        },
        index=idx,
    )
    return {"^GSPC": ohlcv}


def _run(data: dict[str, pd.DataFrame], cash: float = 100_000.0):
    from ai_trade.backtest.engine import ExecutionConfig, ExecutionSimulator, Runner
    from ai_trade.backtest.strategies.ehlers_bp_swing import EhlersBPSwingStrategy

    strategy = EhlersBPSwingStrategy(data=data, symbol="^GSPC")
    runner = Runner(executor=ExecutionSimulator(ExecutionConfig()))
    return runner.run(strategy, data, initial_cash=cash)


# ---------------------------------------------------------------------------
# Engine contract
# ---------------------------------------------------------------------------


class TestEngineContract:
    def test_equity_curve_is_nonempty_and_finite(self, synthetic_cyclic_ohlcv):
        result = _run(synthetic_cyclic_ohlcv)

        assert not result.equity_curve.empty
        assert np.isfinite(result.equity_curve.to_numpy()).all()
        assert result.final_equity > 0

    def test_final_equity_nonzero_and_bounded(self, synthetic_cyclic_ohlcv):
        """Engine-level sanity: equity neither blows up nor vanishes.

        A pure sinusoid is *not* profitable for the strategy as configured
        — each whipsaw costs up to ``risk_pct_of_equity × stop_pct`` of
        equity, and the anticipatory-entry rules fire too often on a
        symmetric cycle (entries happen on the way down to the bottom,
        not at the bottom itself). A realistic regime with real-world
        noise + long cycles behaves better; see ``reports/
        ehlers_replication_notes.md`` for the ^GSPC replication numbers.
        """
        result = _run(synthetic_cyclic_ohlcv)

        # Guardrails: no negative equity, no unbounded runaway.
        assert result.final_equity > 0
        assert result.final_equity < 100.0 * result.initial_cash

    def test_trades_have_consistent_entry_exit_times(self, synthetic_cyclic_ohlcv):
        result = _run(synthetic_cyclic_ohlcv)

        for t in result.trades:
            assert t.entry_time <= t.exit_time
            assert t.volume > 0
            assert t.entry_price > 0
            assert t.exit_price > 0


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


class TestReportGeneration:
    def test_generate_report_produces_markdown_and_png(
        self, synthetic_cyclic_ohlcv, tmp_path: Path
    ):
        from ai_trade.backtest.metrics.report import generate_report

        result = _run(synthetic_cyclic_ohlcv)

        md_path = generate_report(
            result=result,
            validation={},
            strategy_name="ehlers_bp_swing_test",
            output_dir=tmp_path,
            data_source="synthetic",
        )

        assert md_path.exists()
        assert md_path.suffix == ".md"
        content = md_path.read_text(encoding="utf-8")
        assert "ehlers_bp_swing_test" in content
        assert "Final equity" in content

        # Asset directory must contain the equity PNG the report references.
        assets = list((tmp_path / "assets").glob("ehlers_bp_swing_test_*.png"))
        assert assets, "expected an equity_vs_drawdown PNG under assets/"

    def test_report_with_walk_forward_validation(
        self, synthetic_cyclic_ohlcv, tmp_path: Path
    ):
        """Walk-forward stats on the equity curve feed into the report."""
        from ai_trade.backtest.metrics.report import generate_report
        from scripts.run_ehlers_replication import _walk_forward_on_equity

        result = _run(synthetic_cyclic_ohlcv)
        wf = _walk_forward_on_equity(result.equity_curve, n_windows=8)
        assert wf is not None  # 1500-bar equity is plenty for 8 windows

        md_path = generate_report(
            result=result,
            validation={"walk_forward": wf},
            strategy_name="ehlers_bp_swing_wf",
            output_dir=tmp_path,
            data_source="synthetic",
        )
        content = md_path.read_text(encoding="utf-8")
        assert "Walk-forward" in content or "walk_forward" in content.lower()


# ---------------------------------------------------------------------------
# CLI wiring (dry-run smoke — no network)
# ---------------------------------------------------------------------------


class TestReplicationCLI:
    def test_parse_args_with_defaults(self):
        """Argparse contract — required/default args."""
        from scripts.run_ehlers_replication import _parse_args

        args = _parse_args(
            ["--start", "2022-01-01", "--end", "2023-12-31"]
        )
        assert args.symbol == "^GSPC"
        assert args.cash == 100_000.0
        assert args.hp_period == 48
        assert args.lp_period == 10
        assert args.pct_of_dcp == pytest.approx(0.90)
        assert args.stop_pct == pytest.approx(0.05)
