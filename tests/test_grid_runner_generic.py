"""Generic grid runner contract tests.

Verifies that ``GridRunner`` + ``TrialResult`` + ``trial_{to,from}_dir``
are not hardcoded to ``ClenowGridConfig`` — they must accept any frozen
dataclass via ``config_cls``. This unblocks the Ehlers execution
(Commit 9) without touching the existing Clenow tests (contract
preserved).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def _fake_backtest_result(n: int = 100):
    """Build a minimal BacktestResult — equity curve only; no trades."""
    from ai_trade.backtest.engine.runner import BacktestResult

    idx = pd.date_range("2023-01-01", periods=n, freq="B")
    equity = pd.Series(100_000.0 * (1 + 0.0005) ** np.arange(n), index=idx)
    return BacktestResult(
        equity_curve=equity,
        trades=[],
        fills=[],
        initial_cash=100_000.0,
        final_equity=float(equity.iloc[-1]),
    )


class TestRunnerAcceptsEhlersConfig:
    def test_run_with_ehlers_configs(self, tmp_path: Path):
        from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
        from ai_trade.backtest.grid.runner import GridRunner

        configs = [
            EhlersGridConfig(hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.02),
            EhlersGridConfig(hp_period=48, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05),
            EhlersGridConfig(hp_period=80, lp_period=20, pct_of_dcp=1.00, stop_pct=0.05),
        ]

        runner = GridRunner(
            checkpoint_dir=tmp_path,
            config_cls=EhlersGridConfig,
        )

        trial_fn = lambda cfg: _fake_backtest_result()  # noqa: E731
        grid_result = runner.run(
            configs=configs,
            trial_fn=trial_fn,
            run_id="ehlers_smoke",
        )

        assert len(grid_result.trials) == 3
        # Each trial should preserve the *concrete* EhlersGridConfig — not
        # silently converted to ClenowGridConfig or Any.
        for trial in grid_result.trials:
            assert isinstance(trial.config, EhlersGridConfig)
            assert trial.status == "ok"


class TestCheckpointRoundtripWithEhlers:
    def test_trial_to_from_dir_with_ehlers_config(self, tmp_path: Path):
        from ai_trade.backtest.grid.ehlers_config import EhlersGridConfig
        from ai_trade.backtest.grid.result import (
            TrialResult,
            trial_from_dir,
            trial_to_dir,
        )

        cfg = EhlersGridConfig(
            hp_period=80, lp_period=10, pct_of_dcp=0.90, stop_pct=0.05,
        )
        trial = TrialResult(
            config_id=7,
            config=cfg,
            result=_fake_backtest_result(),
            sharpe=0.42,
            cagr=0.08,
            max_drawdown=0.12,
            status="ok",
        )
        directory = tmp_path / "trial_7"
        trial_to_dir(trial, directory)

        # Must specify the class — meta.json stores __dict__ only.
        restored = trial_from_dir(directory, config_cls=EhlersGridConfig)
        assert restored.config == cfg
        assert isinstance(restored.config, EhlersGridConfig)
        assert restored.config_id == 7
        assert restored.sharpe == 0.42


class TestBackwardCompatibility:
    def test_trial_from_dir_default_is_clenow(self, tmp_path: Path):
        """Existing call-sites that omit ``config_cls`` keep working."""
        from ai_trade.backtest.grid.config import ClenowGridConfig
        from ai_trade.backtest.grid.result import (
            TrialResult,
            trial_from_dir,
            trial_to_dir,
        )

        cfg = ClenowGridConfig(lookback_regression=90, top_pct=0.20, risk_factor=0.001)
        trial = TrialResult(
            config_id=0,
            config=cfg,
            result=_fake_backtest_result(),
            sharpe=0.5,
            cagr=0.10,
            max_drawdown=0.15,
            status="ok",
        )
        directory = tmp_path / "trial_0"
        trial_to_dir(trial, directory)

        restored = trial_from_dir(directory)  # no config_cls arg
        assert isinstance(restored.config, ClenowGridConfig)
        assert restored.config == cfg

    def test_runner_defaults_to_clenow(self, tmp_path: Path):
        """GridRunner without ``config_cls`` also keeps working for Clenow."""
        from ai_trade.backtest.grid.config import ClenowGridConfig
        from ai_trade.backtest.grid.runner import GridRunner

        configs = [
            ClenowGridConfig(lookback_regression=60, top_pct=0.10, risk_factor=0.001),
        ]
        runner = GridRunner(checkpoint_dir=tmp_path)

        grid_result = runner.run(
            configs=configs,
            trial_fn=lambda _cfg: _fake_backtest_result(),
            run_id="clenow_default",
        )

        assert len(grid_result.trials) == 1
        assert isinstance(grid_result.trials[0].config, ClenowGridConfig)
