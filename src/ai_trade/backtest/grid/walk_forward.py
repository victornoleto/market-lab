"""Per-config walk-forward for grid trials.

For fixed-configuration strategies (Clenow — no per-window re-optimization)
running the full backtest once and slicing the equity curve into contiguous
OOS chunks yields the same OOS metrics as running each window
independently. This module implements that slice-and-aggregate pattern,
matching ``scripts/run_clenow_replication.py:_walk_forward_on_equity``.

The canonical gate (rule #5 from ``knowledge/SKILL.md``): at least
``min_windows`` windows, at least ``min_profitable_ratio`` of them
profitable, and max drawdown within any window ``≤ max_drawdown``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd
from joblib import Parallel, delayed

from ai_trade.backtest.grid.result import GridResult
from ai_trade.backtest.validation.walk_forward import walk_forward_gate


_log = logging.getLogger("ai_trade.grid.wf")


@dataclass
class WFResult:
    """Walk-forward summary for one config."""

    config_id: int
    n_windows: int
    n_profitable: int
    max_drawdown: float
    verdict: str
    oos_returns: list[float] = field(default_factory=list)
    oos_drawdowns: list[float] = field(default_factory=list)


def wf_for_config(
    *,
    equity_curve: pd.Series,
    config_id: int,
    n_windows: int = 8,
    min_window_bars: int = 10,
    min_profitable_ratio: float = 6.0 / 8.0,
    max_drawdown: float = 0.25,
) -> WFResult:
    """Split ``equity_curve`` into ``n_windows`` contiguous chunks and gate.

    If the curve is too short (< ``n_windows × min_window_bars`` bars) the
    result is returned with ``n_windows=0`` and ``verdict="reject"``.
    """
    n_total = len(equity_curve)
    if n_total < n_windows * min_window_bars:
        return WFResult(
            config_id=config_id,
            n_windows=0,
            n_profitable=0,
            max_drawdown=0.0,
            verdict="reject",
        )

    returns: list[float] = []
    drawdowns: list[float] = []
    size = n_total // n_windows
    for i in range(n_windows):
        start = i * size
        stop = start + size if i < n_windows - 1 else n_total
        window = equity_curve.iloc[start:stop]
        if len(window) < 2:
            continue
        ret = float(window.iloc[-1] / window.iloc[0] - 1.0)
        peak = window.cummax()
        dd = float(((peak - window) / peak).max())
        returns.append(ret)
        drawdowns.append(dd)

    verdict = walk_forward_gate(
        returns,
        drawdowns,
        min_windows=n_windows,
        min_profitable_ratio=min_profitable_ratio,
        max_drawdown=max_drawdown,
    )
    return WFResult(
        config_id=config_id,
        n_windows=len(returns),
        n_profitable=sum(1 for r in returns if r > 0),
        max_drawdown=max(drawdowns) if drawdowns else 0.0,
        verdict=verdict,
        oos_returns=returns,
        oos_drawdowns=drawdowns,
    )


def wf_for_grid(
    grid: GridResult,
    *,
    n_windows: int = 8,
    n_jobs: int = 1,
    **wf_kwargs,
) -> dict[int, WFResult]:
    """Run :func:`wf_for_config` for each OK trial in the grid.

    Returns a dict ``{config_id: WFResult}``. Error trials (no BacktestResult)
    are skipped silently — they already don't contribute to the PBO matrix
    or the DSR gate.
    """
    ok_trials = grid.ok_trials
    if not ok_trials:
        return {}

    def _one(trial):
        assert trial.result is not None
        return wf_for_config(
            equity_curve=trial.result.equity_curve,
            config_id=trial.config_id,
            n_windows=n_windows,
            **wf_kwargs,
        )

    if n_jobs == 1 or len(ok_trials) <= 1:
        results = [_one(t) for t in ok_trials]
    else:
        results = Parallel(n_jobs=n_jobs, backend="loky", return_as="list")(
            delayed(_one)(t) for t in ok_trials
        )
    return {r.config_id: r for r in results}
