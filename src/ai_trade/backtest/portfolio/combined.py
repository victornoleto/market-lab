"""combine equity curves + compute metrics + build synthetic trial.

Weighted-returns offline combination — zero engine changes.
Citations: `[systematic_trading, Carver — capital allocation]`,
`[risk_parity, Qian — risk-parity math]`.
"""

from __future__ import annotations

import pandas as pd


def combine_equity_curves(
    curves: list[pd.Series],
    weights: list[float],
    initial_capital: float,
) -> pd.Series:
    """Combine N equity curves into one via weighted daily returns.

    Steps:
    1. Align all curves on their DatetimeIndex intersection.
    2. Compute per-curve daily returns (pct_change, drop NaN row).
    3. Portfolio return = sum(weights[i] * returns[i]).
    4. Rebuild equity curve from ``initial_capital`` by cumprod(1+r).

    The first bar of the output equals ``initial_capital`` (no returns
    yet); subsequent bars reflect the weighted cumulative return.
    """
    if not curves:
        raise ValueError("curves must be non-empty")
    if len(curves) != len(weights):
        raise ValueError(
            f"len(curves)={len(curves)} != len(weights)={len(weights)}"
        )
    weight_sum = sum(weights)
    if not (0.999 <= weight_sum <= 1.001):
        raise ValueError(
            f"weights must sum to 1.0 (got {weight_sum:.4f})"
        )

    # Step 1: align on intersection
    common = curves[0].index
    for c in curves[1:]:
        common = common.intersection(c.index)
    if len(common) < 2:
        raise ValueError(
            f"aligned index too short ({len(common)} bars) — curves do not overlap enough"
        )
    aligned = [c.reindex(common).ffill() for c in curves]

    # Step 2 + 3: weighted returns
    returns = [c.pct_change() for c in aligned]
    port_ret = sum(w * r for w, r in zip(weights, returns))

    # Step 4: rebuild equity
    port_ret.iloc[0] = 0.0  # first bar has no return
    equity = initial_capital * (1.0 + port_ret).cumprod()
    equity.name = "equity"
    return equity


import numpy as np

from ai_trade.backtest.engine.runner import BacktestResult
from ai_trade.backtest.grid.result import TrialResult
from ai_trade.backtest.metrics.performance import (
    cagr,
    max_drawdown,
    returns_from_equity,
    sharpe,
)


def compute_portfolio_metrics(
    equity_curve: pd.Series,
    periods_per_year: int = 252,
) -> dict[str, float]:
    """Compute Sharpe / CAGR / max DD for a portfolio equity curve.

    Matches the helper semantics used by :class:`GridRunner` so the
    numbers are comparable with sub-strategy per-trial metrics.
    """
    if len(equity_curve) < 2:
        return {"sharpe": 0.0, "cagr": 0.0, "max_drawdown": 0.0}
    rets = returns_from_equity(equity_curve)
    sh = float(sharpe(rets, periods_per_year=periods_per_year))
    cg = float(cagr(equity_curve, periods_per_year=periods_per_year))
    dd = float(max_drawdown(equity_curve))
    return {"sharpe": sh, "cagr": cg, "max_drawdown": dd}


def make_portfolio_trial(
    config_id: int,
    config,
    equity_curve: pd.Series,
    initial_cash: float,
    periods_per_year: int = 252,
) -> TrialResult:
    """Wrap a combined equity curve into a synthetic TrialResult.

    The produced TrialResult has empty ``trades`` and ``fills`` lists
    (we're working at the equity-curve level, not per-trade). That is
    fine — the existing gate pipeline uses ``equity_curve`` and the
    scalar metrics; it never iterates trades for PBO/DSR/WF.
    """
    result = BacktestResult(
        equity_curve=equity_curve,
        trades=[],
        fills=[],
        initial_cash=float(initial_cash),
        final_equity=float(equity_curve.iloc[-1]),
    )
    metrics = compute_portfolio_metrics(
        equity_curve, periods_per_year=periods_per_year,
    )
    sh = metrics["sharpe"]
    if not np.isfinite(sh):
        sh = 0.0
    return TrialResult(
        config_id=config_id,
        config=config,
        result=result,
        sharpe=float(sh),
        cagr=float(metrics["cagr"]),
        max_drawdown=float(metrics["max_drawdown"]),
        status="ok",
    )
