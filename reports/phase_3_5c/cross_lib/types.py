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
