"""quantstats adapter — analytics-only cross-check.

Does NOT run the strategy. Consumes an equity curve produced by another adapter
(bt/vectorbt/backtrader) and re-computes CAGR/Sharpe/MaxDD independently using
quantstats' own formulas. Used to isolate metric-computation bugs from
strategy-execution bugs.
"""
from __future__ import annotations

import traceback

import numpy as np
import pandas as pd

from studies._archive.phase_3_5c.reports.cross_lib.adapters.bt_adapter import (
    _empty_result,
    _walk_forward_sharpe,
    _dsr_pval,
)
from studies._archive.phase_3_5c.reports.cross_lib.types import RunResult, VariantConfig


class QuantstatsAdapter:
    name: str = "quantstats"

    def run_on_equity(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
        equity: pd.Series,
        source_lib: str,
    ) -> RunResult:
        """quantstats consumes an equity curve from another run.

        `source_lib` is recorded in error_detail for traceability.
        """
        try:
            import quantstats as qs  # noqa: F401
        except ImportError as exc:
            return _empty_result(
                variant, self.name, window, stage, "SKIPPED", str(exc)
            )

        try:
            import quantstats as qs

            rets = equity.pct_change().dropna()
            cagr = qs.stats.cagr(rets)
            sharpe = qs.stats.sharpe(rets)
            max_dd = qs.stats.max_drawdown(equity)
            monthly = rets.resample("ME").apply(lambda x: (1 + x).prod() - 1)

            return RunResult(
                variant_id=variant.variant_id,
                lib=f"{self.name}(from={source_lib})",
                window=window,
                stage=stage,
                equity_curve=equity,
                monthly_returns=monthly,
                trade_dates=[],
                cagr=float(cagr),
                sharpe=float(sharpe),
                max_dd=float(max_dd),
                wf_splits_8=_walk_forward_sharpe(rets, 8),
                dsr_pval=_dsr_pval(float(sharpe), rets),
                outcome="OK",
                error_detail=f"recomputed from {source_lib} equity",
            )
        except Exception as exc:  # pragma: no cover
            return _empty_result(
                variant,
                self.name,
                window,
                stage,
                "ERROR",
                f"{exc}\n{traceback.format_exc()}",
            )

    def run(
        self,
        variant: VariantConfig,
        window: tuple[str, str],
        stage: int,
    ) -> RunResult:
        """Not a standalone backtester; direct run returns DATA_UNAVAILABLE.

        Callers should use `run_on_equity` passing the equity curve from bt/vectorbt.
        """
        return _empty_result(
            variant,
            self.name,
            window,
            stage,
            "DATA_UNAVAILABLE",
            "quantstats requires equity curve input; use run_on_equity",
        )
