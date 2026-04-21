"""Core typed structures for cross-lib validation.

Citations
---------
Design spec: docs/superpowers/specs/2026-04-20-plano-b-cross-lib-validation-design.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd

SignalType = Literal["ema_regime", "donchian"]
RebalanceMode = Literal["daily", "monthly_sell", "monthly_cashflow", "threshold"]
ExecutionModel = Literal["letf_synthetic", "cfd_synthetic", "real_etf"]
StrategyFamily = Literal["plano_b", "plano_a"]


@dataclass(frozen=True)
class LegConfig:
    """Config for a single portfolio leg.

    signal_ticker : str
        Underlying index/ETF the signal is computed on (e.g. SPY for SSO leg).
        `[leverage_for_the_long_run, p.13]` — signal on 1x index, execution on LETF.
    execution_ticker : str
        Instrument that holds the position when signal is LONG (e.g. SSO).
    """

    signal_type: SignalType
    signal_params: dict
    signal_ticker: str
    execution_ticker: str


@dataclass(frozen=True)
class RebalanceConfig:
    """Portfolio rebalance cadence.

    `[advances_fin_ml, p.275-278]` — drift-triggered (threshold) rebalance rules.
    """

    mode: RebalanceMode
    threshold_pp: float | None

    def __post_init__(self) -> None:
        if self.mode == "threshold" and self.threshold_pp is None:
            raise ValueError("threshold_pp required when mode='threshold'")


@dataclass(frozen=True)
class VariantConfig:
    """Declarative description of a single run configuration.

    A VariantConfig is strategy-family-agnostic by design — Plano A will add
    its own variants under `family="plano_a"` with `execution_model="cfd_synthetic"`.
    """

    variant_id: str
    family: StrategyFamily
    execution_model: ExecutionModel
    legs: tuple[LegConfig, ...]
    rebalance: RebalanceConfig
    target_weights: tuple[float, ...]
    windows: tuple[tuple[str, str], ...]


Outcome = Literal["OK", "SKIPPED", "DATA_UNAVAILABLE", "ERROR"]


@dataclass
class RunResult:
    """Output of a single adapter run.

    Non-frozen because pandas Series are unhashable; we treat it as an
    immutable value by convention (don't mutate after construction).

    window : tuple[str, str]
        (start_date, end_date) as strings for the run backtest period.
    stage : int
        1 = Stage 1 (our own historical data), 2 = Stage 2 (independent data).
    equity_curve : pd.Series
        Daily $1 → cumulative (compounded), indexed by trading day (not calendar day).
    monthly_returns : pd.Series
        Per-month returns (e.g., Jan 2020 return, Feb 2020 return), used for verdict comparison.
    trade_dates : list[pd.Timestamp]
        Dates when signal or position status changed (useful for reviewing turnover/rebalance timing).
    cagr : float
        Compound Annual Growth Rate (%).
    sharpe : float
        Annualized Sharpe ratio.
    max_dd : float
        Maximum drawdown (negative value, e.g., -0.25 for 25% DD).
    wf_splits_8 : list[float]
        Walk-forward Sharpe ratio per split (N=8 splits); N=8 matches project gate
        `WF≥6/8` (CLAUDE.md §5). Methodology per [advances_fin_ml, ch.12].
    dsr_pval : float
        Deflated Sharpe Ratio p-value (Bailey & López de Prado, [advances_fin_ml, p.275]).
        If p-value < 0.05, the Sharpe is statistically significant after correction for trials.
    outcome : Outcome
        Terminal status: "OK" (passed all gates), "SKIPPED" (adapter not available),
        "DATA_UNAVAILABLE" (insufficient history), or "ERROR" (runtime failure).
    error_detail : str | None
        Human-readable reason when outcome ≠ "OK"; None otherwise.
    """

    variant_id: str
    lib: str
    window: tuple[str, str]
    stage: int
    equity_curve: pd.Series
    monthly_returns: pd.Series
    trade_dates: list[pd.Timestamp]
    cagr: float
    sharpe: float
    max_dd: float
    wf_splits_8: list[float]
    dsr_pval: float
    outcome: Outcome
    error_detail: str | None
